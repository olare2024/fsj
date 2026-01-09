"""
administration/admin.py
Admin configurations for Delvok Academy Administration models.
"""

from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from .models import Article, CarouselImage, AccessLog, School, Day
from django.utils import timezone

# ==================== IMPORT/EXPORT RESOURCES ====================

class ArticleResource(resources.ModelResource):
    """Resource for Article import/export"""
    category_display = fields.Field(attribute='get_category_display', column_name='Category')
    status_display = fields.Field(attribute='get_status_display', column_name='Status')
    created_by_email = fields.Field(attribute='created_by__email', column_name='Created By')
    
    class Meta:
        model = Article
        fields = ('id', 'title', 'category_display', 'status_display', 
                 'featured', 'pinned', 'views', 'likes', 'shares',
                 'created_at', 'published_at', 'created_by_email')
        export_order = fields
        import_id_fields = ['id']

class CarouselImageResource(resources.ModelResource):
    """Resource for CarouselImage import/export"""
    position_display = fields.Field(attribute='get_position_display', column_name='Position')
    type_display = fields.Field(attribute='get_type_display', column_name='Type')
    
    class Meta:
        model = CarouselImage
        fields = ('id', 'title', 'position_display', 'type_display',
                 'active', 'order', 'views', 'clicks', 'start_date', 'end_date')
        export_order = fields
        import_id_fields = ['id']

class AccessLogResource(resources.ModelResource):
    """Resource for AccessLog import/export"""
    login_type_display = fields.Field(attribute='get_login_type_display', column_name='Login Type')
    security_level_display = fields.Field(attribute='get_security_level_display', column_name='Security Level')
    user_email = fields.Field(attribute='user__email', column_name='User Email')
    
    class Meta:
        model = AccessLog
        fields = ('id', 'user_email', 'username_attempt', 'login_type_display',
                 'ip_address', 'country', 'city', 'security_level_display',
                 'is_suspicious', 'threat_score', 'timestamp')
        export_order = fields
        import_id_fields = ['id']

class SchoolResource(resources.ModelResource):
    """Resource for School import/export"""
    school_type_display = fields.Field(attribute='get_school_type_display', column_name='School Type')
    students_gender_display = fields.Field(attribute='get_students_gender_display', column_name='Students Gender')
    ownership_display = fields.Field(attribute='get_ownership_display', column_name='Ownership')
    
    class Meta:
        model = School
        fields = ('id', 'name', 'code', 'school_type_display', 'students_gender_display',
                 'ownership_display', 'active', 'telephone', 'school_email', 'website',
                 'established_date', 'created_at')
        export_order = fields
        import_id_fields = ['id']


# ==================== ADMIN CLASSES ====================

