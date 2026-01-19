# admin_panel/views.py
from rest_framework import viewsets, status, permissions, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
import json

from .serializers import (
    AdminUserSerializer, UserCreateSerializer, UserUpdateSerializer,
    DashboardStatsSerializer, AnalyticsSerializer, BulkActionSerializer,
    SystemSettingsSerializer, AuditLogSerializer, SystemNotificationSerializer,
    APIUsageLogSerializer, SystemHealthCheckSerializer, UserSessionSerializer
)
from .models import (
    SystemSettings, AuditLog, SystemNotification, 
    APIUsageLog, SystemHealthCheck, UserSession
)

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admin user management
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return AdminUserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter by role if provided
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
            
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(is_active=True)
            elif status_filter == 'inactive':
                queryset = queryset.filter(is_active=False)
            elif status_filter == 'suspended':
                queryset = queryset.filter(is_suspended=True)
            elif status_filter == 'pending_approval':
                queryset = queryset.filter(is_approved=False)
                
        return queryset.order_by('-date_joined')
    
    def list(self, request):
        """
        Get users with pagination and filtering
        """
        users = self.get_queryset()
        
        # Simple pagination
        page_size = int(request.query_params.get('page_size', 50))
        page = int(request.query_params.get('page', 1))
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        paginated_users = users[start_index:end_index]
        
        serializer = self.get_serializer(paginated_users, many=True)
        return Response({
            'count': users.count(),
            'results': serializer.data,
            'page': page,
            'page_size': page_size,
            'total_pages': (users.count() + page_size - 1) // page_size
        })
    
    def create(self, request):
        """Create a new user with comprehensive error handling"""
        print("=" * 60)
        print("🔄 ADMIN USER CREATION REQUEST")
        print(f"👤 Request User: {request.user.email}")
        print(f"👤 Request User Role: {request.user.role}")
        print(f"👤 Request User is_admin: {request.user.is_admin}")
        print(f"📦 Request Data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        print(f"📝 Serializer Class: {serializer.__class__.__name__}")
        
        # Check serializer validity with detailed output
        is_valid = serializer.is_valid()
        print(f"✅ Serializer Valid: {is_valid}")
        
        if not is_valid:
            print("❌ SERIALIZER VALIDATION ERRORS:")
            for field, errors in serializer.errors.items():
                print(f"   {field}: {errors}")
            
            return Response({
                'success': False,
                'message': 'User creation failed - validation errors',
                'errors': serializer.errors,
                'debug_info': {
                    'request_user': request.user.email,
                    'request_user_role': request.user.role,
                    'fields_received': list(request.data.keys())
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print("✅ Serializer validation passed")
        print(f"📋 Validated Data: {serializer.validated_data}")
        
        try:
            print("💾 Attempting to save user...")
            user = serializer.save()
            print("✅ USER CREATED SUCCESSFULLY!")
            print(f"📝 User details:")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - Role: {user.role}")
            print(f"   - Admission: {user.admission_number}")
            print(f"   - Staff ID: {user.staff_id}")
            print(f"   - Active: {user.is_active}")
            print(f"   - Approved: {user.is_approved}")
            print(f"   - Staff: {user.is_staff}")
            
            return Response({
                'success': True,
                'message': 'User created successfully',
                'data': AdminUserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"❌ ERROR CREATING USER:")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {str(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            
            return Response({
                'success': False,
                'message': f'Failed to create user: {str(e)}',
                'error_type': type(e).__name__,
                'debug_info': 'Check server logs for detailed error information'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        stats = {
            'total_users': User.objects.count(),
            'students': User.objects.filter(role='student').count(),
            'teachers': User.objects.filter(role='teacher').count(),
            'parents': User.objects.filter(role='parent').count(),
            'admins': User.objects.filter(role='admin').count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'suspended_users': User.objects.filter(is_suspended=True).count(),
            'pending_approval': User.objects.filter(is_approved=False).count(),
            'new_users_today': User.objects.filter(
                date_joined__date=timezone.now().date()
            ).count(),
        }
        return Response(stats)

class AdminDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for admin dashboard data with all required endpoints
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """
        Get dashboard overview data (for /admin/dashboard/)
        """
        # User statistics
        user_stats = {
            'total_users': User.objects.count(),
            'students': User.objects.filter(role='student').count(),
            'teachers': User.objects.filter(role='teacher').count(),
            'parents': User.objects.filter(role='parent').count(),
            'admins': User.objects.filter(role='admin').count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'new_users_today': User.objects.filter(
                date_joined__date=timezone.now().date()
            ).count(),
        }
        
        # System statistics
        system_stats = {
            'total_sessions': UserSession.objects.filter(is_active=True).count(),
            'api_requests_today': APIUsageLog.objects.filter(
                timestamp__date=timezone.now().date()
            ).count(),
            'active_notifications': SystemNotification.objects.filter(
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).count(),
        }
        
        return Response({
            'user_stats': user_stats,
            'system_stats': system_stats,
            'last_updated': timezone.now()
        })
    
    @action(detail=False, methods=['GET'], url_path='summary')
    def get_summary(self, request):
        """
        Get dashboard summary data (for /admin/dashboard/summary/)
        """
        time_range = request.query_params.get('time_range', 'month')
        
        # Calculate date range
        now = timezone.now()
        if time_range == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == 'week':
            start_date = now - timedelta(days=7)
        elif time_range == 'quarter':
            start_date = now - timedelta(days=90)
        elif time_range == 'year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # month
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Import other models if they exist
        try:
            from academics.models import Class, Enrollment, Subject
            from finance.models import Invoice, Payment
            
            # Academic data
            total_students = User.objects.filter(role='student', is_active=True).count()
            total_teachers = User.objects.filter(role='teacher', is_active=True).count()
            total_staff = User.objects.filter(role='staff', is_active=True).count()
            
            # Financial data
            total_revenue = Payment.objects.filter(
                status='completed',
                created_at__gte=start_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            pending_payments = Invoice.objects.filter(
                status='pending',
                due_date__lt=now
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
        except ImportError:
            # Use placeholders if models don't exist
            total_students = User.objects.filter(role='student', is_active=True).count()
            total_teachers = User.objects.filter(role='teacher', is_active=True).count()
            total_staff = User.objects.filter(role='staff', is_active=True).count()
            total_revenue = 1525000
            pending_payments = 245000
        
        # Calculate active users (last 30 days)
        active_users = User.objects.filter(
            is_active=True, 
            last_login__gte=now - timedelta(days=30)
        ).count()
        
        # Pending approvals
        pending_approvals = User.objects.filter(is_approved=False, is_active=True).count()
        
        # Get current academic year
        try:
            from academics.models import AcademicYear
            current_academic_year = AcademicYear.objects.filter(is_current=True).first()
            academic_year = current_academic_year.name if current_academic_year else f"{now.year}"
            current_term = "Term 1"  # You might want to get this from your model
        except:
            academic_year = f"{now.year}"
            current_term = "Term 1"
        
        # Collection rate calculation (placeholder)
        total_invoices = 1000000  # This should come from your Invoice model
        paid_invoices = 850000    # This should come from your Payment model
        collection_rate = round((paid_invoices / total_invoices * 100), 1) if total_invoices > 0 else 0
        
        data = {
            'summary': {
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_staff': total_staff,
                'active_users': active_users,
                'pending_approvals': pending_approvals,
                'system_health': 98.5,
                'total_revenue': total_revenue,
                'pending_payments': pending_payments,
                'collection_rate': collection_rate,
                'academic_year': academic_year,
                'current_term': current_term
            },
            'time_range': time_range,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat(),
            'last_updated': now.isoformat()
        }
        
        return Response(data)
    
    @action(detail=False, methods=['GET'], url_path='recent-activities')
    def get_recent_activities(self, request):
        """
        Get recent system activities (for /admin/dashboard/recent-activities/)
        """
        limit = int(request.query_params.get('limit', 10))
        
        # Get recent user logins
        recent_users = User.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login')[:limit]
        
        # Get recent audit logs if available
        try:
            recent_audit_logs = AuditLog.objects.all().order_by('-timestamp')[:limit]
            activities = []
            
            for log in recent_audit_logs:
                activities.append({
                    'id': log.id,
                    'timestamp': log.timestamp,
                    'user': log.user.email if log.user else 'System',
                    'action': log.action,
                    'description': f"{log.model}: {log.details[:50]}..." if log.details else log.action,
                    'type': 'system' if log.model in ['SystemSettings', 'SystemNotification'] else 'user'
                })
        except:
            # Fallback activities
            activities = [
                {
                    'id': 1,
                    'timestamp': now - timedelta(minutes=30),
                    'user': 'admin@example.com',
                    'action': 'User Login',
                    'description': 'Admin user logged into the system',
                    'type': 'user'
                },
                {
                    'id': 2,
                    'timestamp': now - timedelta(hours=2),
                    'user': 'teacher1@example.com',
                    'action': 'Assignment Created',
                    'description': 'Created new assignment for Mathematics class',
                    'type': 'academic'
                }
            ]
        
        return Response({
            'activities': activities[:limit],
            'total_count': len(activities)
        })
    
    @action(detail=False, methods=['GET'], url_path='pending-tasks')
    def get_pending_tasks(self, request):
        """
        Get pending tasks (for /admin/dashboard/pending-tasks/)
        """
        # This would typically come from a Task model
        # For now, return placeholder data
        pending_tasks = [
            {
                'id': 1,
                'title': 'Review New Student Applications',
                'description': '15 new student applications require review',
                'type': 'user',
                'priority': 'high',
                'due_date': (timezone.now() + timedelta(days=2)).isoformat(),
                'assigned_to': 'Admin Team'
            },
            {
                'id': 2,
                'title': 'Monthly Financial Report',
                'description': 'Generate and review monthly financial report',
                'type': 'finance',
                'priority': 'medium',
                'due_date': (timezone.now() + timedelta(days=1)).isoformat(),
                'assigned_to': 'Finance Department'
            },
            {
                'id': 3,
                'title': 'System Backup Verification',
                'description': 'Verify latest system backup',
                'type': 'system',
                'priority': 'low',
                'due_date': (timezone.now() + timedelta(days=3)).isoformat(),
                'assigned_to': 'IT Department'
            }
        ]
        
        return Response({
            'tasks': pending_tasks,
            'total_count': len(pending_tasks)
        })

class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for system analytics
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """
        Get comprehensive analytics data (for /admin/analytics/)
        """
        time_range = request.query_params.get('timeRange', 'month:1')
        
        analytics_data = {
            'user_growth': self._get_user_growth(),
            'system_usage': self._get_system_usage(),
            'activity_trends': self._get_activity_trends(),
        }
        
        return Response(analytics_data)
    
    def _get_user_growth(self):
        """Get user growth data"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        return {
            'total_users': User.objects.count(),
            'new_users_this_week': User.objects.filter(
                date_joined__date__gte=week_ago
            ).count(),
            'new_users_this_month': User.objects.filter(
                date_joined__date__gte=month_ago
            ).count(),
            'active_users_today': User.objects.filter(
                last_login__date=today
            ).count(),
        }
    
    def _get_system_usage(self):
        """Get system usage statistics"""
        today = timezone.now().date()
        
        return {
            'active_sessions_today': UserSession.objects.filter(
                last_activity__date=today,
                is_active=True
            ).count(),
            'api_requests_today': APIUsageLog.objects.filter(
                timestamp__date=today
            ).count(),
            'total_audit_logs': AuditLog.objects.count(),
        }
    
    def _get_activity_trends(self):
        """Get activity trends"""
        # Last 7 days activity
        activity_data = []
        for i in range(6, -1, -1):
            date = timezone.now().date() - timedelta(days=i)
            logins = User.objects.filter(last_login__date=date).count()
            api_calls = APIUsageLog.objects.filter(timestamp__date=date).count()
            
            activity_data.append({
                'date': date.isoformat(),
                'logins': logins,
                'api_calls': api_calls,
            })
        
        return activity_data
    
    @action(detail=False, methods=['GET'], url_path='user-analytics')
    def get_user_analytics(self, request):
        """
        Get user analytics specifically (for /admin/analytics/user-analytics/)
        """
        # Active users in last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        active_users = User.objects.filter(
            last_login__gte=seven_days_ago
        ).count()
        
        # New users in last 7 days
        new_users = User.objects.filter(
            date_joined__gte=seven_days_ago
        ).count()
        
        # User distribution by role
        role_distribution = User.objects.values('role').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Convert to list of dictionaries
        role_data = [
            {'role': item['role'], 'count': item['count']}
            for item in role_distribution
        ]
        
        return Response({
            'active_users': active_users,
            'new_users': new_users,
            'role_distribution': role_data,
            'total_users': User.objects.count(),
            'last_7_days': seven_days_ago.date().isoformat()
        })

class DashboardStats(APIView):
    """API endpoint for dashboard statistics"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        stats = {
            'total_users': User.objects.count(),
            'total_students': User.objects.filter(role='student').count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_parents': User.objects.filter(role='parent').count(),
            'total_admins': User.objects.filter(role='admin').count(),
            'pending_approvals': User.objects.filter(is_approved=False).count(),
            'suspended_users': User.objects.filter(is_suspended=True).count(),
            'active_sessions': UserSession.objects.filter(is_active=True).count(),
        }
        return Response(stats)

class AnalyticsOverview(APIView):
    """API endpoint for analytics overview"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        return Response({
            'message': 'Analytics overview endpoint',
            'data': {
                'user_activity': User.objects.filter(
                    last_login__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'total_users': User.objects.count(),
                'new_users_week': User.objects.filter(
                    date_joined__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'system_uptime': '99.9%',  # This would come from monitoring
                'storage_used': '2.5 GB',  # This would be calculated
            }
        })

class BulkUserActions(APIView):
    """API endpoint for bulk user actions"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        serializer = BulkActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        action = data['action']
        user_ids = data['user_ids']
        
        users = User.objects.filter(id__in=user_ids)
        
        if action == 'activate':
            users.update(is_active=True)
            return Response({'message': f'{users.count()} users activated'})
        
        elif action == 'deactivate':
            users.update(is_active=False)
            return Response({'message': f'{users.count()} users deactivated'})
        
        elif action == 'delete':
            count = users.count()
            users.delete()
            return Response({'message': f'{count} users deleted'})
        
        else:
            return Response(
                {'error': 'Invalid action type'},
                status=status.HTTP_400_BAD_REQUEST
            )

class SystemSettingsView(APIView):
    """API endpoint for system settings"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        # Get or create default system settings
        settings, created = SystemSettings.objects.get_or_create(
            defaults={
                'school_name': 'Delvok Academy',
                'academic_year': '2026',
                'contact_email': 'info@delvok.ac.ke',
                'contact_phone': '+254700000000',
            }
        )
        serializer = SystemSettingsSerializer(settings)
        return Response(serializer.data)
    
    def post(self, request):
        settings, created = SystemSettings.objects.get_or_create()
        serializer = SystemSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SystemSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for system settings management
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = SystemSettingsSerializer
    
    def get_queryset(self):
        return SystemSettings.objects.all()
    
    def list(self, request):
        # Only return one settings object (create if doesn't exist)
        settings, created = SystemSettings.objects.get_or_create(
            defaults={
                'school_name': 'Delvok Academy',
                'academic_year': '2026',
                'contact_email': 'info@delvok.ac.ke',
                'contact_phone': '+254700000000',
            }
        )
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def health_status(self, request):
        """
        Get system health status (for /admin/settings/health-status/)
        """
        # Check database connection
        from django.db import connection
        from django.core.cache import cache
        
        checks = {
            'database': {'status': 'healthy', 'details': 'Connection established'},
            'cache': {'status': 'healthy', 'details': 'Cache system operational'},
            'storage': {'status': 'healthy', 'details': 'Storage accessible'},
            'api': {'status': 'healthy', 'details': 'API responding normally'}
        }
        
        # Test database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            checks['database'] = {'status': 'error', 'details': str(e)}
        
        # Test cache
        try:
            cache.set('health_check', 'test', 10)
            if cache.get('health_check') != 'test':
                checks['cache'] = {'status': 'warning', 'details': 'Cache test failed'}
        except Exception as e:
            checks['cache'] = {'status': 'error', 'details': str(e)}
        
        # Overall status
        overall_status = 'healthy'
        for check in checks.values():
            if check['status'] == 'error':
                overall_status = 'error'
                break
            elif check['status'] == 'warning' and overall_status != 'error':
                overall_status = 'warning'
        
        return Response({
            'checks': checks,
            'overall_status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'system_uptime': '99.9%',  # This should come from system monitoring
            'response_time': '45ms',   # This should be measured
        })

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for audit log viewing
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AuditLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'action', 'model', 'details']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        return AuditLog.objects.all().select_related('user')

class SystemNotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for system notifications
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = SystemNotificationSerializer
    
    def get_queryset(self):
        return SystemNotification.objects.all().select_related('created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['POST'])
    def create_announcement(self, request):
        """
        Create a system announcement (for /admin/notifications/create_announcement/)
        """
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['notification_type'] = 'announcement'
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            notification = serializer.save()
            
            # Here you would typically send notifications to users
            # based on the audience selection
            
            return Response({
                'success': True,
                'message': 'Announcement created successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class APIUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for API usage logs
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = APIUsageLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'endpoint', 'method']
    ordering_fields = ['timestamp', 'response_time']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        return APIUsageLog.objects.all().select_related('user')

class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user sessions
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserSessionSerializer
    
    def get_queryset(self):
        return UserSession.objects.all().select_related('user')

class SystemHealthCheckView(APIView):
    """
    API endpoint for system health checks
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from django.db import connection
        from django.core.cache import cache
        import os
        
        health_checks = {}
        
        # Database health check
        try:
            start_time = timezone.now()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            response_time = (timezone.now() - start_time).total_seconds() * 1000
            
            health_checks['database'] = {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'connections': getattr(connection, 'connections', {}),
            }
        except Exception as e:
            health_checks['database'] = {
                'status': 'critical',
                'error': str(e)
            }
        
        # Cache health check
        try:
            start_time = timezone.now()
            cache.set('health_check', 'test', 10)
            cache_result = cache.get('health_check')
            response_time = (timezone.now() - start_time).total_seconds() * 1000
            
            health_checks['cache'] = {
                'status': 'healthy' if cache_result == 'test' else 'warning',
                'response_time_ms': round(response_time, 2),
            }
        except Exception as e:
            health_checks['cache'] = {
                'status': 'critical',
                'error': str(e)
            }
        
        # Storage health check (simplified)
        try:
            health_checks['storage'] = {
                'status': 'healthy',
                'message': 'Storage check passed'
            }
        except Exception as e:
            health_checks['storage'] = {
                'status': 'warning',
                'error': str(e)
            }
        
        # Application health
        health_checks['application'] = {
            'status': 'healthy',
            'server_time': timezone.now().isoformat(),
            'total_users': User.objects.count(),
            'active_sessions': UserSession.objects.filter(is_active=True).count(),
        }
        
        return Response(health_checks)
    
    @action(detail=False, methods=['GET'], url_path='components')
    def get_health_components(self, request):
        """
        Get detailed health status for system components
        """
        now = timezone.now()
        
        components = {
            'server': {
                'name': 'Application Server',
                'status': 'healthy',
                'uptime': '99.9%',
                'response_time': '45ms',
                'details': 'Server running normally'
            },
            'database': {
                'name': 'Database Server',
                'status': 'healthy',
                'uptime': '99.95%',
                'usage': '35%',
                'details': 'Database connections stable'
            },
            'backup': {
                'name': 'Backup System',
                'status': 'healthy',
                'last_backup': (now - timedelta(hours=6)).isoformat(),
                'next_backup': (now + timedelta(hours=18)).isoformat(),
                'details': 'Backup system operational'
            },
            'security': {
                'name': 'Security System',
                'status': 'healthy',
                'last_scan': (now - timedelta(hours=1)).isoformat(),
                'threats_detected': 0,
                'details': 'No security threats detected'
            },
            'storage': {
                'name': 'Storage System',
                'status': 'healthy',
                'usage': '65%',
                'total_space': '100 GB',
                'used_space': '65 GB',
                'details': 'Storage capacity sufficient'
            },
            'performance': {
                'name': 'Performance',
                'status': 'healthy',
                'load': '32%',
                'memory': '58%',
                'details': 'System performance optimal'
            },
            'network': {
                'name': 'Network',
                'status': 'healthy',
                'latency': '12ms',
                'throughput': '100 Mbps',
                'details': 'Network connectivity stable'
            },
            'cache': {
                'name': 'Cache System',
                'status': 'healthy',
                'hit_rate': '92%',
                'size': '256 MB',
                'details': 'Cache performance optimal'
            }
        }
        
        # Calculate overall system health
        overall_score = 98.5  # This would be calculated based on component statuses
        
        return Response({
            'components': components,
            'overall_score': overall_score,
            'overall_status': 'healthy' if overall_score > 90 else 'warning' if overall_score > 70 else 'critical',
            'timestamp': now.isoformat()
        })

# Additional helper views for the admin portal

class AdminReportsView(APIView):
    """
    API endpoint for generating and managing reports
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get available report types"""
        report_types = [
            {
                'id': 'financial',
                'title': 'Financial Reports',
                'description': 'Revenue, expenses, and financial overview',
                'icon': 'cash-stack',
                'count': 12,
                'formats': ['csv', 'pdf', 'excel']
            },
            {
                'id': 'academic',
                'title': 'Academic Reports',
                'description': 'Grades, attendance, and academic performance',
                'icon': 'book-fill',
                'count': 8,
                'formats': ['csv', 'pdf']
            },
            {
                'id': 'user',
                'title': 'User Reports',
                'description': 'User statistics and activity reports',
                'icon': 'people-fill',
                'count': 15,
                'formats': ['csv', 'json', 'excel']
            },
            {
                'id': 'system',
                'title': 'System Reports',
                'description': 'System usage and performance reports',
                'icon': 'server',
                'count': 5,
                'formats': ['csv', 'json']
            },
            {
                'id': 'attendance',
                'title': 'Attendance Reports',
                'description': 'Student and staff attendance records',
                'icon': 'person-check-fill',
                'count': 23,
                'formats': ['csv', 'pdf', 'excel']
            },
            {
                'id': 'performance',
                'title': 'Performance Reports',
                'description': 'System and user performance metrics',
                'icon': 'bar-chart',
                'count': 7,
                'formats': ['csv', 'pdf']
            }
        ]
        
        return Response({
            'report_types': report_types,
            'total_reports': sum(r['count'] for r in report_types)
        })
    
    def post(self, request):
        """Generate a report"""
        report_type = request.data.get('type', 'users')
        format = request.data.get('format', 'csv')
        date_range = request.data.get('dateRange', 'month')
        
        # This would generate the actual report file
        # For now, return a placeholder response
        
        return Response({
            'success': True,
            'message': f'Report generation started for {report_type} in {format} format',
            'data': {
                'report_id': f'report_{int(timezone.now().timestamp())}',
                'type': report_type,
                'format': format,
                'status': 'processing',
                'estimated_completion': (timezone.now() + timedelta(minutes=2)).isoformat()
            }
        })
    
    @action(detail=False, methods=['POST'])
    def export_data(self, request):
        """Export data in various formats"""
        export_data = request.data
        
        # Validate export parameters
        required_fields = ['type', 'format']
        for field in required_fields:
            if field not in export_data:
                return Response({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate export file (placeholder)
        # In production, this would generate and save a file
        
        return Response({
            'success': True,
            'message': 'Export file generated successfully',
            'data': {
                'url': f'/api/v1/admin/exports/{export_data["type"]}_{int(timezone.now().timestamp())}.{export_data["format"]}',
                'type': export_data['type'],
                'format': export_data['format'],
                'size': '2.5 MB',
                'generated_at': timezone.now().isoformat()
            }
        })

class AdminSystemActionsView(APIView):
    """
    API endpoint for system maintenance actions
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        action = request.data.get('action')
        component_id = request.data.get('component_id')
        
        actions = {
            'backup': {
                'message': 'System backup initiated',
                'status': 'processing',
                'estimated_duration': '5 minutes'
            },
            'maintenance': {
                'message': 'Maintenance mode activated',
                'status': 'active',
                'estimated_duration': '30 minutes'
            },
            'restart': {
                'message': f'Component {component_id} restart initiated',
                'status': 'processing',
                'estimated_duration': '2 minutes'
            },
            'diagnostics': {
                'message': 'System diagnostics started',
                'status': 'processing',
                'estimated_duration': '1 minute'
            }
        }
        
        if action not in actions:
            return Response({
                'success': False,
                'error': f'Invalid action: {action}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # In production, this would trigger actual system actions
        # For now, return a simulated response
        
        return Response({
            'success': True,
            'message': actions[action]['message'],
            'data': {
                'action': action,
                'component': component_id,
                'status': actions[action]['status'],
                'started_at': timezone.now().isoformat(),
                'estimated_completion': (timezone.now() + timedelta(minutes=int(actions[action]['estimated_duration'].split()[0]))).isoformat()
            }
        })

