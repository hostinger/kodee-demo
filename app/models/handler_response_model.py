from typing import Optional
from pydantic import BaseModel
from enum import Enum
from models.chat.chat_message_output_model import OutputChatbotLabel


class HandlerResponseStatus(str, Enum):
    SUCCESS = "success"
    SUPPORT_HANDOFF = "support_handoff"


class HandlerResponse(BaseModel):
    status: HandlerResponseStatus
    message: str
    chatbot_label: Optional[OutputChatbotLabel] = None

    def to_dict(self):
        response_dict = self.dict(exclude_none=True)
        filtered_dict = {k: v for k, v in response_dict.items() if v != []}
        return filtered_dict
