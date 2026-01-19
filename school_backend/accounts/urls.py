# accounts/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'two-factor-auth', views.TwoFactorAuthViewSet, basename='two-factor-auth')
router.register(r'otp-tokens', views.OTPTokenViewSet, basename='otp-token')
router.register(r'login-sessions', views.LoginSessionViewSet, basename='login-session')
router.register(r'login-history', views.LoginHistoryViewSet, basename='login-history')

urlpatterns = [
    # ==================== AUTHENTICATION ENDPOINTS ====================
    
    # Login/OTP flow (React is calling these)
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    
    # Resend endpoints (MUST be there - your frontend is calling /auth/resend-verification/)
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    
    # JWT Token endpoints
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Profile completion endpoints (MUST be there)
    path('profile/completion-status/', views.ProfileCompletionStatusView.as_view(), name='profile-completion-status'),
    path('profile/mark-completed/', views.MarkProfileCompletedView.as_view(), name='mark-profile-completed'),
    
    # Logout
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Password Management
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/change/', views.ChangePasswordView.as_view(), name='password_change'),
    
    # ==================== USER PROFILE ENDPOINTS ====================
    
    # Current user endpoints (these are called by your frontend)
    path('me/', views.UserViewSet.as_view({'get': 'me', 'put': 'update_me', 'patch': 'update_me'}), name='me'),
    path('dashboard-info/', views.UserViewSet.as_view({'get': 'dashboard_info'}), name='dashboard_info'),
    
    # Dashboard and preferences
    path('dashboard-preferences/', views.DashboardPreferencesView.as_view(), name='dashboard-preferences'),
    path('redirect/', views.UserRedirectView.as_view(), name='user-redirect'),
    
    # Permissions
    path('permissions/', views.UserViewSet.as_view({'get': 'permissions'}), name='permissions'),
    
    # Registration
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # ==================== VERIFICATION ENDPOINTS ====================
    
    # Email verification
    path('email/verify/', views.EmailVerificationView.as_view(), name='email-verification'),
    path('email/verify/confirm/', views.VerifyEmailView.as_view(), name='verify-email'),
    
    # Phone verification
    path('phone/verify/', views.PhoneVerificationView.as_view(), name='phone-verification'),
    path('phone/verify/confirm/', views.VerifyPhoneView.as_view(), name='verify-phone'),
    
    # ==================== STATISTICS & ANALYTICS ====================
    path('stats/', views.UserStatsView.as_view(), name='user-stats'),
    path('search/', views.UserSearchView.as_view(), name='user-search'),
    
    # ==================== BULK OPERATIONS ====================
    path('bulk-update/', views.BulkUserUpdateView.as_view(), name='bulk-update'),
    path('bulk-delete/', views.BulkUserDeleteView.as_view(), name='bulk-delete'),
    path('export/', views.UserExportView.as_view(), name='user-export'),
    
    # ==================== UTILITY & DEBUG ENDPOINTS ====================
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('system-info/', views.SystemInfoView.as_view(), name='system-info'),
    path('test/', views.TestEndpoint.as_view(), name='test-endpoint'),
    path('otp-debug/', views.OTPDebugView.as_view(), name='otp-debug'),
    
    # ==================== INCLUDE ROUTER URLS ====================
    path('', include(router.urls)),
]

# Error handlers
handler404 = 'accounts.views.handler404'
handler500 = 'accounts.views.handler500'
handler400 = 'accounts.views.handler400'
handler403 = 'accounts.views.handler403'
handler405 = 'accounts.views.handler405'