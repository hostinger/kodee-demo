from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, field_validator
import re


class InputRole(StrEnum):
    USER = "user"


class InputChatbotLabel(StrEnum):
    CHATBOT = "chatbot"


class ChatbotLabel(StrEnum):
    DOMAIN = "domain"
    OUT_OF_SCOPE = "out_of_scope"


class ChatMessage(BaseModel):
    user_id: Optional[str] = None
    role: InputRole
    content: str
    chatbot_label: InputChatbotLabel

    @field_validator("content")
    def clean_whitespaces_and_validate_content(cls, value: str) -> str:
        cleaned_value = re.sub(r"\s+", " ", value.strip())

        if not cleaned_value:
            raise ValueError("Content must not be empty or whitespace")

        return cleaned_value

    def to_dict(self):
        return {"role": self.role, "content": self.content}
