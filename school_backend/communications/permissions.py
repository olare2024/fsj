from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()

class IsTeacher(permissions.BasePermission):
    """
    Check if user is a teacher
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

class IsParent(permissions.BasePermission):
    """
    Check if user is a parent
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'parent'

class IsStudent(permissions.BasePermission):
    """
    Check if user is a student
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class CanSendMessages(permissions.BasePermission):
    """
    Check if user can send messages based on their role and restrictions
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin and teachers can always send messages
        if request.user.role in ['admin', 'head_teacher', 'teacher']:
            return True
        
        # Parents can send messages to teachers and admins
        if request.user.role == 'parent' and view.action == 'create':
            return True
        
        # Students might have restrictions (check school policy)
        if request.user.role == 'student' and view.action == 'create':
            # Allow students to send messages to teachers
            return True
        
        return True

class IsMessageRecipient(permissions.BasePermission):
    """
    Check if user is a recipient of the message
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'recipients'):
            return request.user in obj.recipients.all()
        return False

class IsMessageSender(permissions.BasePermission):
    """
    Check if user is the sender of the message
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        return False

class IsGroupMember(permissions.BasePermission):
    """
    Check if user is a member of the message group
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'members'):
            return request.user in obj.members.all()
        return False

class IsGroupAdmin(permissions.BasePermission):
    """
    Check if user is an admin of the message group
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'groupmembership_set'):
            try:
                membership = obj.groupmembership_set.get(user=request.user)
                return membership.role in ['admin', 'moderator']
            except:
                return False
        return False

class CanCreateAnnouncement(permissions.BasePermission):
    """
    Check if user can create announcements
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only staff, teachers, and admins can create announcements
        return request.user.role in ['admin', 'head_teacher', 'teacher']

class IsMeetingParticipant(permissions.BasePermission):
    """
    Check if user is a participant in the meeting
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'parents'):
            return request.user in obj.parents.all()
        if hasattr(obj, 'teacher'):
            return obj.teacher.user == request.user
        return False

class IsFeedbackOwner(permissions.BasePermission):
    """
    Check if user is the owner of the feedback
    """
    def has_object_permission(self, request, view, obj):
        return obj.submitted_by == request.user

class CanManageFeedback(permissions.BasePermission):
    """
    Check if user can manage (assign, respond to) feedback
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only admins and head teachers can manage feedback
        return request.user.role in ['admin', 'head_teacher']
    
    def has_object_permission(self, request, view, obj):
        return request.user.role in ['admin', 'head_teacher']

class IsNotificationRecipient(permissions.BasePermission):
    """
    Check if user is the recipient of the notification
    """
    def has_object_permission(self, request, view, obj):
        return obj.recipient == request.user

class HasCommunicationPreferencesAccess(permissions.BasePermission):
    """
    Check if user can access communication preferences
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user