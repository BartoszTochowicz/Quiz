import socketio
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('connected to server')

@sio.on('disconnect')
def on_disconnect():
    print("disconnected from server")

try:
    sio.connect('http://localhost:5000', wait_timeout=10)  # Dodaj timeout
    sio.emit('join_lobby', {'lobby_id': '1', 'username': 'skibidi'})
    sio.wait()
except socketio.exceptions.ConnectionError as e:
    print("Connection failed:", e)