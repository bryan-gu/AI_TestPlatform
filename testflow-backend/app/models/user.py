from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    project = Column(String(100), default="")  # 所属项目（简单文本）
    status = Column(String(20), nullable=False, default="活跃")  # 活跃/离线/待激活/禁用
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    role = relationship("Role", backref="users")
