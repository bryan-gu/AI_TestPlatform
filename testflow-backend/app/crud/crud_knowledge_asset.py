import hashlib
import os

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.knowledge_asset import KnowledgeAsset
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.document import Document
from app.models.module import Module
from app.models.user import User
from app.schemas.knowledge_asset import KnowledgeAssetCreate, KnowledgeAssetUpdate


ASSET_TYPE_LABELS = {
    "requirement_doc": "需求文档",
    "meeting_note": "会议纪要",
    "feature_spec": "功能点规格",
    "test_case_json": "测试用例 JSON",
    "test_case_excel": "测试用例 Excel",
    "api_doc_md": "接口 Markdown",
    "api_doc_openapi": "OpenAPI 文档",
    "test_script": "自动化脚本",
    "selector_map": "选择器文件",
    "execution_report": "执行报告",
    "screenshot": "截图",
    "other": "其他",
}


def infer_asset_type(file_name: str = "", file_type: str = "", *, source_kind: str = "uploaded") -> str:
    ext = os.path.splitext(file_name or "")[1].lower()
    lower_name = (file_name or "").lower()

    if source_kind == "ai_generated" and "功能点" in file_name:
        return "feature_spec"
    if source_kind == "ai_generated" and "测试用例" in file_name and file_type == "JSON":
        return "test_case_json"
    if source_kind == "ai_generated" and "测试用例" in file_name and file_type == "Excel":
        return "test_case_excel"

    if ext in (".pdf", ".doc", ".docx", ".md"):
        if "api" in lower_name or "接口" in file_name:
            return "api_doc_md"
        if "会议" in file_name:
            return "meeting_note"
        return "requirement_doc"
    if ext in (".xlsx", ".xls"):
        return "test_case_excel"
    if ext == ".json":
        if "openapi" in lower_name or "swagger" in lower_name:
            return "api_doc_openapi"
        return "test_case_json"
    if ext in (".ts", ".js", ".spec.ts"):
        return "test_script"
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        return "screenshot"
    return "other"


def calculate_file_hash(file_path: str) -> str:
    if not file_path or not os.path.exists(file_path):
        return ""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def get_assets(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    asset_type: str | None = None,
    module_id: int | None = None,
    keyword: str | None = None,
    status: str | None = None,
) -> list[KnowledgeAsset]:
    query = db.query(KnowledgeAsset)
    if project_id:
        query = query.filter(KnowledgeAsset.project_id == project_id)
    if sprint_id:
        query = query.filter(KnowledgeAsset.sprint_id == sprint_id)
    if asset_type:
        query = query.filter(KnowledgeAsset.asset_type == asset_type)
    if module_id:
        query = query.filter(KnowledgeAsset.module_id == module_id)
    if status:
        query = query.filter(KnowledgeAsset.status == status)
    if keyword:
        query = query.filter(
            or_(
                KnowledgeAsset.name.ilike(f"%{keyword}%"),
                KnowledgeAsset.file_type.ilike(f"%{keyword}%"),
                KnowledgeAsset.file_path.ilike(f"%{keyword}%"),
            )
        )
    return query.order_by(KnowledgeAsset.updated_at.desc(), KnowledgeAsset.created_at.desc()).all()


def get_asset(db: Session, asset_id: int) -> KnowledgeAsset | None:
    return db.query(KnowledgeAsset).filter(KnowledgeAsset.id == asset_id).first()


def get_asset_by_document(db: Session, document_id: int) -> KnowledgeAsset | None:
    return db.query(KnowledgeAsset).filter(KnowledgeAsset.document_id == document_id).first()


