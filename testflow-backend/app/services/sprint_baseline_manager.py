from copy import deepcopy

from sqlalchemy.orm import Session

from app.crud import crud_graph, crud_sprint, crud_trace_link
from app.models.api_endpoint import ApiEndpoint
from app.models.coverage import FeaturePointTestCase
from app.models.feature_point import FeaturePoint
from app.models.sprint import Sprint
from app.models.testcase import TestCase
from app.models.trace_link import TraceLink
from app.schemas.trace_link import TraceLinkCreate


class SprintBaselineManager:
    """同步普通 Sprint 的结构化实体到项目最新汇总基线。"""

    MAPPED_ENTITY_TYPES = {"feature", "api", "testcase"}

    def __init__(self, db: Session):
        self.db = db

    def sync_sprint_to_all(self, source_sprint_id: int) -> dict:
        source_sprint = crud_sprint.get_sprint(self.db, source_sprint_id)
        if not source_sprint:
            raise ValueError("源 Sprint 不存在")
        if crud_sprint.is_sprint_all(source_sprint):
            raise ValueError("sprint_all 不能作为同步源")
        if not source_sprint.project_id:
            raise ValueError("源 Sprint 必须归属项目")

        target_sprint = crud_sprint.ensure_sprint_all(self.db, source_sprint.project_id)
        if target_sprint.id == source_sprint.id:
            raise ValueError("源 Sprint 与 sprint_all 不能相同")

        feature_map, feature_stats = self._sync_feature_points(source_sprint, target_sprint)
        api_map, api_stats = self._sync_api_endpoints(source_sprint, target_sprint)
        testcase_map, testcase_stats = self._sync_testcases(source_sprint, target_sprint)
        coverage_stats = self._sync_coverages(feature_map, testcase_map)
        trace_stats = self._sync_trace_links(
            source_sprint,
            target_sprint,
            {
                "feature": feature_map,
                "api": api_map,
                "testcase": testcase_map,
            },
        )

        self.db.commit()
        graph = crud_graph.generate_graph_for_scope(
            self.db,
            project_id=source_sprint.project_id,
            sprint_id=target_sprint.id,
        )

        return {
            "source_sprint": self._sprint_summary(source_sprint),
            "target_sprint": self._sprint_summary(target_sprint),
            "features": feature_stats,
            "api_endpoints": api_stats,
            "testcases": testcase_stats,
            "coverages": coverage_stats,
            "trace_links": trace_stats,
            "graph": {
                "id": graph.id,
                "node_count": graph.node_count or 0,
                "edge_count": graph.edge_count or 0,
                "status": graph.status,
            },
        }

    def _sync_feature_points(self, source_sprint: Sprint, target_sprint: Sprint) -> tuple[dict[int, FeaturePoint], dict]:
        stats = self._new_stats()
        feature_map: dict[int, FeaturePoint] = {}
        source_items = self.db.query(FeaturePoint).filter(
            FeaturePoint.sprint_id == source_sprint.id,
            FeaturePoint.is_deleted == False,  # noqa: E712
        ).all()

        for source in source_items:
            target = self._find_target_feature(source, target_sprint.id)
            created = target is None
            if created:
                target = FeaturePoint(name=source.name, sprint_id=target_sprint.id)
                self.db.add(target)

            target.name = source.name
            target.description = source.description or ""
            target.entry_path = source.entry_path or ""
            target.interaction_elements = source.interaction_elements or ""
            target.business_rules = source.business_rules or ""
            target.priority = source.priority or "中"
            target.source_doc_id = source.source_doc_id
            target.sprint_id = target_sprint.id
            target.module_id = source.module_id
            target.linked_cases = source.linked_cases or ""
            target.source_type = source.source_type or "manual"
            target.status = source.status or "active"
            target.version = source.version or "v1.0"
            target.fingerprint = source.fingerprint or ""
            target.raw_data = self._merge_baseline_metadata(
                source.raw_data,
                source_sprint.id,
                "baseline_source_feature_id",
                source.id,
            )
            target.is_deleted = False
            self.db.flush()

            feature_map[source.id] = target
            self._count(stats, created)

        return feature_map, stats

    def _sync_api_endpoints(self, source_sprint: Sprint, target_sprint: Sprint) -> tuple[dict[int, ApiEndpoint], dict]:
        stats = self._new_stats()
        api_map: dict[int, ApiEndpoint] = {}
        source_items = self.db.query(ApiEndpoint).filter(
            ApiEndpoint.sprint_id == source_sprint.id,
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).all()

        for source in source_items:
            target = self._find_target_api(source, target_sprint.id, source_sprint.project_id)
            created = target is None
            if created:
                target = ApiEndpoint(
                    project_id=source.project_id or source_sprint.project_id,
                    sprint_id=target_sprint.id,
                    method=(source.method or "").upper(),
                    path=source.path or "",
                )
                self.db.add(target)

            target.project_id = source.project_id or source_sprint.project_id
            target.sprint_id = target_sprint.id
            target.source_asset_id = source.source_asset_id
            target.module_id = source.module_id
            target.method = (source.method or "").upper()
            target.path = source.path or ""
            target.summary = source.summary or ""
            target.description = source.description or ""
            target.tag = source.tag or ""
            target.operation_id = source.operation_id or ""
            target.status = source.status or "active"
            target.priority = source.priority or "中"
            target.auth_required = source.auth_required
            target.request_schema = deepcopy(source.request_schema) if source.request_schema is not None else {}
            target.response_schema = deepcopy(source.response_schema) if source.response_schema is not None else {}
            target.parameters = deepcopy(source.parameters) if source.parameters is not None else []
            target.error_codes = deepcopy(source.error_codes) if source.error_codes is not None else []
            target.version = source.version or "v1"
            target.fingerprint = source.fingerprint or ""
            target.raw_data = self._merge_baseline_metadata(
                source.raw_data,
                source_sprint.id,
                "baseline_source_api_id",
                source.id,
            )
            target.is_deleted = False
            self.db.flush()

            api_map[source.id] = target
            self._count(stats, created)

        return api_map, stats

    def _sync_testcases(self, source_sprint: Sprint, target_sprint: Sprint) -> tuple[dict[int, TestCase], dict]:
        stats = self._new_stats()
        testcase_map: dict[int, TestCase] = {}
        source_items = self.db.query(TestCase).filter(
            TestCase.sprint_id == source_sprint.id,
            TestCase.is_deleted == False,  # noqa: E712
        ).all()

        for source in source_items:
            target = self._find_target_testcase(source, target_sprint.id, source_sprint.project_id)
            created = target is None
            if created:
                target = TestCase(
                    case_no=source.case_no or f"BASELINE-{source.id}",
                    title=source.title,
                    project_id=source.project_id or source_sprint.project_id,
                    sprint_id=target_sprint.id,
                )
                self.db.add(target)

            target.case_no = source.case_no or f"BASELINE-{source.id}"
            target.title = source.title
            target.priority = source.priority or "中"
            target.exec_status = source.exec_status or "待执行"
            target.executor_id = source.executor_id
            target.project_id = source.project_id or source_sprint.project_id
            target.sprint_id = target_sprint.id
            target.module = source.module
            target.module_id = source.module_id
            target.case_type = source.case_type or "ui"
            target.automation_status = source.automation_status or "not_generated"
            target.automation_path = source.automation_path or ""
            target.selector_path = source.selector_path or ""
            target.source = source.source or "manual"
            target.version = source.version or "v1.0"
            target.fingerprint = source.fingerprint or ""
            target.raw_data = self._merge_baseline_metadata(
                source.raw_data,
                source_sprint.id,
                "baseline_source_testcase_id",
                source.id,
            )
            target.preconditions = source.preconditions or ""
            target.test_data = source.test_data or ""
            target.test_steps = source.test_steps or ""
            target.expected_result = source.expected_result or ""
            target.actual_result = source.actual_result or ""
            target.is_deleted = False
            self.db.flush()

            testcase_map[source.id] = target
            self._count(stats, created)

        return testcase_map, stats

    def _sync_coverages(self, feature_map: dict[int, FeaturePoint], testcase_map: dict[int, TestCase]) -> dict:
        stats = self._new_stats()
        if not feature_map or not testcase_map:
            return stats

        source_items = self.db.query(FeaturePointTestCase).filter(
            FeaturePointTestCase.feature_point_id.in_(list(feature_map.keys())),
            FeaturePointTestCase.testcase_id.in_(list(testcase_map.keys())),
        ).all()

        for source in source_items:
            target_feature = feature_map.get(source.feature_point_id)
            target_case = testcase_map.get(source.testcase_id)
            if not target_feature or not target_case:
                stats["skipped"] += 1
                continue

            target = self.db.query(FeaturePointTestCase).filter(
                FeaturePointTestCase.feature_point_id == target_feature.id,
                FeaturePointTestCase.testcase_id == target_case.id,
            ).first()
            created = target is None
            if created:
                target = FeaturePointTestCase(
                    feature_point_id=target_feature.id,
                    testcase_id=target_case.id,
                )
                self.db.add(target)

            target.coverage_type = source.coverage_type or "functional"
            target.confidence = source.confidence or 100
            target.evidence = source.evidence or ""
            self.db.flush()
            self._count(stats, created)

        return stats

    def _sync_trace_links(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        entity_maps: dict[str, dict[int, object]],
    ) -> dict:
        stats = self._new_stats()
        source_items = self.db.query(TraceLink).filter(
            TraceLink.sprint_id == source_sprint.id,
            TraceLink.status == "active",
        ).all()

        for source in source_items:
            mapped_source_type, mapped_source_id, source_mapped = self._map_trace_endpoint(
                source.source_type,
                source.source_id,
                entity_maps,
            )
            mapped_target_type, mapped_target_id, target_mapped = self._map_trace_endpoint(
                source.target_type,
                source.target_id,
                entity_maps,
            )
            if mapped_source_type is None or mapped_target_type is None:
                stats["skipped"] += 1
                continue
            if not source_mapped and not target_mapped:
                stats["skipped"] += 1
                continue

            metadata = deepcopy(source.link_metadata) if isinstance(source.link_metadata, dict) else {}
            metadata.update({
                "baseline_source_trace_id": source.id,
                "baseline_source_sprint_id": source_sprint.id,
            })

            existing = self.db.query(TraceLink).filter(
                TraceLink.project_id == source_sprint.project_id,
                TraceLink.sprint_id == target_sprint.id,
                TraceLink.source_type == mapped_source_type,
                TraceLink.source_id == mapped_source_id,
                TraceLink.target_type == mapped_target_type,
                TraceLink.target_id == mapped_target_id,
                TraceLink.relation_type == source.relation_type,
            ).first()

            crud_trace_link.upsert_trace_link(
                self.db,
                TraceLinkCreate(
                    project_id=source_sprint.project_id,
                    sprint_id=target_sprint.id,
                    source_type=mapped_source_type,
                    source_id=mapped_source_id,
                    target_type=mapped_target_type,
                    target_id=mapped_target_id,
                    relation_type=source.relation_type,
                    confidence=source.confidence or 100,
                    evidence=source.evidence or "",
                    metadata=metadata,
                    status="active",
                    created_by="baseline_sync",
                ),
                commit=False,
            )
            self._count(stats, existing is None)

        return stats

    def _find_target_feature(self, source: FeaturePoint, target_sprint_id: int) -> FeaturePoint | None:
        if source.fingerprint:
            target = self.db.query(FeaturePoint).filter(
                FeaturePoint.sprint_id == target_sprint_id,
                FeaturePoint.fingerprint == source.fingerprint,
                FeaturePoint.is_deleted == False,  # noqa: E712
            ).first()
            if target:
                return target

        candidates = self.db.query(FeaturePoint).filter(
            FeaturePoint.sprint_id == target_sprint_id,
            FeaturePoint.module_id == source.module_id,
            FeaturePoint.is_deleted == False,  # noqa: E712
        ).all()
        normalized_name = self._normalize_text(source.name)
        return next((item for item in candidates if self._normalize_text(item.name) == normalized_name), None)

    def _find_target_api(self, source: ApiEndpoint, target_sprint_id: int, project_id: int) -> ApiEndpoint | None:
        candidates = self.db.query(ApiEndpoint).filter(
            ApiEndpoint.project_id == (source.project_id or project_id),
            ApiEndpoint.sprint_id == target_sprint_id,
            ApiEndpoint.method == (source.method or "").upper(),
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).all()
        normalized_path = self._normalize_path(source.path)
        return next((item for item in candidates if self._normalize_path(item.path) == normalized_path), None)

    def _find_target_testcase(self, source: TestCase, target_sprint_id: int, project_id: int) -> TestCase | None:
        resolved_project_id = source.project_id or project_id
        if source.case_no:
            target = self.db.query(TestCase).filter(
                TestCase.project_id == resolved_project_id,
                TestCase.sprint_id == target_sprint_id,
                TestCase.case_no == source.case_no,
                TestCase.is_deleted == False,  # noqa: E712
            ).first()
            if target:
                return target

        if source.fingerprint:
            target = self.db.query(TestCase).filter(
                TestCase.project_id == resolved_project_id,
                TestCase.sprint_id == target_sprint_id,
                TestCase.fingerprint == source.fingerprint,
                TestCase.is_deleted == False,  # noqa: E712
            ).first()
            if target:
                return target

        candidates = self.db.query(TestCase).filter(
            TestCase.project_id == resolved_project_id,
            TestCase.sprint_id == target_sprint_id,
            TestCase.module_id == source.module_id,
            TestCase.is_deleted == False,  # noqa: E712
        ).all()
        normalized_title = self._normalize_text(source.title)
        return next((item for item in candidates if self._normalize_text(item.title) == normalized_title), None)

    def _map_trace_endpoint(
        self,
        entity_type: str,
        entity_id: int,
        entity_maps: dict[str, dict[int, object]],
    ) -> tuple[str | None, int | None, bool]:
        if entity_type not in self.MAPPED_ENTITY_TYPES:
            return entity_type, entity_id, False
        target = entity_maps.get(entity_type, {}).get(entity_id)
        if not target:
            return None, None, False
        return entity_type, target.id, True

    def _merge_baseline_metadata(
        self,
        raw_data: dict | None,
        source_sprint_id: int,
        source_key: str,
        source_id: int,
    ) -> dict:
        data = deepcopy(raw_data) if isinstance(raw_data, dict) else {}
        data.update({
            "baseline_source_sprint_id": source_sprint_id,
            source_key: source_id,
            "baseline_sync": True,
        })
        return data

    def _normalize_text(self, value: str | None) -> str:
        return "".join((value or "").lower().split())

    def _normalize_path(self, value: str | None) -> str:
        path = (value or "").strip().lower()
        if path != "/":
            path = path.rstrip("/")
        return path

    def _new_stats(self) -> dict:
        return {"created": 0, "updated": 0, "skipped": 0}

    def _count(self, stats: dict, created: bool) -> None:
        if created:
            stats["created"] += 1
        else:
            stats["updated"] += 1

    def _sprint_summary(self, sprint: Sprint) -> dict:
        return {
            "id": sprint.id,
            "name": sprint.name,
            "project_id": sprint.project_id,
            "status": sprint.status,
            "is_all": sprint.is_all,
        }
