from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Graph(Base):
    __tablename__ = "graphs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    node_count = Column(Integer, default=0)
    edge_count = Column(Integer, default=0)
    status = Column(String(20), default="最新")  # 最新 / 需更新
    generated_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", backref="graphs")
    sprint = relationship("Sprint", backref="graphs")
    nodes = relationship("GraphNode", backref="graph", cascade="all, delete-orphan")
    edges = relationship("GraphEdge", backref="graph", cascade="all, delete-orphan")


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    graph_id = Column(Integer, ForeignKey("graphs.id"), nullable=False)
    name = Column(String(200), nullable=False)
    node_type = Column(String(20), nullable=False)  # document / module / testcase / feature
    properties = Column(JSON, default=dict)

    # 反向关联：该节点作为边的起点或终点
    outgoing_edges = relationship(
        "GraphEdge", foreign_keys="GraphEdge.source_node_id",
        backref="source_node", cascade="all, delete-orphan"
    )
    incoming_edges = relationship(
        "GraphEdge", foreign_keys="GraphEdge.target_node_id",
        backref="target_node", cascade="all, delete-orphan"
    )


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    graph_id = Column(Integer, ForeignKey("graphs.id"), nullable=False)
    source_node_id = Column(Integer, ForeignKey("graph_nodes.id"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("graph_nodes.id"), nullable=False)
    relation_type = Column(String(30), nullable=False)  # dependency / include / call / dataflow
    description = Column(Text, default="")
