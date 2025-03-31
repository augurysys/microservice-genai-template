import logging
import os
from contextlib import asynccontextmanager
import uvicorn

from api.routers import support_response_route
from utils.log_wrapper import LogWrapper
from starlette.middleware import Middleware

from utils.RequestBodyMiddleware import CacheRequestBodyMiddleware
from fastapi import FastAPI
from langchain_openai import AzureOpenAIEmbeddings
from pymongo import MongoClient
from raven import Client as RavenClient
from auth_sdk.auth_middleware import AuthenticationMiddleware
from auth_sdk.init import init_oauth_client
from utils.logger import LogRequestMiddleware, get_logger


@asynccontextmanager
async def lifespan_main(_app: FastAPI):
    async with lifespan_gen_ai(_app):
        yield


logger = LogWrapper(get_logger(name="Main", log_level=logging.INFO), RavenClient())
oauth_client_internal = init_oauth_client()

middlewares = [
    Middleware(CacheRequestBodyMiddleware, logger=logger),
    Middleware(LogRequestMiddleware, logger=logger),
    Middleware(AuthenticationMiddleware, logger=logger, oauth_client=oauth_client_internal,
               scopes="augury,user")
]

app = FastAPI(title="AuguryGenAIAPI", lifespan=lifespan_main, middleware=middlewares)
app.include_router(health_check.router)

# example domain routes
app.include_router(support_response_route.router)


@asynccontextmanager
async def lifespan_gen_ai(_app: FastAPI):
    try:
        mongodb_url = os.environ.get("MONGODB_URL", None)
        if mongodb_url is None:
            raise EnvironmentError('please set MONGODB_URL')
        mongodb_name = os.environ.get("MONGODB_DB", None)
        if mongodb_name is None:
            raise EnvironmentError('please set MONGODB_DB')

        azure_embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002")
        db = MongoClient(mongodb_url)[mongodb_name]

        _app.state.mongodb_url = mongodb_url
        _app.state.mongodb_name = mongodb_name
        _app.state.azure_embeddings = azure_embeddings
        _app.state.db = db
    except Exception as e:
        logger.error("error while starting app", tags={"error": str(e)})
        raise e

    yield


if __name__ == '__main__':
    logger.info("Starting.")
    uvicorn.run(app, port=3000, host='0.0.0.0')
    logger.info("Exiting.")
