import json


VALID_BODY = json.dumps({"text": "the fox ran fast", "keywords": ["fox"]})


def test_missing_api_key_returns_401(client):
    resp = client.post("/search", data=VALID_BODY, content_type="application/json")
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["code"] == "MISSING_API_KEY"
    assert "WWW-Authenticate" in resp.headers


def test_invalid_api_key_returns_403(client, invalid_headers):
    resp = client.post("/search", data=VALID_BODY, headers=invalid_headers)
    assert resp.status_code == 403
    assert resp.get_json()["code"] == "INVALID_API_KEY"


def test_valid_api_key_passes(client, valid_headers):
    resp = client.post("/search", data=VALID_BODY, headers=valid_headers)
    assert resp.status_code == 200


def test_health_no_auth_required(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_empty_api_key_header_returns_401(client):
    resp = client.post(
        "/search",
        data=VALID_BODY,
        content_type="application/json",
        headers={"X-API-Key": ""},
    )
    assert resp.status_code == 401
    assert resp.get_json()["code"] == "MISSING_API_KEY"
