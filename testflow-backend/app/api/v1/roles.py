from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut
from app.crud import crud_role

router = APIRouter(prefix="/roles", tags=["角色管理"])


def _to_out(role, db: Session) -> dict:
    return RoleOut(
        id=role.id,
        name=role.name,
        type=role.type,
        permissions=role.permissions or [],
        is_editable=role.is_editable,
        member_count=crud_role.get_member_count(db, role.id),
        created_at=role.created_at,
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_roles(
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    roles = crud_role.get_roles(db, keyword=keyword)
    return ResponseModel(data=[_to_out(r, db) for r in roles])


@router.get("/stats", response_model=ResponseModel)
def role_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ResponseModel(data=crud_role.get_role_stats(db))


@router.post("", response_model=ResponseModel)
def create_role(data: RoleCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    role = crud_role.create_role(db, data)
    return ResponseModel(data=_to_out(role, db))


@router.put("/{role_id}", response_model=ResponseModel)
def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    role = crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if not role.is_editable:
        raise HTTPException(status_code=400, detail="内置角色不可编辑")
    role = crud_role.update_role(db, role, data)
    return ResponseModel(data=_to_out(role, db))


@router.delete("/{role_id}", response_model=ResponseModel)
def delete_role(role_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    role = crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if not role.is_editable:
        raise HTTPException(status_code=400, detail="内置角色不可删除")
    crud_role.delete_role(db, role)
    return ResponseModel(message="删除成功")
