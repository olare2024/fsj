# backend/apps/it/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    SystemComponent, ComponentStatusLog, SupportTicket, TicketComment,
    TimeEntry, SystemAlert, AlertLog, MaintenanceTask, BackupJob,
    PerformanceMetric, KnowledgeBaseArticle, ArticleRating, ITResource,
    ResourceLog, ITProject, ITDashboard
)


class BaseAdmin(admin.ModelAdmin):
    """Base admin class with common configurations"""
    list_display = ['id', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(SystemComponent)
class SystemComponentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'component_code', 'component_type', 'status',
        'criticality', 'ip_address', 'assigned_to', 'department',
        'is_monitored', 'created_at'
    ]
    list_filter = [
        'component_type', 'status', 'criticality',
        'is_monitored', 'department', 'created_at'
    ]
    search_fields = [
        'name', 'component_code', 'ip_address',
        'hostname', 'serial_number', 'asset_tag'
    ]
    readonly_fields = ['created_at', 'updated_at', 'component_code', 'last_check']
    filter_horizontal = ['dependencies']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'component_code', 'component_type', 'description')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'hostname', 'mac_address', 'serial_number', 'asset_tag')
        }),
        ('Hardware Specifications', {
            'fields': ('manufacturer', 'model', 'os', 'firmware_version',
                      'cpu_cores', 'memory_gb', 'storage_gb', 'processor')
        }),
        ('Status and Monitoring', {
            'fields': ('status', 'criticality', 'is_monitored', 'last_check', 'uptime')
        }),
        ('Location and Assignment', {
            'fields': ('location', 'building', 'room', 'rack', 'rack_unit',
                      'assigned_to', 'department')
        }),
        ('Purchase Information', {
            'fields': ('purchase_date', 'warranty_expiry', 'purchase_price', 'vendor')
        }),
        ('Maintenance Information', {
            'fields': ('last_maintenance', 'next_maintenance', 'maintenance_schedule')
        }),
        ('Monitoring URLs', {
            'fields': ('monitoring_url', 'management_url', 'documentation_url')
        }),
        ('Alert Configuration', {
            'fields': ('alert_email', 'alert_threshold_cpu',
                      'alert_threshold_memory', 'alert_threshold_disk')
        }),
        ('Dependencies', {
            'fields': ('dependencies',)
        }),
        ('Additional Information', {
            'fields': ('custom_fields', 'tags', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_active')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by user if new object"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        queryset = super().get_queryset(request)
        return queryset.select_related('assigned_to', 'created_by')
    
    def view_status_logs(self, obj):
        """Link to status logs"""
        count = obj.status_logs.count()
        url = reverse('admin:it_componentstatuslog_changelist') + f'?component__id={obj.id}'
        return format_html('<a href="{}">{} Logs</a>', url, count)
    
    view_status_logs.short_description = 'Status Logs'


@admin.register(ComponentStatusLog)
class ComponentStatusLogAdmin(admin.ModelAdmin):
    list_display = ['component', 'old_status', 'new_status', 'changed_by', 'checked_at']
    list_filter = ['new_status', 'checked_at', 'component__component_type']
    search_fields = ['component__name', 'component__component_code', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('component', 'changed_by')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'title', 'category', 'priority', 'status',
        'created_by', 'assigned_to', 'created_at', 'is_overdue'
    ]
    list_filter = [
        'category', 'priority', 'status', 'sla_status',
        'created_at', 'due_date', 'resolved_at'
    ]
    search_fields = [
        'ticket_number', 'title', 'description',
        'reported_by_name', 'reported_by_email'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'ticket_number',
        'first_response_at', 'resolved_at', 'closed_at'
    ]
    filter_horizontal = ['affected_components', 'related_tickets']
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'priority', 'status')
        }),
        ('People Involved', {
            'fields': ('created_by', 'assigned_to', 'reported_by_name',
                      'reported_by_email', 'reported_by_phone')
        }),
        ('Dates and SLA', {
            'fields': ('due_date', 'sla_target', 'sla_status',
                      'first_response_at', 'resolved_at', 'closed_at')
        }),
        ('Related Items', {
            'fields': ('affected_components', 'related_tickets')
        }),
        ('Time Tracking', {
            'fields': ('estimated_time', 'actual_time', 'time_spent')
        }),
        ('Additional Information', {
            'fields': ('attachments', 'tags', 'impact', 'resolution',
                      'resolution_notes', 'feedback_score', 'feedback_comments')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_active')
        }),
    )
    
    def is_overdue(self, obj):
        """Display overdue status"""
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('created_by', 'assigned_to')
    
    def view_comments(self, obj):
        """Link to comments"""
        count = obj.comments.count()
        url = reverse('admin:it_ticketcomment_changelist') + f'?ticket__id={obj.id}'
        return format_html('<a href="{}">{} Comments</a>', url, count)
    
    def view_time_entries(self, obj):
        """Link to time entries"""
        count = obj.time_entries.count()
        url = reverse('admin:it_timeentry_changelist') + f'?ticket__id={obj.id}'
        return format_html('<a href="{}">{} Time Entries</a>', url, count)


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'created_at', 'is_internal']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['ticket__ticket_number', 'comment', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['mentions']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'user')


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'hours', 'date_worked', 'billable', 'created_at']
    list_filter = ['billable', 'date_worked', 'created_at']
    search_fields = ['ticket__ticket_number', 'user__email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'user')


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'status', 'component', 'detected_at', 'requires_action']
    list_filter = ['severity', 'status', 'source', 'detected_at']
    search_fields = ['title', 'message', 'component__name']
    readonly_fields = ['created_at', 'updated_at', 'detected_at', 'acknowledged_at', 'resolved_at']
    
    def requires_action(self, obj):
        """Display if action is required"""
        return obj.requires_action
    requires_action.boolean = True
    requires_action.short_description = 'Requires Action'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('component', 'ticket', 'assigned_to', 'created_by')
    
    def view_logs(self, obj):
        """Link to alert logs"""
        count = obj.logs.count()
        url = reverse('admin:it_alertlog_changelist') + f'?alert__id={obj.id}'
        return format_html('<a href="{}">{} Logs</a>', url, count)


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['alert__title', 'user__email', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('alert', 'user')


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = [
        'task_number', 'title', 'task_type', 'status',
        'impact_level', 'scheduled_start', 'assigned_to',
        'is_active'
    ]
    list_filter = ['task_type', 'status', 'impact_level', 'scheduled_start']
    search_fields = ['task_number', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'task_number', 'actual_start', 'actual_end']
    filter_horizontal = ['affected_components', 'team_members']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assigned_to', 'created_by', 'approved_by')
    
    def is_active(self, obj):
        """Display if task is active"""
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'


@admin.register(BackupJob)
class BackupJobAdmin(admin.ModelAdmin):
    list_display = [
        'job_name', 'backup_type', 'status', 'scheduled_time',
        'success', 'backup_size', 'created_by', 'created_at'
    ]
    list_filter = ['backup_type', 'status', 'success', 'scheduled_time']
    search_fields = ['job_name', 'source_path', 'destination_path']
    readonly_fields = [
        'created_at', 'updated_at', 'started_at',
        'completed_at', 'duration', 'logs'
    ]
    filter_horizontal = ['components']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
    
    def formatted_size(self, obj):
        """Display formatted size"""
        return obj.formatted_size
    formatted_size.short_description = 'Size'


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = [
        'component', 'cpu_usage', 'memory_usage',
        'disk_usage', 'response_time', 'timestamp'
    ]
    list_filter = ['timestamp', 'component__component_type']
    search_fields = ['component__name', 'component__component_code']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('component')


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'status', 'author',
        'views', 'rating', 'published_at', 'is_published'
    ]
    list_filter = ['category', 'status', 'published_at']
    search_fields = ['title', 'content', 'summary', 'slug']
    readonly_fields = [
        'created_at', 'updated_at', 'slug', 'views',
        'rating', 'helpful_count', 'not_helpful_count',
        'published_at', 'last_reviewed_at'
    ]
    filter_horizontal = ['related_tickets', 'related_components', 'reviewers']
    prepopulated_fields = {'slug': ('title',)}
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'author', 'last_reviewed_by', 'last_updated_by'
        )
    
    def is_published(self, obj):
        """Display if article is published"""
        return obj.is_published
    is_published.boolean = True
    is_published.short_description = 'Published'


