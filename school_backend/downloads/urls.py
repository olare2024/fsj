# downloads/urls.py - UPDATED VERSION
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DownloadCategoryViewSet, DownloadFileViewSet,
    DownloadHistoryViewSet, FileRatingViewSet
)

router = DefaultRouter()
router.register(r'categories', DownloadCategoryViewSet, basename='download-category')
router.register(r'files', DownloadFileViewSet, basename='download-file')
router.register(r'history', DownloadHistoryViewSet, basename='download-history')
router.register(r'ratings', FileRatingViewSet, basename='file-rating')

# Add additional endpoints that aren't covered by the router
urlpatterns = [
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('files/<int:pk>/download/', 
         DownloadFileViewSet.as_view({'post': 'download'}), 
         name='download-file-download'),
    path('files/popular/', 
         DownloadFileViewSet.as_view({'get': 'popular'}), 
         name='popular-downloads'),
    path('files/stats/', 
         DownloadFileViewSet.as_view({'get': 'stats'}), 
         name='download-stats'),
    path('files/<int:pk>/download-history/', 
         DownloadFileViewSet.as_view({'get': 'download_history'}), 
         name='file-download-history'),
]