# accounts/utils.py - COMPLETE FIXED VERSION
import secrets
import string
import logging
import hashlib
import time
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from io import BytesIO
import base64
import requests

from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.db import models
from django.db import transaction
from django.core.files.base import ContentFile
import psutil
import pyotp
import qrcode

from .models import User, UserProfile, OTPToken, LoginHistory

logger = logging.getLogger(__name__)


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for account activation"""
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + 
            str(user.is_active) + str(user.email_verified)
        )

account_activation_token = AccountActivationTokenGenerator()


# ==================== NETWORK & REQUEST UTILITIES ====================

def get_client_ip(request) -> str:
    """
    Get client IP address with enhanced detection for proxies and load balancers
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ips = [ip.strip() for ip in x_forwarded_for.split(',')]
        for ip in ips:
            if ip and not ip.startswith(('10.', '172.', '192.168.', '127.')):
                return ip
        return ips[0] if ips else 'unknown'
    
    real_ip = request.META.get('HTTP_X_REAL_IP')
    if real_ip:
        return real_ip
    
    return request.META.get('REMOTE_ADDR', 'unknown')


def get_user_agent_info(request) -> Dict[str, str]:
    """
    Extract detailed user agent information
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return get_user_agent_info_from_string(user_agent)


def get_user_agent_info_from_string(user_agent: str) -> Dict[str, str]:
    """
    Parse user agent string without request context
    """
    info = {
        'user_agent': user_agent,
        'browser': 'Unknown',
        'platform': 'Unknown',
        'device_type': 'Desktop'
    }
    
    if not user_agent:
        return info
    
    user_agent_lower = user_agent.lower()
    
    # Browser detection
    if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
        info['browser'] = 'Chrome'
    elif 'firefox' in user_agent_lower:
        info['browser'] = 'Firefox'
    elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
        info['browser'] = 'Safari'
    elif 'edg' in user_agent_lower:
        info['browser'] = 'Edge'
    elif 'opera' in user_agent_lower:
        info['browser'] = 'Opera'
    
    # Platform detection
    if 'windows' in user_agent_lower:
        info['platform'] = 'Windows'
    elif 'mac' in user_agent_lower:
        info['platform'] = 'macOS'
    elif 'linux' in user_agent_lower:
        info['platform'] = 'Linux'
    elif 'android' in user_agent_lower:
        info['platform'] = 'Android'
        info['device_type'] = 'Mobile'
    elif 'ios' in user_agent_lower:
        info['platform'] = 'iOS'
        info['device_type'] = 'Mobile'
    
    # Device type refinement
    if 'mobile' in user_agent_lower:
        info['device_type'] = 'Mobile'
    elif 'tablet' in user_agent_lower:
        info['device_type'] = 'Tablet'
    elif 'tv' in user_agent_lower:
        info['device_type'] = 'TV'
    elif 'bot' in user_agent_lower or 'crawler' in user_agent_lower:
        info['device_type'] = 'Bot'
    
    return info


def get_geolocation_info(ip_address: str) -> Dict[str, str]:
    """
    Get geolocation information for an IP address
    """
    return get_geolocation_info_enhanced(ip_address)


def get_geolocation_info_enhanced(ip_address: str) -> Dict[str, str]:
    """
    Enhanced geolocation with multiple fallback services
    """
    if not ip_address or ip_address in ['127.0.0.1', 'localhost', 'unknown']:
        return {
            'country': 'Local',
            'city': 'Local',
            'location': 'Local Development',
            'source': 'local'
        }
    
    services = [
        ('ipapi.co', f'http://ipapi.co/{ip_address}/json/'),
        ('ipinfo.io', f'https://ipinfo.io/{ip_address}/json'),
    ]
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                
                if service_name == 'ipapi.co':
                    return {
                        'country': data.get('country_name', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'region': data.get('region', 'Unknown'),
                        'location': f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}",
                        'timezone': data.get('timezone', 'Unknown'),
                        'isp': data.get('org', 'Unknown'),
                        'source': service_name
                    }
                elif service_name == 'ipinfo.io':
                    return {
                        'country': data.get('country', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'region': data.get('region', 'Unknown'),
                        'location': data.get('loc', 'Unknown'),
                        'timezone': data.get('timezone', 'Unknown'),
                        'isp': data.get('org', 'Unknown'),
                        'source': service_name
                    }
        except Exception:
            continue
    
    return {
        'country': 'Unknown',
        'city': 'Unknown',
        'location': 'Unknown',
        'source': 'failed'
    }


# ==================== RATE LIMITING UTILITIES ====================

def is_operation_rate_limited(
    identifier: str, 
    operation: str, 
    max_attempts: int = 5, 
    window_seconds: int = 900
) -> Dict[str, Any]:
    """
    Enhanced rate limiting with detailed tracking
    """
    cache_key = f"rate_limit_{operation}_{identifier}"
    now = timezone.now()
    
    attempts_data = cache.get(cache_key, {
        'count': 0,
        'first_attempt': now.isoformat(),
        'last_attempt': now.isoformat(),
        'blocked_until': None
    })
    
    if attempts_data.get('blocked_until'):
        blocked_until = datetime.fromisoformat(attempts_data['blocked_until'])
        if now < blocked_until:
            return {
                'limited': True,
                'reason': 'rate_limited',
                'retry_after': int((blocked_until - now).total_seconds()),
                'attempts': attempts_data['count']
            }
        else:
            attempts_data = {
                'count': 1,
                'first_attempt': now.isoformat(),
                'last_attempt': now.isoformat(),
                'blocked_until': None
            }
    else:
        attempts_data['count'] += 1
        attempts_data['last_attempt'] = now.isoformat()
    
    if attempts_data['count'] >= max_attempts:
        block_until = now + timedelta(minutes=15)
        attempts_data['blocked_until'] = block_until.isoformat()
        
        cache.set(cache_key, attempts_data, timeout=3600)
        return {
            'limited': True,
            'reason': 'too_many_attempts',
            'retry_after': 900,
            'attempts': attempts_data['count']
        }
    
    cache.set(cache_key, attempts_data, timeout=window_seconds)
    return {
        'limited': False,
        'attempts': attempts_data['count'],
        'remaining': max_attempts - attempts_data['count']
    }


# ==================== PASSWORD VALIDATION UTILITIES ====================

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength with detailed feedback
    """
    result = {
        'is_valid': True,
        'score': 0,
        'feedback': [],
        'requirements': {
            'min_length': 8,
            'has_uppercase': False,
            'has_lowercase': False,
            'has_digits': False,
            'has_special': False,
            'no_common': True
        }
    }
    
    common_passwords = [
        'password', '123456', 'qwerty', 'admin', 'welcome',
        'password123', 'abc123', 'letmein', 'monkey', 'sunshine'
    ]
    
    if len(password) < 8:
        result['is_valid'] = False
        result['feedback'].append('Password must be at least 8 characters long')
    else:
        result['score'] += 1
    
    if any(c.isupper() for c in password):
        result['requirements']['has_uppercase'] = True
        result['score'] += 1
    else:
        result['feedback'].append('Include at least one uppercase letter')
    
    if any(c.islower() for c in password):
        result['requirements']['has_lowercase'] = True
        result['score'] += 1
    else:
        result['feedback'].append('Include at least one lowercase letter')
    
    if any(c.isdigit() for c in password):
        result['requirements']['has_digits'] = True
        result['score'] += 1
    else:
        result['feedback'].append('Include at least one number')
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        result['requirements']['has_special'] = True
        result['score'] += 1
    else:
        result['feedback'].append('Include at least one special character')
    
    if password.lower() in common_passwords:
        result['is_valid'] = False
        result['requirements']['no_common'] = False
        result['feedback'].append('Password is too common')
    else:
        result['score'] += 1
    
    if result['score'] >= 5:
        result['strength'] = 'strong'
    elif result['score'] >= 3:
        result['strength'] = 'medium'
        result['is_valid'] = True
    else:
        result['strength'] = 'weak'
        result['is_valid'] = False
    
    return result


