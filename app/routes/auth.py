from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from app import db, mail
from app.models import User, EmailCaptcha
from app.forms import LoginForm, RegistrationForm
import string
import random
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
            if datetime.utcnow() - email_captcha.create_time > timedelta(minutes=5):
                flash('验证码已过期，请重新获取', 'error')
                EmailCaptcha.query.filter_by(email=form.email.data).delete()
                db.session.commit()
                print(f"DEBUG: Captcha expired")
                return render_template('auth/register.html', form=form)
        
        # 创建用户
        user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            student_id=form.student_id.data if form.role.data == 'student' else None
        )
        db.session.add(user)
        
        # 删除验证码记录
        EmailCaptcha.query.filter_by(email=form.email.data).delete()
        db.session.commit()
        
        # 自动登录用户
        login_user(user, remember=True)
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

@bp.route('/logout')
def logout():
    logout_user()
    # 不在首页显示logout flash消息
    return redirect(url_for('main.index'))
