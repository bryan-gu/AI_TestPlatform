from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.schemas.testcase import TestCaseOut
from app.schemas.report import ReportOut
from app.crud import crud_project, crud_testcase, crud_report

router = APIRouter(prefix="/projects", tags=["项目管理"])


def _to_out(project, db: Session) -> dict:
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description or "",
        status=project.status,
        progress=project.progress,
        owner_id=project.owner_id,
        owner=crud_project.get_owner_name(db, project.owner_id),
        case_prefix=project.case_prefix,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_projects(
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    projects = crud_project.get_projects(db, keyword=keyword)
    return ResponseModel(data=[_to_out(p, db) for p in projects])


@router.get("/{project_id}", response_model=ResponseModel)
def get_project(project_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    project = crud_project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return ResponseModel(data=_to_out(project, db))


@router.post("", response_model=ResponseModel)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    project = crud_project.create_project(db, data)
    return ResponseModel(data=_to_out(project, db))


@router.put("/{project_id}", response_model=ResponseModel)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    project = crud_project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    project = crud_project.update_project(db, project, data)
    return ResponseModel(data=_to_out(project, db))


@router.delete("/{project_id}", response_model=ResponseModel)
def delete_project(project_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    project = crud_project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    crud_project.delete_project(db, project)
    return ResponseModel(message="删除成功")


@router.get("/{project_id}/testcases", response_model=ResponseModel)
def get_project_testcases(project_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    cases = db.query(crud_testcase.TestCase).filter(crud_testcase.TestCase.project_id == project_id).all()
    result = []
    for c in cases:
        result.append(TestCaseOut(
            id=c.id, case_no=c.case_no, title=c.title, priority=c.priority,
            exec_status=c.exec_status,
            executor=crud_testcase.get_executor_name(db, c.executor_id),
            project=crud_testcase.get_project_name(db, c.project_id),
            project_id=c.project_id, module=c.module,
            test_data=c.test_data or "",
            actual_result=c.actual_result or "",
            updated_at=c.updated_at,
        ).model_dump())
    return ResponseModel(data=result)


@router.get("/{project_id}/reports", response_model=ResponseModel)
def get_project_reports(project_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    reports = db.query(crud_report.Report).filter(crud_report.Report.project_id == project_id).all()
    result = []
    for r in reports:
        result.append(ReportOut(
            id=r.id, name=r.name,
            project=crud_report.get_project_name(db, r.project_id),
            project_id=r.project_id,
            pass_rate=r.pass_rate, defect_count=r.defect_count,
            status=r.status, created_at=r.created_at,
        ).model_dump())
    return ResponseModel(data=result)
