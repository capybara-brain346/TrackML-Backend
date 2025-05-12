from typing import TypeVar, Generic, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseApiResponse(BaseModel):
    success: bool
    message: str
    statusCode: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseApiResponse, Generic[T]):
    data: T
    metadata: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseApiResponse):
    error: Optional[str] = None


class ApiResponseHandler:
    @staticmethod
    def success(
        data: Any,
        message: str = "Success",
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        response = SuccessResponse(
            success=True,
            message=message,
            statusCode=status_code,
            data=data,
            metadata=metadata,
        )
        return response.model_dump()

    @staticmethod
    def error(
        message: str = "Error occurred",
        status_code: int = 500,
        error: Optional[str] = None,
    ) -> Dict:
        response = ErrorResponse(
            success=False, message=message, statusCode=status_code, error=error
        )
        return response.model_dump()
