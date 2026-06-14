from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.models.graph import Graph, GraphNode, GraphEdge
from app.schemas.graph import (
    GraphCreate, GraphOut, GraphDetailOut,
    GraphNodeOut, GraphEdgeOut, GraphStatsOut,
)
from app.crud import crud_graph

router = APIRouter(prefix="/graphs", tags=["知识图谱"])


# ── helpers ──

def _graph_to_out(g: Graph) -> dict:
    project_name = g.project.name if g.project else ""
    sprint_name = g.sprint.name if g.sprint else ""
    out = GraphOut(
        id=g.id,
        name=g.name,
        project_id=g.project_id,
        sprint_id=g.sprint_id,
        node_count=g.node_count,
        edge_count=g.edge_count,
        status=g.status,
        generated_at=g.generated_at,
        created_at=g.created_at,
        project_name=project_name,
        sprint_name=sprint_name,
    )
    return out.model_dump()


def _detail_to_out(g: Graph) -> dict:
    base = _graph_to_out(g)
    nodes = [
        GraphNodeOut(
            id=n.id, graph_id=n.graph_id, name=n.name,
            node_type=n.node_type, properties=n.properties,
        ).model_dump()
        for n in g.nodes
    ]
    # 建立 node id → name 映射
    node_map = {n.id: n.name for n in g.nodes}
    edges = [
        GraphEdgeOut(
            id=e.id, graph_id=e.graph_id,
            source_node_id=e.source_node_id, target_node_id=e.target_node_id,
            relation_type=e.relation_type, description=e.description,
            source_node_name=node_map.get(e.source_node_id, ""),
            target_node_name=node_map.get(e.target_node_id, ""),
        ).model_dump()
        for e in g.edges
    ]
    return {**base, "nodes": nodes, "edges": edges}


# ── endpoints ──

@router.get("/stats")
def get_graph_stats(db: Session = Depends(get_db)):
    stats = crud_graph.get_graph_stats(db)
    return ResponseModel(data=stats)


@router.get("/")
def get_graphs(project_id: int | None = None, db: Session = Depends(get_db)):
    graphs = crud_graph.get_graphs(db, project_id=project_id)
    return ResponseModel(data=[_graph_to_out(g) for g in graphs])


@router.post("/generate")
def generate_graph(
    project_id: int,
    sprint_id: int | None = None,
    db: Session = Depends(get_db),
):
    graph = crud_graph.generate_graph_for_scope(db, project_id=project_id, sprint_id=sprint_id)
    return ResponseModel(data=_graph_to_out(graph), message="图谱生成完成")


@router.get("/{graph_id}")
def get_graph(graph_id: int, db: Session = Depends(get_db)):
    graph = crud_graph.get_graph(db, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="图谱不存在")
    return ResponseModel(data=_detail_to_out(graph))


@router.post("/")
def create_graph(body: GraphCreate, db: Session = Depends(get_db)):
    graph = crud_graph.create_graph(
        db, name=body.name, project_id=body.project_id,
        sprint_id=body.sprint_id, status=body.status,
    )
    return ResponseModel(data=_graph_to_out(graph), message="图谱创建成功")


@router.delete("/{graph_id}")
def delete_graph(graph_id: int, db: Session = Depends(get_db)):
    graph = crud_graph.get_graph(db, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="图谱不存在")
    crud_graph.delete_graph(db, graph)
    return ResponseModel(message="图谱删除成功")


@router.post("/{graph_id}/regenerate")
def regenerate_graph(graph_id: int, db: Session = Depends(get_db)):
    graph = crud_graph.get_graph(db, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="图谱不存在")
    graph = crud_graph.regenerate_graph(db, graph)
    return ResponseModel(data=_graph_to_out(graph), message="图谱重新生成完成")


# ── 图谱查询（增强项批次 5）：子图 / 邻居 / 搜索 ──

def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _node_to_out(n: GraphNode) -> dict:
    return GraphNodeOut(
        id=n.id, graph_id=n.graph_id, name=n.name,
        node_type=n.node_type, properties=n.properties,
    ).model_dump()


