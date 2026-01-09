from rest_framework import serializers
from .models import DownloadCategory, DownloadFile, DownloadHistory, FileRating
from django.contrib.auth import get_user_model

User = get_user_model()

class DownloadCategorySerializer(serializers.ModelSerializer):
    file_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DownloadCategory
        fields = ['id', 'name', 'description', 'file_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_file_count(self, obj):
        return obj.files.filter(is_active=True).count()

class DownloadFileSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    file_size_display = serializers.CharField(read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    can_download = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DownloadFile
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'file_type', 'file', 'file_url', 'file_size', 'file_size_display',
            'downloads', 'rating', 'required_role', 'is_active',
            'upload_date', 'last_download', 'uploaded_by', 'uploaded_by_name',
            'can_download', 'user_rating'
        ]
        read_only_fields = [
            'downloads', 'rating', 'upload_date', 'last_download', 
            'uploaded_by', 'file_size_display'
        ]
    
    def get_can_download(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_role = getattr(request.user, 'role', 'student')  # Default to student if no role
            return obj.required_role == 'all' or obj.required_role == user_role
        return False
    
    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = FileRating.objects.get(user=request.user, file=obj)
                return rating.rating
            except FileRating.DoesNotExist:
                return None
        return None
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class DownloadHistorySerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source='file.name', read_only=True)
    file_type = serializers.CharField(source='file.file_type', read_only=True)
    file_size = serializers.CharField(source='file.file_size_display', read_only=True)
    category_name = serializers.CharField(source='file.category.name', read_only=True)
    
    class Meta:
        model = DownloadHistory
        fields = [
            'id', 'file', 'file_name', 'file_type', 'file_size', 
            'category_name', 'download_date', 'ip_address'
        ]
        read_only_fields = ['download_date', 'ip_address']

class FileRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    file_name = serializers.CharField(source='file.name', read_only=True)
    
    class Meta:
        model = FileRating
        fields = ['id', 'file', 'file_name', 'user', 'user_name', 'rating', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DownloadStatsSerializer(serializers.Serializer):
    total_downloads = serializers.IntegerField()
    total_files = serializers.IntegerField()
    pdf_count = serializers.IntegerField()
    most_popular_downloads = serializers.IntegerField()
    category_stats = serializers.DictField()
    recent_downloads = serializers.IntegerField()
    user_download_count = serializers.IntegerField()