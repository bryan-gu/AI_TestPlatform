from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.knowledge import KnowledgeBase, Folder, Document
from app.models.project import Project
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate,
    FolderCreate, FolderUpdate,
    DocumentUpdate,
)


# ========== 知识库 ==========
def get_knowledge_bases(db: Session, keyword: str | None = None) -> list[KnowledgeBase]:
    query = db.query(KnowledgeBase)
    if keyword:
        query = query.filter(
            or_(
                KnowledgeBase.name.ilike(f"%{keyword}%"),
                KnowledgeBase.description.ilike(f"%{keyword}%")
            )
        )
    return query.all()


def get_knowledge_base(db: Session, kb_id: int) -> KnowledgeBase | None:
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()


def create_knowledge_base(db: Session, data: KnowledgeBaseCreate, creator_id: int) -> KnowledgeBase:
    kb = KnowledgeBase(
        name=data.name,
        description=data.description,
        project_id=data.project_id,
        creator_id=creator_id,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


def update_knowledge_base(db: Session, kb: KnowledgeBase, data: KnowledgeBaseUpdate) -> KnowledgeBase:
    if data.name is not None:
        kb.name = data.name
    if data.description is not None:
        kb.description = data.description
    if data.project_id is not None:
        kb.project_id = data.project_id
    db.commit()
    db.refresh(kb)
    return kb


def delete_knowledge_base(db: Session, kb: KnowledgeBase) -> None:
    db.delete(kb)
    db.commit()


def get_knowledge_stats(db: Session) -> dict:
    total_bases = db.query(KnowledgeBase).count()
    total_docs = db.query(Document).count()
    return {"totalBases": total_bases, "totalDocs": total_docs, "newDocs": 0}


# ========== 文件夹 ==========
def get_folders(db: Session, kb_id: int) -> list[Folder]:
    return db.query(Folder).filter(Folder.knowledge_base_id == kb_id).all()


def get_folder(db: Session, folder_id: int) -> Folder | None:
    return db.query(Folder).filter(Folder.id == folder_id).first()


def create_folder(db: Session, kb_id: int, data: FolderCreate) -> Folder:
    folder = Folder(name=data.name, knowledge_base_id=kb_id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


def update_folder(db: Session, folder: Folder, data: FolderUpdate) -> Folder:
    if data.name is not None:
        folder.name = data.name
    db.commit()
    db.refresh(folder)
    return folder


def delete_folder(db: Session, folder: Folder) -> None:
    db.delete(folder)
    db.commit()


# ========== 文档 ==========
def get_documents(db: Session, folder_id: int) -> list[Document]:
    return db.query(Document).filter(Document.folder_id == folder_id).all()


def get_document(db: Session, doc_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == doc_id).first()


def create_document(db: Session, folder_id: int, name: str, file_path: str, file_type: str, file_size: int, uploader_id: int) -> Document:
    doc = Document(
        name=name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        folder_id=folder_id,
        uploader_id=uploader_id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_document(db: Session, doc: Document, data: DocumentUpdate) -> Document:
    if data.name is not None:
        doc.name = data.name
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc: Document) -> None:
    db.delete(doc)
    db.commit()


# ========== 辅助函数 ==========
def get_project_name(db: Session, project_id: int | None) -> str:
    if not project_id:
        return ""
    proj = db.query(Project).filter(Project.id == project_id).first()
    return proj.name if proj else ""


def get_user_name(db: Session, user_id: int | None) -> str:
    if not user_id:
        return ""
    user = db.query(User).filter(User.id == user_id).first()
    return user.name if user else ""


def get_doc_count_for_kb(db: Session, kb_id: int) -> int:
    folders = db.query(Folder).filter(Folder.knowledge_base_id == kb_id).all()
    if not folders:
        return 0
    folder_ids = [f.id for f in folders]
    return db.query(Document).filter(Document.folder_id.in_(folder_ids)).count()


def get_doc_count_for_folder(db: Session, folder_id: int) -> int:
    return db.query(Document).filter(Document.folder_id == folder_id).count()
