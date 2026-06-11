import json
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.api_endpoint import (
    ApiEndpointCreate,
    ApiEndpointUpdate,
    ApiEndpointOut,
    ApiEndpointImportRequest,
    ApiEndpointImportResult,
    TestCaseApiEndpointCreate,
    TestCaseApiEndpointOut,
)
from app.crud import crud_api_endpoint, crud_trace_link
from app.models.api_endpoint import ApiEndpoint, TestCaseApiEndpoint
from app.models.knowledge_asset import KnowledgeAsset
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.module import Module
from app.models.testcase import TestCase
from app.services.api_doc_parser import parse_openapi_file, build_endpoint_fingerprint


router = APIRouter(prefix="/api-endpoints", tags=["接口清单"])


def _to_out(endpoint: ApiEndpoint, db: Session) -> dict:
    """将 ApiEndpoint ORM 对象转换为输出字典"""
    # 关联名称
    project_name = ""
    if endpoint.project_id:
        proj = db.query(Project).filter(Project.id == endpoint.project_id).first()
        project_name = proj.name if proj else ""

    sprint_name = ""
    if endpoint.sprint_id:
        sp = db.query(Sprint).filter(Sprint.id == endpoint.sprint_id).first()
        sprint_name = sp.name if sp else ""

    source_asset_name = ""
    if endpoint.source_asset_id:
        asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == endpoint.source_asset_id).first()
        source_asset_name = asset.name if asset else ""

    module_name = ""
    if endpoint.module_id:
        mod = db.query(Module).filter(Module.id == endpoint.module_id).first()
        module_name = mod.name if mod else ""

    testcase_count = crud_api_endpoint.get_testcase_count(db, endpoint.id)

    return ApiEndpointOut(
        id=endpoint.id,
        project_id=endpoint.project_id,
        sprint_id=endpoint.sprint_id,
        source_asset_id=endpoint.source_asset_id,
        module_id=endpoint.module_id,
        method=endpoint.method,
        path=endpoint.path,
        summary=endpoint.summary or "",
        description=endpoint.description or "",
        tag=endpoint.tag or "",
        operation_id=endpoint.operation_id or "",
        status=endpoint.status or "active",
        priority=endpoint.priority or "中",
        auth_required=endpoint.auth_required,
        request_schema=endpoint.request_schema or {},
        response_schema=endpoint.response_schema or {},
        parameters=endpoint.parameters or [],
        error_codes=endpoint.error_codes or [],
        version=endpoint.version or "v1",
        fingerprint=endpoint.fingerprint or "",
        is_deleted=endpoint.is_deleted or False,
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
        project_name=project_name,
        sprint_name=sprint_name,
        source_asset_name=source_asset_name,
        module_name=module_name,
        testcase_count=testcase_count,
    ).model_dump()


def _link_to_out(link: TestCaseApiEndpoint, db: Session) -> dict:
    """将 TestCaseApiEndpoint ORM 对象转换为输出字典"""
    testcase_name = ""
    testcase_case_no = ""
    tc = db.query(TestCase).filter(TestCase.id == link.testcase_id).first()
    if tc:
        testcase_name = tc.title
        testcase_case_no = tc.case_no or ""

    api_method = ""
    api_path = ""
    api_summary = ""
    ep = db.query(ApiEndpoint).filter(ApiEndpoint.id == link.api_endpoint_id).first()
    if ep:
        api_method = ep.method
        api_path = ep.path
        api_summary = ep.summary or ""

    return TestCaseApiEndpointOut(
        id=link.id,
        testcase_id=link.testcase_id,
        api_endpoint_id=link.api_endpoint_id,
        coverage_type=link.coverage_type or "functional",
        confidence=link.confidence or 100,
        evidence=link.evidence or "",
        created_at=link.created_at,
        testcase_name=testcase_name,
        testcase_case_no=testcase_case_no,
        api_method=api_method,
        api_path=api_path,
        api_summary=api_summary,
    ).model_dump()


# ========== 接口端点 ==========

