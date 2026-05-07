from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def get_health():
    return jsonify({"status": "ok", "version": current_app.config["VERSION"]}), 200
