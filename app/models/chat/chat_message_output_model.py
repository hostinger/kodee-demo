from enum import StrEnum
from pydantic import BaseModel
from typing import Optional


class OutputRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class OutputChatbotLabel(StrEnum):
    DOMAIN_BOT = "domain_bot"
    OUT_OF_SCOPE_BOT = "out_of_scope_bot"
    SUPPORT_HANDOFF_BOT = "support_handoff_bot"


class ConversationMessages(BaseModel):
    role: OutputRole
    content: str

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class HandoffDetails(BaseModel):
    should_handoff: bool


class ConversationMessagesOutput(BaseModel):
    conversation_id: str
    message: ConversationMessages
    handoff: Optional[HandoffDetails] = None
