# events/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()
router.register(r'categories', views.EventCategoryViewSet, basename='eventcategory')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'registrations', views.EventRegistrationViewSet, basename='eventregistration')
router.register(r'feedback', views.EventFeedbackViewSet, basename='eventfeedback')
router.register(r'reminders', views.EventReminderViewSet, basename='eventreminder')
router.register(r'attachments', views.EventAttachmentViewSet, basename='eventattachment')

# Additional custom endpoints
urlpatterns = [
    # API v1 routes
    path('', include(router.urls)),
    
    # Custom event endpoints
    path('events/upcoming/', views.EventViewSet.as_view({'get': 'upcoming'}), name='upcoming-events'),
    path('events/ongoing/', views.EventViewSet.as_view({'get': 'ongoing'}), name='ongoing-events'),
    path('events/featured/', views.EventViewSet.as_view({'get': 'featured'}), name='featured-events'),
    path('events/past/', views.EventViewSet.as_view({'get': 'past'}), name='past-events'),
    
    # Event-specific actions
    path('events/<int:pk>/register/', views.EventViewSet.as_view({'post': 'register'}), name='event-register'),
    path('events/<int:pk>/approve/', views.EventViewSet.as_view({'post': 'approve'}), name='event-approve'),
    path('events/<int:pk>/publish/', views.EventViewSet.as_view({'post': 'publish'}), name='event-publish'),
    path('events/<int:pk>/cancel/', views.EventViewSet.as_view({'post': 'cancel'}), name='event-cancel'),
    path('events/<int:pk>/registrations/', views.EventViewSet.as_view({'get': 'registrations'}), name='event-registrations'),
    path('events/<int:pk>/feedback/', views.EventViewSet.as_view({'get': 'feedback'}), name='event-feedback'),
    
    # Registration actions
    path('registrations/<int:pk>/check-in/', views.EventRegistrationViewSet.as_view({'post': 'check_in'}), name='registration-check-in'),
    path('registrations/<int:pk>/record-payment/', views.EventRegistrationViewSet.as_view({'post': 'record_payment'}), name='registration-record-payment'),
    
    # Feedback actions
    path('feedback/<int:pk>/mark-helpful/', views.EventFeedbackViewSet.as_view({'post': 'mark_helpful'}), name='feedback-mark-helpful'),
    path('feedback/<int:pk>/approve/', views.EventFeedbackViewSet.as_view({'post': 'approve'}), name='feedback-approve'),
    
    # User-specific endpoints
    path('my-events/', views.EventViewSet.as_view({'get': 'list'}), name='my-events'),
    path('my-registrations/', views.EventRegistrationViewSet.as_view({'get': 'list'}), name='my-registrations'),
    path('my-feedback/', views.EventFeedbackViewSet.as_view({'get': 'list'}), name='my-feedback'),
]

# The full path will be: /api/v1/events/