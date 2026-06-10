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
