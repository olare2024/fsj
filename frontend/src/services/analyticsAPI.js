import api from './api.js';

// ==================== ANALYTICS CONSTANTS ====================

export const ANALYTICS_CONSTANTS = {
  // Time periods
  PERIOD: {
    TODAY: 'today',
    YESTERDAY: 'yesterday',
    LAST_7_DAYS: 'last_7_days',
    LAST_30_DAYS: 'last_30_days',
    THIS_MONTH: 'this_month',
    LAST_MONTH: 'last_month',
    THIS_QUARTER: 'this_quarter',
    LAST_QUARTER: 'last_quarter',
    THIS_YEAR: 'this_year',
    LAST_YEAR: 'last_year',
    CUSTOM: 'custom',
    THIS_TERM: 'this_term',
    NEXT_QUARTER: 'next_quarter'
  },
  
  // Metrics types
  METRIC_TYPE: {
    COUNT: 'count',
    SUM: 'sum',
    AVERAGE: 'average',
    PERCENTAGE: 'percentage',
    GROWTH: 'growth',
    RATIO: 'ratio',
    TREND: 'trend'
  },
  
  // Chart types
  CHART_TYPE: {
    LINE: 'line',
    BAR: 'bar',
    PIE: 'pie',
    DOUGHNUT: 'doughnut',
    AREA: 'area',
    SCATTER: 'scatter',
    RADAR: 'radar',
    HEATMAP: 'heatmap',
    GAUGE: 'gauge'
  },
  
  // User roles
  USER_ROLE: {
    ADMIN: 'admin',
    TEACHER: 'teacher',
    STUDENT: 'student',
    PARENT: 'parent',
    ACCOUNTANT: 'accountant',
    HEAD_TEACHER: 'head_teacher'
  },
  
  // Analytics categories
  CATEGORY: {
    ACADEMIC: 'academic',
    FINANCE: 'finance',
    ATTENDANCE: 'attendance',
    USER: 'user',
    SYSTEM: 'system',
    PERFORMANCE: 'performance',
    ENGAGEMENT: 'engagement'
  },
  
  // Export formats
  EXPORT_FORMAT: {
    CSV: 'csv',
    EXCEL: 'excel',
    PDF: 'pdf',
    JSON: 'json'
  }
};

// ==================== CACHE MANAGEMENT ====================

const analyticsCache = new Map();
const cacheTimeouts = new Map();

const getCacheKey = (endpoint, params = {}) => {
  const paramString = JSON.stringify(params);
  return `${endpoint}_${paramString}`;
};

const setCache = (key, data, ttl = 5 * 60 * 1000) => {
  analyticsCache.set(key, {
    data,
    timestamp: Date.now(),
    ttl
  });
  
  if (cacheTimeouts.has(key)) {
    clearTimeout(cacheTimeouts.get(key));
  }
  
  const timeout = setTimeout(() => {
    analyticsCache.delete(key);
    cacheTimeouts.delete(key);
  }, ttl);
  
  cacheTimeouts.set(key, timeout);
};

const getCache = (key) => {
  const cached = analyticsCache.get(key);
  if (!cached) return null;
  
  const isExpired = Date.now() - cached.timestamp > cached.ttl;
  if (isExpired) {
    analyticsCache.delete(key);
    if (cacheTimeouts.has(key)) {
      clearTimeout(cacheTimeouts.get(key));
      cacheTimeouts.delete(key);
    }
    return null;
  }
  
  return cached.data;
};

const clearAnalyticsCache = (pattern = null) => {
  if (!pattern) {
    analyticsCache.clear();
    cacheTimeouts.forEach(timeout => clearTimeout(timeout));
    cacheTimeouts.clear();
  } else {
    for (const [key] of analyticsCache) {
      if (key.includes(pattern)) {
        analyticsCache.delete(key);
        if (cacheTimeouts.has(key)) {
          clearTimeout(cacheTimeouts.get(key));
          cacheTimeouts.delete(key);
        }
      }
    }
  }
};

// ==================== ERROR HANDLER ====================

