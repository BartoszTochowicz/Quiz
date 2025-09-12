import threading
from app.db.db import db
from app.db.models import TokenBlocklist
from flask import Flask, jsonify
from app.extensions import cors, jwt, swagger


def initialize_db(app: Flask):
    with app.app_context():
        db.init_app(app)
        db.create_all()

def initialize_route(app: Flask):
    from app.modules.auth.route import auth_bp
    from app.modules.quiz_singleplayer.route import singlePlayer_bp
    from app.modules.quiz_multiplayer.route import multiplayer_bp
    app.register_blueprint(auth_bp,url_prefix='/api/v1/auth')
    app.register_blueprint(singlePlayer_bp,url_prefix = '/api/v1/singleplayer')
    app.register_blueprint(multiplayer_bp,url_prefix = '/api/v1/multiplayer')

def initialize_swagger(app:Flask):
    with app.app_context():
        swagger.init_app(app=app)
        return swagger
def initialize_cors(app: Flask):
    with app.app_context():
        cors.init_app(app,supports_credentials=True, origins=['*'])

def initialize_jwt(app: Flask):
    with app.app_context():
        from app.db.models import User
        jwt.init_app(app)

        @jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header,jwt_data):
            identity = jwt_data["sub"]
            return User.query.filter_by(id=identity).one_or_none()
        @jwt.expired_token_loader
        def expierd_token_callback(jwt_header, jwt_payload):
            return jsonify({
                'message' : 'Token has expierd. Please log in again.',
                'error': 'token_expired'
            }), 401
        return jwt
def initialize_blocklist_cleanup(app: Flask):
    import schedule, time
    from datetime import datetime, timedelta, timezone
    from threading import Event

    # Event used to signal the scheduler thread to stop
    stop_event = Event()

    # Deletes entries from the blocklist model that are older than the expiration_time
    def delete_expired_entries(session, model, expiration_time):
        expired = datetime.now(timezone(timedelta(hours=2))) - expiration_time
        session.query(model).filter(model.created_at < expired).delete()
        session.commit()
    
    # Scheduler thread function: runs the cleanup job every 10 minutes
    def run_scheduler():
        with app.app_context():
            # Schedule the cleanup job every 10 minutes
            schedule.every(10).minutes.do(
                delete_expired_entries,
                session=db.session, 
                model=TokenBlocklist,
                expiration_time=app.config['JWT_REFRESH_TOKEN_EXPIRES']
            )
            # Loop to keep the scheduler running and check for stop_event
            while not stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)

    # Start the scheduler in a background daemon thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Function to stop the scheduler thread gracefully
    def stop_scheduler():
        stop_event.set()
        scheduler_thread.join()
    # Attach the stop function to the app for later use (e.g. on shutdown)
    app.stop_scheduler = stop_scheduler
def initialize_socketio(app: Flask):
    from app.extensions import socketio
    with app.app_context():
        socketio.init_app(app)
        return socketio