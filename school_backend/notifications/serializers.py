from rest_framework import serializers
from .models import Notification, NotificationTemplate, UserNotificationSettings, NotificationStats
from accounts.models import User
import uuid
from django.utils import timezone
from django.utils.timesince import timesince


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    sender_email = serializers.EmailField(source='sender.email', read_only=True, allow_null=True)
    sender_full_name = serializers.CharField(source='sender.get_full_name', read_only=True, allow_null=True)
    time_ago = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    can_be_deleted = serializers.BooleanField(read_only=True)
    absolute_url = serializers.SerializerMethodField()
    delivery_status = serializers.SerializerMethodField()
    related_object_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'user_role',
            'title', 'message', 'type', 'priority', 'channel', 'status',
            'delivery_method', 'data', 'actions', 'metadata',
            'created_at', 'updated_at', 'read_at', 'expires_at', 'sent_at',
            'time_ago', 'is_expired', 'can_be_deleted', 'absolute_url',
            'email_sent', 'sms_sent', 'push_sent', 'in_app_sent',
            'sender', 'sender_email', 'sender_full_name',
            'related_object_type', 'related_object_id', 'related_object_url',
            'delivery_status'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'read_at', 'sent_at',
            'time_ago', 'is_expired', 'can_be_deleted', 'absolute_url',
            'email_sent', 'sms_sent', 'push_sent', 'in_app_sent',
            'delivery_status', 'related_object_url'
        ]
        extra_kwargs = {
            'user': {'required': False, 'write_only': True},
            'sender': {'required': False, 'write_only': True}
        }

    def get_time_ago(self, obj):
        """Calculate time ago for notification"""
        if not obj.created_at:
            return None
        
        return timesince(obj.created_at, timezone.now()) + ' ago'

    def get_absolute_url(self, obj):
        """Get absolute URL for the notification"""
        return obj.get_absolute_url()

    def get_delivery_status(self, obj):
        """Get delivery status"""
        return {
            'email': obj.email_sent,
            'sms': obj.sms_sent,
            'push': obj.push_sent,
            'in_app': obj.in_app_sent,
            'sent': bool(obj.sent_at)
        }

    def get_related_object_url(self, obj):
        """Get URL for related object if applicable"""
        if obj.related_object_type and obj.related_object_id:
            # This would depend on your URL structure
            # Example: /api/{object_type}/{object_id}/
            try:
                from django.urls import reverse
                return reverse(
                    f'{obj.related_object_type}_detail',
                    kwargs={'pk': str(obj.related_object_id)}
                )
            except:
                return None
        return None

    def validate(self, data):
        """Validate notification data"""
        # Validate expiration date
        if 'expires_at' in data and data['expires_at']:
            if data['expires_at'] <= timezone.now():
                raise serializers.ValidationError({
                    'expires_at': 'Expiration time must be in the future'
                })
        
        # Validate actions format
        if 'actions' in data and data['actions']:
            if not isinstance(data['actions'], list):
                raise serializers.ValidationError({
                    'actions': 'Actions must be a list'
                })
            
            for action in data['actions']:
                if not isinstance(action, dict):
                    raise serializers.ValidationError({
                        'actions': 'Each action must be a dictionary'
                    })
                if 'label' not in action or 'url' not in action:
                    raise serializers.ValidationError({
                        'actions': 'Each action must have label and url keys'
                    })
        
        # Validate metadata format
        if 'metadata' in data and data['metadata']:
            if not isinstance(data['metadata'], dict):
                raise serializers.ValidationError({
                    'metadata': 'Metadata must be a dictionary'
                })
        
        return data

    def create(self, validated_data):
        """Create notification with user from request context"""
        request = self.context.get('request')
        if request and request.user:
            # Set user from request if not provided
            if 'user' not in validated_data:
                validated_data['user'] = request.user
            
            # Set sender to current user if not provided
            if 'sender' not in validated_data and request.user != validated_data['user']:
                validated_data['sender'] = request.user
        
        notification = super().create(validated_data)
        
        # Auto-send notification if requested
        auto_send = self.context.get('auto_send', True)
        if auto_send:
            notification.send()
        
        return notification


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification lists"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    time_ago = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    has_actions = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user_email', 'user_full_name', 'title', 'message', 
            'type', 'type_display', 'priority', 'priority_display',
            'channel', 'status', 'created_at', 'read_at', 
            'time_ago', 'is_expired', 'has_actions', 'data'
        ]
        read_only_fields = fields

    def get_time_ago(self, obj):
        if not obj.created_at:
            return None
        return timesince(obj.created_at, timezone.now()) + ' ago'

    def get_has_actions(self, obj):
        return bool(obj.actions and len(obj.actions) > 0)


class MarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)
    
    def validate(self, data):
        """Validate serializer data"""
        if not data.get('notification_ids') and not data.get('mark_all'):
            raise serializers.ValidationError(
                "Either provide notification_ids or set mark_all to True"
            )
        
        if data.get('notification_ids') and data.get('mark_all'):
            raise serializers.ValidationError(
                "Cannot specify both notification_ids and mark_all=True"
            )
        
        return data
    
    def validate_notification_ids(self, value):
        """Validate notification IDs"""
        if not value:
            return value
        
        # Check if notifications exist and belong to user
        request = self.context.get('request')
        if request and request.user:
            existing_ids = Notification.objects.filter(
                id__in=value,
                user=request.user
            ).values_list('id', flat=True)
            
            invalid_ids = set(value) - set(existing_ids)
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Invalid notification IDs: {', '.join(str(id) for id in invalid_ids)}"
                )
        
        return value


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for bulk notification creation"""
    
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPES,
        default='system'
    )
    channel = serializers.ChoiceField(
        choices=Notification.CHANNELS,
        default='all'
    )
    priority = serializers.ChoiceField(
        choices=Notification.PRIORITY_LEVELS,
        default='medium'
    )
    delivery_method = serializers.ChoiceField(
        choices=Notification.DELIVERY_METHODS,
        default='in_app'
    )
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=[]
    )
    role = serializers.CharField(required=False)
    data = serializers.JSONField(required=False, default=dict)
    actions = serializers.JSONField(required=False, default=list)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    auto_send = serializers.BooleanField(default=True)

    def validate(self, data):
        """Validate bulk notification data"""
        if not data.get('user_ids') and not data.get('role'):
            raise serializers.ValidationError(
                "Either user_ids or role must be specified"
            )
        
        if data.get('user_ids') and data.get('role'):
            raise serializers.ValidationError(
                "Specify either user_ids or role, not both"
            )
        
        # Validate expiration date
        if 'expires_at' in data and data['expires_at']:
            if data['expires_at'] <= timezone.now():
                raise serializers.ValidationError({
                    'expires_at': 'Expiration time must be in the future'
                })
        
        # Validate actions format
        if 'actions' in data and data['actions']:
            if not isinstance(data['actions'], list):
                raise serializers.ValidationError({
                    'actions': 'Actions must be a list'
                })
        
        return data


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model"""
    
    variables_description = serializers.SerializerMethodField()
    template_type_display = serializers.CharField(
        source='get_template_type_display', 
        read_only=True
    )
    default_priority_display = serializers.CharField(
        source='get_default_priority_display', 
        read_only=True
    )
    default_channel_display = serializers.CharField(
        source='get_default_channel_display', 
        read_only=True
    )
    default_delivery_display = serializers.CharField(
        source='get_default_delivery_display', 
        read_only=True
    )
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'usage_count']
        extra_kwargs = {
            'variables': {'help_text': 'Available template variables as JSON'}
        }
    
    def get_variables_description(self, obj):
        """Get human-readable description of template variables"""
        if not obj.variables:
            return "No variables defined"
        
        description_lines = []
        for var_name, var_info in obj.variables.items():
            if isinstance(var_info, dict):
                description = var_info.get('description', 'No description')
                example = var_info.get('example', 'No example')
                required = var_info.get('required', False)
                description_lines.append(
                    f"{var_name} ({'required' if required else 'optional'}): {description} (e.g., {example})"
                )
            else:
                description_lines.append(f"{var_name}: {var_info}")
        
        return "\n".join(description_lines)
    
    def get_usage_count(self, obj):
        """Get count of notifications created from this template"""
        # This would require a field in Notification model tracking template usage
        # For now, we'll return 0 or implement a custom count method
        return 0


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for UserNotificationSettings"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    is_quiet_hours_active = serializers.SerializerMethodField()
    
    class Meta:
        model = UserNotificationSettings
        fields = '__all__'
        read_only_fields = ['user', 'user_email', 'user_full_name', 'user_role', 
                           'created_at', 'updated_at', 'is_quiet_hours_active']
    
    def validate_notification_preferences(self, value):
        """Validate notification preferences"""
        valid_types = [choice[0] for choice in Notification.NOTIFICATION_TYPES]
        valid_methods = ['email', 'sms', 'push', 'in_app']
        
        for notif_type, methods in value.items():
            if notif_type not in valid_types:
                raise serializers.ValidationError(
                    f"Invalid notification type: {notif_type}"
                )
            
            if not isinstance(methods, dict):
                raise serializers.ValidationError(
                    f"Preferences for {notif_type} must be a dictionary"
                )
            
            for method, enabled in methods.items():
                if method not in valid_methods:
                    raise serializers.ValidationError(
                        f"Invalid delivery method: {method}"
                    )
                if not isinstance(enabled, bool):
                    raise serializers.ValidationError(
                        f"Value for {method} must be boolean"
                    )
        
        return value
    
    def validate(self, data):
        """Validate quiet hours"""
        if 'quiet_hours_start' in data and 'quiet_hours_end' in data:
            if data['quiet_hours_start'] == data['quiet_hours_end']:
                raise serializers.ValidationError({
                    'quiet_hours_start': 'Start and end times cannot be the same',
                    'quiet_hours_end': 'Start and end times cannot be the same'
                })
        
        return data
    
    def get_is_quiet_hours_active(self, obj):
        """Check if quiet hours are currently active"""
        return obj.is_quiet_hours()


