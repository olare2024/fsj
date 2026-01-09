# accounts/urls.py - UPDATED & ENHANCED VERSION
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views
from .views import (
    # New viewsets
    UserViewSet,
    UserProfileViewSet,
    
    # Authentication views
    RegisterView,
    LoginView,
    LogoutView,
    TwoFactorLoginView,
    
    # Password and verification views
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerificationView,
    ResendVerificationView,
    
    # Two-factor authentication views
    TwoFactorSetupView,
    TwoFactorVerifyView,
    TwoFactorDisableView,
    TwoFactorBackupCodesView,
    
    # Dashboard and statistics views
    DashboardView,
    UserStatisticsView,
    
    # Search and filter views
    UserSearchView,
    
    # Utility views
    CheckEmailView,
    CheckUsernameView,
    ProfileCompletionView,
    ActivityUpdateView,
    
    # Public views
    health_check,
    version_info,
    
    # Custom JWT view
    CustomTokenObtainPairView,
)

# Create router for viewset-based endpoints
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')

# ==================== APP NAME FOR REVERSE URL RESOLUTION ====================
app_name = 'accounts'

# ==================== ROOT URL PATTERNS ====================
urlpatterns = [
    # === API Root ===
    path('', views.api_root, name='api-root'),
    
    # === Router URLs (for ViewSet CRUD operations) ===
    path('', include(router.urls)),
    
    # ==================== AUTHENTICATION URLS ====================
    # Registration
    path('register/', RegisterView.as_view(), name='register'),
    
    # Login/Logout
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # 2FA Login
    path('login/2fa/', TwoFactorLoginView.as_view(), name='login-2fa'),
    
    # JWT Token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    
    # ==================== PASSWORD MANAGEMENT URLS ====================
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Email verification
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    
    # ==================== TWO-FACTOR AUTHENTICATION URLS ====================
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('2fa/disable/', TwoFactorDisableView.as_view(), name='2fa-disable'),
    path('2fa/backup-codes/', TwoFactorBackupCodesView.as_view(), name='2fa-backup-codes'),
    
    # ==================== DASHBOARD AND STATISTICS URLS ====================
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('statistics/', UserStatisticsView.as_view(), name='statistics'),
    
    # ==================== SEARCH AND FILTER URLS ====================
    path('search/users/', UserSearchView.as_view(), name='user-search'),
    
    # ==================== UTILITY URLS ====================
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('profile-completion/', ProfileCompletionView.as_view(), name='profile-completion'),
    path('activity/', ActivityUpdateView.as_view(), name='activity-update'),
    
    # ==================== PUBLIC URLS ====================
    path('health/', health_check, name='health-check'),
    path('version/', version_info, name='api-version'),
    
    # ==================== USER-SPECIFIC URLS ====================
    # Current user endpoints (using UserViewSet actions)
    path('me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('me/update-profile/', UserViewSet.as_view({'post': 'update_profile'}), name='user-update-profile'),
    path('me/change-password/', UserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    
    # User profile endpoints (using UserProfileViewSet actions)
    path('me/profile/', UserProfileViewSet.as_view({'get': 'my_profile'}), name='my-profile'),
    path('me/profile/update/', UserProfileViewSet.as_view({'post': 'update_my_profile'}), name='update-my-profile'),
    
    # ==================== ADMIN URLS ====================
    # User management (using UserViewSet actions)
    path('admin/users/<uuid:pk>/activate/', UserViewSet.as_view({'post': 'activate'}), name='admin-activate-user'),
    path('admin/users/<uuid:pk>/deactivate/', UserViewSet.as_view({'post': 'deactivate'}), name='admin-deactivate-user'),
    path('admin/users/<uuid:pk>/verify/', UserViewSet.as_view({'post': 'verify'}), name='admin-verify-user'),
    path('admin/users/<uuid:pk>/suspend/', UserViewSet.as_view({'post': 'suspend'}), name='admin-suspend-user'),
    
    # Bulk operations
    path('admin/users/bulk-update-status/', UserViewSet.as_view({'post': 'bulk_update_status'}), name='admin-bulk-update-status'),
    
    # Export
    path('admin/users/export/', UserViewSet.as_view({'get': 'export'}), name='admin-export-users'),
    
    # Statistics
    path('admin/statistics/', UserViewSet.as_view({'get': 'statistics'}), name='admin-statistics'),
]

# ==================== API VERSIONING SUPPORT ====================
# If you need API versioning, you can structure like this:
api_v1_patterns = [
    # Auth endpoints
    path('auth/login/', LoginView.as_view(), name='v1-auth-login'),
    path('auth/register/', RegisterView.as_view(), name='v1-auth-register'),
    path('auth/logout/', LogoutView.as_view(), name='v1-auth-logout'),
    
    # User endpoints
    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='v1-user-me'),
    path('users/me/profile/', UserProfileViewSet.as_view({'get': 'my_profile'}), name='v1-user-profile'),
    
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='v1-dashboard'),
]

# You can include versioned patterns like this:
# urlpatterns += [
#     path('api/v1/', include(api_v1_patterns)),
# ]

# ==================== DEBUG ENDPOINTS (Development only) ====================
if settings.DEBUG:
    from .views import debug_urls
    
    urlpatterns += [
        path('debug/urls/', debug_urls, name='debug-urls'),
        path('debug/token-test/', CustomTokenObtainPairView.as_view(), name='debug-token-test'),
    ]