from models.generate_support_response_request import GenerateSupportResponseRequest


def test_health_check(client):
    response = client.get("/_ping")
    assert response.status_code == 200


def test_generate_support_response(client):
    request = GenerateSupportResponseRequest(domain_data="hello", query="hello")
    # TODO replace with SDK call
    response = client.post("/support/generate/support_response", json=request.dict())
    assert response.status_code == 200
