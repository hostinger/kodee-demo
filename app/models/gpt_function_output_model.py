from typing import Optional, Dict
from pydantic import BaseModel
from enum import Enum


class OutputStatus(str, Enum):
    EXIT = "exit"
    SUCCESS = "success"


class GPTFunctionOutput(BaseModel):
    status: OutputStatus
    message: str
    data: Optional[Dict] = None

    class Config:
        use_enum_values = True

    def __str__(self):
        return self.model_dump_json()

    def to_dict(self):
        return self.model_dump()
