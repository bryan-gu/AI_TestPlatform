from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    file_path = Column(String(500), default="")
    file_type = Column(String(20), default="")  # PDF/Word/Markdown/Excel
    file_size = Column(Integer, default=0)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=False)  # 直接挂在 Sprint 下
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    version = Column(String(20), default="v1.0")
    content_preview = Column(Text, default="")
    ai_summary = Column(Text, default="")
    keywords = Column(JSON, default=list)
    module_ids = Column(JSON, default=list)  # AI 识别的模块 ID 列表，如 [1, 3, 5]
    ai_status = Column(String(20), default="待分析")  # 已分析/分析中/待分析
    created_at = Column(DateTime, server_default=func.now())

    uploader = relationship("User", backref="uploaded_documents")
