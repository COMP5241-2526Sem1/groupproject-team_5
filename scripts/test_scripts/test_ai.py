#!/usr/bin/env python3
"""
AI功能测试脚本
用于测试QA教育平台的AI功能模块
"""

import os
import sys
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv未安装，环境变量可能无法加载")

def test_ai_functions():
    """测试AI功能"""
    try:
        from app.ai_utils import generate_questions, generate_activity_from_content, group_answers
        
        print("🤖 AI功能测试开始...")
        print("="*60)
        
        # 测试用的教学文本
        test_text = """
        Python是一种高级编程语言，由Guido van Rossum在1989年发明。
        Python具有简洁明了的语法，强大的标准库，以及活跃的社区支持。
        它广泛应用于Web开发、数据科学、人工智能、自动化脚本等领域。
        Python的设计哲学强调代码的可读性和简洁性，遵循"优雅胜于丑陋，
        明了胜于晦涩，简洁胜于复杂"的原则。
        """
        
        # 1. 测试问题生成功能
        print("\n📝 测试1: AI问题生成功能")
        print("-" * 30)
        try:
            questions = generate_questions(test_text.strip())
            print("✅ 问题生成成功!")
            for i, question in enumerate(questions, 1):
                print(f"   {i}. {question}")
            
            if len(questions) == 3:
                print("✅ 生成数量正确 (3个问题)")
            else:
                print(f"⚠️  生成数量异常 ({len(questions)}个问题)")
                
        except Exception as e:
            print(f"❌ 问题生成失败: {e}")
        
        # 2. 测试活动生成功能 - 测验类型
        print("\n🎯 测试2: AI活动生成功能 (测验)")
        print("-" * 30)
        try:
            quiz_activity = generate_activity_from_content(test_text.strip(), "quiz")
            print("✅ 测验活动生成成功!")
            print(f"   标题: {quiz_activity.get('title', 'N/A')}")
            print(f"   问题: {quiz_activity.get('question', 'N/A')}")
            print(f"   选项: {quiz_activity.get('options', 'N/A')}")
            print(f"   正确答案: {quiz_activity.get('correct_answer', 'N/A')}")
            print(f"   解释: {quiz_activity.get('explanation', 'N/A')}")
            
        except Exception as e:
            print(f"❌ 测验活动生成失败: {e}")
        
        # 3. 测试活动生成功能 - 投票类型
        print("\n📊 测试3: AI活动生成功能 (投票)")
        print("-" * 30)
        try:
            poll_activity = generate_activity_from_content(test_text.strip(), "poll")
            print("✅ 投票活动生成成功!")
            print(f"   标题: {poll_activity.get('title', 'N/A')}")
            print(f"   问题: {poll_activity.get('question', 'N/A')}")
            print(f"   选项: {poll_activity.get('options', 'N/A')}")
            
        except Exception as e:
            print(f"❌ 投票活动生成失败: {e}")
        
        # 4. 测试答案分组功能
        print("\n🧠 测试4: AI答案分组功能")
        print("-" * 30)
        try:
            # 模拟学生答案
            sample_answers = [
                "Python语法简单易学，适合初学者",
                "Python的语法设计很人性化，容易上手", 
                "Python应用领域广泛，包括Web开发和AI",
                "Python在数据科学和机器学习方面很强大",
                "Python有丰富的第三方库和活跃的社区",
                "Python社区支持很好，文档完善",
                "Python执行速度相对较慢",
                "Python的性能不如C++和Java"
            ]
            
            grouped_data = group_answers(sample_answers)
            print("✅ 答案分组成功!")
            print(f"   分组数量: {len(grouped_data.get('groups', []))}")
            
            for i, group in enumerate(grouped_data.get('groups', []), 1):
                print(f"   分组 {i}: {group.get('theme', 'N/A')} ({len(group.get('answers', []))}个答案)")
                
        except Exception as e:
            print(f"❌ 答案分组失败: {e}")
        
        # 5. 检查API配置
        print("\n🔧 测试5: API配置检查")
        print("-" * 30)
        
        ark_key = os.environ.get('ARK_API_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY')
        
        if ark_key and ark_key != 'your-bytedance-ark-api-key-here' and len(ark_key) > 10:
            print("✅ Ark API密钥已配置")
            print(f"   密钥前缀: {ark_key[:10]}...")
        elif openai_key and openai_key != 'your-openai-api-key-here' and openai_key.startswith('sk-'):
            print("✅ OpenAI API密钥已配置") 
            print(f"   密钥前缀: {openai_key[:10]}...")
        else:
            print("⚠️  未配置API密钥，将使用降级算法")
            print("   建议配置环境变量: ARK_API_KEY 或 OPENAI_API_KEY")
        
        print("\n" + "="*60)
        print("🎉 AI功能测试完成!")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保在项目根目录运行此脚本")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        sys.exit(1)

def test_api_endpoints():
    """测试API端点 (需要应用运行)"""
    import requests
    
    print("\n🌐 API端点测试")
    print("-" * 30)
    
    base_url = "http://localhost:5001"
    
    # 测试应用是否运行
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 应用服务正常运行")
        else:
            print(f"⚠️  应用响应异常: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ 无法连接到应用服务")
        print("   请先运行: python3 run.py")
        return
    
    # 注意: API端点需要登录会话，这里只做连通性测试
    print("💡 完整API测试需要有效的登录会话")
    print("   建议在Web界面中测试AI功能")

def show_usage_examples():
    """显示使用示例"""
    print("\n📚 AI功能使用示例")
    print("="*60)
    
    examples = [
        {
            "title": "1. 在Python代码中直接调用",
            "code": """
from app.ai_utils import generate_questions

# 生成问题
text = "你的教学内容..."
questions = generate_questions(text)
print(questions)
"""
        },
        {
            "title": "2. 在Web界面中使用",
            "code": """
1. 启动应用: python3 run.py
2. 登录管理员账户: admin@example.com / admin123  
3. 创建课程并进入课程详情
4. 点击"创建活动"
5. 在"AI辅助生成"区域输入教学文本
6. 点击"🤖 生成题目"按钮
"""
        },
        {
            "title": "3. 通过API调用",
            "code": """
// JavaScript示例
fetch('/activities/generate_questions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: '教学内容'})
})
.then(response => response.json())
.then(data => console.log(data.questions));
"""
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}")
        print("-" * len(example['title']))
        print(example['code'])

if __name__ == "__main__":
    print("🤖 QA教育平台 - AI功能测试工具")
    print("="*60)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--api":
            test_api_endpoints()
        elif sys.argv[1] == "--examples":
            show_usage_examples()
        elif sys.argv[1] == "--help":
            print("使用方法:")
            print("  python3 test_ai.py           # 基础功能测试")
            print("  python3 test_ai.py --api     # API端点测试")  
            print("  python3 test_ai.py --examples # 显示使用示例")
            print("  python3 test_ai.py --help    # 显示帮助信息")
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 --help 查看可用选项")
    else:
        # 默认运行基础功能测试
        test_ai_functions()
        
        # 显示配置建议
        print("\n💡 使用建议:")
        print("1. 配置API密钥以获得更好的AI效果")
        print("2. 运行 'python3 test_ai.py --examples' 查看使用示例")
        print("3. 在Web界面中测试完整功能")
