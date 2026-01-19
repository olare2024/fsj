# accounts/signals.py - COMPLETE UPDATED VERSION
from django.db.models.signals import post_save, pre_save, m2m_changed, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.apps import apps
from django.db import transaction, IntegrityError
from django.contrib.auth.models import Group
from contextlib import contextmanager
import logging
from datetime import timedelta
import json

from .models import User, UserProfile, TwoFactorAuth, OTPToken, LoginHistory, LoginSession

logger = logging.getLogger(__name__)


# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

@contextmanager
def disable_signals(signals=None):
    """
    Context manager to temporarily disable signals.
    Useful for bulk operations in admin or data migrations.
    
    Args:
        signals: List of signals to disable. If None, disables common signals.
    """
    if signals is None:
        signals = [post_save, pre_save, m2m_changed]
    
    original_receivers = {}
    
    try:
        for signal in signals:
            original_receivers[signal] = signal.receivers
            signal.receivers = []
        
        yield
        
    finally:
        for signal, receivers in original_receivers.items():
            signal.receivers = receivers

@contextmanager
def bulk_create_context():
    """
    Context manager for bulk create operations that optimizes performance.
    """
    with disable_signals(), transaction.atomic():
        yield

# ============================================================================
# CONFIGURATION
# ============================================================================

class SignalConfig:
    """Configuration for signal handlers"""
    
    # Email settings
    EMAIL_ENABLED = getattr(settings, 'EMAIL_ENABLED', True)
    EMAIL_RATE_LIMIT = 5  # emails per hour per user
    WELCOME_EMAIL_DELAY = 5  # seconds delay for async sending
    
    # Auto-create settings
    AUTO_CREATE_PROFILE = True
    AUTO_CREATE_2FA = True
    
    # Cache settings
    IDENTIFIER_CACHE_TTL = 3600  # 1 hour
    EMAIL_RATE_LIMIT_TTL = 3600  # 1 hour
    
    # Default admin settings
    DEFAULT_ADMIN_EMAIL = getattr(settings, 'DEFAULT_ADMIN_EMAIL', 'admin@delvok.ac.ke')
    DEFAULT_ADMIN_PASSWORD = getattr(settings, 'DEFAULT_ADMIN_PASSWORD', 'Admin@1234')
    
    # School settings
    SCHOOL_NAME = getattr(settings, 'SCHOOL_NAME', 'Delvok Academy')
    SCHOOL_SUPPORT_EMAIL = getattr(settings, 'SCHOOL_SUPPORT_EMAIL', 'support@delvok.ac.ke')
    SCHOOL_WEBSITE = getattr(settings, 'SCHOOL_WEBSITE', 'https://delvok.ac.ke')
    SCHOOL_PHONE = getattr(settings, 'SCHOOL_PHONE', '+254-700-000-000')
    
    # Frontend URLs
    FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'https://delvok.ac.ke')
    LOGIN_URL = f"{FRONTEND_URL}/login"
    
    # Profile completion tracking fields
    PROFILE_FIELDS_TO_TRACK = {
        'first_name', 'last_name', 'email', 'phone_number', 
        'date_of_birth', 'address', 'gender', 'nationality'
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_redis_client():
    """Get Redis client if available"""
    try:
        from django_redis import get_redis_connection
        return get_redis_connection("default")
    except ImportError:
        return None

def can_send_email(user_id, email_type="welcome", limit_per_hour=SignalConfig.EMAIL_RATE_LIMIT):
    """Check if we can send email to user (rate limiting with Redis if available)"""
    redis_client = get_redis_client()
    
    if redis_client:
        # Use Redis for rate limiting if available
        key = f"email:rate_limit:{user_id}:{email_type}"
        count = redis_client.get(key)
        
        if count is None:
            count = 0
        else:
            count = int(count)
        
        if count >= limit_per_hour:
            logger.warning(f"Rate limit exceeded for {email_type} email to user {user_id}")
            return False
        
        # Increment counter with pipeline for atomicity
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, SignalConfig.EMAIL_RATE_LIMIT_TTL)
        pipe.execute()
        return True
    else:
        # Fallback to Django cache
        cache_key = f"email_rate_limit_{user_id}_{email_type}"
        count = cache.get(cache_key, 0)
        
        if count >= limit_per_hour:
            logger.warning(f"Rate limit exceeded for {email_type} email to user {user_id}")
            return False
        
        cache.set(cache_key, count + 1, SignalConfig.EMAIL_RATE_LIMIT_TTL)
        return True

