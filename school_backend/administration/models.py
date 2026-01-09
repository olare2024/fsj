"""
administration/models.py
Enhanced administration models for Delvok Academy school management system.
Handles school configuration, announcements, security logs, and non-academic structures.
"""

import logging
from datetime import date, datetime
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from user_agents import parse

logger = logging.getLogger(__name__)

# ==================== CONSTANTS ====================

SCHOOL_TYPE_CHOICE = [
    ('primary', 'Primary School'),
    ('secondary', 'Secondary School'),
    ('mixed', 'Mixed Primary & Secondary'),
    ('international', 'International School'),
    ('private', 'Private School'),
    ('public', 'Public School'),
    ('boarding', 'Boarding School'),
    ('day', 'Day School'),
]

SCHOOL_STUDENTS_GENDER = [
    ('boys', 'Boys Only'),
    ('girls', 'Girls Only'),
    ('mixed', 'Mixed'),
]

SCHOOL_OWNERSHIP = [
    ('private', 'Private'),
    ('public', 'Public'),
    ('religious', 'Religious Organization'),
    ('community', 'Community Owned'),
    ('government', 'Government'),
    ('trust', 'Trust/Society'),
]

STUDENT_GRADE_CHOICES = [
    ('pre_primary', 'Pre-Primary'),
    ('grade_1', 'Grade 1'),
    ('grade_2', 'Grade 2'),
    ('grade_3', 'Grade 3'),
    ('grade_4', 'Grade 4'),
    ('grade_5', 'Grade 5'),
    ('grade_6', 'Grade 6'),
    ('grade_7', 'Grade 7'),
    ('grade_8', 'Grade 8'),
    ('grade_9', 'Grade 9'),
    ('grade_10', 'Grade 10'),
    ('grade_11', 'Grade 11'),
    ('grade_12', 'Grade 12'),
]

CURRICULUM_CHOICES = [
    ('cbc', 'Competency Based Curriculum (CBC)'),
    ('8-4-4', '8-4-4 System'),
    ('cambridge', 'Cambridge International'),
    ('ib', 'International Baccalaureate'),
    ('american', 'American Curriculum'),
    ('montessori', 'Montessori'),
    ('national', 'National Curriculum'),
    ('combined', 'Combined Curriculum'),
]

# ==================== CUSTOM EXCEPTIONS ====================

class AdministrationValidationError(ValidationError):
    """Custom exception for administration validation errors"""
    pass

class AcademicYearConflictError(Exception):
    """Custom exception for academic year conflicts"""
    pass

# ==================== BASE MODEL ====================

class BaseAdministrationModel(models.Model):
    """
    Base model for administration models with audit trail.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    
    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_entries',
        verbose_name=_("Created By")
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_entries',
        verbose_name=_("Updated By")
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Auto-set audit fields if user is available in request.
        """
        from django.contrib.auth.models import AnonymousUser
        request = getattr(settings, 'CURRENT_REQUEST', None)
        
        if request and hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            if not self.pk and not self.created_by:
                self.created_by = request.user
            if not self.updated_by:
                self.updated_by = request.user
        
        super().save(*args, **kwargs)

# ==================== ADMINISTRATION MODELS ====================

