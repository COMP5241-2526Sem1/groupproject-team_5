#!/usr/bin/env python3
"""
Render环境变量诊断脚本
检查为什么Shell能读取环境变量但Web应用不能
"""

import os
import sys

def check_env_in_shell():
    """检查Shell环境中的变量"""
    print("🔍 Shell环境变量检查")
    print("=" * 50)
    
    env_vars = ['ARK_API_KEY', 'OPENAI_API_KEY', 'DATABASE_URL', 'SECRET_KEY']
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'KEY' in var:
                print(f"✅ {var}: {value[:10]}...{value[-5:] if len(value) > 15 else ''}")
            else:
                print(f"✅ {var}: 已设置")
        else:
            print(f"❌ {var}: 未设置")
    
    print()

def check_env_in_flask_context():
    """检查Flask上下文中的变量"""
    print("🌐 Flask应用上下文环境变量检查")
    print("=" * 50)
    
    try:
        sys.path.insert(0, '/opt/render/project/src')
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            env_vars = ['ARK_API_KEY', 'OPENAI_API_KEY', 'DATABASE_URL', 'SECRET_KEY']
            
            for var in env_vars:
                value = os.environ.get(var)
                if value:
                    if 'KEY' in var:
                        print(f"✅ {var}: {value[:10]}...")
                    else:
                        print(f"✅ {var}: 已设置")
                else:
                    print(f"❌ {var}: 未设置")
        
        print("✅ Flask应用可以访问环境变量")
        return True
        
    except Exception as e:
        print(f"❌ Flask应用上下文检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_in_flask_context():
    """在Flask上下文中测试AI功能"""
    print("\n🧪 Flask上下文中测试AI功能")
    print("=" * 50)
    
    try:
        sys.path.insert(0, '/opt/render/project/src')
        from app import create_app
        from app.ai_utils import generate_questions
        
        app = create_app()
        
        with app.app_context():
            test_text = "Python is a programming language."
            
            print("🔄 正在生成问题...")
            questions = generate_questions(test_text)
            
            print(f"✅ 成功生成 {len(questions)} 个问题:")
            for i, q in enumerate(questions, 1):
                print(f"   {i}. {q}")
            
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_worker_process():
    """检查是否在worker进程中"""
    print("\n🔧 进程信息")
    print("=" * 50)
    
    import subprocess
    
    try:
        # 检查当前进程
        pid = os.getpid()
        print(f"📍 当前进程ID: {pid}")
        
        # 检查是否有gunicorn进程
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        gunicorn_lines = [line for line in result.stdout.split('\n') if 'gunicorn' in line]
        
        if gunicorn_lines:
            print(f"✅ 找到 {len(gunicorn_lines)} 个gunicorn进程")
            for line in gunicorn_lines[:3]:
                print(f"   {line[:100]}")
        else:
            print("❌ 未找到gunicorn进程")
        
    except Exception as e:
        print(f"⚠️  进程检查失败: {e}")

def main():
    print("🚀 Render环境变量诊断")
    print("🎯 找出为什么Shell正常但Web不正常")
    print("=" * 60)
    print()
    
    # 检查Shell环境
    check_env_in_shell()
    
    # 检查Flask上下文
    check_env_in_flask_context()
    
    # 测试AI功能
    test_ai_in_flask_context()
    
    # 检查进程信息
    check_worker_process()
    
    print("\n" + "=" * 60)
    print("💡 诊断建议:")
    print("1. 如果Shell有环境变量但Flask没有:")
    print("   - 检查.env文件是否正确加载")
    print("   - 检查Render环境变量配置")
    print("   - 重启Web服务")
    print()
    print("2. 如果Flask上下文测试成功但Web端失败:")
    print("   - 检查gunicorn worker配置")
    print("   - 检查前端请求是否正确")
    print("   - 查看Web应用日志")
    print("=" * 60)

if __name__ == "__main__":
    main()
