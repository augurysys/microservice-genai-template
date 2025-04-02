from auth_sdk.auth_middleware import AuthenticationMiddleware

from api.app_context import AppContext
from utils.logger import LogRequestMiddleware
from api.routers import support_response_route, health_check
from starlette.middleware import Middleware
from fastapi import FastAPI
from utils.RequestBodyMiddleware import CacheRequestBodyMiddleware


def create_app(context: AppContext = AppContext(), lifespan_main=None) -> FastAPI:

    oauth_client = context.get("oauth_client")
    logger = context.get("logger")

    middlewares = [
        Middleware(CacheRequestBodyMiddleware, logger=logger),
        Middleware(LogRequestMiddleware, logger=logger),
        Middleware(AuthenticationMiddleware, logger=logger, oauth_client=oauth_client,
                   scopes="augury,user")
    ]

    app = FastAPI(title="AuguryGenAIAPI", lifespan=lifespan_main, middleware=middlewares)
    app.include_router(health_check.router)
    app.include_router(support_response_route.router)
    app.include_router(health_check.router)

    # example domain routes
    app.include_router(support_response_route.router)
    return app
