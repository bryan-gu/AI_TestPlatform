"""LLM 辅助的 PRD 变更识别（增强项批次 6 子项 A）。

规则分析（ChangeAnalyzer）后，用 LLM 读 PRD 文本复核，补充规则可能遗漏的语义级变更。
- 规则为主，LLM 为补充；LLM 失败 / 无 PRD 文本时跳过，不影响规则结果。
- LLM 识别的变更项 raw_data.analyzer='llm'，confidence 较低（待人工确认）。
"""
import json
import re
import logging

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.feature_point import FeaturePoint
from app.models.sprint import Sprint
from app.models.module import Module
from app.models.change_item import ChangeItem
from app.crud import crud_change_item, crud_sprint
from app.schemas.change_item import ChangeItemCreate
from app.services.llm_adapter import LLMAdapter
from app.services.prompts.skill_prompts import build_change_detection_prompt

logger = logging.getLogger(__name__)

MAX_PRD_CHARS = 3000
MAX_BASELINE_FEATURES = 30


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


def detect_changes_with_llm(db: Session, sprint_id: int) -> dict:
    """规则分析后用 LLM 复核 PRD，补充语义级变更。"""
    sprint = db.query(Sprint).filter(
        Sprint.id == sprint_id,
        Sprint.is_deleted == False,  # noqa: E712
    ).first()
    if not sprint:
        return {"detected": 0, "skipped": "Sprint 不存在"}
    if not sprint.project_id:
        return {"detected": 0, "skipped": "Sprint 无项目"}

    # PRD 文本（拼接当前 Sprint 文档的 content_preview）
    docs = db.query(Document).filter(
        Document.sprint_id == sprint_id,
        Document.is_deleted == False,  # noqa: E712
    ).all()
    prd_text = "\n\n".join(d.content_preview for d in docs if d.content_preview)[:MAX_PRD_CHARS]
    if not prd_text:
        return {"detected": 0, "skipped": "当前 Sprint 无 PRD 文本"}

    # 基线功能点
    baseline = crud_sprint.get_sprint_all(db, sprint.project_id)
    if not baseline:
        return {"detected": 0, "skipped": "无 sprint_all 基线"}
    baseline_fps = db.query(FeaturePoint).filter(
        FeaturePoint.sprint_id == baseline.id,
        FeaturePoint.is_deleted == False,  # noqa: E712
    ).limit(MAX_BASELINE_FEATURES).all()
    lines = []
    for fp in baseline_fps:
        mod_name = ""
        if fp.module_id:
            m = db.query(Module).filter(Module.id == fp.module_id).first()
            mod_name = m.name if m else ""
        lines.append(f"- {fp.name}（模块：{mod_name or '未分类'}，优先级：{fp.priority or '中'}）")
    baseline_features = "\n".join(lines) or "（基线暂无功能点）"

    # 已有变更项标题（去重，避免与规则结果重复）
    existing = {r[0] for r in db.query(ChangeItem.title).filter(
        ChangeItem.sprint_id == sprint_id,
        ChangeItem.is_deleted == False,  # noqa: E712
    ).all()}

    prompt = build_change_detection_prompt(prd_text, baseline_features)
    try:
        adapter = LLMAdapter(db)
        result = adapter.call("PRD 变更识别", prompt)
        parsed = _extract_json(result.get("content", ""))
    except Exception as e:
        logger.warning("LLM 变更识别失败: %s", e)
        return {"detected": 0, "skipped": f"LLM 调用失败：{e}"}

    changes = (parsed or {}).get("changes", []) if isinstance(parsed, dict) else []
    detected = 0
    for c in changes:
        if not isinstance(c, dict):
            continue
        title = (c.get("title") or "").strip()
        if not title or title in existing:
            continue
        change_type = c.get("change_type") or "modified"
        if change_type not in ("added", "modified", "removed"):
            change_type = "modified"
        priority = c.get("priority") or "中"
        if priority not in ("高", "中", "低"):
            priority = "中"
        fingerprint = f"llm:{sprint_id}:{title}:{change_type}"
        data = ChangeItemCreate(
            project_id=sprint.project_id,
            sprint_id=sprint_id,
            title=title,
            description=(c.get("description") or "")[:500],
            change_type=change_type,
            target_type="feature",
            target_id=None,
            priority=priority,
            impact_level=priority,
            status="open",
            evidence="LLM PRD 变更识别（待人工确认）",
            confidence=70,
            fingerprint=fingerprint,
            raw_data={"analyzer": "llm", "module_name": c.get("module_name", "")},
        )
        item, created = crud_change_item.upsert_change_item(db, data, commit=False)
        if created:
            existing.add(title)
            detected += 1
    db.commit()
    return {"detected": detected, "candidates": len(changes)}
