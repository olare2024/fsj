from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.http import FileResponse, Http404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import DownloadCategory, DownloadFile, DownloadHistory, FileRating
from .serializers import (
    DownloadCategorySerializer, DownloadFileSerializer, 
    DownloadHistorySerializer, FileRatingSerializer, DownloadStatsSerializer
)
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class DownloadCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DownloadCategory.objects.all()
    serializer_class = DownloadCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class DownloadFileViewSet(viewsets.ModelViewSet):
    serializer_class = DownloadFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'file_type', 'required_role', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'downloads', 'upload_date', 'file_size', 'rating']
    ordering = ['-upload_date']
    
    def get_queryset(self):
        queryset = DownloadFile.objects.filter(is_active=True).select_related('category', 'uploaded_by')
        
        # Apply additional filters from query parameters
        category_name = self.request.query_params.get('category', None)
        if category_name and category_name != 'all':
            queryset = queryset.filter(category__name=category_name)
        
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) | 
                Q(description__icontains=search_term)
            )
        
        # Role-based filtering
        user_role = getattr(self.request.user, 'role', 'student')
        queryset = queryset.filter(
            Q(required_role='all') | Q(required_role=user_role)
        )
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def download(self, request, pk=None):
        """Download a file and track the download"""
        try:
            file_obj = self.get_object()
            
            # Check if user has permission to download
            user_role = getattr(request.user, 'role', 'student')
            if not (file_obj.required_role == 'all' or file_obj.required_role == user_role):
                return Response(
                    {'error': 'You do not have permission to download this file.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update download statistics
            file_obj.downloads += 1
            file_obj.last_download = timezone.now()
            file_obj.save()
            
            # Record download history
            DownloadHistory.objects.create(
                user=request.user,
                file=file_obj,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Serve file for download
            response = FileResponse(
                file_obj.file.open('rb'),
                as_attachment=True,
                filename=f"{file_obj.name}.{file_obj.file_type}"
            )
            
            logger.info(f"File downloaded: {file_obj.name} by user {request.user.username}")
            return response
            
        except DownloadFile.DoesNotExist:
            raise Http404("File not found")
        except Exception as e:
            logger.error(f"Download error for file {pk}: {str(e)}")
            return Response(
                {'error': 'An error occurred while downloading the file.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular downloads (top 3 by download count)"""
        popular_files = self.get_queryset().order_by('-downloads')[:3]
        serializer = self.get_serializer(popular_files, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive download statistics"""
        # Overall statistics
        total_downloads = DownloadFile.objects.aggregate(
            total=Count('downloads')
        )['total'] or 0
        
        total_files = DownloadFile.objects.filter(is_active=True).count()
        pdf_count = DownloadFile.objects.filter(file_type='pdf', is_active=True).count()
        
        # Most popular download count
        most_popular = DownloadFile.objects.filter(is_active=True).order_by('-downloads').first()
        most_popular_downloads = most_popular.downloads if most_popular else 0
        
        # Recent downloads (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_downloads = DownloadHistory.objects.filter(
            download_date__gte=thirty_days_ago
        ).count()
        
        # User's download count
        user_download_count = DownloadHistory.objects.filter(user=request.user).count()
        
        # Category statistics
        category_stats = {}
        for category in DownloadCategory.objects.all():
            count = category.files.filter(is_active=True).count()
            if count > 0:
                category_stats[category.name] = count
        
        stats_data = {
            'total_downloads': total_downloads,
            'total_files': total_files,
            'pdf_count': pdf_count,
            'most_popular_downloads': most_popular_downloads,
            'category_stats': category_stats,
            'recent_downloads': recent_downloads,
            'user_download_count': user_download_count,
        }
        
        serializer = DownloadStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download_history(self, request, pk=None):
        """Get download history for a specific file"""
        file_history = DownloadHistory.objects.filter(file_id=pk).select_related('user').order_by('-download_date')
        serializer = DownloadHistorySerializer(file_history, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class DownloadHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DownloadHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['download_date']
    ordering = ['-download_date']
    
    def get_queryset(self):
        return DownloadHistory.objects.filter(user=self.request.user).select_related('file', 'file__category')

class FileRatingViewSet(viewsets.ModelViewSet):
    serializer_class = FileRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FileRating.objects.filter(user=self.request.user).select_related('file')
    
    def perform_create(self, serializer):
        file_id = self.request.data.get('file')
        rating_value = self.request.data.get('rating')
        
        # Update or create rating
        rating, created = FileRating.objects.update_or_create(
            user=self.request.user,
            file_id=file_id,
            defaults={'rating': rating_value}
        )
        
        logger.info(f"Rating {'created' if created else 'updated'} for file {file_id} by user {self.request.user.username}")