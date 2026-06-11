import hashlib
import json
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.crud import crud_change_item, crud_graph, crud_trace_link
from app.models.api_endpoint import ApiEndpoint
from app.models.change_item import ChangeItem
from app.models.document import Document
from app.models.feature_point import FeaturePoint
from app.models.knowledge_asset import KnowledgeAsset
from app.models.module import Module
from app.models.sprint import Sprint
from app.models.testcase import TestCase
from app.schemas.change_item import ChangeAnalyzeRequest, ChangeAnalyzeResult, ChangeItemCreate
from app.schemas.trace_link import TraceLinkCreate


@dataclass
class AnalyzeCounters:
    total: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    added: int = 0
    modified: int = 0
    removed: int = 0
    high_impact: int = 0
    impacted_testcases: int = 0


class ChangeAnalyzer:
    """Sprint 增量变更规则分析器。"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_sprint(self, sprint_id: int, request: ChangeAnalyzeRequest | None = None) -> ChangeAnalyzeResult:
        request = request or ChangeAnalyzeRequest()
        sprint = self.db.query(Sprint).filter(
            Sprint.id == sprint_id,
            Sprint.is_deleted == False,  # noqa: E712
        ).first()
        if not sprint:
            raise ValueError("Sprint 不存在")

        baseline, baseline_type = self._resolve_baseline(sprint, request.baseline_sprint_id)
        counters = AnalyzeCounters()
        seen_testcases: set[int] = set()

        if request.overwrite:
            existing_items = self.db.query(ChangeItem).filter(
                ChangeItem.sprint_id == sprint.id,
                ChangeItem.is_deleted == False,  # noqa: E712
            ).all()
            for item in existing_items:
                item.is_deleted = True

        include_types = set(request.include_target_types or ["feature", "api"])
        if "feature" in include_types:
            self._analyze_features(sprint, baseline, counters, seen_testcases, detect_removed=request.detect_removed)
        if "api" in include_types:
            self._analyze_apis(sprint, baseline, counters, seen_testcases, detect_removed=request.detect_removed)

        self.db.commit()

        graph = None
        if sprint.project_id:
            graph = crud_graph.generate_graph_for_scope(self.db, project_id=sprint.project_id, sprint_id=sprint.id)

        message = "增量分析完成"
        if not baseline:
            message = "未找到基线 Sprint，已按当前 Sprint 新增内容生成变更项"

        return ChangeAnalyzeResult(
            project_id=sprint.project_id,
            sprint_id=sprint.id,
            baseline_sprint_id=baseline.id if baseline else None,
            baseline_type=baseline_type,
            total=counters.total,
            created=counters.created,
            updated=counters.updated,
            skipped=counters.skipped,
            added=counters.added,
            modified=counters.modified,
            removed=counters.removed,
            high_impact=counters.high_impact,
            impacted_testcases=len(seen_testcases),
            graph_id=graph.id if graph else None,
            node_count=graph.node_count if graph else 0,
            edge_count=graph.edge_count if graph else 0,
            message=message,
        )

    def get_change_impact(self, change_id: int, max_depth: int = 2) -> dict:
        item = crud_change_item.get_change_item(self.db, change_id)
        if not item:
            raise ValueError("变更项不存在")

        impact = crud_trace_link.get_entity_impact(self.db, "change", change_id)
        buckets = {
            "testcases": impact.get("testcases", []),
            "assets": impact.get("assets", []),
            "features": impact.get("features", []),
            "modules": impact.get("modules", []),
            "api_endpoints": impact.get("api_endpoints", []),
            "scripts": impact.get("scripts", []),
            "changes": impact.get("changes", []),
        }
        seen = {(entry["type"], entry["id"]) for values in buckets.values() for entry in values}
        frontier = [("change", change_id, 0)]
        visited = {("change", change_id)}
        bucket_map = {
            "testcase": "testcases",
            "asset": "assets",
            "feature": "features",
            "module": "modules",
            "api": "api_endpoints",
            "script": "scripts",
            "change": "changes",
        }

        while frontier:
            entity_type, entity_id, depth = frontier.pop(0)
            if depth >= max_depth:
                continue
            links = crud_trace_link.get_entity_links(self.db, entity_type, entity_id)
            for link in links:
                neighbors = [
                    (link.source_type, link.source_id),
                    (link.target_type, link.target_id),
                ]
                for next_type, next_id in neighbors:
                    if (next_type, next_id) == (entity_type, entity_id):
                        continue
                    if (next_type, next_id) in visited:
                        continue
                    visited.add((next_type, next_id))
                    frontier.append((next_type, next_id, depth + 1))
                    bucket = bucket_map.get(next_type)
                    key = (next_type, next_id)
                    if not bucket or key in seen:
                        continue
                    seen.add(key)
                    if len(buckets[bucket]) >= 100:
                        continue
                    buckets[bucket].append({
                        "type": next_type,
                        "id": next_id,
                        "name": crud_trace_link.get_entity_name(self.db, next_type, next_id),
                        "relation_type": link.relation_type,
                        "relation_label": crud_trace_link.get_relation_label(link.relation_type),
                        "confidence": link.confidence or 0,
                        "evidence": link.evidence or "",
                        "depth": depth + 1,
                    })

        impact.update(buckets)
        impact["max_depth"] = max_depth
        return impact

    def _resolve_baseline(self, sprint: Sprint, baseline_sprint_id: int | None) -> tuple[Sprint | None, str]:
        if baseline_sprint_id and baseline_sprint_id != sprint.id:
            baseline = self.db.query(Sprint).filter(
                Sprint.id == baseline_sprint_id,
                Sprint.project_id == sprint.project_id,
                Sprint.is_deleted == False,  # noqa: E712
            ).first()
            if baseline:
                return baseline, "specified"

        baseline = self.db.query(Sprint).filter(
            Sprint.project_id == sprint.project_id,
            Sprint.id != sprint.id,
            Sprint.is_all == True,  # noqa: E712
            Sprint.is_deleted == False,  # noqa: E712
        ).order_by(Sprint.updated_at.desc()).first()
        if baseline:
            return baseline, "sprint_all"

        baseline = self.db.query(Sprint).filter(
            Sprint.project_id == sprint.project_id,
            Sprint.id != sprint.id,
            Sprint.status.in_(["基线", "已完成", "最新汇总"]),
            Sprint.is_deleted == False,  # noqa: E712
        ).order_by(Sprint.updated_at.desc()).first()
        if baseline:
            return baseline, "status"

        return None, "none"

    def _analyze_features(
        self,
        sprint: Sprint,
        baseline: Sprint | None,
        counters: AnalyzeCounters,
        seen_testcases: set[int],
        *,
        detect_removed: bool = False,
    ):
        current = self.db.query(FeaturePoint).filter(
            FeaturePoint.sprint_id == sprint.id,
            FeaturePoint.is_deleted == False,  # noqa: E712
        ).all()
        baseline_items = []
        if baseline:
            baseline_items = self.db.query(FeaturePoint).filter(
                FeaturePoint.sprint_id == baseline.id,
                FeaturePoint.is_deleted == False,  # noqa: E712
            ).all()
        baseline_map = {self._feature_key(fp): fp for fp in baseline_items}
        current_map = {self._feature_key(fp): fp for fp in current}

        for fp in current:
            key = self._feature_key(fp)
            base_fp = baseline_map.get(key)
            if not base_fp:
                self._create_feature_change(sprint, fp, None, "added", counters, seen_testcases)
            elif self._feature_hash(fp) != self._feature_hash(base_fp):
                self._create_feature_change(sprint, fp, base_fp, "modified", counters, seen_testcases)
            else:
                counters.skipped += 1

        if detect_removed:
            for key, base_fp in baseline_map.items():
                if key not in current_map:
                    self._create_feature_change(sprint, None, base_fp, "removed", counters, seen_testcases)

    def _analyze_apis(
        self,
        sprint: Sprint,
        baseline: Sprint | None,
        counters: AnalyzeCounters,
        seen_testcases: set[int],
        *,
        detect_removed: bool = False,
    ):
        current = self.db.query(ApiEndpoint).filter(
            ApiEndpoint.sprint_id == sprint.id,
            ApiEndpoint.is_deleted == False,  # noqa: E712
        ).all()
        baseline_items = []
        if baseline:
            baseline_items = self.db.query(ApiEndpoint).filter(
                ApiEndpoint.sprint_id == baseline.id,
                ApiEndpoint.is_deleted == False,  # noqa: E712
            ).all()
        baseline_map = {self._api_key(api): api for api in baseline_items}
        current_map = {self._api_key(api): api for api in current}

        for api in current:
            key = self._api_key(api)
            base_api = baseline_map.get(key)
            if not base_api:
                self._create_api_change(sprint, api, None, "added", counters, seen_testcases)
            elif self._api_hash(api) != self._api_hash(base_api):
                self._create_api_change(sprint, api, base_api, "modified", counters, seen_testcases)
            else:
                counters.skipped += 1

        if detect_removed:
            for key, base_api in baseline_map.items():
                if key not in current_map:
                    self._create_api_change(sprint, None, base_api, "removed", counters, seen_testcases)

    def _create_feature_change(
        self,
        sprint: Sprint,
        current: FeaturePoint | None,
        baseline: FeaturePoint | None,
        change_type: str,
        counters: AnalyzeCounters,
        seen_testcases: set[int],
    ):
        target = current or baseline
        if not target:
            return
        module_name = self._module_name(target.module_id)
        title_prefix = {"added": "新增功能点", "modified": "修改功能点", "removed": "删除功能点"}.get(change_type, "功能点变更")
        title = f"{title_prefix}：{target.name}"
        priority = target.priority or "中"
        impact_level = self._impact_level(priority, target_type="feature", change_type=change_type)
        source_doc_id, source_asset_id = self._resolve_source(sprint, current, baseline)
        data = ChangeItemCreate(
            project_id=sprint.project_id,
            sprint_id=sprint.id,
            source_doc_id=source_doc_id,
            source_asset_id=source_asset_id,
            module_id=target.module_id,
            title=title,
            description=self._change_description(change_type, "功能点", target.name, module_name),
            change_type=change_type,
            target_type="feature",
            target_id=current.id if current else baseline.id,
            priority=priority,
            impact_level=impact_level,
            status="open",
            before_snapshot=self._feature_snapshot(baseline) if baseline else {},
            after_snapshot=self._feature_snapshot(current) if current else {},
            evidence=self._feature_evidence(change_type, current, baseline, module_name),
            confidence=90 if change_type in ("added", "modified") else 70,
            fingerprint=self._change_fingerprint(sprint.project_id, sprint.id, change_type, "feature", target.module_id, target.name),
            raw_data={"analyzer": "rule", "entity": "feature"},
        )
        item, created = crud_change_item.upsert_change_item(self.db, data, commit=False)
        self._count_change(change_type, impact_level, created, counters)
        self._link_change_sources(sprint, item, source_doc_id, source_asset_id)
        if target.module_id:
            self._upsert_link(sprint, "change", item.id, "module", target.module_id, "changes", f"变更项涉及模块：{module_name}", 90)
        if current:
            self._upsert_link(sprint, "change", item.id, "feature", current.id, "changes", data.evidence, data.confidence)
        elif baseline:
            self._upsert_link(sprint, "change", item.id, "feature", baseline.id, "changes", data.evidence, data.confidence)
        self._link_impacted_testcases(sprint, item, "feature", target.id, target.module_id, seen_testcases)

    def _create_api_change(
        self,
        sprint: Sprint,
        current: ApiEndpoint | None,
        baseline: ApiEndpoint | None,
        change_type: str,
        counters: AnalyzeCounters,
        seen_testcases: set[int],
    ):
        target = current or baseline
        if not target:
            return
        api_name = f"{target.method} {target.path}"
        title_prefix = {"added": "新增接口", "modified": "修改接口", "removed": "删除接口"}.get(change_type, "接口变更")
        title = f"{title_prefix}：{api_name}"
        priority = target.priority or "中"
        impact_level = self._impact_level(priority, target_type="api", change_type=change_type)
        source_asset_id = current.source_asset_id if current else baseline.source_asset_id
        source_doc_id = self._doc_id_by_asset(source_asset_id)
        data = ChangeItemCreate(
            project_id=sprint.project_id,
            sprint_id=sprint.id,
            source_doc_id=source_doc_id,
            source_asset_id=source_asset_id,
            module_id=target.module_id,
            title=title,
            description=self._change_description(change_type, "接口", api_name, target.tag or ""),
            change_type=change_type,
            target_type="api",
            target_id=current.id if current else baseline.id,
            priority=priority,
            impact_level=impact_level,
            status="open",
            before_snapshot=self._api_snapshot(baseline) if baseline else {},
            after_snapshot=self._api_snapshot(current) if current else {},
            evidence=self._api_evidence(change_type, current, baseline),
            confidence=90 if change_type in ("added", "modified") else 70,
            fingerprint=self._change_fingerprint(sprint.project_id, sprint.id, change_type, "api", target.method, target.path),
            raw_data={"analyzer": "rule", "entity": "api"},
        )
        item, created = crud_change_item.upsert_change_item(self.db, data, commit=False)
        self._count_change(change_type, impact_level, created, counters)
        self._link_change_sources(sprint, item, source_doc_id, source_asset_id)
        if target.module_id:
            self._upsert_link(sprint, "change", item.id, "module", target.module_id, "changes", "接口变更涉及模块", 90)
        if current:
            self._upsert_link(sprint, "change", item.id, "api", current.id, "changes", data.evidence, data.confidence)
        elif baseline:
            self._upsert_link(sprint, "change", item.id, "api", baseline.id, "changes", data.evidence, data.confidence)
        self._link_impacted_testcases(sprint, item, "api", target.id, target.module_id, seen_testcases)

    def _link_change_sources(self, sprint: Sprint, item: ChangeItem, source_doc_id: int | None, source_asset_id: int | None):
        if source_doc_id:
            self._upsert_link(sprint, "document", source_doc_id, "change", item.id, "changes", "来源文档识别变更项", 90)
        if source_asset_id:
            self._upsert_link(sprint, "asset", source_asset_id, "change", item.id, "changes", "来源资产识别变更项", 90)

    def _link_impacted_testcases(
        self,
        sprint: Sprint,
        item: ChangeItem,
        target_type: str,
        target_id: int,
        module_id: int | None,
        seen_testcases: set[int],
    ):
        testcase_ids: set[int] = set()
        if target_type == "feature":
            links = crud_trace_link.get_trace_links(
                self.db,
                project_id=sprint.project_id,
                source_type="feature",
                source_id=target_id,
                target_type="testcase",
                relation_type="covers",
            )
            testcase_ids.update(link.target_id for link in links)
        if target_type == "api":
            links = crud_trace_link.get_trace_links(
                self.db,
                project_id=sprint.project_id,
                target_type="api",
                target_id=target_id,
                source_type="testcase",
                relation_type="tests_api",
            )
            testcase_ids.update(link.source_id for link in links)
        if module_id:
            cases = self.db.query(TestCase).filter(
                TestCase.project_id == sprint.project_id,
                TestCase.module_id == module_id,
                TestCase.is_deleted == False,  # noqa: E712
            ).limit(50).all()
            testcase_ids.update(case.id for case in cases)

        for testcase_id in testcase_ids:
            self._upsert_link(sprint, "change", item.id, "testcase", testcase_id, "changes", "同模块或覆盖关系推断受影响用例", 70)
            seen_testcases.add(testcase_id)

    def _upsert_link(
        self,
        sprint: Sprint,
        source_type: str,
        source_id: int,
        target_type: str,
        target_id: int,
        relation_type: str,
        evidence: str,
        confidence: int,
    ):
        crud_trace_link.upsert_trace_link(self.db, TraceLinkCreate(
            project_id=sprint.project_id,
            sprint_id=sprint.id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence,
            evidence=evidence,
            metadata={"analyzer": "change_analyzer"},
            created_by="change-analyzer",
        ), commit=False)

    def _count_change(self, change_type: str, impact_level: str, created: bool, counters: AnalyzeCounters):
        counters.total += 1
        if created:
            counters.created += 1
        else:
            counters.updated += 1
        if change_type == "added":
            counters.added += 1
        elif change_type == "modified":
            counters.modified += 1
        elif change_type == "removed":
            counters.removed += 1
        if impact_level == "高":
            counters.high_impact += 1

    def _resolve_source(self, sprint: Sprint, current, baseline) -> tuple[int | None, int | None]:
        source_doc_id = getattr(current, "source_doc_id", None) if current else getattr(baseline, "source_doc_id", None)
        if not source_doc_id:
            doc = self.db.query(Document).filter(
                Document.sprint_id == sprint.id,
                Document.is_deleted == False,  # noqa: E712
            ).order_by(Document.created_at.asc()).first()
            source_doc_id = doc.id if doc else None
        source_asset_id = None
        if source_doc_id:
            asset = self.db.query(KnowledgeAsset).filter(KnowledgeAsset.document_id == source_doc_id).first()
            source_asset_id = asset.id if asset else None
        return source_doc_id, source_asset_id

    def _doc_id_by_asset(self, asset_id: int | None) -> int | None:
        if not asset_id:
            return None
        asset = self.db.query(KnowledgeAsset).filter(KnowledgeAsset.id == asset_id).first()
        return asset.document_id if asset else None

    def _feature_key(self, fp: FeaturePoint) -> str:
        return self._normalize(f"{fp.module_id or ''}|{fp.name or ''}")

    def _feature_hash(self, fp: FeaturePoint) -> str:
        payload = {
            "name": fp.name or "",
            "description": fp.description or "",
            "entry_path": fp.entry_path or "",
            "interaction_elements": fp.interaction_elements or "",
            "business_rules": fp.business_rules or "",
        }
        return self._hash(payload)

    def _api_key(self, api: ApiEndpoint) -> str:
        return self._normalize(f"{api.method or ''}|{api.path or ''}")

    def _api_hash(self, api: ApiEndpoint) -> str:
        payload = {
            "summary": api.summary or "",
            "description": api.description or "",
            "parameters": api.parameters or [],
            "request_schema": api.request_schema or {},
            "response_schema": api.response_schema or {},
            "error_codes": api.error_codes or [],
        }
        return self._hash(payload)

    def _feature_snapshot(self, fp: FeaturePoint | None) -> dict:
        if not fp:
            return {}
        return {
            "id": fp.id,
            "name": fp.name or "",
            "module_id": fp.module_id,
            "module_name": self._module_name(fp.module_id),
            "description": fp.description or "",
            "entry_path": fp.entry_path or "",
            "interaction_elements": fp.interaction_elements or "",
            "business_rules": fp.business_rules or "",
            "priority": fp.priority or "中",
            "fingerprint": fp.fingerprint or "",
        }

    def _api_snapshot(self, api: ApiEndpoint | None) -> dict:
        if not api:
            return {}
        return {
            "id": api.id,
            "method": api.method,
            "path": api.path,
            "summary": api.summary or "",
            "description": api.description or "",
            "tag": api.tag or "",
            "module_id": api.module_id,
            "module_name": self._module_name(api.module_id),
            "priority": api.priority or "中",
            "request_schema": api.request_schema or {},
            "response_schema": api.response_schema or {},
            "parameters": api.parameters or [],
            "error_codes": api.error_codes or [],
            "fingerprint": api.fingerprint or "",
        }

    def _feature_evidence(self, change_type: str, current: FeaturePoint | None, baseline: FeaturePoint | None, module_name: str) -> str:
        if change_type == "added":
            return f"当前 Sprint 中存在基线未匹配的功能点，模块：{module_name}"
        if change_type == "modified":
            return "功能点名称和模块匹配，但描述、入口、交互元素或业务规则发生变化"
        if change_type == "removed":
            return "基线存在该功能点，当前 Sprint 未匹配到同名功能点"
        return "规则分析识别功能点变更"

    def _api_evidence(self, change_type: str, current: ApiEndpoint | None, baseline: ApiEndpoint | None) -> str:
        if change_type == "added":
            return "当前 Sprint 中存在基线未匹配的接口 method + path"
        if change_type == "modified":
            return "接口 method + path 匹配，但摘要、参数、请求或响应结构发生变化"
        if change_type == "removed":
            return "基线存在该接口，当前 Sprint 未匹配到相同 method + path"
        return "规则分析识别接口变更"

    def _change_description(self, change_type: str, entity_label: str, name: str, scope: str) -> str:
        action = {"added": "新增", "modified": "修改", "removed": "删除"}.get(change_type, "变更")
        suffix = f"，范围：{scope}" if scope else ""
        return f"规则分析识别到{entity_label}{action}：{name}{suffix}"

    def _impact_level(self, priority: str, *, target_type: str, change_type: str) -> str:
        if priority == "高" or target_type == "api":
            return "高"
        if change_type == "modified":
            return "中"
        return priority if priority in ("高", "中", "低") else "中"

    def _module_name(self, module_id: int | None) -> str:
        if not module_id:
            return ""
        module = self.db.query(Module).filter(Module.id == module_id).first()
        return module.name if module else ""

    def _change_fingerprint(self, *parts) -> str:
        return self._hash([self._normalize(str(part or "")) for part in parts])

    def _hash(self, payload) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _normalize(self, value: str) -> str:
        return re.sub(r"\s+", "", (value or "").lower().strip())
