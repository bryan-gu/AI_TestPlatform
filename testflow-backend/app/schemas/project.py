from pydantic import BaseModel, field_validator
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    status: str = "pending"
    progress: int = 0
    owner_id: int | None = None
    case_prefix: str

    @field_validator('case_prefix')
    @classmethod
    def validate_prefix(cls, v):
        if not v or not v.strip():
            raise ValueError('用例前缀不能为空')
        v = v.strip().upper()
        if not v.isalnum():
            raise ValueError('用例前缀只能包含英文字母和数字')
        return v


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    progress: int | None = None
    owner_id: int | None = None
    case_prefix: str | None = None

    @field_validator('case_prefix')
    @classmethod
    def validate_prefix(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('用例前缀不能为空')
            v = v.strip().upper()
            if not v.isalnum():
                raise ValueError('用例前缀只能包含英文字母和数字')
        return v


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str = ""
    status: str = "pending"
    progress: int = 0
    owner_id: int | None = None
    owner: str = ""  # 负责人姓名
    case_prefix: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
