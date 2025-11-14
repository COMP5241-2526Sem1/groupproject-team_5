import os
import re
import requests
import openai
from typing import List, Dict, Any
from collections import Counter
import json

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

def generate_questions(text: str) -> List[str]:
    # Check for valid API keys in priority order
    ark_api_key = os.environ.get('ARK_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if ark_api_key and ark_api_key != 'your-bytedance-ark-api-key-here' and len(ark_api_key) > 10:
        return generate_questions_with_ark(text, ark_api_key)
    elif openai_api_key and openai_api_key != 'your-openai-api-key-here' and openai_api_key.startswith('sk-'):
        return generate_questions_with_openai(text, openai_api_key)
    else:
        return generate_questions_fallback(text)

def generate_questions_with_ark(text: str, api_key: str) -> List[str]:
    """Generate questions using ByteDance Ark API with volcengine SDK - Enhanced error handling"""
    try:
        if not Ark:
            print("⚠️  Volcengine SDK not available, using fallback")
            return generate_questions_fallback(text)
        
        print(f"🔧 Initializing ARK client...")
        print(f"   API Key: {api_key[:10]}...{api_key[-5:]}")
        print(f"   Base URL: https://ark.cn-beijing.volces.com/api/v3")
        
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key,
            timeout=30  # 设置30秒超时
        )
        
        print(f"📡 Calling ARK API...")
        print(f"   Model: doubao-1-5-pro-32k-250115")
        print(f"   Text length: {len(text)} characters")
        
        completion = client.chat.completions.create(
            model="doubao-1-5-pro-32k-250115",
            messages=[
                {
                    "role": "system",
                    "content": "You are an education expert skilled at generating high-quality classroom interaction questions from teaching text. Please generate 3 questions suitable for classroom interaction based on the given teaching text. Questions should: 1) Test students' understanding of key concepts; 2) Encourage critical thinking; 3) Be suitable for short answer or poll format. Please return 3 questions directly, one per line, without numbering."
                },
                {
                    "role": "user",
                    "content": f"Please generate 3 classroom interaction questions for the following teaching text:\n\n{text[:2000]}"  # 限制文本长度
                }
            ]
        )
        
        print(f"✅ ARK API response received")
        
        questions_text = completion.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        print(f"📝 Parsed {len(questions)} questions")
        
        if len(questions) < 3:
            print(f"⚠️  Only {len(questions)} questions generated, adding fallback questions")
            questions.extend(generate_questions_fallback(text)[:3-len(questions)])
        
        return questions[:3]
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ark API error: {error_msg}")
        
        # 详细的错误类型判断
        if 'timeout' in error_msg.lower():
            print("   Error type: Timeout - API request took too long")
        elif 'connection' in error_msg.lower():
            print("   Error type: Connection - Failed to connect to ARK API")
        elif 'authentication' in error_msg.lower() or '401' in error_msg:
            print("   Error type: Authentication - Invalid API key")
        elif 'rate' in error_msg.lower() or '429' in error_msg:
            print("   Error type: Rate limit - Too many requests")
        else:
            print(f"   Error type: Unknown - {error_msg[:200]}")
        
        # 打印完整的错误堆栈
        import traceback
        traceback.print_exc()
        
        print("🔄 Falling back to local question generation")
        return generate_questions_fallback(text)

