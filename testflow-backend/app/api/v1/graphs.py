from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ResponseModel
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