@router.get("", response_model=ResponseModel)
def list_api_endpoints(
    project_id: int | None = Query(None, description="项目 ID"),
    sprint_id: int | None = Query(None, description="Sprint ID"),
    source_asset_id: int | None = Query(None, description="来源资产 ID"),
    module_id: int | None = Query(None, description="模块 ID"),
    method: str | None = Query(None, description="HTTP Method"),
    status: str | None = Query(None, description="状态"),
    keyword: str | None = Query(None, description="关键词"),
    skip: int = Query(0, description="分页偏移"),
    limit: int = Query(100, description="每页数量"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    endpoints = crud_api_endpoint.get_api_endpoints(
        db,
        project_id=project_id,
        sprint_id=sprint_id,
        source_asset_id=source_asset_id,
        module_id=module_id,
        method=method,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )
    total = crud_api_endpoint.count_api_endpoints(
        db,
        project_id=project_id,
        sprint_id=sprint_id,
        source_asset_id=source_asset_id,
        module_id=module_id,
        method=method,
        status=status,
        keyword=keyword,
    )
    return ResponseModel(data={
        "items": [_to_out(ep, db) for ep in endpoints],
        "total": total,
    })


@router.get("/{endpoint_id}", response_model=ResponseModel)
def get_api_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    endpoint = crud_api_endpoint.get_api_endpoint(db, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="接口端点不存在")
    return ResponseModel(data=_to_out(endpoint, db))


@router.post("/import-openapi", response_model=ResponseModel)
def import_openapi(
    data: ApiEndpointImportRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """从 KnowledgeAsset 导入 OpenAPI 接口"""
    # 1. 校验资产存在
    asset = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == data.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    # 校验资产类型
    is_openapi = (
        asset.asset_type == "api_doc_openapi"
        or (asset.asset_metadata or {}).get("is_openapi") is True
    )
    if not is_openapi:
        raise HTTPException(status_code=400, detail="该资产不是 OpenAPI 接口文档")

    # 2. 读取原始文件
    file_path = asset.file_path
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="资产文件路径无效或文件不存在")

    # 3. 解析
    try:
        raw_endpoints = parse_openapi_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析 OpenAPI 文件失败: {str(e)}")

    if not raw_endpoints:
        return ResponseModel(data=ApiEndpointImportResult(total=0, created=0, updated=0, skipped=0).model_dump())

    # 4. 幂等写入
    created = 0
    updated = 0
    for raw in raw_endpoints:
        fingerprint = build_endpoint_fingerprint(
            project_id=asset.project_id,
            source_asset_id=asset.id,
            method=raw["method"],
            path=raw["path"],
            operation_id=raw.get("operation_id", ""),
        )
        create_data = ApiEndpointCreate(
            project_id=asset.project_id,
            sprint_id=asset.sprint_id,
            source_asset_id=asset.id,
            method=raw["method"],
            path=raw["path"],
            summary=raw.get("summary", ""),
            description=raw.get("description", ""),
            tag=raw.get("tag", ""),
            operation_id=raw.get("operation_id", ""),
            status=raw.get("status", "active"),
            priority=raw.get("priority", "中"),
            auth_required=raw.get("auth_required"),
            request_schema=raw.get("request_schema", {}),
            response_schema=raw.get("response_schema", {}),
            parameters=raw.get("parameters", []),
            error_codes=raw.get("error_codes", []),
            version="v1",
            fingerprint=fingerprint,
            raw_data=raw.get("raw_data", {}),
        )

        # 检查是创建还是更新
        existing = None
        if fingerprint:
            existing = db.query(ApiEndpoint).filter(
                ApiEndpoint.fingerprint == fingerprint,
                ApiEndpoint.is_deleted == False,  # noqa: E712
            ).first()

        endpoint = crud_api_endpoint.upsert_api_endpoint(db, create_data, commit=False)

        if existing:
            updated += 1
        else:
            created += 1

        # 5. 写 TraceLink: asset -> api, derived_from
        from app.schemas.trace_link import TraceLinkCreate
        crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
            project_id=asset.project_id,
            sprint_id=asset.sprint_id,
            source_type="asset",
            source_id=asset.id,
            target_type="api",
            target_id=endpoint.id,
            relation_type="derived_from",
            confidence=100,
            evidence="OpenAPI 导入自动关联",
            metadata={"import_type": "openapi"},
            created_by="import-openapi",
        ), commit=False)

    db.commit()

    result = ApiEndpointImportResult(
        total=len(raw_endpoints),
        created=created,
        updated=updated,
        skipped=0,
    )
    return ResponseModel(data=result.model_dump(), message=f"导入完成：共 {result.total} 个接口，新建 {result.created} 个，更新 {result.updated} 个")


@router.delete("/{endpoint_id}", response_model=ResponseModel)
def delete_api_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    endpoint = crud_api_endpoint.get_api_endpoint(db, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="接口端点不存在")
    crud_api_endpoint.soft_delete_api_endpoint(db, endpoint)
    return ResponseModel(message="删除成功")


# ========== 接口-用例关联 ==========

@router.get("/{endpoint_id}/testcases", response_model=ResponseModel)
def get_endpoint_testcases(
    endpoint_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    links = crud_api_endpoint.get_testcases_by_endpoint(db, endpoint_id)
    return ResponseModel(data=[_link_to_out(link, db) for link in links])


@router.post("/{endpoint_id}/link-testcase/{case_id}", response_model=ResponseModel)
def link_testcase(
    endpoint_id: int,
    case_id: int,
    coverage_type: str = Query("functional", description="覆盖类型"),
    confidence: int = Query(100, description="置信度"),
    evidence: str = Query("", description="证据"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    # 校验接口存在
    endpoint = crud_api_endpoint.get_api_endpoint(db, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="接口端点不存在")

    link = crud_api_endpoint.link_testcase_endpoint(db, TestCaseApiEndpointCreate(
        testcase_id=case_id,
        api_endpoint_id=endpoint_id,
        coverage_type=coverage_type,
        confidence=confidence,
        evidence=evidence,
    ))

    # 写 TraceLink: testcase -> api, tests_api
    from app.schemas.trace_link import TraceLinkCreate
    crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
        project_id=endpoint.project_id,
        sprint_id=endpoint.sprint_id,
        source_type="testcase",
        source_id=case_id,
        target_type="api",
        target_id=endpoint_id,
        relation_type="tests_api",
        confidence=confidence,
        evidence=evidence or "手动关联",
        metadata={"coverage_type": coverage_type},
        created_by="manual",
    ))

    return ResponseModel(data=_link_to_out(link, db), message="关联成功")


@router.delete("/{endpoint_id}/link-testcase/{case_id}", response_model=ResponseModel)
def unlink_testcase(
    endpoint_id: int,
    case_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    ok = crud_api_endpoint.unlink_testcase_endpoint(db, case_id, endpoint_id)
    if not ok:
        raise HTTPException(status_code=404, detail="关联关系不存在")

    # 同步删除 TraceLink
    crud_trace_link.deactivate_entity_relation(
        db,
        source_type="testcase",
        source_id=case_id,
        target_type="api",
        target_id=endpoint_id,
        relation_type="tests_api",
    )

    return ResponseModel(message="取消关联成功")


@router.get("/testcases/{case_id}", response_model=ResponseModel)
def get_testcase_endpoints(
    case_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    links = crud_api_endpoint.get_endpoints_by_testcase(db, case_id)
    return ResponseModel(data=[_link_to_out(link, db) for link in links])
