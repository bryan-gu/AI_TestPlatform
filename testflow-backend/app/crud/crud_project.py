from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_projects(db: Session) -> list[Project]:
    return db.query(Project).all()


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        status=data.status,
        progress=data.progress,
        owner_id=data.owner_id,
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
