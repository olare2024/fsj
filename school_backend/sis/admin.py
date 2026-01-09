# sis/admin.py
from django.contrib import admin
from .models import StudentBulkUpload

@admin.register(StudentBulkUpload)
class StudentBulkUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'csv_file', 'date_uploaded', 'file_size']
    list_filter = ['date_uploaded']
    search_fields = ['csv_file']
    readonly_fields = ['date_uploaded', 'file_size']
    
    def file_size(self, obj):
        if obj.csv_file and obj.csv_file.size:
            size = obj.csv_file.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "Unknown"
    file_size.short_description = 'File Size'