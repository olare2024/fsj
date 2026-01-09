# fix_all_migrations.py
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_backend.settings')
django.setup()

from django.db import connection
import re

def fix_migration_dependencies():
    print("Fixing migration dependencies...")
    print("=" * 60)
    
    # Define the correct migration order based on your app dependencies
    migration_order = [
        'accounts.0001_initial',      # First - User model
        'academics.0001_initial',     # Second - Academic models
        'teachers.0001_initial',      # Third - Teachers (depends on accounts)
        'students.0001_initial',      # Fourth - Students (depends on accounts, academics)
        'attendance.0001_initial',    # Fifth - Attendance (depends on teachers, students, academics)
        # Add other apps as needed
    ]
    
    with connection.cursor() as cursor:
        # First, clear all migration history except accounts
        cursor.execute("DELETE FROM django_migrations WHERE app != 'accounts'")
        print("✓ Cleared migration history for all apps except accounts")
        
        # Now add migrations in correct order with fake timestamps
        import time
        base_time = time.time() - len(migration_order) * 3600  # Spread over hours
        
        for i, migration in enumerate(migration_order):
            app, name = migration.split('.')
            applied_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(base_time + i*3600))
            
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES (%s, %s, %s)
            """, [app, name, applied_time])
            print(f"✓ Added {migration} to migration history")
    
    print("\n" + "=" * 60)
    print("✅ All migrations added to history in correct order!")
    print("Now you can run: python manage.py migrate --fake")

def create_missing_migrations():
    """Create missing initial migrations for each app"""
    apps = ['academics', 'teachers', 'students', 'attendance', 'grading', 
            'curriculum', 'timetable', 'finance', 'library', 'events']
    
    print("\nCreating missing initial migrations...")
    print("=" * 60)
    
    for app in apps:
        migration_dir = f"{app}/migrations"
        
        # Check if migration directory exists
        if not os.path.exists(migration_dir):
            os.makedirs(migration_dir, exist_ok=True)
            open(f"{migration_dir}/__init__.py", 'w').close()
        
        # Check if 0001_initial.py exists
        initial_migration = f"{migration_dir}/0001_initial.py"
        if not os.path.exists(initial_migration):
            print(f"Creating {app}.0001_initial...")
            os.system(f"python manage.py makemigrations {app} --name 0001_initial --empty")
        else:
            print(f"✓ {app}.0001_initial already exists")

if __name__ == "__main__":
    print("MIGRATION FIX SCRIPT")
    print("=" * 60)
    
    choice = input("\nChoose option:\n1. Fix migration history only\n2. Create missing migrations\n3. Do both (recommended)\nEnter choice (1/2/3): ").strip()
    
    if choice in ['2', '3']:
        create_missing_migrations()
    
    if choice in ['1', '3']:
        fix_migration_dependencies()
    
    print("\n" + "=" * 60)
    print("COMPLETE! Now run these commands:")
    print("1. python manage.py migrate --fake")
    print("2. python manage.py migrate")
    print("=" * 60)