class Article(BaseAdministrationModel):
    """Enhanced Article model for school announcements and news"""
    
    ARTICLE_CATEGORIES = [
        ('announcement', 'Announcement'),
        ('news', 'News'),
        ('event', 'Event'),
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('achievement', 'Achievement'),
        ('parent_info', 'Parent Information'),
        ('student_info', 'Student Information'),
        ('staff_info', 'Staff Information'),
        ('other', 'Other'),
    ]
    
    ARTICLE_STATUS = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('scheduled', 'Scheduled'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=150, blank=False, null=False, verbose_name=_("Title"))
    content = models.TextField(blank=False, null=False, verbose_name=_("Content"))
    summary = models.TextField(
        max_length=500, 
        blank=True, 
        null=True, 
        help_text=_("Brief summary for preview"),
        verbose_name=_("Summary")
    )
    
    # Classification
    category = models.CharField(
        max_length=20, 
        choices=ARTICLE_CATEGORIES, 
        default='announcement',
        verbose_name=_("Category")
    )
    status = models.CharField(
        max_length=20, 
        choices=ARTICLE_STATUS, 
        default='draft',
        verbose_name=_("Status")
    )
    
    # Media
    picture = models.ImageField(
        upload_to="articles/%Y/%m/", 
        blank=True, 
        null=True,
        verbose_name=_("Picture")
    )
    attachments = models.JSONField(
        default=list, 
        blank=True,
        help_text=_("List of attached files with metadata"),
        verbose_name=_("Attachments")
    )
    
    # Visibility Settings
    featured = models.BooleanField(
        default=False, 
        help_text=_("Feature this article prominently"),
        verbose_name=_("Featured")
    )
    pinned = models.BooleanField(
        default=False, 
        help_text=_("Pin this article to the top"),
        verbose_name=_("Pinned")
    )
    
    # Audience Targeting
    target_roles = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("Roles that should see this article"),
        verbose_name=_("Target Roles")
    )
    target_grades = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("Specific grades this article applies to"),
        verbose_name=_("Target Grades")
    )
    
    # Scheduling
    published_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name=_("Published At")
    )
    expire_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text=_("When to automatically archive this article"),
        verbose_name=_("Expire At")
    )
    
    # Engagement Tracking
    views = models.PositiveIntegerField(default=0, verbose_name=_("Views"))
    likes = models.PositiveIntegerField(default=0, verbose_name=_("Likes"))
    shares = models.PositiveIntegerField(default=0, verbose_name=_("Shares"))
    
    # SEO & Metadata
    meta_title = models.CharField(
        max_length=70, 
        blank=True, 
        null=True,
        help_text=_("SEO title (max 70 characters)"),
        verbose_name=_("Meta Title")
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        null=True,
        help_text=_("SEO description (max 160 characters)"),
        verbose_name=_("Meta Description")
    )
    keywords = models.JSONField(
        default=list, 
        blank=True,
        help_text=_("Keywords for search and categorization"),
        verbose_name=_("Keywords")
    )

    class Meta:
        db_table = 'articles'
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ['-pinned', '-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['featured', 'published_at']),
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['expire_at']),
        ]
        permissions = [
            ('can_publish_article', _('Can publish articles')),
            ('can_feature_article', _('Can feature articles')),
            ('can_schedule_article', _('Can schedule articles')),
            ('can_delete_article', _('Can delete articles')),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Validate article data."""
        errors = {}
        
        # Published date validation
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        if self.published_at and self.published_at > timezone.now():
            if self.status != 'scheduled':
                errors['published_at'] = _('Published date cannot be in the future for non-scheduled articles')
        
        # Expiration date validation
        if self.expire_at and self.published_at:
            if self.expire_at <= self.published_at:
                errors['expire_at'] = _('Expiration date must be after publish date')
        
        # Auto-generate summary if empty
        if not self.summary and self.content:
            self.summary = self.content[:497] + '...' if len(self.content) > 500 else self.content
        
        # Auto-generate meta fields if empty
        if not self.meta_title and self.title:
            self.meta_title = self.title[:70]
        
        if not self.meta_description and self.summary:
            self.meta_description = self.summary[:160]
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def increment_views(self):
        """Increment article view count."""
        self.views += 1
        self.save(update_fields=['views'])

    def increment_likes(self):
        """Increment article like count."""
        self.likes += 1
        self.save(update_fields=['likes'])

    def increment_shares(self):
        """Increment article share count."""
        self.shares += 1
        self.save(update_fields=['shares'])

    @property
    def is_published(self):
        """Check if article is published and visible."""
        if self.status != 'published':
            return False
        if not self.published_at:
            return False
        if self.published_at > timezone.now():
            return False
        if self.expire_at and self.expire_at < timezone.now():
            return False
        return True

    @property
    def reading_time(self):
        """Calculate estimated reading time in minutes."""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))

    @property
    def engagement_rate(self):
        """Calculate engagement rate."""
        if self.views == 0:
            return 0
        return round(((self.likes + self.shares) / self.views) * 100, 2)

    def get_target_audience_display(self):
        """Get formatted target audience."""
        audiences = []
        if self.target_roles:
            audiences.append(f"Roles: {', '.join(self.target_roles)}")
        if self.target_grades:
            audiences.append(f"Grades: {', '.join(self.target_grades)}")
        return ' | '.join(audiences) if audiences else _("All Users")


class CarouselImage(BaseAdministrationModel):
    """Enhanced Carousel model for school homepage"""
    
    CAROUSEL_POSITIONS = [
        ('main', 'Main Carousel'),
        ('sidebar', 'Sidebar'),
        ('events', 'Events Section'),
        ('announcements', 'Announcements Section'),
        ('admissions', 'Admissions Section'),
        ('achievements', 'Achievements Section'),
    ]
    
    CAROUSEL_TYPES = [
        ('image', 'Image Only'),
        ('image_text', 'Image with Text'),
        ('video', 'Video'),
        ('slider', 'Image Slider'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=150, blank=False, null=False, verbose_name=_("Title"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    # Media
    picture = models.ImageField(upload_to="carousel/%Y/%m/", verbose_name=_("Picture"))
    thumbnail = models.ImageField(
        upload_to="carousel/thumbnails/%Y/%m/", 
        blank=True, 
        null=True,
        verbose_name=_("Thumbnail")
    )
    
    # Display Settings
    position = models.CharField(
        max_length=20, 
        choices=CAROUSEL_POSITIONS, 
        default='main',
        verbose_name=_("Position")
    )
    type = models.CharField(
        max_length=20, 
        choices=CAROUSEL_TYPES, 
        default='image',
        verbose_name=_("Type")
    )
    order = models.PositiveIntegerField(
        default=0, 
        help_text=_("Display order (lower numbers first)"),
        verbose_name=_("Order")
    )
    active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # Link Configuration
    link_url = models.URLField(
        blank=True, 
        null=True, 
        help_text=_("Optional link when image is clicked"),
        verbose_name=_("Link URL")
    )
    link_text = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text=_("Text for the link button"),
        verbose_name=_("Link Text")
    )
    open_in_new_tab = models.BooleanField(default=False, verbose_name=_("Open in New Tab"))
    
    # Scheduling
    start_date = models.DateTimeField(
        default=timezone.now, 
        help_text=_("When to start showing this image"),
        verbose_name=_("Start Date")
    )
    end_date = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text=_("When to stop showing this image"),
        verbose_name=_("End Date")
    )
    
    # Analytics
    views = models.PositiveIntegerField(default=0, verbose_name=_("Views"))
    clicks = models.PositiveIntegerField(default=0, verbose_name=_("Clicks"))
    
    # Customization
    overlay_color = models.CharField(
        max_length=7, 
        default='#00000080',
        help_text=_("Overlay color in hex with opacity (e.g., #00000080)"),
        verbose_name=_("Overlay Color")
    )
    text_color = models.CharField(
        max_length=7, 
        default='#FFFFFF',
        help_text=_("Text color in hex"),
        verbose_name=_("Text Color")
    )

    class Meta:
        db_table = 'carousel_images'
        verbose_name = _("Carousel Image")
        verbose_name_plural = _("Carousel Images")
        ordering = ['position', 'order', '-created_at']
        indexes = [
            models.Index(fields=['position', 'active']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['type', 'active']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Validate carousel image dates."""
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError({'end_date': _('End date must be after start date')})
        
        if not self.link_text and self.link_url:
            self.link_text = _("Learn More")
        
        # Auto-generate thumbnail if not provided
        if not self.thumbnail and self.picture:
            # In a real implementation, you would generate a thumbnail here
            # For now, we'll use the same picture
            pass

    @property
    def is_active(self):
        """Check if carousel image should be displayed."""
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True

    @property
    def click_through_rate(self):
        """Calculate click-through rate."""
        if self.views == 0:
            return 0
        return round((self.clicks / self.views) * 100, 2)

    def increment_views(self):
        """Increment view count."""
        self.views += 1
        self.save(update_fields=['views'])

    def increment_clicks(self):
        """Increment click count."""
        self.clicks += 1
        self.save(update_fields=['clicks'])

    def get_display_config(self):
        """Get display configuration."""
        return {
            'title': self.title,
            'description': self.description,
            'image_url': self.picture.url if self.picture else None,
            'thumbnail_url': self.thumbnail.url if self.thumbnail else None,
            'link': {
                'url': self.link_url,
                'text': self.link_text,
                'open_in_new_tab': self.open_in_new_tab,
            },
            'style': {
                'overlay_color': self.overlay_color,
                'text_color': self.text_color,
            },
            'analytics': {
                'views': self.views,
                'clicks': self.clicks,
                'ctr': self.click_through_rate,
            }
        }


class AccessLog(models.Model):
    """Enhanced Access Log model for security and analytics"""
    
    LOGIN_TYPES = [
        ('success', 'Successful Login'),
        ('failed', 'Failed Login'),
        ('logout', 'Logout'),
        ('token_refresh', 'Token Refresh'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('session_timeout', 'Session Timeout'),
    ]
    
    SECURITY_LEVELS = [
        ('normal', 'Normal'),
        ('suspicious', 'Suspicious'),
        ('malicious', 'Malicious'),
        ('blocked', 'Blocked'),
    ]
    
    # User Information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='access_logs',
        verbose_name=_("User")
    )
    username_attempt = models.CharField(
        max_length=150, 
        blank=True, 
        null=True,
        help_text=_("Username used in login attempt"),
        verbose_name=_("Username Attempt")
    )
    
    # Device & Network Information
    user_agent = models.TextField(
        help_text=_("User agent string for browser/OS detection"),
        verbose_name=_("User Agent")
    )
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"))
    forwarded_ip = models.GenericIPAddressField(
        blank=True, 
        null=True,
        help_text=_("X-Forwarded-For IP if behind proxy"),
        verbose_name=_("Forwarded IP")
    )
    
    # Session Information
    session_key = models.CharField(max_length=40, blank=True, null=True, verbose_name=_("Session Key"))
    device_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Device ID"))
    
    # Access Details
    login_type = models.CharField(
        max_length=20, 
        choices=LOGIN_TYPES, 
        default='success',
        verbose_name=_("Login Type")
    )
    usage_description = models.CharField(max_length=255, verbose_name=_("Usage Description"))
    
    # Location Data
    location_data = models.JSONField(
        default=dict, 
        blank=True, 
        help_text=_("Geolocation data from IP"),
        verbose_name=_("Location Data")
    )
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Country"))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("City"))
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        verbose_name=_("Latitude")
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        blank=True, 
        null=True,
        verbose_name=_("Longitude")
    )
    
    # Security Information
    security_level = models.CharField(
        max_length=20, 
        choices=SECURITY_LEVELS, 
        default='normal',
        verbose_name=_("Security Level")
    )
    is_suspicious = models.BooleanField(default=False, verbose_name=_("Is Suspicious"))
    suspicious_reason = models.TextField(blank=True, null=True, verbose_name=_("Suspicious Reason"))
    threat_score = models.IntegerField(
        default=0, 
        help_text=_("Threat score from 0-100"),
        verbose_name=_("Threat Score")
    )
    
    # Authentication Details
    auth_method = models.CharField(
        max_length=50, 
        default='password',
        help_text=_("Authentication method used"),
        verbose_name=_("Authentication Method")
    )
    two_factor_used = models.BooleanField(default=False, verbose_name=_("2FA Used"))
    two_factor_method = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name=_("2FA Method")
    )
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))
    duration = models.DurationField(
        blank=True, 
        null=True,
        help_text=_("Session duration for logout events"),
        verbose_name=_("Duration")
    )

    class Meta:
        db_table = 'access_logs'
        verbose_name = _("Access Log")
        verbose_name_plural = _("Access Logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['login_type', 'timestamp']),
            models.Index(fields=['is_suspicious', 'timestamp']),
            models.Index(fields=['security_level', 'timestamp']),
            models.Index(fields=['country', 'timestamp']),
        ]

    def __str__(self):
        user_display = self.user.email if self.user else self.username_attempt or 'Unknown'
        return f"{user_display} - {self.login_type} at {self.timestamp}"

    def extract_device_info(self):
        """Extract device information from user agent."""
        try:
            user_agent = parse(self.user_agent)
            return {
                'operating_system': user_agent.os.family,
                'os_version': user_agent.os.version_string,
                'browser': user_agent.browser.family,
                'browser_version': user_agent.browser.version_string,
                'device': user_agent.device.family,
                'device_brand': user_agent.device.brand,
                'device_model': user_agent.device.model,
                'is_mobile': user_agent.is_mobile,
                'is_tablet': user_agent.is_tablet,
                'is_pc': user_agent.is_pc,
                'is_bot': user_agent.is_bot,
                'is_email_client': user_agent.is_email_client,
            }
        except Exception as e:
            logger.warning(f"Error extracting device info from UA: {e}")
            return {
                'operating_system': 'Unknown',
                'browser': 'Unknown',
                'device': 'Unknown',
            }

    def get_device_summary(self):
        """Get formatted device summary."""
        device_info = self.extract_device_info()
        return {
            'os': device_info.get('operating_system', 'Unknown'),
            'browser': device_info.get('browser', 'Unknown'),
            'device_type': self._get_device_type(device_info),
            'is_bot': device_info.get('is_bot', False),
        }

    def _get_device_type(self, device_info):
        """Determine device type from device info."""
        if device_info.get('is_mobile'):
            return "Mobile"
        elif device_info.get('is_tablet'):
            return "Tablet"
        elif device_info.get('is_pc'):
            return "Desktop"
        elif device_info.get('is_bot'):
            return "Bot"
        else:
            return "Unknown"

    def get_location_summary(self):
        """Get formatted location summary."""
        return {
            'country': self.country or self.location_data.get('country', 'Unknown'),
            'city': self.city or self.location_data.get('city', 'Unknown'),
            'coordinates': {
                'latitude': float(self.latitude) if self.latitude else None,
                'longitude': float(self.longitude) if self.longitude else None,
            },
            'ip': self.ip_address,
        }

    def flag_as_suspicious(self, reason, threat_score_increment=10):
        """Flag this access attempt as suspicious."""
        self.is_suspicious = True
        self.security_level = 'suspicious'
        self.suspicious_reason = reason
        self.threat_score = min(100, self.threat_score + threat_score_increment)
        self.save(update_fields=['is_suspicious', 'security_level', 'suspicious_reason', 'threat_score'])

    def flag_as_malicious(self, reason):
        """Flag this access attempt as malicious."""
        self.is_suspicious = True
        self.security_level = 'malicious'
        self.suspicious_reason = reason
        self.threat_score = 100
        self.save(update_fields=['is_suspicious', 'security_level', 'suspicious_reason', 'threat_score'])

    def calculate_threat_score(self):
        """Calculate threat score based on various factors."""
        score = 0
        
        # Failed login attempts
        if self.login_type == 'failed':
            score += 20
        
        # Suspicious IP patterns
        if self.ip_address:
            # Check for known VPN/Tor/proxy (simplified)
            if any(ip in self.ip_address for ip in ['10.', '172.', '192.168.']):
                score += 10
        
        # Suspicious user agent
        device_info = self.extract_device_info()
        if device_info.get('is_bot'):
            score += 30
        
        # Geographic anomalies (simplified)
        if self.country and self.user and hasattr(self.user, 'profile'):
            # Compare with user's usual country
            pass
        
        self.threat_score = min(100, score)
        self.save(update_fields=['threat_score'])
        
        return self.threat_score

    @property
    def needs_review(self):
        """Check if this log needs security review."""
        return self.threat_score >= 50 or self.is_suspicious

    @property
    def session_duration_minutes(self):
        """Get session duration in minutes."""
        if self.duration:
            return self.duration.total_seconds() / 60
        return 0


