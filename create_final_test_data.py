"""
Create comprehensive test data for the education platform
Includes: Teacher account, 3 courses (Database System, Computer Vision, Machine Learning),
all activity types with 100+ student responses each
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Course, Enrollment, Activity, Response
from werkzeug.security import generate_password_hash
from app import get_beijing_time

# Teacher credentials
TEACHER_EMAIL = "teacher@test.com"
TEACHER_PASSWORD = "teacher123"
TEACHER_NAME = "Dr. Sarah Johnson"

# Test student credentials (no responses)
TEST_STUDENT_EMAIL = "test_student@test.com"
TEST_STUDENT_PASSWORD = "student123"
TEST_STUDENT_NAME = "Test Student"

# Course data
COURSES = [
    {
        "name": "Database System",
        "semester": "Spring 2025",
        "description": "Comprehensive course covering database design, SQL, normalization, transactions, and database management systems."
    },
    {
        "name": "Computer Vision",
        "semester": "Spring 2025",
        "description": "Introduction to computer vision including image processing, feature detection, object recognition, and deep learning for vision."
    },
    {
        "name": "Machine Learning",
        "semester": "Spring 2025",
        "description": "Fundamentals of machine learning including supervised learning, unsupervised learning, neural networks, and model evaluation."
    }
]

# Activity data for each course
ACTIVITIES_DATA = {
    "Database System": {
        "poll": {
            "title": "Favorite Database Type",
            "question": "Which type of database do you prefer working with?",
            "options": ["Relational (SQL)", "NoSQL (MongoDB)", "Graph Database", "Time-Series Database", "Not Sure"],
        },
        "short_answer": {
            "title": "Understanding Normalization",
            "question": "Explain in your own words what database normalization means and why it is important. Provide a brief example.",
        },
        "quiz_multiple_choice": {
            "title": "SQL Query Basics",
            "question": "What is the primary purpose of the SQL JOIN clause?",
            "options": ["To combine rows from two or more tables", "To filter data in a table", "To sort data in a table", "To delete data from a table"],
            "correct_answer": "To combine rows from two or more tables",
            "quiz_type": "multiple_choice"
        },
        "quiz_true_false": {
            "title": "ACID Properties",
            "question": "ACID properties guarantee that database transactions are processed reliably: Atomicity, Consistency, Isolation, and Durability.",
            "correct_answer": "True",
            "quiz_type": "true_false"
        },
        "quiz_fill_blank": {
            "title": "SQL Basics",
            "question": "The SQL command used to retrieve data from a database is _____.",
            "correct_answer": "SELECT",
            "quiz_type": "fill_blank"
        },
        "word_cloud": {
            "title": "Database Concepts",
            "question": "What words come to mind when you think about database systems? Enter words separated by commas.",
        },
        "memory_game": {
            "title": "SQL Query Order",
            "question": "Remember the correct order of SQL clauses: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY",
            "correct_sequence": "SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY"
        }
    },
    "Computer Vision": {
        "poll": {
            "title": "Computer Vision Application Interest",
            "question": "Which application of computer vision interests you the most?",
            "options": ["Object Detection", "Image Classification", "Face Recognition", "Medical Imaging", "Autonomous Vehicles"],
        },
        "short_answer": {
            "title": "Convolutional Neural Networks",
            "question": "Explain how convolutional neural networks (CNNs) work for image recognition. What makes them effective for visual tasks?",
        },
        "quiz_multiple_choice": {
            "title": "Image Filtering",
            "question": "What is the purpose of a convolution operation in image processing?",
            "options": ["To detect edges and features in images", "To resize images", "To compress images", "To convert color images to grayscale"],
            "correct_answer": "To detect edges and features in images",
            "quiz_type": "multiple_choice"
        },
        "quiz_true_false": {
            "title": "Deep Learning for Vision",
            "question": "Transfer learning allows us to use pre-trained models on new vision tasks, significantly reducing training time and improving performance.",
            "correct_answer": "True",
            "quiz_type": "true_false"
        },
        "quiz_fill_blank": {
            "title": "Computer Vision Basics",
            "question": "The process of identifying and locating objects in an image is called object _____.",
            "correct_answer": "detection",
            "quiz_type": "fill_blank"
        },
        "word_cloud": {
            "title": "Vision Concepts",
            "question": "What words come to mind when you think about computer vision? Enter words separated by commas.",
        },
        "memory_game": {
            "title": "CNN Architecture",
            "question": "Remember the typical layers in a CNN: Convolution, Activation, Pooling, Fully Connected",
            "correct_sequence": "Convolution, Activation, Pooling, Fully Connected"
        }
    },
    "Machine Learning": {
        "poll": {
            "title": "ML Algorithm Preference",
            "question": "Which machine learning algorithm do you find most interesting?",
            "options": ["Neural Networks", "Decision Trees", "Support Vector Machines", "K-Means Clustering", "Linear Regression"],
        },
        "short_answer": {
            "title": "Overfitting Problem",
            "question": "What is overfitting in machine learning? How can it be prevented? Provide a brief explanation with examples.",
        },
        "quiz_multiple_choice": {
            "title": "Supervised Learning",
            "question": "What is the main difference between supervised and unsupervised learning?",
            "options": ["Supervised learning uses labeled data, unsupervised uses unlabeled data", "Supervised learning is faster", "Unsupervised learning requires more data", "There is no difference"],
            "correct_answer": "Supervised learning uses labeled data, unsupervised uses unlabeled data",
            "quiz_type": "multiple_choice"
        },
        "quiz_true_false": {
            "title": "Model Evaluation",
            "question": "Cross-validation is a technique used to assess how well a machine learning model generalizes to an independent dataset.",
            "correct_answer": "True",
            "quiz_type": "true_false"
        },
        "quiz_fill_blank": {
            "title": "ML Basics",
            "question": "The process of training a model to make predictions is called _____ learning.",
            "correct_answer": "supervised",
            "quiz_type": "fill_blank"
        },
        "word_cloud": {
            "title": "ML Concepts",
            "question": "What words come to mind when you think about machine learning? Enter words separated by commas.",
        },
        "memory_game": {
            "title": "ML Pipeline",
            "question": "Remember the steps in a machine learning pipeline: Data Collection, Preprocessing, Training, Evaluation, Deployment",
            "correct_sequence": "Data Collection, Preprocessing, Training, Evaluation, Deployment"
        }
    }
}

# Sample answers for each course and activity type
SAMPLE_ANSWERS = {
    "Database System": {
        "poll": ["Relational (SQL)", "NoSQL (MongoDB)", "Graph Database", "Time-Series Database", "Not Sure"],
        "short_answer": [
            "Normalization is the process of organizing data in a database to reduce redundancy and improve data integrity. It involves dividing large tables into smaller, related tables and defining relationships between them. For example, instead of storing customer information in every order record, we create a separate customers table and reference it.",
            "Database normalization helps eliminate data redundancy and anomalies. It ensures that each piece of data is stored only once, making updates easier and preventing inconsistencies. For instance, in a denormalized database, if a customer's address changes, we'd need to update it in multiple places, but with normalization, we update it once.",
            "Normalization is important because it reduces data duplication and ensures data consistency. It makes databases more efficient and easier to maintain. An example would be separating student information from course enrollment data to avoid repeating student details for each course.",
            "Normalization means structuring database tables to minimize redundancy and dependency. It's crucial for maintaining data integrity and making queries more efficient. For example, creating separate tables for products and orders instead of embedding product details in each order.",
            "The goal of normalization is to organize data to prevent anomalies during insertions, updates, and deletions. It divides data into logical groups. A practical example is separating author information from book information to avoid repeating author details.",
        ],
        "word_cloud": [
            "database, SQL, tables, queries, normalization, ACID, transactions, indexes, relationships, foreign keys",
            "MySQL, PostgreSQL, schema, data integrity, primary key, join, select, insert, update, delete",
            "relational, NoSQL, MongoDB, Redis, data modeling, ER diagram, constraints, triggers, stored procedures",
            "tables, rows, columns, database design, SQL Server, Oracle, data warehouse, OLTP, OLAP",
            "database management, queries, normalization, transactions, concurrency, locking, backup, recovery",
        ],
    },
    "Computer Vision": {
        "poll": ["Object Detection", "Image Classification", "Face Recognition", "Medical Imaging", "Autonomous Vehicles"],
        "short_answer": [
            "Convolutional Neural Networks (CNNs) use convolutional layers to detect features in images through filters. These filters slide across the image to identify patterns like edges, shapes, and textures. Pooling layers reduce dimensionality, and fully connected layers make final predictions. CNNs are effective because they can automatically learn hierarchical features from raw pixels.",
            "CNNs work by applying convolutional filters that detect local patterns in images. Each layer builds upon previous layers to recognize more complex features. The convolution operation preserves spatial relationships, making CNNs ideal for images. They're effective because they require fewer parameters than fully connected networks and can learn translation-invariant features.",
            "Convolutional Neural Networks process images through layers that detect increasingly complex features. Early layers detect edges and basic shapes, while deeper layers identify objects. The key advantage is weight sharing, which reduces parameters and allows the network to recognize patterns regardless of their location in the image.",
            "CNNs use convolution operations to extract features from images. The network learns filters that detect specific patterns through training. Pooling layers help reduce computation and provide translation invariance. This architecture is effective for vision tasks because it mimics how the human visual system processes information hierarchically.",
            "CNNs apply learnable filters to input images to detect features. These filters are shared across the entire image, making the network translation-invariant. The hierarchical structure allows the network to learn simple features first, then combine them into more complex patterns, which is why they excel at image recognition tasks.",
        ],
        "word_cloud": [
            "images, pixels, CNN, convolution, filters, features, detection, classification, recognition, deep learning",
            "computer vision, image processing, object detection, neural networks, YOLO, ResNet, feature extraction",
            "vision, images, deep learning, convolutional layers, pooling, activation, recognition, classification",
            "computer vision, image analysis, feature detection, edge detection, pattern recognition, machine learning",
            "images, neural networks, convolutional, filters, pooling, recognition, detection, classification, deep learning",
        ],
    },
    "Machine Learning": {
        "poll": ["Neural Networks", "Decision Trees", "Support Vector Machines", "K-Means Clustering", "Linear Regression"],
        "short_answer": [
            "Overfitting occurs when a model learns the training data too well, including noise and irrelevant patterns, resulting in poor performance on new data. It can be prevented by using techniques like cross-validation, regularization (L1/L2), early stopping, increasing training data, or reducing model complexity. For example, a decision tree that memorizes every training example will fail on test data.",
            "Overfitting is when a model performs excellently on training data but poorly on unseen data because it has memorized the training set. Prevention methods include dropout for neural networks, pruning for decision trees, using more training data, reducing features, and ensemble methods. An example is a polynomial regression with too high a degree that fits training points exactly but fails on new data.",
            "Overfitting happens when a model becomes too complex and captures noise in training data. To prevent it, we can use regularization techniques, holdout validation, cross-validation, or simplify the model. For instance, a neural network with too many layers might overfit, so we reduce layers or add dropout.",
            "Overfitting means the model has learned training data patterns too specifically, including random fluctuations. Prevention includes early stopping, cross-validation, feature selection, and regularization. A practical example is a random forest with too many trees that starts memorizing training data instead of learning generalizable patterns.",
            "Overfitting occurs when a model's complexity exceeds what's needed, causing it to fit training noise. We can prevent it by using validation sets, regularization, reducing model complexity, or collecting more data. For example, a support vector machine with a very complex kernel might overfit to training examples.",
        ],
        "word_cloud": [
            "machine learning, algorithms, training, prediction, neural networks, data, features, model, accuracy",
            "ML, supervised learning, unsupervised learning, classification, regression, clustering, deep learning",
            "machine learning, data science, algorithms, models, training, testing, validation, prediction, AI",
            "learning, algorithms, neural networks, data, features, training, model, prediction, accuracy, evaluation",
            "ML, algorithms, training data, features, model, prediction, accuracy, validation, cross-validation, overfitting",
        ],
    }
}

def create_teacher():
    """Create or update teacher account"""
    print("Creating teacher account...")
    teacher = User.query.filter_by(email=TEACHER_EMAIL).first()
    if teacher:
        teacher.password_hash = generate_password_hash(TEACHER_PASSWORD)
        teacher.name = TEACHER_NAME
        teacher.role = 'instructor'
        print(f"  Updated existing teacher: {TEACHER_EMAIL}")
    else:
        teacher = User(
            email=TEACHER_EMAIL,
            password_hash=generate_password_hash(TEACHER_PASSWORD),
            name=TEACHER_NAME,
            role='instructor'
        )
        db.session.add(teacher)
        print(f"  Created new teacher: {TEACHER_EMAIL}")
    db.session.commit()
    return teacher

def create_test_student():
    """Create test student account (no responses)"""
    print("Creating test student account...")
    student = User.query.filter_by(email=TEST_STUDENT_EMAIL).first()
    if student:
        student.password_hash = generate_password_hash(TEST_STUDENT_PASSWORD)
        student.name = TEST_STUDENT_NAME
        student.role = 'student'
        print(f"  Updated existing test student: {TEST_STUDENT_EMAIL}")
    else:
        student = User(
            email=TEST_STUDENT_EMAIL,
            password_hash=generate_password_hash(TEST_STUDENT_PASSWORD),
            name=TEST_STUDENT_NAME,
            role='student',
            student_id=User.generate_student_id()
        )
        db.session.add(student)
        print(f"  Created new test student: {TEST_STUDENT_EMAIL}")
    db.session.commit()
    return student

def create_students(num_students=150):
    """Create student accounts for responses"""
    print(f"Creating {num_students} student accounts...")
    students = []
    for i in range(1, num_students + 1):
        email = f"student{i}@test.com"
        student = User.query.filter_by(email=email).first()
        if not student:
            student = User(
                email=email,
                password_hash=generate_password_hash('student123'),
                name=f"Student {i}",
                role='student',
                student_id=User.generate_student_id()
            )
            db.session.add(student)
            students.append(student)
        else:
            students.append(student)
    db.session.commit()
    print(f"  Created/updated {len(students)} students")
    return students

def create_courses(teacher):
    """Create courses"""
    print("Creating courses...")
    courses = []
    for course_data in COURSES:
        course = Course.query.filter_by(name=course_data["name"]).first()
        if course:
            course.semester = course_data["semester"]
            course.description = course_data["description"]
            course.instructor_id = teacher.id
            print(f"  Updated course: {course_data['name']}")
        else:
            course = Course(
                name=course_data["name"],
                semester=course_data["semester"],
                description=course_data["description"],
                instructor_id=teacher.id
            )
            db.session.add(course)
            print(f"  Created course: {course_data['name']}")
        courses.append(course)
    db.session.commit()
    return courses

def enroll_students(courses, students):
    """Enroll all students in all courses"""
    print("Enrolling students in courses...")
    enrollments_created = 0
    for course in courses:
        for student in students:
            enrollment = Enrollment.query.filter_by(course_id=course.id, student_id=student.id).first()
            if not enrollment:
                enrollment = Enrollment(
                    course_id=course.id,
                    student_id=student.id
                )
                db.session.add(enrollment)
                enrollments_created += 1
    db.session.commit()
    print(f"  Created {enrollments_created} enrollments")

def create_activities(courses, teacher):
    """Create activities for each course"""
    print("Creating activities...")
    activities = []
    
    for course in courses:
        course_name = course.name
        if course_name not in ACTIVITIES_DATA:
            continue
            
        activity_data = ACTIVITIES_DATA[course_name]
        
        # Poll activity
        poll_data = activity_data.get("poll")
        if poll_data:
            activity = Activity(
                title=poll_data["title"],
                question=poll_data["question"],
                type="poll",
                options=json.dumps(poll_data["options"]),
                course_id=course.id,
                instructor_id=teacher.id,
                duration_seconds=600,
                is_active=False
            )
            db.session.add(activity)
            activities.append(activity)
        
        # Short answer activity
        short_answer_data = activity_data.get("short_answer")
        if short_answer_data:
            activity = Activity(
                title=short_answer_data["title"],
                question=short_answer_data["question"],
                type="short_answer",
                course_id=course.id,
                instructor_id=teacher.id,
                duration_seconds=1800,
                is_active=False
            )
            db.session.add(activity)
            activities.append(activity)
        
        # Quiz - Multiple Choice
        quiz_mc_data = activity_data.get("quiz_multiple_choice")
        if quiz_mc_data:
            activity = Activity(
                title=quiz_mc_data["title"],
                question=quiz_mc_data["question"],
                type="quiz",
                quiz_type=quiz_mc_data["quiz_type"],
                options=json.dumps(quiz_mc_data["options"]),
                correct_answer=quiz_mc_data["correct_answer"],
                course_id=course.id,
                instructor_id=teacher.id,
                duration_seconds=900,
                is_active=False
            )
            db.session.add(activity)
            activities.append(activity)
        
        # Quiz - True/False
        quiz_tf_data = activity_data.get("quiz_true_false")
        if quiz_tf_data:
            activity = Activity(
                title=quiz_tf_data["title"],
                question=quiz_tf_data["question"],
                type="quiz",
                quiz_type=quiz_tf_data["quiz_type"],
                correct_answer=quiz_tf_data["correct_answer"],
                course_id=course.id,
                instructor_id=teacher.id,
                duration_seconds=300,
                is_active=False
            )
            db.session.add(activity)
            activities.append(activity)
        
        # Quiz - Fill in the Blank
        quiz_fb_data = activity_data.get("quiz_fill_blank")
        if quiz_fb_data:
            activity = Activity(
                title=quiz_fb_data["title"],
                question=quiz_fb_data["question"],
                type="quiz",
                quiz_type=quiz_fb_data["quiz_type"],
                correct_answer=quiz_fb_data["correct_answer"],
                course_id=course.id,
                instructor_id=teacher.id,
                duration_seconds=600,
                is_active=False
            )
            db.session.add(activity)
            activities.append(activity)
        
        # Word cloud activity
        word_cloud_data = activity_data.get("word_cloud")
        if word_cloud_data:
            activity = Activity(
                title=word_cloud_data["title"],
                question=word_cloud_data["question"],
                type="word_cloud",
                course_id=course.id,
                instructor_id=teacher.id,
                duration_seconds=600,
                is_active=False
            )
            db.session.add(activity)
            activities.append(activity)
        
        # Memory game activity
        memory_game_data = activity_data.get("memory_game")
        if memory_game_data:
            activity = Activity(
                title=memory_game_data["title"],
                question=memory_game_data["question"],
                type="memory_game",
                correct_answer=memory_game_data["correct_sequence"],
                course_id=course.id,
                instructor_id=teacher.id,
                duration_seconds=1200,
                is_active=False
            )
            db.session.add(activity)
            activities.append(activity)
    
    db.session.commit()
    print(f"  Created {len(activities)} activities")
    return activities

def create_responses(activities, students):
    """Create responses for each activity"""
    print("Creating student responses...")
    total_responses = 0
    
    for activity in activities:
        course_name = activity.course.name
        activity_type = activity.type
        
        # Get sample answers for this course and activity type
        if course_name in SAMPLE_ANSWERS:
            course_answers = SAMPLE_ANSWERS[course_name]
        else:
            course_answers = {}
        
        # Select 100+ random students for this activity (ensure at least 100)
        num_responses = min(120, len(students))
        if num_responses < 100:
            num_responses = min(100, len(students))
        selected_students = random.sample(students, num_responses)
        
        responses_created = 0
        for student in selected_students:
            # Skip if response already exists
            existing = Response.query.filter_by(
                student_id=student.id,
                activity_id=activity.id
            ).first()
            if existing:
                continue
            
            answer = None
            is_correct = None
            score = 0
            points = 0
            
            if activity_type == "poll":
                # Poll: select random option
                options = json.loads(activity.options) if activity.options else []
                if options:
                    answer = random.choice(options)
            
            elif activity_type == "short_answer":
                # Short answer: use sample answers or generate variation
                sample_answers = course_answers.get("short_answer", [])
                if sample_answers:
                    base_answer = random.choice(sample_answers)
                    # Add more variation to create diverse answers
                    variation_type = random.random()
                    if variation_type < 0.3:  # 30% use base answer as-is
                        answer = base_answer
                    elif variation_type < 0.5:  # 20% add additional sentence
                        additions = [
                            " In addition, this concept is fundamental to understanding the subject.",
                            " Moreover, it helps maintain consistency in practice.",
                            " Furthermore, practical examples make it clearer.",
                            " Additionally, real-world applications demonstrate its importance.",
                            " It is also important to note that this concept has wide applications.",
                        ]
                        answer = base_answer + random.choice(additions)
                    elif variation_type < 0.7:  # 20% modify middle
                        parts = base_answer.split(". ")
                        if len(parts) > 1:
                            mid = len(parts) // 2
                            parts.insert(mid, "Additionally, this approach has several advantages.")
                            answer = ". ".join(parts)
                        else:
                            answer = base_answer
                    else:  # 30% create variation with different wording
                        # Replace some common words/phrases
                        modified = base_answer
                        replacements = [
                            ("important", "crucial"),
                            ("help", "assist"),
                            ("example", "instance"),
                            ("concept", "idea"),
                            ("process", "procedure"),
                            ("understand", "comprehend"),
                        ]
                        for old, new in random.sample(replacements, min(2, len(replacements))):
                            if old in modified.lower():
                                modified = modified.replace(old, new, 1)
                        answer = modified
                else:
                    answer = f"This is a sample answer about {course_name} and {activity.title}."
            
            elif activity_type == "quiz":
                quiz_type = activity.quiz_type
                if quiz_type == "multiple_choice":
                    # Multiple choice: mostly correct answer, some wrong
                    options = json.loads(activity.options) if activity.options else []
                    if random.random() < 0.7:  # 70% correct
                        answer = activity.correct_answer
                        is_correct = True
                        score = 1
                        points = 1
                    else:
                        answer = random.choice([opt for opt in options if opt != activity.correct_answer])
                        is_correct = False
                        score = 0
                        points = 0
                
                elif quiz_type == "true_false":
                    # True/False: mostly correct
                    if random.random() < 0.75:  # 75% correct
                        answer = activity.correct_answer
                        is_correct = True
                        score = 1
                        points = 1
                    else:
                        answer = "False" if activity.correct_answer == "True" else "True"
                        is_correct = False
                        score = 0
                        points = 0
                
                elif quiz_type == "fill_blank":
                    # Fill blank: mostly correct with variations
                    correct = activity.correct_answer.lower().strip()
                    if random.random() < 0.65:  # 65% correct
                        answer = activity.correct_answer
                        is_correct = True
                        score = 1
                        points = 1
                    else:
                        # Generate wrong answers
                        wrong_answers = [
                            "INSERT", "UPDATE", "DELETE", "CREATE",
                            "classification", "regression", "clustering",
                            "unsupervised", "reinforcement", "transfer"
                        ]
                        answer = random.choice(wrong_answers)
                        is_correct = False
                        score = 0
                        points = 0
            
            elif activity_type == "word_cloud":
                # Word cloud: use sample word lists
                sample_words = course_answers.get("word_cloud", [])
                if sample_words:
                    base_words = random.choice(sample_words)
                    # Add some variation
                    word_list = base_words.split(", ")
                    # Randomly add or remove words
                    if random.random() < 0.5 and len(word_list) > 5:
                        word_list = word_list[:-1]
                    elif len(word_list) < 10:
                        extra_words = random.sample([
                            "important", "key", "essential", "fundamental",
                            "advanced", "basic", "complex", "simple"
                        ], 2)
                        word_list.extend(extra_words)
                    answer = ", ".join(word_list)
                else:
                    answer = f"learning, concepts, {course_name.lower()}, important, key, fundamental"
            
            elif activity_type == "memory_game":
                # Memory game: mostly correct sequence, some wrong
                correct_sequence = activity.correct_answer
                if correct_sequence:
                    def normalize_sequence(seq):
                        return [part.strip().lower() for part in seq.split(',') if part.strip()]
                    
                    if random.random() < 0.6:  # 60% correct
                        answer = correct_sequence
                        # Normalize both for comparison
                        normalized_answer = normalize_sequence(answer)
                        normalized_correct = normalize_sequence(correct_sequence)
                        is_correct = normalized_answer == normalized_correct
                        score = 1 if is_correct else 0
                        points = score
                    else:
                        # Generate wrong sequence by swapping elements
                        sequence_parts = [p.strip() for p in correct_sequence.split(",")]
                        if len(sequence_parts) > 1:
                            # Swap two adjacent elements
                            idx = random.randint(0, len(sequence_parts) - 2)
                            sequence_parts[idx], sequence_parts[idx + 1] = sequence_parts[idx + 1], sequence_parts[idx]
                            answer = ", ".join(sequence_parts)
                        else:
                            answer = correct_sequence
                        # Normalize and compare
                        normalized_answer = normalize_sequence(answer)
                        normalized_correct = normalize_sequence(correct_sequence)
                        is_correct = normalized_answer == normalized_correct
                        score = 1 if is_correct else 0
                        points = score
                else:
                    answer = "Sample sequence"
                    is_correct = False
                    score = 0
                    points = 0
            
            if answer is None:
                answer = "Sample answer"
            
            # Create response
            response = Response(
                student_id=student.id,
                activity_id=activity.id,
                answer=answer,
                is_correct=is_correct,
                score=score,
                points_earned=points,
                submitted_at=get_beijing_time() - timedelta(minutes=random.randint(1, 1440))
            )
            db.session.add(response)
            responses_created += 1
            total_responses += 1
            
            # Commit in batches
            if responses_created % 50 == 0:
                db.session.commit()
        
        db.session.commit()
        print(f"  Created {responses_created} responses for activity: {activity.title}")
    
    print(f"  Total responses created: {total_responses}")
    return total_responses

def main():
    """Main function to create all test data"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("Creating Final Test Data")
            print("=" * 60)
            print()
            
            # Create teacher
            teacher = create_teacher()
            print()
            
            # Create test student (no responses)
            test_student = create_test_student()
            print()
            
            # Create students for responses
            students = create_students(150)
            print()
            
            # Create courses
            courses = create_courses(teacher)
            print()
            
            # Enroll students (including test student)
            all_students = students + [test_student]
            enroll_students(courses, all_students)
            print()
            
            # Create activities
            activities = create_activities(courses, teacher)
            print()
            
            # Create responses (only for regular students, not test student)
            create_responses(activities, students)
            print()
            
            print("=" * 60)
            print("Test Data Creation Complete!")
            print("=" * 60)
            print()
            print("Teacher Account:")
            print(f"  Email: {TEACHER_EMAIL}")
            print(f"  Password: {TEACHER_PASSWORD}")
            print()
            print("Test Student Account (No Responses):")
            print(f"  Email: {TEST_STUDENT_EMAIL}")
            print(f"  Password: {TEST_STUDENT_PASSWORD}")
            print()
            print("Summary:")
            print(f"  - Teacher: 1")
            print(f"  - Courses: {len(courses)}")
            print(f"  - Activities: {len(activities)}")
            print(f"  - Students with responses: {len(students)}")
            print(f"  - Test student (no responses): 1")
            print()
            
        except Exception as e:
            print(f"\n❌ Error creating test data: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    main()

