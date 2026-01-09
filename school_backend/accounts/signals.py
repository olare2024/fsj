# accounts/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import logging
from .models import User, UserProfile, TwoFactorAuth

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def handle_user_post_save(sender, instance, created, **kwargs):
    """
    Consolidated signal handler for User post_save events.
    Handles all related object creation and notifications in one place.
    """
    if kwargs.get('raw', False):  # Skip for fixture loading
        return
    
    if created:
        # Create UserProfile if it doesn't exist
        create_user_profile(instance)
        
        # Create TwoFactorAuth settings if they don't exist
        create_two_fa_settings(instance)
        
        # Generate identifiers if needed
        generate_user_identifiers(instance)
        
        # Send welcome email
        send_welcome_email(instance)
        
        logger.info(f"Successfully created related objects for new user: {instance.email}")

@receiver(pre_save, sender=User)
def handle_user_pre_save(sender, instance, **kwargs):
    """
    Handle pre_save operations for User model.
    Generate identifiers before saving to avoid validation errors.
    """
    if not instance.pk:  # New user being created
        generate_identifiers_before_save(instance)

def create_user_profile(user):
    """Create UserProfile if it doesn't exist"""
    try:
        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)
            logger.debug(f"Created UserProfile for {user.email}")
    except Exception as e:
        logger.error(f"Error creating UserProfile for {user.email}: {e}")

def create_two_fa_settings(user):
    """Create TwoFactorAuth settings if they don't exist"""
    try:
        if not TwoFactorAuth.objects.filter(user=user).exists():
            TwoFactorAuth.objects.create(user=user)
            logger.debug(f"Created TwoFactorAuth settings for {user.email}")
    except Exception as e:
        logger.error(f"Error creating TwoFactorAuth settings for {user.email}: {e}")

def generate_identifiers_before_save(user):
    """
    Generate admission number or staff ID before saving new user.
    This helps avoid validation errors in the clean method.
    """
    try:
        # Generate admission number for students
        if user.role == User.Role.STUDENT and not user.admission_number:
            user.admission_number = generate_admission_number()
            logger.debug(f"Generated admission number for student: {user.admission_number}")
        
        # Generate staff ID for staff roles
        elif user.role in [
            User.Role.TEACHER, User.Role.HEAD_TEACHER, User.Role.CURRICULUM_COORDINATOR,
            User.Role.ACCOUNTANT, User.Role.IT_SUPPORT, User.Role.COUNSELOR,
            User.Role.LIBRARIAN, User.Role.OFFICE_STAFF
        ] and not user.staff_id:
            user.staff_id = generate_staff_id(user.role)
            logger.debug(f"Generated staff ID for {user.role}: {user.staff_id}")
            
    except Exception as e:
        logger.error(f"Error generating identifiers for {user.email}: {e}")

def generate_user_identifiers(user):
    """
    Generate identifiers after user creation as a backup.
    This ensures identifiers are created even if pre_save fails.
    """
    try:
        needs_save = False
        
        # Generate admission number for students
        if user.role == User.Role.STUDENT and not user.admission_number:
            user.admission_number = generate_admission_number()
            needs_save = True
            logger.info(f"Generated admission number post-save: {user.admission_number}")
        
        # Generate staff ID for staff roles
        elif user.role in [
            User.Role.TEACHER, User.Role.HEAD_TEACHER, User.Role.CURRICULUM_COORDINATOR,
            User.Role.ACCOUNTANT, User.Role.IT_SUPPORT, User.Role.COUNSELOR,
            User.Role.LIBRARIAN, User.Role.OFFICE_STAFF
        ] and not user.staff_id:
            user.staff_id = generate_staff_id(user.role)
            needs_save = True
            logger.info(f"Generated staff ID post-save: {user.staff_id}")
        
        # Save if any identifiers were generated
        if needs_save:
            # Use update to avoid triggering signals again
            User.objects.filter(pk=user.pk).update(
                admission_number=user.admission_number,
                staff_id=user.staff_id
            )
            
    except Exception as e:
        logger.error(f"Error in post-save identifier generation for {user.email}: {e}")

