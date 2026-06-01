from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import LoginRequest, RegisterRequest, ChangePasswordRequest, UserInfo, RoleInfo
from app.schemas.common import ResponseModel, TokenResponse
from app.crud.crud_user import create_user, get_user_by_email, update_last_login
from app.schemas.user import UserCreate
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=ResponseModel)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")
    update_last_login(db, user)
    token = create_access_token(user.id)
    return ResponseModel(data=TokenResponse(token=token).model_dump())


@router.post("/register", response_model=ResponseModel)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册")
    # 默认分配测试工程师角色
    default_role = db.query(Role).filter(Role.name == "测试工程师").first()
    user = create_user(db, UserCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        role_id=default_role.id if default_role else None,
    ))
    token = create_access_token(user.id)
    return ResponseModel(data=TokenResponse(token=token).model_dump())


@router.post("/logout", response_model=ResponseModel)
def logout():
    return ResponseModel(message="已登出")


@router.get("/me", response_model=ResponseModel)
def get_me(current_user: User = Depends(get_current_user)):
    role = None
    if current_user.role:
        role = RoleInfo(name=current_user.role.name, permissions=current_user.role.permissions or [])
    user_info = UserInfo(id=current_user.id, name=current_user.name, email=current_user.email, role=role)
    return ResponseModel(data=user_info.model_dump())


@router.post("/change-password", response_model=ResponseModel)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return ResponseModel(message="密码修改成功")
