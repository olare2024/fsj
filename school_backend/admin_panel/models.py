from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()

class SystemSettings(models.Model):
    """
    System-wide settings and configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_name = models.CharField(max_length=255, default="Delvok Academy")
    school_logo = models.ImageField(upload_to='school/logo/', blank=True, null=True)
    school_motto = models.CharField(max_length=500, blank=True)
    academic_year = models.CharField(max_length=20, default="2024")
    contact_email = models.EmailField(default="info@delvok.ac.ke")
    contact_phone = models.CharField(max_length=20, default="+254700000000")
    address = models.TextField(blank=True)
    
    # Academic Settings
    max_students_per_class = models.IntegerField(default=40)
    grading_system = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('letter_grade', 'Letter Grade'),
            ('gpa', 'GPA'),
        ],
        default='percentage'
    )
    
    # System Settings
    enable_2fa = models.BooleanField(default=True)
    enable_email_notifications = models.BooleanField(default=True)
    enable_sms_notifications = models.BooleanField(default=False)
    session_timeout = models.IntegerField(default=30, help_text="Session timeout in minutes")
    
    # Backup Settings
    auto_backup = models.BooleanField(default=False)
    backup_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='daily'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("System Settings")
        verbose_name_plural = _("System Settings")
    
    def __str__(self):
        return f"System Settings - {self.school_name}"

class AuditLog(models.Model):
    """
    Audit trail for system activities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email if self.user else 'System'} - {self.action} - {self.timestamp}"

class SystemBackup(models.Model):
    """
    System backup records
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup_file = models.FileField(upload_to='backups/')
    backup_type = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full Backup'),
            ('database', 'Database Only'),
            ('media', 'Media Files Only'),
        ],
        default='full'
    )
    file_size = models.BigIntegerField(help_text="File size in bytes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _("System Backup")
        verbose_name_plural = _("System Backups")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Backup - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class SystemNotification(models.Model):
    """
    System-wide notifications and announcements
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Information'),
            ('warning', 'Warning'),
            ('alert', 'Alert'),
            ('maintenance', 'Maintenance'),
        ],
        default='info'
    )
    target_roles = models.JSONField(
        default=list,
        help_text="List of roles to receive this notification"
    )
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("System Notification")
        verbose_name_plural = _("System Notifications")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class APIUsageLog(models.Model):
    """
    API usage tracking and monitoring
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time = models.FloatField(help_text="Response time in milliseconds")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("API Usage Log")
        verbose_name_plural = _("API Usage Logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['status_code', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.endpoint} - {self.status_code} - {self.timestamp}"

class SystemHealthCheck(models.Model):
    """
    System health monitoring
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check_type = models.CharField(
        max_length=50,
        choices=[
            ('database', 'Database'),
            ('storage', 'Storage'),
            ('email', 'Email Service'),
            ('api', 'API Endpoints'),
            ('background_tasks', 'Background Tasks'),
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('healthy', 'Healthy'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ]
    )
    details = models.JSONField(default=dict)
    response_time = models.FloatField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("System Health Check")
        verbose_name_plural = _("System Health Checks")
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.check_type} - {self.status}"

class UserSession(models.Model):
    """
    Track user sessions for security and analytics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict)
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("User Session")
        verbose_name_plural = _("User Sessions")
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.login_time}"

class DataExport(models.Model):
    """
    Track data export requests
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    export_type = models.CharField(max_length=100)
    filters = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _("Data Export")
        verbose_name_plural = _("Data Exports")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.export_type} - {self.user.email}"

class SystemMaintenance(models.Model):
    """
    System maintenance schedule
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("System Maintenance")
        verbose_name_plural = _("System Maintenance")
        ordering = ['-start_time']
    
    def __str__(self):
        return self.title

# Utility functions
def create_audit_log(user, action, model, object_id=None, details=None, request=None):
    """
    Utility function to create audit logs
    """
    audit_log = AuditLog(
        user=user,
        action=action,
        model=model,
        object_id=str(object_id) if object_id else '',
        details=details or {}
    )
    
    if request:
        audit_log.ip_address = get_client_ip(request)
        audit_log.user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    audit_log.save()
    return audit_log

def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip