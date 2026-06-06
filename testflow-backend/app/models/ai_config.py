from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIProvider(Base):
    """AI 服务商配置"""
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_type = Column(String(50), nullable=False, comment="服务商类型: OpenAI/Anthropic/DeepSeek/Custom")
    name = Column(String(100), nullable=False, comment="显示名称")
    api_key = Column(String(500), nullable=False, comment="API Key（加密存储）")
    model = Column(String(100), nullable=False, comment="模型名称，如 gpt-4o")
    endpoint_url = Column(String(500), nullable=True, comment="自定义端点 URL")
    max_tokens = Column(Integer, default=4096, comment="最大 Token 数")
    status = Column(String(20), default="正常", comment="状态: 正常/限流/错误")
    last_call_at = Column(DateTime, nullable=True, comment="最近调用时间")
    created_at = Column(DateTime, server_default=func.now())

    # relationships
    strategies = relationship("ModelStrategy", backref="provider")
    call_logs = relationship("AICallLog", backref="provider")


class ModelStrategy(Base):
    """模型分配策略 — 每种任务类型一条"""
    __tablename__ = "model_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(50), unique=True, nullable=False, comment="任务类型: 需求文档分析/测试用例生成/自动化脚本生成/知识图谱关联/测试报告摘要")
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True, comment="关联服务商")
    model_name = Column(String(100), nullable=False, comment="使用的模型名称")


class AIGlobalConfig(Base):
    """AI 全局参数配置"""
    __tablename__ = "ai_global_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, comment="参数键名")
    value = Column(Text, nullable=False, comment="参数值")


class AICallLog(Base):
    """AI 调用日志"""
    __tablename__ = "ai_call_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(50), nullable=True, comment="任务类型")
    model = Column(String(100), nullable=True, comment="调用的模型")
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True, comment="关联服务商")
    input_tokens = Column(Integer, default=0, comment="输入 Token 数")
    output_tokens = Column(Integer, default=0, comment="输出 Token 数")
    duration_ms = Column(Integer, default=0, comment="耗时（毫秒）")
    status = Column(String(20), default="成功", comment="状态: 成功/失败/超时")
    error_message = Column(Text, nullable=True, comment="错误信息")
    request_summary = Column(String(500), nullable=True, comment="请求摘要")
    created_at = Column(DateTime, server_default=func.now())
