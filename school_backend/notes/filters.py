# notes/filters.py
import django_filters
from .models import (
    TextContent, VideoContent, AudioContent, PDFContent,
    PresentationContent, InteractiveContent, ExternalLinkContent,
    LearningModule
)


class ContentFilter(django_filters.FilterSet):
    """Base filter for all content types"""
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = None  # Will be set in subclasses
        fields = ['subject', 'class_field', 'curriculum', 'is_published', 'is_approved']


class TextContentFilter(ContentFilter):
    class Meta:
        model = TextContent
        fields = ContentFilter.Meta.fields + ['word_count']


class VideoContentFilter(ContentFilter):
    min_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='lte')
    
    class Meta:
        model = VideoContent
        fields = ContentFilter.Meta.fields + ['duration']


class AudioContentFilter(ContentFilter):
    min_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='lte')
    
    class Meta:
        model = AudioContent
        fields = ContentFilter.Meta.fields + ['duration']


class LearningModuleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    min_completion_threshold = django_filters.NumberFilter(field_name='completion_threshold', lookup_expr='gte')
    max_completion_threshold = django_filters.NumberFilter(field_name='completion_threshold', lookup_expr='lte')
    
    class Meta:
        model = LearningModule
        fields = ['subject', 'class_field', 'curriculum', 'is_published']