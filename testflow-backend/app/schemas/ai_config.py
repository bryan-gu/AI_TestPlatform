from datetime import datetime
from pydantic import BaseModel


# ============ AIProvider ============

class AIProviderCreate(BaseModel):
    provider_type: str  # OpenAI/Anthropic/DeepSeek/Custom
    name: str
    api_key: str
    model: str
    endpoint_url: str | None = None
    temperature: float = 0.3
    max_tokens: int = 4096


class AIProviderUpdate(BaseModel):
    provider_type: str | None = None
    name: str | None = None
    api_key: str | None = None
    model: str | None = None
    endpoint_url: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    status: str | None = None


class AIProviderOut(BaseModel):
    id: int
    provider_type: str
    name: str
    api_key_masked: str = ""  # 脱敏后的 API Key
    model: str
    endpoint_url: str | None = None
    temperature: float = 0.3
    max_tokens: int = 4096
    status: str = "正常"
    last_call_at: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


# ============ ModelStrategy ============

class ModelStrategyUpdate(BaseModel):
    """单条策略更新"""
    task_type: str
    provider_id: int | None = None
    model_name: str
    temperature: float = 0.3


class ModelStrategyBatchUpdate(BaseModel):
    """批量更新策略"""
    strategies: list[ModelStrategyUpdate]


class ModelStrategyOut(BaseModel):
    id: int
    task_type: str
    provider_id: int | None = None
    model_name: str
    temperature: float = 0.3
    provider_name: str = ""  # computed

    class Config:
        from_attributes = True


# ============ AIGlobalConfig ============

class AIGlobalConfigUpdate(BaseModel):
    """单个参数更新"""
    key: str
    value: str


class AIGlobalConfigBatchUpdate(BaseModel):
    """批量更新全局参数"""
    configs: list[AIGlobalConfigUpdate]


class AIGlobalConfigOut(BaseModel):
    id: int
    key: str
    value: str
    label: str = ""  # computed: 中文标签

    class Config:
        from_attributes = True


# ============ AICallLog ============

class AICallLogOut(BaseModel):
    id: int
    task_type: str | None = None
    model: str | None = None
    provider_id: int | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    status: str = "成功"
    created_at: datetime | None = None
    provider_name: str = ""  # computed

    class Config:
        from_attributes = True


# ============ Stats ============

class AIStatsOut(BaseModel):
    configured_models: int = 0
    monthly_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    avg_duration_ms: int = 0