def generate_identifier_with_lock(prefix, year, role_specific=False):
    """
    Generate unique identifier with distributed lock to prevent race conditions.
    
    Args:
        prefix: Identifier prefix (e.g., 'DEL-STU', 'DEL-TCH')
        year: Year for identifier
        role_specific: Whether this is role-specific generation
    
    Returns:
        str: Generated identifier
    """
    redis_client = get_redis_client()
    
    if redis_client:
        # Use Redis lock for distributed systems
        lock_key = f"lock:identifier:{prefix}:{year}"
        identifier_key = f"last_identifier:{prefix}:{year}"
        
        # Try to acquire lock with 5 second timeout
        lock_acquired = redis_client.set(lock_key, '1', nx=True, ex=5)
        
        if not lock_acquired:
            # Wait a bit and retry or use fallback
            import time
            time.sleep(0.1)
            return generate_identifier_fallback(prefix, year, role_specific)
    
    return generate_identifier_local(prefix, year, role_specific)

def generate_identifier_local(prefix, year, role_specific=False):
    """Generate identifier using local cache/database"""
    cache_key = f"last_identifier_{prefix}_{year}"
    last_number = cache.get(cache_key)
    
    if last_number is None:
        # Query database
        if role_specific:
            filter_kwargs = {
                'staff_id__isnull': False,
                'staff_id__startswith': f"{prefix}-{year}"
            }
        else:
            filter_kwargs = {
                'admission_number__isnull': False,
                'admission_number__startswith': f"{prefix}-{year}"
            }
        
        last_user = User.objects.filter(**filter_kwargs).order_by(
            '-admission_number' if not role_specific else '-staff_id'
        ).first()
        
        if last_user:
            identifier = last_user.admission_number if not role_specific else last_user.staff_id
            try:
                last_number = int(identifier.split('-')[-1])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0
        
        cache.set(cache_key, last_number, SignalConfig.IDENTIFIER_CACHE_TTL)
    
    new_number = last_number + 1
    cache.set(cache_key, new_number, SignalConfig.IDENTIFIER_CACHE_TTL)
    
    return f"{prefix}-{year}-{new_number:04d}"

def generate_identifier_fallback(prefix, year, role_specific=False):
    """Fallback identifier generation"""
    import time
    timestamp = int(time.time() * 1000) % 1000000
    return f"{prefix}-{year}-{timestamp:06d}"

def generate_admission_number():
    """Generate a unique admission number with distributed lock"""
    year = timezone.now().year
    return generate_identifier_with_lock("DEL-STU", year, role_specific=False)

def generate_staff_id(role):
    """Generate a unique staff ID based on role"""
    year = timezone.now().year
    
    role_prefix = {
        User.Role.TEACHER: 'TCH',
        User.Role.HEAD_TEACHER: 'HT',
        User.Role.CURRICULUM_COORDINATOR: 'CC',
        User.Role.ACCOUNTANT: 'ACC',
        User.Role.ADMIN: 'ADM',
        User.Role.IT_SUPPORT: 'IT',
        User.Role.COUNSELOR: 'COU',
        User.Role.LIBRARIAN: 'LIB',
        User.Role.OFFICE_STAFF: 'OFF'
    }.get(role, 'EMP')
    
    return generate_identifier_with_lock(f"DEL-{role_prefix}", year, role_specific=True)

def create_related_objects(user):
    """Create all related objects for a user in transaction"""
    try:
        with transaction.atomic():
            # Create UserProfile if it doesn't exist
            if SignalConfig.AUTO_CREATE_PROFILE and not hasattr(user, 'user_profile'):
                UserProfile.objects.create(user=user)
                logger.info(f"Created UserProfile for {user.email}")
            
            # Create TwoFactorAuth settings if they don't exist
            if SignalConfig.AUTO_CREATE_2FA and not hasattr(user, 'two_factor_auth'):
                TwoFactorAuth.objects.create(user=user)
                logger.info(f"Created TwoFactorAuth settings for {user.email}")
            
            # Add to appropriate groups based on role
            assign_user_to_groups(user)
            
    except IntegrityError as e:
        logger.error(f"Integrity error creating related objects for {user.email}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error creating related objects for {user.email}: {e}")
        # Continue anyway, as these are non-critical objects

