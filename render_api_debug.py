#!/usr/bin/env python3
"""
Render环境AI功能调试脚本
专门用于在Render Shell中测试AI功能和网络连接
"""

import os
import sys
import requests
import time
from datetime import datetime

def print_env_info():
    """打印环境信息"""
    print("🔍 Render环境信息")
    print("=" * 50)
    print(f"⏰ 时间: {datetime.now()}")
    print(f"🐍 Python版本: {sys.version}")
    print(f"📍 工作目录: {os.getcwd()}")
    print(f"🌐 主机名: {os.environ.get('HOSTNAME', 'unknown')}")
    print()

def check_proxy_settings():
    """检查代理设置"""
    print("🔧 代理设置检查")
    print("=" * 50)
    
    proxy_vars = ['http_proxy', 'https_proxy', 'no_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY']
    
    for var in proxy_vars:
        value = os.environ.get(var, 'not set')
        print(f"📝 {var}: {value}")
    
    print()

def test_network_connectivity():
    """测试网络连接"""
    print("🌐 网络连接测试")
    print("=" * 50)
    
    test_urls = [
        {
            "name": "ARK API 域名",
            "url": "https://ark.cn-beijing.volces.com",
            "timeout": 10
        },
        {
            "name": "火山引擎主站", 
            "url": "https://www.volces.com",
            "timeout": 10
        },
        {
            "name": "Google DNS",
            "url": "https://8.8.8.8",
            "timeout": 5
        }
    ]
    
    for test in test_urls:
        print(f"🔄 测试 {test['name']}: {test['url']}")
        try:
            start_time = time.time()
            response = requests.get(
                test['url'], 
                timeout=test['timeout'],
                headers={'User-Agent': 'Mozilla/5.0 (compatible; RenderBot/1.0)'}
            )
            end_time = time.time()
            
            print(f"✅ 连接成功 - 状态码: {response.status_code}, 耗时: {end_time - start_time:.2f}s")
            
        except requests.exceptions.ConnectTimeout:
            print(f"❌ 连接超时 (>{test['timeout']}s)")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {str(e)[:100]}...")
        except Exception as e:
            print(f"❌ 其他错误: {str(e)[:100]}...")
        
        print()

def check_api_keys():
    """检查API密钥"""
    print("🔑 API密钥检查")
    print("=" * 50)
    
    ark_key = os.environ.get('ARK_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    if ark_key:
        print(f"✅ ARK_API_KEY: {ark_key[:10]}...{ark_key[-5:] if len(ark_key) > 15 else ''}")
        print(f"   长度: {len(ark_key)} 字符")
    else:
        print("❌ ARK_API_KEY: 未设置")
    
    if openai_key:
        print(f"✅ OPENAI_API_KEY: {openai_key[:10]}...")
    else:
        print("❌ OPENAI_API_KEY: 未设置")
    
    print()

def test_ark_api_direct():
    """直接测试ARK API"""
    print("🤖 直接ARK API测试")
    print("=" * 50)
    
    ark_key = os.environ.get('ARK_API_KEY')
    
    if not ark_key:
        print("❌ 无法测试 - ARK_API_KEY 未设置")
        return
    
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {ark_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; RenderBot/1.0)"
    }
    
    data = {
        "model": "doubao-1-5-pro-32k-250115",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer briefly."
            },
            {
                "role": "user",
                "content": "Say hello in one word."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print(f"📡 正在调用 ARK API...")
    print(f"🎯 模型: {data['model']}")
    print(f"📝 请求: {data['messages'][1]['content']}")
    
    try:
        start_time = time.time()
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            timeout=30
        )
        end_time = time.time()
        
        print(f"📊 状态码: {response.status_code}")
        print(f"⏱️  耗时: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
            print(f"✅ API调用成功!")
            print(f"📝 响应: {content}")
            return True
            
        else:
            print(f"❌ API调用失败:")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data}")
            except:
                print(f"   响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时 (30秒)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")
        return False

def test_ai_utils_function():
    """测试AI工具函数"""
    print("🧪 AI工具函数测试")
    print("=" * 50)
    
    try:
        # 导入AI工具
        sys.path.insert(0, '/opt/render/project/src')  # Render项目路径
        from app.ai_utils import generate_questions
        
        test_text = "Machine learning is a powerful technology for data analysis."
        
        print(f"📝 测试文本: {test_text}")
        print("🔄 正在生成问题...")
        
        start_time = time.time()
        questions = generate_questions(test_text)
        end_time = time.time()
        
        print(f"⏱️  耗时: {end_time - start_time:.2f}秒")
        
        if len(questions) >= 3:
            print(f"✅ 成功生成 {len(questions)} 个问题:")
            for i, q in enumerate(questions, 1):
                print(f"   {i}. {q}")
            return True
        else:
            print(f"⚠️  仅生成 {len(questions)} 个问题:")
            for i, q in enumerate(questions, 1):
                print(f"   {i}. {q}")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保在正确的项目目录中运行")
        return False
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Render环境AI功能诊断")
    print("🎯 检查网络连接、API配置和AI功能")
    print("=" * 60)
    print()
    
    # 运行所有测试
    tests = [
        ("环境信息", print_env_info),
        ("代理设置", check_proxy_settings),
        ("API密钥", check_api_keys),
        ("网络连接", test_network_connectivity),
        ("ARK API", test_ark_api_direct),
        ("AI工具函数", test_ai_utils_function)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"🔍 开始 {test_name} 测试...")
        try:
            if test_func == print_env_info or test_func == check_proxy_settings or test_func == check_api_keys:
                test_func()
                results[test_name] = True
            else:
                result = test_func()
                results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 测试失败: {e}")
            results[test_name] = False
        
        print("-" * 50)
        print()
    
    # 汇总结果
    print("📊 测试结果汇总")
    print("=" * 50)
    
    for test_name, result in results.items():
        if isinstance(result, bool):
            status = "✅" if result else "❌"
            print(f"{status} {test_name}")
        else:
            print(f"ℹ️  {test_name}")
    
    # 计算成功率
    bool_results = [r for r in results.values() if isinstance(r, bool)]
    if bool_results:
        success_rate = sum(bool_results) / len(bool_results) * 100
        print(f"\n📈 成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 AI功能基本正常!")
        elif success_rate >= 50:
            print("⚠️  AI功能部分正常，需要排查")
        else:
            print("❌ AI功能存在严重问题")
    
    print("=" * 50)

if __name__ == "__main__":
    main()