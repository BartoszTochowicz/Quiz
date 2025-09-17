import time
from datetime import datetime, timedelta
from app.db.db import db
from app.db.models import Lobby, Quiz, QuizParticipant
from app.extensions import socketio
from flask_socketio import emit,join_room,leave_room
from flask import current_app, request
from requests import get
from app.modules.quiz_multiplayer.controller import QuizMultiplayerController

quizMultiplayerController = QuizMultiplayerController()

# maps
sid_to_username = {} # sid -> username
username_to_sids = {} # username -> [sid, sid, ...]

# How long user can refresh/reconnect without being removed (seconds)
GRACE_PERIOD_SECONDS = 30

def schedule_remove_if_offline(username):
    app = current_app._get_current_object()
    socketio.start_background_task(_remove_if_offline,username,app)

def _remove_if_offline(username,app):
    """
    Wait GRACE_PERIOD_SECONDS, check if user is still offline
    If yes -> delete him from lobby and delete QuizParticipant record
    """
    
    time.sleep(GRACE_PERIOD_SECONDS)
    with app.app_context():
        quiz_participant = QuizParticipant.query.filter_by(username=username).first()
        if not quiz_participant:
            return # Already deleted or never existed
        
        if quiz_participant.status == "online":
            return
        timestamp_of_disconnection = quiz_participant.timestamp_of_disconnection
        if not timestamp_of_disconnection :
            return
        
        # delta = datetime.utcnow() - quiz_participant.time_of_disconnect

        if not quiz_participant.checkTimeStamp(timestamp_of_disconnection,GRACE_PERIOD_SECONDS):
            return
        
        lobby = Lobby.query.filter_by(quiz_id=quiz_participant.quiz_id).first()

        try:
            if lobby and quiz_participant.username:
                lobby.current_players = max(lobby.current_players-1,0)

            db.session.delete(quiz_participant)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Error cleaning up offline participant: ",e)
            return
        
        if lobby:
            emit_lobby_updated(lobby)
            socketio.emit('player_left', {'username': username, 'player_left': lobby.current_players},room=lobby.lobby_id)
            participant = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).first()
            if not participant:
                try:
                    db.session.delete(lobby)
                    db.session.commit()
                    socketio.emit('lobby_deleted', {'lobby_id':lobby.lobby_id}, room=lobby.lobby_id)
                except Exception as e:
                    db.session.rollback()
                    print("DB error deleting empty lobby after offline cleanup:", e)


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
    
    user_info = validation.json()
    username = user_info.get('username')
    user_sid = request.sid

    sid_to_username[user_sid] = username
    username_to_sids.setdefault(username, []).append(user_sid)

    print('Client connected: ',user_info)

    quiz_participant = QuizParticipant.query.filter_by(username=username).first()
    if not quiz_participant:
        return
    try:
        now = datetime.utcnow()
        if quiz_participant.status == "offline" and not quiz_participant.checkTimeStamp(now):
            quiz_participant.mark_reconnected()
            db.session.commit()

            lobby = Lobby.query.filter_by(quiz_id=quiz_participant.quiz_id).first()
            if lobby:
                join_room(lobby.lobby_id)
                emit_lobby_updated(lobby)
                socketio.emit('player_reconnected', {'username':username}, room=lobby.lobby_id)
    except Exception as e:
        db.session.rollback()
        print("Error handling reconnection:", e)
    emit('auth_success', {'data':'Connected successfully!'})

@socketio.on('disconnect')
def handle_disconnect():
    user_sid = request.sid
    username = sid_to_username.pop(user_sid, None)

    print("Disconnecting user:", username)

    if not username:
        print("Username not in the lobby")
        return
    
    user_sids = username_to_sids.get(username, [])
    if user_sid in user_sids:
        user_sids.remove(user_sid)
    if user_sids:
        username_to_sids[username] = user_sids
        print('User still has active SIDs, not marking offline:', username, username_to_sids[username])
        return
    else:
        username_to_sids.pop(username,None)
    
    quiz_participant = QuizParticipant.query.filter_by(username=username).first()
    if not quiz_participant:
        print("No QuizParticipant record for",username)
        return
    
    lobby = Lobby.query.filter_by(quiz_id=quiz_participant.quiz_id).first()
    
    try:
        quiz_participant.mark_disconnected()
        db.session.commit()
        print(f"Marked participant offline: {username} at {quiz_participant.timestamp_of_disconnection}")
    except Exception as e:
        db.session.rollback()
        print("DB error marking participant offline:", e)
        return
    
    # Dont delete user from lobby at once
    # Start task in background which will delete user after GRACE_PERIOD_SECONDS 
    # socketio.start_background_task(schedule_remove_if_offline,sid_to_username)
    schedule_remove_if_offline(username=username)