def assign_user_to_groups(user):
    """Assign user to appropriate groups based on role"""
    try:
        group_mapping = {
            User.Role.TEACHER: ['Teachers', 'Staff'],
            User.Role.STUDENT: ['Students'],
            User.Role.PARENT: ['Parents'],
            User.Role.ADMIN: ['Administrators', 'Staff'],
            User.Role.HEAD_TEACHER: ['Administrators', 'Teachers', 'Staff'],
            User.Role.CURRICULUM_COORDINATOR: ['Curriculum_Team', 'Staff'],
            User.Role.ACCOUNTANT: ['Finance_Team', 'Staff'],
            User.Role.IT_SUPPORT: ['IT_Team', 'Staff'],
            User.Role.COUNSELOR: ['Counselors', 'Staff'],
            User.Role.LIBRARIAN: ['Library_Staff', 'Staff'],
            User.Role.OFFICE_STAFF: ['Office_Staff', 'Staff'],
        }
        
        groups_to_add = group_mapping.get(user.role, [])
        
        for group_name in groups_to_add:
            group, created = Group.objects.get_or_create(name=group_name)
            if group not in user.groups.all():
                user.groups.add(group)
        
        if groups_to_add:
            logger.debug(f"Assigned {user.email} to groups: {groups_to_add}")
            
    except Exception as e:
        logger.error(f"Error assigning groups to user {user.email}: {e}")

def generate_user_identifiers(user):
    """Generate identifiers for user with proper error handling"""
    needs_save = False
    updates = {}
    
    try:
        # Generate admission number for students
        if user.role == User.Role.STUDENT and not user.admission_number:
            user.admission_number = generate_admission_number()
            updates['admission_number'] = user.admission_number
            needs_save = True
            logger.info(f"Generated admission number for student: {user.admission_number}")
        
        # Generate staff ID for staff roles
        elif user.role in [
            User.Role.TEACHER, User.Role.HEAD_TEACHER, User.Role.CURRICULUM_COORDINATOR,
            User.Role.ACCOUNTANT, User.Role.IT_SUPPORT, User.Role.COUNSELOR,
            User.Role.LIBRARIAN, User.Role.OFFICE_STAFF, User.Role.ADMIN
        ] and not user.staff_id:
            user.staff_id = generate_staff_id(user.role)
            updates['staff_id'] = user.staff_id
            needs_save = True
            logger.info(f"Generated staff ID for {user.role}: {user.staff_id}")
        
        # Save if any identifiers were generated
        if needs_save and updates:
            User.objects.filter(pk=user.pk).update(**updates)
            
    except Exception as e:
        logger.error(f"Error generating identifiers for {user.email}: {e}")
        # Try fallback method
        try:
            generate_identifiers_fallback(user)
        except Exception as fallback_error:
            logger.error(f"Fallback identifier generation also failed: {fallback_error}")

def generate_identifiers_fallback(user):
    """Fallback identifier generation using timestamp"""
    from datetime import datetime
    
    timestamp = int(datetime.now().timestamp() % 1000000)
    
    if user.role == User.Role.STUDENT and not user.admission_number:
        user.admission_number = f"DEL-STU-{timestamp:06d}"
        User.objects.filter(pk=user.pk).update(admission_number=user.admission_number)
        logger.warning(f"Used fallback admission number for {user.email}")
    
    elif user.role in User.get_staff_roles() and not user.staff_id:
        user.staff_id = f"DEL-EMP-{timestamp:06d}"
        User.objects.filter(pk=user.pk).update(staff_id=user.staff_id)
        logger.warning(f"Used fallback staff ID for {user.email}")

def send_email_async(user, subject, template_name, context, email_type="general"):
    """Send email asynchronously or queue it for later processing"""
    # Check if Celery is available
    try:
        from celery import shared_task
        
        @shared_task
        def send_email_task(user_id, subject, template_name, context, email_type):
            try:
                user = User.objects.get(id=user_id)
                _send_email_sync(user, subject, template_name, context, email_type)
            except User.DoesNotExist:
                logger.error(f"User {user_id} not found for email task")
        
        # Queue the email task
        send_email_task.delay(
            user.id, 
            subject, 
            template_name, 
            context, 
            email_type
        )
        logger.debug(f"Queued {email_type} email for {user.email}")
        
    except ImportError:
        # Fall back to synchronous sending
        logger.debug(f"Celery not available, sending email synchronously to {user.email}")
        _send_email_sync(user, subject, template_name, context, email_type)

