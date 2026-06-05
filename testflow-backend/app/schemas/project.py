from pydantic import BaseModel
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    status: str = "pending"
    progress: int = 0
    owner_id: int | None = None
    case_prefix: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    progress: int | None = None
    owner_id: int | None = None
    case_prefix: str | None = None


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
