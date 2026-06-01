from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate


def get_roles(db: Session) -> list[Role]:
    return db.query(Role).all()


def get_role(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()


def create_role(db: Session, data: RoleCreate) -> Role:
    role = Role(name=data.name, permissions=data.permissions, type="自定义", is_editable=True)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role: Role, data: RoleUpdate) -> Role:
    if data.name is not None:
        role.name = data.name
    if data.permissions is not None:
        role.permissions = data.permissions
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: Role) -> None:
    db.delete(role)
    db.commit()


def get_role_stats(db: Session) -> dict:
    total = db.query(Role).count()
    built_in = db.query(Role).filter(Role.type == "内置").count()
    # 统计权限数量（去重）
    roles = db.query(Role).all()
    all_perms = set()
    for r in roles:
        if r.permissions:
            all_perms.update(r.permissions)
    return {"totalRoles": total, "builtInRoles": built_in, "totalPermissions": len(all_perms)}


def get_member_count(db: Session, role_id: int) -> int:
    return db.query(User).filter(User.role_id == role_id).count()
