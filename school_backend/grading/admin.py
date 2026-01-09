from django.contrib import admin
from .models import (
    GradingScale, GradingPeriod, AssessmentType, Assessment,
    StudentGrade, SubjectGrade, ReportCard, Gradebook
)

@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'min_score', 'max_score', 'grade_points', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'grade', 'remark')
    ordering = ('min_score',)

@admin.register(GradingPeriod)
class GradingPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'academic_year', 'start_date', 'end_date', 'is_active', 'is_finalized')
    list_filter = ('term', 'academic_year', 'is_active', 'is_finalized')
    search_fields = ('name', 'academic_year')
    ordering = ('-academic_year', 'start_date')

@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'weight', 'max_score', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('weight', 'name')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'class_level', 'grading_period', 'total_marks', 'assessment_date', 'is_published')
    list_filter = ('subject', 'class_level', 'grading_period', 'is_published')
    search_fields = ('name', 'subject__name', 'class_level__name')
    ordering = ('-assessment_date',)
    raw_id_fields = ('subject', 'class_level', 'grading_period', 'created_by')

@admin.register(StudentGrade)
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'marks_obtained', 'percentage', 'grade', 'graded_at')
    list_filter = ('grade', 'is_absent', 'is_exempted', 'graded_at')
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name', 'assessment__name')
    raw_id_fields = ('student', 'assessment', 'graded_by')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'assessment')

@admin.register(SubjectGrade)
class SubjectGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grading_period', 'percentage', 'grade', 'is_finalized')
    list_filter = ('subject', 'grading_period', 'grade', 'is_finalized')
    search_fields = ('student__admission_number', 'subject__name')
    raw_id_fields = ('student', 'subject', 'class_level', 'grading_period', 'finalized_by')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'subject', 'grading_period')

@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ('student', 'grading_period', 'overall_percentage', 'overall_grade', 'gpa', 'status')
    list_filter = ('grading_period', 'status', 'class_level')
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name')
    raw_id_fields = ('student', 'grading_period', 'class_level', 'published_by')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'grading_period', 'class_level')

@admin.register(Gradebook)
class GradebookAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'class_level', 'grading_period', 'is_published', 'last_updated')
    list_filter = ('subject', 'class_level', 'grading_period', 'is_published')
    search_fields = ('teacher__username', 'subject__name', 'class_level__name')
    raw_id_fields = ('teacher', 'subject', 'class_level', 'grading_period')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher', 'subject', 'class_level', 'grading_period')