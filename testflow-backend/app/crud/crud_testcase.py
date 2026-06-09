import re
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.testcase import TestCase
from app.models.module import Module
from app.models.project import Project
from app.models.user import User
from app.schemas.testcase import TestCaseCreate, TestCaseUpdate


def _generate_legacy_case_no(db: Session) -> str:
    """旧格式 TC-XXX，用于无前缀项目"""
    last = db.query(TestCase).order_by(TestCase.id.desc()).first()
    if last and last.case_no.startswith("TC-"):
        num = int(last.case_no.split("-")[1]) + 1
    else:
        num = 1
    return f"TC-{num:03d}"


def _resolve_module_code(db: Session, module_id: int | None, module_str: str, project_id: int) -> str:
    """从 module_id 解析英文代码，无则用 module_str"""
    if module_id:
        mod = db.query(Module).filter(Module.id == module_id).first()
        if mod and mod.code:
            return mod.code.upper()
    return module_str.upper()


def _generate_case_no(db: Session, project_id: int, module_str: str, module_id: int | None = None) -> str:
    """
    生成用例编号：{prefix}_TC_{module_code}_{seq:03d}
    优先从 module_id 解析代码，否则用 module_str
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or not project.case_prefix:
        return _generate_legacy_case_no(db)

    prefix = project.case_prefix.upper()
    module_code = _resolve_module_code(db, module_id, module_str, project_id)
    pattern = f"{prefix}_TC_{module_code}_%"

    # 查该项目+模块下最后一条
    last_case = (
        db.query(TestCase)
        .filter(TestCase.project_id == project_id)
        .filter(TestCase.case_no.like(pattern))
        .order_by(TestCase.id.desc())
        .first()
    )

    if last_case:
        match = re.search(r'(\d{3})$', last_case.case_no)
        seq = int(match.group(1)) + 1 if match else 1
    else:
        seq = 1

    return f"{prefix}_TC_{module_code}_{seq:03d}"


def get_testcases(
    db: Session,
    project: str | None = None,
    keyword: str | None = None,
    sprint_id: int | None = None,
    module_id: int | None = None,
    case_type: str | None = None,
) -> list[TestCase]:
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
    if sprint_id:
        query = query.filter(TestCase.sprint_id == sprint_id)
    if module_id:
        query = query.filter(TestCase.module_id == module_id)
    if case_type:
        query = query.filter(TestCase.case_type == case_type)
    return query.all()


def get_testcase(db: Session, case_id: int) -> TestCase | None:
    return db.query(TestCase).filter(TestCase.id == case_id).first()


def create_testcase(db: Session, data: TestCaseCreate) -> TestCase:
    project_id = data.project_id
    module_id = data.module_id
    module_str = data.module or ""

    # 如果有 module_id，从 Module 记录解析 code
    if module_id:
        mod = db.query(Module).filter(Module.id == module_id).first()
        if mod:
            module_str = mod.code or mod.name

    case_no = _generate_case_no(db, project_id, module_str, module_id)

    case = TestCase(
        case_no=case_no,
        title=data.title,
        priority=data.priority,
        exec_status=data.exec_status,
        executor_id=data.executor_id,
        project_id=project_id,
        sprint_id=data.sprint_id,
        module_id=module_id,
        module=module_str,
        case_type=data.case_type,
        automation_status=data.automation_status,
        automation_path=data.automation_path,
        selector_path=data.selector_path,
        source=data.source,
        version=data.version,
        fingerprint=data.fingerprint,
        raw_data=data.raw_data,
        preconditions=data.preconditions,
        test_data=data.test_data,
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
    if data.sprint_id is not None:
        case.sprint_id = data.sprint_id
    if data.module_id is not None:
        case.module_id = data.module_id
        # 自动同步 module 字符串
        if data.module_id:
            mod = db.query(Module).filter(Module.id == data.module_id).first()
            if mod:
                case.module = mod.code or mod.name
    if data.preconditions is not None:
        case.preconditions = data.preconditions
    if data.test_data is not None:
        case.test_data = data.test_data
    if data.test_steps is not None:
        case.test_steps = data.test_steps
    if data.expected_result is not None:
        case.expected_result = data.expected_result
    if data.actual_result is not None:
        case.actual_result = data.actual_result
    if data.case_type is not None:
        case.case_type = data.case_type
    if data.automation_status is not None:
        case.automation_status = data.automation_status
    if data.automation_path is not None:
        case.automation_path = data.automation_path
    if data.selector_path is not None:
        case.selector_path = data.selector_path
    if data.source is not None:
        case.source = data.source
    if data.version is not None:
        case.version = data.version
    if data.fingerprint is not None:
        case.fingerprint = data.fingerprint
    if data.raw_data is not None:
        case.raw_data = data.raw_data
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


def _extract_module_from_case_no(case_no: str) -> str | None:
    """从用例编号中提取模块代码，如 NJ_TC_Integration_001 → Integration"""
    if not case_no:
        return None
    match = re.match(r'^.+_TC_(.+)_(\d{3})$', case_no.strip())
    if match:
        return match.group(1)
    return None


def import_testcases(db: Session, project_id: int, rows: list[dict]) -> dict:
    """批量导入测试用例
    优先从 case_no 提取英文模块代码，从 module 列获取中文名
    匹配/创建 Module 并设置 module_id
    如果 case_no 在目标项目中已存在则更新，否则新建"""
    from app.crud import crud_module

    success = 0
    updated = 0
    errors = []
    for i, row in enumerate(rows, start=2):  # Excel 行号从 2 开始（1 是表头）
        title = (row.get('title') or '').strip()
        # 提取英文代码和中文名
        english_code = _extract_module_from_case_no(row.get('case_no', ''))
        chinese_name = (row.get('module') or '').strip()
        # 优先用英文代码，降级用中文名
        module_input = english_code or chinese_name
        if not title:
            errors.append({"row": i, "reason": "标题不能为空"})
            continue
        if not module_input:
            errors.append({"row": i, "reason": "模块不能为空"})
            continue

        # 尝试匹配已有 Module
        module_id, module_str = crud_module.resolve_module(db, project_id, module_input)

        # 如果未匹配且有中文名和英文代码，尝试用另一个维度匹配
        if module_id is None and english_code and chinese_name:
            mod = db.query(Module).filter(
                Module.project_id == project_id,
                Module.name == chinese_name
            ).first()
            if mod:
                module_id = mod.id
                module_str = mod.code or module_str

        # 仍未匹配：自动创建 Module（同时设置中文名和英文代码）
        if module_id is None and project_id:
            new_name = chinese_name if chinese_name else module_input
            new_code = english_code.upper() if english_code else module_str
            new_mod = Module(
                name=new_name,
                code=new_code,
                project_id=project_id,
                color="",
            )
            db.add(new_mod)
            db.flush()  # 获取 id
            module_id = new_mod.id
            module_str = new_code

        # 检查 case_no 是否已存在于目标项目
        imported_case_no = (row.get('case_no') or '').strip()
        existing = None
        if imported_case_no:
            existing = db.query(TestCase).filter(
                TestCase.project_id == project_id,
                TestCase.case_no == imported_case_no
            ).first()

        if existing:
            # 更新已有用例
            existing.title = title
            existing.module_id = module_id
            existing.module = module_str
            existing.preconditions = row.get('preconditions', '') or ''
            existing.test_data = row.get('test_data', '') or ''
            existing.test_steps = row.get('test_steps', '') or ''
            existing.expected_result = row.get('expected_result', '') or ''
            if row.get('actual_result'):
                existing.actual_result = row['actual_result']
            if row.get('sprint_id'):
                existing.sprint_id = row['sprint_id']
            updated += 1
        else:
            # 新建用例
            case_no = _generate_case_no(db, project_id, module_str, module_id)
            case = TestCase(
                case_no=case_no,
                project_id=project_id,
                sprint_id=row.get('sprint_id'),
                module_id=module_id,
                module=module_str,
                title=title,
                case_type=row.get('case_type', 'ui'),
                source=row.get('source', 'manual'),
                automation_status=row.get('automation_status', 'not_generated'),
                automation_path=row.get('automation_path', ''),
                selector_path=row.get('selector_path', ''),
                version=row.get('version', 'v1.0'),
                fingerprint=row.get('fingerprint', ''),
                raw_data=row.get('raw_data', {}),
                preconditions=row.get('preconditions', ''),
                test_data=row.get('test_data', ''),
                test_steps=row.get('test_steps', ''),
                expected_result=row.get('expected_result', ''),
                actual_result=row.get('actual_result', ''),
            )
            db.add(case)
            success += 1
    db.commit()
    return {"success_count": success, "updated_count": updated, "fail_count": len(errors), "errors": errors}


def get_module_name(db: Session, module_id: int | None) -> str:
    """获取模块中文名称"""
    if not module_id:
        return ""
    mod = db.query(Module).filter(Module.id == module_id).first()
    return mod.name if mod else ""


def get_executor_name(db: Session, executor_id: int | None) -> str:
    if not executor_id:
        return ""
    user = db.query(User).filter(User.id == executor_id).first()
    return user.name if user else ""


def get_sprint_name(db: Session, sprint_id: int | None) -> str:
    if not sprint_id:
        return ""
    from app.models.sprint import Sprint
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    return sprint.name if sprint else ""


def get_coverage_count(db: Session, testcase_id: int) -> int:
    from app.models.coverage import FeaturePointTestCase
    return db.query(FeaturePointTestCase).filter(
        FeaturePointTestCase.testcase_id == testcase_id
    ).count()


def get_project_name(db: Session, project_id: int | None) -> str:
    if not project_id:
        return ""
    proj = db.query(Project).filter(Project.id == project_id).first()
    return proj.name if proj else ""
