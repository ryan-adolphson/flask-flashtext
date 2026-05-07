from flask import Blueprint, abort, jsonify, request

from ..services.keyword_search import search_keywords
from ..validators import validate_search_request

search_bp = Blueprint("search", __name__)


@search_bp.post("/search")
def post_search():
    if not request.is_json:
        abort(400, description={"error": "Request must be JSON", "code": "INVALID_CONTENT_TYPE"})

    req = validate_search_request(request.get_json())
    result = search_keywords(req.text, req.keywords, req.case_sensitive)
    return jsonify(result), 200
