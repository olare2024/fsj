# teachers/signals.py 
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import TeacherProfile, TeacherLeave  
from accounts.models import User

@receiver(post_save, sender=TeacherProfile)
def generate_teacher_id(sender, instance, created, **kwargs):
    """
    Generate teacher ID if not provided
    """
    # Your TeacherProfile model uses tsc_number, not teacher_id
    # Remove or modify this signal if not needed
    pass
    # if created and not instance.tsc_number:  # Assuming tsc_number is your ID
    #     from .models import generate_tsc_number
    #     instance.tsc_number = generate_tsc_number()
    #     instance.save(update_fields=['tsc_number'])

@receiver(post_save, sender=TeacherLeave)  # <-- Changed from TeacherLeaveApplication
def notify_leave_application(sender, instance, created, **kwargs):
    """
    Send notifications for leave applications
    """
    if created:
        # Notify head teacher or admin
        subject = f"New Leave Application - {instance.teacher.full_name}"  # <-- Changed
        message = f"""
        A new leave application has been submitted:
        
        Teacher: {instance.teacher.full_name}  # <-- Changed
        Leave Type: {instance.get_leave_type_display()}
        Period: {instance.start_date} to {instance.end_date}
        Reason: {instance.reason}
        
        Please review the application in the system.
        """
        
        # This would send to appropriate administrators
        # send_mail(subject, message, 'noreply@delvok.ac.ke', ['admin@delvok.ac.ke'])
        print(f"Leave application notification: {subject}")  # For debugging

@receiver(pre_save, sender=TeacherProfile)
def update_class_teacher_status(sender, instance, **kwargs):
    """
    Update class teacher status based on assignment
    """
    # Your TeacherProfile model has is_class_teacher field
    # Check if teacher has any classes assigned
    if hasattr(instance, 'classes') and instance.classes.exists():
        instance.is_class_teacher = True
    else:
        instance.is_class_teacher = False

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
            instance.teacher.role = User.Role.HEAD_TEACHER
        elif instance.is_deputy_principal or instance.is_head_of_department:
            instance.teacher.role = User.Role.CURRICULUM_COORDINATOR
        else:
            instance.teacher.role = User.Role.TEACHER
        
        instance.teacher.save()