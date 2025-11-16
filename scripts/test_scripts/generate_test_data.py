"""
Test Data Generator for Classroom Interaction Platform
This script generates comprehensive test data for testing all features including pagination
"""

from app import create_app, db
from app.models import User, Course, Enrollment, Activity, Response, Question, Answer, AnswerVote
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_test_users():
    """Create test users for different roles"""
    print("Creating test users...")
    
    users = []
    
    # Create admin (if not exists)
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            name='Admin User',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        users.append(admin)
    
    # Create 5 instructors
    for i in range(1, 6):
        email = f'instructor{i}@example.com'
        if not User.query.filter_by(email=email).first():
            instructor = User(
                name=f'Instructor {i}',
                email=email,
                password_hash=generate_password_hash('password123'),
                role='instructor'
            )
            db.session.add(instructor)
            users.append(instructor)
    
    # Create 30 students
    for i in range(1, 31):
        email = f'student{i}@example.com'
        if not User.query.filter_by(email=email).first():
            student = User(
                name=f'Student {i}',
                email=email,
                password_hash=generate_password_hash('password123'),
                role='student',
                student_id=f'S{i:04d}'
            )
            db.session.add(student)
            users.append(student)
    
    db.session.commit()
    print(f"✓ Created {len(users)} new users")
    return User.query.all()

def create_test_courses(users):
    """Create 20 courses for pagination testing"""
    print("Creating test courses...")
    
    instructors = [u for u in users if u.role == 'instructor']
    
    course_names = [
        "Introduction to Python Programming",
        "Data Structures and Algorithms",
        "Web Development with Flask",
        "Machine Learning Fundamentals",
        "Database Systems",
        "Software Engineering Principles",
        "Computer Networks",
        "Operating Systems",
        "Artificial Intelligence",
        "Mobile App Development",
        "Cloud Computing",
        "Cybersecurity Basics",
        "Computer Graphics",
        "Distributed Systems",
        "Human-Computer Interaction",
        "Software Testing",
        "Agile Project Management",
        "DevOps Practices",
        "Blockchain Technology",
        "Internet of Things"
    ]
    
    semesters = ["Fall 2024", "Spring 2024", "Summer 2024"]
    courses = []
    
    for i, name in enumerate(course_names):
        # Check if course already exists
        if Course.query.filter_by(name=name).first():
            continue
            
        course = Course(
            name=name,
            semester=random.choice(semesters),
            description=f"This is a comprehensive course on {name.lower()}. "
                       f"Students will learn fundamental concepts and practical skills. "
                       f"Prerequisites may apply. Join us for an exciting learning journey!",
            instructor_id=instructors[i % len(instructors)].id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
        )
        db.session.add(course)
        courses.append(course)
    
    db.session.commit()
    print(f"✓ Created {len(courses)} courses")
    return Course.query.all()

