from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ai_config import AIProvider, ModelStrategy, AIGlobalConfig, AICallLog
from app.schemas.ai_config import (
    AIProviderCreate, AIProviderUpdate,
    ModelStrategyBatchUpdate,
    AIGlobalConfigBatchUpdate,
)


# ============ AIProvider ============

def get_providers(db: Session) -> list[AIProvider]:
    return db.query(AIProvider).order_by(AIProvider.created_at.desc()).all()


def get_provider(db: Session, provider_id: int) -> AIProvider | None:
    return db.query(AIProvider).filter(AIProvider.id == provider_id).first()


def create_provider(db: Session, data: AIProviderCreate) -> AIProvider:
    provider = AIProvider(
        provider_type=data.provider_type,
        name=data.name,
        api_key=data.api_key,
        model=data.model,
        endpoint_url=data.endpoint_url,
        max_tokens=data.max_tokens,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


def update_provider(db: Session, provider: AIProvider, data: AIProviderUpdate) -> AIProvider:
    if data.provider_type is not None:
        provider.provider_type = data.provider_type
    if data.name is not None:
        provider.name = data.name
    if data.api_key is not None:
        provider.api_key = data.api_key
    if data.model is not None:
        provider.model = data.model
    if data.endpoint_url is not None:
        provider.endpoint_url = data.endpoint_url
    if data.max_tokens is not None:
        provider.max_tokens = data.max_tokens
    if data.status is not None:
        provider.status = data.status
    db.commit()
    db.refresh(provider)
    return provider


def delete_provider(db: Session, provider: AIProvider) -> None:
    db.delete(provider)
    db.commit()


def mask_api_key(api_key: str) -> str:
    """脱敏 API Key：只显示前缀和后4位"""
    if not api_key or len(api_key) < 12:
        return "****"
    return f"{api_key[:7]}****{api_key[-4:]}"


# ============ ModelStrategy ============

TASK_TYPES = [
    "需求文档分析",
    "测试用例生成",
    "自动化脚本生成",
    "知识图谱关联",
    "测试报告摘要",
]


def get_strategies(db: Session) -> list[ModelStrategy]:
    return db.query(ModelStrategy).order_by(ModelStrategy.id).all()


def batch_update_strategies(db: Session, data: ModelStrategyBatchUpdate) -> list[ModelStrategy]:
    """批量更新策略：按 task_type 匹配"""
    for item in data.strategies:
        strategy = db.query(ModelStrategy).filter(ModelStrategy.task_type == item.task_type).first()
        if strategy:
            strategy.provider_id = item.provider_id
            strategy.model_name = item.model_name
        else:
            # 如果不存在则创建
            new_strategy = ModelStrategy(
                task_type=item.task_type,
                provider_id=item.provider_id,
                model_name=item.model_name,
            )
            db.add(new_strategy)
    db.commit()
    return db.query(ModelStrategy).order_by(ModelStrategy.id).all()


def get_provider_name(db: Session, provider_id: int | None) -> str:
    if not provider_id:
        return ""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    return provider.name if provider else ""


# ============ AIGlobalConfig ============

# 默认全局参数
DEFAULT_CONFIGS = {
    "max_tokens": "4096",
    "timeout": "60",
    "retries": "3",
    "concurrency": "5",
    "log_level": "INFO",
    # 被测系统配置（Phase B/C 使用，Phase A 先预留）
    "target_url": "",
    "test_username": "",
    "test_password": "",
    "project_prefix": "",
    # 文档解析配置
    "mineru_api_token": "",
}

# 参数 key → 中文标签
CONFIG_LABELS = {
    "max_tokens": "最大 Token 数",
    "timeout": "超时时间（秒）",
    "retries": "重试次数",
    "concurrency": "请求并发数",
    "log_level": "日志级别",
    "target_url": "被测系统地址",
    "test_username": "测试账号",
    "test_password": "测试密码",
    "project_prefix": "用例ID前缀",
    "mineru_api_token": "MinerU Token",
}

# 参数分组（前端按组展示）
CONFIG_GROUPS = {
    "max_tokens": "system",
    "timeout": "system",
    "retries": "system",
    "concurrency": "system",
    "log_level": "system",
    "target_url": "target",
    "test_username": "target",
    "test_password": "target",
    "project_prefix": "target",
    "mineru_api_token": "target",
}


def get_global_configs(db: Session) -> list[AIGlobalConfig]:
    return db.query(AIGlobalConfig).order_by(AIGlobalConfig.id).all()


def batch_update_global_configs(db: Session, data: AIGlobalConfigBatchUpdate) -> list[AIGlobalConfig]:
    """批量更新全局参数"""
    for item in data.configs:
        config = db.query(AIGlobalConfig).filter(AIGlobalConfig.key == item.key).first()
        if config:
            config.value = item.value
        else:
            new_config = AIGlobalConfig(key=item.key, value=item.value)
            db.add(new_config)
    db.commit()
    return db.query(AIGlobalConfig).order_by(AIGlobalConfig.id).all()


def seed_global_configs(db: Session) -> None:
    """插入默认全局参数种子数据"""
    for key, value in DEFAULT_CONFIGS.items():
        existing = db.query(AIGlobalConfig).filter(AIGlobalConfig.key == key).first()
        if not existing:
            db.add(AIGlobalConfig(key=key, value=value))
    db.commit()


def seed_strategies(db: Session) -> None:
    """插入默认策略种子数据"""
    for task_type in TASK_TYPES:
        existing = db.query(ModelStrategy).filter(ModelStrategy.task_type == task_type).first()
        if not existing:
            db.add(ModelStrategy(
                task_type=task_type,
                model_name="--",
            ))
    db.commit()


def get_config_label(key: str) -> str:
    return CONFIG_LABELS.get(key, key)


def get_config_group(key: str) -> str:
    return CONFIG_GROUPS.get(key, "system")


# ============ AICallLog ============

def get_call_logs(
    db: Session,
    provider_id: int | None = None,
    status: str | None = None,
    task_type: str | None = None,
    limit: int = 50,
) -> list[AICallLog]:
    query = db.query(AICallLog)
    if provider_id:
        query = query.filter(AICallLog.provider_id == provider_id)
    if status:
        query = query.filter(AICallLog.status == status)
    if task_type:
        query = query.filter(AICallLog.task_type == task_type)
    return query.order_by(AICallLog.created_at.desc()).limit(limit).all()


def create_call_log(db: Session, **kwargs) -> AICallLog:
    log = AICallLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ============ Stats ============

def get_ai_stats(db: Session) -> dict:
    """AI 配置统计：模型数、本月调用次数、Token 消耗、平均响应"""
    from datetime import datetime
    provider_count = db.query(AIProvider).count()

    # 本月调用次数
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    monthly_calls = db.query(AICallLog).filter(AICallLog.created_at >= month_start).count()

    # Token 统计
    token_result = db.query(
        func.coalesce(func.sum(AICallLog.input_tokens), 0),
        func.coalesce(func.sum(AICallLog.output_tokens), 0),
        func.coalesce(func.avg(AICallLog.duration_ms), 0),
    ).filter(AICallLog.created_at >= month_start).first()

    total_input = int(token_result[0]) if token_result else 0
    total_output = int(token_result[1]) if token_result else 0
    avg_duration = int(token_result[2]) if token_result else 0

    return {
        "configured_models": provider_count,
        "monthly_calls": monthly_calls,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "avg_duration_ms": avg_duration,
    }
