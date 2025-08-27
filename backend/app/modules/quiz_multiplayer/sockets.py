from app.extensions import socketio
from flask_socketio import emit,join_room,leave_room,romms

@socketio.on('join_lobby')
def handle_join_lobby(data):
    lobby__id = data.get("lobby_id")
    username = data.get("username")