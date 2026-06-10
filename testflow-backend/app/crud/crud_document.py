from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.module import Module
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate


def get_documents(db: Session, sprint_id: int) -> list[Document]:
    return db.query(Document).filter(
        Document.sprint_id == sprint_id,
        Document.is_deleted == False,  # noqa: E712
    ).order_by(Document.created_at.desc()).all()


def get_document(db: Session, doc_id: int) -> Document | None:
    return db.query(Document).filter(
        Document.id == doc_id,
        Document.is_deleted == False,  # noqa: E712
    ).first()


def create_document(db: Session, data: DocumentCreate) -> Document:
    doc = Document(
        name=data.name,
        file_type=data.file_type,
        sprint_id=data.sprint_id,
        uploader_id=data.uploader_id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_document(db: Session, doc: Document, data: DocumentUpdate) -> Document:
    if data.name is not None:
        doc.name = data.name
    if data.version is not None:
        doc.version = data.version
    if data.content_preview is not None:
        doc.content_preview = data.content_preview
    if data.ai_summary is not None:
        doc.ai_summary = data.ai_summary
    if data.keywords is not None:
        doc.keywords = data.keywords
    if data.module_ids is not None:
        doc.module_ids = data.module_ids
    if data.ai_status is not None:
        doc.ai_status = data.ai_status
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc: Document) -> None:
    from datetime import datetime
    doc.is_deleted = True
    doc.deleted_at = datetime.utcnow()
    db.commit()


def get_uploader_name(db: Session, uploader_id: int | None) -> str:
    if not uploader_id:
        return ""
    user = db.query(User).filter(User.id == uploader_id).first()
    return user.name if user else ""


def get_module_names(db: Session, module_ids: list[int] | None) -> list[str]:
    if not module_ids:
        return []
    modules = db.query(Module).filter(Module.id.in_(module_ids)).all()
    return [m.name for m in modules]
