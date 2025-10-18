from flask import Blueprint, render_template, redirect, url_for, flash, request
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
        # Dashboard只显示最新的4门课程
        dashboard_courses = enrolled_courses[:4]
        has_more_courses = len(enrolled_courses) > 4
        
        activities = []
        for course in enrolled_courses:
            activities.extend(course.activities)
        
        active_activities = [a for a in activities if a.is_active]
        my_responses = Response.query.filter_by(student_id=current_user.id).all()
        
        # 获取别人对我的问题的回复（优化版本）
        from app.models import Question, Answer
        my_questions = Question.query.filter_by(author_id=current_user.id).all()
        others_replies = []
        total_replies_count = 0
        
        for question in my_questions:
            # 获取别人（非自己）对我问题的回复
            replies = Answer.query.filter(
                Answer.question_id == question.id,
                Answer.author_id != current_user.id
            ).order_by(Answer.created_at.desc()).all()
            
            total_replies_count += len(replies)
            
            # 只取每个问题的最新回复用于dashboard显示
            if replies:
                others_replies.append({
                    'answer': replies[0],  # 只取最新的一个回复
                    'question': question,
                    'course': question.course,
                    'total_replies_for_question': len(replies)
                })
        
        # 按时间排序，最新的在前，只显示最新的4条
        others_replies.sort(key=lambda x: x['answer'].created_at, reverse=True)
        dashboard_replies = others_replies[:4]  # Dashboard只显示4条
        
        stats = {
            'enrolled_courses': len(enrolled_courses),
            'active_activities': len(active_activities),
            'my_responses': len(my_responses),
            'others_replies': total_replies_count
        }
        
        return render_template('student_dashboard.html', 
                             stats=stats, 
                             courses=dashboard_courses, 
                             all_courses_count=len(enrolled_courses),
                             has_more_courses=has_more_courses,
                             activities=activities,
                             others_replies=dashboard_replies,
                             has_more_replies=len(others_replies) > 4)

@bp.route('/my-courses')
@login_required
def my_courses():
    """显示学生的所有课程"""
    if current_user.role != 'student':
        flash('只有学生可以查看此页面', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # 获取学生的所有课程（分页）
    page = request.args.get('page', 1, type=int)
    per_page = 8  # 每页显示8门课程
    
    enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
    
    # 手动实现分页
    total = len(enrolled_courses)
    start = (page - 1) * per_page
    end = start + per_page
    courses_on_page = enrolled_courses[start:end]
    
    # 计算分页信息
    has_prev = page > 1
    has_next = end < total
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    return render_template('my_courses.html', 
                         courses=courses_on_page,
                         total=total,
                         page=page,
                         per_page=per_page,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_num=prev_num,
                         next_num=next_num)

@bp.route('/my-replies')
@login_required
def my_replies():
    """显示所有对我问题的回复"""
    if current_user.role != 'student':
        flash('只有学生可以查看此页面', 'warning')
        return redirect(url_for('main.dashboard'))
    
    from app.models import Question, Answer
    
    # 获取我的所有问题
    my_questions = Question.query.filter_by(author_id=current_user.id).all()
    
    # 获取所有对我问题的回复（分页）
    page = request.args.get('page', 1, type=int)
    per_page = 5  # 每页显示5条回复
    
    all_replies = []
    for question in my_questions:
        replies = Answer.query.filter(
            Answer.question_id == question.id,
            Answer.author_id != current_user.id
        ).all()
        
        for reply in replies:
            all_replies.append({
                'answer': reply,
                'question': question,
                'course': question.course
            })
    
    # 按时间排序，最新的在前
    all_replies.sort(key=lambda x: x['answer'].created_at, reverse=True)
    
    # 手动实现分页
    total = len(all_replies)
    start = (page - 1) * per_page
    end = start + per_page
    replies_on_page = all_replies[start:end]
    
    # 计算分页信息
    has_prev = page > 1
    has_next = end < total
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    return render_template('my_replies.html', 
                         replies=replies_on_page,
                         total=total,
                         page=page,
                         per_page=per_page,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_num=prev_num,
                         next_num=next_num)

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
