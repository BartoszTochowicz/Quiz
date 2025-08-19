import datetime
import uuid
from flask_jwt_extended import current_user
import jwt
import requests

from typing import final 

from flask import request
from app.db.db import db
from app.config.config import BaseConfig
from app.db.models import QuizSinglePlayer

class SinglePlayerQuizController():
    def fetch_quiz(self):
        amount = request.args.get('amount')
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        type_of_questions = request.args.get('type_of_questions')
        print("amount:", amount, "category:", category, "difficulty:", difficulty, "type_of_questions:", type_of_questions)
        if not all([amount,category,difficulty,type_of_questions]):
            return {"error": "Missing required parameters"}, 400
        try:
            response = requests.get(f'https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={type_of_questions}')
            data = response.json()
            print(data)
            if not data.get("results"):
                return {"error":"Invalid quiz request"},404
            result = []
            quiz_id = self.generate_ID()
            category_name = data["results"][0]["category"] if data["results"] else ""
            for quiz in data["results"]:
                question_id = self.generate_ID()
                question = quiz["question"]
                answers = [quiz["correct_answer"]]+quiz["incorrect_answers"]
                token = self.encode_jwt(
                    quiz_id=str(quiz_id),
                    question_id=str(question_id),
                    category=category,
                    answers=answers,
                    correct_answer=quiz["correct_answer"])
                result.append({
                    "question_id":str(question_id),
                    "question":question,
                    "answers": answers,
                    "token":token
                })
            return {"quiz_id":str(quiz_id),"category":category_name,"questions":result}, 200
        except Exception as e:
            return {"error": f"Exception occured: {str(e)}"},500
    @final
    def encode_jwt(self,quiz_id,question_id,category,answers,correct_answer):
        # Token will be used to check data integrity
        # Token contains quiz_id, question_id, answers, correct_answer and expiration time
        now = datetime.datetime.utcnow()
        payload = {
            "quiz_id":quiz_id,
            "question_id":question_id,
            "category":category,
            "answers":answers,
            "correct_answer":correct_answer,
            "exp": int((now+datetime.timedelta(minutes=10)).timestamp())
        }
        baseConfig =BaseConfig()
        token = jwt.encode(payload,baseConfig.JWT_SECRET_KEY,algorithm="HS256")
        return token
    @final
    def decode_jwt(self,token):
        baseConfig = BaseConfig()
        result = jwt.decode(token,baseConfig.JWT_SECRET_KEY,algorithms="HS256")
        return result

    @final
    def generate_ID(self):
        # Generate either question id and quiz id
        id = uuid.uuid4()
        return id
    @final
    def check_answer(self,response):
        try:
            token = response.get("token")
            userAnswer = response.get("answer")

            result = self.decode_jwt(token=token)
            quiz_id = result["quiz_id"]
            correctAnswer = result["correct_answer"]
            category = result["category"]

            now = datetime.datetime.utcnow()
            if result.get("exp")<int(now.timestamp()):
                return {"error":"Token expired"},400
            
            is_correct = userAnswer==correctAnswer
            score = 1 if is_correct else 0

            quiz = QuizSinglePlayer.query.filter_by(quiz_id=quiz_id).first()

            if quiz is None:
                quiz = QuizSinglePlayer(
                quiz_id = quiz_id,
                category = category,
                username = current_user.username,
                score = score,
                total_questions = 1,
                timestamp = now)
                db.session.add(quiz)
            else:
                quiz.increase_score(score)
                quiz.add_question_to_total(1)
            db.session.commit()
            return {
                "is_correct":is_correct,
                "current_score":quiz.score
                },200
        except Exception as e:
            return {"error":"Error occuered"+str(e)},500