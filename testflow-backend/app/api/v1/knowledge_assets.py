from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.knowledge_asset import KnowledgeAssetCreate, KnowledgeAssetUpdate, KnowledgeAssetOut
from app.crud import crud_knowledge_asset


router = APIRouter(prefix="/knowledge-assets", tags=["知识资产"])


def _to_out(asset, db: Session) -> dict:
    return KnowledgeAssetOut(
        id=asset.id,
        project_id=asset.project_id,
        sprint_id=asset.sprint_id,
        document_id=asset.document_id,
        name=asset.name,
        asset_type=asset.asset_type or "other",
        source_kind=asset.source_kind or "uploaded",
        file_path=asset.file_path or "",
        file_type=asset.file_type or "",
        file_size=asset.file_size or 0,
        module_id=asset.module_id,
        version=asset.version or "v1.0",
        status=asset.status or "active",
        parse_status=asset.parse_status or "pending",
        content_hash=asset.content_hash or "",
        metadata=asset.asset_metadata or {},
        created_by=asset.created_by,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        project_name=crud_knowledge_asset.get_project_name(db, asset.project_id),
        sprint_name=crud_knowledge_asset.get_sprint_name(db, asset.sprint_id),
        document_name=crud_knowledge_asset.get_document_name(db, asset.document_id),
        module_name=crud_knowledge_asset.get_module_name(db, asset.module_id),
        creator_name=crud_knowledge_asset.get_creator_name(db, asset.created_by),
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_assets(
    project_id: int | None = Query(None, description="项目 ID"),
    sprint_id: int | None = Query(None, description="Sprint ID"),
    asset_type: str | None = Query(None, description="资产类型"),
    module_id: int | None = Query(None, description="模块 ID"),
    keyword: str | None = Query(None, description="搜索关键词"),
    status: str | None = Query("active", description="资产状态"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    assets = crud_knowledge_asset.get_assets(
        db,
        project_id=project_id,
        sprint_id=sprint_id,
        asset_type=asset_type,
        module_id=module_id,
        keyword=keyword,
        status=status,
    )
    return ResponseModel(data=[_to_out(a, db) for a in assets])


@router.get("/{asset_id}", response_model=ResponseModel)
def get_asset(asset_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    asset = crud_knowledge_asset.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="知识资产不存在")
    return ResponseModel(data=_to_out(asset, db))


@router.post("", response_model=ResponseModel)
def create_asset(
    data: KnowledgeAssetCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    asset = crud_knowledge_asset.create_asset(db, data)
    return ResponseModel(data=_to_out(asset, db), message="创建成功")


@router.put("/{asset_id}", response_model=ResponseModel)
def update_asset(
    asset_id: int,
    data: KnowledgeAssetUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    asset = crud_knowledge_asset.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="知识资产不存在")
    asset = crud_knowledge_asset.update_asset(db, asset, data)
    return ResponseModel(data=_to_out(asset, db), message="更新成功")


@router.delete("/{asset_id}", response_model=ResponseModel)
def delete_asset(asset_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    asset = crud_knowledge_asset.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="知识资产不存在")
    asset.status = "deleted"
    db.commit()
    return ResponseModel(message="删除成功")
