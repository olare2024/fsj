# accounts/views.py - CORRECTED VERSION WITH ALL IMPORTS

from rest_framework import viewsets, generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, logout
from django.db.models import Count, Q, F, Value
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import csv
import json
from datetime import datetime, timedelta
import logging

from .models import User, UserProfile, TwoFactorAuth, OTPToken, LoginHistory
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserDetailSerializer, UserUpdateSerializer, UserListSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    PasswordChangeSerializer, EmailVerificationSerializer,
    ResendVerificationSerializer, TwoFactorSetupSerializer,
    TwoFactorVerifySerializer, TwoFactorLoginSerializer,
    TwoFactorDisableSerializer, BackupCodesSerializer,
    UserCreateByAdminSerializer, UserUpdateByAdminSerializer,
    UserStatusUpdateSerializer, UserStatisticsSerializer,
    DashboardStatsSerializer, UserExportSerializer,
    UserSearchSerializer, UserFilterSerializer
)

logger = logging.getLogger(__name__)


# ============================================================================
# PERMISSION CLASSES
# ============================================================================

class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to allow owners or admins to access objects"""
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsProfileOwnerOrAdmin(permissions.BasePermission):
    """Permission to allow profile owners or admins"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission to allow admins full access, others read-only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class IsTeacherOrAdmin(permissions.BasePermission):
    """Permission for teachers and admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_teacher or request.user.is_staff
        )


class IsStudentOrParent(permissions.BasePermission):
    """Permission for students and parents"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_student or request.user.is_parent
        )


