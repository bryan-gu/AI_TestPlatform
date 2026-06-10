from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.models.project import Project
from app.models.testcase import TestCase
from app.models.document import Document
from app.models.user import User
from app.schemas.search import SearchResultItem, SearchResponse

router = APIRouter(prefix="/search", tags=["全局搜索"])

# 项目状态英文 → 中文映射
_PROJECT_STATUS_MAP = {
    "pending": "待启动",
    "active": "进行中",
    "testing": "测试中",
    "completed": "已完成",
}


@router.get("")
def global_search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    types: str = Query("project,testcase,document,user", description="搜索类型，逗号分隔"),
    db: Session = Depends(get_db),
):
    keyword = f"%{q}%"
    type_list = [t.strip() for t in types.split(",") if t.strip()]

    response = SearchResponse()
    total = 0

    # 搜索项目
    if "project" in type_list:
        results = db.query(Project).filter(
            Project.name.ilike(keyword),
            Project.is_deleted == False,  # noqa: E712
        ).limit(10).all()
        for p in results:
            response.projects.append(SearchResultItem(
                id=p.id,
                title=p.name,
                type="project",
                description=_PROJECT_STATUS_MAP.get(p.status, p.status or ""),
                route=f"/projects",
            ))
        total += len(results)

    # 搜索测试用例
    if "testcase" in type_list:
        results = db.query(TestCase).filter(
            or_(TestCase.title.ilike(keyword), TestCase.case_no.ilike(keyword)),
            TestCase.is_deleted == False,  # noqa: E712
        ).limit(10).all()
        for tc in results:
            response.testcases.append(SearchResultItem(
                id=tc.id,
                title=f"{tc.case_no} {tc.title}",
                type="testcase",
                description=tc.exec_status or "",
                route="/testcases",
            ))
        total += len(results)

    # 搜索文档
    if "document" in type_list:
        results = db.query(Document).filter(
            Document.name.ilike(keyword),
            Document.is_deleted == False,  # noqa: E712
        ).limit(10).all()
        for doc in results:
            response.documents.append(SearchResultItem(
                id=doc.id,
                title=doc.name,
                type="document",
                description=doc.file_type or "",
                route=f"/knowledge/{doc.sprint_id}" if doc.sprint_id else "/knowledge",
            ))
        total += len(results)

    # 搜索用户
    if "user" in type_list:
        results = db.query(User).filter(
            or_(User.name.ilike(keyword), User.email.ilike(keyword))
        ).limit(10).all()
        for u in results:
            response.users.append(SearchResultItem(
                id=u.id,
                title=u.name,
                type="user",
                description=u.email,
                route="/users",
            ))
        total += len(results)

    response.total = total
    return ResponseModel(data=response.model_dump())
