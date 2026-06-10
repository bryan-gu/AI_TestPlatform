from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 如"用户认证"、"购物车"、"安全"
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # 项目级别，不隶属某个 Sprint
    code = Column(String(50), nullable=True)  # 英文缩写，如 "SJZH"、"DL"，用于用例编号
    color = Column(String(20), default="")  # 前端标签颜色，如 "#2563eb"
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="modules")
    testcases = relationship("TestCase", backref="module_ref")
