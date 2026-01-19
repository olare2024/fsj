from pathlib import Path
from datetime import timedelta
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add apps directory to Python path
sys.path.append(os.path.join(BASE_DIR, 'apps'))

# ==================== CORE SETTINGS ====================
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ==================== APPLICATION DEFINITION ====================
INSTALLED_APPS = [
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    'drf_yasg',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'debug_toolbar',
    'import_export',
    'dirtyfields',
    'django_object_actions',
    
    # Local apps
    'admin_panel',
    'accounts.apps.AccountsConfig',
    'academics',
    'students',
    'teachers',
    'attendance',
    'grading',
    'curriculum',
    'timetable',
    "notes",
    'library',
    "analytics",
    'events',
    'communications',
    'finance',
    'administration',
    'sis',
    'assignments',
    'notifications',
    'examination',
    'downloads',
    'blog',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'school_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'school_backend.wsgi.application'

# ==================== DATABASE CONFIGURATION ====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', default_storage_engine=INNODB, character_set_connection=utf8mb4",
            'charset': 'utf8mb4',
            'use_unicode': True,
            'isolation_level': 'read committed',
        },
        'CONN_MAX_AGE': 300,
        'CONN_HEALTH_CHECKS': True,
        'TEST': {
            'NAME': 'test_delvok_academy',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# ==================== AUTHENTICATION & SECURITY ====================
AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ==================== INTERNATIONALIZATION ====================
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==================== STATIC & MEDIA FILES ====================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== REST FRAMEWORK CONFIGURATION ====================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'UNAUTHENTICATED_USER': None,
}

# ==================== JWT SETTINGS ====================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# OTP Configuration
OTP_VALIDITY_SECONDS = 300  # 5 minutes
OTP_LOGIN_REQUIRED_FOR_ALL = True  # Require OTP for all users
OTP_BYPASS_ROLES = ['admin']  # Roles that can bypass OTP (optional)

# 2FA Configuration
TWO_FACTOR_AUTH_METHODS = {
    'authenticator': True,
    'email': True,
    'sms': True,
}

# Security settings
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 1800  # 30 minutes

# ==================== CORS & SECURITY ====================
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with', 'x-request-id',
]

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7

# ==================== EMAIL CONFIGURATION ====================
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
EMAIL_TIMEOUT = 30

# ==================== SCHOOL INFORMATION ====================
SCHOOL_NAME = os.getenv('SCHOOL_NAME', 'Delvok Academy')
SCHOOL_MOTTO = os.getenv('SCHOOL_MOTTO', 'Excellence in Education')
SCHOOL_LOCATION = os.getenv('SCHOOL_LOCATION', 'Kenya')
SCHOOL_PHONE = os.getenv('SCHOOL_PHONE', '+254-700-000-000')
SCHOOL_EMAIL = os.getenv('SCHOOL_EMAIL', 'info@delvok.ac.ke')
SCHOOL_WEBSITE = os.getenv('SCHOOL_WEBSITE', 'https://delvok.ac.ke')
SCHOOL_SUPPORT_EMAIL = os.getenv('SCHOOL_SUPPORT_EMAIL', 'delvokacademy@gmail.com')

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5177')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# ==================== SECURITY SETTINGS ====================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==================== SESSION & CACHE CONFIGURATION ====================
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_NAME = 'delvok_sessionid'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = 'Lax'


REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Make sure we're using the right database (0 or 1)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,  
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 5,  # seconds
            "SOCKET_TIMEOUT": 5,  # seconds
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True
            },
        },
        "KEY_PREFIX": "delvok",
        "TIMEOUT": 600,  # 5 minutes default
    }
}

# Also add SESSION_CACHE_ALIAS
SESSION_CACHE_ALIAS = "default"


# ==================== 2FA SECURITY SETTINGS ====================
REQUIRE_2FA_FOR_STAFF = os.getenv('REQUIRE_2FA_FOR_STAFF', 'True').lower() == 'true'
REQUIRE_2FA_FOR_STUDENTS = os.getenv('REQUIRE_2FA_FOR_STUDENTS', 'False').lower() == 'true'
REQUIRE_2FA_FOR_PARENTS = os.getenv('REQUIRE_2FA_FOR_PARENTS', 'True').lower() == 'true'

OTP_VALIDITY_MINUTES = 10
OTP_LENGTH = 6
MAX_OTP_ATTEMPTS = 3

LOGIN_ATTEMPT_LIMIT = 5
LOGIN_TIMEOUT_MINUTES = 15
ACCOUNT_LOCKOUT_DURATION = 30

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_COMPLEXITY = {
    'UPPER': 1,
    'LOWER': 1,
    'DIGITS': 1,
    'SPECIAL': 1,
}

# ==================== TWILIO CONFIGURATION ====================
TWILIO_ENABLED = os.getenv('TWILIO_ENABLED', 'True').lower() == 'true'
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_VERIFY_SERVICE_SID = os.getenv('TWILIO_VERIFY_SERVICE_SID', '')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+15005550006')

# ==================== DEBUG TOOLBAR ====================
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: (
            request.META.get('REMOTE_ADDR') in INTERNAL_IPS and
            not request.path.startswith('/admin/') and
            not request.path.startswith('/api/') and
            not request.path.startswith('/swagger/') and
            not request.path.startswith('/redoc/')
        ),
        'DISABLE_PANELS': {
            'debug_toolbar.panels.redirects.RedirectsPanel',
        },
        'RESULTS_CACHE_SIZE': 10,
        'SHOW_COLLAPSED': True,
        'RENDER_PANELS': False,
    }
    
    INTERNAL_IPS = ['127.0.0.1', 'localhost', '::1']

# ==================== LOGGING CONFIGURATION ====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'security': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'delvok_academy.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'security',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file', 'security_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==================== CUSTOM SCHOOL SETTINGS ====================
DELVOK_SETTINGS = {
    'SCHOOL_NAME': SCHOOL_NAME,
    'SCHOOL_MOTTO': SCHOOL_MOTTO,
    'SCHOOL_EMAIL': SCHOOL_EMAIL,
    'SCHOOL_SUPPORT_EMAIL': SCHOOL_SUPPORT_EMAIL,
    'CURRICULA': ['cbc', 'icse', 'american'],
    'GRADE_LEVELS': {
        'pre_primary': ['PP1', 'PP2'],
        'primary': ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6'],
        'junior_secondary': ['Grade 7', 'Grade 8', 'Grade 9'],
        'senior_secondary': ['Grade 10', 'Grade 11', 'Grade 12'],
    },
    'HOUSES': ['unity', 'courage', 'wisdom', 'success'],
    'ACADEMIC_TERMS': ['Term 1', 'Term 2', 'Term 3'],
    'MAX_STUDENTS_PER_CLASS': 35,
    'SCHOOL_HOURS': {
        'start': '08:00',
        'end': '16:00',
    },
    'SECURITY': {
        'REQUIRE_2FA_FOR_STAFF': REQUIRE_2FA_FOR_STAFF,
        'REQUIRE_2FA_FOR_STUDENTS': REQUIRE_2FA_FOR_STUDENTS,
        'REQUIRE_2FA_FOR_PARENTS': REQUIRE_2FA_FOR_PARENTS,
        'LOGIN_ATTEMPT_LIMIT': LOGIN_ATTEMPT_LIMIT,
        'ACCOUNT_LOCKOUT_DURATION': ACCOUNT_LOCKOUT_DURATION,
    }
}

APP_VERSION = '1.0.0'

# Create required directories
for dir_name in ['static', 'media', 'logs', 'templates/emails']:
    os.makedirs(BASE_DIR / dir_name, exist_ok=True)