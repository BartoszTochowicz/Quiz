from flask import Blueprint, jsonify, request
from .controllers import fetch_quiz_questions

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/', methods=['GET'])
def get_questions():
    category = request.args.get('category', 'Linux')
    limit = request.args.get('limit', 5)
    try:
        questions = fetch_quiz_questions(category, limit)
        return jsonify(questions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500