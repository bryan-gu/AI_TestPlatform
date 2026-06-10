from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def _check_prefix_unique(db: Session, prefix: str, exclude_id: int | None = None) -> None:
    """校验 case_prefix 唯一性（仅在未删除项目中校验）"""
    q = db.query(Project).filter(
        Project.case_prefix == prefix,
        Project.is_deleted == False,  # noqa: E712
    )
    if exclude_id:
        q = q.filter(Project.id != exclude_id)
    if q.first():
        raise ValueError(f"用例前缀 '{prefix}' 已被其他项目使用")


def get_projects(db: Session, keyword: str | None = None) -> list[Project]:
    query = db.query(Project).filter(Project.is_deleted == False)  # noqa: E712
    if keyword:
        query = query.filter(
            or_(
                Project.name.ilike(f"%{keyword}%"),
                Project.description.ilike(f"%{keyword}%")
            )
        )
    return query.all()


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False,  # noqa: E712
    ).first()


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
    # 中文状态 → 英文存储
    _STATUS_REVERSE = {"待启动": "pending", "进行中": "active", "测试中": "testing", "已完成": "completed"}
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.status is not None:
        project.status = _STATUS_REVERSE.get(data.status, data.status)
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
    """级联软删除：项目 + 其下 sprint/module/用例/功能点/图谱/文档，资产置 deleted。
    AI 流水线记录保留不动。"""
    from datetime import datetime
    from app.models.sprint import Sprint
    from app.models.module import Module
    from app.models.testcase import TestCase
    from app.models.feature_point import FeaturePoint
    from app.models.graph import Graph
    from app.models.document import Document
    from app.models.knowledge_asset import KnowledgeAsset

    now = datetime.utcnow()
    pid = project.id

    sprint_ids = [s.id for s in db.query(Sprint.id).filter(
        Sprint.project_id == pid, Sprint.is_deleted == False).all()]  # noqa: E712

    db.query(Sprint).filter(Sprint.project_id == pid, Sprint.is_deleted == False).update(  # noqa: E712
        {"is_deleted": True, "deleted_at": now}, synchronize_session=False)
    db.query(Module).filter(Module.project_id == pid, Module.is_deleted == False).update(  # noqa: E712
        {"is_deleted": True, "deleted_at": now}, synchronize_session=False)
    db.query(TestCase).filter(TestCase.project_id == pid, TestCase.is_deleted == False).update(  # noqa: E712
        {"is_deleted": True, "deleted_at": now}, synchronize_session=False)
    db.query(Graph).filter(Graph.project_id == pid, Graph.is_deleted == False).update(  # noqa: E712
        {"is_deleted": True, "deleted_at": now}, synchronize_session=False)
    if sprint_ids:
        db.query(FeaturePoint).filter(
            FeaturePoint.sprint_id.in_(sprint_ids), FeaturePoint.is_deleted == False).update(  # noqa: E712
            {"is_deleted": True, "deleted_at": now}, synchronize_session=False)
        db.query(Document).filter(
            Document.sprint_id.in_(sprint_ids), Document.is_deleted == False).update(  # noqa: E712
            {"is_deleted": True, "deleted_at": now}, synchronize_session=False)
    db.query(KnowledgeAsset).filter(
        KnowledgeAsset.project_id == pid, KnowledgeAsset.status != "deleted").update(
        {"status": "deleted"}, synchronize_session=False)

    project.is_deleted = True
    project.deleted_at = now
    db.commit()


def get_owner_name(db: Session, owner_id: int | None) -> str:
    if not owner_id:
        return ""
    user = db.query(User).filter(User.id == owner_id).first()
    return user.name if user else ""
