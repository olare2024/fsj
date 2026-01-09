from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Announcement, Message, MessageRecipient, MessageGroup,
    GroupMembership, Notification, ParentTeacherMeeting,
    MeetingParticipant, CommunicationPreference, Feedback
)

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role']

class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    specific_classes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    specific_users = UserBasicSerializer(many=True, read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'excerpt', 'audience', 'specific_grades',
            'specific_classes', 'specific_users', 'priority', 'is_published',
            'publish_at', 'expires_at', 'image', 'attachments', 'created_by',
            'created_at', 'updated_at', 'published_at', 'is_active'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'published_at']

class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'excerpt', 'audience', 'specific_grades',
            'specific_classes', 'specific_users', 'priority', 'publish_at',
            'expires_at', 'image', 'attachments'
        ]

    def validate(self, data):
        """Validate announcement data"""
        if data.get('publish_at') and data.get('expires_at'):
            if data['publish_at'] >= data['expires_at']:
                raise serializers.ValidationError(
                    "Expiry date must be after publish date"
                )
        return data

class MessageGroupSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    members = UserBasicSerializer(many=True, read_only=True)
    member_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = MessageGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'related_class',
            'related_subject', 'is_active', 'allow_member_messages',
            'created_by', 'created_at', 'updated_at', 'members', 'member_count'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class MessageGroupCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = MessageGroup
        fields = [
            'name', 'description', 'group_type', 'related_class',
            'related_subject', 'allow_member_messages', 'member_ids'
        ]

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        group = MessageGroup.objects.create(**validated_data)
        
        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            group.members.set(members)
        
        return group

class MessageSerializer(serializers.ModelSerializer):
    sender = UserBasicSerializer(read_only=True)
    recipients = UserBasicSerializer(many=True, read_only=True)
    group = MessageGroupSerializer(read_only=True)
    parent_message = serializers.StringRelatedField(read_only=True)
    is_read = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'message_type', 'subject', 'content', 'sender', 'recipients',
            'group', 'class_recipient', 'parent_message', 'attachments',
            'is_important', 'created_at', 'updated_at', 'is_read', 'reply_count'
        ]
        read_only_fields = ['sender', 'created_at', 'updated_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                recipient = MessageRecipient.objects.get(
                    message=obj, recipient=request.user
                )
                return recipient.is_read
            except MessageRecipient.DoesNotExist:
                return False
        return False

class MessageCreateSerializer(serializers.ModelSerializer):
    recipient_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    group_id = serializers.UUIDField(write_only=True, required=False)
    class_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = [
            'message_type', 'subject', 'content', 'recipient_ids',
            'group_id', 'class_id', 'attachments', 'is_important'
        ]

    def validate(self, data):
        message_type = data.get('message_type')
        
        if message_type == 'direct' and not data.get('recipient_ids'):
            raise serializers.ValidationError(
                "Recipient IDs are required for direct messages"
            )
        elif message_type == 'group' and not data.get('group_id'):
            raise serializers.ValidationError(
                "Group ID is required for group messages"
            )
        elif message_type == 'class' and not data.get('class_id'):
            raise serializers.ValidationError(
                "Class ID is required for class messages"
            )
        
        return data

class MessageRecipientSerializer(serializers.ModelSerializer):
    message = MessageSerializer(read_only=True)
    recipient = UserBasicSerializer(read_only=True)

    class Meta:
        model = MessageRecipient
        fields = [
            'id', 'message', 'recipient', 'is_read', 'read_at',
            'is_archived', 'archived_at', 'created_at'
        ]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'channel', 'title', 'message',
            'action_url', 'action_text', 'is_read', 'read_at',
            'scheduled_for', 'expires_at', 'created_at'
        ]
        read_only_fields = ['is_read', 'read_at', 'created_at']

class ParentTeacherMeetingSerializer(serializers.ModelSerializer):
    teacher = serializers.StringRelatedField()
    student = serializers.StringRelatedField()
    parents = UserBasicSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    participant_count = serializers.IntegerField(source='parents.count', read_only=True)

    class Meta:
        model = ParentTeacherMeeting
        fields = [
            'id', 'meeting_type', 'title', 'description', 'teacher', 'student',
            'parents', 'start_time', 'end_time', 'duration_minutes', 'location',
            'online_meeting_link', 'is_online', 'status', 'agenda', 'notes',
            'outcome', 'follow_up_required', 'follow_up_notes', 'created_by',
            'created_at', 'updated_at', 'participant_count'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class ParentTeacherMeetingCreateSerializer(serializers.ModelSerializer):
    parent_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = ParentTeacherMeeting
        fields = [
            'meeting_type', 'title', 'description', 'teacher', 'student',
            'start_time', 'end_time', 'location', 'online_meeting_link',
            'is_online', 'agenda', 'parent_ids'
        ]

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(
                "End time must be after start time"
            )
        
        if data['start_time'] < timezone.now():
            raise serializers.ValidationError(
                "Meeting cannot be scheduled in the past"
            )
        
        return data

class MeetingParticipantSerializer(serializers.ModelSerializer):
    parent = UserBasicSerializer(read_only=True)
    meeting = ParentTeacherMeetingSerializer(read_only=True)

    class Meta:
        model = MeetingParticipant
        fields = [
            'id', 'meeting', 'parent', 'status', 'confirmation_date',
            'notes', 'created_at'
        ]

class CommunicationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationPreference
        fields = [
            'id', 'receive_announcements', 'receive_grades_notifications',
            'receive_attendance_notifications', 'receive_event_reminders',
            'receive_assignment_notifications', 'receive_behavior_notifications',
            'preferred_channel', 'email_notifications', 'sms_notifications',
            'push_notifications', 'in_app_notifications', 'quiet_hours_start',
            'quiet_hours_end', 'updated_at'
        ]

class FeedbackSerializer(serializers.ModelSerializer):
    submitted_by = UserBasicSerializer(read_only=True)
    assigned_to = UserBasicSerializer(read_only=True)
    responded_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'feedback_type', 'title', 'description', 'submitted_by',
            'contact_email', 'status', 'priority', 'assigned_to', 'admin_notes',
            'response', 'responded_at', 'responded_by', 'is_anonymous',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'submitted_by', 'assigned_to', 'responded_by',
            'responded_at', 'created_at', 'updated_at'
        ]

class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'feedback_type', 'title', 'description', 'contact_email',
            'priority', 'is_anonymous'
        ]

# Statistics Serializers
class CommunicationStatisticsSerializer(serializers.Serializer):
    total_announcements = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    total_notifications = serializers.IntegerField()
    total_meetings = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    upcoming_meetings = serializers.IntegerField()

class AnnouncementStatisticsSerializer(serializers.Serializer):
    total_announcements = serializers.IntegerField()
    published_announcements = serializers.IntegerField()
    scheduled_announcements = serializers.IntegerField()
    expired_announcements = serializers.IntegerField()
    by_audience = serializers.DictField()
    by_priority = serializers.DictField()

class MessageStatisticsSerializer(serializers.Serializer):
    total_messages = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    sent_messages = serializers.IntegerField()
    received_messages = serializers.IntegerField()
    by_type = serializers.DictField()