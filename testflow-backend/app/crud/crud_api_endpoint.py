from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.api_endpoint import ApiEndpoint, TestCaseApiEndpoint
from app.schemas.api_endpoint import ApiEndpointCreate, ApiEndpointUpdate
from app.schemas.api_endpoint import TestCaseApiEndpointCreate, TestCaseApiEndpointUpdate


# ========== ApiEndpoint CRUD ==========

def get_api_endpoints(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    source_asset_id: int | None = None,
    module_id: int | None = None,
    method: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[ApiEndpoint]:
    query = db.query(ApiEndpoint).filter(ApiEndpoint.is_deleted == False)  # noqa: E712
    if project_id is not None:
        query = query.filter(ApiEndpoint.project_id == project_id)
    if sprint_id is not None:
        query = query.filter(ApiEndpoint.sprint_id == sprint_id)
    if source_asset_id is not None:
        query = query.filter(ApiEndpoint.source_asset_id == source_asset_id)
    if module_id is not None:
        query = query.filter(ApiEndpoint.module_id == module_id)
    if method:
        query = query.filter(ApiEndpoint.method == method.upper())
    if status:
        query = query.filter(ApiEndpoint.status == status)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            (ApiEndpoint.path.ilike(kw))
            | (ApiEndpoint.summary.ilike(kw))
            | (ApiEndpoint.tag.ilike(kw))
            | (ApiEndpoint.description.ilike(kw))
        )
    return query.order_by(ApiEndpoint.path, ApiEndpoint.method).offset(skip).limit(limit).all()


def count_api_endpoints(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    source_asset_id: int | None = None,
    module_id: int | None = None,
    method: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> int:
    query = db.query(func.count(ApiEndpoint.id)).filter(ApiEndpoint.is_deleted == False)  # noqa: E712
    if project_id is not None:
        query = query.filter(ApiEndpoint.project_id == project_id)
    if sprint_id is not None:
        query = query.filter(ApiEndpoint.sprint_id == sprint_id)
    if source_asset_id is not None:
        query = query.filter(ApiEndpoint.source_asset_id == source_asset_id)
    if module_id is not None:
        query = query.filter(ApiEndpoint.module_id == module_id)
    if method:
        query = query.filter(ApiEndpoint.method == method.upper())
    if status:
        query = query.filter(ApiEndpoint.status == status)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            (ApiEndpoint.path.ilike(kw))
            | (ApiEndpoint.summary.ilike(kw))
            | (ApiEndpoint.tag.ilike(kw))
            | (ApiEndpoint.description.ilike(kw))
        )
    return query.scalar()


def get_api_endpoint(db: Session, endpoint_id: int) -> ApiEndpoint | None:
    return db.query(ApiEndpoint).filter(
        ApiEndpoint.id == endpoint_id,
        ApiEndpoint.is_deleted == False,  # noqa: E712
    ).first()


