from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import (
    Announcement, Message, Notification, ParentTeacherMeeting,
    CommunicationPreference, Feedback
)
from .services import NotificationService, AnnouncementService, MeetingService

User = get_user_model()

@receiver(post_save, sender=Announcement)
def handle_announcement_publishing(sender, instance, created, **kwargs):
    """
    Handle announcement publishing and notifications
    """
    if instance.is_published and not created:
        # Announcement was just published
        AnnouncementService._notify_announcement_recipients(instance)
    
    elif not instance.is_published and created:
        # New draft announcement - no notifications
        pass

@receiver(post_save, sender=Message)
def handle_message_creation(sender, instance, created, **kwargs):
    """
    Handle message creation and recipient notifications
    """
    if created:
        # Notify recipients about new message
        from .services import MessageService
        MessageService._notify_message_recipients(instance)

@receiver(post_save, sender=ParentTeacherMeeting)
def handle_meeting_creation(sender, instance, created, **kwargs):
    """
    Handle meeting creation and participant notifications
    """
    if created:
        # Notify participants about new meeting
        MeetingService._notify_meeting_participants(instance)

@receiver(pre_save, sender=ParentTeacherMeeting)
def handle_meeting_status_change(sender, instance, **kwargs):
    """
    Handle meeting status changes and notifications
    """
    if instance.pk:
        try:
            old_instance = ParentTeacherMeeting.objects.get(pk=instance.pk)
            
            # Check if status changed
            if old_instance.status != instance.status:
                # Notify participants about status change
                MeetingService._notify_meeting_status_change(instance, old_instance.status)
            
            # Check if meeting time changed
            if (old_instance.start_time != instance.start_time or 
                old_instance.end_time != instance.end_time):
                # Notify participants about schedule change
                MeetingService._notify_meeting_schedule_change(instance)
                
        except ParentTeacherMeeting.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def create_communication_preferences(sender, instance, created, **kwargs):
    """
    Create default communication preferences for new users
    """
    if created:
        CommunicationPreference.objects.get_or_create(user=instance)

@receiver(post_save, sender=Feedback)
def handle_feedback_assignment(sender, instance, created, **kwargs):
    """
    Handle feedback assignment and notifications
    """
    if not created and instance.assigned_to:
        # Notify assigned staff member
        NotificationService.create_notification(
            recipient=instance.assigned_to,
            notification_type='info',
            title=f"Feedback Assigned: {instance.title}",
            message=f"You have been assigned to handle feedback: {instance.description[:100]}...",
            action_url=f"/feedback/{instance.id}/",
            action_text="View Feedback",
            related_object_type='feedback',
            related_object_id=instance.id
        )

@receiver(pre_save, sender=Notification)
def handle_notification_delivery(sender, instance, **kwargs):
    """
    Handle notification delivery based on schedule
    """
    from .services import NotificationService
    
    if not instance.is_sent and (not instance.scheduled_for or instance.scheduled_for <= timezone.now()):
        NotificationService._deliver_notification(instance)

# Meeting reminder signal (would typically be called by a scheduled task)
@receiver(post_save, sender=ParentTeacherMeeting)
def schedule_meeting_reminders(sender, instance, created, **kwargs):
    """
    Schedule meeting reminders (this would integrate with a task queue like Celery)
    """
    if created and instance.status in ['scheduled', 'confirmed']:
        # In a real implementation, this would schedule a Celery task
        # For now, we'll handle reminders in the service layer
        pass