@socketio.on('create_lobby')
def handle_create_lobby(data):
    print("create_lobby data:", data)
    result, status = quizMultiplayerController.create_lobby(data)
    if status != 201:
        emit('error', {'message': result.get('error', 'Failed to create lobby')}, room=request.sid)
        return
    
    user_sid = request.sid
    host_username = data.get("host_username")
    sid_to_username[user_sid] = host_username
    username_to_sids.setdefault(host_username,[]).append(user_sid)

    lobby_id = result['data']['lobby_id']
    join_room(lobby_id)


    emit('lobby_created', result)

@socketio.on('join_lobby')
def handle_join_lobby(data):
    print("join_lobby data:", data)
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()

    if not lobby or not username:
        print("Lobby not found or username missing")
        emit('error', {'message': 'Invalid data'},room=request.sid)
        return

    if lobby.status != "waiting":
        print("Cannot join, game already started")
        emit('error', {'message': 'Cannot join, game already started'},room=request.sid)
        return
    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    print('participants: ', [p.username for p in participants])

    if any(p.username == username for p in participants):
        print("User already in lobby")
        emit('error', {'message': 'User already in lobby'},room=request.sid)
        return

    if lobby.current_players >= lobby.max_players:
        print("Lobby is full")
        emit('error', {'message': 'Lobby is full'},room=request.sid)
        return

    password = data.get("password", None)
    if (not lobby.isOpen) and (lobby.check_password(password) is False):
        print("Incorrect password for private lobby")
        emit('error', {'message': 'Incorrect password'},room=request.sid)
        return

    # Add player, commit first (so DB is consistent)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB commit error when adding player:", e)
        emit('error', {'message': 'Internal server error'},room=request.sid)
        return

    quiz_participant = QuizParticipant(
        quiz_id=lobby.quiz_id,
        username=username
    )
    db.session.add(quiz_participant)
    lobby.current_players += 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB commit error when creating participant:", e)
        emit('error', {'message': 'Internal server error'},room=request.sid)
        return

    join_room(lobby_id)

    user_sid = request.sid
    if not sid_to_username.get(user_sid):
        sid_to_username[user_sid] = username
    username_to_sids.setdefault(username,[]).append(user_sid)
    
    emit('player_joined', {'username': username,'lobby_id':lobby_id}, room=lobby_id)
    emit_lobby_updated(lobby)
    print(f"User {username} joined lobby {lobby.lobby_name}")

@socketio.on('leave_lobby')
def handle_leave_lobby(data):
    print("leave lobby data:", data)
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()

    if not lobby:
        print("Lobby not found")
        emit('error', {'message': 'Lobby not found'},room=request.sid)
        return
    
    quiz_participant = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id,username=username).first()
    if not quiz_participant:
        print("User not found in Lobby")
        emit('error', {'message': 'User not in lobby'},room=request.sid)
        return
    
    db.session.delete(quiz_participant)
    lobby.current_players = max(0, lobby.current_players - 1)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB commit error when removing player:", e)
        emit('error', {'message': 'Internal server error'},room=request.sid)
        return

    # leave_room(lobby_id)

    user_sid = request.sid
    if sid_to_username.get(user_sid):
        sid_to_username.pop(user_sid)
    user_sids = username_to_sids.get(username,[])
    if user_sid in user_sids:
        user_sids.remove(user_sid)
        if user_sids:
            username_to_sids[username]=user_sids
        else:
            username_to_sids.pop(username,None)


    emit_lobby_updated(lobby)
    # leave_room(lobby_id)
    emit('player_left', {'username': username}, room=lobby_id)
    print(f"User {username} left lobby {lobby.lobby_name}")
    
    participant = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).first()
    if not participant:
        try:
            db.session.delete(lobby)
            db.session.commit()
            emit('lobby_deleted', {'lobby_id': lobby.lobby_id}, room=lobby.lobby_id)
        except Exception as e:
            db.session.rollback()
            print("DB error deleting lobby after last left:", e)
            emit('error', {'message': 'Internal server error'},room=request.sid)
            return
    leave_room(lobby_id)

@socketio.on('delete_lobby')
def handle_delete_lobby(data):
    print("delete_lobby data:", data)
    lobby_id = data.get("lobby_id")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'},room=request.sid)
        return
    username = data.get("username")
    if lobby.host_username != username:
        emit('error', {'message': 'Only host can delete the lobby'},room=request.sid)
        return

    emit('lobby_deleted', {'lobby_id': lobby_id}, room=lobby_id)
    # emit('lobby_deleted', {'lobby_id': lobby_id}, broadcast=True)
    try:
        db.session.delete(lobby)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB error deleting lobby:", e)
        emit('error', {'message': 'Internal server error'},room=request.sid)
        return

