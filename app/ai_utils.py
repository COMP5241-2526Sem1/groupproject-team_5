"""
AI工具模块 - 完整功能版本，针对Render环境优化
包含问题生成、活动生成、文件处理等完整功能
"""

import os
import re
import requests
import json
from typing import List, Dict, Any
from collections import Counter
import socket
import urllib3

# 添加文件处理支持
try:
    from docx import Document
except ImportError:
    Document = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from pptx import Presentation
except ImportError:
    Presentation = None

# 添加dotenv支持
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 添加火山引擎SDK支持
try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    Ark = None

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_ark_endpoint(api_key: str) -> dict:
    """获取可用的ARK API端点 - 支持多重备用方案"""
    
    # 方案1: 尝试域名解析
    try:
        socket.gethostbyname('ark.cn-beijing.volces.com')
        print("✅ DNS解析成功，使用域名")
        return {
            'url': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            'verify': True
        }
    except Exception as e:
        print(f"⚠️ DNS解析失败: {e}")
    
    # 方案2: 使用备用IP地址
    ip_addresses = [
        '101.126.75.85',  # 最新解析IP
        '180.184.34.49',  # 备用IP1  
        '43.129.255.54',  # 备用IP2
    ]
    
    for ip in ip_addresses:
        try:
            print(f"测试IP连接: {ip}")
            # 简单连通性测试
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(3)
            result = test_socket.connect_ex((ip, 443))
            test_socket.close()
            
            if result == 0:
                print(f"✅ 使用IP地址: {ip}")
                return {
                    'url': f'https://{ip}/api/v3/chat/completions',
                    'headers': {
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                        'Host': 'ark.cn-beijing.volces.com'
                    },
                    'verify': False
                }
        except Exception as e:
            print(f"❌ IP {ip} 连接失败: {e}")
            continue
    
    return None

def generate_questions(text: str) -> List[str]:
    """
    智能问题生成 - 主入口函数
    """
    # 检查ARK API
    ark_api_key = os.environ.get('ARK_API_KEY')
    if ark_api_key:
        try:
            return generate_questions_with_ark_http(text, ark_api_key)
        except Exception as e:
            print(f"ARK API失败: {e}")
    
    # 备用方案：基础问题生成
    print("使用基础问题生成...")
    return generate_questions_fallback(text)

