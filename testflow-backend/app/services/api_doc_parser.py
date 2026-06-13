"""OpenAPI / Swagger 文档解析服务"""

import json
import re
import hashlib
from pathlib import Path

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head", "trace"}

# Markdown 表头别名 → 规范字段
_MD_HEADER_ALIASES = {
    "method": {"method", "方法", "请求方法", "http method", "请求类型", "类型", "verb"},
    "path": {"path", "路径", "接口地址", "接口路径", "url", "地址", "endpoint"},
    "summary": {"summary", "说明", "描述", "简介", "接口说明", "名称", "接口名", "name", "title"},
    "status": {"status", "状态", "接口状态"},
    "priority": {"priority", "优先级"},
    "tag": {"tag", "标签", "模块", "分类"},
    "operation_id": {"operationid", "operation_id", "operation id", "接口id", "id"},
}

_STATUS_MAP = {
    "现有": "active", "已实现": "active", "active": "active", "已完成": "active",
    "待开发": "planned", "计划": "planned", "planned": "planned", "todo": "planned",
    "待确认": "pending", "待定": "pending", "pending": "pending",
    "废弃": "deprecated", "弃用": "deprecated", "deprecated": "deprecated",
}

_PRIORITY_MAP = {
    "p0": "高", "p1": "高", "高": "高", "high": "高",
    "p2": "中", "中": "中", "medium": "中",
    "p3": "低", "低": "低", "low": "低",
}

_METHOD_RE = re.compile(
    r"\b(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD|TRACE)\b",
    re.IGNORECASE,
)
_PATH_RE = re.compile(r"(/[\w\-./{}:]+)")
_METHOD_PATH_RE = re.compile(
    r"\b(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD|TRACE)\b\s*(/[\w\-./{}:]+)",
    re.IGNORECASE,
)



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


# ============ Markdown 接口文档解析 ============

def parse_markdown_file(file_path: str) -> tuple[list, list]:
    """从文件读取 Markdown 接口文档并解析，返回 (endpoints, warnings)。"""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_markdown_api_text(text)


def parse_markdown_api_text(text: str) -> tuple[list, list]:
    """
    解析 Markdown 接口文档，返回 (endpoints, warnings)。

    解析顺序：
    1. 优先解析 Markdown 表格（识别 方法/路径/说明/状态/优先级 表头）。
    2. 其次扫描文本行中的 `METHOD /path` 模式。

    对无法识别 method/path 的行不强行猜测，记入 warnings。
    """
    if not text or not text.strip():
        return [], ["文档内容为空"]

    endpoints: list = []
    warnings: list = []

    # 1. 表格解析
    table_endpoints, table_warnings, table_hit = _parse_markdown_tables(text)
    endpoints.extend(table_endpoints)
    warnings.extend(table_warnings)

    # 2. 文本行扫描（仅当表格未命中时启用，避免重复）
    if not table_hit:
        line_endpoints, line_warnings = _parse_markdown_lines(text)
        endpoints.extend(line_endpoints)
        warnings.extend(line_warnings)

    if not endpoints:
        warnings.append("未能从文档中识别出任何 method + path 的接口")

    return endpoints, warnings


def _parse_markdown_tables(text: str) -> tuple[list, list, bool]:
    """解析 Markdown 表格，返回 (endpoints, warnings, table_hit)。"""
    lines = text.splitlines()
    endpoints: list = []
    warnings: list = []
    i = 0
    table_hit = False

    while i < len(lines):
        if "|" not in lines[i]:
            i += 1
            continue

        # 收集连续的表格行块
        block: list = []
        while i < len(lines) and "|" in lines[i] and lines[i].strip():
            block.append(lines[i])
            i += 1

        result = _parse_one_table(block)
        if result is None:
            # 不是接口表格，跳过该块
            continue

        table_hit = True
        block_endpoints, block_warnings = result
        endpoints.extend(block_endpoints)
        warnings.extend(block_warnings)

    return endpoints, warnings, table_hit


