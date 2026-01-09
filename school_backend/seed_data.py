# seed_data.py - Updated for your models

import os
import django
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_backend.settings')
django.setup()

from academics.models import (
    AcademicYear, AcademicTerm, Subject, Class, 
    SubTopic, SubjectAssignment, StudentEnrollment,
    StudentClassAssignment, LessonPlan, Syllabus,
    AcademicEvent, Stream
)

from accounts.models import User  # Import your custom User model

def create_academic_years():
    """Create academic years if they don't exist"""
    print("Creating academic years...")
    
    years_data = [
        {
            'name': '2025/2026 Academic Year',
            'code': 'AY2025-2026',
            'start_date': datetime.date(2025, 9, 1),
            'end_date': datetime.date(2026, 7, 31),
            'is_current': True,
            'description': 'Primary academic year for 2025-2026 session',
            'total_terms': 3,
            'grading_system': 'percentage',
        },
        {
            'name': '2026/2027 Academic Year',
            'code': 'AY2026-2027',
            'start_date': datetime.date(2026, 9, 1),
            'end_date': datetime.date(2027, 7, 31),
            'is_current': False,
            'description': 'Primary academic year for 2026-2027 session',
            'total_terms': 3,
            'grading_system': 'percentage',
        },
        {
            'name': '2027/2028 Academic Year',
            'code': 'AY2027-2028',
            'start_date': datetime.date(2027, 9, 1),
            'end_date': datetime.date(2028, 7, 31),
            'is_current': False,
            'description': 'Primary academic year for 2027-2028 session',
            'total_terms': 3,
            'grading_system': 'percentage',
        }
    ]
    
    academic_years = []
    for data in years_data:
        # Check if exists by name or code
        year = AcademicYear.objects.filter(
            models.Q(name=data['name']) | models.Q(code=data['code'])
        ).first()
        
        if year:
            # Update if exists
            for key, value in data.items():
                setattr(year, key, value)
            year.save()
            print(f"Updated academic year: {year.name}")
        else:
            # Create new
            year = AcademicYear.objects.create(**data)
            print(f"Created academic year: {year.name}")
        
        academic_years.append(year)
    
    return academic_years

def create_academic_terms(academic_year):
    """Create academic terms for a given academic year"""
    print(f"Creating academic terms for {academic_year.name}...")
    
    terms_data = [
        {
            'academic_year': academic_year,
            'name': 'term_1',
            'start_date': academic_year.start_date,
            'end_date': datetime.date(academic_year.start_date.year + (1 if academic_year.start_date.month < 6 else 0), 12, 15),
            'is_current': True if academic_year.is_current else False,
            'term_order': 1,
        },
        {
            'academic_year': academic_year,
            'name': 'term_2',
            'start_date': datetime.date(academic_year.start_date.year + 1, 1, 8),
            'end_date': datetime.date(academic_year.start_date.year + 1, 4, 5),
            'is_current': False,
            'term_order': 2,
        },
        {
            'academic_year': academic_year,
            'name': 'term_3',
            'start_date': datetime.date(academic_year.start_date.year + 1, 4, 23),
            'end_date': academic_year.end_date,
            'is_current': False,
            'term_order': 3,
        }
    ]
    
    terms = []
    for data in terms_data:
        term = AcademicTerm.objects.filter(
            academic_year=data['academic_year'],
            name=data['name']
        ).first()
        
        if term:
            # Update if exists
            for key, value in data.items():
                setattr(term, key, value)
            term.save()
            print(f"Updated term: {term.get_name_display()} for {academic_year.name}")
        else:
            # Create new
            term = AcademicTerm.objects.create(**data)
            print(f"Created term: {term.get_name_display()} for {academic_year.name}")
        
        terms.append(term)
    
    return terms

