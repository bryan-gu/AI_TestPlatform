from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role_id: int | None = None
    project: str = ""
    status: str = "活跃"


class UserUpdate(BaseModel):
    name: str | None = None
    role_id: int | None = None
    project: str | None = None
    status: str | None = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role_id: int | None = None
    role_name: str = ""
    project: str = ""
    status: str = "活跃"
    last_login: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    totalUsers: int = 0
    newUsers: int = 0
    activeUsers: int = 0
    onlineToday: int = 0
    disabledUsers: int = 0
    pendingUsers: int = 0
