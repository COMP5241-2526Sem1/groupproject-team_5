"""
Email utility functions for sending emails
"""

from flask import render_template_string
from flask_mail import Message
from app import mail
import logging

logger = logging.getLogger(__name__)


def send_temp_password_email(recipient_email, user_name, temp_password):
    """
    Send temporary password email to new user
    
    Args:
        recipient_email: User's email address
        user_name: User's name
        temp_password: Generated temporary password
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email subject
        subject = "欢迎！您的临时密码"
        
        # HTML email template
        html_body = f"""
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
                .password-box {{
                    background: white;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .password {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 2px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                }}
                .btn {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎓 欢迎加入问答平台</h1>
            </div>
            
            <div class="content">
                <h2>你好，{user_name}！</h2>
                
                <p>您的账号已通过二维码快速注册成功创建。</p>
                
                <p>以下是您的临时密码：</p>
                
                <div class="password-box">
                    <div class="password">{temp_password}</div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ 重要安全提示：</strong>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>这是一个<strong>临时密码</strong></li>
                        <li>请在首次登录后<strong>立即更改密码</strong></li>
                        <li>不要与任何人分享此密码</li>
                        <li>更改密码后请妥善保管或删除此邮件</li>
                    </ul>
                </div>
                
                <h3>如何登录：</h3>
                <ol>
                    <li>访问平台登录页面</li>
                    <li>输入您的邮箱：<strong>{recipient_email}</strong></li>
                    <li>输入上面的临时密码</li>
                    <li>进入个人资料页面更改密码</li>
                </ol>
                
                <p style="margin-top: 30px;">如果您没有请求此账号，请忽略此邮件。</p>
            </div>
            
            <div class="footer">
                <p>这是一封自动发送的邮件，请勿回复。</p>
                <p>© 2024 问答教育平台。保留所有权利。</p>
            </div>
        </body>
        </html>
        """
        
        # Plain text alternative
        text_body = f"""
Welcome to Q&A Platform!

Hello, {user_name}!

Your account has been successfully created through QR code quick registration.

Your temporary password is: {temp_password}

IMPORTANT SECURITY NOTICE:
- This is a temporary password
- Please change it immediately after your first login
- Do not share this password with anyone

How to login:
1. Visit the platform login page
2. Enter your email: {recipient_email}
3. Enter the temporary password above
4. Go to your profile and change your password

If you didn't request this account, please ignore this email.

---
This is an automated email. Please do not reply.
© 2024 Q&A Education Platform. All rights reserved.
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=text_body,
            html=html_body
        )
        
        # Send email with timeout handling
        try:
            mail.send(msg)
            logger.info(f"Temporary password email sent successfully to {recipient_email}")
            return True
        except Exception as mail_error:
            logger.error(f"Failed to send email to {recipient_email}: {str(mail_error)}")
            return False
        
    except Exception as e:
        logger.error(f"Error preparing email for {recipient_email}: {str(e)}")
        return False


def send_password_reset_email(recipient_email, user_name, reset_link):
    """
    Send password reset email (for future implementation)
    
    Args:
        recipient_email: User's email address
        user_name: User's name
        reset_link: Password reset link
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = "Password Reset Request"
        
        html_body = f"""
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
                .btn {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 Password Reset</h1>
            </div>
            
            <div class="content">
                <h2>Hello, {user_name}!</h2>
                
                <p>We received a request to reset your password.</p>
                
                <p style="text-align: center;">
                    <a href="{reset_link}" class="btn">Reset Password</a>
                </p>
                
                <p>If you didn't request this, please ignore this email.</p>
                
                <p><small>This link will expire in 24 hours.</small></p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Hello, {user_name}!

We received a request to reset your password.

Click the link below to reset your password:
{reset_link}

If you didn't request this, please ignore this email.

This link will expire in 24 hours.
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=text_body,
            html=html_body
        )
        
        mail.send(msg)
        logger.info(f"Password reset email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {recipient_email}: {str(e)}")
        return False
