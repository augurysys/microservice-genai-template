from typing import Dict, Optional, Any
from unittest.mock import MagicMock

from starlette.testclient import TestClient

from api.app import app
from core.llms.llm import ChainResult, LLMFactory

client = TestClient(app)





def test_generate_support_response():
    app.dependency_overrides[LLMFactory.create_chain] = mock_base_chain
    print("Dependency override applied")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
