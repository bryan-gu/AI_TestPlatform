from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.knowledge_asset import KnowledgeAsset
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/stats", response_model=ResponseModel)
def knowledge_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """知识库统计：阶段 2 起按 active KnowledgeAsset 作为资产口径"""
    active_assets = db.query(KnowledgeAsset).filter(KnowledgeAsset.status == "active").count()
    active_sprints = db.query(KnowledgeAsset.sprint_id).filter(
        KnowledgeAsset.status == "active",
        KnowledgeAsset.sprint_id.isnot(None),
    ).distinct().count()
    return ResponseModel(data={
        "totalBases": active_sprints,
        "totalDocs": active_assets,
        "newDocs": 0,
    })
