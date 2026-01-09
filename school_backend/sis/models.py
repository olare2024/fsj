# sis/models.py
from django.db import models

class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="api/sis/students/bulkupload")
    
    def __str__(self):
        return f"Bulk Upload {self.id} - {self.date_uploaded}"
    
    class Meta:
        verbose_name = "Student Bulk Upload"
        verbose_name_plural = "Student Bulk Uploads"