"""Playwright 脚本解析与用例映射服务（增强项批次 3）。

职责：
- 解析 .spec.ts 文件中 test() 标题里的 case_no。
- 按 case_no 关联 TestCase，更新 automation_status / automation_path。
- 写 testcase -> script (generated_by) TraceLink。
- 解析 spec 的 selector import，建立 script -> selector (depends_on) 关系（文件名匹配）。

case_no 正则参考《知识库与知识图谱增强项开发计划》附录 17.7：
    ([A-Za-z0-9]+_TC_[A-Za-z0-9]+_\\d{3,})
"""
import os
import re
import logging

from sqlalchemy.orm import Session

from app.models.testcase import TestCase
from app.models.knowledge_asset import KnowledgeAsset
from app.crud import crud_trace_link
from app.schemas.trace_link import TraceLinkCreate

logger = logging.getLogger(__name__)

# test('...') / test("...") / test(`...`)
TEST_TITLE_RE = re.compile(r"\btest\s*\(\s*['\"`]([^'\"`]+)['\"`]")
# case_no：PREFIX_TC_MODULE_NUM（数字 3 位以上）
CASE_NO_RE = re.compile(r"([A-Za-z0-9]+_TC_[A-Za-z0-9]+_\d{3,})")
# import selector：from '...selectors...' / import '...selectors...'
SELECTOR_IMPORT_RE = re.compile(
    r"(?:from|import)\s+['\"]([^'\"]*selectors[^'\"]*)['\"]"
)

AUTOMATION_STATUS_GENERATED = "generated"


def _read_text(path: str) -> str:
    """读取文件文本，优先 UTF-8，失败回退 GBK。"""
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def parse_spec_file(path: str) -> list[dict]:
    """解析 Playwright spec 文件，返回每个 test() 的 [{case_no, test_title, line}, ...]。

    无 case_no 的 test() 不返回（无法稳定映射）。
    """
    if not path or not os.path.exists(path):
        return []
    text = _read_text(path)
    if not text:
        return []
    results: list[dict] = []
    for m in TEST_TITLE_RE.finditer(text):
        title = m.group(1).strip()
        cm = CASE_NO_RE.search(title)
        if not cm:
            continue
        line = text.count("\n", 0, m.start()) + 1
        results.append({
            "case_no": cm.group(1),
            "test_title": title,
            "line": line,
        })
    return results


def parse_selector_imports(spec_path: str) -> list[str]:
    """从 spec 文件解析 import 的 selector 相对路径。"""
    if not spec_path or not os.path.exists(spec_path):
        return []
    text = _read_text(spec_path)
    if not text:
        return []
    paths: list[str] = []
    for m in SELECTOR_IMPORT_RE.finditer(text):
        p = m.group(1)
        if p and p not in paths:
            paths.append(p)
    return paths


def link_script_asset_to_testcases(
    db: Session,
    asset: KnowledgeAsset,
    file_path: str | None = None,
) -> dict:
    """解析 script 资产文件，按 case_no 关联 TestCase，更新自动化状态，写 TraceLink。

    file_path 默认用 asset.file_path（API 手动触发场景）；导入场景传入实际路径。
    返回 {linked, not_found, total_tests, selectors_linked, error?}
    """
    path = file_path or asset.file_path
    result = {
        "linked": 0,
        "not_found": 0,
        "total_tests": 0,
        "selectors_linked": 0,
    }
    if not path or not os.path.exists(path):
        result["error"] = "脚本文件路径无效或文件不存在"
        return result

    tests = parse_spec_file(path)
    result["total_tests"] = len(tests)
    if not tests:
        result["error"] = "未在脚本中识别到带 case_no 的 test()"
        return result

    project_id = asset.project_id
    sprint_id = asset.sprint_id
    for t in tests:
        tc = db.query(TestCase).filter(
            TestCase.project_id == project_id,
            TestCase.case_no == t["case_no"],
            TestCase.is_deleted == False,  # noqa: E712
        ).first()
        if not tc:
            result["not_found"] += 1
            continue
        # 更新自动化状态
        tc.automation_status = AUTOMATION_STATUS_GENERATED
        tc.automation_path = path
        # testcase -> script (generated_by)
        crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
            project_id=project_id,
            sprint_id=sprint_id,
            source_type="testcase",
            source_id=tc.id,
            target_type="script",
            target_id=asset.id,
            relation_type="generated_by",
            confidence=100,
            evidence=f"spec test(): {t['test_title']}",
            metadata={"test_title": t["test_title"], "line": t.get("line")},
            created_by="script-parser",
        ), commit=False)
        result["linked"] += 1

    # script -> selector (depends_on)：按 selector import 路径文件名匹配同 sprint 的 selector 资产
    result["selectors_linked"] = _link_selectors(db, asset, path)

    db.commit()
    return result


def _link_selectors(db: Session, script_asset: KnowledgeAsset, spec_path: str) -> int:
    """根据 spec 的 selector import，建立 script -> selector TraceLink。"""
    sel_paths = parse_selector_imports(spec_path)
    if not sel_paths:
        return 0
    # 同 sprint 的 selector_map 资产，按文件名片段匹配
    candidates = db.query(KnowledgeAsset).filter(
        KnowledgeAsset.sprint_id == script_asset.sprint_id,
        KnowledgeAsset.asset_type == "selector_map",
        KnowledgeAsset.status != "deleted",
    ).all()
    if not candidates:
        return 0
    linked = 0
    for sel in candidates:
        sel_name = (sel.name or "").lower()
        matched = any(
            os.path.splitext(os.path.basename(p))[0].lower() in sel_name
            or sel_name in p.lower()
            for p in sel_paths
        )
        if not matched:
            continue
        crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
            project_id=script_asset.project_id,
            sprint_id=script_asset.sprint_id,
            source_type="script",
            source_id=script_asset.id,
            target_type="selector",
            target_id=sel.id,
            relation_type="depends_on",
            confidence=70,
            evidence="spec import selector 匹配",
            created_by="script-parser",
        ), commit=False)
        linked += 1
    return linked
