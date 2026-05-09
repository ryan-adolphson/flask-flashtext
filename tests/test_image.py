import io
from unittest.mock import MagicMock, patch

# Minimal valid image bytes (magic bytes only — enough for signature detection)
VALID_JPEG = b"\xff\xd8\xff" + b"\x00" * 64
VALID_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
INVALID_IMAGE = b"\x00\x01\x02\x03" + b"\x00" * 64

# Gemini returns JSON wrapped in a markdown code fence
GEMINI_RESPONSE = '```json\n{"found": ["Roger Federer", "Nike"], "keyword_count": 2, "match_count": 2, "not_found": []}\n```'
GEMINI_RESPONSE_PLAIN = '{"found": ["Serena Williams"], "keyword_count": 1, "match_count": 1, "not_found": []}'


def _post_image(client, data, headers):
    return client.post("/image", data=data, headers={"X-API-Key": headers["X-API-Key"]},
                       content_type="multipart/form-data")


@patch("app.services.image_analysis.genai")
def test_jpeg_image_returns_parsed_json(mock_genai, client, valid_headers):
    mock_genai.GenerativeModel.return_value.generate_content.return_value = MagicMock(text=GEMINI_RESPONSE)

    data = {"image": (io.BytesIO(VALID_JPEG), "photo.jpg")}
    resp = _post_image(client, data, valid_headers)

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["found"] == ["Roger Federer", "Nike"]
    assert body["match_count"] == 2
    assert body["keyword_count"] == 2
    assert body["not_found"] == []


@patch("app.services.image_analysis.genai")
def test_png_image_returns_parsed_json(mock_genai, client, valid_headers):
    mock_genai.GenerativeModel.return_value.generate_content.return_value = MagicMock(text=GEMINI_RESPONSE)

    data = {"image": (io.BytesIO(VALID_PNG), "photo.png")}
    resp = _post_image(client, data, valid_headers)

    assert resp.status_code == 200
    assert "found" in resp.get_json()


@patch("app.services.image_analysis.genai")
def test_plain_json_without_fence_is_parsed(mock_genai, client, valid_headers):
    mock_genai.GenerativeModel.return_value.generate_content.return_value = MagicMock(text=GEMINI_RESPONSE_PLAIN)

    data = {"image": (io.BytesIO(VALID_JPEG), "photo.jpg")}
    resp = _post_image(client, data, valid_headers)

    assert resp.status_code == 200
    assert resp.get_json()["found"] == ["Serena Williams"]


def test_unsupported_format_returns_400(client, valid_headers):
    data = {"image": (io.BytesIO(INVALID_IMAGE), "file.gif")}
    resp = _post_image(client, data, valid_headers)

    assert resp.status_code == 400
    assert resp.get_json()["code"] == "UNSUPPORTED_IMAGE_FORMAT"


def test_missing_image_field_returns_400(client, valid_headers):
    resp = _post_image(client, {}, valid_headers)

    assert resp.status_code == 400
    assert resp.get_json()["code"] == "MISSING_IMAGE"


def test_no_api_key_returns_401(client):
    data = {"image": (io.BytesIO(VALID_JPEG), "photo.jpg")}
    resp = client.post("/image", data=data, content_type="multipart/form-data")

    assert resp.status_code == 401


def test_invalid_api_key_returns_403(client, invalid_headers):
    data = {"image": (io.BytesIO(VALID_JPEG), "photo.jpg")}
    resp = _post_image(client, data, invalid_headers)

    assert resp.status_code == 403


@patch("app.services.image_analysis.genai")
def test_gemini_called_with_correct_mime_type(mock_genai, client, valid_headers):
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.return_value = MagicMock(text=GEMINI_RESPONSE)

    data = {"image": (io.BytesIO(VALID_PNG), "photo.png")}
    _post_image(client, data, valid_headers)

    call_args = mock_model.generate_content.call_args[0][0]
    image_part = call_args[1]
    assert image_part["mime_type"] == "image/png"