class School(BaseAdministrationModel):
    """Enhanced School model for Delvok Academy Kenya"""
    
    # Status and Identification
    active = models.BooleanField(
        default=False,
        help_text=_("WARNING: Only one school can be active. This will become the default school system-wide."),
        verbose_name=_("Active")
    )
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    code = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True, 
        help_text=_("School code (e.g., DELVOK)"),
        verbose_name=_("Code")
    )
    
    # Academic Configuration
    current_academic_year = models.ForeignKey(
        'academics.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='school_settings',
        help_text=_("Currently active academic year"),
        verbose_name=_("Current Academic Year")
    )
    default_curriculum = models.CharField(
        max_length=20, 
        choices=CURRICULUM_CHOICES, 
        default='cbc',
        verbose_name=_("Default Curriculum")
    )
    supported_curriculums = models.JSONField(
        default=list, 
        blank=True,
        help_text=_("List of supported curricula"),
        verbose_name=_("Supported Curriculums")
    )
    
    # School Information
    address = models.TextField(verbose_name=_("Address"))
    school_type = models.CharField(
        max_length=25, 
        choices=SCHOOL_TYPE_CHOICE,
        verbose_name=_("School Type")
    )
    students_gender = models.CharField(
        max_length=25, 
        choices=SCHOOL_STUDENTS_GENDER,
        verbose_name=_("Students Gender")
    )
    ownership = models.CharField(
        max_length=25, 
        choices=SCHOOL_OWNERSHIP,
        verbose_name=_("Ownership")
    )
    
    # Contact Information
    telephone = models.CharField(max_length=20, verbose_name=_("Telephone"))
    mobile = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_("Mobile")
    )
    school_email = models.EmailField(verbose_name=_("School Email"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    
    # Additional Contacts
    principal_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Principal Name"))
    principal_email = models.EmailField(blank=True, null=True, verbose_name=_("Principal Email"))
    principal_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Principal Phone"))
    
    # School Details
    mission = models.TextField(blank=True, null=True, verbose_name=_("Mission"))
    vision = models.TextField(blank=True, null=True, verbose_name=_("Vision"))
    motto = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Motto"))
    core_values = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("List of core values"),
        verbose_name=_("Core Values")
    )
    history = models.TextField(blank=True, null=True, verbose_name=_("History"))
    
    # Media
    school_logo = models.ImageField(
        upload_to="school_info/logos/%Y/", 
        blank=True, 
        null=True,
        verbose_name=_("School Logo")
    )
    school_banner = models.ImageField(
        upload_to="school_info/banners/%Y/", 
        blank=True, 
        null=True,
        verbose_name=_("School Banner")
    )
    gallery = models.JSONField(
        default=list, 
        blank=True,
        help_text=_("School gallery images"),
        verbose_name=_("Gallery")
    )
    
    # Academic Settings
    language = models.CharField(
        max_length=50, 
        default='English', 
        help_text=_("Primary language of instruction"),
        verbose_name=_("Language")
    )
    additional_languages = models.JSONField(
        default=list, 
        blank=True,
        help_text=_("Additional languages taught"),
        verbose_name=_("Additional Languages")
    )
    
    # Academic Calendar
    academic_calendar = models.JSONField(
        default=dict, 
        blank=True,
        help_text=_("Academic calendar configuration"),
        verbose_name=_("Academic Calendar")
    )
    
    # Facilities
    facilities = models.JSONField(
        default=list, 
        blank=True,
        help_text=_("School facilities and infrastructure"),
        verbose_name=_("Facilities")
    )
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True, verbose_name=_("Facebook URL"))
    twitter_url = models.URLField(blank=True, null=True, verbose_name=_("Twitter URL"))
    instagram_url = models.URLField(blank=True, null=True, verbose_name=_("Instagram URL"))
    linkedin_url = models.URLField(blank=True, null=True, verbose_name=_("LinkedIn URL"))
    youtube_url = models.URLField(blank=True, null=True, verbose_name=_("YouTube URL"))
    
    # Timestamps
    established_date = models.DateField(blank=True, null=True, verbose_name=_("Established Date"))
    registration_date = models.DateField(blank=True, null=True, verbose_name=_("Registration Date"))
    registration_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name=_("Registration Number")
    )

    class Meta:
        db_table = 'schools'
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['code']),
            models.Index(fields=['school_type']),
            models.Index(fields=['current_academic_year']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['active'],
                condition=models.Q(active=True),
                name='unique_active_school'
            )
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate school data."""
        errors = {}
        
        # Active school validation
        if self.active:
            existing_active = School.objects.filter(active=True).exclude(pk=self.pk)
            if existing_active.exists():
                errors['active'] = _(
                    'Only one school can be active at a time. '
                    'Please deactivate the current active school first.'
                )
        
        # Code generation
        if not self.code and self.name:
            self.code = self.name.upper().replace(' ', '_')[:20]
        
        # Curriculum validation
        if self.default_curriculum not in self.supported_curriculums:
            self.supported_curriculums.append(self.default_curriculum)
        
        # Date validation
        if self.established_date and self.established_date > date.today():
            errors['established_date'] = _('Established date cannot be in the future')
        
        if self.registration_date and self.established_date:
            if self.registration_date < self.established_date:
                errors['registration_date'] = _('Registration date cannot be before established date')
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Get formatted school name."""
        return f"Delvok Academy - {self.name}"

    def get_statistics(self):
        """Get school statistics."""
        try:
            from django.apps import apps
            
            # Safely get models to avoid circular imports
            User = apps.get_model('accounts', 'User')
            StudentEnrollment = apps.get_model('students', 'StudentEnrollment')
            
            current_year = self.current_academic_year
            
            stats = {
                'total_students': User.objects.filter(role='student', is_active=True).count(),
                'total_staff': User.objects.filter(
                    role__in=['teacher', 'admin', 'staff', 'accountant'],
                    is_active=True
                ).count(),
                'total_teachers': User.objects.filter(role='teacher', is_active=True).count(),
                'total_classes': self._get_class_count(current_year),
                'total_subjects': self._get_subject_count(),
            }
            
            if current_year:
                stats.update({
                    'current_year_students': StudentEnrollment.objects.filter(
                        academic_year=current_year,
                        status='active'
                    ).count() if StudentEnrollment else 0,
                    'current_year_name': current_year.name,
                })
            
            return stats
        except (LookupError, ImportError) as e:
            logger.error(f"Error getting school statistics: {e}")
            return {}

    def _get_class_count(self, academic_year):
        """Get number of classes for academic year."""
        try:
            from django.apps import apps
            Class = apps.get_model('academics', 'Class')
            if academic_year:
                return Class.objects.filter(academic_year=academic_year, is_active=True).count()
            return Class.objects.filter(is_active=True).count()
        except LookupError:
            return 0

    def _get_subject_count(self):
        """Get number of subjects."""
        try:
            from django.apps import apps
            Subject = apps.get_model('academics', 'Subject')
            return Subject.objects.filter(is_active=True).count()
        except LookupError:
            return 0

    def get_contact_info(self):
        """Get formatted contact information."""
        return {
            'primary': {
                'telephone': self.telephone,
                'mobile': self.mobile,
                'email': self.school_email,
                'website': self.website,
            },
            'principal': {
                'name': self.principal_name,
                'email': self.principal_email,
                'phone': self.principal_phone,
            }
        }

    def get_social_links(self):
        """Get social media links."""
        links = {}
        if self.facebook_url:
            links['facebook'] = self.facebook_url
        if self.twitter_url:
            links['twitter'] = self.twitter_url
        if self.instagram_url:
            links['instagram'] = self.instagram_url
        if self.linkedin_url:
            links['linkedin'] = self.linkedin_url
        if self.youtube_url:
            links['youtube'] = self.youtube_url
        return links

    def get_academic_info(self):
        """Get academic information."""
        return {
            'current_academic_year': self.current_academic_year.name if self.current_academic_year else None,
            'default_curriculum': self.get_default_curriculum_display(),
            'supported_curriculums': [
                dict(CURRICULUM_CHOICES).get(curriculum, curriculum)
                for curriculum in self.supported_curriculums
            ],
            'language': self.language,
            'additional_languages': self.additional_languages,
        }

    def activate(self):
        """Activate this school as the current school."""
        School.objects.filter(active=True).update(active=False)
        self.active = True
        self.save()
        return True

    def deactivate(self):
        """Deactivate this school."""
        self.active = False
        self.save()
        return True


