from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from .models import (
    Announcement, Message, MessageRecipient, MessageGroup,
    GroupMembership, Notification, ParentTeacherMeeting,
    MeetingParticipant, CommunicationPreference, Feedback
)
from .serializers import (
    AnnouncementSerializer, AnnouncementCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    MessageRecipientSerializer, MessageGroupSerializer, 
    MessageGroupCreateSerializer,
    NotificationSerializer, ParentTeacherMeetingSerializer,
    ParentTeacherMeetingCreateSerializer, MeetingParticipantSerializer,
    CommunicationPreferenceSerializer, FeedbackSerializer, 
    FeedbackCreateSerializer, CommunicationStatisticsSerializer,
    AnnouncementStatisticsSerializer, MessageStatisticsSerializer
)
from .filters import AnnouncementFilter, MessageFilter, NotificationFilter
from .permissions import IsTeacher, CanSendMessages, IsParent, IsStudent

User = get_user_model()

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnnouncementFilter
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        
        # Base queryset - only active announcements for list actions
        if self.action == 'list':
            queryset = Announcement.objects.filter(
                Q(is_published=True) &
                Q(Q(publish_at__isnull=True) | Q(publish_at__lte=now)) &
                Q(Q(expires_at__isnull=True) | Q(expires_at__gte=now))
            )
        else:
            queryset = Announcement.objects.all()
        
        # Filter by audience for non-admin users
        if not user.is_staff and user.role not in ['admin', 'head_teacher']:
            if user.role == 'student':
                queryset = queryset.filter(
                    Q(audience='all') | 
                    Q(audience='students') |
                    Q(specific_grades__contains=[user.grade_level]) |
                    Q(specific_classes__enrollments__student__user=user) |
                    Q(specific_users=user)
                ).distinct()
            elif user.role == 'parent':
                queryset = queryset.filter(
                    Q(audience='all') | 
                    Q(audience='parents') |
                    Q(specific_users=user)
                ).distinct()
            elif user.role == 'teacher':
                queryset = queryset.filter(
                    Q(audience='all') | 
                    Q(audience='teachers') |
                    Q(audience='staff') |
                    Q(specific_users=user)
                ).distinct()
        
        return queryset.select_related('created_by').prefetch_related(
            'specific_classes', 'specific_users'
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AnnouncementCreateSerializer
        return AnnouncementSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser | IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        
        # Only allow creators or admins to update
        if instance.created_by != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only update your own announcements")
        
        serializer.save()

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an announcement"""
        announcement = self.get_object()
        
        # Check permissions
        if (announcement.created_by != request.user and 
            not request.user.is_staff and 
            request.user.role not in ['admin', 'head_teacher']):
            raise PermissionDenied("You can only publish your own announcements")
        
        announcement.is_published = True
        announcement.published_at = timezone.now()
        announcement.save()
        
        return Response(
            {"message": "Announcement published successfully"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish an announcement"""
        announcement = self.get_object()
        
        if (announcement.created_by != request.user and 
            not request.user.is_staff):
            raise PermissionDenied("You can only unpublish your own announcements")
        
        announcement.is_published = False
        announcement.save()
        
        return Response(
            {"message": "Announcement unpublished successfully"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def my_announcements(self, request):
        """Get announcements created by the current user"""
        if not request.user.is_staff and request.user.role not in ['teacher', 'admin', 'head_teacher']:
            raise PermissionDenied("Only staff can create announcements")
        
        queryset = Announcement.objects.filter(created_by=request.user)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, CanSendMessages]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        
        # Users can see messages they sent or received
        return Message.objects.filter(
            Q(sender=user) | Q(recipients=user)
        ).distinct().select_related(
            'sender', 'group', 'class_recipient', 'parent_message'
        ).prefetch_related('recipients').order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        try:
            message = serializer.save(sender=self.request.user)
            
            # The recipients are handled in the model's save method
            # via the _create_recipients method
            
        except Exception as e:
            raise ValidationError(f"Error creating message: {str(e)}")

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a message as read for the current user"""
        try:
            message = self.get_object()
            
            # Get or create message recipient record
            message_recipient, created = MessageRecipient.objects.get_or_create(
                message=message,
                recipient=request.user,
                defaults={'is_read': True, 'read_at': timezone.now()}
            )
            
            if not created and not message_recipient.is_read:
                message_recipient.mark_as_read()
            
            return Response(
                {"message": "Message marked as read"},
                status=status.HTTP_200_OK
            )
            
        except Message.DoesNotExist:
            return Response(
                {"error": "Message not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Reply to a message"""
        parent_message = self.get_object()
        serializer = MessageCreateSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        
        if serializer.is_valid():
            try:
                reply = serializer.save(
                    sender=request.user,
                    parent_message=parent_message,
                    message_type='direct'
                )
                
                # Add original sender as recipient
                reply.recipients.add(parent_message.sender)
                
                return Response(
                    MessageSerializer(reply, context=self.get_serializer_context()).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": f"Error creating reply: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages"""
        unread_count = MessageRecipient.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        
        return Response({"unread_count": unread_count})

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get messages sent by the current user"""
        queryset = Message.objects.filter(sender=request.user)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get messages received by the current user"""
        queryset = Message.objects.filter(recipients=request.user)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MessageGroupViewSet(viewsets.ModelViewSet):
    serializer_class = MessageGroupSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        
        # Users can see groups they are members of or groups they created
        return MessageGroup.objects.filter(
            Q(members=user) | Q(created_by=user)
        ).distinct().select_related(
            'created_by', 'related_class', 'related_subject'
        ).prefetch_related('members').order_by('name')

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageGroupCreateSerializer
        return MessageGroupSerializer

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        
        # Add creator as admin member
        GroupMembership.objects.create(
            group=group,
            user=self.request.user,
            role='admin'
        )

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the group"""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if user has permission to add members
            membership = GroupMembership.objects.get(
                group=group, user=request.user
            )
            if membership.role not in ['admin', 'moderator']:
                raise PermissionDenied("You don't have permission to add members")
            
            user = User.objects.get(id=user_id)
            GroupMembership.objects.get_or_create(
                group=group,
                user=user,
                defaults={'role': 'member'}
            )
            
            return Response({"message": "Member added successfully"})
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except GroupMembership.DoesNotExist:
            raise PermissionDenied("You are not a member of this group")

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a member from the group"""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check if user has permission to remove members
            membership = GroupMembership.objects.get(
                group=group, user=request.user
            )
            if membership.role not in ['admin', 'moderator']:
                raise PermissionDenied("You don't have permission to remove members")
            
            # Prevent removing yourself if you're the only admin
            if str(user_id) == str(request.user.id):
                admin_count = GroupMembership.objects.filter(
                    group=group, role='admin'
                ).count()
                if admin_count <= 1:
                    return Response(
                        {"error": "Cannot remove the only admin from the group"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            GroupMembership.objects.filter(
                group=group, user_id=user_id
            ).delete()
            
            return Response({"message": "Member removed successfully"})
            
        except GroupMembership.DoesNotExist:
            raise PermissionDenied("You are not a member of this group")

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('recipient').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        
        if notification.recipient != request.user:
            raise PermissionDenied("You can only mark your own notifications as read")
        
        notification.mark_as_read()
        
        return Response({"message": "Notification marked as read"})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({"message": f"{updated} notifications marked as read"})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        
        return Response({"unread_count": unread_count})

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications (last 30 days)"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        queryset = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ParentTeacherMeetingViewSet(viewsets.ModelViewSet):
    serializer_class = ParentTeacherMeetingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'teacher':
            return ParentTeacherMeeting.objects.filter(teacher__user=user)
        elif user.role == 'parent':
            return ParentTeacherMeeting.objects.filter(parents=user)
        elif user.role in ['admin', 'head_teacher']:
            return ParentTeacherMeeting.objects.all()
        else:
            return ParentTeacherMeeting.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return ParentTeacherMeetingCreateSerializer
        return ParentTeacherMeetingSerializer

    def perform_create(self, serializer):
        meeting = serializer.save(created_by=self.request.user)
        
        # Add parents if provided
        parent_ids = self.request.data.get('parent_ids', [])
        if parent_ids:
            parents = User.objects.filter(id__in=parent_ids, role='parent')
            meeting.parents.set(parents)

    @action(detail=True, methods=['post'])
    def confirm_attendance(self, request, pk=None):
        """Confirm attendance for a meeting (for parents)"""
        if request.user.role != 'parent':
            raise PermissionDenied("Only parents can confirm attendance")
        
        meeting = self.get_object()
        
        try:
            participant = MeetingParticipant.objects.get(
                meeting=meeting, parent=request.user
            )
            participant.status = 'confirmed'
            participant.confirmation_date = timezone.now()
            participant.save()
            
            return Response({"message": "Attendance confirmed successfully"})
        except MeetingParticipant.DoesNotExist:
            return Response(
                {"error": "You are not a participant of this meeting"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update meeting status (for teachers/admins)"""
        meeting = self.get_object()
        new_status = request.data.get('status')
        
        # Check permissions
        if (meeting.teacher.user != request.user and 
            not request.user.is_staff and 
            request.user.role not in ['admin', 'head_teacher']):
            raise PermissionDenied("You can only update your own meetings")
        
        if new_status not in dict(ParentTeacherMeeting.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        meeting.status = new_status
        meeting.save()
        
        return Response({"message": f"Meeting status updated to {new_status}"})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming meetings"""
        queryset = self.get_queryset().filter(
            start_time__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('start_time')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CommunicationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = CommunicationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        return CommunicationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        # Always return the current user's preferences
        return CommunicationPreference.objects.get(user=self.request.user)

class FeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        
        if user.role in ['admin', 'head_teacher']:
            return Feedback.objects.all()
        else:
            return Feedback.objects.filter(submitted_by=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        return FeedbackSerializer

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

# Statistics and Dashboard Views
class CommunicationStatisticsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        now = timezone.now()
        
        statistics = {
            'total_announcements': Announcement.objects.filter(
                is_published=True,
                publish_at__lte=now,
                expires_at__gte=now
            ).count(),
            'total_messages': Message.objects.filter(
                Q(sender=user) | Q(recipients=user)
            ).distinct().count(),
            'total_notifications': Notification.objects.filter(recipient=user).count(),
            'total_meetings': ParentTeacherMeeting.objects.filter(
                Q(teacher__user=user) | Q(parents=user)
            ).distinct().count(),
            'unread_messages': MessageRecipient.objects.filter(
                recipient=user, is_read=False
            ).count(),
            'unread_notifications': Notification.objects.filter(
                recipient=user, is_read=False
            ).count(),
            'upcoming_meetings': ParentTeacherMeeting.objects.filter(
                Q(teacher__user=user) | Q(parents=user),
                start_time__gte=now,
                status__in=['scheduled', 'confirmed']
            ).distinct().count(),
        }
        
        serializer = CommunicationStatisticsSerializer(statistics)
        return Response(serializer.data)


# Add these classes to communications/views.py

class MessageRecipientView(generics.ListAPIView):
    """Get message recipients for a specific message"""
    serializer_class = MessageRecipientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        message_id = self.kwargs.get('message_id')
        user = self.request.user
        
        # Users can only see recipients for messages they sent or received
        return MessageRecipient.objects.filter(
            message_id=message_id,
            message__in=Message.objects.filter(
                Q(sender=user) | Q(recipients=user)
            )
        ).select_related('recipient', 'message')

class MeetingParticipantsView(generics.ListAPIView):
    """Get participants for a specific meeting"""
    serializer_class = MeetingParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_id')
        user = self.request.user
        
        # Users can only see participants for meetings they're involved in
        return MeetingParticipant.objects.filter(
            meeting_id=meeting_id,
            meeting__in=ParentTeacherMeeting.objects.filter(
                Q(teacher__user=user) | Q(parents=user) | Q(created_by=user)
            )
        ).select_related('parent', 'meeting')



class AnnouncementStatisticsView(generics.GenericAPIView):
    permission_classes = [IsAdminUser | IsTeacher]
    
    def get(self, request):
        now = timezone.now()
        
        statistics = {
            'total_announcements': Announcement.objects.count(),
            'published_announcements': Announcement.objects.filter(is_published=True).count(),
            'scheduled_announcements': Announcement.objects.filter(
                is_published=True, publish_at__gt=now
            ).count(),
            'expired_announcements': Announcement.objects.filter(
                expires_at__lt=now
            ).count(),
            'by_audience': dict(Announcement.objects.values('audience').annotate(
                count=Count('id')
            ).values_list('audience', 'count')),
            'by_priority': dict(Announcement.objects.values('priority').annotate(
                count=Count('id')
            ).values_list('priority', 'count')),
        }
        
        serializer = AnnouncementStatisticsSerializer(statistics)
        return Response(serializer.data)

class MyCommunicationsView(generics.GenericAPIView):
    """Get current user's communications dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        now = timezone.now()
        
        # Recent announcements
        recent_announcements = Announcement.objects.filter(
            is_published=True,
            publish_at__lte=now,
            expires_at__gte=now
        ).order_by('-created_at')[:5]
        
        # Unread messages
        unread_messages = MessageRecipient.objects.filter(
            recipient=user, is_read=False
        ).select_related('message__sender')[:10]
        
        # Recent notifications
        recent_notifications = Notification.objects.filter(
            recipient=user
        ).order_by('-created_at')[:10]
        
        # Upcoming meetings
        upcoming_meetings = ParentTeacherMeeting.objects.filter(
            Q(teacher__user=user) | Q(parents=user),
            start_time__gte=now,
            status__in=['scheduled', 'confirmed']
        ).order_by('start_time')[:5]
        
        dashboard_data = {
            'recent_announcements': AnnouncementSerializer(recent_announcements, many=True).data,
            'unread_messages': MessageRecipientSerializer(unread_messages, many=True).data,
            'recent_notifications': NotificationSerializer(recent_notifications, many=True).data,
            'upcoming_meetings': ParentTeacherMeetingSerializer(upcoming_meetings, many=True).data,
        }
        
        return Response(dashboard_data)