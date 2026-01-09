# assignments/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Assignment, StudentAssignment
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_assignment_notifications():
    """
    Send notifications for upcoming assignment deadlines
    Runs daily via Celery beat
    """
    try:
        # Find assignments due in the next 3 days
        three_days_from_now = timezone.now() + timezone.timedelta(days=3)
        
        assignments = Assignment.objects.filter(
            due_date__lte=three_days_from_now,
            due_date__gte=timezone.now(),
            status__in=['published', 'in_progress']
        )
        
        for assignment in assignments:
            # Get students who haven't submitted
            not_submitted = StudentAssignment.objects.filter(
                assignment=assignment,
                status='not_started'
            ).select_related('student__user')
            
            for student_assignment in not_submitted:
                send_due_date_notification.delay(
                    student_assignment.student.user.email,
                    assignment.title,
                    assignment.due_date
                )
        
        logger.info(f"Sent notifications for {assignments.count()} assignments")
    except Exception as e:
        logger.error(f"Error sending assignment notifications: {str(e)}")

@shared_task
def send_due_date_notification(email, assignment_title, due_date):
    """
    Send due date notification to student
    """
    try:
        subject = f"Assignment Reminder: {assignment_title}"
        message = f"""
        Dear Student,
        
        This is a reminder that your assignment "{assignment_title}" 
        is due on {due_date.strftime('%B %d, %Y at %I:%M %p')}.
        
        Please ensure you submit your assignment before the deadline.
        
        Best regards,
        Academic Team
        """
        
        send_mail(
            subject,
            message,
            'noreply@school.edu',
            [email],
            fail_silently=False,
        )
        
        logger.info(f"Sent due date notification to {email}")
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")

@shared_task
def calculate_assignment_analytics(assignment_id):
    """
    Calculate analytics for an assignment in the background
    """
    try:
        from .models import AssignmentAnalytics
        
        assignment = Assignment.objects.get(id=assignment_id)
        analytics, created = AssignmentAnalytics.objects.get_or_create(
            assignment=assignment
        )
        
        analytics.update_analytics()
        logger.info(f"Calculated analytics for assignment {assignment_id}")
    except Exception as e:
        logger.error(f"Error calculating analytics: {str(e)}")