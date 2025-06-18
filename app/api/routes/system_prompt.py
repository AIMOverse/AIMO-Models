from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Depends

from app.utils.prompt_manager import PromptManager
from app.ai.aimo import AIMO

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
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-system-prompt")
async def change_system_prompt(
    section: str,
    content: str,
    modified_by: Optional[str] = "Admin",
    purpose: str = "Update system prompt"
):
    """Change the system prompt and record its history"""
    try:
        # Update the prompt
        prompt_manager.update_prompt(section, content, modified_by, purpose)
        
        # Update the system prompt in the AIMO instance (in practice, this requires a way to update all active AIMO instances)
        # Here we assume AIMO is a singleton or there is a way to get the current active instance
        aimo = AIMO()  # Get the AIMO instance
        prompt_data = prompt_manager.get_prompt()
        aimo._self_cognition = prompt_data["self_cognition"]
        aimo._guidelines = prompt_data["guidelines"]
        aimo._rules = prompt_data["rules"]
        aimo._overall_style = prompt_data["overall_style"]
        
        return {"message": "System prompt updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        raise HTTPException(status_code=404, detail=str(e))