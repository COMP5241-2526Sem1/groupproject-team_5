from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, socketio
from app.models import Course, Activity, Response, User, Enrollment
from app.forms import ActivityForm, AIQuestionForm
from app.ai_utils import generate_questions, generate_activity_from_content, group_answers, extract_text_from_file, validate_file_upload
from datetime import datetime, timedelta
import json
import re
import csv
import io
import time
import os
import tempfile
from collections import Counter
from flask import make_response
from werkzeug.utils import secure_filename

bp = Blueprint('activities', __name__)

# English stopwords for word cloud filtering
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
    'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'them', 'their', 'what', 'which', 'who', 'when', 'where', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'just', 'don', 'now', 'my', 'me', 'about', 'up', 'out',
    'if', 'into', 'through', 'over', 'before', 'after', 'above', 'below',
    'between', 'during', 'without', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'also', 'any', 'because', 'until', 'while'
}

@bp.route('/activities')
@login_required
def list_activities():
    page = request.args.get('page', 1, type=int)
    per_page = 9  # 每页显示9个活动
    
    if current_user.role == 'admin':
        activities = Activity.query.order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    elif current_user.role == 'instructor':
        activities = Activity.query.join(Course).filter(
            Course.instructor_id == current_user.id
        ).order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
        course_ids = [course.id for course in enrolled_courses]
        activities = Activity.query.filter(
            Activity.course_id.in_(course_ids)
        ).order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('activities/activity_list.html', activities=activities.items, pagination=activities)

def auto_end_activity(activity_id, duration_seconds):
    """后台任务：自动结束活动"""
    print(f"Starting timer for activity {activity_id}, will end in {duration_seconds} seconds")
    time.sleep(duration_seconds)
    
    try:
        # 使用全局的db和socketio，避免循环导入
        from app import db, socketio
        from app.models import Activity
        from datetime import datetime
        
        # 不需要app_context，因为我们在同一个应用进程中
        activity = Activity.query.get(activity_id)
        if activity and activity.is_active:
            print(f"Auto-ending activity {activity_id}")
            activity.is_active = False
            activity.ended_at = datetime.utcnow()
            db.session.commit()
            
            print(f"Activity {activity_id} ended at {activity.ended_at}")
            
            # 通知所有用户活动已结束
            socketio.emit('activity_update', {
                'activity_id': activity_id,
                'update_type': 'auto_ended',
                'data': {
                    'is_active': False,
                    'ended_at': activity.ended_at.isoformat(),
                    'message': 'Activity has ended automatically'
                }
            }, room=f'activity_{activity_id}')
            
            print(f"Notification sent for activity {activity_id}")
        else:
            print(f"Activity {activity_id} not found or already ended")
    except Exception as e:
        print(f"Error in auto_end_activity: {e}")
        import traceback
        traceback.print_exc()

@bp.route('/courses/<int:course_id>/activities/create', methods=['GET', 'POST'])
@login_required
def create_activity(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and course.instructor_id != current_user.id):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = ActivityForm()
    if form.validate_on_submit():
        options = None
        correct_answer = None
        quiz_type = None
        
        if form.type.data == 'poll' and form.options.data:
            options = form.options.data
        elif form.type.data == 'quiz':
            quiz_type = request.form.get('quiz_type')
            correct_answer = request.form.get('correct_answer')
            if quiz_type == 'multiple_choice' and form.options.data:
                options = form.options.data
        
        activity = Activity(
            title=form.title.data,
            type=form.type.data,
            question=form.question.data,
            quiz_type=quiz_type,
            options=options,
            correct_answer=correct_answer,
            course_id=course_id,
            instructor_id=current_user.id,
            duration_minutes=form.duration_minutes.data
        )
        db.session.add(activity)
        db.session.commit()
        flash('Activity created successfully!', 'success')
        return redirect(url_for('activities.activity_detail', activity_id=activity.id))
    
    return render_template('activities/create_activity.html', form=form, course=course)

@bp.route('/activities/<int:activity_id>')
@login_required
def activity_detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=activity.course_id).first()
        if not enrollment:
            flash('You are not enrolled in this course', 'error')
            return redirect(url_for('main.dashboard'))
    elif current_user.role == 'instructor' and activity.course.instructor_id != current_user.id:
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    my_response = None
    if current_user.role == 'student':
        my_response = Response.query.filter_by(student_id=current_user.id, activity_id=activity_id).first()
    
    return render_template('activities/activity_detail.html', activity=activity, my_response=my_response)

