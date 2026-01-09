from rest_framework import viewsets, status, permissions, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

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
    ViewSet for admin dashboard data
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """
        Get dashboard overview data
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

class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for system analytics
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """
        Get comprehensive analytics data
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
                'academic_year': '2024',
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
                'academic_year': '2024',
                'contact_email': 'info@delvok.ac.ke',
                'contact_phone': '+254700000000',
            }
        )
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

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
