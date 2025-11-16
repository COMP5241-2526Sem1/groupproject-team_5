#!/usr/bin/env python3
"""
测试脚本：查看数据库中Answer内容的编码情况
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/dududu/Desktop/QA_Platform/final_integrated_platform')

from app import create_app, db
from app.models import Answer, Question, User

# 设置配置，避免启动服务器
os.environ['FLASK_ENV'] = 'testing'
app = create_app()
app.config['DEBUG'] = False

with app.app_context():
    # 获取一些答案查看内容
    answers = Answer.query.limit(5).all()
    
    print("=== 数据库中的Answer内容检查 ===")
    for i, answer in enumerate(answers, 1):
        print(f"\n{i}. Answer ID: {answer.id}")
        print(f"   Author: {answer.author.username if answer.author else 'Unknown'}")
        print(f"   Content Type: {type(answer.content)}")
        print(f"   Content Length: {len(answer.content) if answer.content else 0}")
        print(f"   Content Preview: {repr(answer.content[:100]) if answer.content else 'None'}")
        
        # 检查是否有不可打印字符
        if answer.content:
            non_printable = [c for c in answer.content[:50] if ord(c) < 32 and c not in '\n\r\t']
            if non_printable:
                print(f"   ⚠️  发现不可打印字符: {[ord(c) for c in non_printable]}")
            else:
                print(f"   ✅ 内容正常，无不可打印字符")
