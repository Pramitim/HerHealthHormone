from flask import Blueprint, request, jsonify
from llama_service import generate_schedule

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/test", methods=["GET"])
def test_ai():
    return {"message": "AI route working"}, 200

@ai_bp.route("/schedule", methods=["POST"])
def schedule():
    user_input = request.json
    schedule = generate_schedule(user_input)
    return jsonify({"schedule": schedule})
