from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.sprint import Sprint
from app.models.document import Document
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/stats", response_model=ResponseModel)
def knowledge_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """知识库统计：使用新的 Sprint/Document 模型"""
    total_sprints = db.query(Sprint).count()
    total_docs = db.query(Document).count()
    return ResponseModel(data={
        "totalBases": total_sprints,
        "totalDocs": total_docs,
        "newDocs": 0,
    })
