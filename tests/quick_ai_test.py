#!/usr/bin/env python3
"""
快速AI测试脚本
用于快速测试AI功能是否正常工作
"""

import os
import sys
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def quick_test():
    """快速测试AI功能"""
    print("🚀 快速AI功能测试")
    print("-" * 40)
    
    # 检查API配置
    ark_key = os.environ.get('ARK_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    print(f"🔑 API配置检查:")
    print(f"   ARK API: {'✅ 已配置' if ark_key else '❌ 未配置'}")
    print(f"   OpenAI API: {'✅ 已配置' if openai_key else '❌ 未配置'}")
    
    if not ark_key and not openai_key:
        print("\n💡 提示: 未检测到API密钥，将使用回退模式")
        print("   要测试完整AI功能，请设置环境变量:")
        print("   export ARK_API_KEY='your_ark_api_key'")
        print("   或")
        print("   export OPENAI_API_KEY='your_openai_api_key'")
    
    # 导入AI工具
    try:
        from app.ai_utils import generate_questions
        print(f"\n✅ AI模块导入成功")
    except Exception as e:
        print(f"\n❌ AI模块导入失败: {e}")
        return False
    
    # 测试问题生成
    test_text = """
    Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。
    它支持多种编程范式，包括面向对象编程和函数式编程。
    Python在数据科学、人工智能、Web开发等领域都有广泛的应用。
    """
    
    print(f"\n🤖 测试AI问题生成...")
    print(f"📝 输入文本: {test_text[:50]}...")
    
    try:
        start_time = time.time()
        questions = generate_questions(test_text)
        end_time = time.time()
        
        print(f"✅ 问题生成成功 (用时: {end_time - start_time:.2f}秒)")
        print(f"📊 生成了 {len(questions)} 个问题:")
        
        for i, question in enumerate(questions, 1):
            print(f"   {i}. {question}")
            
        print(f"\n🎉 AI功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 问题生成失败: {e}")
        return False

def test_with_custom_text():
    """使用自定义文本测试"""
    print("\n" + "="*50)
    print("📝 自定义文本测试")
    print("="*50)
    
    custom_text = input("请输入要测试的文本内容: ").strip()
    
    if not custom_text:
        print("❌ 输入内容为空")
        return
    
    try:
        from app.ai_utils import generate_questions
        
        print(f"\n🤖 正在为您的文本生成问题...")
        start_time = time.time()
        questions = generate_questions(custom_text)
        end_time = time.time()
        
        print(f"✅ 生成完成 (用时: {end_time - start_time:.2f}秒)")
        print(f"📊 生成的问题:")
        
        for i, question in enumerate(questions, 1):
            print(f"   {i}. {question}")
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")

if __name__ == "__main__":
    # 快速测试
    success = quick_test()
    
    if success:
        # 询问是否要进行自定义测试
        choice = input(f"\n💡 是否要测试自定义文本？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            test_with_custom_text()
    
    print(f"\n👋 测试结束")
