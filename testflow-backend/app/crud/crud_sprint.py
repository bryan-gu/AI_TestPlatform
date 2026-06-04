from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.sprint import Sprint
from app.models.document import Document
from app.models.feature_point import FeaturePoint
from app.models.project import Project
from app.schemas.sprint import SprintCreate, SprintUpdate


def get_sprints(db: Session, project_id: int | None = None, keyword: str | None = None) -> list[Sprint]:
    query = db.query(Sprint)
    if project_id:
        query = query.filter(Sprint.project_id == project_id)
    if keyword:
        query = query.filter(
            or_(
                Sprint.name.ilike(f"%{keyword}%"),
                Sprint.description.ilike(f"%{keyword}%"),
            )
        )
    return query.order_by(Sprint.created_at.desc()).all()


def get_sprint(db: Session, sprint_id: int) -> Sprint | None:
    return db.query(Sprint).filter(Sprint.id == sprint_id).first()


def create_sprint(db: Session, data: SprintCreate) -> Sprint:
    sprint = Sprint(
        name=data.name,
        description=data.description,
        project_id=data.project_id,
        status=data.status,
        is_all=data.is_all,
    )
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint


def update_sprint(db: Session, sprint: Sprint, data: SprintUpdate) -> Sprint:
    if data.name is not None:
        sprint.name = data.name
    if data.description is not None:
        sprint.description = data.description
    if data.status is not None:
        sprint.status = data.status
    if data.is_all is not None:
        sprint.is_all = data.is_all
    db.commit()
    db.refresh(sprint)
    return sprint


def delete_sprint(db: Session, sprint: Sprint) -> None:
    db.delete(sprint)
    db.commit()


def get_sprint_stats(db: Session, project_id: int | None = None) -> dict:
    """统计：sprintCount / totalDocs / moduleCount / featurePointCount"""
    sprint_query = db.query(Sprint)
    if project_id:
        sprint_query = sprint_query.filter(Sprint.project_id == project_id)
    sprints = sprint_query.all()

    sprint_count = len(sprints)
    total_docs = 0
    all_module_ids = set()
    sprint_ids = []
    for s in sprints:
        sprint_ids.append(s.id)
        docs = db.query(Document).filter(Document.sprint_id == s.id).all()
        total_docs += len(docs)
        for doc in docs:
            if doc.module_ids:
                all_module_ids.update(doc.module_ids)

    # 统计功能点数量
    fp_count = 0
    if sprint_ids:
        fp_count = db.query(FeaturePoint).filter(FeaturePoint.sprint_id.in_(sprint_ids)).count()

    return {
        "sprintCount": sprint_count,
        "totalDocs": total_docs,
        "moduleCount": len(all_module_ids),
        "featurePointCount": fp_count,
    }


def get_project_name(db: Session, project_id: int | None) -> str:
    if not project_id:
        return ""
    project = db.query(Project).filter(Project.id == project_id).first()
    return project.name if project else ""
