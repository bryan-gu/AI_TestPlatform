from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.graph import Graph, GraphNode, GraphEdge


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


def delete_graph(db: Session, graph: Graph):
    from datetime import datetime
    graph.is_deleted = True
    graph.deleted_at = datetime.utcnow()
    db.commit()


def regenerate_graph(db: Session, graph: Graph):
    """触发重新生成（当前为模拟，更新时间和状态）"""
    graph.generated_at = func.now()
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