def _send_email_sync(user, subject, template_name, context, email_type):
    """Synchronous email sending"""
    if not SignalConfig.EMAIL_ENABLED:
        logger.info(f"Email disabled, skipping {email_type} email for {user.email}")
        return
    
    if not can_send_email(user.id, email_type):
        return
    
    try:
        # Add common context variables
        context.update({
            'user': user,
            'school_name': SignalConfig.SCHOOL_NAME,
            'school_email': SignalConfig.SCHOOL_SUPPORT_EMAIL,
            'school_website': SignalConfig.SCHOOL_WEBSITE,
            'login_url': SignalConfig.LOGIN_URL,
            'support_email': SignalConfig.SCHOOL_SUPPORT_EMAIL,
            'support_phone': SignalConfig.SCHOOL_PHONE,
            'current_year': timezone.now().year,
        })
        
        # Render templates
        html_template = f'accounts/emails/{template_name}.html'
        text_template = f'accounts/emails/{template_name}.txt'
        
        try:
            html_message = render_to_string(html_template, context)
            plain_message = strip_tags(html_message)
        except Exception:
            # Try text template as fallback
            try:
                plain_message = render_to_string(text_template, context)
                html_message = None
            except Exception as e:
                logger.error(f"Email templates not found for {template_name}: {e}")
                plain_message = f"{subject}\n\nHello {user.first_name},\n\nPlease check your account."
                html_message = None
        
        # Send email
        from_email = settings.DEFAULT_FROM_EMAIL
        
        if html_message:
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=[user.email],
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
        else:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
        
        logger.info(f"Sent {email_type} email to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send {email_type} email to {user.email}: {e}")

def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = f"Welcome to {SignalConfig.SCHOOL_NAME}, {user.first_name}!"
    
    context = {
        'role_display': user.get_role_display(),
        'identifier': user.admission_number or user.staff_id,
        'dashboard_url': f"{SignalConfig.FRONTEND_URL}{user.get_dashboard_url()}",
        'profile_completion_url': f"{SignalConfig.FRONTEND_URL}/complete-profile",
    }
    
    send_email_async(
        user=user,
        subject=subject,
        template_name='welcome_email',
        context=context,
        email_type='welcome'
    )

def send_verification_email(user):
    """Send email verification email"""
    subject = f"Verify your email address - {SignalConfig.SCHOOL_NAME}"
    
    context = {
        'verification_url': f"{SignalConfig.FRONTEND_URL}/verify-email?token=TOKEN_PLACEHOLDER",
    }
    
    send_email_async(
        user=user,
        subject=subject,
        template_name='email_verification',
        context=context,
        email_type='verification'
    )

def handle_profile_completion(user):
    """Check and update profile completion status with caching"""
    cache_key = f"profile_completion_check_{user.id}"
    
    # Prevent checking too frequently
    if cache.get(cache_key):
        return
    
    try:
        completion_data = user.update_profile_completion_status()
        
        if completion_data.get('just_completed'):
            # Send profile completion notification
            send_profile_completion_notification(user, completion_data)
        
        # Set cache to prevent frequent checks (5 minutes)
        cache.set(cache_key, True, 300)
        
    except Exception as e:
        logger.error(f"Error checking profile completion for {user.email}: {e}")

def send_profile_completion_notification(user, completion_data):
    """Send notification when profile is completed"""
    if not user.profile_completed:
        return
    
    subject = f"Profile Complete - {SignalConfig.SCHOOL_NAME}"
    
    context = {
        'completion_percentage': completion_data.get('completion_percentage', 100),
        'dashboard_url': f"{SignalConfig.FRONTEND_URL}{user.get_dashboard_url()}",
    }
    
    send_email_async(
        user=user,
        subject=subject,
        template_name='profile_complete',
        context=context,
        email_type='profile_complete'
    )

def clear_user_cache(user):
    """Clear all cached data for a user"""
    cache_keys = [
        f"profile_completion_{user.id}",
        f"user_permissions_{user.id}",
        f"feature_flags_{user.id}",
        f"profile_completion_check_{user.id}",
        f"user_{user.id}_dashboard_data",
        f"user_{user.id}_permissions",
    ]
    
    redis_client = get_redis_client()
    if redis_client:
        # Clear Redis cache
        pipe = redis_client.pipeline()
        for key in cache_keys:
            pipe.delete(key)
        pipe.execute()
    else:
        # Clear Django cache
        for key in cache_keys:
            cache.delete(key)

