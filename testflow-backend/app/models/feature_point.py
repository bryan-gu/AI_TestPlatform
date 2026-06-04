from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class FeaturePoint(Base):
    __tablename__ = "feature_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    source_doc_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    linked_cases = Column(String(200), default="")  # "TC-001~TC-005"
    graph_node_id = Column(Integer, nullable=True)  # Phase 5 知识图谱预留
    created_at = Column(DateTime, server_default=func.now())

    document = relationship("Document", backref="feature_points")
    sprint = relationship("Sprint", backref="feature_points")
    module = relationship("Module", backref="feature_points")