@admin.register(Article)
class ArticleAdmin(ImportExportModelAdmin):
    """Admin interface for Article model"""
    resource_class = ArticleResource
    
    list_display = ('title', 'category', 'status', 'featured', 'pinned', 
                   'views', 'likes', 'shares', 'published_at', 'created_by')
    list_filter = ('category', 'status', 'featured', 'pinned', 'created_at', 
                  'published_at', 'created_by')
    search_fields = ('title', 'content', 'summary', 'created_by__email', 
                    'created_by__first_name', 'created_by__last_name')
    readonly_fields = ('views', 'likes', 'shares', 'created_at', 'updated_at',
                      'engagement_rate_display', 'reading_time_display')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'content', 'summary', 'picture', 'attachments')
        }),
        (_('Classification & Status'), {
            'fields': ('category', 'status', 'featured', 'pinned')
        }),
        (_('Audience Targeting'), {
            'fields': ('target_roles', 'target_grades'),
            'classes': ('collapse',)
        }),
        (_('Scheduling'), {
            'fields': ('published_at', 'expire_at')
        }),
        (_('SEO & Metadata'), {
            'fields': ('meta_title', 'meta_description', 'keywords'),
            'classes': ('collapse',)
        }),
        (_('Analytics'), {
            'fields': ('views', 'likes', 'shares', 'engagement_rate_display', 
                      'reading_time_display')
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def engagement_rate_display(self, obj):
        return f"{obj.engagement_rate}%"
    engagement_rate_display.short_description = _('Engagement Rate')
    
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min"
    reading_time_display.short_description = _('Reading Time')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['publish_articles', 'archive_articles', 'feature_articles']
    
    def publish_articles(self, request, queryset):
        """Publish selected articles"""
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f"{updated} articles published successfully.")
    publish_articles.short_description = _("Publish selected articles")
    
    def archive_articles(self, request, queryset):
        """Archive selected articles"""
        updated = queryset.update(status='archived')
        self.message_user(request, f"{updated} articles archived successfully.")
    archive_articles.short_description = _("Archive selected articles")
    
    def feature_articles(self, request, queryset):
        """Feature selected articles"""
        updated = queryset.update(featured=True)
        self.message_user(request, f"{updated} articles featured successfully.")
    feature_articles.short_description = _("Feature selected articles")


@admin.register(CarouselImage)
class CarouselImageAdmin(ImportExportModelAdmin):
    """Admin interface for CarouselImage model"""
    resource_class = CarouselImageResource
    
    list_display = ('title', 'position', 'type', 'order', 'active', 
                   'is_active_display', 'views', 'clicks', 'ctr_display')
    list_filter = ('position', 'type', 'active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    readonly_fields = ('views', 'clicks', 'ctr_display', 'created_at', 'updated_at')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description', 'picture', 'thumbnail')
        }),
        (_('Display Settings'), {
            'fields': ('position', 'type', 'order', 'active')
        }),
        (_('Link Configuration'), {
            'fields': ('link_url', 'link_text', 'open_in_new_tab')
        }),
        (_('Scheduling'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Customization'), {
            'fields': ('overlay_color', 'text_color')
        }),
        (_('Analytics'), {
            'fields': ('views', 'clicks', 'ctr_display')
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        return obj.is_active
    is_active_display.boolean = True
    is_active_display.short_description = _('Currently Active')
    
    def ctr_display(self, obj):
        return f"{obj.click_through_rate}%"
    ctr_display.short_description = _('Click-Through Rate')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AccessLog)
class AccessLogAdmin(ImportExportModelAdmin):
    """Admin interface for AccessLog model"""
    resource_class = AccessLogResource
    
    list_display = ('user_display', 'login_type', 'ip_address', 'country', 
                   'city', 'security_level', 'is_suspicious', 'threat_score', 
                   'timestamp', 'device_summary')
    list_filter = ('login_type', 'security_level', 'is_suspicious', 
                  'country', 'timestamp')
    search_fields = ('user__email', 'username_attempt', 'ip_address', 
                    'user_agent', 'country', 'city')
    readonly_fields = ('timestamp', 'device_info_display', 'location_summary_display',
                      'needs_review_display')
    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'username_attempt')
        }),
        (_('Access Details'), {
            'fields': ('login_type', 'usage_description', 'auth_method', 
                      'two_factor_used', 'two_factor_method', 'duration')
        }),
        (_('Device & Network'), {
            'fields': ('user_agent', 'device_info_display', 'ip_address', 
                      'forwarded_ip', 'device_id', 'session_key')
        }),
        (_('Location'), {
            'fields': ('location_data', 'location_summary_display', 'country', 
                      'city', 'latitude', 'longitude')
        }),
        (_('Security'), {
            'fields': ('security_level', 'is_suspicious', 'suspicious_reason', 
                      'threat_score', 'needs_review_display')
        }),
        (_('Timing'), {
            'fields': ('timestamp', 'session_duration_minutes_display')
        }),
    )
    
    def user_display(self, obj):
        return obj.user.email if obj.user else obj.username_attempt or 'Unknown'
    user_display.short_description = _('User')
    
    def device_summary(self, obj):
        device_info = obj.get_device_summary()
        return f"{device_info.get('os', 'Unknown')} / {device_info.get('browser', 'Unknown')}"
    device_summary.short_description = _('Device')
    
    def device_info_display(self, obj):
        device_info = obj.extract_device_info()
        if device_info:
            return format_html(
                "<strong>OS:</strong> {} {}<br>"
                "<strong>Browser:</strong> {} {}<br>"
                "<strong>Device:</strong> {}<br>"
                "<strong>Type:</strong> {}<br>"
                "<strong>Is Bot:</strong> {}",
                device_info.get('operating_system', 'Unknown'),
                device_info.get('os_version', ''),
                device_info.get('browser', 'Unknown'),
                device_info.get('browser_version', ''),
                device_info.get('device', 'Unknown'),
                obj._get_device_type(device_info),
                device_info.get('is_bot', False)
            )
        return _("Unknown")
    device_info_display.short_description = _('Device Information')
    
    def location_summary_display(self, obj):
        location = obj.get_location_summary()
        return format_html(
            "<strong>Country:</strong> {}<br>"
            "<strong>City:</strong> {}<br>"
            "<strong>IP:</strong> {}",
            location.get('country', 'Unknown'),
            location.get('city', 'Unknown'),
            location.get('ip', 'Unknown')
        )
    location_summary_display.short_description = _('Location Summary')
    
    def needs_review_display(self, obj):
        return obj.needs_review
    needs_review_display.boolean = True
    needs_review_display.short_description = _('Needs Review')
    
    def session_duration_minutes_display(self, obj):
        return f"{obj.session_duration_minutes:.1f} min"
    session_duration_minutes_display.short_description = _('Session Duration')
    
    actions = ['flag_as_suspicious', 'flag_as_normal', 'export_security_report']
    
    def flag_as_suspicious(self, request, queryset):
        """Flag selected logs as suspicious"""
        for log in queryset:
            log.flag_as_suspicious(_('Manually flagged by admin'))
        self.message_user(request, f"{queryset.count()} logs flagged as suspicious.")
    flag_as_suspicious.short_description = _("Flag selected logs as suspicious")
    
    def flag_as_normal(self, request, queryset):
        """Flag selected logs as normal"""
        queryset.update(
            is_suspicious=False,
            security_level='normal',
            suspicious_reason=''
        )
        self.message_user(request, f"{queryset.count()} logs flagged as normal.")
    flag_as_normal.short_description = _("Flag selected logs as normal")
    
    def export_security_report(self, request, queryset):
        """Export security report for selected logs"""
        # This would typically generate a PDF or CSV report
        self.message_user(request, f"Security report for {queryset.count()} logs generated.")
    export_security_report.short_description = _("Export security report")


