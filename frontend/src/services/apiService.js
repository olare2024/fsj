// src/services/apiService.js - 统一的API服务文件
import api from './api';

// Enhanced error handling
const handleError = (error, operation = 'operation', context = {}) => {
  console.error(`❌ API Error (${operation}):`, {
    error: error.response?.data || error.message,
    status: error.response?.status,
    url: error.config?.url,
    ...context
  });
  
  // Auto-logout on 401 Unauthorized
  if (error.response?.status === 401) {
    console.warn('🔐 Authentication expired, redirecting to login');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    window.location.href = '/login?session=expired';
    return null;
  }
  
  // Handle 404 specifically
  if (error.response?.status === 404) {
    console.warn(`🔍 Endpoint not found: ${error.config?.url}`);
    return {
      success: false,
      error: 'Endpoint not found',
      message: 'The requested resource was not found',
      status: 404
    };
  }
  
  return {
    success: false,
    error: error.response?.data || error.message,
    message: error.response?.data?.message || error.response?.data?.detail || `Failed to ${operation}`,
    status: error.response?.status,
    code: error.response?.data?.code
  };
};

// Success response wrapper
const wrapSuccess = (data, message = 'Operation completed successfully') => ({
  success: true,
  data,
  message,
  status: 200
});

// Try multiple endpoints
const tryEndpoints = async (endpoints, config = {}) => {
  for (const endpoint of endpoints) {
    try {
      console.log(`🔄 Trying endpoint: ${endpoint}`);
      const response = await api.get(endpoint, config);
      console.log(`✅ Success from endpoint: ${endpoint}`);
      return {
        success: true,
        data: response.data,
        endpoint,
        status: response.status
      };
    } catch (error) {
      console.warn(`⚠️ Endpoint failed: ${endpoint}`, error.message);
      continue;
    }
  }
  return {
    success: false,
    error: 'All endpoints failed',
    message: 'Could not reach any available endpoint'
  };
};

