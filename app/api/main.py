from fastapi import APIRouter

from app.api.routes import chat, emo, auth, invitation_code, user_survey, system_prompt

"""
Author: Jack Pan, Wesley Xu
Date: 2025-1-20
Description:
    This module defines the routers and paths of the services
"""


api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])  # Chat service
api_router.include_router(emo.router, prefix="/emotion", tags=["emotion"])  # Emotion router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])  # Authentication router
api_router.include_router(invitation_code.router, prefix="/invitation-code",
                          tags=["invitation_code"])  # Invitation code router
api_router.include_router(user_survey.router, prefix="/survey",
                          tags=["survey"])  # User survey router
api_router.include_router(system_prompt.router, prefix="/system-prompt",
                          tags=["system_prompt"])  # System prompt router