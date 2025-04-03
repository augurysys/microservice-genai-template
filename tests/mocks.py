import json
from unittest.mock import MagicMock

from api.handlers.support_response_handler import SupportResponse


class BaseLLMMock:
    def invoke(
            self, prompt
    ) -> str:
        return SupportResponse(response="mocked_response", action_required=True).json()


async def mock_llm():
    mock = MagicMock()
    mock.return_value = BaseLLMMock()
    return mock


# TODO move this to the SDK
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
