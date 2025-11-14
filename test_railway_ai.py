#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway数据库连接 + AI问题生成综合测试
"""
import os
import sys
import pymysql
from datetime import datetime

# 设置项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_railway_database():
    """测试Railway数据库连接"""
    print("🗄️ 测试Railway数据库连接...")
    
    # Railway数据库配置
    config = {
        'host': '66.33.22.236',
        'port': 53176,
        'user': 'root',
        'password': 'HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr',
        'database': 'railway',
        'charset': 'utf8mb4',
        'connect_timeout': 60,
        'read_timeout': 60,
        'write_timeout': 60
    }
    
    try:
        # 连接数据库
        connection = pymysql.connect(**config)
        print("   ✅ 数据库连接成功!")
        
        # 获取数据库信息
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"   📊 数据库版本: {version}")
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"   🏷️  当前数据库: {db_name}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"   📋 数据库表数量: {len(tables)}")
            
            # 显示表名
            if tables:
                print("   📝 表列表:")
                for table in tables:
                    print(f"      - {table[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        return False

def test_ai_question_generation():
    """测试AI问题生成功能"""
    print("\n🤖 测试AI问题生成功能...")
    
    # 设置环境变量
    os.environ['ARK_API_KEY'] = '0c5aba5d-082c-4220-b1dc-e026e87f905b'
    
    try:
        from app.ai_utils import generate_questions
        
        # 测试文本样本
        test_texts = [
            """人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。
            AI包括机器学习、深度学习、自然语言处理等多个子领域。""",
            
            """Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。
            它广泛应用于Web开发、数据科学、机器学习等领域。""",
            
            """数据库是存储和管理数据的系统。关系数据库使用表格来组织数据，
            而NoSQL数据库提供更灵活的数据存储方式。"""
        ]
        
        success_count = 0
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n   🧪 测试样本 {i}:")
            print(f"      内容: {text[:50]}...")
            
            try:
                questions = generate_questions(text)
                
                if questions and len(questions) > 0:
                    print(f"      ✅ 成功生成 {len(questions)} 个问题:")
                    for j, question in enumerate(questions, 1):
                        print(f"         {j}. {question}")
                    success_count += 1
                else:
                    print("      ❌ 未生成任何问题")
                    
            except Exception as e:
                print(f"      ❌ 生成失败: {e}")
        
        print(f"\n   📊 AI测试结果: {success_count}/{len(test_texts)} 成功")
        return success_count == len(test_texts)
        
    except Exception as e:
        print(f"   ❌ AI模块导入失败: {e}")
        return False

def test_integrated_workflow():
    """测试集成工作流程"""
    print("\n🔗 测试集成工作流程...")
    
    try:
        # 设置环境变量
        os.environ['ARK_API_KEY'] = '0c5aba5d-082c-4220-b1dc-e026e87f905b'
        
        # 导入应用模块
        from app.ai_utils import generate_questions
        from app import create_app
        
        print("   ✅ Flask应用模块导入成功")
        
        # 创建应用实例（测试配置）
        app = create_app()
        print("   ✅ Flask应用创建成功")
        
        # 在应用上下文中测试
        with app.app_context():
            # 测试AI功能
            test_text = "Flask是一个轻量级的Python Web框架，提供了构建Web应用的基础功能。"
            questions = generate_questions(test_text)
            
            if questions:
                print(f"   ✅ 应用上下文中AI功能正常 (生成{len(questions)}个问题)")
                return True
            else:
                print("   ❌ 应用上下文中AI功能异常")
                return False
                
    except Exception as e:
        print(f"   ❌ 集成测试失败: {e}")
        import traceback
        print(f"   📄 详细错误: {traceback.format_exc()}")
        return False

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查Python版本
    print(f"   🐍 Python版本: {sys.version}")
    
    # 检查重要的包
    packages = ['pymysql', 'flask', 'volcenginesdkarkruntime']
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}: 已安装")
        except ImportError:
            print(f"   ❌ {package}: 未安装")
    
    # 检查环境变量
    env_vars = ['ARK_API_KEY', 'MYSQL_HOST', 'MYSQL_PASSWORD']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'KEY' in var or 'PASSWORD' in var:
                display = f"{value[:8]}..." if len(value) > 8 else "***"
                print(f"   ✅ {var}: {display}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: 未设置")

def main():
    print("🚀 Railway数据库 + AI功能综合测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查环境
    check_environment()
    print()
    
    # 测试数据库连接
    db_success = test_railway_database()
    
    # 测试AI功能
    ai_success = test_ai_question_generation()
    
    # 测试集成工作流程
    integration_success = test_integrated_workflow()
    
    print("\n" + "=" * 60)
    print("📊 综合测试结果:")
    print(f"   🗄️ Railway数据库: {'✅ 通过' if db_success else '❌ 失败'}")
    print(f"   🤖 AI问题生成: {'✅ 通过' if ai_success else '❌ 失败'}")
    print(f"   🔗 集成工作流程: {'✅ 通过' if integration_success else '❌ 失败'}")
    
    if all([db_success, ai_success, integration_success]):
        print("\n🎉 所有测试通过！系统准备就绪！")
        print("\n📋 建议下一步:")
        print("   1. 将AI修复提交到Git")
        print("   2. 推送到Render进行部署")
        print("   3. 在Web界面测试完整功能")
    else:
        print("\n⚠️ 部分测试失败，需要进一步排查")
    
    return all([db_success, ai_success, integration_success])

if __name__ == "__main__":
    main()
