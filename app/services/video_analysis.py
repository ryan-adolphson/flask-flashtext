import google.generativeai as genai

CUSTOM_CONTEXT = "custom context here"

# MP4 boxes have a 4-byte size followed by a 4-byte type; valid MP4/MOV files use "ftyp"
_MP4_SIG = b"ftyp"


def detect_mime_type(data: bytes) -> str:
    if len(data) >= 8 and data[4:8] == _MP4_SIG:
        return "video/mp4"
    return ""


def analyze_video(video_bytes: bytes, mime_type: str, api_key: str, model_name: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([
        CUSTOM_CONTEXT,
        {"mime_type": mime_type, "data": video_bytes},
    ])
    return response.text
