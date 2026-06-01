from pydantic import BaseModel
from datetime import datetime


class RoleCreate(BaseModel):
    name: str
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    permissions: list[str] | None = None


class RoleOut(BaseModel):
    id: int
    name: str
    type: str = "自定义"
    permissions: list[str] = []
    is_editable: bool = True
    member_count: int = 0
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class RoleStats(BaseModel):
    totalRoles: int = 0
    builtInRoles: int = 0
    totalPermissions: int = 0
