import google.generativeai as genai

CUSTOM_CONTEXT = "custom context here"

_JPEG_SIG = b"\xff\xd8\xff"
_PNG_SIG = b"\x89PNG\r\n\x1a\n"
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


def detect_mime_type(data: bytes) -> str:
    if data[:3] == _JPEG_SIG:
        return "image/jpeg"
    if data[:8] == _PNG_SIG:
        return "image/png"
    return ""


def analyze_image(image_bytes: bytes, mime_type: str, api_key: str, model_name: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([
        CUSTOM_CONTEXT,
        {"mime_type": mime_type, "data": image_bytes},
    ])
    return response.text
