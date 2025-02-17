import logging
from typing import Any, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.chat_schemas import ChatDto, ChatItem, HealthCheck, Message
from app.ai.aimo import AIMO


"""
Author: Jack Pan, Wesley Xu
Date: 2025-1-20
Description:
    This module defines the controller of chat services
"""
router = APIRouter(prefix="", tags=["chat"])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the AI model
aimo = AIMO()

@router.post("/", response_model=ChatItem)
async def generate(dto: ChatDto) -> ChatItem:
    """
    生成聊天响应
    """
    try:
        if not dto.messages:
            raise HTTPException(
                status_code=400,
                detail="消息列表不能为空"
            )
            
        logger.debug(f"收到请求类型: {type(dto)}")
        logger.debug(f"消息列表类型: {type(dto.messages)}")
        logger.debug(f"第一条消息类型: {type(dto.messages[0])}")
        logger.debug(f"消息内容: {[m.dict() for m in dto.messages]}")
        
        response = await aimo.get_response(
            messages=dto.messages,
            temperature=dto.temperature,
            max_new_tokens=dto.max_tokens
        )
        
        result = ChatItem(content=response, role="assistant")
        logger.debug(f"返回结果: {result.dict()}")
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"错误详情: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    健康检查端点
    """
    return HealthCheck(status="healthy")