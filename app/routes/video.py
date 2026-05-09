from flask import Blueprint, abort, current_app, jsonify, request

from ..services.video_analysis import analyze_video, detect_mime_type

video_bp = Blueprint("video", __name__)


@video_bp.post("/video")
def post_video():
    if "file" not in request.files:
        abort(400, description={"error": "No video field in request", "code": "MISSING_VIDEO"})

    file = request.files["file"]
    if file.filename == "":
        abort(400, description={"error": "No file selected", "code": "MISSING_VIDEO"})

    video_bytes = file.read()
    mime_type = detect_mime_type(video_bytes)

    if not mime_type:
        abort(400, description={
            "error": "Unsupported video format. Only MP4 is accepted",
            "code": "UNSUPPORTED_VIDEO_FORMAT",
        })

    api_key = current_app.config.get("GEMINI_API_KEY", "")
    if not api_key:
        abort(500, description={"error": "Gemini API key not configured", "code": "INTERNAL_ERROR"})

    result = analyze_video(
        video_bytes,
        mime_type,
        api_key=api_key,
        model_name=current_app.config["GEMINI_MODEL"],
    )
    return jsonify(result), 200
