from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TraceLinkCreate(BaseModel):
    project_id: int | None = None
    sprint_id: int | None = None
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    relation_type: str
    confidence: int = 100
    evidence: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str = "active"
    created_by: str = "system"


class TraceLinkUpdate(BaseModel):
    project_id: int | None = None
    sprint_id: int | None = None
    confidence: int | None = None
    evidence: str | None = None
    metadata: dict[str, Any] | None = None
    status: str | None = None
    created_by: str | None = None


class TraceLinkOut(BaseModel):
    id: int
    project_id: int | None = None
    sprint_id: int | None = None
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    relation_type: str
    confidence: int = 100
    evidence: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str = "active"
    created_by: str = "system"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    source_name: str = ""
    target_name: str = ""
    relation_label: str = ""

    class Config:
        from_attributes = True
