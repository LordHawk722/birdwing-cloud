"""
AI 鸟类识别服务

支持两种模式：
1. 模拟模式（默认）：从数据库中随机返回鸟类作为识别结果
2. 百度AI模式：调用百度AI鸟类识别API（需配置API密钥）
"""
import random
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Bird


async def recognize_bird(image_path: str, db: Session) -> List[dict]:
    """
    识别鸟类
    返回 Top3 识别结果，格式：
    [{"bird_id": 1, "name": "麻雀", "confidence": 0.95}, ...]
    """
    # 尝试真实 AI 识别（这里预留百度AI接口）
    # result = await _baidu_ai_recognize(image_path, db)
    # if result:
    #     return result

    # 默认：模拟识别结果
    return _mock_recognize(db)


def _mock_recognize(db: Session) -> List[dict]:
    """模拟鸟类识别 - 从数据库中随机选3种鸟"""
    birds = db.query(Bird).order_by(Bird.search_count.desc()).all()

    if len(birds) < 3:
        # 数据不足时生成默认数据
        return [
            {"bird_id": 0, "name": "麻雀", "confidence": 0.85},
            {"bird_id": 0, "name": "喜鹊", "confidence": 0.72},
            {"bird_id": 0, "name": "燕子", "confidence": 0.58},
        ]

    # 按搜索量加权随机（越常见的鸟越容易被"识别"出来）
    weights = [b.search_count + 1 for b in birds]
    selected = random.choices(birds, weights=weights, k=3)

    # 去重
    seen = set()
    unique_selected = []
    for b in selected:
        if b.id not in seen:
            seen.add(b.id)
            unique_selected.append(b)

    # 如果不足3个，再补充
    while len(unique_selected) < 3:
        for b in birds:
            if b.id not in seen:
                seen.add(b.id)
                unique_selected.append(b)
                break

    # 生成结果，置信度递减
    confidences = [
        round(random.uniform(0.75, 0.95), 2),
        round(random.uniform(0.50, 0.74), 2),
        round(random.uniform(0.25, 0.49), 2),
    ]

    result = []
    for i, bird in enumerate(unique_selected[:3]):
        result.append({
            "bird_id": bird.id,
            "name": bird.name,
            "confidence": confidences[i],
        })

    return result


async def _baidu_ai_recognize(image_path: str, db: Session) -> Optional[List[dict]]:
    """
    百度AI鸟类识别（预留）
    需要配置 BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY
    参考文档：https://ai.baidu.com/tech/imagerecognition/animal
    """
    from app.config import settings

    if not settings.BAIDU_API_KEY or not settings.BAIDU_SECRET_KEY:
        return None  # 未配置，走模拟模式

    try:
        # TODO: 实现百度AI API调用
        # 1. 获取 access_token
        # 2. 调用鸟类识别接口
        # 3. 解析结果，匹配数据库中的鸟类
        pass
    except Exception as e:
        print(f"百度AI识别失败: {e}")
        return None
