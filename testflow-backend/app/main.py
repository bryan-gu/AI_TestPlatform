import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import SessionLocal
from app.api.v1.router import api_router


def _seed_database():
    """初始化默认数据"""
    from app.models.role import Role
    from app.models.user import User
    from app.models.activity import Activity
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        # 创建默认角色
        if db.query(Role).count() == 0:
            roles = [
                Role(name="超级管理员", type="内置", permissions=["*"], is_editable=False),
                Role(name="项目管理员", type="自定义", permissions=["project.view", "project.edit", "case.view", "case.edit", "report.view"], is_editable=True),
                Role(name="测试工程师", type="自定义", permissions=["case.view", "case.edit", "report.view"], is_editable=True),
                Role(name="只读观察员", type="自定义", permissions=["project.view", "case.view", "report.view"], is_editable=True),
            ]
            db.add_all(roles)
            db.commit()
            print("✓ 默认角色已创建")

        # 创建默认管理员
        if db.query(User).count() == 0:
            admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
            admin = User(
                name="张测试",
                email="zhang@test.com",
                password_hash=hash_password("123456"),
                role_id=admin_role.id if admin_role else None,
                project="全部",
                status="活跃",
            )
            db.add(admin)
            db.commit()
            print("✓ 默认管理员已创建 (zhang@test.com / 123456)")

            # 创建初始动态
            if db.query(Activity).count() == 0:
                activities = [
                    Activity(icon="CircleCheck", text="TestFlow 平台初始化完成", user_id=admin.id),
                    Activity(icon="UserFilled", text="管理员账号已创建", user_id=admin.id),
                ]
                db.add_all(activities)
                db.commit()
                print("✓ 初始动态已创建")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化种子数据（表结构由 Alembic 迁移管理）
    _seed_database()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"✓ {settings.APP_NAME} v{settings.APP_VERSION} 已启动")
    print("  提示: 请使用 'alembic upgrade head' 管理数据库表结构")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} API", "version": settings.APP_VERSION, "docs": "/docs"}
