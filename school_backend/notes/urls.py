"""
Learning Management System URLs for Delvok Academy
Corrected version - only includes views that actually exist
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notes'

# Create a main router
router = DefaultRouter()

# ==================== CONTENT TYPE VIEWSETS ====================
router.register(r'categories', views.ContentCategoryViewSet, basename='category')
router.register(r'tags', views.ContentTagViewSet, basename='tag')
router.register(r'text-content', views.TextContentViewSet, basename='text-content')
router.register(r'video-content', views.VideoContentViewSet, basename='video-content')
router.register(r'audio-content', views.AudioContentViewSet, basename='audio-content')
router.register(r'pdf-content', views.PDFContentViewSet, basename='pdf-content')
router.register(r'presentation-content', views.PresentationContentViewSet, basename='presentation-content')
router.register(r'interactive-content', views.InteractiveContentViewSet, basename='interactive-content')
router.register(r'quiz-content', views.QuizContentViewSet, basename='quiz-content')
router.register(r'assignment-content', views.AssignmentContentViewSet, basename='assignment-content')
router.register(r'link-content', views.LinkContentViewSet, basename='link-content')
router.register(r'file-content', views.FileContentViewSet, basename='file-content')

# ==================== MODULE VIEWSETS ====================
router.register(r'modules', views.LearningModuleViewSet, basename='module')
router.register(r'module-contents', views.ModuleContentViewSet, basename='module-content')

# ==================== ENROLLMENT VIEWSETS ====================
router.register(r'enrollments', views.EnrollmentViewSet, basename='enrollment')

# ==================== PROGRESS VIEWSETS ====================
router.register(r'content-progress', views.ContentProgressViewSet, basename='content-progress')

# ==================== ASSESSMENT VIEWSETS ====================
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'quiz-attempts', views.QuizAttemptViewSet, basename='quiz-attempt')

# ==================== USER INTERACTION VIEWSETS ====================
router.register(r'content-notes', views.ContentNoteViewSet, basename='content-note')
router.register(r'content-ratings', views.ContentRatingViewSet, basename='content-rating')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # ==================== DASHBOARD ENDPOINTS ====================
    path('dashboard/student/', views.StudentDashboardView.as_view(), name='student-dashboard'),
    
    # ==================== SEARCH ENDPOINTS ====================
    path('search/', views.AdvancedSearchView.as_view(), name='content-search'),
    
    # ==================== ANALYTICS ENDPOINTS ====================
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    
    # ==================== RECOMMENDATION ENDPOINTS ====================
    path('recommendations/', views.ContentRecommendationView.as_view(), name='recommendations'),
    
    # ==================== BULK OPERATIONS ENDPOINTS ====================
    path('bulk-operations/', views.BulkOperationsView.as_view(), name='bulk-operations'),
]

# Custom URL patterns for specific actions
urlpatterns += [
    # ==================== CONTENT-SPECIFIC ACTIONS ====================
    path('content/<uuid:pk>/publish/',
         views.ContentTypeViewSet.as_view({'post': 'publish'}), 
         name='publish-content'),
    
    path('content/<uuid:pk>/unpublish/',
         views.ContentTypeViewSet.as_view({'post': 'unpublish'}), 
         name='unpublish-content'),
    
    path('content/<uuid:pk>/analytics/',
         views.ContentTypeViewSet.as_view({'get': 'analytics'}), 
         name='content-analytics'),
    
    path('content/<uuid:pk>/progress/',
         views.ContentTypeViewSet.as_view({'get': 'progress'}), 
         name='content-progress'),
    
    path('content/<uuid:pk>/update-progress/',
         views.ContentTypeViewSet.as_view({'post': 'update_progress'}), 
         name='content-update-progress'),
    
    # ==================== MODULE-SPECIFIC ACTIONS ====================
    path('modules/<uuid:pk>/contents/',
         views.LearningModuleViewSet.as_view({'get': 'contents'}), 
         name='module-contents'),
    
    path('modules/<uuid:pk>/analytics/',
         views.LearningModuleViewSet.as_view({'get': 'analytics'}), 
         name='module-analytics'),
    
    path('modules/<uuid:pk>/my-progress/',
         views.LearningModuleViewSet.as_view({'get': 'my_progress'}), 
         name='module-my-progress'),
    
    path('modules/<uuid:pk>/enroll/',
         views.LearningModuleViewSet.as_view({'post': 'enroll'}), 
         name='module-enroll'),
    
    # ==================== QUIZ ATTEMPT ACTIONS ====================
    path('quiz-attempts/<uuid:pk>/submit-answers/',
         views.QuizAttemptViewSet.as_view({'post': 'submit_answers'}), 
         name='quiz-submit-answers'),
    
    # ==================== PROGRESS ACTIONS ====================
    path('content-progress/bulk-update/',
         views.ContentProgressViewSet.as_view({'post': 'bulk_update'}), 
         name='bulk-update-content-progress'),
    
    # ==================== CATEGORY ACTIONS ====================
    path('categories/<uuid:pk>/contents/',
         views.ContentCategoryViewSet.as_view({'get': 'contents'}), 
         name='category-contents'),
]

# ==================== HEALTH CHECK ====================
urlpatterns += [
    path('health/', views.learning_health_check, name='learning-health'),
]