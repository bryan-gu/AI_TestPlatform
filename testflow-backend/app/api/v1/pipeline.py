from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.models.pipeline import PipelineExecution, PipelineStage
from app.models.feature_point import FeaturePoint
from app.models.testcase import TestCase
from app.models.module import Module
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
    # 软删除场景：项目/Sprint 已删除时仍展示历史名称，但标记 deleted 供前端禁用跳转
    sprint_deleted = bool(e.sprint.is_deleted) if e.sprint else False
    project_deleted = bool(e.project.is_deleted) if e.project else False
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
        sprint_deleted=sprint_deleted,
        project_deleted=project_deleted,
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
def create_execution(
    body: PipelineCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    execution = crud_pipeline.create_execution(
        db,
        project_id=body.project_id,
        sprint_id=body.sprint_id,
        mode=body.mode,
    )
    # 启动后台真实执行
    from app.services.pipeline_executor import PipelineExecutor
    executor = PipelineExecutor()
    background_tasks.add_task(executor.execute, execution.id)
    return ResponseModel(data=_detail_to_out(execution), message="流水线已启动")


@router.post("/executions/{execution_id}/pause")
def pause_execution(execution_id: int, db: Session = Depends(get_db)):
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    execution = crud_pipeline.pause_execution(db, execution)
    return ResponseModel(data=_detail_to_out(execution), message="已暂停")


@router.post("/executions/{execution_id}/resume")
def resume_execution(
    execution_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    execution = crud_pipeline.resume_execution(db, execution)
    # 启动后台继续执行
    from app.services.pipeline_executor import PipelineExecutor
    executor = PipelineExecutor()
    background_tasks.add_task(executor.execute, execution.id)
    return ResponseModel(data=_detail_to_out(execution), message="流水线已恢复执行")


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


# ── 产物查询端点 ──

@router.get("/executions/{execution_id}/feature-points")
def get_execution_feature_points(execution_id: int, db: Session = Depends(get_db)):
    """获取本次执行提取的功能点列表"""
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    if not execution.sprint_id:
        return ResponseModel(data=[])

    # 查询该 Sprint 下的功能点，附带模块信息
    feature_points = db.query(FeaturePoint).filter(
        FeaturePoint.sprint_id == execution.sprint_id,
        FeaturePoint.is_deleted == False,  # noqa: E712
    ).all()

    result = []
    for fp in feature_points:
        module_name = fp.module.name if fp.module else ""
        module_code = fp.module.code if fp.module else ""
        result.append({
            "id": fp.id,
            "name": fp.name,
            "module_name": module_name,
            "module_code": module_code,
            "sprint_id": fp.sprint_id,
            "source_doc_id": fp.source_doc_id,
            "linked_cases": fp.linked_cases,
            "created_at": fp.created_at.isoformat() if fp.created_at else None,
        })

    return ResponseModel(data=result)


@router.get("/executions/{execution_id}/test-cases")
def get_execution_test_cases(execution_id: int, db: Session = Depends(get_db)):
    """获取本次执行生成的测试用例列表"""
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    if not execution.project_id:
        return ResponseModel(data=[])

    # 查询该项目下的待执行用例（本次流水线生成的）
    # 通过 project_id + 最近创建时间筛选
    cases = db.query(TestCase).filter(
        TestCase.project_id == execution.project_id,
        TestCase.is_deleted == False,  # noqa: E712
    ).order_by(TestCase.id.desc()).all()

    # 如果执行有 sprint，通过 module 关联筛选
    if execution.sprint_id:
        sprint_fp_module_ids = [
            fp.module_id for fp in
            db.query(FeaturePoint).filter(
                FeaturePoint.sprint_id == execution.sprint_id,
                FeaturePoint.is_deleted == False,  # noqa: E712
            ).all()
            if fp.module_id
        ]
        if sprint_fp_module_ids:
            cases = [c for c in cases if c.module_id in sprint_fp_module_ids or not c.module_id]

    result = []
    for case in cases:
        result.append({
            "id": case.id,
            "case_no": case.case_no,
            "title": case.title,
            "priority": case.priority,
            "exec_status": case.exec_status,
            "module": case.module,
            "module_id": case.module_id,
            "preconditions": case.preconditions,
            "test_data": case.test_data,
            "test_steps": case.test_steps,
            "expected_result": case.expected_result,
            "actual_result": case.actual_result,
            "created_at": case.created_at.isoformat() if case.created_at else None,
        })

    return ResponseModel(data=result)


@router.get("/executions/{execution_id}/download/excel")
def download_execution_excel(execution_id: int, db: Session = Depends(get_db)):
    """下载本次执行生成的测试用例 Excel"""
    execution = crud_pipeline.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    if not execution.sprint_id:
        raise HTTPException(status_code=404, detail="该执行未关联 Sprint，无 Excel 产物")

    from app.services.artifact_manager import ArtifactManager
    mgr = ArtifactManager(db, execution.sprint_id)
    file_path = mgr.get_excel_path()

    if not file_path or not __import__('os').path.exists(file_path):
        raise HTTPException(status_code=404, detail="Excel 文件尚未生成，请等待流水线执行完成")

    return FileResponse(
        path=file_path,
        filename=__import__('os').path.basename(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
