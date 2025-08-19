from flask import Blueprint, jsonify, make_response
from flask_jwt_extended import jwt_required

from .controller import SinglePlayerQuizController
from app.db.models import QuizSinglePlayer

singlePlayer_bp = Blueprint("singlePlayer",__name__)
singlePlayerQuizController = SinglePlayerQuizController()

@singlePlayer_bp.get('/quiz/singleplayer')
@jwt_required()
def get_quiz():
    """
    Get single player quiz.
    ---
    tags:
      - Quiz
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        description: Bearer token for authentication
      - name: amount
        in: query
        type: integer
        required: true
        description: Number of questions
      - name: category
        in: query
        type: integer
        required: true
        description: Category ID from OpenTDB
      - name: difficulty
        in: query
        type: string
        required: true
        enum: [easy, medium, hard]
        description: Difficulty level
      - name: type_of_questions
        in: query
        type: string
        required: true
        enum: [multiple, boolean]
        description: Type of questions
    responses:
      200:
        description: Successfully fetched quiz
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Quiz fetched successfully"
            data:
              type: object
              example: { "results": [...] }
      400:
        description: Invalid parameters
      404:
        description: Quiz not found or fetch failed
    """
    print("Fetching single player quiz")
    result,status = singlePlayerQuizController.fetch_quiz()
    if status !=200:
        return make_response(jsonify(result),status)
    return make_response(jsonify({"message": "Quiz fetched successfully", "data": result}),status)

@singlePlayer_bp.post('/quiz/singleplayer/answer')
@jwt_required()
def post_answer(response):
    singlePlayerQuizController.check_answer(response)

@singlePlayer_bp.get('/quiz/singleplayer/score/<quiz_id>')
@jwt_required()
def get_score(quiz_id):
    quiz = QuizSinglePlayer.query.filter_by(quiz_id=quiz_id).first()
    if not quiz:
        return jsonify({"error": "Quiz not found"}),404
    return jsonify({
        "category":quiz.category,
        "score":quiz.score,
        "total_questions": quiz.total.questions,
        "username": quiz.total.username,
        "timestamp": quiz.timestamp.isoformat()
    }),200