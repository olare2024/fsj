# admin_panel/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'users', views.AdminUserViewSet, basename='admin-users')
router.register(r'dashboard', views.AdminDashboardViewSet, basename='admin-dashboard')
router.register(r'analytics', views.AnalyticsViewSet, basename='admin-analytics')
router.register(r'settings', views.SystemSettingsViewSet, basename='system-settings')
router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-logs')
router.register(r'notifications', views.SystemNotificationViewSet, basename='system-notifications')
router.register(r'api-logs', views.APIUsageLogViewSet, basename='api-logs')
router.register(r'user-sessions', views.UserSessionViewSet, basename='user-sessions')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Additional admin endpoints
    path('users/bulk-actions/', views.BulkUserActions.as_view(), name='bulk-user-actions'),
    path('dashboard/stats/', views.DashboardStats.as_view(), name='dashboard-stats'),
    path('analytics/overview/', views.AnalyticsOverview.as_view(), name='analytics-overview'),
    path('settings/view/', views.SystemSettingsView.as_view(), name='system-settings-view'),
    path('health-check/', views.SystemHealthCheckView.as_view(), name='system-health-check'),
]