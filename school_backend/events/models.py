from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import uuid
from datetime import timedelta

User = get_user_model()

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_categories'
        verbose_name_plural = 'Event categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class EventManager(models.Manager):
    def published(self):
        return self.filter(is_published=True, is_cancelled=False)
    
    def upcoming(self):
        return self.published().filter(start_date__gt=timezone.now())
    
    def ongoing(self):
        now = timezone.now()
        return self.published().filter(start_date__lte=now, end_date__gte=now)
    
    def past(self):
        return self.published().filter(end_date__lt=timezone.now())
    
    def by_type(self, event_type):
        return self.published().filter(event_type=event_type)
    
    def for_user_audience(self, user):
        """Filter events based on user type and audience targeting"""
        # This would need to be customized based on your user profile structure
        from students.models import StudentProfile
        from teachers.models import TeacherProfile
        
        if hasattr(user, 'student_profile'):
            return self.published().filter(
                models.Q(target_audience__in=['all', 'students']) |
                models.Q(target_audience='specific_grades', specific_grades__contains=[user.student_profile.grade_level])
            )
        elif hasattr(user, 'teacher_profile'):
            return self.published().filter(target_audience__in=['all', 'teachers'])
        elif hasattr(user, 'parent_profile'):
            return self.published().filter(target_audience__in=['all', 'parents'])
        else:
            return self.published().filter(target_audience='all')


