from typing import List, Optional
from pydantic_settings import BaseSettings
import os
from functools import lru_cache
from raven import Client as RavenClient
from ai_logger.logger import get_logger
from utils.log_wrapper import LogWrapper
import logging


class Settings(BaseSettings):
    client_id: str = os.environ.get("OAUTH2_CLIENT_ID")
    client_secret: str = os.environ.get("OAUTH2_CLIENT_SECRET")
    token_url: str = os.environ.get("AUGURY_OAUTH2_INTERNAL_URL") + '/token/'
    environment: str = os.getenv("AUGURY_ENV", "development")
    expose_prometheus: str = os.environ.get("EXPOSE_PROMETHEUS")
    backend_lookupd_http_addresses: List[Optional[str]] = os.getenv('LOOKUPD_HTTP_ADDRESSES', '').split(',')


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
logger = LogWrapper(get_logger(name="API", log_level=logging.INFO), RavenClient())
