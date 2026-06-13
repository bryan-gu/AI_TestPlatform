from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.graph import Graph, GraphNode, GraphEdge
from app.models.trace_link import TraceLink
from app.models.project import Project
from app.models.sprint import Sprint
from app.crud import crud_trace_link


# ============ Graph CRUD ============

def get_graphs(db: Session, project_id: int | None = None):
    q = db.query(Graph).filter(Graph.is_deleted == False)  # noqa: E712
    if project_id is not None:
        q = q.filter(Graph.project_id == project_id)
    return q.order_by(Graph.created_at.desc()).all()


def get_graph(db: Session, graph_id: int):
    return db.query(Graph).filter(
        Graph.id == graph_id,
        Graph.is_deleted == False,  # noqa: E712
    ).first()


def create_graph(db: Session, name: str, project_id: int | None = None,
                 sprint_id: int | None = None, status: str = "最新"):
    graph = Graph(name=name, project_id=project_id, sprint_id=sprint_id, status=status)
    db.add(graph)
    db.commit()
    db.refresh(graph)
    return graph


def get_graph_by_scope(db: Session, project_id: int | None = None, sprint_id: int | None = None):
    query = db.query(Graph).filter(Graph.is_deleted == False)  # noqa: E712
    if project_id is None:
        query = query.filter(Graph.project_id.is_(None))
    else:
        query = query.filter(Graph.project_id == project_id)
    if sprint_id is None:
        query = query.filter(Graph.sprint_id.is_(None))
    else:
        query = query.filter(Graph.sprint_id == sprint_id)
    return query.order_by(Graph.created_at.desc()).first()


def _build_graph_name(db: Session, project_id: int | None = None, sprint_id: int | None = None) -> str:
    project = db.query(Project).filter(Project.id == project_id).first() if project_id else None
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first() if sprint_id else None
    if project and sprint:
        return f"{project.name}-{sprint.name}-知识图谱"
    if project:
        return f"{project.name}-知识图谱"
    if sprint:
        return f"{sprint.name}-知识图谱"
    return "知识图谱"


def get_or_create_graph_for_scope(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    name: str | None = None,
):
    graph = get_graph_by_scope(db, project_id=project_id, sprint_id=sprint_id)
    if graph:
        return graph
    return create_graph(
        db,
        name=name or _build_graph_name(db, project_id=project_id, sprint_id=sprint_id),
        project_id=project_id,
        sprint_id=sprint_id,
        status="需更新",
    )


def generate_graph_for_scope(
    db: Session,
    project_id: int | None = None,
    sprint_id: int | None = None,
    name: str | None = None,
):
    graph = get_or_create_graph_for_scope(db, project_id=project_id, sprint_id=sprint_id, name=name)
    return regenerate_graph(db, graph)


def delete_graph(db: Session, graph: Graph):
    from datetime import datetime
    graph.is_deleted = True
    graph.deleted_at = datetime.utcnow()
    db.commit()


