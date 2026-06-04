from typing import Any, Optional
from pydantic import BaseModel


class SearchResultItem(BaseModel):
    """单条搜索结果"""
    id: int
    title: str
    type: str  # project / testcase / document / user
    description: str = ""
    route: str = ""  # 前端跳转路由


class SearchResponse(BaseModel):
    """搜索响应 - 按类型分组"""
    total: int = 0
    projects: list[SearchResultItem] = []
    testcases: list[SearchResultItem] = []
    documents: list[SearchResultItem] = []
    users: list[SearchResultItem] = []
