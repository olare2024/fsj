# backend/apps/it/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .additional_views import (
    MyTicketsView, MyAssignedTicketsView, MyComponentsView,
    MyResourcesView, ActiveAlertsView, OverdueTasksView,
    ExportTicketsView, ExportComponentsView, ExportResourcesView
)

router = DefaultRouter()
router.register(r'components', views.SystemComponentViewSet, basename='component')
router.register(r'component-status-logs', views.ComponentStatusLogViewSet, basename='component-status-log')
router.register(r'tickets', views.SupportTicketViewSet, basename='ticket')
router.register(r'ticket-comments', views.TicketCommentViewSet, basename='ticket-comment')
router.register(r'time-entries', views.TimeEntryViewSet, basename='time-entry')
router.register(r'alerts', views.SystemAlertViewSet, basename='alert')
router.register(r'alert-logs', views.AlertLogViewSet, basename='alert-log')
router.register(r'maintenance-tasks', views.MaintenanceTaskViewSet, basename='maintenance-task')
router.register(r'backup-jobs', views.BackupJobViewSet, basename='backup-job')
router.register(r'performance-metrics', views.PerformanceMetricViewSet, basename='performance-metric')
router.register(r'knowledge-base', views.KnowledgeBaseArticleViewSet, basename='knowledge-base')
router.register(r'article-ratings', views.ArticleRatingViewSet, basename='article-rating')
router.register(r'resources', views.ITResourceViewSet, basename='resource')
router.register(r'resource-logs', views.ResourceLogViewSet, basename='resource-log')
router.register(r'projects', views.ITProjectViewSet, basename='project')
router.register(r'dashboards', views.ITDashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('metrics/', views.ITMetricsView.as_view(), name='it-metrics'),
    
    # Additional endpoints
    path('my-tickets/', MyTicketsView.as_view(), name='my-tickets'),
    path('my-assigned-tickets/', MyAssignedTicketsView.as_view(), name='my-assigned-tickets'),
    path('my-components/', MyComponentsView.as_view(), name='my-components'),
    path('my-resources/', MyResourcesView.as_view(), name='my-resources'),
    path('active-alerts/', ActiveAlertsView.as_view(), name='active-alerts'),
    path('overdue-tasks/', OverdueTasksView.as_view(), name='overdue-tasks'),
    
    # Export endpoints
    path('export/tickets/', ExportTicketsView.as_view(), name='export-tickets'),
    path('export/components/', ExportComponentsView.as_view(), name='export-components'),
    path('export/resources/', ExportResourcesView.as_view(), name='export-resources'),
]