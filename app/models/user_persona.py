from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field, field_validator

# Survey form models

class UserBasic(BaseModel):
    """User persona data"""
    survey_responses: Dict[str, Any]
    username: str = Field(..., description="Username")
    timestamp: Optional[str] = Field(None, description="Submission timestamp")

class Demographics(BaseModel):
    """Demographics information (gender and age)"""
    gender: str = Field(..., description="User gender")
    age_range: str = Field(..., description="User age range")


class HabitsPermissions(BaseModel):
    """User habits and permissions"""
    bedtime: str = Field(..., description="Typical bedtime")
    biometric_consent: bool = Field(..., description="Biometric data consent")


class EmotionalState(BaseModel):
    """User emotional state"""
    primary_emotions: List[str] = Field(..., description="List of primary emotions")


class MBTIPersonality(BaseModel):
    """MBTI personality assessment"""
    energy: str = Field(..., description="Energy orientation (introvert/extrovert)")
    information: str = Field(..., description="Information processing (sensing/intuitive)")
    decision: str = Field(..., description="Decision making (thinking/feeling)")
    lifestyle: str = Field(..., description="Lifestyle preference (judging/perceiving)")


class StressLevel(BaseModel):
    """Stress assessment"""
    stress_level: str = Field(..., description="Stress level value")


class SurveyRequest(BaseModel):
    """User survey request model"""
    username: str = Field(None, description="Username")
    demographics: Demographics
    habits_permissions: HabitsPermissions
    emotional_state: EmotionalState
    personality_assessment: MBTIPersonality
    stress_assessment: StressLevel


class SurveyResponse(BaseModel):
    """User survey response model"""
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message") 
    processed_data: Dict[str, Any] = Field(..., description="Processed data")