@socketio.on('get_lobby_details')
def handle_get_lobby_details(data):
    print("get_lobby_details data:", data)
    lobby_id = data.get('lobby_id')
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'},room=request.sid)
        return
    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    usernames = [p.username for p in participants]

    lobby_data = {
        'lobby_id': lobby.lobby_id,
        'lobby_name': lobby.lobby_name,
        'host_username': lobby.host_username,
        'max_players': lobby.max_players,
        'current_players': len(usernames),
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
            'current_players': lobby.current_players,
            'isOpen': lobby.isOpen,
            'status': lobby.status
        })
    emit('lobbies_listed', {'lobbies': lobbies_data}, broadcast=True)

@socketio.on('start_quiz')
def handle_start_quiz(data):
    lobby_id = data.get("lobby_id")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'},room=request.sid)
        return
    username = data.get("username")
    if lobby.host_username != username:
        emit('error', {'message': 'Only host can start the quiz'},room=request.sid)
        return
    
    lobby.status = "in_game"
    quiz = Quiz.query.filter_by(quiz_id=lobby.quiz_id).first()

    print(quiz.questions)

    questions = [
        {k: v for k,v in question.items() if k != 'correct_answer'}
        for question in quiz.questions
    ]

    quiz_data = {
        "quiz_id": quiz.quiz_id,
        "category": quiz.category,
        "questions": questions,
        "total_questions": quiz.total_questions,
    }
    emit('quiz_started', {'lobby_id': lobby_id, 'quiz_data':quiz_data,'category':lobby.category}, room=lobby_id)

    try: 
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        emit('error', {'message': 'Internal server error'},room=request.sid)
        return

@socketio.on('submit_answer')
def handle_submit_answer(data):
    lobby_id = data.get("lobby_id")
    username = data.get("username")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()

    if not lobby:
        emit('error', {'message': 'Lobby not found'},room=request.sid)
        return
    
    if lobby.status != "in_game":
        emit('error', {'message': 'Quiz not in progress'},room=request.sid)
        return
    
    quiz_participant = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id,username=username).first()
    if not quiz_participant:
        emit('error', {'message': 'Participant record not found'},room=request.sid)
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
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     emit('error', {'message': 'Internal server error'},room=request.sid)
    #     return

    emit('answer_submited', {
        'username': username,
        'correct': correct_answer == answer,
        'current_question': quiz_participant.current_question - 1,
        'score': quiz_participant.score
    }, room=lobby_id)

    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    all_answered = all(p.current_question > current_question_index for p in participants)

    if all_answered:
        scores = [{"username": p.username, "score":p.score }for p in participants]
        socketio.emit("show_scores",{"scores": scores}, room=lobby_id)

        def send_next():
            next_index = current_question_index+1
            if next_index < len(quiz.questions):
                q = quiz.questions[next_index]
                socketio.emit('next_question',{
                    "question_index": next_index,
                    "question": q['question'],
                    "choices": q['choices']
                }, room=lobby_id)
            else:
                socketio.emit('quiz_ended',{'scores':scores},room=lobby_id)
        socketio.start_background_task(lambda: (time.sleep(5), send_next()))

@socketio.on('next_question')
def handle_next_question(data):
    lobby_id = data.get("lobby_id")
    lobby = Lobby.query.filter_by(lobby_id=lobby_id).first()
    if not lobby:
        emit('error', {'message': 'Lobby not found'},room=request.sid)
        return
    
    quiz = Quiz.query.filter_by(quiz_id=lobby.quiz_id).first()
    if not quiz:
        emit('error', {'message': 'Quiz not found'},room=request.sid)
        return
    
    current_question_index = data.get('current_question_index')
    if current_question_index is None or current_question_index < 0 or current_question_index >= len(quiz.questions):
        emit('error', {'message': 'Invalid question index'},room=request.sid)
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
        emit('error', {'message': 'Lobby not found'},room=request.sid)
        return
    if lobby.status != "in_game":
        emit('error', {'message': 'Quiz not in progress'},room=request.sid)
        return

    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    scores = [{"username": p.username, "score": p.score} for p in participants]

    emit('quiz_ended', {'scores': scores}, room=lobby_id)
    try:
        # db.session.delete(lobby)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        emit('error', {'message': 'Internal server error'},room=request.sid)
        return
def generate_lobby_id():
    import uuid
    return str(uuid.uuid4())

def emit_lobby_updated(lobby):
    participants = QuizParticipant.query.filter_by(quiz_id=lobby.quiz_id).all()
    usernames = [p.username for p in participants]
    lobby_data = {
        'lobby_id': lobby.lobby_id,
        'lobby_name': lobby.lobby_name,
        'host_username': lobby.host_username,
        'max_players': lobby.max_players,
        'current_players': lobby.current_players,
        'players': usernames,
        'status': lobby.status
    }
    print("Players in lobby:", usernames)
    socketio.emit('lobby_updated', lobby_data, room=lobby.lobby_id)