@bp.route('/activities/<int:activity_id>/start', methods=['POST'])
@login_required
def start_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    activity.is_active = True
    activity.started_at = datetime.utcnow()
    # 清除之前的结束时间，活动现在是活跃的
    activity.ended_at = None
    db.session.commit()
    
    # 计算预计结束时间（仅用于显示）
    from datetime import timedelta
    will_end_at = activity.started_at + timedelta(minutes=activity.duration_minutes)
    
    # 启动后台任务，在指定时间后自动结束活动 (暂时禁用)
    # socketio.start_background_task(target=auto_end_activity, activity_id=activity_id, duration_seconds=activity.duration_minutes * 60)
    
    # Broadcast to all users in the activity room
    socketio.emit('activity_update', {
        'activity_id': activity_id,
        'update_type': 'started',
        'data': {
            'is_active': True,
            'started_at': activity.started_at.isoformat(),
            'duration_minutes': activity.duration_minutes,
            'will_end_at': will_end_at.isoformat()
        }
    }, room=f'activity_{activity_id}')
    
    return jsonify({
        'success': True, 
        'message': f'Activity started for {activity.duration_minutes} minutes',
        'duration_minutes': activity.duration_minutes,
        'will_end_at': will_end_at.isoformat()
    })

@bp.route('/activities/<int:activity_id>/stop', methods=['POST'])
@login_required
def stop_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    activity.is_active = False
    activity.ended_at = datetime.utcnow()
    db.session.commit()
    
    # Broadcast to all users in the activity room
    socketio.emit('activity_update', {
        'activity_id': activity_id,
        'update_type': 'ended',
        'data': {
            'is_active': False,
            'ended_at': activity.ended_at.isoformat()
        }
    }, room=f'activity_{activity_id}')
    
    return jsonify({'success': True, 'message': 'Activity ended'})

@bp.route('/activities/<int:activity_id>/reset', methods=['POST'])
@login_required
def reset_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    # 重置活动状态
    activity.is_active = False
    activity.started_at = None
    activity.ended_at = None
    
    # 清除所有学生的回答记录 (可选)
    Response.query.filter_by(activity_id=activity_id).delete()
    
    db.session.commit()
    
    # Broadcast to all users in the activity room
    socketio.emit('activity_update', {
        'activity_id': activity_id,
        'update_type': 'reset',
        'data': {
            'is_active': False,
            'message': 'Activity has been reset'
        }
    }, room=f'activity_{activity_id}')
    
    return jsonify({'success': True, 'message': 'Activity reset successfully'})

@bp.route('/activities/<int:activity_id>/submit', methods=['POST'])
@login_required
def submit_response(activity_id):
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': 'Only students can submit answers'})
    
    activity = Activity.query.get_or_404(activity_id)
    
    if not activity.is_active:
        return jsonify({'success': False, 'message': 'Activity not started or already ended'})
    
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=activity.course_id).first()
    if not enrollment:
        return jsonify({'success': False, 'message': 'You are not enrolled in this course'})
    
    data = request.get_json()
    answer = data.get('answer', '').strip()
    
    if not answer:
        return jsonify({'success': False, 'message': 'Answer cannot be empty'})

    is_correct = None
    score = 0
    points = 0

    if activity.type == 'quiz':
        correct_answer = (activity.correct_answer or '').strip()
        quiz_type = (activity.quiz_type or '').strip()
        normalized_answer = answer.lower()
        normalized_correct = correct_answer.lower()
        
        if quiz_type == 'fill_blank':
            is_correct = normalized_answer == normalized_correct
        elif quiz_type == 'true_false':
            is_correct = normalized_answer in ['true', 'false'] and normalized_answer == normalized_correct
        else:
            is_correct = normalized_answer == normalized_correct
        
        score = 1 if is_correct else 0
        points = score
    elif activity.type == 'memory_game':
        correct_sequence = (data.get('correct_sequence', '') or '').strip()
        if correct_sequence:
            def normalize_sequence(seq):
                return [part.strip().lower() for part in seq.split(',') if part.strip()]
            is_correct = normalize_sequence(answer) == normalize_sequence(correct_sequence)
            score = 1 if is_correct else 0
            points = score
    
    # Check if there's already a response
    existing_response = Response.query.filter_by(student_id=current_user.id, activity_id=activity_id).first()
    if existing_response:
        existing_response.answer = answer
        existing_response.submitted_at = datetime.utcnow()
        existing_response.is_correct = is_correct
        existing_response.score = score
        existing_response.points_earned = points
    else:
        response = Response(
            student_id=current_user.id,
            activity_id=activity_id,
            answer=answer,
            is_correct=is_correct,
            score=score,
            points_earned=points
        )
        db.session.add(response)
    
    db.session.commit()
    
    # Broadcast new response to all users in the activity room
    socketio.emit('response_added', {
        'activity_id': activity_id,
        'response_count': Response.query.filter_by(activity_id=activity_id).count(),
        'message': 'New response submitted'
    }, room=f'activity_{activity_id}')
    
    return jsonify({'success': True, 'message': 'Answer submitted successfully'})

