from typing import Any, Optional
from pydantic import BaseModel


class ResponseModel(BaseModel):
    """统一响应格式"""
    code: int = 200
    data: Any = None
    message: Optional[str] = None


class TokenResponse(BaseModel):
    token: str
