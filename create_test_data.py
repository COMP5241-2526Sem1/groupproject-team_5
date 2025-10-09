from app import create_app, db
from app.models import User, Course, Activity, Enrollment, Response
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_test_data():
    app = create_app()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        admin = User(
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            name='Administrator',
            role='admin'
        )
        db.session.add(admin)
        
        instructors = []
        for i in range(3):
            instructor = User(
                email=f'instructor{i+1}@example.com',
                password_hash=generate_password_hash('instructor123'),
                name=f'Instructor{i+1}',
                role='instructor'
            )
            instructors.append(instructor)
            db.session.add(instructor)
        
        students = []
        for i in range(20):
            student = User(
                email=f'student{i+1}@example.com',
                password_hash=generate_password_hash('student123'),
                name=f'Student{i+1}',
                role='student',
                student_id=f'2024{i+1:03d}'
            )
            students.append(student)
            db.session.add(student)
        
        db.session.commit()
        
        courses = []
        course_names = ['Python Programming Basics', 'Data Structures and Algorithms', 'Web Development', 'Database Principles', 'Software Engineering']
        semesters = ['2024 Spring', '2024 Summer', '2024 Fall']
        
        for i, name in enumerate(course_names):
            course = Course(
                name=name,
                semester=random.choice(semesters),
                description=f'This is the course description for {name}, mainly learning related basic knowledge and practical skills.',
                instructor_id=instructors[i % len(instructors)].id
            )
            courses.append(course)
            db.session.add(course)
        
        db.session.commit()
        
        for course in courses:
            enrolled_students = random.sample(students, random.randint(5, 15))
            for student in enrolled_students:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id
                )
                db.session.add(enrollment)
        
        db.session.commit()
        
        activities = []
        activity_titles = [
            'Understanding Python Basic Syntax',
            'Variables and Data Types',
            'Control Flow Statements',
            'Function Definition and Calling',
            'Object-Oriented Programming',
            'Exception Handling',
            'File Operations',
            'Using Modules and Packages'
        ]
        
        for course in courses:
            for i, title in enumerate(activity_titles[:random.randint(3, 6)]):
                activity_type = random.choice(['poll', 'short_answer', 'quiz', 'word_cloud', 'memory_game'])
                question = f'Question about {title}: Please briefly explain your understanding.'
                options = None
                correct_answer = None
                quiz_type = None
                
                if activity_type == 'poll':
                    options = 'Fully understand\nBasically understand\nPartially understand\nNot very clear\nCompletely unclear'
                elif activity_type == 'quiz':
                    quiz_type = random.choice(['multiple_choice', 'true_false', 'fill_blank'])
                    if quiz_type == 'multiple_choice':
                        options = 'Option A\nOption B\nOption C\nOption D'
                        correct_answer = random.choice(['Option A', 'Option B', 'Option C', 'Option D'])
                    elif quiz_type == 'true_false':
                        correct_answer = random.choice(['True', 'False'])
                    else:  # fill_blank
                        correct_answer = 'Python'
                elif activity_type == 'word_cloud':
                    question = f'What words come to mind when you think about {title}? Enter words separated by commas.'
                elif activity_type == 'memory_game':
                    question = f'Memory game related to {title}. Remember the sequence of items shown.'
                
                activity = Activity(
                    title=title,
                    type=activity_type,
                    question=question,
                    options=options,
                    correct_answer=correct_answer,
                    quiz_type=quiz_type,
                    course_id=course.id,
                    is_active=random.choice([True, False]),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                
                if activity.is_active:
                    activity.started_at = activity.created_at + timedelta(minutes=random.randint(1, 60))
                
                activities.append(activity)
                db.session.add(activity)
        
        db.session.commit()
        
        for activity in activities:
            if activity.is_active:
                enrolled_students = [enrollment.student for enrollment in activity.course.enrollments]
                responding_students = random.sample(enrolled_students, random.randint(2, len(enrolled_students)))
                
                for student in responding_students:
                    if activity.type == 'poll':
                        answer = random.choice(activity.options.split('\n'))
                    else:
                        answers = [
                            'This is a great question, I think...',
                            'Based on my understanding, this question involves...',
                            'I think this knowledge point is important because...',
                            'In practical applications, we need to pay attention to...',
                            'This question reminds me of...'
                        ]
                        answer = random.choice(answers)
                    
                    response = Response(
                        student_id=student.id,
                        activity_id=activity.id,
                        answer=answer,
                        submitted_at=activity.started_at + timedelta(minutes=random.randint(1, 30))
                    )
                    db.session.add(response)
        
        db.session.commit()
        
        print("Test data created successfully!")
        print("Admin account: admin@example.com / admin123")
        print("Instructor account: instructor1@example.com / instructor123")
        print("Student account: student1@example.com / student123")
        print(f"Created {len(courses)} courses, {len(activities)} activities, {len(students)} students")

if __name__ == '__main__':
    create_test_data()
