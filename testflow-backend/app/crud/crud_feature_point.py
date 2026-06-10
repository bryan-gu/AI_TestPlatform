from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.feature_point import FeaturePoint
from app.models.document import Document
from app.models.sprint import Sprint
from app.models.module import Module
from app.schemas.feature_point import FeaturePointCreate, FeaturePointUpdate


def get_feature_points(
    db: Session,
    sprint_id: int | None = None,
    module_id: int | None = None,
    source_doc_id: int | None = None,
    keyword: str | None = None,
) -> list[FeaturePoint]:
    query = db.query(FeaturePoint)
    if sprint_id:
        query = query.filter(FeaturePoint.sprint_id == sprint_id)
    if module_id:
        query = query.filter(FeaturePoint.module_id == module_id)
    if source_doc_id:
        query = query.filter(FeaturePoint.source_doc_id == source_doc_id)
    if keyword:
        query = query.filter(
            or_(
                FeaturePoint.name.ilike(f"%{keyword}%"),
                FeaturePoint.description.ilike(f"%{keyword}%"),
                FeaturePoint.entry_path.ilike(f"%{keyword}%"),
                FeaturePoint.business_rules.ilike(f"%{keyword}%"),
                FeaturePoint.linked_cases.ilike(f"%{keyword}%"),
            )
        )
    return query.order_by(FeaturePoint.created_at.desc()).all()


def get_feature_point(db: Session, fp_id: int) -> FeaturePoint | None:
    return db.query(FeaturePoint).filter(FeaturePoint.id == fp_id).first()


def create_feature_point(db: Session, data: FeaturePointCreate) -> FeaturePoint:
    fp = FeaturePoint(
        name=data.name,
        description=data.description,
        entry_path=data.entry_path,
        interaction_elements=data.interaction_elements,
        business_rules=data.business_rules,
        priority=data.priority,
        source_doc_id=data.source_doc_id,
        sprint_id=data.sprint_id,
        module_id=data.module_id,
        linked_cases=data.linked_cases,
        source_type=data.source_type,
        status=data.status,
        version=data.version,
        fingerprint=data.fingerprint,
        raw_data=data.raw_data,
    )
    db.add(fp)
    db.commit()
    db.refresh(fp)
    return fp


def update_feature_point(db: Session, fp: FeaturePoint, data: FeaturePointUpdate) -> FeaturePoint:
    if data.name is not None:
        fp.name = data.name
    if data.description is not None:
        fp.description = data.description
    if data.entry_path is not None:
        fp.entry_path = data.entry_path
    if data.interaction_elements is not None:
        fp.interaction_elements = data.interaction_elements
    if data.business_rules is not None:
        fp.business_rules = data.business_rules
    if data.priority is not None:
        fp.priority = data.priority
    if data.source_doc_id is not None:
        fp.source_doc_id = data.source_doc_id
    if data.sprint_id is not None:
        fp.sprint_id = data.sprint_id
    if data.module_id is not None:
        fp.module_id = data.module_id
    if data.linked_cases is not None:
        fp.linked_cases = data.linked_cases
    if data.source_type is not None:
        fp.source_type = data.source_type
    if data.status is not None:
        fp.status = data.status
    if data.version is not None:
        fp.version = data.version
    if data.fingerprint is not None:
        fp.fingerprint = data.fingerprint
    if data.raw_data is not None:
        fp.raw_data = data.raw_data
    db.commit()
    db.refresh(fp)
    return fp


def delete_feature_point(db: Session, fp: FeaturePoint) -> None:
    from app.models.coverage import FeaturePointTestCase
    db.query(FeaturePointTestCase).filter(
        FeaturePointTestCase.feature_point_id == fp.id
    ).delete(synchronize_session=False)
    db.delete(fp)
    db.commit()


def get_feature_point_count(db: Session, sprint_id: int | None = None) -> int:
    """统计功能点数量，可按 sprint_id 筛选"""
    query = db.query(FeaturePoint)
    if sprint_id:
        query = query.filter(FeaturePoint.sprint_id == sprint_id)
    return query.count()


def get_coverage_count(db: Session, feature_point_id: int) -> int:
    from app.models.coverage import FeaturePointTestCase
    return db.query(FeaturePointTestCase).filter(
        FeaturePointTestCase.feature_point_id == feature_point_id
    ).count()


def get_source_doc_name(db: Session, doc_id: int | None) -> str:
    if not doc_id:
        return ""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    return doc.name if doc else ""


def get_sprint_name(db: Session, sprint_id: int | None) -> str:
    if not sprint_id:
        return ""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    return sprint.name if sprint else ""


def get_module_name(db: Session, module_id: int | None) -> str:
    if not module_id:
        return ""
    module = db.query(Module).filter(Module.id == module_id).first()
    return module.name if module else ""