def create_subjects():
    """Create sample subjects"""
    print("Creating subjects...")
    
    subjects_data = [
        {
            'name': 'Mathematics',
            'code': 'MATH101',
            'short_name': 'Math',
            'description': 'Core mathematics covering algebra, geometry, and calculus',
            'category': 'core',
            'curriculum': 'cbc',
            'difficulty_level': 'intermediate',
            'grade_levels': ['form_1', 'form_2', 'form_3', 'form_4'],
            'credits': 4.0,
            'periods_per_week': 6,
            'is_compulsory': True,
            'has_practical': False,
            'has_theory': True,
        },
        {
            'name': 'English Language',
            'code': 'ENG101',
            'short_name': 'English',
            'description': 'English language and literature studies',
            'category': 'core',
            'curriculum': 'cbc',
            'difficulty_level': 'basic',
            'grade_levels': ['form_1', 'form_2', 'form_3', 'form_4'],
            'credits': 3.0,
            'periods_per_week': 5,
            'is_compulsory': True,
            'has_practical': False,
            'has_theory': True,
        },
        {
            'name': 'Physics',
            'code': 'PHY101',
            'short_name': 'Physics',
            'description': 'Fundamental principles of physics',
            'category': 'sciences',
            'curriculum': 'igcse',
            'difficulty_level': 'advanced',
            'grade_levels': ['form_2', 'form_3', 'form_4'],
            'credits': 4.0,
            'periods_per_week': 5,
            'is_compulsory': False,
            'has_practical': True,
            'has_theory': True,
        },
        {
            'name': 'History',
            'code': 'HIST101',
            'short_name': 'History',
            'description': 'World history and civilizations',
            'category': 'humanities',
            'curriculum': 'american',
            'difficulty_level': 'intermediate',
            'grade_levels': ['form_1', 'form_2', 'form_3'],
            'credits': 3.0,
            'periods_per_week': 4,
            'is_compulsory': False,
            'has_practical': False,
            'has_theory': True,
        },
        {
            'name': 'Computer Science',
            'code': 'CS101',
            'short_name': 'CompSci',
            'description': 'Introduction to programming and computer systems',
            'category': 'technical',
            'curriculum': 'combined',
            'difficulty_level': 'intermediate',
            'grade_levels': ['form_2', 'form_3', 'form_4'],
            'credits': 4.0,
            'periods_per_week': 5,
            'is_compulsory': False,
            'has_practical': True,
            'has_theory': True,
        }
    ]
    
    subjects = []
    for data in subjects_data:
        subject = Subject.objects.filter(code=data['code']).first()
        
        if subject:
            # Update if exists
            for key, value in data.items():
                setattr(subject, key, value)
            subject.save()
            print(f"Updated subject: {subject.name}")
        else:
            # Create new
            subject = Subject.objects.create(**data)
            print(f"Created subject: {subject.name}")
        
        subjects.append(subject)
    
    return subjects

def create_classes(academic_year):
    """Create sample classes for an academic year"""
    print(f"Creating classes for {academic_year.name}...")
    
    classes_data = [
        {
            'name': 'Form 1',
            'grade_level': 'form_1',
            'section': 'A',
            'stream': 'general',
            'room_number': '101',
            'academic_year': academic_year,
            'primary_curriculum': 'cbc',
            'capacity': 30,
            'current_strength': 28,
            'description': 'First year secondary education class',
        },
        {
            'name': 'Form 1',
            'grade_level': 'form_1',
            'section': 'B',
            'stream': 'general',
            'room_number': '102',
            'academic_year': academic_year,
            'primary_curriculum': 'cbc',
            'capacity': 30,
            'current_strength': 26,
            'description': 'First year secondary education class - Section B',
        },
        {
            'name': 'Form 2',
            'grade_level': 'form_2',
            'section': 'A',
            'stream': 'science',
            'room_number': '201',
            'academic_year': academic_year,
            'primary_curriculum': 'icse',
            'capacity': 25,
            'current_strength': 22,
            'description': 'Second year science stream',
        },
        {
            'name': 'Form 2',
            'grade_level': 'form_2',
            'section': 'B',
            'stream': 'arts',
            'room_number': '202',
            'academic_year': academic_year,
            'primary_curriculum': 'american',
            'capacity': 28,
            'current_strength': 24,
            'description': 'Second year arts stream',
        },
        {
            'name': 'Form 3',
            'grade_level': 'form_3',
            'section': 'A',
            'stream': 'science',
            'room_number': '301',
            'academic_year': academic_year,
            'primary_curriculum': 'igcse',
            'capacity': 25,
            'current_strength': 20,
            'description': 'Third year science stream - Advanced',
        }
    ]
    
    classes = []
    for data in classes_data:
        cls = Class.objects.filter(
            name=data['name'],
            academic_year=data['academic_year'],
            section=data['section']
        ).first()
        
        if cls:
            # Update if exists
            for key, value in data.items():
                setattr(cls, key, value)
            cls.save()
            print(f"Updated class: {cls.display_name}")
        else:
            # Create new
            cls = Class.objects.create(**data)
            print(f"Created class: {cls.display_name}")
        
        classes.append(cls)
    
    return classes

