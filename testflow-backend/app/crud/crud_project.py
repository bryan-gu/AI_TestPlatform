from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def _check_prefix_unique(db: Session, prefix: str, exclude_id: int | None = None) -> None:
    """校验 case_prefix 唯一性"""
    q = db.query(Project).filter(Project.case_prefix == prefix)
    if exclude_id:
        q = q.filter(Project.id != exclude_id)
    if q.first():
        raise ValueError(f"用例前缀 '{prefix}' 已被其他项目使用")


def get_projects(db: Session, keyword: str | None = None) -> list[Project]:
    query = db.query(Project)
    if keyword:
        query = query.filter(
            or_(
                Project.name.ilike(f"%{keyword}%"),
                Project.description.ilike(f"%{keyword}%")
            )
        )
    return query.all()


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, data: ProjectCreate) -> Project:
    _check_prefix_unique(db, data.case_prefix)
    project = Project(
        name=data.name,
        description=data.description,
        status=data.status,
        progress=data.progress,
        owner_id=data.owner_id,
        case_prefix=data.case_prefix,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project, data: ProjectUpdate) -> Project:
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.status is not None:
        project.status = data.status
    if data.progress is not None:
        project.progress = data.progress
    if data.owner_id is not None:
        project.owner_id = data.owner_id
    if data.case_prefix is not None:
        _check_prefix_unique(db, data.case_prefix, exclude_id=project.id)
        project.case_prefix = data.case_prefix
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()


def get_owner_name(db: Session, owner_id: int | None) -> str:
    if not owner_id:
        return ""
    user = db.query(User).filter(User.id == owner_id).first()
    return user.name if user else ""
