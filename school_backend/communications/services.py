from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Announcement, Message, Notification, ParentTeacherMeeting

class NotificationService:
    """
    Service class for handling notification creation and delivery
    """
    
    @staticmethod
    def create_notification(recipient, notification_type, title, message, **kwargs):
        """
        Create a new notification
        """
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=kwargs.get('action_url', ''),
            action_text=kwargs.get('action_text', ''),
            related_object_type=kwargs.get('related_object_type', ''),
            related_object_id=kwargs.get('related_object_id'),
            scheduled_for=kwargs.get('scheduled_for'),
            expires_at=kwargs.get('expires_at'),
            channel=kwargs.get('channel', 'in_app')
        )
        
        # Send immediate notifications if scheduled for now or no schedule
        if not notification.scheduled_for or notification.scheduled_for <= timezone.now():
            NotificationService._deliver_notification(notification)
        
        return notification
    
    @staticmethod
    def _deliver_notification(notification):
        """
        Deliver notification through appropriate channels
        """
        try:
            # In-app notification (always delivered)
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
            # Email notification
            if notification.channel in ['email', 'all']:
                NotificationService._send_email_notification(notification)
            
            # SMS notification (would integrate with SMS service)
            if notification.channel in ['sms', 'all']:
                NotificationService._send_sms_notification(notification)
            
            # Push notification (would integrate with push service)
            if notification.channel in ['push', 'all']:
                NotificationService._send_push_notification(notification)
                
        except Exception as e:
            # Log the error but don't crash
            print(f"Error delivering notification: {e}")
    
    @staticmethod
    def _send_email_notification(notification):
        """
        Send email notification
        """
        subject = f"{settings.EMAIL_SUBJECT_PREFIX} {notification.title}"
        
        # Render email template
        context = {
            'notification': notification,
            'site_name': settings.SITE_NAME,
        }
        
        html_message = render_to_string('communications/email_notification.html', context)
        plain_message = render_to_string('communications/email_notification.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            html_message=html_message,
            fail_silently=True
        )
    
    @staticmethod
    def _send_sms_notification(notification):
        """
        Send SMS notification (placeholder for SMS integration)
        """
        # Integrate with your SMS service provider
        # Example: Twilio, AWS SNS, etc.
        pass
    
    @staticmethod
    def _send_push_notification(notification):
        """
        Send push notification (placeholder for push service integration)
        """
        # Integrate with your push notification service
        # Example: Firebase Cloud Messaging, Apple Push Notification Service, etc.
        pass

class AnnouncementService:
    """
    Service class for handling announcement-related operations
    """
    
    @staticmethod
    def publish_announcement(announcement):
        """
        Publish an announcement and notify targeted users
        """
        announcement.is_published = True
        announcement.published_at = timezone.now()
        announcement.save()
        
        # Notify targeted users
        AnnouncementService._notify_announcement_recipients(announcement)
    
    @staticmethod
    def _notify_announcement_recipients(announcement):
        """
        Create notifications for all users who should receive this announcement
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get targeted users based on announcement audience
        targeted_users = announcement.get_targeted_users()
        
        for user in targeted_users:
            # Check user's communication preferences
            preferences = getattr(user, 'communication_preferences', None)
            if preferences and not preferences.receive_announcements:
                continue
            
            # Create notification
            NotificationService.create_notification(
                recipient=user,
                notification_type='announcement',
                title=f"New Announcement: {announcement.title}",
                message=announcement.excerpt or announcement.content[:100] + "...",
                action_url=f"/announcements/{announcement.id}/",
                action_text="View Announcement",
                related_object_type='announcement',
                related_object_id=announcement.id
            )

class MessageService:
    """
    Service class for handling message-related operations
    """
    
    @staticmethod
    def send_message(sender, message_data):
        """
        Send a message and create notifications for recipients
        """
        from .serializers import MessageCreateSerializer
        
        serializer = MessageCreateSerializer(data=message_data)
        if serializer.is_valid():
            message = serializer.save(sender=sender)
            
            # Create notifications for recipients
            MessageService._notify_message_recipients(message)
            
            return message
        return None
    
    @staticmethod
    def _notify_message_recipients(message):
        """
        Create notifications for message recipients
        """
        for recipient in message.recipients.all():
            # Skip notification for sender
            if recipient == message.sender:
                continue
            
            # Check user's communication preferences
            preferences = getattr(recipient, 'communication_preferences', None)
            if preferences and not preferences.in_app_notifications:
                continue
            
            NotificationService.create_notification(
                recipient=recipient,
                notification_type='info',
                title=f"New Message from {message.sender.get_full_name()}",
                message=message.subject or message.content[:100] + "...",
                action_url=f"/messages/{message.id}/",
                action_text="View Message",
                related_object_type='message',
                related_object_id=message.id
            )

class MeetingService:
    """
    Service class for handling meeting-related operations
    """
    
    @staticmethod
    def schedule_meeting(creator, meeting_data):
        """
        Schedule a new parent-teacher meeting
        """
        from .serializers import ParentTeacherMeetingCreateSerializer
        
        serializer = ParentTeacherMeetingCreateSerializer(data=meeting_data)
        if serializer.is_valid():
            meeting = serializer.save(created_by=creator)
            
            # Create notifications for participants
            MeetingService._notify_meeting_participants(meeting)
            
            return meeting
        return None
    
    @staticmethod
    def _notify_meeting_participants(meeting):
        """
        Create notifications for meeting participants
        """
        # Notify parents
        for parent in meeting.parents.all():
            NotificationService.create_notification(
                recipient=parent,
                notification_type='event',
                title=f"New Meeting: {meeting.title}",
                message=f"Meeting scheduled with {meeting.teacher.user.get_full_name()} on {meeting.start_time.strftime('%B %d, %Y at %I:%M %p')}",
                action_url=f"/meetings/{meeting.id}/",
                action_text="View Meeting",
                related_object_type='meeting',
                related_object_id=meeting.id
            )
        
        # Notify teacher
        NotificationService.create_notification(
            recipient=meeting.teacher.user,
            notification_type='event',
            title=f"New Meeting: {meeting.title}",
            message=f"Meeting scheduled with parents on {meeting.start_time.strftime('%B %d, %Y at %I:%M %p')}",
            action_url=f"/meetings/{meeting.id}/",
            action_text="View Meeting",
            related_object_type='meeting',
            related_object_id=meeting.id
        )
    
    @staticmethod
    def send_meeting_reminder(meeting):
        """
        Send reminder for an upcoming meeting
        """
        if meeting.reminder_sent:
            return
        
        # Send reminders 24 hours before meeting
        reminder_time = meeting.start_time - timezone.timedelta(hours=24)
        if timezone.now() >= reminder_time:
            for parent in meeting.parents.all():
                NotificationService.create_notification(
                    recipient=parent,
                    notification_type='reminder',
                    title=f"Meeting Reminder: {meeting.title}",
                    message=f"Reminder: Your meeting is scheduled for {meeting.start_time.strftime('%B %d, %Y at %I:%M %p')}",
                    action_url=f"/meetings/{meeting.id}/",
                    action_text="View Meeting",
                    related_object_type='meeting',
                    related_object_id=meeting.id
                )
            
            meeting.reminder_sent = True
            meeting.save()