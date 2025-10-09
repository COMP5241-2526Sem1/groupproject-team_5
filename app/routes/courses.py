from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import Course, User, Enrollment, Activity
from app.forms import CourseForm, StudentImportForm
import csv
import io

bp = Blueprint('courses', __name__)

@bp.route('/courses')
@login_required
def list_courses():
    if current_user.role == 'admin':
        courses = Course.query.all()
    elif current_user.role == 'instructor':
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
    else:
        enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
        return render_template('courses/student_courses.html', courses=enrolled_courses)
    
    return render_template('courses/course_list.html', courses=courses)

@bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role not in ['admin', 'instructor']:
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            name=form.name.data,
            semester=form.semester.data,
            description=form.description.data,
            instructor_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('courses.course_detail', course_id=course.id))
    
    return render_template('courses/create_course.html', form=form)

@bp.route('/courses/<int:course_id>')
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
        if not enrollment:
            flash('You are not enrolled in this course', 'error')
            return redirect(url_for('main.dashboard'))
    elif current_user.role == 'instructor' and course.instructor_id != current_user.id:
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    activities = Activity.query.filter_by(course_id=course_id).order_by(Activity.created_at.desc()).all()
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    return render_template('courses/course_detail.html', course=course, activities=activities, enrollments=enrollments)

@bp.route('/courses/<int:course_id>/import_students', methods=['GET', 'POST'])
@login_required
def import_students(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and course.instructor_id != current_user.id):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = StudentImportForm()
    if form.validate_on_submit():
        if form.csv_file.data:
            try:
                csv_data = form.csv_file.data.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(csv_data))
                
                imported_count = 0
                for row in csv_reader:
                    name = row.get('name', '').strip()
                    email = row.get('email', '').strip()
                    student_id = row.get('student_id', '').strip()
                    
                    if not name or not email:
                        continue
                    
                    user = User.query.filter_by(email=email).first()
                    if not user:
                        user = User(
                            name=name,
                            email=email,
                            password_hash=generate_password_hash('123456'),
                            role='student',
                            student_id=student_id
                        )
                        db.session.add(user)
                        db.session.flush()
                    
                    existing_enrollment = Enrollment.query.filter_by(student_id=user.id, course_id=course_id).first()
                    if not existing_enrollment:
                        enrollment = Enrollment(student_id=user.id, course_id=course_id)
                        db.session.add(enrollment)
                        imported_count += 1
                
                db.session.commit()
                flash(f'Successfully imported {imported_count} students', 'success')
                return redirect(url_for('courses.course_detail', course_id=course_id))
                
            except Exception as e:
                flash(f'Import failed: {str(e)}', 'error')
    
    return render_template('courses/import_students.html', form=form, course=course)

@bp.route('/courses/<int:course_id>/enrollments')
@login_required
def course_enrollments(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and course.instructor_id != current_user.id):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    return render_template('courses/course_enrollments.html', course=course, enrollments=enrollments)
