from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash
import os

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    # Get the directory of this file
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///classroom.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page'
    socketio.init_app(app, cors_allowed_origins="*")
    
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from .routes import main, auth, courses, activities
    from . import socket_events  # Import socket events
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(courses.bp)
    app.register_blueprint(activities.bp)
    
    with app.app_context():
        db.create_all()
        
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                name='Administrator'
            )
            db.session.add(admin)
            db.session.commit()
    
    return app
