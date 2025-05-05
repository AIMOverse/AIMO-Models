import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, Body, Depends, Header
from fastapi.security import OAuth2PasswordBearer

from app.models.auth import SurveyRequest, SurveyResponse
from app.exceptions.auth_exceptions import AuthException
from app.utils.jwt_utils import JWTUtils

router = APIRouter(prefix="", tags=["survey"])
jwt_utils = JWTUtils()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/submit", response_model=SurveyResponse)
async def submit_survey(
    survey_data: SurveyRequest = Body(...),
    token: str = Depends(oauth2_scheme)
) -> SurveyResponse:
    """
    Submit user survey data
    
    Args:
        survey_data (SurveyRequest): User survey data in metaphorical format
        token (str): Authentication token
        
    Returns:
        SurveyResponse: Processing result and standardized data
    """
    try:
        # Validate token
        decoded_token = jwt_utils.decode_token(token)
        
        # Since the frontend is already sending direct meaning fields,
        # we don't need to process metaphorical mappings
        
        # Add username from token if available
        username = decoded_token.get("username", "anonymous_user")
        
        # Construct response with received data
        return SurveyResponse(
            success=True,
            message="Survey data submitted successfully",
            processed_data={
                "username": username,
                "survey_responses": survey_data.dict(),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise AuthException(status_code=400, message=f"Failed to process survey data: {str(e)}")
