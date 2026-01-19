// authAPI.js - UPDATED TO MATCH DJANGO ENDPOINTS
import api from './api.js';

// Built-in error handling utility
const handleAPIError = (error, defaultMessage = 'An error occurred') => {
  console.error('🔴 API Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
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
  
  login: async (credentials) => {
    try {
      console.log('🔄 API Request: POST /auth/login/', { 
        email: credentials.email, 
        hasPassword: !!credentials.password 
      });
      
      const response = await api.post('/auth/login/', credentials);
      console.log('✅ Login API Response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData.success === true) {
        console.log('✅ Login successful');
        
        if (responseData.user) {
          localStorage.setItem('user_data', JSON.stringify(responseData.user));
          console.log('💾 User data stored:', responseData.user.email);
        }
        
        if (responseData.tokens) {
          localStorage.setItem('access_token', responseData.tokens.access);
          localStorage.setItem('refresh_token', responseData.tokens.refresh);
          console.log('🔑 Tokens stored');
        }
        
        return {
          success: true,
          message: responseData.message || 'Login successful',
          user: responseData.user,
          tokens: responseData.tokens,
          redirect_url: responseData.redirect_url || '/dashboard',
          requires_2fa: responseData.requires_2fa || false,
          session_token: responseData.session_token,
          user_id: responseData.user?.id,
          data: responseData
        };
      }
      
      console.error('❌ Login failed:', responseData);
      return {
        success: false,
        message: responseData.message || responseData.detail || 'Login failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Login API error:', error.response?.data || error.message);
      return handleAPIError(error, 'Login failed. Please check your credentials.');
    }
  },

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
      
      // Check for success boolean
      if (responseData.success === true) {
        console.log('✅ OTP verification successful');
        
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
          message: responseData.message || 'OTP verified successfully',
          user: responseData.user,
          tokens: responseData.tokens,
          redirect_url: responseData.redirect_url,
          data: responseData
        };
      }
      
      console.error('❌ OTP verification failed:', responseData);
      return {
        success: false,
        message: responseData.message || responseData.detail || 'OTP verification failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ OTP verification error:', error.response?.data || error.message);
      return handleAPIError(error, 'OTP verification failed');
    }
  },

  // IMPORTANT FIX: Add this method that matches Django endpoint
  verifyLoginOTP: async (otpData) => {
    try {
      console.log('🔄 Verifying Login OTP:', { 
        email: otpData.email,
        otp: otpData.otp,
        method: otpData.method,
        session_token: otpData.session_token
      });
      
      const response = await api.post('/auth/verify-otp/', {
        otp: otpData.otp,
        session_token: otpData.session_token,
        email: otpData.email
      });
      
      console.log('✅ Login OTP verification response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData.success === true) {
        console.log('✅ Login OTP verification successful');
        
        if (responseData.user) {
          localStorage.setItem('user_data', JSON.stringify(responseData.user));
          console.log('💾 User data stored after login OTP verification');
        }
        
        if (responseData.tokens) {
          localStorage.setItem('access_token', responseData.tokens.access);
          localStorage.setItem('refresh_token', responseData.tokens.refresh);
          console.log('🔑 Tokens stored after login OTP verification');
        }
        
        return {
          success: true,
          message: responseData.message || 'Login OTP verified successfully',
          user: responseData.user,
          tokens: responseData.tokens,
          redirect_url: responseData.redirect_url,
          data: responseData
        };
      }
      
      console.error('❌ Login OTP verification failed:', responseData);
      return {
        success: false,
        message: responseData.message || responseData.detail || 'Login OTP verification failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Login OTP verification error:', error.response?.data || error.message);
      return handleAPIError(error, 'Login OTP verification failed');
    }
  },

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
      
      // Check for success boolean
      if (responseData.success === true) {
        console.log('✅ Registration successful');
        
        return {
          success: true,
          message: responseData.message || 'Registration successful!',
          user: responseData.user,
          requires_verification: responseData.requires_verification || false,
          data: responseData
        };
      }
      
      console.error('❌ Registration failed:', responseData);
      return {
        success: false,
        message: responseData.message || responseData.detail || 'Registration failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Registration error:', error.response?.data || error.message);
      return handleAPIError(error, 'Registration failed');
    }
  },

  logout: async (logoutData = null) => {
    try {
      console.log('🔄 API Request: POST /auth/logout/');
      
      const data = logoutData ? { refresh: logoutData.refresh } : {};
      
      const response = await api.post('/auth/logout/', data);
      console.log('✅ Logout response:', response.data);
      
      // Check for success boolean
      if (response.data.success === true) {
        return {
          success: true,
          message: response.data.message || 'Logged out successfully'
        };
      }
      
      return {
        success: true, // Still return true for logout even if API fails
        message: response.data?.message || 'Logged out locally'
      };
    } catch (error) {
      console.error('❌ Logout API error (ignoring):', error);
      return {
        success: true, // Always return success for logout
        message: 'Logged out locally'
      };
    } finally {
      authAPI.clearAuthData();
      console.log('🧹 Auth data cleared from localStorage');
    }
  },

  requestPasswordReset: async (email) => {
    try {
      console.log('🔄 Requesting password reset:', { email });
      const response = await api.post('/auth/password/reset/', { email });
      console.log('✅ Password reset request response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData && responseData.success === true) {
        return {
          success: true,
          message: responseData.message || 'Password reset instructions sent!',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.message || responseData?.detail || 'Password reset request failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Password reset request error:', error.response?.data || error.message);
      return handleAPIError(error, 'Password reset request failed');
    }
  },

  confirmPasswordReset: async (resetData) => {
    try {
      console.log('🔄 Confirming password reset');
      const response = await api.post('/auth/password/reset/confirm/', resetData);
      console.log('✅ Password reset confirmation response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData && responseData.success === true) {
        return {
          success: true,
          message: responseData.message || 'Password reset successfully!',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.message || responseData?.detail || 'Password reset failed',
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
   */
  getCurrentUser: async () => {
    try {
      console.log('🔄 Getting current user profile from /auth/me/...');
      
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
      
      // Handle both formats: {success: true, user: {...}} or direct user object
      if (responseData.success === true && responseData.user) {
        const userData = responseData.user;
        localStorage.setItem('user_data', JSON.stringify(userData));
        console.log('💾 User profile stored in localStorage:', userData.email);
        
        return {
          success: true,
          user: userData,
          message: responseData.message || 'User profile fetched successfully',
          data: responseData
        };
      } else if (responseData.email) {
        // Direct user object
        localStorage.setItem('user_data', JSON.stringify(responseData));
        console.log('💾 User profile stored in localStorage:', responseData.email);
        
        return {
          success: true,
          user: responseData,
          message: 'User profile fetched successfully',
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
   * Update User Profile - PATCH to /api/v1/auth/me/
   */
  updateProfile: async (userData) => {
    try {
      console.log('🔄 Updating user profile via PATCH /auth/me/', {
        firstName: userData.first_name,
        lastName: userData.last_name,
        phoneNumber: userData.phone_number
      });
      
      const response = await api.patch('/auth/me/', userData);
      console.log('✅ Profile update response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData && responseData.success === true) {
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
        message: responseData?.message || responseData?.detail || 'Profile update failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Profile update error:', error.response?.data || error.message);
      return handleAPIError(error, 'Profile update failed');
    }
  },

  /**
   * Change Password - POST to /api/v1/auth/me/change-password/
   */
  changePassword: async (passwordData) => {
    try {
      console.log('🔄 Changing password via /auth/me/change-password/');
      const response = await api.post('/auth/me/change-password/', passwordData);
      console.log('✅ Password change response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData && responseData.success === true) {
        return {
          success: true,
          message: responseData.message || 'Password changed successfully!',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.message || responseData?.detail || 'Password change failed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Password change error:', error.response?.data || error.message);
      return handleAPIError(error, 'Password change failed');
    }
  },

  // ==================== TOKEN MANAGEMENT ====================
  
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

      console.log('🔄 Refreshing token via /auth/token/refresh/');
      const response = await api.post('/auth/token/refresh/', {
        refresh: refreshToken
      });
      
      console.log('✅ Token refresh response:', response.data);
      
      // Django SimpleJWT returns {access: "...", refresh: "..."} directly
      if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        
        // Update refresh token if new one is provided
        if (response.data.refresh) {
          localStorage.setItem('refresh_token', response.data.refresh);
        }
        
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

  // ==================== PROFILE COMPLETION ====================
  
  /**
   * Get Profile Completion Status - GET to /api/v1/auth/profile/completion-status/
   */
  getProfileCompletion: async () => {
    try {
      console.log('🔄 Getting profile completion status via /auth/profile/completion-status/');
      const response = await api.get('/auth/profile/completion-status/');
      console.log('✅ Profile completion response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData && responseData.success === true) {
        return {
          success: true,
          completion_percentage: responseData.completion_percentage || 0,
          missing_fields: responseData.missing_fields || [],
          is_completed: responseData.is_completed || false,
          message: responseData.message || 'Profile completion status fetched',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.message || responseData?.detail || 'Failed to get profile completion status',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Profile completion error:', error.response?.data || error.message);
      return handleAPIError(error, 'Failed to get profile completion status');
    }
  },

  /**
   * Mark Profile as Completed
   */
  markProfileCompleted: async () => {
    try {
      console.log('🔄 Marking profile as completed via POST /auth/profile/mark-completed/');
      
      const response = await api.post('/auth/profile/mark-completed/');
      
      console.log('✅ Profile marked as completed:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData && responseData.success === true) {
        const updatedUserData = responseData.user || responseData;
        authAPI.updateStoredUser(updatedUserData);
        
        return {
          success: true,
          message: responseData.message || 'Profile marked as completed!',
          user: updatedUserData,
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData?.message || responseData?.detail || 'Failed to mark profile as completed',
        status: response.status,
        data: responseData
      };
      
    } catch (error) {
      console.error('❌ Mark profile completed error:', error.response?.data || error.message);
      return handleAPIError(error, 'Failed to mark profile as completed');
    }
  },

  // ==================== ADDITIONAL METHODS ====================
  
  resendOTP: async (email, purpose = 'login') => {
    try {
      console.log('🔄 Resending verification to:', email, 'purpose:', purpose);
      
      let endpoint, data;
      
      if (purpose === 'login') {
        endpoint = '/auth/resend-otp/';
        data = { email };
      } else {
        endpoint = '/auth/resend-verification/';
        data = { email, purpose };
      }
      
      const response = await api.post(endpoint, data);
      
      console.log('✅ Resend response:', response.data);
      
      const responseData = response.data;
      
      // Check for success boolean
      if (responseData.success === true) {
        return {
          success: true,
          message: responseData.message || 'Verification code sent!',
          data: responseData
        };
      }
      
      return {
        success: false,
        message: responseData.message || 'Failed to resend verification',
        data: responseData
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
    if (!user) return '/dashboard';
    
    // Map Django role to dashboard URL - updated to match your routes
    const dashboardMap = {
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
      'office_staff': '/staff/staff-portal'
    };
    
    return dashboardMap[user.role] || '/dashboard';
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
      dashboardUrl: authAPI.getDashboardUrl()
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
      { path: '/auth/login/', method: 'POST', data: { email: 'test@example.com', password: 'test123' } },
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
          data: endpoint.data,
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

  // Test login directly
  testLogin: async (email = 'test@delvok.ac.ke', password = 'Password123!') => {
    try {
      console.log('🧪 Testing login with:', email);
      
      const result = await authAPI.login({ email, password });
      console.log('🧪 Login test result:', result);
      
      return result;
    } catch (error) {
      console.error('🧪 Login test error:', error);
      return {
        success: false,
        message: 'Login test failed',
        error: error.message
      };
    }
  }
};

export default authAPI;