def track_user_change(instance, field, old_value, new_value, change_type="update"):
    """Track user changes for audit logging"""
    if old_value == new_value:
        return
    
    # Create audit log entry
    try:
        from .models import AuditLog
        
        AuditLog.objects.create(
            user=instance,
            action_type=f"user_{change_type}",
            model_name='User',
            field_name=field,
            old_value=str(old_value)[:500] if old_value else None,
            new_value=str(new_value)[:500] if new_value else None,
            ip_address='system',
            user_agent='system-signal'
        )
        
        logger.info(f"User {instance.email} {field} changed from {old_value} to {new_value}")
        
    except ImportError:
        # AuditLog model not available
        logger.debug(f"User change: {instance.email} {field}: {old_value} -> {new_value}")

# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

@receiver(pre_save, sender=User, dispatch_uid="handle_user_pre_save")
def handle_user_pre_save(sender, instance, **kwargs):
    """
    Handle pre_save operations for User model.
    Generate identifiers before saving to avoid validation errors.
    """
    if kwargs.get('raw', False):  # Skip for fixture loading
        return
    
    # Check if we're creating a new user or updating an existing one
    is_new = instance._state.adding
    
    try:
        # Generate identifiers for new users or users missing them
        if is_new or not (instance.admission_number or instance.staff_id):
            generate_identifiers_before_save(instance)
        
        # Set academic year for students if not set
        if instance.role == User.Role.STUDENT and not instance.academic_year:
            current_year = timezone.now().year
            current_month = timezone.now().month
            
            # Academic year typically runs from September to August
            if current_month >= 9:  # September to December
                instance.academic_year = f"{current_year}-{current_year + 1}"
            else:  # January to August
                instance.academic_year = f"{current_year - 1}-{current_year}"
        
        # Set is_staff based on role for new users
        if is_new and not instance.is_staff:
            instance.is_staff = instance.role in User.get_staff_roles()
        
        # Track profile field changes
        if not is_new and instance.pk:
            try:
                original = User.objects.get(pk=instance.pk)
                for field in SignalConfig.PROFILE_FIELDS_TO_TRACK:
                    old_value = getattr(original, field, None)
                    new_value = getattr(instance, field, None)
                    if old_value != new_value:
                        track_user_change(instance, field, old_value, new_value)
            except User.DoesNotExist:
                pass  # User doesn't exist yet
            
    except Exception as e:
        logger.error(f"Error in user pre_save handler for {instance.email}: {e}")

def generate_identifiers_before_save(instance):
    """Generate identifiers before saving"""
    try:
        # Generate admission number for students
        if instance.role == User.Role.STUDENT and not instance.admission_number:
            instance.admission_number = generate_admission_number()
            logger.debug(f"Pre-save generated admission number: {instance.admission_number}")
        
        # Generate staff ID for staff roles
        elif instance.role in User.get_staff_roles() and not instance.staff_id:
            instance.staff_id = generate_staff_id(instance.role)
            logger.debug(f"Pre-save generated staff ID: {instance.staff_id}")
            
    except Exception as e:
        logger.error(f"Error generating identifiers before save for {instance.email if hasattr(instance, 'email') else 'unknown'}: {e}")

@receiver(post_save, sender=User, dispatch_uid="handle_user_post_save")
def handle_user_post_save(sender, instance, created, **kwargs):
    """
    Consolidated signal handler for User post_save events.
    Handles all related object creation and notifications in one place.
    """
    if kwargs.get('raw', False):  # Skip for fixture loading
        return
    
    try:
        if created:
            # Create related objects (profile, 2FA, etc.)
            create_related_objects(instance)
            
            # Generate identifiers if needed (as backup)
            generate_user_identifiers(instance)
            
            # Send welcome email (in background)
            if instance.email:
                send_welcome_email(instance)
            
            # Check profile completion
            handle_profile_completion(instance)
            
            logger.info(f"Successfully created user: {instance.email}")
            
        else:
            # For updates, check profile completion if relevant fields changed
            update_fields = kwargs.get('update_fields')
            
            if update_fields is None or isinstance(update_fields, (list, tuple, set)):
                # Convert to set for efficient checking
                updated_fields = set(update_fields) if update_fields else set()
                
                # Check if any profile-related fields were updated
                profile_fields = SignalConfig.PROFILE_FIELDS_TO_TRACK
                if not updated_fields or updated_fields.intersection(profile_fields):
                    handle_profile_completion(instance)
            
            # Clear user cache
            clear_user_cache(instance)
            
            # Check for significant status changes
            check_status_changes(instance, kwargs)
        
    except Exception as e:
        logger.error(f"Error in user post_save handler for {instance.email if hasattr(instance, 'email') else 'unknown'}: {e}")

