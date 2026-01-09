"""
administration/checks.py
System checks for Administration app.
"""

from django.core.checks import register, Tags, Warning, Error
from .models import School, Day


@register(Tags.models)
def check_school_configuration(app_configs, **kwargs):
    """Check school configuration."""
    errors = []
    
    # Check if there's exactly one active school
    active_schools = School.objects.filter(active=True, is_active=True).count()
    
    if active_schools == 0:
        errors.append(
            Warning(
                'No active school configured',
                hint='Set one school as active in the administration panel',
                obj=School,
                id='administration.W001',
            )
        )
    elif active_schools > 1:
        errors.append(
            Error(
                'Multiple active schools configured',
                hint='Only one school should be active at a time',
                obj=School,
                id='administration.E001',
            )
        )
    
    # Check if all days of the week are configured
    days_count = Day.objects.filter(is_active=True).count()
    if days_count != 7:
        errors.append(
            Warning(
                f'Incomplete days configuration ({days_count}/7 days)',
                hint='Ensure all 7 days of the week are configured',
                obj=Day,
                id='administration.W002',
            )
        )
    
    return errors


@register(Tags.security)
def check_security_configuration(app_configs, **kwargs):
    """Check security configuration."""
    errors = []
    
    # Check if access logging is properly configured
    from .models import AccessLog
    
    # Check for suspicious activity (more than 10 failed logins in last hour)
    from django.utils import timezone
    from datetime import timedelta
    
    one_hour_ago = timezone.now() - timedelta(hours=1)
    failed_logins = AccessLog.objects.filter(
        login_type='failed',
        timestamp__gte=one_hour_ago
    ).count()
    
    if failed_logins > 10:
        errors.append(
            Warning(
                f'High number of failed logins ({failed_logins} in last hour)',
                hint='Review security logs for potential brute force attacks',
                obj=AccessLog,
                id='administration.W003',
            )
        )
    
    return errors