from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class PipelineExecution(Base):
    __tablename__ = "pipeline_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    mode = Column(String(20), nullable=False, default="full")  # full / incremental
    status = Column(String(20), nullable=False, default="waiting")  # waiting/running/paused/completed/failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    total_duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="pipeline_executions")
    sprint = relationship("Sprint", backref="pipeline_executions")
    stages = relationship("PipelineStage", backref="execution", cascade="all, delete-orphan",
                          order_by="PipelineStage.stage_no")


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("pipeline_executions.id"), nullable=False)
    stage_no = Column(Integer, nullable=False)  # 1~4
    stage_name = Column(String(50), nullable=False)  # 需求分析/测试用例生成/E2E脚本生成/执行与自愈
    status = Column(String(20), nullable=False, default="waiting")  # waiting/running/completed/failed
    model = Column(String(100), nullable=True)  # 使用的 AI 模型名称
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    duration_ms = Column(Integer, nullable=True)
    result_summary = Column(JSON, default=dict)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
