import logging
from typing import Generator, Optional, Dict, Any
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from api.app_context import AppContext
from api.bootstrap import create_app
from core.llms.llm import ChainResult, LLMFactory
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


class BaseChainMock:
    def invoke(
            self,
            prompt: Dict[str, Any],
            memory: Optional[Any] = None,
    ) -> ChainResult:
        return ChainResult(result="mocked result", run_id="mocked_run_id")


def create_app_context() -> AppContext:
    return (AppContext().
            set("logger", logger).
            set("oauth_client", mock_oauth_client()))


async def mock_base_chain():
    mock = MagicMock()
    mock.create_chain.return_value = BaseChainMock()
    return mock


def mock_oauth_client():
    mock = MagicMock()
    mock.validate_token.return_value = {
        "scopes": ["augury", "user"],
        "client": {
            "id": "mocked_client_id",
            "name": "mocked_client_name"
        }
    }
    return mock


@pytest.fixture(scope="module")
def client() -> Generator:
    app = create_app(context=create_app_context())
    with AppTestClient(app) as client:
        app.dependency_overrides[LLMFactory.create_chain] = mock_base_chain
        yield client
        app.dependency_overrides = {}


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OAUTH2_CLIENT_ID", "mocked-secret")
    monkeypatch.setenv("OAUTH2_CLIENT_SECRET", "https://mocked-url.com")
