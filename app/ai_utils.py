import os
import re
import requests
import openai
from typing import List, Dict, Any
from collections import Counter
import json

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
    
    print(f"Debug: ARK API Key: {ark_api_key[:8]}..." if ark_api_key else "Debug: No ARK API Key")
    print(f"Debug: OpenAI API Key exists: {bool(openai_api_key)}")
    
    # 修复ARK API Key检查 - 支持UUID格式的key
    if ark_api_key and ark_api_key != 'your-bytedance-ark-api-key-here' and len(ark_api_key) > 10:
        print("Attempting to use ARK API")
        return generate_questions_with_ark(text, ark_api_key)
    elif openai_api_key and openai_api_key != 'your-openai-api-key-here' and openai_api_key.startswith('sk-'):
        print("Using OpenAI API")
        return generate_questions_with_openai(text, openai_api_key)
    else:
        print("Using fallback method")
        return generate_questions_fallback(text)

def generate_questions_with_ark(text: str, api_key: str) -> List[str]:
    """Generate questions using ByteDance Ark API with volcengine SDK"""
    try:
        if not Ark:
            print("Volcengine SDK not available, using fallback")
            return generate_questions_fallback(text)
            
        # 使用提供的初始化方法
        client = Ark(
            api_key=api_key,
        )
        
        print(f"Making API call to Ark with model: doubao-1-5-pro-32k-250115")
        
        completion = client.chat.completions.create(
            model="doubao-1-5-pro-32k-250115",
            messages=[
                {
                    "role": "system",
                    "content": "You are an education expert skilled at generating high-quality classroom interaction questions from teaching text. Please generate 3 questions suitable for classroom interaction based on the given teaching text. Questions should: 1) Test students' understanding of key concepts; 2) Encourage critical thinking; 3) Be suitable for short answer or poll format. Please return 3 questions directly, one per line, without numbering."
                },
                {
                    "role": "user",
                    "content": f"Please generate 3 classroom interaction questions for the following teaching text:\n\n{text}"
                }
            ]
        )
        
        print(f"API response received successfully")
        questions_text = completion.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        print(f"Generated {len(questions)} questions: {questions}")
        
        if len(questions) < 3:
            questions.extend(generate_questions_fallback(text)[:3-len(questions)])
        
        return questions[:3]
        
    except Exception as e:
        print(f"Ark API error: {e}")
        print(f"Error type: {type(e).__name__}")
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
            "model": "doubao-pro-1.5-32k",
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
            "model": "doubao-pro-1.5-32k",
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
