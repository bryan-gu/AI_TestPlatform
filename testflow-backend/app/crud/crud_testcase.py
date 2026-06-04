from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.testcase import TestCase
from app.models.project import Project
from app.models.user import User
from app.schemas.testcase import TestCaseCreate, TestCaseUpdate


def _generate_case_no(db: Session) -> str:
    """自动生成用例编号 TC-XXX"""
    last = db.query(TestCase).order_by(TestCase.id.desc()).first()
    if last and last.case_no.startswith("TC-"):
        num = int(last.case_no.split("-")[1]) + 1
    else:
        num = 1
    return f"TC-{num:03d}"


def get_testcases(db: Session, project: str | None = None, keyword: str | None = None) -> list[TestCase]:
    query = db.query(TestCase)
    if project:
        proj = db.query(Project).filter(Project.name == project).first()
        if proj:
            query = query.filter(TestCase.project_id == proj.id)
    if keyword:
        query = query.filter(
            or_(
                TestCase.case_no.ilike(f"%{keyword}%"),
                TestCase.title.ilike(f"%{keyword}%")
            )
        )
    return query.all()


def get_testcase(db: Session, case_id: int) -> TestCase | None:
    return db.query(TestCase).filter(TestCase.id == case_id).first()


def create_testcase(db: Session, data: TestCaseCreate) -> TestCase:
    case = TestCase(
        case_no=_generate_case_no(db),
        title=data.title,
        priority=data.priority,
        exec_status=data.exec_status,
        executor_id=data.executor_id,
        project_id=data.project_id,
        preconditions=data.preconditions,
        test_steps=data.test_steps,
        expected_result=data.expected_result,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def update_testcase(db: Session, case: TestCase, data: TestCaseUpdate) -> TestCase:
    if data.title is not None:
        case.title = data.title
    if data.priority is not None:
        case.priority = data.priority
    if data.exec_status is not None:
        case.exec_status = data.exec_status
    if data.executor_id is not None:
        case.executor_id = data.executor_id
    if data.preconditions is not None:
        case.preconditions = data.preconditions
    if data.test_steps is not None:
        case.test_steps = data.test_steps
    if data.expected_result is not None:
        case.expected_result = data.expected_result
    db.commit()
    db.refresh(case)
    return case


def batch_execute(db: Session, project_id: int | None = None) -> int:
    """将所有'待执行'的用例批量标记为'通过'，返回受影响行数"""
    query = db.query(TestCase).filter(TestCase.exec_status == "待执行")
    if project_id:
        query = query.filter(TestCase.project_id == project_id)
    count = query.count()
    query.update({"exec_status": "通过"})
    db.commit()
    return count


def delete_testcase(db: Session, case: TestCase) -> None:
    db.delete(case)
    db.commit()


def get_testcase_stats(db: Session) -> dict:
    total = db.query(TestCase).count()
    passed = db.query(TestCase).filter(TestCase.exec_status == "通过").count()
    failed = db.query(TestCase).filter(TestCase.exec_status == "失败").count()
    pending = db.query(TestCase).filter(TestCase.exec_status == "待执行").count()
    project_count = db.query(func.count(func.distinct(TestCase.project_id))).scalar() or 0
    pass_rate = round(passed / total * 100) if total > 0 else 0
    return {
        "total": total,
        "projectCount": project_count,
        "passed": passed,
        "passRate": pass_rate,
        "failed": failed,
        "pending": pending,
    }


def get_executor_name(db: Session, executor_id: int | None) -> str:
    if not executor_id:
        return ""
    user = db.query(User).filter(User.id == executor_id).first()
    return user.name if user else ""


def get_project_name(db: Session, project_id: int | None) -> str:
    if not project_id:
        return ""
    proj = db.query(Project).filter(Project.id == project_id).first()
    return proj.name if proj else ""
