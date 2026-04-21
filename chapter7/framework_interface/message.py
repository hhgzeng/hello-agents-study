"""message system"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

# define message role type, limit it's value
MessageRole = Literal["user", "assistant", "system", "tool"]


class Message(BaseModel):
    """message class"""

    content: str
    role: MessageRole
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, content: str, role: MessageRole, **kwargs):
        super().__init__(
            content=content,
            role=role,
            timestamp=kwargs.get("timestmap", datetime.now()),
            metadata=kwargs.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """transform dictionary type (OpenAI API format)"""
        return {
            "role": self.role,
            "content": self.content
        }

    def __str__(self) -> str:
        return f"[{self.role}] {self.content}"
        