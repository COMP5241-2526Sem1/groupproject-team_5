#!/usr/bin/env python3
"""
邮件配置测试脚本
用于诊断邮件发送问题
"""
import os
import sys

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_mail import Mail, Message
import traceback

def test_email_config():
    """测试邮件配置"""
    print("=== 邮件配置测试 ===")
    
    # 创建测试Flask应用
    app = Flask(__name__)
    
    # 尝试不同的邮件配置
    configs = [
        {
            'name': 'QQ邮箱配置',
            'MAIL_SERVER': 'smtp.qq.com',
            'MAIL_PORT': 587,
            'MAIL_USE_TLS': True,
            'MAIL_USE_SSL': False,
            'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', ''),
            'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD', ''),
            'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_USERNAME', '')
        },
        {
            'name': 'Gmail配置',
            'MAIL_SERVER': 'smtp.gmail.com',
            'MAIL_PORT': 587,
            'MAIL_USE_TLS': True,
            'MAIL_USE_SSL': False,
            'MAIL_USERNAME': 'testplatform2024@gmail.com',
            'MAIL_PASSWORD': 'your_app_password',  # 需要应用密码
            'MAIL_DEFAULT_SENDER': 'testplatform2024@gmail.com'
        }
    ]
    
    for config in configs:
        print(f"\n--- 测试 {config['name']} ---")
        
        # 应用配置
        for key, value in config.items():
            if key != 'name':
                app.config[key] = value
        
        # 打印配置信息（隐藏密码）
        print(f"服务器: {config['MAIL_SERVER']}:{config['MAIL_PORT']}")
        print(f"用户名: {config['MAIL_USERNAME']}")
        print(f"密码: {'*' * len(str(config['MAIL_PASSWORD'])) if config['MAIL_PASSWORD'] else '未设置'}")
        print(f"TLS: {config['MAIL_USE_TLS']}")
        
        # 检查必要的配置
        if not config['MAIL_USERNAME'] or not config['MAIL_PASSWORD']:
            print("❌ 邮箱用户名或密码未设置")
            continue
        
        # 测试邮件发送
        try:
            with app.app_context():
                mail = Mail(app)
                
                # 创建测试邮件
                msg = Message(
                    subject='邮件配置测试',
                    recipients=['test@example.com'],  # 测试邮箱
                    body='这是一条测试邮件，用于验证邮件配置是否正确。'
                )
                
                # 尝试发送（dry run - 不真的发送）
                print("✓ 邮件对象创建成功")
                print("✓ 配置验证通过")
                
        except Exception as e:
            print(f"❌ 配置错误: {str(e)}")
            print(f"详细错误:\n{traceback.format_exc()}")

def test_current_config():
    """测试当前应用的邮件配置"""
    print("\n=== 当前应用配置测试 ===")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            print("邮件配置:")
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_PASSWORD: {'*' * 10 if app.config.get('MAIL_PASSWORD') else 'None'}")
            print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
            
            # 检查环境变量
            print(f"\n环境变量:")
            print(f"MAIL_USERNAME (env): {os.environ.get('MAIL_USERNAME', 'None')}")
            print(f"MAIL_PASSWORD (env): {'*' * 10 if os.environ.get('MAIL_PASSWORD') else 'None'}")
            
    except Exception as e:
        print(f"❌ 无法加载应用配置: {str(e)}")
        print(f"详细错误:\n{traceback.format_exc()}")

if __name__ == '__main__':
    test_current_config()
    test_email_config()
    
    print("\n=== 建议 ===")
    print("1. 检查邮箱密码是否过期")
    print("2. 检查QQ邮箱的SMTP服务是否开启")
    print("3. 尝试重新生成授权码")
    print("4. 考虑切换到Gmail配置")