def enroll_students(courses, users):
    """Enroll students in courses"""
    print("Enrolling students in courses...")
    
    students = [u for u in users if u.role == 'student']
    enrollments_created = 0
    
    # First, enroll student1-student3 in many courses for pagination testing
    test_students = [s for s in students if s.email in ['student1@example.com', 'student2@example.com', 'student3@example.com']]
    for student in test_students:
        # Enroll in 12-15 courses to test pagination (2-3 pages)
        num_courses = random.randint(12, 15)
        selected_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in selected_courses:
            if not Enrollment.query.filter_by(course_id=course.id, student_id=student.id).first():
                enrollment = Enrollment(
                    course_id=course.id,
                    student_id=student.id,
                    enrolled_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(enrollment)
                enrollments_created += 1
    
    # Then enroll other students randomly in courses
    for course in courses:
        # Enroll 5-15 random students per course
        num_students = random.randint(5, 15)
        selected_students = random.sample(students, num_students)
        
        for student in selected_students:
            # Check if already enrolled
            if not Enrollment.query.filter_by(course_id=course.id, student_id=student.id).first():
                enrollment = Enrollment(
                    course_id=course.id,
                    student_id=student.id,
                    enrolled_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(enrollment)
                enrollments_created += 1
    
    db.session.commit()
    print(f"✓ Created {enrollments_created} enrollments")

def create_test_activities(courses, users):
    """Create 30+ activities across different courses for pagination testing"""
    print("Creating test activities...")
    
    from app.models import Activity
    
    activity_types = ['poll', 'quiz', 'short_answer', 'word_cloud']
    quiz_questions = [
        "What is the main advantage of object-oriented programming?",
        "Explain the difference between a stack and a queue.",
        "What is the time complexity of binary search?",
        "Define polymorphism in programming.",
        "What is the purpose of a constructor?",
        "Explain the concept of inheritance.",
        "What is encapsulation?",
        "Describe the MVC architecture pattern.",
        "What is the difference between SQL and NoSQL?",
        "Explain what RESTful API means.",
    ]
    
    poll_questions = [
        "Which programming language do you prefer?",
        "How many hours do you study per week?",
        "Rate your understanding of this topic",
        "Which IDE do you use most often?",
        "Do you prefer online or in-person classes?",
        "How challenging is this course?",
        "Would you recommend this course to others?",
        "What is your favorite part of programming?",
        "How confident are you with debugging?",
        "Which learning resource is most helpful?",
    ]
    
    poll_options = [
        "Python,Java,JavaScript,C++",
        "Less than 5,5-10,10-15,More than 15",
        "Excellent,Good,Fair,Poor",
        "VS Code,PyCharm,IntelliJ,Eclipse",
        "Strongly prefer online,Prefer online,No preference,Prefer in-person,Strongly prefer in-person",
        "Very Easy,Easy,Moderate,Hard,Very Hard",
        "Definitely,Probably,Maybe,Probably Not,Definitely Not",
        "Problem Solving,Building Projects,Learning New Concepts,Debugging",
        "Very Confident,Confident,Neutral,Not Very Confident,Not Confident",
        "Textbooks,Video Tutorials,Practice Problems,Documentation,Office Hours"
    ]
    
    word_cloud_questions = [
        "What is the first word that comes to mind when you think of this course?",
        "Describe your learning experience in one word",
        "What word best describes programming?",
        "Share one keyword about today's lecture",
        "What concept was most important in this chapter?",
        "Name one technology you want to learn",
        "What is your biggest challenge in coding?",
        "Describe your ideal project in one word",
    ]
    
    short_answer_questions = [
        "Describe your understanding of the topic in your own words",
        "What did you find most interesting about this lesson?",
        "How would you apply this concept in real life?",
        "What questions do you still have about this topic?",
        "Share an example of this concept from your experience",
    ]
    
    activities_created = 0
    
    # Create activities for each course
    for course in courses[:10]:  # First 10 courses get activities
        num_activities = random.randint(2, 5)
        
        for i in range(num_activities):
            activity_type = random.choice(activity_types)
            
            if activity_type == 'quiz':
                question = random.choice(quiz_questions)
                options = None
            elif activity_type == 'poll':
                question = random.choice(poll_questions)
                options = random.choice(poll_options)
            elif activity_type == 'word_cloud':
                question = random.choice(word_cloud_questions)
                options = None
            else:  # short_answer
                question = random.choice(short_answer_questions)
                options = None
            
            activity = Activity(
                title=f"{activity_type.capitalize()} {i+1} - {course.name[:30]}",
                type=activity_type,
                question=question,
                options=options,
                course_id=course.id,
                instructor_id=course.instructor_id,
                duration_minutes=random.choice([15, 30, 45, 60]),
                is_active=random.choice([True, True, True, False]),  # 75% active
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 45))
            )
            db.session.add(activity)
            activities_created += 1
    
    db.session.commit()
    print(f"✓ Created {activities_created} activities")
    return Activity.query.all()

