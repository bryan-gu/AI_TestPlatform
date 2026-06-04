from pydantic import BaseModel
from datetime import datetime


class ReportCreate(BaseModel):
    name: str
    project_id: int | None = None
    report_type: str = ""     # 回归/冒烟/迭代/全量
    test_scope: str = ""      # 测试范围描述


class ReportUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    report_type: str | None = None
    test_scope: str | None = None


class ReportOut(BaseModel):
    id: int
    name: str
    project: str = ""  # 项目名称
    project_id: int | None = None
    pass_rate: float = 0.0
    defect_count: int = 0
    status: str = "待审批"
    report_type: str = ""
    test_scope: str = ""
    approved_by: int | None = None
    approved_by_name: str = ""   # 审批人姓名（computed）
    approved_at: datetime | None = None
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
