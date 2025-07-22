import datetime
import uuid
import jwt
import requests

from typing import final 

from flask import request
from app.config.config import BaseConfig


class SinglePlayerQuizController():
    def fetch_quiz(self):
        amount = request.args.get('amount')
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        type_of_questions = request.args.get('type_of_questions')
        if not all([amount,category,difficulty,type_of_questions]):
            return {"error": "Missing required parameters"}, 400
        try:
            response = requests.get(f'https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={type_of_questions}')
            data = response.json()
            print(data)
            if not data.get("results"):
                return {"error":"Invalid quiz request"},404
            result = []
            quiz_id = self.generateID()
            
            for quiz in data["results"]:
                question_id = self.generateID()
                answers = [quiz["correct_answer"]]+quiz["incorrect_answers"]
                token = self.generate_jwt(
                    quiz_id=str(quiz_id),
                    question_id=str(question_id),
                    answers=answers,
                    correct_answer=quiz["correct_answer"])
                result.append({
                    "question_id":str(question_id),
                    "answers": answers,
                    "token":token
                })
            return {"quiz_id":str(quiz_id),"questions":result}, 200
        except Exception as e:
            return {"error": f"Exception occured: {str(e)}"},500
    @final
    def generate_jwt(self,quiz_id,question_id,answers,correct_answer):
        # Token will be used to check data integrity
        # Token contains quiz_id, question_id, answers, correct_answer and expiration time
        now = datetime.datetime.utcnow()
        payload = {
            "quiz_id":quiz_id,
            "question_id":question_id,
            "answers":answers,
            "correct_answer":correct_answer,
            "exp": int((now+datetime.timedelta(minutes=5)).timestamp())
        }
        baseConfig =BaseConfig()
        token = jwt.encode(payload,baseConfig.JWT_SECRET_KEY,algorithm="HS256")
        return token
    @final
    def generateID(self):
        # Generate either question id and quiz id
        id = uuid.uuid4()
        return id