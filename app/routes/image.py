from flask import Blueprint, abort, current_app, jsonify, request

from ..services.image_analysis import ALLOWED_MIME_TYPES, analyze_image, detect_mime_type

image_bp = Blueprint("image", __name__)


@image_bp.post("/image")
def post_image():
    if "file" not in request.files:
        abort(400, description={"error": "No image field in request", "code": "MISSING_IMAGE"})

    file = request.files["file"]
    if file.filename == "":
        abort(400, description={"error": "No file selected", "code": "MISSING_IMAGE"})

    image_bytes = file.read()
    mime_type = detect_mime_type(image_bytes)

    if not mime_type:
        abort(400, description={
            "error": "Unsupported image format. Only JPEG and PNG are accepted",
            "code": "UNSUPPORTED_IMAGE_FORMAT",
        })

    api_key = current_app.config.get("GEMINI_API_KEY", "")
    if not api_key:
        abort(500, description={"error": "Gemini API key not configured", "code": "INTERNAL_ERROR"})

    result = analyze_image(
        image_bytes,
        mime_type,
        api_key=api_key,
        model_name=current_app.config["GEMINI_MODEL"],
    )
    return jsonify(result), 200
