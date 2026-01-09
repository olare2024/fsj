// authAPI.js - FIXED & IMPROVED VERSION
import api from './api.js';

// Built-in error handling utility - ALWAYS RETURNS, NEVER THROWS
const handleAPIError = (error, defaultMessage = 'An error occurred') => {
  console.error('🔴 API Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
    // Handle specific status codes
    if (status === 401) {
      return {
        success: false,
        message: 'Authentication failed. Please check your credentials.',
        status: 401,
        data: serverError,
        requiresReauth: true
      };
    }
    
    if (status === 400) {
      return {
        success: false,
        message: serverError.detail || serverError.message || serverError.error || defaultMessage,
        errors: serverError.errors || serverError.details || serverError,
        status: status,
        data: serverError
      };
    }
    
    // Handle Django error formats
    if (typeof serverError === 'object') {
      return {
        success: false,
        message: serverError.detail || serverError.message || serverError.error || defaultMessage,
        errors: serverError.errors || serverError.details,
        status: status,
        data: serverError
      };
    } else if (typeof serverError === 'string') {
      return {
        success: false,
        message: serverError,
        status: status
      };
    }
  } else if (error.request) {
    return {
      success: false,
      message: 'Network error: Unable to connect to server',
      status: 0
    };
  } else {
    return {
      success: false,
      message: error.message || defaultMessage
    };
  }
  
  return {
    success: false,
    message: defaultMessage
  };
};

