from fastapi import APIRouter

from app.api.routes import chat

"""
Author: Jack Pan
Date: 2025-1-20
Description:
    This module defines the routers and paths of the services
"""


api_router = APIRouter()
api_router.include_router(chat.router)
