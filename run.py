#!/usr/bin/env python3
"""
Classroom Interaction Platform - Main Entry Point
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, socketio

def main():
    # Set default environment variables if not provided
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///classroom.db'
    
    # Create application
    app = create_app()
    
    # Check if test data needs to be created
    if len(sys.argv) > 1 and sys.argv[1] == '--init-db':
        print("Creating test data...")
        from create_test_data import create_test_data
        create_test_data()
        print("Test data created successfully!")
        return
    
    # Run application
    print("Starting Classroom Interaction Platform...")
    print("Access URL: http://localhost:5000")
    print("Admin account: admin@example.com / admin123")
    print("Press Ctrl+C to stop the service")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