# ============================================================================
# USER VIEWSET
# ============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Override permissions based on action"""
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsOwnerOrAdmin | IsAdminUser]
        elif self.action in ['list']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['retrieve']:
            self.permission_classes = [IsOwnerOrAdmin | IsAdminUser]
        elif self.action in ['me', 'update_profile', 'change_password']:
            self.permission_classes = [IsAuthenticated]
        
        return super().get_permissions()
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.is_superuser or user.is_admin:
            return User.objects.all()
        
        if user.is_teacher or user.is_head_teacher:
            # Teachers can see students and other teachers in their department
            return User.objects.filter(
                Q(role=User.Role.STUDENT) |
                Q(role__in=[User.Role.TEACHER, User.Role.HEAD_TEACHER], department=user.department)
            )
        
        if user.is_student:
            # Students can see themselves and teachers
            return User.objects.filter(
                Q(id=user.id) |
                Q(role__in=[User.Role.TEACHER, User.Role.HEAD_TEACHER])
            )
        
        if user.is_parent:
            # Parents can see themselves and their children
            children = user.get_children()
            return User.objects.filter(
                Q(id=user.id) | Q(id__in=children.values_list('id', flat=True))
            )
        
        return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return UserCreateByAdminSerializer
        elif self.action in ['update', 'partial_update']:
            if self.request.user.is_staff:
                return UserUpdateByAdminSerializer
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user details"""
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='update-profile')
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': _('Profile updated successfully'),
                'user': UserDetailSerializer(user, context={'request': request}).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': _('Password changed successfully'),
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """Activate user (admin only)"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'message': _('User activated successfully'),
            'user': {
                'id': user.id,
                'email': user.email,
                'is_active': user.is_active
            }
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate user (admin only)"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response({
            'message': _('User deactivated successfully'),
            'user': {
                'id': user.id,
                'email': user.email,
                'is_active': user.is_active
            }
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        """Verify user (admin only)"""
        user = self.get_object()
        user.is_verified = True
        user.is_approved = True
        user.save()
        
        return Response({
            'message': _('User verified successfully'),
            'user': {
                'id': user.id,
                'email': user.email,
                'is_verified': user.is_verified,
                'is_approved': user.is_approved
            }
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def suspend(self, request, pk=None):
        """Suspend user (admin only)"""
        user = self.get_object()
        user.is_suspended = True
        user.is_active = False
        user.save()
        
        return Response({
            'message': _('User suspended successfully'),
            'user': {
                'id': user.id,
                'email': user.email,
                'is_suspended': user.is_suspended,
                'is_active': user.is_active
            }
        })
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get user profile"""
        user = self.get_object()
        try:
            profile = user.user_profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({
                'detail': _('User profile not found')
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def statistics(self, request):
        """Get user statistics"""
        # Total users
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users_today = User.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        new_users_this_week = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()
        verified_users = User.objects.filter(is_verified=True).count()
        pending_approval = User.objects.filter(
            is_approved=False, is_suspended=False
        ).count()
        suspended_users = User.objects.filter(is_suspended=True).count()
        
        # Role distribution
        role_distribution = {}
        for role, label in User.Role.choices:
            count = User.objects.filter(role=role).count()
            role_distribution[label] = count
        
        # Profile completion stats
        completed = User.objects.filter(profile_completed=True).count()
        incomplete = User.objects.filter(profile_completed=False).count()
        
        profile_completion_stats = {
            'completed': completed,
            'incomplete': incomplete,
            'completion_rate': (completed / total_users * 100) if total_users > 0 else 0
        }
        
        data = {
            'total_users': total_users,
            'active_users': active_users,
            'new_users_today': new_users_today,
            'new_users_this_week': new_users_this_week,
            'verified_users': verified_users,
            'pending_approval': pending_approval,
            'suspended_users': suspended_users,
            'role_distribution': role_distribution,
            'profile_completion_stats': profile_completion_stats
        }
        
        serializer = UserStatisticsSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_update_status(self, request):
        """Bulk update user status"""
        user_ids = request.data.get('user_ids', [])
        status_field = request.data.get('status_field')
        status_value = request.data.get('status_value')
        
        if not user_ids or not status_field or status_value is None:
            return Response({
                'error': _('user_ids, status_field, and status_value are required')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status field
        valid_status_fields = ['is_active', 'is_verified', 'is_approved', 'is_suspended']
        if status_field not in valid_status_fields:
            return Response({
                'error': _('Invalid status field'),
                'valid_fields': valid_status_fields
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update users
        updated_count = User.bulk_update_status(user_ids, status_field, status_value)
        
        return Response({
            'message': _('Users updated successfully'),
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def export(self, request):
        """Export users to CSV"""
        # Get filter parameters
        role = request.query_params.get('role')
        is_active = request.query_params.get('is_active')
        is_verified = request.query_params.get('is_verified')
        format_type = request.query_params.get('format', 'csv')
        
        # Filter users
        queryset = User.objects.all()
        
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Export based on format
        if format_type == 'csv':
            return self._export_csv(queryset)
        elif format_type == 'json':
            return self._export_json(queryset)
        else:
            return Response({
                'error': _('Invalid format. Supported formats: csv, json')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _export_csv(self, queryset):
        """Export to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'Email', 'Full Name', 'Role', 'Phone Number',
            'Date of Birth', 'Gender', 'Nationality', 'Admission Number',
            'Staff ID', 'Grade Level', 'Current Class', 'Department',
            'Designation', 'Is Active', 'Is Verified', 'Is Approved',
            'Date Joined', 'Last Login'
        ])
        
        # Write data
        for user in queryset:
            writer.writerow([
                user.id, user.email, user.get_full_name(), user.get_role_display(),
                user.phone_number, user.date_of_birth, user.get_gender_display(),
                user.nationality, user.admission_number, user.staff_id,
                user.grade_level, user.current_class, user.department,
                user.designation, user.is_active, user.is_verified,
                user.is_approved, user.date_joined, user.last_login
            ])
        
        return response
    
    def _export_json(self, queryset):
        """Export to JSON"""
        serializer = UserExportSerializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# USER PROFILE VIEWSET
