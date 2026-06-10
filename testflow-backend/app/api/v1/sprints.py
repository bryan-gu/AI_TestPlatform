import os
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.schemas.common import ResponseModel
from app.schemas.sprint import SprintCreate, SprintUpdate, SprintOut
from app.schemas.document import DocumentUpdate, DocumentOut
from app.crud import crud_sprint, crud_document, crud_knowledge_asset


router = APIRouter(prefix="/sprints", tags=["Sprint 管理"])


def _sprint_to_out(sprint, db: Session) -> dict:
    docs = db.query(Document).filter(Document.sprint_id == sprint.id).all()
    all_module_ids = set()
    for d in docs:
        if d.module_ids:
            all_module_ids.update(d.module_ids)

    return SprintOut(
        id=sprint.id,
        name=sprint.name,
        description=sprint.description or "",
        project_id=sprint.project_id,
        status=sprint.status,
        is_all=sprint.is_all,
        created_at=sprint.created_at,
        updated_at=sprint.updated_at,
        project_name=crud_sprint.get_project_name(db, sprint.project_id),
        doc_count=len(docs),
        module_count=len(all_module_ids),
    ).model_dump()


def _doc_to_out(doc, db: Session) -> dict:
    return DocumentOut(
        id=doc.id,
        name=doc.name,
        file_path=doc.file_path or "",
        file_type=doc.file_type or "",
        file_size=doc.file_size or 0,
        sprint_id=doc.sprint_id,
        uploader_id=doc.uploader_id,
        version=doc.version or "v1.0",
        content_preview=doc.content_preview or "",
        ai_summary=doc.ai_summary or "",
        keywords=doc.keywords or [],
        module_ids=doc.module_ids or [],
        ai_status=doc.ai_status or "待分析",
        parse_status=doc.parse_status or "待解析",
        created_at=doc.created_at,
        uploader_name=crud_document.get_uploader_name(db, doc.uploader_id),
        module_names=crud_document.get_module_names(db, doc.module_ids),
    ).model_dump()


# ========== Sprint CRUD ==========

@router.get("", response_model=ResponseModel)
def list_sprints(
    project_id: int | None = Query(None, description="项目ID"),
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    sprints = crud_sprint.get_sprints(db, project_id=project_id, keyword=keyword)
    return ResponseModel(data=[_sprint_to_out(s, db) for s in sprints])


@router.get("/stats", response_model=ResponseModel)
def sprint_stats(
    project_id: int | None = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    stats = crud_sprint.get_sprint_stats(db, project_id=project_id)
    return ResponseModel(data=stats)


@router.get("/{sprint_id}", response_model=ResponseModel)
def get_sprint(sprint_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    return ResponseModel(data=_sprint_to_out(sprint, db))


@router.post("", response_model=ResponseModel)
def create_sprint(data: SprintCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.create_sprint(db, data)
    return ResponseModel(data=_sprint_to_out(sprint, db))


@router.put("/{sprint_id}", response_model=ResponseModel)
def update_sprint(sprint_id: int, data: SprintUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    sprint = crud_sprint.update_sprint(db, sprint, data)
    return ResponseModel(data=_sprint_to_out(sprint, db))


@router.delete("/{sprint_id}", response_model=ResponseModel)
def delete_sprint(sprint_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    crud_sprint.delete_sprint(db, sprint)
    return ResponseModel(message="删除成功")


# ========== Sprint 下文档 ==========

@router.get("/{sprint_id}/documents", response_model=ResponseModel)
def list_documents(sprint_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    docs = crud_document.get_documents(db, sprint_id)
    return ResponseModel(data=[_doc_to_out(d, db) for d in docs])


@router.post("/{sprint_id}/documents", response_model=ResponseModel)
async def upload_document(
    sprint_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")

    # 确定文件类型
    ext = os.path.splitext(file.filename or "")[1].lower()
    type_map = {
        ".pdf": "PDF", ".doc": "Word", ".docx": "Word",
        ".md": "Markdown", ".xlsx": "Excel", ".xls": "Excel",
    }
    file_type = type_map.get(ext, "其他")

    # 保存文件
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 入库
    from app.schemas.document import DocumentCreate
    doc_data = DocumentCreate(
        name=file.filename or filename,
        file_type=file_type,
        sprint_id=sprint_id,
        uploader_id=user.id,
    )
    doc = crud_document.create_document(db, doc_data)
    # 补充 file_path 和 file_size
    doc.file_path = file_path
    doc.file_size = len(content)
    db.commit()
    db.refresh(doc)
    crud_knowledge_asset.upsert_asset_for_document(db, doc, source_kind="uploaded")

    # 触发后台 MinerU 文档解析
    from app.services.document_parser import DocumentParser
    parser = DocumentParser()
    background_tasks.add_task(parser.parse_document, None, doc.id)

    return ResponseModel(data=_doc_to_out(doc, db))


@router.put("/{sprint_id}/documents/{doc_id}", response_model=ResponseModel)
def update_document(sprint_id: int, doc_id: int, data: DocumentUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doc = crud_document.get_document(db, doc_id)
    if not doc or doc.sprint_id != sprint_id:
        raise HTTPException(status_code=404, detail="文档不存在")
    doc = crud_document.update_document(db, doc, data)
    crud_knowledge_asset.upsert_asset_for_document(db, doc, source_kind="uploaded")
    return ResponseModel(data=_doc_to_out(doc, db))


@router.delete("/{sprint_id}/documents/{doc_id}", response_model=ResponseModel)
def delete_document(sprint_id: int, doc_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doc = crud_document.get_document(db, doc_id)
    if not doc or doc.sprint_id != sprint_id:
        raise HTTPException(status_code=404, detail="文档不存在")
    # 删除物理文件
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    crud_knowledge_asset.mark_document_asset_deleted(db, doc.id)
    crud_document.delete_document(db, doc)
    return ResponseModel(message="删除成功")


@router.post("/{sprint_id}/documents/{doc_id}/reparse", response_model=ResponseModel)
def reparse_document(
    sprint_id: int,
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """重新触发 MinerU 文档解析"""
    doc = crud_document.get_document(db, doc_id)
    if not doc or doc.sprint_id != sprint_id:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 重置解析状态
    doc.parse_status = "待解析"
    db.commit()

    from app.services.document_parser import DocumentParser
    parser = DocumentParser()
    background_tasks.add_task(parser.parse_document, None, doc.id)

    return ResponseModel(message="已触发重新解析")
