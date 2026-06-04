from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.models.pipeline import PipelineExecution, PipelineStage
from app.schemas.pipeline import (
    PipelineCreate, PipelineOut, PipelineDetailOut,
    PipelineStageOut,
)
from app.crud import crud_pipeline

router = APIRouter(prefix="/pipeline", tags=["AI 流水线"])


# ── helpers ──

def _format_duration(ms: int | None) -> str:
    if ms is None:
        return ""
    seconds = ms // 1000
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def _stage_to_out(s: PipelineStage) -> dict:
    out = PipelineStageOut(
        id=s.id,
        execution_id=s.execution_id,
        stage_no=s.stage_no,
        stage_name=s.stage_name,
        status=s.status,
        model=s.model,
        input_tokens=s.input_tokens,
        output_tokens=s.output_tokens,
        duration_ms=s.duration_ms,
        result_summary=s.result_summary,
        started_at=s.started_at,
        completed_at=s.completed_at,
        duration_display=_format_duration(s.duration_ms),
    )
    return out.model_dump()


def _execution_to_out(e: PipelineExecution) -> dict:
    project_name = e.project.name if e.project else ""
    sprint_name = e.sprint.name if e.sprint else ""
    out = PipelineOut(
        id=e.id,
        project_id=e.project_id,
        sprint_id=e.sprint_id,
        mode=e.mode,
        status=e.status,
        started_at=e.started_at,
        completed_at=e.completed_at,
        total_duration_ms=e.total_duration_ms,
        created_at=e.created_at,
        project_name=project_name,
        sprint_name=sprint_name,
        duration_display=_format_duration(e.total_duration_ms),
    )
    return out.model_dump()


def _detail_to_out(e: PipelineExecution) -> dict:
    base = _execution_to_out(e)
    stages = [_stage_to_out(s) for s in e.stages]
    return {**base, "stages": stages}


# ── endpoints ──

@router.get("/executions")
def get_executions(project_id: int | None = None, db: Session = Depends(get_db)):
    executions = crud_pipeline.get_executions(db, project_id=project_id)
    return ResponseModel(data=[_execution_to_out(e) for e in executions])


@router.get("/executions/{execution_id}")
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return ResponseModel(data=_detail_to_out(execution))


@router.post("/executions")
def create_execution(body: PipelineCreate, db: Session = Depends(get_db)):
    execution = crud_pipeline.create_execution(
        db,
        project_id=body.project_id,
        sprint_id=body.sprint_id,
        mode=body.mode,
    )
    # 模拟执行
    execution = crud_pipeline.simulate_execution(db, execution)
    return ResponseModel(data=_detail_to_out(execution), message="流水线执行完成")


@router.post("/executions/{execution_id}/pause")
def pause_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    execution = crud_pipeline.pause_execution(db, execution)
    return ResponseModel(data=_detail_to_out(execution), message="已暂停")


@router.post("/executions/{execution_id}/resume")
def resume_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    execution = crud_pipeline.resume_execution(db, execution)
    # 继续模拟后续阶段
    execution = crud_pipeline.simulate_execution(db, execution)
    return ResponseModel(data=_detail_to_out(execution), message="执行完成")


@router.get("/executions/{execution_id}/status")
def get_execution_status(execution_id: int, db: Session = Depends(get_db)):
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return ResponseModel(data=_detail_to_out(execution))


@router.delete("/executions/{execution_id}")
def delete_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    crud_pipeline.delete_execution(db, execution)
    return ResponseModel(message="执行记录已删除")
