from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, socketio
from app.models import Course, Activity, Response, User, Enrollment
from app.forms import ActivityForm, AIQuestionForm
from app.ai_utils import generate_questions, generate_activity_from_content, group_answers
from datetime import datetime
import json
import re
import csv
import io
from collections import Counter
from flask import make_response

bp = Blueprint('activities', __name__)

@bp.route('/activities')
@login_required
def list_activities():
    if current_user.role == 'admin':
        activities = Activity.query.order_by(Activity.created_at.desc()).all()
    elif current_user.role == 'instructor':
        activities = Activity.query.join(Course).filter(Course.instructor_id == current_user.id).order_by(Activity.created_at.desc()).all()
    else:
        enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
        course_ids = [course.id for course in enrolled_courses]
        activities = Activity.query.filter(Activity.course_id.in_(course_ids)).order_by(Activity.created_at.desc()).all()
    
    return render_template('activities/activity_list.html', activities=activities)

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
            instructor_id=current_user.id
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
    db.session.commit()
    
    # Broadcast to all users in the activity room
    socketio.emit('activity_update', {
        'activity_id': activity_id,
        'update_type': 'started',
        'data': {
            'is_active': True,
            'started_at': activity.started_at.isoformat()
        }
    }, room=f'activity_{activity_id}')
    
    return jsonify({'success': True, 'message': 'Activity started'})

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
    
    # Check if answer is correct for quiz type
    is_correct = None
    score = 0.0
    if activity.type == 'quiz' and activity.correct_answer:
        is_correct = (answer.strip().lower() == activity.correct_answer.strip().lower())
        score = 1.0 if is_correct else 0.0
    
    existing_response = Response.query.filter_by(student_id=current_user.id, activity_id=activity_id).first()
    if existing_response:
        existing_response.answer = answer
        existing_response.is_correct = is_correct
        existing_response.score = score
        existing_response.submitted_at = datetime.utcnow()
    else:
        response = Response(
            student_id=current_user.id,
            activity_id=activity_id,
            answer=answer,
            is_correct=is_correct,
            score=score
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
    elif activity.type == 'word_cloud':
        # Process word cloud data
        all_words = []
        for response in responses:
            words = [word.strip().lower() for word in response.answer.split(',')]
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        common_words = word_freq.most_common(50)
        
        results = {
            'type': 'word_cloud',
            'word_frequency': common_words,
            'total_responses': len(responses)
        }
    else:
        answers = [response.answer for response in responses]
        word_freq = Counter()
        
        for answer in answers:
            words = re.findall(r'\b\w+\b', answer.lower())
            word_freq.update(words)
        
        common_words = word_freq.most_common(20)
        
        results = {
            'type': 'short_answer',
            'answers': answers,
            'word_frequency': common_words,
            'total_responses': len(responses)
        }
    
    return render_template('activities/activity_results.html', activity=activity, results=results, responses=responses)

@bp.route('/activities/generate_questions', methods=['POST'])
@login_required
def generate_questions_route():
    if current_user.role not in ['admin', 'instructor']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'message': 'Please enter teaching text'})
    
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
            words = re.findall(r'\b\w+\b', all_text.lower())
            word_freq = Counter(words)
            analytics['word_analysis'] = {
                'total_words': len(words),
                'unique_words': len(word_freq),
                'most_common': word_freq.most_common(10)
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
