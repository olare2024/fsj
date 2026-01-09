"""
administration/permissions.py
Custom permissions for Delvok Academy Administration.
"""

from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Read-only access for authenticated users.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff


class CanManageArticles(permissions.BasePermission):
    """Permission to manage articles"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user has specific permission
        if hasattr(request.user, 'has_perm'):
            return (
                request.user.has_perm('administration.can_publish_article') or
                request.user.has_perm('administration.can_feature_article') or
                request.user.is_staff
            )
        
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is the creator or has admin permissions
        if hasattr(request.user, 'has_perm'):
            return (
                obj.created_by == request.user or
                request.user.has_perm('administration.can_publish_article') or
                request.user.has_perm('administration.can_feature_article') or
                request.user.is_staff
            )
        
        return request.user and request.user.is_staff


class CanManageCarousel(permissions.BasePermission):
    """Permission to manage carousel images"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


class CanViewAccessLogs(permissions.BasePermission):
    """Permission to view access logs"""
    
    def has_permission(self, request, view):
        # Only admin users can view access logs
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Only admin users can view access logs
        return request.user and request.user.is_staff


class CanManageSchool(permissions.BasePermission):
    """Permission to manage schools"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only superusers can create/update/delete schools
        return request.user and request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only superusers can update/delete schools
        return request.user and request.user.is_superuser


class CanManageDays(permissions.BasePermission):
    """Permission to manage days"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only admin users can manage days
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only admin users can manage days
        return request.user and request.user.is_staff


class CanManageSettings(permissions.BasePermission):
    """Permission to manage system settings"""
    
    def has_permission(self, request, view):
        # Only superusers can manage settings
        return request.user and request.user.is_superuser


class IsSchoolAdmin(permissions.BasePermission):
    """Permission for school administrators"""
    
    def has_permission(self, request, view):
        # Check if user is admin or has school admin role
        if request.user and request.user.is_staff:
            return True
        
        # Check for specific role
        if hasattr(request.user, 'role'):
            return request.user.role in ['admin', 'school_admin', 'principal']
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # School admins can manage their own school's data
        if hasattr(obj, 'school'):
            # Check if user is associated with this school
            if hasattr(request.user, 'school') and request.user.school == obj.school:
                return True
        
        return self.has_permission(request, view)


class IsContentManager(permissions.BasePermission):
    """Permission for content managers"""
    
    def has_permission(self, request, view):
        # Check if user has content management permissions
        if request.user and request.user.is_staff:
            return True
        
        # Check for specific role or permissions
        if hasattr(request.user, 'role'):
            return request.user.role in ['content_manager', 'editor']
        
        # Check for specific permissions
        if hasattr(request.user, 'has_perm'):
            return (
                request.user.has_perm('administration.can_publish_article') or
                request.user.has_perm('administration.can_feature_article') or
                request.user.has_perm('administration.can_manage_carousel')
            )
        
        return False


class PublicReadOnly(permissions.BasePermission):
    """Permission for public read-only access"""
    
    def has_permission(self, request, view):
        # Only allow safe methods (GET, HEAD, OPTIONS)
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        # Only allow safe methods (GET, HEAD, OPTIONS)
        return request.method in permissions.SAFE_METHODS


# ==================== PERMISSION HELPERS ====================

def get_user_permissions(user):
    """Get all permissions for a user"""
    permissions = {
        'can_manage_articles': CanManageArticles().has_permission(None, None),
        'can_manage_carousel': CanManageCarousel().has_permission(None, None),
        'can_view_access_logs': CanViewAccessLogs().has_permission(None, None),
        'can_manage_school': CanManageSchool().has_permission(None, None),
        'can_manage_days': CanManageDays().has_permission(None, None),
        'can_manage_settings': CanManageSettings().has_permission(None, None),
        'is_school_admin': IsSchoolAdmin().has_permission(None, None),
        'is_content_manager': IsContentManager().has_permission(None, None),
        'is_admin': user.is_staff,
        'is_superuser': user.is_superuser,
    }
    
    # Check actual permissions
    if hasattr(user, 'has_perm'):
        permissions.update({
            'can_publish_article': user.has_perm('administration.can_publish_article'),
            'can_feature_article': user.has_perm('administration.can_feature_article'),
            'can_schedule_article': user.has_perm('administration.can_schedule_article'),
            'can_delete_article': user.has_perm('administration.can_delete_article'),
        })
    
    return permissions


def check_permission(user, permission_class):
    """Check if user has a specific permission"""
    if not user or not user.is_authenticated:
        return False
    
    # Create instance of permission class
    permission = permission_class()
    
    # Check permission
    return permission.has_permission(None, None)