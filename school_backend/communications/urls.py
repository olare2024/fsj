from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Register viewsets
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'message-groups', views.MessageGroupViewSet, basename='messagegroup')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'meetings', views.ParentTeacherMeetingViewSet, basename='meeting')
router.register(r'communication-preferences', views.CommunicationPreferenceViewSet, basename='communicationpreference')
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')

# Additional URL patterns
urlpatterns = [
    path('', include(router.urls)),
    
    # Statistics and dashboard endpoints
    path('statistics/communication/', views.CommunicationStatisticsView.as_view(), name='communication-statistics'),
    path('statistics/announcements/', views.AnnouncementStatisticsView.as_view(), name='announcement-statistics'),
    path('dashboard/my-communications/', views.MyCommunicationsView.as_view(), name='my-communications'),
    
    # Message recipient specific endpoints
    path('messages/<uuid:message_id>/recipients/', views.MessageRecipientView.as_view(), name='message-recipients'),
    
    # Meeting participant endpoints
    path('meetings/<uuid:meeting_id>/participants/', views.MeetingParticipantsView.as_view(), name='meeting-participants'),
]

# Optional: API versioning
app_name = 'communications'

# Optional: Include these in your main urls.py with:
# path('api/communications/', include('communications.urls')),