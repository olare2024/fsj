# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active', 'event_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {};">⬤</span> {}',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def event_count(self, obj):
        return obj.events.count()
    event_count.short_description = 'Events'


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ['registration_date', 'payment_status']
    fields = ['user', 'student', 'status', 'payment_status', 'checked_in']
    can_delete = True


class EventFeedbackInline(admin.TabularInline):
    model = EventFeedback
    extra = 0
    readonly_fields = ['submitted_at']
    fields = ['user', 'rating', 'comment', 'approved']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'event_type', 'start_date', 'end_date', 'location',
        'is_published', 'is_cancelled', 'status', 'registered_count',
        'available_slots_display', 'created_by'
    ]
    list_filter = [
        'event_type', 'target_audience', 'is_published', 'is_cancelled',
        'status', 'priority', 'requires_registration', 'has_fee',
        'start_date', 'created_at'
    ]
    search_fields = ['title', 'description', 'location', 'event_code']
    readonly_fields = [
        'event_code', 'created_at', 'updated_at', 'published_at',
        'approved_at', 'views_count', 'registered_count', 'waitlist_count'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'slug', 'event_code', 'description', 'event_type',
                'categories', 'status', 'priority'
            )
        }),
        ('Timing', {
            'fields': (
                'start_date', 'end_date', 'all_day',
                'is_recurring', 'recurrence_rule', 'recurrence_end_date'
            )
        }),
        ('Location', {
            'fields': (
                'location', 'room_number', 'is_online', 'is_hybrid',
                'online_link', 'venue_capacity'
            )
        }),
        ('Organization', {
            'fields': (
                'organizer', 'organizer_contact', 'coordinator', 'co_organizers'
            )
        }),
        ('Audience & Registration', {
            'fields': (
                'target_audience', 'specific_grades', 'specific_classes',
                'requires_registration', 'registration_start_date', 'registration_deadline',
                'max_participants', 'min_participants', 'waitlist_enabled', 'waitlist_capacity',
                'allow_guest_registrations', 'max_guests_per_registration'
            )
        }),
        ('Media', {
            'fields': (
                'image', 'banner_image', 'gallery', 'video_url', 'documents'
            )
        }),
        ('Financial', {
            'fields': (
                'has_fee', 'fee_amount', 'fee_currency',
                'early_bird_discount', 'early_bird_deadline'
            )
        }),
        ('Publication', {
            'fields': (
                'is_published', 'is_featured', 'is_cancelled', 'cancellation_reason',
                'requires_approval', 'approved_by', 'approved_at', 'published_at'
            )
        }),
        ('SEO & Analytics', {
            'fields': (
                'meta_title', 'meta_description', 'views_count'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by', 'created_at', 'updated_at'
            )
        }),
    )
    filter_horizontal = ['categories', 'co_organizers']
    inlines = [EventRegistrationInline, EventFeedbackInline]
    actions = ['publish_events', 'cancel_events', 'approve_events']
    
    def available_slots_display(self, obj):
        if obj.max_participants:
            return f"{obj.available_slots or 0}/{obj.max_participants}"
        return "Unlimited"
    available_slots_display.short_description = 'Available Slots'
    
    def publish_events(self, request, queryset):
        updated = queryset.update(is_published=True, status='published')
        self.message_user(request, f'{updated} events published successfully.')
    publish_events.short_description = "Publish selected events"
    
    def cancel_events(self, request, queryset):
        updated = queryset.update(is_cancelled=True, status='cancelled')
        self.message_user(request, f'{updated} events cancelled successfully.')
    cancel_events.short_description = "Cancel selected events"
    
    def approve_events(self, request, queryset):
        updated = queryset.update(
            requires_approval=False,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} events approved successfully.')
    approve_events.short_description = "Approve selected events"
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories', 'registrations')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'event', 'status', 'payment_status',
        'amount_paid', 'balance_due', 'checked_in', 'registration_date'
    ]
    list_filter = [
        'status', 'payment_status', 'checked_in', 'is_guest_registration',
        'event', 'registration_date'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 'user__email',
        'student__user__first_name', 'student__user__last_name',
        'event__title', 'guest_name', 'guest_email'
    ]
    readonly_fields = ['registration_date', 'payment_amount', 'balance_due']
    fieldsets = (
        ('Registration Details', {
            'fields': (
                'event', 'user', 'student', 'is_guest_registration',
                'guest_name', 'guest_email', 'guest_count'
            )
        }),
        ('Status', {
            'fields': (
                'status', 'registration_date'
            )
        }),
        ('Additional Information', {
            'fields': (
                'dietary_restrictions', 'special_requirements',
                'emergency_contact', 'emergency_phone',
                'medical_conditions', 'allergies'
            )
        }),
        ('Payment', {
            'fields': (
                'payment_status', 'payment_amount', 'amount_paid',
                'payment_date', 'payment_reference', 'payment_method'
            )
        }),
        ('Check-in', {
            'fields': (
                'checked_in', 'check_in_time', 'checked_in_by'
            )
        }),
        ('Communication', {
            'fields': (
                'confirmation_sent', 'reminder_sent'
            )
        }),
        ('Notes', {
            'fields': (
                'notes', 'internal_notes'
            )
        }),
    )
    actions = ['mark_as_attended', 'mark_as_paid', 'send_confirmation']

    def mark_as_attended(self, request, queryset):
        updated = queryset.update(status='attended', checked_in=True, check_in_time=timezone.now())
        self.message_user(request, f'{updated} registrations marked as attended.')
    mark_as_attended.short_description = "Mark selected as attended"

    def mark_as_paid(self, request, queryset):
        for registration in queryset:
            registration.amount_paid = registration.payment_amount
            registration.payment_status = 'paid'
            registration.payment_date = timezone.now()
            registration.save()
        self.message_user(request, f'{queryset.count()} registrations marked as paid.')
    mark_as_paid.short_description = "Mark selected as fully paid"


