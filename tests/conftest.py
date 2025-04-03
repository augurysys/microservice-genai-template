import logging
from typing import Generator
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.app_context import AppContext
from api.bootstrap import create_app
from core.llms.llm import LLMFactory
from tests.mocks import mock_oauth_client, mock_llm
from utils.log_wrapper import LogWrapper
from utils.logger import get_logger

logger = LogWrapper(get_logger(name="Main", log_level=logging.INFO))


class AppTestClient(TestClient):
    def __init__(self, app):
        super().__init__(app)

    def request(self, method, url, **kwargs):
        headers = kwargs.pop("headers") or dict()
        headers["Authorization"] = "Bearer dummy"
        return super().request(method, url, headers=headers, **kwargs)


def create_app_context() -> AppContext:
    return (AppContext().
            set("logger", logger).
            set("oauth_client", mock_oauth_client()))


def add_mocks(app: FastAPI):
    app.dependency_overrides[LLMFactory.create_openai_llm] = mock_llm


@pytest.fixture(scope="module")
def client() -> Generator:
    app = create_app(context=create_app_context())
    with AppTestClient(app) as client:
        add_mocks(app)
        app.dependency_overrides[LLMFactory.create_openai_llm] = mock_llm
        yield client
        app.dependency_overrides = {}


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OAUTH2_CLIENT_ID", "mock-id")
    monkeypatch.setenv("OAUTH2_CLIENT_SECRET", "mock-secret")
