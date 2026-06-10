from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TraceLink(Base):
    __tablename__ = "trace_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)

    source_type = Column(String(40), nullable=False)
    source_id = Column(Integer, nullable=False)
    target_type = Column(String(40), nullable=False)
    target_id = Column(Integer, nullable=False)
    relation_type = Column(String(40), nullable=False)

    confidence = Column(Integer, default=100)
    evidence = Column(Text, default="")
    link_metadata = Column("metadata", JSON, default=dict)
    status = Column(String(30), default="active")
    created_by = Column(String(30), default="system")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", backref="trace_links")
    sprint = relationship("Sprint", backref="trace_links")
