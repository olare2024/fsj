# find_date_hierarchy_errors.py
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_backend.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    django.setup()
    
    from django.apps import apps
    
    print("Checking admin configurations...")
    
    # Check all admin classes
    from django.contrib import admin
    
    for model, admin_class in admin.site._registry.items():
        if hasattr(admin_class, 'date_hierarchy'):
            model_name = model.__name__
            field_name = admin_class.date_hierarchy
            
            # Check if field exists in the model
            if not hasattr(model, field_name):
                print(f"ERROR: {admin_class.__class__.__name__} for {model_name}")
                print(f"  → date_hierarchy='{field_name}' but field doesn't exist in {model_name}")
                print(f"  → Available fields: {[f.name for f in model._meta.get_fields()]}")
                print()
    
    print("Check complete.")
    
except Exception as e:
    print(f"Error: {e}")