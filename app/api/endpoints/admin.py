from typing import Dict, Any
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.utils.jwt_utils import JWTUtils
from app.core.redis import RedisClient
from app.api import deps

router = APIRouter()

class QuotaUpdate(BaseModel):
    token: str
    new_quota: int

class QuotaResponse(BaseModel):
    new_token: str
    quota: int
    message: str

@router.post(
    "/update-quota", 
    response_model=QuotaResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user token quota",
    description="Admin functionality: Update API call quota for a specific JWT token"
)
async def update_token_quota(
    data: QuotaUpdate,
    admin_user = Depends(deps.get_admin_user),
    jwt_utils: JWTUtils = Depends(deps.get_jwt_utils)
) -> Dict[str, Any]:
    """Update the quota limit for a user token"""
    if data.new_quota <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quota must be greater than zero"
        )
    
    try:
        # Decode current token to validate its validity
        payload = jwt_utils.decode_token(data.token)
        jti = payload.get("jti")
        
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token format: Missing JTI claim"
            )
        
        # Generate new token
        new_token = jwt_utils.update_token_quota(data.token, data.new_quota)
        
        # Clear any existing rate limit counts
        try:
            redis_client = RedisClient.get_client()
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            key = f"rate_limit:{jti}:{today}"
            redis_client.delete(key)
        except Exception as e:
            # If Redis operation fails, continue but log error
            print(f"Failed to clear rate limit count: {str(e)}")
        
        return {
            "new_token": new_token,
            "quota": data.new_quota,
            "message": "Token quota successfully updated"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update token quota: {str(e)}"
        )
