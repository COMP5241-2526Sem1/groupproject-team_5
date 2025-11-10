"""
Q&A Education Platform - Database Models
"""

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from app.utils import beijing_now

class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, instructor, admin
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    
    # Relationships
    courses = db.relationship('Course', backref='instructor', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    responses = db.relationship('Response', backref='student', lazy=True)
    questions = db.relationship('Question', backref='author', lazy=True)
    answers = db.relationship('Answer', backref='author', lazy=True)
    
    @staticmethod
    def generate_student_id():
        """生成下一个学生ID"""
        from app import db
        # 查找最大的学生ID
        last_student = db.session.query(User).filter(
            User.student_id.like('2025%'),
            User.role == 'student'
        ).order_by(User.student_id.desc()).first()
        
        if last_student and last_student.student_id:
            # 从最后一个学生ID中提取数字并加1
            try:
                last_number = int(last_student.student_id)
                return str(last_number + 1)
            except ValueError:
                pass
        
        # 如果没有找到或解析失败，从2025001开始
        return '2025001'

class EmailCaptcha(db.Model):
    """邮箱验证码模型"""
    __tablename__ = 'email_captcha'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    captcha = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))

class Course(db.Model):
    """课程模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    activities = db.relationship('Activity', backref='course', lazy=True)
    questions = db.relationship('Question', backref='course', lazy=True)

class Enrollment(db.Model):
    """选课记录模型"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id'),)

class Activity(db.Model):
    """活动模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    question = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # poll, short_answer, quiz, etc.
    quiz_type = db.Column(db.String(50), nullable=True)  # multiple_choice, true_false, fill_blank
    options = db.Column(db.Text)  # JSON string for poll options
    correct_answer = db.Column(db.String(500))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    duration_minutes = db.Column(db.Integer, default=5)  # 活动持续时间（分钟）
    created_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # QR Code quick join fields
    allow_quick_join = db.Column(db.Boolean, default=True)  # 是否允许二维码快速加入
    join_token = db.Column(db.String(64), unique=True, nullable=True)  # 加入令牌
    token_expires_at = db.Column(db.DateTime, nullable=True)  # 令牌过期时间
    
    # Relationships
    responses = db.relationship('Response', backref='activity', lazy=True, cascade='all, delete-orphan')
    
    def generate_join_token(self):
        """生成唯一的加入令牌（使用北京时间）"""
        import secrets
        from datetime import timedelta, timezone
        
        self.join_token = secrets.token_urlsafe(32)
        
        # 获取当前北京时间（UTC+8）
        beijing_tz = timezone(timedelta(hours=8))
        now_beijing = datetime.now(beijing_tz)
        
        # 令牌在活动结束后 24 小时过期
        if self.ended_at:
            # ended_at 是 naive datetime（无时区），假设为 UTC
            ended_utc = self.ended_at.replace(tzinfo=timezone.utc)
            ended_beijing = ended_utc.astimezone(beijing_tz)
            expires_beijing = ended_beijing + timedelta(hours=24)
        else:
            # 如果活动未结束，设置为当前北京时间 + 7 天
            expires_beijing = now_beijing + timedelta(days=7)
        
        # 转换为 UTC 时间存储（naive datetime，不带时区信息）
        self.token_expires_at = expires_beijing.astimezone(timezone.utc).replace(tzinfo=None)
        return self.join_token
    
    def is_token_valid(self):
        """检查令牌是否有效"""
        if not self.join_token or not self.allow_quick_join:
            return False
        if self.token_expires_at:
            # 使用 UTC 时间进行比较
            if beijing_now().replace(tzinfo=None) > self.token_expires_at:
                return False
        return True
    
    def get_token_expires_beijing_time(self):
        """获取令牌过期时间的北京时间（用于显示）"""
        if not self.token_expires_at:
            return None
        from datetime import timezone, timedelta
        beijing_tz = timezone(timedelta(hours=8))
        utc_time = self.token_expires_at.replace(tzinfo=timezone.utc)
        return utc_time.astimezone(beijing_tz)

class Response(db.Model):
    """活动响应模型"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)  # Whether the answer is correct
    score = db.Column(db.Integer, default=0)  # Score for this response
    points_earned = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    
    __table_args__ = (db.UniqueConstraint('student_id', 'activity_id'),)

# Q&A System Models
class Question(db.Model):
    """问题模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    best_answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=True)
    is_resolved = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None), onupdate=lambda: beijing_now().replace(tzinfo=None))
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, 
                            foreign_keys='Answer.question_id', cascade='all, delete-orphan')

class Answer(db.Model):
    """回答模型"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    is_instructor_answer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None), onupdate=lambda: beijing_now().replace(tzinfo=None))
    
    # Relationships
    votes = db.relationship('AnswerVote', backref='answer', lazy=True, cascade='all, delete-orphan')

class AnswerVote(db.Model):
    """回答投票模型"""
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=lambda: beijing_now().replace(tzinfo=None))
    
    # Relationships
    user = db.relationship('User', backref='answer_votes')
    
    __table_args__ = (db.UniqueConstraint('answer_id', 'user_id'),)
