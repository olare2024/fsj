from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.DownloadCategoryViewSet)
router.register(r'files', views.DownloadFileViewSet, basename='downloadfile')
router.register(r'history', views.DownloadHistoryViewSet, basename='downloadhistory')
router.register(r'ratings', views.FileRatingViewSet, basename='filerating')

urlpatterns = [
    path('', include(router.urls)),
]