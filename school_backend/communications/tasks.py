from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ParentTeacherMeeting, Notification
from .services import MeetingService, NotificationService

@shared_task
def send_scheduled_notifications():
    """
    Send scheduled notifications that are due
    """
    now = timezone.now()
    due_notifications = Notification.objects.filter(
        scheduled_for__lte=now,
        is_sent=False
    )
    
    for notification in due_notifications:
        from .services import NotificationService
        NotificationService._deliver_notification(notification)

@shared_task
def send_meeting_reminders():
    """
    Send reminders for upcoming meetings
    """
    now = timezone.now()
    upcoming_meetings = ParentTeacherMeeting.objects.filter(
        start_time__gte=now,
        start_time__lte=now + timedelta(hours=24),
        status__in=['scheduled', 'confirmed'],
        reminder_sent=False
    )
    
    for meeting in upcoming_meetings:
        MeetingService.send_meeting_reminder(meeting)

@shared_task
def cleanup_old_notifications():
    """
    Clean up old notifications that have expired
    """
    expired_notifications = Notification.objects.filter(
        expires_at__lt=timezone.now()
    )
    
    count = expired_notifications.count()
    expired_notifications.delete()
    
    return f"Cleaned up {count} expired notifications"

@shared_task
def send_bulk_notifications(notification_data_list):
    """
    Send multiple notifications in bulk
    """
    for data in notification_data_list:
        NotificationService.create_notification(**data)

@shared_task
def process_announcement_publishing(announcement_id):
    """
    Process announcement publishing (for scheduled announcements)
    """
    from .models import Announcement
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        if not announcement.is_published:
            AnnouncementService.publish_announcement(announcement)
    except Announcement.DoesNotExist:
        pass