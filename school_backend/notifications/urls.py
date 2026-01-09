from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'templates', views.NotificationTemplateViewSet, basename='template')

# API URL patterns
urlpatterns = [
    # Include router URLs for API endpoints
    path('', include(router.urls)),
    
    # Additional endpoints not covered by router
    path('unread-count/', 
         views.UnreadCountView.as_view(), 
         name='unread-count'),
    
    path('settings/', 
         views.UserNotificationSettingsView.as_view(), 
         name='user-notification-settings'),
    
    path('stats/', 
         views.NotificationStatsView.as_view(), 
         name='notification-stats'),
    
    path('preferences/', 
         views.NotificationPreferencesView.as_view(), 
         name='notification-preferences'),
    
    path('admin/cleanup/', 
         views.NotificationCleanupView.as_view(), 
         name='notification-cleanup'),
    
    path('webhook/', 
         views.NotificationWebhookView.as_view(), 
         name='notification-webhook'),
]