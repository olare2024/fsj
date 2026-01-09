# administration/filters.py
"""
administration/common_objs.py
Common constants and choices for administration models.
"""


import django_filters
from django.db.models import Q
from .models import Article, AccessLog, SchoolEvent
from django.utils.translation import gettext_lazy as _

SCHOOL_TYPE_CHOICE = [
    ('primary', _('Primary School')),
    ('secondary', _('Secondary School')),
    ('mixed', _('Mixed Primary & Secondary')),
    ('international', _('International School')),
    ('private', _('Private School')),
    ('public', _('Public School')),
    ('boarding', _('Boarding School')),
    ('day', _('Day School')),
]

SCHOOL_STUDENTS_GENDER = [
    ('boys', _('Boys Only')),
    ('girls', _('Girls Only')),
    ('mixed', _('Mixed')),
]

SCHOOL_OWNERSHIP = [
    ('private', _('Private')),
    ('public', _('Public')),
    ('religious', _('Religious Organization')),
    ('community', _('Community Owned')),
    ('government', _('Government')),
    ('trust', _('Trust/Society')),
]

class ArticleFilter(django_filters.FilterSet):
    """Filter for Article model"""
    category = django_filters.ChoiceFilter(choices=Article.ARTICLE_CATEGORIES)
    status = django_filters.ChoiceFilter(choices=Article.ARTICLE_STATUS)
    featured = django_filters.BooleanFilter()
    pinned = django_filters.BooleanFilter()
    published_after = django_filters.DateFilter(field_name='published_at', lookup_expr='gte')
    published_before = django_filters.DateFilter(field_name='published_at', lookup_expr='lte')
    
    class Meta:
        model = Article
        fields = ['category', 'status', 'featured', 'pinned']


class AccessLogFilter(django_filters.FilterSet):
    """Filter for AccessLog model"""
    login_type = django_filters.ChoiceFilter(choices=AccessLog.LOGIN_TYPES)
    is_suspicious = django_filters.BooleanFilter()
    date_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    date_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    
    class Meta:
        model = AccessLog
        fields = ['login_type', 'is_suspicious', 'user']


class SchoolEventFilter(django_filters.FilterSet):
    """Filter for SchoolEvent model"""
    event_type = django_filters.ChoiceFilter(choices=SchoolEvent.EVENT_TYPES)
    category = django_filters.ChoiceFilter(choices=SchoolEvent.EVENT_CATEGORIES)
    priority = django_filters.ChoiceFilter(choices=SchoolEvent.PRIORITY_LEVELS)
    is_published = django_filters.BooleanFilter()
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    term = django_filters.ModelChoiceFilter(queryset=lambda: SchoolEvent.objects.values_list('term', flat=True).distinct())
    
    class Meta:
        model = SchoolEvent
        fields = ['event_type', 'category', 'priority', 'is_published', 'term']