from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func
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
    report_type = Column(String(20), default="")  # 回归/冒烟/迭代/全量
    test_scope = Column(Text, default="")  # 测试范围描述
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 审批人
    approved_at = Column(DateTime, nullable=True)  # 审批时间
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="reports")
    approver = relationship("User", backref="approved_reports", foreign_keys=[approved_by])