def _get_entity_properties(db: Session, entity_type: str, entity_id: int) -> dict:
    """返回图谱节点的业务摘要 properties（不含完整 raw_data，避免膨胀）。"""
    base = {"entity_type": entity_type, "entity_id": entity_id}
    if not entity_id:
        return base
    try:
        if entity_type == "asset":
            from app.models.knowledge_asset import KnowledgeAsset
            o = db.query(KnowledgeAsset).filter(KnowledgeAsset.id == entity_id).first()
            if not o:
                return base
            base.update({
                "asset_type": o.asset_type or "",
                "source_kind": o.source_kind or "",
                "sprint_id": o.sprint_id,
                "project_id": o.project_id,
                "module_id": o.module_id,
                "status": o.status or "",
                "parse_status": o.parse_status or "",
                "file_type": o.file_type or "",
                "file_size": o.file_size or 0,
                "document_id": o.document_id,
            })
        elif entity_type == "document":
            from app.models.document import Document
            o = db.query(Document).filter(Document.id == entity_id).first()
            if not o:
                return base
            base.update({
                "file_type": o.file_type or "",
                "sprint_id": o.sprint_id,
                "parse_status": o.parse_status or "",
                "ai_status": o.ai_status or "",
                "version": o.version or "",
            })
        elif entity_type == "feature":
            from app.models.feature_point import FeaturePoint
            o = db.query(FeaturePoint).filter(FeaturePoint.id == entity_id).first()
            if not o:
                return base
            base.update({
                "priority": o.priority or "中",
                "status": o.status or "active",
                "sprint_id": o.sprint_id,
                "module_id": o.module_id,
                "source_doc_id": o.source_doc_id,
                "source_asset_id": o.source_asset_id,
                "source_type": o.source_type or "manual",
                "fingerprint": (o.fingerprint or "")[:12],
            })
        elif entity_type == "testcase":
            from app.models.testcase import TestCase
            o = db.query(TestCase).filter(TestCase.id == entity_id).first()
            if not o:
                return base
            base.update({
                "case_no": o.case_no or "",
                "priority": o.priority or "中",
                "exec_status": o.exec_status or "待执行",
                "project_id": o.project_id,
                "sprint_id": o.sprint_id,
                "module_id": o.module_id,
                "case_type": o.case_type or "ui",
                "automation_status": o.automation_status or "not_generated",
                "source": o.source or "manual",
                "source_asset_id": o.source_asset_id,
            })
        elif entity_type == "api":
            from app.models.api_endpoint import ApiEndpoint
            o = db.query(ApiEndpoint).filter(ApiEndpoint.id == entity_id).first()
            if not o:
                return base
            base.update({
                "method": o.method or "",
                "path": o.path or "",
                "summary": o.summary or "",
                "tag": o.tag or "",
                "status": o.status or "active",
                "priority": o.priority or "中",
                "source_asset_id": o.source_asset_id,
                "module_id": o.module_id,
                "auth_required": o.auth_required,
            })
        elif entity_type == "change":
            from app.models.change_item import ChangeItem
            o = db.query(ChangeItem).filter(ChangeItem.id == entity_id).first()
            if not o:
                return base
            base.update({
                "change_type": o.change_type or "unknown",
                "target_type": o.target_type or "feature",
                "target_id": o.target_id,
                "priority": o.priority or "中",
                "impact_level": o.impact_level or "中",
                "status": o.status or "open",
                "source_asset_id": o.source_asset_id,
            })
        elif entity_type == "module":
            from app.models.module import Module
            o = db.query(Module).filter(Module.id == entity_id).first()
            if not o:
                return base
            base.update({
                "project_id": o.project_id,
                "code": o.code or "",
            })
        elif entity_type == "sprint":
            o = db.query(Sprint).filter(Sprint.id == entity_id).first()
            if not o:
                return base
            base.update({
                "project_id": o.project_id,
                "status": o.status or "",
                "is_all": bool(o.is_all),
            })
    except Exception:
        return base
    return base


def regenerate_graph(db: Session, graph: Graph):
    """从 TraceLink 重建图谱节点和边。"""
    links_query = db.query(TraceLink).filter(TraceLink.status == "active")
    if graph.project_id is not None:
        links_query = links_query.filter(TraceLink.project_id == graph.project_id)
    if graph.sprint_id is not None:
        links_query = links_query.filter(TraceLink.sprint_id == graph.sprint_id)
    links = links_query.all()

    db.query(GraphEdge).filter(GraphEdge.graph_id == graph.id).delete()
    db.query(GraphNode).filter(GraphNode.graph_id == graph.id).delete()
    db.flush()

    node_map: dict[tuple[str, int], GraphNode] = {}

    def get_or_create_node(entity_type: str, entity_id: int) -> GraphNode:
        key = (entity_type, entity_id)
        if key in node_map:
            return node_map[key]
        node = GraphNode(
            graph_id=graph.id,
            name=crud_trace_link.get_entity_name(db, entity_type, entity_id),
            node_type=entity_type,
            properties=_get_entity_properties(db, entity_type, entity_id),
        )
        db.add(node)
        db.flush()
        node_map[key] = node
        return node

    edge_count = 0
    for link in links:
        source_node = get_or_create_node(link.source_type, link.source_id)
        target_node = get_or_create_node(link.target_type, link.target_id)
        edge = GraphEdge(
            graph_id=graph.id,
            source_node_id=source_node.id,
            target_node_id=target_node.id,
            relation_type=link.relation_type,
            description=link.evidence or "",
        )
        db.add(edge)
        edge_count += 1

    graph.node_count = len(node_map)
    graph.edge_count = edge_count
    graph.generated_at = datetime.utcnow()
    graph.status = "最新"
    db.commit()
    db.refresh(graph)
    return graph


