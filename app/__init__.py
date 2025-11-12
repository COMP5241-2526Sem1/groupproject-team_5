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

# 加载环境变量
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
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
    
    # 构建数据库 URI
    # 生产环境（Railway）需要 SSL 配置
    if 'railway' in HOSTNAME or 'rlwy.net' in HOSTNAME or os.getenv('FLASK_ENV') == 'production':
        # Railway 连接配置
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}'
            f'?charset=utf8mb4&ssl_ca=&ssl_verify_cert=false'
        )
    else:
        # 本地开发连接
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}'
            f'?charset=utf8mb4'
        )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,  # 避免 MySQL 连接超时
        'pool_pre_ping': True,  # 连接前测试可用性
        'pool_size': 10,  # 连接池大小
        'max_overflow': 20,  # 最大溢出连接数
        'connect_args': {
            'connect_timeout': 30,  # 连接超时30秒（增加超时时间）
            'read_timeout': 30,     # 读取超时30秒
            'write_timeout': 30     # 写入超时30秒
        }
    }
    
    # Email Configuration
    # 支持从环境变量配置邮件服务器（用于生产环境）
    # 如果环境变量未设置，则使用默认配置（开发环境）
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.qq.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '2966602258@qq.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'nihtjcxaseuedcdd')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', '2966602258@qq.com')


    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请登录以访问此页面'
    socketio.init_app(app, cors_allowed_origins="*")
    mail.init_app(app)
    
    # User loader
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 添加时区转换函数
    @app.template_filter('local_time')
    def local_time_filter(utc_time):
        """将UTC时间转换为北京时间"""
        if utc_time is None:
            return ''
        # 北京时间 = UTC时间 + 8小时
        beijing_time = utc_time + timedelta(hours=8)
        return beijing_time.strftime('%Y-%m-%d %H:%M')
    
    @app.template_filter('local_date')
    def local_date_filter(utc_time):
        """将UTC时间转换为北京日期"""
        if utc_time is None:
            return ''
        beijing_time = utc_time + timedelta(hours=8)
        return beijing_time.strftime('%Y-%m-%d')
    
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
