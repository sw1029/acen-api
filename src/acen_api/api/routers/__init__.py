"""FastAPI 애플리케이션 라우터 모음."""

from fastapi import APIRouter

from .dates import router as dates_router
from .evaluate import router as evaluate_router
from .feedback import router as feedback_router
from .health import router as health_router
from .model import router as model_router
from .products import router as products_router
from .calendars import router as calendars_router
from .uploads import router as uploads_router
from .users import router as users_router
from .templates import router as templates_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(templates_router)
api_router.include_router(dates_router)
api_router.include_router(products_router)
api_router.include_router(calendars_router)
api_router.include_router(model_router)
api_router.include_router(evaluate_router)
api_router.include_router(feedback_router)
api_router.include_router(uploads_router)
api_router.include_router(users_router)

__all__ = [
    "api_router",
    "health_router",
    "templates_router",
    "dates_router",
    "model_router",
    "evaluate_router",
    "feedback_router",
    "uploads_router",
    "users_router",
]