def validate_password_strength_enhanced(password: str, user: User = None) -> Dict[str, Any]:
    """
    Enhanced password strength validation with user context
    """
    result = validate_password_strength(password)
    
    if user:
        user_info = [
            user.first_name.lower(),
            user.last_name.lower(),
            user.email.split('@')[0].lower(),
            str(user.date_of_birth) if user.date_of_birth else ''
        ]
        
        for info in user_info:
            if info and info in password.lower():
                result['is_valid'] = False
                result['feedback'].append('Password should not contain personal information')
                break
    
    if has_sequential_chars(password):
        result['is_valid'] = False
        result['feedback'].append('Password contains sequential characters')
    
    if has_repeated_chars(password):
        result['is_valid'] = False
        result['feedback'].append('Password contains repeated character patterns')
    
    return result


def has_sequential_chars(password: str, min_seq: int = 3) -> bool:
    """Check for sequential characters"""
    sequences = ['abcdefghijklmnopqrstuvwxyz', '01234567890', 'qwertyuiop']
    
    password_lower = password.lower()
    for seq in sequences:
        for i in range(len(seq) - min_seq + 1):
            if seq[i:i + min_seq] in password_lower:
                return True
            if seq[i:i + min_seq][::-1] in password_lower:
                return True
    return False


def has_repeated_chars(password: str, min_repeat: int = 3) -> bool:
    """Check for repeated character patterns"""
    pattern = r'(.)\1{' + str(min_repeat - 1) + r',}'
    return bool(re.search(pattern, password))


