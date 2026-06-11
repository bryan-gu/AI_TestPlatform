from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.change_item import (
    ChangeAnalyzeRequest,
    ChangeItemCreate,
    ChangeItemOut,
    ChangeItemUpdate,
)
from app.crud import crud_change_item, crud_trace_link
from app.models.change_item import ChangeItem
from app.models.document import Document
from app.models.knowledge_asset import KnowledgeAsset
from app.models.module import Module
from app.models.project import Project
from app.models.sprint import Sprint
from app.services.change_analyzer import ChangeAnalyzer
from app.schemas.trace_link import TraceLinkCreate


router = APIRouter(prefix="/change-items", tags=["变更项"])


def _to_out(item: ChangeItem, db: Session) -> dict:
    project_name = ""
    if item.project_id:
        project = db.query(Project).filter(Project.id == item.project_id).first()
        project_name = project.name if project else ""

    sprint_name = ""
    if item.sprint_id:
        sprint = db.query(Sprint).filter(Sprint.id == item.sprint_id).first()
        sprint_name = sprint.name if sprint else ""

    source_doc_name = ""
    if item.source_doc_id:
        doc = db.query(Document).filter(Document.id == item.source_doc_id).first()
        source_doc_name = doc.name if doc else ""

    source_asset_name = ""
    if item.source_asset_id:
        asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == item.source_asset_id).first()
        source_asset_name = asset.name if asset else ""

    module_name = ""
    if item.module_id:
        module = db.query(Module).filter(Module.id == item.module_id).first()
        module_name = module.name if module else ""

    target_name = ""
    if item.target_type and item.target_id:
        target_name = crud_trace_link.get_entity_name(db, item.target_type, item.target_id)

    return ChangeItemOut(
        id=item.id,
        project_id=item.project_id,
        sprint_id=item.sprint_id,
        source_doc_id=item.source_doc_id,
        source_asset_id=item.source_asset_id,
        module_id=item.module_id,
        title=item.title,
        description=item.description or "",
        change_type=item.change_type or "unknown",
        target_type=item.target_type or "feature",
        target_id=item.target_id,
        priority=item.priority or "中",
        impact_level=item.impact_level or "中",
        status=item.status or "open",
        before_snapshot=item.before_snapshot or {},
        after_snapshot=item.after_snapshot or {},
        evidence=item.evidence or "",
        confidence=item.confidence or 0,
        fingerprint=item.fingerprint or "",
        raw_data=item.raw_data or {},
        is_deleted=item.is_deleted or False,
        created_at=item.created_at,
        updated_at=item.updated_at,
        project_name=project_name,
        sprint_name=sprint_name,
        source_doc_name=source_doc_name,
        source_asset_name=source_asset_name,
        module_name=module_name,
        target_name=target_name,
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_change_items(
    project_id: int | None = Query(None, description="项目 ID"),
    sprint_id: int | None = Query(None, description="Sprint ID"),
    source_doc_id: int | None = Query(None, description="来源文档 ID"),
    source_asset_id: int | None = Query(None, description="来源资产 ID"),
    module_id: int | None = Query(None, description="模块 ID"),
    change_type: str | None = Query(None, description="变更类型"),
    target_type: str | None = Query(None, description="目标实体类型"),
    target_id: int | None = Query(None, description="目标实体 ID"),
    priority: str | None = Query(None, description="优先级"),
    impact_level: str | None = Query(None, description="影响等级"),
    status: str | None = Query(None, description="状态"),
    keyword: str | None = Query(None, description="关键词"),
    skip: int = Query(0, description="分页偏移"),
    limit: int = Query(100, description="每页数量"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    items = crud_change_item.get_change_items(
        db,
        project_id=project_id,
        sprint_id=sprint_id,
        source_doc_id=source_doc_id,
        source_asset_id=source_asset_id,
        module_id=module_id,
        change_type=change_type,
        target_type=target_type,
        target_id=target_id,
        priority=priority,
        impact_level=impact_level,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )
    total = crud_change_item.count_change_items(
        db,
        project_id=project_id,
        sprint_id=sprint_id,
        source_doc_id=source_doc_id,
        source_asset_id=source_asset_id,
        module_id=module_id,
        change_type=change_type,
        target_type=target_type,
        target_id=target_id,
        priority=priority,
        impact_level=impact_level,
        status=status,
        keyword=keyword,
    )
    return ResponseModel(data={
        "items": [_to_out(item, db) for item in items],
        "total": total,
    })


@router.post("/analyze-sprint/{sprint_id}", response_model=ResponseModel)
def analyze_sprint_changes(
    sprint_id: int,
    data: ChangeAnalyzeRequest | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        result = ChangeAnalyzer(db).analyze_sprint(sprint_id, data or ChangeAnalyzeRequest())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return ResponseModel(data=result.model_dump(), message=result.message or "增量分析完成")


@router.get("/{change_id}", response_model=ResponseModel)
def get_change_item(
    change_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    item = crud_change_item.get_change_item(db, change_id)
    if not item:
        raise HTTPException(status_code=404, detail="变更项不存在")
    return ResponseModel(data=_to_out(item, db))


@router.post("", response_model=ResponseModel)
def create_change_item(
    data: ChangeItemCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    item = crud_change_item.create_change_item(db, data)
    if item.target_type and item.target_id:
        crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
            project_id=item.project_id,
            sprint_id=item.sprint_id,
            source_type="change",
            source_id=item.id,
            target_type=item.target_type,
            target_id=item.target_id,
            relation_type="changes",
            confidence=item.confidence or 80,
            evidence=item.evidence or "手工创建变更项",
            metadata={"source": "manual"},
            created_by="manual",
        ))
    return ResponseModel(data=_to_out(item, db), message="创建成功")


@router.put("/{change_id}", response_model=ResponseModel)
def update_change_item(
    change_id: int,
    data: ChangeItemUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    item = crud_change_item.get_change_item(db, change_id)
    if not item:
        raise HTTPException(status_code=404, detail="变更项不存在")
    item = crud_change_item.update_change_item(db, item, data)
    return ResponseModel(data=_to_out(item, db), message="更新成功")


@router.delete("/{change_id}", response_model=ResponseModel)
def delete_change_item(
    change_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    item = crud_change_item.get_change_item(db, change_id)
    if not item:
        raise HTTPException(status_code=404, detail="变更项不存在")
    crud_change_item.soft_delete_change_item(db, item)
    return ResponseModel(message="删除成功")


@router.get("/{change_id}/impact", response_model=ResponseModel)
def get_change_impact(
    change_id: int,
    max_depth: int = Query(2, ge=1, le=3, description="影响分析深度"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        result = ChangeAnalyzer(db).get_change_impact(change_id, max_depth=max_depth)
        result["links"] = []
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return ResponseModel(data=result)
