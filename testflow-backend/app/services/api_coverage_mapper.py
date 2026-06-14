"""接口-用例智能覆盖映射服务（增强项批次 6 子项 C）。

用 LLM 判断 Sprint 内测试用例是否覆盖某接口，自动补齐 tests_api 关系。
- 已有 TestCaseApiEndpoint 或 tests_api TraceLink 的对不再重复映射。
- LLM 失败时返回 error，不阻断（保留现有关系）。
- 只接受 LLM 返回的、且 id 在本次候选范围内的映射，防止幻觉 id。
"""
import json
import re
import logging

from sqlalchemy.orm import Session

from app.models.api_endpoint import ApiEndpoint, TestCaseApiEndpoint
from app.models.testcase import TestCase
from app.models.trace_link import TraceLink
from app.crud import crud_trace_link, crud_api_endpoint
from app.schemas.trace_link import TraceLinkCreate
from app.schemas.api_endpoint import TestCaseApiEndpointCreate
from app.services.llm_adapter import LLMAdapter
from app.services.prompts.skill_prompts import build_api_coverage_prompt

logger = logging.getLogger(__name__)

MAX_ENDPOINTS = 60
MAX_TESTCASES = 60
MIN_CONFIDENCE = 60


def _extract_json(content: str) -> dict | None:
    if not content:
        return None
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _existing_pairs(db: Session, sprint_id: int) -> set[tuple[int, int]]:
    """已存在的 (testcase_id, api_id) 覆盖对。"""
    pairs: set[tuple[int, int]] = set()
    for r in db.query(TestCaseApiEndpoint.testcase_id, TestCaseApiEndpoint.api_endpoint_id).all():
        pairs.add((r[0], r[1]))
    for r in db.query(TraceLink.source_id, TraceLink.target_id).filter(
        TraceLink.sprint_id == sprint_id,
        TraceLink.source_type == "testcase",
        TraceLink.target_type == "api",
        TraceLink.relation_type == "tests_api",
        TraceLink.status == "active",
    ).all():
        pairs.add((r[0], r[1]))
    return pairs


def map_coverage_with_llm(db: Session, sprint_id: int) -> dict:
    """LLM 智能映射 Sprint 内 testcase↔api 覆盖关系，写 tests_api + TestCaseApiEndpoint。"""
    endpoints = db.query(ApiEndpoint).filter(
        ApiEndpoint.sprint_id == sprint_id,
        ApiEndpoint.is_deleted == False,  # noqa: E712
    ).order_by(ApiEndpoint.path).limit(MAX_ENDPOINTS).all()
    testcases = db.query(TestCase).filter(
        TestCase.sprint_id == sprint_id,
        TestCase.is_deleted == False,  # noqa: E712
    ).limit(MAX_TESTCASES).all()

    base = {
        "mapped": 0,
        "total_endpoints": len(endpoints),
        "total_testcases": len(testcases),
        "candidates_considered": 0,
    }
    if not endpoints or not testcases:
        base["skipped"] = "Sprint 内无接口或用例"
        return base

    project_id = endpoints[0].project_id
    ep_data = [
        {"id": e.id, "method": e.method, "path": e.path, "summary": (e.summary or "")[:120], "tag": e.tag or ""}
        for e in endpoints
    ]
    tc_data = [
        {"id": t.id, "case_no": t.case_no, "title": t.title, "steps": (t.test_steps or "")[:200]}
        for t in testcases
    ]

    prompt = build_api_coverage_prompt(ep_data, tc_data)
    try:
        adapter = LLMAdapter(db)
        result = adapter.call("接口用例覆盖映射", prompt)
        parsed = _extract_json(result.get("content", ""))
    except Exception as e:
        logger.warning("LLM 接口覆盖映射失败: %s", e)
        base["error"] = str(e)
        return base

    mappings = (parsed or {}).get("mappings", []) if isinstance(parsed, dict) else []
    base["candidates_considered"] = len(mappings)

    tc_ids = {t.id for t in testcases}
    ep_ids = {e.id for e in endpoints}
    existing = _existing_pairs(db, sprint_id)

    mapped = 0
    for m in mappings:
        if not isinstance(m, dict):
            continue
        tc_id = m.get("testcase_id")
        ep_id = m.get("api_id")
        conf = m.get("confidence", 80)
        try:
            conf = int(conf)
        except (TypeError, ValueError):
            conf = 80
        if conf < MIN_CONFIDENCE:
            continue
        if tc_id not in tc_ids or ep_id not in ep_ids:
            continue
        if (tc_id, ep_id) in existing:
            continue
        evidence = (m.get("evidence") or "LLM 智能映射")[:300]
        crud_api_endpoint.link_testcase_endpoint(db, TestCaseApiEndpointCreate(
            testcase_id=tc_id, api_endpoint_id=ep_id,
            coverage_type="api", confidence=conf, evidence=evidence,
        ), commit=False)
        crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
            project_id=project_id, sprint_id=sprint_id,
            source_type="testcase", source_id=tc_id,
            target_type="api", target_id=ep_id,
            relation_type="tests_api", confidence=conf, evidence=evidence,
            metadata={"mapped_by": "llm"}, created_by="api-coverage-mapper",
        ), commit=False)
        existing.add((tc_id, ep_id))
        mapped += 1

    db.commit()
    base["mapped"] = mapped
    return base
