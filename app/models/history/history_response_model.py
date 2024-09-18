from enum import StrEnum
from typing import TypeVar, Optional, Dict
from pydantic import BaseModel

DataType = TypeVar("DataType")


class HistoryResponseStatusCode(StrEnum):
    SUCCESS = "success"
    ERROR = "error"


class HistoryAPIResponse(BaseModel):
    status: HistoryResponseStatusCode
    data: Optional[DataType] = None
    error_message: Optional[str] = None

    def convert_to_success_response(self) -> Dict:
        return {
            "status": self.status,
            "data": self.data,
        }

    def convert_to_error_response(self) -> Dict:
        return {
            "status": self.status,
            "error_message": self.error_message,
        }
