from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.trace_link import TraceLink
from app.models.knowledge_asset import KnowledgeAsset
from app.models.document import Document
from app.models.feature_point import FeaturePoint
from app.models.testcase import TestCase
from app.models.module import Module
from app.models.sprint import Sprint
from app.schemas.trace_link import TraceLinkCreate, TraceLinkUpdate


RELATION_LABELS = {
    "contains": "包含",
    "derived_from": "来源于",
    "belongs_to": "属于",
    "covers": "覆盖",
    "tests_api": "测试接口",
    "implements": "实现",
    "changes": "变更",
    "depends_on": "依赖",
    "calls": "调用",
    "uses_schema": "使用 Schema",
    "generated_by": "生成自",
    "verified_by": "验证于",
    "mentions": "提及",
}


ENTITY_LABELS = {
    "asset": "资产",
    "document": "文档",
    "module": "模块",
    "feature": "功能点",
    "testcase": "测试用例",
    "api": "接口",
    "script": "脚本",
    "selector": "选择器",
    "execution": "执行结果",
    "change": "变更项",
    "sprint": "Sprint",
}


def get_trace_link(db: Session, link_id: int) -> TraceLink | None:
    return db.query(TraceLink).filter(TraceLink.id == link_id).first()


def get_trace_links(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    source_type: str | None = None,
    source_id: int | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    relation_type: str | None = None,
    status: str | None = "active",
) -> list[TraceLink]:
    query = db.query(TraceLink)
    if project_id is not None:
        query = query.filter(TraceLink.project_id == project_id)
    if sprint_id is not None:
        query = query.filter(TraceLink.sprint_id == sprint_id)
    if source_type:
        query = query.filter(TraceLink.source_type == source_type)
    if source_id is not None:
        query = query.filter(TraceLink.source_id == source_id)
    if target_type:
        query = query.filter(TraceLink.target_type == target_type)
    if target_id is not None:
        query = query.filter(TraceLink.target_id == target_id)
    if relation_type:
        query = query.filter(TraceLink.relation_type == relation_type)
    if status:
        query = query.filter(TraceLink.status == status)
    return query.order_by(TraceLink.created_at.desc()).all()


def get_entity_links(
    db: Session,
    entity_type: str,
    entity_id: int,
    direction: str = "both",
    status: str | None = "active",
) -> list[TraceLink]:
    query = db.query(TraceLink)
    if direction == "source":
        query = query.filter(TraceLink.source_type == entity_type, TraceLink.source_id == entity_id)
    elif direction == "target":
        query = query.filter(TraceLink.target_type == entity_type, TraceLink.target_id == entity_id)
    else:
        query = query.filter(or_(
            (TraceLink.source_type == entity_type) & (TraceLink.source_id == entity_id),
            (TraceLink.target_type == entity_type) & (TraceLink.target_id == entity_id),
        ))
    if status:
        query = query.filter(TraceLink.status == status)
    return query.order_by(TraceLink.created_at.desc()).all()


