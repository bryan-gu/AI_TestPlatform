from datetime import datetime
from typing import Any

from pydantic import BaseModel, computed_field


# ============ GraphNode ============

class GraphNodeOut(BaseModel):
    id: int
    graph_id: int
    name: str
    node_type: str  # document / module / testcase / feature
    properties: dict[str, Any] | None = None

    class Config:
        from_attributes = True


# ============ GraphEdge ============

class GraphEdgeOut(BaseModel):
    id: int
    graph_id: int
    source_node_id: int
    target_node_id: int
    relation_type: str  # dependency / include / call / dataflow
    description: str = ""

    # computed
    source_node_name: str = ""
    target_node_name: str = ""

    class Config:
        from_attributes = True


# ============ Graph ============

class GraphCreate(BaseModel):
    name: str
    project_id: int | None = None
    sprint_id: int | None = None
    status: str = "最新"


class GraphOut(BaseModel):
    id: int
    name: str
    project_id: int | None = None
    sprint_id: int | None = None
    node_count: int = 0
    edge_count: int = 0
    status: str = "最新"
    generated_at: datetime | None = None
    created_at: datetime | None = None

    # computed
    project_name: str = ""
    sprint_name: str = ""

    class Config:
        from_attributes = True


class GraphDetailOut(GraphOut):
    """图谱详情，包含 nodes 和 edges"""
    nodes: list[GraphNodeOut] = []
    edges: list[GraphEdgeOut] = []


# ============ Stats ============

class GraphStatsOut(BaseModel):
    total_graphs: int = 0
    total_nodes: int = 0
    total_edges: int = 0
    coverage: str = "0%"
