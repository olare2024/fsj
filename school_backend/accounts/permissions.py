# accounts/permissions.py - COMPREHENSIVE ENHANCED VERSION
import logging
from datetime import datetime, time
from functools import lru_cache

from django.core.cache import cache
from django.utils import timezone
from rest_framework import permissions

from .models import User, UserRole  # IMPORTANT: Import UserRole

logger = logging.getLogger(__name__)


# ==================== CORE ROLE PERMISSIONS ====================

class IsAdminUser(permissions.BasePermission):
    """Allows access only to users with Admin role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.ADMIN  # CHANGED
        )


class IsHeadTeacherUser(permissions.BasePermission):
    """Allows access only to users with Head Teacher role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.HEAD_TEACHER  # CHANGED
        )


class IsCurriculumCoordinatorUser(permissions.BasePermission):
    """Allows access only to users with Curriculum Coordinator role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.CURRICULUM_COORDINATOR  # CHANGED
        )


class IsTeacherUser(permissions.BasePermission):
    """Allows access only to users with Teacher role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.TEACHER  # CHANGED
        )


class IsOfficeStaffUser(permissions.BasePermission):
    """Allows access only to users with Office Staff role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.OFFICE_STAFF  # CHANGED
        )


class IsStudentUser(permissions.BasePermission):
    """Allows access only to users with Student role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.STUDENT  # CHANGED
        )


class IsParentUser(permissions.BasePermission):
    """Allows access only to users with Parent role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.PARENT  # CHANGED
        )


class IsLibrarianUser(permissions.BasePermission):
    """Allows access only to users with Librarian role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.LIBRARIAN  # CHANGED
        )


class IsAccountantUser(permissions.BasePermission):
    """Allows access only to users with Accountant role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.ACCOUNTANT  # CHANGED
        )


class IsITSupportUser(permissions.BasePermission):
    """Allows access only to users with IT Support role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.IT_SUPPORT  # CHANGED
        )


# Add these classes to your existing accounts/permissions.py file
# They're the missing classes that your views are trying to import

class IsAdmin(permissions.BasePermission):
    """Allows access only to users with Admin role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.ADMIN  # CHANGED
        )


class IsTeacher(permissions.BasePermission):
    """Allows access only to users with Teacher role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.TEACHER  # CHANGED
        )


class IsStudent(permissions.BasePermission):
    """Allows access only to users with Student role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.STUDENT  # CHANGED
        )


class IsParent(permissions.BasePermission):
    """Allows access only to users with Parent role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.PARENT  # CHANGED
        )


# Add aliases for backward compatibility with existing code
# Note: These aliases are already defined above, so we don't need to redefine them
# IsAdminUser = IsAdmin  # Already defined above
# IsTeacherUser = IsTeacher  # Already defined above
# IsStudentUser = IsStudent  # Already defined above
# IsParentUser = IsParent  # Already defined above

class IsCounselorUser(permissions.BasePermission):
    """Allows access only to users with Counselor role."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == UserRole.COUNSELOR  # CHANGED
        )


# ==================== COMPOSITE ROLE PERMISSIONS ====================

class IsStaffUser(permissions.BasePermission):
    """Allows access only to staff users (all staff roles except students and parents)."""
    
    STAFF_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.OFFICE_STAFF,  # CHANGED
        UserRole.LIBRARIAN,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.IT_SUPPORT,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.STAFF_ROLES
        )


class IsAcademicStaff(permissions.BasePermission):
    """Allows access to academic staff (teachers, coordinators, head teachers)."""
    
    ACADEMIC_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.LIBRARIAN,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.ACADEMIC_ROLES
        )


class IsAdministrativeStaff(permissions.BasePermission):
    """Allows access to administrative staff."""
    
    ADMIN_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.OFFICE_STAFF,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.IT_SUPPORT,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.ADMIN_ROLES
        )


class IsFinanceStaff(permissions.BasePermission):
    """Allows access to finance-related staff."""
    
    FINANCE_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.FINANCE_ROLES
        )


# ==================== STATUS-BASED PERMISSIONS ====================

class IsVerifiedUser(permissions.BasePermission):
    """Allows access only to verified users."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_verified
        )


