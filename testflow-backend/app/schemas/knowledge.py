from pydantic import BaseModel
from datetime import datetime


# ========== 知识库 ==========
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ""
    project_id: int | None = None


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    project_id: int | None = None


class KnowledgeBaseOut(BaseModel):
    id: int
    name: str
    description: str = ""
    project: str = ""  # 项目名称
    project_id: int | None = None
    creator: str = ""  # 创建人姓名
    creator_id: int | None = None
    doc_count: int = 0
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class KnowledgeStats(BaseModel):
    totalBases: int = 0
    totalDocs: int = 0
    newDocs: int = 0


# ========== 文件夹 ==========
class FolderCreate(BaseModel):
    name: str


class FolderUpdate(BaseModel):
    name: str | None = None


class FolderOut(BaseModel):
    id: int
    name: str
    doc_count: int = 0
    created_at: datetime | None = None

    class Config:
        from_attributes = True


# ========== 文档 ==========
class DocumentUpdate(BaseModel):
    name: str | None = None


class DocumentOut(BaseModel):
    id: int
    name: str
    file_type: str = ""
    file_size: int = 0
    uploader: str = ""  # 上传人姓名
    uploader_id: int | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
