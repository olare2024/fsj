"""
administration/serializers.py
Serializers for Delvok Academy Administration models.
"""

from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Article, CarouselImage, AccessLog, School, Day
from academics.serializers import AcademicYearSerializer


# ==================== HELPER SERIALIZERS ====================

class UserMinimalSerializer(serializers.Serializer):
    """Minimal user serializer for related fields"""
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


# ==================== MAIN SERIALIZERS ====================

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    engagement_rate = serializers.FloatField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    created_by_info = UserMinimalSerializer(source='created_by', read_only=True)
    updated_by_info = UserMinimalSerializer(source='updated_by', read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'summary', 'category', 'category_display',
            'status', 'status_display', 'picture', 'attachments', 'featured',
            'pinned', 'target_roles', 'target_grades', 'published_at',
            'expire_at', 'views', 'likes', 'shares', 'meta_title',
            'meta_description', 'keywords', 'reading_time', 'engagement_rate',
            'is_published', 'created_by_info', 'updated_by_info', 'created_at',
            'updated_at', 'is_active'
        ]
        read_only_fields = ['views', 'likes', 'shares', 'created_by', 'updated_by']
    
    def validate(self, data):
        """Validate article data"""
        if data.get('status') == 'published' and not data.get('published_at'):
            data['published_at'] = timezone.now()
        
        # Validate publish date for scheduled articles
        if data.get('published_at') and data.get('published_at') > timezone.now():
            if data.get('status') != 'scheduled':
                raise serializers.ValidationError({
                    'published_at': _('Published date cannot be in the future for non-scheduled articles')
                })
        
        # Validate expiration date
        if data.get('expire_at') and data.get('published_at'):
            if data.get('expire_at') <= data.get('published_at'):
                raise serializers.ValidationError({
                    'expire_at': _('Expiration date must be after publish date')
                })
        
        return data
    
    def create(self, validated_data):
        """Create article with current user as creator"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        # Auto-generate summary if empty
        if not validated_data.get('summary') and validated_data.get('content'):
            content = validated_data['content']
            validated_data['summary'] = content[:497] + '...' if len(content) > 500 else content
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update article with current user as updater"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class ArticleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for article listings"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'summary', 'category', 'category_display', 'status',
            'status_display', 'picture', 'featured', 'pinned', 'published_at',
            'views', 'likes', 'shares', 'reading_time', 'is_published',
            'created_by_name', 'created_at'
        ]
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return None


class CarouselImageSerializer(serializers.ModelSerializer):
    """Serializer for CarouselImage model"""
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    click_through_rate = serializers.FloatField(read_only=True)
    created_by_info = UserMinimalSerializer(source='created_by', read_only=True)
    updated_by_info = UserMinimalSerializer(source='updated_by', read_only=True)
    
    class Meta:
        model = CarouselImage
        fields = [
            'id', 'title', 'description', 'picture', 'thumbnail', 'position',
            'position_display', 'type', 'type_display', 'order', 'active',
            'link_url', 'link_text', 'open_in_new_tab', 'start_date',
            'end_date', 'views', 'clicks', 'overlay_color', 'text_color',
            'is_active', 'click_through_rate', 'created_by_info',
            'updated_by_info', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['views', 'clicks', 'created_by', 'updated_by']
    
    def validate(self, data):
        """Validate carousel image data"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError({
                    'end_date': _('End date must be after start date')
                })
        
        # Auto-generate link text if not provided
        if data.get('link_url') and not data.get('link_text'):
            data['link_text'] = _('Learn More')
        
        return data
    
    def create(self, validated_data):
        """Create carousel image with current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update carousel image with current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class CarouselImageListSerializer(serializers.ModelSerializer):
    """Simplified serializer for carousel image listings"""
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    click_through_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = CarouselImage
        fields = [
            'id', 'title', 'picture', 'thumbnail', 'position', 'position_display',
            'order', 'active', 'link_url', 'start_date', 'end_date', 'views',
            'clicks', 'is_active', 'click_through_rate', 'created_at'
        ]


class AccessLogSerializer(serializers.ModelSerializer):
    """Serializer for AccessLog model"""
    login_type_display = serializers.CharField(source='get_login_type_display', read_only=True)
    security_level_display = serializers.CharField(source='get_security_level_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField(read_only=True)
    device_info = serializers.SerializerMethodField(read_only=True)
    location_summary = serializers.SerializerMethodField(read_only=True)
    needs_review = serializers.BooleanField(read_only=True)
    session_duration_minutes = serializers.FloatField(read_only=True)
    
    class Meta:
        model = AccessLog
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'username_attempt',
            'user_agent', 'ip_address', 'forwarded_ip', 'session_key',
            'device_id', 'login_type', 'login_type_display', 'usage_description',
            'location_data', 'country', 'city', 'latitude', 'longitude',
            'security_level', 'security_level_display', 'is_suspicious',
            'suspicious_reason', 'threat_score', 'auth_method',
            'two_factor_used', 'two_factor_method', 'timestamp', 'duration',
            'device_info', 'location_summary', 'needs_review',
            'session_duration_minutes'
        ]
        read_only_fields = ['timestamp']
    
    def get_user_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return None
    
    def get_device_info(self, obj):
        return obj.get_device_summary()
    
    def get_location_summary(self, obj):
        return obj.get_location_summary()
    
    def create(self, validated_data):
        """Create access log entry"""
        # Typically access logs are created automatically, not via API
        return super().create(validated_data)


class AccessLogListSerializer(serializers.ModelSerializer):
    """Simplified serializer for access log listings"""
    login_type_display = serializers.CharField(source='get_login_type_display', read_only=True)
    security_level_display = serializers.CharField(source='get_security_level_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    device_summary = serializers.SerializerMethodField(read_only=True)
    needs_review = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AccessLog
        fields = [
            'id', 'user_email', 'login_type', 'login_type_display',
            'ip_address', 'country', 'city', 'security_level',
            'security_level_display', 'is_suspicious', 'threat_score',
            'timestamp', 'device_summary', 'needs_review'
        ]
    
    def get_device_summary(self, obj):
        device_info = obj.get_device_summary()
        return f"{device_info.get('os', 'Unknown')} / {device_info.get('browser', 'Unknown')}"


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model"""
    school_type_display = serializers.CharField(source='get_school_type_display', read_only=True)
    students_gender_display = serializers.CharField(source='get_students_gender_display', read_only=True)
    ownership_display = serializers.CharField(source='get_ownership_display', read_only=True)
    default_curriculum_display = serializers.CharField(source='get_default_curriculum_display', read_only=True)
    current_academic_year_info = AcademicYearSerializer(source='current_academic_year', read_only=True)
    statistics = serializers.SerializerMethodField(read_only=True)
    contact_info = serializers.SerializerMethodField(read_only=True)
    social_links = serializers.SerializerMethodField(read_only=True)
    academic_info = serializers.SerializerMethodField(read_only=True)
    created_by_info = UserMinimalSerializer(source='created_by', read_only=True)
    updated_by_info = UserMinimalSerializer(source='updated_by', read_only=True)
    
    class Meta:
        model = School
        fields = [
            'id', 'active', 'name', 'code', 'current_academic_year',
            'current_academic_year_info', 'default_curriculum',
            'default_curriculum_display', 'supported_curriculums',
            'address', 'school_type', 'school_type_display',
            'students_gender', 'students_gender_display', 'ownership',
            'ownership_display', 'telephone', 'mobile', 'school_email',
            'website', 'principal_name', 'principal_email', 'principal_phone',
            'mission', 'vision', 'motto', 'core_values', 'history',
            'school_logo', 'school_banner', 'gallery', 'language',
            'additional_languages', 'academic_calendar', 'facilities',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url',
            'youtube_url', 'established_date', 'registration_date',
            'registration_number', 'statistics', 'contact_info',
            'social_links', 'academic_info', 'created_by_info',
            'updated_by_info', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_by', 'updated_by']
    
    def get_statistics(self, obj):
        return obj.get_statistics()
    
    def get_contact_info(self, obj):
        return obj.get_contact_info()
    
    def get_social_links(self, obj):
        return obj.get_social_links()
    
    def get_academic_info(self, obj):
        return obj.get_academic_info()
    
    def validate(self, data):
        """Validate school data"""
        errors = {}
        
        # Active school validation
        if data.get('active'):
            existing_active = School.objects.filter(active=True)
            if self.instance:
                existing_active = existing_active.exclude(pk=self.instance.pk)
            
            if existing_active.exists():
                errors['active'] = _(
                    'Only one school can be active at a time. '
                    'Please deactivate the current active school first.'
                )
        
        # Date validation
        if data.get('established_date') and data.get('established_date') > timezone.now().date():
            errors['established_date'] = _('Established date cannot be in the future')
        
        if data.get('registration_date') and data.get('established_date'):
            if data['registration_date'] < data['established_date']:
                errors['registration_date'] = _('Registration date cannot be before established date')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create school with current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        # Generate code if not provided
        if not validated_data.get('code') and validated_data.get('name'):
            validated_data['code'] = validated_data['name'].upper().replace(' ', '_')[:20]
        
        # Ensure default curriculum is in supported curricula
        default_curriculum = validated_data.get('default_curriculum')
        supported_curriculums = validated_data.get('supported_curriculums', [])
        
        if default_curriculum and default_curriculum not in supported_curriculums:
            validated_data['supported_curriculums'] = supported_curriculums + [default_curriculum]
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update school with current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        # Handle active school deactivation
        if validated_data.get('active') and instance.active != validated_data['active']:
            # This will be handled by the signal
            pass
        
        return super().update(instance, validated_data)


class SchoolListSerializer(serializers.ModelSerializer):
    """Simplified serializer for school listings"""
    school_type_display = serializers.CharField(source='get_school_type_display', read_only=True)
    students_gender_display = serializers.CharField(source='get_students_gender_display', read_only=True)
    ownership_display = serializers.CharField(source='get_ownership_display', read_only=True)
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'code', 'active', 'school_type', 'school_type_display',
            'students_gender', 'students_gender_display', 'ownership',
            'ownership_display', 'telephone', 'school_email', 'website',
            'school_logo', 'established_date', 'created_at'
        ]


