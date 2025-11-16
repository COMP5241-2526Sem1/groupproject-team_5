"""
Q&A Education Platform - Database Models
"""

from app import db, login_manager, get_beijing_time
from flask_login import UserMixin
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, instructor, admin
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    
    # Relationships
    courses = db.relationship('Course', backref='instructor', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    responses = db.relationship('Response', backref='student', lazy=True)
    questions = db.relationship('Question', backref='author', lazy=True)
    answers = db.relationship('Answer', backref='author', lazy=True)
    
    @staticmethod
    def generate_student_id():
        """Generate next student ID"""
        from app import db
        # Find largest student ID
        last_student = db.session.query(User).filter(
            User.student_id.like('2025%'),
            User.role == 'student'
        ).order_by(User.student_id.desc()).first()
        
        if last_student and last_student.student_id:
            # Extract number from last student ID and add 1
            try:
                last_number = int(last_student.student_id)
                return str(last_number + 1)
            except ValueError:
                pass
        
        # If not found or parsing failed, start from 2025001
        return '2025001'

class EmailCaptcha(db.Model):
    """Email verification code model"""
    __tablename__ = 'email_captcha'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    captcha = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DateTime, default=lambda: get_beijing_time())

class Course(db.Model):
    """Course model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    activities = db.relationship('Activity', backref='course', lazy=True)
    questions = db.relationship('Question', backref='course', lazy=True)

class Enrollment(db.Model):
    """Enrollment record model"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id'),)

class Activity(db.Model):
    """Activity model"""
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
    duration_minutes = db.Column(db.Integer, default=5)  # Activity duration (minutes) - for backward compatibility
    duration_seconds = db.Column(db.Integer, nullable=True)  # Activity duration (seconds) - precise duration
    created_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # QR Code quick join fields
    allow_quick_join = db.Column(db.Boolean, default=True)  # Whether to allow QR code quick join
    join_token = db.Column(db.String(64), unique=True, nullable=True)  # Join token
    token_expires_at = db.Column(db.DateTime, nullable=True)  # Token expiration time
    
    # Relationships
    responses = db.relationship('Response', backref='activity', lazy=True, cascade='all, delete-orphan')
    
    def generate_join_token(self):
        """Generate unique join token (using Beijing time)"""
        import secrets
        from datetime import timedelta, timezone
        
        self.join_token = secrets.token_urlsafe(32)
        
        # Get current Beijing time (UTC+8)
        beijing_tz = timezone(timedelta(hours=8))
        now_beijing = datetime.now(beijing_tz)
        
        # Token expires 24 hours after activity ends
        if self.ended_at:
            # ended_at is naive datetime (no timezone), assume UTC
            ended_utc = self.ended_at.replace(tzinfo=timezone.utc)
            ended_beijing = ended_utc.astimezone(beijing_tz)
            expires_beijing = ended_beijing + timedelta(hours=24)
        else:
            # If activity hasn't ended, set to current Beijing time + 7 days
            expires_beijing = now_beijing + timedelta(days=7)
        
        # Convert to UTC time for storage (naive datetime, no timezone info)
        self.token_expires_at = expires_beijing.astimezone(timezone.utc).replace(tzinfo=None)
        return self.join_token
    
    def is_token_valid(self):
        """Check if token is valid"""
        if not self.join_token or not self.allow_quick_join:
            return False
        if self.token_expires_at:
            # Compare using Beijing time
            if get_beijing_time() > self.token_expires_at:
                return False
        return True
    
    def get_token_expires_beijing_time(self):
        """Get token expiration time in Beijing time (for display)"""
        if not self.token_expires_at:
            return None
        from datetime import timezone, timedelta
        beijing_tz = timezone(timedelta(hours=8))
        utc_time = self.token_expires_at.replace(tzinfo=timezone.utc)
        return utc_time.astimezone(beijing_tz)

class Response(db.Model):
    """Activity response model"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)  # Whether the answer is correct
    score = db.Column(db.Integer, default=0)  # Score for this response
    points_earned = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    
    __table_args__ = (db.UniqueConstraint('student_id', 'activity_id'),)

# Q&A System Models
class Question(db.Model):
    """Question model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    best_answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=True)
    is_resolved = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    updated_at = db.Column(db.DateTime, default=lambda: get_beijing_time(), onupdate=lambda: get_beijing_time())
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, 
                            foreign_keys='Answer.question_id', cascade='all, delete-orphan')

class Answer(db.Model):
    """Answer model"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    is_instructor_answer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    updated_at = db.Column(db.DateTime, default=lambda: get_beijing_time(), onupdate=lambda: get_beijing_time())
    
    # Relationships
    votes = db.relationship('AnswerVote', backref='answer', lazy=True, cascade='all, delete-orphan')

class AnswerVote(db.Model):
    """Answer vote model"""
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=lambda: get_beijing_time())
    
    # Relationships
    user = db.relationship('User', backref='answer_votes')
    
    __table_args__ = (db.UniqueConstraint('answer_id', 'user_id'),)
