from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


def get_users(db: Session, keyword: str | None = None) -> list[User]:
    query = db.query(User)
    if keyword:
        query = query.filter(
            or_(
                User.name.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%")
            )
        )
    return query.all()


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role_id=data.role_id,
        project=data.project,
        status=data.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    if data.name is not None:
        user.name = data.name
    if data.role_id is not None:
        user.role_id = data.role_id
    if data.project is not None:
        user.project = data.project
    if data.status is not None:
        user.status = data.status
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def update_last_login(db: Session, user: User) -> None:
    user.last_login = datetime.now(timezone.utc)
    db.commit()


def get_user_stats(db: Session) -> dict:
    total = db.query(User).count()
    active = db.query(User).filter(User.status == "活跃").count()
    disabled = db.query(User).filter(User.status == "禁用").count()
    pending = db.query(User).filter(User.status == "待激活").count()
    # 本月新增
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_users = db.query(User).filter(User.created_at >= month_start).count()
    return {
        "totalUsers": total,
        "newUsers": new_users,
        "activeUsers": active,
        "onlineToday": active,  # 简化处理
        "disabledUsers": disabled,
        "pendingUsers": pending,
    }
