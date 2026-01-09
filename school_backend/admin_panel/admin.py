# admin_panel/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (
    SystemSettings, AuditLog, SystemNotification, 
    APIUsageLog, SystemHealthCheck, UserSession,
    DataExport, SystemMaintenance, SystemBackup
)

User = get_user_model()

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'academic_year', 'contact_email', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one system settings instance
        return not SystemSettings.objects.exists()

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model', 'timestamp', 'ip_address']
    list_filter = ['action', 'model', 'timestamp']
    search_fields = ['user__email', 'action', 'model', 'details']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'is_active', 'start_date', 'end_date', 'created_by']
    list_filter = ['notification_type', 'is_active', 'start_date']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']

@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'endpoint', 'method', 'status_code', 'response_time', 'timestamp']
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['user__email', 'endpoint']
    readonly_fields = ['timestamp']

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_time', 'last_activity', 'is_active']
    list_filter = ['is_active', 'login_time']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['login_time', 'last_activity']

@admin.register(SystemHealthCheck)
class SystemHealthCheckAdmin(admin.ModelAdmin):
    list_display = ['check_type', 'status', 'response_time', 'checked_at']
    list_filter = ['check_type', 'status', 'checked_at']
    readonly_fields = ['checked_at']

@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['user', 'export_type', 'status', 'created_at', 'completed_at']
    list_filter = ['export_type', 'status', 'created_at']
    search_fields = ['user__email', 'export_type']
    readonly_fields = ['created_at']

@admin.register(SystemMaintenance)
class SystemMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'is_active', 'created_by']
    list_filter = ['is_active', 'start_time']
    search_fields = ['title', 'description']

@admin.register(SystemBackup)
class SystemBackupAdmin(admin.ModelAdmin):
    list_display = ['backup_type', 'file_size', 'created_by', 'created_at']
    list_filter = ['backup_type', 'created_at']
    readonly_fields = ['created_at']