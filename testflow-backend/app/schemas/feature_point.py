from datetime import datetime
from pydantic import BaseModel


class FeaturePointCreate(BaseModel):
    name: str
    source_doc_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None
    linked_cases: str = ""


class FeaturePointUpdate(BaseModel):
    name: str | None = None
    source_doc_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None
    linked_cases: str | None = None


class FeaturePointOut(BaseModel):
    id: int
    name: str
    source_doc_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None
    linked_cases: str = ""
    graph_node_id: int | None = None
    created_at: datetime | None = None
    # computed fields
    source_doc_name: str = ""
    sprint_name: str = ""
    module_name: str = ""

    class Config:
        from_attributes = True