@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'helpful', 'created_at']
    list_filter = ['helpful', 'created_at']
    search_fields = ['article__title', 'user__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('article', 'user')


@admin.register(ITResource)
class ITResourceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'resource_code', 'resource_type', 'status',
        'assigned_to', 'quantity', 'purchase_date', 'is_under_warranty'
    ]
    list_filter = ['resource_type', 'status', 'purchase_date', 'warranty_expiry']
    search_fields = [
        'name', 'resource_code', 'serial_number',
        'asset_tag', 'model', 'license_key'
    ]
    readonly_fields = ['created_at', 'updated_at', 'resource_code', 'assigned_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assigned_to', 'created_by', 'installed_on')
    
    def is_under_warranty(self, obj):
        """Display warranty status"""
        return obj.is_under_warranty
    is_under_warranty.boolean = True
    is_under_warranty.short_description = 'Under Warranty'
    
    def view_logs(self, obj):
        """Link to resource logs"""
        count = obj.logs.count()
        url = reverse('admin:it_resourcelog_changelist') + f'?resource__id={obj.id}'
        return format_html('<a href="{}">{} Logs</a>', url, count)


@admin.register(ResourceLog)
class ResourceLogAdmin(admin.ModelAdmin):
    list_display = ['resource', 'action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['resource__name', 'user__email', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('resource', 'user')


@admin.register(ITProject)
class ITProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project_code', 'name', 'status', 'priority',
        'project_manager', 'start_date', 'end_date', 'progress_percentage'
    ]
    list_filter = ['status', 'priority', 'start_date', 'end_date']
    search_fields = ['project_code', 'name', 'description']
    readonly_fields = [
        'created_at', 'updated_at', 'project_code',
        'actual_start_date', 'actual_end_date'
    ]
    filter_horizontal = ['team_members', 'stakeholders', 'resources', 'components']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project_manager', 'created_by')
    
    def progress_percentage(self, obj):
        """Display progress percentage"""
        return f"{obj.progress_percentage}%"
    progress_percentage.short_description = 'Progress'


@admin.register(ITDashboard)
class ITDashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard_type', 'is_public', 'created_by', 'view_count']
    list_filter = ['dashboard_type', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_viewed', 'view_count']
    filter_horizontal = ['allowed_users']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')