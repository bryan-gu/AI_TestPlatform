from typing import Any
from pydantic import BaseModel
from datetime import datetime


class DocumentCreate(BaseModel):
    name: str
    file_type: str = ""
    sprint_id: int
    uploader_id: int | None = None


class DocumentUpdate(BaseModel):
    name: str | None = None
    version: str | None = None
    content_preview: str | None = None
    ai_summary: str | None = None
    keywords: list[Any] | None = None
    module_ids: list[int] | None = None
    ai_status: str | None = None


class DocumentOut(BaseModel):
    id: int
    name: str
    file_path: str = ""
    file_type: str = ""
    file_size: int = 0
    sprint_id: int
    uploader_id: int | None = None
    version: str = "v1.0"
    content_preview: str = ""
    ai_summary: str = ""
    keywords: list[Any] = []
    module_ids: list[int] = []
    ai_status: str = "待分析"
    parse_status: str = "待解析"
    created_at: datetime | None = None
    # computed
    uploader_name: str = ""
    module_names: list[str] = []

    class Config:
        from_attributes = True
