import hmac

from flask import abort, current_app, request


def require_api_key() -> None:
    provided = request.headers.get("X-API-Key", "")
    if not provided:
        abort(401)

    valid_keys: set = current_app.config["API_KEYS"]
    for key in valid_keys:
        if hmac.compare_digest(provided, key):
            return

    abort(403)