class IsApprovedUser(permissions.BasePermission):
    """Allows access only to approved users (for roles that require approval)."""
    
    NO_APPROVAL_NEEDED = [UserRole.STUDENT, UserRole.PARENT]  # CHANGED
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Roles that don't require approval
        if request.user.role in self.NO_APPROVAL_NEEDED:
            return True
        
        return request.user.is_approved


class IsActiveUser(permissions.BasePermission):
    """Allows access only to active (non-suspended) users."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_active and 
            not request.user.is_suspended
        )


# ==================== OBJECT-LEVEL PERMISSIONS ====================

class IsOwnerOrAdmin(permissions.BasePermission):
    """Allows access to object owners or admin users."""
    
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.role == UserRole.ADMIN:  # CHANGED
            return True
        
        # Check if the object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object is the user itself
        if hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsSameUserOrAdmin(permissions.BasePermission):
    """Allows users to access their own data or admin to access any user's data."""
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.role == UserRole.ADMIN:  # CHANGED
            return True
        
        # Users can access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsParentOfStudent(permissions.BasePermission):
    """Allows parents to access their children's data."""
    
    def has_object_permission(self, request, view, obj):
        # Admin and teachers can access all student data
        if request.user.role in [UserRole.ADMIN, UserRole.TEACHER, UserRole.HEAD_TEACHER]:  # CHANGED
            return True
        
        # Parents can only access their children's data
        if request.user.role == UserRole.PARENT:  # CHANGED
            try:
                from students.models import Parent
                parent_profile = request.user.parent_profile
                
                # Check if object is a student profile
                if hasattr(obj, 'student_profile'):
                    return parent_profile.students.filter(id=obj.student_profile.id).exists()
                
                # Check if object is a student-related record
                if hasattr(obj, 'student'):
                    return parent_profile.students.filter(id=obj.student.id).exists()
                
                # Check if object is a StudentProfile
                if obj.__class__.__name__ == 'StudentProfile':
                    return parent_profile.students.filter(id=obj.id).exists()
                    
            except (AttributeError, ImportError):
                return False
        
        return False
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


# ==================== CAPABILITY-BASED PERMISSIONS ====================

class CanManageUsers(permissions.BasePermission):
    """Allows access to users who can manage other users."""
    
    MANAGEMENT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.IT_SUPPORT,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.MANAGEMENT_ROLES
        )


class CanManageStudents(permissions.BasePermission):
    """Allows access to users who can manage students."""
    
    STUDENT_MANAGEMENT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
        UserRole.OFFICE_STAFF,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.STUDENT_MANAGEMENT_ROLES
        )


class CanManageAcademicContent(permissions.BasePermission):
    """Allows access to users who can manage academic content."""
    
    ACADEMIC_CONTENT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.LIBRARIAN,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.ACADEMIC_CONTENT_ROLES
        )


class CanViewReports(permissions.BasePermission):
    """Allows access to users who can view reports."""
    
    REPORT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.PARENT,  # CHANGED - Parents can view their children's reports
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.REPORT_ROLES
        )


# ==================== PERMISSION-SYSTEM PERMISSIONS ====================

class HasPermission(permissions.BasePermission):
    """Generic permission checker based on user permissions."""
    
    def __init__(self, required_permission):
        self.required_permission = required_permission
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_permissions = request.user.get_permissions()
        
        # Check if user has the required permission or wildcard access
        return (
            self.required_permission in user_permissions or
            '*' in user_permissions or
            request.user.role == UserRole.ADMIN  # CHANGED
        )


class HasAnyPermission(permissions.BasePermission):
    """Allows access if user has any of the specified permissions."""
    
    def __init__(self, required_permissions):
        self.required_permissions = required_permissions
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_permissions = request.user.get_permissions()
        
        # Admin has all permissions
        if request.user.role == UserRole.ADMIN:  # CHANGED
            return True
        
        # Check if user has any of the required permissions
        return any(
            perm in user_permissions or perm == '*' 
            for perm in self.required_permissions
        )


# ==================== READ-ONLY PATTERNS ====================

