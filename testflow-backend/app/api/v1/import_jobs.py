"""异步导入任务 API（增强项批次 4）。

本地项目导入等耗时操作走异步 Job，后台执行 + 进度可查。
dry_run 预览仍走同步 /knowledge-assets/import-local-project。
"""
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.core.deps import get_current_user
from app.models.import_job import ImportJob
from app.models.project import Project
from app.schemas.common import ResponseModel
from app.schemas.import_job import ImportJobCreate, ImportJobOut
from app.services.local_project_importer import LocalProjectImporter


router = APIRouter(prefix="/import-jobs", tags=["导入任务"])


def _to_out(job: ImportJob) -> dict:
    return ImportJobOut(
        id=job.id,
        project_id=job.project_id,
        root_path=job.root_path,
        job_type=job.job_type or "local_project",
        status=job.status or "pending",
        dry_run=job.dry_run or False,
        total_files=job.total_files or 0,
        processed_files=job.processed_files or 0,
        success_count=job.success_count or 0,
        failed_count=job.failed_count or 0,
        result_summary=job.result_summary or {},
        warnings=job.warnings or [],
        errors=job.errors or [],
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    ).model_dump()


def _run_import_job(job_id: int, project_id: int, root_path: str):
    """后台执行导入任务（独立 db session）。"""
    db = SessionLocal()
    try:
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        if not job:
            return
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        def on_progress(processed: int, total: int):
            job.processed_files = processed
            job.total_files = total
            db.commit()

        importer = LocalProjectImporter(db)
        result = importer.import_project(root_path, project_id, dry_run=False, on_progress=on_progress)
        asset_count = len(result.assets) if result.assets else 0
        job.status = "succeeded"
        job.completed_at = datetime.utcnow()
        job.result_summary = result.model_dump()
        job.total_files = asset_count
        job.processed_files = asset_count
        job.warnings = result.warnings or []
        db.commit()
    except Exception as e:
        try:
            job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.errors = [str(e)]
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.post("/local-project", response_model=ResponseModel)
def create_local_project_job(
    data: ImportJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """创建本地项目导入任务（异步执行，返回 job_id 供轮询）。"""
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="项目不存在")
    if not data.root_path or not data.root_path.strip():
        raise HTTPException(status_code=400, detail="root_path 不能为空")
    job = ImportJob(
        project_id=data.project_id,
        root_path=data.root_path.strip(),
        job_type="local_project",
        status="pending",
        dry_run=False,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(_run_import_job, job.id, data.project_id, data.root_path.strip())
    return ResponseModel(data=_to_out(job), message="导入任务已创建，正在后台执行")


@router.get("", response_model=ResponseModel)
def list_jobs(
    project_id: int | None = Query(None, description="项目 ID"),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(ImportJob)
    if project_id:
        query = query.filter(ImportJob.project_id == project_id)
    jobs = query.order_by(ImportJob.created_at.desc()).offset(skip).limit(limit).all()
    return ResponseModel(data=[_to_out(j) for j in jobs])


@router.get("/{job_id}", response_model=ResponseModel)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="导入任务不存在")
    return ResponseModel(data=_to_out(job))


@router.post("/{job_id}/cancel", response_model=ResponseModel)
def cancel_job(
    job_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="导入任务不存在")
    if job.status not in ("pending", "running"):
        raise HTTPException(status_code=400, detail=f"任务当前状态 {job.status}，不可取消")
    job.status = "cancelled"
    job.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return ResponseModel(data=_to_out(job), message="任务已请求取消")
