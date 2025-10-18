#!/usr/bin/env python3
"""
AI功能测试模块
测试QA平台的AI问题生成、内容分析等功能
"""

import os
import sys
import time
import json
from typing import List, Dict

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_utils import generate_questions, analyze_content_quality, generate_questions_fallback

class AITester:
    """AI功能测试类"""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} | {test_name}"
        if message:
            result += f" | {message}"
        
        print(result)
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_environment_setup(self):
        """测试环境配置"""
        print("\n🔧 测试环境配置...")
        
        # 检查API密钥
        ark_key = os.environ.get('ARK_API_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY')
        
        if ark_key:
            self.log_test("ARK API密钥检测", True, "ARK API密钥已配置")
            return "ark"
        elif openai_key:
            self.log_test("OpenAI API密钥检测", True, "OpenAI API密钥已配置")
            return "openai"
        else:
            self.log_test("API密钥检测", True, "未配置API密钥，将使用回退模式")
            return "fallback"
    
    def test_fallback_question_generation(self):
        """测试回退模式问题生成"""
        print("\n🎯 测试回退模式问题生成...")
        
        test_text = """
        Python是一种高级编程语言，具有简洁的语法和强大的功能。
        Python支持面向对象编程、函数式编程等多种编程范式。
        在数据科学、人工智能、Web开发等领域都有广泛应用。
        """
        
        try:
            questions = generate_questions_fallback(test_text)
            
            # 检查是否返回了问题
            if questions and len(questions) > 0:
                self.log_test("回退模式生成问题", True, f"生成了{len(questions)}个问题")
                for i, q in enumerate(questions, 1):
                    print(f"   问题{i}: {q}")
            else:
                self.log_test("回退模式生成问题", False, "未生成任何问题")
                
        except Exception as e:
            self.log_test("回退模式生成问题", False, f"发生错误: {str(e)}")
    
    def test_ai_question_generation(self, api_type: str):
        """测试AI问题生成"""
        print(f"\n🤖 测试AI问题生成 ({api_type.upper()})...")
        
        test_text = """
        机器学习是人工智能的一个重要分支，它让计算机能够从数据中学习规律，
        而不需要显式编程。主要包括监督学习、无监督学习和强化学习三种类型。
        监督学习使用标注数据进行训练，无监督学习从未标注数据中发现模式，
        强化学习通过与环境交互来学习最优策略。
        """
        
        try:
            start_time = time.time()
            questions = generate_questions(test_text)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if questions and len(questions) > 0:
                self.log_test(f"{api_type.upper()} API响应", True, f"响应时间: {response_time:.2f}秒")
                self.log_test(f"{api_type.upper()} 问题生成", True, f"生成了{len(questions)}个问题")
                
                print(f"   📝 生成的问题:")
                for i, q in enumerate(questions, 1):
                    print(f"   {i}. {q}")
                    
                # 检查问题质量
                self.check_question_quality(questions)
                
            else:
                self.log_test(f"{api_type.upper()} 问题生成", False, "未生成任何问题")
                
        except Exception as e:
            self.log_test(f"{api_type.upper()} API调用", False, f"API调用失败: {str(e)}")
            print(f"   错误详情: {str(e)}")
    
    def check_question_quality(self, questions: List[str]):
        """检查问题质量"""
        print(f"\n📊 问题质量分析...")
        
        # 检查问题长度
        avg_length = sum(len(q) for q in questions) / len(questions)
        length_ok = 10 <= avg_length <= 200
        self.log_test("问题长度检查", length_ok, f"平均长度: {avg_length:.1f}字符")
        
        # 检查是否包含问号
        has_question_marks = sum(1 for q in questions if '?' in q or '？' in q)
        question_mark_ok = has_question_marks >= len(questions) * 0.5
        self.log_test("问号检查", question_mark_ok, f"{has_question_marks}/{len(questions)}个问题包含问号")
        
        # 检查重复性
        unique_questions = len(set(questions))
        uniqueness_ok = unique_questions == len(questions)
        self.log_test("问题唯一性", uniqueness_ok, f"{unique_questions}/{len(questions)}个问题是唯一的")
        
        # 检查关键词覆盖
        keywords = ['什么', '如何', '为什么', '哪些', 'what', 'how', 'why', 'which']
        has_keywords = sum(1 for q in questions for kw in keywords if kw.lower() in q.lower())
        keyword_ok = has_keywords > 0
        self.log_test("关键词检查", keyword_ok, f"包含{has_keywords}个问题关键词")
    
    def test_content_analysis(self):
        """测试内容质量分析"""
        print(f"\n📈 测试内容质量分析...")
        
        test_content = """
        这是一个详细的回答，解释了Python编程语言的特点。
        Python具有简洁的语法，易于学习和使用。
        它支持多种编程范式，包括面向对象和函数式编程。
        Python在数据科学、AI、Web开发等领域都有广泛应用。
        """
        
        try:
            analysis = analyze_content_quality(test_content)
            
            if analysis and isinstance(analysis, dict):
                self.log_test("内容分析功能", True, "成功分析内容质量")
                
                print(f"   📊 分析结果:")
                for key, value in analysis.items():
                    print(f"   - {key}: {value}")
                    
                # 检查分析结果的完整性
                expected_keys = ['length', 'readability', 'completeness', 'accuracy']
                has_all_keys = all(key in analysis for key in expected_keys)
                self.log_test("分析结果完整性", has_all_keys, f"包含{len(analysis)}个分析维度")
                
            else:
                self.log_test("内容分析功能", False, "分析结果格式错误")
                
        except Exception as e:
            self.log_test("内容分析功能", False, f"分析失败: {str(e)}")
    
    def test_api_error_handling(self):
        """测试API错误处理"""
        print(f"\n🚨 测试错误处理...")
        
        # 测试空文本
        try:
            questions = generate_questions("")
            empty_text_ok = isinstance(questions, list)
            self.log_test("空文本处理", empty_text_ok, "正确处理空文本输入")
        except Exception as e:
            self.log_test("空文本处理", False, f"空文本处理失败: {str(e)}")
        
        # 测试超长文本
        try:
            long_text = "这是一个测试文本。" * 1000  # 非常长的文本
            questions = generate_questions(long_text)
            long_text_ok = isinstance(questions, list)
            self.log_test("超长文本处理", long_text_ok, "正确处理超长文本")
        except Exception as e:
            self.log_test("超长文本处理", True, f"预期的错误处理: {str(e)}")
    
    def test_performance(self, api_type: str):
        """测试性能"""
        print(f"\n⚡ 性能测试 ({api_type.upper()})...")
        
        test_texts = [
            "Python是一种编程语言。",
            "机器学习包括监督学习、无监督学习和强化学习。",
            "Web开发中常用的框架有Django、Flask、FastAPI等。"
        ]
        
        total_time = 0
        successful_calls = 0
        
        for i, text in enumerate(test_texts, 1):
            try:
                start_time = time.time()
                questions = generate_questions(text)
                end_time = time.time()
                
                call_time = end_time - start_time
                total_time += call_time
                successful_calls += 1
                
                print(f"   测试{i}: {call_time:.2f}秒, 生成{len(questions)}个问题")
                
            except Exception as e:
                print(f"   测试{i}: 失败 - {str(e)}")
        
        if successful_calls > 0:
            avg_time = total_time / successful_calls
            performance_ok = avg_time < 10.0  # 10秒内完成
            self.log_test("平均响应时间", performance_ok, f"{avg_time:.2f}秒/次")
            self.log_test("成功率", successful_calls == len(test_texts), f"{successful_calls}/{len(test_texts)}次成功")
        else:
            self.log_test("性能测试", False, "所有API调用都失败了")
    
    def run_interactive_test(self):
        """交互式测试"""
        print(f"\n🎮 交互式测试...")
        print("您可以输入自定义文本来测试AI问题生成功能。")
        
        while True:
            user_input = input("\n请输入测试文本 (输入'quit'退出): ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                break
            
            if not user_input:
                print("请输入有效的文本！")
                continue
            
            try:
                print("🤖 正在生成问题...")
                start_time = time.time()
                questions = generate_questions(user_input)
                end_time = time.time()
                
                print(f"✅ 生成完成 (用时: {end_time - start_time:.2f}秒)")
                print(f"📝 生成了{len(questions)}个问题:")
                
                for i, q in enumerate(questions, 1):
                    print(f"   {i}. {q}")
                    
            except Exception as e:
                print(f"❌ 生成失败: {str(e)}")
    
    def print_summary(self):
        """打印测试总结"""
        print(f"\n" + "="*60)
        print(f"🏁 测试总结")
        print(f"="*60)
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"📊 总计: {self.passed + self.failed}")
        
        if self.failed == 0:
            print(f"🎉 所有测试都通过了！")
        else:
            print(f"⚠️  有{self.failed}个测试失败")
            
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"📈 成功率: {success_rate:.1f}%")
        
        return self.failed == 0

def main():
    """主测试函数"""
    print("🚀 QA平台AI功能测试启动")
    print("=" * 60)
    
    tester = AITester()
    
    # 环境检测
    api_type = tester.test_environment_setup()
    
    # 基础功能测试
    tester.test_fallback_question_generation()
    
    # AI功能测试（如果有API密钥）
    if api_type in ['ark', 'openai']:
        tester.test_ai_question_generation(api_type)
        tester.test_performance(api_type)
    
    # 内容分析测试
    tester.test_content_analysis()
    
    # 错误处理测试
    tester.test_api_error_handling()
    
    # 打印测试总结
    success = tester.print_summary()
    
    # 询问是否进行交互式测试
    if api_type in ['ark', 'openai']:
        choice = input(f"\n💡 是否进行交互式测试？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            tester.run_interactive_test()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
