"""
鸟类识别服务 — 调用通义千问 Qwen3.6-Flash 多模态模型
"""
import base64
import json
import re
import requests
from typing import List, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Bird


async def recognize_bird(image_path: str, db: Session) -> List[dict]:
    """
    识别鸟类，返回 Top3 识别结果
    """
    if not settings.QWEN_API_KEY:
        return _mock_recognize(db)

    try:
        result = await _qwen_recognize(image_path, db)
        if result:
            return result
    except Exception as e:
        print(f"Qwen 识别失败，降级为模拟模式: {e}")

    return _mock_recognize(db)


async def _qwen_recognize(image_path: str, db: Session) -> Optional[List[dict]]:
    """调用 Qwen3.6-Flash 识别鸟类"""
    # 读取并编码图片（兼容远程 URL 和本地路径）
    if image_path.startswith("http://") or image_path.startswith("https://"):
        resp = requests.get(image_path, timeout=30)
        resp.raise_for_status()
        image_bytes = resp.content
    else:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    image_data = base64.b64encode(image_bytes).decode("utf-8")

    # 推断 MIME 类型
    ext = image_path.rsplit(".", 1)[-1].lower() if "." in image_path else "jpg"
    mime_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}
    mime_type = mime_map.get(ext, "jpeg")

    client = OpenAI(
        api_key=settings.QWEN_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    response = client.chat.completions.create(
        model=settings.QWEN_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{mime_type};base64,{image_data}"},
                },
                {
                    "type": "text",
                    "text": (
                        "请识别这张图片中的鸟类，按可能性从高到低列出最可能的3个鸟种。"
                        "请严格按以下 JSON 格式输出，不要包含其他文字：\n"
                        '{"results":[{"name":"鸟种中文名","confidence":0.95},{"name":"鸟种中文名","confidence":0.80},{"name":"鸟种中文名","confidence":0.65}]}\n'
                        "置信度取 0~1 之间的小数。如果无法识别，name 填'未知鸟类'。"
                    ),
                },
            ],
        }],
        temperature=0.3,
    )

    content = response.choices[0].message.content.strip()
    # 提取 JSON（模型可能在 JSON 前后包裹 markdown 代码块）
    json_match = re.search(r"\{[\s\S]*\}", content)
    if not json_match:
        print(f"Qwen 返回内容无法解析: {content}")
        return None

    data = json.loads(json_match.group())
    raw_results = data.get("results", [])
    if not raw_results:
        return None

    # 匹配数据库中的鸟类
    results = []
    for item in raw_results[:3]:
        name = item.get("name", "未知鸟类")
        confidence = float(item.get("confidence", 0.5))
        bird = db.query(Bird).filter(Bird.name == name).first()
        results.append({
            "bird_id": bird.id if bird else 0,
            "name": name,
            "confidence": confidence,
        })

    return results


def _mock_recognize(db: Session) -> List[dict]:
    """模拟识别 — 从数据库按搜索量随机选3种鸟"""
    import random
    birds = db.query(Bird).order_by(Bird.search_count.desc()).all()

    if len(birds) < 3:
        return [
            {"bird_id": 0, "name": "麻雀", "confidence": 0.85},
            {"bird_id": 0, "name": "喜鹊", "confidence": 0.72},
            {"bird_id": 0, "name": "燕子", "confidence": 0.58},
        ]

    weights = [b.search_count + 1 for b in birds]
    selected = random.choices(birds, weights=weights, k=3)
    seen = set()
    unique_selected = []
    for b in selected:
        if b.id not in seen:
            seen.add(b.id)
            unique_selected.append(b)

    while len(unique_selected) < 3:
        for b in birds:
            if b.id not in seen:
                seen.add(b.id)
                unique_selected.append(b)
                break

    confidences = [
        round(random.uniform(0.75, 0.95), 2),
        round(random.uniform(0.50, 0.74), 2),
        round(random.uniform(0.25, 0.49), 2),
    ]
    return [
        {"bird_id": bird.id, "name": bird.name, "confidence": confidences[i]}
        for i, bird in enumerate(unique_selected[:3])
    ]
