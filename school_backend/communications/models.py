from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import json

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Announcement(BaseModel):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    AUDIENCE_CHOICES = (
        ('all', 'All'),
        ('students', 'Students'),
        ('teachers', 'Teachers'),
        ('parents', 'Parents'),
        ('staff', 'Staff'),
        ('specific_grades', 'Specific Grades'),
        ('specific_classes', 'Specific Classes'),
        ('specific_users', 'Specific Users'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(blank=True, max_length=500)
    
    # Audience and targeting
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    specific_grades = models.JSONField(blank=True, null=True, help_text="List of grade levels")
    specific_classes = models.ManyToManyField('academics.Class', blank=True)
    specific_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    
    # Priority and scheduling
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_published = models.BooleanField(default=False)
    publish_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Media and attachments
    image = models.ImageField(upload_to='announcements/images/', blank=True, null=True)
    attachments = models.JSONField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_announcements'
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', 'publish_at']),
            models.Index(fields=['audience']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Validate model data"""
        if self.publish_at and self.expires_at and self.publish_at >= self.expires_at:
            raise ValidationError("Expiry date must be after publish date")
        
        if self.specific_grades:
            try:
                grades = json.loads(self.specific_grades) if isinstance(self.specific_grades, str) else self.specific_grades
                if not isinstance(grades, list):
                    raise ValidationError("Specific grades must be a list")
            except (json.JSONDecodeError, TypeError):
                raise ValidationError("Invalid format for specific grades")

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if announcement is currently active"""
        now = timezone.now()
        if not self.is_published:
            return False
        if self.publish_at and self.publish_at > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        return True

class MessageGroup(BaseModel):
    GROUP_TYPES = (
        ('class', 'Class Group'),
        ('subject', 'Subject Group'),
        ('committee', 'Committee'),
        ('custom', 'Custom Group'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=10, choices=GROUP_TYPES, default='custom')
    
    # Group members
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='GroupMembership',
        related_name='message_groups'
    )
    
    # For class/subject groups
    related_class = models.ForeignKey(
        'academics.Class', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    related_subject = models.ForeignKey(
        'academics.Subject', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    
    
    # Settings
    is_active = models.BooleanField(default=True)
    allow_member_messages = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_groups_new'
    )

    class Meta:
        db_table = 'message_groups'
        ordering = ['name']

    def __str__(self):
        return self.name

class GroupMembership(BaseModel):
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    )

    group = models.ForeignKey(MessageGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    class Meta:
        db_table = 'group_memberships'
        unique_together = ['group', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group.name} ({self.role})"

class Message(BaseModel):
    MESSAGE_TYPES = (
        ('direct', 'Direct Message'),
        ('group', 'Group Message'),
        ('class', 'Class Message'),
        ('broadcast', 'Broadcast'),
    )

    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='direct')
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # Sender and recipients
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='MessageRecipient',
        related_name='received_messages',
        blank=True
    )
    
    # For group/class messages
    group = models.ForeignKey(
        MessageGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    class_recipient = models.ForeignKey(
        'academics.Class', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Parent message for threading
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    
    # Attachments
    attachments = models.JSONField(blank=True, null=True)
    
    # Status
    is_important = models.BooleanField(default=False)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['message_type']),
        ]

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} - {self.subject}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create message recipients for new messages
        if is_new:
            self._create_recipients()

    def _create_recipients(self):
        """Create MessageRecipient records based on message type"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        recipients = []
        
        if self.message_type == 'direct' and self.recipients.exists():
            recipients = self.recipients.all()
        elif self.message_type == 'group' and self.group:
            recipients = self.group.members.all()
        elif self.message_type == 'class' and self.class_recipient:
            # Get all students in the class
            recipients = User.objects.filter(
                student_profile__enrollments__class_obj=self.class_recipient,
                student_profile__enrollments__status='active'
            ).distinct()
        elif self.message_type == 'broadcast':
            # Send to all users (be careful with this!)
            recipients = User.objects.all()
        
        # Create recipient records
        for recipient in recipients:
            MessageRecipient.objects.get_or_create(
                message=self,
                recipient=recipient
            )

class MessageRecipient(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Read status for each recipient
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Archive status
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'message_recipients'
        unique_together = ['message', 'recipient']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.message.subject}"

    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class Notification(BaseModel):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('reminder', 'Reminder'),
        ('assignment', 'Assignment'),
        ('grade', 'Grade'),
        ('attendance', 'Attendance'),
        ('event', 'Event'),
        ('announcement', 'Announcement'),
    )

    CHANNEL_CHOICES = (
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('all', 'All Channels'),
    )

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='in_app')
    
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=50, blank=True)
    
    # Recipient
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    
    # Related object (for contextual notifications)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)
    
    # Status and delivery
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class ParentTeacherMeeting(BaseModel):
    MEETING_TYPES = (
        ('individual', 'Individual Meeting'),
        ('group', 'Group Meeting'),
        ('parent_teacher', 'Parent-Teacher Conference'),
        ('open_house', 'Open House'),
    )

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    )

    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES, default='individual')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Participants
    teacher = models.ForeignKey(
        'teachers.TeacherProfile', 
        on_delete=models.CASCADE, 
        related_name='scheduled_meetings'
    )
    parents = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='MeetingParticipant',
        related_name='scheduled_meetings',
        limit_choices_to={'role': 'parent'}
    )
    student = models.ForeignKey(
        'students.StudentProfile', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='parent_teacher_meetings'
    )
    
    # Scheduling
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    online_meeting_link = models.URLField(blank=True)
    is_online = models.BooleanField(default=False)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    agenda = models.JSONField(blank=True, null=True)
    notes = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_meetings'
    )

    class Meta:
        db_table = 'parent_teacher_meetings'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['teacher', 'start_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} with {self.teacher.user.get_full_name()}"

    def clean(self):
        """Validate meeting data"""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        
        if self.start_time and self.start_time < timezone.now():
            raise ValidationError("Meeting cannot be scheduled in the past")

class MeetingParticipant(BaseModel):
    ATTENDANCE_STATUS = (
        ('confirmed', 'Confirmed'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    meeting = models.ForeignKey(ParentTeacherMeeting, on_delete=models.CASCADE)
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='confirmed')
    confirmation_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'meeting_participants'
        unique_together = ['meeting', 'parent']

    def __str__(self):
        return f"{self.parent.get_full_name()} - {self.meeting.title}"

class CommunicationPreference(BaseModel):
    CHANNEL_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='communication_preferences'
    )
    
    # Notification preferences
    receive_announcements = models.BooleanField(default=True)
    receive_grades_notifications = models.BooleanField(default=True)
    receive_attendance_notifications = models.BooleanField(default=True)
    receive_event_reminders = models.BooleanField(default=True)
    receive_assignment_notifications = models.BooleanField(default=True)
    receive_behavior_notifications = models.BooleanField(default=True)
    
    # Channel preferences
    preferred_channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='email')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'communication_preferences'
        verbose_name = 'Communication Preference'
        verbose_name_plural = 'Communication Preferences'

    def __str__(self):
        return f"Preferences for {self.user.get_full_name()}"

class Feedback(BaseModel):
    FEEDBACK_TYPES = (
        ('general', 'General Feedback'),
        ('technical', 'Technical Issue'),
        ('suggestion', 'Suggestion'),
        ('complaint', 'Complaint'),
        ('compliment', 'Compliment'),
    )

    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('addressed', 'Addressed'),
        ('closed', 'Closed'),
    )

    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='general')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Submitter information
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='submitted_feedback'
    )
    contact_email = models.EmailField(blank=True)
    
    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=Announcement.PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_feedback',
        limit_choices_to={'role__in': ['admin', 'head_teacher']}
    )
    
    # Response
    admin_notes = models.TextField(blank=True)
    response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='responded_feedback',
        limit_choices_to={'role__in': ['admin', 'head_teacher']}
    )
    
    # Metadata
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']
        verbose_name_plural = 'Feedback'

    def __str__(self):
        return f"{self.feedback_type}: {self.title}"