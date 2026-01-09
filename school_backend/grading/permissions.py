# grading/permissions.py
from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    """Check if user is a teacher"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'teacher'

class IsPrincipal(permissions.BasePermission):
    """Check if user is a principal"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'principal'

class IsAdminOrTeacher(permissions.BasePermission):
    """Allow access to admins and teachers"""
    def has_permission(self, request, view):
        return request.user.is_staff or (
            hasattr(request.user, 'role') and request.user.role == 'teacher'
        )

class IsAdminOrPrincipal(permissions.BasePermission):
    """Allow access to admins and principals"""
    def has_permission(self, request, view):
        return request.user.is_staff or (
            hasattr(request.user, 'role') and request.user.role == 'principal'
        )

class IsStudentOwner(permissions.BasePermission):
    """Allow students to access their own grades"""
    def has_object_permission(self, request, view, obj):
        # Check if object has student attribute
        if hasattr(obj, 'student'):
            return obj.student == request.user
        return False

class IsParentOrStudent(permissions.BasePermission):
    """Allow parents and students to access report cards"""
    def has_permission(self, request, view):
        return request.user.role in ['parent', 'student']
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'student':
            return obj.student == request.user
        elif request.user.role == 'parent':
            # Check if student is child of parent
            return obj.student in request.user.parent.children.all()
        return False