def check_status_changes(instance, kwargs):
    """Check for significant status changes during updates"""
    if not instance.pk:
        return
    
    try:
        original = User.objects.get(pk=instance.pk)
        
        # Track suspension changes
        if original.is_suspended != instance.is_suspended:
            if instance.is_suspended:
                send_account_suspended_email(instance)
                logger.warning(f"Account suspended: {instance.email}")
            else:
                send_account_reactivated_email(instance)
                logger.info(f"Account reactivated: {instance.email}")
        
        # Track approval changes
        if original.is_approved != instance.is_approved:
            if instance.is_approved:
                send_account_approved_email(instance)
                logger.info(f"Account approved: {instance.email}")
        
        # Track verification changes
        if original.is_verified != instance.is_verified:
            if instance.is_verified:
                logger.info(f"Account verified: {instance.email}")
        
    except User.DoesNotExist:
        pass

def send_account_suspended_email(user):
    """Send account suspended notification"""
    subject = f"Account Suspended - {SignalConfig.SCHOOL_NAME}"
    
    context = {
        'suspension_reason': 'Violation of terms of service',  # You might want to make this dynamic
        'support_email': SignalConfig.SCHOOL_SUPPORT_EMAIL,
        'support_phone': SignalConfig.SCHOOL_PHONE,
    }
    
    send_email_async(
        user=user,
        subject=subject,
        template_name='account_suspended',
        context=context,
        email_type='account_suspended'
    )

def send_account_reactivated_email(user):
    """Send account reactivated notification"""
    subject = f"Account Reactivated - {SignalConfig.SCHOOL_NAME}"
    
    context = {
        'login_url': SignalConfig.LOGIN_URL,
        'dashboard_url': f"{SignalConfig.FRONTEND_URL}{user.get_dashboard_url()}",
    }
    
    send_email_async(
        user=user,
        subject=subject,
        template_name='account_reactivated',
        context=context,
        email_type='account_reactivated'
    )

def send_account_approved_email(user):
    """Send account approved notification"""
    subject = f"Account Approved - {SignalConfig.SCHOOL_NAME}"
    
    context = {
        'dashboard_url': f"{SignalConfig.FRONTEND_URL}{user.get_dashboard_url()}",
        'role_display': user.get_role_display(),
    }
    
    send_email_async(
        user=user,
        subject=subject,
        template_name='account_approved',
        context=context,
        email_type='account_approved'
    )

@receiver(pre_delete, sender=User, dispatch_uid="handle_user_pre_delete")
def handle_user_pre_delete(sender, instance, **kwargs):
    """Handle user deletion - archive data instead of actually deleting"""
    try:
        # Archive user data before deletion
        archive_user_data(instance)
        
        # Send deletion notification (optional)
        if settings.DEBUG:
            logger.info(f"Archiving data for user {instance.email} before deletion")
        
    except Exception as e:
        logger.error(f"Error in user pre_delete handler for {instance.email}: {e}")

def archive_user_data(user):
    """Archive user data before deletion (GDPR compliance)"""
    try:
        # Create an archive record
        from .models import UserArchive
        
        archive_data = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'created_at': user.created_at,
            'last_login': user.last_login,
            'profile_data': user.export_data(include_sensitive=True),
        }
        
        UserArchive.objects.create(
            original_user_id=user.id,
            email=user.email,
            archive_data=archive_data,
            archived_at=timezone.now(),
            archive_reason='account_deletion'
        )
        
        logger.info(f"Archived data for user {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to archive user data for {user.email}: {e}")

