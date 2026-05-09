import json
import re

import google.generativeai as genai

CUSTOM_CONTEXT = """
    take this image and return a list of peoples and brands you see. Only include the result if you are 98% sure it is correct. Also return the results in JSON that looks like this
    {
        "found": [
            "stephani"
        ],
        "keyword_count": 2,
        "match_count": 1,
        "not_found": []
    }
    """

_JPEG_SIG = b"\xff\xd8\xff"
_PNG_SIG = b"\x89PNG\r\n\x1a\n"
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


def detect_mime_type(data: bytes) -> str:
    if data[:3] == _JPEG_SIG:
        return "image/jpeg"
    if data[:8] == _PNG_SIG:
        return "image/png"
    return ""


def _parse_gemini_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    return json.loads(text.strip())


def analyze_image(image_bytes: bytes, mime_type: str, api_key: str, model_name: str) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([
        CUSTOM_CONTEXT,
        {"mime_type": mime_type, "data": image_bytes},
    ])
    return _parse_gemini_json(response.text)
