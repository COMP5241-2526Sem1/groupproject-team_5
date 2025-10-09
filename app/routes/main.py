from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Course, Activity, Response
from sqlalchemy import func

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        courses = Course.query.all()
        activities = Activity.query.all()
        students = User.query.filter_by(role='student').all()
        instructors = User.query.filter_by(role='instructor').all()
        
        stats = {
            'total_courses': len(courses),
            'total_activities': len(activities),
            'total_students': len(students),
            'total_instructors': len(instructors)
        }
        
        return render_template('admin_dashboard.html', stats=stats, courses=courses)
    
    elif current_user.role == 'instructor':
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
        activities = Activity.query.join(Course).filter(Course.instructor_id == current_user.id).all()
        
        stats = {
            'my_courses': len(courses),
            'my_activities': len(activities),
            'active_activities': len([a for a in activities if a.is_active])
        }
        
        return render_template('instructor_dashboard.html', stats=stats, courses=courses, activities=activities)
    
    else:
        enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
        activities = []
        for course in enrolled_courses:
            activities.extend(course.activities)
        
        active_activities = [a for a in activities if a.is_active]
        my_responses = Response.query.filter_by(student_id=current_user.id).all()
        
        stats = {
            'enrolled_courses': len(enrolled_courses),
            'active_activities': len(active_activities),
            'my_responses': len(my_responses)
        }
        
        return render_template('student_dashboard.html', stats=stats, courses=enrolled_courses, activities=activities)

@bp.route('/leaderboard')
@login_required
def leaderboard():
    if current_user.role == 'student':
        flash('Students cannot access leaderboard', 'warning')
        return redirect(url_for('main.dashboard'))
    
    students = User.query.filter_by(role='student').all()
    student_stats = []
    
    for student in students:
        response_count = Response.query.filter_by(student_id=student.id).count()
        student_stats.append({
            'student': student,
            'response_count': response_count
        })
    
    student_stats.sort(key=lambda x: x['response_count'], reverse=True)
    
    return render_template('leaderboard.html', student_stats=student_stats)
