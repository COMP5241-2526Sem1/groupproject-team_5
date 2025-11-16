from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, login_user
from app import db, socketio, get_beijing_time
from app.models import Course, Activity, Response, User, Enrollment
from app.forms import ActivityForm, AIQuestionForm
from app.ai_utils import generate_questions, generate_activity_from_content, group_answers, extract_text_from_file, validate_file_upload
from app.email_utils import send_temp_password_email
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import json
import re
import csv
import io
import time
import os
import tempfile
import secrets
import string
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
    per_page = 9  # Display 9 activities per page
    
    # Get courses for create activity dropdown
    user_courses = []
    if current_user.role == 'admin':
        activities = Activity.query.order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        user_courses = Course.query.order_by(Course.name).all()
    elif current_user.role == 'instructor':
        activities = Activity.query.join(Course).filter(
            Course.instructor_id == current_user.id
        ).order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        user_courses = Course.query.filter_by(instructor_id=current_user.id).order_by(Course.name).all()
    else:
        enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
        course_ids = [course.id for course in enrolled_courses]
        activities = Activity.query.filter(
            Activity.course_id.in_(course_ids)
        ).order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('activities/activity_list.html', activities=activities.items, pagination=activities, user_courses=user_courses)

def auto_end_activity(activity_id, duration_seconds, started_at_timestamp):
    """Background task: Automatically end activity
    
    Args:
        activity_id: Activity ID
        duration_seconds: Duration in seconds
        started_at_timestamp: Timestamp when activity was started (used to verify if it's the current start)
    """
    print(f"[AUTO-END] Starting timer for activity {activity_id}, will end in {duration_seconds} seconds")
    print(f"[AUTO-END] Started at timestamp: {started_at_timestamp}")
    time.sleep(duration_seconds)
    
    try:
        # Use global db and socketio to avoid circular imports
        from app import db, socketio
        from app.models import Activity
        from datetime import datetime
        
        # No need for app_context as we're in the same application process
        activity = Activity.query.get(activity_id)
        if activity:
            # Check if activity's started_at matches when the task was launched
            current_started_timestamp = activity.started_at.timestamp() if activity.started_at else 0
            
            print(f"[AUTO-END] Activity {activity_id} current started_at: {activity.started_at}")
            print(f"[AUTO-END] Current timestamp: {current_started_timestamp}")
            print(f"[AUTO-END] Expected timestamp: {started_at_timestamp}")
            
            # Only end if timestamp matches (indicates this is the current start task)
            if activity.is_active and abs(current_started_timestamp - started_at_timestamp) < 1:
                print(f"[AUTO-END] Auto-ending activity {activity_id}")
                activity.is_active = False
                activity.ended_at = get_beijing_time()
                db.session.commit()
                
                print(f"[AUTO-END] Activity {activity_id} ended at {activity.ended_at}")
                
                # Notify all users that activity has ended
                socketio.emit('activity_update', {
                    'activity_id': activity_id,
                    'update_type': 'auto_ended',
                    'data': {
                        'is_active': False,
                        'ended_at': activity.ended_at.isoformat(),
                        'message': 'Activity has ended automatically'
                    }
                }, room=f'activity_{activity_id}')
                
                print(f"[AUTO-END] Notification sent for activity {activity_id}")
            else:
                print(f"[AUTO-END] Activity {activity_id} was restarted or already ended, skipping auto-end")
        else:
            print(f"[AUTO-END] Activity {activity_id} not found")
    except Exception as e:
        print(f"[AUTO-END] Error in auto_end_activity: {e}")
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
        # Read activity duration (in seconds)
        duration_seconds = int(request.form.get('duration_seconds', 300))  # Default 5 minutes = 300 seconds
        duration_minutes = max(1, round(duration_seconds / 60))  # Calculate minutes for backward compatibility
        
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
        
        # Get quick join option
        allow_quick_join = request.form.get('allow_quick_join') == 'on'
        
        activity = Activity(
            title=form.title.data,
            type=form.type.data,
            question=form.question.data,
            quiz_type=quiz_type,
            options=options,
            correct_answer=correct_answer,
            course_id=course_id,
            instructor_id=current_user.id,
            duration_minutes=duration_minutes,  # For backward compatibility and display
            duration_seconds=duration_seconds,  # Precise duration (in seconds)
            allow_quick_join=allow_quick_join
        )
        
        # Generate token if quick join is allowed
        if allow_quick_join:
            activity.generate_join_token()
        
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
    
    # Generate QR code for instructors and admins
    qr_code = None
    if current_user.role in ['admin', 'instructor']:
        if current_user.role == 'admin' or activity.course.instructor_id == current_user.id:
            # Generate QR code if activity allows quick join and has token
            if activity.allow_quick_join:
                if not activity.join_token:
                    activity.generate_join_token()
                    db.session.commit()
                
                try:
                    from app.qr_utils import generate_activity_qr_code
                    qr_code = generate_activity_qr_code(activity, _external=True)
                except ImportError:
                    pass  # qrcode library not installed
    
    # Pass activity start time to frontend (using ISO format string)
    started_at_iso = None
    if activity.started_at:
        # Database stores Beijing time, pass ISO string to frontend
        started_at_iso = activity.started_at.isoformat()
    
    # Parse options (supports JSON format and newline-separated format)
    parsed_options = None
    if activity.options:
        try:
            # Try to parse as JSON first
            parsed = json.loads(activity.options)
            if isinstance(parsed, list):
                parsed_options = [str(opt).strip() for opt in parsed if opt]
            else:
                # If not a list, treat as newline-separated text
                parsed_options = [opt.strip() for opt in activity.options.split('\n') if opt.strip()]
        except (json.JSONDecodeError, ValueError, TypeError):
            # If not JSON, treat as newline-separated text
            parsed_options = [opt.strip() for opt in activity.options.split('\n') if opt.strip()]
    
    return render_template('activities/activity_detail.html', 
                         activity=activity, 
                         my_response=my_response,
                         qr_code=qr_code,
                         started_at_iso=started_at_iso,
                         parsed_options=parsed_options)

