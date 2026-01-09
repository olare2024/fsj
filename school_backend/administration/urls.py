"""
administration/urls.py
URL configurations for Delvok Academy Administration API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# ==================== ROUTER SETUP ====================

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'carousel', views.CarouselImageViewSet, basename='carousel')
router.register(r'access-logs', views.AccessLogViewSet, basename='access-log')
router.register(r'schools', views.SchoolViewSet, basename='school')
router.register(r'days', views.DayViewSet, basename='day')

# ==================== URL PATTERNS ====================

urlpatterns = [
    # API Routes
    path('api/', include(router.urls)),
    
    # Dashboard
    path('api/dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/dashboard/activity/', views.RecentActivityView.as_view(), name='recent-activity'),
    
    # Public endpoints (no authentication required)
    path('api/public/articles/', views.PublicArticlesView.as_view(), name='public-articles'),
    path('api/public/carousel/', views.PublicCarouselView.as_view(), name='public-carousel'),
    path('api/public/school/contact/', views.SchoolContactView.as_view(), name='school-contact'),
    
    # Helper endpoints
    path('api/check-permissions/', views.check_permissions, name='check-permissions'),
    path('api/create-access-log/', views.create_access_log, name='create-access-log'),
    
    # API documentation
    path('api/docs/', include('rest_framework.urls', namespace='rest_framework')),
]


# ==================== API DOCUMENTATION ====================

api_documentation = {
    'title': 'Delvok Academy Administration API',
    'description': """
    # Administration API Documentation
    
    This API provides endpoints for managing Delvok Academy's administrative functions.
    
    ## Authentication
    
    Most endpoints require authentication. Use JWT tokens or session authentication.
    
    ## Endpoints
    
    ### Articles
    - `GET /api/articles/` - List articles
    - `POST /api/articles/` - Create article
    - `GET /api/articles/{id}/` - Retrieve article
    - `PUT /api/articles/{id}/` - Update article
    - `DELETE /api/articles/{id}/` - Delete article
    - `POST /api/articles/{id}/publish/` - Publish article
    - `POST /api/articles/{id}/archive/` - Archive article
    - `POST /api/articles/{id}/feature/` - Feature article
    - `POST /api/articles/bulk_update/` - Bulk update articles
    
    ### Carousel Images
    - `GET /api/carousel/` - List carousel images
    - `POST /api/carousel/` - Create carousel image
    - `GET /api/carousel/{id}/` - Retrieve carousel image
    - `PUT /api/carousel/{id}/` - Update carousel image
    - `DELETE /api/carousel/{id}/` - Delete carousel image
    - `POST /api/carousel/{id}/activate/` - Activate carousel image
    - `POST /api/carousel/{id}/deactivate/` - Deactivate carousel image
    - `GET /api/carousel/active_for_position/` - Get active images by position
    
    ### Access Logs
    - `GET /api/access-logs/` - List access logs
    - `GET /api/access-logs/{id}/` - Retrieve access log
    - `GET /api/access-logs/security_summary/` - Get security summary
    - `GET /api/access-logs/today_summary/` - Get today's summary
    - `POST /api/access-logs/{id}/flag_suspicious/` - Flag as suspicious
    - `POST /api/access-logs/{id}/flag_normal/` - Flag as normal
    
    ### Schools
    - `GET /api/schools/` - List schools
    - `POST /api/schools/` - Create school
    - `GET /api/schools/{id}/` - Retrieve school
    - `PUT /api/schools/{id}/` - Update school
    - `DELETE /api/schools/{id}/` - Delete school
    - `POST /api/schools/{id}/activate/` - Activate school
    - `POST /api/schools/{id}/deactivate/` - Deactivate school
    - `GET /api/schools/{id}/statistics/` - Get school statistics
    - `GET /api/schools/{id}/dashboard/` - Get school dashboard
    - `GET /api/schools/active_school/` - Get active school
    
    ### Days
    - `GET /api/days/` - List days
    - `POST /api/days/` - Create day
    - `GET /api/days/{id}/` - Retrieve day
    - `PUT /api/days/{id}/` - Update day
    - `DELETE /api/days/{id}/` - Delete day
    - `GET /api/days/week_schedule/` - Get week schedule
    - `GET /api/days/school_days/` - Get school days
    - `GET /api/days/{id}/period_schedule/` - Get period schedule
    
    ### Dashboard
    - `GET /api/dashboard/` - Get dashboard statistics
    - `GET /api/dashboard/activity/` - Get recent activity
    
    ### Public Endpoints (No Authentication)
    - `GET /api/public/articles/` - Get published articles
    - `GET /api/public/carousel/` - Get active carousel images
    - `GET /api/public/school/contact/` - Get school contact info
    
    ### Helper Endpoints
    - `GET /api/check-permissions/` - Check user permissions
    - `POST /api/create-access-log/` - Create access log (testing)
    
    ## Permissions
    
    Different endpoints require different permissions:
    
    - **Articles**: `administration.can_manage_articles`
    - **Carousel**: `administration.can_manage_carousel`
    - **Access Logs**: `administration.can_view_access_logs`
    - **Schools**: `administration.can_manage_school`
    - **Days**: `administration.can_manage_days`
    
    ## Filtering
    
    Most list endpoints support filtering, searching, and ordering:
    
    ### Common Query Parameters
    
    - `search`: Full-text search
    - `ordering`: Sort by field (prepend '-' for descending)
    - `page`: Page number
    - `page_size`: Items per page
    
    ### Model-specific Filters
    
    #### Articles
    - `category`: Filter by category
    - `status`: Filter by status
    - `featured`: Filter by featured status
    - `pinned`: Filter by pinned status
    - `start_date`: Filter by publish date start
    - `end_date`: Filter by publish date end
    - `target_role`: Filter by target role
    - `target_grade`: Filter by target grade
    
    #### Access Logs
    - `login_type`: Filter by login type
    - `security_level`: Filter by security level
    - `is_suspicious`: Filter by suspicious flag
    - `start_date`: Filter by timestamp start
    - `end_date`: Filter by timestamp end
    - `ip_address`: Filter by IP address
    - `country`: Filter by country
    
    #### Schools
    - `active`: Filter by active status
    - `school_type`: Filter by school type
    - `students_gender`: Filter by students gender
    - `ownership`: Filter by ownership
    
    ## Response Format
    
    All endpoints return JSON responses with consistent structure:
    
    ### Success Response
    ```json
    {
        "data": { ... },
        "status": "success",
        "message": "Operation completed successfully"
    }
    ```
    
    ### Error Response
    ```json
    {
        "error": "Error type",
        "detail": "Error details",
        "status": "error"
    }
    ```
    
    ### Paginated Response
    ```json
    {
        "count": 100,
        "next": "http://api.example.com/endpoint/?page=2",
        "previous": null,
        "results": [ ... ]
    }
    ```
    
    ## Rate Limiting
    
    API is rate limited:
    - 100 requests per minute for authenticated users
    - 10 requests per minute for anonymous users
    
    ## Versioning
    
    API version is included in the URL (e.g., `/api/v1/`).
    Current version: v1
    
    ## Support
    
    For API support, contact: admin@delvokacademy.ac.ke
    """,
}

# Add documentation endpoint
urlpatterns.append(
    path('api/documentation/', views.APIDocumentationView.as_view(api_documentation), name='api-documentation')
)