"""统一覆盖率计算服务。

全平台覆盖率口径统一在此处实现，避免各页面/接口算法漂移。
覆盖定义见《知识库与知识图谱增强项开发计划》批次 2 / 附录 17.8。

口径：
- 功能点覆盖率：active 功能点中有 FeaturePointTestCase 或 feature->testcase covers TraceLink 的数 / 总数
- API 覆盖率：active 接口中有 TestCaseApiEndpoint 或 testcase->api tests_api TraceLink 的数 / 总数
- 自动化覆盖率：用例 automation_status in AUTOMATION_DONE 或 testcase->script generated_by 的数 / 总数
- 变更覆盖率：变更项 status in CHANGE_DONE 的数 / 总数
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.feature_point import FeaturePoint
from app.models.testcase import TestCase
from app.models.api_endpoint import ApiEndpoint, TestCaseApiEndpoint
from app.models.change_item import ChangeItem
from app.models.knowledge_asset import KnowledgeAsset
from app.models.coverage import FeaturePointTestCase
from app.models.trace_link import TraceLink


# 已生成自动化的状态（不含 not_generated / failed）
AUTOMATION_DONE = ("generated", "validated", "executed", "healed")
# 已处理的变更状态
CHANGE_DONE = ("applied", "ignored", "resolved")


def _rate(covered: int, total: int) -> int:
    return round(covered / total * 100) if total > 0 else 0


def _coverage_dict(total: int, covered: int) -> dict:
    return {
        "total": total,
        "covered": covered,
        "uncovered": total - covered,
        "rate": _rate(covered, total),
    }


def feature_coverage(db: Session, sprint_id: int) -> dict:
    fp_ids = [r[0] for r in db.query(FeaturePoint.id).filter(
        FeaturePoint.sprint_id == sprint_id,
        FeaturePoint.is_deleted == False,  # noqa: E712
    ).all()]
    total = len(fp_ids)
    if total == 0:
        return _coverage_dict(0, 0)
    via_fptc = {r[0] for r in db.query(FeaturePointTestCase.feature_point_id).filter(
        FeaturePointTestCase.feature_point_id.in_(fp_ids)
    ).all()}
    via_link = {r[0] for r in db.query(TraceLink.source_id).filter(
        TraceLink.source_type == "feature",
        TraceLink.source_id.in_(fp_ids),
        TraceLink.target_type == "testcase",
        TraceLink.relation_type == "covers",
        TraceLink.status == "active",
    ).all()}
    covered = len(via_fptc | via_link)
    return _coverage_dict(total, covered)


def api_coverage(db: Session, sprint_id: int) -> dict:
    ep_ids = [r[0] for r in db.query(ApiEndpoint.id).filter(
        ApiEndpoint.sprint_id == sprint_id,
        ApiEndpoint.is_deleted == False,  # noqa: E712
    ).all()]
    total = len(ep_ids)
    if total == 0:
        return _coverage_dict(0, 0)
    via_tcae = {r[0] for r in db.query(TestCaseApiEndpoint.api_endpoint_id).filter(
        TestCaseApiEndpoint.api_endpoint_id.in_(ep_ids)
    ).all()}
    via_link = {r[0] for r in db.query(TraceLink.target_id).filter(
        TraceLink.target_type == "api",
        TraceLink.target_id.in_(ep_ids),
        TraceLink.source_type == "testcase",
        TraceLink.relation_type == "tests_api",
        TraceLink.status == "active",
    ).all()}
    covered = len(via_tcae | via_link)
    return _coverage_dict(total, covered)


def automation_coverage(db: Session, sprint_id: int) -> dict:
    tc_ids = [r[0] for r in db.query(TestCase.id).filter(
        TestCase.sprint_id == sprint_id,
        TestCase.is_deleted == False,  # noqa: E712
    ).all()]
    total = len(tc_ids)
    if total == 0:
        return _coverage_dict(0, 0)
    via_status = {r[0] for r in db.query(TestCase.id).filter(
        TestCase.id.in_(tc_ids),
        TestCase.automation_status.in_(AUTOMATION_DONE),
    ).all()}
    via_link = {r[0] for r in db.query(TraceLink.source_id).filter(
        TraceLink.source_type == "testcase",
        TraceLink.source_id.in_(tc_ids),
        TraceLink.target_type == "script",
        TraceLink.relation_type == "generated_by",
        TraceLink.status == "active",
    ).all()}
    covered = len(via_status | via_link)
    return _coverage_dict(total, covered)


def change_coverage(db: Session, sprint_id: int) -> dict:
    total = db.query(func.count(ChangeItem.id)).filter(
        ChangeItem.sprint_id == sprint_id,
        ChangeItem.is_deleted == False,  # noqa: E712
    ).scalar() or 0
    if total == 0:
        return _coverage_dict(0, 0)
    covered = db.query(func.count(ChangeItem.id)).filter(
        ChangeItem.sprint_id == sprint_id,
        ChangeItem.is_deleted == False,  # noqa: E712
        ChangeItem.status.in_(CHANGE_DONE),
    ).scalar() or 0
    return _coverage_dict(total, covered)


def sprint_knowledge_overview(db: Session, sprint_id: int) -> dict:
    """Sprint 知识概览：各类实体计数 + 四类覆盖率。"""
    asset_count = db.query(func.count(KnowledgeAsset.id)).filter(
        KnowledgeAsset.sprint_id == sprint_id,
        KnowledgeAsset.status != "deleted",
    ).scalar() or 0
    feature_count = db.query(func.count(FeaturePoint.id)).filter(
        FeaturePoint.sprint_id == sprint_id,
        FeaturePoint.is_deleted == False,  # noqa: E712
    ).scalar() or 0
    testcase_count = db.query(func.count(TestCase.id)).filter(
        TestCase.sprint_id == sprint_id,
        TestCase.is_deleted == False,  # noqa: E712
    ).scalar() or 0
    api_count = db.query(func.count(ApiEndpoint.id)).filter(
        ApiEndpoint.sprint_id == sprint_id,
        ApiEndpoint.is_deleted == False,  # noqa: E712
    ).scalar() or 0
    script_count = db.query(func.count(KnowledgeAsset.id)).filter(
        KnowledgeAsset.sprint_id == sprint_id,
        KnowledgeAsset.asset_type == "test_script",
        KnowledgeAsset.status != "deleted",
    ).scalar() or 0
    change_count = db.query(func.count(ChangeItem.id)).filter(
        ChangeItem.sprint_id == sprint_id,
        ChangeItem.is_deleted == False,  # noqa: E712
    ).scalar() or 0
    return {
        "asset_count": asset_count,
        "feature_count": feature_count,
        "testcase_count": testcase_count,
        "api_count": api_count,
        "script_count": script_count,
        "change_count": change_count,
        "feature_coverage": feature_coverage(db, sprint_id),
        "api_coverage": api_coverage(db, sprint_id),
        "automation_coverage": automation_coverage(db, sprint_id),
        "change_coverage": change_coverage(db, sprint_id),
    }
