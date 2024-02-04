from fastapi import APIRouter
from app.api.web.v1.auth import router as auth_router
from app.api.web.v1.wallet import router as wallet_router
from app.api.web.v1.token import router as token_router
from app.core.conf import settings

v1 = APIRouter(prefix=settings.API_V1_STR)

v1.include_router(auth_router, prefix="/auth", tags=["Auth"])
v1.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
v1.include_router(token_router, prefix="/token", tags=["Wallet"])
