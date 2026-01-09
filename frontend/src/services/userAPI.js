// userAPI.js - COMPLETE UPDATED VERSION FOR DJANGO BACKEND
import api from './api.js';

// Enhanced error handling utility
const handleUserAPIError = (error, operation = 'operation') => {
  console.error(`❌ User API Error (${operation}):`, error.response?.data || error.message);
  
  if (error.response?.status === 401) {
    // Auto-logout on unauthorized
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }
  
  return {
    success: false,
    error: {
      message: error.response?.data?.message || error.response?.data?.detail || error.response?.data?.error || error.message,
      details: error.response?.data?.errors || error.response?.data,
      status: error.response?.status,
      code: error.response?.data?.code
    }
  };
};

const userAPI = {
  // ==================== USER PROFILE & MANAGEMENT ====================

  /**
   * Get current user profile - GET /api/v1/auth/me/
   */
  getCurrentUser: async () => {
    try {
      console.log('🔄 Fetching current user profile');
      const response = await api.get('/auth/me/');
      console.log('✅ Current user profile:', response.data);
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getCurrentUser');
    }
  },

  /**
   * Get user profile - GET /api/v1/auth/profile/
   */
  getProfile: async () => {
    try {
      console.log('🔄 Fetching user profile');
      const response = await api.get('/auth/profile/');
      console.log('✅ User profile fetched:', response.data);
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getProfile');
    }
  },

  /**
   * Update user profile - PUT/PATCH /api/v1/auth/profile/
   */
  updateProfile: async (profileData) => {
    try {
      console.log('🔄 Updating user profile:', profileData);
      const response = await api.patch('/auth/profile/', profileData);
      console.log('✅ Profile updated successfully:', response.data);
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        message: response.data.message || 'Profile updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'updateProfile');
    }
  },

  /**
   * Get user activity - GET /api/v1/auth/activity/
   */
  getActivity: async () => {
    try {
      console.log('🔄 Fetching user activity');
      const response = await api.get('/auth/activity/');
      console.log('✅ User activity fetched');
      
      return {
        success: true,
        data: response.data,
        activity: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getActivity');
    }
  },

  /**
   * Change password - POST /api/v1/auth/password/change/
   */
  changePassword: async (passwordData) => {
    try {
      console.log('🔄 Changing password');
      const response = await api.post('/auth/password/change/', passwordData);
      console.log('✅ Password changed successfully');
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'Password changed successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'changePassword');
    }
  },

  // ==================== PROFILE COMPLETION & ANALYTICS ====================

  /**
   * Get profile completion status
   */
  getProfileCompletion: async () => {
    try {
      console.log('🔄 Calculating profile completion');
      const response = await api.get('/auth/profile/');
      const userData = response.data;
      
      // Define required fields for each role
      const requiredFields = {
        student: ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'grade_level'],
        teacher: ['first_name', 'last_name', 'email', 'phone_number', 'subject_specialization', 'qualifications'],
        parent: ['first_name', 'last_name', 'email', 'phone_number', 'emergency_contact'],
        admin: ['first_name', 'last_name', 'email', 'phone_number']
      };
      
      const userRole = userData.role || 'student';
      const fieldsToCheck = requiredFields[userRole] || requiredFields.student;
      
      // Calculate completion
      let completedFields = 0;
      const missingFields = [];
      
      fieldsToCheck.forEach(field => {
        const value = userData[field];
        if (value !== null && value !== undefined && value.toString().trim() !== '') {
          completedFields++;
        } else {
          missingFields.push(field);
        }
      });
      
      const completionPercentage = Math.round((completedFields / fieldsToCheck.length) * 100);
      const isComplete = completionPercentage >= 90;
      
      const completionData = {
        percentage: completionPercentage,
        completed: isComplete,
        completedFields,
        totalFields: fieldsToCheck.length,
        missingFields,
        nextSteps: missingFields.map(field => `Please provide your ${field.replace(/_/g, ' ')}`),
        role: userRole
      };

      return {
        success: true,
        data: completionData,
        completion: completionData,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getProfileCompletion');
    }
  },

  // ==================== ADMIN USER MANAGEMENT ====================

  /**
   * Get all users (Admin) - GET /api/v1/auth/users/
   */
  getUsers: async (params = {}) => {
    try {
      console.log('🔄 Fetching users list', params);
      const response = await api.get('/auth/users/', { params });
      console.log('✅ Users list fetched:', response.data.results?.length || 0, 'users');
      
      return {
        success: true,
        data: response.data,
        users: response.data.results || response.data,
        pagination: {
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
          page: response.data.page,
          totalPages: response.data.total_pages
        },
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getUsers');
    }
  },

  /**
   * Get user by ID (Admin) - GET /api/v1/auth/users/{id}/
   */
  getUserById: async (userId) => {
    try {
      console.log('🔄 Fetching user by ID:', userId);
      const response = await api.get(`/auth/users/${userId}/`);
      console.log('✅ User fetched:', response.data.email);
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getUserById');
    }
  },

  /**
   * Create user (Admin) - POST /api/v1/auth/users/
   */
  createUser: async (userData) => {
    try {
      console.log('🔄 Creating new user:', userData.email);
      const response = await api.post('/auth/users/', userData);
      console.log('✅ User created successfully:', response.data.email);
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        message: response.data.message || 'User created successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'createUser');
    }
  },

  /**
   * Update user (Admin) - PATCH /api/v1/auth/users/{id}/
   */
  updateUser: async (userId, userData) => {
    try {
      console.log('🔄 Updating user:', userId);
      const response = await api.patch(`/auth/users/${userId}/`, userData);
      console.log('✅ User updated successfully');
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        message: response.data.message || 'User updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'updateUser');
    }
  },

  /**
   * Delete user (Admin) - DELETE /api/v1/auth/users/{id}/
   */
  deleteUser: async (userId) => {
    try {
      console.log('🔄 Deleting user:', userId);
      const response = await api.delete(`/auth/users/${userId}/`);
      console.log('✅ User deleted successfully');
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'User deleted successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'deleteUser');
    }
  },

  /**
   * Bulk import users (Admin) - POST /api/v1/auth/admin/bulk-import/
   */
  bulkImportUsers: async (importData) => {
    try {
      console.log('🔄 Bulk importing users');
      const response = await api.post('/auth/admin/bulk-import/', importData);
      console.log('✅ Users bulk import completed');
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'Users imported successfully',
        imported: response.data.imported_count,
        failed: response.data.failed_count,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'bulkImportUsers');
    }
  },

  // ==================== ADMIN STATISTICS & DASHBOARD ====================

  /**
   * Get user statistics (Admin) - GET /api/v1/auth/admin/stats/
   */
  getUserStatistics: async () => {
    try {
      console.log('🔄 Fetching user statistics');
      const response = await api.get('/auth/admin/stats/');
      console.log('✅ User statistics fetched');
      
      return {
        success: true,
        data: response.data,
        statistics: response.data,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getUserStatistics');
    }
  },

  /**
   * Get teacher dashboard (Admin) - GET /api/v1/auth/admin/teacher-dashboard/
   */
  getTeacherDashboard: async () => {
    try {
      console.log('🔄 Fetching teacher dashboard');
      const response = await api.get('/auth/admin/teacher-dashboard/');
      console.log('✅ Teacher dashboard fetched');
      
      return {
        success: true,
        data: response.data,
        dashboard: response.data,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'getTeacherDashboard');
    }
  },

  // ==================== AVATAR MANAGEMENT ====================

  /**
   * Upload user avatar - PATCH /api/v1/auth/profile/
   */
  uploadAvatar: async (avatarFile) => {
    try {
      console.log('🔄 Uploading avatar');
      const formData = new FormData();
      formData.append('avatar', avatarFile);
      
      const response = await api.patch('/auth/profile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('✅ Avatar uploaded successfully');
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        message: response.data.message || 'Avatar updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'uploadAvatar');
    }
  },

  /**
   * Remove user avatar - PATCH /api/v1/auth/profile/
   */
  removeAvatar: async () => {
    try {
      console.log('🔄 Removing avatar');
      const response = await api.patch('/auth/profile/', { avatar: null });
      console.log('✅ Avatar removed successfully');
      
      return {
        success: true,
        data: response.data,
        user: response.data,
        message: response.data.message || 'Avatar removed successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'removeAvatar');
    }
  },

  // ==================== SEARCH & FILTERING ====================

  /**
   * Search users - GET /api/v1/auth/users/ with search params
   */
  searchUsers: async (query, filters = {}) => {
    try {
      console.log('🔄 Searching users:', { query, filters });
      
      const params = {
        search: query,
        ...filters
      };
      
      const response = await api.get('/auth/users/', { params });
      console.log('✅ Search completed:', response.data.results?.length || 0, 'results');
      
      return {
        success: true,
        data: response.data,
        results: response.data.results || response.data,
        query: query,
        filters: filters,
        count: response.data.count,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'searchUsers');
    }
  },

  /**
   * Advanced user search with multiple criteria
   */
  advancedSearch: async (criteria = {}) => {
    try {
      console.log('🔄 Advanced user search:', criteria);
      
      const response = await api.get('/auth/users/', { params: criteria });
      console.log('✅ Advanced search completed:', response.data.results?.length || 0, 'results');
      
      return {
        success: true,
        data: response.data,
        results: response.data.results || response.data,
        criteria: criteria,
        count: response.data.count,
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'advancedSearch');
    }
  },

  // ==================== USER STATUS & ACTIVATION ====================

  /**
   * Deactivate user account (Admin) - POST /api/v1/auth/users/{id}/deactivate/
   */
  deactivateUser: async (userId, reason = 'No reason provided') => {
    try {
      console.log('🔄 Deactivating user:', userId);
      const response = await api.post(`/auth/users/${userId}/deactivate/`, { reason });
      console.log('✅ User deactivated successfully');
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'User deactivated successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'deactivateUser');
    }
  },

  /**
   * Activate user account (Admin) - POST /api/v1/auth/users/{id}/activate/
   */
  activateUser: async (userId) => {
    try {
      console.log('🔄 Activating user:', userId);
      const response = await api.post(`/auth/users/${userId}/activate/`);
      console.log('✅ User activated successfully');
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'User activated successfully',
        status: response.status
      };
    } catch (error) {
      return handleUserAPIError(error, 'activateUser');
    }
  },

  /**
   * Bulk deactivate users (Admin)
   */
  bulkDeactivateUsers: async (userIds, reason = 'Bulk deactivation') => {
    try {
      console.log('🔄 Bulk deactivating users:', userIds.length, 'users');
      
      const promises = userIds.map(userId => 
        api.post(`/auth/users/${userId}/deactivate/`, { reason })
      );
      
      const results = await Promise.allSettled(promises);
      
      const successful = results.filter(result => result.status === 'fulfilled').length;
      const failed = results.filter(result => result.status === 'rejected').length;
      
      console.log('✅ Bulk deactivation completed:', successful, 'successful,', failed, 'failed');
      
      return {
        success: true,
        data: { successful, failed },
        message: `Bulk deactivation completed: ${successful} successful, ${failed} failed`,
        status: 200
      };
    } catch (error) {
      return handleUserAPIError(error, 'bulkDeactivateUsers');
    }
  },

  // ==================== UTILITY METHODS ====================

  /**
   * Check if current user has admin privileges
   */
  isAdmin: () => {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    return userData.role === 'admin' || userData.is_staff || userData.is_superuser;
  },

  /**
   * Check if current user has specific role
   */
  hasRole: (role) => {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    return userData.role === role;
  },

  /**
   * Get current user role
   */
  getCurrentUserRole: () => {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    return userData.role;
  },

  /**
   * Get user display name
   */
  getDisplayName: () => {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    
    if (userData.first_name && userData.last_name) {
      return `${userData.first_name} ${userData.last_name}`;
    } else if (userData.firstName && userData.lastName) {
      return `${userData.firstName} ${userData.lastName}`;
    }
    
    return userData.email || userData.username || 'User';
  },

  /**
   * Get user initials for avatar
   */
  getUserInitials: () => {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    
    const firstName = userData.first_name || userData.firstName || '';
    const lastName = userData.last_name || userData.lastName || '';
    
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  },

  /**
   * Debug method to check user API state
   */
  debugUserState: () => {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    
    return {
      hasUserData: !!userData && Object.keys(userData).length > 0,
      user: userData,
      role: userData.role,
      email: userData.email,
      isAdmin: userAPI.isAdmin(),
      displayName: userAPI.getDisplayName(),
      initials: userAPI.getUserInitials()
    };
  }
};

export default userAPI;