@bp.route('/activities/<int:activity_id>/start', methods=['POST'])
@login_required
def start_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    activity.is_active = True
    activity.started_at = get_beijing_time()
    # Clear previous end time, activity is now active
    activity.ended_at = None
    db.session.commit()
    
    print(f"[START] Activity {activity_id} started at {activity.started_at}")
    print(f"[START] is_active: {activity.is_active}")
    
    # Get start timestamp for verifying auto-end task
    started_at_timestamp = activity.started_at.timestamp()
    
    # Calculate activity duration (in seconds), prefer duration_seconds, otherwise use duration_minutes * 60
    duration_seconds = activity.duration_seconds if activity.duration_seconds else (activity.duration_minutes * 60)
    
    # Calculate expected end time (for display only)
    from datetime import timedelta
    will_end_at = activity.started_at + timedelta(seconds=duration_seconds)
    
    # Start background task to automatically end activity after specified time
    # Pass timestamp to ensure only the current start task will end the activity
    socketio.start_background_task(
        target=auto_end_activity, 
        activity_id=activity_id, 
        duration_seconds=duration_seconds,
        started_at_timestamp=started_at_timestamp
    )
    
    # Broadcast to all users in the activity room
    socketio.emit('activity_update', {
        'activity_id': activity_id,
        'update_type': 'started',
        'data': {
            'is_active': True,
            'started_at': activity.started_at.isoformat(),
            'duration_seconds': duration_seconds,  # Send seconds
            'duration_minutes': activity.duration_minutes,  # Backward compatibility
            'will_end_at': will_end_at.isoformat()
        }
    }, room=f'activity_{activity_id}')
    
    return jsonify({
        'success': True, 
        'message': f'Activity started for {duration_seconds} seconds',
        'duration_seconds': duration_seconds,  # Send seconds
        'duration_minutes': activity.duration_minutes,  # Backward compatibility
        'will_end_at': will_end_at.isoformat()
    })

