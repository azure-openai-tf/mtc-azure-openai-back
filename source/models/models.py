"""
@created_by ayaan
@created_at 2023.05.12
"""
from pydantic import BaseModel


class ChatbotQuery(BaseModel):
    """ChatbotQuery"""

    query: str
    messages: list = []