const authAPI = {
  // ==================== AUTHENTICATION ENDPOINTS ====================
  
  /**
   * User Login - POST to /api/v1/auth/login/
   * FIXED: Returns object, never throws
   */
  login: async (credentials) => {
    try {
      console.log('🔄 API Request: POST /auth/login/', { 
        email: credentials.email, 
        hasPassword: !!credentials.password 
      });
      
      const response = await api.post('/auth/login/', credentials);
      console.log('✅ Login API Response:', response.data);
      
      const responseData = response.data;
      
      // Handle successful login
      if (response.status >= 200 && response.status < 300) {
        console.log('✅ Login successful with status:', response.status);
        
        // Store user data
        if (responseData.user) {
          localStorage.setItem('user_data', JSON.stringify(responseData.user));
          console.log('💾 User data stored:', responseData.user.email);
        }
        
        // Store tokens if available
        if (responseData.tokens) {
          localStorage.setItem('access_token', responseData.tokens.access);
          localStorage.setItem('refresh_token', responseData.tokens.refresh);
          console.log('🔑 Tokens stored');
        }
        
        return {
          success: true,
          status: 'success',
          message: responseData.message || 'Login successful',
          user: responseData.user,
          tokens: responseData.tokens,
          redirect_url: responseData.redirect_url || '/dashboard',
          requires_2fa: responseData.requires_2fa || false,
          session_token: responseData.session_token,
          user_id: responseData.user_id,
          data: responseData
        };
      }
      
      // Handle error response
      console.error('❌ Unexpected login response format:', responseData);
      return {
        success: false,
        message: responseData.detail || responseData.message || 'Login failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Login API error:', error.response?.data || error.message);
      return handleAPIError(error, 'Login failed. Please check your credentials.');
    }
  },

  /**
   * Verify OTP/2FA - POST to /api/v1/auth/verify-otp/
   * FIXED: Returns object, never throws
   */
  verifyOTP: async (otpData) => {
    try {
      console.log('🔄 Verifying OTP:', { 
        email: otpData.email, 
        method: otpData.method,
        otpLength: otpData.otp?.length 
      });
      
      const response = await api.post('/auth/verify-otp/', otpData);
      console.log('✅ OTP verification response:', response.data);
      
      const responseData = response.data;
      
      // Handle successful OTP verification
      if (responseData.status === 'success' || response.status === 200) {
        console.log('✅ OTP verification successful');
        
        // Store user data and tokens
        if (responseData.user) {
          localStorage.setItem('user_data', JSON.stringify(responseData.user));
          console.log('💾 User data stored after OTP verification');
        }
        
        if (responseData.tokens) {
          localStorage.setItem('access_token', responseData.tokens.access);
          localStorage.setItem('refresh_token', responseData.tokens.refresh);
          console.log('🔑 Tokens stored after OTP verification');
        }
        
        return {
          success: true,
          status: 'success',
          message: responseData.message || 'OTP verified successfully',
          user: responseData.user,
          tokens: responseData.tokens,
          redirect_url: responseData.redirect_url,
          data: responseData
        };
      }
      
      // Handle OTP verification failure
      console.error('❌ OTP verification failed:', responseData);
      return {
        success: false,
        message: responseData.detail || responseData.message || 'OTP verification failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ OTP verification error:', error.response?.data || error.message);
      return handleAPIError(error, 'OTP verification failed');
    }
  },

  /**
   * User Registration - POST to /api/v1/auth/register/
   * FIXED: Returns object, never throws
   */
  register: async (userData) => {
    try {
      console.log('🔄 API Request: POST /auth/register/', {
        email: userData.email,
        firstName: userData.first_name,
        role: userData.role
      });
      
      const response = await api.post('/auth/register/', userData);
      console.log('✅ Registration Response:', response.data);
      
      const responseData = response.data;
      
      // Handle successful registration
      if (responseData.status === 'success' || response.status === 201) {
        console.log('✅ Registration successful');
        
        return {
          success: true,
          message: responseData.message || 'Registration successful!',
          user: responseData.user,
          requires_verification: responseData.requires_verification || false,
          data: responseData
        };
      }
      
      // Handle registration error
      console.error('❌ Registration failed:', responseData);
      return {
        success: false,
        message: responseData.detail || responseData.message || 'Registration failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Registration error:', error.response?.data || error.message);
      return handleAPIError(error, 'Registration failed');
    }
  },

  /**
   * User Logout - POST to /api/v1/auth/logout/
   * UPDATED: Accepts logout data for token blacklisting
   */
  logout: async (logoutData = null) => {
    try {
      console.log('🔄 API Request: POST /auth/logout/');
      
      // If logoutData is provided, use it (for blacklisting refresh token)
      const data = logoutData ? { refresh: logoutData.refresh } : {};
      
      const response = await api.post('/auth/logout/', data);
      console.log('✅ Logout response:', response.data);
      
      return {
        success: true,
        message: response.data?.message || 'Logged out successfully'
      };
    } catch (error) {
      console.error('❌ Logout API error (ignoring):', error);
      // Return success anyway - we'll clear local storage regardless
      return {
        success: true,
        message: 'Logged out locally'
      };
    } finally {
      // Always clear local storage
      authAPI.clearAuthData();
      console.log('🧹 Auth data cleared from localStorage');
    }
  },

  /**
   * Request Password Reset - POST to /api/v1/auth/password/reset/
   * FIXED: Returns object, never throws
   */
  requestPasswordReset: async (email) => {
    try {
      console.log('🔄 Requesting password reset:', { email });
      const response = await api.post('/auth/password/reset/', { email });
      console.log('✅ Password reset request response:', response.data);
      
      const responseData = response.data;
      
      if (responseData && (responseData.status === 'success' || response.status === 200)) {
        return {
          success: true,
          message: responseData.message || 'Password reset instructions sent!',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.detail || responseData?.message || 'Password reset request failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Password reset request error:', error.response?.data || error.message);
      return handleAPIError(error, 'Password reset request failed');
    }
  },

  /**
   * Confirm Password Reset - POST to /api/v1/auth/password/reset/confirm/
   * FIXED: Returns object, never throws
   */
  confirmPasswordReset: async (resetData) => {
    try {
      console.log('🔄 Confirming password reset');
      const response = await api.post('/auth/password/reset/confirm/', resetData);
      console.log('✅ Password reset confirmation response:', response.data);
      
      const responseData = response.data;
      
      if (responseData && (responseData.status === 'success' || response.status === 200)) {
        return {
          success: true,
          message: responseData.message || 'Password reset successfully!',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.detail || responseData?.message || 'Password reset failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Password reset confirmation error:', error.response?.data || error.message);
      return handleAPIError(error, 'Password reset failed');
    }
  },

  // ==================== USER PROFILE ENDPOINTS ====================
  
  /**
   * Get Current User Profile - GET to /api/v1/auth/me/
   * FIXED: Returns object, never throws
   */
  getCurrentUser: async () => {
    try {
      console.log('🔄 Getting current user profile...');
      
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('🔑 No token found, user is not authenticated');
        return {
          success: false,
          message: 'No authentication token found',
          status: 401,
          requiresLogin: true
        };
      }
      
      const response = await api.get('/auth/me/');
      console.log('✅ Current user response received:', response.data);
      
      const responseData = response.data;
      
      // Extract user from responseData.user or fallback to responseData
      const userData = responseData.user || responseData;
      
      if (userData && (userData.id || userData.email)) {
        localStorage.setItem('user_data', JSON.stringify(userData));
        console.log('💾 User profile stored in localStorage:', userData.email);
        
        return {
          success: true,
          user: userData,
          message: responseData.message || 'User profile fetched successfully',
          data: responseData
        };
      }
      
      console.error('❌ Invalid user data structure:', responseData);
      return {
        success: false,
        message: 'Invalid user data in response',
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Get current user error:', error.response?.data || error.message);
      
      if (error.response?.status === 401) {
        console.log('🔐 Token expired or invalid');
        localStorage.removeItem('access_token');
        return {
          success: false,
          message: 'Authentication expired. Please login again.',
          status: 401,
          requiresReauth: true
        };
      }
      
      if (error.code === 'ECONNABORTED') {
        console.log('⏰ Request timed out');
        return {
          success: false,
          message: 'Request timeout. Please check your connection.'
        };
      }
      
      if (!error.response) {
        console.log('🌐 Network error - server may be down');
        return {
          success: false,
          message: 'Cannot connect to server. Please try again later.'
        };
      }
      
      return handleAPIError(error, 'Failed to get user profile');
    }
  },

  /**
   * Update User Profile - PATCH to /api/v1/auth/profile/
   * FIXED: Returns object, never throws
   */
  updateProfile: async (userData) => {
    try {
      console.log('🔄 Updating user profile:', {
        firstName: userData.first_name,
        lastName: userData.last_name
      });
      
      const response = await api.patch('/auth/profile/', userData);
      console.log('✅ Profile update response:', response.data);
      
      const responseData = response.data;
      
      if (responseData && (responseData.status === 'success' || response.status === 200)) {
        const updatedUserData = responseData.user || responseData;
        authAPI.updateStoredUser(updatedUserData);
        console.log('💾 User profile updated in localStorage');
        
        return {
          success: true,
          message: responseData.message || 'Profile updated successfully!',
          user: updatedUserData,
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.detail || responseData?.message || 'Profile update failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Profile update error:', error.response?.data || error.message);
      return handleAPIError(error, 'Profile update failed');
    }
  },

  /**
   * Change Password - POST to /api/v1/auth/password/change/
   * FIXED: Returns object, never throws
   */
  changePassword: async (passwordData) => {
    try {
      console.log('🔄 Changing password');
      const response = await api.post('/auth/password/change/', passwordData);
      console.log('✅ Password change response:', response.data);
      
      const responseData = response.data;
      
      if (responseData && (responseData.status === 'success' || response.status === 200)) {
        return {
          success: true,
          message: responseData.message || 'Password changed successfully!',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.detail || responseData?.message || 'Password change failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Password change error:', error.response?.data || error.message);
      return handleAPIError(error, 'Password change failed');
    }
  },

  // ==================== TOKEN MANAGEMENT ====================
  
  /**
   * Refresh Token - POST to /api/v1/auth/token/refresh/
   * FIXED: Returns object, never throws
   */
  refreshToken: async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        return {
          success: false,
          message: 'No refresh token available',
          requiresLogin: true
        };
      }

      console.log('🔄 Refreshing token');
      const response = await api.post('/auth/token/refresh/', {
        refresh: refreshToken
      });
      
      console.log('✅ Token refresh response:', response.data);
      
      if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        console.log('🔑 New access token stored');
        
        return {
          success: true,
          message: 'Token refreshed successfully',
          accessToken: response.data.access,
          data: response.data
        };
      }
      
      return {
        success: false,
        message: 'Token refresh failed - no access token in response',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Token refresh error:', error.response?.data || error.message);
      
      // Check if token is blacklisted
      if (error.response?.data?.detail?.includes('blacklisted')) {
        authAPI.clearAuthData();
        return {
          success: false,
          message: 'Token has been blacklisted. Please login again.',
          status: 401,
          requiresReauth: true
        };
      }
      
      return handleAPIError(error, 'Token refresh failed');
    }
  },

  // ==================== TWO-FACTOR AUTHENTICATION ====================
  
  /**
   * Setup 2FA - POST to /api/v1/auth/2fa/setup/
   * FIXED: Returns object, never throws
   */
  setup2FA: async () => {
    try {
      console.log('🔄 Setting up 2FA');
      const response = await api.post('/auth/2fa/setup/');
      console.log('✅ 2FA setup response:', response.data);
      
      return {
        success: true,
        ...response.data
      };
    } catch (error) {
      console.error('❌ 2FA setup error:', error);
      return handleAPIError(error, '2FA setup failed');
    }
  },

  /**
   * Verify 2FA - POST to /api/v1/auth/2fa/verify/
   * FIXED: Returns object, never throws
   */
  verify2FA: async (otp) => {
    try {
      console.log('🔄 Verifying 2FA');
      const response = await api.post('/auth/2fa/verify/', { otp });
      console.log('✅ 2FA verification response:', response.data);
      
      return {
        success: true,
        ...response.data
      };
    } catch (error) {
      console.error('❌ 2FA verification error:', error);
      return handleAPIError(error, '2FA verification failed');
    }
  },

  /**
   * Check 2FA Status - GET to /api/v1/auth/2fa/status/
   * FIXED: Returns object, never throws
   */
  get2FAStatus: async () => {
    try {
      console.log('🔄 Getting 2FA status');
      const response = await api.get('/auth/2fa/status/');
      console.log('✅ 2FA status response:', response.data);
      
      return {
        success: true,
        ...response.data
      };
    } catch (error) {
      console.error('❌ 2FA status error:', error);
      return handleAPIError(error, 'Failed to get 2FA status');
    }
  },

  // ==================== ADDITIONAL METHODS ====================
  
  /**
   * Resend Verification Code
   */
  resendVerification: async (email, purpose = 'login') => {
    try {
      console.log('🔄 Resending verification to:', email);
      const response = await api.post('/auth/resend-verification/', {
        email,
        purpose
      });
      
      console.log('✅ Resend verification response:', response.data);
      
      return {
        success: true,
        message: response.data?.message || 'Verification code sent!',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Resend verification error:', error);
      return handleAPIError(error, 'Failed to resend verification');
    }
  },

  // ==================== UTILITY METHODS ====================

  clearAuthData: () => {
    const items = [
      'access_token',
      'refresh_token', 
      'user_data',
      'last_activity',
      'auth_timestamp'
    ];
    
    items.forEach(item => localStorage.removeItem(item));
    console.log('🧹 Cleared all auth data from localStorage');
  },

  getStoredUser: () => {
    try {
      const userData = localStorage.getItem('user_data');
      if (!userData) {
        console.log('📭 No user data found in localStorage');
        return null;
      }
      
      const user = JSON.parse(userData);
      
      if (user && (user.id || user.email)) {
        console.log('📋 Retrieved stored user:', user.email);
        return user;
      }
      
      console.log('⚠️ Invalid user data in localStorage');
      return null;
    } catch (error) {
      console.error('❌ Error parsing stored user:', error);
      return null;
    }
  },

  updateStoredUser: (userData) => {
    try {
      const currentData = authAPI.getStoredUser() || {};
      const updatedData = { ...currentData, ...userData };
      localStorage.setItem('user_data', JSON.stringify(updatedData));
      console.log('✅ Updated stored user data:', updatedData.email);
      return updatedData;
    } catch (error) {
      console.error('❌ Failed to update stored user data:', error);
      return null;
    }
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('access_token');
    const user = authAPI.getStoredUser();
    
    if (!token || !user) {
      console.log('🔐 Not authenticated - missing token or user data');
      return false;
    }
    
    console.log('🔐 User is authenticated:', user.email);
    return true;
  },

  getToken: () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.log('🔐 No token found');
      return null;
    }
    return token;
  },

  hasRole: (role) => {
    const user = authAPI.getStoredUser();
    const hasRole = user && user.role === role;
    console.log(`👤 Role check: ${role} - ${hasRole ? 'Yes' : 'No'}`);
    return hasRole;
  },

  hasAnyRole: (roles) => {
    const user = authAPI.getStoredUser();
    const hasAnyRole = user && roles.includes(user.role);
    console.log(`👤 Any role check: ${roles} - ${hasAnyRole ? 'Yes' : 'No'}`);
    return hasAnyRole;
  },

  isAdmin: () => {
    return authAPI.hasRole('admin');
  },

  isTeacher: () => {
    return authAPI.hasRole('teacher');
  },

  isStudent: () => {
    return authAPI.hasRole('student');
  },

  isParent: () => {
    return authAPI.hasRole('parent');
  },

  getDisplayName: () => {
    const user = authAPI.getStoredUser();
    if (!user) return 'Guest';
    
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    } else if (user.firstName && user.lastName) {
      return `${user.firstName} ${user.lastName}`;
    }
    
    return user.email || user.username || 'User';
  },

  getUserInitials: () => {
    const user = authAPI.getStoredUser();
    if (!user) return '';
    
    const firstName = user.first_name || user.firstName || '';
    const lastName = user.last_name || user.lastName || '';
    
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  },

  getUserEmail: () => {
    const user = authAPI.getStoredUser();
    return user?.email || '';
  },

  getUserId: () => {
    const user = authAPI.getStoredUser();
    return user?.id || '';
  },

  getDashboardUrl: () => {
    const user = authAPI.getStoredUser();
    return user?.dashboard_url || '/dashboard';
  },

  // Debug method to check stored data
  debugAuthState: () => {
    const user = authAPI.getStoredUser();
    const token = localStorage.getItem('access_token');
    
    return {
      isAuthenticated: authAPI.isAuthenticated(),
      hasToken: !!token,
      hasRefreshToken: !!localStorage.getItem('refresh_token'),
      hasUserData: !!user,
      user: user,
      tokenPreview: token ? token.substring(0, 20) + '...' : null,
      displayName: authAPI.getDisplayName(),
      role: user?.role,
      userId: user?.id,
      dashboardUrl: user?.dashboard_url
    };
  },

  // Health check for auth state
  checkAuthHealth: () => {
    const state = authAPI.debugAuthState();
    
    if (!state.isAuthenticated) {
      return {
        healthy: false,
        message: 'Not authenticated',
        state: state
      };
    }
    
    if (!state.hasToken) {
      return {
        healthy: false,
        message: 'No access token',
        state: state
      };
    }
    
    if (!state.hasUserData) {
      return {
        healthy: false,
        message: 'No user data',
        state: state
      };
    }
    
    return {
      healthy: true,
      message: 'Auth state is healthy',
      state: state
    };
  },

  // Test endpoint connectivity
  testEndpoints: async () => {
    const endpoints = [
      { path: '/auth/login/', method: 'OPTIONS' },
      { path: '/auth/register/', method: 'OPTIONS' },
      { path: '/auth/me/', method: 'GET' },
      { path: '/auth/token/refresh/', method: 'OPTIONS' },
    ];
    
    const results = [];
    
    for (const endpoint of endpoints) {
      try {
        console.log(`Testing ${endpoint.method} ${endpoint.path}`);
        const response = await api({
          method: endpoint.method,
          url: endpoint.path,
          timeout: 5000
        });
        results.push({
          endpoint: endpoint.path,
          status: response.status,
          success: true
        });
      } catch (error) {
        results.push({
          endpoint: endpoint.path,
          status: error.response?.status || 0,
          success: false,
          error: error.message
        });
      }
    }
    
    console.log('🔍 Endpoint Test Results:', results);
    return results;
  },

  // Compatibility layer to ensure consistent response format
  ensureResponseFormat: (response) => {
    return {
      success: response.success || false,
      message: response.message || '',
      status: response.status || (response.success ? 'success' : 'error'),
      data: response.data || response,
      ...response
    };
  },

  // ==================== PERMISSIONS METHODS ====================

  /**
   * Get user permissions - GET to /api/v1/auth/permissions/
   * Returns permissions array or empty array on failure
   */
  getPermissions: async () => {
    try {
      console.log('🔄 Fetching user permissions...');
      const response = await api.get('/auth/permissions/');
      console.log('✅ Permissions response:', response.data);
      
      return {
        success: true,
        permissions: response.data.permissions || response.data || [],
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error fetching permissions:', error.response?.data || error.message);
      
      // Don't return failure - just return empty permissions to avoid breaking the UI
      return {
        success: true,
        permissions: [],
        message: 'Using default permissions',
        error: error.message
      };
    }
  },

  /**
   * Get user with permissions - Enhanced version of getCurrentUser
   * Combines user data with permissions
   */
  getUserWithPermissions: async () => {
    try {
      // First get user data
      const userResponse = await authAPI.getCurrentUser();
      
      if (!userResponse.success) {
        return userResponse;
      }
      
      // Then fetch permissions separately if not included
      if (!userResponse.user.permissions) {
        const permResponse = await authAPI.getPermissions();
        userResponse.user.permissions = permResponse.permissions || [];
        userResponse.permissions = permResponse.permissions || [];
      } else {
        userResponse.permissions = userResponse.user.permissions;
      }
      
      return userResponse;
    } catch (error) {
      console.error('❌ Error in getUserWithPermissions:', error);
      return {
        success: false,
        message: 'Failed to get user with permissions',
        user: null,
        permissions: []
      };
    }
  },

  /**
   * Check if user has specific permission
   * @param {string|Array} permission - Permission string or array of permissions
   * @returns {Promise<boolean>}
   */
  hasPermission: async (permission) => {
    try {
      const permissionsResponse = await authAPI.getPermissions();
      const permissions = permissionsResponse.permissions || [];
      
      if (Array.isArray(permission)) {
        // Check if user has ANY of the permissions in the array
        return permission.some(perm => permissions.includes(perm));
      } else {
        // Check for single permission
        return permissions.includes(permission);
      }
    } catch (error) {
      console.error('❌ Error checking permission:', error);
      return false;
    }
  },

  /**
   * Check if user has all specified permissions
   * @param {Array} permissions - Array of required permissions
   * @returns {Promise<boolean>}
   */
  hasAllPermissions: async (permissions) => {
    try {
      const permissionsResponse = await authAPI.getPermissions();
      const userPermissions = permissionsResponse.permissions || [];
      
      return permissions.every(perm => userPermissions.includes(perm));
    } catch (error) {
      console.error('❌ Error checking all permissions:', error);
      return false;
    }
  },

  // ==================== SESSION MANAGEMENT ====================

  /**
   * Validate current session
   * Checks if token is valid and user is properly authenticated
   */
  validateSession: async () => {
    try {
      if (!authAPI.isAuthenticated()) {
        return {
          valid: false,
          message: 'Not authenticated',
          requiresLogin: true
        };
      }

      // Try to get current user to validate token
      const userResponse = await authAPI.getCurrentUser();
      
      if (userResponse.success) {
        return {
          valid: true,
          message: 'Session is valid',
          user: userResponse.user
        };
      }
      
      // If token is expired, try to refresh it
      if (userResponse.status === 401 || userResponse.requiresReauth) {
        console.log('🔑 Token expired, attempting refresh...');
        const refreshResponse = await authAPI.refreshToken();
        
        if (refreshResponse.success) {
          // Retry getting user with new token
          const retryUserResponse = await authAPI.getCurrentUser();
          
          if (retryUserResponse.success) {
            return {
              valid: true,
              message: 'Session refreshed and valid',
              user: retryUserResponse.user,
              refreshed: true
            };
          }
        }
        
        return {
          valid: false,
          message: 'Session expired, please login again',
          requiresLogin: true
        };
      }
      
      return {
        valid: false,
        message: userResponse.message || 'Session validation failed',
        requiresLogin: true
      };
    } catch (error) {
      console.error('❌ Session validation error:', error);
      return {
        valid: false,
        message: 'Session validation failed',
        requiresLogin: true
      };
    }
  },

  /**
   * Initialize and check authentication state
   * Useful for app initialization
   */
  initializeAuth: async () => {
    console.log('🚀 Initializing authentication...');
    
    const session = await authAPI.validateSession();
    
    if (session.valid) {
      console.log('✅ Authentication initialized successfully');
      return {
        success: true,
        authenticated: true,
        user: session.user,
        refreshed: session.refreshed || false,
        message: session.message
      };
    }
    
    console.log('⚠️ Authentication initialization failed');
    return {
      success: false,
      authenticated: false,
      requiresLogin: true,
      message: session.message
    };
  }
};

export default authAPI;