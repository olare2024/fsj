import django_filters
from django_filters import rest_framework as filters
from .models import Grade, SubjectGradeSummary

class GradeFilter(filters.FilterSet):
    student = filters.UUIDFilter(field_name='student__id')
    subject = filters.UUIDFilter(field_name='subject__id')
    class_enrolled = filters.UUIDFilter(field_name='class_enrolled__id')
    academic_year = filters.UUIDFilter(field_name='academic_year__id')
    term = filters.UUIDFilter(field_name='term__id')
    assessment_type = filters.UUIDFilter(field_name='assessment_type__id')
    
    score_min = filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = filters.NumberFilter(field_name='score', lookup_expr='lte')
    percentage_min = filters.NumberFilter(field_name='percentage', lookup_expr='gte')
    percentage_max = filters.NumberFilter(field_name='percentage', lookup_expr='lte')
    
    date_from = filters.DateFilter(field_name='assessment_date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='assessment_date', lookup_expr='lte')
    
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'class_enrolled', 'academic_year', 'term', 
                 'assessment_type', 'is_published']

class SubjectGradeSummaryFilter(filters.FilterSet):
    student = filters.UUIDFilter(field_name='student__id')
    subject = filters.UUIDFilter(field_name='subject__id')
    class_enrolled = filters.UUIDFilter(field_name='class_enrolled__id')
    academic_year = filters.UUIDFilter(field_name='academic_year__id')
    term = filters.UUIDFilter(field_name='term__id')
    
    average_min = filters.NumberFilter(field_name='average_percentage', lookup_expr='gte')
    average_max = filters.NumberFilter(field_name='average_percentage', lookup_expr='lte')
    
    class Meta:
        model = SubjectGradeSummary
        fields = ['student', 'subject', 'class_enrolled', 'academic_year', 'term', 'is_finalized']