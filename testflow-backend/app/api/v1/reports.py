from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.report import ReportCreate, ReportUpdate, ReportOut
from app.crud import crud_report

router = APIRouter(prefix="/reports", tags=["测试报告"])


def _to_out(report, db: Session) -> dict:
    return ReportOut(
        id=report.id, name=report.name,
        project=crud_report.get_project_name(db, report.project_id),
        project_id=report.project_id,
        pass_rate=report.pass_rate, defect_count=report.defect_count,
        status=report.status,
        report_type=report.report_type or "",
        test_scope=report.test_scope or "",
        approved_by=report.approved_by,
        approved_by_name=crud_report.get_approver_name(db, report.approved_by),
        approved_at=report.approved_at,
        created_at=report.created_at,
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_reports(
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    reports = crud_report.get_reports(db, keyword=keyword)
    return ResponseModel(data=[_to_out(r, db) for r in reports])


@router.get("/stats", response_model=ResponseModel)
def report_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ResponseModel(data=crud_report.get_report_stats(db))


@router.post("", response_model=ResponseModel)
def create_report(data: ReportCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = crud_report.create_report(db, data)
    return ResponseModel(data=_to_out(report, db))


@router.put("/{report_id}", response_model=ResponseModel)
def update_report(report_id: int, data: ReportUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = crud_report.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    report = crud_report.update_report(db, report, data)
    return ResponseModel(data=_to_out(report, db))


@router.put("/{report_id}/approve", response_model=ResponseModel)
def approve_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    report = crud_report.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    if report.status == "已审批":
        raise HTTPException(status_code=400, detail="报告已审批")
    report = crud_report.approve_report(db, report, current_user.id)
    return ResponseModel(data=_to_out(report, db), message="报告已审批")


@router.delete("/{report_id}", response_model=ResponseModel)
def delete_report(report_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = crud_report.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    crud_report.delete_report(db, report)
    return ResponseModel(message="删除成功")
