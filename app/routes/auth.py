from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from app import db, mail
from app.models import User, EmailCaptcha
from app.forms import LoginForm, RegistrationForm
from app.email_utils import send_temp_password_email
from app.utils import beijing_now
import string
import random
import secrets
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if request.method == 'POST':
        print(f"DEBUG: POST request received")
        print(f"DEBUG: Form data: {dict(request.form)}")
        
        if form.validate_on_submit():
            print(f"DEBUG: Form validation passed for email: {form.email.data}")
            # 验证邮箱验证码
            email_captcha = EmailCaptcha.query.filter_by(
                email=form.email.data, 
                captcha=form.captcha.data
            ).first()
            
            print(f"DEBUG: Looking for captcha {form.captcha.data} for email {form.email.data}")
            
            if not email_captcha:
                flash('验证码错误或已过期', 'error')
                print(f"DEBUG: Captcha not found or expired")
                return render_template('auth/register.html', form=form)
            
            # 检查验证码是否过期（5分钟）
            if beijing_now().replace(tzinfo=None) - email_captcha.create_time > timedelta(minutes=5):
                flash('验证码已过期，请重新获取', 'error')
                EmailCaptcha.query.filter_by(email=form.email.data).delete()
                db.session.commit()
                print(f"DEBUG: Captcha expired")
                return render_template('auth/register.html', form=form)
        
        # 为学生自动生成学生ID
        student_id = None
        if form.role.data == 'student':
            student_id = User.generate_student_id()
        elif form.role.data == 'instructor' and form.student_id.data:
            student_id = form.student_id.data
        
        # 创建用户
        user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            student_id=student_id
        )
        db.session.add(user)
        
        # 删除验证码记录
        EmailCaptcha.query.filter_by(email=form.email.data).delete()
        db.session.commit()
        
        # 自动登录用户
        login_user(user, remember=True)
        if form.role.data == 'student':
            flash(f'注册成功！欢迎您，{user.name}！您的学号是：{student_id}', 'success')
        else:
            flash(f'注册成功！欢迎您，{user.name}！', 'success')
        print(f"DEBUG: User {user.name} registered successfully, redirecting to dashboard")
        return redirect(url_for('main.dashboard'))
    else:
        print(f"DEBUG: Form validation failed: {form.errors}")
    
    return render_template('auth/register.html', form=form)

@bp.route('/send_email_captcha', methods=['POST'])
def send_email_captcha():
    """发送邮箱验证码"""
    email = request.json.get('email')
    
    if not email:
        return jsonify({'code': 400, 'message': '邮箱不能为空'})
    
    # 检查邮箱是否已注册
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'code': 400, 'message': '该邮箱已注册'})
    
    # 生成6位随机验证码
    captcha = ''.join(random.choices(string.digits, k=6))
    
    # 删除该邮箱之前的验证码
    EmailCaptcha.query.filter_by(email=email).delete()
    
    # 保存新验证码
    email_captcha = EmailCaptcha(email=email, captcha=captcha)
    db.session.add(email_captcha)
    db.session.commit()
    
    # 发送邮件
    try:
        message = Message(
            subject='教室互动平台 - 邮箱验证码',
            recipients=[email],
            body=f'''
亲爱的用户：

感谢您注册教室互动平台！

您的邮箱验证码是：{captcha}

验证码有效期为5分钟，请及时使用。

如果这不是您的操作，请忽略此邮件。

教室互动平台团队
            '''
        )
        mail.send(message)
        return jsonify({'code': 200, 'message': '验证码发送成功！请查收邮件'})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'验证码发送失败：{str(e)}'})

@bp.route('/profile')
@login_required
def profile():
    """用户个人信息页面"""
    return render_template('auth/profile.html', user=current_user)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证当前密码
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return render_template('auth/change_password.html')
        
        # 验证新密码
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('auth/change_password.html')
        
        # 更新密码
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码 - 通过邮箱验证码重置"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        captcha = request.form.get('captcha', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # 验证用户是否存在
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email not found. Please check your email or register first.', 'error')
            return render_template('auth/forgot_password.html')
        
        # 验证验证码
        email_captcha = EmailCaptcha.query.filter_by(
            email=email,
            captcha=captcha
        ).first()
        
        if not email_captcha:
            flash('Invalid or expired verification code', 'error')
            return render_template('auth/forgot_password.html')
        
        # 检查验证码是否过期（5分钟）
        if beijing_now().replace(tzinfo=None) - email_captcha.create_time > timedelta(minutes=5):
            flash('Verification code expired. Please request a new one.', 'error')
            EmailCaptcha.query.filter_by(email=email).delete()
            db.session.commit()
            return render_template('auth/forgot_password.html')
        
        # 验证新密码
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('auth/forgot_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/forgot_password.html')
        
        # 更新密码
        user.password_hash = generate_password_hash(new_password)
        
        # 删除验证码
        EmailCaptcha.query.filter_by(email=email).delete()
        db.session.commit()
        
        flash('Password reset successfully! Please login with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@bp.route('/send_reset_captcha', methods=['POST'])
def send_reset_captcha():
    """发送密码重置验证码"""
    email = request.json.get('email')
    
    if not email:
        return jsonify({'code': 400, 'message': 'Email cannot be empty'})
    
    # 检查邮箱是否已注册
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'code': 400, 'message': 'Email not registered'})
    
    # 生成6位随机验证码
    captcha = ''.join(random.choices(string.digits, k=6))
    
    # 删除该邮箱之前的验证码
    EmailCaptcha.query.filter_by(email=email).delete()
    
    # 保存新验证码
    email_captcha = EmailCaptcha(email=email, captcha=captcha)
    db.session.add(email_captcha)
    db.session.commit()
    
    # 发送邮件
    try:
        message = Message(
            subject='Q&A Platform - Password Reset Code',
            recipients=[email],
            body=f'''
Dear {user.name},

You requested to reset your password.

Your verification code is: {captcha}

This code is valid for 5 minutes.

If you did not request this, please ignore this email.

Q&A Education Platform Team
            ''',
            html=f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .code-box {{
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }}
        .code {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔐 Password Reset Request</h1>
    </div>
    
    <div class="content">
        <h2>Hello, {user.name}!</h2>
        
        <p>You requested to reset your password on Q&A Platform.</p>
        
        <p>Your verification code is:</p>
        
        <div class="code-box">
            <div class="code">{captcha}</div>
        </div>
        
        <div class="warning">
            <strong>⚠️ Important:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>This code is valid for <strong>5 minutes</strong></li>
                <li>Do not share this code with anyone</li>
                <li>If you didn't request this, please ignore this email</li>
            </ul>
        </div>
        
        <p>If you didn't request this password reset, you can safely ignore this email. Your password will not be changed.</p>
    </div>
</body>
</html>
            '''
        )
        mail.send(message)
        return jsonify({'code': 200, 'message': 'Verification code sent! Please check your email.'})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'Failed to send email: {str(e)}'})

@bp.route('/logout')
def logout():
    logout_user()
    # 不在首页显示logout flash消息
    return redirect(url_for('main.index'))
