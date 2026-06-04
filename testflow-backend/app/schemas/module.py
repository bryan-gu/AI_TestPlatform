from pydantic import BaseModel
from datetime import datetime


class ModuleCreate(BaseModel):
    name: str
    project_id: int | None = None
    color: str = ""


class ModuleUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class ModuleOut(BaseModel):
    id: int
    name: str
    project_id: int | None = None
    color: str = ""
    created_at: datetime | None = None
    # computed
    doc_count: int = 0

    class Config:
        from_attributes = True