class DaySerializer(serializers.ModelSerializer):
    """Serializer for Day model"""
    day_number_display = serializers.CharField(source='get_day_number_display', read_only=True)
    day_type_display = serializers.CharField(source='get_day_type_display', read_only=True)
    is_weekend = serializers.BooleanField(read_only=True)
    total_instructional_hours = serializers.FloatField(read_only=True)
    schedule_template = serializers.SerializerMethodField(read_only=True)
    created_by_info = UserMinimalSerializer(source='created_by', read_only=True)
    updated_by_info = UserMinimalSerializer(source='updated_by', read_only=True)
    
    class Meta:
        model = Day
        fields = [
            'id', 'day_number', 'day_number_display', 'short_name', 'full_name',
            'day_type', 'day_type_display', 'is_school_day', 'is_instructional_day',
            'start_time', 'end_time', 'break_start_time', 'break_end_time',
            'lunch_start_time', 'lunch_end_time', 'total_periods',
            'period_duration', 'special_instructions', 'color_code', 'weight',
            'is_weekend', 'total_instructional_hours', 'schedule_template',
            'created_by_info', 'updated_by_info', 'created_at', 'updated_at',
            'is_active'
        ]
        read_only_fields = ['created_by', 'updated_by']
    
    def get_schedule_template(self, obj):
        return obj.schedule_template
    
    def validate(self, data):
        """Validate day configuration"""
        errors = {}
        
        # Time validation
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                errors['end_time'] = _('End time must be after start time')
        
        if data.get('break_start_time') and data.get('break_end_time'):
            if data['break_start_time'] >= data['break_end_time']:
                errors['break_end_time'] = _('Break end time must be after break start time')
        
        if data.get('lunch_start_time') and data.get('lunch_end_time'):
            if data['lunch_start_time'] >= data['lunch_end_time']:
                errors['lunch_end_time'] = _('Lunch end time must be after lunch start time')
        
        # Period validation
        if data.get('total_periods'):
            if data['total_periods'] < 1 or data['total_periods'] > 12:
                errors['total_periods'] = _('Total periods must be between 1 and 12')
        
        if data.get('period_duration'):
            if data['period_duration'] < 5 or data['period_duration'] > 120:
                errors['period_duration'] = _('Period duration must be between 5 and 120 minutes')
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create day with current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update day with current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class DayListSerializer(serializers.ModelSerializer):
    """Simplified serializer for day listings"""
    day_number_display = serializers.CharField(source='get_day_number_display', read_only=True)
    day_type_display = serializers.CharField(source='get_day_type_display', read_only=True)
    is_weekend = serializers.BooleanField(read_only=True)
    total_instructional_hours = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Day
        fields = [
            'id', 'day_number', 'day_number_display', 'short_name', 'full_name',
            'day_type', 'day_type_display', 'is_school_day', 'is_instructional_day',
            'start_time', 'end_time', 'total_periods', 'period_duration',
            'is_weekend', 'total_instructional_hours', 'created_at'
        ]


