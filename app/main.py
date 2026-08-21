from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import AsyncSessionLocal
from app.seed.currencies import seed_currencies
from app.seed.countries import seed_countries
from app.seed.mobile_money import seed_mobile_money_networks
from app.api.admin_orders import router as admin_orders_router
from app.api.admin_cards import router as admin_cards_router
from app.api.admin_core import router as admin_core_router
from app.api.admin_revenue import router as admin_revenue_router
from app.api.auth import router as auth_router
from app.api.countries import router as countries_router
from app.api.cards import router as cards_router
from app.api.deposit import router as deposit_router
from app.api.history import router as history_router
from app.api.mobile_money import router as mobile_money_router
from app.api.notifications import router as notifications_router
from app.api.orders import router as orders_router
from app.api.profile import router as profile_router
from app.api.shop import router as shop_router
from app.api.settings import router as settings_router
from app.api.transactions import router as transactions_router
from app.api.transfer import router as transfer_router
from app.api.wallet import router as wallet_router
from app.api.webhooks import router as webhooks_router
from app.api.withdrawal import router as withdrawal_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed the static catalog only after Alembic migrations have been applied.
    async with AsyncSessionLocal() as db:
        await seed_currencies(db)
        await seed_countries(db)
        await seed_mobile_money_networks(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
    openapi_url="/openapi.json" if settings.app_env != "production" else None,
    lifespan=lifespan,
)


for router in (
    auth_router,
    countries_router,
    history_router,
    notifications_router,
    orders_router,
    shop_router,
    settings_router,
    admin_revenue_router,
    admin_orders_router,
    admin_cards_router,
    admin_core_router,
    profile_router,
    deposit_router,
    webhooks_router,
    withdrawal_router,
    transactions_router,
    transfer_router,
    wallet_router,
    mobile_money_router,
    cards_router,
):
    app.include_router(router)


if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Telegram-Init-Data"],
    )


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
    }
