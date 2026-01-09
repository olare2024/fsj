from django.contrib import admin
from .models import DownloadCategory, DownloadFile, DownloadHistory, FileRating

@admin.register(DownloadCategory)
class DownloadCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_count', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    def file_count(self, obj):
        return obj.files.count()
    file_count.short_description = 'File Count'

@admin.register(DownloadFile)
class DownloadFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'file_type', 'downloads', 'rating', 'required_role', 'is_active', 'upload_date']
    list_filter = ['category', 'file_type', 'required_role', 'is_active', 'upload_date']
    search_fields = ['name', 'description']
    readonly_fields = ['downloads', 'rating', 'upload_date', 'last_download', 'file_size']
    list_editable = ['is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'file_type')
        }),
        ('File Details', {
            'fields': ('file', 'file_size', 'required_role', 'is_active')
        }),
        ('Statistics', {
            'fields': ('downloads', 'rating', 'upload_date', 'last_download', 'uploaded_by')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'download_date', 'ip_address']
    list_filter = ['download_date']
    search_fields = ['user__username', 'file__name']
    readonly_fields = ['download_date']
    date_hierarchy = 'download_date'

@admin.register(FileRating)
class FileRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'file__name']
    readonly_fields = ['created_at', 'updated_at']