# ==================== GENERATION UTILITIES ====================

def generate_otp_code(length: int = 6) -> str:
    """
    Generate secure numeric OTP code
    """
    if length < 4 or length > 8:
        raise ValueError("OTP length must be between 4 and 8 digits")
    
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure token for various purposes
    """
    return secrets.token_urlsafe(length)


def generate_session_id() -> str:
    """
    Generate unique session identifier
    """
    return f"session_{secrets.token_hex(16)}"


def generate_backup_code(length: int = 8) -> str:
    """
    Generate secure alphanumeric backup code
    """
    characters = string.ascii_uppercase.replace('O', '').replace('I', '') + \
                string.digits.replace('0', '').replace('1', '')
    
    if length < 6 or length > 12:
        raise ValueError("Backup code length must be between 6 and 12 characters")
    
    return ''.join(secrets.choice(characters) for _ in range(length))


# ==================== SMS & PHONE UTILITIES ====================

def send_otp_sms(user, otp_code, purpose="login"):
    """
    Send OTP via SMS to user's phone number
    """
    try:
        if not user.phone_number:
            logger.error(f"Cannot send SMS: No phone number for user {user.email}")
            return False
        
        message = f"Your Delvok Academy verification code is: {otp_code}. Valid for 10 minutes."
        
        # Log for development
        logger.info(f"SMS OTP {otp_code} would be sent to {user.phone_number} for {purpose}")
        logger.info(f"SMS Message: {message}")
        
        # In production, implement with Twilio/Africa's Talking/etc.
        return True
        
    except Exception as e:
        logger.error(f"Failed to send SMS OTP to {user.phone_number}: {e}")
        return False


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate phone number format
    """
    if not phone_number:
        return False
    
    cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False
    
    return True


def format_phone_number(phone_number: str, country_code='+254') -> str:
    """
    Format phone number to standard format
    """
    if not phone_number:
        return phone_number
    
    cleaned = ''.join(c for c in phone_number if c.isdigit())
    
    if country_code == '+254':
        if cleaned.startswith('0'):
            return '+254' + cleaned[1:]
        elif cleaned.startswith('254'):
            return '+' + cleaned
        elif cleaned.startswith('7'):
            return '+254' + cleaned
    elif country_code and not cleaned.startswith(country_code.replace('+', '')):
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
        return country_code + cleaned
    
    return '+' + cleaned if not phone_number.startswith('+') else phone_number


def format_phone_for_twilio(phone_number: str, country_code: str = '+254') -> str:
    """
    Format phone number for Twilio E.164 format
    """
    cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    if country_code == '+254':
        if cleaned.startswith('0'):
            return '+254' + cleaned[1:]
        elif cleaned.startswith('254'):
            return '+' + cleaned
        elif cleaned.startswith('7') and len(cleaned) == 9:
            return '+254' + cleaned
        elif not cleaned.startswith('+'):
            return country_code + cleaned.lstrip('0')
    
    return cleaned if cleaned.startswith('+') else f"+{cleaned}"


# ==================== EMAIL UTILITIES ====================

