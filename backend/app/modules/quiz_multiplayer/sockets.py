from app.db.db import db
from app.db.models import Lobby, Quiz, QuizParticipant
from app.extensions import socketio
from flask_socketio import emit,join_room,leave_room,romms

@socketio.on('join_lobby')
def handle_join_lobby(data):
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.querry.filter_by(lobby_id=lobby_id).first()

    if not lobby or not username:
        emit('error', {'message': 'Invalid data'})
        return
    
    if lobby.status != "waiting":
        emit('error', {'message': 'Cannot join, game already started'})
        return
    
    if username in lobby.players:
        emit('error', {'message': 'User already in lobby'})
        return
    
    if len(lobby.players)>=lobby.max_players:
        emit('error', {'message': 'Lobby is full'})
        return
    
    password = data.get("password",None)
    if not lobby.isOpen and lobby.check_password(password) is False:
        emit('error', {'message': 'Incorrect password'})
        return
    
    lobby.players.append(username)
    db.session.commit()

    quiz_participant = QuizParticipant(
        quiz_id = lobby.quiz_id,
        username = username
    )
    db.session.add(quiz_participant)
    db.session.commit()

    join_room(lobby_id)
    emit('user_joined', {'username': username}, room=lobby_id)
    print(f"User {username} joined lobby {lobby_id}")

@socketio.on('leave_lobby')
def handle_leave_lobby(data):
    lobby__id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.querry.filter_by(lobby_id=lobby__id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    if username not in lobby.players:
        emit('error', {'message': 'User not in lobby'})
        return
    lobby.players.remove(username)
    db.session.commit()
    leave_room(lobby__id)
    emit('user_left', {'username': username}, room=lobby__id)
    if len(lobby.players)==0:
        db.session.delete(lobby)
        db.session.commit()

@socketio.on('delete_lobby')
def handle_delete_lobby(data):
    lobby_id = data.get("lobby_id")
    lobby = Lobby.querry.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    username = data.get("username")
    if lobby.host_username != username:
        emit('error', {'message': 'Only host can delete the lobby'})
        return
    emit('lobby_deleted', {'lobby_id': lobby_id}, room=lobby_id)
    emit('lobby_deleted', {'lobby_id': lobby_id}, broadcast=True)
    for user in lobby.players:
        leave_room(lobby_id)
    # Notify all users in the lobby that it has been deleted
    db.session.delete(lobby)
    db.session.commit()

@socketio.on('start_quiz')
def handle_start_quiz(data):
    lobby_id = data.get("lobby_id")
    lobby = Lobby.querry.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    username = data.get("username")
    if lobby.host_name != username:
        emit('error',{'message':'Onyl host can delete the lobby'})
        return
    lobby.status = "in_game"

    emit('quiz_started', {'lobby_id': lobby_id}, room=lobby_id)
    # Notify all users in the lobby that the quiz has started

@socketio.on('submit_answer')
def handle_submit_answer(data):
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.querry.filter_by(lobby_id=lobby_id).first()

    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    
    if username not in lobby.players:
        emit('error', {'message': 'User not in lobby'})
        return
    
    if lobby.status != "in_game":
        emit('error', {'message': 'Quiz not in progress'})
        return
    
    quiz_participant = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id,username=username).first()
    if not quiz_participant:
        emit('error', {'message': 'Participant record not found'})
        return
    
    answer = data.get("answer")
    current_question_index = quiz_participant.current_question
    quiz = Quiz.query.filter_by(quiz_id=lobby.quiz_id).first()

    if not quiz or current_question_index >= len(quiz.questions):
        emit("error",{"message":"Invalid quiz or question index"})
        return
    
    current_question = quiz.questions[current_question_index]
    correct_answer = current_question['correct_answer']

    if correct_answer==answer:
        quiz_participant.score += 1

    quiz_participant.answers.append(answer)
    quiz_participant.current_question += 1
    db.session.commit()

    emit('answer_submitted',{
        'username': username,
        'correct': correct_answer==answer,
        'current_question': quiz_participant.current_question - 1,
        'score': quiz_participant.score
    },room=lobby_id)

@socketio.on('next_question')
def handle_next_question(data):
    lobby_id = data.get("lobby_id")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    
    quiz = Quiz.query.filter_by(quiz_id=lobby.quiz_id).first()
    if not quiz:
        emit('error', {'message': 'Quiz not found'})
        return
    
    current_question_index = data.get('current_question_index')
    if current_question_index is None or current_question_index < 0 or current_question_index >= len(quiz.questions):
        emit('error', {'message': 'Invalid question index'})
        return
    
    question = quiz.questions[current_question_index]
    emit('new_question', {
        'question_index':current_question_index,
        "question":question["question"],
        "choices":question["choices"]
    },room=lobby_id)

@socketio.on('end_quiz')
def handle_end_quiz(data):
    lobby_id = data.get('lobby_id')
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    if lobby.status != "in_game":
        emit('error', {'message': 'Quiz not in progress'})
        return

    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    scores = [{"username":p.username,"score":p.score} for p in participants]

    emit('game_ended',{'scores':scores},room=lobby_id)

    db.session.delete(lobby)
    db.session.commit()

def generate_lobby_id():
    import uuid
    return str(uuid.uuid4())
