from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.coverage import CoverageCreate, CoverageUpdate, CoverageOut
from app.crud import crud_coverage
from app.models.feature_point import FeaturePoint
from app.models.testcase import TestCase


router = APIRouter(prefix="/coverage", tags=["覆盖关系"])


def _to_out(coverage, db: Session) -> dict:
    testcase_no, testcase_title = crud_coverage.get_testcase_info(db, coverage.testcase_id)
    return CoverageOut(
        id=coverage.id,
        feature_point_id=coverage.feature_point_id,
        testcase_id=coverage.testcase_id,
        coverage_type=coverage.coverage_type or "functional",
        confidence=coverage.confidence or 0,
        evidence=coverage.evidence or "",
        created_at=coverage.created_at,
        feature_point_name=crud_coverage.get_feature_point_name(db, coverage.feature_point_id),
        testcase_no=testcase_no,
        testcase_title=testcase_title,
    ).model_dump()


@router.get("/feature-points/{feature_point_id}/testcases", response_model=ResponseModel)
def list_testcases_by_feature_point(
    feature_point_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    coverages = crud_coverage.get_testcases_by_feature_point(db, feature_point_id)
    return ResponseModel(data=[_to_out(c, db) for c in coverages])


@router.get("/testcases/{testcase_id}/feature-points", response_model=ResponseModel)
def list_feature_points_by_testcase(
    testcase_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    coverages = crud_coverage.get_feature_points_by_testcase(db, testcase_id)
    return ResponseModel(data=[_to_out(c, db) for c in coverages])


@router.post("/feature-points/{feature_point_id}/testcases/{testcase_id}", response_model=ResponseModel)
def create_feature_point_testcase_coverage(
    feature_point_id: int,
    testcase_id: int,
    data: CoverageCreate | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    if not db.query(FeaturePoint).filter(FeaturePoint.id == feature_point_id).first():
        raise HTTPException(status_code=404, detail="功能点不存在")
    if not db.query(TestCase).filter(TestCase.id == testcase_id).first():
        raise HTTPException(status_code=404, detail="用例不存在")

    payload = data or CoverageCreate(feature_point_id=feature_point_id, testcase_id=testcase_id)
    payload.feature_point_id = feature_point_id
    payload.testcase_id = testcase_id
    coverage = crud_coverage.create_coverage(db, payload)
    return ResponseModel(data=_to_out(coverage, db), message="关联成功")


@router.put("/{coverage_id}", response_model=ResponseModel)
def update_coverage(
    coverage_id: int,
    data: CoverageUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    coverage = crud_coverage.get_coverage(db, coverage_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="覆盖关系不存在")
    coverage = crud_coverage.update_coverage(db, coverage, data)
    return ResponseModel(data=_to_out(coverage, db), message="更新成功")


@router.delete("/{coverage_id}", response_model=ResponseModel)
def delete_coverage(
    coverage_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    coverage = crud_coverage.get_coverage(db, coverage_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="覆盖关系不存在")
    crud_coverage.delete_coverage(db, coverage)
    return ResponseModel(message="删除成功")
