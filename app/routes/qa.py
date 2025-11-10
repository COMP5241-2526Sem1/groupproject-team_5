"""
Q&A Feature Routes
Q&A system integrated into the classroom interaction platform
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Question, Answer, AnswerVote, Course, Enrollment
from datetime import datetime

qa_bp = Blueprint('qa', __name__)

@qa_bp.route('/course/<int:course_id>/qa')
@login_required
def course_qa_list(course_id):
    """Display course Q&A list"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user has permission to access this course
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id, 
            course_id=course_id
        ).first()
        if not enrollment:
            flash('You do not have permission to access this course', 'danger')
            return redirect(url_for('main.dashboard'))
    elif current_user.role == 'instructor' and course.instructor_id != current_user.id:
        flash('You do not have permission to access this course', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # 获取问题列表（按创建时间排序）
    page = request.args.get('page', 1, type=int)
    questions = Question.query.filter_by(course_id=course_id)\
        .order_by(Question.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('qa/question_list.html', 
                         course=course, 
                         questions=questions)

@qa_bp.route('/course/<int:course_id>/qa/ask', methods=['GET', 'POST'])
@login_required
def ask_question(course_id):
    """Ask question page"""
    course = Course.query.get_or_404(course_id)
    
    # Check permission
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id, 
            course_id=course_id
        ).first()
        if not enrollment:
            flash('You do not have permission to ask questions in this course', 'danger')
            return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            flash('Title and content cannot be empty', 'danger')
            return render_template('qa/ask_question.html', course=course)
        
        # Create question
        question = Question(
            title=title,
            content=content,
            course_id=course_id,
            author_id=current_user.id
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question published successfully!', 'success')
        return redirect(url_for('qa.course_qa_list', course_id=course_id))
    
    return render_template('qa/ask_question.html', course=course)

@qa_bp.route('/course/<int:course_id>/qa/<int:question_id>')
@login_required
def question_detail(course_id, question_id):
    """Question detail page"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    
    # Check if question belongs to this course
    if question.course_id != course_id:
        flash('Question does not exist', 'danger')
        return redirect(url_for('qa.course_qa_list', course_id=course_id))
    
    # Check permission
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id, 
            course_id=course_id
        ).first()
        if not enrollment:
            flash('You do not have permission to access this content', 'danger')
            return redirect(url_for('main.dashboard'))
    elif current_user.role == 'instructor' and course.instructor_id != current_user.id:
        flash('You do not have permission to access this content', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # 获取答案（按投票数和创建时间排序，添加分页）
    page = request.args.get('page', 1, type=int)
    answers_query = Answer.query.filter_by(question_id=question_id)\
        .order_by(Answer.upvotes.desc(), Answer.created_at.asc())
    
    # 如果有最佳答案，将其置顶
    best_answer = None
    if question.best_answer_id:
        best_answer = Answer.query.get(question.best_answer_id)
        answers_query = answers_query.filter(Answer.id != question.best_answer_id)
    
    answers_pagination = answers_query.paginate(page=page, per_page=5, error_out=False)
    answers = answers_pagination.items
    
    # 将最佳答案添加到列表开头
    if best_answer:
        answers.insert(0, best_answer)
    
    return render_template('qa/question_detail.html', 
                         course=course, 
                         question=question,
                         answers=answers,
                         answers_pagination=answers_pagination)

@qa_bp.route('/course/<int:course_id>/qa/<int:question_id>/answer', methods=['POST'])
@login_required
def submit_answer(course_id, question_id):
    """Submit answer"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Answer content cannot be empty', 'danger')
        return redirect(url_for('qa.question_detail', 
                              course_id=course_id, 
                              question_id=question_id))
    
    # Check if this is an instructor answer
    is_instructor_answer = (current_user.role == 'instructor' and 
                           course.instructor_id == current_user.id)
    
    # Create answer
    answer = Answer(
        content=content,
        question_id=question_id,
        author_id=current_user.id,
        is_instructor_answer=is_instructor_answer
    )
    
    db.session.add(answer)
    db.session.commit()
    
    flash('Answer submitted successfully!', 'success')
    return redirect(url_for('qa.question_detail', 
                          course_id=course_id, 
                          question_id=question_id))

@qa_bp.route('/answer/<int:answer_id>/vote', methods=['POST'])
@login_required
def vote_answer(answer_id):
    """Vote on answer"""
    answer = Answer.query.get_or_404(answer_id)
    vote_type = request.json.get('vote_type')  # 'upvote' or 'downvote'
    
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({'success': False, 'message': 'Invalid vote type'})
    
    # Check if already voted
    existing_vote = AnswerVote.query.filter_by(
        answer_id=answer_id,
        user_id=current_user.id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Cancel vote
            db.session.delete(existing_vote)
            if vote_type == 'upvote':
                answer.upvotes = max(0, answer.upvotes - 1)
        else:
            # Change vote type
            existing_vote.vote_type = vote_type
            if vote_type == 'upvote':
                answer.upvotes += 1
            else:
                answer.upvotes = max(0, answer.upvotes - 1)
    else:
        # New vote
        vote = AnswerVote(
            answer_id=answer_id,
            user_id=current_user.id,
            vote_type=vote_type
        )
        db.session.add(vote)
        if vote_type == 'upvote':
            answer.upvotes += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'upvotes': answer.upvotes,
        'message': 'Vote successful'
    })

@qa_bp.route('/question/<int:question_id>/mark_best/<int:answer_id>', methods=['POST'])
@login_required
def mark_best_answer(question_id, answer_id):
    """Mark best answer (instructors only)"""
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.get_or_404(answer_id)
    
    # Check permission (must be course instructor)
    if (current_user.role != 'instructor' or 
        question.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action'})
    
    # Check if answer belongs to this question
    if answer.question_id != question_id:
        return jsonify({'success': False, 'message': 'Answer does not belong to this question'})
    
    # Update best answer
    question.best_answer_id = answer_id
    question.is_resolved = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Marked as best answer'})

@qa_bp.route('/course/<int:course_id>/qa/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(course_id, question_id):
    """Delete question - Admin and instructor permission"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    
    # Check if question belongs to this course
    if question.course_id != course_id:
        return jsonify({'success': False, 'message': 'Question does not exist'})
    
    # Check permission - only admin can delete any question, instructors can delete questions in their own courses
    if current_user.role == 'admin':
        # Admin can delete any question
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        # Instructor can delete questions in their own courses
        pass
    else:
        return jsonify({'success': False, 'message': 'You do not have permission to delete this question'})
    
    try:
        # Step 1: Clear best_answer_id to avoid foreign key constraint
        if question.best_answer_id:
            question.best_answer_id = None
            db.session.flush()  # Apply this change first
        
        # Step 2: Delete related vote records
        for answer in question.answers:
            AnswerVote.query.filter_by(answer_id=answer.id).delete()
        
        # Step 3: Delete all answers
        Answer.query.filter_by(question_id=question_id).delete()
        
        # Step 4: Delete the question itself
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Question deleted successfully',
            'redirect_url': url_for('qa.course_qa_list', course_id=course_id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Delete failed: {str(e)}'})

@qa_bp.route('/course/<int:course_id>/qa/<int:question_id>/delete_answer/<int:answer_id>', methods=['POST'])
@login_required  
def delete_answer(course_id, question_id, answer_id):
    """Delete answer - Admin and instructor permission"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.get_or_404(answer_id)
    
    # Check permission - admin, instructor or answer author can delete
    if current_user.role == 'admin':
        # Admin can delete any answer
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        # Instructor can delete answers in their own courses
        pass
    elif answer.user_id == current_user.id:
        # User can delete their own answer
        pass
    else:
        return jsonify({'success': False, 'message': 'You do not have permission to delete this answer'})
    
    try:
        # Delete related vote records
        AnswerVote.query.filter_by(answer_id=answer_id).delete()
        
        # If this is the best answer, clear the best answer mark
        if question.best_answer_id == answer_id:
            question.best_answer_id = None
            question.is_resolved = False
        
        # Delete answer
        db.session.delete(answer)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Answer deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Delete failed: {str(e)}'})
