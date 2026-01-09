"""
administration/views.py
API views for Delvok Academy Administration.
"""

import logging
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article, CarouselImage, AccessLog, School, Day
from .serializers import (
    ArticleSerializer, ArticleListSerializer,
    CarouselImageSerializer, CarouselImageListSerializer,
    AccessLogSerializer, AccessLogListSerializer,
    SchoolSerializer, SchoolListSerializer,
    DaySerializer, DayListSerializer,
    DashboardStatisticsSerializer, SchoolDashboardSerializer,
    BulkArticleUpdateSerializer, BulkCarouselUpdateSerializer,
    RecentActivitySerializer
)
from .permissions import (
    IsAdminOrReadOnly, CanManageArticles, CanManageCarousel,
    CanViewAccessLogs, CanManageSchool, CanManageDays
)

logger = logging.getLogger(__name__)


# ==================== PAGINATION CLASSES ====================

class StandardPagination(PageNumberPagination):
    """Standard pagination class"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargePagination(PageNumberPagination):
    """Large pagination class for lists"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


# ==================== FILTER CLASSES ====================

class ArticleFilter(filters.BaseFilterBackend):
    """Custom filter for Article model"""
    
    def filter_queryset(self, request, queryset, view):
        # Filter by category
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by status
        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by featured
        featured = request.query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')
        
        # Filter by pinned
        pinned = request.query_params.get('pinned')
        if pinned is not None:
            queryset = queryset.filter(pinned=pinned.lower() == 'true')
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(published_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(published_at__lte=end_date)
        
        # Filter by target audience
        role = request.query_params.get('target_role')
        if role:
            queryset = queryset.filter(target_roles__contains=[role])
        
        grade = request.query_params.get('target_grade')
        if grade:
            queryset = queryset.filter(target_grades__contains=[grade])
        
        return queryset


class AccessLogFilter(filters.BaseFilterBackend):
    """Custom filter for AccessLog model"""
    
    def filter_queryset(self, request, queryset, view):
        # Filter by login type
        login_type = request.query_params.get('login_type')
        if login_type:
            queryset = queryset.filter(login_type=login_type)
        
        # Filter by security level
        security_level = request.query_params.get('security_level')
        if security_level:
            queryset = queryset.filter(security_level=security_level)
        
        # Filter by suspicious flag
        is_suspicious = request.query_params.get('is_suspicious')
        if is_suspicious is not None:
            queryset = queryset.filter(is_suspicious=is_suspicious.lower() == 'true')
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        
        # Filter by IP address
        ip_address = request.query_params.get('ip_address')
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        # Filter by country
        country = request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        return queryset


# ==================== VIEWSETS ====================

class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for Article model"""
    queryset = Article.objects.filter(is_active=True)
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, CanManageArticles]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ArticleFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'featured', 'pinned']
    search_fields = ['title', 'content', 'summary', 'created_by__email']
    ordering_fields = ['published_at', 'created_at', 'views', 'likes', 'shares']
    ordering = ['-published_at', '-created_at']
    
    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return ArticleListSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # For non-admin users, only show published articles
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(status='published') & Q(published_at__lte=timezone.now())
            )
            
            # Filter by target audience if applicable
            user_role = self.request.user.role
            if user_role:
                queryset = queryset.filter(
                    Q(target_roles__contains=[user_role]) | Q(target_roles=[])
                )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by and updated_by on create"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by on update"""
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Increment article view count"""
        article = self.get_object()
        article.increment_views()
        return Response({'views': article.views})
    
    @action(detail=True, methods=['post'])
    def increment_likes(self, request, pk=None):
        """Increment article like count"""
        article = self.get_object()
        article.increment_likes()
        return Response({'likes': article.likes})
    
    @action(detail=True, methods=['post'])
    def increment_shares(self, request, pk=None):
        """Increment article share count"""
        article = self.get_object()
        article.increment_shares()
        return Response({'shares': article.shares})
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an article"""
        article = self.get_object()
        if article.status != 'published':
            article.status = 'published'
            if not article.published_at:
                article.published_at = timezone.now()
            article.save()
        return Response({'status': 'published', 'published_at': article.published_at})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive an article"""
        article = self.get_object()
        article.status = 'archived'
        article.save()
        return Response({'status': 'archived'})
    
    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        """Feature an article"""
        article = self.get_object()
        article.featured = True
        article.save()
        return Response({'featured': True})
    
    @action(detail=True, methods=['post'])
    def unfeature(self, request, pk=None):
        """Unfeature an article"""
        article = self.get_object()
        article.featured = False
        article.save()
        return Response({'featured': False})
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update articles"""
        serializer = BulkArticleUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        articles = Article.objects.filter(id__in=data['ids'], is_active=True)
        
        update_data = {}
        if 'status' in data:
            update_data['status'] = data['status']
        if 'featured' in data:
            update_data['featured'] = data['featured']
        if 'pinned' in data:
            update_data['pinned'] = data['pinned']
        if 'category' in data:
            update_data['category'] = data['category']
        
        if update_data:
            update_data['updated_by'] = request.user
            articles.update(**update_data)
        
        return Response({'updated': articles.count()})
    
    @action(detail=False, methods=['get'])
    def categories_summary(self, request):
        """Get summary of articles by category"""
        summary = Article.objects.filter(is_active=True).values('category').annotate(
            count=Count('id'),
            published=Count('id', filter=Q(status='published')),
            drafts=Count('id', filter=Q(status='draft')),
            archived=Count('id', filter=Q(status='archived'))
        ).order_by('category')
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular articles"""
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 10))
        
        since_date = timezone.now() - timezone.timedelta(days=days)
        
        popular_articles = Article.objects.filter(
            is_active=True,
            status='published',
            published_at__gte=since_date
        ).order_by('-views')[:limit]
        
        serializer = ArticleListSerializer(popular_articles, many=True)
        return Response(serializer.data)


class CarouselImageViewSet(viewsets.ModelViewSet):
    """ViewSet for CarouselImage model"""
    queryset = CarouselImage.objects.filter(is_active=True)
    serializer_class = CarouselImageSerializer
    permission_classes = [IsAuthenticated, CanManageCarousel]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['position', 'type', 'active']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'created_at', 'views', 'clicks']
    ordering = ['position', 'order', '-created_at']
    
    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return CarouselImageListSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        """Filter queryset based on active status"""
        queryset = super().get_queryset()
        
        # For public endpoints, only show active and scheduled items
        if self.action in ['list', 'retrieve'] and not self.request.user.is_staff:
            queryset = queryset.filter(active=True, is_active=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by and updated_by on create"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by on update"""
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Increment carousel view count"""
        carousel = self.get_object()
        carousel.increment_views()
        return Response({'views': carousel.views})
    
    @action(detail=True, methods=['post'])
    def increment_clicks(self, request, pk=None):
        """Increment carousel click count"""
        carousel = self.get_object()
        carousel.increment_clicks()
        return Response({'clicks': carousel.clicks})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate carousel image"""
        carousel = self.get_object()
        carousel.active = True
        carousel.save()
        return Response({'active': True})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate carousel image"""
        carousel = self.get_object()
        carousel.active = False
        carousel.save()
        return Response({'active': False})
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update carousel images"""
        serializer = BulkCarouselUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        carousel_images = CarouselImage.objects.filter(id__in=data['ids'], is_active=True)
        
        update_data = {}
        if 'active' in data:
            update_data['active'] = data['active']
        if 'position' in data:
            update_data['position'] = data['position']
        
        if update_data:
            update_data['updated_by'] = request.user
            carousel_images.update(**update_data)
        
        return Response({'updated': carousel_images.count()})
    
    @action(detail=False, methods=['get'])
    def active_for_position(self, request):
        """Get active carousel images for specific position"""
        position = request.query_params.get('position', 'main')
        
        carousel_images = CarouselImage.objects.filter(
            position=position,
            active=True,
            is_active=True
        ).order_by('order')
        
        serializer = CarouselImageListSerializer(carousel_images, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def positions_summary(self, request):
        """Get summary of carousel images by position"""
        summary = CarouselImage.objects.filter(is_active=True).values('position').annotate(
            total=Count('id'),
            active=Count('id', filter=Q(active=True)),
            inactive=Count('id', filter=Q(active=False))
        ).order_by('position')
        
        return Response(summary)


class AccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AccessLog model (read-only)"""
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated, CanViewAccessLogs]
    pagination_class = LargePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, AccessLogFilter, filters.OrderingFilter]
    filterset_fields = ['login_type', 'security_level', 'is_suspicious', 'country']
    search_fields = ['user__email', 'username_attempt', 'ip_address', 'user_agent', 'country', 'city']
    ordering_fields = ['timestamp', 'threat_score']
    ordering = ['-timestamp']
    
    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return AccessLogListSerializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=['get'])
    def security_summary(self, request):
        """Get security summary"""
        days = int(request.query_params.get('days', 7))
        
        since_date = timezone.now() - timezone.timedelta(days=days)
        
        summary = {
            'total_logs': AccessLog.objects.filter(timestamp__gte=since_date).count(),
            'successful_logins': AccessLog.objects.filter(
                timestamp__gte=since_date,
                login_type='success'
            ).count(),
            'failed_logins': AccessLog.objects.filter(
                timestamp__gte=since_date,
                login_type='failed'
            ).count(),
            'suspicious_attempts': AccessLog.objects.filter(
                timestamp__gte=since_date,
                is_suspicious=True
            ).count(),
            'unique_ips': AccessLog.objects.filter(
                timestamp__gte=since_date
            ).values('ip_address').distinct().count(),
            'unique_users': AccessLog.objects.filter(
                timestamp__gte=since_date
            ).values('user').distinct().count(),
            'by_country': AccessLog.objects.filter(
                timestamp__gte=since_date
            ).exclude(country__isnull=True).values('country').annotate(
                count=Count('id'),
                suspicious=Count('id', filter=Q(is_suspicious=True))
            ).order_by('-count')[:10],
            'by_device': AccessLog.objects.filter(
                timestamp__gte=since_date
            ).values('user_agent').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
        }
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def today_summary(self, request):
        """Get today's access log summary"""
        today = timezone.now().date()
        
        summary = {
            'today_logs': AccessLog.objects.filter(timestamp__date=today).count(),
            'successful_logins': AccessLog.objects.filter(
                timestamp__date=today,
                login_type='success'
            ).count(),
            'failed_logins': AccessLog.objects.filter(
                timestamp__date=today,
                login_type='failed'
            ).count(),
            'suspicious_attempts': AccessLog.objects.filter(
                timestamp__date=today,
                is_suspicious=True
            ).count(),
            'unique_ips_today': AccessLog.objects.filter(
                timestamp__date=today
            ).values('ip_address').distinct().count(),
            'recent_logs': AccessLog.objects.filter(
                timestamp__date=today
            ).order_by('-timestamp')[:10]
        }
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def flag_suspicious(self, request, pk=None):
        """Flag access log as suspicious"""
        access_log = self.get_object()
        reason = request.data.get('reason', 'Manually flagged by admin')
        
        access_log.flag_as_suspicious(reason)
        return Response({
            'is_suspicious': access_log.is_suspicious,
            'security_level': access_log.security_level,
            'threat_score': access_log.threat_score
        })
    
    @action(detail=True, methods=['post'])
    def flag_normal(self, request, pk=None):
        """Flag access log as normal"""
        access_log = self.get_object()
        
        access_log.is_suspicious = False
        access_log.security_level = 'normal'
        access_log.suspicious_reason = ''
        access_log.save()
        
        return Response({
            'is_suspicious': access_log.is_suspicious,
            'security_level': access_log.security_level
        })


class SchoolViewSet(viewsets.ModelViewSet):
    """ViewSet for School model"""
    queryset = School.objects.filter(is_active=True)
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, CanManageSchool]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'school_type', 'students_gender', 'ownership']
    search_fields = ['name', 'code', 'address', 'school_email', 'telephone', 'principal_name']
    ordering_fields = ['name', 'code', 'created_at', 'established_date']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return SchoolListSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """Set created_by and updated_by on create"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by on update"""
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate school"""
        school = self.get_object()
        if school.activate():
            return Response({'active': True, 'message': f"School '{school.name}' activated successfully."})
        return Response({'active': False, 'message': f"Failed to activate school '{school.name}'."},
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate school"""
        school = self.get_object()
        school.deactivate()
        return Response({'active': False, 'message': f"School '{school.name}' deactivated successfully."})
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get school statistics"""
        school = self.get_object()
        stats = school.get_statistics()
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get school dashboard data"""
        school = self.get_object()
        serializer = SchoolDashboardSerializer(school)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_school(self, request):
        """Get active school"""
        active_school = School.objects.filter(active=True, is_active=True).first()
        if active_school:
            serializer = SchoolSerializer(active_school)
            return Response(serializer.data)
        return Response({'detail': 'No active school found.'}, status=status.HTTP_404_NOT_FOUND)


