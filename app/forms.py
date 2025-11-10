from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    captcha = StringField('Email Verification Code', validators=[DataRequired(), Length(min=6, max=6)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('instructor', 'Instructor')], validators=[DataRequired()])
    student_id = StringField('Student ID (Optional for instructors)')
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered')
    
    def validate_student_id(self, student_id):
        # 只验证重复性，不再要求学生必须输入（会自动生成）
        if student_id.data:
            user = User.query.filter_by(student_id=student_id.data).first()
            if user:
                raise ValidationError('This student ID is already in use')

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired(), Length(min=2, max=200)])
    semester = StringField('Semester', validators=[DataRequired()])
    description = TextAreaField('Course Description')
    submit = SubmitField('Create Course')

class ActivityForm(FlaskForm):
    title = StringField('Activity Title', validators=[DataRequired(), Length(min=2, max=200)])
    type = SelectField('Activity Type', choices=[('poll', 'Poll'), ('short_answer', 'Short Answer'), ('quiz', 'Quiz'), ('word_cloud', 'Word Cloud'), ('memory_game', 'Memory Game')], validators=[DataRequired()])
    question = TextAreaField('Question', validators=[DataRequired()])
    options = TextAreaField('Options (Required for polls, one per line)')
    duration_minutes = SelectField('Activity Duration', choices=[(1, '1 minute'), (3, '3 minutes'), (5, '5 minutes'), (10, '10 minutes'), (15, '15 minutes'), (30, '30 minutes')], coerce=int, default=5)
    submit = SubmitField('Create Activity')

class AIQuestionForm(FlaskForm):
    text = TextAreaField('Teaching Text', validators=[DataRequired()])
    submit = SubmitField('Generate Questions')

class StudentImportForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[DataRequired()])
    submit = SubmitField('Import Students')
