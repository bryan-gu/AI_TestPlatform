"""
接口模块归属推断（P0.3）

用 LLM 批量推断 module_id IS NULL 的接口归属到哪个模块，写回 module_id +
api→module/belongs_to TraceLink。让 Stage 2 的 related_apis 查询生效。

分批调用 LLM（每批 BATCH_SIZE 个接口，控制上下文），单批失败兜底不阻断。
"""
import json
import re
import logging
from sqlalchemy.orm import Session

from app.models.api_endpoint import ApiEndpoint
from app.models.module import Module
from app.crud import crud_trace_link
from app.schemas.trace_link import TraceLinkCreate
from app.services.llm_adapter import LLMAdapter
from app.services.prompts.skill_prompts import build_api_module_classify_prompt

logger = logging.getLogger(__name__)

BATCH_SIZE = 40  # 每批接口数，控制 LLM 上下文


def classify_api_modules_with_llm(db: Session, project_id: int, sprint_id: int | None = None) -> dict:
    """对项目下 module_id IS NULL 的接口，LLM 推断归属模块并写回。

    Args:
        db: 数据库会话
        project_id: 项目 ID
        sprint_id: 可选，限定 sprint 范围

    Returns:
        {"total": 待归属数, "classified": 已归属数, "undetermined": 未确定数,
         "batches": 批次数, "skipped"?: 跳过原因, "error"?: 错误}
    """
    # 1. 查项目模块列表
    modules = db.query(Module).filter(
        Module.project_id == project_id,
        Module.is_deleted == False,  # noqa: E712
    ).all()
    if not modules:
        return {"skipped": "项目下无模块，无法归属", "total": 0, "classified": 0}

    modules_for_prompt = [{"id": m.id, "name": m.name, "code": m.code or ""} for m in modules]
    module_id_set = {m.id for m in modules}

    # 2. 查待归属接口（module_id IS NULL）
    query = db.query(ApiEndpoint).filter(
        ApiEndpoint.project_id == project_id,
        ApiEndpoint.module_id.is_(None),
        ApiEndpoint.is_deleted == False,  # noqa: E712
    )
    if sprint_id is not None:
        query = query.filter(ApiEndpoint.sprint_id == sprint_id)
    endpoints = query.all()

    if not endpoints:
        return {"skipped": "无待归属接口（module_id 均已填充）", "total": 0, "classified": 0}

    adapter = LLMAdapter(db)
    classified = 0
    undetermined = 0
    batches = 0

    # 3. 分批 LLM 推断
    for i in range(0, len(endpoints), BATCH_SIZE):
        batch = endpoints[i:i + BATCH_SIZE]
        apis_for_prompt = [
            {
                "id": ep.id,
                "method": ep.method or "",
                "path": ep.path or "",
                "summary": ep.summary or "",
                "tag": ep.tag or "",
            }
            for ep in batch
        ]
        prompt = build_api_module_classify_prompt(modules_for_prompt, apis_for_prompt)
        batches += 1
        try:
            result = _call_classify_llm(adapter, prompt)
            mappings = _parse_mappings(result.get("content", ""))
        except Exception as e:
            logger.warning(f"接口归属推断 batch {batches} 失败: {e}")
            undetermined += len(batch)
            continue

        # 4. 写回 module_id + TraceLink
        mapping_by_api = {m.get("api_id"): m for m in mappings if m.get("api_id") is not None}
        for ep in batch:
            m = mapping_by_api.get(ep.id)
            if not m:
                undetermined += 1
                continue
            mod_id = m.get("module_id")
            if mod_id is None or mod_id not in module_id_set:
                undetermined += 1
                continue
            ep.module_id = mod_id
            classified += 1
            crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
                project_id=project_id,
                sprint_id=ep.sprint_id,
                source_type="api",
                source_id=ep.id,
                target_type="module",
                target_id=mod_id,
                relation_type="belongs_to",
                confidence=m.get("confidence", 80),
                evidence=m.get("reason", "") or "LLM 推断接口归属模块",
                metadata={"classifier": "llm", "stage": "api_classify"},
                created_by="api-module-classifier",
            ), commit=False)
        db.commit()

    return {
        "total": len(endpoints),
        "classified": classified,
        "undetermined": undetermined,
        "batches": batches,
    }


def _call_classify_llm(adapter, prompt: str) -> dict:
    """调用 LLM 做接口归属推断。优先专门 task_type，未配置则 fallback 到接口相关/通用 task_type，
    避免要求用户必须为新任务类型单独配置策略。"""
    for task_type in ("接口模块归属推断", "接口用例覆盖映射", "测试用例生成", "需求文档分析"):
        try:
            return adapter.call(task_type, prompt)
        except ValueError as e:
            if "未配置" in str(e):
                continue
            raise
    raise ValueError("无可用 LLM 策略：接口模块归属推断/接口用例覆盖映射/测试用例生成/需求文档分析 均未配置，请先在 AI 配置中设置")


def _parse_mappings(content: str) -> list[dict]:
    """从 LLM 回复解析 mappings 数组。"""
    if not content:
        return []
    # 提取 JSON 块（优先对象，其次数组）
    text = content.strip()
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    else:
        mobj = re.search(r'\{[\s\S]*\}', text) or re.search(r'\[[\s\S]*\]', text)
        if not mobj:
            return []
        text = mobj.group(0)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 尝试移除尾随逗号
        try:
            data = json.loads(re.sub(r',\s*([}\]])', r'\1', text))
        except json.JSONDecodeError:
            return []
    if isinstance(data, dict):
        for key in ("mappings", "data", "results", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return []
    if isinstance(data, list):
        return data
    return []
