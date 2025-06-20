from typing import Optional
from fastapi import APIRouter

from app.utils.prompt_manager import PromptManager
from app.ai.aimo import AIMO
from app.exceptions.server_exceptions import ServerException

from app.models.system_prompt import SystemPromptUpdate

# Create a singleton PromptManager
prompt_manager = PromptManager()

router = APIRouter(
    prefix="",
    tags=["system-prompt"],
)

@router.get("/get-system-prompt")
async def get_system_prompt(section: Optional[str] = None):
    """Retrieve the current system prompt"""
    try:
        return prompt_manager.get_prompt(section)
    except ValueError as e:
        raise ServerException(detail=str(e))

@router.post("/change-system-prompt")
async def change_system_prompt(update_data: SystemPromptUpdate):
    """Change the system prompt and record its history"""
    try:
        # Update the prompt
        prompt_manager.update_prompt(
            update_data.section, 
            update_data.content, 
            update_data.modified_by, 
            update_data.purpose
        )
        
        # Update the system prompt in the AIMO instance (in practice, this requires a way to update all active AIMO instances)
        # Here we assume AIMO is a singleton or there is a way to get the current active instance
        aimo = AIMO()  # Get the AIMO instance
        prompt_data = prompt_manager.get_prompt()
        aimo._self_cognition = prompt_data["self_cognition"]
        aimo._guidelines = prompt_data["guidelines"]
        aimo._rules = prompt_data["rules"]
        aimo._overall_style = prompt_data["overall_style"]
        # Return HTTP Response 200 directly
        return {"status": "success", "code": 200}
    except ValueError as e:
        raise ServerException(detail=str(e))

@router.get("/review-history-prompt")
async def review_history_prompt():
    """View the history of system prompts"""
    return prompt_manager.get_history()

@router.get("/select-history-prompt/{history_id}")
async def select_history_prompt(history_id: int):
    """Select a specific historical version"""
    try:
        return prompt_manager.get_history_prompt(history_id)
    except ValueError as e:
        raise ServerException(detail=str(e))