class ReadOnly(permissions.BasePermission):
    """Allows read-only access for all authenticated users."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.method in permissions.SAFE_METHODS
        )


class ReadOnlyOrAdmin(permissions.BasePermission):
    """Allows read-only access for all authenticated users, but write access only for admin."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.role == UserRole.ADMIN  # CHANGED


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allows owners to edit their objects, but read-only for others."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsStaffOrReadOnly(permissions.BasePermission):
    """Allows staff users to edit, but read-only for non-staff users."""
    
    STAFF_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.OFFICE_STAFF,  # CHANGED
        UserRole.LIBRARIAN,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.IT_SUPPORT,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return (
            request.user.is_authenticated and 
            request.user.role in self.STAFF_ROLES
        )


# ==================== STUDENT-SPECIFIC PERMISSIONS ====================

class IsStudentOrParent(permissions.BasePermission):
    """Allows access to students or parents."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in [UserRole.STUDENT, UserRole.PARENT]  # CHANGED
        )


class IsStudentOwner(permissions.BasePermission):
    """Allows students to access only their own data."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.role != UserRole.STUDENT:  # CHANGED
            return False
        
        # Get student_id from view kwargs
        student_id = view.kwargs.get('student_id') or view.kwargs.get('pk')
        
        # If no student_id in URL, it's about current user
        if student_id is None:
            return True
        
        # Check if student_id matches current user's student profile
        try:
            return str(request.user.student_profile.id) == str(student_id)
        except AttributeError:
            return False


class CanViewStudentData(permissions.BasePermission):
    """Allows users to view student data based on their role."""
    
    @lru_cache(maxsize=128)
    def _check_teacher_access(self, user, student_id):
        """Cached method to check teacher access to student."""
        try:
            from academics.models import SubjectAssignment
            from students.models import StudentEnrollment
            
            student_enrollment = StudentEnrollment.objects.filter(
                student_id=student_id,
                status='active'
            ).first()
            
            if not student_enrollment:
                return False
            
            return SubjectAssignment.objects.filter(
                teacher__user=user,
                class_assigned=student_enrollment.class_enrolled
            ).exists()
        except (ImportError, AttributeError):
            return False
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get student_id from view kwargs
        student_id = view.kwargs.get('student_id') or view.kwargs.get('pk')
        
        # Admin and head teacher can view all student data
        if request.user.role in [UserRole.ADMIN, UserRole.HEAD_TEACHER]:  # CHANGED
            return True
        
        # If no student_id specified, allow access based on role
        if student_id is None:
            return request.user.role in [
                UserRole.STUDENT,  # CHANGED
                UserRole.PARENT,  # CHANGED
                UserRole.TEACHER,  # CHANGED
                UserRole.CURRICULUM_COORDINATOR,  # CHANGED
                UserRole.COUNSELOR,  # CHANGED
            ]
        
        # Check specific permissions for the given student_id
        cache_key = f"student_access_{request.user.id}_{student_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        result = self._check_student_access(request.user, student_id)
        cache.set(cache_key, result, timeout=300)  # 5 minutes
        return result
    
    def _check_student_access(self, user, student_id):
        """Check if user can access specific student data."""
        if user.role == UserRole.STUDENT:  # CHANGED
            # Students can only view their own data
            try:
                return str(user.student_profile.id) == str(student_id)
            except AttributeError:
                return False
        
        elif user.role == UserRole.PARENT:  # CHANGED
            # Parents can only view their children's data
            try:
                from students.models import Parent
                parent_profile = user.parent_profile
                return parent_profile.students.filter(id=student_id).exists()
            except (AttributeError, ImportError):
                return False
        
        elif user.role == UserRole.TEACHER:  # CHANGED
            # Teachers can view data of students in their classes
            return self._check_teacher_access(user, student_id)
        
        elif user.role == UserRole.COUNSELOR:  # CHANGED
            # Counselors can view student data
            return True
        
        return False


class CanManageStudentAttendance(permissions.BasePermission):
    """Allows users to manage student attendance."""
    
    ATTENDANCE_MANAGEMENT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.TEACHER,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.ATTENDANCE_MANAGEMENT_ROLES
        )


class CanViewStudentAttendance(permissions.BasePermission):
    """Allows users to view student attendance."""
    
    ATTENDANCE_VIEW_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.STUDENT,  # CHANGED
        UserRole.PARENT,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.ATTENDANCE_VIEW_ROLES
        )


class CanManageStudentGrades(permissions.BasePermission):
    """Allows users to manage student grades."""
    
    GRADE_MANAGEMENT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.GRADE_MANAGEMENT_ROLES
        )


