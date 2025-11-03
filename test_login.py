#!/usr/bin/env python3
"""
测试登录功能脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash
from flask_login import login_user

def test_login():
    """测试登录功能"""
    app = create_app()
    
    with app.app_context():
        # 测试数据
        test_accounts = [
            ('admin@example.com', 'admin123'),
            ('teacher@example.com', 'teacher123'),
            ('student@example.com', 'student123'),
            ('ruonan111421@163.com', '123456')  # 如果有的话
        ]
        
        print("🔐 测试登录功能")
        print("=" * 50)
        
        for email, password in test_accounts:
            print(f"\n📧 测试账户: {email}")
            print(f"🔑 测试密码: {password}")
            
            # 查找用户
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"✅ 用户存在: {user.name} ({user.role})")
                
                # 验证密码
                if check_password_hash(user.password_hash, password):
                    print(f"✅ 密码验证成功")
                    
                    # 测试登录后的跳转
                    if user.role == 'admin':
                        dashboard = 'admin_dashboard'
                    elif user.role == 'instructor':
                        dashboard = 'instructor_dashboard'
                    else:
                        dashboard = 'student_dashboard'
                    
                    print(f"📊 应跳转到: {dashboard}")
                    
                else:
                    print(f"❌ 密码验证失败")
                    
                    # 尝试其他可能的密码
                    other_passwords = ['123456', 'password', '111111', 'abc123']
                    print("🔍 尝试其他常见密码:")
                    for test_pwd in other_passwords:
                        if check_password_hash(user.password_hash, test_pwd):
                            print(f"   ✅ 正确密码: {test_pwd}")
                            break
                    else:
                        print("   ❌ 未找到正确密码")
                        
            else:
                print(f"❌ 用户不存在")
                
        print("\n" + "=" * 50)
        print("📋 登录测试总结:")
        print("1. 管理员: admin@example.com / admin123")
        print("2. 教师: teacher@example.com / teacher123") 
        print("3. 学生: student@example.com / student123")
        print("\n💡 如果登录失败，请检查:")
        print("   - 邮箱地址是否正确 (区分大小写)")
        print("   - 密码是否正确 (区分大小写)")
        print("   - 用户是否存在于数据库中")
        print("   - 网络连接是否正常")

def debug_user_password(email):
    """调试特定用户的密码"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"🔍 调试用户: {email}")
            print(f"用户名: {user.name}")
            print(f"角色: {user.role}")
            print(f"密码哈希: {user.password_hash[:20]}...")
            
            # 测试多个密码
            test_passwords = [
                'teacher123', 'Teacher123', 'TEACHER123',
                '123456', 'password', 'admin123',
                'instructor123', 'Instructor123'
            ]
            
            print("\n密码测试结果:")
            for pwd in test_passwords:
                result = check_password_hash(user.password_hash, pwd)
                status = "✅" if result else "❌"
                print(f"  {status} {pwd}")
                
        else:
            print(f"❌ 用户 {email} 不存在")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 调试特定用户
        debug_user_password(sys.argv[1])
    else:
        # 测试所有用户
        test_login()
