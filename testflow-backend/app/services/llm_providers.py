"""
LLM 服务商适配器

统一调用接口，每个 Provider 返回 {content, input_tokens, output_tokens, model}
"""

import httpx


class OpenAIProvider:
    """OpenAI 兼容服务商（含 DeepSeek、自定义端点）"""

    def call(self, provider, model_name: str, prompt: str,
             max_tokens: int = 4096, timeout: int = 120) -> dict:
        endpoint = provider.endpoint_url or "https://api.openai.com"
        url = f"{endpoint.rstrip('/')}/v1/chat/completions"

        resp = httpx.post(
            url,
            headers={"Authorization": f"Bearer {provider.api_key}"},
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
            },
            timeout=timeout,
        )

        if resp.status_code != 200:
            raise LLMCallError(f"OpenAI API 返回 {resp.status_code}: {resp.text[:500]}")

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return {
            "content": content,
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "model": data.get("model", model_name),
        }


class AnthropicProvider:
    """Anthropic Claude 系列"""

    def call(self, provider, model_name: str, prompt: str,
             max_tokens: int = 4096, timeout: int = 120) -> dict:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": provider.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model_name,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )

        if resp.status_code != 200:
            raise LLMCallError(f"Anthropic API 返回 {resp.status_code}: {resp.text[:500]}")

        data = resp.json()
        content = data["content"][0]["text"]
        usage = data.get("usage", {})
        return {
            "content": content,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "model": data.get("model", model_name),
        }


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek — 兼容 OpenAI 格式，默认 endpoint 不同"""

    def call(self, provider, model_name: str, prompt: str,
             max_tokens: int = 4096, timeout: int = 120) -> dict:
        # DeepSeek 未配置 endpoint 时使用默认值
        if not provider.endpoint_url:
            provider.endpoint_url = "https://api.deepseek.com"
        return super().call(provider, model_name, prompt, max_tokens, timeout)


class CustomProvider(OpenAIProvider):
    """自定义服务商 — 兼容 OpenAI 格式，endpoint 由用户配置"""
    pass


class LLMCallError(Exception):
    """LLM 调用异常"""
    pass


# 服务商类型 → Provider 类映射
PROVIDER_MAP = {
    "OpenAI": OpenAIProvider,
    "Anthropic": AnthropicProvider,
    "DeepSeek": DeepSeekProvider,
    "Custom": CustomProvider,
}


def get_provider_adapter(provider_type: str):
    """根据服务商类型获取适配器实例"""
    cls = PROVIDER_MAP.get(provider_type, CustomProvider)
    return cls()
