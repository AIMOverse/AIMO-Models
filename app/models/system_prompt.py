from pydantic import BaseModel
from typing import Optional

"""
Author: Wesley Xu
Date: 2025-6-20
Description:
    This module defines the models and structure of data used system prompts setting services
"""

class SystemPromptUpdate(BaseModel):
    """
    SystemPromptUpdate Model

    This model represents the structure for updating system prompts in the application.

    Attributes:
        section (str): The section of the system prompt to be updated.
        content (str): The new content for the system prompt.
        modified_by (Optional[str]): The user who modified the system prompt. Defaults to "Admin".
        purpose (str): The purpose of the update. Defaults to "Update system prompt".
    """
    section: str
    content: str
    modified_by: Optional[str] = "Admin"
    purpose: str = "Update system prompt"