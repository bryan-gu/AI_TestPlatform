from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ChangeItem(Base):
    """Sprint 增量变更项"""
    __tablename__ = "change_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=False)
    source_doc_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    source_asset_id = Column(Integer, ForeignKey("knowledge_assets.id"), nullable=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)

    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    change_type = Column(String(30), default="unknown")  # added / modified / removed / deprecated / unknown
    target_type = Column(String(40), default="feature")   # feature / api / testcase / module / document / asset
    target_id = Column(Integer, nullable=True)

    priority = Column(String(10), default="中")
    impact_level = Column(String(10), default="中")
    status = Column(String(30), default="open")           # open / confirmed / ignored / resolved

    before_snapshot = Column(JSON, default=dict)
    after_snapshot = Column(JSON, default=dict)
    evidence = Column(Text, default="")
    confidence = Column(Integer, default=80)
    fingerprint = Column(String(200), default="")
    raw_data = Column(JSON, default=dict)

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", backref="change_items")
    sprint = relationship("Sprint", backref="change_items")
    source_doc = relationship("Document", backref="change_items")
    source_asset = relationship("KnowledgeAsset", backref="change_items")
    module = relationship("Module", backref="change_items")
