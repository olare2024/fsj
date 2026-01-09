# school_backend/urls.py (Enhanced Version)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.decorators.cache import cache_page

# Schema views for different versions
schema_view_v1 = get_schema_view(
    openapi.Info(
        title="Delvok Academy API v1",
        default_version='v1',
        description="Delvok Academy School Management System API - Version 1",
        terms_of_service="https://delvok.ac.ke/terms/",
        contact=openapi.Contact(email="api@delvok.ac.ke"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path('api/v1/', include('finance.urls'))],  # Include main patterns
)

urlpatterns = [
    # ==================== ADMIN SECTION ====================
    path('admin/', admin.site.urls),
    
    # ==================== DOCUMENTATION ====================
    path('api-docs/v1/swagger.json', schema_view_v1.without_ui(cache_timeout=0), name='schema-json-v1'),
    path('api-docs/v1/swagger/', schema_view_v1.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-v1'),
    path('api-docs/v1/redoc/', schema_view_v1.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
    
    # ==================== PUBLIC APIs ====================
    path('api/public/v1/', include([
        path('school/', include('public.urls')),           # Public school info
        path('admissions/', include('admissions.urls')),   # Online applications
        path('fees/', include('public_fees.urls')),       # Public fee structure
        path('calendar/', include('public_calendar.urls')),# School calendar
    ])),
    
    # ==================== PRIVATE APIs (v1) ====================
    path('api/v1/', include([
        # Core modules
        path('auth/', include('accounts.urls')),
        path('finance/', include('finance.urls')),
        path('students/', include('students.urls')),
        path('teachers/', include('teachers.urls')),
        path('parents/', include('parents.urls')),
        path('academics/', include('academics.urls')),
        
        # Academic operations
        path('assignments/', include('assignments.urls')),
        path('attendance/', include('attendance.urls')),
        path('grading/', include('grading.urls')),
        path('examinations/', include('examinations.urls')),
        path('curriculum/', include('curriculum.urls')),
        path('timetable/', include('timetable.urls')),
        
        # Support services
        path('library/', include('library.urls')),
        path('hostel/', include('hostel.urls')),
        path('transport/', include('transport.urls')),
        path('health/', include('health.urls')),
        path('canteen/', include('canteen.urls')),
        
        # Communications
        path('communications/', include('communications.urls')),
        path('events/', include('events.urls')),
        path('notices/', include('notices.urls')),
        
        # Inventory & resources
        path('inventory/', include('inventory.urls')),
        path('resources/', include('resources.urls')),
        
        # Administration
        path('admin-panel/', include('admin_panel.urls')),
        path('reports/', include('reports.urls')),
        
        # Alumni
        path('alumni/', include('alumni.urls')),
    ])),
    
    # ==================== MOBILE APIs ====================
    path('api/mobile/v1/', include('mobile_api.urls')),
    
    # ==================== GATEWAY & UTILITIES ====================
    path('api/gateway/', include([
        path('webhooks/', include('webhooks.urls')),
        path('integrations/', include('integrations.urls')),
    ])),
    
    # ==================== MONITORING ====================
    path('monitoring/', include([
        path('health/', include('health_check.urls')),
        path('metrics/', include('metrics.urls')),
        path('status/', include('status.urls')),
    ])),
    
    # ==================== SECURITY ====================
    path('security/', include('security.urls')),
]

# ==================== DEVELOPMENT ONLY ====================
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
            path('api-auth/', include('rest_framework.urls')),  # DRF browsable API
            path('dev/', include('dev_tools.urls')),            # Development tools
        ] + urlpatterns
    except ImportError:
        pass
    
    # Serve media and static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ==================== ERROR HANDLERS ====================
handler404 = 'school_backend.views.handler404'
handler500 = 'school_backend.views.handler500'
handler403 = 'school_backend.views.handler403'
handler400 = 'school_backend.views.handler400'

# Custom admin site configuration
admin.site.site_header = "Delvok Academy Administration"
admin.site.site_title = "Delvok Academy Admin Portal"
admin.site.index_title = "Welcome to Delvok Academy Management System"