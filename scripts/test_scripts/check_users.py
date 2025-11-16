"""
Check users in the database
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

def check_users():
    """Check all users in the database"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("  User List")
            print("=" * 60)
            print()
            
            users = User.query.order_by(User.role, User.email).all()
            
            if not users:
                print("❌ No users found in database!")
                print()
                print("Run: python3 generate_test_data.py")
                return
            
            print(f"Total users: {len(users)}")
            print()
            
            # Group by role
            roles = {}
            for user in users:
                if user.role not in roles:
                    roles[user.role] = []
                roles[user.role].append(user)
            
            # Display by role
            for role in ['admin', 'instructor', 'student']:
                if role in roles:
                    print(f"\n{'='*60}")
                    print(f"  {role.upper()} ({len(roles[role])} users)")
                    print(f"{'='*60}")
                    
                    for user in roles[role]:
                        print(f"\n  Name: {user.name}")
                        print(f"  Email: {user.email}")
                        print(f"  Role: {user.role}")
                        if user.student_id:
                            print(f"  Student ID: {user.student_id}")
                        
                        # Test passwords
                        test_passwords = ['password123', 'admin123']
                        password_found = False
                        for pwd in test_passwords:
                            if check_password_hash(user.password_hash, pwd):
                                print(f"  Password: {pwd} ✓")
                                password_found = True
                                break
                        
                        if not password_found:
                            print(f"  Password: (not in test list)")
            
            print()
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    check_users()
