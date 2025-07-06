from flask import Blueprint, jsonify, request
from .controllers import fetch_quiz_questions

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/registration', methods=['POST'])
def post_register_user():
    data = request.get_json()
    
    return jsonify({"message": "User registered successfully", "data": data}), 201