def _edge_to_out(e: GraphEdge, node_map: dict[int, str]) -> dict:
    return GraphEdgeOut(
        id=e.id, graph_id=e.graph_id,
        source_node_id=e.source_node_id, target_node_id=e.target_node_id,
        relation_type=e.relation_type, description=e.description,
        source_node_name=node_map.get(e.source_node_id, ""),
        target_node_name=node_map.get(e.target_node_id, ""),
    ).model_dump()


@router.get("/{graph_id}/subgraph")
def get_subgraph(
    graph_id: int,
    node_types: str | None = Query(None, description="逗号分隔的节点类型"),
    relation_types: str | None = Query(None, description="逗号分隔的关系类型"),
    limit: int = Query(300, description="节点上限"),
    db: Session = Depends(get_db),
):
    """按节点/关系类型过滤的子图（大图不全量加载）。"""
    graph = crud_graph.get_graph(db, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="图谱不存在")

    nodes_q = db.query(GraphNode).filter(GraphNode.graph_id == graph_id)
    nt = _split_csv(node_types)
    if nt:
        nodes_q = nodes_q.filter(GraphNode.node_type.in_(nt))
    total_nodes = nodes_q.count()
    nodes = nodes_q.limit(limit).all()
    truncated = total_nodes > len(nodes)

    node_ids = {n.id for n in nodes}
    node_map = {n.id: n.name for n in nodes}
    edges_q = db.query(GraphEdge).filter(
        GraphEdge.graph_id == graph_id,
        GraphEdge.source_node_id.in_(node_ids),
        GraphEdge.target_node_id.in_(node_ids),
    )
    rt = _split_csv(relation_types)
    if rt:
        edges_q = edges_q.filter(GraphEdge.relation_type.in_(rt))
    edges = edges_q.all()

    return ResponseModel(data={
        "graph": _graph_to_out(graph),
        "nodes": [_node_to_out(n) for n in nodes],
        "edges": [_edge_to_out(e, node_map) for e in edges],
        "truncated": truncated,
        "limit": limit,
    })


@router.get("/{graph_id}/node/{node_id}/neighbors")
def get_neighbors(
    graph_id: int,
    node_id: int,
    direction: str = Query("both", description="out/in/both"),
    depth: int = Query(1, description="最大 2"),
    db: Session = Depends(get_db),
):
    """节点的邻居（BFS，direction + depth）。"""
    graph = crud_graph.get_graph(db, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="图谱不存在")
    depth = max(1, min(depth, 2))

    visited: set[int] = {node_id}
    frontier: list[int] = [node_id]
    edge_ids: set[int] = set()
    edges: list[GraphEdge] = []

    for _ in range(depth):
        if not frontier:
            break
        out_edges, in_edges = [], []
        if direction in ("out", "both"):
            out_edges = db.query(GraphEdge).filter(
                GraphEdge.graph_id == graph_id,
                GraphEdge.source_node_id.in_(frontier),
            ).all()
        if direction in ("in", "both"):
            in_edges = db.query(GraphEdge).filter(
                GraphEdge.graph_id == graph_id,
                GraphEdge.target_node_id.in_(frontier),
            ).all()
        next_frontier: list[int] = []
        for e in (out_edges + in_edges):
            if e.id in edge_ids:
                continue
            edge_ids.add(e.id)
            edges.append(e)
            peer = e.target_node_id if e.source_node_id in frontier else e.source_node_id
            if peer not in visited:
                visited.add(peer)
                next_frontier.append(peer)
        frontier = next_frontier

    nodes = db.query(GraphNode).filter(
        GraphNode.graph_id == graph_id,
        GraphNode.id.in_(visited),
    ).all()
    node_map = {n.id: n.name for n in nodes}
    return ResponseModel(data={
        "center_node_id": node_id,
        "nodes": [_node_to_out(n) for n in nodes],
        "edges": [_edge_to_out(e, node_map) for e in edges],
    })


@router.get("/{graph_id}/search")
def search_nodes(
    graph_id: int,
    keyword: str = Query(..., description="节点名称关键词"),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    """按名称搜索节点。"""
    graph = crud_graph.get_graph(db, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="图谱不存在")
    nodes = db.query(GraphNode).filter(
        GraphNode.graph_id == graph_id,
        GraphNode.name.ilike(f"%{keyword}%"),
    ).limit(limit).all()
    return ResponseModel(data=[_node_to_out(n) for n in nodes])