@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'event', 'user', 'rating', 'would_recommend',
        'approved', 'submitted_at'
    ]
    list_filter = ['rating', 'approved', 'would_recommend', 'is_anonymous', 'submitted_at']
    search_fields = [
        'event__title', 'user__first_name', 'user__last_name',
        'comment', 'suggestions'
    ]
    readonly_fields = ['submitted_at']
    actions = ['approve_feedback', 'disapprove_feedback']

    def approve_feedback(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f'{updated} feedback entries approved.')
    approve_feedback.short_description = "Approve selected feedback"

    def disapprove_feedback(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, f'{updated} feedback entries disapproved.')
    disapprove_feedback.short_description = "Disapprove selected feedback"


@admin.register(EventReminder)
class EventReminderAdmin(admin.ModelAdmin):
    list_display = ['event', 'reminder_type', 'trigger_type', 'reminder_time', 'sent', 'send_attempts']
    list_filter = ['reminder_type', 'trigger_type', 'sent', 'reminder_time']
    search_fields = ['event__title', 'message', 'subject']
    readonly_fields = ['sent', 'sent_at', 'send_attempts']
    actions = ['send_reminders']

    def send_reminders(self, request, queryset):
        # This would typically call your reminder sending logic
        sent_count = 0
        for reminder in queryset.filter(sent=False):
            # Implement your sending logic here
            reminder.sent = True
            reminder.sent_at = timezone.now()
            reminder.save()
            sent_count += 1
        self.message_user(request, f'{sent_count} reminders sent.')
    send_reminders.short_description = "Send selected reminders"


@admin.register(EventAttachment)
class EventAttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'file_type', 'is_public', 'download_count', 'uploaded_at']
    list_filter = ['file_type', 'is_public', 'uploaded_at']
    search_fields = ['name', 'event__title', 'description']
    readonly_fields = ['download_count', 'uploaded_by', 'uploaded_at']