def create_subtopics(subjects):
    """Create subtopics for subjects"""
    print("Creating subtopics...")
    
    # Find subjects
    math_subject = next((s for s in subjects if s.code == 'MATH101'), None)
    physics_subject = next((s for s in subjects if s.code == 'PHY101'), None)
    cs_subject = next((s for s in subjects if s.code == 'CS101'), None)
    
    if not math_subject or not physics_subject or not cs_subject:
        print("Required subjects not found for subtopics")
        return []
    
    subtopics_data = [
        {
            'topic': 'Algebra',
            'name': 'Quadratic Equations',
            'subject': math_subject,
            'description': 'Solving quadratic equations using various methods',
            'order': 1,
            'estimated_hours': 6.0,
            'priority': 'high'
        },
        {
            'topic': 'Algebra',
            'name': 'Linear Equations',
            'subject': math_subject,
            'description': 'Solving and graphing linear equations',
            'order': 2,
            'estimated_hours': 4.0,
            'priority': 'medium'
        },
        {
            'topic': 'Mechanics',
            'name': 'Newton\'s Laws of Motion',
            'subject': physics_subject,
            'description': 'Understanding and applying Newton\'s three laws',
            'order': 1,
            'estimated_hours': 8.0,
            'priority': 'high'
        },
        {
            'topic': 'Programming',
            'name': 'Python Basics',
            'subject': cs_subject,
            'description': 'Introduction to Python programming language',
            'order': 1,
            'estimated_hours': 10.0,
            'priority': 'high'
        }
    ]
    
    subtopics = []
    for data in subtopics_data:
        subtopic = SubTopic.objects.filter(
            topic=data['topic'],
            name=data['name'],
            subject=data['subject']
        ).first()
        
        if subtopic:
            # Update if exists
            for key, value in data.items():
                setattr(subtopic, key, value)
            subtopic.save()
            print(f"Updated subtopic: {subtopic.full_name}")
        else:
            # Create new
            subtopic = SubTopic.objects.create(**data)
            print(f"Created subtopic: {subtopic.full_name}")
        
        subtopics.append(subtopic)
    
    return subtopics

def create_academic_events(academic_year, term):
    """Create sample academic events"""
    print("Creating academic events...")
    
    events_data = [
        {
            'title': 'Mid-term Examinations',
            'event_type': 'exam',
            'description': 'First term mid-term examinations for all classes',
            'priority': 'high',
            'start_date': term.start_date + datetime.timedelta(days=45),
            'end_date': term.start_date + datetime.timedelta(days=49),
            'academic_year': academic_year,
            'term': term,
            'venue': 'Exam Hall',
            'organizer': 'Academic Department',
            'is_published': True,
            'requires_attendance': True
        },
        {
            'title': 'Annual Sports Day',
            'event_type': 'sports',
            'description': 'School-wide sports competition and activities',
            'priority': 'medium',
            'start_date': datetime.date(academic_year.start_date.year + 1, 3, 15),
            'end_date': datetime.date(academic_year.start_date.year + 1, 3, 15),
            'academic_year': academic_year,
            'venue': 'School Sports Ground',
            'organizer': 'Sports Department',
            'is_published': True,
            'requires_attendance': False
        },
        {
            'title': 'Parent-Teacher Meeting',
            'event_type': 'parent_meeting',
            'description': 'Termly parent-teacher conference',
            'priority': 'medium',
            'start_date': term.start_date + datetime.timedelta(days=60),
            'end_date': term.start_date + datetime.timedelta(days=60),
            'start_time': datetime.time(14, 0),
            'end_time': datetime.time(17, 0),
            'academic_year': academic_year,
            'term': term,
            'venue': 'School Auditorium',
            'organizer': 'Administration',
            'is_published': True,
            'requires_attendance': True
        }
    ]
    
    events = []
    for data in events_data:
        event = AcademicEvent.objects.filter(
            title=data['title'],
            start_date=data['start_date']
        ).first()
        
        if event:
            # Update if exists
            for key, value in data.items():
                setattr(event, key, value)
            event.save()
            print(f"Updated event: {event.title}")
        else:
            # Create new
            event = AcademicEvent.objects.create(**data)
            print(f"Created event: {event.title}")
        
        events.append(event)
    
    return events

