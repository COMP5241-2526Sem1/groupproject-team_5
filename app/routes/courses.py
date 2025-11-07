from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import Course, User, Enrollment, Activity, Question, Answer
from app.forms import CourseForm, StudentImportForm
import csv
import io

bp = Blueprint('courses', __name__)

@bp.route('/courses')
@login_required
def list_courses():
    page = request.args.get('page', 1, type=int)
    per_page = 6  # 每页显示6个课程
    
    if current_user.role == 'admin':
        courses = Course.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
    elif current_user.role == 'instructor':
        courses = Course.query.filter_by(instructor_id=current_user.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
        return render_template('courses/student_courses.html', courses=enrolled_courses)
    
    return render_template('courses/course_list.html', courses=courses.items, pagination=courses)

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

@bp.route('/courses/browse')
@login_required
def browse_courses():
    """学生浏览所有可选课程"""
    if current_user.role != 'student':
        return redirect(url_for('courses.list_courses'))
    
    # 获取所有课程
    all_courses = Course.query.all()
    
    # 获取学生已选课程ID
    enrolled_course_ids = [enrollment.course_id for enrollment in current_user.enrollments]
    
    # 筛选出未选修的课程
    available_courses = [course for course in all_courses if course.id not in enrolled_course_ids]
    
    return render_template('courses/browse_courses.html', 
                         available_courses=available_courses)

@bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    """学生选修课程"""
    if current_user.role != 'student':
        flash('只有学生可以选修课程', 'error')
        return redirect(url_for('courses.list_courses'))
    
    course = Course.query.get_or_404(course_id)
    
    # 检查是否已经选修
    existing_enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('您已经选修了这门课程', 'warning')
    else:
        enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash(f'成功选修课程：{course.name}', 'success')
    
    return redirect(url_for('courses.browse_courses'))

@bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """编辑课程 - 管理员可以编辑所有课程，教师只能编辑自己的课程"""
    course = Course.query.get_or_404(course_id)
    
    # 权限检查
    if current_user.role == 'admin':
        # 管理员可以编辑所有课程
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        # 教师只能编辑自己的课程
        pass
    else:
        flash('您没有编辑此课程的权限', 'error')
        return redirect(url_for('courses.list_courses'))
    
    form = CourseForm()
    
    if form.validate_on_submit():
        course.name = form.name.data
        course.semester = form.semester.data
        course.description = form.description.data
        
        db.session.commit()
        flash('课程信息更新成功！', 'success')
        return redirect(url_for('courses.course_detail', course_id=course.id))
    
    # 预填充表单数据
    if request.method == 'GET':
        form.name.data = course.name
        form.semester.data = course.semester
        form.description.data = course.description
    
    return render_template('courses/edit_course.html', form=form, course=course)

@bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    """删除课程 - 管理员可以删除所有课程，教师只能删除自己的课程"""
    course = Course.query.get_or_404(course_id)
    
    # 权限检查
    if current_user.role == 'admin':
        # 管理员可以删除所有课程
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        # 教师只能删除自己的课程
        pass
    else:
        flash('您没有删除此课程的权限', 'error')
        return redirect(url_for('courses.list_courses'))
    
    try:
        # 删除相关数据
        # 1. 删除课程相关的问题和答案
        for question in course.questions:
            # 删除问题的所有答案
            Answer.query.filter_by(question_id=question.id).delete()
            # 删除问题
            db.session.delete(question)
        
        # 2. 删除课程相关的活动和响应
        for activity in course.activities:
            db.session.delete(activity)  # 响应会通过级联删除
        
        # 3. 删除选课记录
        Enrollment.query.filter_by(course_id=course.id).delete()
        
        # 4. 删除课程本身
        db.session.delete(course)
        db.session.commit()
        
        flash('课程删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除课程时发生错误，请稍后重试', 'error')
    
    return redirect(url_for('courses.list_courses'))
