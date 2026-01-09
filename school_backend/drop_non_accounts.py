# drop_non_accounts.py
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_backend.settings')
django.setup()

from django.db import connection

def drop_non_accounts_tables():
    with connection.cursor() as cursor:
        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Tables to KEEP
        keep_tables = {
            # Accounts tables
            'accounts_user',
            'accounts_twofactorauth', 
            'accounts_userprofile',
            'accounts_otptoken',
            'accounts_loginhistory',
            'accounts_user_groups',
            'accounts_user_user_permissions',
            
            # Django system tables
            'django_migrations',
            'django_session',
            'django_content_type',
            'django_admin_log',
            'auth_group',
            'auth_permission',
            'auth_group_permissions',
        }
        
        # Drop all other tables
        dropped_count = 0
        for table in tables:
            if table not in keep_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"✓ Dropped: {table}")
                    dropped_count += 1
                except Exception as e:
                    print(f"✗ Failed to drop {table}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        print(f"\n✅ Dropped {dropped_count} tables!")
        print("✅ Remaining tables:")
        
        cursor.execute("SHOW TABLES")
        remaining = [row[0] for row in cursor.fetchall()]
        for table in sorted(remaining):
            print(f"  • {table}")
        
        return dropped_count

if __name__ == "__main__":
    print("=" * 60)
    print("DROPPING ALL NON-ACCOUNTS TABLES")
    print("=" * 60)
    
    confirm = input("\n⚠️  WARNING: This will delete all data except user accounts.\nAre you sure? (yes/NO): ").strip().lower()
    
    if confirm == 'yes':
        drop_non_accounts_tables()
        print("\n" + "=" * 60)
        print("DONE! Only accounts tables remain.")
        print("=" * 60)
    else:
        print("\nOperation cancelled.")