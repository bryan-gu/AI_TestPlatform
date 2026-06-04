from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.testcase import TestCaseCreate, TestCaseUpdate, TestCaseOut
from app.crud import crud_testcase

router = APIRouter(prefix="/testcases", tags=["测试用例"])


def _to_out(case, db: Session) -> dict:
    return TestCaseOut(
        id=case.id, case_no=case.case_no, title=case.title,
        priority=case.priority, exec_status=case.exec_status,
        executor=crud_testcase.get_executor_name(db, case.executor_id),
        project=crud_testcase.get_project_name(db, case.project_id),
        project_id=case.project_id,
        preconditions=case.preconditions or "",
        test_steps=case.test_steps or "",
        expected_result=case.expected_result or "",
        updated_at=case.updated_at,
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_testcases(
    project: str | None = None,
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    cases = crud_testcase.get_testcases(db, project=project, keyword=keyword)
    return ResponseModel(data=[_to_out(c, db) for c in cases])


@router.get("/stats", response_model=ResponseModel)
def testcase_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ResponseModel(data=crud_testcase.get_testcase_stats(db))


@router.post("/batch-execute", response_model=ResponseModel)
def batch_execute(
    project_id: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    count = crud_testcase.batch_execute(db, project_id)
    return ResponseModel(data={"executed_count": count}, message=f"已批量执行 {count} 条用例")


@router.post("", response_model=ResponseModel)
def create_testcase(data: TestCaseCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    case = crud_testcase.create_testcase(db, data)
    return ResponseModel(data=_to_out(case, db))


@router.put("/{case_id}", response_model=ResponseModel)
def update_testcase(case_id: int, data: TestCaseUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    case = crud_testcase.get_testcase(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="用例不存在")
    case = crud_testcase.update_testcase(db, case, data)
    return ResponseModel(data=_to_out(case, db))


@router.delete("/{case_id}", response_model=ResponseModel)
def delete_testcase(case_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    case = crud_testcase.get_testcase(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="用例不存在")
    crud_testcase.delete_testcase(db, case)
    return ResponseModel(message="删除成功")
