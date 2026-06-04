from sqlalchemy.orm import Session

from app.models.module import Module
from app.models.document import Document
from app.schemas.module import ModuleCreate, ModuleUpdate


def get_modules(db: Session, project_id: int | None = None) -> list[Module]:
    query = db.query(Module)
    if project_id:
        query = query.filter(Module.project_id == project_id)
    return query.order_by(Module.created_at.desc()).all()


def get_module(db: Session, module_id: int) -> Module | None:
    return db.query(Module).filter(Module.id == module_id).first()


def create_module(db: Session, data: ModuleCreate) -> Module:
    module = Module(
        name=data.name,
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
    if data.color is not None:
        module.color = data.color
    db.commit()
    db.refresh(module)
    return module


def delete_module(db: Session, module: Module) -> None:
    db.delete(module)
    db.commit()


def get_module_doc_count(db: Session, module_id: int) -> int:
    """统计包含该 module_id 的文档数量"""
    docs = db.query(Document).all()
    count = 0
    for doc in docs:
        if doc.module_ids and module_id in doc.module_ids:
            count += 1
    return count
