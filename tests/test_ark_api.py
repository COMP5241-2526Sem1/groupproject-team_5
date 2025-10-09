#!/usr/bin/env python3
"""
Test script for ByteDance Ark API integration
This script tests the AI functionality with Ark API
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai_utils import generate_questions, generate_activity_from_content, group_answers

def test_ark_api():
    """Test Ark API functionality"""
    print("Testing ByteDance Ark API Integration...")
    print("=" * 50)
    
    # Test content
    test_text = """
    Machine learning is a subset of artificial intelligence that focuses on algorithms 
    that can learn and make decisions from data. It includes supervised learning, 
    unsupervised learning, and reinforcement learning. Supervised learning uses 
    labeled data to train models, while unsupervised learning finds patterns in 
    unlabeled data.
    """
    
    print("1. Testing question generation...")
    try:
        questions = generate_questions(test_text)
        print(f"Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        print("✅ Question generation test passed")
    except Exception as e:
        print(f"❌ Question generation test failed: {e}")
    
    print("\n2. Testing activity generation...")
    try:
        activity = generate_activity_from_content(test_text, 'quiz')
        print(f"Generated activity: {activity.get('title', 'No title')}")
        print(f"Question: {activity.get('question', 'No question')}")
        print("✅ Activity generation test passed")
    except Exception as e:
        print(f"❌ Activity generation test failed: {e}")
    
    print("\n3. Testing answer grouping...")
    try:
        test_answers = [
            "Supervised learning uses labeled data",
            "Machine learning is part of AI",
            "Unsupervised learning finds patterns",
            "AI includes machine learning algorithms"
        ]
        grouped = group_answers(test_answers)
        print(f"Grouped into {len(grouped.get('groups', []))} groups")
        print("✅ Answer grouping test passed")
    except Exception as e:
        print(f"❌ Answer grouping test failed: {e}")
    
    print("\n" + "=" * 50)
    print("API Integration Test Complete!")

def check_api_keys():
    """Check which API keys are available"""
    print("Checking API Keys...")
    print("=" * 30)
    
    ark_key = os.environ.get('ARK_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    if ark_key and ark_key != 'your-bytedance-ark-api-key-optional':
        print("✅ ByteDance Ark API Key found")
        print(f"   Key: {ark_key[:10]}...")
    else:
        print("❌ ByteDance Ark API Key not found or not configured")
    
    if openai_key and openai_key != 'your-openai-api-key-optional':
        print("✅ OpenAI API Key found")
        print(f"   Key: {openai_key[:10]}...")
    else:
        print("❌ OpenAI API Key not found or not configured")
    
    if not ark_key or ark_key == 'your-bytedance-ark-api-key-optional':
        if not openai_key or openai_key == 'your-openai-api-key-optional':
            print("⚠️  No API keys configured - using fallback methods")
    
    print("=" * 30)

if __name__ == "__main__":
    check_api_keys()
    print()
    test_ark_api()
