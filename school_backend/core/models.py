# core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import BaseModel

class Department(BaseModel):
    """Department model aligned with TSC and CBC structure"""
    
    TSC_CATEGORY_CHOICES = [
        ('primary', _('Primary School')),
        ('junior_secondary', _('Junior Secondary School')),
        ('senior_secondary', _('Senior Secondary School')),
        ('special_needs', _('Special Needs Education')),
        ('technical', _('Technical/Vocational')),
        ('ecde', _('Early Childhood Development Education')),
    ]
    
    CBC_PATHWAY_CHOICES = [
        ('stem', _('STEM Pathway')),
        ('social_sciences', _('Social Sciences Pathway')),
        ('arts_sports', _('Arts & Sports Pathway')),
        ('general', _('General Pathway')),
        ('applied', _('Applied Pathway')),
        ('technical', _('Technical Pathway')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_("Department Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Department Code"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    tsc_category = models.CharField(
        max_length=50,
        choices=TSC_CATEGORY_CHOICES,
        default='junior_secondary',
        verbose_name=_("TSC Category")
    )
    
    cbc_pathway = models.CharField(
        max_length=50,
        choices=CBC_PATHWAY_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway")
    )
    
    # Head of Department - Will be a ForeignKey to TeacherProfile
    hod = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments_headed',
        verbose_name=_("Head of Department")
    )
    
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Location"))
    building = models.CharField(max_length=100, blank=True, verbose_name=_("Building"))
    room_number = models.CharField(max_length=20, blank=True, verbose_name=_("Room Number"))
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"