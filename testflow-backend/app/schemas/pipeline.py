from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


# ── Create ──

class PipelineCreate(BaseModel):
    project_id: int | None = None
    sprint_id: int | None = None
    mode: str = "full"  # full / incremental


# ── Stage Out ──

class PipelineStageOut(BaseModel):
    id: int
    execution_id: int
    stage_no: int
    stage_name: str
    status: str  # waiting/running/completed/failed
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int | None = None
    result_summary: Any = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    # 计算字段：格式化耗时
    duration_display: str = ""

    class Config:
        from_attributes = True


# ── Execution Out ──

class PipelineOut(BaseModel):
    id: int
    project_id: int | None = None
    sprint_id: int | None = None
    mode: str = "full"
    status: str = "waiting"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_duration_ms: int | None = None
    created_at: datetime | None = None
    # 计算字段
    project_name: str = ""
    sprint_name: str = ""
    sprint_deleted: bool = False
    project_deleted: bool = False
    duration_display: str = ""

    class Config:
        from_attributes = True


# ── Detail (含 stages) ──

class PipelineDetailOut(PipelineOut):
    stages: list[PipelineStageOut] = []
