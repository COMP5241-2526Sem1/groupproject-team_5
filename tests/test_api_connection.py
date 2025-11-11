#!/usr/bin/env python3
"""
API配置和连接测试
测试ARK API和OpenAI API的连接状态
"""

import os
import requests
import json
import time
from typing import Dict, Any

def test_ark_api() -> Dict[str, Any]:
    """测试ARK API连接"""
    print("🔮 测试ARK API连接...")
    
    api_key = os.environ.get('ARK_API_KEY')
    if not api_key:
        return {
            'success': False,
            'message': 'ARK_API_KEY环境变量未设置',
            'suggestion': 'export ARK_API_KEY="your_ark_api_key"'
        }
    
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "doubao-pro-1.5-32k",
        "messages": [
            {
                "role": "user",
                "content": "Hello, please respond with 'API test successful'"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                'success': True,
                'message': 'ARK API连接成功',
                'response_time': response_time,
                'response_content': content,
                'model': payload['model']
            }
        else:
            return {
                'success': False,
                'message': f'ARK API请求失败: HTTP {response.status_code}',
                'error_detail': response.text,
                'response_time': response_time
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'ARK API请求超时',
            'suggestion': '检查网络连接或增加超时时间'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'ARK API连接错误',
            'suggestion': '检查网络连接和API端点'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'ARK API测试失败: {str(e)}',
            'error_type': type(e).__name__
        }

def test_openai_api() -> Dict[str, Any]:
    """测试OpenAI API连接"""
    print("🤖 测试OpenAI API连接...")
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return {
            'success': False,
            'message': 'OPENAI_API_KEY环境变量未设置',
            'suggestion': 'export OPENAI_API_KEY="your_openai_api_key"'
        }
    
    try:
        import openai
        openai.api_key = api_key
        
        start_time = time.time()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, please respond with 'API test successful'"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        content = response.choices[0].message.content
        
        return {
            'success': True,
            'message': 'OpenAI API连接成功',
            'response_time': response_time,
            'response_content': content,
            'model': 'gpt-3.5-turbo'
        }
        
    except ImportError:
        return {
            'success': False,
            'message': 'OpenAI库未安装',
            'suggestion': 'pip install openai'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'OpenAI API测试失败: {str(e)}',
            'error_type': type(e).__name__
        }

def print_test_result(api_name: str, result: Dict[str, Any]):
    """打印测试结果"""
    print(f"\n{'='*50}")
    print(f"📋 {api_name} API测试结果")
    print(f"{'='*50}")
    
    if result['success']:
        print(f"✅ 状态: 成功")
        print(f"💬 消息: {result['message']}")
        if 'response_time' in result:
            print(f"⏱️  响应时间: {result['response_time']:.2f}秒")
        if 'model' in result:
            print(f"🤖 模型: {result['model']}")
        if 'response_content' in result:
            print(f"📝 API响应: {result['response_content']}")
    else:
        print(f"❌ 状态: 失败")
        print(f"💬 错误信息: {result['message']}")
        if 'suggestion' in result:
            print(f"💡 建议: {result['suggestion']}")
        if 'error_detail' in result:
            print(f"🔍 详细错误: {result['error_detail']}")
        if 'error_type' in result:
            print(f"🏷️  错误类型: {result['error_type']}")

def main():
    """主测试函数"""
    print("🧪 AI API连接测试工具")
    print("="*60)
    
    # 测试ARK API
    ark_result = test_ark_api()
    print_test_result("ARK", ark_result)
    
    # 测试OpenAI API
    openai_result = test_openai_api()
    print_test_result("OpenAI", openai_result)
    
    # 总结
    print(f"\n🏁 测试总结")
    print(f"-"*30)
    
    working_apis = []
    if ark_result['success']:
        working_apis.append("ARK API")
    if openai_result['success']:
        working_apis.append("OpenAI API")
    
    if working_apis:
        print(f"✅ 可用的API: {', '.join(working_apis)}")
        print(f"🎉 您的AI功能已就绪！")
    else:
        print(f"❌ 没有可用的API")
        print(f"💡 请配置至少一个API密钥:")
        print(f"   - ARK API: export ARK_API_KEY='your_key'")
        print(f"   - OpenAI API: export OPENAI_API_KEY='your_key'")
        print(f"   或者使用回退模式（无AI功能）")
    
    return len(working_apis) > 0

if __name__ == "__main__":
    success = main()
    print(f"\n👋 测试完成")
    exit(0 if success else 1)
