"""
Q&A功能路由
集成到课堂互动平台中的问答系统
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
    """显示课程的Q&A列表"""
    course = Course.query.get_or_404(course_id)
    
    # 检查用户是否有权限访问此课程
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id, 
            course_id=course_id
        ).first()
        if not enrollment:
            flash('您没有权限访问此课程', 'danger')
            return redirect(url_for('main.dashboard'))
    elif current_user.role == 'instructor' and course.instructor_id != current_user.id:
        flash('您没有权限访问此课程', 'danger')
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
    """提问页面"""
    course = Course.query.get_or_404(course_id)
    
    # 检查权限
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id, 
            course_id=course_id
        ).first()
        if not enrollment:
            flash('您没有权限在此课程中提问', 'danger')
            return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return render_template('qa/ask_question.html', course=course)
        
        # 创建问题
        question = Question(
            title=title,
            content=content,
            course_id=course_id,
            author_id=current_user.id
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('问题发布成功！', 'success')
        return redirect(url_for('qa.course_qa_list', course_id=course_id))
    
    return render_template('qa/ask_question.html', course=course)

@qa_bp.route('/course/<int:course_id>/qa/<int:question_id>')
@login_required
def question_detail(course_id, question_id):
    """问题详情页"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    
    # 检查问题是否属于该课程
    if question.course_id != course_id:
        flash('问题不存在', 'danger')
        return redirect(url_for('qa.course_qa_list', course_id=course_id))
    
    # 检查权限
    if current_user.role == 'student':
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id, 
            course_id=course_id
        ).first()
        if not enrollment:
            flash('您没有权限访问此内容', 'danger')
            return redirect(url_for('main.dashboard'))
    elif current_user.role == 'instructor' and course.instructor_id != current_user.id:
        flash('您没有权限访问此内容', 'danger')
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
    """提交答案"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('回答内容不能为空', 'danger')
        return redirect(url_for('qa.question_detail', 
                              course_id=course_id, 
                              question_id=question_id))
    
    # 检查是否为教师回答
    is_instructor_answer = (current_user.role == 'instructor' and 
                           course.instructor_id == current_user.id)
    
    # 创建答案
    answer = Answer(
        content=content,
        question_id=question_id,
        author_id=current_user.id,
        is_instructor_answer=is_instructor_answer
    )
    
    db.session.add(answer)
    db.session.commit()
    
    flash('回答提交成功！', 'success')
    return redirect(url_for('qa.question_detail', 
                          course_id=course_id, 
                          question_id=question_id))

@qa_bp.route('/answer/<int:answer_id>/vote', methods=['POST'])
@login_required
def vote_answer(answer_id):
    """对答案投票"""
    answer = Answer.query.get_or_404(answer_id)
    vote_type = request.json.get('vote_type')  # 'upvote' or 'downvote'
    
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({'success': False, 'message': '无效的投票类型'})
    
    # 检查是否已投票
    existing_vote = AnswerVote.query.filter_by(
        answer_id=answer_id,
        user_id=current_user.id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # 取消投票
            db.session.delete(existing_vote)
            if vote_type == 'upvote':
                answer.upvotes = max(0, answer.upvotes - 1)
        else:
            # 改变投票类型
            existing_vote.vote_type = vote_type
            if vote_type == 'upvote':
                answer.upvotes += 1
            else:
                answer.upvotes = max(0, answer.upvotes - 1)
    else:
        # 新投票
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
        'message': '投票成功'
    })

@qa_bp.route('/question/<int:question_id>/mark_best/<int:answer_id>', methods=['POST'])
@login_required
def mark_best_answer(question_id, answer_id):
    """标记最佳答案（仅教师可操作）"""
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.get_or_404(answer_id)
    
    # 检查权限（必须是课程教师）
    if (current_user.role != 'instructor' or 
        question.course.instructor_id != current_user.id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    # 检查答案是否属于该问题
    if answer.question_id != question_id:
        return jsonify({'success': False, 'message': '答案不属于该问题'})
    
    # 更新最佳答案
    question.best_answer_id = answer_id
    question.is_resolved = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已标记为最佳答案'})

@qa_bp.route('/course/<int:course_id>/qa/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(course_id, question_id):
    """删除问题 - 仅管理员权限"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    
    # 检查问题是否属于该课程
    if question.course_id != course_id:
        return jsonify({'success': False, 'message': '问题不存在'})
    
    # 检查权限 - 只有管理员可以删除任何问题，教师可以删除自己课程的问题
    if current_user.role == 'admin':
        # 管理员可以删除任何问题
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        # 教师可以删除自己课程的问题
        pass
    else:
        return jsonify({'success': False, 'message': '您没有权限删除此问题'})
    
    try:
        # 删除相关的投票记录
        for answer in question.answers:
            AnswerVote.query.filter_by(answer_id=answer.id).delete()
        
        # 删除所有回答
        Answer.query.filter_by(question_id=question_id).delete()
        
        # 删除问题
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '问题已成功删除',
            'redirect_url': url_for('qa.course_qa_list', course_id=course_id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

@qa_bp.route('/course/<int:course_id>/qa/<int:question_id>/delete_answer/<int:answer_id>', methods=['POST'])
@login_required  
def delete_answer(course_id, question_id, answer_id):
    """删除回答 - 管理员和教师权限"""
    course = Course.query.get_or_404(course_id)
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.get_or_404(answer_id)
    
    # 检查权限 - 管理员、教师或回答者本人可以删除
    if current_user.role == 'admin':
        # 管理员可以删除任何回答
        pass
    elif current_user.role == 'instructor' and course.instructor_id == current_user.id:
        # 教师可以删除自己课程的回答
        pass
    elif answer.user_id == current_user.id:
        # 用户可以删除自己的回答
        pass
    else:
        return jsonify({'success': False, 'message': '您没有权限删除此回答'})
    
    try:
        # 删除相关投票记录
        AnswerVote.query.filter_by(answer_id=answer_id).delete()
        
        # 如果是最佳答案，清除最佳答案标记
        if question.best_answer_id == answer_id:
            question.best_answer_id = None
            question.is_resolved = False
        
        # 删除回答
        db.session.delete(answer)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '回答已成功删除'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})
