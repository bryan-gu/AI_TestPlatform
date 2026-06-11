"""OpenAPI / Swagger 文档解析服务"""

import json
import hashlib
from pathlib import Path

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head", "trace"}


def build_endpoint_fingerprint(
    project_id: int | None,
    source_asset_id: int | None,
    method: str,
    path: str,
    operation_id: str = "",
) -> str:
    """生成接口端点幂等指纹"""
    raw = f"{project_id or 0}:{source_asset_id or 0}:{method.upper()}:{path}:{operation_id}"
    return hashlib.md5(raw.encode()).hexdigest()


def parse_openapi_file(file_path: str) -> list[dict]:
    """从文件路径读取并解析 OpenAPI 文档"""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return parse_openapi_data(data)


def parse_openapi_data(data: dict) -> list[dict]:
    """
    解析 OpenAPI 3.x 或 Swagger 2.0 数据，返回接口端点列表。
    每个元素为一个可直接传入 ApiEndpointCreate 的字典。
    """
    if not isinstance(data, dict):
        raise ValueError("文档数据不是有效的 JSON 对象")

    # 检测版本
    is_openapi3 = "openapi" in data and data["openapi"].startswith("3")
    is_swagger2 = data.get("swagger") == "2.0"

    if not is_openapi3 and not is_swagger2:
        raise ValueError("不支持的 API 文档格式，需要 OpenAPI 3.x 或 Swagger 2.0")

    paths = data.get("paths", {})
    if not paths:
        return []

    endpoints = []
    for url_path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        # path-level parameters
        path_level_params = path_item.get("parameters", [])

        for method in HTTP_METHODS:
            operation = path_item.get(method)
            if not operation or not isinstance(operation, dict):
                continue

            endpoint = _extract_endpoint(url_path, method, operation, path_level_params, is_openapi3)
            endpoints.append(endpoint)

    return endpoints


def _extract_endpoint(
    path: str,
    method: str,
    operation: dict,
    path_level_params: list,
    is_openapi3: bool,
) -> dict:
    """从单个 operation 提取接口端点信息"""
    # 基本信息
    summary = operation.get("summary", "")
    description = operation.get("description", "")
    operation_id = operation.get("operationId", "")
    tags = operation.get("tags", [])
    tag = tags[0] if tags else ""

    # 是否需要认证
    security = operation.get("security")
    auth_required = security is not None if security is not None else None

    # Parameters（合并 path-level 和 operation-level）
    op_params = operation.get("parameters", [])
    parameters = extract_parameters(path_level_params, op_params)

    # Request Schema
    request_schema = extract_request_schema(operation, is_openapi3)

    # Response Schema
    response_schema = extract_response_schema(operation)

    # Error Codes
    error_codes = _extract_error_codes(operation)

    # raw_data 保留原始 operation + path-level 信息
    raw_data = {**operation}
    if path_level_params:
        raw_data["_path_level_parameters"] = path_level_params

    return {
        "method": method.upper(),
        "path": path,
        "summary": summary,
        "description": description,
        "tag": tag,
        "operation_id": operation_id,
        "status": "active",
        "priority": "中",
        "auth_required": auth_required,
        "request_schema": request_schema,
        "response_schema": response_schema,
        "parameters": parameters,
        "error_codes": error_codes,
        "version": "v1",
        "raw_data": raw_data,
    }


def extract_request_schema(operation: dict, is_openapi3: bool) -> dict:
    """提取请求体 Schema"""
    if is_openapi3:
        body = operation.get("requestBody", {})
        if not body:
            return {}
        content = body.get("content", {})
        # 优先 JSON
        for ct in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data"):
            media = content.get(ct, {})
            schema = media.get("schema", {})
            if schema:
                return schema
        return {}
    else:
        # Swagger 2.0: body parameter
        for param in operation.get("parameters", []):
            if param.get("in") == "body":
                return param.get("schema", {})
        return {}


def extract_response_schema(operation: dict) -> dict:
    """提取响应 Schema（优先 200 / 201 / default）"""
    responses = operation.get("responses", {})
    if not responses:
        return {}
    # 优先级: 200 > 201 > 2XX > default
    for code in ("200", "201", "2XX", "default"):
        resp = responses.get(code)
        if resp and isinstance(resp, dict):
            content = resp.get("content", {})
            for ct in ("application/json",):
                media = content.get(ct, {})
                schema = media.get("schema", {})
                if schema:
                    return schema
            # Swagger 2.0
            schema = resp.get("schema", {})
            if schema:
                return schema
    return {}


def extract_parameters(path_level_params: list, op_params: list) -> list:
    """合并 path-level 和 operation-level parameters"""
    merged = {}
    for p in path_level_params:
        key = f"{p.get('in', '')}:{p.get('name', '')}"
        merged[key] = p
    for p in op_params:
        key = f"{p.get('in', '')}:{p.get('name', '')}"
        merged[key] = p  # operation-level 覆盖 path-level
    return list(merged.values())


def _extract_error_codes(operation: dict) -> list:
    """提取错误码列表"""
    responses = operation.get("responses", {})
    error_codes = []
    for code, resp in responses.items():
        if code.startswith("4") or code.startswith("5"):
            desc = resp.get("description", "") if isinstance(resp, dict) else ""
            error_codes.append({"code": code, "description": desc})
    return error_codes
