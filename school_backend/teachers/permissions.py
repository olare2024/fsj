# teachers/permissions.py
from rest_framework import permissions


class IsDepartmentHOD(permissions.BasePermission):
    """Permission to allow Department HODs to access their department data"""
    
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        
        if hasattr(request.user, 'teacher_profile'):
            return request.user.teacher_profile.departments_headed.exists()
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if hasattr(request.user, 'teacher_profile'):
            if hasattr(obj, 'department'):
                return obj.department.hod == request.user.teacher_profile
            elif hasattr(obj, 'teacher'):
                return obj.teacher.department.hod == request.user.teacher_profile
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners to edit objects"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'teacher'):
            return obj.teacher.teacher == request.user
        
        if hasattr(obj, 'teacher_profile'):
            return obj.teacher_profile.teacher == request.user
        
        return False