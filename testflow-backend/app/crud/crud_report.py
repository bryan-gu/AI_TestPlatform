from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.report import Report
from app.models.project import Project
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate


def get_reports(db: Session, keyword: str | None = None) -> list[Report]:
    query = db.query(Report)
    if keyword:
        query = query.filter(Report.name.ilike(f"%{keyword}%"))
    return query.all()


def get_report(db: Session, report_id: int) -> Report | None:
    return db.query(Report).filter(Report.id == report_id).first()


def create_report(db: Session, data: ReportCreate) -> Report:
    report = Report(
        name=data.name,
        project_id=data.project_id,
        report_type=data.report_type,
        test_scope=data.test_scope,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def update_report(db: Session, report: Report, data: ReportUpdate) -> Report:
    if data.name is not None:
        report.name = data.name
    if data.status is not None:
        report.status = data.status
    if data.report_type is not None:
        report.report_type = data.report_type
    if data.test_scope is not None:
        report.test_scope = data.test_scope
    db.commit()
    db.refresh(report)
    return report


def approve_report(db: Session, report: Report, approver_id: int) -> Report:
    report.status = "已审批"
    report.approved_by = approver_id
    report.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(report)
    return report


def get_approver_name(db: Session, approver_id: int | None) -> str:
    if not approver_id:
        return ""
    user = db.query(User).filter(User.id == approver_id).first()
    return user.name if user else ""


def delete_report(db: Session, report: Report) -> None:
    db.delete(report)
    db.commit()


def get_report_stats(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly = db.query(Report).filter(Report.created_at >= month_start).count()
    total = db.query(Report).count()
    all_reports = db.query(Report).all()
    avg_pass = round(sum(r.pass_rate for r in all_reports) / total) if total > 0 else 0
    total_defects = sum(r.defect_count for r in all_reports)
    fixed = sum(r.defect_count for r in all_reports if r.status == "已审批")
    pending = db.query(Report).filter(Report.status == "待审批").count()
    return {
        "monthlyReports": monthly,
        "monthlyChange": 0,
        "avgPassRate": avg_pass,
        "totalDefects": total_defects,
        "fixedDefects": fixed,
        "pendingApproval": pending,
    }


def get_project_name(db: Session, project_id: int | None) -> str:
    if not project_id:
        return ""
    proj = db.query(Project).filter(Project.id == project_id).first()
    return proj.name if proj else ""