def update_graph_counts(db: Session, graph_id: int):
    """更新图谱的 node_count 和 edge_count"""
    node_count = db.query(func.count(GraphNode.id)).filter(GraphNode.graph_id == graph_id).scalar()
    edge_count = db.query(func.count(GraphEdge.id)).filter(GraphEdge.graph_id == graph_id).scalar()
    graph = db.query(Graph).filter(Graph.id == graph_id).first()
    if graph:
        graph.node_count = node_count
        graph.edge_count = edge_count
        db.commit()


# ============ GraphNode CRUD ============

def create_node(db: Session, graph_id: int, name: str, node_type: str,
                properties: dict | None = None):
    node = GraphNode(graph_id=graph_id, name=name, node_type=node_type,
                     properties=properties or {})
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def get_nodes_by_graph(db: Session, graph_id: int):
    return db.query(GraphNode).filter(GraphNode.graph_id == graph_id).all()


def delete_nodes_by_graph(db: Session, graph_id: int):
    db.query(GraphNode).filter(GraphNode.graph_id == graph_id).delete()
    db.commit()


# ============ GraphEdge CRUD ============

def create_edge(db: Session, graph_id: int, source_node_id: int, target_node_id: int,
                relation_type: str, description: str = ""):
    edge = GraphEdge(graph_id=graph_id, source_node_id=source_node_id,
                     target_node_id=target_node_id, relation_type=relation_type,
                     description=description)
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return edge


def get_edges_by_graph(db: Session, graph_id: int):
    return db.query(GraphEdge).filter(GraphEdge.graph_id == graph_id).all()


def delete_edges_by_graph(db: Session, graph_id: int):
    db.query(GraphEdge).filter(GraphEdge.graph_id == graph_id).delete()
    db.commit()


# ============ Stats ============

def get_graph_stats(db: Session):
    total_graphs = db.query(func.count(Graph.id)).filter(Graph.is_deleted == False).scalar() or 0  # noqa: E712
    total_nodes = db.query(func.count(GraphNode.id)).scalar() or 0
    total_edges = db.query(func.count(GraphEdge.id)).scalar() or 0

    # 覆盖率：有至少 1 条关联的节点占总节点数的比例
    nodes_with_edges = (
        db.query(func.count(func.distinct(GraphEdge.source_node_id)))
        .filter(GraphEdge.target_node_id.isnot(None))
        .scalar()
    ) or 0
    nodes_incoming = (
        db.query(func.count(func.distinct(GraphEdge.target_node_id)))
        .filter(GraphEdge.source_node_id.isnot(None))
        .scalar()
    ) or 0
    connected = len(set(
        [r for r in db.query(GraphEdge.source_node_id).distinct().all() if r[0]] +
        [r for r in db.query(GraphEdge.target_node_id).distinct().all() if r[0]]
    ))
    if total_nodes > 0:
        coverage = f"{min(100, int(connected / total_nodes * 100))}%"
    else:
        coverage = "0%"

    return {
        "total_graphs": total_graphs,
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "coverage": coverage,
    }