def create_test_responses(activities, users):
    """Create student responses to activities"""
    print("Creating student responses...")
    
    students = [u for u in users if u.role == 'student']
    responses_created = 0
    
    for activity in activities:
        # Get enrolled students for this course
        enrollments = Enrollment.query.filter_by(course_id=activity.course_id).all()
        enrolled_student_ids = [e.student_id for e in enrollments]
        enrolled_students = [s for s in students if s.id in enrolled_student_ids]
        
        # 50-100% of enrolled students respond
        num_responses = random.randint(len(enrolled_students)//2, len(enrolled_students))
        responding_students = random.sample(enrolled_students, num_responses)
        
        for student in responding_students:
            # Check if response already exists
            if Response.query.filter_by(activity_id=activity.id, student_id=student.id).first():
                continue
            
            if activity.type == 'quiz':
                answer = random.choice([
                    "This is a detailed answer explaining the concept thoroughly.",
                    "The answer involves multiple factors including...",
                    "Based on my understanding, the solution is...",
                    "I believe the correct approach would be...",
                ])
            elif activity.type == 'poll':
                # Check if options exist (they might be None for some activities)
                if activity.options:
                    answer = random.choice(activity.options.split(','))
                else:
                    answer = "Option 1"  # Fallback answer
            elif activity.type == 'word_cloud':
                # Generate single words or short phrases for word cloud
                answer = random.choice([
                    "Innovation", "Challenging", "Exciting", "Interesting", "Complex",
                    "Rewarding", "Practical", "Theoretical", "Engaging", "Difficult",
                    "Inspiring", "Collaborative", "Creative", "Analytical", "Dynamic",
                    "Problem-solving", "Learning", "Growth", "Development", "Skills",
                    "Knowledge", "Understanding", "Application", "Practice", "Experience"
                ])
            else:  # short_answer
                answer = random.choice([
                    "I found this topic very interesting because it relates to real-world applications.",
                    "My understanding is that this concept helps us solve practical problems efficiently.",
                    "This lesson taught me the importance of proper planning and design.",
                    "I can apply this in my future projects to improve performance and reliability.",
                    "The most valuable takeaway is understanding how different components work together.",
                ])
            
            response = Response(
                activity_id=activity.id,
                student_id=student.id,
                answer=answer,
                submitted_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(response)
            responses_created += 1
    
    db.session.commit()
    print(f"✓ Created {responses_created} responses")

def create_test_qa(courses, users):
    """Create 40+ Q&A questions for pagination testing"""
    print("Creating Q&A questions and answers...")
    
    students = [u for u in users if u.role == 'student']
    instructors = [u for u in users if u.role == 'instructor']
    
    question_templates = [
        ("How to {action} in {topic}?", "I'm having trouble understanding how to {action} in {topic}. Can someone explain with examples?"),
        ("What is the difference between {concept1} and {concept2}?", "I'm confused about the differences between {concept1} and {concept2}. When should I use each?"),
        ("Best practices for {topic}?", "What are the best practices when working with {topic}? Any tips from experienced developers?"),
        ("Error: {error_msg}", "I'm getting this error: '{error_msg}'. How can I fix it?"),
        ("{topic} tutorial recommendation?", "Can anyone recommend good tutorials or resources for learning {topic}?"),
        ("How does {concept} work?", "I don't understand how {concept} works. Can someone break it down for me?"),
        ("Is {approach} a good practice?", "I've been using {approach} in my code. Is this considered good practice or is there a better way?"),
        ("{topic} performance issues", "My code using {topic} is running slowly. What can I do to improve performance?"),
    ]
    
    topics = ["Python", "Flask", "SQL", "JavaScript", "Git", "APIs", "CSS", "HTML", "Testing"]
    actions = ["implement", "debug", "optimize", "deploy", "test"]
    concepts = ["lists", "functions", "classes", "loops", "variables", "databases", "algorithms"]
    errors = ["IndexError", "TypeError", "ValueError", "KeyError", "AttributeError"]
    
    questions_created = 0
    answers_created = 0
    votes_created = 0
    
    # Create questions for first 5 courses
    for course in courses[:5]:
        num_questions = random.randint(8, 12)
        
        for _ in range(num_questions):
            template = random.choice(question_templates)
            title_template, content_template = template
            
            # Fill in template
            title = title_template.format(
                action=random.choice(actions),
                topic=random.choice(topics),
                concept1=random.choice(concepts),
                concept2=random.choice(concepts),
                error_msg=random.choice(errors),
                concept=random.choice(concepts),
                approach=random.choice(concepts)
            )
            
            content = content_template.format(
                action=random.choice(actions),
                topic=random.choice(topics),
                concept1=random.choice(concepts),
                concept2=random.choice(concepts),
                error_msg=random.choice(errors),
                concept=random.choice(concepts),
                approach=random.choice(concepts)
            )
            
            author = random.choice(students)
            
            question = Question(
                title=title,
                content=content,
                course_id=course.id,
                author_id=author.id,
                view_count=random.randint(0, 100),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            db.session.add(question)
            db.session.flush()  # Get question ID
            questions_created += 1
            
            # Create 2-5 answers per question
            num_answers = random.randint(2, 5)
            answers = []
            
            for i in range(num_answers):
                is_instructor = i == 0 and random.choice([True, False])
                answerer = course.instructor if is_instructor else random.choice(students)
                
                answer_content = random.choice([
                    "Here's a detailed explanation of the solution...",
                    "I had the same problem! This is how I solved it:",
                    "Based on my experience, you should try...",
                    "The documentation mentions that...",
                    "A good approach would be to...",
                ])
                
                answer = Answer(
                    content=answer_content,
                    question_id=question.id,
                    author_id=answerer.id,
                    is_instructor_answer=is_instructor,
                    upvotes=random.randint(0, 15),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 55))
                )
                db.session.add(answer)
                db.session.flush()
                answers.append(answer)
                answers_created += 1
                
                # Create votes for this answer
                num_votes = random.randint(0, 10)
                voters = random.sample(students, min(num_votes, len(students)))
                
                for voter in voters:
                    vote = AnswerVote(
                        answer_id=answer.id,
                        user_id=voter.id,
                        vote_type='upvote'
                    )
                    db.session.add(vote)
                    votes_created += 1
            
            # Mark random answer as best (50% chance)
            if answers and random.choice([True, False]):
                best_answer = random.choice(answers)
                question.best_answer_id = best_answer.id
                question.is_resolved = True
    
    db.session.commit()
    print(f"✓ Created {questions_created} questions")
    print(f"✓ Created {answers_created} answers")
    print(f"✓ Created {votes_created} votes")

def main():
    """Main function to generate all test data"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("  Classroom Platform - Test Data Generator")
        print("="*60 + "\n")
        
        # Create all test data
        users = create_test_users()
        courses = create_test_courses(users)
        enroll_students(courses, users)
        activities = create_test_activities(courses, users)
        create_test_responses(activities, users)
        create_test_qa(courses, users)
        
        print("\n" + "="*60)
        print("  Test Data Generation Complete!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"  • Users: {User.query.count()}")
        print(f"  • Courses: {Course.query.count()}")
        print(f"  • Enrollments: {Enrollment.query.count()}")
        print(f"  • Activities: {Activity.query.count()}")
        print(f"  • Responses: {Response.query.count()}")
        print(f"  • Questions: {Question.query.count()}")
        print(f"  • Answers: {Answer.query.count()}")
        print(f"  • Votes: {AnswerVote.query.count()}")
        
        print("\n🔐 Test Accounts:")
        print("  Admin:")
        print("    Email: admin@example.com")
        print("    Password: admin123")
        print("\n  Instructors:")
        print("    Email: instructor1@example.com to instructor5@example.com")
        print("    Password: password123")
        print("\n  Students:")
        print("    Email: student1@example.com to student30@example.com")
        print("    Password: password123")
        
        print("\n✅ You can now run the tests from TEST_GUIDE.md")
        print("="*60 + "\n")

if __name__ == '__main__':
    main()
