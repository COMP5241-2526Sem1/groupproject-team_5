"""
Clear all test data from the database
This script removes all data from the database while keeping the schema intact.
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Course, Enrollment, Activity, Response, Question, Answer, AnswerVote, EmailCaptcha

def clear_database():
    """Remove all data from the database"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("  Clearing Test Data")
            print("=" * 60)
            print()
            print("⚠️  WARNING: This will delete ALL data from the database!")
            print()
            
            # Ask for confirmation
            response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
            
            if response != 'yes':
                print("\n❌ Operation cancelled.")
                return
            
            print("\nDeleting data...")
            
            # Delete in correct order to respect foreign key constraints
            tables_deleted = []
            
            # Delete votes first
            vote_count = AnswerVote.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Votes: {vote_count}")
            
            # Clear best_answer_id from questions (foreign key to answers)
            questions = Question.query.all()
            for question in questions:
                question.best_answer_id = None
            db.session.commit()
            
            # Delete answers
            answer_count = Answer.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Answers: {answer_count}")
            
            # Delete questions
            question_count = Question.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Questions: {question_count}")
            
            # Delete responses
            response_count = Response.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Responses: {response_count}")
            
            # Delete activities
            activity_count = Activity.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Activities: {activity_count}")
            
            # Delete enrollments
            enrollment_count = Enrollment.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Enrollments: {enrollment_count}")
            
            # Delete courses
            course_count = Course.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Courses: {course_count}")
            
            # Delete email captchas
            captcha_count = EmailCaptcha.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Email Captchas: {captcha_count}")
            
            # Delete users (except admin will be auto-created on next app start)
            user_count = User.query.delete()
            db.session.commit()
            tables_deleted.append(f"  • Users: {user_count}")
            
            print("\n✅ Successfully deleted:")
            for table in tables_deleted:
                print(table)
            
            print()
            print("=" * 60)
            print("  Database cleared successfully!")
            print("=" * 60)
            print()
            print("ℹ️  The database is now empty.")
            print("   - Admin user (admin@example.com) will be auto-created on next app start")
            print("   - You can register new users or run test data scripts")
            print()
            
        except Exception as e:
            print(f"\n❌ Error clearing database: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    clear_database()
