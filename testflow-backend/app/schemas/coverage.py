from datetime import datetime
from pydantic import BaseModel


class CoverageCreate(BaseModel):
    feature_point_id: int
    testcase_id: int
    coverage_type: str = "functional"
    confidence: int = 100
    evidence: str = ""


class CoverageUpdate(BaseModel):
    coverage_type: str | None = None
    confidence: int | None = None
    evidence: str | None = None


class CoverageOut(BaseModel):
    id: int
    feature_point_id: int
    testcase_id: int
    coverage_type: str = "functional"
    confidence: int = 100
    evidence: str = ""
    created_at: datetime | None = None
    feature_point_name: str = ""
    testcase_no: str = ""
    testcase_title: str = ""

    class Config:
        from_attributes = True
