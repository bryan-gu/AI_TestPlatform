from datetime import datetime
from pydantic import BaseModel, Field


class FeaturePointCreate(BaseModel):
    name: str
    description: str = ""
    entry_path: str = ""
    interaction_elements: str = ""
    business_rules: str = ""
    priority: str = "中"
    source_doc_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None
    linked_cases: str = ""
    source_type: str = "manual"
    status: str = "active"
    version: str = "v1.0"
    fingerprint: str = ""
    raw_data: dict = Field(default_factory=dict)


class FeaturePointUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    entry_path: str | None = None
    interaction_elements: str | None = None
    business_rules: str | None = None
    priority: str | None = None
    source_doc_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None
    linked_cases: str | None = None
    source_type: str | None = None
    status: str | None = None
    version: str | None = None
    fingerprint: str | None = None
    raw_data: dict | None = None


class FeaturePointOut(BaseModel):
    id: int
    name: str
    description: str = ""
    entry_path: str = ""
    interaction_elements: str = ""
    business_rules: str = ""
    priority: str = "中"
    source_doc_id: int | None = None
    sprint_id: int | None = None
    module_id: int | None = None
    linked_cases: str = ""
    graph_node_id: int | None = None
    source_type: str = "manual"
    status: str = "active"
    version: str = "v1.0"
    fingerprint: str = ""
    raw_data: dict = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # computed fields
    source_doc_name: str = ""
    sprint_name: str = ""
    module_name: str = ""
    coverage_count: int = 0

    class Config:
        from_attributes = True
