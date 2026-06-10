from sqlalchemy.orm import Session

from app.models.module import Module
from app.models.document import Document
from app.schemas.module import ModuleCreate, ModuleUpdate


def get_modules(db: Session, project_id: int | None = None) -> list[Module]:
    query = db.query(Module).filter(Module.is_deleted == False)  # noqa: E712
    if project_id:
        query = query.filter(Module.project_id == project_id)
    return query.order_by(Module.created_at.desc()).all()


def get_module(db: Session, module_id: int) -> Module | None:
    return db.query(Module).filter(
        Module.id == module_id,
        Module.is_deleted == False,  # noqa: E712
    ).first()


def create_module(db: Session, data: ModuleCreate) -> Module:
    module = Module(
        name=data.name,
        code=(data.code or "").strip().upper(),
        project_id=data.project_id,
        color=data.color,
    )
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


def update_module(db: Session, module: Module, data: ModuleUpdate) -> Module:
    if data.name is not None:
        module.name = data.name
    if data.code is not None:
        module.code = data.code.strip().upper()
    if data.color is not None:
        module.color = data.color
    db.commit()
    db.refresh(module)
    return module


def delete_module(db: Session, module: Module) -> None:
    from datetime import datetime
    module.is_deleted = True
    module.deleted_at = datetime.utcnow()
    db.commit()


def get_module_doc_count(db: Session, module_id: int) -> int:
    """统计包含该 module_id 的文档数量"""
    docs = db.query(Document).all()
    count = 0
    for doc in docs:
        if doc.module_ids and module_id in doc.module_ids:
            count += 1
    return count


def get_module_by_code(db: Session, project_id: int, code: str) -> Module | None:
    """按项目 + 英文代码查找模块"""
    return db.query(Module).filter(
        Module.project_id == project_id,
        Module.code == code.upper(),
        Module.is_deleted == False,  # noqa: E712
    ).first()


def resolve_module(db: Session, project_id: int | None, module_input: str) -> tuple[int | None, str]:
    """
    将用户输入的模块信息解析为 (module_id, module_code)。
    匹配策略：先按 code 精确匹配 → 再按 name 精确匹配 → 未匹配返回原输入。
    """
    if not module_input or not project_id:
        return None, (module_input or "").strip().upper()

    # 先按 code 匹配
    mod = get_module_by_code(db, project_id, module_input)
    if mod:
        return mod.id, mod.code or mod.name

    # 再按 name 匹配
    mod = db.query(Module).filter(
        Module.project_id == project_id,
        Module.name == module_input.strip(),
        Module.is_deleted == False,  # noqa: E712
    ).first()
    if mod:
        return mod.id, mod.code or mod.name

    # 未匹配，返回原始输入作为 code
    return None, module_input.strip().upper()
