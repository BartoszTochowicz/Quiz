from app.db.db import db
from app.db.models import Lobby, Quiz, QuizParticipant
from app.extensions import socketio
from flask_socketio import emit,join_room,leave_room
from flask import request
from requests import get
from app.modules.quiz_multiplayer.controller import QuizMultiplayerController

quizMultiplayerController = QuizMultiplayerController()

# Mapping of socket IDs to usernames for tracking connected users
sid_to_username = {}

@socketio.on('connect')
def test_connect(auth):
    print('Connection attempt with auth:', auth)
    validation = get(request.url_root + 'api/v1/auth/login', headers={"Authorization" : f"Bearer {auth['token']}"})
    if validation.status_code == 200:
        print('Client connected:', validation.json())
        emit('auth_success', {'data': 'Connected successfully!'})
    else:
        print('Connection failed:', validation.json())
        raise ConnectionRefusedError('auth_fail')


@socketio.on('disconnect')
def handle_disconnect():

    print('Disconnecting handler')
    username = sid_to_username.get(request.sid)
    print("Disconnecting user:", username)
    if not username:
        print("Username not in the lobby")
        return

    quizParticipant = QuizParticipant.query.filter_by(username=username).first()
    if quizParticipant:
        lobby = Lobby.query.filter_by(quiz_id=quizParticipant.quiz_id).first()
        if lobby and username in lobby.players:
            lobby.players.remove(username)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("DB commit error when removing player on disconnect:", e)
                return

            emit('player_left', {'username': username, 'players_left': len(lobby.players)}, room=lobby.lobby_id)
            if len(lobby.players) == 0:
                try:
                    db.session.delete(lobby)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print("DB error deleting empty lobby:", e)
                    return
                emit('lobby_deleted', {'lobby_id': lobby.lobby_id}, broadcast=True)

        try:
            db.session.delete(quizParticipant)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error removing participant on disconnect:', e)

@socketio.on('create_lobby')
def handle_create_lobby(data):
    print("create_lobby data:", data)
    result, status = quizMultiplayerController.create_lobby(data)
    if status != 201:
        emit('error', {'message': result.get('error', 'Failed to create lobby')})
        return
    user_id = request.sid
    sid_to_username[user_id] = data.get("host_username")
    emit('lobby_created', result)

@socketio.on('join_lobby')
def handle_join_lobby(data):
    print("join_lobby data:", data)
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()

    if not lobby or not username:
        print("Lobby not found or username missing")
        emit('error', {'message': 'Invalid data'})
        return

    if lobby.status != "waiting":
        print("Cannot join, game already started")
        emit('error', {'message': 'Cannot join, game already started'})
        return

    if username in lobby.players:
        print("User already in lobby")
        emit('error', {'message': 'User already in lobby'})
        return

    if len(lobby.players) >= lobby.max_players:
        print("Lobby is full")
        emit('error', {'message': 'Lobby is full'})
        return

    password = data.get("password", None)
    if (not lobby.isOpen) and (lobby.check_password(password) is False):
        print("Incorrect password for private lobby")
        emit('error', {'message': 'Incorrect password'})
        return

    # Add player, commit first (so DB is consistent)
    lobby.players.append(username)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB commit error when adding player:", e)
        emit('error', {'message': 'Internal server error'})
        return

    quiz_participant = QuizParticipant(
        quiz_id=lobby.quiz_id,
        username=username
    )
    db.session.add(quiz_participant)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB commit error when creating participant:", e)
        emit('error', {'message': 'Internal server error'})
        return

    join_room(lobby_id)

    user_id = request.sid
    if not sid_to_username.get(user_id):
        sid_to_username[user_id] = username
    
    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    usernames = [p.username for p in participants]
    emit('player_joined', {'username': username,'lobby_id':lobby_id}, room=lobby_id)
    emit('lobby_updated', {'users': usernames}, room=lobby_id)
    print(f"User {username} joined lobby {lobby.lobby_name}")
    print("Players in lobby:", usernames)

