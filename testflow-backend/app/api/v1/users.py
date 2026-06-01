from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.crud import crud_user

router = APIRouter(prefix="/users", tags=["用户管理"])


def _to_out(user: User, db: Session) -> dict:
    role_name = user.role.name if user.role else ""
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        role_name=role_name,
        project=user.project or "",
        status=user.status,
        last_login=user.last_login,
        created_at=user.created_at,
    ).model_dump()


@router.get("", response_model=ResponseModel)
def list_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    users = crud_user.get_users(db)
    return ResponseModel(data=[_to_out(u, db) for u in users])


@router.get("/stats", response_model=ResponseModel)
def user_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ResponseModel(data=crud_user.get_user_stats(db))


@router.post("", response_model=ResponseModel)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if crud_user.get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    user = crud_user.create_user(db, data)
    return ResponseModel(data=_to_out(user, db))


@router.put("/{user_id}", response_model=ResponseModel)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user = crud_user.update_user(db, user, data)
    return ResponseModel(data=_to_out(user, db))


@router.delete("/{user_id}", response_model=ResponseModel)
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    crud_user.delete_user(db, user)
    return ResponseModel(message="删除成功")
