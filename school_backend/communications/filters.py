import django_filters
from django.db.models import Q
from .models import Announcement, Message, Notification

class AnnouncementFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    audience = django_filters.ChoiceFilter(choices=Announcement.AUDIENCE_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Announcement.PRIORITY_CHOICES)
    is_published = django_filters.BooleanFilter()
    created_by = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains')
    
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    publish_after = django_filters.DateTimeFilter(field_name='publish_at', lookup_expr='gte')
    publish_before = django_filters.DateTimeFilter(field_name='publish_at', lookup_expr='lte')
    
    expires_after = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_before = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'audience', 'priority', 'is_published',
            'created_by', 'created_after', 'created_before',
            'publish_after', 'publish_before', 'expires_after', 'expires_before'
        ]

class MessageFilter(django_filters.FilterSet):
    subject = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    message_type = django_filters.ChoiceFilter(choices=Message.MESSAGE_TYPES)
    sender = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains')
    is_important = django_filters.BooleanFilter()
    
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    has_attachments = django_filters.BooleanFilter(method='filter_has_attachments')
    is_read = django_filters.BooleanFilter(method='filter_is_read')
    
    class Meta:
        model = Message
        fields = [
            'subject', 'content', 'message_type', 'sender', 'is_important',
            'created_after', 'created_before', 'has_attachments', 'is_read'
        ]
    
    def filter_has_attachments(self, queryset, name, value):
        if value:
            return queryset.exclude(attachments__isnull=True).exclude(attachments='[]')
        return queryset.filter(Q(attachments__isnull=True) | Q(attachments='[]'))
    
    def filter_is_read(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(
                messagerecipient__recipient=user,
                messagerecipient__is_read=True
            )
        return queryset.filter(
            messagerecipient__recipient=user,
            messagerecipient__is_read=False
        )

class NotificationFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    message = django_filters.CharFilter(lookup_expr='icontains')
    notification_type = django_filters.ChoiceFilter(choices=Notification.NOTIFICATION_TYPES)
    channel = django_filters.ChoiceFilter(choices=Notification.CHANNEL_CHOICES)
    is_read = django_filters.BooleanFilter()
    is_sent = django_filters.BooleanFilter()
    
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    scheduled_after = django_filters.DateTimeFilter(field_name='scheduled_for', lookup_expr='gte')
    scheduled_before = django_filters.DateTimeFilter(field_name='scheduled_for', lookup_expr='lte')
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'channel',
            'is_read', 'is_sent', 'created_after', 'created_before',
            'scheduled_after', 'scheduled_before'
        ]