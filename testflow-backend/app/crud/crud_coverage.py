from sqlalchemy.orm import Session

from app.models.coverage import FeaturePointTestCase
from app.models.feature_point import FeaturePoint
from app.models.testcase import TestCase
from app.schemas.coverage import CoverageCreate, CoverageUpdate


def get_coverage(db: Session, coverage_id: int) -> FeaturePointTestCase | None:
    return db.query(FeaturePointTestCase).filter(FeaturePointTestCase.id == coverage_id).first()


def get_testcases_by_feature_point(db: Session, feature_point_id: int) -> list[FeaturePointTestCase]:
    return db.query(FeaturePointTestCase).filter(
        FeaturePointTestCase.feature_point_id == feature_point_id
    ).order_by(FeaturePointTestCase.created_at.desc()).all()


def get_feature_points_by_testcase(db: Session, testcase_id: int) -> list[FeaturePointTestCase]:
    return db.query(FeaturePointTestCase).filter(
        FeaturePointTestCase.testcase_id == testcase_id
    ).order_by(FeaturePointTestCase.created_at.desc()).all()


def create_coverage(db: Session, data: CoverageCreate) -> FeaturePointTestCase:
    existing = db.query(FeaturePointTestCase).filter(
        FeaturePointTestCase.feature_point_id == data.feature_point_id,
        FeaturePointTestCase.testcase_id == data.testcase_id,
    ).first()
    if existing:
        existing.coverage_type = data.coverage_type
        existing.confidence = data.confidence
        existing.evidence = data.evidence
        db.commit()
        db.refresh(existing)
        return existing

    coverage = FeaturePointTestCase(
        feature_point_id=data.feature_point_id,
        testcase_id=data.testcase_id,
        coverage_type=data.coverage_type,
        confidence=data.confidence,
        evidence=data.evidence,
    )
    db.add(coverage)
    db.commit()
    db.refresh(coverage)
    return coverage


def update_coverage(db: Session, coverage: FeaturePointTestCase, data: CoverageUpdate) -> FeaturePointTestCase:
    if data.coverage_type is not None:
        coverage.coverage_type = data.coverage_type
    if data.confidence is not None:
        coverage.confidence = data.confidence
    if data.evidence is not None:
        coverage.evidence = data.evidence
    db.commit()
    db.refresh(coverage)
    return coverage


def delete_coverage(db: Session, coverage: FeaturePointTestCase) -> None:
    db.delete(coverage)
    db.commit()


def get_feature_point_name(db: Session, feature_point_id: int) -> str:
    fp = db.query(FeaturePoint).filter(FeaturePoint.id == feature_point_id).first()
    return fp.name if fp else ""


def get_testcase_info(db: Session, testcase_id: int) -> tuple[str, str]:
    case = db.query(TestCase).filter(TestCase.id == testcase_id).first()
    if not case:
        return "", ""
    return case.case_no or "", case.title or ""
