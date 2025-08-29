from flask_cors import CORS
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
cors = CORS()
swagger = Swagger()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins='*')