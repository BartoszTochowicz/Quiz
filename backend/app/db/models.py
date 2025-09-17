from datetime import timedelta,datetime
from uuid import uuid4
from app.extensions import jwt
from app.db.db import db
from sqlalchemy.orm import mapped_column
import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    __tablename__ = 'user'
    id = mapped_column(sa.String(),primary_key=True, default=lambda:str(uuid4()))
    email = mapped_column(sa.String(255),unique=True,nullable=False)
    username = mapped_column(sa.String(255),unique=True,nullable=False)
    password = mapped_column(sa.String(255),nullable=False)

    def check_password(self,password):
        return check_password_hash(self.password,password)
    def set_password(self,password):
        self.password = generate_password_hash(password=password)
        
    @classmethod
    def get_by_username(cls,username):
        return cls.query.filter_by(username=username).first()
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

class Quiz(db.Model):
    __tablename__ = "quiz"
    quiz_id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    questions = db.Column(db.JSON, nullable=False, default=[])  # List of question IDs or question dicts
    total_questions = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    type_of_questions = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def increase_score(self,score):
        self.score += score
    def add_question_to_total(self,question):
        self.total_questions += question

class Lobby(db.Model):
    __tablename__ = "lobby"
    lobby_id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    lobby_name = db.Column(db.String(255),nullable = False)
    host_username = db.Column(db.String(255), nullable=False)
    max_players = db.Column(db.Integer, nullable=False)
    current_players = db.Column(db.Integer, nullable=False, default=0) # Current players in lobby
    category = db.Column(db.String(255), nullable=False)
    isOpen = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(db.String(50), nullable=False)  # waiting, in_game, finished
    password = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    quiz_id = db.Column(db.String(255), nullable=True)  # Associated quiz ID
    
    def check_password(self,password):
        return check_password_hash(self.password,password)
    def set_password(self,password):
        self.password = generate_password_hash(password=password)

class QuizParticipant(db.Model):
    __tablename__ = "quiz_participant"
    id = db.Column(db.Integer,primary_key=True)
    quiz_id = db.Column(db.String(255),db.ForeignKey('quiz.quiz_id'),nullable=False)
    username = db.Column(db.String(255),nullable=False)
    score = db.Column(db.Integer,nullable=False, default=0)
    current_question = db.Column(db.Integer,nullable=False, default=0)
    answers = db.Column(db.PickleType, nullable=False, default=list)  # List of answers given by the participant
    status = db.Column(db.String(255),nullable=False, default="online") # Thoose two parameters are used to prevent  
    timestamp_of_disconnection = db.Column(db.DateTime,nullable=True) # from kicking participant from Lobby

    def toString(self):
        return f"QuizParticipant(quiz_id={self.quiz_id}, username={self.username}, score={self.score}, current_question={self.current_question}, answers={self.answers})"
    
    def mark_disconnected(self):
        # Sets status to offline and saves timestamp of disconnection
        self.status = "offline"
        self.timestamp_of_disconnection = datetime.utcnow()
    
    def mark_reconnected(self):
        """ Sets status to online """
        self.status = "online"
        self.timestamp_of_disconnection = None
    def checkTimeStamp(self, timestamp_of_reconnection, grace_period_seconds = 30):
        """
        Checks, if player reconnected in time.
        Returns True if player exceeded time limit and player can be removed
        """
        if not self.timestamp_of_disconnection:
            return False
        delta = timestamp_of_reconnection - self.timestamp_of_disconnection
        
        return delta > timedelta(seconds=grace_period_seconds)