@bp.route('/activities/<int:activity_id>/stop', methods=['POST'])
@login_required
def stop_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    if current_user.role not in ['admin', 'instructor'] or (current_user.role == 'instructor' and activity.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    activity.is_active = False
    activity.ended_at = get_beijing_time()
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
    
    # Reset activity status
    activity.is_active = False
    activity.started_at = None
    activity.ended_at = None
    
    # Clear all student response records (optional)
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
    
    # Add debug information
    print(f"[DEBUG] Activity {activity_id} submission attempt")
    print(f"[DEBUG] is_active: {activity.is_active}")
    print(f"[DEBUG] started_at: {activity.started_at}")
    print(f"[DEBUG] ended_at: {activity.ended_at}")
    
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
        normalized_answer = answer.lower().strip()
        normalized_correct = correct_answer.lower().strip()
        
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
        existing_response.submitted_at = get_beijing_time()
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
    try:
        from sqlalchemy.orm import joinedload
        
        # Load activity with course relationship
        activity = Activity.query.options(
            joinedload(Activity.course)
        ).get_or_404(activity_id)
        
        # Check permissions
        if current_user.role not in ['admin', 'instructor']:
            flash('Insufficient permissions', 'error')
            return redirect(url_for('main.dashboard'))
            
        if current_user.role == 'instructor' and activity.course.instructor_id != current_user.id:
            flash('Insufficient permissions', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Eager load student relationship to avoid N+1 queries
        responses = Response.query.options(
            joinedload(Response.student)
        ).filter_by(activity_id=activity_id).all()
        
        if activity.type == 'poll':
            # Handle both JSON format (from test data) and newline-separated format (from form)
            options = []
            if activity.options:
                try:
                    # Try to parse as JSON first
                    parsed_options = json.loads(activity.options)
                    if isinstance(parsed_options, list):
                        options = [str(opt).strip() for opt in parsed_options if opt]
                    else:
                        # If not a list, treat as newline-separated text
                        options = [opt.strip() for opt in activity.options.split('\n') if opt.strip()]
                except (json.JSONDecodeError, ValueError, TypeError):
                    # If not JSON, treat as newline-separated text
                    options = [opt.strip() for opt in activity.options.split('\n') if opt.strip()]
            
            option_counts = {}
            for option in options:
                if option:  # Only add non-empty options
                    option_counts[option] = 0
            
            # Count responses for each option
            for response in responses:
                if response.answer:
                    answer = response.answer.strip()
                    # Try exact match first
                    if answer in option_counts:
                        option_counts[answer] += 1
                    else:
                        # Try case-insensitive match
                        for option in option_counts.keys():
                            if answer.lower() == option.lower():
                                option_counts[option] += 1
                                break
            
            results = {
                'type': 'poll',
                'options': option_counts,
                'total_responses': len(responses)
            }
        elif activity.type == 'quiz':
            correct_count = sum(1 for r in responses if r.is_correct)
            average_score = sum(r.score or 0 for r in responses) / len(responses) if responses else 0
            
            # Parse options for multiple choice quiz
            options = []
            option_counts = {}
            option_labels = {}  # Map option text to label (A, B, C, D, ...)
            options_list = []  # Keep ordered list of options for display
            
            if activity.quiz_type == 'multiple_choice' and activity.options:
                try:
                    parsed_options = json.loads(activity.options)
                    if isinstance(parsed_options, list):
                        options = [str(opt).strip() for opt in parsed_options if opt]
                    else:
                        # If not a list, treat as newline-separated text
                        options = [opt.strip() for opt in activity.options.split('\n') if opt.strip()]
                except (json.JSONDecodeError, ValueError, TypeError):
                    # If not JSON, treat as newline-separated text
                    options = [opt.strip() for opt in activity.options.split('\n') if opt.strip()]
                
                # Create label mapping and initialize counts (A, B, C, D, ...)
                for idx, option in enumerate(options):
                    label = chr(65 + idx)  # 65 is 'A' in ASCII
                    option_labels[option] = label
                    option_counts[option] = 0
                    options_list.append(option)  # Keep order
            
            # Count responses for each option (for multiple choice quiz)
            if activity.quiz_type == 'multiple_choice' and options:
                for response in responses:
                    if response.answer:
                        answer = response.answer.strip()
                        # Try exact match first
                        if answer in option_counts:
                            option_counts[answer] += 1
                        else:
                            # Try case-insensitive match
                            for option in option_counts.keys():
                                if answer.lower() == option.lower():
                                    option_counts[option] += 1
                                    break
            
            results = {
                'type': 'quiz',
                'quiz_type': activity.quiz_type,
                'correct_count': correct_count,
                'total_responses': len(responses),
                'average_score': average_score,
                'options': option_counts if activity.quiz_type == 'multiple_choice' else None,
                'options_list': options_list if activity.quiz_type == 'multiple_choice' else None,  # Ordered list
                'option_labels': option_labels if activity.quiz_type == 'multiple_choice' else None,
                'responses': [{
                    'answer': r.answer or '', 
                    'answer_label': option_labels.get(r.answer or '', '') if activity.quiz_type == 'multiple_choice' and r.answer else '',
                    'is_correct': r.is_correct or False, 
                    'score': r.score or 0, 
                    'student': r.student.name if r.student else 'Unknown'
                } for r in responses]
            }
        elif activity.type == 'memory_game':
            correct_count = sum(1 for r in responses if r.is_correct)
            results = {
                'type': 'memory_game',
                'total_responses': len(responses),
                'correct_count': correct_count,
                'accuracy': (correct_count / len(responses) * 100) if responses else 0,
                'responses': [{
                    'student': r.student.name if r.student else 'Unknown',
                    'answer': r.answer or '',
                    'is_correct': r.is_correct or False,
                    'submitted_at': r.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if r.submitted_at else ''
                } for r in responses]
            }
        elif activity.type == 'word_cloud':
            # Process word cloud data - use same logic as short_answer
            answers = [response.answer for response in responses if response.answer]
            
            word_freq = Counter()
            
            for answer in answers:
                # Extract words from comma-separated list
                # First split by comma, then extract words from each part
                parts = [part.strip().lower() for part in answer.split(',') if part.strip()]
                for part in parts:
                    # Extract words using regex (handles multi-word entries)
                    words = re.findall(r'\b[a-zA-Z]+\b', part)
                    # Filter: remove stopwords and words shorter than 3 characters
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
            # short_answer type
            answers = [response.answer for response in responses if response.answer]
            
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
    
    except Exception as e:
        # Log the error
        import traceback
        print(f"❌ Error in activity_results: {str(e)}")
        print(traceback.format_exc())
        
        flash(f'Error loading activity results: {str(e)}', 'error')
        return redirect(url_for('activities.list_activities'))

@bp.route('/activities/generate_questions', methods=['POST'])
@login_required
def generate_questions_route():
    """AI question generation route - Enhanced error handling and logging"""
    if current_user.role not in ['admin', 'instructor']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'})
    
    text = ""
    
    # Check if it's a file upload request
    if 'file' in request.files:
        file = request.files['file']
        
        # Validate file
        is_valid, message = validate_file_upload(file)
        if not is_valid:
            print(f"❌ File validation failed: {message}")
            return jsonify({'success': False, 'message': message})
        
        # Save temporary file and extract text
        try:
            # Create temporary file
            file_extension = os.path.splitext(secure_filename(file.filename))[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            print(f"📄 Processing file: {file.filename}, extension: {file_extension}")
            
            # Extract text
            text = extract_text_from_file(temp_file_path, file_extension)
            print(f"✅ Extracted {len(text)} characters from file")
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"❌ File processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'File processing failed: {str(e)}'})
    
    else:
        # Process JSON request (original text input method)
        data = request.get_json()
        if not data:
            print("❌ No JSON data provided")
            return jsonify({'success': False, 'message': 'No data provided'})
        text = data.get('text', '').strip()
        print(f"📝 Received text input: {len(text)} characters")
    
    if not text:
        print("❌ Empty text provided")
        return jsonify({'success': False, 'message': 'Please enter teaching text or upload a file'})
    
    # Limit text length to avoid overly long input
    if len(text) > 10000:
        text = text[:10000]
        print(f"⚠️  Text truncated to 10000 characters")
    
    try:
        print("=" * 80)
        print(f"🤖 [ROUTE] Starting AI question generation...")
        print(f"   [ROUTE] User: {current_user.name} (ID: {current_user.id}, Role: {current_user.role})")
        print(f"   [ROUTE] Text length: {len(text)} characters")
        print(f"   [ROUTE] Text preview: {text[:100]}...")
        
        # Check environment variables
        ark_key = os.environ.get('ARK_API_KEY', '')
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        no_proxy = os.environ.get('no_proxy', '')
        print(f"   [ROUTE] ARK_API_KEY: {'SET (' + ark_key[:10] + '...' + ark_key[-5:] + ')' if ark_key else 'NOT SET'}")
        print(f"   [ROUTE] OPENAI_API_KEY: {'SET (' + openai_key[:10] + '...)' if openai_key else 'NOT SET'}")
        print(f"   [ROUTE] no_proxy: {no_proxy if no_proxy else 'NOT SET'}")
        print(f"   [ROUTE] Calling generate_questions()...")
        print("=" * 80)
        
        questions = generate_questions(text)
        
        print("=" * 80)
        print(f"✅ [ROUTE] Successfully generated {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            print(f"   [ROUTE] {i}. {q}")
        print("=" * 80)
        
        return jsonify({'success': True, 'questions': questions})
        
    except Exception as e:
        print("=" * 80)
        print(f"❌ [ROUTE] Question generation error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"   [ROUTE] Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        
        # Provide more detailed error information
        error_message = str(e)
        error_type = type(e).__name__
        if 'connection' in error_message.lower():
            error_message = f"[{error_type}] AI service connection failed. Please check network settings. Details: {error_message}"
        elif 'timeout' in error_message.lower():
            error_message = f"[{error_type}] AI service request timeout. Please try again. Details: {error_message}"
        elif 'api' in error_message.lower():
            error_message = f"[{error_type}] AI service API error. Details: {error_message}"
        else:
            error_message = f"[{error_type}] {error_message}"
        
        return jsonify({'success': False, 'message': f'Generation failed: {error_message}'})

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
#         # Admin can edit all activities
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


# ============ QR Code Quick Join Routes ============

@bp.route('/activity/join/<token>')
def quick_join(token):
    """Quick join activity via QR code token"""
    # Find activity
    activity = Activity.query.filter_by(join_token=token).first()
    
    if not activity:
        flash('Invalid activity link', 'error')
        return redirect(url_for('main.index'))
    
    # Check if token is valid
    if not activity.is_token_valid():
        flash('This activity link has expired or been disabled', 'error')
        return redirect(url_for('main.index'))
    
    # If already logged in
    if current_user.is_authenticated:
        # Check if already enrolled
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=activity.course_id
        ).first()
        
        # If not enrolled, automatically enroll
        if not enrollment:
            enrollment = Enrollment(
                student_id=current_user.id,
                course_id=activity.course_id
            )
            db.session.add(enrollment)
            db.session.commit()
            flash(f'Automatically enrolled in course: {activity.course.name}', 'success')
        
        # Redirect to activity detail page
        return redirect(url_for('activities.activity_detail', activity_id=activity.id))
    
    # If not logged in, redirect to quick register page
    return redirect(url_for('activities.quick_register', token=token))


@bp.route('/activity/quick-register/<token>', methods=['GET', 'POST'])
def quick_register(token):
    """Quick register and join activity"""
    # If already logged in, directly redirect to join flow
    if current_user.is_authenticated:
        return redirect(url_for('activities.quick_join', token=token))
    
    # Find activity
    activity = Activity.query.filter_by(join_token=token).first()
    
    if not activity:
        flash('Invalid activity link', 'error')
        return redirect(url_for('main.index'))
    
    # Check if token is valid
    if not activity.is_token_valid():
        flash('This activity link has expired or been disabled', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        
        if not name or not email:
            flash('Please enter name and email', 'error')
            return render_template('activities/quick_register.html', 
                                 activity=activity, 
                                 course=activity.course)
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            # If user already exists, prompt user to login
            flash(f'This email is already registered, please login with password', 'info')
            return redirect(url_for('auth.login', next=url_for('activities.quick_join', token=token)))
        else:
            # Create new user
            # Generate readable random password (8 characters, letters and numbers)
            characters = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(characters) for _ in range(8))
            
            user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(temp_password),
                role='student',
                student_id=User.generate_student_id()
            )
            db.session.add(user)
            
            # Don't commit yet, wait for email to be sent successfully
            db.session.flush()  # Get user.id but don't commit
            
            # Send temporary password to email (with timeout, non-blocking)
            email_sent = False
            email_error = None
            
            try:
                import signal
                
                # Define timeout handler
                def timeout_handler(signum, frame):
                    raise TimeoutError("Email sending timeout")
                
                # Set 10 second timeout (Unix systems only)
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(10)
                    email_sent = send_temp_password_email(email, name, temp_password)
                    signal.alarm(0)  # Cancel timeout
                except (AttributeError, ValueError):
                    # Windows doesn't support signal.SIGALRM, send directly
                    email_sent = send_temp_password_email(email, name, temp_password)
                    
            except TimeoutError:
                email_error = "Email sending timeout (10 seconds). Please check your network connection."
                email_sent = False
            except Exception as e:
                email_error = f"Email sending failed: {str(e)}"
                email_sent = False
            
            # Decide whether to create user based on email sending result
            if email_sent:
                # Email sent successfully, commit user
                try:
                    db.session.commit()
                    flash(f'✅ Account created successfully! Temporary password sent to {email}', 'success')
                    flash(f'📧 Please check your email (including spam folder) for the password', 'info')
                    # Redirect to login page, will auto-redirect to activity after login
                    return redirect(url_for('auth.login', next=url_for('activities.quick_join', token=token)))
                except Exception as db_error:
                    db.session.rollback()
                    flash(f'Account creation failed: {str(db_error)}', 'error')
                    return render_template('activities/quick_register.html', 
                                         activity=activity, 
                                         course=activity.course)
            else:
                # Email sending failed, rollback user creation
                db.session.rollback()
                flash('❌ Account creation failed: Unable to send verification email', 'error')
                flash(f'🔍 Reason: {email_error}', 'warning')
                flash('💡 Please check:', 'info')
                flash('   1. Make sure your email address is valid and active', 'info')
                flash('   2. Check your internet connection', 'info')
                flash('   3. Try again in a few moments', 'info')
                return render_template('activities/quick_register.html', 
                                     activity=activity, 
                                     course=activity.course)
    
    return render_template('activities/quick_register.html', 
                         activity=activity, 
                         course=activity.course)


@bp.route('/activity/<int:activity_id>/regenerate-qr', methods=['POST'])
@login_required
def regenerate_qr_code(activity_id):
    """Regenerate QR code token for activity"""
    activity = Activity.query.get_or_404(activity_id)
    course = Course.query.get_or_404(activity.course_id)
    
    # Permission check
    if current_user.role == 'admin':
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        pass
    else:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Regenerate token
    activity.generate_join_token()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'QR code regenerated successfully',
        'token': activity.join_token
    })


@bp.route('/activity/<int:activity_id>/toggle-quick-join', methods=['POST'])
@login_required
def toggle_quick_join(activity_id):
    """Toggle quick join feature for activity"""
    activity = Activity.query.get_or_404(activity_id)
    course = Course.query.get_or_404(activity.course_id)
    
    # Permission check
    if current_user.role == 'admin':
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        pass
    else:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Toggle status
    activity.allow_quick_join = not activity.allow_quick_join
    
    # If enabling quick join but no token exists, generate one
    if activity.allow_quick_join and not activity.join_token:
        activity.generate_join_token()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'allow_quick_join': activity.allow_quick_join,
        'message': 'Quick join ' + ('enabled' if activity.allow_quick_join else 'disabled')
    })
