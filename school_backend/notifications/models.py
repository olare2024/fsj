from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
import uuid
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class Notification(models.Model):
    """Notification model for storing user notifications"""
    
    # Notification Types
    NOTIFICATION_TYPES = (
        ('system', 'System'),
        ('academic', 'Academic'),
        ('financial', 'Financial'),
        ('security', 'Security'),
        ('event', 'Event'),
        ('announcement', 'Announcement'),
        ('message', 'Message'),
        ('assignment', 'Assignment'),
        ('grade', 'Grade'),
        ('attendance', 'Attendance'),
        ('reminder', 'Reminder'),
        ('approval', 'Approval'),
        ('alert', 'Alert'),
        ('welcome', 'Welcome'),
    )
    
    # Priority Levels
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    # Delivery Methods
    DELIVERY_METHODS = (
        ('in_app', 'In App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('all', 'All'),
    )
    
    # Status
    STATUS_CHOICES = (
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )
    
    # Channels
    CHANNELS = (
        ('all', 'All Users'),
        ('admin', 'Administrators'),
        ('teacher', 'Teachers'),
        ('student', 'Students'),
        ('parent', 'Parents'),
        ('staff', 'Staff'),
        ('accountant', 'Accountants'),
        ('it', 'IT Support'),
        ('custom', 'Custom'),
    )
    
    # Constants for easy reference
    TYPE_SYSTEM = 'system'
    TYPE_ACADEMIC = 'academic'
    TYPE_FINANCIAL = 'financial'
    TYPE_SECURITY = 'security'
    TYPE_EVENT = 'event'
    TYPE_ANNOUNCEMENT = 'announcement'
    TYPE_MESSAGE = 'message'
    TYPE_ASSIGNMENT = 'assignment'
    TYPE_GRADE = 'grade'
    TYPE_ATTENDANCE = 'attendance'
    TYPE_REMINDER = 'reminder'
    TYPE_APPROVAL = 'approval'
    TYPE_ALERT = 'alert'
    TYPE_WELCOME = 'welcome'
    
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    
    DELIVERY_IN_APP = 'in_app'
    DELIVERY_EMAIL = 'email'
    DELIVERY_SMS = 'sms'
    DELIVERY_PUSH = 'push'
    DELIVERY_ALL = 'all'
    
    STATUS_UNREAD = 'unread'
    STATUS_READ = 'read'
    STATUS_ARCHIVED = 'archived'
    STATUS_DELETED = 'deleted'
    
    CHANNEL_ALL = 'all'
    CHANNEL_ADMIN = 'admin'
    CHANNEL_TEACHER = 'teacher'
    CHANNEL_STUDENT = 'student'
    CHANNEL_PARENT = 'parent'
    CHANNEL_STAFF = 'staff'
    CHANNEL_ACCOUNTANT = 'accountant'
    CHANNEL_IT = 'it'
    CHANNEL_CUSTOM = 'custom'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_new')
    
    # Core fields
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    channel = models.CharField(max_length=20, choices=CHANNELS, default='all')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHODS, default='in_app')
    
    # Metadata
    data = models.JSONField(default=dict, blank=True)  # Additional data for the notification
    actions = models.JSONField(default=list, blank=True)  # Available actions for the notification
    metadata = models.JSONField(default=dict, blank=True)  # Additional metadata
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Foreign keys (optional)
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sent_notifications'
    )
    related_object_type = models.CharField(max_length=50, blank=True)  # e.g., 'assignment', 'payment'
    related_object_id = models.UUIDField(null=True, blank=True)
    
    # Delivery tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    in_app_sent = models.BooleanField(default=True)  # Default True since it's created in-app
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['channel', 'created_at']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    @property
    def is_expired(self):
        """Check if notification is expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def can_be_deleted(self):
        """Check if notification can be deleted"""
        return self.status != self.STATUS_DELETED

    def get_absolute_url(self):
        """Get absolute URL for notification"""
        return reverse('notification_detail', kwargs={'pk': str(self.id)})

    def __str__(self):
        return f"{self.title} - {self.user.email} ({self.get_status_display()})"

    def clean(self):
        """Validate the notification"""
        if self.expires_at and self.expires_at < timezone.now():
            raise ValidationError("Expiry date cannot be in the past")
        
        # Validate actions JSON structure
        if self.actions:
            for action in self.actions:
                if not isinstance(action, dict):
                    raise ValidationError("Actions must be a list of dictionaries")
                if 'label' not in action or 'url' not in action:
                    raise ValidationError("Each action must have 'label' and 'url' keys")

    def save(self, *args, **kwargs):
        """Override save to handle timestamps and validation"""
        self.full_clean()
        
        if self.status == self.STATUS_READ and not self.read_at:
            self.read_at = timezone.now()
        
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = self.STATUS_ARCHIVED
        
        super().save(*args, **kwargs)

    def mark_as_read(self, commit=True):
        """Mark notification as read"""
        self.status = self.STATUS_READ
        self.read_at = timezone.now()
        
        if commit:
            self.save(update_fields=['status', 'read_at'])

    def mark_as_unread(self, commit=True):
        """Mark notification as unread"""
        self.status = self.STATUS_UNREAD
        self.read_at = None
        
        if commit:
            self.save(update_fields=['status', 'read_at'])

    def archive(self, commit=True):
        """Archive notification"""
        self.status = self.STATUS_ARCHIVED
        
        if commit:
            self.save(update_fields=['status'])

    def delete(self, soft_delete=True, *args, **kwargs):
        """Override delete to support soft delete"""
        if soft_delete:
            self.status = self.STATUS_DELETED
            self.save()
        else:
            super().delete(*args, **kwargs)

    def send(self):
        """Send notification through configured delivery methods"""
        if self.sent_at:
            return False  # Already sent
        
        self.sent_at = timezone.now()
        
        # Send through configured delivery methods
        if self.delivery_method in [self.DELIVERY_IN_APP, self.DELIVERY_ALL]:
            self.send_in_app()
        
        if self.delivery_method in [self.DELIVERY_EMAIL, self.DELIVERY_ALL]:
            self.send_email()
        
        if self.delivery_method in [self.DELIVERY_SMS, self.DELIVERY_ALL]:
            self.send_sms()
        
        if self.delivery_method in [self.DELIVERY_PUSH, self.DELIVERY_ALL]:
            self.send_push()
        
        self.save(update_fields=['sent_at'])
        return True

    def send_in_app(self):
        """Send in-app notification (WebSocket)"""
        # Note: This is a placeholder. Implement WebSocket logic in consumers.py
        # WebSocket implementation will be in consumers.py
        try:
            # This should be called from a WebSocket consumer
            # from .consumers import NotificationConsumer
            # NotificationConsumer.send_notification(self.user.id, {
            #     'type': 'notification',
            #     'notification': self.to_dict()
            # })
            
            # Mark as sent in-app
            self.in_app_sent = True
            self.save(update_fields=['in_app_sent'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to send in-app notification: {e}")
            return False

    def send_email(self):
        """Send email notification"""
        try:
            # Check if user has email notifications enabled
            from .models import UserNotificationSettings
            try:
                settings_obj = UserNotificationSettings.objects.get(user=self.user)
                if not settings_obj.email_notifications:
                    return False
            except UserNotificationSettings.DoesNotExist:
                pass
            
            subject = f"[Delvok Academy] {self.title}"
            
            # Try to render email template, fallback to simple message
            try:
                html_message = render_to_string('notifications/email_notification.html', {
                    'notification': self,
                    'user': self.user
                })
            except:
                html_message = f"""
                <html>
                <body>
                    <h2>{self.title}</h2>
                    <p>{self.message}</p>
                    <p><small>Sent from Delvok Academy</small></p>
                </body>
                </html>
                """
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                fail_silently=False
            )
            
            self.email_sent = True
            self.save(update_fields=['email_sent'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    def send_sms(self):
        """Send SMS notification"""
        try:
            # Check if user has SMS notifications enabled
            from .models import UserNotificationSettings
            try:
                settings_obj = UserNotificationSettings.objects.get(user=self.user)
                if not settings_obj.sms_notifications:
                    return False
            except UserNotificationSettings.DoesNotExist:
                pass
            
            if not settings.TWILIO_ENABLED or not self.user.phone_number:
                return False
            
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # Truncate message if too long for SMS
            sms_message = self.message
            if len(sms_message) > 150:
                sms_message = sms_message[:147] + "..."
            
            message = client.messages.create(
                body=f"Delvok Academy: {sms_message}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=str(self.user.phone_number)
            )
            
            self.sms_sent = True
            self.save(update_fields=['sms_sent'])
            return True
            
        except ImportError:
            logger.warning("Twilio not installed or configured")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return False

    def send_push(self):
        """Send push notification"""
        try:
            # Check if user has push notifications enabled
            from .models import UserNotificationSettings
            try:
                settings_obj = UserNotificationSettings.objects.get(user=self.user)
                if not settings_obj.push_notifications:
                    return False
            except UserNotificationSettings.DoesNotExist:
                pass
            
            # Implement push notification service (e.g., Firebase, OneSignal)
            # This is a placeholder implementation
            
            # Example with Firebase Cloud Messaging
            # if hasattr(self.user, 'fcm_token') and self.user.fcm_token:
            #     # Send push notification
            #     from firebase_admin import messaging
            #     
            #     message = messaging.Message(
            #         notification=messaging.Notification(
            #             title=self.title,
            #             body=self.message,
            #         ),
            #         token=self.user.fcm_token,
            #     )
            #     response = messaging.send(message)
            
            self.push_sent = True
            self.save(update_fields=['push_sent'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False

    def to_dict(self):
        """Convert notification to dictionary for API response"""
        return {
            'id': str(self.id),
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'priority': self.priority,
            'channel': self.channel,
            'status': self.status,
            'data': self.data,
            'actions': self.actions,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'sender': self.sender.email if self.sender else None,
            'sender_id': str(self.sender.id) if self.sender else None,
            'is_expired': self.is_expired,
            'can_be_deleted': self.can_be_deleted,
            'absolute_url': self.get_absolute_url(),
            'delivery_status': {
                'email': self.email_sent,
                'sms': self.sms_sent,
                'push': self.push_sent,
                'in_app': self.in_app_sent,
            }
        }

    @classmethod
    def create_notification(cls, user, title, message, **kwargs):
        """Create a new notification"""
        notification = cls(
            user=user,
            title=title,
            message=message,
            **kwargs
        )
        notification.full_clean()
        notification.save()
        
        # Auto-send if configured
        if kwargs.get('auto_send', True):
            notification.send()
        
        return notification

    @classmethod
    def create_bulk_notifications(cls, users, title, message, **kwargs):
        """Create bulk notifications for multiple users"""
        notifications = []
        for user in users:
            notification = cls(
                user=user,
                title=title,
                message=message,
                **{k: v for k, v in kwargs.items() if k != 'auto_send'}
            )
            notification.full_clean()
            notifications.append(notification)
        
        cls.objects.bulk_create(notifications)
        
        # Auto-send if configured
        if kwargs.get('auto_send', True):
            for notification in notifications:
                notification.send()
        
        return notifications

    @classmethod
    def send_system_notification(cls, title, message, channel='all', priority='medium', **kwargs):
        """Send system notification to all users in a channel"""
        users = User.objects.filter(is_active=True)
        
        if channel != 'all':
            # Filter users by channel/role
            # Assuming User model has a 'role' field
            role_mapping = {
                'admin': 'admin',
                'teacher': 'teacher',
                'student': 'student',
                'parent': 'parent',
                'staff': 'staff',
                'accountant': 'accountant',
                'it': 'it_support',
            }
            
            if channel in role_mapping:
                users = users.filter(role=role_mapping[channel])
            elif channel == 'custom':
                # Custom channel - would need additional logic
                users = users.none()
        
        notifications = cls.create_bulk_notifications(
            users=users,
            title=title,
            message=message,
            type='system',
            channel=channel,
            priority=priority,
            delivery_method='in_app',
            **kwargs
        )
        
        return notifications


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class NotificationTemplate(BaseModel):
    """Template for notification messages"""
    
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    title_template = models.CharField(max_length=255)
    message_template = models.TextField()
    default_priority = models.CharField(max_length=10, choices=Notification.PRIORITY_LEVELS, default='medium')
    default_channel = models.CharField(max_length=20, choices=Notification.CHANNELS, default='all')
    default_delivery = models.CharField(max_length=10, choices=Notification.DELIVERY_METHODS, default='in_app')
    variables = models.JSONField(default=dict, help_text="Available template variables")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, help_text="Template description and usage")

    class Meta:
        ordering = ['name']
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    def render(self, context):
        """Render template with context"""
        from django.template import Template, Context
        
        try:
            title = Template(self.title_template).render(Context(context))
            message = Template(self.message_template).render(Context(context))
            return title, message
        except Exception as e:
            logger.error(f"Error rendering template {self.name}: {e}")
            return self.title_template, self.message_template
    
    @classmethod
    def create_from_template(cls, template_name, user, context_data, **kwargs):
        """Create notification from template"""
        try:
            template = cls.objects.get(name=template_name, is_active=True)
            title, message = template.render(context_data)
            
            notification_data = {
                'type': template.template_type,
                'priority': template.default_priority,
                'channel': template.default_channel,
                'delivery_method': template.default_delivery,
                **kwargs
            }
            
            return Notification.create_notification(
                user=user,
                title=title,
                message=message,
                **notification_data
            )
        except cls.DoesNotExist:
            logger.error(f"Template '{template_name}' not found or inactive")
            return None


class UserNotificationSettings(BaseModel):
    """User-specific notification settings and preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Global settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    sound_enabled = models.BooleanField(default=True)
    desktop_notifications = models.BooleanField(default=True)
    
    # Type-specific settings
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='07:00')
    
    # Frequency
    digest_frequency = models.CharField(
        max_length=10,
        choices=(
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ),
        default='immediate'
    )
    last_digest_sent = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Notification Settings'
        verbose_name_plural = 'User Notification Settings'

    def __str__(self):
        return f"Notification settings for {self.user.email}"

    def save(self, *args, **kwargs):
        """Ensure default preferences are set"""
        if not self.notification_preferences:
            self.set_default_preferences()
        super().save(*args, **kwargs)

    def set_default_preferences(self):
        """Set default notification preferences"""
        self.notification_preferences = {
            'system': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'academic': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'financial': {'email': True, 'sms': True, 'push': True, 'in_app': True},
            'security': {'email': True, 'sms': True, 'push': True, 'in_app': True},
            'event': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'announcement': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'message': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'assignment': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'grade': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'attendance': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'reminder': {'email': True, 'sms': True, 'push': True, 'in_app': True},
            'approval': {'email': True, 'sms': False, 'push': True, 'in_app': True},
            'alert': {'email': True, 'sms': True, 'push': True, 'in_app': True},
            'welcome': {'email': True, 'sms': False, 'push': True, 'in_app': True},
        }

    def can_receive_notification(self, notification_type, delivery_method):
        """Check if user can receive notification of given type via given method"""
        # Check quiet hours first
        if self.is_quiet_hours() and delivery_method in ['sms', 'push']:
            return False
        
        # Check global settings
        if delivery_method == 'email' and not self.email_notifications:
            return False
        if delivery_method == 'sms' and not self.sms_notifications:
            return False
        if delivery_method == 'push' and not self.push_notifications:
            return False
        if delivery_method == 'in_app' and not self.in_app_notifications:
            return False
        
        # Check type-specific preferences
        type_prefs = self.notification_preferences.get(notification_type, {})
        return type_prefs.get(delivery_method, True)

    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_enabled:
            return False
        
        now = timezone.now().time()
        if self.quiet_hours_start <= self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end