class DayViewSet(viewsets.ModelViewSet):
    """ViewSet for Day model"""
    queryset = Day.objects.filter(is_active=True)
    serializer_class = DaySerializer
    permission_classes = [IsAuthenticated, CanManageDays]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['day_type', 'is_school_day', 'is_instructional_day']
    search_fields = ['full_name', 'short_name', 'special_instructions']
    ordering_fields = ['day_number', 'order']
    ordering = ['day_number']
    
    def get_serializer_class(self):
        """Use different serializer for list view"""
        if self.action == 'list':
            return DayListSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """Set created_by and updated_by on create"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by on update"""
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_active = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def week_schedule(self, request):
        """Get full week schedule"""
        days = Day.objects.filter(is_active=True).order_by('day_number')
        serializer = DaySerializer(days, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def school_days(self, request):
        """Get school days only"""
        days = Day.objects.filter(
            is_active=True,
            is_school_day=True
        ).order_by('day_number')
        serializer = DayListSerializer(days, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def period_schedule(self, request, pk=None):
        """Get period schedule for specific day"""
        day = self.get_object()
        schedule = day.get_period_schedule()
        return Response(schedule)


# ==================== CUSTOM VIEWS ====================

class DashboardView(APIView):
    """Dashboard view for administration"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get dashboard statistics"""
        from django.apps import apps
        
        try:
            # Get counts using utility functions to avoid circular imports
            from .utils import get_model_counts, get_student_count, get_staff_count, get_teacher_count
            
            stats = get_model_counts()
            
            # Add user counts
            stats.update({
                'total_students': get_student_count(),
                'total_teachers': get_teacher_count(),
                'total_staff': get_staff_count(),
            })
            
            serializer = DashboardStatisticsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting dashboard statistics: {e}")
            return Response(
                {'error': 'Failed to load dashboard statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecentActivityView(APIView):
    """Recent activity view"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get recent activity across all models"""
        try:
            activities = []
            
            # Recent articles
            recent_articles = Article.objects.filter(
                is_active=True
            ).order_by('-updated_at')[:5]
            
            for article in recent_articles:
                activities.append({
                    'model': 'Article',
                    'action': 'updated' if article.updated_at > article.created_at else 'created',
                    'object_id': article.id,
                    'object_name': article.title,
                    'timestamp': article.updated_at,
                    'user': {
                        'id': article.updated_by.id if article.updated_by else None,
                        'email': article.updated_by.email if article.updated_by else None,
                        'name': f"{article.updated_by.first_name} {article.updated_by.last_name}".strip() 
                               if article.updated_by else None
                    }
                })
            
            # Recent access logs (suspicious only)
            recent_logs = AccessLog.objects.filter(
                is_suspicious=True
            ).order_by('-timestamp')[:5]
            
            for log in recent_logs:
                activities.append({
                    'model': 'AccessLog',
                    'action': 'suspicious_login',
                    'object_id': log.id,
                    'object_name': f"Login from {log.ip_address}",
                    'timestamp': log.timestamp,
                    'user': {
                        'id': log.user.id if log.user else None,
                        'email': log.user.email if log.user else log.username_attempt,
                        'name': f"{log.user.first_name} {log.user.last_name}".strip() 
                               if log.user else None
                    }
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            serializer = RecentActivitySerializer(activities, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return Response(
                {'error': 'Failed to load recent activity'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicArticlesView(APIView):
    """Public articles view (no authentication required)"""
    permission_classes = []
    
    def get(self, request):
        """Get published articles for public viewing"""
        try:
            articles = Article.objects.filter(
                is_active=True,
                status='published',
                published_at__lte=timezone.now()
            ).order_by('-published_at', '-created_at')
            
            # Apply filters
            category = request.query_params.get('category')
            if category:
                articles = articles.filter(category=category)
            
            featured = request.query_params.get('featured')
            if featured is not None:
                articles = articles.filter(featured=featured.lower() == 'true')
            
            pinned = request.query_params.get('pinned')
            if pinned is not None:
                articles = articles.filter(pinned=pinned.lower() == 'true')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = articles.count()
            articles = articles[start:end]
            
            serializer = ArticleListSerializer(articles, many=True)
            
            return Response({
                'count': total_count,
                'next': end < total_count,
                'previous': page > 1,
                'page': page,
                'page_size': page_size,
                'results': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting public articles: {e}")
            return Response(
                {'error': 'Failed to load articles'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicCarouselView(APIView):
    """Public carousel view (no authentication required)"""
    permission_classes = []
    
    def get(self, request):
        """Get active carousel images for public viewing"""
        try:
            position = request.query_params.get('position', 'main')
            
            carousel_images = CarouselImage.objects.filter(
                position=position,
                active=True,
                is_active=True,
                start_date__lte=timezone.now()
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
            ).order_by('order')
            
            serializer = CarouselImageListSerializer(carousel_images, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting public carousel: {e}")
            return Response(
                {'error': 'Failed to load carousel images'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SchoolContactView(APIView):
    """School contact information view (no authentication required)"""
    permission_classes = []
    
    def get(self, request):
        """Get active school contact information"""
        try:
            active_school = School.objects.filter(active=True, is_active=True).first()
            if not active_school:
                return Response(
                    {'error': 'No active school found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            contact_info = active_school.get_contact_info()
            return Response(contact_info)
            
        except Exception as e:
            logger.error(f"Error getting school contact info: {e}")
            return Response(
                {'error': 'Failed to load contact information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== HELPER VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_permissions(request):
    """Check user permissions for administration"""
    from .permissions import (
        CanManageArticles, CanManageCarousel, CanViewAccessLogs,
        CanManageSchool, CanManageDays
    )
    
    permissions = {
        'can_manage_articles': CanManageArticles().has_permission(request, None),
        'can_manage_carousel': CanManageCarousel().has_permission(request, None),
        'can_view_access_logs': CanViewAccessLogs().has_permission(request, None),
        'can_manage_school': CanManageSchool().has_permission(request, None),
        'can_manage_days': CanManageDays().has_permission(request, None),
        'is_admin': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    }
    
    return Response(permissions)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_access_log(request):
    """Create access log entry (for testing)"""
    from .models import AccessLog
    
    try:
        serializer = AccessLogSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating access log: {e}")
        return Response(
            {'error': 'Failed to create access log'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== ERROR HANDLING ====================

class AdministrationErrorHandler:
    """Error handler for administration views"""
    
    @staticmethod
    def handle_validation_error(exc, context):
        """Handle validation errors"""
        return Response(
            {
                'error': 'Validation Error',
                'details': exc.detail
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def handle_not_found_error(exc, context):
        """Handle not found errors"""
        return Response(
            {
                'error': 'Not Found',
                'detail': str(exc)
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def handle_permission_error(exc, context):
        """Handle permission errors"""
        return Response(
            {
                'error': 'Permission Denied',
                'detail': str(exc)
            },
            status=status.HTTP_403_FORBIDDEN
        )