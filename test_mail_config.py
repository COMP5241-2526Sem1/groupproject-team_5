#!/usr/bin/env python3
"""
测试邮件发送功能
"""
import os
import sys

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mail_config():
    """测试邮件配置"""
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            # 检查配置
            print("📧 邮件配置检查：")
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_PASSWORD: {'***' if app.config.get('MAIL_PASSWORD') else 'None'}")
            
            # 测试发送邮件
            from flask_mail import Message
            from app import mail
            
            print("\n📤 测试发送邮件...")
            msg = Message(
                subject='测试邮件',
                recipients=['test@example.com'],  # 这个不会真的发送，只是测试连接
                body='这是一个测试邮件'
            )
            
            # 尝试连接邮件服务器
            with mail.connect() as conn:
                print("✅ 邮件服务器连接成功！")
                # 不实际发送邮件，只测试连接
                
        except Exception as e:
            print(f"❌ 邮件配置测试失败: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_mail_config()
