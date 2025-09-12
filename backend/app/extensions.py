from flask_cors import CORS
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")
cors = CORS()
swagger = Swagger()
jwt = JWTManager()