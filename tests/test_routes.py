import json


def test_post_search_success_200(client, valid_headers):
    body = json.dumps({"text": "the fox ran past the dog", "keywords": ["fox", "dog", "cat"]})
    resp = client.post("/search", data=body, headers=valid_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data.keys()) == {"found", "not_found", "match_count", "keyword_count"}
    assert "fox" in data["found"]
    assert "dog" in data["found"]
    assert "cat" in data["not_found"]
    assert data["match_count"] == 2
    assert data["keyword_count"] == 3


def test_missing_text_field_422(client, valid_headers):
    body = json.dumps({"keywords": ["fox"]})
    resp = client.post("/search", data=body, headers=valid_headers)
    assert resp.status_code == 422
    data = resp.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "detail" in data


def test_missing_keywords_field_422(client, valid_headers):
    body = json.dumps({"text": "the fox ran fast"})
    resp = client.post("/search", data=body, headers=valid_headers)
    assert resp.status_code == 422
    assert resp.get_json()["code"] == "VALIDATION_ERROR"


def test_empty_keywords_list_422(client, valid_headers):
    body = json.dumps({"text": "the fox ran fast", "keywords": []})
    resp = client.post("/search", data=body, headers=valid_headers)
    assert resp.status_code == 422
    assert resp.get_json()["code"] == "VALIDATION_ERROR"


def test_text_too_long_422(client, valid_headers):
    body = json.dumps({"text": "a" * 1_048_577, "keywords": ["a"]})
    resp = client.post("/search", data=body, headers=valid_headers)
    assert resp.status_code == 422
    assert resp.get_json()["code"] == "VALIDATION_ERROR"


def test_non_json_body_400(client, valid_headers):
    headers = {**valid_headers, "Content-Type": "text/plain"}
    resp = client.post("/search", data="not json", headers=headers)
    assert resp.status_code == 400
    assert resp.get_json()["code"] == "INVALID_CONTENT_TYPE"


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "version" in data


def test_get_method_not_allowed_on_search(client, valid_headers):
    resp = client.get("/search", headers=valid_headers)
    assert resp.status_code == 405


def test_response_always_has_all_fields(client, valid_headers):
    body = json.dumps({"text": "nothing matches here", "keywords": ["xyz123"]})
    resp = client.post("/search", data=body, headers=valid_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "found" in data
    assert "not_found" in data
    assert "match_count" in data
    assert "keyword_count" in data


def test_case_sensitive_flag_respected(client, valid_headers):
    body = json.dumps({"text": "the Fox ran fast", "keywords": ["fox"], "case_sensitive": True})
    resp = client.post("/search", data=body, headers=valid_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "fox" in data["not_found"]

    body2 = json.dumps({"text": "the Fox ran fast", "keywords": ["Fox"], "case_sensitive": True})
    resp2 = client.post("/search", data=body2, headers=valid_headers)
    assert "Fox" in resp2.get_json()["found"]