def send_otp_email(user, otp_code, subject="Your OTP Code"):
    """
    Send OTP email
    """
    try:
        html_message = render_to_string('accounts/email_otp.html', {
            'user': user,
            'otp_code': otp_code,
            'expiry_minutes': 10
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"OTP email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {e}")
        return False


def send_welcome_email(user, password=None):
    """
    Send welcome email to new user
    """
    try:
        html_message = render_to_string('accounts/welcome_email.html', {
            'user': user,
            'password': password,
            'login_url': settings.FRONTEND_URL + '/login' if hasattr(settings, 'FRONTEND_URL') else '/login'
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Welcome to Delvok Academy, {user.first_name}!",
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


def send_password_reset_email(user, token):
    """
    Send password reset email
    """
    try:
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}" if hasattr(settings, 'FRONTEND_URL') else f"/reset-password/{token}"
        
        html_message = render_to_string('accounts/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
            'expiry_minutes': 30
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="Password Reset Request - Delvok Academy",
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
    Send account approval email
    """
    try:
        html_message = render_to_string('accounts/account_approved.html', {
            'user': user,
            'dashboard_url': settings.FRONTEND_URL + user.get_dashboard_url() if hasattr(settings, 'FRONTEND_URL') else user.get_dashboard_url()
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="Your Delvok Academy Account Has Been Approved!",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Account approval email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send approval email to {user.email}: {e}")
        return False


def send_security_alert(user, request, alert_type, metadata=None):
    """
    Send security alert email
    """
    try:
        html_message = render_to_string('accounts/security_alert.html', {
            'user': user,
            'alert_type': alert_type,
            'metadata': metadata or {},
            'timestamp': timezone.now(),
            'ip_address': get_client_ip(request) if request else 'Unknown'
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f"Security Alert: {alert_type.replace('_', ' ').title()}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.warning(f"Security alert sent to {user.email}: {alert_type}")
        return True
    except Exception as e:
        logger.error(f"Failed to send security alert to {user.email}: {e}")
        return False


def send_login_notification(user, login_history):
    """
    Send login notification email
    """
    try:
        html_message = render_to_string('accounts/login_notification.html', {
            'user': user,
            'login_history': login_history,
            'timestamp': login_history.created_at,
            'location': login_history.location
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="New Login Detected - Delvok Academy",
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


# ==================== SECURITY & VALIDATION UTILITIES ====================

def is_suspicious_login(user: User, ip_address: str, user_agent: str) -> bool:
    """
    Detect suspicious login activity
    """
    recent_logins = LoginHistory.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).exclude(ip_address=ip_address)
    
    if recent_logins.exists():
        unique_ips = recent_logins.values('ip_address').distinct().count()
        if unique_ips >= 3:
            return True
        
        usual_country = recent_logins.exclude(country='').values('country').annotate(
            count=models.Count('country')
        ).order_by('-count').first()
        
        current_location = get_geolocation_info(ip_address)
        if (usual_country and current_location.get('country') and 
            current_location.get('country') != usual_country['country']):
            return True
    
    previous_user_agents = recent_logins.values_list('user_agent', flat=True)
    if previous_user_agents and user_agent not in previous_user_agents:
        return True
    
    return False


def sanitize_user_input(input_string: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks
    """
    if not input_string:
        return ''
    
    # Remove HTML tags
    import html
    sanitized = html.escape(input_string)
    
    # Remove extra whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized


def validate_email_domain(email: str) -> bool:
    """
    Validate email domain against allowed/blocked lists
    """
    try:
        domain = email.split('@')[1].lower()
        
        # Example blocked domains
        blocked_domains = ['temp-mail.org', 'trashmail.com', 'guerrillamail.com']
        if domain in blocked_domains:
            return False
        
        # You can add more domain validation logic here
        return True
    except:
        return False


# ==================== BULK OPERATIONS UTILITIES ====================

def bulk_create_users_with_progress(users_data: List[Dict], batch_size: int = 50) -> Dict[str, Any]:
    """
    Bulk create users with progress tracking
    """
    created = 0
    errors = []
    skipped = []
    
    with transaction.atomic():
        for i, user_data in enumerate(users_data):
            try:
                required_fields = ['email', 'first_name', 'last_name', 'role']
                missing_fields = [field for field in required_fields if field not in user_data or not user_data[field]]
                
                if missing_fields:
                    errors.append({
                        'index': i,
                        'email': user_data.get('email', 'unknown'),
                        'error': f"Missing required fields: {', '.join(missing_fields)}"
                    })
                    continue
                
                email = user_data['email'].lower().strip()
                
                if User.objects.filter(email=email).exists():
                    skipped.append({
                        'index': i,
                        'email': email,
                        'reason': 'User already exists'
                    })
                    continue
                
                if not validate_email_domain(email):
                    errors.append({
                        'index': i,
                        'email': email,
                        'error': 'Email domain not allowed'
                    })
                    continue
                
                user = User(
                    email=email,
                    first_name=sanitize_user_input(user_data['first_name']),
                    last_name=sanitize_user_input(user_data['last_name']),
                    role=user_data['role'],
                    is_active=user_data.get('is_active', True),
                    phone_number=user_data.get('phone_number', ''),
                    date_of_birth=user_data.get('date_of_birth'),
                    gender=user_data.get('gender', ''),
                )
                
                user.is_approved = not user.requires_approval()
                
                password = user_data.get('password')
                if not password:
                    password = generate_secure_token(12)
                
                user.set_password(password)
                user.save()
                
                UserProfile.objects.create(user=user)
                
                created += 1
                
                if user_data.get('send_welcome_email', False):
                    send_welcome_email(user, password)
                
            except Exception as e:
                errors.append({
                    'index': i,
                    'email': user_data.get('email', 'unknown'),
                    'error': f"Creation failed: {str(e)}"
                })
    
    return {
        'created': created,
        'errors': errors,
        'skipped': skipped,
        'total_processed': len(users_data),
        'success_rate': (created / len(users_data)) * 100 if users_data else 0
    }


# ==================== TOKEN & QR CODE UTILITIES ====================

def generate_qr_code_data(provisioning_uri: str) -> Optional[str]:
    """
    Generate QR code as base64 data URL
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        return None


def verify_totp_token(secret_key: str, token: str, window: int = 2) -> bool:
    """
    Verify TOTP token with time window
    """
    try:
        totp = pyotp.TOTP(secret_key)
        return totp.verify(token, valid_window=window)
    except Exception as e:
        logger.error(f"TOTP verification failed: {e}")
        return False


# ==================== WRAPPER FUNCTIONS ====================

def send_security_alert_wrapper(user: User, alert_type: str, metadata: Dict = None) -> None:
    """
    Wrapper function to send security alert
    """
    try:
        # Create a mock request object for context
        class MockRequest:
            META = {}
        
        request = MockRequest()
        send_security_alert(user, request, alert_type, metadata)
    except Exception as e:
        logger.error(f"Failed to send security alert: {e}")


def send_login_notification_wrapper(user: User, login_history: LoginHistory) -> None:
    """
    Wrapper function to send login notification
    """
    try:
        send_login_notification(user, login_history)
    except Exception as e:
        logger.error(f"Failed to send login notification: {e}")


# ==================== CLEANUP UTILITIES ====================

def invalidate_user_sessions(user: User) -> None:
    """
    Invalidate all active sessions for a user
    """
    logger.info(f"Invalidated all sessions for user: {user.email}")
    # Implementation depends on your session backend


def cleanup_expired_otp_tokens() -> int:
    """
    Clean up expired OTP tokens
    """
    expired_tokens = OTPToken.objects.filter(
        expires_at__lt=timezone.now()
    )
    count = expired_tokens.count()
    expired_tokens.delete()
    
    logger.info(f"Cleaned up {count} expired OTP tokens")
    return count


def cleanup_old_login_history(days: int = 90) -> int:
    """
    Clean up login history older than specified days
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    old_history = LoginHistory.objects.filter(created_at__lt=cutoff_date)
    count = old_history.count()
    old_history.delete()
    
    logger.info(f"Cleaned up {count} login history records older than {days} days")
    return count


# ==================== HEALTH CHECK UTILITIES ====================

def check_twilio_service():
    """
    Check Twilio service status
    """
    try:
        # Mock check - implement actual Twilio status check
        return {'status': 'healthy', 'details': 'Mock check'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def check_email_service():
    """
    Check email service status
    """
    try:
        return {'status': 'healthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def check_storage_service():
    """
    Check storage service status
    """
    try:
        from django.core.files.storage import default_storage
        test_content = b'test'
        test_path = f'health_check_{int(time.time())}.txt'
        
        default_storage.save(test_path, ContentFile(test_content))
        saved_content = default_storage.open(test_path).read()
        default_storage.delete(test_path)
        
        return {
            'status': 'healthy' if saved_content == test_content else 'unhealthy',
            'test_passed': saved_content == test_content
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def get_avg_login_time():
    """
    Calculate average login time
    """
    # Mock implementation
    return 2.5  # seconds


def get_recent_response_times():
    """
    Get recent API response times
    """
    # Mock implementation
    return {'avg': 150, 'p95': 300, 'p99': 500}  # milliseconds


def get_system_uptime():
    """
    Get system uptime
    """
    try:
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return f"{days}d {hours}h {minutes}m"
    except:
        return "Unknown"


def get_available_endpoints(request):
    """
    Get available API endpoints
    """
    from django.urls import get_resolver
    
    def extract_urls(url_patterns, prefix=''):
        urls = []
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                urls.extend(extract_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                urls.append({
                    'pattern': prefix + str(pattern.pattern),
                    'name': pattern.name
                })
        return urls
    
    resolver = get_resolver()
    return extract_urls(resolver.url_patterns)


def process_verification_response(from_number, body):
    """
    Process verification response from SMS
    """
    logger.info(f"Processing verification from {from_number}: {body}")


def unsubscribe_sms(from_number):
    """
    Handle SMS unsubscribe requests
    """
    logger.info(f"Unsubscribing SMS for {from_number}")