# accounts/email_utils.py
import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_otp_email(user, otp_code, subject=None, purpose="login"):
    """
    Send OTP email to user for various purposes
    """
    try:
        if subject is None:
            subject = f"Your OTP Code - Delvok Academy"
        
        context = {
            'user': user,
            'otp_code': otp_code,
            'purpose': purpose,
            'timestamp': timezone.now(),
            'expiry_minutes': 10,
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke'
        }
        
        html_message = render_to_string('emails/otp_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"OTP email sent to {user.email} for {purpose}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {e}")
        return False


def send_welcome_email(user, temp_password=None):
    """
    Send welcome email to new users
    """
    try:
        subject = "Welcome to Delvok Academy!"
        
        context = {
            'user': user,
            'temp_password': temp_password,
            'login_url': f"{settings.FRONTEND_URL}/login",
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'timestamp': timezone.now()
        }
        
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        return False


def send_password_reset_email(user, reset_token):
    """
    Send password reset email with token
    """
    try:
        subject = "Password Reset Request - Delvok Academy"
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'reset_token': reset_token,
            'expiry_minutes': 30,
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'timestamp': timezone.now()
        }
        
        html_message = render_to_string('emails/password_reset_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False


def send_account_approved_email(user):
    """
    Send account approval notification email
    """
    try:
        subject = "Account Approved - Welcome to Delvok Academy!"
        
        context = {
            'user': user,
            'login_url': f"{settings.FRONTEND_URL}/login",
            'dashboard_url': user.get_dashboard_url(),
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'timestamp': timezone.now()
        }
        
        html_message = render_to_string('emails/account_approved_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Account approval email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send account approval email to {user.email}: {e}")
        return False


def send_security_alert(user, login_history=None, alert_type=None, metadata=None):
    """
    Send security alert email for important account activities
    """
    try:
        alert_subjects = {
            'password_changed': 'Password Changed - Security Alert',
            '2fa_enabled': 'Two-Factor Authentication Enabled',
            '2fa_disabled': 'Two-Factor Authentication Disabled',
            'email_changed': 'Email Address Changed - Security Alert',
            'suspicious_login': 'Suspicious Login Detected',
            'password_reset': 'Password Reset Completed',
            'account_approved': 'Account Approved',
            'account_suspended': 'Account Suspended',
            'account_activated': 'Account Activated',
            'account_deactivated': 'Account Deactivated'
        }
        
        subject = alert_subjects.get(alert_type, "Security Alert - Delvok Academy")
        subject = f"{subject} - Delvok Academy"
        
        context = {
            'user': user,
            'alert_type': alert_type,
            'login_history': login_history,
            'metadata': metadata or {},
            'timestamp': timezone.now(),
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'contact_email': 'security@delvok.ac.ke'
        }
        
        html_message = render_to_string('emails/security_alert.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Security alert ({alert_type}) sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send security alert to {user.email}: {e}")
        return False


def send_login_notification(user, login_history):
    """
    Send login notification email with device and location details
    """
    try:
        subject = "New Login Detected - Delvok Academy"
        
        context = {
            'user': user,
            'login_history': login_history,
            'timestamp': timezone.now(),
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'security_email': 'security@delvok.ac.ke'
        }
        
        template = 'emails/suspicious_login_alert.html' if login_history.is_suspicious else 'emails/new_login_notification.html'
        
        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Login notification sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send login notification to {user.email}: {e}")
        return False


def send_bulk_welcome_email(users_data):
    """
    Send welcome emails in bulk
    """
    try:
        successful_sends = 0
        failed_sends = []
        
        for user_data in users_data:
            try:
                # This would need to be adapted based on your user data structure
                # For now, it's a placeholder for bulk email functionality
                send_welcome_email(user_data['user'])
                successful_sends += 1
            except Exception as e:
                failed_sends.append({
                    'user': user_data.get('email', 'Unknown'),
                    'error': str(e)
                })
        
        logger.info(f"Bulk welcome emails: {successful_sends} successful, {len(failed_sends)} failed")
        return {
            'successful': successful_sends,
            'failed': failed_sends
        }
        
    except Exception as e:
        logger.error(f"Bulk welcome email sending failed: {e}")
        return {
            'successful': 0,
            'failed': [{'error': str(e)}]
        }


def send_system_notification(users, subject, message, html_message=None):
    """
    Send system notification to multiple users
    """
    try:
        recipient_list = [user.email for user in users if user.email]
        
        if not recipient_list:
            logger.warning("No valid email addresses for system notification")
            return False
        
        if html_message is None:
            html_message = render_to_string('emails/system_notification.html', {
                'message': message,
                'academy_name': 'Delvok Academy',
                'timestamp': timezone.now()
            })
        
        plain_message = strip_tags(html_message) if html_message else message
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"System notification sent to {len(recipient_list)} users: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send system notification: {e}")
        return False


def send_phone_verification_sms(user, otp_code):
    """
    Send OTP via SMS for phone verification
    Note: This is a placeholder - implement with your SMS provider
    """
    try:
        # Placeholder for SMS integration
        # You would integrate with services like:
        # - Twilio
        # - Africa's Talking
        # - Amazon SNS
        # - Other SMS gateways
        
        logger.info(f"SMS OTP {otp_code} would be sent to {user.phone_number}")
        
        # Example implementation (commented out):
        """
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=f"Your Delvok Academy verification code is: {otp_code}. Valid for 10 minutes.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )
        """
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send SMS OTP to {user.phone_number}: {e}")
        return False


def send_parent_invitation_email(parent_email, student_name, invitation_token):
    """
    Send parent invitation email to link parent account with student
    """
    try:
        subject = f"Parent Portal Invitation - {student_name} - Delvok Academy"
        
        invitation_url = f"{settings.FRONTEND_URL}/parent-signup?token={invitation_token}"
        
        context = {
            'student_name': student_name,
            'invitation_url': invitation_url,
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'timestamp': timezone.now()
        }
        
        html_message = render_to_string('emails/parent_invitation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[parent_email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Parent invitation sent to {parent_email} for student {student_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send parent invitation to {parent_email}: {e}")
        return False


def send_staff_credentials_email(user, temp_password):
    """
    Send staff credentials email for new staff members
    """
    try:
        subject = "Your Staff Account Credentials - Delvok Academy"
        
        context = {
            'user': user,
            'temp_password': temp_password,
            'login_url': f"{settings.FRONTEND_URL}/login",
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'timestamp': timezone.now()
        }
        
        html_message = render_to_string('emails/staff_credentials.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Staff credentials email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send staff credentials to {user.email}: {e}")
        return False


def send_weekly_digest_email(user, digest_data):
    """
    Send weekly digest email with user activity summary
    """
    try:
        subject = "Your Weekly Activity Digest - Delvok Academy"
        
        context = {
            'user': user,
            'digest_data': digest_data,
            'academy_name': 'Delvok Academy',
            'support_email': 'support@delvok.ac.ke',
            'timestamp': timezone.now()
        }
        
        html_message = render_to_string('emails/weekly_digest.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Weekly digest email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send weekly digest to {user.email}: {e}")
        return False


# Email template rendering helper functions
def render_email_template(template_name, context):
    """
    Helper function to render email templates
    """
    try:
        html_content = render_to_string(f'emails/{template_name}', context)
        plain_content = strip_tags(html_content)
        return html_content, plain_content
    except Exception as e:
        logger.error(f"Failed to render email template {template_name}: {e}")
        return None, None


def validate_email_address(email):
    """
    Basic email validation
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None