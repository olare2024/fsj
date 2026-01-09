# school_backend/context_processors.py
from django.conf import settings

def school_info(request):
    return {
        'SCHOOL_NAME': settings.SCHOOL_NAME,
        'SCHOOL_MOTTO': settings.SCHOOL_MOTTO,
        'SCHOOL_EMAIL': settings.SCHOOL_EMAIL,
        'SCHOOL_PHONE': settings.SCHOOL_PHONE,
        'SCHOOL_WEBSITE': settings.SCHOOL_WEBSITE,
        'APP_VERSION': settings.APP_VERSION,
    }

def app_version(request):
    return {
        'APP_VERSION': settings.APP_VERSION,
    }