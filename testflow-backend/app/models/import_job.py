from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ImportJob(Base):
    """异步导入任务（增强项批次 4）。

    用于本地项目导入等耗时操作，后台执行 + 进度可查，避免接口超时。
    """
    __tablename__ = "import_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    root_path = Column(String(500), nullable=False)
    job_type = Column(String(40), default="local_project")
    status = Column(String(30), default="pending")  # pending/running/succeeded/failed/partial_success/cancelled
    dry_run = Column(Boolean, default=False)

    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    result_summary = Column(JSON, default=dict)
    warnings = Column(JSON, default=list)
    errors = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", backref="import_jobs")
