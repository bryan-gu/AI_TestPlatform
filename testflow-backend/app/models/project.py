from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), nullable=False, default="pending")  # pending/active/testing/completed
    progress = Column(Integer, default=0)  # 0-100
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    case_prefix = Column(String(20), unique=True, nullable=True)  # 用例编号前缀，如 SPD、VAgent
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", backref="owned_projects")