# ==================== DASHBOARD SERIALIZERS ====================

class DashboardStatisticsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_articles = serializers.IntegerField()
    active_carousel_images = serializers.IntegerField()
    access_logs_today = serializers.IntegerField()
    total_schools = serializers.IntegerField()
    active_school = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_staff = serializers.IntegerField()


class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent activity"""
    model = serializers.CharField()
    action = serializers.CharField()
    object_id = serializers.IntegerField()
    object_name = serializers.CharField()
    timestamp = serializers.DateTimeField()
    user = serializers.DictField()


class SchoolDashboardSerializer(serializers.ModelSerializer):
    """Serializer for school dashboard"""
    statistics = serializers.SerializerMethodField(read_only=True)
    recent_articles = serializers.SerializerMethodField(read_only=True)
    active_carousel = serializers.SerializerMethodField(read_only=True)
    recent_access_logs = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'code', 'active', 'school_logo', 'statistics',
            'recent_articles', 'active_carousel', 'recent_access_logs'
        ]
    
    def get_statistics(self, obj):
        return obj.get_statistics()
    
    def get_recent_articles(self, obj):
        articles = Article.objects.filter(
            is_active=True,
            status='published'
        ).order_by('-published_at')[:5]
        return ArticleListSerializer(articles, many=True).data
    
    def get_active_carousel(self, obj):
        carousel = CarouselImage.objects.filter(
            active=True,
            is_active=True
        ).order_by('position', 'order')[:10]
        return CarouselImageListSerializer(carousel, many=True).data
    
    def get_recent_access_logs(self, obj):
        logs = AccessLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).order_by('-timestamp')[:10]
        return AccessLogListSerializer(logs, many=True).data


# ==================== BULK OPERATION SERIALIZERS ====================

class BulkArticleUpdateSerializer(serializers.Serializer):
    """Serializer for bulk article updates"""
    ids = serializers.ListField(child=serializers.IntegerField())
    status = serializers.ChoiceField(choices=Article.ARTICLE_STATUS, required=False)
    featured = serializers.BooleanField(required=False)
    pinned = serializers.BooleanField(required=False)
    category = serializers.ChoiceField(choices=Article.ARTICLE_CATEGORIES, required=False)
    
    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError(_("IDs list cannot be empty"))
        return value


class BulkCarouselUpdateSerializer(serializers.Serializer):
    """Serializer for bulk carousel updates"""
    ids = serializers.ListField(child=serializers.IntegerField())
    active = serializers.BooleanField(required=False)
    position = serializers.ChoiceField(choices=CarouselImage.CAROUSEL_POSITIONS, required=False)
    
    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError(_("IDs list cannot be empty"))
        return value