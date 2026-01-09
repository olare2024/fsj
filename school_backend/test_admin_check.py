# find_teacher_leave_fk.py
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_backend.settings')
django.setup()

try:
    from teachers.models import TeacherLeave
    from teachers.models import TeacherProfile
    
    print("Checking TeacherLeave model structure...")
    print("=" * 60)
    
    # Get all fields
    print("\nAll fields in TeacherLeave:")
    for field in TeacherLeave._meta.get_fields():
        field_type = field.__class__.__name__
        print(f"  - {field.name}: {field_type}")
        
        # If it's a relation field, show what it points to
        if hasattr(field, 'related_model') and field.related_model:
            print(f"     → points to: {field.related_model.__name__}")
    
    print("\n" + "=" * 60)
    print("Checking ForeignKeys specifically:")
    
    # Count ForeignKeys to TeacherProfile
    fk_to_teacherprofile = []
    for field in TeacherLeave._meta.get_fields():
        if hasattr(field, 'related_model') and field.related_model == TeacherProfile:
            fk_to_teacherprofile.append(field.name)
            print(f"  - {field.name}: ForeignKey to TeacherProfile")
    
    print(f"\nTotal ForeignKeys to TeacherProfile: {len(fk_to_teacherprofile)}")
    
    if len(fk_to_teacherprofile) > 1:
        print("\n⚠️ WARNING: Multiple ForeignKeys found. TeacherLeaveInline MUST specify fk_name.")
        print("\nPossible fk_name values:")
        for fk in fk_to_teacherprofile:
            print(f"  fk_name = '{fk}'")
    elif len(fk_to_teacherprofile) == 1:
        print(f"\n✅ Only one ForeignKey found. fk_name should be: '{fk_to_teacherprofile[0]}'")
    else:
        print("\n❌ No ForeignKey to TeacherProfile found!")
        
    print("\n" + "=" * 60)
    print("Checking model string attributes (potential problem sources):")
    
    for attr_name in dir(TeacherLeave):
        if not attr_name.startswith('_'):  # Skip private attributes
            attr_value = getattr(TeacherLeave, attr_name, None)
            if isinstance(attr_value, str):
                print(f"  - {attr_name}: '{attr_value}'")
                
except ImportError as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()