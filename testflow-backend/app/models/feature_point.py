from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class FeaturePoint(Base):
    __tablename__ = "feature_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    entry_path = Column(Text, default="")
    interaction_elements = Column(Text, default="")
    business_rules = Column(Text, default="")
    priority = Column(String(10), default="中")
    source_doc_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    source_asset_id = Column(Integer, ForeignKey("knowledge_assets.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    linked_cases = Column(String(200), default="")  # "TC-001~TC-005"
    graph_node_id = Column(Integer, nullable=True)  # Phase 5 知识图谱预留
    source_type = Column(String(30), default="manual")
    status = Column(String(30), default="active")
    version = Column(String(40), default="v1.0")
    fingerprint = Column(String(64), default="")
    raw_data = Column(JSON, default=dict)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    document = relationship("Document", backref="feature_points")
    source_asset = relationship("KnowledgeAsset", backref="feature_points")
    sprint = relationship("Sprint", backref="feature_points")
    module = relationship("Module", backref="feature_points")