class CanViewStudentGrades(permissions.BasePermission):
    """Allows users to view student grades."""
    
    GRADE_VIEW_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.STUDENT,  # CHANGED
        UserRole.PARENT,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.GRADE_VIEW_ROLES
        )


class CanManageStudentFees(permissions.BasePermission):
    """Allows users to manage student fees."""
    
    FEE_MANAGEMENT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.OFFICE_STAFF,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.FEE_MANAGEMENT_ROLES
        )


class CanViewStudentFees(permissions.BasePermission):
    """Allows users to view student fees."""
    
    FEE_VIEW_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.STUDENT,  # CHANGED
        UserRole.PARENT,  # CHANGED
        UserRole.OFFICE_STAFF,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.FEE_VIEW_ROLES
        )


from rest_framework import permissions
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Comprehensive permission class for teacher and admin access.
    Features:
    - Role-based access control
    - Caching for performance
    - Logging for audit trail
    - Configurable via settings
    - Graceful degradation
    """
    
    # Default allowed roles
    DEFAULT_ALLOWED_ROLES = ['ADMIN', 'TEACHER']
    
    # Cache settings
    CACHE_PREFIX = "perm_teacher_admin_"
    CACHE_TIMEOUT = getattr(settings, 'PERMISSION_CACHE_TIMEOUT', 300)
    
    @classmethod
    def get_allowed_roles(cls):
        """Get allowed roles from settings or use defaults."""
        return getattr(
            settings, 
            'TEACHER_ADMIN_ALLOWED_ROLES', 
            cls.DEFAULT_ALLOWED_ROLES
        )
    
    def has_permission(self, request, view):
        """
        Check if user has teacher or admin permission.
        
        Args:
            request: HTTP request object
            view: View being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Step 1: Basic authentication check
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Step 2: Check if user model has role attribute
        if not hasattr(request.user, 'role'):
            logger.debug(f"User {request.user.id} has no role attribute")
            return False
        
        # Step 3: Check cache
        user_id = request.user.id
        cache_key = f"{self.CACHE_PREFIX}{user_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Step 4: Check user status
        if hasattr(request.user, 'is_active') and not request.user.is_active:
            result = False
        elif hasattr(request.user, 'is_suspended') and request.user.is_suspended:
            result = False
        else:
            # Step 5: Check role
            allowed_roles = self.get_allowed_roles()
            result = request.user.role in allowed_roles
        
        # Step 6: Cache the result
        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        
        # Step 7: Log the result (debug level for success, warning for denial)
        if result:
            logger.debug(
                f"Permission granted: User {user_id} ({request.user.role}) "
                f"accessing {view.__class__.__name__}"
            )
        else:
            logger.warning(
                f"Permission denied: User {user_id} ({request.user.role}) "
                f"tried accessing {view.__class__.__name__}. "
                f"Allowed roles: {allowed_roles}"
            )
        
        return result
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.
        Can be extended for specific object types.
        """
        # Default: use same permission as has_permission
        # Override in subclasses for object-specific logic
        return self.has_permission(request, view)

class CanViewFees(CanViewStudentFees):
    """Alias for CanViewStudentFees for backward compatibility."""
    pass


class CanManageStudentDiscipline(permissions.BasePermission):
    """Allows users to manage student discipline records."""
    
    DISCIPLINE_MANAGEMENT_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.DISCIPLINE_MANAGEMENT_ROLES
        )


class CanViewStudentDiscipline(permissions.BasePermission):
    """Allows users to view student discipline records."""
    
    DISCIPLINE_VIEW_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
        UserRole.PARENT,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.DISCIPLINE_VIEW_ROLES
        )


class CanViewDashboard(permissions.BasePermission):
    """Allows users to view their dashboard."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


# ==================== ENHANCED PERMISSIONS ====================

