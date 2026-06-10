from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.trace_link import TraceLinkCreate, TraceLinkUpdate, TraceLinkOut
from app.crud import crud_trace_link, crud_graph


router = APIRouter(prefix="/trace-links", tags=["追踪关系"])


def _to_out(link, db: Session) -> dict:
    return TraceLinkOut(
        id=link.id,
        project_id=link.project_id,
        sprint_id=link.sprint_id,
        source_type=link.source_type,
        source_id=link.source_id,
        target_type=link.target_type,
        target_id=link.target_id,
        relation_type=link.relation_type,
        confidence=link.confidence or 0,
        evidence=link.evidence or "",
        metadata=link.link_metadata or {},
        status=link.status or "active",
        created_by=link.created_by or "system",
        created_at=link.created_at,
        updated_at=link.updated_at,
        source_name=crud_trace_link.get_entity_name(db, link.source_type, link.source_id),
        target_name=crud_trace_link.get_entity_name(db, link.target_type, link.target_id),
        relation_label=crud_trace_link.get_relation_label(link.relation_type),
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_trace_links(
    project_id: int | None = Query(None, description="项目 ID"),
    sprint_id: int | None = Query(None, description="Sprint ID"),
    source_type: str | None = Query(None, description="来源实体类型"),
    source_id: int | None = Query(None, description="来源实体 ID"),
    target_type: str | None = Query(None, description="目标实体类型"),
    target_id: int | None = Query(None, description="目标实体 ID"),
    relation_type: str | None = Query(None, description="关系类型"),
    status: str | None = Query("active", description="关系状态"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    links = crud_trace_link.get_trace_links(
        db,
        project_id=project_id,
        sprint_id=sprint_id,
        source_type=source_type,
        source_id=source_id,
        target_type=target_type,
        target_id=target_id,
        relation_type=relation_type,
        status=status,
    )
    return ResponseModel(data=[_to_out(link, db) for link in links])


@router.get("/entity/{entity_type}/{entity_id}", response_model=ResponseModel)
def get_entity_links(
    entity_type: str,
    entity_id: int,
    direction: str = Query("both", description="both/source/target"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    links = crud_trace_link.get_entity_links(db, entity_type, entity_id, direction=direction)
    return ResponseModel(data=[_to_out(link, db) for link in links])


@router.get("/entity/{entity_type}/{entity_id}/impact", response_model=ResponseModel)
def get_entity_impact(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    impact = crud_trace_link.get_entity_impact(db, entity_type, entity_id)
    impact["links"] = [_to_out(link, db) for link in impact["links"]]
    return ResponseModel(data=impact)


@router.post("/backfill", response_model=ResponseModel)
def backfill_trace_links(
    project_id: int | None = Query(None, description="项目 ID"),
    sprint_id: int | None = Query(None, description="Sprint ID"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    result = crud_trace_link.backfill_trace_links(db, project_id=project_id, sprint_id=sprint_id)
    graph = None
    if project_id is not None:
        graph = crud_graph.generate_graph_for_scope(db, project_id=project_id, sprint_id=sprint_id)
        result.update({
            "graph_id": graph.id,
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
        })
    return ResponseModel(data=result, message="追踪关系回填完成")


@router.get("/{link_id}", response_model=ResponseModel)
def get_trace_link(link_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    link = crud_trace_link.get_trace_link(db, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="追踪关系不存在")
    return ResponseModel(data=_to_out(link, db))


@router.post("", response_model=ResponseModel)
def create_trace_link(
    data: TraceLinkCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    link = crud_trace_link.upsert_trace_link(db, data)
    return ResponseModel(data=_to_out(link, db), message="保存成功")


@router.put("/{link_id}", response_model=ResponseModel)
def update_trace_link(
    link_id: int,
    data: TraceLinkUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    link = crud_trace_link.get_trace_link(db, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="追踪关系不存在")
    link = crud_trace_link.update_trace_link(db, link, data)
    return ResponseModel(data=_to_out(link, db), message="更新成功")


@router.delete("/{link_id}", response_model=ResponseModel)
def delete_trace_link(link_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    link = crud_trace_link.get_trace_link(db, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="追踪关系不存在")
    crud_trace_link.deactivate_trace_link(db, link)
    return ResponseModel(message="删除成功")
