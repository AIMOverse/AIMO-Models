from typing import Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.ai.aimo import AIMO
from app.models.chat import ChatDto, ChatItem, HealthCheck


"""
Author: Jack Pan, Wesley Xu
Date: 2025-1-20
Description:
    This module defines the controller of chat services
"""
router = APIRouter(prefix="/chat", tags=["chat"])


# Initialize the AI model
aimo = AIMO()

@router.post("/", response_model=ChatItem)
async def generate(dto: ChatDto) -> Any:
    """
    处理 /chat/ 端点的 POST 请求
    """
    try:
        # 验证消息数组
        if not dto.messages or not isinstance(dto.messages, list):
            raise HTTPException(
                status_code=400,
                detail="Invalid request body: messages array is required"
            )
            
        # 使用 AI 模型生成响应
        response = await aimo.get_response(
            messages=dto.messages,
            temperature=dto.temperature or 1.32,  # 默认值与前端保持一致
            max_new_tokens=dto.max_new_tokens or 500  # 默认值与前端保持一致
        )

        return ChatItem(role="assistant", content=response)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    健康检查端点
    """
    return HealthCheck(status="healthy")