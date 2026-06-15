"""
AI 聊天路由 — 代理 OpenAI 兼容 API
"""
import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from app.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 超长连接的超时设置
HTTPX_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = True


@router.post("")
async def chat(request: ChatRequest):
    """AI 聊天（支持流式 SSE 输出）"""
    if not settings.AI_API_KEY:
        return {"code": 200, "message": "AI not configured", "data": {"content": "AI 服务未配置，请在 .env 中设置 AI_API_KEY。"}}

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    # 自动添加系统提示词
    has_system = any(m["role"] == "system" for m in messages)
    if not has_system:
        messages.insert(0, {"role": "system", "content": settings.AI_SYSTEM_PROMPT})

    if request.stream:
        return StreamingResponse(
            _stream_chat(messages),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    else:
        content = await _call_ai(messages)
        return {"code": 200, "message": "success", "data": {"content": content}}


async def _call_ai(messages: list) -> str:
    """非流式调用 AI API"""
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        resp = await client.post(
            f"{settings.AI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.AI_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _stream_chat(messages: list):
    """流式调用 AI API，逐 token 返回 SSE"""
    try:
        async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
            async with client.stream(
                "POST",
                f"{settings.AI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "stream": True,
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            yield "data: [DONE]\n\n"
                            break
                        yield f"data: {data}\n\n"
    except Exception as e:
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        yield "data: [DONE]\n\n"
