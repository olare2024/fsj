from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Q, F
from django.core.cache import cache
import csv
from django.http import HttpResponse
from datetime import datetime, timedelta

from .models import Notification, NotificationTemplate, UserNotificationSettings, NotificationStats


# ==================== CUSTOM FILTERS ====================

class ExpiredFilter(SimpleListFilter):
    """Filter notifications by expiration status"""
    title = 'Expiration Status'
    parameter_name = 'expired'

    def lookups(self, request, model_admin):
        return (
            ('expired', 'Expired'),
            ('active', 'Active'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'expired':
            return queryset.filter(expires_at__lt=now)
        elif self.value() == 'active':
            return queryset.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=now))
        return queryset


class DeliveryStatusFilter(SimpleListFilter):
    """Filter by delivery status"""
    title = 'Delivery Status'
    parameter_name = 'delivery_status'

    def lookups(self, request, model_admin):
        return (
            ('delivered', 'Delivered'),
            ('failed', 'Failed'),
            ('partial', 'Partially Delivered'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'delivered':
            return queryset.filter(sent_at__isnull=False)
        elif self.value() == 'failed':
            return queryset.filter(sent_at__isnull=True, created_at__lt=timezone.now() - timedelta(hours=1))
        elif self.value() == 'partial':
            return queryset.filter(
                Q(email_sent=False, delivery_method__in=['email', 'all']) |
                Q(sms_sent=False, delivery_method__in=['sms', 'all']) |
                Q(push_sent=False, delivery_method__in=['push', 'all'])
            )
        return queryset


class UserRoleFilter(SimpleListFilter):
    """Filter by user role"""
    title = 'User Role'
    parameter_name = 'user_role'

    def lookups(self, request, model_admin):
        from accounts.models import User
        roles = User.objects.values_list('role', flat=True).distinct()
        return [(role, role.title()) for role in roles]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__role=self.value())
        return queryset


class PriorityFilter(SimpleListFilter):
    """Filter by priority"""
    title = 'Priority'
    parameter_name = 'priority'

    def lookups(self, request, model_admin):
        return Notification.PRIORITY_LEVELS

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(priority=self.value())
        return queryset


# ==================== CUSTOM ACTIONS ====================

@admin.action(description='Mark selected as read')
def mark_as_read(modeladmin, request, queryset):
    updated = queryset.filter(status='unread').update(status='read', read_at=timezone.now())
    modeladmin.message_user(request, f'{updated} notifications marked as read.')


@admin.action(description='Mark selected as unread')
def mark_as_unread(modeladmin, request, queryset):
    updated = queryset.filter(status='read').update(status='unread', read_at=None)
    modeladmin.message_user(request, f'{updated} notifications marked as unread.')


@admin.action(description='Archive selected')
def archive_notifications(modeladmin, request, queryset):
    updated = queryset.exclude(status='archived').update(status='archived')
    modeladmin.message_user(request, f'{updated} notifications archived.')


@admin.action(description='Resend selected notifications')
def resend_notifications(modeladmin, request, queryset):
    success_count = 0
    fail_count = 0
    
    for notification in queryset:
        try:
            if notification.send():
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            fail_count += 1
    
    modeladmin.message_user(
        request, 
        f'{success_count} notifications resent successfully. {fail_count} failed.'
    )


@admin.action(description='Export selected notifications to CSV')
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="notifications_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'User', 'User Email', 'User Role', 'Title', 'Type', 'Priority', 'Status',
        'Created At', 'Read At', 'Expires At', 'Sent At',
        'Email Sent', 'SMS Sent', 'Push Sent', 'In App Sent',
        'Channel', 'Delivery Method', 'Sender', 'Is Expired'
    ])
    
    for notification in queryset:
        writer.writerow([
            str(notification.id),
            notification.user.get_full_name(),
            notification.user.email,
            notification.user.role if hasattr(notification.user, 'role') else '',
            notification.title,
            notification.get_type_display(),
            notification.get_priority_display(),
            notification.get_status_display(),
            notification.created_at.strftime('%Y-%m-%d %H:%M:%S') if notification.created_at else '',
            notification.read_at.strftime('%Y-%m-%d %H:%M:%S') if notification.read_at else '',
            notification.expires_at.strftime('%Y-%m-%d %H:%M:%S') if notification.expires_at else '',
            notification.sent_at.strftime('%Y-%m-%d %H:%M:%S') if notification.sent_at else '',
            'Yes' if notification.email_sent else 'No',
            'Yes' if notification.sms_sent else 'No',
            'Yes' if notification.push_sent else 'No',
            'Yes' if notification.in_app_sent else 'No',
            notification.get_channel_display(),
            notification.get_delivery_method_display(),
            notification.sender.email if notification.sender else '',
            'Yes' if notification.is_expired else 'No'
        ])
    
    return response


