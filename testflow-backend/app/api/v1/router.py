from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.projects import router as projects_router
from app.api.v1.testcases import router as testcases_router
from app.api.v1.reports import router as reports_router
from app.api.v1.sprints import router as sprints_router
from app.api.v1.modules import router as modules_router
from app.api.v1.roles import router as roles_router
from app.api.v1.users import router as users_router
from app.api.v1.feature_points import router as feature_points_router
from app.api.v1.ai_config import router as ai_config_router
from app.api.v1.graphs import router as graphs_router
from app.api.v1.pipeline import router as pipeline_router
from app.api.v1.search import router as search_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.knowledge_assets import router as knowledge_assets_router
from app.api.v1.coverage import router as coverage_router
from app.api.v1.trace_links import router as trace_links_router
from app.api.v1.api_endpoints import router as api_endpoints_router
from app.api.v1.change_items import router as change_items_router
from app.api.v1.import_jobs import router as import_jobs_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(projects_router)
api_router.include_router(testcases_router)
api_router.include_router(reports_router)
api_router.include_router(sprints_router)
api_router.include_router(modules_router)
api_router.include_router(roles_router)
api_router.include_router(users_router)
api_router.include_router(feature_points_router)
api_router.include_router(ai_config_router)
api_router.include_router(graphs_router)
api_router.include_router(pipeline_router)
api_router.include_router(search_router)
api_router.include_router(knowledge_router)
api_router.include_router(knowledge_assets_router)
api_router.include_router(coverage_router)
api_router.include_router(trace_links_router)
api_router.include_router(api_endpoints_router)
api_router.include_router(change_items_router)
api_router.include_router(import_jobs_router)