class Day(BaseAdministrationModel):
    """Enhanced Day model for timetable scheduling"""
    
    DAY_CHOICES = [
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    ]
    
    DAY_TYPES = [
        ('school_day', 'School Day'),
        ('weekend', 'Weekend'),
        ('holiday', 'Holiday'),
        ('half_day', 'Half Day'),
        ('exam_day', 'Examination Day'),
    ]
    
    # Day Information
    day_number = models.IntegerField(choices=DAY_CHOICES, unique=True, verbose_name=_("Day Number"))
    short_name = models.CharField(
        max_length=3, 
        blank=True, 
        null=True, 
        help_text=_("Short name (e.g., Mon)"),
        verbose_name=_("Short Name")
    )
    full_name = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_("Full Name")
    )
    
    # Day Configuration
    day_type = models.CharField(
        max_length=20, 
        choices=DAY_TYPES, 
        default='school_day',
        verbose_name=_("Day Type")
    )
    is_school_day = models.BooleanField(
        default=True, 
        help_text=_("Whether this is typically a school day"),
        verbose_name=_("Is School Day")
    )
    is_instructional_day = models.BooleanField(
        default=True, 
        help_text=_("Whether instructional activities occur on this day"),
        verbose_name=_("Is Instructional Day")
    )
    
    # Timetable Configuration
    start_time = models.TimeField(
        default='08:00',
        help_text=_("Default start time for this day"),
        verbose_name=_("Start Time")
    )
    end_time = models.TimeField(
        default='16:00',
        help_text=_("Default end time for this day"),
        verbose_name=_("End Time")
    )
    break_start_time = models.TimeField(
        default='10:30',
        blank=True, 
        null=True,
        help_text=_("Break start time"),
        verbose_name=_("Break Start Time")
    )
    break_end_time = models.TimeField(
        default='11:00',
        blank=True, 
        null=True,
        help_text=_("Break end time"),
        verbose_name=_("Break End Time")
    )
    lunch_start_time = models.TimeField(
        default='13:00',
        blank=True, 
        null=True,
        help_text=_("Lunch start time"),
        verbose_name=_("Lunch Start Time")
    )
    lunch_end_time = models.TimeField(
        default='14:00',
        blank=True, 
        null=True,
        help_text=_("Lunch end time"),
        verbose_name=_("Lunch End Time")
    )
    
    # Period Configuration
    total_periods = models.IntegerField(
        default=8,
        help_text=_("Total number of periods on this day"),
        verbose_name=_("Total Periods")
    )
    period_duration = models.IntegerField(
        default=40,
        help_text=_("Duration of each period in minutes"),
        verbose_name=_("Period Duration")
    )
    
    # Special Configuration
    special_instructions = models.TextField(
        blank=True, 
        null=True,
        help_text=_("Special instructions or notes for this day"),
        verbose_name=_("Special Instructions")
    )
    color_code = models.CharField(
        max_length=7, 
        default='#3B82F6',
        help_text=_("Color code for calendar display"),
        verbose_name=_("Color Code")
    )
    weight = models.IntegerField(
        default=1,
        help_text=_("Weight for scheduling algorithms (higher = more important)"),
        verbose_name=_("Weight")
    )

    class Meta:
        db_table = 'days'
        verbose_name = _("Day")
        verbose_name_plural = _("Days")
        ordering = ['day_number']
        indexes = [
            models.Index(fields=['day_number', 'is_school_day']),
            models.Index(fields=['day_type']),
        ]

    def __str__(self):
        return self.get_day_number_display()

    def save(self, *args, **kwargs):
        """Auto-generate names if not provided."""
        if not self.short_name:
            self.short_name = self.get_day_number_display()[:3]
        
        if not self.full_name:
            self.full_name = self.get_day_number_display()
        
        # Auto-set day type based on day number
        if self.day_number in [6, 7]:  # Saturday, Sunday
            self.day_type = 'weekend'
            self.is_school_day = False
            self.is_instructional_day = False
        
        super().save(*args, **kwargs)

    def clean(self):
        """Validate day configuration."""
        errors = {}
        
        # Time validation
        if self.start_time >= self.end_time:
            errors['end_time'] = _('End time must be after start time')
        
        if self.break_start_time and self.break_end_time:
            if self.break_start_time >= self.break_end_time:
                errors['break_end_time'] = _('Break end time must be after break start time')
        
        if self.lunch_start_time and self.lunch_end_time:
            if self.lunch_start_time >= self.lunch_end_time:
                errors['lunch_end_time'] = _('Lunch end time must be after lunch start time')
        
        # Period validation
        if self.total_periods < 1 or self.total_periods > 12:
            errors['total_periods'] = _('Total periods must be between 1 and 12')
        
        if self.period_duration < 5 or self.period_duration > 120:
            errors['period_duration'] = _('Period duration must be between 5 and 120 minutes')
        
        if errors:
            raise ValidationError(errors)

    @property
    def is_weekend(self):
        """Check if this day is a weekend."""
        return self.day_number in [6, 7]

    @property
    def total_instructional_hours(self):
        """Calculate total instructional hours."""
        if not self.is_instructional_day:
            return 0
        
        total_minutes = self.total_periods * self.period_duration
        
        # Subtract break and lunch times if applicable
        if self.break_start_time and self.break_end_time:
            break_duration = self._time_difference(self.break_start_time, self.break_end_time)
            total_minutes -= break_duration
        
        if self.lunch_start_time and self.lunch_end_time:
            lunch_duration = self._time_difference(self.lunch_start_time, self.lunch_end_time)
            total_minutes -= lunch_duration
        
        return round(total_minutes / 60, 2)

    def _time_difference(self, start_time, end_time):
        """Calculate time difference in minutes."""
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        return (end_dt - start_dt).seconds // 60

    @property
    def schedule_template(self):
        """Get schedule template for this day."""
        template = {
            'day': self.get_day_number_display(),
            'short_name': self.short_name,
            'type': self.get_day_type_display(),
            'is_school_day': self.is_school_day,
            'is_instructional_day': self.is_instructional_day,
            'timings': {
                'start': self.start_time.strftime('%H:%M'),
                'end': self.end_time.strftime('%H:%M'),
                'break': {
                    'start': self.break_start_time.strftime('%H:%M') if self.break_start_time else None,
                    'end': self.break_end_time.strftime('%H:%M') if self.break_end_time else None,
                },
                'lunch': {
                    'start': self.lunch_start_time.strftime('%H:%M') if self.lunch_start_time else None,
                    'end': self.lunch_end_time.strftime('%H:%M') if self.lunch_end_time else None,
                },
            },
            'periods': {
                'total': self.total_periods,
                'duration_minutes': self.period_duration,
                'total_hours': self.total_instructional_hours,
            },
            'display': {
                'color': self.color_code,
                'weight': self.weight,
            }
        }
        
        return template

    def get_period_schedule(self):
        """Generate period schedule for this day."""
        if not self.is_instructional_day:
            return []
        
        schedule = []
        current_time = datetime.combine(date.today(), self.start_time)
        
        for period in range(1, self.total_periods + 1):
            period_start = current_time
            period_end = period_start + timedelta(minutes=self.period_duration)
            
            # Check for breaks
            if self.break_start_time and self.break_end_time:
                break_start = datetime.combine(date.today(), self.break_start_time)
                break_end = datetime.combine(date.today(), self.break_end_time)
                
                if period_start <= break_start < period_end:
                    # Adjust period end to break start
                    period_end = break_start
            
            if self.lunch_start_time and self.lunch_end_time:
                lunch_start = datetime.combine(date.today(), self.lunch_start_time)
                lunch_end = datetime.combine(date.today(), self.lunch_end_time)
                
                if period_start <= lunch_start < period_end:
                    # Adjust period end to lunch start
                    period_end = lunch_start
            
            schedule.append({
                'period_number': period,
                'start_time': period_start.time(),
                'end_time': period_end.time(),
                'duration_minutes': self.period_duration,
            })
            
            current_time = period_end
        
        return schedule


