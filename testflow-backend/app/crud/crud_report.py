from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.project import Project
from app.schemas.report import ReportCreate, ReportUpdate


def get_reports(db: Session) -> list[Report]:
    return db.query(Report).all()


def get_report(db: Session, report_id: int) -> Report | None:
    return db.query(Report).filter(Report.id == report_id).first()


def create_report(db: Session, data: ReportCreate) -> Report:
    report = Report(name=data.name, project_id=data.project_id)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def update_report(db: Session, report: Report, data: ReportUpdate) -> Report:
    if data.name is not None:
        report.name = data.name
    if data.status is not None:
        report.status = data.status
    db.commit()
    db.refresh(report)
    return report


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