@receiver(post_save, sender=UserProfile, dispatch_uid="handle_user_profile_save")
def handle_user_profile_save(sender, instance, created, **kwargs):
    """Handle UserProfile save events"""
    if created:
        logger.info(f"UserProfile created for {instance.user.email}")
    else:
        # Update user's last_profile_update timestamp
        if instance.user:
            instance.user.last_profile_update = timezone.now()
            instance.user.save(update_fields=['last_profile_update'])
            logger.debug(f"Updated last_profile_update for {instance.user.email}")

@receiver(post_save, sender=TwoFactorAuth, dispatch_uid="handle_two_factor_auth_save")
def handle_two_factor_auth_save(sender, instance, created, **kwargs):
    """Handle TwoFactorAuth save events"""
    if created:
        logger.info(f"TwoFactorAuth created for {instance.user.email}")
    elif instance.is_enabled and not instance.backup_codes:
        # Generate backup codes when 2FA is enabled
        try:
            backup_codes = instance.generate_backup_codes()
            logger.info(f"Generated backup codes for {instance.user.email}")
        except Exception as e:
            logger.error(f"Failed to generate backup codes for {instance.user.email}: {e}")

@receiver(post_save, sender=OTPToken, dispatch_uid="handle_otp_token_creation")
def handle_otp_token_creation(sender, instance, created, **kwargs):
    """Handle OTP token creation events"""
    if created:
        logger.debug(f"OTP token created for {instance.user.email} - Type: {instance.token_type}")
        
        # Send email for certain token types
        if instance.token_type == OTPToken.TokenType.EMAIL_VERIFICATION:
            send_verification_email(instance.user)
        elif instance.token_type == OTPToken.TokenType.PASSWORD_RESET:
            send_password_reset_email(instance.user, instance)

def send_password_reset_email(user, otp_token):
    """Send password reset email"""
    subject = f"Password Reset Request - {SignalConfig.SCHOOL_NAME}"
    
    context = {
        'reset_url': f"{SignalConfig.FRONTEND_URL}/reset-password?token={otp_token.token}",
        'expiry_minutes': 30,
    }
    
    send_email_async(
        user=user,
        subject=subject,
        template_name='password_reset',
        context=context,
        email_type='password_reset'
    )

@receiver(post_save, sender=LoginHistory, dispatch_uid="handle_login_history")
def handle_login_history(sender, instance, created, **kwargs):
    """Handle login history events"""
    if created and instance.is_suspicious:
        handle_suspicious_login(instance)

def handle_suspicious_login(login_history):
    """Handle suspicious login attempts"""
    logger.warning(f"Suspicious login detected for {login_history.user.email} from {login_history.ip_address}")
    
    # Send alert to admins
    send_suspicious_login_alert(login_history)
    
    # Optionally lock the account or require additional verification
    if should_lock_account(login_history):
        lock_user_account(login_history.user)

def send_suspicious_login_alert(login_history):
    """Send alert about suspicious login attempt"""
    subject = f"Suspicious Login Alert - {SignalConfig.SCHOOL_NAME}"
    
    context = {
        'user_email': login_history.user.email,
        'ip_address': login_history.ip_address,
        'location': login_history.location,
        'device': login_history.device_type,
        'browser': login_history.browser,
        'time': login_history.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'admin_url': f"{SignalConfig.FRONTEND_URL}/admin/users/{login_history.user.id}",
    }
    
    # Send to admin email
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        admin_email = getattr(settings, 'ADMIN_ALERT_EMAIL', settings.ADMINS[0][1] if settings.ADMINS else SignalConfig.SCHOOL_SUPPORT_EMAIL)
        
        html_message = render_to_string('accounts/emails/suspicious_login_alert.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=True,
        )
        
    except Exception as e:
        logger.error(f"Failed to send suspicious login alert: {e}")

def should_lock_account(login_history):
    """Determine if account should be locked based on suspicious activity"""
    # Check for multiple suspicious logins in short time
    recent_suspicious = LoginHistory.objects.filter(
        user=login_history.user,
        is_suspicious=True,
        created_at__gte=timezone.now() - timedelta(hours=1)
    ).count()
    
    return recent_suspicious >= 3

def lock_user_account(user):
    """Lock user account due to suspicious activity"""
    user.is_suspended = True
    user.account_locked_until = timezone.now() + timedelta(hours=24)
    user.save(update_fields=['is_suspended', 'account_locked_until'])
    
    logger.warning(f"Locked account for {user.email} due to suspicious activity")
    send_account_suspended_email(user)

