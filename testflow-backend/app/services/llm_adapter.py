"""
LLM 统一调用入口

职责：
1. 根据 task_type 查找 ModelStrategy → Provider → 调用
2. 重试逻辑（仅网络错误）
3. 调用日志记录（AICallLog）
4. 更新 Provider 状态

使用方式：
    adapter = LLMAdapter(db)
    result = adapter.call("需求文档分析", "分析以下文档...")
    # result = {content, input_tokens, output_tokens, model}
"""

import time
import httpx
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.ai_config import AIProvider, ModelStrategy, AIGlobalConfig, AICallLog
from app.services.llm_providers import get_provider_adapter, LLMCallError


class LLMAdapter:
    """统一 LLM 调用入口"""

    def __init__(self, db: Session):
        self.db = db

    # ============ 主调用方法 ============

    def call(self, task_type: str, prompt: str, **kwargs) -> dict:
        """
        根据 task_type 查找策略和 Provider，调用 LLM

        Args:
            task_type: 任务类型，如 "需求文档分析"、"测试用例生成"
            prompt: 完整的 prompt 文本

        Returns:
            {"content": str, "input_tokens": int, "output_tokens": int, "model": str}

        Raises:
            ValueError: 未找到策略或 Provider 配置
            LLMCallError: API 调用失败（重试耗尽后）
        """
        # 1. 查策略
        strategy = self._get_strategy(task_type)
        if not strategy or not strategy.provider_id:
            raise ValueError(f"任务类型 '{task_type}' 未配置服务商策略，请先在 AI 配置中设置")

        # 2. 查 Provider
        provider = self.db.query(AIProvider).filter(AIProvider.id == strategy.provider_id).first()
        if not provider:
            raise ValueError(f"服务商 ID={strategy.provider_id} 不存在")

        # 3. 读取全局配置
        timeout = self._get_global_config("timeout", 120, as_int=True)
        retries = self._get_global_config("retries", 3, as_int=True)
        max_tokens = provider.max_tokens or self._get_global_config("max_tokens", 4096, as_int=True)

        # 4. 限制 prompt 摘要长度用于日志
        request_summary = prompt[:200].replace("\n", " ") + "..." if len(prompt) > 200 else prompt[:200]

        # 5. 调用（带重试）
        adapter = get_provider_adapter(provider.provider_type)
        last_error = None
        start = time.time()

        for attempt in range(1, retries + 1):
            try:
                result = adapter.call(
                    provider=provider,
                    model_name=strategy.model_name,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
                duration_ms = int((time.time() - start) * 1000)

                # 记录成功日志
                self._log_call(
                    provider_id=provider.id,
                    task_type=task_type,
                    model=result["model"],
                    input_tokens=result["input_tokens"],
                    output_tokens=result["output_tokens"],
                    duration_ms=duration_ms,
                    status="成功",
                    request_summary=request_summary,
                )

                # 更新 Provider 状态
                self._update_provider_status(provider, "正常")

                return result

            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
                last_error = e
                if attempt < retries:
                    time.sleep(1 * attempt)  # 线性退避
                    continue
                # 重试耗尽

            except LLMCallError as e:
                last_error = e
                break  # API 返回非 200，不重试

            except Exception as e:
                last_error = e
                break  # 未知错误，不重试

        # 所有尝试失败
        duration_ms = int((time.time() - start) * 1000)
        error_msg = str(last_error)[:500] if last_error else "未知错误"

        # 判断是否超时
        log_status = "超时" if isinstance(last_error, httpx.TimeoutException) else "失败"

        self._log_call(
            provider_id=provider.id,
            task_type=task_type,
            model=strategy.model_name,
            input_tokens=0,
            output_tokens=0,
            duration_ms=duration_ms,
            status=log_status,
            error_message=error_msg,
            request_summary=request_summary,
        )

        # 更新 Provider 状态
        self._update_provider_status(provider, "错误")

        raise LLMCallError(f"LLM 调用失败（{log_status}）: {error_msg}")

    # ============ 测试连接方法 ============

    def call_with_provider(self, provider: AIProvider, prompt: str) -> dict:
        """
        直接指定 Provider 调用（用于测试连接，不经过 Strategy）

        Args:
            provider: AIProvider 实例
            prompt: 测试 prompt

        Returns:
            {"content": str, "input_tokens": int, "output_tokens": int, "model": str}
        """
        timeout = self._get_global_config("timeout", 120, as_int=True)
        max_tokens = min(provider.max_tokens or 100, 100)  # 测试时限制 token

        adapter = get_provider_adapter(provider.provider_type)
        start = time.time()
        try:
            result = adapter.call(
                provider=provider,
                model_name=provider.model,
                prompt=prompt,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            duration_ms = int((time.time() - start) * 1000)

            self._log_call(
                provider_id=provider.id,
                task_type="连接测试",
                model=result["model"],
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                duration_ms=duration_ms,
                status="成功",
            )
            self._update_provider_status(provider, "正常")
            return result

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            error_msg = str(e)[:500]
            self._log_call(
                provider_id=provider.id,
                task_type="连接测试",
                model=provider.model,
                input_tokens=0, output_tokens=0,
                duration_ms=duration_ms,
                status="失败",
                error_message=error_msg,
            )
            self._update_provider_status(provider, "错误")
            raise

    # ============ 内部方法 ============

    def _get_strategy(self, task_type: str) -> ModelStrategy | None:
        return self.db.query(ModelStrategy).filter(
            ModelStrategy.task_type == task_type
        ).first()

    def _get_global_config(self, key: str, default, as_int: bool = False):
        config = self.db.query(AIGlobalConfig).filter(AIGlobalConfig.key == key).first()
        if config:
            return int(config.value) if as_int else config.value
        return default

    def _log_call(self, *, provider_id, task_type, model,
                  input_tokens, output_tokens, duration_ms,
                  status, error_message=None, request_summary=None):
        log = AICallLog(
            provider_id=provider_id,
            task_type=task_type,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message,
            request_summary=request_summary,
        )
        self.db.add(log)
        self.db.commit()

    def _update_provider_status(self, provider: AIProvider, status: str):
        provider.status = status
        provider.last_call_at = datetime.utcnow()
        self.db.commit()