@bp.route('/activities/<int:activity_id>/results')
@login_required
def activity_results(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    responses = Response.query.filter_by(activity_id=activity_id).all()
    
    if activity.type == 'poll':
        options = activity.options.split('\n') if activity.options else []
        option_counts = {}
        for option in options:
            option_counts[option.strip()] = 0
        
        for response in responses:
            answer = response.answer.strip()
            if answer in option_counts:
                option_counts[answer] += 1
        
        results = {
            'type': 'poll',
            'options': option_counts,
            'total_responses': len(responses)
        }
    elif activity.type == 'quiz':
        correct_count = sum(1 for r in responses if r.is_correct)
        average_score = sum(r.score for r in responses) / len(responses) if responses else 0
        
        results = {
            'type': 'quiz',
            'correct_count': correct_count,
            'total_responses': len(responses),
            'average_score': average_score,
            'responses': [{'answer': r.answer, 'is_correct': r.is_correct, 'score': r.score, 'student': r.student.name} for r in responses]
        }
    elif activity.type == 'memory_game':
        correct_count = sum(1 for r in responses if r.is_correct)
        results = {
            'type': 'memory_game',
            'total_responses': len(responses),
            'correct_count': correct_count,
            'accuracy': (correct_count / len(responses) * 100) if responses else 0,
            'responses': [{
                'student': r.student,
                'answer': r.answer,
                'is_correct': r.is_correct,
                'submitted_at': r.submitted_at
            } for r in responses]
        }
    elif activity.type == 'word_cloud':
        answers = [response.answer for response in responses]
        
        word_freq = Counter()
        for answer in answers:
            # Extract words, normalize, and filter stopwords
            words = re.findall(r'\b[a-zA-Z]+\b', answer.lower())
            filtered_words = [w for w in words if w not in STOPWORDS and len(w) >= 3]
            word_freq.update(filtered_words)
        
        common_words = word_freq.most_common(200)
        
        results = {
            'type': 'word_cloud',
            'answers': answers,
            'word_frequency': common_words,
            'total_responses': len(responses),
            'unique_words': len(word_freq)
        }
    else:
        answers = [response.answer for response in responses]
        
        word_freq = Counter()
        
        for answer in answers:
            # Extract words, filter by length and stopwords
            words = re.findall(r'\b[a-zA-Z]+\b', answer.lower())
            # Filter: remove stopwords and words shorter than 3 characters
            filtered_words = [w for w in words if w not in STOPWORDS and len(w) >= 3]
            word_freq.update(filtered_words)
        
        common_words = word_freq.most_common(200)
        
        results = {
            'type': 'short_answer',
            'answers': answers,
            'word_frequency': common_words,
            'total_responses': len(responses),
            'unique_words': len(word_freq)
        }
    
    return render_template('activities/activity_results.html', activity=activity, results=results, responses=responses)

@bp.route('/activities/generate_questions', methods=['POST'])
@login_required
def generate_questions_route():
    if current_user.role not in ['admin', 'instructor']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    text = ""
    
    # 统一文本变量
    text = None
    
    # 检查是否是文件上传请求
    if 'file' in request.files:
        file = request.files['file']
        
        # 验证文件
        is_valid, message = validate_file_upload(file)
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        # 保存临时文件并提取文本
        try:
            # 创建临时文件
            file_extension = os.path.splitext(secure_filename(file.filename))[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            # 提取文本
            text = extract_text_from_file(temp_file_path, file_extension)
            
            # 清理临时文件
            os.unlink(temp_file_path)
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'File processing failed: {str(e)}'})
    
    else:
        # 处理JSON请求（原有的文本输入方式）
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'message': 'Please enter teaching text or upload a file'})
    
    try:
        questions = generate_questions(text)
        return jsonify({'success': True, 'questions': questions})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Generation failed: {str(e)}'})

