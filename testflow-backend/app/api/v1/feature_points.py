from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.feature_point import FeaturePointCreate, FeaturePointUpdate, FeaturePointOut
from app.crud import crud_feature_point


router = APIRouter(prefix="/feature-points", tags=["FeaturePoint 管理"])


def _to_out(fp, db: Session) -> dict:
    return FeaturePointOut(
        id=fp.id,
        name=fp.name,
        source_doc_id=fp.source_doc_id,
        sprint_id=fp.sprint_id,
        module_id=fp.module_id,
        linked_cases=fp.linked_cases or "",
        graph_node_id=fp.graph_node_id,
        created_at=fp.created_at,
        source_doc_name=crud_feature_point.get_source_doc_name(db, fp.source_doc_id),
        sprint_name=crud_feature_point.get_sprint_name(db, fp.sprint_id),
        module_name=crud_feature_point.get_module_name(db, fp.module_id),
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_feature_points(
    sprint_id: int | None = Query(None, description="Sprint ID"),
    module_id: int | None = Query(None, description="模块 ID"),
    source_doc_id: int | None = Query(None, description="来源文档 ID"),
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    fps = crud_feature_point.get_feature_points(
        db, sprint_id=sprint_id, module_id=module_id,
        source_doc_id=source_doc_id, keyword=keyword,
    )
    return ResponseModel(data=[_to_out(fp, db) for fp in fps])


@router.post("", response_model=ResponseModel)
def create_feature_point(
    data: FeaturePointCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    fp = crud_feature_point.create_feature_point(db, data)
    return ResponseModel(data=_to_out(fp, db), message="创建成功")


@router.put("/{fp_id}", response_model=ResponseModel)
def update_feature_point(
    fp_id: int,
    data: FeaturePointUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    fp = crud_feature_point.get_feature_point(db, fp_id)
    if not fp:
        raise HTTPException(status_code=404, detail="功能点不存在")
    fp = crud_feature_point.update_feature_point(db, fp, data)
    return ResponseModel(data=_to_out(fp, db), message="更新成功")


@router.delete("/{fp_id}", response_model=ResponseModel)
def delete_feature_point(
    fp_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    fp = crud_feature_point.get_feature_point(db, fp_id)
    if not fp:
        raise HTTPException(status_code=404, detail="功能点不存在")
    crud_feature_point.delete_feature_point(db, fp)
    return ResponseModel(message="删除成功")
