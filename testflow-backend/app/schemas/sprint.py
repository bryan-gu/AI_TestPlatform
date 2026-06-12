from pydantic import BaseModel
from datetime import datetime


class SprintCreate(BaseModel):
    name: str
    description: str = ""
    project_id: int | None = None
    status: str = "待启动"
    is_all: bool = False


class SprintUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    is_all: bool | None = None


class SprintPrepareFromAllRequest(BaseModel):
    update_existing: bool = False


class SprintMergeToAllRequest(BaseModel):
    change_item_ids: list[int] = []
    statuses: list[str] = ["confirmed", "resolved"]
    target_types: list[str] = ["feature", "api"]
    dry_run: bool = False


class SprintOut(BaseModel):
    id: int
    name: str
    description: str = ""
    project_id: int | None = None
    status: str = "待启动"
    is_all: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # computed
    project_name: str = ""
    doc_count: int = 0
    module_count: int = 0

    class Config:
        from_attributes = True
