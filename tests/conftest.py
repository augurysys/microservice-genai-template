from typing import Generator, Optional, Dict, Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.app import app
from core.llms.llm import ChainResult, LLMFactory


class BaseChainMock:
    def invoke(
            self,
            prompt: Dict[str, Any],
            memory: Optional[Any] = None,
    ) -> ChainResult:
        return ChainResult(result="mocked result", run_id="mocked_run_id")


async def mock_base_chain():
    mock = MagicMock()
    mock.create_chain.return_value = BaseChainMock()
    return mock


@pytest.fixture
def client() -> Generator:
    with TestClient(app) as client:
        app.dependency_overrides[LLMFactory.create_chain] = mock_base_chain
        yield client
        app.dependency_overrides = {}


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OAUTH2_CLIENT_ID", "mocked-secret")
    monkeypatch.setenv("OAUTH2_CLIENT_SECRET", "https://mocked-url.com")