# ============================================================================

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrAdmin]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.is_staff:
            return UserProfile.objects.all()
        
        return UserProfile.objects.filter(user=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def perform_create(self, serializer):
        """Create user profile"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's profile"""
        try:
            profile = request.user.user_profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({
                'detail': _('Profile not found')
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], url_path='update-my-profile')
    def update_my_profile(self, request):
        """Update current user's profile"""
        try:
            profile = request.user.user_profile
            serializer = UserProfileUpdateSerializer(
                instance=profile,
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': _('Profile updated successfully'),
                    'profile': serializer.data
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except UserProfile.DoesNotExist:
            return Response({
                'detail': _('Profile not found')
            }, status=status.HTTP_404_NOT_FOUND)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Handle user registration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Send verification email
        try:
            user.send_verification_email(request)
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            # Continue even if email fails
        
        # Prepare response data
        response_data = {
            'message': _('User registered successfully. Please check your email for verification.'),
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'requires_verification': not user.is_verified
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """View for user login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle user login"""
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        
        # Check if 2FA is required
        requires_2fa = False
        two_fa_data = None
        
        try:
            two_fa = user.two_factor_auth
            if two_fa.is_enabled:
                requires_2fa = True
                
                # Create pending session for 2FA
                session_token = RefreshToken.for_user(user).access_token
                two_fa.create_pending_session(
                    session_token=str(session_token),
                    redirect_url=user.get_dashboard_url()
                )
                
                two_fa_data = {
                    'requires_2fa': True,
                    'primary_method': two_fa.primary_method,
                    'session_token': str(session_token),
                    'user_id': user.id,
                    'email': user.email
                }
        except TwoFactorAuth.DoesNotExist:
            pass
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Prepare response data
        response_data = {
            'message': _('Login successful'),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
                'is_verified': user.is_verified,
                'is_approved': user.is_approved,
                'profile_completed': user.profile_completed,
                'requires_2fa_setup': user.requires_2fa_setup,
                'dashboard_url': user.get_dashboard_url()
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'permissions': user.get_permissions(),
            'feature_flags': user.get_feature_flags()
        }
        
        if requires_2fa:
            response_data['requires_2fa'] = True
            response_data['two_fa'] = two_fa_data
            response_data['user']['requires_2fa_verification'] = True
        else:
            response_data['requires_2fa'] = False
        
        return Response(response_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """View for user logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle user logout"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Logout from Django session
            logout(request)
            
            return Response({
                'message': _('Logged out successfully')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': _('Logout failed'),
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorLoginView(APIView):
    """View for 2FA login verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Verify 2FA OTP and complete login"""
        serializer = TwoFactorLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        remember_device = serializer.validated_data.get('remember_device', False)
        
        # Get pending session
        try:
            two_fa = user.two_factor_auth
            session_token = request.data.get('session_token')
            
            if session_token:
                is_valid, redirect_url = two_fa.verify_pending_session(session_token, request.data['otp'])
                
                if not is_valid:
                    return Response({
                        'error': _('Invalid or expired session')
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Direct OTP verification
                if not two_fa.verify_otp(request.data['otp']):
                    return Response({
                        'error': _('Invalid OTP code')
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                redirect_url = user.get_dashboard_url()
        except TwoFactorAuth.DoesNotExist:
            redirect_url = user.get_dashboard_url()
        
        # Generate new tokens
        refresh = RefreshToken.for_user(user)
        
        # Prepare response
        response_data = {
            'message': _('2FA verification successful'),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
                'is_verified': user.is_verified,
                'is_approved': user.is_approved,
                'profile_completed': user.profile_completed,
                'dashboard_url': redirect_url
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'permissions': user.get_permissions(),
            'feature_flags': user.get_feature_flags(),
            'redirect_url': redirect_url
        }
        
        # Set device token if remember device is enabled
        if remember_device:
            device_token = RefreshToken.for_user(user).access_token
            response_data['device_token'] = str(device_token)
        
        return Response(response_data, status=status.HTTP_200_OK)


# ============================================================================
# PASSWORD AND VERIFICATION VIEWS
# ============================================================================

class PasswordResetRequestView(generics.GenericAPIView):
    """View for requesting password reset"""
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle password reset request"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Check if user is active
                if not user.is_active:
                    return Response({
                        'error': _('Account is deactivated. Please contact support.')
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Initiate password reset
                token = user.initiate_password_reset(request)
                
                return Response({
                    'message': _('Password reset email sent successfully.'),
                    'email': email,
                    'token_id': token.id,
                    'expires_at': token.expires_at
                })
                
            except User.DoesNotExist:
                # Don't reveal that user doesn't exist for security
                return Response({
                    'message': _('If your email is registered, you will receive a password reset link.')
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    """View for confirming password reset"""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle password reset confirmation"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': _('Password reset successful. You can now login with your new password.'),
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(generics.GenericAPIView):
    """View for email verification"""
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle email verification"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': _('Email verified successfully.'),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'is_verified': user.is_verified,
                    'is_approved': user.is_approved
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(generics.GenericAPIView):
    """View for resending verification email"""
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle resend verification request"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Check if already verified
            if user.email_verified:
                return Response({
                    'error': _('Email is already verified.')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Send verification email
            token = user.send_verification_email(request)
            
            return Response({
                'message': _('Verification email sent successfully.'),
                'email': email,
                'token_id': token.id,
                'expires_at': token.expires_at
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# TWO-FACTOR AUTHENTICATION VIEWS
# ============================================================================

class TwoFactorSetupView(generics.GenericAPIView):
    """View for setting up 2FA"""
    serializer_class = TwoFactorSetupSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current 2FA status"""
        try:
            two_fa = request.user.two_factor_auth
            serializer = self.get_serializer(two_fa)
            return Response(serializer.data)
        except TwoFactorAuth.DoesNotExist:
            return Response({
                'is_enabled': False,
                'message': _('2FA is not setup')
            })
    
    def post(self, request):
        """Setup 2FA"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            two_fa = serializer.save()
            
            return Response({
                'message': _('2FA setup initiated. Please verify with OTP.'),
                'qr_code': two_fa.generate_qr_code(),
                'secret_key': two_fa.secret_key,
                'provisioning_uri': two_fa.generate_provisioning_uri(),
                'primary_method': two_fa.primary_method
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorVerifyView(generics.GenericAPIView):
    """View for verifying 2FA setup"""
    serializer_class = TwoFactorVerifySerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Verify 2FA setup"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            result = serializer.save()
            two_fa = result['two_fa']
            backup_codes = result['backup_codes']
            
            return Response({
                'message': _('2FA enabled successfully.'),
                'is_enabled': two_fa.is_enabled,
                'primary_method': two_fa.primary_method,
                'backup_codes': backup_codes,
                'warning': _('Please save these backup codes in a secure location. They will not be shown again.')
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorDisableView(generics.GenericAPIView):
    """View for disabling 2FA"""
    serializer_class = TwoFactorDisableSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Disable 2FA"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            two_fa = serializer.save()
            
            return Response({
                'message': _('2FA disabled successfully.'),
                'is_enabled': two_fa.is_enabled
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorBackupCodesView(generics.GenericAPIView):
    """View for managing 2FA backup codes"""
    serializer_class = BackupCodesSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get unused backup codes"""
        try:
            two_fa = request.user.two_factor_auth
            
            if not two_fa.is_enabled:
                return Response({
                    'error': _('2FA is not enabled.')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            unused_codes = two_fa.get_unused_backup_codes()
            
            return Response({
                'unused_codes': [code['code'] for code in unused_codes],
                'total_codes': len(two_fa.backup_codes),
                'unused_count': len(unused_codes)
            })
            
        except TwoFactorAuth.DoesNotExist:
            return Response({
                'error': _('2FA is not setup.')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """Generate new backup codes"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            backup_codes = serializer.save()
            
            return Response({
                'message': _('New backup codes generated successfully.'),
                'backup_codes': backup_codes,
                'warning': _('Please save these backup codes in a secure location. They will not be shown again.')
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# DASHBOARD AND STATISTICS VIEWS
# ============================================================================

class DashboardView(APIView):
    """View for dashboard data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard data based on user role"""
        user = request.user
        role = user.role
        
        # Common dashboard data
        dashboard_data = {
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': role,
                'role_display': user.get_role_display(),
                'profile_completed': user.profile_completed,
                'profile_completion_percentage': user.profile_completion_percentage,
                'missing_profile_fields': user.get_missing_profile_fields(),
                'dashboard_url': user.get_dashboard_url(),
                'requires_2fa_setup': user.requires_2fa_setup,
                'has_2fa_enabled': user.has_2fa_enabled()
            },
            'permissions': user.get_permissions(),
            'feature_flags': user.get_feature_flags(),
            'quick_actions': self._get_quick_actions(user),
            'notifications': self._get_notifications(user)
        }
        
        # Role-specific data
        if role == User.Role.ADMIN:
            dashboard_data['admin_stats'] = self._get_admin_stats()
        elif role == User.Role.TEACHER:
            dashboard_data['teacher_stats'] = self._get_teacher_stats(user)
        elif role == User.Role.STUDENT:
            dashboard_data['student_stats'] = self._get_student_stats(user)
        elif role == User.Role.PARENT:
            dashboard_data['parent_stats'] = self._get_parent_stats(user)
        elif role == User.Role.ACCOUNTANT:
            dashboard_data['finance_stats'] = self._get_finance_stats()
        
        return Response(dashboard_data)
    
    def _get_quick_actions(self, user):
        """Get quick actions based on user role"""
        actions = []
        
        if not user.profile_completed:
            actions.append({
                'title': _('Complete Profile'),
                'description': _('Complete your profile to access all features'),
                'icon': 'user',
                'url': '/complete-profile',
                'priority': 'high'
            })
        
        if user.requires_2fa_setup and not user.has_2fa_enabled():
            actions.append({
                'title': _('Setup 2FA'),
                'description': _('Enable two-factor authentication for extra security'),
                'icon': 'shield',
                'url': '/setup-2fa',
                'priority': 'medium'
            })
        
        if user.is_password_expired():
            actions.append({
                'title': _('Change Password'),
                'description': _('Your password has expired. Please change it.'),
                'icon': 'key',
                'url': '/change-password',
                'priority': 'high'
            })
        
        # Role-specific actions
        if user.is_teacher:
            actions.extend([
                {
                    'title': _('Create Lesson'),
                    'description': _('Create a new lesson plan'),
                    'icon': 'book',
                    'url': '/lessons/create',
                    'priority': 'medium'
                },
                {
                    'title': _('Mark Attendance'),
                    'description': _('Mark today\'s attendance'),
                    'icon': 'check-circle',
                    'url': '/attendance/mark',
                    'priority': 'high'
                }
            ])
        
        elif user.is_student:
            actions.extend([
                {
                    'title': _('View Grades'),
                    'description': _('Check your latest grades'),
                    'icon': 'award',
                    'url': '/grades',
                    'priority': 'medium'
                },
                {
                    'title': _('View Timetable'),
                    'description': _('Check your class schedule'),
                    'icon': 'calendar',
                    'url': '/timetable',
                    'priority': 'medium'
                }
            ])
        
        return actions
    
    def _get_notifications(self, user):
        """Get user notifications"""
        notifications = []
        
        # Example notifications
        if not user.email_verified:
            notifications.append({
                'id': 'email_verification',
                'title': _('Verify Email'),
                'message': _('Please verify your email address'),
                'type': 'warning',
                'action_url': '/verify-email',
                'created_at': user.date_joined.isoformat()
            })
        
        if not user.is_approved and user.requires_approval():
            notifications.append({
                'id': 'account_approval',
                'title': _('Account Pending Approval'),
                'message': _('Your account is pending admin approval'),
                'type': 'info',
                'action_url': None,
                'created_at': user.date_joined.isoformat()
            })
        
        # Recent login notification
        if user.last_login:
            notifications.append({
                'id': 'last_login',
                'title': _('Last Login'),
                'message': _('Last login: {}').format(user.last_login.strftime('%Y-%m-%d %H:%M')),
                'type': 'info',
                'action_url': '/security',
                'created_at': user.last_login.isoformat()
            })
        
        return notifications
    
    def _get_admin_stats(self):
        """Get admin dashboard statistics"""
        today = timezone.now().date()
        
        return {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'new_users_today': User.objects.filter(date_joined__date=today).count(),
            'pending_approvals': User.objects.filter(is_approved=False, is_suspended=False).count(),
            'suspended_users': User.objects.filter(is_suspended=True).count(),
            'profile_completion_rate': self._get_profile_completion_rate()
        }
    
    def _get_teacher_stats(self, teacher):
        """Get teacher dashboard statistics"""
        # This would typically connect to other apps
        return {
            'total_students': User.objects.filter(role=User.Role.STUDENT).count(),
            'my_students': 0,  # Would come from class assignment
            'pending_grading': 0,
            'attendance_today': 0,
            'upcoming_classes': []
        }
    
    def _get_student_stats(self, student):
        """Get student dashboard statistics"""
        return {
            'attendance_rate': 95,  # Example
            'average_grade': 'A-',
            'upcoming_assignments': 3,
            'pending_submissions': 1,
            'next_class': None  # Would come from timetable
        }
    
    def _get_parent_stats(self, parent):
        """Get parent dashboard statistics"""
        children = parent.get_children()
        
        return {
            'total_children': children.count(),
            'children_attendance': {},
            'children_grades': {},
            'upcoming_events': []
        }
    
    def _get_finance_stats(self):
        """Get finance dashboard statistics"""
        return {
            'total_revenue': 0,
            'pending_payments': 0,
            'overdue_payments': 0,
            'monthly_collection': 0
        }
    
    def _get_profile_completion_rate(self):
        """Calculate overall profile completion rate"""
        total_users = User.objects.count()
        completed_profiles = User.objects.filter(profile_completed=True).count()
        
        if total_users == 0:
            return 0
        
        return round((completed_profiles / total_users) * 100, 2)


class UserStatisticsView(APIView):
    """View for detailed user statistics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get detailed user statistics"""
        # Time-based statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Daily registrations
        daily_registrations = (
            User.objects.filter(date_joined__date__gte=week_ago)
            .annotate(day=TruncDay('date_joined'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        
        # Monthly registrations
        monthly_registrations = (
            User.objects.filter(date_joined__gte=month_ago)
            .annotate(month=TruncMonth('date_joined'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        # Role distribution
        role_distribution = {}
        for role, label in User.Role.choices:
            count = User.objects.filter(role=role).count()
            role_distribution[label] = {
                'count': count,
                'percentage': round((count / User.objects.count() * 100), 2) if User.objects.count() > 0 else 0
            }
        
        # Activity statistics
        active_today = User.objects.filter(
            last_activity__date=today
        ).count()
        
        active_this_week = User.objects.filter(
            last_activity__gte=week_ago
        ).count()
        
        never_logged_in = User.objects.filter(
            last_login__isnull=True
        ).count()
        
        # Profile completion by role
        profile_completion_by_role = {}
        for role, label in User.Role.choices:
            total = User.objects.filter(role=role).count()
            completed = User.objects.filter(role=role, profile_completed=True).count()
            
            if total > 0:
                profile_completion_by_role[label] = {
                    'total': total,
                    'completed': completed,
                    'percentage': round((completed / total * 100), 2)
                }
        
        statistics = {
            'time_series': {
                'daily_registrations': list(daily_registrations),
                'monthly_registrations': list(monthly_registrations)
            },
            'role_distribution': role_distribution,
            'activity': {
                'active_today': active_today,
                'active_this_week': active_this_week,
                'never_logged_in': never_logged_in,
                'avg_logins_per_user': self._calculate_avg_logins()
            },
            'profile_completion': {
                'by_role': profile_completion_by_role,
                'overall_rate': self._get_profile_completion_rate()
            },
            'verification_status': {
                'verified': User.objects.filter(is_verified=True).count(),
                'unverified': User.objects.filter(is_verified=False).count(),
                'approved': User.objects.filter(is_approved=True).count(),
                'pending': User.objects.filter(is_approved=False, is_suspended=False).count()
            }
        }
        
        return Response(statistics)
    
    def _calculate_avg_logins(self):
        """Calculate average logins per user"""
        total_logins = User.objects.aggregate(total=Count('login_count'))['total']
        total_users = User.objects.count()
        
        if total_users == 0:
            return 0
        
        return round(total_logins / total_users, 2)
    
    def _get_profile_completion_rate(self):
        """Calculate overall profile completion rate"""
        total_users = User.objects.count()
        completed_profiles = User.objects.filter(profile_completed=True).count()
        
        if total_users == 0:
            return 0
        
        return round((completed_profiles / total_users) * 100, 2)


# ============================================================================
# SEARCH AND FILTER VIEWS
# ============================================================================

class UserSearchView(generics.ListAPIView):
    """View for searching users"""
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on search parameters"""
        queryset = User.objects.all()
        user = self.request.user
        
        # Apply permission-based filtering
        if not user.is_staff:
            if user.is_teacher or user.is_head_teacher:
                queryset = queryset.filter(
                    Q(role=User.Role.STUDENT) |
                    Q(role__in=[User.Role.TEACHER, User.Role.HEAD_TEACHER], department=user.department)
                )
            elif user.is_student:
                queryset = queryset.filter(
                    Q(id=user.id) |
                    Q(role__in=[User.Role.TEACHER, User.Role.HEAD_TEACHER])
                )
            elif user.is_parent:
                children = user.get_children()
                queryset = queryset.filter(
                    Q(id=user.id) | Q(id__in=children.values_list('id', flat=True))
                )
            else:
                queryset = queryset.filter(id=user.id)
        
        # Apply search filters
        from .serializers import UserSearchSerializer
        serializer = UserSearchSerializer(data=self.request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Search query
            if data.get('query'):
                query = data['query']
                queryset = queryset.filter(
                    Q(email__icontains=query) |
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(admission_number__icontains=query) |
                    Q(staff_id__icontains=query) |
                    Q(phone_number__icontains=query)
                )
            
            # Role filter
            if data.get('role'):
                queryset = queryset.filter(role=data['role'])
            
            # Status filters
            if data.get('is_active') is not None:
                queryset = queryset.filter(is_active=data['is_active'])
            
            if data.get('is_verified') is not None:
                queryset = queryset.filter(is_verified=data['is_verified'])
            
            if data.get('is_approved') is not None:
                queryset = queryset.filter(is_approved=data['is_approved'])
            
            if data.get('profile_completed') is not None:
                queryset = queryset.filter(profile_completed=data['profile_completed'])
            
            # Date filters
            if data.get('date_joined_start'):
                queryset = queryset.filter(date_joined__date__gte=data['date_joined_start'])
            
            if data.get('date_joined_end'):
                queryset = queryset.filter(date_joined__date__lte=data['date_joined_end'])
            
            # Academic filters
            if data.get('grade_level'):
                queryset = queryset.filter(grade_level=data['grade_level'])
            
            if data.get('department'):
                queryset = queryset.filter(department__icontains=data['department'])
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to add pagination metadata"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # Calculate pagination
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        users = queryset[start:end]
        
        # Serialize data
        serializer = self.get_serializer(users, many=True)
        
        return Response({
            'count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size,
            'results': serializer.data
        })


# ============================================================================
# HELPER AND UTILITY VIEWS
# ============================================================================

class CheckEmailView(APIView):
    """View to check if email is available"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Check email availability"""
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': _('Email is required')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        exists = User.objects.filter(email=email).exists()
        
        return Response({
            'email': email,
            'available': not exists,
            'exists': exists
        })


class CheckUsernameView(APIView):
    """View to check if username/admission number/staff ID is available"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Check identifier availability"""
        identifier_type = request.data.get('type')  # 'admission_number' or 'staff_id'
        value = request.data.get('value')
        
        if not identifier_type or not value:
            return Response({
                'error': _('Type and value are required')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if identifier_type not in ['admission_number', 'staff_id']:
            return Response({
                'error': _('Invalid type. Must be admission_number or staff_id')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        exists = User.objects.filter(**{identifier_type: value}).exists()
        
        return Response({
            'type': identifier_type,
            'value': value,
            'available': not exists,
            'exists': exists
        })


class ProfileCompletionView(APIView):
    """View to check and update profile completion"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get profile completion status"""
        user = request.user
        
        return Response({
            'profile_completed': user.profile_completed,
            'profile_completion_percentage': user.profile_completion_percentage,
            'missing_fields': user.get_missing_profile_fields(),
            'requirements_met': user.profile_requirements_met
        })
    
    def post(self, request):
        """Manually check and update profile completion"""
        user = request.user
        user.check_profile_completion()
        
        return Response({
            'message': _('Profile completion checked'),
            'profile_completed': user.profile_completed,
            'profile_completion_percentage': user.profile_completion_percentage,
            'missing_fields': user.get_missing_profile_fields()
        })


class ActivityUpdateView(APIView):
    """View to update user activity"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Update user last activity timestamp"""
        user = request.user
        user.update_activity()
        
        return Response({
            'message': _('Activity updated'),
            'last_activity': user.last_activity
        })


# ============================================================================
# PUBLIC VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'accounts-api'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def version_info(request):
    """API version information"""
    return Response({
        'version': '1.0.0',
        'name': 'Delvok Academy Accounts API',
        'description': 'User management API for Delvok Academy',
        'documentation': '/api/docs/'
    })


# ============================================================================
# CUSTOM JWT VIEWS
# ============================================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with extended response"""
    def post(self, request, *args, **kwargs):
        """Override to add custom response data"""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user from token
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(response.data['access'])
            user_id = access_token['user_id']
            
            try:
                user = User.objects.get(id=user_id)
                
                # Add user data to response
                response.data['user'] = {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'role': user.role,
                    'is_verified': user.is_verified,
                    'is_approved': user.is_approved,
                    'profile_completed': user.profile_completed,
                    'dashboard_url': user.get_dashboard_url()
                }
                
                response.data['permissions'] = user.get_permissions()
                response.data['feature_flags'] = user.get_feature_flags()
                
            except User.DoesNotExist:
                pass
        
        return response


# ============================================================================
# ADDITIONAL COMPATIBILITY VIEWS (for old imports)
# ============================================================================

# These are for compatibility with the old urls.py imports
@api_view(['GET'])
def api_root(request):
    """API root endpoint"""
    return Response({
        'message': 'Delvok Academy Accounts API',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'verify-email': '/api/auth/verify-email/',
            },
            'users': {
                'me': '/api/auth/me/',
                'profile': '/api/auth/profile/',
                'change-password': '/api/auth/change-password/',
            },
            'admin': {
                'users': '/api/auth/users/',
                'statistics': '/api/auth/statistics/',
            }
        }
    })


@api_view(['GET'])
def system_metrics(request):
    """System metrics endpoint"""
    return Response({
        'users': User.objects.count(),
        'active_sessions': 0,  # Would need session tracking
        'uptime': 'N/A',
        'memory_usage': 'N/A'
    })


@api_view(['POST'])
def verify_backup_code(request):
    """Verify backup code endpoint"""
    from .serializers import TwoFactorVerifySerializer
    
    serializer = TwoFactorVerifySerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        result = serializer.save()
        
        return Response({
            'message': _('Backup code verified successfully'),
            'verified': True
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def debug_urls(request):
    """Debug endpoint to list all URLs"""
    from django.urls import get_resolver
    from django.http import JsonResponse
    
    url_patterns = []
    resolver = get_resolver()
    
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'pattern'):
            url_patterns.append(str(pattern.pattern))
    
    return JsonResponse({'urls': url_patterns})