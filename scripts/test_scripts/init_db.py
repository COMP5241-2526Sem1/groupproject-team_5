#!/usr/bin/env python3
"""
数据库初始化脚本
用于在 Render 首次部署后初始化数据库表
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    print("=" * 60)
    
    try:
        # 导入应用
        from app import create_app, db
        from app.models import User
        from werkzeug.security import generate_password_hash
        
        print("✅ 成功导入应用模块")
        
        # 创建应用上下文
        app = create_app()
        
        with app.app_context():
            print("\n📊 当前数据库配置:")
            print(f"   URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # 创建所有表
            print("\n📋 创建数据库表...")
            db.create_all()
            print("✅ 数据库表创建成功！")
            
            # 检查是否已有管理员账户
            admin = User.query.filter_by(email='admin@example.com').first()
            
            if not admin:
                print("\n👤 创建默认管理员账户...")
                admin = User(
                    email='admin@example.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    name='Administrator'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ 管理员账户创建成功！")
                print("   邮箱: admin@example.com")
                print("   密码: admin123")
                print("   ⚠️  请登录后立即修改密码！")
            else:
                print("\n✅ 管理员账户已存在")
            
            # 显示统计信息
            print("\n📊 数据库统计:")
            user_count = User.query.count()
            print(f"   用户总数: {user_count}")
            
            # 按角色统计
            admin_count = User.query.filter_by(role='admin').count()
            instructor_count = User.query.filter_by(role='instructor').count()
            student_count = User.query.filter_by(role='student').count()
            
            print(f"   管理员: {admin_count}")
            print(f"   教师: {instructor_count}")
            print(f"   学生: {student_count}")
            
        print("\n" + "=" * 60)
        print("🎉 数据库初始化完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {str(e)}")
        print("\n请检查:")
        print("1. 数据库连接配置是否正确")
        print("2. 数据库是否可访问")
        print("3. 数据库凭据是否正确")
        import traceback
        traceback.print_exc()
        return False

def test_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    try:
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            # 执行简单查询
            db.session.execute(db.text("SELECT 1"))
            print("✅ 数据库连接成功！")
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("数据库初始化脚本")
    print("=" * 60)
    
    # 检查环境变量
    print("\n🔍 检查环境变量...")
    required_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  缺少环境变量: {', '.join(missing_vars)}")
        print("请设置以下环境变量:")
        for var in missing_vars:
            print(f"   export {var}=your_value")
        sys.exit(1)
    
    print("✅ 环境变量配置完整")
    
    # 测试连接
    if not test_connection():
        print("\n请先解决数据库连接问题")
        sys.exit(1)
    
    # 初始化数据库
    success = init_database()
    
    if success:
        print("\n✨ 您可以开始使用系统了！")
        sys.exit(0)
    else:
        sys.exit(1)