class HasRoleAtLeast(permissions.BasePermission):
    """Allows access if user has role at or above minimum level."""
    
    ROLE_HIERARCHY = {
        UserRole.STUDENT: 0,  # CHANGED
        UserRole.PARENT: 1,  # CHANGED
        UserRole.LIBRARIAN: 2,  # CHANGED
        UserRole.IT_SUPPORT: 2,  # CHANGED
        UserRole.ACCOUNTANT: 3,  # CHANGED
        UserRole.OFFICE_STAFF: 3,  # CHANGED
        UserRole.COUNSELOR: 4,  # CHANGED
        UserRole.TEACHER: 5,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR: 6,  # CHANGED
        UserRole.HEAD_TEACHER: 7,  # CHANGED
        UserRole.ADMIN: 10,  # CHANGED
    }
    
    def __init__(self, min_role):
        self.min_role = min_role
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role_level = self.ROLE_HIERARCHY.get(request.user.role, 0)
        min_role_level = self.ROLE_HIERARCHY.get(self.min_role, 0)
        
        return user_role_level >= min_role_level


class HasAccessDuringHours(permissions.BasePermission):
    """Restrict access to specific hours of the day."""
    
    def __init__(self, start_time=(8, 0), end_time=(17, 0)):
        self.start_time = time(*start_time)
        self.end_time = time(*end_time)
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        current_time = datetime.now().time()
        
        # Check if current time is within allowed hours
        return self.start_time <= current_time <= self.end_time


class HasAccessInContext(permissions.BasePermission):
    """Check permissions based on request context (e.g., school year, term)."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get context from request or view
        context = getattr(view, 'access_context', {})
        
        # Check if current term is active
        if not context.get('current_term_active', True):
            return False
        
        # Check school year
        if 'allowed_school_years' in context:
            current_year = context.get('current_school_year')
            if current_year not in context['allowed_school_years']:
                return False
        
        return True


# ==================== LOGGING MIXIN ====================

class LoggingPermissionMixin:
    """Mixin to log permission denials for audit trails."""
    
    def log_permission_denial(self, request, view, reason):
        logger.warning(
            f"Permission denied for user {request.user.id} ({request.user.email}) "
            f"on view {view.__class__.__name__}: {reason} "
            f"at {timezone.now()} - Method: {request.method}"
        )
    
    def has_permission(self, request, view):
        result = super().has_permission(request, view)
        if not result:
            self.log_permission_denial(request, view, "Permission check failed")
        return result


# ==================== PERMISSION COMBINATIONS ====================

class IsActiveVerifiedUser(permissions.BasePermission):
    """Combination permission for active and verified users."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.is_active and 
            request.user.is_verified and
            not request.user.is_suspended
        )


