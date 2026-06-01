from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.projects import router as projects_router
from app.api.v1.testcases import router as testcases_router
from app.api.v1.reports import router as reports_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.roles import router as roles_router
from app.api.v1.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(projects_router)
api_router.include_router(testcases_router)
api_router.include_router(reports_router)
api_router.include_router(knowledge_router)
api_router.include_router(roles_router)
api_router.include_router(users_router)
