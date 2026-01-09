# backend/apps/it/views_fixed.py
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    SystemComponent, ComponentStatusLog, SupportTicket, TicketComment,
    TimeEntry, SystemAlert, AlertLog, MaintenanceTask, BackupJob,
    PerformanceMetric, KnowledgeBaseArticle, ArticleRating, ITResource,
    ResourceLog, ITProject, ITDashboard
)
from .serializers import (
    SystemComponentSerializer, ComponentStatusLogSerializer,
    SupportTicketSerializer, TicketCommentSerializer, TimeEntrySerializer,
    SystemAlertSerializer, AlertLogSerializer, MaintenanceTaskSerializer,
    BackupJobSerializer, PerformanceMetricSerializer,
    KnowledgeBaseArticleSerializer, ArticleRatingSerializer,
    ITResourceSerializer, ResourceLogSerializer, ITProjectSerializer,
    ITDashboardSerializer
)
from accounts.models import User

logger = logging.getLogger(__name__)


class IsITStaffOrReadOnly(permissions.BasePermission):
    """Custom permission for IT staff or read-only access"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in [
            User.Role.IT_SUPPORT,
            User.Role.ADMIN,
        ]


class IsOwnerOrITStaff(permissions.BasePermission):
    """Permission to allow owners or IT staff to edit"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        if request.user.role in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            return True
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        
        return False


class SystemComponentViewSet(viewsets.ModelViewSet):
    """ViewSet for System Components"""
    serializer_class = SystemComponentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'component_type', 'status', 'criticality',
        'department', 'location', 'assigned_to'
    ]
    search_fields = ['name', 'component_code', 'hostname', 'ip_address', 'serial_number']
    ordering_fields = ['name', 'status', 'criticality', 'last_check', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        queryset = SystemComponent.objects.all()
        user = self.request.user
        
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(
                Q(assigned_to=user) |
                Q(department=user.department)
            ).distinct()
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


class SupportTicketViewSet(viewsets.ModelViewSet):
    """ViewSet for Support Tickets"""
    serializer_class = SupportTicketSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'category', 'priority', 'status', 'assigned_to',
        'created_by', 'sla_status'
    ]
    search_fields = ['ticket_number', 'title', 'description', 'resolution']
    ordering_fields = ['created_at', 'priority', 'due_date', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        queryset = SupportTicket.objects.all()
        user = self.request.user
        
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(
                Q(created_by=user) | Q(assigned_to=user)
            ).distinct()
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]


class TicketCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Ticket Comments"""
    serializer_class = TicketCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ticket', 'user', 'is_internal']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        queryset = TicketComment.objects.all()
        user = self.request.user
        
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(
                Q(ticket__created_by=user) | Q(ticket__assigned_to=user)
            )
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]


class SystemAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for System Alerts"""
    serializer_class = SystemAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'status', 'source', 'component', 'assigned_to']
    search_fields = ['title', 'message']
    ordering_fields = ['detected_at', 'severity', 'status']
    ordering = ['-detected_at']
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        return SystemAlert.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Maintenance Tasks - FIXED VERSION"""
    serializer_class = MaintenanceTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['task_type', 'status', 'impact_level', 'assigned_to']
    search_fields = ['task_number', 'title', 'description']
    ordering_fields = ['scheduled_start', 'status', 'impact_level']
    ordering = ['-scheduled_start']
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        return MaintenanceTask.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start maintenance task"""
        task = self.get_object()
        task.start_task(user=request.user)
        return Response({'status': 'Task started.'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete maintenance task"""
        task = self.get_object()
        outcome = request.data.get('outcome', '')
        issues = request.data.get('issues_encountered', '')
        lessons = request.data.get('lessons_learned', '')
        
        task.complete_task(outcome, issues, lessons)
        return Response({'status': 'Task completed.'})


class KnowledgeBaseArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for Knowledge Base Articles"""
    serializer_class = KnowledgeBaseArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'author']
    search_fields = ['title', 'content', 'summary', 'tags']
    ordering_fields = ['created_at', 'views', 'rating', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        queryset = KnowledgeBaseArticle.objects.all()
        user = self.request.user
        
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(status=KnowledgeBaseArticle.ArticleStatus.PUBLISHED)
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


class ITResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for IT Resources"""
    serializer_class = ITResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'status', 'assigned_to', 'department', 'location']
    search_fields = ['name', 'resource_code', 'serial_number', 'asset_tag', 'model']
    ordering_fields = ['name', 'resource_type', 'status', 'purchase_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        return ITResource.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


class ITDashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for IT Dashboards"""
    serializer_class = ITDashboardSerializer
    
    def get_queryset(self):
        """Get queryset WITHOUT is_active filter"""
        queryset = ITDashboard.objects.all()
        user = self.request.user
        
        accessible_dashboards = []
        for dashboard in queryset:
            if dashboard.can_access(user):
                accessible_dashboards.append(dashboard.pk)
        
        return queryset.filter(pk__in=accessible_dashboards)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


# Simple ViewSets for other models (without is_active filter)
class ComponentStatusLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ComponentStatusLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['component', 'new_status', 'changed_by']
    ordering_fields = ['checked_at']
    ordering = ['-checked_at']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ComponentStatusLog.objects.all()


class TimeEntryViewSet(viewsets.ModelViewSet):
    serializer_class = TimeEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ticket', 'user', 'billable', 'date_worked']
    ordering_fields = ['date_worked', 'created_at']
    ordering = ['-date_worked']
    
    def get_queryset(self):
        return TimeEntry.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]


class AlertLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlertLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['alert', 'action', 'user']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AlertLog.objects.all()


class BackupJobViewSet(viewsets.ModelViewSet):
    serializer_class = BackupJobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['backup_type', 'status', 'success', 'source_type']
    search_fields = ['job_name', 'source_path', 'destination_path']
    ordering_fields = ['scheduled_time', 'created_at', 'status']
    ordering = ['-scheduled_time']
    
    def get_queryset(self):
        return BackupJob.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


class PerformanceMetricViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PerformanceMetricSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['component']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PerformanceMetric.objects.all()


class ArticleRatingViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleRatingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article', 'user', 'helpful']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ArticleRating.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]


class ResourceLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResourceLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['resource', 'action', 'user']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ResourceLog.objects.all()


class ITProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ITProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project_manager']
    search_fields = ['project_code', 'name', 'description']
    ordering_fields = ['start_date', 'end_date', 'priority', 'status']
    ordering = ['-start_date']
    
    def get_queryset(self):
        return ITProject.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


class ITMetricsView(APIView):
    """View for IT system metrics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            return Response(
                {'error': 'Access denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        metrics = {
            'system_health': self.get_system_health_metrics(),
            'tickets': self.get_ticket_metrics(),
            'alerts': self.get_alert_metrics(),
            'resources': self.get_resource_metrics(),
            'performance': self.get_performance_metrics(),
            'timestamp': timezone.now()
        }
        
        return Response(metrics)
    
    def get_system_health_metrics(self):
        components = SystemComponent.objects.filter(is_monitored=True)
        
        return {
            'total': components.count(),
            'online': components.filter(status=SystemComponent.ComponentStatus.ONLINE).count(),
            'offline': components.filter(status=SystemComponent.ComponentStatus.OFFLINE).count(),
            'degraded': components.filter(status=SystemComponent.ComponentStatus.DEGRADED).count(),
            'maintenance': components.filter(status=SystemComponent.ComponentStatus.MAINTENANCE).count(),
            'health_percentage': self.calculate_health_percentage(components)
        }
    
    def calculate_health_percentage(self, components):
        if not components.exists():
            return 0
        
        healthy = components.filter(status=SystemComponent.ComponentStatus.ONLINE).count()
        return round((healthy / components.count()) * 100, 2)
    
    def get_ticket_metrics(self):
        tickets = SupportTicket.objects.all()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        return {
            'total': tickets.count(),
            'open': tickets.filter(status=SupportTicket.TicketStatus.OPEN).count(),
            'in_progress': tickets.filter(status=SupportTicket.TicketStatus.IN_PROGRESS).count(),
            'resolved_30_days': tickets.filter(
                status=SupportTicket.TicketStatus.RESOLVED,
                resolved_at__gte=thirty_days_ago
            ).count(),
            'average_resolution_time_hours': self.calculate_avg_resolution_time(),
        }
    
    def calculate_avg_resolution_time(self):
        resolved_tickets = SupportTicket.objects.filter(
            status=SupportTicket.TicketStatus.RESOLVED,
            resolved_at__isnull=False
        )
        
        if not resolved_tickets.exists():
            return 0
        
        total_seconds = sum(
            (ticket.resolved_at - ticket.created_at).total_seconds()
            for ticket in resolved_tickets
        )
        
        avg_hours = total_seconds / resolved_tickets.count() / 3600
        return round(avg_hours, 2)
    
    def get_alert_metrics(self):
        alerts = SystemAlert.objects.all()
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        return {
            'total': alerts.count(),
            'active': alerts.filter(status=SystemAlert.AlertStatus.ACTIVE).count(),
            'last_24_hours': alerts.filter(detected_at__gte=twenty_four_hours_ago).count(),
            'critical': alerts.filter(severity=SystemAlert.AlertSeverity.CRITICAL).count(),
        }
    
    def get_resource_metrics(self):
        resources = ITResource.objects.all()
        
        return {
            'total': resources.count(),
            'available': resources.filter(status=ITResource.ResourceStatus.AVAILABLE).count(),
            'in_use': resources.filter(status=ITResource.ResourceStatus.IN_USE).count(),
            'maintenance': resources.filter(status=ITResource.ResourceStatus.MAINTENANCE).count(),
            'software_licenses': resources.filter(resource_type=ITResource.ResourceType.SOFTWARE).count(),
            'hardware': resources.filter(resource_type=ITResource.ResourceType.HARDWARE).count()
        }
    
    def get_performance_metrics(self):
        recent_metrics = PerformanceMetric.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=1)
        )
        
        if not recent_metrics.exists():
            return {
                'average_cpu': 0,
                'average_memory': 0,
                'average_disk': 0,
                'healthy_systems': 0
            }
        
        avg_cpu = recent_metrics.aggregate(Avg('cpu_usage'))['cpu_usage__avg'] or 0
        avg_memory = recent_metrics.aggregate(Avg('memory_usage'))['memory_usage__avg'] or 0
        avg_disk = recent_metrics.aggregate(Avg('disk_usage'))['disk_usage__avg'] or 0
        
        healthy_systems = sum(1 for metric in recent_metrics if metric.is_healthy)
        
        return {
            'average_cpu': round(avg_cpu, 2),
            'average_memory': round(avg_memory, 2),
            'average_disk': round(avg_disk, 2),
            'healthy_systems': healthy_systems,
            'total_systems': recent_metrics.count()
        }