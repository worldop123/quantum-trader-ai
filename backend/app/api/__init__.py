from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.market import router as market_router
from app.api.trading import router as trading_router
from app.api.strategy import router as strategy_router
from app.api.risk import router as risk_router
from app.api.option import router as option_router
from app.api.local_model import router as local_model_router
from app.api.notification import router as notification_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(market_router)
api_router.include_router(trading_router)
api_router.include_router(strategy_router)
api_router.include_router(risk_router)
api_router.include_router(option_router)
api_router.include_router(local_model_router)
api_router.include_router(notification_router)

__all__ = ["api_router"]
