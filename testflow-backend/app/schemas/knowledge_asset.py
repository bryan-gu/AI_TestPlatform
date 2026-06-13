from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime


class KnowledgeAssetCreate(BaseModel):
    project_id: int | None = None
    sprint_id: int | None = None
    document_id: int | None = None
    name: str
    asset_type: str = "other"
    source_kind: str = "uploaded"
    file_path: str = ""
    file_type: str = ""
    file_size: int = 0
    module_id: int | None = None
    version: str = "v1.0"
    status: str = "active"
    parse_status: str = "pending"
    content_hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_by: int | None = None


class KnowledgeAssetUpdate(BaseModel):
    name: str | None = None
    asset_type: str | None = None
    source_kind: str | None = None
    file_path: str | None = None
    file_type: str | None = None
    file_size: int | None = None
    module_id: int | None = None
    version: str | None = None
    status: str | None = None
    parse_status: str | None = None
    content_hash: str | None = None
    metadata: dict[str, Any] | None = None


class KnowledgeAssetOut(BaseModel):
    id: int
    project_id: int | None = None
    sprint_id: int | None = None
    document_id: int | None = None
    name: str
    asset_type: str = "other"
    source_kind: str = "uploaded"
    file_path: str = ""
    file_type: str = ""
    file_size: int = 0
    module_id: int | None = None
    version: str = "v1.0"
    status: str = "active"
    parse_status: str = "pending"
    content_hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    project_name: str = ""
    sprint_name: str = ""
    document_name: str = ""
    module_name: str = ""
    creator_name: str = ""

    class Config:
        from_attributes = True


# ========== 本地项目导入 ==========

class LocalProjectImportRequest(BaseModel):
    root_path: str
    project_id: int
    dry_run: bool = False


class LocalProjectImportAssetPreview(BaseModel):
    rel_path: str
    name: str
    asset_type: str
    file_type: str = ""
    file_size: int = 0
    sprint_name: str = ""
    module_hint: str = ""


class LocalProjectImportSprintPreview(BaseModel):
    name: str
    asset_count: int = 0


class LocalProjectImportResult(BaseModel):
    root_path: str
    project_id: int
    dry_run: bool = False
    sprints: list[LocalProjectImportSprintPreview] = Field(default_factory=list)
    assets: list[LocalProjectImportAssetPreview] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    # 正式导入后的统计
    imported: dict[str, int] = Field(default_factory=dict)
    graph: dict = Field(default_factory=dict)