class NotificationStats(BaseModel):
    """Statistics for notification tracking and analytics"""
    
    date = models.DateField()
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=Notification.CHANNELS)
    
    # Counts
    sent_count = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    read_count = models.PositiveIntegerField(default=0)
    clicked_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    
    # Delivery methods
    email_sent = models.PositiveIntegerField(default=0)
    sms_sent = models.PositiveIntegerField(default=0)
    push_sent = models.PositiveIntegerField(default=0)
    in_app_sent = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_delivery_time_seconds = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        unique_together = ['date', 'notification_type', 'channel']
        verbose_name = 'Notification Statistics'
        verbose_name_plural = 'Notification Statistics'
        ordering = ['-date']

    def __str__(self):
        return f"Stats for {self.date} - {self.get_notification_type_display()} ({self.channel})"

    @classmethod
    def update_stats(cls, notification):
        """Update statistics for a notification"""
        date = notification.created_at.date()
        
        # Calculate delivery time if sent
        delivery_time = None
        if notification.sent_at and notification.created_at:
            delivery_time = (notification.sent_at - notification.created_at).total_seconds()
        
        stats, created = cls.objects.get_or_create(
            date=date,
            notification_type=notification.type,
            channel=notification.channel,
            defaults={
                'sent_count': 1,
                'delivered_count': 1 if notification.sent_at else 0,
                'read_count': 1 if notification.status == Notification.STATUS_READ else 0,
                'email_sent': 1 if notification.email_sent else 0,
                'sms_sent': 1 if notification.sms_sent else 0,
                'push_sent': 1 if notification.push_sent else 0,
                'in_app_sent': 1 if notification.delivery_method in ['in_app', 'all'] else 0,
                'avg_delivery_time_seconds': delivery_time if delivery_time else 0,
            }
        )
        
        if not created:
            stats.sent_count += 1
            if notification.sent_at:
                stats.delivered_count += 1
            if notification.status == Notification.STATUS_READ:
                stats.read_count += 1
            if notification.email_sent:
                stats.email_sent += 1
            if notification.sms_sent:
                stats.sms_sent += 1
            if notification.push_sent:
                stats.push_sent += 1
            if notification.delivery_method in ['in_app', 'all']:
                stats.in_app_sent += 1
            
            # Update average delivery time
            if delivery_time:
                total_delivered = stats.delivered_count
                current_total_time = stats.avg_delivery_time_seconds * (total_delivered - 1)
                stats.avg_delivery_time_seconds = (current_total_time + delivery_time) / total_delivered
            
            stats.save()
        
        return stats

    @property
    def delivery_rate(self):
        """Calculate delivery success rate"""
        if self.sent_count == 0:
            return 0
        return (self.delivered_count / self.sent_count) * 100

    @property
    def read_rate(self):
        """Calculate read rate"""
        if self.delivered_count == 0:
            return 0
        return (self.read_count / self.delivered_count) * 100

    @property
    def click_rate(self):
        """Calculate click-through rate"""
        if self.delivered_count == 0:
            return 0
        return (self.clicked_count / self.delivered_count) * 100

    @classmethod
    def get_daily_summary(cls, date):
        """Get daily summary for a specific date"""
        stats = cls.objects.filter(date=date)
        
        summary = {
            'date': date,
            'total_sent': sum(s.sent_count for s in stats),
            'total_delivered': sum(s.delivered_count for s in stats),
            'total_read': sum(s.read_count for s in stats),
            'delivery_rate': 0,
            'read_rate': 0,
            'by_type': {},
            'by_channel': {},
        }
        
        if summary['total_sent'] > 0:
            summary['delivery_rate'] = (summary['total_delivered'] / summary['total_sent']) * 100
        
        if summary['total_delivered'] > 0:
            summary['read_rate'] = (summary['total_read'] / summary['total_delivered']) * 100
        
        # Group by type
        for stat in stats:
            if stat.notification_type not in summary['by_type']:
                summary['by_type'][stat.notification_type] = {
                    'sent': 0,
                    'delivered': 0,
                    'read': 0,
                }
            summary['by_type'][stat.notification_type]['sent'] += stat.sent_count
            summary['by_type'][stat.notification_type]['delivered'] += stat.delivered_count
            summary['by_type'][stat.notification_type]['read'] += stat.read_count
        
        # Group by channel
        for stat in stats:
            if stat.channel not in summary['by_channel']:
                summary['by_channel'][stat.channel] = {
                    'sent': 0,
                    'delivered': 0,
                    'read': 0,
                }
            summary['by_channel'][stat.channel]['sent'] += stat.sent_count
            summary['by_channel'][stat.channel]['delivered'] += stat.delivered_count
            summary['by_channel'][stat.channel]['read'] += stat.read_count
        
        return summary