def generate_admission_number():
    """Generate a unique admission number"""
    from .models import User
    year = timezone.now().year
    
    try:
        last_student = User.objects.filter(
            role=User.Role.STUDENT,
            admission_number__isnull=False
        ).order_by('-admission_number').first()
        
        new_number = 1
        if last_student and last_student.admission_number:
            try:
                # Extract number from format like "DEL-STU-2024-0001"
                last_number = int(last_student.admission_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                pass
        
        return f"DEL-STU-{year}-{new_number:04d}"
    except Exception as e:
        logger.error(f"Error generating admission number: {e}")
        return f"DEL-STU-{year}-0001"

def generate_staff_id(role):
    """Generate a unique staff ID based on role"""
    from .models import User
    year = timezone.now().year
    
    try:
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
        
        last_staff = User.objects.filter(
            role__in=[
                User.Role.TEACHER, User.Role.HEAD_TEACHER, User.Role.CURRICULUM_COORDINATOR,
                User.Role.ACCOUNTANT, User.Role.ADMIN, User.Role.IT_SUPPORT, 
                User.Role.COUNSELOR, User.Role.LIBRARIAN, User.Role.OFFICE_STAFF
            ],
            staff_id__isnull=False
        ).order_by('-staff_id').first()
        
        new_number = 1
        if last_staff and last_staff.staff_id:
            try:
                last_number = int(last_staff.staff_id.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                pass
        
        return f"DEL-{role_prefix}-{year}-{new_number:04d}"
    except Exception as e:
        logger.error(f"Error generating staff ID: {e}")
        return f"DEL-{role_prefix}-{year}-0001"

def send_welcome_email(user):
    """Send welcome email to new user"""
    if not user.email:
        return
        
    try:
        subject = f"Welcome to Delvok Academy, {user.first_name}!"
        
        # Create email context
        context = {
            'user': user,
            'school_name': 'Delvok Academy',
            'login_url': 'https://delvok.ac.ke/login',
            'support_email': 'support@delvok.ac.ke'
        }
        
        # Try to render HTML template
        try:
            html_message = render_to_string('accounts/emails/welcome_email.html', context)
            plain_message = strip_tags(html_message)
        except:
            # Fallback plain message if template doesn't exist
            plain_message = f"""
            Welcome to Delvok Academy, {user.first_name}!
            
            Your account has been successfully created.
            
            Login: https://delvok.ac.ke/login
            Email: {user.email}
            Role: {user.get_role_display()}
            
            If you have any questions, please contact support@delvok.ac.ke
            
            Best regards,
            Delvok Academy Team
            """
            html_message = None
        
        from_email = 'noreply@delvok.ac.ke'
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")

# Additional signal for profile updates
@receiver(pre_save, sender=UserProfile)
def handle_profile_update(sender, instance, **kwargs):
    """Handle UserProfile updates"""
    if instance.pk:  # Existing profile
        logger.debug(f"UserProfile updated for user: {instance.user.email}")

# Signal for important user changes
@receiver(pre_save, sender=User)
def track_user_changes(sender, instance, **kwargs):
    """Track important user changes for audit purposes"""
    if instance.pk:  # Existing user
        try:
            original = User.objects.get(pk=instance.pk)
            
            # Track role changes
            if original.role != instance.role:
                logger.info(f"User {instance.email} role changed from {original.role} to {instance.role}")
            
            # Track suspension changes
            if original.is_suspended != instance.is_suspended:
                action = "suspended" if instance.is_suspended else "unsuspended"
                logger.info(f"User {instance.email} {action}")
            
            # Track approval changes
            if original.is_approved != instance.is_approved:
                action = "approved" if instance.is_approved else "unapproved"
                logger.info(f"User {instance.email} {action}")
                
        except User.DoesNotExist:
            pass  # User doesn't exist yet (shouldn't happen)