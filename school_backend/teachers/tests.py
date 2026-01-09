from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import TeacherProfile, TeacherDocument


@receiver(post_save, sender=TeacherProfile)
def update_user_role(sender, instance, created, **kwargs):
    """
    Update user role when teacher profile is created or updated
    """
    if instance.teacher:
        # Update user staff_id from TSC number
        if not instance.teacher.staff_id and instance.tsc_number:
            instance.teacher.staff_id = instance.tsc_number
        
        # Set user role based on teacher designation
        if instance.is_principal:
            instance.teacher.role = 'head_teacher'
        elif instance.is_deputy_principal:
            instance.teacher.role = 'deputy_principal'
        elif instance.is_head_of_department:
            instance.teacher.role = 'curriculum_coordinator'
        else:
            instance.teacher.role = 'teacher'
        
        instance.teacher.save()


@receiver(pre_save, sender=TeacherDocument)
def check_document_expiry(sender, instance, **kwargs):
    """
    Automatically mark documents as expired
    """
    if instance.expiry_date and instance.expiry_date < timezone.now().date():
        instance.status = 'expired'


@receiver(post_save, sender=TeacherProfile)
def create_required_documents(sender, instance, created, **kwargs):
    """
    Create required document entries for new teachers
    """
    if created:
        required_docs = [
            ('tsc_certificate', 'TSC Certificate', True),
            ('good_conduct', 'Certificate of Good Conduct', True),
            ('academic_certificate', 'Academic Certificate', True),
            ('id_copy', 'National ID Copy', True),
        ]
        
        for doc_type, title, is_required in required_docs:
            TeacherDocument.objects.create(
                teacher=instance,
                document_type=doc_type,
                title=title,
                is_required=is_required,
                status='pending'
            )