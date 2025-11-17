"""
Q&A Education Platform - Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail
from werkzeug.security import generate_password_hash
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Initialize SocketIO with threading mode for Python 3.12+ compatibility
# This avoids eventlet SSL issues with Python 3.12+
import sys
if sys.version_info >= (3, 12):
    socketio = SocketIO(async_mode='threading')
else:
    socketio = SocketIO()  # Auto-detect for older Python versions

mail = Mail()

# Timezone utility - Beijing Time (UTC+8)
def get_beijing_time():
    """Get current Beijing time (UTC+8)"""
    return datetime.utcnow() + timedelta(hours=8)

def create_app():
    """Application factory pattern"""
    
    # Create Flask app with correct template directory
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MySQL Database Configuration
    HOSTNAME = os.getenv('MYSQL_HOST', '127.0.0.1')
    PORT = os.getenv('MYSQL_PORT', '3307')
    USERNAME = os.getenv('MYSQL_USER', 'root')
    PASSWORD = os.getenv('MYSQL_PASSWORD', '1234')
    DATABASE = os.getenv('MYSQL_DATABASE', 'platform')
    
    # Build database URI
    # Production environment (Railway) requires SSL configuration
    if 'railway' in HOSTNAME or 'rlwy.net' in HOSTNAME or os.getenv('FLASK_ENV') == 'production':
        # Railway connection configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}'
            f'?charset=utf8mb4&ssl_ca=&ssl_verify_cert=false'
        )
    else:
        # Local development connection
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}'
            f'?charset=utf8mb4'
        )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,  # Avoid MySQL connection timeout
        'pool_pre_ping': True,  # Test availability before connection
        'pool_size': 10,  # Connection pool size
        'max_overflow': 20,  # Maximum overflow connections
        'connect_args': {
            'connect_timeout': 30,  # Connection timeout 30 seconds (increased timeout)
            'read_timeout': 30,     # Read timeout 30 seconds
            'write_timeout': 30     # Write timeout 30 seconds
        }
    }
    
    # Email Configuration - QQ Mail (using IP address to bypass DNS resolution)
    # Due to Render platform DNS resolution issues, connect directly using IP address
    
    # QQ Mail SMTP server IP address (obtained from dig smtp.qq.com)
    app.config['MAIL_SERVER'] = '43.129.255.54'  # QQ SMTP server IP
    app.config['MAIL_PORT'] = 465  # SSL port
    app.config['MAIL_USE_SSL'] = True  # Enable SSL
    app.config['MAIL_USE_TLS'] = False  # Port 465 doesn't need TLS
    app.config['MAIL_USERNAME'] = '2966602258@qq.com'  # QQ Mail account
    app.config['MAIL_PASSWORD'] = 'ldjbtknevwftdcid'  # QQ Mail SMTP authorization code
    app.config['MAIL_DEFAULT_SENDER'] = '2966602258@qq.com'
    
    # Backup IP address: 43.163.178.76 (can manually switch if primary IP doesn't work)
    # app.config['MAIL_SERVER'] = '43.163.178.76'
    
    # Note: Using IP address may have SSL certificate verification issues, but usually works fine for email sending
    
    # Backup option: 163 Mail
    # app.config['MAIL_SERVER'] = 'smtp.163.com'
    # app.config['MAIL_PORT'] = 465
    # app.config['MAIL_USE_SSL'] = True
    # app.config['MAIL_USE_TLS'] = False
    # app.config['MAIL_USERNAME'] = 'your163@163.com'
    # app.config['MAIL_PASSWORD'] = 'your163authcode'
    # app.config['MAIL_DEFAULT_SENDER'] = 'your163@163.com'
    
    # Option 3: Gmail with IP (if DNS has issues)
    # app.config['MAIL_SERVER'] = '64.233.184.108'  # Gmail SMTP IP
    # app.config['MAIL_PORT'] = 465
    # app.config['MAIL_USE_SSL'] = True
    # app.config['MAIL_USE_TLS'] = False
    # app.config['MAIL_USERNAME'] = 'zhangPandada@gmail.com'
    # app.config['MAIL_PASSWORD'] = 'tccaqoeqxbqjjnpl'
    # app.config['MAIL_DEFAULT_SENDER'] = 'zhangPandada@gmail.com'
    
    # Email debug settings
    app.config['MAIL_SUPPRESS_SEND'] = False
    app.config['MAIL_DEBUG'] = True
    
    print(f"[EMAIL CONFIG] Gmail server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    print(f"[EMAIL CONFIG] Username: {app.config['MAIL_USERNAME']}")


    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page'
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    mail.init_app(app)
    
    # User loader
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add timezone conversion functions
    @app.template_filter('local_time')
    def local_time_filter(time_obj):
        """Display time (already in Beijing time, no conversion needed)"""
        if time_obj is None:
            return ''
        # Format directly for display, database already stores Beijing time
        return time_obj.strftime('%Y-%m-%d %H:%M')
    
    @app.template_filter('local_date')
    def local_date_filter(time_obj):
        """Display date (already in Beijing time, no conversion needed)"""
        if time_obj is None:
            return ''
        # Format directly for display, database already stores Beijing time
        return time_obj.strftime('%Y-%m-%d')
    
    # Register blueprints
    from .routes import main, auth, courses, activities, qa
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(courses.bp)
    app.register_blueprint(activities.bp)
    app.register_blueprint(qa.qa_bp)
    
    # Create database tables and initial data
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Create default admin user
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
                print("✅ Default admin user created")
            else:
                print("✅ Admin user already exists")
        except Exception as e:
            print(f"⚠️ Database initialization error: {str(e)}")
            print("   Application will start but database operations may fail")
            print("   Please check database connection settings")
    
    return app