class IsTeacherOrHeadTeacher(permissions.BasePermission):
    """Combination permission for teachers or head teachers."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in [UserRole.TEACHER, UserRole.HEAD_TEACHER]  # CHANGED
        )


class IsAcademicOrAdmin(permissions.BasePermission):
    """Combination permission for academic staff or admin."""
    
    ACADEMIC_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.LIBRARIAN,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.ACADEMIC_ROLES
        )


class IsStaffOrAdmin(permissions.BasePermission):
    """Combination permission for staff users or admin."""
    
    STAFF_ROLES = [
        UserRole.ADMIN,  # CHANGED
        UserRole.HEAD_TEACHER,  # CHANGED
        UserRole.CURRICULUM_COORDINATOR,  # CHANGED
        UserRole.TEACHER,  # CHANGED
        UserRole.OFFICE_STAFF,  # CHANGED
        UserRole.LIBRARIAN,  # CHANGED
        UserRole.ACCOUNTANT,  # CHANGED
        UserRole.IT_SUPPORT,  # CHANGED
        UserRole.COUNSELOR,  # CHANGED
    ]
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in self.STAFF_ROLES
        )


# ==================== PERMISSION FACTORIES ====================

def create_permission_combination(*permission_classes):
    """Helper function to create permission combinations dynamically."""
    
    class CombinedPermission(permissions.BasePermission):
        def has_permission(self, request, view):
            return all(
                permission().has_permission(request, view)
                for permission in permission_classes
            )
    
    return CombinedPermission


# Pre-defined permission combinations
IsActiveVerifiedStaff = create_permission_combination(
    permissions.IsAuthenticated,
    IsActiveUser,
    IsVerifiedUser,
    IsStaffUser
)

IsAcademicStaffWithApproval = create_permission_combination(
    permissions.IsAuthenticated,
    IsActiveUser,
    IsVerifiedUser,
    IsApprovedUser,
    IsAcademicStaff
)

IsStudentOwnerOrParent = create_permission_combination(
    permissions.IsAuthenticated,
    IsStudentOrParent,
    CanViewStudentData
)

CanManageStudentRecords = create_permission_combination(
    permissions.IsAuthenticated,
    IsActiveUser,
    CanManageStudents
)


# ==================== PERMISSION GROUPS ====================

class PermissionGroup:
    """Group multiple permissions for easier management."""
    
    GROUPS = {
        'student_management': [
            IsActiveUser,
            CanManageStudents,
            IsAcademicOrAdmin,
        ],
        'finance_access': [
            IsActiveUser,
            IsVerifiedUser,
            IsFinanceStaff,
        ],
        'academic_content': [
            IsActiveUser,
            IsVerifiedUser,
            IsApprovedUser,
            CanManageAcademicContent,
        ],
        'admin_only': [
            IsActiveUser,
            IsAdminUser,
        ],
        'teacher_access': [
            IsActiveUser,
            IsVerifiedUser,
            IsApprovedUser,
            IsTeacherUser,
        ],
    }
    
    @classmethod
    def get_group(cls, name):
        """Get a permission group by name."""
        return cls.GROUPS.get(name, [permissions.IsAuthenticated])
    
    @classmethod
    def create_group(cls, name, permissions_list):
        """Create a new permission group."""
        cls.GROUPS[name] = permissions_list
        return permissions_list


# ==================== PERMISSION BUILDER ====================

class PermissionBuilder:
    """Build complex permission rules dynamically."""
    
    @staticmethod
    def create_field_based_permission(allowed_fields, allowed_roles):
        """
        Create permission with field-level access control.
        
        Args:
            allowed_fields: Dict of {field_name: [allowed_roles]}
            allowed_roles: List of roles that can access all fields
        """
        
        class FieldBasedPermission(permissions.BasePermission):
            def has_permission(self, request, view):
                return request.user.is_authenticated
            
            def has_object_permission(self, request, view, obj):
                # Check if user role has full access
                if request.user.role in allowed_roles:
                    return True
                
                # For PATCH/PUT, check each field being updated
                if request.method in ['PATCH', 'PUT']:
                    update_fields = request.data.keys()
                    for field in update_fields:
                        field_roles = allowed_fields.get(field, [])
                        if request.user.role not in field_roles:
                            return False
                
                return True
        
        return FieldBasedPermission
    
    @staticmethod
    def create_action_based_permission(actions_permissions):
        """
        Create permission with action-based access control.
        
        Args:
            actions_permissions: Dict of {action: [permission_classes]}
        """
        
        class ActionBasedPermission(permissions.BasePermission):
            def has_permission(self, request, view):
                action = getattr(view, 'action', None)
                
                if action is None:
                    # For non-viewset views
                    action = view.__class__.__name__.lower()
                
                permissions_list = actions_permissions.get(
                    action, 
                    [permissions.IsAuthenticated]
                )
                
                # Check all permissions in the list
                return all(
                    perm().has_permission(request, view)
                    for perm in permissions_list
                )
        
        return ActionBasedPermission


# ==================== DECORATOR-BASED PERMISSION CHECKERS ====================

def check_permission(permission_class):
    """Decorator to check permissions on view methods."""
    
    def decorator(view_method):
        def wrapper(self, request, *args, **kwargs):
            permission = permission_class()
            if not permission.has_permission(request, self):
                from rest_framework.response import Response
                from rest_framework import status
                return Response(
                    {'error': 'You do not have permission to perform this action.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_method(self, request, *args, **kwargs)
        return wrapper
    return decorator


def check_object_permission(permission_class):
    """Decorator to check object-level permissions on view methods."""
    
    def decorator(view_method):
        def wrapper(self, request, *args, **kwargs):
            # Get the object
            obj = self.get_object()
            
            # Check permission
            permission = permission_class()
            if not permission.has_object_permission(request, self, obj):
                from rest_framework.response import Response
                from rest_framework import status
                return Response(
                    {'error': 'You do not have permission to access this object.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_method(self, request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== PERMISSION UTILITIES ====================

def get_permissions_for_view(view_class, action=None):
    """Utility function to get appropriate permissions for a view based on action."""
    
    if action is None:
        action = getattr(view_class, 'action', 'default')
    
    permission_map = {
        # Student views
        'student_dashboard': [permissions.IsAuthenticated, CanViewDashboard],
        'student_profile': [permissions.IsAuthenticated, IsStudentOwner],
        'student_timetable': [permissions.IsAuthenticated, CanViewStudentData],
        'student_assignments': [permissions.IsAuthenticated, CanViewStudentData],
        'student_grades': [permissions.IsAuthenticated, CanViewStudentGrades],
        'student_attendance': [permissions.IsAuthenticated, CanViewStudentAttendance],
        'student_fees': [permissions.IsAuthenticated, CanViewStudentFees],
        'student_discipline': [permissions.IsAuthenticated, CanViewStudentDiscipline],
        
        # Teacher views
        'teacher_dashboard': [permissions.IsAuthenticated, IsTeacherUser],
        'manage_attendance': [permissions.IsAuthenticated, CanManageStudentAttendance],
        'manage_grades': [permissions.IsAuthenticated, CanManageStudentGrades],
        
        # Admin views
        'manage_users': [permissions.IsAuthenticated, CanManageUsers],
        'system_settings': [permissions.IsAuthenticated, IsAdminUser],
        
        # CRUD operations
        'list': [permissions.IsAuthenticated, CanManageStudents],
        'retrieve': [permissions.IsAuthenticated, CanViewStudentData],
        'create': [permissions.IsAuthenticated, CanManageStudents],
        'update': [permissions.IsAuthenticated, CanManageStudents],
        'partial_update': [permissions.IsAuthenticated, CanManageStudents],
        'destroy': [permissions.IsAuthenticated, IsAdminUser],
        
        # Default
        'default': [permissions.IsAuthenticated],
    }
    
    return permission_map.get(action, permission_map['default'])


def check_user_can_access_student(user, student_id):
    """Check if a user can access a specific student's data."""
    
    if not user.is_authenticated:
        return False
    
    # Admin and head teacher can access all students
    if user.role in [UserRole.ADMIN, UserRole.HEAD_TEACHER]:  # CHANGED
        return True
    
    # Check if user is the student
    if user.role == UserRole.STUDENT:  # CHANGED
        try:
            return str(user.student_profile.id) == str(student_id)
        except AttributeError:
            return False
    
    # Check if user is parent of the student
    if user.role == UserRole.PARENT:  # CHANGED
        try:
            from students.models import Parent
            parent_profile = user.parent_profile
            return parent_profile.students.filter(id=student_id).exists()
        except (AttributeError, ImportError):
            return False
    
    # Check if user is teacher of the student
    if user.role == UserRole.TEACHER:  # CHANGED
        try:
            from academics.models import SubjectAssignment
            from students.models import StudentEnrollment
            
            student_enrollment = StudentEnrollment.objects.filter(
                student_id=student_id,
                status='active'
            ).first()
            
            if not student_enrollment:
                return False
            
            return SubjectAssignment.objects.filter(
                teacher__user=user,
                class_assigned=student_enrollment.class_enrolled
            ).exists()
        except (ImportError, AttributeError):
            return False
    
    # Counselors can access student data
    if user.role == UserRole.COUNSELOR:  # CHANGED
        return True
    
    return False


def get_user_permissions_summary(user):
    """Get a summary of all permissions for a user."""
    
    if not user.is_authenticated:
        return {}
    
    permissions_summary = {
        'is_active': user.is_active and not user.is_suspended,
        'is_verified': user.is_verified,
        'is_approved': user.is_approved if hasattr(user, 'is_approved') else True,
        'role': user.role,
        'role_label': user.get_role_display(),
        'can_manage_users': user.role in CanManageUsers.MANAGEMENT_ROLES,
        'can_manage_students': user.role in CanManageStudents.STUDENT_MANAGEMENT_ROLES,
        'can_view_reports': user.role in CanViewReports.REPORT_ROLES,
        'can_manage_academic_content': user.role in CanManageAcademicContent.ACADEMIC_CONTENT_ROLES,
        'is_staff': user.role in IsStaffUser.STAFF_ROLES,
        'is_academic_staff': user.role in IsAcademicStaff.ACADEMIC_ROLES,
    }
    
    return permissions_summary


# ==================== PERMISSION MIDDLEWARE ====================

class PermissionMiddleware:
    """Middleware to add permission context to requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add permission summary to request
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.permissions = get_user_permissions_summary(request.user)
        
        response = self.get_response(request)
        return response