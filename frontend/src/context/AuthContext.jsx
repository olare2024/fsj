// src/context/AuthContext.jsx - COMPLETE FIXED VERSION WITH PROFILE COMPLETION TRACKING
import React, { createContext, useState, useContext, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import authAPI from '../services/authAPI.js';
import api from '../services/api.js';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  // ==================== STATE ====================
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [userPermissions, setUserPermissions] = useState([]);
  const [financeAccess, setFinanceAccess] = useState({
    canViewFinance: false,
    canManageReceipts: false,
    canManagePayments: false,
    canViewReports: false,
    canReconcile: false,
    canApprovePayments: false
  });
  const [featureFlags, setFeatureFlags] = useState({});
  
  // Refs for preventing race conditions
  const isCheckingAuth = useRef(false);
  const lastCheckTime = useRef(0);
  const profileCheckComplete = useRef(false);
  const navigate = useNavigate();
  const location = useLocation();

  // ==================== CONSTANTS ====================
  const DASHBOARD_URLS = {
    admin: '/admin/admin-portal',
    head_teacher: '/head-teacher/headteacher-portal',
    curriculum_coordinator: '/curriculum/curriculum-portal',
    teacher: '/teacher/teacher-portal',
    office_staff: '/staff/staff-portal',
    student: '/student/student-portal',
    parent: '/parent/parent-portal',
    librarian: '/library/library-portal',
    accountant: '/accountant/accountant-portal',
    it_support: '/it/it-portal',
    counselor: '/counselor/counselor-portal',
  };

  // ==================== UTILITY FUNCTIONS ====================
  const clearError = () => setError(null);

  const clearAuth = useCallback((message = 'Session expired. Please login again.') => {
    console.log('🧹 Clearing auth data...');
    
    // Clear all storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('last_activity');
    localStorage.removeItem('auth_timestamp');
    sessionStorage.clear();
    
    // Clear cookies related to authentication
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
    
    // Clear state
    setCurrentUser(null);
    setIsAuthenticated(false);
    setError(message);
    setSessionData(null);
    setUserPermissions([]);
    setFinanceAccess({
      canViewFinance: false,
      canManageReceipts: false,
      canManagePayments: false,
      canViewReports: false,
      canReconcile: false,
      canApprovePayments: false
    });
    setFeatureFlags({});
    
    // Reset refs
    isCheckingAuth.current = false;
    lastCheckTime.current = 0;
    profileCheckComplete.current = false;
    
    // Redirect to login
    if (window.location.pathname !== '/login' && !window.location.pathname.includes('/auth/')) {
      navigate('/login?session=expired', { replace: true });
    }
  }, [navigate]);

  // ==================== PERMISSION LOADING FUNCTIONS ====================
  const loadUserPermissions = useCallback((user) => {
    const userData = user?.user || user;
    if (!userData?.role) return;

    const role = userData.role;
    const permissions = [];
    const financeAccessConfig = {
      canViewFinance: false,
      canManageReceipts: false,
      canManagePayments: false,
      canViewReports: false,
      canReconcile: false,
      canApprovePayments: false
    };

    const roleConfigs = {
      admin: {
        permissions: ['*', 'users.manage', 'system.manage', 'finance.manage', 'reports.manage', 'academic.manage'],
        finance: { all: true }
      },
      accountant: {
        permissions: ['finance.view', 'finance.manage', 'reports.view', 'reports.generate', 'billing.manage'],
        finance: { all: true }
      },
      teacher: {
        permissions: ['students.view', 'attendance.manage', 'grades.manage', 'lessons.manage'],
        finance: { canViewFinance: true }
      },
      head_teacher: {
        permissions: ['students.manage', 'teachers.manage', 'attendance.manage', 'grades.manage', 'reports.view'],
        finance: { canViewFinance: true, canViewReports: true }
      },
      curriculum_coordinator: {
        permissions: ['curriculum.manage', 'courses.manage', 'programs.manage'],
        finance: {}
      },
      student: {
        permissions: ['profile.view', 'grades.view', 'attendance.view', 'courses.view'],
        finance: { canViewFinance: true }
      },
      parent: {
        permissions: ['profile.view', 'children.view', 'grades.view', 'attendance.view'],
        finance: { canViewFinance: true }
      },
      librarian: {
        permissions: ['library.manage', 'resources.manage'],
        finance: {}
      },
      it_support: {
        permissions: ['system.view', 'users.manage', 'tickets.manage'],
        finance: {}
      },
      counselor: {
        permissions: ['students.view', 'counseling.manage', 'reports.view'],
        finance: {}
      },
      office_staff: {
        permissions: ['students.view', 'attendance.view', 'reports.view'],
        finance: {}
      }
    };

    const config = roleConfigs[role] || {};
    permissions.push(...(config.permissions || []));
    
    // Set finance access
    if (config.finance?.all) {
      Object.keys(financeAccessConfig).forEach(key => financeAccessConfig[key] = true);
    } else {
      Object.keys(config.finance || {}).forEach(key => {
        if (financeAccessConfig.hasOwnProperty(key)) {
          financeAccessConfig[key] = config.finance[key];
        }
      });
    }

    setUserPermissions(permissions);
    setFinanceAccess(financeAccessConfig);
  }, []);

  const loadFeatureFlags = useCallback((user) => {
    const userData = user?.user || user;
    if (!userData?.role) return;

    const role = userData.role;
    const flags = {
      canViewDashboard: true,
      canExportData: ['admin', 'accountant', 'head_teacher'].includes(role),
      canManageStudents: ['admin', 'teacher', 'head_teacher'].includes(role),
      canViewStudentFinance: ['admin', 'accountant', 'teacher', 'head_teacher'].includes(role),
      canGenerateReports: ['admin', 'accountant', 'head_teacher'].includes(role),
      canViewAnalytics: ['admin', 'accountant', 'head_teacher', 'teacher'].includes(role),
      canManageUsers: ['admin', 'head_teacher'].includes(role),
      canManageSystem: ['admin', 'it_support'].includes(role),
      canManageCurriculum: ['admin', 'curriculum_coordinator', 'head_teacher'].includes(role),
      canManageLibrary: ['admin', 'librarian'].includes(role),
      canManageCounseling: ['admin', 'counselor'].includes(role),
      canReceiveNotifications: true,
      canManageNotifications: ['admin', 'teacher', 'head_teacher'].includes(role),
      requires2FASetup: ['admin', 'accountant', 'it_support'].includes(role) && !userData.has_2fa_enabled,
    };
    
    setFeatureFlags(flags);
  }, []);

  // ==================== HELPER FUNCTIONS ====================
  const getUserData = (user = null) => {
    const targetUser = user || currentUser;
    return targetUser?.user || targetUser;
  };

  const getDashboardUrl = (user = null) => {
    const userData = getUserData(user);
    if (!userData?.role) return '/dashboard';
    return DASHBOARD_URLS[userData.role] || '/dashboard';
  };

  // ==================== FIXED: PROFILE COMPLETION CHECKING ====================
  const hasCompletedProfile = (user = null) => {
    const targetUser = user || currentUser;
    const userData = getUserData(targetUser);
    
    if (!userData) return false;

    // Use the backend's profile_completed flag if available
    // This is the key fix - we check the stored flag, not recalculate
    if (userData.profile_completed !== undefined) {
      return userData.profile_completed === true;
    }

    // Fallback to field-based check for backward compatibility
    // This is only used if the backend doesn't send profile_completed flag
    const requiredFields = ['first_name', 'last_name', 'phone_number'];

    if (userData.role === 'student') {
      requiredFields.push('date_of_birth', 'grade_level', 'current_class');
    } else if (userData.role === 'parent') {
      requiredFields.push('address');
    } else if (['teacher', 'head_teacher', 'curriculum_coordinator', 'accountant', 'it_support', 'counselor'].includes(userData.role)) {
      requiredFields.push('department', 'designation');
    }

    for (const field of requiredFields) {
      const value = userData[field];
      const isEmpty = !value || (typeof value === 'string' && value.trim() === '');
      
      if (isEmpty) return false;
    }

    return true;
  };

  // ==================== MARK PROFILE AS COMPLETED ====================
  const markProfileCompleted = async () => {
    try {
      const response = await api.post('/auth/profile/mark-completed/');
      
      if (response.data.success) {
        // Update local user data
        const updatedUser = {
          ...currentUser,
          profile_completed: true,
          profile_completion_date: response.data.profile_completion_date
        };
        
        setCurrentUser(updatedUser);
        localStorage.setItem('user_data', JSON.stringify(updatedUser));
        
        console.log('✅ Profile marked as completed in backend');
        
        return {
          success: true,
          message: 'Profile marked as completed'
        };
      }
      
      return {
        success: false,
        message: response.data.message || 'Failed to mark profile as completed'
      };
    } catch (error) {
      console.error('❌ Error marking profile as completed:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to mark profile as completed'
      };
    }
  };

  // ==================== CHECK PROFILE COMPLETION ON BACKEND ====================
  const checkProfileCompletionOnBackend = async () => {
    try {
      const response = await api.get('/auth/profile/completion-status/');
      
      if (response.data.success) {
        const { profile_completed, profile_completion_date, missing_fields } = response.data;
        
        // Update local user data with backend status
        if (currentUser) {
          const updatedUser = {
            ...currentUser,
            profile_completed,
            profile_completion_date
          };
          
          setCurrentUser(updatedUser);
          localStorage.setItem('user_data', JSON.stringify(updatedUser));
        }
        
        return {
          success: true,
          profile_completed,
          profile_completion_date,
          missing_fields
        };
      }
      
      return {
        success: false,
        message: response.data.message || 'Failed to check profile completion'
      };
    } catch (error) {
      console.error('❌ Error checking profile completion:', error);
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to check profile completion'
      };
    }
  };

  const requiresApproval = (user = null) => {
    const userData = getUserData(user);
    if (!userData) return false;
    
    return [
      'teacher', 
      'head_teacher', 
      'curriculum_coordinator',
      'accountant',
      'it_support',
      'counselor'
    ].includes(userData.role);
  };

  const getRedirectUrlAfterLogin = (user = null) => {
    const userData = getUserData(user);
    if (!userData) return '/login';
    
    // Use the stored profile_completed flag from backend
    if (userData.profile_completed === false) {
      console.log('📝 Profile not completed, redirecting to complete-profile');
      return '/complete-profile';
    }
    
    if (userData.is_suspended) {
      return '/account-suspended';
    }
    
    if (!userData.is_approved && requiresApproval(userData)) {
      return '/pending-approval';
    }
    
    if (userData.is_password_expired) {
      return '/change-password';
    }
    
    return getDashboardUrl(userData);
  };

  // ==================== FIXED: CHECK AUTH STATUS ====================
  const checkAuthStatus = useCallback(async (forceCheck = false) => {
    // Prevent concurrent checks
    if (isCheckingAuth.current && !forceCheck) {
      console.log('⏳ Auth check already in progress, skipping...');
      return;
    }
    
    // Throttle checks (minimum 2 seconds between checks)
    const now = Date.now();
    if (!forceCheck && now - lastCheckTime.current < 2000) {
      console.log('⏳ Auth check throttled, skipping...');
      return;
    }
    
    isCheckingAuth.current = true;
    lastCheckTime.current = now;
    
    try {
      const token = localStorage.getItem('access_token');
      
      // If no token, user is not authenticated
      if (!token) {
        console.log('🔐 No token found, user is not authenticated');
        setIsAuthenticated(false);
        setCurrentUser(null);
        setLoading(false);
        return;
      }

      console.log('🔄 Checking authentication status...');
      setLoading(true);
      
      try {
        // Get fresh user data from server
        const userResponse = await authAPI.getCurrentUser();
        
        if (userResponse.success) {
          console.log('✅ User authenticated:', userResponse.user.email);
          
          // Ensure profile_completed field is included
          const userWithProfileFlag = {
            ...userResponse.user,
            profile_completed: userResponse.user.profile_completed || false
          };
          
          setCurrentUser(userWithProfileFlag);
          setIsAuthenticated(true);
          
          // Load permissions and feature flags
          loadUserPermissions(userWithProfileFlag);
          loadFeatureFlags(userWithProfileFlag);
          
          // Store auth timestamp and user data
          localStorage.setItem('auth_timestamp', Date.now().toString());
          localStorage.setItem('user_data', JSON.stringify(userWithProfileFlag));
          
          console.log('✅ Profile completion status:', userWithProfileFlag.profile_completed);
        } else {
          console.log('❌ User authentication failed');
          clearAuth();
        }
      } catch (error) {
        console.log('❌ Auth check failed:', error.message);
        
        // If it's a 401 error, try to refresh token
        if (error.message.includes('Authentication expired') || error.message.includes('401')) {
          console.log('🔄 Attempting token refresh...');
          const refreshed = await handleTokenRefresh();
          if (!refreshed) {
            clearAuth();
          }
        } else {
          clearAuth();
        }
      }
    } catch (error) {
      console.error('❌ Error in checkAuthStatus:', error);
      clearAuth();
    } finally {
      setLoading(false);
      isCheckingAuth.current = false;
    }
  }, [clearAuth, loadUserPermissions, loadFeatureFlags]);

  // ==================== FIXED: HANDLE TOKEN REFRESH ====================
  const handleTokenRefresh = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        console.log('🔐 No refresh token available');
        clearAuth('No refresh token available');
        return false;
      }

      console.log('🔄 Attempting to refresh token...');
      
      // Use the correct endpoint from authAPI
      const refreshResponse = await authAPI.refreshToken();
      
      if (refreshResponse.success) {
        console.log('✅ Token refresh successful');
        return true;
      }
      
      console.log('❌ Token refresh failed:', refreshResponse.message);
      clearAuth('Token refresh failed');
      return false;
    } catch (error) {
      console.error('❌ Token refresh error:', error);
      
      // Don't immediately clear tokens for network errors
      if (error.message.includes('Network') || error.message.includes('timeout')) {
        console.log('🌐 Network error during token refresh, retrying later...');
        return false;
      }
      
      clearAuth('Authentication failed. Please login again.');
      return false;
    }
  }, [clearAuth]);

  // ==================== FIXED: INITIAL AUTH CHECK ====================
  useEffect(() => {
    console.log('🚀 AuthContext mounting - initial auth check');
    
    const initAuth = async () => {
      // Check if we have a token
      const token = localStorage.getItem('access_token');
      const userData = localStorage.getItem('user_data');
      
      if (!token) {
        console.log('🔐 No token found, setting not authenticated');
        setIsAuthenticated(false);
        setCurrentUser(null);
        setLoading(false);
        return;
      }
      
      // If we have user data, set it immediately (for faster UI)
      if (userData) {
        try {
          const parsedUser = JSON.parse(userData);
          if (parsedUser && parsedUser.email) {
            console.log('📋 Using cached user data while checking auth');
            
            // Ensure profile_completed flag exists in cached data
            const userWithProfileFlag = {
              ...parsedUser,
              profile_completed: parsedUser.profile_completed || false
            };
            
            setCurrentUser(userWithProfileFlag);
            loadUserPermissions(userWithProfileFlag);
            loadFeatureFlags(userWithProfileFlag);
            setIsAuthenticated(true);
          }
        } catch (e) {
          console.error('Error parsing cached user data:', e);
        }
      }
      
      // Then do the actual auth check
      await checkAuthStatus(true);
    };
    
    initAuth();
  }, [checkAuthStatus, loadUserPermissions, loadFeatureFlags]);

  // ==================== AUTO-REFRESH AUTH ====================
  useEffect(() => {
    if (!isAuthenticated) return;
    
    // Set up periodic auth refresh (every 10 minutes)
    const refreshInterval = setInterval(() => {
      console.log('🔄 Auto-refreshing auth status...');
      checkAuthStatus();
    }, 10 * 60 * 1000); // 10 minutes
    
    return () => clearInterval(refreshInterval);
  }, [isAuthenticated, checkAuthStatus]);

  // ==================== MAIN AUTH METHODS ====================
  const login = async (credentials) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await authAPI.login(credentials);

      if (result.success) {
        if (result.user) {
          // Ensure profile_completed field is included
          const userWithProfileFlag = {
            ...result.user,
            profile_completed: result.user.profile_completed || false
          };
          
          setCurrentUser(userWithProfileFlag);
          setIsAuthenticated(true);
          localStorage.setItem('user_data', JSON.stringify(userWithProfileFlag));
          localStorage.setItem('auth_timestamp', Date.now().toString());
        }
        
        if (result.tokens) {
          localStorage.setItem('access_token', result.tokens.access);
          localStorage.setItem('refresh_token', result.tokens.refresh);
        }
        
        if (result.requires_2fa || result.status === '2fa_required') {
          setSessionData({
            requires_2fa: true,
            session_token: result.session_token,
            user_id: result.user_id,
            email: credentials.email,
            method: result.method,
            masked_email: result.masked_email || credentials.email,
            expires_in: result.expires_in,
            message: result.message,
            intended_redirect: getRedirectUrlAfterLogin(result.user)
          });
          
          return {
            success: true,
            requires_2fa: true,
            message: result.message,
            session_token: result.session_token,
            user_id: result.user_id,
            method: result.method,
            email: credentials.email,
            expires_in: result.expires_in
          };
        }
        
        loadUserPermissions(result.user);
        loadFeatureFlags(result.user);
        
        const redirectUrl = getRedirectUrlAfterLogin(result.user);
        
        return {
          success: true,
          message: result.message || 'Login successful',
          user: result.user,
          redirect_url: redirectUrl,
          requires_2fa: false
        };
      } else {
        const errorMessage = result.message || 'Login failed';
        setError(errorMessage);
        return {
          success: false,
          message: errorMessage,
          errors: result.errors
        };
      }
    } catch (error) {
      const errorMessage = error.message || 'Login failed. Please try again.';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  // ==================== VERIFY LOGIN OTP ====================
  const verifyLoginOTP = async (otpData) => {
    try {
      setLoading(true);
      setError(null);
      
      // Validate session data
      if (!sessionData || !sessionData.session_token) {
        throw new Error('Session expired. Please login again.');
      }
      
      const result = await authAPI.verifyOTP(otpData);

      if (result.success) {
        if (result.user) {
          // Ensure profile_completed field is included
          const userWithProfileFlag = {
            ...result.user,
            profile_completed: result.user.profile_completed || false
          };
          
          setCurrentUser(userWithProfileFlag);
          setIsAuthenticated(true);
          localStorage.setItem('user_data', JSON.stringify(userWithProfileFlag));
          localStorage.setItem('auth_timestamp', Date.now().toString());
        }
        
        if (result.tokens) {
          localStorage.setItem('access_token', result.tokens.access);
          localStorage.setItem('refresh_token', result.tokens.refresh);
        }
        
        loadUserPermissions(result.user);
        loadFeatureFlags(result.user);
        
        let redirectUrl = sessionData?.intended_redirect;
        if (!redirectUrl) {
          redirectUrl = getRedirectUrlAfterLogin(result.user);
        }
        
        setSessionData(null);
        
        return {
          success: true,
          message: result.message || 'OTP verification successful',
          user: result.user,
          redirect_url: redirectUrl
        };
      } else {
        const errorMessage = result.message || 'OTP verification failed';
        setError(errorMessage);
        return {
          success: false,
          message: errorMessage
        };
      }
    } catch (error) {
      const errorMessage = error.message || 'OTP verification failed';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  // ==================== RESEND OTP ====================
  const resendOTP = async (email, purpose = 'login') => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await authAPI.resendVerification(email, purpose);
      
      if (result.success) {
        return {
          success: true,
          message: result.message || 'OTP sent successfully'
        };
      } else {
        throw new Error(result.message || 'Failed to resend OTP');
      }
    } catch (error) {
      const errorMessage = error.message || 'Failed to resend OTP. Please try again.';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await authAPI.register(userData);

      if (result.success) {
        if (result.requires_verification) {
          return {
            success: true,
            requires_verification: true,
            message: result.message || 'Registration successful! Please verify your email.'
          };
        } else if (result.user) {
          const userWithProfileFlag = {
            ...result.user,
            profile_completed: result.user.profile_completed || false
          };
          
          setCurrentUser(userWithProfileFlag);
          setIsAuthenticated(true);
          localStorage.setItem('user_data', JSON.stringify(userWithProfileFlag));
          localStorage.setItem('auth_timestamp', Date.now().toString());
          
          loadUserPermissions(userWithProfileFlag);
          loadFeatureFlags(userWithProfileFlag);
          
          return {
            success: true,
            user: userWithProfileFlag,
            message: result.message || 'Registration successful!'
          };
        } else {
          return {
            success: true,
            message: result.message || 'Registration successful! Please login.'
          };
        }
      } else {
        const errorMessage = result.message || 'Registration failed';
        setError(errorMessage);
        return {
          success: false,
          message: errorMessage,
          errors: result.errors
        };
      }
    } catch (error) {
      const errorMessage = error.message || 'Registration failed';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  // ==================== PROFILE MANAGEMENT ====================
  const updateUser = async (userData = null) => {
    try {
      if (userData) {
        // Ensure profile_completed is preserved
        const updatedUser = { 
          ...currentUser, 
          ...userData,
          profile_completed: userData.profile_completed !== undefined ? userData.profile_completed : currentUser?.profile_completed || false
        };
        setCurrentUser(updatedUser);
        localStorage.setItem('user_data', JSON.stringify(updatedUser));
        return { success: true, user: updatedUser };
      }
      
      const result = await authAPI.getCurrentUser();
      if (result.success) {
        const user = result.user || result.data;
        const userWithProfileFlag = {
          ...user,
          profile_completed: user.profile_completed || false
        };
        setCurrentUser(userWithProfileFlag);
        localStorage.setItem('user_data', JSON.stringify(userWithProfileFlag));
        return { success: true, user: userWithProfileFlag };
      }
      return { success: false, message: result.message };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await authAPI.updateProfile(profileData);
      
      if (result.success) {
        const updatedUser = { 
          ...currentUser, 
          ...result.user,
          profile_completed: result.user?.profile_completed !== undefined ? result.user.profile_completed : currentUser?.profile_completed || false
        };
        setCurrentUser(updatedUser);
        localStorage.setItem('user_data', JSON.stringify(updatedUser));
        
        return { success: true, user: updatedUser, message: result.message };
      } else {
        throw new Error(result.message || 'Profile update failed');
      }
    } catch (error) {
      const errorMessage = error.message || 'Failed to update profile';
      setError(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async (passwordData) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await authAPI.changePassword(passwordData);
      
      if (result.success) {
        return { success: true, message: result.message || 'Password updated successfully' };
      } else {
        throw new Error(result.message || 'Password change failed');
      }
    } catch (error) {
      const errorMessage = error.message || 'Failed to change password';
      setError(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const requestPasswordReset = async (email) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await authAPI.requestPasswordReset(email);
      
      if (result.success) {
        return {
          success: true,
          message: result.message || 'Password reset instructions sent to your email'
        };
      } else {
        throw new Error(result.message || 'Failed to request password reset');
      }
    } catch (error) {
      const errorMessage = error.message || 'Failed to request password reset';
      setError(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const confirmPasswordReset = async (resetData) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await authAPI.confirmPasswordReset(resetData);
      
      if (result.success) {
        return {
          success: true,
          message: result.message || 'Password reset successfully'
        };
      } else {
        throw new Error(result.message || 'Failed to reset password');
      }
    } catch (error) {
      const errorMessage = error.message || 'Failed to reset password';
      setError(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // ==================== PERMISSION & ROLE METHODS ====================
  const hasPermission = (permission) => {
    return userPermissions.includes('*') || userPermissions.includes(permission);
  };

  const hasAnyPermission = (permissions) => {
    return permissions.some(permission => hasPermission(permission));
  };

  const hasAllPermissions = (permissions) => {
    return permissions.every(permission => hasPermission(permission));
  };

  const hasRole = (role) => {
    const userData = getUserData();
    return userData?.role === role;
  };

  const hasAnyRole = (roles) => {
    const userData = getUserData();
    return roles.includes(userData?.role);
  };

  const isStudent = () => hasRole('student');
  const isTeacher = () => hasRole('teacher');
  const isParent = () => hasRole('parent');
  const isAdmin = () => hasRole('admin');
  const isAccountant = () => hasRole('accountant');
  const isHeadTeacher = () => hasRole('head_teacher');
  const isCurriculumCoordinator = () => hasRole('curriculum_coordinator');
  const isLibrarian = () => hasRole('librarian');
  const isCounselor = () => hasRole('counselor');
  const isITSupport = () => hasRole('it_support');
  const isOfficeStaff = () => hasRole('office_staff');

  const canViewFinance = () => financeAccess.canViewFinance;
  const canManageReceipts = () => financeAccess.canManageReceipts;
  const canManagePayments = () => financeAccess.canManagePayments;
  const canViewReports = () => financeAccess.canViewReports;
  const canReconcile = () => financeAccess.canReconcile;
  const canApprovePayments = () => financeAccess.canApprovePayments;

  const canExportData = () => featureFlags.canExportData || false;
  const canManageStudents = () => featureFlags.canManageStudents || false;
  const canViewStudentFinance = () => featureFlags.canViewStudentFinance || false;
  const canGenerateReports = () => featureFlags.canGenerateReports || false;
  const canViewAnalytics = () => featureFlags.canViewAnalytics || false;
  const canManageUsers = () => featureFlags.canManageUsers || false;
  const canManageSystem = () => featureFlags.canManageSystem || false;
  const canManageCurriculum = () => featureFlags.canManageCurriculum || false;
  const canManageLibrary = () => featureFlags.canManageLibrary || false;
  const canManageCounseling = () => featureFlags.canManageCounseling || false;

  const getUserInitials = () => {
    const userData = getUserData();
    if (!userData) return '';
    const firstName = userData.first_name || userData.firstName || '';
    const lastName = userData.last_name || userData.lastName || '';
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const getFullName = () => {
    const userData = getUserData();
    if (!userData) return '';
    const firstName = userData.first_name || userData.firstName || '';
    const lastName = userData.last_name || userData.lastName || '';
    return `${firstName} ${lastName}`.trim();
  };

  // ==================== CONTEXT VALUE ====================
  const value = {
    // State
    currentUser,
    isAuthenticated,
    loading,
    error,
    sessionData,
    userPermissions,
    financeAccess,
    featureFlags,
    
    // Authentication methods
    login,
    verifyLoginOTP,
    resendOTP,
    register,
    logout: clearAuth,
    clearError,
    
    // Password reset methods
    requestPasswordReset,
    confirmPasswordReset,
    
    // Profile management
    updateUser,
    updateProfile,
    changePassword,
    markProfileCompleted,
    checkProfileCompletionOnBackend,
    
    // Dashboard & Redirection methods
    getDashboardUrl,
    getRedirectUrlAfterLogin,
    hasCompletedProfile,
    requiresApproval,
    
    // Permission checking
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    isStudent,
    isTeacher,
    isParent,
    isAdmin,
    isAccountant,
    isHeadTeacher,
    isCurriculumCoordinator,
    isLibrarian,
    isCounselor,
    isITSupport,
    isOfficeStaff,
    
    // Finance permissions
    canViewFinance,
    canManageReceipts,
    canManagePayments,
    canViewReports,
    canReconcile,
    canApprovePayments,
    
    // Feature flags
    canExportData,
    canManageStudents,
    canViewStudentFinance,
    canGenerateReports,
    canViewAnalytics,
    canManageUsers,
    canManageSystem,
    canManageCurriculum,
    canManageLibrary,
    canManageCounseling,
    
    // Utility functions
    getUserInitials,
    getFullName,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};