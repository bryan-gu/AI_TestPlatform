from pydantic import BaseModel
from datetime import datetime


class TestCaseCreate(BaseModel):
    title: str
    priority: str = "中"
    exec_status: str = "待执行"
    executor_id: int | None = None
    project_id: int | None = None


class TestCaseUpdate(BaseModel):
    title: str | None = None
    priority: str | None = None
    exec_status: str | None = None
    executor_id: int | None = None


class TestCaseOut(BaseModel):
    id: int
    case_no: str
    title: str
    priority: str = "中"
    exec_status: str = "待执行"
    executor: str = ""  # 执行人姓名
    project: str = ""  # 项目名称
    project_id: int | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class TestCaseStats(BaseModel):
    total: int = 0
    projectCount: int = 0
    passed: int = 0
    passRate: int = 0
    failed: int = 0
    pending: int = 0
