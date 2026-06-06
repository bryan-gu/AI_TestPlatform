import os
import re
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import SessionLocal
from app.api.v1.router import api_router

# 北京时间 UTC+8
_BEIJING_TZ = timezone(timedelta(hours=8))
# 匹配 ISO datetime 字符串（如 2026-06-06T16:47:06 或 2026-06-06 16:47:06）
_DT_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}')


def _convert_datetimes(obj):
    """递归将响应中所有 UTC datetime / ISO 字符串转为北京时间"""
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=timezone.utc)
        return obj.astimezone(_BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, str) and _DT_PATTERN.match(obj):
        try:
            dt = datetime.fromisoformat(obj.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(_BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return obj
    if isinstance(obj, dict):
        return {k: _convert_datetimes(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_convert_datetimes(item) for item in obj]
    return obj


class BeijingJSONResponse(JSONResponse):
    """自定义 JSON 响应：自动将所有时间字段转为北京时间"""
    def render(self, content) -> bytes:
        content = _convert_datetimes(content)
        return super().render(content)


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
                email="admin@test.com",
                password_hash=hash_password("Aa123456"),
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

        # AI 配置种子数据
        try:
            from app.crud import crud_ai_config
            crud_ai_config.seed_global_configs(db)
            crud_ai_config.seed_strategies(db)
            print("✓ AI 配置种子数据已初始化")
        except Exception:
            # 表可能尚未迁移，跳过
            pass
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
    default_response_class=BeijingJSONResponse,
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
