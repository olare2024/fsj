# backend/apps/it/views.py
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F, Sum
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
        # Allow read-only access for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Allow full access for IT staff
        return request.user.is_authenticated and request.user.role in [
            User.Role.IT_SUPPORT,
            User.Role.ADMIN,
        ]


class IsOwnerOrITStaff(permissions.BasePermission):
    """Permission to allow owners or IT staff to edit"""
    
    def has_object_permission(self, request, view, obj):
        # Allow read-only for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Check if user is IT staff
        if request.user.role in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            return True
        
        # Check if user is owner (created_by)
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Check if user is assigned
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        
        return False


class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common functionality"""
    
    def get_queryset(self):
        """Get queryset with fallback for is_active field"""
        queryset = super().get_queryset()
        
        # Try to filter by is_active if the field exists
        try:
            # Check if model has is_active field
            model = self.get_serializer().Meta.model
            if hasattr(model, '_meta'):
                model._meta.get_field('is_active')
                queryset = queryset.filter(is_active=True)
        except Exception:
            # If field doesn't exist or any other error, return all
            pass
            
        return queryset


class SystemComponentViewSet(BaseViewSet):
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
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Non-IT staff can only see components assigned to them or in their department
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(
                Q(assigned_to=user) |
                Q(department=user.department)
            ).distinct()
        
        # Apply additional filters from query params
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        criticality_filter = self.request.query_params.get('criticality', None)
        if criticality_filter:
            queryset = queryset.filter(criticality=criticality_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update component status"""
        component = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(SystemComponent.ComponentStatus.choices):
            return Response(
                {'error': 'Invalid status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        component.update_status(new_status, notes)
        return Response({'status': 'Status updated successfully.'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get component statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_components': queryset.count(),
            'by_status': dict(queryset.values_list('status').annotate(count=Count('id'))),
            'by_type': dict(queryset.values_list('component_type').annotate(count=Count('id'))),
            'by_criticality': dict(queryset.values_list('criticality').annotate(count=Count('id'))),
            'online_percentage': round(
                (queryset.filter(status=SystemComponent.ComponentStatus.ONLINE).count() / 
                 max(queryset.count(), 1)) * 100, 2
            ),
            'components_needing_maintenance': queryset.filter(
                next_maintenance__lte=timezone.now().date()
            ).count(),
        }
        
        return Response(stats)


class SupportTicketViewSet(BaseViewSet):
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
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Regular users can only see tickets they created or are assigned to them
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(
                Q(created_by=user) | Q(assigned_to=user)
            ).distinct()
        
        # Apply additional filters
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create ticket with current user"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to a user"""
        ticket = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(pk=user_id)
            if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
                return Response(
                    {'error': 'User must be IT staff.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            ticket.assign_to_user(user)
            return Response({'status': 'Ticket assigned successfully.'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def add_time_entry(self, request, pk=None):
        """Add time entry to ticket"""
        ticket = self.get_object()
        serializer = TimeEntrySerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(ticket=ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get ticket statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_tickets': queryset.count(),
            'by_status': dict(queryset.values_list('status').annotate(count=Count('id'))),
            'by_category': dict(queryset.values_list('category').annotate(count=Count('id'))),
            'by_priority': dict(queryset.values_list('priority').annotate(count=Count('id'))),
            'overdue_tickets': sum(1 for ticket in queryset if ticket.is_overdue),
            'average_resolution_time': None,
        }
        
        # Calculate average resolution time for resolved tickets
        resolved_tickets = queryset.filter(
            status=SupportTicket.TicketStatus.RESOLVED,
            resolved_at__isnull=False
        )
        if resolved_tickets.exists():
            total_seconds = sum(
                (ticket.resolved_at - ticket.created_at).total_seconds()
                for ticket in resolved_tickets
            )
            stats['average_resolution_time'] = total_seconds / resolved_tickets.count()
        
        return Response(stats)


class TicketCommentViewSet(BaseViewSet):
    """ViewSet for Ticket Comments"""
    serializer_class = TicketCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ticket', 'user', 'is_internal']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter comments based on user role and ticket access"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Non-IT staff can only see comments on their tickets
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(
                Q(ticket__created_by=user) | Q(ticket__assigned_to=user)
            )
        
        # Filter by ticket if provided
        ticket_id = self.request.query_params.get('ticket', None)
        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create comment with current user"""
        serializer.save()


class SystemAlertViewSet(BaseViewSet):
    """ViewSet for System Alerts"""
    serializer_class = SystemAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['severity', 'status', 'source', 'component', 'assigned_to']
    search_fields = ['title', 'message']
    ordering_fields = ['detected_at', 'severity', 'status']
    ordering = ['-detected_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        notes = request.data.get('notes', '')
        
        alert.acknowledge(user=request.user, notes=notes)
        return Response({'status': 'Alert acknowledged.'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        alert.resolve(resolution_notes=resolution_notes, user=request.user)
        return Response({'status': 'Alert resolved.'})
    
    @action(detail=False, methods=['get'])
    def active_alerts(self, request):
        """Get active alerts"""
        queryset = self.get_queryset().filter(status=SystemAlert.AlertStatus.ACTIVE)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MaintenanceTaskViewSet(BaseViewSet):
    """ViewSet for Maintenance Tasks"""
    serializer_class = MaintenanceTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['task_type', 'status', 'impact_level', 'assigned_to']
    search_fields = ['task_number', 'title', 'description']
    ordering_fields = ['scheduled_start', 'status', 'impact_level']
    ordering = ['-scheduled_start']
    
    def get_permissions(self):
        """Set permissions based on action"""
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


class KnowledgeBaseArticleViewSet(BaseViewSet):
    """ViewSet for Knowledge Base Articles"""
    serializer_class = KnowledgeBaseArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'author']
    search_fields = ['title', 'content', 'summary', 'tags']
    ordering_fields = ['created_at', 'views', 'rating', 'title']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter published articles for non-staff users"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Non-IT staff can only see published articles
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            queryset = queryset.filter(status=KnowledgeBaseArticle.ArticleStatus.PUBLISHED)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an article"""
        article = self.get_object()
        article.publish(reviewed_by=request.user)
        return Response({'status': 'Article published.'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate an article"""
        article = self.get_object()
        helpful = request.data.get('helpful', True)
        comment = request.data.get('comment', '')
        
        try:
            rating = ArticleRating.objects.get(article=article, user=request.user)
            return Response(
                {'error': 'You have already rated this article.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ArticleRating.DoesNotExist:
            ArticleRating.objects.create(
                article=article,
                user=request.user,
                helpful=helpful,
                comment=comment
            )
            
            # Update article counts
            if helpful:
                article.helpful_count += 1
            else:
                article.not_helpful_count += 1
            
            total_votes = article.helpful_count + article.not_helpful_count
            if total_votes > 0:
                article.rating = (article.helpful_count / total_votes) * 5
            
            article.save()
            
            return Response({'status': 'Rating submitted.'})
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Increment article view count"""
        article = self.get_object()
        article.increment_views()
        return Response({'status': 'View count incremented.'})


class ITResourceViewSet(BaseViewSet):
    """ViewSet for IT Resources"""
    serializer_class = ITResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'status', 'assigned_to', 'department', 'location']
    search_fields = ['name', 'resource_code', 'serial_number', 'asset_tag', 'model']
    ordering_fields = ['name', 'resource_type', 'status', 'purchase_date']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign resource to user"""
        resource = self.get_object()
        user_id = request.data.get('user_id')
        location = request.data.get('location', '')
        department = request.data.get('department', '')
        
        try:
            user = User.objects.get(pk=user_id)
            resource.assign(user, location, department)
            return Response({'status': 'Resource assigned successfully.'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Unassign resource"""
        resource = self.get_object()
        resource.unassign()
        return Response({'status': 'Resource unassigned.'})


class ITDashboardViewSet(BaseViewSet):
    """ViewSet for IT Dashboards"""
    serializer_class = ITDashboardSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter dashboards based on user access"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter by access permissions
        accessible_dashboards = []
        for dashboard in queryset:
            if dashboard.can_access(user):
                accessible_dashboards.append(dashboard.pk)
        
        return queryset.filter(pk__in=accessible_dashboards)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get dashboard data"""
        dashboard = self.get_object()
        
        # Check access
        if not dashboard.can_access(request.user):
            return Response(
                {'error': 'Access denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Increment view count
        dashboard.increment_view_count()
        
        # Get dashboard data
        data = dashboard.get_dashboard_data()
        return Response(data)


class ITMetricsView(APIView):
    """View for IT system metrics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get overall IT system metrics"""
        user = request.user
        
        # Basic permission check
        if user.role not in [User.Role.IT_SUPPORT, User.Role.ADMIN]:
            return Response(
                {'error': 'Access denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate metrics
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
        """Get system health metrics"""
        components = SystemComponent.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            SystemComponent._meta.get_field('is_active')
            components = components.filter(is_active=True)
        except Exception:
            pass
        
        components = components.filter(is_monitored=True)
        
        return {
            'total': components.count(),
            'online': components.filter(status=SystemComponent.ComponentStatus.ONLINE).count(),
            'offline': components.filter(status=SystemComponent.ComponentStatus.OFFLINE).count(),
            'degraded': components.filter(status=SystemComponent.ComponentStatus.DEGRADED).count(),
            'maintenance': components.filter(status=SystemComponent.ComponentStatus.MAINTENANCE).count(),
            'health_percentage': self.calculate_health_percentage(components)
        }
    
    def calculate_health_percentage(self, components):
        """Calculate overall health percentage"""
        if not components.exists():
            return 0
        
        healthy = components.filter(status=SystemComponent.ComponentStatus.ONLINE).count()
        return round((healthy / components.count()) * 100, 2)
    
    def get_ticket_metrics(self):
        """Get ticket metrics"""
        tickets = SupportTicket.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            SupportTicket._meta.get_field('is_active')
            tickets = tickets.filter(is_active=True)
        except Exception:
            pass
        
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
            'sla_compliance': self.calculate_sla_compliance()
        }
    
    def calculate_avg_resolution_time(self):
        """Calculate average resolution time"""
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
    
    def calculate_sla_compliance(self):
        """Calculate SLA compliance percentage"""
        resolved_tickets = SupportTicket.objects.filter(
            status=SupportTicket.TicketStatus.RESOLVED,
            resolved_at__isnull=False,
            sla_status__isnull=False
        )
        
        if not resolved_tickets.exists():
            return 0
        
        within_sla = resolved_tickets.filter(sla_status='within_sla').count()
        return round((within_sla / resolved_tickets.count()) * 100, 2)
    
    def get_alert_metrics(self):
        """Get alert metrics"""
        alerts = SystemAlert.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            SystemAlert._meta.get_field('is_active')
            alerts = alerts.filter(is_active=True)
        except Exception:
            pass
        
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        return {
            'total': alerts.count(),
            'active': alerts.filter(status=SystemAlert.AlertStatus.ACTIVE).count(),
            'last_24_hours': alerts.filter(detected_at__gte=twenty_four_hours_ago).count(),
            'critical': alerts.filter(severity=SystemAlert.AlertSeverity.CRITICAL).count(),
            'average_response_time': self.calculate_avg_alert_response_time()
        }
    
    def calculate_avg_alert_response_time(self):
        """Calculate average alert response time"""
        acknowledged_alerts = SystemAlert.objects.filter(
            status=SystemAlert.AlertStatus.ACKNOWLEDGED,
            acknowledged_at__isnull=False
        )
        
        if not acknowledged_alerts.exists():
            return 0
        
        total_seconds = sum(
            (alert.acknowledged_at - alert.detected_at).total_seconds()
            for alert in acknowledged_alerts
        )
        
        avg_minutes = total_seconds / acknowledged_alerts.count() / 60
        return round(avg_minutes, 2)
    
    def get_resource_metrics(self):
        """Get resource metrics"""
        resources = ITResource.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            ITResource._meta.get_field('is_active')
            resources = resources.filter(is_active=True)
        except Exception:
            pass
        
        return {
            'total': resources.count(),
            'available': resources.filter(status=ITResource.ResourceStatus.AVAILABLE).count(),
            'in_use': resources.filter(status=ITResource.ResourceStatus.IN_USE).count(),
            'maintenance': resources.filter(status=ITResource.ResourceStatus.MAINTENANCE).count(),
            'software_licenses': resources.filter(resource_type=ITResource.ResourceType.SOFTWARE).count(),
            'hardware': resources.filter(resource_type=ITResource.ResourceType.HARDWARE).count()
        }
    
    def get_performance_metrics(self):
        """Get performance metrics"""
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


# Additional ViewSets for missing models
class ComponentStatusLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Component Status Logs"""
    serializer_class = ComponentStatusLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['component', 'new_status', 'changed_by']
    ordering_fields = ['checked_at']
    ordering = ['-checked_at']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset with fallback for is_active field"""
        queryset = ComponentStatusLog.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            ComponentStatusLog._meta.get_field('is_active')
            queryset = queryset.filter(is_active=True)
        except Exception:
            pass
        
        return queryset


class TimeEntryViewSet(BaseViewSet):
    """ViewSet for Time Entries"""
    serializer_class = TimeEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ticket', 'user', 'billable', 'date_worked']
    ordering_fields = ['date_worked', 'created_at']
    ordering = ['-date_worked']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]


class AlertLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Alert Logs"""
    serializer_class = AlertLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['alert', 'action', 'user']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset with fallback for is_active field"""
        queryset = AlertLog.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            AlertLog._meta.get_field('is_active')
            queryset = queryset.filter(is_active=True)
        except Exception:
            pass
        
        return queryset


class BackupJobViewSet(BaseViewSet):
    """ViewSet for Backup Jobs"""
    serializer_class = BackupJobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['backup_type', 'status', 'success', 'source_type']
    search_fields = ['job_name', 'source_path', 'destination_path']
    ordering_fields = ['scheduled_time', 'created_at', 'status']
    ordering = ['-scheduled_time']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]


class PerformanceMetricViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Performance Metrics"""
    serializer_class = PerformanceMetricSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['component']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset with fallback for is_active field"""
        queryset = PerformanceMetric.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            PerformanceMetric._meta.get_field('is_active')
            queryset = queryset.filter(is_active=True)
        except Exception:
            pass
        
        return queryset


class ArticleRatingViewSet(BaseViewSet):
    """ViewSet for Article Ratings"""
    serializer_class = ArticleRatingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article', 'user', 'helpful']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrITStaff]
        return [permission() for permission in permission_classes]


class ResourceLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Resource Logs"""
    serializer_class = ResourceLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['resource', 'action', 'user']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset with fallback for is_active field"""
        queryset = ResourceLog.objects.all()
        
        # Try to filter by is_active if field exists
        try:
            ResourceLog._meta.get_field('is_active')
            queryset = queryset.filter(is_active=True)
        except Exception:
            pass
        
        return queryset


class ITProjectViewSet(BaseViewSet):
    """ViewSet for IT Projects"""
    serializer_class = ITProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project_manager']
    search_fields = ['project_code', 'name', 'description']
    ordering_fields = ['start_date', 'end_date', 'priority', 'status']
    ordering = ['-start_date']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsITStaffOrReadOnly]
        return [permission() for permission in permission_classes]