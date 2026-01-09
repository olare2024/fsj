from django.contrib import admin
from .models import (
    Curriculum, CBCStrand, CBCSubStrand, ICSESubject,
    AmericanStandard, AmericanCourse, CurriculumMapping,
    CurriculumImplementation, LearningObjective, ResourceLibrary,
    ProfessionalDevelopment
)

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['name', 'full_name', 'country_origin', 'is_active', 'coordinator', 'implementation_date']
    list_filter = ['is_active', 'name']
    search_fields = ['name', 'full_name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CBCStrand)
class CBCStrandAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'learning_area', 'curriculum']
    list_filter = ['learning_area', 'curriculum']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CBCSubStrand)
class CBCSubStrandAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'strand', 'priority_level', 'suggested_weeks']
    list_filter = ['strand', 'priority_level']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ICSESubject)
class ICSESubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'subject_group', 'is_compulsory', 'total_marks']
    list_filter = ['subject_group', 'is_compulsory', 'has_practical']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AmericanStandard)
class AmericanStandardAdmin(admin.ModelAdmin):
    list_display = ['standard_code', 'domain', 'grade_level', 'complexity_level']
    list_filter = ['domain', 'grade_level', 'complexity_level']
    search_fields = ['standard_code', 'description', 'cluster']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AmericanCourse)
class AmericanCourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'name', 'course_type', 'credit_type', 'credits', 'is_active']
    list_filter = ['course_type', 'credit_type', 'is_active']
    search_fields = ['name', 'course_code', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CurriculumMapping)
class CurriculumMappingAdmin(admin.ModelAdmin):
    list_display = ['source_curriculum', 'target_curriculum', 'source_component', 'target_component', 'mapping_strength', 'is_verified']
    list_filter = ['source_curriculum', 'target_curriculum', 'mapping_strength', 'is_verified']
    search_fields = ['source_component', 'target_component', 'source_identifier', 'target_identifier']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CurriculumImplementation)
class CurriculumImplementationAdmin(admin.ModelAdmin):
    list_display = ['curriculum', 'class_enrolled', 'academic_year', 'implementation_status', 'is_primary']
    list_filter = ['curriculum', 'academic_year', 'implementation_status', 'is_primary']
    search_fields = ['class_enrolled__name', 'curriculum__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(LearningObjective)
class LearningObjectiveAdmin(admin.ModelAdmin):
    list_display = ['code', 'curriculum', 'bloom_level', 'subject']
    list_filter = ['curriculum', 'bloom_level']
    search_fields = ['code', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ResourceLibrary)
class ResourceLibraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'curriculum', 'author', 'is_approved', 'usage_count']
    list_filter = ['resource_type', 'curriculum', 'is_approved']
    search_fields = ['title', 'author', 'description']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']

@admin.register(ProfessionalDevelopment)
class ProfessionalDevelopmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'curriculum', 'development_type', 'start_date', 'end_date', 'is_completed']
    list_filter = ['curriculum', 'development_type', 'is_completed']
    search_fields = ['title', 'description', 'facilitator']
    readonly_fields = ['created_at', 'updated_at']