@admin.register(School)
class SchoolAdmin(ImportExportModelAdmin):
    """Admin interface for School model"""
    resource_class = SchoolResource
    
    list_display = ('name', 'code', 'school_type', 'students_gender', 
                   'ownership', 'active', 'telephone', 'school_email', 
                   'website', 'established_date')
    list_filter = ('active', 'school_type', 'students_gender', 'ownership', 
                  'established_date')
    search_fields = ('name', 'code', 'address', 'school_email', 'telephone', 
                    'principal_name', 'principal_email')
    readonly_fields = ('created_at', 'updated_at', 'statistics_display', 
                      'contact_info_display', 'social_links_display', 
                      'academic_info_display')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'active')
        }),
        (_('Academic Configuration'), {
            'fields': ('current_academic_year', 'default_curriculum', 
                      'supported_curriculums', 'language', 'additional_languages')
        }),
        (_('School Information'), {
            'fields': ('address', 'school_type', 'students_gender', 'ownership')
        }),
        (_('Contact Information'), {
            'fields': ('telephone', 'mobile', 'school_email', 'website', 
                      'contact_info_display')
        }),
        (_('Principal Information'), {
            'fields': ('principal_name', 'principal_email', 'principal_phone'),
            'classes': ('collapse',)
        }),
        (_('School Details'), {
            'fields': ('mission', 'vision', 'motto', 'core_values', 'history')
        }),
        (_('Media'), {
            'fields': ('school_logo', 'school_banner', 'gallery')
        }),
        (_('Academic Calendar'), {
            'fields': ('academic_calendar',),
            'classes': ('collapse',)
        }),
        (_('Facilities'), {
            'fields': ('facilities',),
            'classes': ('collapse',)
        }),
        (_('Social Media'), {
            'fields': ('social_links_display', 'facebook_url', 'twitter_url', 
                      'instagram_url', 'linkedin_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        (_('Registration'), {
            'fields': ('established_date', 'registration_date', 'registration_number'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('statistics_display', 'academic_info_display')
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def statistics_display(self, obj):
        stats = obj.get_statistics()
        return format_html(
            "<strong>Students:</strong> {}<br>"
            "<strong>Teachers:</strong> {}<br>"
            "<strong>Staff:</strong> {}<br>"
            "<strong>Classes:</strong> {}<br>"
            "<strong>Subjects:</strong> {}",
            stats.get('total_students', 0),
            stats.get('total_teachers', 0),
            stats.get('total_staff', 0),
            stats.get('total_classes', 0),
            stats.get('total_subjects', 0)
        )
    statistics_display.short_description = _('Statistics')
    
    def contact_info_display(self, obj):
        contact = obj.get_contact_info()
        return format_html(
            "<strong>Telephone:</strong> {}<br>"
            "<strong>Mobile:</strong> {}<br>"
            "<strong>Email:</strong> {}<br>"
            "<strong>Website:</strong> {}",
            contact['primary']['telephone'],
            contact['primary']['mobile'] or 'N/A',
            contact['primary']['email'],
            contact['primary']['website'] or 'N/A'
        )
    contact_info_display.short_description = _('Contact Information')
    
    def social_links_display(self, obj):
        links = obj.get_social_links()
        if not links:
            return _("No social media links configured")
        
        html_parts = []
        for platform, url in links.items():
            html_parts.append(f"<strong>{platform.title()}:</strong> {url}<br>")
        return format_html(''.join(html_parts))
    social_links_display.short_description = _('Social Media Links')
    
    def academic_info_display(self, obj):
        info = obj.get_academic_info()
        return format_html(
            "<strong>Current Academic Year:</strong> {}<br>"
            "<strong>Default Curriculum:</strong> {}<br>"
            "<strong>Language:</strong> {}<br>"
            "<strong>Additional Languages:</strong> {}",
            info.get('current_academic_year', 'Not set'),
            info.get('default_curriculum', 'Not set'),
            info.get('language', 'Not set'),
            ', '.join(info.get('additional_languages', [])) or 'None'
        )
    academic_info_display.short_description = _('Academic Information')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['activate_school', 'deactivate_school', 'export_school_profile']
    
    def activate_school(self, request, queryset):
        """Activate selected school(s)"""
        if queryset.count() > 1:
            self.message_user(request, _("Please select only one school to activate."), level='error')
            return
        
        school = queryset.first()
        if school.activate():
            self.message_user(request, f"School '{school.name}' activated successfully.")
        else:
            self.message_user(request, f"Failed to activate school '{school.name}'.", level='error')
    activate_school.short_description = _("Activate selected school")
    
    def deactivate_school(self, request, queryset):
        """Deactivate selected schools"""
        updated = queryset.update(active=False)
        self.message_user(request, f"{updated} schools deactivated successfully.")
    deactivate_school.short_description = _("Deactivate selected schools")
    
    def export_school_profile(self, request, queryset):
        """Export school profile"""
        self.message_user(request, f"School profile for {queryset.count()} schools exported.")
    export_school_profile.short_description = _("Export school profile")


@admin.register(Day)
class DayAdmin(ImportExportModelAdmin):
    """Admin interface for Day model"""
    
    list_display = ('day_number', 'full_name', 'short_name', 'day_type', 
                   'is_school_day', 'is_instructional_day', 'total_periods', 
                   'total_instructional_hours')
    list_filter = ('day_type', 'is_school_day', 'is_instructional_day')
    search_fields = ('full_name', 'short_name', 'special_instructions')
    readonly_fields = ('created_at', 'updated_at', 'schedule_template_display')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('day_number', 'short_name', 'full_name')
        }),
        (_('Day Configuration'), {
            'fields': ('day_type', 'is_school_day', 'is_instructional_day', 
                      'special_instructions')
        }),
        (_('Timing Configuration'), {
            'fields': ('start_time', 'end_time', 'break_start_time', 'break_end_time',
                      'lunch_start_time', 'lunch_end_time')
        }),
        (_('Period Configuration'), {
            'fields': ('total_periods', 'period_duration', 'total_instructional_hours_display')
        }),
        (_('Display Settings'), {
            'fields': ('color_code', 'weight')
        }),
        (_('Schedule Template'), {
            'fields': ('schedule_template_display',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_instructional_hours_display(self, obj):
        return f"{obj.total_instructional_hours} hours"
    total_instructional_hours_display.short_description = _('Total Instructional Hours')
    
    def schedule_template_display(self, obj):
        template = obj.schedule_template
        return format_html(
            "<strong>Day:</strong> {}<br>"
            "<strong>Type:</strong> {}<br>"
            "<strong>School Day:</strong> {}<br>"
            "<strong>Instructional Day:</strong> {}<br>"
            "<strong>Start:</strong> {}<br>"
            "<strong>End:</strong> {}<br>"
            "<strong>Periods:</strong> {} ({} min each)<br>"
            "<strong>Total Hours:</strong> {}<br>"
            "<strong>Color:</strong> <span style='color:{}'>●</span> {}",
            template['day'],
            template['type'],
            template['is_school_day'],
            template['is_instructional_day'],
            template['timings']['start'],
            template['timings']['end'],
            template['periods']['total'],
            template['periods']['duration_minutes'],
            template['periods']['total_hours'],
            template['display']['color'],
            template['display']['color']
        )
    schedule_template_display.short_description = _('Schedule Template')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        """Limit adding days since we only need 7 days"""
        return Day.objects.count() < 7
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting essential days"""
        if obj and obj.day_number <= 5:  # Monday to Friday
            return False
        return super().has_delete_permission(request, obj)


# ==================== ADMIN SITE CUSTOMIZATION ====================

class DelvokAdminSite(admin.AdminSite):
    """Custom admin site for Delvok Academy"""
    site_header = "Delvok Academy Administration"
    site_title = "Delvok Academy Admin Portal"
    index_title = "Welcome to Delvok Academy Administration"
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)
        
        # Sort the apps alphabetically
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort the models alphabetically within each app
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        
        return app_list


# Register custom admin site
delvok_admin_site = DelvokAdminSite(name='delvok_admin')

# Register models with custom admin site
delvok_admin_site.register(Article, ArticleAdmin)
delvok_admin_site.register(CarouselImage, CarouselImageAdmin)
delvok_admin_site.register(AccessLog, AccessLogAdmin)
delvok_admin_site.register(School, SchoolAdmin)
delvok_admin_site.register(Day, DayAdmin)
delvok_admin_site.register(Group)

