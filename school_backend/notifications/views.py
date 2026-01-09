from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, F, Case, When, Value, IntegerField
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from datetime import timedelta

from .models import Notification, NotificationTemplate, UserNotificationSettings, NotificationStats
from .serializers import (
    NotificationSerializer, NotificationListSerializer,
    MarkAsReadSerializer, BulkNotificationSerializer,
    NotificationTemplateSerializer, UserNotificationSettingsSerializer,
    NotificationStatsSerializer, NotificationStatsSummarySerializer,
    NotificationFilterSerializer, NotificationCreateFromTemplateSerializer
)
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class IsAdmin(IsAdminUser):
    """Custom admin permission for clarity"""
    pass


class StandardPagination(PageNumberPagination):
    """Custom pagination for notifications"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notification CRUD operations
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'priority', 'channel', 'status']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get notifications for current user"""
        user = self.request.user
        
        # Base queryset - only show user's notifications unless admin
        if user.is_staff and self.request.query_params.get('all_users') == 'true':
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(user=user)
        
        # Apply filters from query parameters
        queryset = self.apply_filters(queryset)
        
        # Prefetch related data
        queryset = queryset.select_related('user', 'sender')
        
        return queryset

    def apply_filters(self, queryset):
        """Apply various filters to the queryset"""
        params = self.request.query_params
        
        # Filter by status
        status_filter = params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by read/unread
        is_read = params.get('read')
        if is_read is not None:
            if is_read.lower() == 'true':
                queryset = queryset.filter(status='read')
            else:
                queryset = queryset.filter(status='unread')
        
        # Filter by type
        notification_type = params.get('type')
        if notification_type:
            queryset = queryset.filter(type=notification_type)
        
        # Filter by priority
        priority = params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by channel
        channel = params.get('channel')
        if channel:
            queryset = queryset.filter(channel=channel)
        
        # Filter by delivery method
        delivery_method = params.get('delivery_method')
        if delivery_method:
            queryset = queryset.filter(delivery_method=delivery_method)
        
        # Filter by date range
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        # Filter expired notifications
        show_expired = params.get('show_expired', 'false').lower() == 'true'
        if not show_expired:
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            )
        
        # Filter by sender
        sender_id = params.get('sender_id')
        if sender_id:
            queryset = queryset.filter(sender_id=sender_id)
        
        # Filter by search term
        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(message__icontains=search) |
                Q(data__icontains=search)
            )
        
        return queryset

    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return NotificationListSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        """Add request context to serializer"""
        context = super().get_serializer_context()
        context['auto_send'] = self.request.data.get('auto_send', True)
        return context

    def perform_create(self, serializer):
        """Set user to current user when creating notification"""
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete notification"""
        instance.delete(soft_delete=True)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get notification summary for current user"""
        queryset = self.get_queryset()
        
        # Calculate counts
        total_count = queryset.count()
        unread_count = queryset.filter(status='unread').count()
        read_count = queryset.filter(status='read').count()
        archived_count = queryset.filter(status='archived').count()
        
        # Count by type
        type_counts = queryset.values('type').annotate(
            count=Count('id'),
            unread=Count('id', filter=Q(status='unread')),
            read=Count('id', filter=Q(status='read'))
        ).order_by('-count')
        
        # Count by priority
        priority_counts = queryset.values('priority').annotate(
            count=Count('id'),
            unread=Count('id', filter=Q(status='unread'))
        ).order_by(
            Case(
                When(priority='urgent', then=Value(0)),
                When(priority='high', then=Value(1)),
                When(priority='medium', then=Value(2)),
                When(priority='low', then=Value(3)),
                default=Value(4),
                output_field=IntegerField()
            )
        )
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_stats = queryset.filter(created_at__gte=week_ago).values(
            'created_at__date'
        ).annotate(
            count=Count('id')
        ).order_by('created_at__date')
        
        return Response({
            'total': total_count,
            'unread': unread_count,
            'read': read_count,
            'archived': archived_count,
            'by_type': list(type_counts),
            'by_priority': list(priority_counts),
            'recent_activity': list(recent_stats),
            'timestamp': timezone.now().isoformat()
        })

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications for current user"""
        queryset = self.get_queryset().filter(status='unread')
        
        # Apply ordering
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications (last 24 hours)"""
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        queryset = self.get_queryset().filter(created_at__gte=twenty_four_hours_ago)
        
        # Prioritize unread and urgent notifications
        queryset = queryset.annotate(
            priority_order=Case(
                When(priority='urgent', then=Value(0)),
                When(priority='high', then=Value(1)),
                When(priority='medium', then=Value(2)),
                When(priority='low', then=Value(3)),
                default=Value(4),
                output_field=IntegerField()
            )
        ).order_by('priority_order', '-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent notifications"""
        queryset = self.get_queryset().filter(
            Q(priority='urgent') | Q(priority='high')
        ).filter(
            Q(status='unread') | Q(created_at__gte=timezone.now() - timedelta(hours=24))
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        
        # Update stats
        NotificationStats.update_stats(notification)
        
        # Clear cache
        cache_key = f"unread_count_{request.user.id}"
        cache.delete(cache_key)
        
        return Response({
            'status': 'success',
            'message': 'Notification marked as read',
            'notification_id': str(notification.id),
            'read_at': notification.read_at.isoformat() if notification.read_at else None
        })

    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """Mark notification as unread"""
        notification = self.get_object()
        notification.mark_as_unread()
        
        # Clear cache
        cache_key = f"unread_count_{request.user.id}"
        cache.delete(cache_key)
        
        return Response({
            'status': 'success',
            'message': 'Notification marked as unread',
            'notification_id': str(notification.id)
        })

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive notification"""
        notification = self.get_object()
        notification.archive()
        return Response({
            'status': 'success',
            'message': 'Notification archived',
            'notification_id': str(notification.id)
        })

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend notification"""
        notification = self.get_object()
        
        # Check if notification can be resent
        if notification.status == 'deleted':
            return Response({
                'status': 'error',
                'message': 'Cannot resend deleted notification'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Resend notification
        success = notification.send()
        
        return Response({
            'status': 'success' if success else 'partial',
            'message': 'Notification resent' if success else 'Notification resend partially failed',
            'notification_id': str(notification.id),
            'sent_at': notification.sent_at.isoformat() if notification.sent_at else None
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        serializer = MarkAsReadSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        if data.get('mark_all'):
            queryset = self.get_queryset().filter(status='unread')
            updated_count = queryset.update(status='read', read_at=timezone.now())
        elif data.get('notification_ids'):
            queryset = self.get_queryset().filter(
                id__in=data['notification_ids'],
                status='unread'
            )
            updated_count = queryset.update(status='read', read_at=timezone.now())
        else:
            return Response({
                'status': 'error',
                'message': 'No notifications to mark as read'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Clear cache
        cache_key = f"unread_count_{request.user.id}"
        cache.delete(cache_key)
        
        # Update stats for each notification
        for notification in queryset:
            NotificationStats.update_stats(notification)
        
        return Response({
            'status': 'success',
            'message': f'{updated_count} notifications marked as read',
            'count': updated_count
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Delete multiple notifications"""
        notification_ids = request.data.get('notification_ids', [])
        
        if not notification_ids:
            return Response({
                'status': 'error',
                'message': 'No notification IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(id__in=notification_ids)
        deleted_count = 0
        
        for notification in queryset:
            notification.delete(soft_delete=True)
            deleted_count += 1
        
        # Clear cache
        cache_key = f"unread_count_{request.user.id}"
        cache.delete(cache_key)
        
        return Response({
            'status': 'success',
            'message': f'{deleted_count} notifications deleted',
            'count': deleted_count
        })

    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get notification counts"""
        queryset = self.get_queryset()
        
        total_count = queryset.count()
        unread_count = queryset.filter(status='unread').count()
        read_count = queryset.filter(status='read').count()
        archived_count = queryset.filter(status='archived').count()
        urgent_count = queryset.filter(priority='urgent', status='unread').count()
        
        # Count by type
        type_counts = queryset.values('type').annotate(count=Count('id'))
        type_counts_dict = {item['type']: item['count'] for item in type_counts}
        
        # Count by priority
        priority_counts = queryset.values('priority').annotate(count=Count('id'))
        priority_counts_dict = {item['priority']: item['count'] for item in priority_counts}
        
        # Cache the unread count
        cache_key = f"unread_count_{request.user.id}"
        cache.set(cache_key, unread_count, 30)
        
        return Response({
            'total': total_count,
            'unread': unread_count,
            'read': read_count,
            'archived': archived_count,
            'urgent': urgent_count,
            'by_type': type_counts_dict,
            'by_priority': priority_counts_dict,
            'timestamp': timezone.now().isoformat()
        })

    @action(detail=False, methods=['post'])
    def create_bulk(self, request):
        """Create bulk notifications"""
        serializer = BulkNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get target users
        if data.get('user_ids'):
            users = User.objects.filter(id__in=data['user_ids'], is_active=True)
        elif data.get('role'):
            # Assuming User model has a 'role' field
            users = User.objects.filter(
                role=data['role'],
                is_active=True
            )
        else:
            users = User.objects.none()
        
        if not users.exists():
            return Response({
                'status': 'error',
                'message': 'No users found for notification'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create notifications
        notifications = []
        with transaction.atomic():
            for user in users:
                notification = Notification(
                    user=user,
                    title=data['title'],
                    message=data['message'],
                    type=data['type'],
                    channel=data['channel'],
                    priority=data['priority'],
                    delivery_method=data['delivery_method'],
                    data=data.get('data', {}),
                    actions=data.get('actions', []),
                    expires_at=data.get('expires_at'),
                    sender=request.user,
                    metadata={
                        'bulk_created': True,
                        'request_id': str(uuid.uuid4())[:8]
                    }
                )
                notifications.append(notification)
            
            Notification.objects.bulk_create(notifications)
            
            # Send notifications if auto_send is True
            sent_count = 0
            failed_count = 0
            if data.get('auto_send', True):
                for notification in notifications:
                    try:
                        if notification.send():
                            sent_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send notification {notification.id}: {e}")
                        failed_count += 1
            
            # Create stats entries
            for notification in notifications:
                NotificationStats.update_stats(notification)
        
        return Response({
            'status': 'success',
            'message': 'Bulk notifications created successfully',
            'total_users': users.count(),
            'notifications_created': len(notifications),
            'sent_count': sent_count,
            'failed_count': failed_count,
            'pending_count': len(notifications) - sent_count - failed_count if not data.get('auto_send', True) else 0
        })

    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Create notification from template"""
        serializer = NotificationCreateFromTemplateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            template = NotificationTemplate.objects.get(
                name=data['template_name'],
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Template not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get users
        user_ids = []
        if data.get('user_id'):
            user_ids = [data['user_id']]
        elif data.get('user_ids'):
            user_ids = data['user_ids']
        
        users = User.objects.filter(id__in=user_ids, is_active=True)
        
        if not users.exists():
            return Response({
                'status': 'error',
                'message': 'No users found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create notifications from template
        created_notifications = []
        failed_notifications = []
        
        for user in users:
            try:
                notification = NotificationTemplate.create_from_template(
                    template_name=data['template_name'],
                    user=user,
                    context_data=data['context'],
                    delivery_method=data.get('delivery_method', 'in_app'),
                    priority=data.get('priority', 'medium'),
                    sender=request.user,
                    auto_send=data.get('auto_send', True)
                )
                
                if notification:
                    created_notifications.append(notification)
                else:
                    failed_notifications.append(str(user.id))
                    
            except Exception as e:
                logger.error(f"Failed to create notification from template for user {user.id}: {e}")
                failed_notifications.append(str(user.id))
        
        return Response({
            'status': 'success',
            'message': 'Notifications created from template',
            'template': template.name,
            'created_count': len(created_notifications),
            'failed_count': len(failed_notifications),
            'failed_users': failed_notifications if failed_notifications else None,
            'notification_ids': [str(n.id) for n in created_notifications]
        })


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for NotificationTemplate CRUD operations"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def perform_destroy(self, instance):
        """Soft delete template by marking as inactive"""
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a template"""
        template = self.get_object()
        
        # Create a copy
        template_copy = NotificationTemplate(
            name=f"{template.name} (Copy)",
            template_type=template.template_type,
            title_template=template.title_template,
            message_template=template.message_template,
            default_priority=template.default_priority,
            default_channel=template.default_channel,
            default_delivery=template.default_delivery,
            variables=template.variables,
            description=template.description,
            is_active=True
        )
        template_copy.save()
        
        serializer = self.get_serializer(template_copy)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview template rendering"""
        template = self.get_object()
        context = request.data.get('context', {})
        
        try:
            title, message = template.render(context)
            return Response({
                'title': title,
                'message': message,
                'template_name': template.name,
                'context_used': context
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Failed to render template'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserNotificationSettingsView(generics.RetrieveUpdateAPIView):
    """View for user notification settings"""
    serializer_class = UserNotificationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create notification settings for user"""
        user = self.request.user
        settings, created = UserNotificationSettings.objects.get_or_create(user=user)
        return settings
    
    def perform_update(self, serializer):
        """Update notification settings"""
        instance = serializer.save()
        
        # Clear any cached notification data
        cache_key = f"notification_settings_{self.request.user.id}"
        cache.delete(cache_key)


class NotificationStatsView(generics.ListAPIView):
    """View for notification statistics"""
    serializer_class = NotificationStatsSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'channel']
    ordering_fields = ['date', 'sent_count', 'delivered_count', 'read_count']
    ordering = ['-date']
    
    def get_queryset(self):
        """Get notification statistics with date filtering"""
        queryset = NotificationStats.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of notification statistics"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date') or timezone.now().date()
        
        if not start_date:
            # Default to last 30 days
            start_date = (timezone.now() - timedelta(days=30)).date()
        
        # Get summary from model class method
        summary = NotificationStats.get_daily_summary(end_date)
        
        serializer = NotificationStatsSummarySerializer(summary)
        return Response(serializer.data)


class UnreadCountView(generics.GenericAPIView):
    """View for getting unread notification count"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get unread notification count"""
        user = request.user
        
        # Try to get from cache first
        cache_key = f"unread_count_{user.id}"
        unread_count = cache.get(cache_key)
        
        if unread_count is None:
            unread_count = Notification.objects.filter(
                user=user,
                status='unread'
            ).count()
            # Cache for 30 seconds
            cache.set(cache_key, unread_count, 30)
        
        # Get urgent count
        urgent_count = Notification.objects.filter(
            user=user,
            status='unread',
            priority='urgent'
        ).count()
        
        return Response({
            'count': unread_count,
            'urgent_count': urgent_count,
            'timestamp': timezone.now().isoformat()
        })


class NotificationPreferencesView(generics.GenericAPIView):
    """View for managing notification preferences"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get notification preferences"""
        user = request.user
        settings, _ = UserNotificationSettings.objects.get_or_create(user=user)
        
        # Check if currently in quiet hours
        is_quiet_hours = settings.is_quiet_hours()
        
        return Response({
            'settings': UserNotificationSettingsSerializer(settings).data,
            'quiet_hours_active': is_quiet_hours,
            'current_time': timezone.now().isoformat(),
            'quiet_hours_start': settings.quiet_hours_start.strftime('%H:%M'),
            'quiet_hours_end': settings.quiet_hours_end.strftime('%H:%M')
        })
    
    def post(self, request):
        """Update notification preferences"""
        user = request.user
        settings, _ = UserNotificationSettings.objects.get_or_create(user=user)
        
        serializer = UserNotificationSettingsSerializer(
            settings, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Clear cache
            cache_key = f"notification_settings_{user.id}"
            cache.delete(cache_key)
            
            return Response({
                'status': 'success',
                'message': 'Notification preferences updated',
                'settings': serializer.data
            })
        
        return Response({
            'status': 'error',
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class NotificationCleanupView(generics.GenericAPIView):
    """View for cleaning up old notifications"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        """Clean up old notifications"""
        days_old = int(request.data.get('days_old', 90))
        cleanup_date = timezone.now() - timedelta(days=days_old)
        
        # Archive expired notifications
        expired_count = Notification.objects.filter(
            expires_at__lt=timezone.now(),
            status__in=['unread', 'read']
        ).update(status='archived')
        
        # Delete old archived notifications
        deleted_count = Notification.objects.filter(
            status='archived',
            updated_at__lt=cleanup_date
        ).delete()[0]
        
        return Response({
            'status': 'success',
            'message': 'Cleanup completed',
            'expired_archived': expired_count,
            'old_deleted': deleted_count,
            'cleanup_date': cleanup_date.isoformat(),
            'days_old': days_old
        })


class NotificationWebhookView(generics.GenericAPIView):
    """View for handling notification webhooks (e.g., delivery status updates)"""
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request):
        """Handle webhook callbacks from notification services"""
        # This would handle webhooks from email/SMS/push services
        # to update delivery status
        
        webhook_type = request.data.get('type')
        notification_id = request.data.get('notification_id')
        status = request.data.get('status')
        
        if not all([webhook_type, notification_id, status]):
            return Response({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            notification = Notification.objects.get(id=notification_id)
            
            # Update delivery status based on webhook type
            if webhook_type == 'email':
                notification.email_sent = status == 'delivered'
            elif webhook_type == 'sms':
                notification.sms_sent = status == 'delivered'
            elif webhook_type == 'push':
                notification.push_sent = status == 'delivered'
            
            notification.save()
            
            # Update stats
            NotificationStats.update_stats(notification)
            
            return Response({
                'status': 'success',
                'message': f'{webhook_type} status updated'
            })
            
        except Notification.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)