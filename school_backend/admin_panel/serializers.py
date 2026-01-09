from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    SystemSettings, AuditLog, SystemNotification, 
    APIUsageLog, SystemHealthCheck, UserSession
)
from accounts.models import User

User = get_user_model()

class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user management"""
    full_name = serializers.SerializerMethodField()
    last_login_display = serializers.SerializerMethodField()
    date_joined_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'role',
            'is_active', 'is_verified', 'is_approved', 'date_joined',
            'date_joined_display', 'last_login', 'last_login_display', 
            'phone_number', 'department', 'grade_level', 'admission_number', 
            'staff_id', 'is_suspended', 'is_on_leave'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    
    def get_date_joined_display(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d %H:%M')

class UserCreateSerializer(serializers.ModelSerializer):
    """Fixed UserCreateSerializer for creating users from admin panel"""
    password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        style={'input_type': 'password'},
        required=True
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        required=True
    )

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role', 
            'password', 'confirm_password',
            'phone_number', 'department', 'grade_level', 'primary_curriculum'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True},
        }

    def validate_email(self, value):
        """Validate email uniqueness"""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        """Validate the complete data"""
        print("=" * 60)
        print("🔄 [VALIDATE] Starting comprehensive validation")
        print(f"📦 [VALIDATE] Raw data: {attrs}")
        
        # Check password match
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        print(f"🔑 [VALIDATE] Password: {password}")
        print(f"🔑 [VALIDATE] Confirm Password: {confirm_password}")
        
        if password != confirm_password:
            print("❌ [VALIDATE] Passwords don't match!")
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        print("✅ [VALIDATE] Passwords match")

        # Role-specific validation
        role = attrs.get('role')
        print(f"👤 [VALIDATE] Role: {role}")
        
        if role == 'student':
            if not attrs.get('grade_level'):
                print("❌ [VALIDATE] Student missing grade_level")
                raise serializers.ValidationError({
                    "grade_level": "Grade level is required for students."
                })
            if not attrs.get('primary_curriculum'):
                print("❌ [VALIDATE] Student missing primary_curriculum")
                raise serializers.ValidationError({
                    "primary_curriculum": "Primary curriculum is required for students."
                })
            print("✅ [VALIDATE] Student validation passed")
            
        elif role in ['teacher', 'admin', 'head_teacher', 'accountant', 'it_support']:
            if not attrs.get('department'):
                print("❌ [VALIDATE] Staff missing department")
                raise serializers.ValidationError({
                    "department": "Department is required for staff members."
                })
            print("✅ [VALIDATE] Staff validation passed")

        print("✅ [VALIDATE] All validations passed successfully")
        print("=" * 60)
        return attrs

    def create(self, validated_data):
        """Create user with proper error handling"""
        print("=" * 60)
        print("🚀 [CREATE] Starting user creation process")
        print(f"📦 [CREATE] Validated data keys: {list(validated_data.keys())}")
        
        # Remove confirm_password from validated data
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        print(f"🔑 [CREATE] Password length: {len(password)}")
        print(f"👤 [CREATE] Role: {validated_data.get('role')}")
        print(f"📧 [CREATE] Email: {validated_data.get('email')}")
        
        # Set default values
        validated_data.setdefault('is_active', True)
        validated_data.setdefault('is_verified', True)
        
        # Auto-approve staff roles
        role = validated_data.get('role')
        if role in ['teacher', 'admin', 'head_teacher', 'accountant', 'it_support']:
            validated_data.setdefault('is_approved', True)
            validated_data.setdefault('is_staff', True)
            print(f"✅ [CREATE] Auto-approved staff user")
        
        print(f"📦 [CREATE] Final data before creation: {validated_data}")
        
        try:
            # Use create_user method from CustomUserManager
            # The admission_number and staff_id will be auto-generated by the User model's save method
            print("💾 [CREATE] Calling User.objects.create_user()")
            user = User.objects.create_user(
                password=password,
                **validated_data
            )
            
            print(f"✅ [CREATE] User created successfully!")
            print(f"📝 [CREATE] User details:")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - Role: {user.role}")
            print(f"   - Admission: {user.admission_number}")
            print(f"   - Staff ID: {user.staff_id}")
            print(f"   - Active: {user.is_active}")
            print(f"   - Approved: {user.is_approved}")
            print(f"   - Staff: {user.is_staff}")
            
            return user
            
        except Exception as e:
            print(f"❌ [CREATE] ERROR creating user: {str(e)}")
            print(f"❌ [CREATE] Error type: {type(e).__name__}")
            import traceback
            print(f"❌ [CREATE] Traceback: {traceback.format_exc()}")
            raise serializers.ValidationError({
                "non_field_errors": [f"Failed to create user: {str(e)}"]
            })

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users from admin panel"""
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role', 'phone_number', 
            'department', 'grade_level', 'admission_number', 'staff_id',
            'is_active', 'is_verified', 'is_approved', 'is_suspended', 'is_on_leave'
        ]

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_users = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_parents = serializers.IntegerField()
    total_admins = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()

class AnalyticsSerializer(serializers.Serializer):
    """Serializer for analytics data"""
    user_growth = serializers.DictField()
    system_usage = serializers.DictField()

class BulkActionSerializer(serializers.Serializer):
    """Serializer for bulk user actions"""
    action = serializers.ChoiceField(choices=['activate', 'deactivate', 'delete'])
    user_ids = serializers.ListField(
        child=serializers.UUIDField()
    )

class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']

class SystemNotificationSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_full_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = SystemNotification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'created_by']

class APIUsageLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = APIUsageLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']

class SystemHealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealthCheck
        fields = '__all__'
        read_only_fields = ['id', 'checked_at']

class UserSessionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserSession
        fields = '__all__'
        read_only_fields = ['id', 'login_time', 'last_activity']

# Additional utility serializers
class UserRoleStatsSerializer(serializers.Serializer):
    """Serializer for user role statistics"""
    role = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()

class SystemOverviewSerializer(serializers.Serializer):
    """Serializer for system overview"""
    total_users = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    storage_usage = serializers.DictField()
    recent_activities = serializers.ListField(child=serializers.DictField())
    system_health = serializers.DictField()

class ExportDataSerializer(serializers.Serializer):
    """Serializer for data export requests"""
    export_type = serializers.ChoiceField(choices=[
        ('users', 'Users'),
        ('students', 'Students'),
        ('teachers', 'Teachers'),
        ('enrollments', 'Enrollments'),
        ('grades', 'Grades'),
    ])
    format = serializers.ChoiceField(choices=[('csv', 'CSV'), ('excel', 'Excel')])
    filters = serializers.DictField(required=False)
    include_sensitive_data = serializers.BooleanField(default=False)