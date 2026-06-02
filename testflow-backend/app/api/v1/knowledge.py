import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseOut,
    FolderCreate, FolderUpdate, FolderOut,
    DocumentUpdate, DocumentOut,
)
from app.crud import crud_knowledge

router = APIRouter(prefix="/knowledge", tags=["知识库"])


def _kb_to_out(kb, db: Session) -> dict:
    return KnowledgeBaseOut(
        id=kb.id, name=kb.name, description=kb.description or "",
        project=crud_knowledge.get_project_name(db, kb.project_id),
        project_id=kb.project_id,
        creator=crud_knowledge.get_user_name(db, kb.creator_id),
        creator_id=kb.creator_id,
        doc_count=crud_knowledge.get_doc_count_for_kb(db, kb.id),
        created_at=kb.created_at,
    ).model_dump()


def _folder_to_out(folder, db: Session) -> dict:
    return FolderOut(
        id=folder.id, name=folder.name,
        doc_count=crud_knowledge.get_doc_count_for_folder(db, folder.id),
        created_at=folder.created_at,
    ).model_dump()


def _doc_to_out(doc, db: Session) -> dict:
    return DocumentOut(
        id=doc.id, name=doc.name, file_type=doc.file_type,
        file_size=doc.file_size,
        uploader=crud_knowledge.get_user_name(db, doc.uploader_id),
        uploader_id=doc.uploader_id,
        created_at=doc.created_at,
    ).model_dump()


# ========== 知识库 ==========
@router.get("", response_model=ResponseModel)
def list_knowledge_bases(
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    kbs = crud_knowledge.get_knowledge_bases(db, keyword=keyword)
    return ResponseModel(data=[_kb_to_out(kb, db) for kb in kbs])


@router.get("/stats", response_model=ResponseModel)
def knowledge_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ResponseModel(data=crud_knowledge.get_knowledge_stats(db))


@router.get("/{kb_id}", response_model=ResponseModel)
def get_knowledge_base(kb_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    kb = crud_knowledge.get_knowledge_base(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return ResponseModel(data=_kb_to_out(kb, db))


@router.post("", response_model=ResponseModel)
def create_knowledge_base(data: KnowledgeBaseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    kb = crud_knowledge.create_knowledge_base(db, data, creator_id=user.id)
    return ResponseModel(data=_kb_to_out(kb, db))


@router.put("/{kb_id}", response_model=ResponseModel)
def update_knowledge_base(kb_id: int, data: KnowledgeBaseUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    kb = crud_knowledge.get_knowledge_base(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    kb = crud_knowledge.update_knowledge_base(db, kb, data)
    return ResponseModel(data=_kb_to_out(kb, db))


@router.delete("/{kb_id}", response_model=ResponseModel)
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    kb = crud_knowledge.get_knowledge_base(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    crud_knowledge.delete_knowledge_base(db, kb)
    return ResponseModel(message="删除成功")


# ========== 文件夹 ==========
@router.get("/{kb_id}/folders", response_model=ResponseModel)
def list_folders(kb_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    folders = crud_knowledge.get_folders(db, kb_id)
    return ResponseModel(data=[_folder_to_out(f, db) for f in folders])


@router.post("/{kb_id}/folders", response_model=ResponseModel)
def create_folder(kb_id: int, data: FolderCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    folder = crud_knowledge.create_folder(db, kb_id, data)
    return ResponseModel(data=_folder_to_out(folder, db))


@router.put("/{kb_id}/folders/{folder_id}", response_model=ResponseModel)
def update_folder(kb_id: int, folder_id: int, data: FolderUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    folder = crud_knowledge.get_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="文件夹不存在")
    folder = crud_knowledge.update_folder(db, folder, data)
    return ResponseModel(data=_folder_to_out(folder, db))


@router.delete("/{kb_id}/folders/{folder_id}", response_model=ResponseModel)
def delete_folder(kb_id: int, folder_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    folder = crud_knowledge.get_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="文件夹不存在")
    crud_knowledge.delete_folder(db, folder)
    return ResponseModel(message="删除成功")


# ========== 文档 ==========
@router.get("/{kb_id}/folders/{folder_id}/documents", response_model=ResponseModel)
def list_documents(kb_id: int, folder_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    docs = crud_knowledge.get_documents(db, folder_id)
    return ResponseModel(data=[_doc_to_out(d, db) for d in docs])


@router.post("/{kb_id}/folders/{folder_id}/documents", response_model=ResponseModel)
async def upload_document(
    kb_id: int, folder_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 确定文件类型
    ext = os.path.splitext(file.filename or "")[1].lower()
    type_map = {".pdf": "PDF", ".doc": "Word", ".docx": "Word", ".md": "Markdown", ".xlsx": "Excel", ".xls": "Excel"}
    file_type = type_map.get(ext, "其他")

    # 保存文件
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    doc = crud_knowledge.create_document(
        db, folder_id=folder_id,
        name=file.filename or filename,
        file_path=file_path,
        file_type=file_type,
        file_size=len(content),
        uploader_id=user.id,
    )
    return ResponseModel(data=_doc_to_out(doc, db))


@router.put("/{kb_id}/folders/{folder_id}/documents/{doc_id}", response_model=ResponseModel)
def update_document(kb_id: int, folder_id: int, doc_id: int, data: DocumentUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doc = crud_knowledge.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    doc = crud_knowledge.update_document(db, doc, data)
    return ResponseModel(data=_doc_to_out(doc, db))


@router.delete("/{kb_id}/folders/{folder_id}/documents/{doc_id}", response_model=ResponseModel)
def delete_document(kb_id: int, folder_id: int, doc_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doc = crud_knowledge.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    crud_knowledge.delete_document(db, doc)
    return ResponseModel(message="删除成功")