def _parse_one_table(block: list) -> tuple[list, list] | None:
    """解析单个表格块，若不是接口表格返回 None。"""
    if len(block) < 2:
        return None

    # 解析每行的单元格
    rows = [_split_md_row(line) for line in block]
    # 定位表头行（含 method + path 语义列）
    header_idx = -1
    col_map: dict = {}
    for idx, cells in enumerate(rows):
        cmap = _match_header(cells)
        if "method" in cmap and "path" in cmap:
            header_idx = idx
            col_map = cmap
            break
    if header_idx == -1:
        return None

    endpoints: list = []
    warnings: list = []
    # 数据行：跳过分隔行（如 |---|---|）和表头之前的行
    for cells in rows[header_idx + 1:]:
        if not cells:
            continue
        if all(set(c) <= set("-: ") for c in cells):  # 分隔行
            continue
        ep = _build_endpoint_from_row(cells, col_map)
        if ep:
            endpoints.append(ep)
        else:
            preview = " ".join(cells).strip()[:60]
            warnings.append(f"表格行无法识别 method/path：{preview}")
    return endpoints, warnings


def _split_md_row(line: str) -> list:
    """拆分 Markdown 表格行为单元格列表（去除首尾空管道）。"""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _match_header(cells: list) -> dict:
    """匹配表头单元格到规范字段，返回 {字段: 列索引}。"""
    cmap: dict = {}
    for idx, raw in enumerate(cells):
        key = re.sub(r"\s+", "", raw).lower()
        if not key:
            continue
        for field, aliases in _MD_HEADER_ALIASES.items():
            if key in aliases and field not in cmap:
                cmap[field] = idx
                break
    return cmap


def _build_endpoint_from_row(cells: list, col_map: dict) -> dict | None:
    """从表格数据行 + 列映射构建接口端点字典。"""
    def cell(field: str) -> str:
        idx = col_map.get(field)
        return cells[idx] if idx is not None and idx < len(cells) else ""

    method_raw = cell("method")
    path_raw = cell("path")
    summary = cell("summary")
    status_raw = cell("status")
    priority_raw = cell("priority")
    tag = cell("tag")
    operation_id = cell("operation_id")

    method = _extract_method(method_raw)
    path = _extract_path(path_raw)

    # method 和 path 可能在同一单元格（如 "GET /api/users"）
    if (not method or not path) and (method_raw or path_raw):
        combined = f"{method_raw} {path_raw}".strip()
        m = _METHOD_PATH_RE.search(combined)
        if m:
            method = method or m.group(1).upper()
            path = path or m.group(2)

    if not method or not path:
        return None

    return {
        "method": method.upper(),
        "path": path,
        "summary": summary,
        "description": summary,
        "tag": tag,
        "operation_id": operation_id,
        "status": _map_status(status_raw) or "active",
        "priority": _map_priority(priority_raw) or "中",
        "auth_required": None,
        "request_schema": {},
        "response_schema": {},
        "parameters": [],
        "error_codes": [],
        "version": "v1",
        "raw_data": {
            "source": "markdown_table",
            "raw_method": method_raw,
            "raw_path": path_raw,
            "raw_status": status_raw,
            "raw_priority": priority_raw,
        },
    }


def _parse_markdown_lines(text: str) -> tuple[list, list]:
    """扫描文本行中的 `METHOD /path` 模式。"""
    endpoints: list = []
    warnings: list = []
    seen: set = set()
    for line in text.splitlines():
        m = _METHOD_PATH_RE.search(line)
        if not m:
            continue
        method = m.group(1).upper()
        path = m.group(2)
        key = (method, path)
        if key in seen:
            continue
        seen.add(key)
        # 用行剩余文本作为 summary（去除匹配片段）
        summary = (line[:m.start()] + " " + line[m.end():]).strip(" -|\t")
        endpoints.append({
            "method": method,
            "path": path,
            "summary": summary,
            "description": summary,
            "tag": "",
            "operation_id": "",
            "status": "active",
            "priority": "中",
            "auth_required": None,
            "request_schema": {},
            "response_schema": {},
            "parameters": [],
            "error_codes": [],
            "version": "v1",
            "raw_data": {"source": "markdown_line", "raw_line": line.strip()},
        })
    if not endpoints:
        warnings.append("文本行模式扫描未识别到接口")
    return endpoints, warnings


def _extract_method(token: str) -> str | None:
    if not token:
        return None
    m = _METHOD_RE.search(token)
    return m.group(1).upper() if m else None


def _extract_path(token: str) -> str | None:
    if not token:
        return None
    m = _PATH_RE.search(token)
    return m.group(1) if m else None


def _map_status(text: str) -> str | None:
    if not text:
        return None
    key = re.sub(r"\s+", "", text).lower()
    return _STATUS_MAP.get(key)


def _map_priority(text: str) -> str | None:
    if not text:
        return None
    key = re.sub(r"\s+", "", text).lower()
    return _PRIORITY_MAP.get(key)