@socketio.on('leave_lobby')
def handle_leave_lobby(data):
    print("leave lobby data:", data)
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        print("Lobby not found")
        emit('error', {'message': 'Lobby not found'})
        return
    if username not in lobby.players:
        print("User not found in Lobby: ", lobby.players)
        emit('error', {'message': 'User not in lobby'})
        return
    
    quiz_participant = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id,username=username).first()
    if not quiz_participant:
        print("Participant record not found")
        emit('error', {'message': 'Participant record not found'})
        return
    
    print("players before removal:", lobby.players)
    lobby.players.remove(username)
    db.session.delete(quiz_participant)
    print("players after removal:", lobby.players)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB commit error when removing player:", e)
        emit('error', {'message': 'Internal server error'})
        return

    leave_room(lobby_id)

    user_id = request.sid
    if sid_to_username.get(user_id):
        sid_to_username.pop(user_id)

    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    usernames = [p.username for p in participants]
    emit('lobby_updated', {'users': usernames}, room=lobby_id)
    emit('player_left', {'username': username}, room=lobby_id)
    print(f"User {username} left lobby {lobby.lobby_name}")
    print("Players left in lobby:", usernames)
    if len(lobby.players) == 0:
        try:
            db.session.delete(lobby)
            db.session.commit()
            emit('lobby_deleted', {'lobby_id': lobby.lobby_id}, broadcast=True)
        except Exception as e:
            db.session.rollback()
            print("DB error deleting lobby after last left:", e)
            emit('error', {'message': 'Internal server error'})
            return

@socketio.on('delete_lobby')
def handle_delete_lobby(data):
    print("delete_lobby data:", data)
    lobby_id = data.get("lobby_id")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    username = data.get("username")
    if lobby.host_username != username:
        emit('error', {'message': 'Only host can delete the lobby'})
        return

    emit('lobby_deleted', {'lobby_id': lobby_id}, room=lobby_id)
    emit('lobby_deleted', {'lobby_id': lobby_id}, broadcast=True)
    try:
        db.session.delete(lobby)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB error deleting lobby:", e)
        emit('error', {'message': 'Internal server error'})
        return

@socketio.on('get_lobby_details')
def handle_get_lobby_details(data):
    print("get_lobby_details data:", data)
    lobby_id = data.get('lobby_id')
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    usernames = [p.username for p in participants]

    lobby_data = {
        'lobby_id': lobby.lobby_id,
        'lobby_name': lobby.lobby_name,
        'host_username': lobby.host_username,
        'max_players': lobby.max_players,
        'current_players': len(lobby.players),
        'players': usernames
    }
    print("lobby details:", lobby_data)
    emit('lobby_details', lobby_data)

@socketio.on('list_lobbies')
def handle_list_lobbies(data=None):
    print("list_lobbies called")
    lobbies = Lobby.query.all()
    lobbies_data = []
    for lobby in lobbies:
        lobbies_data.append({
            'lobby_id': lobby.lobby_id,
            'lobby_name': lobby.lobby_name,
            'host_username': lobby.host_username,
            'max_players': lobby.max_players,
            'current_players': len(lobby.players),
            'isOpen': lobby.isOpen,
            'status': lobby.status
        })
    emit('lobbies_listed', {'lobbies': lobbies_data}, broadcast=True)

@socketio.on('start_quiz')
def handle_start_quiz(data):
    lobby_id = data.get("lobby_id")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    username = data.get("username")
    if lobby.host_username != username:
        emit('error', {'message': 'Only host can start the quiz'})
        return
    lobby.status = "in_game"

    emit('quiz_started', {'lobby_id': lobby_id}, room=lobby_id)

@socketio.on('submit_answer')
def handle_submit_answer(data):
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()

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
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        emit('error', {'message': 'Internal server error'})
        return

    emit('answer_submited', {
        'username': username,
        'correct': correct_answer == answer,
        'current_question': quiz_participant.current_question - 1,
        'score': quiz_participant.score
    }, room=lobby_id)

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
    emit('next_question', {
        'question_index': current_question_index,
        "question": question["question"],
        "choices": question["choices"]
    }, room=lobby_id)

@socketio.on('end_quiz')
def handle_end_quiz(data):
    print("end_quiz data:", data)
    lobby_id = data.get('lobby_id')
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'})
        return
    if lobby.status != "in_game":
        emit('error', {'message': 'Quiz not in progress'})
        return

    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    scores = [{"username": p.username, "score": p.score} for p in participants]

    emit('quiz_ended', {'scores': scores}, room=lobby_id)
    try:
        db.session.delete(lobby)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        emit('error', {'message': 'Internal server error'})
        return
def generate_lobby_id():
    import uuid
    return str(uuid.uuid4())