def create_asset(db: Session, data: KnowledgeAssetCreate) -> KnowledgeAsset:
    asset = KnowledgeAsset(
        project_id=data.project_id,
        sprint_id=data.sprint_id,
        document_id=data.document_id,
        name=data.name,
        asset_type=data.asset_type,
        source_kind=data.source_kind,
        file_path=data.file_path,
        file_type=data.file_type,
        file_size=data.file_size,
        module_id=data.module_id,
        version=data.version,
        status=data.status,
        parse_status=data.parse_status,
        content_hash=data.content_hash,
        asset_metadata=data.metadata,
        created_by=data.created_by,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(db: Session, asset: KnowledgeAsset, data: KnowledgeAssetUpdate) -> KnowledgeAsset:
    if data.name is not None:
        asset.name = data.name
    if data.asset_type is not None:
        asset.asset_type = data.asset_type
    if data.source_kind is not None:
        asset.source_kind = data.source_kind
    if data.file_path is not None:
        asset.file_path = data.file_path
    if data.file_type is not None:
        asset.file_type = data.file_type
    if data.file_size is not None:
        asset.file_size = data.file_size
    if data.module_id is not None:
        asset.module_id = data.module_id
    if data.version is not None:
        asset.version = data.version
    if data.status is not None:
        asset.status = data.status
    if data.parse_status is not None:
        asset.parse_status = data.parse_status
    if data.content_hash is not None:
        asset.content_hash = data.content_hash
    if data.metadata is not None:
        asset.asset_metadata = data.metadata
    db.commit()
    db.refresh(asset)
    return asset


def upsert_asset_for_document(
    db: Session,
    document: Document,
    *,
    project_id: int | None = None,
    source_kind: str = "uploaded",
    asset_type: str | None = None,
    module_id: int | None = None,
    metadata: dict | None = None,
) -> KnowledgeAsset:
    sprint = db.query(Sprint).filter(Sprint.id == document.sprint_id).first() if document.sprint_id else None
    resolved_project_id = project_id if project_id is not None else (sprint.project_id if sprint else None)
    resolved_asset_type = asset_type or infer_asset_type(document.name, document.file_type, source_kind=source_kind)
    content_hash = calculate_file_hash(document.file_path)
    existing = get_asset_by_document(db, document.id)

    if existing:
        existing.project_id = resolved_project_id
        existing.sprint_id = document.sprint_id
        existing.name = document.name
        existing.asset_type = resolved_asset_type
        existing.source_kind = source_kind
        existing.file_path = document.file_path or ""
        existing.file_type = document.file_type or ""
        existing.file_size = document.file_size or 0
        existing.module_id = module_id
        existing.version = document.version or "v1.0"
        existing.status = "active"
        existing.parse_status = document.parse_status or "pending"
        existing.content_hash = content_hash
        existing.asset_metadata = metadata or existing.asset_metadata or {}
        existing.created_by = document.uploader_id
        db.commit()
        db.refresh(existing)
        return existing

    return create_asset(db, KnowledgeAssetCreate(
        project_id=resolved_project_id,
        sprint_id=document.sprint_id,
        document_id=document.id,
        name=document.name,
        asset_type=resolved_asset_type,
        source_kind=source_kind,
        file_path=document.file_path or "",
        file_type=document.file_type or "",
        file_size=document.file_size or 0,
        module_id=module_id,
        version=document.version or "v1.0",
        status="active",
        parse_status=document.parse_status or "pending",
        content_hash=content_hash,
        metadata=metadata or {},
        created_by=document.uploader_id,
    ))


def mark_document_asset_deleted(db: Session, document_id: int) -> None:
    asset = get_asset_by_document(db, document_id)
    if asset:
        asset.status = "deleted"
        db.commit()


def delete_asset(db: Session, asset: KnowledgeAsset) -> None:
    db.delete(asset)
    db.commit()


def get_project_name(db: Session, project_id: int | None) -> str:
    if not project_id:
        return ""
    project = db.query(Project).filter(Project.id == project_id).first()
    return project.name if project else ""


def get_sprint_name(db: Session, sprint_id: int | None) -> str:
    if not sprint_id:
        return ""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    return sprint.name if sprint else ""


def get_document_name(db: Session, document_id: int | None) -> str:
    if not document_id:
        return ""
    document = db.query(Document).filter(Document.id == document_id).first()
    return document.name if document else ""


def get_module_name(db: Session, module_id: int | None) -> str:
    if not module_id:
        return ""
    module = db.query(Module).filter(Module.id == module_id).first()
    return module.name if module else ""


def get_creator_name(db: Session, user_id: int | None) -> str:
    if not user_id:
        return ""
    user = db.query(User).filter(User.id == user_id).first()
    return user.name if user else ""
