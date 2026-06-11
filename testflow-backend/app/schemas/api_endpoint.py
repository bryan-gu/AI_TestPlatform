from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime


# ========== ApiEndpoint ==========

class ApiEndpointCreate(BaseModel):
    project_id: int | None = None
    sprint_id: int | None = None
    source_asset_id: int | None = None
    module_id: int | None = None
    method: str
    path: str
    summary: str = ""
    description: str = ""
    tag: str = ""
    operation_id: str = ""
    status: str = "active"
    priority: str = "中"
    auth_required: bool | None = None
    request_schema: dict[str, Any] = Field(default_factory=dict)
    response_schema: dict[str, Any] = Field(default_factory=dict)
    parameters: list = Field(default_factory=list)
    error_codes: list = Field(default_factory=list)
    version: str = "v1"
    fingerprint: str = ""
    raw_data: dict[str, Any] = Field(default_factory=dict)


class ApiEndpointUpdate(BaseModel):
    module_id: int | None = None
    summary: str | None = None
    description: str | None = None
    tag: str | None = None
    status: str | None = None
    priority: str | None = None
    auth_required: bool | None = None
    request_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None
    parameters: list | None = None
    error_codes: list | None = None
    version: str | None = None


class ApiEndpointOut(BaseModel):
    id: int
    project_id: int | None = None
    sprint_id: int | None = None
    source_asset_id: int | None = None
    module_id: int | None = None
    method: str
    path: str
    summary: str = ""
    description: str = ""
    tag: str = ""
    operation_id: str = ""
    status: str = "active"
    priority: str = "中"
    auth_required: bool | None = None
    request_schema: dict[str, Any] = Field(default_factory=dict)
    response_schema: dict[str, Any] = Field(default_factory=dict)
    parameters: list = Field(default_factory=list)
    error_codes: list = Field(default_factory=list)
    version: str = "v1"
    fingerprint: str = ""
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # 关联名称（前端展示用）
    project_name: str = ""
    sprint_name: str = ""
    source_asset_name: str = ""
    module_name: str = ""
    testcase_count: int = 0

    class Config:
        from_attributes = True


class ApiEndpointImportRequest(BaseModel):
    asset_id: int
    overwrite: bool = False


class ApiEndpointImportResult(BaseModel):
    total: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0


# ========== TestCaseApiEndpoint ==========

class TestCaseApiEndpointCreate(BaseModel):
    testcase_id: int
    api_endpoint_id: int
    coverage_type: str = "functional"
    confidence: int = 100
    evidence: str = ""


class TestCaseApiEndpointUpdate(BaseModel):
    coverage_type: str | None = None
    confidence: int | None = None
    evidence: str | None = None


class TestCaseApiEndpointOut(BaseModel):
    id: int
    testcase_id: int
    api_endpoint_id: int
    coverage_type: str = "functional"
    confidence: int = 100
    evidence: str = ""
    created_at: datetime | None = None
    # 关联名称
    testcase_name: str = ""
    testcase_case_no: str = ""
    api_method: str = ""
    api_path: str = ""
    api_summary: str = ""

    class Config:
        from_attributes = True
