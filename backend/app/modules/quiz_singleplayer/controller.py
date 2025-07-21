import datetime
import jwt
import requests
from flask import current_app
from flask import request

class SinglePlayerQuizController():
    def fetch_quiz():
        amount = request.args.get('amount')
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        type_of_questions = request.args.get('type_of_questions')
        if not all([amount,category,difficulty,type_of_questions]):
            return {"error": "Missing required parameters"}, 400
        try:
            response = requests.get(f'https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={type_of_questions}')
            data = response.json()
            if len(data) == 0:
                return {"error":"Invalid quiz request"},404
            
            return data, 200
        except Exception as e:
            return {"error": f"Exception occured: {str(e)}"},500
    def create_jwt(quiz_id,question_id,answers,correct_answer):
        payload = {
            "quiz_id":quiz_id,
            "question_id":question_id,
            "answers":answers,
            "correct_answer":correct_answer,
            "iat": datetime.datetime.utcnow(),
            "eat": datetime.datetime.utcnow()+datetime.timedelta(minutes=5)
        }
        token = jwt.encode(payload,S)