# ==================== SIGNAL HANDLERS ====================

@receiver(models.signals.pre_save, sender=School)
def ensure_single_active_school(sender, instance, **kwargs):
    """Ensure only one school is active at a time."""
    if instance.active:
        School.objects.exclude(pk=instance.pk).update(active=False)


@receiver(models.signals.post_save, sender=School)
def setup_default_school_config(sender, instance, created, **kwargs):
    """Setup default configuration when a school is created."""
    if created:
        # Create default days of the week
        for day_num, day_name in Day.DAY_CHOICES:
            Day.objects.get_or_create(
                day_number=day_num,
                defaults={
                    'short_name': day_name[:3],
                    'full_name': day_name,
                    'is_school_day': day_num <= 5,  # Monday to Friday
                    'is_instructional_day': day_num <= 5,
                }
            )
        
        logger.info(f"Default configuration created for school: {instance.name}")


@receiver(models.signals.pre_save, sender=Day)
def validate_day_times(sender, instance, **kwargs):
    """Validate day timing configuration before save."""
    try:
        instance.clean()
    except ValidationError as e:
        logger.error(f"Day validation error: {e}")
        raise


# ==================== HELPER FUNCTIONS ====================

def get_school_statistics(school_id=None):
    """
    Get statistics for a specific school or the active school.
    
    Args:
        school_id: Optional school ID. If None, uses active school.
    
    Returns:
        dict: School statistics
    """
    try:
        if school_id:
            school = School.objects.get(id=school_id, is_active=True)
        else:
            school = School.objects.filter(active=True, is_active=True).first()
        
        if not school:
            return {}
        
        return school.get_statistics()
    except School.DoesNotExist:
        logger.error(f"School not found: {school_id}")
        return {}
    except Exception as e:
        logger.error(f"Error getting school statistics: {e}")
        return {}


def get_active_school():
    """
    Get the currently active school.
    
    Returns:
        School: Active school instance or None
    """
    try:
        return School.objects.filter(active=True, is_active=True).first()
    except Exception as e:
        logger.error(f"Error getting active school: {e}")
        return None