def upsert_api_endpoint(db: Session, data: ApiEndpointCreate, *, commit: bool = False) -> ApiEndpoint:
    """按 fingerprint 或 (project_id + source_asset_id + method + path) 幂等导入"""
    existing = None
    if data.fingerprint:
        existing = db.query(ApiEndpoint).filter(
            ApiEndpoint.fingerprint == data.fingerprint,
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).first()
    if not existing and data.project_id and data.source_asset_id:
        existing = db.query(ApiEndpoint).filter(
            ApiEndpoint.project_id == data.project_id,
            ApiEndpoint.source_asset_id == data.source_asset_id,
            ApiEndpoint.method == data.method,
            ApiEndpoint.path == data.path,
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).first()

    if existing:
        # 更新已有记录
        existing.method = data.method
        existing.path = data.path
        existing.summary = data.summary
        existing.description = data.description
        existing.tag = data.tag
        existing.operation_id = data.operation_id
        existing.status = data.status
        existing.priority = data.priority
        existing.auth_required = data.auth_required
        existing.request_schema = data.request_schema
        existing.response_schema = data.response_schema
        existing.parameters = data.parameters
        existing.error_codes = data.error_codes
        existing.version = data.version
        existing.fingerprint = data.fingerprint
        existing.raw_data = data.raw_data
        if data.module_id is not None:
            existing.module_id = data.module_id
        if commit:
            db.commit()
            db.refresh(existing)
        else:
            db.flush()
        return existing

    endpoint = ApiEndpoint(
        project_id=data.project_id,
        sprint_id=data.sprint_id,
        source_asset_id=data.source_asset_id,
        module_id=data.module_id,
        method=data.method,
        path=data.path,
        summary=data.summary,
        description=data.description,
        tag=data.tag,
        operation_id=data.operation_id,
        status=data.status,
        priority=data.priority,
        auth_required=data.auth_required,
        request_schema=data.request_schema,
        response_schema=data.response_schema,
        parameters=data.parameters,
        error_codes=data.error_codes,
        version=data.version,
        fingerprint=data.fingerprint,
        raw_data=data.raw_data,
    )
    db.add(endpoint)
    if commit:
        db.commit()
        db.refresh(endpoint)
    else:
        db.flush()
    return endpoint


def update_api_endpoint(db: Session, endpoint: ApiEndpoint, data: ApiEndpointUpdate) -> ApiEndpoint:
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(endpoint, field, value)
    db.commit()
    db.refresh(endpoint)
    return endpoint


def soft_delete_api_endpoint(db: Session, endpoint: ApiEndpoint) -> None:
    endpoint.is_deleted = True
    db.commit()


def get_testcase_count(db: Session, endpoint_id: int) -> int:
    return db.query(func.count(TestCaseApiEndpoint.id)).filter(
        TestCaseApiEndpoint.api_endpoint_id == endpoint_id
    ).scalar()


# ========== TestCaseApiEndpoint CRUD ==========

def get_testcases_by_endpoint(db: Session, endpoint_id: int) -> list[TestCaseApiEndpoint]:
    return db.query(TestCaseApiEndpoint).filter(
        TestCaseApiEndpoint.api_endpoint_id == endpoint_id
    ).order_by(TestCaseApiEndpoint.created_at.desc()).all()


def get_endpoints_by_testcase(db: Session, testcase_id: int) -> list[TestCaseApiEndpoint]:
    return db.query(TestCaseApiEndpoint).filter(
        TestCaseApiEndpoint.testcase_id == testcase_id
    ).order_by(TestCaseApiEndpoint.created_at.desc()).all()


def link_testcase_endpoint(db: Session, data: TestCaseApiEndpointCreate, *, commit: bool = True) -> TestCaseApiEndpoint:
    """关联测试用例与接口，已存在则更新覆盖类型和置信度"""
    existing = db.query(TestCaseApiEndpoint).filter(
        TestCaseApiEndpoint.testcase_id == data.testcase_id,
        TestCaseApiEndpoint.api_endpoint_id == data.api_endpoint_id,
    ).first()
    if existing:
        existing.coverage_type = data.coverage_type
        existing.confidence = data.confidence
        existing.evidence = data.evidence
        if commit:
            db.commit()
            db.refresh(existing)
        else:
            db.flush()
        return existing

    link = TestCaseApiEndpoint(
        testcase_id=data.testcase_id,
        api_endpoint_id=data.api_endpoint_id,
        coverage_type=data.coverage_type,
        confidence=data.confidence,
        evidence=data.evidence,
    )
    db.add(link)
    if commit:
        db.commit()
        db.refresh(link)
    else:
        db.flush()
    return link


def unlink_testcase_endpoint(db: Session, testcase_id: int, endpoint_id: int) -> bool:
    link = db.query(TestCaseApiEndpoint).filter(
        TestCaseApiEndpoint.testcase_id == testcase_id,
        TestCaseApiEndpoint.api_endpoint_id == endpoint_id,
    ).first()
    if not link:
        return False
    db.delete(link)
    db.commit()
    return True
