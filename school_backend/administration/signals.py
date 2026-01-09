"""
administration/signals.py
Signal handlers for Administration models.
"""

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import School, Day, Article
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=School)
def ensure_single_active_school(sender, instance, **kwargs):
    """Ensure only one school is active at a time."""
    if instance.active and instance.pk:
        School.objects.exclude(pk=instance.pk).update(active=False)
        logger.info(f"Deactivated other schools, activating: {instance.name}")


@receiver(post_save, sender=School)
def setup_default_school_config(sender, instance, created, **kwargs):
    """Setup default configuration when a school is created."""
    if created:
        from datetime import date
        
        # Create default days of the week
        DAY_CHOICES = [
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
            (6, "Saturday"),
            (7, "Sunday"),
        ]
        
        for day_num, day_name in DAY_CHOICES:
            Day.objects.get_or_create(
                day_number=day_num,
                defaults={
                    'short_name': day_name[:3],
                    'full_name': day_name,
                    'is_school_day': day_num <= 5,  # Monday to Friday
                    'is_instructional_day': day_num <= 5,
                    'day_type': 'weekend' if day_num in [6, 7] else 'school_day',
                }
            )
        
        logger.info(f"Default configuration created for school: {instance.name}")


@receiver(pre_save, sender=Article)
def handle_article_publishing(sender, instance, **kwargs):
    """Handle article publishing logic."""
    if instance.status == 'published' and not instance.published_at:
        instance.published_at = timezone.now()
        logger.info(f"Article '{instance.title}' published at {instance.published_at}")


@receiver(pre_save, sender=Day)
def validate_day_configuration(sender, instance, **kwargs):
    """Validate day configuration before saving."""
    try:
        instance.clean()
    except Exception as e:
        logger.error(f"Day validation error: {e}")
        raise


@receiver(post_save, sender=Article)
def log_article_activity(sender, instance, created, **kwargs):
    """Log article creation/update activity."""
    action = "created" if created else "updated"
    logger.info(f"Article '{instance.title}' {action} by {instance.updated_by or 'system'}")


@receiver(pre_delete, sender=School)
def prevent_active_school_deletion(sender, instance, **kwargs):
    """Prevent deletion of active school."""
    if instance.active:
        raise ValueError("Cannot delete active school. Deactivate it first.")