def create_trace_link(db: Session, data: TraceLinkCreate) -> TraceLink:
    link = TraceLink(
        project_id=data.project_id,
        sprint_id=data.sprint_id,
        source_type=data.source_type,
        source_id=data.source_id,
        target_type=data.target_type,
        target_id=data.target_id,
        relation_type=data.relation_type,
        confidence=data.confidence,
        evidence=data.evidence,
        link_metadata=data.metadata,
        status=data.status,
        created_by=data.created_by,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def upsert_trace_link(db: Session, data: TraceLinkCreate, *, commit: bool = True) -> TraceLink:
    link = db.query(TraceLink).filter(
        TraceLink.project_id == data.project_id,
        TraceLink.sprint_id == data.sprint_id,
        TraceLink.source_type == data.source_type,
        TraceLink.source_id == data.source_id,
        TraceLink.target_type == data.target_type,
        TraceLink.target_id == data.target_id,
        TraceLink.relation_type == data.relation_type,
    ).first()

    if link:
        link.confidence = data.confidence
        link.evidence = data.evidence
        link.link_metadata = data.metadata
        link.status = data.status
        link.created_by = data.created_by
        if commit:
            db.commit()
            db.refresh(link)
        else:
            db.flush()
        return link

    link = TraceLink(
        project_id=data.project_id,
        sprint_id=data.sprint_id,
        source_type=data.source_type,
        source_id=data.source_id,
        target_type=data.target_type,
        target_id=data.target_id,
        relation_type=data.relation_type,
        confidence=data.confidence,
        evidence=data.evidence,
        link_metadata=data.metadata,
        status=data.status,
        created_by=data.created_by,
    )
    db.add(link)
    if commit:
        db.commit()
        db.refresh(link)
    else:
        db.flush()
    return link


def update_trace_link(db: Session, link: TraceLink, data: TraceLinkUpdate) -> TraceLink:
    if data.project_id is not None:
        link.project_id = data.project_id
    if data.sprint_id is not None:
        link.sprint_id = data.sprint_id
    if data.confidence is not None:
        link.confidence = data.confidence
    if data.evidence is not None:
        link.evidence = data.evidence
    if data.metadata is not None:
        link.link_metadata = data.metadata
    if data.status is not None:
        link.status = data.status
    if data.created_by is not None:
        link.created_by = data.created_by
    db.commit()
    db.refresh(link)
    return link


def deactivate_trace_link(db: Session, link: TraceLink) -> None:
    link.status = "inactive"
    db.commit()


def deactivate_entity_relation(
    db: Session,
    source_type: str,
    source_id: int,
    target_type: str,
    target_id: int,
    relation_type: str,
) -> int:
    links = db.query(TraceLink).filter(
        TraceLink.source_type == source_type,
        TraceLink.source_id == source_id,
        TraceLink.target_type == target_type,
        TraceLink.target_id == target_id,
        TraceLink.relation_type == relation_type,
        TraceLink.status == "active",
    ).all()
    for link in links:
        link.status = "inactive"
    db.commit()
    return len(links)


def get_relation_label(relation_type: str) -> str:
    return RELATION_LABELS.get(relation_type, relation_type)


def get_entity_name(db: Session, entity_type: str, entity_id: int) -> str:
    if not entity_id:
        return ""
    model_map = {
        "asset": (KnowledgeAsset, KnowledgeAsset.name),
        "document": (Document, Document.name),
        "feature": (FeaturePoint, FeaturePoint.name),
        "testcase": (TestCase, TestCase.title),
        "module": (Module, Module.name),
        "sprint": (Sprint, Sprint.name),
    }
    item = model_map.get(entity_type)
    if not item:
        return f"{ENTITY_LABELS.get(entity_type, entity_type)} #{entity_id}"
    model, name_column = item
    obj = db.query(model).filter(model.id == entity_id).first()
    if not obj:
        return f"{ENTITY_LABELS.get(entity_type, entity_type)} #{entity_id}"
    if entity_type == "testcase" and getattr(obj, "case_no", ""):
        return f"{obj.case_no} {obj.title}".strip()
    return getattr(obj, name_column.key, "") or f"{ENTITY_LABELS.get(entity_type, entity_type)} #{entity_id}"


def get_entity_impact(db: Session, entity_type: str, entity_id: int) -> dict:
    links = get_entity_links(db, entity_type, entity_id)
    impact = {
        "entity": {
            "type": entity_type,
            "id": entity_id,
            "name": get_entity_name(db, entity_type, entity_id),
        },
        "links": links,
        "testcases": [],
        "assets": [],
        "features": [],
        "modules": [],
        "api_endpoints": [],
        "scripts": [],
        "changes": [],
    }
    seen = set()
    bucket_map = {
        "testcase": "testcases",
        "asset": "assets",
        "feature": "features",
        "module": "modules",
        "api": "api_endpoints",
        "script": "scripts",
        "change": "changes",
    }
    for link in links:
        endpoints = [
            (link.source_type, link.source_id),
            (link.target_type, link.target_id),
        ]
        for target_type, target_id in endpoints:
            if target_type == entity_type and target_id == entity_id:
                continue
            bucket = bucket_map.get(target_type)
            key = (target_type, target_id)
            if not bucket or key in seen:
                continue
            seen.add(key)
            impact[bucket].append({
                "type": target_type,
                "id": target_id,
                "name": get_entity_name(db, target_type, target_id),
                "relation_type": link.relation_type,
                "relation_label": get_relation_label(link.relation_type),
                "confidence": link.confidence or 0,
                "evidence": link.evidence or "",
            })
    return impact


def backfill_trace_links(db: Session, project_id: int | None = None, sprint_id: int | None = None) -> dict:
    created_or_updated = 0

    def upsert(data: TraceLinkCreate):
        nonlocal created_or_updated
        upsert_trace_link(db, data, commit=False)
        created_or_updated += 1

    assets_query = db.query(KnowledgeAsset).filter(KnowledgeAsset.document_id.isnot(None))
    if project_id is not None:
        assets_query = assets_query.filter(KnowledgeAsset.project_id == project_id)
    if sprint_id is not None:
        assets_query = assets_query.filter(KnowledgeAsset.sprint_id == sprint_id)
    for asset in assets_query.all():
        upsert(TraceLinkCreate(
            project_id=asset.project_id,
            sprint_id=asset.sprint_id,
            source_type="asset",
            source_id=asset.id,
            target_type="document",
            target_id=asset.document_id,
            relation_type="derived_from",
            confidence=100,
            evidence="KnowledgeAsset 关联 Document 回填",
            metadata={"backfilled": True},
            created_by="backfill",
        ))

    fp_query = db.query(FeaturePoint).filter(FeaturePoint.is_deleted == False)  # noqa: E712
    if sprint_id is not None:
        fp_query = fp_query.filter(FeaturePoint.sprint_id == sprint_id)
    for fp in fp_query.all():
        if project_id is not None:
            sprint = db.query(Sprint).filter(Sprint.id == fp.sprint_id).first() if fp.sprint_id else None
            if not sprint or sprint.project_id != project_id:
                continue
        sprint = db.query(Sprint).filter(Sprint.id == fp.sprint_id).first() if fp.sprint_id else None
        resolved_project_id = sprint.project_id if sprint else project_id
        if fp.source_doc_id:
            upsert(TraceLinkCreate(
                project_id=resolved_project_id,
                sprint_id=fp.sprint_id,
                source_type="document",
                source_id=fp.source_doc_id,
                target_type="feature",
                target_id=fp.id,
                relation_type="contains",
                confidence=90,
                evidence="FeaturePoint.source_doc_id 回填",
                metadata={"backfilled": True},
                created_by="backfill",
            ))
            asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.document_id == fp.source_doc_id).first()
            if asset:
                upsert(TraceLinkCreate(
                    project_id=resolved_project_id,
                    sprint_id=fp.sprint_id,
                    source_type="asset",
                    source_id=asset.id,
                    target_type="feature",
                    target_id=fp.id,
                    relation_type="derived_from",
                    confidence=90,
                    evidence="来源文档资产回填",
                    metadata={"backfilled": True},
                    created_by="backfill",
                ))
        if fp.module_id:
            upsert(TraceLinkCreate(
                project_id=resolved_project_id,
                sprint_id=fp.sprint_id,
                source_type="feature",
                source_id=fp.id,
                target_type="module",
                target_id=fp.module_id,
                relation_type="belongs_to",
                confidence=100,
                evidence="FeaturePoint.module_id 回填",
                metadata={"backfilled": True},
                created_by="backfill",
            ))

    tc_query = db.query(TestCase).filter(TestCase.is_deleted == False)  # noqa: E712
    if project_id is not None:
        tc_query = tc_query.filter(TestCase.project_id == project_id)
    if sprint_id is not None:
        tc_query = tc_query.filter(TestCase.sprint_id == sprint_id)
    for case in tc_query.all():
        if case.module_id:
            upsert(TraceLinkCreate(
                project_id=case.project_id,
                sprint_id=case.sprint_id,
                source_type="testcase",
                source_id=case.id,
                target_type="module",
                target_id=case.module_id,
                relation_type="belongs_to",
                confidence=100,
                evidence="TestCase.module_id 回填",
                metadata={"backfilled": True},
                created_by="backfill",
            ))

    from app.models.coverage import FeaturePointTestCase
    coverage_query = db.query(FeaturePointTestCase)
    for coverage in coverage_query.all():
        fp = db.query(FeaturePoint).filter(FeaturePoint.id == coverage.feature_point_id).first()
        case = db.query(TestCase).filter(TestCase.id == coverage.testcase_id).first()
        if not fp or not case:
            continue
        if project_id is not None and case.project_id != project_id:
            continue
        if sprint_id is not None and case.sprint_id != sprint_id and fp.sprint_id != sprint_id:
            continue
        upsert(TraceLinkCreate(
            project_id=case.project_id,
            sprint_id=case.sprint_id or fp.sprint_id,
            source_type="feature",
            source_id=coverage.feature_point_id,
            target_type="testcase",
            target_id=coverage.testcase_id,
            relation_type="covers",
            confidence=coverage.confidence or 100,
            evidence=coverage.evidence or "FeaturePointTestCase 回填",
            metadata={"backfilled": True, "coverage_type": coverage.coverage_type or "functional"},
            created_by="backfill",
        ))

    db.commit()
    return {"upserted_count": created_or_updated}