# ============================================================================
# GROUP AND PERMISSION SIGNALS
# ============================================================================

@receiver(m2m_changed, sender=User.groups.through)
def user_groups_changed(sender, instance, action, **kwargs):
    """Handle user group membership changes"""
    if action in ["post_add", "post_remove", "post_clear"]:
        logger.info(f"User {instance.email} groups changed")
        clear_user_cache(instance)

@receiver(m2m_changed, sender=User.user_permissions.through)
def user_permissions_changed(sender, instance, action, **kwargs):
    """Handle user permission changes"""
    if action in ["post_add", "post_remove", "post_clear"]:
        logger.info(f"User {instance.email} permissions changed")
        clear_user_cache(instance)

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_user_system():
    """Initialize user system components on startup"""
    try:
        # Create default admin user if it doesn't exist
        if not User.objects.filter(email=SignalConfig.DEFAULT_ADMIN_EMAIL).exists():
            with disable_signals():
                admin_user = User.objects.create_superuser(
                    email=SignalConfig.DEFAULT_ADMIN_EMAIL,
                    password=SignalConfig.DEFAULT_ADMIN_PASSWORD,
                    first_name='System',
                    last_name='Administrator',
                    role=User.Role.ADMIN,
                    is_verified=True,
                    is_approved=True,
                    is_active=True,
                )
                logger.info(f"Created default admin user: {SignalConfig.DEFAULT_ADMIN_EMAIL}")
        
        # Create default user groups
        create_default_groups()
        
        logger.info("User system initialization complete")
        
    except Exception as e:
        logger.error(f"Error during user system initialization: {e}")

def create_default_groups():
    """Create default user groups with permissions"""
    groups_to_create = {
        'Teachers': {
            'description': 'Teaching staff with access to student management',
            'default_permissions': [
                'can_view_students',
                'can_manage_grades',
                'can_manage_attendance',
                'can_view_courses',
            ]
        },
        'Students': {
            'description': 'Student users',
            'default_permissions': [
                'can_view_grades',
                'can_view_courses',
                'can_view_attendance',
                'can_view_profile',
            ]
        },
        'Parents': {
            'description': 'Parent/Guardian users',
            'default_permissions': [
                'can_view_children',
                'can_receive_notifications',
                'can_view_grades',
                'can_view_attendance',
            ]
        },
        'Administrators': {
            'description': 'System administrators',
            'default_permissions': [
                'can_manage_users',
                'can_view_reports',
                'can_manage_system',
                'can_view_analytics',
            ]
        },
        'Staff': {
            'description': 'All staff members',
            'default_permissions': [
                'can_view_directory',
                'can_receive_notifications',
            ]
        },
        'Curriculum_Team': {
            'description': 'Curriculum coordinators and developers',
            'default_permissions': [
                'can_manage_courses',
                'can_view_curriculum',
                'can_manage_lessons',
            ]
        },
        'Finance_Team': {
            'description': 'Finance and accounting staff',
            'default_permissions': [
                'can_manage_finance',
                'can_view_reports',
                'can_generate_invoices',
            ]
        },
        'IT_Team': {
            'description': 'IT support staff',
            'default_permissions': [
                'can_manage_system',
                'can_view_logs',
                'can_manage_tickets',
            ]
        },
        'Counselors': {
            'description': 'School counselors',
            'default_permissions': [
                'can_view_students',
                'can_manage_counseling',
                'can_view_psychometric',
            ]
        },
        'Library_Staff': {
            'description': 'Library management staff',
            'default_permissions': [
                'can_manage_library',
                'can_view_books',
                'can_manage_borrowing',
            ]
        },
        'Office_Staff': {
            'description': 'Administrative office staff',
            'default_permissions': [
                'can_manage_documents',
                'can_view_reports',
                'can_send_notifications',
            ]
        },
    }
    
    for group_name, group_info in groups_to_create.items():
        group, created = Group.objects.get_or_create(name=group_name)
        
        if created:
            # Set description if custom Group model supports it
            try:
                group.description = group_info['description']
                group.save()
            except AttributeError:
                pass
            
            logger.info(f"Created group: {group_name}")

# Initialize on module import
try:
    # Only initialize in production or when explicitly configured
    if getattr(settings, 'AUTO_INITIALIZE_USER_SYSTEM', True):
        initialize_user_system()
except Exception as e:
    logger.error(f"Failed to initialize user system: {e}")