def generate_questions_with_openai(text: str, api_key: str) -> List[str]:
    """Generate questions using OpenAI API"""
    try:
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an education expert skilled at generating high-quality classroom interaction questions from teaching text. Please generate 3 questions suitable for classroom interaction based on the given teaching text. Questions should: 1) Test students' understanding of key concepts; 2) Encourage critical thinking; 3) Be suitable for short answer or poll format. Please return 3 questions directly, one per line, without numbering."},
                {"role": "user", "content": f"Please generate 3 classroom interaction questions for the following teaching text:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        if len(questions) < 3:
            questions.extend(generate_questions_fallback(text)[:3-len(questions)])
        
        return questions[:3]
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return generate_questions_fallback(text)

def generate_questions_fallback(text: str) -> List[str]:
    sentences = re.split(r'[.!?。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if len(sentences) < 3:
        return [
            "What are the main points of this text?",
            "What core ideas do you think the author wants to express?",
            "What are the most important concepts in this content?"
        ]
    
    questions = []
    for i, sentence in enumerate(sentences[:3]):
        if '是' in sentence or '为' in sentence or '有' in sentence:
            questions.append(f"According to the text, {sentence}?")
        elif '可以' in sentence or '能够' in sentence:
            questions.append(f"The text mentions {sentence}, what do you think this means?")
        else:
            questions.append(f"Please explain: {sentence}?")
    
    return questions

def generate_activity_from_content(content: str, activity_type: str) -> Dict[str, Any]:
    """Generate a complete activity from teaching content"""
    # Check for valid API keys in priority order
    ark_api_key = os.environ.get('ARK_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if ark_api_key and ark_api_key != 'your-bytedance-ark-api-key-here' and ark_api_key.startswith('ak-'):
        return generate_activity_with_ark(content, activity_type, ark_api_key)
    elif openai_api_key and openai_api_key != 'your-openai-api-key-here' and openai_api_key.startswith('sk-'):
        return generate_activity_with_openai(content, activity_type, openai_api_key)
    else:
        return generate_activity_fallback(content, activity_type)

def generate_activity_with_ark(content: str, activity_type: str, api_key: str) -> Dict[str, Any]:
    """Generate activity using ByteDance Ark API"""
    try:
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if activity_type == 'quiz':
            prompt = f"""Based on the following teaching content, create a quiz question with multiple choice options and correct answer.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the quiz
- question: The quiz question
- options: Array of 4 multiple choice options
- correct_answer: The correct option
- explanation: Brief explanation of why this is correct

Format as valid JSON only."""
        
        elif activity_type == 'poll':
            prompt = f"""Based on the following teaching content, create a poll question with response options.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the poll
- question: The poll question
- options: Array of 4-6 response options

Format as valid JSON only."""
        
        elif activity_type == 'word_cloud':
            prompt = f"""Based on the following teaching content, create a word cloud activity.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the word cloud
- question: Instructions for students to submit words/phrases

Format as valid JSON only."""
        
        else:  # short_answer
            prompt = f"""Based on the following teaching content, create a short answer question.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the question
- question: The short answer question

Format as valid JSON only."""
        
        payload = {
            "model": "doubao-1-5-pro-32k-250115",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert educator creating interactive learning activities. Always return valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        activity_data = json.loads(result["choices"][0]["message"]["content"].strip())
        return activity_data
        
    except Exception as e:
        print(f"Ark API error: {e}")
        return generate_activity_fallback(content, activity_type)

def generate_activity_with_openai(content: str, activity_type: str, api_key: str) -> Dict[str, Any]:
    """Generate activity using OpenAI API"""
    try:
        openai.api_key = api_key
        
        if activity_type == 'quiz':
            prompt = f"""Based on the following teaching content, create a quiz question with multiple choice options and correct answer.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the quiz
- question: The quiz question
- options: Array of 4 multiple choice options
- correct_answer: The correct option
- explanation: Brief explanation of why this is correct

Format as valid JSON only."""
        
        elif activity_type == 'poll':
            prompt = f"""Based on the following teaching content, create a poll question with response options.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the poll
- question: The poll question
- options: Array of 4-6 response options

Format as valid JSON only."""
        
        elif activity_type == 'word_cloud':
            prompt = f"""Based on the following teaching content, create a word cloud activity.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the word cloud
- question: Instructions for students to submit words/phrases

Format as valid JSON only."""
        
        else:  # short_answer
            prompt = f"""Based the following teaching content, create a short answer question.

Content: {content}

Please return a JSON object with:
- title: A descriptive title for the question
- question: The short answer question

Format as valid JSON only."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert educator creating interactive learning activities. Always return valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        return result
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return generate_activity_fallback(content, activity_type)

def generate_activity_fallback(content: str, activity_type: str) -> Dict[str, Any]:
    """Fallback activity generation without OpenAI"""
    sentences = re.split(r'[.!?。！？]', content)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return {
            'title': 'Generated Activity',
            'question': 'Please discuss the main points of this content.',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'] if activity_type in ['quiz', 'poll'] else None,
            'correct_answer': 'Option A' if activity_type == 'quiz' else None
        }
    
    main_sentence = sentences[0]
    
    if activity_type == 'quiz':
        return {
            'title': 'Understanding Check',
            'question': f'Based on the content, what is the main point about: {main_sentence[:50]}...?',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct_answer': 'Option A',
            'explanation': 'This is the correct answer based on the content.'
        }
    elif activity_type == 'poll':
        return {
            'title': 'Quick Poll',
            'question': f'How well do you understand: {main_sentence[:50]}...?',
            'options': ['Very well', 'Somewhat', 'Not very well', 'Not at all']
        }
    elif activity_type == 'word_cloud':
        return {
            'title': 'Word Association',
            'question': f'What key words come to mind when thinking about: {main_sentence[:50]}...?'
        }
    else:  # short_answer
        return {
            'title': 'Reflection Question',
            'question': f'Please explain your understanding of: {main_sentence[:50]}...'
        }

def group_answers(answers: List[str]) -> Dict[str, Any]:
    """Group and analyze student answers using AI"""
    # Check for valid API keys in priority order
    ark_api_key = os.environ.get('ARK_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if ark_api_key and ark_api_key != 'your-bytedance-ark-api-key-here' and ark_api_key.startswith('ak-'):
        return group_answers_with_ark(answers, ark_api_key)
    elif openai_api_key and openai_api_key != 'your-openai-api-key-here' and openai_api_key.startswith('sk-'):
        return group_answers_with_openai(answers, openai_api_key)
    else:
        return group_answers_fallback(answers)

def group_answers_with_ark(answers: List[str], api_key: str) -> Dict[str, Any]:
    """Group answers using ByteDance Ark API"""
    try:
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        answers_text = '\n'.join([f"{i+1}. {answer}" for i, answer in enumerate(answers)])
        
        prompt = f"""Analyze and group the following student answers. Return a JSON object with:
- groups: Array of groups, each with 'name', 'description', 'answers' (array of answer indices)
- summary: Overall summary of the answers
- insights: Key insights from the analysis

Student answers:
{answers_text}

Format as valid JSON only."""
        
        payload = {
            "model": "doubao-1-5-pro-32k-250115",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert educator analyzing student responses. Group similar answers and provide insights. Always return valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 800,
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        grouped_data = json.loads(result["choices"][0]["message"]["content"].strip())
        return grouped_data
        
    except Exception as e:
        print(f"Ark API error: {e}")
        return group_answers_fallback(answers)

def group_answers_with_openai(answers: List[str], api_key: str) -> Dict[str, Any]:
    """Group answers using OpenAI API"""
    try:
        openai.api_key = api_key
        
        answers_text = '\n'.join([f"{i+1}. {answer}" for i, answer in enumerate(answers)])
        
        prompt = f"""Analyze and group the following student answers. Return a JSON object with:
- groups: Array of groups, each with 'name', 'description', 'answers' (array of answer indices)
- summary: Overall summary of the answers
- insights: Key insights from the analysis

Student answers:
{answers_text}

Format as valid JSON only."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert educator analyzing student responses. Group similar answers and provide insights. Always return valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        return result
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return group_answers_fallback(answers)

def group_answers_fallback(answers: List[str]) -> Dict[str, Any]:
    """Fallback answer grouping without OpenAI"""
    # Simple keyword-based grouping
    word_freq = Counter()
    for answer in answers:
        words = re.findall(r'\b\w+\b', answer.lower())
        word_freq.update(words)
    
    # Group by common keywords
    groups = []
    common_words = [word for word, freq in word_freq.most_common(5) if freq > 1]
    
    for i, word in enumerate(common_words[:3]):
        group_answers = [j for j, answer in enumerate(answers) if word in answer.lower()]
        if group_answers:
            groups.append({
                'name': f'Group {i+1}: {word.title()}',
                'description': f'Answers containing "{word}"',
                'answers': group_answers
            })
    
    return {
        'groups': groups,
        'summary': f'Analyzed {len(answers)} responses with {len(groups)} main themes',
        'insights': f'Most common themes: {", ".join(common_words[:3])}'
    }

def extract_text_from_file(file_path: str, file_extension: str) -> str:
    """
    从上传的文件中提取文本内容
    支持的文件格式：.docx, .pdf, .pptx
    """
    try:
        if file_extension.lower() == '.docx':
            return extract_text_from_docx(file_path)
        elif file_extension.lower() == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_extension.lower() == '.pptx':
            return extract_text_from_pptx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise Exception(f"Failed to extract text from file: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    """从Word文档中提取文本"""
    if not Document:
        raise ImportError("python-docx library not installed")
    
    try:
        doc = Document(file_path)
        full_text = []
        
        # 提取段落文本
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text.strip())
        
        # 提取表格文本
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        full_text.append(cell.text.strip())
        
        text = '\n'.join(full_text)
        if not text.strip():
            raise ValueError("No text content found in the Word document")
        
        return text
    except Exception as e:
        raise Exception(f"Error reading Word document: {str(e)}")

def extract_text_from_pdf(file_path: str) -> str:
    """从PDF文件中提取文本，优先使用pdfplumber，回退到PyPDF2"""
    text = ""
    
    # 优先使用pdfplumber，它对复杂PDF的处理更好
    if pdfplumber:
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")
    
    # 回退到PyPDF2
    if PyPDF2:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF with PyPDF2: {str(e)}")
    
    if not text.strip():
        raise ValueError("No text content found in the PDF file or PDF libraries not available")
    
    return text

def extract_text_from_pptx(file_path: str) -> str:
    """从PowerPoint文档中提取文本"""
    if not Presentation:
        raise ImportError("python-pptx library not installed")
    
    try:
        presentation = Presentation(file_path)
        full_text = []
        
        # 遍历所有幻灯片
        for slide_num, slide in enumerate(presentation.slides, 1):
            slide_text = []
            
            # 提取幻灯片中的所有文本
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text.strip())
                
                # 如果是表格，提取表格中的文本
                if shape.has_table:
                    table = shape.table
                    for row in table.rows:
                        for cell in row.cells:
                            if cell.text.strip():
                                slide_text.append(cell.text.strip())
            
            # 如果幻灯片有内容，添加幻灯片标题
            if slide_text:
                full_text.append(f"=== Slide {slide_num} ===")
                full_text.extend(slide_text)
                full_text.append("")  # 添加空行分隔
        
        text = '\n'.join(full_text)
        if not text.strip():
            raise ValueError("No text content found in the PowerPoint presentation")
        
        return text
    except Exception as e:
        raise Exception(f"Error reading PowerPoint presentation: {str(e)}")

def validate_file_upload(file, allowed_extensions=None):
    """
    验证上传的文件
    """
    if allowed_extensions is None:
        allowed_extensions = {'.pdf', '.docx', '.pptx'}
    
    if not file or not file.filename:
        return False, "No file selected"
    
    # 检查文件扩展名
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        return False, f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
    
    # 检查文件大小（限制为10MB）
    file.seek(0, 2)  # 移动到文件末尾
    file_size = file.tell()
    file.seek(0)  # 重置文件指针
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        return False, f"File too large. Maximum size allowed: {max_size // (1024*1024)}MB"
    
    return True, "File is valid"
