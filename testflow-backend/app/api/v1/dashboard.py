from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.project import Project
from app.models.testcase import TestCase
from app.models.activity import Activity
from app.models.sprint import Sprint
from app.models.document import Document
from app.models.pipeline import PipelineExecution
from app.models.ai_config import AICallLog
from app.schemas.common import ResponseModel
from app.schemas.dashboard import DashboardStats, ActivityOut

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=ResponseModel)
def dashboard_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    active = db.query(Project).filter(Project.status.in_(["active", "testing"])).count()
    total_cases = db.query(TestCase).count()
    passed = db.query(TestCase).filter(TestCase.exec_status == "通过").count()
    pass_rate = round(passed / total_cases * 100) if total_cases > 0 else 0
    failed = db.query(TestCase).filter(TestCase.exec_status == "失败").count()
    pending = db.query(TestCase).filter(TestCase.exec_status == "待执行").count()

    # Phase 7 增强统计
    total_sprints = db.query(Sprint).count()
    total_documents = db.query(Document).count()
    pipeline_executions = db.query(PipelineExecution).count()
    ai_call_count = db.query(AICallLog).count()

    stats = DashboardStats(
        activeProjects=active,
        totalCases=total_cases,
        newCases=0,
        passRate=pass_rate,
        passRateChange=0,
        pendingBugs=failed,
        severeBugs=0,
        normalBugs=failed,
        totalSprints=total_sprints,
        totalDocuments=total_documents,
        pipelineExecutions=pipeline_executions,
        aiCallCount=ai_call_count,
    )
    return ResponseModel(data=stats.model_dump())


@router.get("/activities", response_model=ResponseModel)
def dashboard_activities(db: Session = Depends(get_db), _=Depends(get_current_user)):
    activities = db.query(Activity).order_by(Activity.created_at.desc()).limit(10).all()
    result = []
    for a in activities:
        user_name = a.user.name if a.user else "系统"
        # 计算相对时间
        now = datetime.now(timezone.utc)
        diff = now - a.created_at.replace(tzinfo=timezone.utc) if a.created_at else now - now
        minutes = diff.total_seconds() / 60
        if minutes < 1:
            time_str = "刚刚"
        elif minutes < 60:
            time_str = f"{int(minutes)} 分钟前"
        elif minutes < 1440:
            time_str = f"{int(minutes / 60)} 小时前"
        else:
            time_str = f"{int(minutes / 1440)} 天前"

        result.append(ActivityOut(
            icon=a.icon,
            text=a.text,
            time=time_str,
            user=user_name,
        ).model_dump())
    return ResponseModel(data=result)
