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
from app.schemas.sprint import SprintCreate, SprintPrepareFromAllRequest, SprintMergeToAllRequest, SprintUpdate, SprintOut
from app.schemas.document import DocumentUpdate, DocumentOut
from app.crud import crud_sprint, crud_document, crud_knowledge_asset, crud_trace_link
from app.schemas.trace_link import TraceLinkCreate
from app.services.sprint_baseline_manager import SprintBaselineManager


router = APIRouter(prefix="/sprints", tags=["Sprint 管理"])


def _sprint_to_out(sprint, db: Session) -> dict:
    docs = db.query(Document).filter(
        Document.sprint_id == sprint.id,
        Document.is_deleted == False,  # noqa: E712
    ).all()
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


@router.get("/all", response_model=ResponseModel)
def get_sprint_all(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    sprint = crud_sprint.get_sprint_all(db, project_id)
    return ResponseModel(data=_sprint_to_out(sprint, db) if sprint else None)


@router.post("/all/ensure", response_model=ResponseModel)
def ensure_sprint_all(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        sprint = crud_sprint.ensure_sprint_all(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=_sprint_to_out(sprint, db), message="已确保最新汇总基线")


@router.get("/{sprint_id}", response_model=ResponseModel)
def get_sprint(sprint_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    return ResponseModel(data=_sprint_to_out(sprint, db))


@router.post("", response_model=ResponseModel)
def create_sprint(data: SprintCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        sprint = crud_sprint.create_sprint(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=_sprint_to_out(sprint, db))


@router.put("/{sprint_id}", response_model=ResponseModel)
def update_sprint(sprint_id: int, data: SprintUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    try:
        sprint = crud_sprint.update_sprint(db, sprint, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=_sprint_to_out(sprint, db))


@router.delete("/{sprint_id}", response_model=ResponseModel)
def delete_sprint(sprint_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    try:
        crud_sprint.delete_sprint(db, sprint)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(message="删除成功")


@router.post("/{sprint_id}/mark-as-baseline", response_model=ResponseModel)
def mark_sprint_as_baseline(
    sprint_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    try:
        sprint = crud_sprint.mark_baseline(db, sprint)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=_sprint_to_out(sprint, db), message="已标记为基线")


@router.post("/{sprint_id}/mark-as-sprint-all", response_model=ResponseModel)
def mark_sprint_as_sprint_all(
    sprint_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    sprint = crud_sprint.get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint 不存在")
    try:
        sprint = crud_sprint.mark_sprint_all(db, sprint)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=_sprint_to_out(sprint, db), message="已标记为最新汇总基线")


@router.post("/{sprint_id}/sync-to-all", response_model=ResponseModel)
def sync_sprint_to_all(
    sprint_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        result = SprintBaselineManager(db).sync_sprint_to_all(sprint_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=result, message="已同步到最新汇总基线")


@router.post("/{sprint_id}/prepare-from-all", response_model=ResponseModel)
def prepare_sprint_from_all(
    sprint_id: int,
    data: SprintPrepareFromAllRequest | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        result = SprintBaselineManager(db).prepare_from_all(
            sprint_id,
            update_existing=data.update_existing if data else False,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=result, message="已从最新汇总准备增量底稿")


@router.post("/{sprint_id}/merge-to-all", response_model=ResponseModel)
def merge_sprint_to_all(
    sprint_id: int,
    data: SprintMergeToAllRequest | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        req = data or SprintMergeToAllRequest()
        result = SprintBaselineManager(db).merge_to_all(
            sprint_id,
            change_item_ids=req.change_item_ids or None,
            statuses=req.statuses,
            target_types=req.target_types,
            dry_run=req.dry_run,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ResponseModel(data=result, message="已将确认变更合并到最新汇总")


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
        ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".txt": "Text",
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
    asset = crud_knowledge_asset.upsert_asset_for_document(db, doc, source_kind="uploaded")
    crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
        project_id=asset.project_id,
        sprint_id=asset.sprint_id,
        source_type="asset",
        source_id=asset.id,
        target_type="document",
        target_id=doc.id,
        relation_type="derived_from",
        confidence=100,
        evidence="上传文档自动生成知识资产",
        metadata={"source": "upload_document"},
        created_by="system",
    ))

    # 触发后台文档解析：文本/JSON 本地解析，复杂文档走 MinerU
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
    asset = crud_knowledge_asset.upsert_asset_for_document(db, doc, source_kind="uploaded")
    crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
        project_id=asset.project_id,
        sprint_id=asset.sprint_id,
        source_type="asset",
        source_id=asset.id,
        target_type="document",
        target_id=doc.id,
        relation_type="derived_from",
        confidence=100,
        evidence="文档更新后同步知识资产",
        metadata={"source": "update_document"},
        created_by="system",
    ))
    return ResponseModel(data=_doc_to_out(doc, db))


@router.delete("/{sprint_id}/documents/{doc_id}", response_model=ResponseModel)
def delete_document(sprint_id: int, doc_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    doc = crud_document.get_document(db, doc_id)
    if not doc or doc.sprint_id != sprint_id:
        raise HTTPException(status_code=404, detail="文档不存在")
    # 软删除：保留物理文件以便恢复，仅同步标记关联资产为 deleted
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
    """重新触发文档解析"""
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
