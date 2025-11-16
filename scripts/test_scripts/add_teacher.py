#!/usr/bin/env python3
"""
手动添加教师用户脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def add_teacher_user():
    """手动添加教师用户"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已存在该教师
        existing_teacher = User.query.filter_by(email='teacher@example.com').first()
        
        if existing_teacher:
            print(f"📋 教师用户已存在:")
            print(f"   邮箱: {existing_teacher.email}")
            print(f"   姓名: {existing_teacher.name}")
            print(f"   角色: {existing_teacher.role}")
            print(f"   ID: {existing_teacher.id}")
            
            # 重置密码
            response = input("是否重置密码为 'teacher123'? (y/n): ")
            if response.lower() == 'y':
                existing_teacher.password_hash = generate_password_hash('teacher123')
                db.session.commit()
                print("✅ 密码已重置为 'teacher123'")
            
        else:
            print("📊 创建新的教师用户...")
            
            # 创建教师用户
            teacher = User(
                email='teacher@example.com',
                password_hash=generate_password_hash('teacher123'),
                role='instructor',
                name='张老师'
            )
            
            try:
                db.session.add(teacher)
                db.session.commit()
                print("✅ 教师用户创建成功!")
                print("📋 账户信息:")
                print("   邮箱: teacher@example.com")
                print("   密码: teacher123")
                print("   姓名: 张老师")
                print("   角色: instructor")
                
            except Exception as e:
                print(f"❌ 创建失败: {e}")
                db.session.rollback()

def check_all_users():
    """检查所有用户"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        print(f"\n📊 数据库中的所有用户 (共 {len(users)} 个):")
        print("-" * 60)
        
        for user in users:
            role_icon = {
                'admin': '👑',
                'instructor': '👨‍🏫',
                'student': '👨‍🎓'
            }.get(user.role, '👤')
            
            print(f"{role_icon} {user.name} ({user.role})")
            print(f"   邮箱: {user.email}")
            print(f"   ID: {user.id}")
            if user.student_id:
                print(f"   学号: {user.student_id}")
            print()

def verify_login():
    """验证登录功能"""
    from werkzeug.security import check_password_hash
    
    app = create_app()
    
    with app.app_context():
        teacher = User.query.filter_by(email='teacher@example.com').first()
        
        if teacher:
            # 测试密码验证
            test_passwords = ['teacher123', 'Teacher123', 'TEACHER123']
            
            print(f"\n🔐 验证教师账户登录:")
            print(f"邮箱: {teacher.email}")
            
            for pwd in test_passwords:
                is_valid = check_password_hash(teacher.password_hash, pwd)
                status = "✅ 正确" if is_valid else "❌ 错误"
                print(f"密码 '{pwd}': {status}")
                
            print(f"\n📋 建议使用:")
            print(f"   邮箱: teacher@example.com")
            print(f"   密码: teacher123")
            
        else:
            print("❌ 未找到教师用户")

if __name__ == '__main__':
    print("🔧 教师用户管理工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check':
            check_all_users()
        elif sys.argv[1] == '--verify':
            verify_login()
        elif sys.argv[1] == '--add':
            add_teacher_user()
        else:
            print("使用方法:")
            print("  python3 add_teacher.py --add     # 添加教师用户")
            print("  python3 add_teacher.py --check   # 检查所有用户")
            print("  python3 add_teacher.py --verify  # 验证登录信息")
    else:
        # 默认操作：添加教师用户
        add_teacher_user()
        check_all_users()
        verify_login()