class Event(models.Model):
    EVENT_TYPES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('community', 'Community'),
        ('holiday', 'Holiday'),
        ('meeting', 'Meeting'),
        ('workshop', 'Workshop'),
        ('celebration', 'Celebration'),
        ('competition', 'Competition'),
        ('field_trip', 'Field Trip'),
    ]
    
    AUDIENCE_CHOICES = [
        ('all', 'All'),
        ('students', 'Students'),
        ('teachers', 'Teachers'),
        ('parents', 'Parents'),
        ('staff', 'Staff'),
        ('specific_grades', 'Specific Grades'),
        ('specific_classes', 'Specific Classes'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    categories = models.ManyToManyField(EventCategory, blank=True, related_name='events')
    event_code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=200, blank=True)
    recurrence_end_date = models.DateTimeField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    
    # Location
    location = models.CharField(max_length=200)
    room_number = models.CharField(max_length=50, blank=True)
    online_link = models.URLField(blank=True)
    is_online = models.BooleanField(default=False)
    is_hybrid = models.BooleanField(default=False)
    venue_capacity = models.PositiveIntegerField(blank=True, null=True)
    
    # Organization
    organizer = models.CharField(max_length=200)
    organizer_contact = models.EmailField(blank=True)
    coordinator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='coordinated_events'
    )
    co_organizers = models.ManyToManyField(User, blank=True, related_name='co_organized_events')
    
    # Audience
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    specific_grades = models.JSONField(blank=True, null=True)
    specific_classes = models.JSONField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(blank=True, null=True)
    min_participants = models.PositiveIntegerField(default=1)
    waitlist_enabled = models.BooleanField(default=False)
    waitlist_capacity = models.PositiveIntegerField(blank=True, null=True)
    
    # Media
    image = models.ImageField(upload_to='events/images/%Y/%m/', blank=True)
    banner_image = models.ImageField(upload_to='events/banners/%Y/%m/', blank=True)
    gallery = models.JSONField(blank=True, null=True)  # Store multiple images
    documents = models.JSONField(blank=True, null=True)
    video_url = models.URLField(blank=True)
    
    # Status and Visibility
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_events'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    
    # Registration
    requires_registration = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    registration_start_date = models.DateTimeField(blank=True, null=True)
    registration_link = models.URLField(blank=True)
    allow_guest_registrations = models.BooleanField(default=False)
    max_guests_per_registration = models.PositiveIntegerField(default=0)
    
    # Financial
    has_fee = models.BooleanField(default=False)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fee_currency = models.CharField(max_length=3, default='KES')
    early_bird_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    early_bird_deadline = models.DateTimeField(blank=True, null=True)
    
    # Notification Settings
    send_reminders = models.BooleanField(default=True)
    auto_send_updates = models.BooleanField(default=True)
    
    # SEO and Analytics
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    views_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    objects = EventManager()

    class Meta:
        db_table = 'events'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['event_type']),
            models.Index(fields=['is_published']),
            models.Index(fields=['target_audience']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['slug']),
        ]
        permissions = [
            ('can_approve_event', 'Can approve events'),
            ('can_publish_event', 'Can publish events'),
            ('can_manage_event_categories', 'Can manage event categories'),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_date.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
            self.status = 'published'
        
        if self.requires_approval and self.approved_by and not self.approved_at:
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Event.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def is_past(self):
        return self.end_date < timezone.now()

    @property
    def duration(self):
        return self.end_date - self.start_date

    @property
    def registered_count(self):
        return self.registrations.filter(status='registered').count()

    @property
    def waitlist_count(self):
        return self.registrations.filter(status='waiting').count()

    @property
    def available_slots(self):
        if self.max_participants:
            return self.max_participants - self.registered_count
        return None

    @property
    def is_fully_booked(self):
        if self.max_participants:
            return self.registered_count >= self.max_participants
        return False

    @property
    def can_register(self):
        if not self.requires_registration:
            return False
        if self.is_cancelled or not self.is_published:
            return False
        if self.registration_deadline and timezone.now() > self.registration_deadline:
            return False
        if self.registration_start_date and timezone.now() < self.registration_start_date:
            return False
        return not self.is_fully_booked

    @property
    def current_fee(self):
        if not self.has_fee:
            return 0
        if self.early_bird_deadline and timezone.now() <= self.early_bird_deadline:
            return max(0, self.fee_amount - self.early_bird_discount)
        return self.fee_amount

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_detail', kwargs={'slug': self.slug})

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.start_date >= self.end_date:
            raise ValidationError(_("End date must be after start date"))
        
        if self.requires_registration and self.registration_deadline:
            if self.registration_deadline > self.start_date:
                raise ValidationError(_("Registration deadline must be before event start date"))
        
        if self.registration_start_date and self.registration_deadline:
            if self.registration_start_date >= self.registration_deadline:
                raise ValidationError(_("Registration start date must be before deadline"))
        
        if self.early_bird_deadline and self.registration_deadline:
            if self.early_bird_deadline > self.registration_deadline:
                raise ValidationError(_("Early bird deadline must be before registration deadline"))
        
        if self.min_participants and self.max_participants:
            if self.min_participants > self.max_participants:
                raise ValidationError(_("Minimum participants cannot exceed maximum participants"))


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('waiting', 'Waiting List'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancellation Fee Applied'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    
    # Student-specific registration
    student = models.ForeignKey(
        'students.StudentProfile', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='event_registrations'
    )
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='registered')
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # Guest registration support
    is_guest_registration = models.BooleanField(default=False)
    guest_name = models.CharField(max_length=200, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_count = models.PositiveIntegerField(default=1)
    
    # Additional information
    dietary_restrictions = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    
    # Payment
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Check-in
    checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(blank=True, null=True)
    checked_in_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='checked_in_registrations'
    )
    
    # Communication
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)  # For staff use only
    
    class Meta:
        db_table = 'event_registrations'
        unique_together = [
            ['event', 'user', 'student'],  # Prevent duplicate registrations
        ]
        ordering = ['registration_date']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['checked_in']),
        ]

    def __str__(self):
        if self.student:
            return f"{self.student.user.get_full_name()} - {self.event.title}"
        elif self.is_guest_registration:
            return f"{self.guest_name} (Guest) - {self.event.title}"
        return f"{self.user.get_full_name()} - {self.event.title}"

    @property
    def display_name(self):
        if self.student:
            return self.student.user.get_full_name()
        elif self.is_guest_registration:
            return self.guest_name
        return self.user.get_full_name()

    @property
    def email(self):
        if self.student:
            return self.student.user.email
        elif self.is_guest_registration:
            return self.guest_email
        return self.user.email

    @property
    def balance_due(self):
        return self.payment_amount - self.amount_paid

    @property
    def is_fully_paid(self):
        return self.amount_paid >= self.payment_amount

    def save(self, *args, **kwargs):
        # Auto-set payment amount based on event fee
        if not self.payment_amount and self.event.has_fee:
            self.payment_amount = self.event.current_fee * self.guest_count
        
        super().save(*args, **kwargs)


