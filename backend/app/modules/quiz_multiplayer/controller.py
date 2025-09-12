from datetime import timedelta
import datetime
import random
import jwt
from typing_extensions import final
import uuid
from flask import request
import requests
from html import unescape

from app.db.models import Quiz, QuizParticipant
from app.db.db import db
from app.db.models import Lobby



class QuizMultiplayerController:
    @final
    def fetch_quiz(self,amount,category,difficulty,type_of_questions):
        try:
            response = requests.get(f'https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={type_of_questions}')
            data = response.json()
            print(data)
            if not data.get("results"):
                return {"error":"Invalid quiz request"},404
            quiz_id = self.generate_ID()
            category_name = data["results"][0]["category"]
            questions = []
            question_id = 0
            for quiz in data["results"]:
                question = unescape(quiz["question"])
                choices = [quiz["correct_answer"]]+quiz["incorrect_answers"]
                choices =[unescape(choice) for choice in choices]
                random.shuffle(choices)
                correct_answer=quiz["correct_answer"]
                questions.append({
                    "id":question_id,
                    "question": question,
                    "choices": choices,
                    "correct_answer": correct_answer
                })
                question_id += 1
            return {"quiz_id":str(quiz_id),"category":category_name,"questions":questions}, 200
        except Exception as e:
            return {"error": f"Exception occured: {str(e)}"},500
    @final
    def save_quiz(self,quiz_id,category,questions,total_questions,difficulty,type_of_questions):
        try:
            new_quiz = Quiz(
                quiz_id=quiz_id,
                category=category,
                questions=questions,
                total_questions=total_questions,
                difficulty=difficulty,
                type_of_questions=type_of_questions,
                timestamp=datetime.datetime.utcnow()
            )
            db.session.add(new_quiz)
            db.session.commit()
            return True,quiz_id
        except Exception as e:
            print(f"Error saving quiz: {str(e)}")
            return False,quiz_id
    @final
    def generate_ID(self):
        # Generate either question id and quiz id
        id = uuid.uuid4()
        return id
    def create_lobby(self,data):
        # data = request.get_json()
        category = data.get("category")
        amount = data.get("amount")
        difficulty = data.get("difficulty")
        type_of_questions = data.get("type_of_questions")
        if not all([amount,category,difficulty,type_of_questions]):
            return {"error": "Missing required parameters"}, 400
        quiz_data, status_code = self.fetch_quiz(amount,category,difficulty,type_of_questions)
        if status_code != 200:
            return quiz_data, status_code
        category_name = quiz_data["category"]
        quiz_id = quiz_data["quiz_id"]
        questions = quiz_data["questions"]
        save_status = self.save_quiz(quiz_id,category_name,questions,int(amount),difficulty,type_of_questions)
        if not save_status:
            return {"error":"Failed to save quiz"},500
        
        lobby_id = self.generate_ID()
        if Lobby.query.filter_by(lobby_id=lobby_id):
            print("Lobby_id already exist")
            lobby_id = self.generate_ID()
        host_username = data.get("host_username")
        lobby_name = data.get("lobby_name")
        max_players = data.get("max_players")
        isOpen = data.get("isOpen",True)
        password = data.get("password",None)
        created_at = datetime.datetime.utcnow()
        try:
            new_lobby = Lobby(
                lobby_id=str(lobby_id),
                host_username=host_username,
                lobby_name = lobby_name,
                max_players=max_players,
                players=[host_username],
                category=category_name,
                isOpen=isOpen,
                status="waiting",
                created_at=created_at,
                quiz_id=str(quiz_id)
            )
            new_lobby.set_password(password)
            quiz_participant = QuizParticipant(
                quiz_id = str(quiz_id),
                username = host_username
            )
            db.session.add(new_lobby,quiz_participant)
            db.session.commit()
            return {"message":"Lobby created successfully","data":{
                "lobby_id": str(lobby_id),
                "host_username": host_username,
                "lobby_name": lobby_name,
                "max_players": max_players,
                "players": [host_username],
                "category": category_name,
                "isOpen": isOpen,
                "status": "waiting",
                "created_at": created_at.isoformat(),
                "quiz_id": str(quiz_id)
            }},201
        except Exception as e:
            print(f"Error creating lobby: {str(e)}")
            db.session.rollback()
            return {"error":"Failed to create lobby"},500
    