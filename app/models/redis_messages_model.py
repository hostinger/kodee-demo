from typing import Optional, List, Dict, Union
from pydantic import BaseModel, model_validator
from models.chat.chat_message_input_model import InputRole
from models.chat.chat_message_output_model import OutputRole


class RedisMessages(BaseModel):
    role: Union[OutputRole, InputRole]
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    content: Optional[str] = None

    @model_validator(mode="after")
    def check_content_and_tool_calls(cls, values):
        if not values.content and not values.tool_calls:
            raise ValueError("Either content or tool_calls must be provided to RedisMessages.")
        return values

    def to_dict(self):
        return {
            "role": self.role,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id,
            "content": self.content,
        }