@bp.route('/activities/status/<int:activity_id>')
@login_required
def activity_status(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=activity.course_id).first()
        if not enrollment:
            return jsonify({'error': 'Not enrolled in this course'})
        
        my_response = Response.query.filter_by(student_id=current_user.id, activity_id=activity_id).first()
        return jsonify({
            'is_active': activity.is_active,
            'has_responded': my_response is not None,
            'my_answer': my_response.answer if my_response else None
        })
    else:
        response_count = Response.query.filter_by(activity_id=activity_id).count()
        return jsonify({
            'is_active': activity.is_active,
            'response_count': response_count
        })

@bp.route('/activities/generate_activity', methods=['POST'])
@login_required
def generate_activity():
    if current_user.role not in ['admin', 'instructor']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    data = request.get_json()
    content = data.get('content', '').strip()
    activity_type = data.get('activity_type', 'short_answer')
    
    if not content:
        return jsonify({'success': False, 'message': 'Please enter content'})
    
    try:
        activity_data = generate_activity_from_content(content, activity_type)
        return jsonify({'success': True, 'activity': activity_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Generation failed: {str(e)}'})

@bp.route('/activities/<int:activity_id>/group_answers', methods=['POST'])
@login_required
def group_activity_answers(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    responses = Response.query.filter_by(activity_id=activity_id).all()
    answers = [response.answer for response in responses]
    
    if not answers:
        return jsonify({'success': False, 'message': 'No answers to group'})
    
    try:
        grouped_data = group_answers(answers)
        return jsonify({'success': True, 'grouped_data': grouped_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Grouping failed: {str(e)}'})

@bp.route('/activities/<int:activity_id>/export')
@login_required
def export_activity_results(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    responses = Response.query.filter_by(activity_id=activity_id).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    if activity.type == 'quiz':
        writer.writerow(['Student Name', 'Student Email', 'Answer', 'Correct', 'Score', 'Submitted At'])
    else:
        writer.writerow(['Student Name', 'Student Email', 'Answer', 'Submitted At'])
    
    # Write data
    for response in responses:
        row = [
            response.student.name,
            response.student.email,
            response.answer,
        ]
        
        if activity.type == 'quiz':
            row.extend([
                'Yes' if response.is_correct else 'No',
                response.score
            ])
        
        row.append(response.submitted_at.strftime('%Y-%m-%d %H:%M:%S'))
        writer.writerow(row)
    
    # Create response
    output.seek(0)
    response_obj = make_response(output.getvalue())
    response_obj.headers['Content-Type'] = 'text/csv'
    response_obj.headers['Content-Disposition'] = f'attachment; filename=activity_{activity_id}_results.csv'
    
    return response_obj

@bp.route('/activities/<int:activity_id>/analytics')
@login_required
def activity_analytics(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    responses = Response.query.filter_by(activity_id=activity_id).all()
    
    # Calculate analytics
    analytics = {
        'total_responses': len(responses),
        'participation_rate': 0,
        'average_response_time': 0,
        'response_distribution': {},
        'word_analysis': {},
        'time_analysis': {}
    }
    
    if responses:
        # Participation rate (assuming all enrolled students)
        enrolled_students = Enrollment.query.filter_by(course_id=activity.course_id).count()
        analytics['participation_rate'] = (len(responses) / enrolled_students * 100) if enrolled_students > 0 else 0
        
        # Response time analysis
        if activity.started_at:
            response_times = []
            for response in responses:
                if response.submitted_at and activity.started_at:
                    time_diff = (response.submitted_at - activity.started_at).total_seconds() / 60  # minutes
                    response_times.append(time_diff)
            
            if response_times:
                analytics['average_response_time'] = sum(response_times) / len(response_times)
                analytics['time_analysis'] = {
                    'min_time': min(response_times),
                    'max_time': max(response_times),
                    'median_time': sorted(response_times)[len(response_times)//2]
                }
        
        # Word analysis for text responses
        if activity.type in ['short_answer', 'word_cloud']:
            all_text = ' '.join([response.answer for response in responses])
            words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
            # Filter stopwords and short words
            filtered_words = [w for w in words if w not in STOPWORDS and len(w) >= 3]
            word_freq = Counter(filtered_words)
            analytics['word_analysis'] = {
                'total_words': len(filtered_words),
                'unique_words': len(word_freq),
                'most_common': word_freq.most_common(200)
            }
        
        # Response distribution
        if activity.type == 'poll':
            option_counts = {}
            if activity.options:
                for option in activity.options.split('\n'):
                    option_counts[option.strip()] = 0
                
                for response in responses:
                    if response.answer in option_counts:
                        option_counts[response.answer] += 1
                
                analytics['response_distribution'] = option_counts
        
        elif activity.type == 'quiz':
            correct_count = sum(1 for r in responses if r.is_correct)
            analytics['response_distribution'] = {
                'correct': correct_count,
                'incorrect': len(responses) - correct_count,
                'accuracy_rate': (correct_count / len(responses) * 100) if responses else 0
            }
    
    return render_template('activities/activity_analytics.html', activity=activity, analytics=analytics)

@bp.route('/courses/<int:course_id>/export_all')
@login_required
def export_course_activities(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and course.instructor_id != current_user.id):
        flash('Insufficient permissions', 'error')
        return redirect(url_for('main.dashboard'))
    
    activities = Activity.query.filter_by(course_id=course_id).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Activity Title', 'Type', 'Question', 'Total Responses', 'Created At', 'Status'])
    
    # Write data
    for activity in activities:
        response_count = Response.query.filter_by(activity_id=activity.id).count()
        status = 'Active' if activity.is_active else 'Ended'
        
        writer.writerow([
            activity.title,
            activity.type,
            activity.question[:100] + '...' if len(activity.question) > 100 else activity.question,
            response_count,
            activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            status
        ])
    
    # Create response
    output.seek(0)
    response_obj = make_response(output.getvalue())
    response_obj.headers['Content-Type'] = 'text/csv'
    response_obj.headers['Content-Disposition'] = f'attachment; filename=course_{course_id}_activities.csv'
    
    return response_obj

@bp.route('/activities/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(activity_id):
    """Delete activity - Admin and instructor permission"""
    activity = Activity.query.get_or_404(activity_id)
    course = Course.query.get_or_404(activity.course_id)
    
    # Permission check
    if current_user.role == 'admin':
        # Admin can delete all activities
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        # Instructor can delete activities in their own courses
        pass
    else:
        flash('You do not have permission to delete this activity', 'error')
        return redirect(url_for('activities.list_activities'))
    
    try:
        # Delete all related responses
        Response.query.filter_by(activity_id=activity_id).delete()
        
        # Delete the activity itself
        db.session.delete(activity)
        db.session.commit()
        
        flash(f'Activity "{activity.title}" deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error occurred while deleting activity, please try again later', 'error')
    
    return redirect(url_for('activities.list_activities'))

# Note: Activity editing is disabled to maintain data integrity
# Once an activity is published, it should not be modified
# 
# @bp.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST'])
# @login_required
# def edit_activity(activity_id):
#     """Edit activity - Admin and instructor permission"""
#     activity = Activity.query.get_or_404(activity_id)
#     course = Course.query.get_or_404(activity.course_id)
#     
#     # Permission check
#     if current_user.role == 'admin':
#         # 管理员可以编辑所有活动
#         pass
#     elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
#         # Instructor can edit activities in their own courses
#         pass
#     else:
#         flash('You do not have permission to edit this activity', 'error')
#         return redirect(url_for('activities.list_activities'))
#     
#     form = ActivityForm()
#     
#     if form.validate_on_submit():
#         activity.title = form.title.data
#         activity.type = form.type.data
#         activity.question = form.question.data
#         activity.options = form.options.data
#         
#         db.session.commit()
#         flash('Activity information updated successfully!', 'success')
#         return redirect(url_for('activities.activity_detail', activity_id=activity.id))
#     
#     # Pre-populate form data
#     if request.method == 'GET':
#         form.title.data = activity.title
#         form.type.data = activity.type
#         form.question.data = activity.question
#         form.options.data = activity.options
#     
#     return render_template('activities/edit_activity.html', form=form, activity=activity, course=course)

