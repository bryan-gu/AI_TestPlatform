from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ImportJobCreate(BaseModel):
    project_id: int
    root_path: str


class ImportJobOut(BaseModel):
    id: int
    project_id: int
    root_path: str
    job_type: str = "local_project"
    status: str = "pending"
    dry_run: bool = False
    total_files: int = 0
    processed_files: int = 0
    success_count: int = 0
    failed_count: int = 0
    result_summary: dict[str, Any] = Field(default_factory=dict)
    warnings: list = Field(default_factory=list)
    errors: list = Field(default_factory=list)
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
