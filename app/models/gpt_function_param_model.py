from pydantic import BaseModel


class DefaultGPTFunctionParams(BaseModel):
    user_id: str
    conversation_id: str