def create_streams():
    """Create sample streams"""
    print("Creating streams...")
    
    streams_data = [
        {
            'name': 'Science Stream',
            'code': 'SCI',
            'description': 'Science focused curriculum with physics, chemistry, biology',
            'grade_level': 'form_3',
            'capacity': 30
        },
        {
            'name': 'Arts Stream',
            'code': 'ART',
            'description': 'Arts and humanities focused curriculum',
            'grade_level': 'form_3',
            'capacity': 35
        },
        {
            'name': 'Commerce Stream',
            'code': 'COM',
            'description': 'Commerce and business studies focused curriculum',
            'grade_level': 'form_3',
            'capacity': 30
        }
    ]
    
    streams = []
    for data in streams_data:
        stream = Stream.objects.filter(code=data['code']).first()
        
        if stream:
            # Update if exists
            for key, value in data.items():
                setattr(stream, key, value)
            stream.save()
            print(f"Updated stream: {stream.name}")
        else:
            # Create new
            stream = Stream.objects.create(**data)
            print(f"Created stream: {stream.name}")
        
        streams.append(stream)
    
    return streams

def create_syllabi(subjects, academic_year):
    """Create sample syllabi"""
    print("Creating syllabi...")
    
    syllabi = []
    for subject in subjects[:3]:  # Create syllabi for first 3 subjects
        syllabus_data = {
            'subject': subject,
            'academic_year': academic_year,
            'curriculum': subject.curriculum,
            'weeks_required': 12,
            'is_complete': False
        }
        
        syllabus = Syllabus.objects.filter(
            subject=subject,
            academic_year=academic_year
        ).first()
        
        if syllabus:
            # Update if exists
            for key, value in syllabus_data.items():
                setattr(syllabus, key, value)
            syllabus.save()
            print(f"Updated syllabus for: {subject.name}")
        else:
            # Create new
            syllabus = Syllabus.objects.create(**syllabus_data)
            print(f"Created syllabus for: {subject.name}")
        
        syllabi.append(syllabus)
    
    return syllabi

def create_sample_users():
    """Create sample users for testing"""
    print("Creating sample users...")
    
    users_data = [
        {
            'email': 'admin@delvok.edu',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_admin': True,
            'is_verified': True,
            'profile_completed': True,
        },
        {
            'email': 'teacher1@delvok.edu',
            'first_name': 'John',
            'last_name': 'Smith',
            'role': User.Role.TEACHER,
            'is_staff': True,
            'staff_id': 'TCH-001',
            'is_verified': True,
            'profile_completed': True,
        },
        {
            'email': 'student1@delvok.edu',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'role': User.Role.STUDENT,
            'admission_number': 'STU-001',
            'is_verified': True,
            'profile_completed': True,
        }
    ]
    
    users = []
    for data in users_data:
        user = User.objects.filter(email=data['email']).first()
        
        if user:
            # Update if exists
            for key, value in data.items():
                if key != 'password':
                    setattr(user, key, value)
            user.set_password('password123')  # Set default password
            user.save()
            print(f"Updated user: {user.email}")
        else:
            # Create new
            user = User.objects.create(**data)
            user.set_password('password123')  # Set default password
            user.save()
            print(f"Created user: {user.email}")
        
        users.append(user)
    
    return users

