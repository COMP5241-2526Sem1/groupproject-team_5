#!/usr/bin/env python3
"""
Test script to verify Flask app and template loading
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_app():
    app = create_app()
    
    with app.app_context():
        print("Flask app created successfully!")
        print(f"Template folder: {app.template_folder}")
        print(f"Template folder exists: {os.path.exists(app.template_folder)}")
        
        # Test template loading
        try:
            from flask import render_template_string
            template_content = "Hello {{ name }}!"
            result = render_template_string(template_content, name="World")
            print(f"Template rendering test: {result}")
        except Exception as e:
            print(f"Template rendering error: {e}")
        
        # List template files
        if os.path.exists(app.template_folder):
            print("\nTemplate files:")
            for root, dirs, files in os.walk(app.template_folder):
                for file in files:
                    if file.endswith('.html'):
                        rel_path = os.path.relpath(os.path.join(root, file), app.template_folder)
                        print(f"  {rel_path}")

if __name__ == '__main__':
    test_app()