class NotificationStatsSerializer(serializers.ModelSerializer):
    """Serializer for NotificationStats"""
    
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', 
        read_only=True
    )
    channel_display = serializers.CharField(
        source='get_channel_display', 
        read_only=True
    )
    delivery_rate = serializers.SerializerMethodField()
    read_rate = serializers.SerializerMethodField()
    click_rate = serializers.SerializerMethodField()
    avg_delivery_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationStats
        fields = '__all__'
        read_only_fields = ['delivery_rate', 'read_rate', 'click_rate', 
                           'avg_delivery_time_formatted']
    
    def get_delivery_rate(self, obj):
        return obj.delivery_rate
    
    def get_read_rate(self, obj):
        return obj.read_rate
    
    def get_click_rate(self, obj):
        return obj.click_rate
    
    def get_avg_delivery_time_formatted(self, obj):
        if not obj.avg_delivery_time_seconds:
            return "N/A"
        
        seconds = obj.avg_delivery_time_seconds
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"


class NotificationStatsSummarySerializer(serializers.Serializer):
    """Serializer for notification statistics summary"""
    
    date = serializers.DateField()
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_read = serializers.IntegerField()
    delivery_rate = serializers.FloatField()
    read_rate = serializers.FloatField()
    by_type = serializers.DictField()
    by_channel = serializers.DictField()


class NotificationFilterSerializer(serializers.Serializer):
    """Serializer for notification filtering"""
    
    status = serializers.ChoiceField(
        choices=Notification.STATUS_CHOICES,
        required=False
    )
    type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPES,
        required=False
    )
    priority = serializers.ChoiceField(
        choices=Notification.PRIORITY_LEVELS,
        required=False
    )
    channel = serializers.ChoiceField(
        choices=Notification.CHANNELS,
        required=False
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    is_expired = serializers.BooleanField(required=False)
    is_read = serializers.BooleanField(required=False)
    has_actions = serializers.BooleanField(required=False)
    search = serializers.CharField(required=False, max_length=100)
    
    def validate(self, data):
        """Validate date range"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError({
                    'start_date': 'Start date must be before end date',
                    'end_date': 'End date must be after start date'
                })
        
        return data


class NotificationCreateFromTemplateSerializer(serializers.Serializer):
    """Serializer for creating notifications from template"""
    
    template_name = serializers.CharField(max_length=100)
    user_id = serializers.UUIDField(required=False)
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    context = serializers.DictField(default=dict)
    delivery_method = serializers.ChoiceField(
        choices=Notification.DELIVERY_METHODS,
        default='in_app',
        required=False
    )
    priority = serializers.ChoiceField(
        choices=Notification.PRIORITY_LEVELS,
        default='medium',
        required=False
    )
    auto_send = serializers.BooleanField(default=True)
    
    def validate(self, data):
        """Validate template creation data"""
        if not data.get('user_id') and not data.get('user_ids'):
            raise serializers.ValidationError(
                "Either user_id or user_ids must be specified"
            )
        
        if data.get('user_id') and data.get('user_ids'):
            raise serializers.ValidationError(
                "Specify either user_id or user_ids, not both"
            )
        
        # Check if template exists
        try:
            NotificationTemplate.objects.get(name=data['template_name'], is_active=True)
        except NotificationTemplate.DoesNotExist:
            raise serializers.ValidationError({
                'template_name': 'Template not found or is inactive'
            })
        
        return data