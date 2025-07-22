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

class QuizSinglePlayer(db.Model):
    __tablename__ = "quiz_singlePlayer"
    quiz_id = mapped_column(sa.String(255),primary_key=True,unique=True,nullable=False)
    username = mapped_column(sa.String(255),nullable=False)
    category = mapped_column(sa.String(255),nullable=False)
    score = mapped_column(db.Integer,nullable=False)
    total_questions = mapped_column(db.Integer,nullable=False)
    timestamp = mapped_column(db.DateTime, nullable=False)

    def increase_score(self,score):
        self.score += score
    def add_question_to_total(self,question):
        self.total_questions += question