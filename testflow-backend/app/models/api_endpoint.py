from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ApiEndpoint(Base):
    """接口端点 - 从 OpenAPI 文档解析生成的一等知识实体"""
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    source_asset_id = Column(Integer, ForeignKey("knowledge_assets.id"), nullable=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)

    # HTTP 方法与路径
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    summary = Column(String(500), default="")
    description = Column(Text, default="")
    tag = Column(String(100), default="")
    operation_id = Column(String(200), default="")

    # 元信息
    status = Column(String(30), default="active")       # active / deprecated / disabled
    priority = Column(String(10), default="中")          # 高 / 中 / 低
    auth_required = Column(Boolean, default=None)        # 是否需要认证

    # Schema 信息（JSON 存储）
    request_schema = Column(JSON, default=dict)
    response_schema = Column(JSON, default=dict)
    parameters = Column(JSON, default=list)
    error_codes = Column(JSON, default=list)

    # 版本与幂等
    version = Column(String(20), default="v1")
    fingerprint = Column(String(200), default="")        # 幂等标识
    raw_data = Column(JSON, default=dict)                # 原始 operation 数据

    # 软删除
    is_deleted = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    project = relationship("Project", backref="api_endpoints")
    sprint = relationship("Sprint", backref="api_endpoints")
    source_asset = relationship("KnowledgeAsset", backref="api_endpoints")
    module = relationship("Module", backref="api_endpoints")


class TestCaseApiEndpoint(Base):
    """测试用例与接口端点的覆盖关系"""
    __tablename__ = "testcase_api_endpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    testcase_id = Column(Integer, ForeignKey("testcases.id", ondelete="CASCADE"), nullable=False)
    api_endpoint_id = Column(Integer, ForeignKey("api_endpoints.id", ondelete="CASCADE"), nullable=False)

    # 覆盖信息
    coverage_type = Column(String(30), default="functional")  # functional / negative / boundary / smoke
    confidence = Column(Integer, default=100)
    evidence = Column(Text, default="")

    created_at = Column(DateTime, server_default=func.now())

    # 关系
    testcase = relationship("TestCase", backref="api_endpoint_links")
    api_endpoint = relationship("ApiEndpoint", backref="testcase_links")
