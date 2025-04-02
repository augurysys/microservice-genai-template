import logging
import os
from contextlib import asynccontextmanager
import uvicorn
from auth_sdk.init import init_oauth_client
from raven import Client as RavenClient

from api.app_context import AppContext
from api.bootstrap import create_app

from fastapi import FastAPI
from langchain_openai import AzureOpenAIEmbeddings
from pymongo import MongoClient

from utils.log_wrapper import LogWrapper
from utils.logger import get_logger

logger = LogWrapper(get_logger(name="Main", log_level=logging.INFO), RavenClient())


@asynccontextmanager
async def lifespan_main(_app: FastAPI):
    async with lifespan_gen_ai(_app):
        yield

app = create_app(context=AppContext().
                 set("oauth_client", init_oauth_client())
                 .set("logger", logger), lifespan_main=lifespan_main)


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
