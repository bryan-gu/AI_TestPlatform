from pydantic import BaseModel
from datetime import datetime


class ReportCreate(BaseModel):
    name: str
    project_id: int | None = None


class ReportUpdate(BaseModel):
    name: str | None = None
    status: str | None = None


class ReportOut(BaseModel):
    id: int
    name: str
    project: str = ""  # 项目名称
    project_id: int | None = None
    pass_rate: float = 0.0
    defect_count: int = 0
    status: str = "待审批"
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ReportStats(BaseModel):
    monthlyReports: int = 0
    monthlyChange: int = 0
    avgPassRate: int = 0
    totalDefects: int = 0
    fixedDefects: int = 0
    pendingApproval: int = 0
