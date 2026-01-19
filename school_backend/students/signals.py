from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from students.models import StudentEnrollment
from academics.models import Classroom  # or AcademicClass, if you renamed it


@receiver([post_save, post_delete], sender=StudentEnrollment)
def update_class_strength(sender, instance, **kwargs):
    """
    Update class current strength whenever a student enrollment
    is created, updated, or deleted.
    """
    enrolled_class = instance.class_enrolled
    if enrolled_class:
        active_count = StudentEnrollment.objects.filter(
            class_enrolled=enrolled_class,
            status='active'
        ).count()

        # Update current_strength field
        enrolled_class.current_strength = active_count
        enrolled_class.save(update_fields=['current_strength'])
