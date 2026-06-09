from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.ai_config import (
    AIProviderCreate, AIProviderUpdate, AIProviderOut,
    ModelStrategyBatchUpdate, ModelStrategyOut,
    AIGlobalConfigBatchUpdate, AIGlobalConfigOut,
    AICallLogOut, AIStatsOut,
)
from app.crud import crud_ai_config


router = APIRouter(prefix="/ai", tags=["AI 配置管理"])


# ============ Helpers ============

def _provider_to_out(p) -> dict:
    return AIProviderOut(
        id=p.id,
        provider_type=p.provider_type,
        name=p.name,
        api_key_masked=crud_ai_config.mask_api_key(p.api_key),
        model=p.model,
        endpoint_url=p.endpoint_url,
        max_tokens=p.max_tokens if p.max_tokens is not None else 4096,
        status=p.status or "正常",
        last_call_at=p.last_call_at,
        created_at=p.created_at,
    ).model_dump()


def _strategy_to_out(s, db: Session) -> dict:
    return ModelStrategyOut(
        id=s.id,
        task_type=s.task_type,
        provider_id=s.provider_id,
        model_name=s.model_name,
        provider_name=crud_ai_config.get_provider_name(db, s.provider_id),
    ).model_dump()


def _config_to_out(c) -> dict:
    return AIGlobalConfigOut(
        id=c.id,
        key=c.key,
        value=c.value,
        label=crud_ai_config.get_config_label(c.key),
        group=crud_ai_config.get_config_group(c.key),
    ).model_dump()


def _log_to_out(log, db: Session) -> dict:
    return AICallLogOut(
        id=log.id,
        task_type=log.task_type,
        model=log.model,
        provider_id=log.provider_id,
        input_tokens=log.input_tokens or 0,
        output_tokens=log.output_tokens or 0,
        duration_ms=log.duration_ms or 0,
        status=log.status or "成功",
        error_message=log.error_message,
        request_summary=log.request_summary,
        created_at=log.created_at,
        provider_name=crud_ai_config.get_provider_name(db, log.provider_id),
    ).model_dump()


# ============ Providers ============

@router.get("/providers", response_model=ResponseModel)
def list_providers(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    providers = crud_ai_config.get_providers(db)
    return ResponseModel(data=[_provider_to_out(p) for p in providers])


@router.post("/providers", response_model=ResponseModel)
def create_provider(
    data: AIProviderCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    provider = crud_ai_config.create_provider(db, data)
    return ResponseModel(data=_provider_to_out(provider), message="创建成功")


@router.put("/providers/{provider_id}", response_model=ResponseModel)
def update_provider(
    provider_id: int,
    data: AIProviderUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    provider = crud_ai_config.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="服务商不存在")
    provider = crud_ai_config.update_provider(db, provider, data)
    return ResponseModel(data=_provider_to_out(provider), message="更新成功")


@router.delete("/providers/{provider_id}", response_model=ResponseModel)
def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    provider = crud_ai_config.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="服务商不存在")
    crud_ai_config.delete_provider(db, provider)
    return ResponseModel(message="删除成功")


@router.post("/providers/{provider_id}/test", response_model=ResponseModel)
def test_provider_connection(
    provider_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """测试服务商连接 — 真实调用 LLM API"""
    provider = crud_ai_config.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="服务商不存在")

    from app.services.llm_adapter import LLMAdapter
    from app.services.llm_providers import LLMCallError

    adapter = LLMAdapter(db)
    try:
        result = adapter.call_with_provider(provider, '请回复"连接成功"两个字。')
        return ResponseModel(data={
            "success": True,
            "message": f"{provider.name} 连接测试成功",
            "model": result.get("model", provider.model),
        })
    except LLMCallError as e:
        return ResponseModel(data={
            "success": False,
            "message": f"连接失败: {str(e)}",
        })
    except Exception as e:
        return ResponseModel(data={
            "success": False,
            "message": f"连接失败: {str(e)}",
        })


# ============ Strategies ============

@router.get("/strategies", response_model=ResponseModel)
def list_strategies(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    strategies = crud_ai_config.get_strategies(db)
    return ResponseModel(data=[_strategy_to_out(s, db) for s in strategies])


@router.put("/strategies", response_model=ResponseModel)
def batch_update_strategies(
    data: ModelStrategyBatchUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    strategies = crud_ai_config.batch_update_strategies(db, data)
    return ResponseModel(data=[_strategy_to_out(s, db) for s in strategies], message="策略更新成功")


# ============ Global Config ============

@router.get("/config", response_model=ResponseModel)
def get_global_config(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    configs = crud_ai_config.get_global_configs(db)
    return ResponseModel(data=[_config_to_out(c) for c in configs])


@router.put("/config", response_model=ResponseModel)
def update_global_config(
    data: AIGlobalConfigBatchUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    configs = crud_ai_config.batch_update_global_configs(db, data)
    return ResponseModel(data=[_config_to_out(c) for c in configs], message="全局参数更新成功")


# ============ Call Logs ============

@router.get("/call-logs", response_model=ResponseModel)
def list_call_logs(
    provider_id: int | None = Query(None),
    status: str | None = Query(None),
    task_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    logs = crud_ai_config.get_call_logs(db, provider_id=provider_id, status=status, task_type=task_type, limit=limit)
    return ResponseModel(data=[_log_to_out(log, db) for log in logs])


# ============ Stats ============

@router.get("/stats", response_model=ResponseModel)
def get_ai_stats(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    stats = crud_ai_config.get_ai_stats(db)
    return ResponseModel(data=stats)
