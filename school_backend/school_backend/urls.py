# school_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Delvok Academy API",
        default_version='v1',
        description="Delvok Academy School Management System API",
        terms_of_service="https://delvok.ac.ke/terms/",
        contact=openapi.Contact(email="api@delvok.ac.ke"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Routes - Version 1 (Consistent structure)
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/academics/', include('academics.urls')),
    path('api/v1/assignments/', include('assignments.urls')),
    path('api/v1/attendance/', include('attendance.urls')),
    path('api/v1/finance/', include('finance.urls')),
     path('api/v1/downloads/', include('downloads.urls')),
    path('api/v1/students/', include('students.urls')),
    path('api/v1/teachers/', include('teachers.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    
    path('api/v1/grading/', include('grading.urls')),
    path('api/v1/library/', include('library.urls')),
    path('api/v1/notes/', include('notes.urls')),
    path('api/v1/curriculum/', include('curriculum.urls')),
    path('api/v1/timetable/', include('timetable.urls')),
    path('api/v1/events/', include('events.urls')),
    path('api/v1/communications/', include('communications.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    
    # Admin Panel Routes
    path('api/v1/admin/', include('admin_panel.urls')),
    
    # Health check URLs
    path('health/', include('health_check.urls')),
]

# ==================== DEBUG TOOLBAR SETUP ====================
# Add Debug Toolbar URLs only in DEBUG mode
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site configuration
admin.site.site_header = "Delvok Academy Administration"
admin.site.site_title = "Delvok Academy Admin Portal"
admin.site.index_title = "Welcome to Delvok Academy Management System"