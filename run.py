#!/usr/bin/env python3
"""
Q&A Education Platform - Final Integrated Version

Features:
- User registration with email verification
- Role-based access (Student/Instructor/Admin)
- Course management
- Q&A system
- Interactive activities
- MySQL database support
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, socketio

def main():
    """Main entry point for the application"""
    
    # Create application
    app = create_app()
    
    # Check if test data needs to be created
    if len(sys.argv) > 1 and sys.argv[1] == '--init-db':
        print("Initializing database and creating test data...")
        from scripts.init_data import create_initial_data
        create_initial_data()
        print("Database initialized successfully!")
        return
    
    # Run application
    print("Starting Q&A Education Platform...")
    print("Access URL: http://localhost:5003")
    print("Admin account: admin@example.com / admin123")
    print("Press Ctrl+C to stop the service")
    print("=" * 50)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5003)

if __name__ == '__main__':
    main()
