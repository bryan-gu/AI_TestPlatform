from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ResponseModel
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleOut
from app.crud import crud_module


router = APIRouter(prefix="/modules", tags=["Module 标签管理"])


def _module_to_out(module, db: Session) -> dict:
    return ModuleOut(
        id=module.id,
        name=module.name,
        code=module.code or "",
        project_id=module.project_id,
        color=module.color or "",
        created_at=module.created_at,
        doc_count=crud_module.get_module_doc_count(db, module.id),
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_modules(
    project_id: int | None = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    modules = crud_module.get_modules(db, project_id=project_id)
    return ResponseModel(data=[_module_to_out(m, db) for m in modules])


@router.get("/{module_id}", response_model=ResponseModel)
def get_module(module_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    module = crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    return ResponseModel(data=_module_to_out(module, db))


@router.post("", response_model=ResponseModel)
def create_module(data: ModuleCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    module = crud_module.create_module(db, data)
    return ResponseModel(data=_module_to_out(module, db))


@router.put("/{module_id}", response_model=ResponseModel)
def update_module(module_id: int, data: ModuleUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    module = crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    module = crud_module.update_module(db, module, data)
    return ResponseModel(data=_module_to_out(module, db))


@router.delete("/{module_id}", response_model=ResponseModel)
def delete_module(module_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    module = crud_module.get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    crud_module.delete_module(db, module)
    return ResponseModel(message="删除成功")
