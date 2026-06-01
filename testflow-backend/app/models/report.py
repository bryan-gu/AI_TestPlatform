from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    pass_rate = Column(Float, default=0.0)
    defect_count = Column(Integer, default=0)
    status = Column(String(20), nullable=False, default="待审批")  # 已审批/待审批
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="reports")
