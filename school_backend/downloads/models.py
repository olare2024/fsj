from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import os

User = get_user_model()

def download_file_path(instance, filename):
    """Generate file path for download files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('downloads/', filename)

class DownloadCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Download Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DownloadFile(models.Model):
    ROLE_CHOICES = [
        ('all', 'All Users'),
        ('student', 'Students'),
        ('teacher', 'Teachers'),
        ('parent', 'Parents'),
        ('admin', 'Administrators'),
        ('staff', 'Staff'),
    ]
    
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('xlsx', 'Excel Spreadsheet'),
        ('pptx', 'PowerPoint'),
        ('mp3', 'Audio File'),
        ('zip', 'ZIP Archive'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(DownloadCategory, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file = models.FileField(upload_to=download_file_path)
    file_size = models.BigIntegerField(help_text="Size in bytes")
    downloads = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    required_role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='all')
    is_active = models.BooleanField(default=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_download = models.DateTimeField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    
    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['required_role', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_file_size_display(self):
        """Convert bytes to human readable format"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def save(self, *args, **kwargs):
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

class DownloadHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='download_history')
    file = models.ForeignKey(DownloadFile, on_delete=models.CASCADE, related_name='download_history')
    download_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Download Histories"
        ordering = ['-download_date']
        indexes = [
            models.Index(fields=['user', 'download_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

class FileRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(DownloadFile, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'file']
        indexes = [
            models.Index(fields=['file', 'rating']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.file.name} - {self.rating}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update file's average rating
        self.update_file_rating()
    
    def update_file_rating(self):
        avg_rating = FileRating.objects.filter(file=self.file).aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating'] or 0.0
        self.file.rating = round(avg_rating, 2)
        self.file.save()