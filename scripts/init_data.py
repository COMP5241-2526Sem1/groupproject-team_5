#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Course, EmailCaptcha
from werkzeug.security import generate_password_hash

def create_initial_data():
    """创建初始数据"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有数据
        if User.query.count() > 1:  # 除了默认管理员
            print("📊 数据库已有数据，跳过初始化")
            return
        
        print("📊 创建初始数据...")
        
        # 创建示例教师用户
        teacher = User(
            email='teacher@example.com',
            password_hash=generate_password_hash('teacher123'),
            role='instructor',
            name='张老师'
        )
        db.session.add(teacher)
        
        # 创建示例学生用户
        student = User(
            email='student@example.com',
            password_hash=generate_password_hash('student123'),
            role='student',
            name='李同学',
            student_id='2024001'
        )
        db.session.add(student)
        
        db.session.commit()
        
        # 创建示例课程
        course = Course(
            name='Python程序设计',
            semester='2024秋季',
            description='学习Python编程基础知识，包括语法、数据结构、面向对象编程等。',
            instructor_id=teacher.id
        )
        db.session.add(course)
        
        course2 = Course(
            name='数据结构与算法',
            semester='2024秋季',
            description='学习常用数据结构和算法，培养编程思维和解决问题的能力。',
            instructor_id=teacher.id
        )
        db.session.add(course2)
        
        db.session.commit()
        
        print("✅ 初始数据创建完成!")
        print("📋 创建的账户:")
        print("   👑 管理员: admin@example.com / admin123")
        print("   👩‍🏫 教师: teacher@example.com / teacher123")
        print("   👨‍🎓 学生: student@example.com / student123")
        print("📚 创建的课程:")
        print("   📖 Python程序设计")
        print("   📊 数据结构与算法")

if __name__ == '__main__':
    create_initial_data()
