import datetime
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from app.services.user_service import UserService
from app.utils.jwt_utils import JWTUtils

router = APIRouter(prefix="/user", tags=["user"])
jwt_utils = JWTUtils()


# Helper function: Extract user_id from JWT token in Authorization header
def get_current_user_id(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1]
    payload = jwt_utils.decode_token(token)
    return payload.get("user_id")


# Route: Get the user's daily token limit usage and next refresh time
@router.get("/token-limit")
async def get_token_limit(request: Request):
    """
    Get the user's daily token usage info.
    Returns: {"total": 10000, "used": 1000, "next_refresh_at": "2025-07-18T09:00:00"}
    """
    user_id = get_current_user_id(request)
    if not user_id:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    info = UserService.get_token_limit_info(user_id)
    if not info:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    return info
