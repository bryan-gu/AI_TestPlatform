from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class RoleInfo(BaseModel):
    name: str
    permissions: list[str] = []

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    role: RoleInfo | None = None

    class Config:
        from_attributes = True
