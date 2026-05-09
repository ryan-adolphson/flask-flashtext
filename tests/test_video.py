import io
from unittest.mock import MagicMock, patch

# Minimal valid MP4: 4-byte box size + "ftyp" at bytes 4-7 (standard MP4 structure)
VALID_MP4 = b"\x00\x00\x00\x20" + b"ftyp" + b"isom" + b"\x00" * 64
INVALID_VIDEO = b"\x00\x01\x02\x03" + b"\x00" * 64

# Gemini returns JSON wrapped in a markdown code fence
GEMINI_RESPONSE = '```json\n{"found": ["Roger Federer", "Nike"], "keyword_count": 2, "match_count": 2, "not_found": []}\n```'
GEMINI_RESPONSE_PLAIN = '{"found": ["Serena Williams"], "keyword_count": 1, "match_count": 1, "not_found": []}'


def _post_video(client, data, headers):
    return client.post("/video", data=data, headers={"X-API-Key": headers["X-API-Key"]},
                       content_type="multipart/form-data")


@patch("app.services.video_analysis.genai")
def test_mp4_video_returns_parsed_json(mock_genai, client, valid_headers):
    mock_genai.GenerativeModel.return_value.generate_content.return_value = MagicMock(text=GEMINI_RESPONSE)

    data = {"video": (io.BytesIO(VALID_MP4), "clip.mp4")}
    resp = _post_video(client, data, valid_headers)

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["found"] == ["Roger Federer", "Nike"]
    assert body["match_count"] == 2
    assert body["keyword_count"] == 2
    assert body["not_found"] == []


@patch("app.services.video_analysis.genai")
def test_plain_json_without_fence_is_parsed(mock_genai, client, valid_headers):
    mock_genai.GenerativeModel.return_value.generate_content.return_value = MagicMock(text=GEMINI_RESPONSE_PLAIN)

    data = {"video": (io.BytesIO(VALID_MP4), "clip.mp4")}
    resp = _post_video(client, data, valid_headers)

    assert resp.status_code == 200
    assert resp.get_json()["found"] == ["Serena Williams"]


def test_unsupported_format_returns_400(client, valid_headers):
    data = {"video": (io.BytesIO(INVALID_VIDEO), "clip.avi")}
    resp = _post_video(client, data, valid_headers)

    assert resp.status_code == 400
    assert resp.get_json()["code"] == "UNSUPPORTED_VIDEO_FORMAT"


def test_missing_video_field_returns_400(client, valid_headers):
    resp = _post_video(client, {}, valid_headers)

    assert resp.status_code == 400
    assert resp.get_json()["code"] == "MISSING_VIDEO"


def test_no_api_key_returns_401(client):
    data = {"video": (io.BytesIO(VALID_MP4), "clip.mp4")}
    resp = client.post("/video", data=data, content_type="multipart/form-data")

    assert resp.status_code == 401


def test_invalid_api_key_returns_403(client, invalid_headers):
    data = {"video": (io.BytesIO(VALID_MP4), "clip.mp4")}
    resp = _post_video(client, data, invalid_headers)

    assert resp.status_code == 403


@patch("app.services.video_analysis.genai")
def test_gemini_called_with_correct_mime_type(mock_genai, client, valid_headers):
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.return_value = MagicMock(text=GEMINI_RESPONSE)

    data = {"video": (io.BytesIO(VALID_MP4), "clip.mp4")}
    _post_video(client, data, valid_headers)

    call_args = mock_model.generate_content.call_args[0][0]
    video_part = call_args[1]
    assert video_part["mime_type"] == "video/mp4"
