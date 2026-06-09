from pydantic import BaseModel, Field
from datetime import datetime


class TestCaseCreate(BaseModel):
    title: str
    priority: str = "高"
    exec_status: str = "待执行"
    executor_id: int | None = None
    project_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None  # FK → modules 表
    module: str | None = None     # 模块代码（module_id 时自动填充）
    case_type: str = "ui"
    automation_status: str = "not_generated"
    automation_path: str = ""
    selector_path: str = ""
    source: str = "manual"
    version: str = "v1.0"
    fingerprint: str = ""
    raw_data: dict = Field(default_factory=dict)
    preconditions: str = ""       # 前置条件
    test_data: str = ""           # 测试数据
    test_steps: str = ""          # 测试步骤
    expected_result: str = ""     # 预期结果


class TestCaseUpdate(BaseModel):
    title: str | None = None
    priority: str | None = None
    exec_status: str | None = None
    executor_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None
    case_type: str | None = None
    automation_status: str | None = None
    automation_path: str | None = None
    selector_path: str | None = None
    source: str | None = None
    version: str | None = None
    fingerprint: str | None = None
    raw_data: dict | None = None
    preconditions: str | None = None
    test_data: str | None = None
    test_steps: str | None = None
    expected_result: str | None = None
    actual_result: str | None = None


class TestCaseOut(BaseModel):
    id: int
    case_no: str
    title: str
    priority: str = "高"
    exec_status: str = "待执行"
    executor: str = ""  # 执行人姓名
    project: str = ""  # 项目名称
    project_id: int | None = None
    sprint_id: int | None = None
    sprint_name: str = ""
    module_id: int | None = None
    module: str | None = None       # 英文代码
    module_name: str = ""           # 中文名称（来自 modules.name）
    case_type: str = "ui"
    automation_status: str = "not_generated"
    automation_path: str = ""
    selector_path: str = ""
    source: str = "manual"
    version: str = "v1.0"
    fingerprint: str = ""
    raw_data: dict = Field(default_factory=dict)
    coverage_count: int = 0
    preconditions: str = ""
    test_data: str = ""
    test_steps: str = ""
    expected_result: str = ""
    actual_result: str = ""
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