const apiService = {
  // ==================== USER AUTHENTICATION ====================
  
  /**
   * Get current user info
   */
  getCurrentUser: async () => {
    try {
      console.log('🔄 Getting current user from /auth/me/');
      
      const response = await api.get('/auth/me/');
      console.log('✅ Current user data:', response.data);
      
      return wrapSuccess(response.data, 'User data fetched successfully');
    } catch (error) {
      return handleError(error, 'getCurrentUser');
    }
  },

  /**
   * Update user profile
   */
  updateProfile: async (profileData) => {
    try {
      console.log('🔄 Updating user profile');
      
      const response = await api.patch('/auth/profile/', profileData);
      console.log('✅ Profile updated successfully');
      
      return wrapSuccess(response.data, 'Profile updated successfully');
    } catch (error) {
      return handleError(error, 'updateProfile');
    }
  },

  /**
   * Get user activity history
   */
  getUserActivity: async () => {
    try {
      console.log('🔄 Getting user activity');
      
      const response = await api.get('/auth/activity/');
      console.log('✅ User activity fetched');
      
      return wrapSuccess(response.data, 'Activity data fetched successfully');
    } catch (error) {
      return handleError(error, 'getUserActivity');
    }
  },

  // ==================== DASHBOARD DATA ====================

  /**
   * Get dashboard data (intelligent endpoint detection)
   */
  getDashboardData: async () => {
    try {
      console.log('🔄 Fetching dashboard data');
      
      // Try multiple endpoints
      const endpoints = [
        '/auth/me/',  // First try /auth/me/ endpoint
        '/auth/users/dashboard/',  // Then try the expected endpoint
        '/auth/users/me/',  // Alternative endpoint
        '/dashboard/',  // Root dashboard endpoint
        '/api/v1/dashboard/'  // Full path endpoint
      ];
      
      const result = await tryEndpoints(endpoints);
      
      if (result.success) {
        console.log('✅ Dashboard data fetched from:', result.endpoint);
        
        // Enhance data with role-specific info
        const enhancedData = apiService.enhanceDashboardData(result.data);
        
        return {
          success: true,
          data: enhancedData,
          message: 'Dashboard data fetched successfully'
        };
      }
      
      // If all endpoints fail, create fallback data
      console.warn('⚠️ No dashboard endpoints available, creating fallback data');
      const fallbackData = await apiService.createFallbackDashboardData();
      
      return {
        success: true,
        data: fallbackData,
        message: 'Using fallback dashboard data',
        isFallback: true
      };
    } catch (error) {
      return handleError(error, 'getDashboardData');
    }
  },

  /**
   * Get role-specific dashboard
   */
  getRoleDashboard: async () => {
    try {
      // First get current user to determine role
      const userResponse = await apiService.getCurrentUser();
      
      if (!userResponse.success) {
        return userResponse;
      }
      
      const user = userResponse.data.user || userResponse.data;
      const role = user.role || 'student';
      
      console.log(`🎯 Detected user role: ${role}, fetching role-specific data`);
      
      // Try role-specific endpoints
      const roleEndpoints = {
        student: ['/auth/students/dashboard/', '/students/dashboard/', '/api/v1/students/dashboard/'],
        teacher: ['/auth/teachers/dashboard/', '/teachers/dashboard/', '/api/v1/teachers/dashboard/'],
        admin: ['/auth/admin/dashboard/', '/admin/dashboard/', '/api/v1/admin/dashboard/'],
        parent: ['/auth/parents/dashboard/', '/parents/dashboard/', '/api/v1/parents/dashboard/'],
        accountant: ['/auth/accountants/dashboard/', '/accountants/dashboard/', '/api/v1/accountants/dashboard/']
      };
      
      const endpoints = roleEndpoints[role] || ['/auth/me/'];
      const result = await tryEndpoints(endpoints);
      
      if (result.success) {
        console.log(`✅ ${role} dashboard data fetched from: ${result.endpoint}`);
        return wrapSuccess(result.data, `${role} dashboard data fetched successfully`);
      }
      
      // Fallback to generic dashboard
      console.log(`⚠️ No ${role}-specific dashboard available, using generic data`);
      return apiService.getDashboardData();
    } catch (error) {
      return handleError(error, 'getRoleDashboard');
    }
  },

  // ==================== ENHANCEMENT UTILITIES ====================

  /**
   * Enhance dashboard data with additional calculations
   */
  enhanceDashboardData: (dashboardData) => {
    try {
      const user = dashboardData.user || dashboardData;
      const role = user.role || 'student';
      
      // Create enhanced data structure
      const enhancedData = {
        ...dashboardData,
        stats: apiService.calculateRoleStats(role, dashboardData),
        recentActivities: apiService.generateRecentActivities(role, dashboardData),
        upcomingEvents: apiService.generateUpcomingEvents(),
        quickActions: apiService.getQuickActions(role),
        welcomeMessage: apiService.getWelcomeMessage(role, user)
      };
      
      return enhancedData;
    } catch (error) {
      console.warn('⚠️ Failed to enhance dashboard data:', error);
      return dashboardData;
    }
  },

  /**
   * Create fallback dashboard data when no API endpoints are available
   */
  createFallbackDashboardData: async () => {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    const role = userData.role || 'student';
    
    return {
      user: userData,
      role: role,
      stats: {
        pendingAssignments: 0,
        averageGrade: 'N/A',
        attendanceRate: 0,
        enrolledClasses: 0
      },
      recentActivities: [
        {
          activity: 'You logged into the system',
          time: 'Just now',
          type: 'login'
        },
        {
          activity: 'Welcome to the dashboard',
          time: 'Today',
          type: 'welcome'
        }
      ],
      upcomingEvents: [],
      quickActions: apiService.getQuickActions(role),
      welcomeMessage: apiService.getWelcomeMessage(role, userData),
      timestamp: new Date().toISOString(),
      isFallback: true
    };
  },

  /**
   * Calculate role-specific stats
   */
  calculateRoleStats: (role, data) => {
    const baseStats = data.stats || {};
    
    switch (role) {
      case 'student':
        return {
          pendingAssignments: baseStats.pendingAssignments || 0,
          averageGrade: baseStats.averageGrade || 'N/A',
          attendanceRate: baseStats.attendanceRate || 0,
          enrolledClasses: baseStats.enrolledClasses || 0
        };
      case 'teacher':
        return {
          totalStudents: baseStats.totalStudents || 0,
          totalClasses: baseStats.totalClasses || 0,
          pendingGrades: baseStats.pendingGrades || 0,
          attendanceRate: baseStats.attendanceRate || 0
        };
      case 'admin':
        return {
          totalUsers: baseStats.totalUsers || 0,
          activeStudents: baseStats.activeStudents || 0,
          activeTeachers: baseStats.activeTeachers || 0,
          pendingApprovals: baseStats.pendingApprovals || 0
        };
      case 'accountant':
        return {
          totalRevenue: baseStats.totalRevenue || 0,
          pendingPayments: baseStats.pendingPayments || 0,
          outstandingDebt: baseStats.outstandingDebt || 0,
          receiptsToday: baseStats.receiptsToday || 0
        };
      default:
        return baseStats;
    }
  },

  /**
   * Generate recent activities based on role
   */
  generateRecentActivities: (role, data) => {
    const activities = data.recentActivities || [];
    
    if (activities.length === 0) {
      return [
        {
          activity: 'You logged into the system',
          time: 'Just now',
          type: 'login'
        },
        {
          activity: 'Welcome to your dashboard',
          time: 'Today',
          type: 'welcome'
        }
      ];
    }
    
    return activities.slice(0, 5); // Limit to 5 most recent
  },

  /**
   * Generate upcoming events
   */
  generateUpcomingEvents: () => {
    const events = [];
    const today = new Date();
    
    // Add sample events
    for (let i = 1; i <= 3; i++) {
      const eventDate = new Date(today);
      eventDate.setDate(today.getDate() + i);
      
      events.push({
        id: i,
        title: `Sample Event ${i}`,
        date: eventDate.toISOString().split('T')[0],
        time: '09:00 AM',
        location: 'School Campus',
        type: i % 2 === 0 ? 'academic' : 'social'
      });
    }
    
    return events;
  },

  /**
   * Get role-specific quick actions
   */
  getQuickActions: (role) => {
    const actions = {
      student: [
        { title: 'View Assignments', link: '/assignments', icon: 'clipboard', color: 'primary' },
        { title: 'Check Grades', link: '/grades', icon: 'graph-up', color: 'success' },
        { title: 'View Timetable', link: '/timetable', icon: 'calendar', color: 'warning' },
        { title: 'Learning Resources', link: '/resources', icon: 'book', color: 'info' }
      ],
      teacher: [
        { title: 'My Classes', link: '/classes', icon: 'journal', color: 'primary' },
        { title: 'Take Attendance', link: '/attendance', icon: 'calendar-check', color: 'success' },
        { title: 'Enter Grades', link: '/grades', icon: 'clipboard', color: 'warning' },
        { title: 'Lesson Plans', link: '/lesson-plans', icon: 'book-open', color: 'info' }
      ],
      admin: [
        { title: 'User Management', link: '/admin/users', icon: 'people', color: 'primary' },
        { title: 'Academic Management', link: '/academic-management', icon: 'school', color: 'success' },
        { title: 'System Settings', link: '/admin/settings', icon: 'gear', color: 'warning' },
        { title: 'Reports & Analytics', link: '/admin/analytics', icon: 'graph-up', color: 'info' }
      ],
      accountant: [
        { title: 'Finance Dashboard', link: '/finance', icon: 'credit-card', color: 'primary' },
        { title: 'Process Payments', link: '/finance/payments', icon: 'payment', color: 'success' },
        { title: 'Manage Receipts', link: '/finance/receipts', icon: 'receipt', color: 'warning' },
        { title: 'Financial Reports', link: '/finance/reports', icon: 'report', color: 'info' }
      ],
      parent: [
        { title: 'Child Progress', link: '/child-progress', icon: 'graph-up', color: 'primary' },
        { title: 'Attendance', link: '/attendance', icon: 'calendar-check', color: 'success' },
        { title: 'Fee Statements', link: '/parent/billing', icon: 'credit-card', color: 'warning' },
        { title: 'Communications', link: '/communications', icon: 'megaphone', color: 'info' }
      ]
    };
    
    return actions[role] || actions.student;
  },

  /**
   * Get welcome message based on role
   */
  getWelcomeMessage: (role, user) => {
    const firstName = user.first_name || user.firstName || user.email?.split('@')[0] || 'User';
    
    const messages = {
      student: `Welcome back, ${firstName}! Track your academic progress and upcoming assignments.`,
      teacher: `Welcome, ${firstName}! Manage your classes, students, and teaching materials.`,
      admin: `Welcome, ${firstName}! Oversee school operations and manage all aspects of the academy.`,
      accountant: `Welcome, ${firstName}! Manage school finances, payments, and financial reporting.`,
      parent: `Welcome, ${firstName}! Monitor your children's academic journey and school activities.`
    };
    
    return messages[role] || `Welcome, ${firstName}! You are logged in as ${role}.`;
  },

  // ==================== UTILITY METHODS ====================

  /**
   * Validate API endpoints
   */
  validateEndpoints: async () => {
    const endpoints = [
      { name: 'Auth User', endpoint: '/auth/me/', method: 'GET' },
      { name: 'User Profile', endpoint: '/auth/profile/', method: 'GET' },
      { name: 'User Activity', endpoint: '/auth/activity/', method: 'GET' },
      { name: 'Dashboard (me)', endpoint: '/auth/me/', method: 'GET' },
      { name: 'Dashboard (users)', endpoint: '/auth/users/dashboard/', method: 'GET' },
      { name: 'Students Dashboard', endpoint: '/students/dashboard/', method: 'GET' },
      { name: 'Teachers Dashboard', endpoint: '/teachers/dashboard/', method: 'GET' }
    ];

    const results = [];
    
    for (const ep of endpoints) {
      try {
        const response = await api.head(ep.endpoint);
        results.push({
          name: ep.name,
          endpoint: ep.endpoint,
          valid: true,
          status: response.status,
          method: ep.method
        });
      } catch (error) {
        // Try GET if HEAD fails
        try {
          const response = await api.get(ep.endpoint);
          results.push({
            name: ep.name,
            endpoint: ep.endpoint,
            valid: true,
            status: response.status,
            method: ep.method,
            note: 'HEAD failed, GET succeeded'
          });
        } catch (getError) {
          results.push({
            name: ep.name,
            endpoint: ep.endpoint,
            valid: false,
            status: getError.response?.status,
            error: getError.message,
            method: ep.method
          });
        }
      }
    }

    console.log('🔍 API Endpoint Validation Results:', results);
    return results;
  },

  /**
   * Get stored user data
   */
  getStoredUser: () => {
    try {
      const userData = localStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting stored user:', error);
      return null;
    }
  },

  /**
   * Update stored user data
   */
  updateStoredUser: (userData) => {
    try {
      const currentData = apiService.getStoredUser() || {};
      const updatedData = { ...currentData, ...userData };
      localStorage.setItem('user_data', JSON.stringify(updatedData));
      console.log('✅ Updated stored user data');
      return updatedData;
    } catch (error) {
      console.error('❌ Failed to update stored user data:', error);
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('access_token');
    const user = apiService.getStoredUser();
    return !!(token && user);
  },

  /**
   * Debug current auth state
   */
  debugAuthState: () => {
    const user = apiService.getStoredUser();
    const token = localStorage.getItem('access_token');
    
    return {
      isAuthenticated: apiService.isAuthenticated(),
      hasToken: !!token,
      hasRefreshToken: !!localStorage.getItem('refresh_token'),
      hasUserData: !!user,
      user: user,
      tokenPreview: token ? token.substring(0, 20) + '...' : null,
      role: user?.role,
      userId: user?.id
    };
  }
};

export default apiService;