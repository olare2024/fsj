"""
administration/utils.py
Utility functions for administration models to avoid circular imports.
"""

from django.apps import apps
import logging

logger = logging.getLogger(__name__)

def get_user_count_by_role(role):
    """
    Safely get user count by role without circular import.
    
    Args:
        role (str): User role to count
    
    Returns:
        int: Count of users with the specified role
    """
    try:
        User = apps.get_model('accounts', 'User')
        return User.objects.filter(role=role, is_active=True).count()
    except LookupError:
        logger.warning(f"User model not found in accounts app")
        return 0
    except Exception as e:
        logger.error(f"Error counting users by role {role}: {e}")
        return 0

def get_student_count():
    """Get total active student count."""
    return get_user_count_by_role('student')

def get_staff_count():
    """Get total active staff count."""
    try:
        User = apps.get_model('accounts', 'User')
        return User.objects.filter(
            role__in=['teacher', 'admin', 'staff', 'accountant', 'supervisor'],
            is_active=True
        ).count()
    except (LookupError, AttributeError):
        return 0
    except Exception as e:
        logger.error(f"Error counting staff: {e}")
        return 0

def get_teacher_count():
    """Get total active teacher count."""
    return get_user_count_by_role('teacher')

def get_model_counts():
    """Get counts for various administration models."""
    try:
        from .models import Article, CarouselImage, AccessLog, School
        
        counts = {
            'articles': Article.objects.filter(is_active=True).count(),
            'carousel_images': CarouselImage.objects.filter(active=True, is_active=True).count(),
            'access_logs_today': AccessLog.objects.filter(
                timestamp__date=timezone.now().date()
            ).count(),
            'total_schools': School.objects.filter(is_active=True).count(),
            'active_school': School.objects.filter(active=True, is_active=True).count(),
        }
        
        return counts
    except Exception as e:
        logger.error(f"Error getting model counts: {e}")
        return {}