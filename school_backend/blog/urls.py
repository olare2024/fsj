# blog/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.BlogCategoryViewSet, basename='blogcategory')
router.register(r'posts', views.BlogPostViewSet, basename='blogpost')
router.register(r'discussions', views.DiscussionThreadViewSet, basename='discussionthread')
router.register(r'discussion-posts', views.DiscussionPostViewSet, basename='discussionpost')
router.register(r'comments', views.BlogCommentViewSet, basename='blogcomment')
router.register(r'study-groups', views.StudyGroupViewSet, basename='studygroup')
router.register(r'study-group-memberships', views.StudyGroupMembershipViewSet, basename='studygroupmembership')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard and analytics
    path('dashboard/', views.blog_dashboard, name='blog-dashboard'),
    path('analytics/', views.blog_analytics, name='blog-analytics'),
    
    # User activity
    path('user-activity/', views.user_blog_activity, name='user-blog-activity'),
    path('user-activity/<uuid:user_id>/', views.user_blog_activity, name='user-blog-activity-detail'),
    
    # Search and utilities
    path('search/', views.search_content, name='content-search'),
    path('mention-suggestions/', views.mention_suggestions, name='mention-suggestions'),
    
    # Additional endpoints for specific functionality
    path('posts/featured/', views.BlogPostViewSet.as_view({'get': 'featured'}), name='featured-posts'),
    path('posts/my-posts/', views.BlogPostViewSet.as_view({'get': 'my_posts'}), name='my-posts'),
    path('discussions/my-discussions/', views.DiscussionThreadViewSet.as_view({'get': 'my_discussions'}), name='my-discussions'),
    path('discussions/participating/', views.DiscussionThreadViewSet.as_view({'get': 'participating'}), name='participating-discussions'),
    path('notifications/mark-all-read/', views.NotificationViewSet.as_view({'post': 'mark_all_read'}), name='mark-all-notifications-read'),
    path('notifications/unread-count/', views.NotificationViewSet.as_view({'get': 'unread_count'}), name='unread-notifications-count'),
]

# Include in main urls.py with namespace
app_name = 'blog'