# permissions.py
from rest_framework import permissions

class IsEventCoordinator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.coordinator == request.user

class IsEventCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class CanApproveEvents(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('events.can_approve_event')