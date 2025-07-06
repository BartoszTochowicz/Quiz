import os
from dotenv import load_dotenv
from app.app import create_app
from werkzeug.serving import WSGIRequestHandler
from app.extensions import socketio


load_dotenv()
config=os.getenv('FLASK_ENV') or 'development'
app = create_app(config)

class CustomRequestHandler(WSGIRequestHandler):
    def log_request(self, code='-', size='-'):
        if self.path.startswith('/flasgger_static') or self.path.startswith('/apidocs') or self.path.startswith('/apispec_1.json'):
            return  # Ignore logging for requests with the specified prefix
        super().log_request(code, size)

if __name__ == "__main__":
    if config == 'development':
        # app.run(debug=True, request_handler=CustomRequestHandler)
        socketio.run(app, debug=True, request_handler=CustomRequestHandler)
    else:
        from werkzeug.serving import run_simple
        run_simple('0.0.0.0', 5000, app)