@admin.action(description='Clean up expired notifications')
def cleanup_expired(modeladmin, request, queryset):
    now = timezone.now()
    expired = queryset.filter(expires_at__lt=now, status__in=['unread', 'read'])
    archived_count = expired.update(status='archived')
    modeladmin.message_user(request, f'{archived_count} expired notifications archived.')


# ==================== INLINE ADMIN CLASSES ====================

class NotificationStatsInline(admin.TabularInline):
    """Inline for showing notification stats"""
    model = NotificationStats
    extra = 0
    can_delete = False
    readonly_fields = ['date', 'notification_type', 'channel', 'sent_count', 
                       'delivered_count', 'read_count', 'delivery_rate_display']
    max_num = 10
    
    def delivery_rate_display(self, obj):
        return f"{obj.delivery_rate:.1f}%"
    delivery_rate_display.short_description = 'Delivery Rate'
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== MODEL ADMIN CLASSES ====================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    
    # List display
    list_display = [
        'id_truncated',
        'user_link',
        'title_truncated',
        'type_display',
        'priority_badge',
        'status_badge',
        'created_ago',
        'delivery_status',
        'actions_column'
    ]
    
    list_display_links = ['id_truncated', 'title_truncated']
    
    # List filters
    list_filter = [
        ExpiredFilter,
        DeliveryStatusFilter,
        UserRoleFilter,
        PriorityFilter,
        'type',
        'channel',
        'status',
        'delivery_method',
        'created_at',
    ]
    
    # Search
    search_fields = [
        'title',
        'message',
        'user__email',
        'user__first_name',
        'user__last_name',
        'sender__email',
    ]
    
    # Actions
    actions = [
        mark_as_read,
        mark_as_unread,
        archive_notifications,
        resend_notifications,
        export_to_csv,
        cleanup_expired
    ]
    
    # Fields for detail view
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'sender', 'title', 'message', 'type', 'priority', 'channel')
        }),
        ('Status & Delivery', {
            'fields': ('status', 'delivery_method', ('email_sent', 'sms_sent', 'push_sent', 'in_app_sent'))
        }),
        ('Dates & Timing', {
            'fields': (('created_at', 'updated_at'), ('read_at', 'sent_at'), 'expires_at')
        }),
        ('Related Data', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('data', 'actions', 'metadata'),
            'classes': ('collapse',)
        }),
    )
    
    # Readonly fields
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'read_at', 
        'sent_at',
        'email_sent',
        'sms_sent',
        'push_sent',
        'in_app_sent'
    ]
    
    # Autocomplete fields
    autocomplete_fields = ['user', 'sender']
    
    # Pagination
    list_per_page = 50
    show_full_result_count = True
    
    # Custom methods for list display
    def id_truncated(self, obj):
        return str(obj.id)[:8] + '...'
    id_truncated.short_description = 'ID'
    id_truncated.admin_order_field = 'id'
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_changelist') + f'?id={obj.user.id}'
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__email'
    
    def title_truncated(self, obj):
        if len(obj.title) > 50:
            return obj.title[:47] + '...'
        return obj.title
    title_truncated.short_description = 'Title'
    
    def type_display(self, obj):
        return obj.get_type_display()
    type_display.short_description = 'Type'
    type_display.admin_order_field = 'type'
    
    def priority_badge(self, obj):
        color_map = {
            'urgent': 'red',
            'high': 'orange',
            'medium': 'blue',
            'low': 'green'
        }
        color = color_map.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def status_badge(self, obj):
        color_map = {
            'unread': 'red',
            'read': 'green',
            'archived': 'gray',
            'deleted': 'darkgray'
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def created_ago(self, obj):
        if not obj.created_at:
            return ''
        delta = timezone.now() - obj.created_at
        if delta.days > 0:
            return f'{delta.days}d ago'
        elif delta.seconds > 3600:
            return f'{delta.seconds // 3600}h ago'
        elif delta.seconds > 60:
            return f'{delta.seconds // 60}m ago'
        else:
            return f'{delta.seconds}s ago'
    created_ago.short_description = 'Created'
    created_ago.admin_order_field = 'created_at'
    
    def delivery_status(self, obj):
        statuses = []
        if obj.delivery_method in ['email', 'all']:
            statuses.append(f'📧: {"✓" if obj.email_sent else "✗"}')
        if obj.delivery_method in ['sms', 'all']:
            statuses.append(f'📱: {"✓" if obj.sms_sent else "✗"}')
        if obj.delivery_method in ['push', 'all']:
            statuses.append(f'📲: {"✓" if obj.push_sent else "✗"}')
        if obj.delivery_method in ['in_app', 'all']:
            statuses.append(f'🖥️: {"✓" if obj.in_app_sent else "✗"}')
        return format_html(' '.join(statuses))
    delivery_status.short_description = 'Delivery'
    
    def actions_column(self, obj):
        buttons = []
        if obj.status == 'unread':
            buttons.append(f'<a href="#" class="button" onclick="markAsRead(\'{obj.id}\')">Mark Read</a>')
        if obj.status == 'read':
            buttons.append(f'<a href="#" class="button" onclick="markAsUnread(\'{obj.id}\')">Mark Unread</a>')
        if obj.status not in ['archived', 'deleted']:
            buttons.append(f'<a href="#" class="button" onclick="archiveNotification(\'{obj.id}\')">Archive</a>')
        return format_html(' '.join(buttons))
    actions_column.short_description = 'Actions'
    
    # Custom changelist view
    def changelist_view(self, request, extra_context=None):
        # Add stats to context
        extra_context = extra_context or {}
        
        # Calculate stats
        total_count = Notification.objects.count()
        unread_count = Notification.objects.filter(status='unread').count()
        read_count = Notification.objects.filter(status='read').count()
        urgent_count = Notification.objects.filter(priority='urgent', status='unread').count()
        
        # Recent activity (last 24 hours)
        day_ago = timezone.now() - timedelta(days=1)
        recent_count = Notification.objects.filter(created_at__gte=day_ago).count()
        
        # Delivery stats
        email_success_rate = 0
        if Notification.objects.filter(delivery_method__in=['email', 'all']).count() > 0:
            email_success_rate = (Notification.objects.filter(email_sent=True).count() / 
                                 Notification.objects.filter(delivery_method__in=['email', 'all']).count() * 100)
        
        extra_context.update({
            'total_count': total_count,
            'unread_count': unread_count,
            'read_count': read_count,
            'urgent_count': urgent_count,
            'recent_count': recent_count,
            'email_success_rate': round(email_success_rate, 1),
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    # Custom JavaScript for admin
    class Media:
        js = (
            'admin/js/notification_admin.js',
        )


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for NotificationTemplate model"""
    
    list_display = [
        'name',
        'template_type_display',
        'default_priority_display',
        'default_channel_display',
        'is_active',
        'created_ago',
        'preview_link'
    ]
    
    list_filter = [
        'template_type',
        'default_priority',
        'default_channel',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'title_template',
        'message_template',
        'description'
    ]
    
    list_editable = ['is_active']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'description', 'is_active')
        }),
        ('Template Content', {
            'fields': ('title_template', 'message_template')
        }),
        ('Default Settings', {
            'fields': ('default_priority', 'default_channel', 'default_delivery')
        }),
        ('Template Variables', {
            'fields': ('variables',),
            'description': 'Define variables that can be used in the template'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def template_type_display(self, obj):
        return obj.get_template_type_display()
    template_type_display.short_description = 'Type'
    template_type_display.admin_order_field = 'template_type'
    
    def default_priority_display(self, obj):
        return obj.get_default_priority_display()
    default_priority_display.short_description = 'Priority'
    default_priority_display.admin_order_field = 'default_priority'
    
    def default_channel_display(self, obj):
        return obj.get_default_channel_display()
    default_channel_display.short_description = 'Channel'
    default_channel_display.admin_order_field = 'default_channel'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: gray; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">Inactive</span>'
            )
    is_active_badge.short_description = 'Status'
    
    def created_ago(self, obj):
        if not obj.created_at:
            return ''
        delta = timezone.now() - obj.created_at
        if delta.days > 365:
            return f'{delta.days // 365}y ago'
        elif delta.days > 30:
            return f'{delta.days // 30}m ago'
        elif delta.days > 0:
            return f'{delta.days}d ago'
        else:
            return 'Today'
    created_ago.short_description = 'Created'
    
    def preview_link(self, obj):
        url = reverse('admin:notifications_notificationtemplate_preview', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Preview</a>', url)
    preview_link.short_description = 'Preview'
    
    @admin.action(description='Activate selected templates')
    def activate_templates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} templates activated.')
    
    @admin.action(description='Deactivate selected templates')
    def deactivate_templates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} templates deactivated.')


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    """Admin interface for UserNotificationSettings model"""
    
    list_display = [
        'user_link',
        'email_notifications',
        'sms_notifications',
        'push_notifications',
        'in_app_notifications',
        'quiet_hours_status',
        'updated_ago'
    ]
    
    list_filter = [
        'email_notifications',
        'sms_notifications',
        'push_notifications',
        'in_app_notifications',
        'quiet_hours_enabled',
        'sound_enabled',
        'desktop_notifications'
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Global Settings', {
            'fields': (
                'email_notifications',
                'sms_notifications',
                'push_notifications',
                'in_app_notifications',
                'sound_enabled',
                'desktop_notifications'
            )
        }),
        ('Quiet Hours', {
            'fields': (
                'quiet_hours_enabled',
                ('quiet_hours_start', 'quiet_hours_end')
            )
        }),
        ('Digest Frequency', {
            'fields': ('digest_frequency', 'last_digest_sent')
        }),
        ('Notification Preferences', {
            'fields': ('notification_preferences',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_changelist') + f'?id={obj.user.id}'
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__email'
    
    def quiet_hours_status(self, obj):
        if not obj.quiet_hours_enabled:
            return format_html(
                '<span style="color: gray;">Disabled</span>'
            )
        
        if obj.is_quiet_hours():
            return format_html(
                '<span style="color: red; font-weight: bold;">Active ({}-{})</span>',
                obj.quiet_hours_start.strftime('%H:%M'),
                obj.quiet_hours_end.strftime('%H:%M')
            )
        else:
            return format_html(
                '<span style="color: green;">Inactive ({}-{})</span>',
                obj.quiet_hours_start.strftime('%H:%M'),
                obj.quiet_hours_end.strftime('%H:%M')
            )
    quiet_hours_status.short_description = 'Quiet Hours'
    
    def updated_ago(self, obj):
        if not obj.updated_at:
            return ''
        delta = timezone.now() - obj.updated_at
        if delta.days > 30:
            return f'{delta.days // 30}m ago'
        elif delta.days > 0:
            return f'{delta.days}d ago'
        elif delta.seconds > 3600:
            return f'{delta.seconds // 3600}h ago'
        else:
            return 'Recently'
    updated_ago.short_description = 'Last Updated'


@admin.register(NotificationStats)
class NotificationStatsAdmin(admin.ModelAdmin):
    """Admin interface for NotificationStats model"""
    
    list_display = [
        'date',
        'notification_type_display',
        'channel_display',
        'sent_count',
        'delivered_count',
        'read_count',
        'delivery_rate_display',
        'read_rate_display'
    ]
    
    list_filter = [
        'date',
        'notification_type',
        'channel'
    ]
    
    search_fields = [
        'notification_type',
        'channel'
    ]
    
    readonly_fields = [
        'date',
        'notification_type',
        'channel',
        'sent_count',
        'delivered_count',
        'read_count',
        'clicked_count',
        'failed_count',
        'email_sent',
        'sms_sent',
        'push_sent',
        'in_app_sent',
        'avg_delivery_time_seconds',
        'delivery_rate_display',
        'read_rate_display',
        'click_rate_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'notification_type', 'channel')
        }),
        ('Counts', {
            'fields': (
                ('sent_count', 'delivered_count', 'read_count'),
                ('clicked_count', 'failed_count')
            )
        }),
        ('Delivery Methods', {
            'fields': (
                ('email_sent', 'sms_sent', 'push_sent', 'in_app_sent')
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'avg_delivery_time_seconds',
                ('delivery_rate_display', 'read_rate_display', 'click_rate_display')
            )
        }),
    )
    
    def notification_type_display(self, obj):
        return obj.get_notification_type_display()
    notification_type_display.short_description = 'Type'
    notification_type_display.admin_order_field = 'notification_type'
    
    def channel_display(self, obj):
        return obj.get_channel_display()
    channel_display.short_description = 'Channel'
    channel_display.admin_order_field = 'channel'
    
    def delivery_rate_display(self, obj):
        return f"{obj.delivery_rate:.1f}%"
    delivery_rate_display.short_description = 'Delivery Rate'
    
    def read_rate_display(self, obj):
        return f"{obj.read_rate:.1f}%"
    read_rate_display.short_description = 'Read Rate'
    
    def click_rate_display(self, obj):
        return f"{obj.click_rate:.1f}%" if obj.click_rate else "N/A"
    click_rate_display.short_description = 'Click Rate'
    
    # Disable add permission
    def has_add_permission(self, request):
        return False
    
    # Disable delete permission
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Disable change permission
    def has_change_permission(self, request, obj=None):
        return False


# ==================== ADMIN SITE CUSTOMIZATION ====================

# Optional: Custom admin dashboard view
class NotificationAdminSite(admin.AdminSite):
    site_header = "Delvok Academy - Notifications"
    site_title = "Notifications Admin"
    index_title = "Notification System Management"
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        
        # Sort the apps alphabetically
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort the models alphabetically within each app
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        
        return app_list

# Uncomment if you want a separate admin site for notifications
# notification_admin_site = NotificationAdminSite(name='notification_admin')
# notification_admin_site.register(Notification, NotificationAdmin)
# notification_admin_site.register(NotificationTemplate, NotificationTemplateAdmin)
# notification_admin_site.register(UserNotificationSettings, UserNotificationSettingsAdmin)
# notification_admin_site.register(NotificationStats, NotificationStatsAdmin)