const handleAnalyticsError = (error, defaultMessage = 'An analytics error occurred') => {
  console.error('📊 Analytics Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
    switch (status) {
      case 400:
        return {
          success: false,
          message: serverError.detail || serverError.message || 'Invalid request',
          status: 400
        };
      
      case 401:
        return {
          success: false,
          message: 'Authentication required',
          status: 401,
          requiresAuth: true
        };
      
      case 403:
        return {
          success: false,
          message: 'Access denied',
          status: 403,
          forbidden: true
        };
      
      case 404:
        return {
          success: false,
          message: 'Analytics endpoint not found',
          status: 404,
          notFound: true
        };
      
      default:
        return {
          success: false,
          message: serverError.detail || serverError.message || defaultMessage,
          status: status
        };
    }
  }
  
  if (error.request) {
    return {
      success: false,
      message: 'Network error. Check your connection.',
      status: 0,
      networkError: true
    };
  }
  
  if (error.code === 'ECONNABORTED') {
    return {
      success: false,
      message: 'Request timeout',
      status: -1,
      timeout: true
    };
  }
  
  return {
    success: false,
    message: error.message || defaultMessage,
    status: -1
  };
};

// ==================== ANALYTICS API ====================

export const analyticsAPI = {
  
  // ==================== CACHE MANAGEMENT ====================
  
  clearCache: clearAnalyticsCache,
  
  getCacheStats: () => {
    return {
      size: analyticsCache.size,
      entries: Array.from(analyticsCache.entries()).map(([key, value]) => ({
        key,
        timestamp: new Date(value.timestamp).toISOString(),
        expiresIn: value.ttl - (Date.now() - value.timestamp)
      }))
    };
  },
  
  // ==================== DASHBOARD & OVERVIEW ====================
  
  getDashboardOverview: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH) => {
    const cacheKey = getCacheKey('dashboard_overview', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      console.log('📊 Serving from cache:', cacheKey);
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: { period, view: 'dashboard' }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, 60000); // 1 minute cache
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch dashboard');
    }
  },
  
  getQuickStats: async () => {
    const cacheKey = 'quick_stats';
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/quick-stats/');
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, 30000); // 30 seconds cache
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch quick stats');
    }
  },
  
  getSystemHealth: async () => {
    try {
      const response = await api.get('/analytics/system-health/');
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch system health');
    }
  },
  
  // ==================== ROLE-SPECIFIC ANALYTICS ====================
  
  getTeacherAnalytics: async (teacherId = null) => {
    const cacheKey = getCacheKey('teacher_analytics', { teacherId });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/role/teacher/', {
        params: { teacher_id: teacherId }
      });
      
      const result = {
        success: true,
        data: response.data,
        teacherId,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch teacher analytics');
    }
  },
  
  getStudentAnalytics: async (studentId = null) => {
    const cacheKey = getCacheKey('student_analytics', { studentId });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/role/student/', {
        params: { student_id: studentId }
      });
      
      const result = {
        success: true,
        data: response.data,
        studentId,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch student analytics');
    }
  },
  
  getParentAnalytics: async (parentId = null) => {
    const cacheKey = getCacheKey('parent_analytics', { parentId });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/role/parent/', {
        params: { parent_id: parentId }
      });
      
      const result = {
        success: true,
        data: response.data,
        parentId,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch parent analytics');
    }
  },
  
  getAdminAnalytics: async () => {
    const cacheKey = 'admin_analytics';
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/role/admin/');
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch admin analytics');
    }
  },
  
  // ==================== ACADEMIC ANALYTICS ====================
  
  getAcademicPerformance: async (params = {}) => {
    const cacheKey = getCacheKey('academic_performance', params);
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) return cached;
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: {
          category: 'academic',
          type: 'performance',
          ...params
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        params,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch academic performance');
    }
  },
  
  getStudentProgress: async (studentId, period = ANALYTICS_CONSTANTS.PERIOD.LAST_30_DAYS) => {
    const cacheKey = getCacheKey('student_progress', { studentId, period });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: {
          category: 'academic',
          type: 'student_progress',
          student_id: studentId,
          period
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        studentId,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch student progress');
    }
  },
  
  // ==================== FINANCIAL ANALYTICS ====================
  
  getFinancialOverview: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH) => {
    const cacheKey = getCacheKey('financial_overview', { period });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: {
          category: 'finance',
          type: 'overview',
          period
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch financial overview');
    }
  },
  
  getRevenueAnalytics: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_YEAR) => {
    const cacheKey = getCacheKey('revenue_analytics', { period });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: {
          category: 'finance',
          type: 'revenue',
          period
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch revenue analytics');
    }
  },
  
  // ==================== USER ANALYTICS ====================
  
  getUserAnalytics: async (period = ANALYTICS_CONSTANTS.PERIOD.LAST_30_DAYS) => {
    const cacheKey = getCacheKey('user_analytics', { period });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: {
          category: 'user',
          type: 'overview',
          period
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch user analytics');
    }
  },
  
  getUserEngagement: async (period = ANALYTICS_CONSTANTS.PERIOD.LAST_30_DAYS) => {
    const cacheKey = getCacheKey('user_engagement', { period });
    const cached = getCache(cacheKey);
    
    if (cached) return cached;
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: {
          category: 'user',
          type: 'engagement',
          period
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch user engagement');
    }
  },
  
  // ==================== ATTENDANCE ANALYTICS ====================
  
  getAttendanceAnalytics: async (params = {}) => {
    const cacheKey = getCacheKey('attendance_analytics', params);
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) return cached;
    
    try {
      const response = await api.get('/analytics/analytics/', {
        params: {
          category: 'attendance',
          ...params
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        params,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to fetch attendance analytics');
    }
  },
  
  // ==================== EXPORT ENDPOINTS ====================
  
  exportAnalytics: async (analyticsType, format = ANALYTICS_CONSTANTS.EXPORT_FORMAT.CSV, params = {}) => {
    try {
      const response = await api.get(`/analytics/export/${analyticsType}/`, {
        params: { format, ...params },
        responseType: format === 'json' ? 'json' : 'blob'
      });
      
      if (format !== 'json') {
        const blob = new Blob([response.data], { type: this.getMimeType(format) });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `analytics_${analyticsType}_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
      
      return {
        success: true,
        message: `Exported as ${format}`,
        data: format === 'json' ? response.data : null,
        format
      };
    } catch (error) {
      return handleAnalyticsError(error, 'Failed to export analytics');
    }
  },
  
  // ==================== UTILITIES ====================
  
  getMimeType: (format) => {
    const mimeTypes = {
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.CSV]: 'text/csv',
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.EXCEL]: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.PDF]: 'application/pdf',
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.JSON]: 'application/json'
    };
    
    return mimeTypes[format] || 'application/octet-stream';
  },
  
  formatNumber: (num, format = 'default') => {
    if (num === null || num === undefined) return 'N/A';
    
    if (format === 'currency') {
      return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(num);
    }
    
    if (format === 'percentage') {
      return `${num.toFixed(1)}%`;
    }
    
    const absNum = Math.abs(num);
    if (absNum >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (absNum >= 1000) return `${(num / 1000).toFixed(1)}K`;
    
    return num.toLocaleString();
  },
  
  getAnalyticsPermissions: (userRole) => {
    const permissions = {
      [ANALYTICS_CONSTANTS.USER_ROLE.ADMIN]: {
        canViewAll: true,
        canExport: true,
        canViewFinancial: true,
        canViewAcademic: true,
        canViewUser: true,
        canViewSystem: true
      },
      [ANALYTICS_CONSTANTS.USER_ROLE.TEACHER]: {
        canViewAll: false,
        canExport: false,
        canViewFinancial: false,
        canViewAcademic: true,
        canViewUser: true,
        canViewSystem: false
      },
      [ANALYTICS_CONSTANTS.USER_ROLE.STUDENT]: {
        canViewAll: false,
        canExport: false,
        canViewFinancial: false,
        canViewAcademic: true,
        canViewUser: false,
        canViewSystem: false
      }
    };
    
    return permissions[userRole] || permissions[ANALYTICS_CONSTANTS.USER_ROLE.STUDENT];
  },
  
  healthCheck: async () => {
    try {
      const response = await api.get('/analytics/health/', { timeout: 5000 });
      return {
        success: true,
        status: 'healthy',
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        status: 'unhealthy',
        message: error.message
      };
    }
  }
};

export default analyticsAPI;