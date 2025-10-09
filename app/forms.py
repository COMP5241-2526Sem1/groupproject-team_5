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
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('instructor', 'Instructor')], validators=[DataRequired()])
    student_id = StringField('Student ID (Required for students)')
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered')
    
    def validate_student_id(self, student_id):
        if self.role.data == 'student' and not student_id.data:
            raise ValidationError('Students must provide a student ID')
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
    submit = SubmitField('Create Activity')

class AIQuestionForm(FlaskForm):
    text = TextAreaField('Teaching Text', validators=[DataRequired()])
    submit = SubmitField('Generate Questions')

class StudentImportForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[DataRequired()])
    submit = SubmitField('Import Students')
