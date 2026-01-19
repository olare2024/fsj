# accounts/views.py - REFACTORED AND ORGANIZED VERSION

import csv
import json
import logging
import xlsxwriter
from datetime import datetime, timedelta
from io import BytesIO

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import (Case, Count, F, IntegerField, Q, Value, When,
                               functions)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework import (filters, generics, permissions, status, viewsets)
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (action, api_view,
                                       permission_classes)
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import (AllowAny, IsAdminUser,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from .models import (
    LoginHistory, LoginSession, OTPToken, TwoFactorAuth, User, UserProfile,
    TwoFAMethodChoices, TokenTypeChoices, LoginStatusChoices, SessionStatusChoices,
    UserRole
)
from .serializers import (BulkUserDeleteSerializer, BulkUserUpdateSerializer,
                          ChangePasswordSerializer,
                          CustomTokenObtainPairSerializer,
                          DashboardPreferencesSerializer,
                          EmailVerificationSerializer, FilterSerializer,
                          LoginHistorySerializer, LoginSerializer,
                          LoginSessionSerializer, OTPTokenSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetRequestSerializer,
                          PhoneVerificationSerializer, SearchSerializer,
                          StatsSerializer, TwoFactorAuthSerializer,
                          TwoFactorBackupCodeSerializer,
                          TwoFactorDisableSerializer, TwoFactorSetupSerializer,
                          TwoFactorVerifySerializer, UserAdminCreateSerializer,
                          UserAdminUpdateSerializer, UserCreateSerializer,
                          UserDetailSerializer, UserExportSerializer,
                          UserListSerializer, UserMinimalSerializer,
                          UserProfileSerializer, UserRedirectSerializer,
                          UserSerializer, UserUpdateSerializer,
                          VerifyEmailSerializer, VerifyPhoneSerializer)

logger = logging.getLogger(__name__)

# ============================================================================
# PERMISSION CLASSES
# ============================================================================

class IsOwner(permissions.BasePermission):
    """Allow users to access their own data only"""
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow owners or admins to access data"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role == UserRole.ADMIN:
            return True
        return obj == request.user


class IsStaffOrAdmin(permissions.BasePermission):
    """Allow staff members or admins"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or
            request.user.role == UserRole.ADMIN
        )


class IsTeacherOrAbove(permissions.BasePermission):
    """Allow teachers, head teachers, curriculum coordinators, and admins"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        teacher_roles = [
            UserRole.TEACHER,
            UserRole.HEAD_TEACHER,
            UserRole.CURRICULUM_COORDINATOR,
            UserRole.ADMIN
        ]
        return request.user.role in teacher_roles


class IsParent(permissions.BasePermission):
    """Allow parents to access their children's data"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.PARENT


class IsStudent(permissions.BasePermission):
    """Allow students to access their own data"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.STUDENT


class HasPermission(permissions.BasePermission):
    """Check if user has specific permission"""
    
    def __init__(self, permission):
        self.permission = permission
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        permissions = request.user.get_permissions()
        return self.permission in permissions or '*' in permissions


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

class CSRFExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication without CSRF for API views
    """
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with enhanced response"""
    
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Token obtain error: {str(e)}")
            return Response({
                'error': 'Invalid credentials',
                'message': 'Unable to log in with provided credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        data = serializer.validated_data
        
        # Check if 2FA setup is required
        if data.get('requires_2fa_setup'):
            return Response({
                'requires_2fa_setup': True,
                'message': 'Two-factor authentication setup required.',
                'user_id': str(data['user']['id'])
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view"""
    
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except TokenError as e:
            return Response({
                'error': 'token_error',
                'message': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenVerifyView(TokenVerifyView):
    """Custom token verify view"""
    
    pass


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    Simple working login view for React frontend
    """
    permission_classes = [AllowAny]
    authentication_classes = [CSRFExemptSessionAuthentication]
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            remember_me = data.get('rememberMe', False)
            
            print(f"\n" + "="*60)
            print(f"🔐 LOGIN ATTEMPT STARTED")
            print("="*60)
            print(f"📧 Email: {email}")
            print(f"📅 Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            # Validate input
            if not email or not password:
                print("❌ Missing email or password")
                return Response({
                    'success': False,
                    'message': 'Email and password are required',
                    'requires_2fa': False
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Authenticate user
            user = authenticate(request, username=email, password=password)
            
            if user is None:
                print(f"❌ AUTHENTICATION FAILED: Invalid credentials for {email}")
                print("="*60 + "\n")
                return Response({
                    'success': False,
                    'message': 'Invalid email or password',
                    'requires_2fa': False
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            print(f"✅ User authenticated: {user.email}")
            print(f"👤 Name: {user.get_full_name()}")
            print(f"🎯 Role: {user.role}")
            
            if not user.is_active:
                print("❌ Account is deactivated")
                print("="*60 + "\n")
                return Response({
                    'success': False,
                    'message': 'Account is deactivated',
                    'requires_2fa': False
                }, status=status.HTTP_403_FORBIDDEN)
            
            # FOR TESTING: Always require 2FA and print OTP
            requires_2fa = True  # Always require for testing
            
            if requires_2fa:
                print("\n" + "="*60)
                print("🔄 2FA REQUIRED - GENERATING OTP")
                print("="*60)
                
                # Generate OTP
                import random
                otp = str(random.randint(100000, 999999))  # 6-digit OTP
                
                # Generate session token
                import uuid
                session_token = str(uuid.uuid4())
                
                # Store in cache/database for verification
                from django.core.cache import cache
                cache_key = f'2fa_session_{session_token}'
                cache_data = {
                    'user_id': str(user.id),
                    'email': user.email,
                    'otp': otp,
                    'created_at': timezone.now().isoformat(),
                    'expires_at': (timezone.now() + timedelta(minutes=10)).isoformat()
                }
                cache.set(cache_key, cache_data, 600)  # 10 minutes
                
                # PRINT OTP CLEARLY
                print("\n" + "🔔" * 30)
                print("📱 OTP FOR LOGIN TESTING")
                print("🔔" * 30)
                print(f"📧 User Email: {user.email}")
                print(f"👤 User Name: {user.get_full_name()}")
                print(f"🎯 User Role: {user.role}")
                print("─" * 40)
                print(f"🔢 OTP CODE: {otp}")
                print(f"🔑 Session Token: {session_token}")
                print(f"⏰ Valid for: 10 minutes")
                print(f"⏰ Generated at: {timezone.now().strftime('%H:%M:%S')}")
                print(f"⏰ Expires at: {(timezone.now() + timedelta(minutes=10)).strftime('%H:%M:%S')}")
                print("─" * 40)
                print(f"💡 Use this OTP in your frontend verification form")
                print(f"💡 Session will be stored in cache key: {cache_key}")
                print("🔔" * 30 + "\n")
                
                # Also print in a very visible format
                print("\n" + "⭐" * 50)
                print(f"⭐ TEST OTP: {otp} ⭐")
                print("⭐" * 50 + "\n")
                
                return Response({
                    'success': True,
                    'requires_2fa': True,
                    'message': '2FA verification required. OTP has been generated and printed to console.',
                    'session_token': session_token,
                    'user_id': str(user.id),
                    'method': 'console',
                    'masked_email': self._mask_email(user.email),
                    'expires_in': 600,  # 10 minutes
                    'console_otp': otp,  # For testing only - remove in production
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'first_name': user.first_name or '',
                        'last_name': user.last_name or '',
                        'role': user.role,
                        'profile_picture': user.profile_picture.url if user.profile_picture else None,
                        'profile_completed': user.profile_completed
                    }
                }, status=status.HTTP_200_OK)
            
            # If no 2FA required (not used in testing mode)
            print("\n" + "="*60)
            print("✅ LOGIN SUCCESSFUL - NO 2FA REQUIRED")
            print("="*60 + "\n")
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            redirect_url = self._get_redirect_url(user)
            
            response_data = {
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'role': user.role,
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'profile_completed': user.profile_completed,
                },
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                },
                'redirect_url': redirect_url,
                'requires_2fa': False,
                'session_token': None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON in request")
            return Response({
                'success': False,
                'message': 'Invalid JSON data',
                'requires_2fa': False
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': 'Server error during login',
                'requires_2fa': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _mask_email(self, email):
        """Mask email for display"""
        if '@' not in email:
            return email
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '***'
        else:
            masked_local = local[0] + '***' + local[-1]
        return f"{masked_local}@{domain}"
    
    def _get_redirect_url(self, user):
        """Get redirect URL based on user role"""
        role = user.role
        
        dashboard_map = {
            'admin': '/admin/admin-portal',
            'teacher': '/teacher/teacher-portal',
            'student': '/student/student-portal',
            'parent': '/parent/parent-portal',
            'head_teacher': '/head-teacher/headteacher-portal',
            'curriculum_coordinator': '/curriculum/curriculum-portal',
            'accountant': '/accountant/accountant-portal',
            'librarian': '/library/library-portal',
            'it_support': '/it/it-portal',
            'counselor': '/counselor/counselor-portal',
            'office_staff': '/staff/staff-portal',
        }
        
        return dashboard_map.get(role, '/dashboard')


class TwoFactorVerifyView(APIView):
    """Verify 2FA OTP and complete login"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        session_token = request.data.get('session_token')
        otp = request.data.get('otp')
        
        if not session_token or not otp:
            return Response({
                'error': 'missing_fields',
                'message': 'Session token and OTP are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            login_session = LoginSession.objects.get(
                session_token=session_token,
                status=LoginSession.SessionStatusChoices.PENDING_OTP
            )
            
            # Verify OTP
            is_valid, message = login_session.verify_otp(otp)
            
            if not is_valid:
                return Response({
                    'error': 'invalid_otp',
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate JWT tokens
            access_token, refresh_token = login_session.generate_jwt_tokens()
            
            user = login_session.user
            
            response_data = {
                'access': access_token,
                'refresh': refresh_token,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'role': user.role,
                    'role_display': user.get_role_display(),
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'dashboard_url': user.get_dashboard_url(),
                    'permissions': user.get_permissions(),
                    'feature_flags': user.get_feature_flags(),
                    'profile_completed': user.profile_completed,
                    'requires_2fa': user.requires_2fa_setup,
                    'has_2fa_enabled': user.has_2fa_enabled(),
                    'profile_completion_percentage': user.profile_completion_percentage,
                },
                'session_id': str(login_session.id),
                'expires_in': 3600 * 12
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except LoginSession.DoesNotExist:
            return Response({
                'error': 'invalid_session',
                'message': 'Invalid or expired session.'
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Handle user logout and session cleanup"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get session ID from token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    access_token = AccessToken(token)
                    session_id = access_token.get('session_id')
                    
                    if session_id:
                        try:
                            login_session = LoginSession.objects.get(id=session_id)
                            login_session.revoke()
                        except LoginSession.DoesNotExist:
                            pass
                except Exception:
                    pass
            
            # Blacklist refresh token if provided
            refresh_token = request.data.get('refresh')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except TokenError:
                    pass
            
            # Log the logout
            logger.info(f"User {request.user.email} logged out")
            
            return Response({
                'message': 'Successfully logged out.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'logout_failed',
                'message': 'Failed to logout.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(APIView):
    """Request password reset"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Don't reveal if email exists for security
        serializer.save()
        
        return Response({
            'message': 'If the email exists in our system, a password reset link has been sent.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Confirm password reset"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'message': 'Password has been successfully reset.',
            'user': {
                'id': str(user.id),
                'email': user.email
            }
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """Change password for authenticated user"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'message': 'Password has been successfully changed.'
        }, status=status.HTTP_200_OK)


# ============================================================================
# USER VIEWS
# ============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model with role-based access control"""
    
    queryset = User.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name', 'admission_number', 'staff_id']
    ordering_fields = ['created_at', 'last_login', 'email', 'first_name', 'last_name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            if self.request.user.is_superuser or self.request.user.role == UserRole.ADMIN:
                return UserAdminCreateSerializer
            return UserCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            if self.request.user.is_superuser or self.request.user.role == UserRole.ADMIN:
                return UserAdminUpdateSerializer
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Return permissions based on action"""
        if self.action == 'create':
            # Allow anyone to register
            if self.request.data.get('role') in [UserRole.ADMIN, UserRole.HEAD_TEACHER]:
                # Only admins can create admin/head teacher accounts
                permission_classes = [IsAdminUser]
            else:
                permission_classes = [AllowAny]
        elif self.action == 'list':
            # Only staff can list users
            permission_classes = [IsStaffOrAdmin]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Users can view/edit their own profile, admins can view/edit all
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'destroy':
            # Only admins can delete users
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Return queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return User.objects.none()
        
        # Superusers see all
        if user.is_superuser or user.role == UserRole.ADMIN:
            return queryset
        
        # Staff can see students and other staff (except admins)
        elif user.is_staff:
            return queryset.filter(
                Q(is_staff=True) | Q(role=UserRole.STUDENT) | Q(role=UserRole.PARENT)
            ).exclude(role=UserRole.ADMIN)
        
        # Parents can see their children
        elif user.role == UserRole.PARENT:
            children_emails = user.get_children().values_list('email', flat=True)
            return queryset.filter(email__in=children_emails)
        
        # Students can only see themselves
        elif user.role == UserRole.STUDENT:
            return queryset.filter(id=user.id)
        
        return User.objects.none()
    
    def perform_create(self, serializer):
        """Create user with additional logic"""
        user = serializer.save()
        
        # Send verification email for non-admin created users
        if not (self.request.user.is_superuser or self.request.user.role == UserRole.ADMIN):
            user.send_verification_email(self.request)
        
        logger.info(f"User created: {user.email} ({user.role})")
    
    def perform_update(self, serializer):
        """Update user with additional logic"""
        old_user = self.get_object()
        user = serializer.save()
        
        # Log profile completion
        if not old_user.profile_completed and user.profile_completed:
            logger.info(f"User {user.email} completed profile")
        
        # Clear caches
        cache.delete(f"profile_completion_{user.id}")
        cache.delete(f"user_permissions_{user.id}")
        cache.delete(f"feature_flags_{user.id}")
    
    def perform_destroy(self, instance):
        """Soft delete user"""
        instance.is_active = False
        instance.save()
        
        logger.info(f"User deactivated: {instance.email}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def activate(self, request, pk=None):
        """Activate user account"""
        user = self.get_object()
        
        if user.is_active:
            return Response({
                'message': 'User is already active.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.save()
        
        logger.info(f"User activated: {user.email}")
        
        return Response({
            'message': 'User activated successfully.'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Approve user account"""
        user = self.get_object()
        
        if user.is_approved:
            return Response({
                'message': 'User is already approved.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_approved = True
        user.save()
        
        # Send approval notification
        try:
            user.email_user(
                subject='Account Approved - Delvok Academy',
                message=f'Your account has been approved. You can now access all features.',
                from_email=settings.DEFAULT_FROM_EMAIL
            )
        except Exception as e:
            logger.error(f"Failed to send approval email: {e}")
        
        logger.info(f"User approved: {user.email}")
        
        return Response({
            'message': 'User approved successfully.'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def suspend(self, request, pk=None):
        """Suspend user account"""
        user = self.get_object()
        
        if user.is_suspended:
            return Response({
                'message': 'User is already suspended.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_suspended = True
        user.save()
        
        # Revoke active sessions
        LoginSession.objects.filter(
            user=user,
            status=LoginSession.SessionStatusChoices.VERIFIED
        ).update(status=LoginSession.SessionStatusChoices.REVOKED)
        
        logger.info(f"User suspended: {user.email}")
        
        return Response({
            'message': 'User suspended successfully.'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def unsuspend(self, request, pk=None):
        """Unsuspend user account"""
        user = self.get_object()
        
        if not user.is_suspended:
            return Response({
                'message': 'User is not suspended.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_suspended = False
        user.save()
        
        logger.info(f"User unsuspended: {user.email}")
        
        return Response({
            'message': 'User unsuspended successfully.'
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsOwnerOrAdmin])
    def profile_completion(self, request, pk=None):
        """Get profile completion details"""
        user = self.get_object()
        
        missing_fields = user.get_missing_profile_fields()
        completion_percentage = user.profile_completion_percentage
        
        return Response({
            'profile_completed': user.profile_completed,
            'completion_percentage': completion_percentage,
            'missing_fields': missing_fields,
            'requirements_met': user.profile_requirements_met
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def check_profile_completion(self, request, pk=None):
        """Check and update profile completion status"""
        user = self.get_object()
        
        user.check_profile_completion(force_check=True)
        
        return Response({
            'profile_completed': user.profile_completed,
            'completion_percentage': user.profile_completion_percentage,
            'message': 'Profile completion status updated.'
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsOwnerOrAdmin])
    def dashboard_info(self, request, pk=None):
        """Get dashboard information and redirect URL"""
        user = self.get_object()
        
        serializer = UserRedirectSerializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsOwnerOrAdmin])
    def permissions(self, request, pk=None):
        """Get user permissions"""
        user = self.get_object()
        
        return Response({
            'permissions': user.get_permissions(),
            'feature_flags': user.get_feature_flags()
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsOwnerOrAdmin])
    def children(self, request, pk=None):
        """Get children for parent user"""
        user = self.get_object()
        
        if user.role != UserRole.PARENT:
            return Response({
                'error': 'invalid_role',
                'message': 'User is not a parent.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        children = user.get_children()
        serializer = UserListSerializer(children, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsOwnerOrAdmin])
    def parents(self, request, pk=None):
        """Get parents for student user"""
        user = self.get_object()
        
        if user.role != UserRole.STUDENT:
            return Response({
                'error': 'invalid_role',
                'message': 'User is not a student.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        parents = user.get_parents()
        serializer = UserListSerializer(parents, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_me(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(generics.CreateAPIView):
    """Public user registration endpoint"""
    
    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_create(serializer)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'error': 'registration_failed',
                'message': 'Failed to create user account.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        headers = self.get_success_headers(serializer.data)
        
        # Don't return password in response
        response_data = serializer.data.copy()
        if 'password' in response_data:
            del response_data['password']
        if 'confirm_password' in response_data:
            del response_data['confirm_password']
        
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


# ============================================================================
# PROFILE VIEWS
# ============================================================================

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser or user.role == UserRole.ADMIN:
            return UserProfile.objects.all()
        
        return UserProfile.objects.filter(user=user)
    
    def get_object(self):
        """Get user profile for current user or specified user"""
        if 'pk' in self.kwargs:
            return super().get_object()
        
        # Return current user's profile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def perform_create(self, serializer):
        """Create user profile"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def add_achievement(self, request, pk=None):
        """Add achievement to user profile"""
        profile = self.get_object()
        
        title = request.data.get('title')
        description = request.data.get('description', '')
        category = request.data.get('category')
        
        if not title:
            return Response({
                'error': 'missing_title',
                'message': 'Achievement title is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date_achieved = timezone.now()
            if 'date_achieved' in request.data:
                date_achieved = datetime.fromisoformat(request.data['date_achieved'])
            
            profile.add_achievement(title, description, date_achieved, category)
            
            return Response({
                'message': 'Achievement added successfully.'
            })
            
        except Exception as e:
            logger.error(f"Error adding achievement: {str(e)}")
            return Response({
                'error': 'add_achievement_failed',
                'message': 'Failed to add achievement.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def add_skill(self, request, pk=None):
        """Add skill to user profile"""
        profile = self.get_object()
        
        skill_name = request.data.get('name')
        proficiency_level = request.data.get('proficiency_level', 'intermediate')
        category = request.data.get('category')
        
        if not skill_name:
            return Response({
                'error': 'missing_skill_name',
                'message': 'Skill name is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile.add_skill(skill_name, proficiency_level, category)
            
            return Response({
                'message': 'Skill added successfully.'
            })
            
        except Exception as e:
            logger.error(f"Error adding skill: {str(e)}")
            return Response({
                'error': 'add_skill_failed',
                'message': 'Failed to add skill.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# TWO-FACTOR AUTHENTICATION VIEWS
# ============================================================================

class TwoFactorAuthViewSet(viewsets.ModelViewSet):
    """ViewSet for TwoFactorAuth model"""
    
    serializer_class = TwoFactorAuthSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser or user.role == UserRole.ADMIN:
            return TwoFactorAuth.objects.all()
        
        return TwoFactorAuth.objects.filter(user=user)
    
    def get_object(self):
        """Get 2FA settings for current user or specified user"""
        if 'pk' in self.kwargs:
            return super().get_object()
        
        # Return current user's 2FA settings
        two_fa, created = TwoFactorAuth.objects.get_or_create(user=self.request.user)
        return two_fa
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def setup(self, request, pk=None):
        """Setup 2FA"""
        two_fa = self.get_object()
        
        serializer = TwoFactorSetupSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = serializer.save()
            return Response(result)
        except Exception as e:
            logger.error(f"2FA setup error: {str(e)}")
            return Response({
                'error': 'setup_failed',
                'message': 'Failed to setup two-factor authentication.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def verify(self, request, pk=None):
        """Verify 2FA setup"""
        two_fa = self.get_object()
        
        serializer = TwoFactorVerifySerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = serializer.save()
            return Response({
                'message': 'Two-factor authentication enabled successfully.',
                'two_fa': TwoFactorAuthSerializer(result).data
            })
        except Exception as e:
            logger.error(f"2FA verify error: {str(e)}")
            return Response({
                'error': 'verification_failed',
                'message': 'Failed to verify two-factor authentication.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def disable(self, request, pk=None):
        """Disable 2FA"""
        two_fa = self.get_object()
        
        serializer = TwoFactorDisableSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = serializer.save()
            return Response({
                'message': 'Two-factor authentication disabled successfully.'
            })
        except Exception as e:
            logger.error(f"2FA disable error: {str(e)}")
            return Response({
                'error': 'disable_failed',
                'message': 'Failed to disable two-factor authentication.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def generate_backup_codes(self, request, pk=None):
        """Generate new backup codes"""
        two_fa = self.get_object()
        
        if not two_fa.is_enabled:
            return Response({
                'error': '2fa_not_enabled',
                'message': 'Two-factor authentication is not enabled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        count = request.data.get('count', 10)
        
        try:
            backup_codes = two_fa.generate_backup_codes(count)
            
            return Response({
                'message': 'Backup codes generated successfully.',
                'backup_codes': backup_codes,
                'warning': 'Store these codes in a secure place. They will not be shown again.'
            })
            
        except Exception as e:
            logger.error(f"Error generating backup codes: {str(e)}")
            return Response({
                'error': 'generation_failed',
                'message': 'Failed to generate backup codes.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def verify_backup_code(self, request, pk=None):
        """Verify 2FA backup code"""
        serializer = TwoFactorBackupCodeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Backup code verified successfully.'
        })


# ============================================================================
# OTP & VERIFICATION VIEWS
# ============================================================================

class OTPTokenViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for OTPToken model (read-only)"""
    
    serializer_class = OTPTokenSerializer
    permission_classes = [IsAdminUser]  # Only admins can view OTP tokens
    
    def get_queryset(self):
        return OTPToken.objects.all()


class EmailVerificationView(APIView):
    """Request email verification"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.email_verified:
            return Response({
                'message': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = user.send_verification_email(request)
            
            return Response({
                'message': 'Verification email sent successfully.',
                'expires_in': 1440  # 24 hours in minutes
            })
            
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return Response({
                'error': 'verification_failed',
                'message': 'Failed to send verification email.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    """Verify email with token"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'message': 'Email verified successfully.',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'email_verified': user.email_verified,
                'is_verified': user.is_verified
            }
        })


class PhoneVerificationView(APIView):
    """Request phone verification"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.phone_verified:
            return Response({
                'message': 'Phone is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.phone_number:
            return Response({
                'error': 'no_phone_number',
                'message': 'Phone number is not set.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PhoneVerificationSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.save()
        
        return Response({
            'message': 'Verification OTP sent successfully.',
            'expires_in': 10  # 10 minutes
        })


class VerifyPhoneView(APIView):
    """Verify phone with OTP"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = VerifyPhoneSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'message': 'Phone verified successfully.',
            'user': {
                'id': str(user.id),
                'phone_number': user.phone_number,
                'phone_verified': user.phone_verified,
                'is_verified': user.is_verified
            }
        })


# ============================================================================
# OTP & VERIFICATION VIEWS - FIXED VERSION
# ============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class VerifyOTPView(APIView):
    """Verify OTP for 2FA login - FIXED VERSION with CSRF Exempt"""
    permission_classes = [AllowAny]
    authentication_classes = [CSRFExemptSessionAuthentication]  # Add this line
    
    def _get_redirect_url(self, user):
        """Get redirect URL based on user role"""
        role = user.role
        
        dashboard_map = {
            'admin': '/admin/admin-portal',
            'teacher': '/teacher/teacher-portal',
            'student': '/student/student-portal',
            'parent': '/parent/parent-portal',
            'head_teacher': '/head-teacher/headteacher-portal',
            'curriculum_coordinator': '/curriculum/curriculum-portal',
            'accountant': '/accountant/accountant-portal',
            'librarian': '/library/library-portal',
            'it_support': '/it/it-portal',
            'counselor': '/counselor/counselor-portal',
            'office_staff': '/staff/staff-portal',
        }
        
        return dashboard_map.get(role, '/dashboard')
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def post(self, request):
        try:
            print(f"\n" + "="*60)
            print(f"🔐 OTP VERIFICATION ATTEMPT")
            print("="*60)
            print(f"⏰ Time: {timezone.now().strftime('%H:%M:%S')}")
            
            data = request.data
            session_token = data.get('session_token')
            otp = data.get('otp')
            
            print(f"📝 Request Data: {data}")
            print(f"🔑 Session Token: {session_token}")
            print(f"🔢 OTP Provided: {otp}")
            
            if not session_token or not otp:
                print("❌ Missing session token or OTP")
                return Response({
                    'success': False,
                    'message': 'Session token and OTP are required',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check session in cache
            from django.core.cache import cache
            cache_key = f'2fa_session_{session_token}'
            session_data = cache.get(cache_key)
            
            if not session_data:
                print(f"❌ Session not found or expired: {session_token}")
                return Response({
                    'success': False,
                    'message': 'Session expired or invalid',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"\n" + "="*60)
            print(f"📋 SESSION DATA FOUND")
            print("="*60)
            print(f"📧 Expected Email: {session_data.get('email')}")
            print(f"🔢 Expected OTP: {session_data.get('otp')}")
            print(f"👤 User ID: {session_data.get('user_id')}")
            
            # Verify OTP
            expected_otp = str(session_data.get('otp', ''))
            provided_otp = str(otp)
            
            print(f"🔍 OTP Comparison:")
            print(f"   Expected: {expected_otp}")
            print(f"   Provided: {provided_otp}")
            
            if expected_otp == provided_otp:
                print(f"\n✅ OTP VERIFIED SUCCESSFULLY!")
                
                # Get user
                try:
                    user = User.objects.get(id=session_data['user_id'])
                    
                    print(f"\n" + "="*60)
                    print(f"👤 USER FOUND")
                    print("="*60)
                    print(f"📧 Email: {user.email}")
                    print(f"👤 Name: {user.get_full_name()}")
                    print(f"🎯 Role: {user.role}")
                    
                    # Check if user can login
                    if not user.is_active:
                        print("❌ Account is deactivated")
                        return Response({
                            'success': False,
                            'message': 'Account is deactivated',
                        }, status=status.HTTP_403_FORBIDDEN)
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)
                    
                    # Clear session from cache
                    cache.delete(cache_key)
                    
                    print(f"\n" + "="*60)
                    print(f"✅ LOGIN COMPLETED")
                    print("="*60)
                    print(f"🔑 Access Token generated")
                    print(f"🔄 Refresh Token generated")
                    print(f"👤 User ID: {user.id}")
                    
                    # Update last login
                    user.last_login = timezone.now()
                    user.login_count = user.login_count + 1 if user.login_count else 1
                    user.save()
                    
                    redirect_url = self._get_redirect_url(user)
                    print(f"🔄 Redirect URL: {redirect_url}")
                    print("="*60 + "\n")
                    
                    # FIXED: Create login history record
                    try:
                        # Check if LoginHistory model exists and create record
                        if hasattr(LoginHistory, 'objects'):
                            # Try to create with 'success' status
                            LoginHistory.objects.create(
                                user=user,
                                login_status='success',  # Use string value
                                ip_address=self._get_client_ip(request),
                                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                                method='2fa_otp'
                            )
                            print("📝 Login history recorded")
                    except Exception as e:
                        print(f"⚠️ Could not create login history: {str(e)}")
                    
                    return Response({
                        'success': True,
                        'message': 'OTP verified successfully',
                        'user': {
                            'id': str(user.id),
                            'email': user.email,
                            'first_name': user.first_name or '',
                            'last_name': user.last_name or '',
                            'role': user.role,
                            'profile_picture': user.profile_picture.url if user.profile_picture else None,
                            'profile_completed': user.profile_completed,
                        },
                        'tokens': {
                            'access': access_token,
                            'refresh': refresh_token
                        },
                        'redirect_url': redirect_url,
                        'requires_2fa': False
                    }, status=status.HTTP_200_OK)
                    
                except User.DoesNotExist:
                    print(f"❌ User not found: {session_data.get('user_id')}")
                    return Response({
                        'success': False,
                        'message': 'User not found',
                    }, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    print(f"❌ Error getting user: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return Response({
                        'success': False,
                        'message': f'Error: {str(e)}',
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print(f"\n❌ INVALID OTP")
                print(f"Expected: {expected_otp}")
                print(f"Received: {provided_otp}")
                print("="*60 + "\n")
                
                return Response({
                    'success': False,
                    'message': 'Invalid OTP',
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"\n❌ OTP verification error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': 'Server error during OTP verification',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# SESSION & LOGIN HISTORY VIEWS
# ============================================================================

class LoginSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for LoginSession model"""
    
    serializer_class = LoginSessionSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser or user.role == UserRole.ADMIN:
            return LoginSession.objects.all()
        
        return LoginSession.objects.filter(user=user)
    
    def perform_destroy(self, instance):
        """Revoke login session"""
        instance.revoke()
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def revoke(self, request, pk=None):
        """Revoke login session"""
        login_session = self.get_object()
        
        if login_session.status == LoginSession.SessionStatusChoices.REVOKED:
            return Response({
                'message': 'Session is already revoked.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        login_session.revoke()
        
        return Response({
            'message': 'Session revoked successfully.'
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def revoke_all(self, request):
        """Revoke all user sessions except current one"""
        user = request.user
        
        # Get current session ID from token
        current_session_id = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                access_token = AccessToken(token)
                current_session_id = access_token.get('session_id')
            except Exception:
                pass
        
        # Revoke all sessions except current one
        sessions = LoginSession.objects.filter(
            user=user,
            status=LoginSession.SessionStatusChoices.VERIFIED
        )
        
        if current_session_id:
            sessions = sessions.exclude(id=current_session_id)
        
        revoked_count = 0
        for session in sessions:
            session.revoke()
            revoked_count += 1
        
        return Response({
            'message': f'{revoked_count} sessions revoked successfully.'
        })


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for LoginHistory model (read-only)"""
    
    serializer_class = LoginHistorySerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'login_status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser or user.role == UserRole.ADMIN:
            return LoginHistory.objects.all()
        
        return LoginHistory.objects.filter(user=user)
    
    @action(detail=False, methods=['get'], permission_classes=[IsOwnerOrAdmin])
    def suspicious(self, request):
        """Get suspicious login attempts"""
        queryset = self.get_queryset().filter(is_suspicious=True)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# VERIFICATION RESEND VIEW
# ============================================================================

class ResendVerificationView(APIView):
    """
    Resend verification email/OTP
    This endpoint must be accessible without authentication (AllowAny)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            purpose = data.get('purpose', 'verification')
            
            print(f"📨 Resend verification requested for: {email}, purpose: {purpose}")
            
            if not email:
                return Response({
                    'success': False,
                    'message': 'Email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Try to find user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # For security, don't reveal if user exists
                print(f"⚠️ User not found for email: {email}")
                return Response({
                    'success': True,
                    'message': 'If an account exists with this email, verification has been resent.'
                })
            
            # Check purpose and resend accordingly
            if purpose == 'verification':
                if user.email_verified:
                    return Response({
                        'success': False,
                        'message': 'Email is already verified.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Resend verification email
                try:
                    user.send_verification_email(request)
                    print(f"✅ Verification email resent to: {email}")
                    
                    return Response({
                        'success': True,
                        'message': 'Verification email has been resent.',
                        'email': self._mask_email(email),
                        'purpose': purpose
                    })
                except Exception as e:
                    print(f"❌ Error sending verification email: {str(e)}")
                    return Response({
                        'success': False,
                        'message': 'Failed to resend verification email. Please try again later.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            elif purpose == 'login':
                # Resend OTP for login
                print(f"📱 Resending OTP for login to: {email}")
                
                # Check if there's a pending login session
                # In a real app, you'd check cache/database for pending OTP
                
                return Response({
                    'success': True,
                    'message': 'OTP has been resent.',
                    'email': self._mask_email(email),
                    'purpose': purpose
                })
            
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid purpose. Use "verification" or "login".'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"❌ Resend verification error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Server error while processing request.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _mask_email(self, email):
        """Mask email for security"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@')
        if len(local) <= 2:
            return f"{local[0]}***@{domain}"
        return f"{local[0]}***{local[-1]}@{domain}"


class ResendOTPView(APIView):
    """
    Specifically for resending OTP during login
    This is separate from verification resend
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            session_token = data.get('session_token')
            
            print(f"🔐 Resend OTP requested for: {email}")
            
            if not email:
                return Response({
                    'success': False,
                    'message': 'Email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # In a real implementation, you would:
            # 1. Validate session_token (if provided)
            # 2. Check rate limiting
            # 3. Generate new OTP
            # 4. Send via email/SMS
            
            # For now, simulate OTP resend
            print(f"📧 Simulating OTP resend to: {email}")
            
            return Response({
                'success': True,
                'message': 'OTP has been resent.',
                'email': self._mask_email(email),
                'method': 'email'
            })
            
        except Exception as e:
            print(f"❌ Resend OTP error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to resend OTP.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _mask_email(self, email):
        """Mask email for security"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@')
        if len(local) <= 2:
            return f"{local[0]}***@{domain}"
        return f"{local[0]}***{local[-1]}@{domain}"


# ============================================================================
# DASHBOARD & PREFERENCES VIEWS
# ============================================================================

class DashboardPreferencesView(APIView):
    """Update dashboard preferences"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current dashboard preferences"""
        serializer = DashboardPreferencesSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update dashboard preferences"""
        serializer = DashboardPreferencesSerializer(
            request.user, 
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRedirectView(APIView):
    """Get user redirect information after login"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserRedirectSerializer(request.user)
        return Response(serializer.data)


# ============================================================================
# BULK OPERATION VIEWS
# ============================================================================

class BulkUserUpdateView(APIView):
    """Bulk update users"""
    
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = BulkUserUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = serializer.save()
        
        return Response({
            'message': f'{result["updated_count"]} users updated successfully.',
            'action': result['action']
        })


class BulkUserDeleteView(APIView):
    """Bulk delete users"""
    
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = BulkUserDeleteSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = serializer.save()
        
        return Response({
            'message': f'{result["deleted_count"]} users deleted successfully.'
        })


# ============================================================================
# EXPORT VIEWS
# ============================================================================

class UserExportView(APIView):
    """Export user data"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Export user data in various formats"""
        format_type = request.query_params.get('format', 'json')
        include_sensitive = request.query_params.get('include_sensitive', 'false').lower() == 'true'
        user_id = request.query_params.get('user_id')
        
        if user_id:
            # Export single user
            try:
                user = User.objects.get(id=user_id)
                data = user.export_data(include_sensitive=include_sensitive)
                
                if format_type == 'json':
                    return JsonResponse(data, safe=False)
                elif format_type == 'csv':
                    return self._export_csv([data])
                elif format_type == 'xlsx':
                    return self._export_excel([data])
                else:
                    return Response({
                        'error': 'invalid_format',
                        'message': 'Supported formats: json, csv, xlsx'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except User.DoesNotExist:
                return Response({
                    'error': 'user_not_found',
                    'message': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Export all users (paginated for large datasets)
            users = User.objects.all()
            page = self.paginate_queryset(users)
            
            if page is not None:
                data = [user.export_data(include_sensitive=include_sensitive) for user in page]
                
                if format_type == 'json':
                    return self.get_paginated_response(data)
                elif format_type == 'csv':
                    return self._export_csv(data)
                elif format_type == 'xlsx':
                    return self._export_excel(data)
                else:
                    return Response({
                        'error': 'invalid_format',
                        'message': 'Supported formats: json, csv, xlsx'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            data = [user.export_data(include_sensitive=include_sensitive) for user in users]
            
            if format_type == 'json':
                return JsonResponse(data, safe=False)
            elif format_type == 'csv':
                return self._export_csv(data)
            elif format_type == 'xlsx':
                return self._export_excel(data)
            else:
                return Response({
                    'error': 'invalid_format',
                    'message': 'Supported formats: json, csv, xlsx'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    def _export_csv(self, data):
        """Export data as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        
        if data:
            # Write headers
            headers = list(data[0].keys())
            writer.writerow(headers)
            
            # Write data
            for item in data:
                row = []
                for header in headers:
                    value = item.get(header, '')
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    row.append(str(value))
                writer.writerow(row)
        
        return response
    
    def _export_excel(self, data):
        """Export data as Excel"""
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="users_export.xlsx"'
        
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet('Users')
        
        if data:
            # Write headers
            headers = list(data[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Write data
            for row_idx, item in enumerate(data, 1):
                for col_idx, header in enumerate(headers):
                    value = item.get(header, '')
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    worksheet.write(row_idx, col_idx, str(value))
        
        workbook.close()
        return response
    
    def paginate_queryset(self, queryset):
        """Paginate queryset"""
        from rest_framework.pagination import PageNumberPagination
        
        paginator = PageNumberPagination()
        paginator.page_size = 100  # Export in chunks
        return paginator.paginate_queryset(queryset, self.request, view=self)


# ============================================================================
# STATISTICS & ANALYTICS VIEWS
# ============================================================================

class UserStatsView(APIView):
    """Get user statistics"""
    
    permission_classes = [IsAdminUser]
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request):
        """Get user statistics"""
        
        # Total counts
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        pending_approval = User.objects.filter(
            is_approved=False,
            role__in=[
                UserRole.TEACHER,
                UserRole.HEAD_TEACHER,
                UserRole.CURRICULUM_COORDINATOR,
                UserRole.ACCOUNTANT,
                UserRole.IT_SUPPORT,
                UserRole.COUNSELOR
            ]
        ).count()
        suspended_users = User.objects.filter(is_suspended=True).count()
        
        # New users
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        new_users_today = User.objects.filter(
            created_at__date=today
        ).count()
        
        new_users_this_week = User.objects.filter(
            created_at__date__gte=week_ago
        ).count()
        
        # Profile completion
        profiles_completed = User.objects.filter(profile_completed=True).count()
        profiles_incomplete = User.objects.filter(profile_completed=False).count()
        
        # Role distribution
        role_distribution = dict(
            User.objects.values('role').annotate(
                count=Count('role')
            ).values_list('role', 'count')
        )
        
        # Activity
        online_now = User.objects.filter(
            last_activity__gte=timezone.now() - timedelta(minutes=15)
        ).count()
        
        logins_today = LoginHistory.objects.filter(
            created_at__date=today,
            login_status=LoginHistory.LoginStatusChoices.SUCCESS
        ).count()
        
        # Monthly registration trend
        monthly_trend = dict(
            User.objects.annotate(
                month=functions.TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month').values_list('month', 'count')
        )
        
        # Device distribution
        device_distribution = dict(
            LoginHistory.objects.values('device_type').annotate(
                count=Count('device_type')
            ).values_list('device_type', 'count')
        )
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'new_users_today': new_users_today,
            'new_users_this_week': new_users_this_week,
            'verified_users': verified_users,
            'pending_approval': pending_approval,
            'suspended_users': suspended_users,
            'role_distribution': role_distribution,
            'profiles_completed': profiles_completed,
            'profiles_incomplete': profiles_incomplete,
            'online_now': online_now,
            'logins_today': logins_today,
            'monthly_trend': monthly_trend,
            'device_distribution': device_distribution
        }
        
        serializer = StatsSerializer(stats)
        return Response(serializer.data)


class UserSearchView(APIView):
    """Search users"""
    
    permission_classes = [IsStaffOrAdmin]
    
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data.get('query', '')
        role = serializer.validated_data.get('role')
        is_active = serializer.validated_data.get('is_active')
        is_verified = serializer.validated_data.get('is_verified')
        is_approved = serializer.validated_data.get('is_approved')
        profile_completed = serializer.validated_data.get('profile_completed')
        
        # Build search query
        search_query = Q()
        
        if query:
            search_query |= Q(email__icontains=query)
            search_query |= Q(first_name__icontains=query)
            search_query |= Q(last_name__icontains=query)
            search_query |= Q(admission_number__icontains=query)
            search_query |= Q(staff_id__icontains=query)
            search_query |= Q(phone_number__icontains=query)
        
        if role:
            search_query &= Q(role=role)
        
        if is_active is not None:
            search_query &= Q(is_active=is_active)
        
        if is_verified is not None:
            search_query &= Q(is_verified=is_verified)
        
        if is_approved is not None:
            search_query &= Q(is_approved=is_approved)
        
        if profile_completed is not None:
            search_query &= Q(profile_completed=profile_completed)
        
        # Apply role-based filtering
        user = request.user
        queryset = User.objects.filter(search_query)
        
        if not (user.is_superuser or user.role == UserRole.ADMIN):
            if user.is_staff:
                queryset = queryset.filter(
                    Q(is_staff=True) | Q(role=UserRole.STUDENT) | Q(role=UserRole.PARENT)
                ).exclude(role=UserRole.ADMIN)
            elif user.role == UserRole.PARENT:
                children_emails = user.get_children().values_list('email', flat=True)
                queryset = queryset.filter(email__in=children_emails)
            elif user.role == UserRole.STUDENT:
                queryset = queryset.filter(id=user.id)
            else:
                queryset = User.objects.none()
        
        # Paginate results
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# UTILITY VIEWS
# ============================================================================

class HealthCheckView(APIView):
    """Health check endpoint"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check system health"""
        try:
            # Check database connection
            User.objects.count()
            
            # Check cache
            cache.set('health_check', 'ok', 10)
            cache_result = cache.get('health_check') == 'ok'
            
            health_status = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'database': 'connected',
                'cache': 'working' if cache_result else 'failed',
                'version': '1.0.0',
                'environment': settings.DEBUG and 'development' or 'production'
            }
            
            return Response(health_status)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class SystemInfoView(APIView):
    """Get system information"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get system information"""
        from django.conf import settings
        
        system_info = {
            'django_version': '3.2+',
            'python_version': '3.8+',
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'installed_apps': list(settings.INSTALLED_APPS),
            'database_backend': settings.DATABASES['default']['ENGINE'],
            'cache_backend': settings.CACHES['default']['BACKEND'],
            'timezone': settings.TIME_ZONE,
            'static_files': settings.STATIC_URL,
            'media_files': settings.MEDIA_URL,
        }
        
        return Response(system_info)


# ============================================================================
# ERROR HANDLING
# ============================================================================

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def handler404(request, exception=None):
    """Handle 404 errors"""
    return Response({
        'error': 'not_found',
        'message': 'The requested resource was not found.',
        'path': request.path
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def handler500(request):
    """Handle 500 errors"""
    logger.error(f"Server error: {request.path}")
    
    return Response({
        'error': 'server_error',
        'message': 'An internal server error occurred.',
        'path': request.path
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def handler400(request, exception=None):
    """Handle 400 errors"""
    return Response({
        'error': 'bad_request',
        'message': 'The request could not be understood.',
        'path': request.path
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def handler403(request, exception=None):
    """Handle 403 errors"""
    return Response({
        'error': 'forbidden',
        'message': 'You do not have permission to perform this action.',
        'path': request.path
    }, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def handler405(request, exception=None):
    """Handle 405 errors"""
    return Response({
        'error': 'method_not_allowed',
        'message': 'This method is not allowed for this resource.',
        'path': request.path,
        'method': request.method
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# ============================================================================
# TEST & DEBUG VIEWS
# ============================================================================

class TestEndpoint(APIView):
    """Test endpoint to verify API is working"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'success',
            'message': 'API is working!',
            'endpoint': '/api/v1/auth/',
            'timestamp': timezone.now().isoformat(),
            'available_endpoints': [
                'POST /api/v1/auth/login/',
                'POST /api/v1/auth/token/',
                'POST /api/v1/auth/token/refresh/',
                'GET /api/v1/auth/me/',
                'POST /api/v1/auth/logout/',
            ]
        })


class OTPDebugView(APIView):
    """
    Debug endpoint to view all active OTPs
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Show all active OTP sessions"""
        from django.core.cache import cache
        
        # Get all cache keys
        cache_keys = []
        if hasattr(cache, 'keys'):  # Redis
            cache_keys = cache.keys('2fa_session_*')
        else:
            # For local memory cache, we can't list all keys easily
            # Just return a message
            return Response({
                'message': 'Cache backend does not support key listing.',
                'tip': 'Check your Django console for OTP output when logging in.'
            })
        
        sessions = []
        for key in cache_keys:
            session_data = cache.get(key)
            if session_data:
                session_token = key.replace('2fa_session_', '')
                sessions.append({
                    'session_token': session_token,
                    'email': session_data.get('email'),
                    'otp': session_data.get('otp'),
                    'user_id': session_data.get('user_id'),
                    'created_at': session_data.get('created_at'),
                    'expires_at': session_data.get('expires_at')
                })
        
        return Response({
            'active_sessions': sessions,
            'count': len(sessions),
            'timestamp': timezone.now().isoformat()
        })
    
    def post(self, request):
        """Manually create a test OTP"""
        email = request.data.get('email', 'test@example.com')
        
        import random
        import uuid
        from django.core.cache import cache
        
        otp = str(random.randint(100000, 999999))
        session_token = str(uuid.uuid4())
        
        cache_key = f'2fa_session_{session_token}'
        cache_data = {
            'email': email,
            'otp': otp,
            'user_id': 'test-user-id',
            'created_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(minutes=10)).isoformat()
        }
        cache.set(cache_key, cache_data, 600)
        
        print("\n" + "⭐" * 50)
        print(f"⭐ MANUAL TEST OTP CREATED ⭐")
        print("⭐" * 50)
        print(f"📧 Email: {email}")
        print(f"🔢 OTP: {otp}")
        print(f"🔑 Session Token: {session_token}")
        print(f"⏰ Expires in: 10 minutes")
        print("⭐" * 50 + "\n")
        
        return Response({
            'success': True,
            'message': 'Test OTP created',
            'otp': otp,
            'session_token': session_token,
            'email': email
        })


class ProfileCompletionStatusView(APIView):
    """
    Check profile completion status
    This endpoint is called by the frontend AuthContext
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        print(f"\n" + "="*60)
        print(f"📋 PROFILE COMPLETION CHECK")
        print("="*60)
        print(f"👤 User: {user.email}")
        print(f"📊 Profile completed: {user.profile_completed}")
        
        # Calculate missing fields
        missing_fields = []
        
        # Check basic required fields
        required_fields = ['first_name', 'last_name', 'phone_number']
        
        for field in required_fields:
            value = getattr(user, field, None)
            if not value or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
        
        # Role-specific requirements
        role = user.role
        
        if role == UserRole.STUDENT:
            student_fields = ['date_of_birth', 'grade_level', 'current_class']
            for field in student_fields:
                value = getattr(user, field, None)
                if not value or (isinstance(value, str) and value.strip() == ''):
                    missing_fields.append(field)
        elif role == UserRole.PARENT:
            if not getattr(user, 'address', ''):
                missing_fields.append('address')
        elif role in [UserRole.TEACHER, UserRole.HEAD_TEACHER, 
                     UserRole.CURRICULUM_COORDINATOR, UserRole.ACCOUNTANT, 
                     UserRole.IT_SUPPORT, UserRole.COUNSELOR]:
            if not getattr(user, 'department', ''):
                missing_fields.append('department')
            if not getattr(user, 'designation', ''):
                missing_fields.append('designation')
        
        completion_percentage = user.profile_completion_percentage
        
        print(f"📈 Completion percentage: {completion_percentage}%")
        print(f"❌ Missing fields: {missing_fields}")
        print("="*60 + "\n")
        
        return Response({
            'success': True,
            'profile_completed': user.profile_completed,
            'profile_completion_date': user.profile_completion_date,
            'missing_fields': missing_fields,
            'completion_percentage': completion_percentage,
            'user_role': role
        })


class MarkProfileCompletedView(APIView):
    """
    Mark profile as completed
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        print(f"\n" + "="*60)
        print(f"✅ MARKING PROFILE AS COMPLETED")
        print("="*60)
        print(f"👤 User: {user.email}")
        
        # Update profile completion
        user.profile_completed = True
        user.profile_completion_date = timezone.now()
        user.save()
        
        print(f"📅 Profile completion date: {user.profile_completion_date}")
        print("="*60 + "\n")
        
        return Response({
            'success': True,
            'message': 'Profile marked as completed',
            'profile_completed': True,
            'profile_completion_date': user.profile_completion_date.isoformat()
        })



