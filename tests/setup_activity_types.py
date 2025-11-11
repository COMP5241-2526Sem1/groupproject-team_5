from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Course, Activity, Enrollment, Response


def ensure_user(email, name, role, password):
    user = User.query.filter_by(email=email).first()
    if user:
        user.name = name
        user.role = role
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        return user
    user = User(
        email=email,
        name=name,
        role=role,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return user


def ensure_course(instructor):
    course = Course.query.filter_by(name="Activity Type Showcase", instructor_id=instructor.id).first()
    if course:
        return course
    course = Course(
        name="Activity Type Showcase",
        semester="2025 Spring",
        description="Hands-on course used to verify every activity type.",
        instructor_id=instructor.id,
    )
    db.session.add(course)
    db.session.commit()
    return course


def ensure_enrollments(course, students):
    for student in students:
        exists = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
        if exists:
            continue
        db.session.add(Enrollment(student_id=student.id, course_id=course.id))
    db.session.commit()


def reset_activity(course, title):
    activity = Activity.query.filter_by(course_id=course.id, title=title).first()
    if activity:
        Response.query.filter_by(activity_id=activity.id).delete()
        db.session.delete(activity)
        db.session.commit()


def enrolled_student_ids(course):
    enrollments = Enrollment.query.filter_by(course_id=course.id).order_by(Enrollment.id).all()
    return [enrollment.student_id for enrollment in enrollments]


def create_poll(course, instructor):
    title = "Poll: Preferred Study Time"
    reset_activity(course, title)
    activity = Activity(
        title=title,
        type="poll",
        question="Which study time suits you best?",
        options="Morning\nAfternoon\nEvening",
        course_id=course.id,
        instructor_id=instructor.id,
        duration_minutes=5,
    )
    db.session.add(activity)
    db.session.commit()
    responses = ["Morning", "Afternoon", "Evening", "Evening"]
    student_ids = enrolled_student_ids(course)
    for idx, answer in enumerate(responses[: len(student_ids)]):
        db.session.add(
            Response(
                student_id=student_ids[idx],
                activity_id=activity.id,
                answer=answer,
                submitted_at=datetime.utcnow() - timedelta(minutes=idx),
            )
        )
    db.session.commit()


def create_short_answer(course, instructor):
    title = "Short Answer: Collaborative Learning"
    reset_activity(course, title)
    activity = Activity(
        title=title,
        type="short_answer",
        question="Describe one strategy that makes group study effective.",
        course_id=course.id,
        instructor_id=instructor.id,
        duration_minutes=10,
    )
    db.session.add(activity)
    db.session.commit()
    student_ids = enrolled_student_ids(course)
    answers = [
        "Assign clear roles so everyone understands their responsibility.",
        "Set a shared goal for the session and check progress halfway through.",
        "Rotate the note taker so each teammate stays engaged.",
        "Use quick summaries at the end to reinforce the key points.",
    ]
    for idx, answer in enumerate(answers[: len(student_ids)]):
        db.session.add(
            Response(
                student_id=student_ids[idx],
                activity_id=activity.id,
                answer=answer,
                submitted_at=datetime.utcnow() - timedelta(minutes=idx * 2),
            )
        )
    db.session.commit()


def create_quiz(course, instructor):
    base_question = "Choose the best explanation for active recall."
    title = "Quiz: Study Techniques"
    reset_activity(course, title)
    activity = Activity(
        title=title,
        type="quiz",
        question=base_question,
        quiz_type="multiple_choice",
        options="Testing yourself without notes\nRereading the textbook\nHighlighting every paragraph\nListening to a lecture",
        correct_answer="Testing yourself without notes",
        course_id=course.id,
        instructor_id=instructor.id,
        duration_minutes=5,
    )
    db.session.add(activity)
    db.session.commit()
    student_ids = enrolled_student_ids(course)
    attempts = [
        ("Testing yourself without notes", True, 1),
        ("Rereading the textbook", False, 0),
        ("Testing yourself without notes", True, 1),
    ]
    for idx, (answer, is_correct, score) in enumerate(attempts[: len(student_ids)]):
        db.session.add(
            Response(
                student_id=student_ids[idx],
                activity_id=activity.id,
                answer=answer,
                is_correct=is_correct,
                score=score,
                submitted_at=datetime.utcnow() - timedelta(minutes=idx * 3),
            )
        )
    db.session.commit()


def create_word_cloud(course, instructor):
    title = "Word Cloud: Motivating Words"
    reset_activity(course, title)
    activity = Activity(
        title=title,
        type="word_cloud",
        question="Submit three words that keep you motivated to study (comma separated).",
        course_id=course.id,
        instructor_id=instructor.id,
        duration_minutes=5,
    )
    db.session.add(activity)
    db.session.commit()
    student_ids = enrolled_student_ids(course)
    entries = [
        "focus, resilience, growth",
        "discipline, curiosity, clarity",
        "balance, progress, optimism",
        "curiosity, focus, momentum",
    ]
    for idx, answer in enumerate(entries[: len(student_ids)]):
        db.session.add(
            Response(
                student_id=student_ids[idx],
                activity_id=activity.id,
                answer=answer,
                submitted_at=datetime.utcnow() - timedelta(minutes=idx),
            )
        )
    db.session.commit()


def create_memory_game(course, instructor):
    title = "Memory Game: Study Checklist"
    reset_activity(course, title)
    activity = Activity(
        title=title,
        type="memory_game",
        question="Remember the checklist shown during class and reproduce the order.",
        course_id=course.id,
        instructor_id=instructor.id,
        duration_minutes=5,
    )
    db.session.add(activity)
    db.session.commit()
    student_ids = enrolled_student_ids(course)
    sequences = [
        "Preview notes, Attend lecture, Review",
        "Plan, Execute, Reflect",
        "Research, Outline, Draft",
    ]
    for idx, answer in enumerate(sequences[: len(student_ids)]):
        is_correct = idx % 2 == 0
        db.session.add(
            Response(
                student_id=student_ids[idx],
                activity_id=activity.id,
                answer=answer,
                submitted_at=datetime.utcnow() - timedelta(minutes=idx * 4),
                is_correct=is_correct,
                score=1 if is_correct else 0,
                points_earned=1 if is_correct else 0,
            )
        )
    db.session.commit()


def main():
    app = create_app()
    with app.app_context():
        instructor = ensure_user("activity_tester@example.com", "Activity Coach", "instructor", "teach123")
        students = [
            ensure_user("activity_student1@example.com", "Activity Student 1", "student", "learn123"),
            ensure_user("activity_student2@example.com", "Activity Student 2", "student", "learn123"),
            ensure_user("activity_student3@example.com", "Activity Student 3", "student", "learn123"),
            ensure_user("activity_student4@example.com", "Activity Student 4", "student", "learn123"),
            ensure_user("activity_student5@example.com", "Activity Student 5", "student", "learn123"),
        ]
        course = ensure_course(instructor)
        ensure_enrollments(course, students)
        create_poll(course, instructor)
        create_short_answer(course, instructor)
        create_quiz(course, instructor)
        create_word_cloud(course, instructor)
        create_memory_game(course, instructor)
        print("Test activities ready.")
        print("Instructor login: activity_tester@example.com / teach123")
        print("Students with sample responses: activity_student1-4@example.com / learn123")
        print("Fresh student (no submissions yet): activity_student5@example.com / learn123")
        print("Open the instructor dashboard, pick 'Activity Type Showcase', and review each activity.")


if __name__ == "__main__":
    main()

