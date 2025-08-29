import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('connected to server')

@sio.on('disconnect')
def on_disconnect():
    print("disconnected from server")

sio.connect('http://localhost:5000')

sio.emit('join_lobby', {'lobby_id':'1','username':'skibidi'})

sio.wait()