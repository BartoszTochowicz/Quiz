from flask import Blueprint, jsonify, make_response,request
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
def post_answer():
    try:
        print("POST /quiz/singleplayer/answer called")
        response = request.get_json()
        print("Received data:", response)
        result, status = singlePlayerQuizController.check_answer(response)
        return make_response(jsonify(result), status)
    except Exception as e:
        print("Error in post_answer:", e)
        return make_response(jsonify({"error": str(e)}), 500)

@singlePlayer_bp.get('/quiz/singleplayer/score')
@jwt_required()
def get_score():
    quiz_id = request.args.get("quiz_id")
    if not quiz_id:
        return make_response(jsonify({"error": "Missing quiz_id parameter"}),400)
    result,status =singlePlayerQuizController.get_score(quiz_id)
    print("Score result:", result, "Status:", status)
    return make_response(jsonify(result),status)