from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload

from app.models.pipeline import PipelineExecution, PipelineStage
from app.models.sprint import Sprint
from app.models.project import Project


# ── 4 阶段定义 ──

STAGE_DEFINITIONS = [
    {"stage_no": 1, "stage_name": "需求分析"},
    {"stage_no": 2, "stage_name": "测试用例生成"},
    {"stage_no": 3, "stage_name": "E2E 脚本生成"},
    {"stage_no": 4, "stage_name": "执行与自愈"},
]


# ── 查询 ──

def get_executions(db: Session, project_id: int | None = None) -> list[PipelineExecution]:
    query = db.query(PipelineExecution).options(joinedload(PipelineExecution.project), joinedload(PipelineExecution.sprint))
    if project_id:
        query = query.filter(PipelineExecution.project_id == project_id)
    return query.order_by(PipelineExecution.created_at.desc()).all()


def get_execution(db: Session, execution_id: int) -> PipelineExecution | None:
    return db.query(PipelineExecution).options(
        joinedload(PipelineExecution.project),
        joinedload(PipelineExecution.sprint),
        joinedload(PipelineExecution.stages),
    ).filter(PipelineExecution.id == execution_id).first()


# ── 创建 ──

def create_execution(db: Session, project_id: int | None = None, sprint_id: int | None = None, mode: str = "full") -> PipelineExecution:
    exec_obj = PipelineExecution(
        project_id=project_id,
        sprint_id=sprint_id,
        mode=mode,
        status="waiting",
    )
    db.add(exec_obj)
    db.flush()

    # 创建 4 个空 stage
    for defn in STAGE_DEFINITIONS:
        stage = PipelineStage(
            execution_id=exec_obj.id,
            stage_no=defn["stage_no"],
            stage_name=defn["stage_name"],
            status="waiting",
        )
        db.add(stage)

    db.commit()
    db.refresh(exec_obj)
    return exec_obj


# ── 暂停 ──

def pause_execution(db: Session, exec_obj: PipelineExecution) -> PipelineExecution:
    if exec_obj.status != "running":
        return exec_obj
    exec_obj.status = "paused"
    # 将当前 running 的 stage 也标记为 waiting（暂停）
    for stage in exec_obj.stages:
        if stage.status == "running":
            stage.status = "waiting"
    db.commit()
    db.refresh(exec_obj)
    return exec_obj


# ── 继续 ──

def resume_execution(db: Session, exec_obj: PipelineExecution) -> PipelineExecution:
    if exec_obj.status != "paused":
        return exec_obj
    exec_obj.status = "running"
    db.commit()
    db.refresh(exec_obj)
    return exec_obj


# ── 删除 ──

def delete_execution(db: Session, exec_obj: PipelineExecution):
    db.delete(exec_obj)
    db.commit()
