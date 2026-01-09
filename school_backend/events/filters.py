import django_filters
from django_filters import rest_framework as filters
from .models import Event, EventRegistration
from django.utils import timezone

class EventFilter(filters.FilterSet):
    event_type = filters.CharFilter(field_name='event_type')
    target_audience = filters.CharFilter(field_name='target_audience')
    priority = filters.CharFilter(field_name='priority')
    is_published = filters.BooleanFilter(field_name='is_published')
    is_cancelled = filters.BooleanFilter(field_name='is_cancelled')
    requires_registration = filters.BooleanFilter(field_name='requires_registration')
    has_fee = filters.BooleanFilter(field_name='has_fee')
    
    start_date_after = filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')
    end_date_after = filters.DateTimeFilter(field_name='end_date', lookup_expr='gte')
    end_date_before = filters.DateTimeFilter(field_name='end_date', lookup_expr='lte')
    
    date_range = filters.CharFilter(method='filter_date_range')
    status = filters.CharFilter(method='filter_status')
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Event
        fields = [
            'event_type', 'target_audience', 'priority', 'is_published',
            'is_cancelled', 'requires_registration', 'has_fee',
            'start_date_after', 'start_date_before', 'end_date_after', 'end_date_before'
        ]
    
    def filter_date_range(self, queryset, name, value):
        """Filter events by date range"""
        if value == 'today':
            today = timezone.now().date()
            return queryset.filter(
                start_date__date__lte=today,
                end_date__date__gte=today
            )
        elif value == 'week':
            start_of_week = timezone.now().date()
            end_of_week = start_of_week + timezone.timedelta(days=7)
            return queryset.filter(
                start_date__date__lte=end_of_week,
                end_date__date__gte=start_of_week
            )
        elif value == 'month':
            start_of_month = timezone.now().date().replace(day=1)
            next_month = start_of_month.replace(month=start_of_month.month + 1)
            end_of_month = next_month - timezone.timedelta(days=1)
            return queryset.filter(
                start_date__date__lte=end_of_month,
                end_date__date__gte=start_of_month
            )
        return queryset
    
    def filter_status(self, queryset, name, value):
        """Filter events by status (upcoming, ongoing, past)"""
        now = timezone.now()
        
        if value == 'upcoming':
            return queryset.filter(start_date__gt=now)
        elif value == 'ongoing':
            return queryset.filter(start_date__lte=now, end_date__gte=now)
        elif value == 'past':
            return queryset.filter(end_date__lt=now)
        
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search events by title, description, or location"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(location__icontains=value) |
            Q(organizer__icontains=value)
        )

class EventRegistrationFilter(filters.FilterSet):
    event = filters.UUIDFilter(field_name='event__id')
    status = filters.CharFilter(field_name='status')
    has_paid = filters.BooleanFilter(field_name='has_paid')
    checked_in = filters.BooleanFilter(field_name='checked_in')
    
    registration_date_after = filters.DateTimeFilter(field_name='registration_date', lookup_expr='gte')
    registration_date_before = filters.DateTimeFilter(field_name='registration_date', lookup_expr='lte')
    
    class Meta:
        model = EventRegistration
        fields = ['event', 'status', 'has_paid', 'checked_in']