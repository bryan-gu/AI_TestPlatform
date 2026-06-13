"""接口文档导入共享服务。

供 HTTP 接口层（api_endpoints.py）和本地项目导入（local_project_importer.py）复用，
将解析后的接口端点字典幂等写入 ApiEndpoint，并写 asset -> api / derived_from TraceLink。
"""
from sqlalchemy.orm import Session

from app.models.api_endpoint import ApiEndpoint
from app.models.knowledge_asset import KnowledgeAsset
from app.crud import crud_api_endpoint, crud_trace_link
from app.schemas.api_endpoint import ApiEndpointCreate
from app.schemas.trace_link import TraceLinkCreate
from app.services.api_doc_parser import build_endpoint_fingerprint


def upsert_endpoints_for_asset(
    db: Session, asset: KnowledgeAsset, raw_endpoints: list[dict]
) -> tuple[int, int]:
    """幂等写入接口端点，并写 asset -> api / derived_from TraceLink。返回 (created, updated)。"""
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

        crud_trace_link.upsert_trace_link(db, TraceLinkCreate(
            project_id=asset.project_id,
            sprint_id=asset.sprint_id,
            source_type="asset",
            source_id=asset.id,
            target_type="api",
            target_id=endpoint.id,
            relation_type="derived_from",
            confidence=100,
            evidence="接口文档导入自动关联",
            metadata={"import_type": raw.get("raw_data", {}).get("source", "openapi")},
            created_by="import-api-doc",
        ), commit=False)

    db.commit()
    return created, updated
