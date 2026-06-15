"""
Stage 2 用例生成的关联上下文构建器（P0.2）

从已建好的知识图谱 / TraceLink / 业务表查询关联信息，注入 Stage 2 的 LLM prompt：
  - related_modules: 通过 module→module TraceLink(depends_on/calls/data_flow) 查关联模块
  - related_apis:    通过 ApiEndpoint.module_id 查当前模块涉及的接口
  - existing_cases:  查历史用例（优先 sprint_all），用于去重 / 借鉴断言

直接基于 model 查询（crud 的查询函数参数风格不统一，且部分不支持多 module_id / project_id，
作为专用上下文构建器直接查 model 更清晰）。各段为空返回 []，有上限控制 prompt 体积。
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.trace_link import TraceLink
from app.models.api_endpoint import ApiEndpoint
from app.models.testcase import TestCase
from app.models.feature_point import FeaturePoint
from app.models.module import Module
from app.crud import crud_trace_link, crud_sprint

# 关联上下文上限（控制 prompt 体积）
MAX_RELATED_MODULES = 8
MAX_FEATURE_NAMES_PER_MODULE = 5
MAX_RELATED_APIS = 10
MAX_CASES_PER_MODULE = 5
MAX_TOTAL_CASES = 20

MODULE_DEP_RELATIONS = ("depends_on", "calls", "data_flow")


def build_case_context(
    db: Session,
    project_id: int | None,
    module_ids: list[int],
    current_sprint_id: int | None = None,
) -> dict:
    """构建 Stage 2 关联上下文，供注入 LLM prompt。

    Args:
        db: 数据库会话
        project_id: 项目 ID
        module_ids: 当前要生成用例的模块 ID 列表
        current_sprint_id: 当前 Sprint ID（existing_cases 排除该 sprint，避免取到正在生成的用例）

    Returns:
        {"related_modules": [...], "related_apis": [...], "existing_cases": [...]}
    """
    module_ids = [mid for mid in module_ids if mid]
    if not module_ids:
        return {"related_modules": [], "related_apis": [], "existing_cases": []}

    return {
        "related_modules": _query_related_modules(db, module_ids),
        "related_apis": _query_related_apis(db, project_id, module_ids),
        "existing_cases": _query_existing_cases(db, project_id, module_ids, current_sprint_id),
    }


def _query_related_modules(db: Session, module_ids: list[int]) -> list[dict]:
    """通过 module→module TraceLink 查关联模块（双向，取另一端不在当前集合的模块）。"""
    links = db.query(TraceLink).filter(
        TraceLink.source_type == "module",
        TraceLink.target_type == "module",
        TraceLink.relation_type.in_(MODULE_DEP_RELATIONS),
        TraceLink.status == "active",
        or_(
            TraceLink.source_id.in_(module_ids),
            TraceLink.target_id.in_(module_ids),
        ),
    ).all()

    peer_module_ids: set[int] = set()
    link_meta: dict[int, set[str]] = {}
    for link in links:
        if link.source_id in module_ids and link.target_id not in module_ids:
            peer_id = link.target_id
        elif link.target_id in module_ids and link.source_id not in module_ids:
            peer_id = link.source_id
        else:
            continue  # 两端都在当前集合，跳过避免自指噪声
        peer_module_ids.add(peer_id)
        link_meta.setdefault(peer_id, set()).add(
            crud_trace_link.get_relation_label(link.relation_type)
        )

    if not peer_module_ids:
        return []

    result = []
    for mid in peer_module_ids:
        mod = db.query(Module).filter(
            Module.id == mid,
            Module.is_deleted == False,  # noqa: E712
        ).first()
        if not mod:
            continue
        feature_names = [r[0] for r in db.query(FeaturePoint.name).filter(
            FeaturePoint.module_id == mid,
            FeaturePoint.is_deleted == False,  # noqa: E712
        ).limit(MAX_FEATURE_NAMES_PER_MODULE).all()]
        result.append({
            "name": mod.name,
            "relations": "、".join(sorted(link_meta.get(mid, set()))),
            "features": feature_names,
        })
        if len(result) >= MAX_RELATED_MODULES:
            break
    return result


def _query_related_apis(db: Session, project_id: int | None, module_ids: list[int]) -> list[dict]:
    """查当前模块涉及的接口（ApiEndpoint.module_id in module_ids）。"""
    query = db.query(ApiEndpoint).filter(
        ApiEndpoint.module_id.in_(module_ids),
        ApiEndpoint.is_deleted == False,  # noqa: E712
        ApiEndpoint.status == "active",
    )
    if project_id is not None:
        query = query.filter(ApiEndpoint.project_id == project_id)
    endpoints = query.order_by(ApiEndpoint.path, ApiEndpoint.method).limit(MAX_RELATED_APIS).all()

    return [
        {
            "method": ep.method or "",
            "path": ep.path or "",
            "summary": ep.summary or "",
        }
        for ep in endpoints
    ]


def _query_existing_cases(
    db: Session,
    project_id: int | None,
    module_ids: list[int],
    current_sprint_id: int | None,
) -> list[dict]:
    """查历史用例（优先 sprint_all），用于去重 / 借鉴断言。排除当前正在生成的 sprint。"""
    query = db.query(TestCase).filter(
        TestCase.module_id.in_(module_ids),
        TestCase.is_deleted == False,  # noqa: E712
    )
    if project_id is not None:
        query = query.filter(TestCase.project_id == project_id)
    if current_sprint_id is not None:
        query = query.filter(TestCase.sprint_id != current_sprint_id)

    cases = query.order_by(TestCase.id.desc()).all()

    # 优先 sprint_all 的用例；识别项目 sprint_all
    sprint_all_id = None
    if project_id is not None:
        sprint_all = crud_sprint.get_sprint_all(db, project_id)
        sprint_all_id = sprint_all.id if sprint_all else None

    # 排序：sprint_all 的用例靠前，再按 id 倒序
    def _sort_key(c):
        return (0 if c.sprint_id == sprint_all_id else 1, -c.id)

    cases = sorted(cases, key=_sort_key)

    # 每模块最多 MAX_CASES_PER_MODULE，总数最多 MAX_TOTAL_CASES
    result: list[dict] = []
    per_module_count: dict[int, int] = {}
    for c in cases:
        if len(result) >= MAX_TOTAL_CASES:
            break
        mid = c.module_id
        if per_module_count.get(mid, 0) >= MAX_CASES_PER_MODULE:
            continue
        result.append({"case_no": c.case_no or "", "title": c.title or ""})
        per_module_count[mid] = per_module_count.get(mid, 0) + 1

    return result
