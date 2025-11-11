#!/usr/bin/env python3
"""
验证数据迁移是否成功
对比本地和 PlanetScale 的数据
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Course, Activity, Question, Answer

def verify():
    """验证迁移"""
    print("=" * 60)
    print("🔍 数据迁移验证工具")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print(f"\n📊 当前数据库: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        
        # 检查连接
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✅ 数据库连接正常")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
        
        # 统计数据
        print(f"\n📈 数据统计:")
        print("-" * 60)
        
        models = {
            'users (用户)': User,
            'courses (课程)': Course,
            'activities (活动)': Activity,
            'questions (问题)': Question,
            'answers (回答)': Answer,
        }
        
        total_records = 0
        
        for name, model in models.items():
            try:
                count = model.query.count()
                total_records += count
                status = "✅" if count > 0 else "⚠️ "
                print(f"  {status} {name:25} {count:>6} 条")
            except Exception as e:
                print(f"  ❌ {name:25} 错误: {e}")
        
        print("-" * 60)
        print(f"  📝 总记录数: {total_records}")
        
        # 检查示例数据
        print(f"\n👤 用户示例 (前5个):")
        users = User.query.limit(5).all()
        if users:
            for user in users:
                role_emoji = {"admin": "👑", "instructor": "👨‍🏫", "student": "🎓"}.get(user.role, "👤")
                print(f"  {role_emoji} {user.email:30} ({user.role})")
        else:
            print("  ⚠️  没有用户数据")
        
        print(f"\n📚 课程示例 (前5个):")
        courses = Course.query.limit(5).all()
        if courses:
            for course in courses:
                instructor = User.query.get(course.instructor_id)
                instructor_name = instructor.name if instructor else "未知"
                print(f"  📖 {course.name:30} (教师: {instructor_name})")
        else:
            print("  ⚠️  没有课程数据")
        
        print(f"\n🎯 活动示例 (前5个):")
        activities = Activity.query.limit(5).all()
        if activities:
            for activity in activities:
                type_emoji = {"quiz": "📝", "poll": "📊", "discussion": "💬"}.get(activity.activity_type, "🎯")
                print(f"  {type_emoji} {activity.title:30} ({activity.activity_type})")
        else:
            print("  ⚠️  没有活动数据")
        
        # 数据完整性检查
        print(f"\n🔍 数据完整性检查:")
        print("-" * 60)
        
        checks = []
        
        # 检查1: 用户邮箱唯一性
        try:
            duplicate_emails = db.session.execute(db.text("""
                SELECT email, COUNT(*) as count 
                FROM user 
                GROUP BY email 
                HAVING count > 1
            """)).fetchall()
            
            if duplicate_emails:
                checks.append(("❌", "用户邮箱唯一性", f"发现 {len(duplicate_emails)} 个重复邮箱"))
            else:
                checks.append(("✅", "用户邮箱唯一性", "所有邮箱唯一"))
        except:
            checks.append(("⚠️ ", "用户邮箱唯一性", "检查失败"))
        
        # 检查2: 课程-教师关联
        try:
            courses_without_instructor = Course.query.filter(
                ~Course.instructor_id.in_(db.session.query(User.id))
            ).count()
            
            if courses_without_instructor > 0:
                checks.append(("⚠️ ", "课程-教师关联", f"{courses_without_instructor} 个课程的教师不存在"))
            else:
                checks.append(("✅", "课程-教师关联", "所有课程都有有效教师"))
        except:
            checks.append(("⚠️ ", "课程-教师关联", "检查失败"))
        
        # 检查3: 活动-课程关联
        try:
            activities_without_course = Activity.query.filter(
                ~Activity.course_id.in_(db.session.query(Course.id))
            ).count()
            
            if activities_without_course > 0:
                checks.append(("⚠️ ", "活动-课程关联", f"{activities_without_course} 个活动的课程不存在"))
            else:
                checks.append(("✅", "活动-课程关联", "所有活动都有有效课程"))
        except:
            checks.append(("⚠️ ", "活动-课程关联", "检查失败"))
        
        for status, name, result in checks:
            print(f"  {status} {name:20} {result}")
        
        print("-" * 60)
        
        # 总结
        print("\n" + "=" * 60)
        
        if total_records == 0:
            print("⚠️  警告: 数据库为空")
            print("\n可能的原因:")
            print("  1. 还没有导入数据")
            print("  2. 导入失败")
            print("\n解决方法:")
            print("  1. 运行: python export_local_data.py")
            print("  2. 运行: python import_to_planetscale.py <备份文件>")
            return False
        elif any(check[0] == "❌" for check in checks):
            print("⚠️  发现数据问题，请检查上述错误")
            return False
        else:
            print("✅ 验证通过！数据迁移成功！")
            print("=" * 60)
            print(f"\n📊 总结:")
            print(f"  - 总记录数: {total_records}")
            print(f"  - 用户数: {User.query.count()}")
            print(f"  - 课程数: {Course.query.count()}")
            print(f"  - 活动数: {Activity.query.count()}")
            print("\n🎉 您可以开始使用 PlanetScale 数据库了！")
            return True

def main():
    """主函数"""
    success = verify()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