class EventReminder(models.Model):
    REMINDER_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]

    TRIGGER_TYPES = [
        ('before_start', 'Before Event Start'),
        ('after_registration', 'After Registration'),
        ('deadline_approaching', 'Registration Deadline Approaching'),
        ('custom', 'Custom Date'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPES)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES, default='before_start')
    trigger_offset = models.DurationField(blank=True, null=True)  # e.g., 2 days before
    custom_trigger_date = models.DateTimeField(blank=True, null=True)
    reminder_time = models.DateTimeField()
    
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    send_attempts = models.PositiveIntegerField(default=0)
    
    # Target audience
    target_audience = models.CharField(max_length=20, choices=Event.AUDIENCE_CHOICES, default='all')
    specific_users = models.ManyToManyField(User, blank=True)
    send_to_registered = models.BooleanField(default=False)
    
    # Content
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    template_name = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_reminders'
        ordering = ['reminder_time']
        indexes = [
            models.Index(fields=['event', 'sent']),
            models.Index(fields=['reminder_time', 'sent']),
        ]

    def __str__(self):
        return f"Reminder for {self.event.title} at {self.reminder_time}"

    def save(self, *args, **kwargs):
        if not self.reminder_time and self.trigger_type == 'before_start' and self.trigger_offset:
            self.reminder_time = self.event.start_date - self.trigger_offset
        elif not self.reminder_time and self.trigger_type == 'custom' and self.custom_trigger_date:
            self.reminder_time = self.custom_trigger_date
        
        super().save(*args, **kwargs)


class EventFeedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_feedbacks')
    
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    
    # Detailed ratings
    organization_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    content_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    venue_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    speaker_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    value_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    # Additional feedback
    would_recommend = models.BooleanField(null=True, blank=True)
    likely_to_attend_again = models.BooleanField(null=True, blank=True)
    suggestions = models.TextField(blank=True)
    highlights = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    
    # Metadata
    is_anonymous = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)  # For moderation
    helpful_count = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_feedbacks'
        unique_together = ['event', 'user']
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['event', 'rating']),
            models.Index(fields=['approved']),
        ]

    def __str__(self):
        return f"Feedback for {self.event.title} by {self.user.get_full_name()}"

    @property
    def average_rating(self):
        ratings = [r for r in [
            self.organization_rating,
            self.content_rating,
            self.venue_rating,
            self.speaker_rating,
            self.value_rating
        ] if r is not None]
        
        if ratings:
            return sum(ratings) / len(ratings)
        return self.rating


class EventAttachment(models.Model):
    ATTACHMENT_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('presentation', 'Presentation'),
        ('sponsor', 'Sponsor Material'),
        ('other', 'Other'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='events/attachments/%Y/%m/')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_type = models.CharField(max_length=15, choices=ATTACHMENT_TYPES, default='document')
    is_public = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_attachments'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} - {self.event.title}"


# Signals and Business Logic
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string

@receiver(pre_save, sender=Event)
def set_event_code_and_slug(sender, instance, **kwargs):
    if not instance.event_code:
        instance.event_code = f"EVT-{uuid.uuid4().hex[:8].upper()}"
    
    if not instance.slug:
        instance.slug = instance._generate_unique_slug()

@receiver(post_save, sender=Event)
def handle_event_status_change(sender, instance, created, **kwargs):
    """
    Handle notifications and actions when event status changes
    """
    if instance.is_published and not created:
        # Send publication notifications
        pass
    
    if instance.is_cancelled:
        # Send cancellation notifications and handle refunds
        pass

@receiver(post_save, sender=EventRegistration)
def handle_registration_creation(sender, instance, created, **kwargs):
    """
    Send confirmation emails and update waitlist status
    """
    if created:
        # Send registration confirmation
        pass
        
        # Check if event is fully booked and move people to waitlist
        if instance.event.is_fully_booked:
            # Logic to manage waitlist
            pass

@receiver(pre_save, sender=EventRegistration)
def handle_registration_payment(sender, instance, **kwargs):
    """
    Update payment status based on amount paid
    """
    if instance.amount_paid >= instance.payment_amount:
        instance.payment_status = 'paid'
    elif instance.amount_paid > 0:
        instance.payment_status = 'partial'