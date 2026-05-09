from flask import Flask, jsonify
from flask_cors import CORS

from .auth import require_api_key
from .config import ProductionConfig
from .routes.health import health_bp
from .routes.image import image_bp
from .routes.search import search_bp


def create_app(config=None):
    app = Flask(__name__)

    cfg = config or ProductionConfig
    app.config.from_object(cfg)

    CORS(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(search_bp)

    @app.before_request
    def auth_gate():
        from flask import request
        if request.blueprint == "health":
            return
        return require_api_key()

    _register_error_handlers(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    def _error_response(code, message, machine_code, status):
        response = {"error": message, "code": machine_code}
        return jsonify(response), status

    @app.errorhandler(400)
    def bad_request(e):
        desc = e.description
        if isinstance(desc, dict):
            return jsonify(desc), 400
        return _error_response(400, "Bad request", "BAD_REQUEST", 400)

    @app.errorhandler(401)
    def unauthorized(e):
        resp = jsonify({"error": "Missing or empty API key", "code": "MISSING_API_KEY"})
        resp.status_code = 401
        resp.headers["WWW-Authenticate"] = "ApiKey"
        return resp

    @app.errorhandler(403)
    def forbidden(e):
        return _error_response(403, "Invalid API key", "INVALID_API_KEY", 403)

    @app.errorhandler(404)
    def not_found(e):
        return _error_response(404, "Not found", "NOT_FOUND", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return _error_response(405, "Method not allowed", "METHOD_NOT_ALLOWED", 405)

    @app.errorhandler(422)
    def unprocessable(e):
        desc = e.description
        if isinstance(desc, dict):
            return jsonify(desc), 422
        return _error_response(422, "Unprocessable entity", "VALIDATION_ERROR", 422)

    @app.errorhandler(500)
    def internal_error(e):
        return _error_response(500, "Internal server error", "INTERNAL_ERROR", 500)
