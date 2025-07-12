import requests
from flask import current_app


def fetch_quiz(self,request):
    amount = request.get('amount')
    category = request.get('category')
    difficulty = request.get('difficulty')
    type_of_questions = request.get('type_of_questions')
    encode = 'base64'
    quiz = requests.get(f'https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={type_of_questions}&encode={encode}')