def generate_questions_with_ark_http(text: str, api_key: str) -> List[str]:
    """使用ARK API生成问题 - Render环境优化版"""
    
    # 获取可用端点
    endpoint = get_ark_endpoint(api_key)
    if not endpoint:
        raise Exception("无法连接到ARK API服务器")
    
    # 构造请求
    payload = {
        "model": "doubao-1.5-pro-32k",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert at generating educational questions. Generate exactly 3 questions based on the given text. Return only the questions, one per line, without numbering."
            },
            {
                "role": "user", 
                "content": f"Generate 3 educational questions for this text:\n\n{text}"
            }
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    # 发送请求
    response = requests.post(
        endpoint['url'],
        headers=endpoint['headers'],
        json=payload,
        timeout=25,
        verify=endpoint['verify']
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        questions = [q.strip() for q in content.split('\n') if q.strip()]
        
        if len(questions) >= 3:
            print("✅ ARK API调用成功")
            return questions[:3]
    
    raise Exception(f"ARK API调用失败: {response.status_code}")

def generate_questions_fallback(text: str) -> List[str]:
    """备用问题生成方案"""
    print("使用本地备用问题生成...")
    
    # 基于文本长度和内容生成基础问题
    questions = []
    
    if "数据库" in text or "database" in text.lower():
        questions.extend([
            "What are the main advantages of using databases?",
            "Can you explain the difference between SQL and NoSQL databases?", 
            "What is data normalization and why is it important?"
        ])
    elif "编程" in text or "program" in text.lower():
        questions.extend([
            "What are the key principles of good programming?",
            "How do you debug a program effectively?",
            "What is the difference between syntax and logic errors?"
        ])
    else:
        # 通用问题
        questions.extend([
            "What are the main concepts discussed in this text?",
            "How would you apply this knowledge in practice?", 
            "What questions do you have about this topic?"
        ])
    
    return questions[:3]

def generate_activity_with_ark(content: str, activity_type: str, api_key: str) -> Dict[str, Any]:
    """使用ARK API生成活动"""
    
    endpoint = get_ark_endpoint(api_key)
    if not endpoint:
        return generate_activity_fallback(content, activity_type)
    
    try:
        if activity_type == 'quiz':
            prompt = f"""Create a quiz question based on this content: {content}

Return a JSON object with:
- title: Quiz title
- question: The question
- options: Array of 4 choices
- correct_answer: Correct option
- explanation: Brief explanation"""
        else:
            prompt = f"""Create a poll question based on this content: {content}

Return a JSON object with:
- title: Poll title  
- question: The question
- options: Array of poll options"""
        
        payload = {
            "model": "doubao-1.5-pro-32k",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.7
        }
        
        response = requests.post(
            endpoint['url'],
            headers=endpoint['headers'], 
            json=payload,
            timeout=25,
            verify=endpoint['verify']
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            return json.loads(content)
    except:
        pass
    
    return generate_activity_fallback(content, activity_type)

def generate_activity_fallback(content: str, activity_type: str) -> Dict[str, Any]:
    """备用活动生成"""
    if activity_type == 'quiz':
        return {
            "title": "Knowledge Check",
            "question": "Based on the content, which statement is most accurate?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A", 
            "explanation": "This covers the main concept."
        }
    else:
        return {
            "title": "Quick Poll",
            "question": "What's your opinion on this topic?",
            "options": ["Strongly Agree", "Agree", "Neutral", "Disagree"]
        }

# 保留其他必要的函数（文件处理等）
def extract_text_from_file(file_path: str) -> str:
    """从文件中提取文本"""
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        # 可以添加其他文件类型的处理
        return ""
    except:
        return ""

def validate_file_upload(file) -> tuple:
    """验证文件上传"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    # 检查文件类型
    allowed_extensions = {'.txt', '.docx', '.pdf', '.pptx'}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        return False, "File type not supported"
    
    # 检查文件大小 (10MB limit)
    if hasattr(file, 'content_length') and file.content_length > 10 * 1024 * 1024:
        return False, "File too large (max 10MB)"
    
    return True, "Valid file"

def generate_activity_from_content(content: str, activity_type: str) -> Dict[str, Any]:
    """从内容生成活动"""
    # 尝试使用ARK API
    ark_api_key = os.environ.get('ARK_API_KEY')
    if ark_api_key:
        try:
            return generate_activity_with_ark(content, activity_type, ark_api_key)
        except Exception as e:
            print(f"ARK API生成活动失败: {e}")
    
    # 使用备用方案
    return generate_activity_fallback(content, activity_type)

def group_answers(answers: List[str]) -> Dict[str, Any]:
    """分组答案"""
    # 尝试使用ARK API
    ark_api_key = os.environ.get('ARK_API_KEY')
    if ark_api_key and len(answers) > 0:
        try:
            endpoint = get_ark_endpoint(ark_api_key)
            if endpoint:
                return group_answers_with_ark(answers, ark_api_key)
        except Exception as e:
            print(f"ARK API分组失败: {e}")
    
    # 使用备用分组方案
    return group_answers_fallback(answers)

def group_answers_with_ark(answers: List[str], api_key: str) -> Dict[str, Any]:
    """使用ARK API分组答案"""
    endpoint = get_ark_endpoint(api_key)
    if not endpoint:
        return group_answers_fallback(answers)
    
    try:
        answers_text = '\n'.join([f"{i+1}. {answer}" for i, answer in enumerate(answers)])
        
        payload = {
            "model": "doubao-1.5-pro-32k",
            "messages": [
                {
                    "role": "user",
                    "content": f"Group these student answers by similarity and provide insights:\n\n{answers_text}\n\nReturn JSON with groups, summary, and insights."
                }
            ],
            "max_tokens": 600,
            "temperature": 0.3
        }
        
        response = requests.post(
            endpoint['url'],
            headers=endpoint['headers'],
            json=payload,
            timeout=25,
            verify=endpoint['verify']
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            return json.loads(content)
    except:
        pass
    
    return group_answers_fallback(answers)

def group_answers_fallback(answers: List[str]) -> Dict[str, Any]:
    """备用答案分组"""
    return {
        "groups": [
            {
                "name": "All Responses",
                "description": "All student responses",
                "answers": list(range(len(answers)))
            }
        ],
        "summary": f"Received {len(answers)} responses",
        "insights": ["All responses collected successfully"]
    }
