from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Announcement, Message, MessageRecipient, MessageGroup,
    GroupMembership, Notification, ParentTeacherMeeting,
    MeetingParticipant, CommunicationPreference, Feedback
)

# ---------------------------
# ANNOUNCEMENT ADMIN
# ---------------------------
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'audience', 'priority', 'is_published',
        'created_by', 'created_at', 'is_active_display'
    ]
    list_filter = ['audience', 'priority', 'is_published', 'created_at']
    search_fields = ['title', 'content', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    date_hierarchy = 'created_at'

    # ✅ keep only safe ManyToMany fields (no through)
    filter_horizontal = ['specific_classes', 'specific_users']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'excerpt')
        }),
        ('Audience & Targeting', {
            'fields': ('audience', 'specific_grades', 'specific_classes', 'specific_users')
        }),
        ('Scheduling & Priority', {
            'fields': ('priority', 'is_published', 'publish_at', 'expires_at')
        }),
        ('Media & Attachments', {
            'fields': ('image', 'attachments'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    def is_active_display(self, obj):
        color = "green" if obj.is_active else "red"
        text = "Active" if obj.is_active else "Inactive"
        return format_html(f'<span style="color:{color};">● {text}</span>')
    is_active_display.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ---------------------------
# MESSAGE ADMIN
# ---------------------------
class MessageRecipientInline(admin.TabularInline):
    model = MessageRecipient
    extra = 0
    readonly_fields = ['read_at', 'archived_at']
    can_delete = False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'subject', 'message_type', 'sender', 'get_recipient_count',
        'created_at', 'is_important'
    ]
    list_filter = ['message_type', 'is_important', 'created_at']
    search_fields = ['subject', 'content', 'sender__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [MessageRecipientInline]

    # ✅ Removed 'recipients' field (uses a through model)
    fieldsets = (
        ('Message Content', {
            'fields': ('message_type', 'subject', 'content')
        }),
        ('Recipients', {
            'fields': ('sender', 'group', 'class_recipient')
        }),
        ('Threading', {
            'fields': ('parent_message',),
            'classes': ('collapse',)
        }),
        ('Attachments & Importance', {
            'fields': ('attachments', 'is_important')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_recipient_count(self, obj):
        return obj.recipients.count()
    get_recipient_count.short_description = 'Recipients'


# ---------------------------
# MESSAGE GROUP ADMIN
# ---------------------------
class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1


@admin.register(MessageGroup)
class MessageGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'group_type', 'created_by', 'get_member_count',
        'is_active', 'created_at'
    ]
    list_filter = ['group_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [GroupMembershipInline]  # ✅ no filter_horizontal

    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'


# ---------------------------
# NOTIFICATION ADMIN
# ---------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'notification_type', 'channel', 'recipient',
        'is_read', 'is_sent', 'created_at'
    ]
    list_filter = ['notification_type', 'channel', 'is_read', 'is_sent', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['created_at', 'read_at', 'sent_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Notification Content', {
            'fields': ('notification_type', 'channel', 'title', 'message')
        }),
        ('Actions', {
            'fields': ('action_url', 'action_text')
        }),
        ('Recipient & Context', {
            'fields': ('recipient', 'related_object_type', 'related_object_id')
        }),
        ('Delivery Status', {
            'fields': ('is_read', 'read_at', 'is_sent', 'sent_at')
        }),
        ('Scheduling', {
            'fields': ('scheduled_for', 'expires_at'),
            'classes': ('collapse',)
        }),
    )


# ---------------------------
# PARENT-TEACHER MEETING ADMIN
# ---------------------------
class MeetingParticipantInline(admin.TabularInline):
    model = MeetingParticipant
    extra = 1


@admin.register(ParentTeacherMeeting)
class ParentTeacherMeetingAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'meeting_type', 'teacher', 'get_parent_count',
        'start_time', 'status', 'created_by'
    ]
    list_filter = ['meeting_type', 'status', 'is_online', 'start_time']
    search_fields = ['title', 'description', 'teacher__user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_time'
    inlines = [MeetingParticipantInline]

    # ✅ Removed 'parents' from fieldsets (through model)
    fieldsets = (
        ('Meeting Details', {
            'fields': ('meeting_type', 'title', 'description')
        }),
        ('Participants', {
            'fields': ('teacher', 'student')
        }),
        ('Scheduling', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('Location', {
            'fields': ('location', 'online_meeting_link', 'is_online')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'agenda', 'notes', 'outcome')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_parent_count(self, obj):
        return obj.parents.count()
    get_parent_count.short_description = 'Parents'


# ---------------------------
# COMMUNICATION PREFERENCES
# ---------------------------
@admin.register(CommunicationPreference)
class CommunicationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'preferred_channel', 'receive_announcements',
        'email_notifications', 'updated_at'
    ]
    list_filter = ['preferred_channel', 'receive_announcements', 'email_notifications']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Preferences', {
            'fields': (
                'receive_announcements', 'receive_grades_notifications',
                'receive_attendance_notifications', 'receive_event_reminders',
                'receive_assignment_notifications', 'receive_behavior_notifications'
            )
        }),
        ('Channel Preferences', {
            'fields': (
                'preferred_channel', 'email_notifications', 'sms_notifications',
                'push_notifications', 'in_app_notifications'
            )
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_start', 'quiet_hours_end'),
            'classes': ('collapse',)
        }),
    )


# ---------------------------
# FEEDBACK ADMIN
# ---------------------------
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'feedback_type', 'submitted_by', 'status',
        'priority', 'created_at', 'is_anonymous'
    ]
    list_filter = ['feedback_type', 'status', 'priority', 'is_anonymous', 'created_at']
    search_fields = ['title', 'description', 'submitted_by__username']
    readonly_fields = ['created_at', 'updated_at', 'responded_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Feedback Content', {
            'fields': ('feedback_type', 'title', 'description', 'is_anonymous')
        }),
        ('Submitter Information', {
            'fields': ('submitted_by', 'contact_email')
        }),
        ('Processing', {
            'fields': ('status', 'priority', 'assigned_to', 'admin_notes')
        }),
        ('Response', {
            'fields': ('response', 'responded_by', 'responded_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status in ['addressed', 'closed']:
            if not obj.responded_at:
                obj.responded_at = timezone.now()
            if not obj.responded_by:
                obj.responded_by = request.user
        super().save_model(request, obj, form, change)


# ---------------------------
# BASIC REGISTRATIONS
# ---------------------------
admin.site.register(MessageRecipient)
admin.site.register(GroupMembership)
admin.site.register(MeetingParticipant)
