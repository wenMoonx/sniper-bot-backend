# We need to set configuration on this file
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from app.common.redis import redis_client
from app.core.conf import settings
from app.api.web.routers import v1
from app.lib.health_check import http_limit_callback
from starlette.middleware.authentication import AuthenticationMiddleware
from app.middleware.jwt_auth_middleware import JwtAuthMiddleware

@asynccontextmanager
async def register_init(app: FastAPI):
    # redis
    await redis_client.open()
    # limiter
    await FastAPILimiter.init(redis_client, prefix=settings.LIMITER_REDIS_PREFIX, http_callback=http_limit_callback)

    yield

    await redis_client.close()
    await FastAPILimiter.close()

def register_app():
    # FastAPI
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        lifespan=register_init
    )

    register_middleware(app)

    register_router(app)
    # ensure_unique_route_names(app)

    return app

def register_middleware(app: FastAPI):
    """
    Middleware, execution order from bottom to top

    :param app:
    :return:
    """
    
    # Keycloak auth, required
    # app.add_middleware(
    #     AuthenticationMiddleware, backend=KeycloakAuthMiddleware(), on_error=KeycloakAuthMiddleware.auth_exception_handler
    # )

    app.add_middleware(
        AuthenticationMiddleware, backend=JwtAuthMiddleware(), on_error=JwtAuthMiddleware.auth_exception_handler
    )
    
    # CORS: Always at the end
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    
    # idp.add_swagger_config(app)
# def register_redis_client(app: FastAPI):

def register_router(app: FastAPI):
    """
    comment
    :param app: FastAPI
    :return:
    """
    # API
    app.include_router(v1)
