from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, func

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    type = Column(String(20), nullable=False, default="自定义")  # 内置 / 自定义
    permissions = Column(JSON, nullable=False, default=list)
    is_editable = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