def main():
    """Main function to seed all data"""
    print("=" * 60)
    print("SEEDING ACADEMIC DATABASE")
    print("=" * 60)
    
    # Import models
    from django.db import models
    
    # 1. Create sample users first
    users = create_sample_users()
    
    # 2. Create academic years
    academic_years = create_academic_years()
    current_year = next((year for year in academic_years if year.is_current), None)
    
    if not current_year:
        current_year = academic_years[0] if academic_years else None
        if current_year:
            current_year.is_current = True
            current_year.save()
    
    if not current_year:
        print("No academic year created!")
        return
    
    # 3. Create academic terms for current year
    terms = create_academic_terms(current_year)
    current_term = next((term for term in terms if term.is_current), terms[0] if terms else None)
    
    # 4. Create subjects
    subjects = create_subjects()
    
    # 5. Create classes for current year
    classes = create_classes(current_year)
    
    # 6. Create subtopics
    subtopics = create_subtopics(subjects)
    
    # 7. Create academic events
    if current_term:
        events = create_academic_events(current_year, current_term)
    
    # 8. Create streams
    streams = create_streams()
    
    # 9. Create syllabi
    syllabi = create_syllabi(subjects, current_year)
    
    # 10. Try to create a sample lesson plan
    try:
        if classes and subjects and current_term and subtopics:
            # Get teacher user
            teacher_user = User.objects.filter(role=User.Role.TEACHER).first()
            
            if teacher_user:
                lesson_plan_data = {
                    'teacher': teacher_user,
                    'subject': subjects[0],  # Mathematics
                    'class_assigned': classes[0],  # Form 1A
                    'academic_year': current_year,
                    'term': current_term,
                    'topic': 'Algebra',
                    'sub_topic': subtopics[0] if subtopics else None,  # Quadratic Equations
                    'week_number': 5,
                    'lesson_date': current_term.start_date + datetime.timedelta(weeks=4),
                    'duration_minutes': 40,
                    'homework': 'Complete worksheet problems 1-10'
                }
                
                lesson_plan = LessonPlan.objects.filter(
                    teacher=teacher_user,
                    subject=subjects[0],
                    class_assigned=classes[0],
                    lesson_date=lesson_plan_data['lesson_date']
                ).first()
                
                if lesson_plan:
                    # Update if exists
                    for key, value in lesson_plan_data.items():
                        setattr(lesson_plan, key, value)
                    lesson_plan.save()
                    print(f"Updated lesson plan: {lesson_plan.topic}")
                else:
                    # Create new
                    lesson_plan = LessonPlan.objects.create(**lesson_plan_data)
                    print(f"Created lesson plan: {lesson_plan.topic}")
    except Exception as e:
        print(f"Could not create lesson plan: {e}")
    
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE")
    print("=" * 60)
    
    # Display summary
    print("\nDATABASE SUMMARY:")
    print(f"Users: {User.objects.count()}")
    print(f"Academic Years: {AcademicYear.objects.count()}")
    print(f"Academic Terms: {AcademicTerm.objects.count()}")
    print(f"Subjects: {Subject.objects.count()}")
    print(f"Classes: {Class.objects.count()}")
    print(f"SubTopics: {SubTopic.objects.count()}")
    print(f"Academic Events: {AcademicEvent.objects.count()}")
    print(f"Streams: {Stream.objects.count()}")
    print(f"Syllabi: {Syllabus.objects.count()}")
    print(f"Lesson Plans: {LessonPlan.objects.count()}")
    
    print("\nCurrent Academic Year:", current_year.name if current_year else "None")
    print("Current Term:", current_term.get_name_display() if current_term else "None")
    
    # Display login information
    print("\n" + "=" * 60)
    print("SAMPLE USER LOGIN CREDENTIALS")
    print("=" * 60)
    for user in users:
        print(f"Email: {user.email}")
        print(f"Password: password123")
        print(f"Role: {user.get_role_display()}")
        print("-" * 30)

if __name__ == "__main__":
    main()