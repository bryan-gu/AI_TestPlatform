from copy import deepcopy
from datetime import datetime

from sqlalchemy.orm import Session

from app.crud import crud_api_endpoint, crud_graph, crud_sprint, crud_trace_link
from app.models.api_endpoint import ApiEndpoint, TestCaseApiEndpoint
from app.models.change_item import ChangeItem
from app.models.coverage import FeaturePointTestCase
from app.models.feature_point import FeaturePoint
from app.models.sprint import Sprint
from app.models.testcase import TestCase
from app.models.trace_link import TraceLink
from app.schemas.api_endpoint import TestCaseApiEndpointCreate
from app.schemas.trace_link import TraceLinkCreate


class SprintBaselineManager:
    """同步 Sprint 结构化实体，用于最新汇总和增量底稿准备。"""

    MAPPED_ENTITY_TYPES = {"feature", "api", "testcase"}
    STRUCTURAL_TRACE_TYPES = {"feature", "api", "testcase", "module"}

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

        return self._sync_between_sprints(
            source_sprint,
            target_sprint,
            direction="to_all",
            update_existing=True,
            copy_source_refs=True,
            trace_link_policy="mapped_related",
            created_by="baseline_sync",
        )

    def prepare_from_all(self, target_sprint_id: int, *, update_existing: bool = False) -> dict:
        target_sprint = crud_sprint.get_sprint(self.db, target_sprint_id)
        if not target_sprint:
            raise ValueError("目标 Sprint 不存在")
        if crud_sprint.is_sprint_all(target_sprint):
            raise ValueError("sprint_all 不能作为增量底稿目标")
        if not target_sprint.project_id:
            raise ValueError("目标 Sprint 必须归属项目")

        source_sprint = crud_sprint.get_sprint_all(self.db, target_sprint.project_id)
        if not source_sprint:
            raise ValueError("当前项目不存在 sprint_all 最新汇总基线")
        if source_sprint.id == target_sprint.id:
            raise ValueError("sprint_all 与目标 Sprint 不能相同")

        result = self._sync_between_sprints(
            source_sprint,
            target_sprint,
            direction="from_all",
            update_existing=update_existing,
            copy_source_refs=False,
            trace_link_policy="structural_only",
            created_by="baseline_prepare",
        )
        result["mode"] = "update_existing" if update_existing else "create_missing"
        return result

    def merge_to_all(
        self,
        source_sprint_id: int,
        *,
        change_item_ids: list[int] | None = None,
        statuses: list[str] | None = None,
        target_types: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict:
        """
        将指定 Sprint 中已确认/已解决的 ChangeItem 指向的目标实体合并到 sprint_all。

        只处理 confirmed/resolved 状态、feature/api 类型的 ChangeItem。
        removed/deprecated 类型不物理删除，只标记目标为 deprecated。
        """
        if statuses is None:
            statuses = ["confirmed", "resolved"]
        if target_types is None:
            target_types = ["feature", "api"]

        # 1. 校验源 Sprint
        source_sprint = crud_sprint.get_sprint(self.db, source_sprint_id)
        if not source_sprint:
            raise ValueError("源 Sprint 不存在")
        if crud_sprint.is_sprint_all(source_sprint):
            raise ValueError("sprint_all 不能作为合并源")
        if not source_sprint.project_id:
            raise ValueError("源 Sprint 必须归属项目")

        # 2. 获取 sprint_all
        target_sprint = crud_sprint.get_sprint_all(self.db, source_sprint.project_id)
        if not target_sprint:
            raise ValueError("当前项目不存在 sprint_all 最新汇总基线")
        if target_sprint.id == source_sprint.id:
            raise ValueError("源 Sprint 与 sprint_all 不能相同")

        # 3. 查询符合条件的 ChangeItem
        query = self.db.query(ChangeItem).filter(
            ChangeItem.sprint_id == source_sprint_id,
            ChangeItem.is_deleted == False,  # noqa: E712
            ChangeItem.status.in_(statuses),
            ChangeItem.target_type.in_(target_types),
        )
        if change_item_ids:
            query = query.filter(ChangeItem.id.in_(change_item_ids))
        change_items = query.all()

        if not change_items:
            return {
                "selected": 0,
                "applied": 0,
                "skipped": 0,
                "failed": 0,
                "features": {"created": 0, "updated": 0, "deprecated": 0, "skipped": 0},
                "api_endpoints": {"created": 0, "updated": 0, "deprecated": 0, "skipped": 0},
                "trace_links": {"created": 0, "updated": 0, "skipped": 0},
                "applied_change_item_ids": [],
                "skipped_items": [],
                "dry_run": dry_run,
            }

        # 4. 按目标类型分组处理
        feature_stats = {"created": 0, "updated": 0, "deprecated": 0, "skipped": 0}
        api_stats = {"created": 0, "updated": 0, "deprecated": 0, "skipped": 0}
        trace_stats = {"created": 0, "updated": 0, "skipped": 0}
        applied_ids = []
        skipped_items = []
        failed = 0

        # 构建 source→target 实体映射（用于后续 TraceLink 复制）
        feature_map: dict[int, FeaturePoint] = {}
        api_map: dict[int, ApiEndpoint] = {}

        for ci in change_items:
            try:
                if ci.target_type == "feature":
                    result_type, entity_id = self._merge_feature_change(
                        source_sprint, target_sprint, ci, feature_stats, dry_run
                    )
                    if entity_id:
                        feature_map[ci.target_id] = self.db.query(FeaturePoint).get(entity_id)
                elif ci.target_type == "api":
                    result_type, entity_id = self._merge_api_change(
                        source_sprint, target_sprint, ci, api_stats, dry_run
                    )
                    if entity_id:
                        api_map[ci.target_id] = self.db.query(ApiEndpoint).get(entity_id)
                else:
                    result_type = "skipped"
                    skipped_items.append({"change_item_id": ci.id, "reason": f"不支持的 target_type: {ci.target_type}"})

                if result_type in ("created", "updated", "deprecated"):
                    applied_ids.append(ci.id)
                    # 标记 ChangeItem 为 applied（非 dry_run 时）
                    if not dry_run:
                        self._mark_change_item_applied(ci, target_sprint.id, result_type)
                else:
                    skipped_items.append({"change_item_id": ci.id, "reason": result_type})
            except Exception as e:
                failed += 1
                skipped_items.append({"change_item_id": ci.id, "reason": str(e)})

        # 5. 复制相关 TraceLink（非 dry_run 时）
        if not dry_run and (feature_map or api_map):
            entity_maps = {"feature": feature_map, "api": api_map, "testcase": {}}
            trace_stats = self._sync_trace_links(
                source_sprint,
                target_sprint,
                entity_maps,
                direction="to_all",
                trace_link_policy="mapped_related",
                created_by="baseline_merge",
            )

        # 6. 重建 sprint_all 图谱（非 dry_run 时）
        graph_info = {}
        if not dry_run:
            self.db.commit()
            graph = crud_graph.generate_graph_for_scope(
                self.db,
                project_id=source_sprint.project_id,
                sprint_id=target_sprint.id,
            )
            graph_info = {
                "id": graph.id,
                "node_count": graph.node_count or 0,
                "edge_count": graph.edge_count or 0,
                "status": graph.status,
            }

        return {
            "selected": len(change_items),
            "applied": len(applied_ids),
            "skipped": len(skipped_items),
            "failed": failed,
            "features": feature_stats,
            "api_endpoints": api_stats,
            "trace_links": trace_stats,
            "applied_change_item_ids": applied_ids,
            "skipped_items": skipped_items,
            "graph": graph_info,
            "dry_run": dry_run,
        }

    def _merge_feature_change(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        change_item: ChangeItem,
        stats: dict,
        dry_run: bool,
    ) -> tuple[str, int | None]:
        """合并单个 FeaturePoint 类型的 ChangeItem 到 sprint_all。"""
        source_fp = self.db.query(FeaturePoint).filter(
            FeaturePoint.id == change_item.target_id,
            FeaturePoint.is_deleted == False,  # noqa: E712
        ).first()
        if not source_fp:
            stats["skipped"] += 1
            return "skipped", None

        project_id = source_sprint.project_id

        if change_item.change_type in ("removed", "deprecated"):
            # 不物理删除，标记 sprint_all 中对应实体为 deprecated
            target = self._find_target_feature(source_fp, target_sprint.id)
            if target:
                if not dry_run:
                    target.status = "deprecated"
                    target.raw_data = self._merge_baseline_metadata(
                        target.raw_data, source_sprint.id,
                        "merge_deprecated_by_change", change_item.id,
                        direction="to_all",
                    )
                    self.db.flush()
                stats["deprecated"] += 1
                return "deprecated", target.id
            else:
                stats["skipped"] += 1
                return "skipped", None

        # added / modified: 将 SprintN 中的实体同步到 sprint_all
        target = self._find_target_feature(source_fp, target_sprint.id)
        created = target is None
        if created:
            target = FeaturePoint(name=source_fp.name, sprint_id=target_sprint.id)
            self.db.add(target)

        if not dry_run:
            target.name = source_fp.name
            target.description = source_fp.description or ""
            target.entry_path = source_fp.entry_path or ""
            target.interaction_elements = source_fp.interaction_elements or ""
            target.business_rules = source_fp.business_rules or ""
            target.priority = source_fp.priority or "中"
            target.sprint_id = target_sprint.id
            target.module_id = source_fp.module_id
            target.source_type = source_fp.source_type or "manual"
            target.status = source_fp.status or "active"
            target.version = source_fp.version or "v1.0"
            target.fingerprint = source_fp.fingerprint or ""
            target.raw_data = self._merge_baseline_metadata(
                source_fp.raw_data, source_sprint.id,
                "merge_source_feature_id", source_fp.id,
                direction="to_all",
            )
            target.raw_data["merge_change_item_id"] = change_item.id
            target.is_deleted = False
            self.db.flush()

        if created:
            stats["created"] += 1
        else:
            stats["updated"] += 1
        return "created" if created else "updated", target.id

    def _merge_api_change(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        change_item: ChangeItem,
        stats: dict,
        dry_run: bool,
    ) -> tuple[str, int | None]:
        """合并单个 ApiEndpoint 类型的 ChangeItem 到 sprint_all。"""
        source_api = self.db.query(ApiEndpoint).filter(
            ApiEndpoint.id == change_item.target_id,
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).first()
        if not source_api:
            stats["skipped"] += 1
            return "skipped", None

        project_id = source_sprint.project_id or target_sprint.project_id

        if change_item.change_type in ("removed", "deprecated"):
            target = self._find_target_api(source_api, target_sprint.id, project_id)
            if target:
                if not dry_run:
                    target.status = "deprecated"
                    target.raw_data = self._merge_baseline_metadata(
                        target.raw_data, source_sprint.id,
                        "merge_deprecated_by_change", change_item.id,
                        direction="to_all",
                    )
                    self.db.flush()
                stats["deprecated"] += 1
                return "deprecated", target.id
            else:
                stats["skipped"] += 1
                return "skipped", None

        target = self._find_target_api(source_api, target_sprint.id, project_id)
        created = target is None
        if created:
            target = ApiEndpoint(
                project_id=project_id,
                sprint_id=target_sprint.id,
                method=(source_api.method or "").upper(),
                path=source_api.path or "",
            )
            self.db.add(target)

        if not dry_run:
            target.project_id = project_id
            target.sprint_id = target_sprint.id
            target.module_id = source_api.module_id
            target.method = (source_api.method or "").upper()
            target.path = source_api.path or ""
            target.summary = source_api.summary or ""
            target.description = source_api.description or ""
            target.tag = source_api.tag or ""
            target.operation_id = source_api.operation_id or ""
            target.status = source_api.status or "active"
            target.priority = source_api.priority or "中"
            target.auth_required = source_api.auth_required
            target.request_schema = deepcopy(source_api.request_schema) if source_api.request_schema is not None else {}
            target.response_schema = deepcopy(source_api.response_schema) if source_api.response_schema is not None else {}
            target.parameters = deepcopy(source_api.parameters) if source_api.parameters is not None else []
            target.error_codes = deepcopy(source_api.error_codes) if source_api.error_codes is not None else []
            target.version = source_api.version or "v1"
            target.fingerprint = source_api.fingerprint or ""
            target.raw_data = self._merge_baseline_metadata(
                source_api.raw_data, source_sprint.id,
                "merge_source_api_id", source_api.id,
                direction="to_all",
            )
            target.raw_data["merge_change_item_id"] = change_item.id
            target.is_deleted = False
            self.db.flush()

        if created:
            stats["created"] += 1
        else:
            stats["updated"] += 1
        return "created" if created else "updated", target.id

    def _mark_change_item_applied(
        self,
        change_item: ChangeItem,
        target_sprint_all_id: int,
        merge_result: str,
    ) -> None:
        """标记 ChangeItem 为 applied，并在 raw_data 中记录合并信息。"""
        change_item.status = "applied"
        raw = deepcopy(change_item.raw_data) if isinstance(change_item.raw_data, dict) else {}
        raw["applied_to_all"] = True
        raw["applied_at"] = datetime.utcnow().isoformat()
        raw["target_sprint_all_id"] = target_sprint_all_id
        raw["merge_result"] = merge_result
        change_item.raw_data = raw
        self.db.flush()

    def _sync_between_sprints(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        *,
        direction: str,
        update_existing: bool,
        copy_source_refs: bool,
        trace_link_policy: str,
        created_by: str,
    ) -> dict:
        feature_map, feature_stats = self._sync_feature_points(
            source_sprint,
            target_sprint,
            direction=direction,
            update_existing=update_existing,
            copy_source_refs=copy_source_refs,
        )
        api_map, api_stats = self._sync_api_endpoints(
            source_sprint,
            target_sprint,
            direction=direction,
            update_existing=update_existing,
            copy_source_refs=copy_source_refs,
        )
        testcase_map, testcase_stats = self._sync_testcases(
            source_sprint,
            target_sprint,
            direction=direction,
            update_existing=update_existing,
        )
        coverage_stats = self._sync_coverages(feature_map, testcase_map)
        testcase_api_stats = self._sync_testcase_api_links(
            testcase_map,
            api_map,
            source_sprint=source_sprint,
            target_sprint=target_sprint,
            direction=direction,
            created_by=created_by,
        )
        trace_stats = self._sync_trace_links(
            source_sprint,
            target_sprint,
            {
                "feature": feature_map,
                "api": api_map,
                "testcase": testcase_map,
            },
            direction=direction,
            trace_link_policy=trace_link_policy,
            created_by=created_by,
        )

        self.db.commit()
        graph = crud_graph.generate_graph_for_scope(
            self.db,
            project_id=target_sprint.project_id or source_sprint.project_id,
            sprint_id=target_sprint.id,
        )

        return {
            "source_sprint": self._sprint_summary(source_sprint),
            "target_sprint": self._sprint_summary(target_sprint),
            "features": feature_stats,
            "api_endpoints": api_stats,
            "testcases": testcase_stats,
            "coverages": coverage_stats,
            "testcase_api_endpoints": testcase_api_stats,
            "trace_links": trace_stats,
            "graph": {
                "id": graph.id,
                "node_count": graph.node_count or 0,
                "edge_count": graph.edge_count or 0,
                "status": graph.status,
            },
        }

    def _sync_feature_points(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        *,
        direction: str,
        update_existing: bool,
        copy_source_refs: bool,
    ) -> tuple[dict[int, FeaturePoint], dict]:
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
            elif not update_existing:
                feature_map[source.id] = target
                stats["skipped"] += 1
                continue

            target.name = source.name
            target.description = source.description or ""
            target.entry_path = source.entry_path or ""
            target.interaction_elements = source.interaction_elements or ""
            target.business_rules = source.business_rules or ""
            target.priority = source.priority or "中"
            target.source_doc_id = source.source_doc_id if copy_source_refs else None
            target.sprint_id = target_sprint.id
            target.module_id = source.module_id
            target.linked_cases = source.linked_cases or ""
            target.source_type = source.source_type or "manual" if copy_source_refs else "baseline_draft"
            target.status = source.status or "active"
            target.version = source.version or "v1.0"
            target.fingerprint = source.fingerprint or ""
            target.raw_data = self._merge_baseline_metadata(
                source.raw_data,
                source_sprint.id,
                "baseline_source_feature_id",
                source.id,
                direction=direction,
            )
            target.is_deleted = False
            self.db.flush()

            feature_map[source.id] = target
            self._count(stats, created)

        return feature_map, stats

    def _sync_api_endpoints(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        *,
        direction: str,
        update_existing: bool,
        copy_source_refs: bool,
    ) -> tuple[dict[int, ApiEndpoint], dict]:
        stats = self._new_stats()
        api_map: dict[int, ApiEndpoint] = {}
        source_items = self.db.query(ApiEndpoint).filter(
            ApiEndpoint.sprint_id == source_sprint.id,
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).all()

        for source in source_items:
            project_id = source.project_id or source_sprint.project_id or target_sprint.project_id
            target = self._find_target_api(source, target_sprint.id, project_id)
            created = target is None
            if created:
                target = ApiEndpoint(
                    project_id=project_id,
                    sprint_id=target_sprint.id,
                    method=(source.method or "").upper(),
                    path=source.path or "",
                )
                self.db.add(target)
            elif not update_existing:
                api_map[source.id] = target
                stats["skipped"] += 1
                continue

            target.project_id = project_id
            target.sprint_id = target_sprint.id
            target.source_asset_id = source.source_asset_id if copy_source_refs else None
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
                direction=direction,
            )
            target.is_deleted = False
            self.db.flush()

            api_map[source.id] = target
            self._count(stats, created)

        return api_map, stats

    def _sync_testcases(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        *,
        direction: str,
        update_existing: bool,
    ) -> tuple[dict[int, TestCase], dict]:
        stats = self._new_stats()
        testcase_map: dict[int, TestCase] = {}
        source_items = self.db.query(TestCase).filter(
            TestCase.sprint_id == source_sprint.id,
            TestCase.is_deleted == False,  # noqa: E712
        ).all()

        for source in source_items:
            project_id = source.project_id or source_sprint.project_id or target_sprint.project_id
            target = self._find_target_testcase(source, target_sprint.id, project_id)
            created = target is None
            if created:
                target = TestCase(
                    case_no=source.case_no or f"BASELINE-{source.id}",
                    title=source.title,
                    project_id=project_id,
                    sprint_id=target_sprint.id,
                )
                self.db.add(target)
            elif not update_existing:
                testcase_map[source.id] = target
                stats["skipped"] += 1
                continue

            is_prepare = direction == "from_all"
            target.case_no = source.case_no or f"BASELINE-{source.id}"
            target.title = source.title
            target.priority = source.priority or "中"
            target.exec_status = "待执行" if is_prepare else (source.exec_status or "待执行")
            target.executor_id = None if is_prepare else source.executor_id
            target.project_id = project_id
            target.sprint_id = target_sprint.id
            target.module = source.module
            target.module_id = source.module_id
            target.case_type = source.case_type or "ui"
            target.automation_status = source.automation_status or "not_generated"
            target.automation_path = source.automation_path or ""
            target.selector_path = source.selector_path or ""
            target.source = "baseline_draft" if is_prepare else (source.source or "manual")
            target.version = source.version or "v1.0"
            target.fingerprint = source.fingerprint or ""
            target.raw_data = self._merge_baseline_metadata(
                source.raw_data,
                source_sprint.id,
                "baseline_source_testcase_id",
                source.id,
                direction=direction,
            )
            target.preconditions = source.preconditions or ""
            target.test_data = source.test_data or ""
            target.test_steps = source.test_steps or ""
            target.expected_result = source.expected_result or ""
            target.actual_result = "" if is_prepare else (source.actual_result or "")
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

    def _sync_testcase_api_links(
        self,
        testcase_map: dict[int, TestCase],
        api_map: dict[int, ApiEndpoint],
        *,
        source_sprint: Sprint,
        target_sprint: Sprint,
        direction: str,
        created_by: str,
    ) -> dict:
        stats = self._new_stats()
        if not testcase_map or not api_map:
            return stats

        source_items = self.db.query(TestCaseApiEndpoint).filter(
            TestCaseApiEndpoint.testcase_id.in_(list(testcase_map.keys())),
            TestCaseApiEndpoint.api_endpoint_id.in_(list(api_map.keys())),
        ).all()

        for source in source_items:
            target_case = testcase_map.get(source.testcase_id)
            target_api = api_map.get(source.api_endpoint_id)
            if not target_case or not target_api:
                stats["skipped"] += 1
                continue

            existing = self.db.query(TestCaseApiEndpoint).filter(
                TestCaseApiEndpoint.testcase_id == target_case.id,
                TestCaseApiEndpoint.api_endpoint_id == target_api.id,
            ).first()
            crud_api_endpoint.link_testcase_endpoint(
                self.db,
                TestCaseApiEndpointCreate(
                    testcase_id=target_case.id,
                    api_endpoint_id=target_api.id,
                    coverage_type=source.coverage_type or "functional",
                    confidence=source.confidence or 100,
                    evidence=source.evidence or "",
                ),
                commit=False,
            )
            self._count(stats, existing is None)

            self._upsert_testcase_api_trace_link(
                target_case,
                target_api,
                source_sprint=source_sprint,
                target_sprint=target_sprint,
                direction=direction,
                source_link_id=source.id,
                confidence=source.confidence or 100,
                evidence=source.evidence or "TestCaseApiEndpoint 同步",
                created_by=created_by,
            )

        return stats

    def _sync_trace_links(
        self,
        source_sprint: Sprint,
        target_sprint: Sprint,
        entity_maps: dict[str, dict[int, object]],
        *,
        direction: str,
        trace_link_policy: str,
        created_by: str,
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
                trace_link_policy=trace_link_policy,
            )
            mapped_target_type, mapped_target_id, target_mapped = self._map_trace_endpoint(
                source.target_type,
                source.target_id,
                entity_maps,
                trace_link_policy=trace_link_policy,
            )
            if mapped_source_type is None or mapped_target_type is None:
                stats["skipped"] += 1
                continue
            if not source_mapped and not target_mapped:
                stats["skipped"] += 1
                continue
            if trace_link_policy == "structural_only" and not self._is_structural_trace(mapped_source_type, mapped_target_type):
                stats["skipped"] += 1
                continue

            metadata = deepcopy(source.link_metadata) if isinstance(source.link_metadata, dict) else {}
            metadata.update(self._baseline_metadata(
                source_sprint.id,
                "baseline_source_trace_id",
                source.id,
                direction=direction,
            ))
            metadata["trace_link_policy"] = trace_link_policy

            existing = self.db.query(TraceLink).filter(
                TraceLink.project_id == (target_sprint.project_id or source_sprint.project_id),
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
                    project_id=target_sprint.project_id or source_sprint.project_id,
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
                    created_by=created_by,
                ),
                commit=False,
            )
            self._count(stats, existing is None)

        return stats

    def _upsert_testcase_api_trace_link(
        self,
        target_case: TestCase,
        target_api: ApiEndpoint,
        *,
        source_sprint: Sprint,
        target_sprint: Sprint,
        direction: str,
        source_link_id: int,
        confidence: int,
        evidence: str,
        created_by: str,
    ) -> None:
        metadata = self._baseline_metadata(
            source_sprint.id,
            "baseline_source_testcase_api_link_id",
            source_link_id,
            direction=direction,
        )
        metadata["trace_link_policy"] = "testcase_api_endpoint"
        crud_trace_link.upsert_trace_link(
            self.db,
            TraceLinkCreate(
                project_id=target_sprint.project_id or source_sprint.project_id,
                sprint_id=target_sprint.id,
                source_type="testcase",
                source_id=target_case.id,
                target_type="api",
                target_id=target_api.id,
                relation_type="tests_api",
                confidence=confidence,
                evidence=evidence,
                metadata=metadata,
                status="active",
                created_by=created_by,
            ),
            commit=False,
        )

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
            ApiEndpoint.project_id == project_id,
            ApiEndpoint.sprint_id == target_sprint_id,
            ApiEndpoint.method == (source.method or "").upper(),
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).all()
        normalized_path = self._normalize_path(source.path)
        return next((item for item in candidates if self._normalize_path(item.path) == normalized_path), None)

    def _find_target_testcase(self, source: TestCase, target_sprint_id: int, project_id: int) -> TestCase | None:
        if source.case_no:
            target = self.db.query(TestCase).filter(
                TestCase.project_id == project_id,
                TestCase.sprint_id == target_sprint_id,
                TestCase.case_no == source.case_no,
                TestCase.is_deleted == False,  # noqa: E712
            ).first()
            if target:
                return target

        if source.fingerprint:
            target = self.db.query(TestCase).filter(
                TestCase.project_id == project_id,
                TestCase.sprint_id == target_sprint_id,
                TestCase.fingerprint == source.fingerprint,
                TestCase.is_deleted == False,  # noqa: E712
            ).first()
            if target:
                return target

        candidates = self.db.query(TestCase).filter(
            TestCase.project_id == project_id,
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
        *,
        trace_link_policy: str,
    ) -> tuple[str | None, int | None, bool]:
        if trace_link_policy == "structural_only" and entity_type not in self.STRUCTURAL_TRACE_TYPES:
            return None, None, False
        if entity_type not in self.MAPPED_ENTITY_TYPES:
            return entity_type, entity_id, False
        target = entity_maps.get(entity_type, {}).get(entity_id)
        if not target:
            return None, None, False
        return entity_type, target.id, True

    def _is_structural_trace(self, source_type: str, target_type: str) -> bool:
        return source_type in self.STRUCTURAL_TRACE_TYPES and target_type in self.STRUCTURAL_TRACE_TYPES

    def _merge_baseline_metadata(
        self,
        raw_data: dict | None,
        source_sprint_id: int,
        source_key: str,
        source_id: int,
        *,
        direction: str,
    ) -> dict:
        data = deepcopy(raw_data) if isinstance(raw_data, dict) else {}
        data.update(self._baseline_metadata(source_sprint_id, source_key, source_id, direction=direction))
        return data

    def _baseline_metadata(
        self,
        source_sprint_id: int,
        source_key: str,
        source_id: int,
        *,
        direction: str,
    ) -> dict:
        data = {
            "baseline_source_sprint_id": source_sprint_id,
            source_key: source_id,
            "baseline_sync": True,
        }
        if direction == "from_all":
            data.update({
                "baseline_direction": "from_all_to_sprint",
                "prepared_from_all": True,
                "baseline_origin": "sprint_all",
            })
        else:
            data["baseline_direction"] = "to_all"
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
