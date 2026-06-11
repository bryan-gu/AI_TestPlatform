from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChangeItemCreate(BaseModel):
    project_id: int | None = None
    sprint_id: int
    source_doc_id: int | None = None
    source_asset_id: int | None = None
    module_id: int | None = None
    title: str
    description: str = ""
    change_type: str = "unknown"
    target_type: str = "feature"
    target_id: int | None = None
    priority: str = "中"
    impact_level: str = "中"
    status: str = "open"
    before_snapshot: dict[str, Any] = Field(default_factory=dict)
    after_snapshot: dict[str, Any] = Field(default_factory=dict)
    evidence: str = ""
    confidence: int = 80
    fingerprint: str = ""
    raw_data: dict[str, Any] = Field(default_factory=dict)


class ChangeItemUpdate(BaseModel):
    source_doc_id: int | None = None
    source_asset_id: int | None = None
    module_id: int | None = None
    title: str | None = None
    description: str | None = None
    change_type: str | None = None
    target_type: str | None = None
    target_id: int | None = None
    priority: str | None = None
    impact_level: str | None = None
    status: str | None = None
    before_snapshot: dict[str, Any] | None = None
    after_snapshot: dict[str, Any] | None = None
    evidence: str | None = None
    confidence: int | None = None
    raw_data: dict[str, Any] | None = None


class ChangeItemOut(BaseModel):
    id: int
    project_id: int | None = None
    sprint_id: int
    source_doc_id: int | None = None
    source_asset_id: int | None = None
    module_id: int | None = None
    title: str
    description: str = ""
    change_type: str = "unknown"
    target_type: str = "feature"
    target_id: int | None = None
    priority: str = "中"
    impact_level: str = "中"
    status: str = "open"
    before_snapshot: dict[str, Any] = Field(default_factory=dict)
    after_snapshot: dict[str, Any] = Field(default_factory=dict)
    evidence: str = ""
    confidence: int = 80
    fingerprint: str = ""
    raw_data: dict[str, Any] = Field(default_factory=dict)
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    project_name: str = ""
    sprint_name: str = ""
    source_doc_name: str = ""
    source_asset_name: str = ""
    module_name: str = ""
    target_name: str = ""

    class Config:
        from_attributes = True


class ChangeAnalyzeRequest(BaseModel):
    overwrite: bool = False
    baseline_sprint_id: int | None = None
    include_target_types: list[str] = Field(default_factory=lambda: ["feature", "api"])
    detect_removed: bool = False
    mode: str = "rule"


class ChangeAnalyzeResult(BaseModel):
    project_id: int | None = None
    sprint_id: int
    baseline_sprint_id: int | None = None
    baseline_type: str = "none"
    total: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    added: int = 0
    modified: int = 0
    removed: int = 0
    high_impact: int = 0
    impacted_testcases: int = 0
    graph_id: int | None = None
    node_count: int = 0
    edge_count: int = 0
    message: str = ""
