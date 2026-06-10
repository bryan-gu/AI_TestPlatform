from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class KnowledgeAsset(Base):
    __tablename__ = "knowledge_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(200), nullable=False)
    asset_type = Column(String(40), nullable=False, default="other")
    source_kind = Column(String(40), default="uploaded")
    file_path = Column(String(500), default="")
    file_type = Column(String(40), default="")
    file_size = Column(Integer, default=0)

    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    version = Column(String(40), default="v1.0")
    status = Column(String(30), default="active")
    parse_status = Column(String(30), default="pending")

    content_hash = Column(String(64), default="")
    asset_metadata = Column("metadata", JSON, default=dict)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", backref="knowledge_assets")
    sprint = relationship("Sprint", backref="knowledge_assets")
    document = relationship("Document", backref="knowledge_assets")
    module = relationship("Module", backref="knowledge_assets")
    creator = relationship("User", backref="created_knowledge_assets")
