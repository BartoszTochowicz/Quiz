import requests
from flask import current_app

def fetch_quiz_questions(category="Linux", limit=5):
    api_key = current_app.config['QUIZ_API_KEY']
    url = f"https://quizapi.io/api/v1/questions?category={category}&limit={limit}"
    headers = {'X-Api-Key': api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()