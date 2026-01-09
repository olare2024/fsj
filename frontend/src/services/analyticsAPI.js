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
    CUSTOM: 'custom'
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
  
  // User roles for analytics
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
  
  // Cache settings
  CACHE_TTL: {
    SHORT: 1 * 60 * 1000, // 1 minute
    MEDIUM: 5 * 60 * 1000, // 5 minutes
    LONG: 30 * 60 * 1000, // 30 minutes
    VERY_LONG: 24 * 60 * 60 * 1000 // 24 hours
  },
  
  // Default limits
  DEFAULT_LIMIT: 10,
  MAX_LIMIT: 1000,
  
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

const setCache = (key, data, ttl = ANALYTICS_CONSTANTS.CACHE_TTL.MEDIUM) => {
  analyticsCache.set(key, {
    data,
    timestamp: Date.now(),
    ttl
  });
  
  // Clear existing timeout if any
  if (cacheTimeouts.has(key)) {
    clearTimeout(cacheTimeouts.get(key));
  }
  
  // Set new timeout for auto-cleanup
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

const clearCache = (pattern = null) => {
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
  console.error('📊 Analytics API Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
    // Handle specific status codes
    switch (status) {
      case 400:
        return {
          success: false,
          message: serverError.detail || serverError.message || 'Invalid analytics request',
          errors: serverError.errors || serverError.details,
          status: 400,
          data: serverError
        };
      
      case 401:
        return {
          success: false,
          message: 'Authentication required to access analytics',
          status: 401,
          requiresAuth: true
        };
      
      case 403:
        return {
          success: false,
          message: 'You do not have permission to access these analytics',
          status: 403,
          forbidden: true
        };
      
      case 429:
        return {
          success: false,
          message: 'Too many analytics requests. Please try again later.',
          status: 429,
          rateLimited: true
        };
      
      case 503:
        return {
          success: false,
          message: 'Analytics service is temporarily unavailable',
          status: 503,
          serviceUnavailable: true
        };
      
      default:
        return {
          success: false,
          message: serverError.detail || serverError.message || defaultMessage,
          status: status,
          data: serverError
        };
    }
  } else if (error.request) {
    return {
      success: false,
      message: 'Unable to connect to analytics service. Please check your internet connection.',
      status: 0,
      networkError: true
    };
  } else if (error.code === 'ECONNABORTED') {
    return {
      success: false,
      message: 'Analytics request timed out. Please try again.',
      status: -1,
      timeout: true
    };
  } else {
    return {
      success: false,
      message: error.message || defaultMessage,
      status: -1
    };
  }
};

// ==================== ANALYTICS API ====================

export const analyticsAPI = {
  // ==================== CACHE MANAGEMENT ====================
  
  clearCache,
  
  getCacheStats: () => {
    return {
      size: analyticsCache.size,
      timeouts: cacheTimeouts.size,
      keys: Array.from(analyticsCache.keys()),
      entries: Array.from(analyticsCache.entries()).map(([key, value]) => ({
        key,
        timestamp: new Date(value.timestamp).toISOString(),
        age: Date.now() - value.timestamp,
        ttl: value.ttl,
        expiresIn: value.ttl - (Date.now() - value.timestamp)
      }))
    };
  },
  
  // ==================== DASHBOARD METRICS ====================
  
  /**
   * Get dashboard overview metrics
   */
  getDashboardOverview: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH) => {
    const cacheKey = getCacheKey('dashboard_overview', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      console.log('📊 Serving dashboard overview from cache');
      return cached;
    }
    
    try {
      console.log('📊 Fetching dashboard overview for period:', period);
      
      const response = await api.get('/analytics/dashboard/overview/', {
        params: { period }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now(),
        fetchedAt: new Date().toISOString()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching dashboard overview:', error);
      return handleAnalyticsError(error, 'Failed to fetch dashboard overview');
    }
  },
  
  /**
   * Get home page analytics (for homepage)
   */
  getHomeAnalytics: async () => {
    const cacheKey = 'home_analytics';
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/home/');
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.MEDIUM);
      return result;
    } catch (error) {
      console.error('❌ Error fetching home analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch home analytics');
    }
  },
  
  /**
   * Get real-time metrics
   */
  getRealtimeMetrics: async () => {
    // Never cache real-time data
    try {
      const response = await api.get('/analytics/realtime/', {
        timeout: 10000 // 10 second timeout for real-time data
      });
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now(),
        isRealtime: true
      };
    } catch (error) {
      console.error('❌ Error fetching real-time metrics:', error);
      return handleAnalyticsError(error, 'Failed to fetch real-time metrics');
    }
  },
  
  /**
   * Get KPIs (Key Performance Indicators)
   */
  getKPIs: async (kpiType = 'all', period = ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH) => {
    const cacheKey = getCacheKey('kpis', { kpiType, period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/kpis/', {
        params: { type: kpiType, period }
      });
      
      const result = {
        success: true,
        data: response.data,
        kpiType,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching KPIs:', error);
      return handleAnalyticsError(error, 'Failed to fetch KPIs');
    }
  },
  
  // ==================== ACADEMIC ANALYTICS ====================
  
  /**
   * Get academic performance analytics
   */
  getAcademicPerformance: async (params = {}) => {
    const cacheKey = getCacheKey('academic_performance', params);
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/academic/performance/', {
        params: {
          period: ANALYTICS_CONSTANTS.PERIOD.THIS_YEAR,
          ...params
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        params,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.MEDIUM);
      return result;
    } catch (error) {
      console.error('❌ Error fetching academic performance:', error);
      return handleAnalyticsError(error, 'Failed to fetch academic performance analytics');
    }
  },
  
  /**
   * Get grade distribution analytics
   */
  getGradeDistribution: async (classId = null, subjectId = null, period = ANALYTICS_CONSTANTS.PERIOD.THIS_TERM) => {
    const cacheKey = getCacheKey('grade_distribution', { classId, subjectId, period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/academic/grades/distribution/', {
        params: { class_id: classId, subject_id: subjectId, period }
      });
      
      const result = {
        success: true,
        data: response.data,
        classId,
        subjectId,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching grade distribution:', error);
      return handleAnalyticsError(error, 'Failed to fetch grade distribution');
    }
  },
  
  /**
   * Get student progress analytics
   */
  getStudentProgress: async (studentId, period = ANALYTICS_CONSTANTS.PERIOD.LAST_30_DAYS) => {
    const cacheKey = getCacheKey('student_progress', { studentId, period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get(`/analytics/students/${studentId}/progress/`, {
        params: { period }
      });
      
      const result = {
        success: true,
        data: response.data,
        studentId,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching student progress:', error);
      return handleAnalyticsError(error, 'Failed to fetch student progress analytics');
    }
  },
  
  /**
   * Get teacher performance analytics
   */
  getTeacherPerformance: async (teacherId = null, period = ANALYTICS_CONSTANTS.PERIOD.THIS_YEAR) => {
    const cacheKey = getCacheKey('teacher_performance', { teacherId, period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/teachers/performance/', {
        params: { teacher_id: teacherId, period }
      });
      
      const result = {
        success: true,
        data: response.data,
        teacherId,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching teacher performance:', error);
      return handleAnalyticsError(error, 'Failed to fetch teacher performance analytics');
    }
  },
  
  // ==================== FINANCIAL ANALYTICS ====================
  
  /**
   * Get financial overview
   */
  getFinancialOverview: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH) => {
    const cacheKey = getCacheKey('financial_overview', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/financial/overview/', {
        params: { period }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching financial overview:', error);
      return handleAnalyticsError(error, 'Failed to fetch financial overview');
    }
  },
  
  /**
   * Get revenue analytics
   */
  getRevenueAnalytics: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_YEAR) => {
    const cacheKey = getCacheKey('revenue_analytics', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/financial/revenue/', {
        params: { period }
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
      console.error('❌ Error fetching revenue analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch revenue analytics');
    }
  },
  
  /**
   * Get expense analytics
   */
  getExpenseAnalytics: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH) => {
    const cacheKey = getCacheKey('expense_analytics', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/financial/expenses/', {
        params: { period }
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
      console.error('❌ Error fetching expense analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch expense analytics');
    }
  },
  
  /**
   * Get fee collection analytics
   */
  getFeeCollectionAnalytics: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH) => {
    const cacheKey = getCacheKey('fee_collection', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/financial/fee-collection/', {
        params: { period }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching fee collection analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch fee collection analytics');
    }
  },
  
  // ==================== ATTENDANCE ANALYTICS ====================
  
  /**
   * Get attendance analytics
   */
  getAttendanceAnalytics: async (params = {}) => {
    const cacheKey = getCacheKey('attendance_analytics', params);
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/attendance/', {
        params: {
          period: ANALYTICS_CONSTANTS.PERIOD.THIS_MONTH,
          ...params
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        params,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching attendance analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch attendance analytics');
    }
  },
  
  /**
   * Get attendance trends
   */
  getAttendanceTrends: async (entityType = 'overall', entityId = null, period = ANALYTICS_CONSTANTS.PERIOD.LAST_30_DAYS) => {
    const cacheKey = getCacheKey('attendance_trends', { entityType, entityId, period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/attendance/trends/', {
        params: { entity_type: entityType, entity_id: entityId, period }
      });
      
      const result = {
        success: true,
        data: response.data,
        entityType,
        entityId,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching attendance trends:', error);
      return handleAnalyticsError(error, 'Failed to fetch attendance trends');
    }
  },
  
  // ==================== USER ANALYTICS ====================
  
  /**
   * Get user engagement analytics
   */
  getUserEngagement: async (period = ANALYTICS_CONSTANTS.PERIOD.LAST_30_DAYS) => {
    const cacheKey = getCacheKey('user_engagement', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/users/engagement/', {
        params: { period }
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
      console.error('❌ Error fetching user engagement:', error);
      return handleAnalyticsError(error, 'Failed to fetch user engagement analytics');
    }
  },
  
  /**
   * Get user growth analytics
   */
  getUserGrowth: async (period = ANALYTICS_CONSTANTS.PERIOD.THIS_YEAR) => {
    const cacheKey = getCacheKey('user_growth', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/users/growth/', {
        params: { period }
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
      console.error('❌ Error fetching user growth:', error);
      return handleAnalyticsError(error, 'Failed to fetch user growth analytics');
    }
  },
  
  /**
   * Get active users analytics
   */
  getActiveUsers: async (period = ANALYTICS_CONSTANTS.PERIOD.LAST_7_DAYS) => {
    const cacheKey = getCacheKey('active_users', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/users/active/', {
        params: { period }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching active users:', error);
      return handleAnalyticsError(error, 'Failed to fetch active users analytics');
    }
  },
  
  // ==================== SYSTEM ANALYTICS ====================
  
  /**
   * Get system performance analytics
   */
  getSystemPerformance: async (period = ANALYTICS_CONSTANTS.PERIOD.LAST_7_DAYS) => {
    const cacheKey = getCacheKey('system_performance', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/system/performance/', {
        params: { period }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.MEDIUM);
      return result;
    } catch (error) {
      console.error('❌ Error fetching system performance:', error);
      return handleAnalyticsError(error, 'Failed to fetch system performance analytics');
    }
  },
  
  /**
   * Get API usage analytics
   */
  getAPIUsage: async (period = ANALYTICS_CONSTANTS.PERIOD.LAST_30_DAYS) => {
    const cacheKey = getCacheKey('api_usage', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/system/api-usage/', {
        params: { period }
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
      console.error('❌ Error fetching API usage:', error);
      return handleAnalyticsError(error, 'Failed to fetch API usage analytics');
    }
  },
  
  /**
   * Get error analytics
   */
  getErrorAnalytics: async (period = ANALYTICS_CONSTANTS.PERIOD.LAST_7_DAYS) => {
    const cacheKey = getCacheKey('error_analytics', { period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/system/errors/', {
        params: { period }
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
      console.error('❌ Error fetching error analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch error analytics');
    }
  },
  
  // ==================== CUSTOM ANALYTICS ====================
  
  /**
   * Get custom analytics query
   */
  getCustomAnalytics: async (query, params = {}) => {
    const cacheKey = getCacheKey('custom_analytics', { query, params });
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      return cached;
    }
    
    try {
      const response = await api.post('/analytics/custom/', {
        query,
        params
      });
      
      const result = {
        success: true,
        data: response.data,
        query,
        params,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching custom analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch custom analytics');
    }
  },
  
  /**
   * Run ad-hoc analytics query
   */
  runAnalyticsQuery: async (query, format = 'json') => {
    try {
      const response = await api.post('/analytics/query/', {
        query,
        format
      });
      
      return {
        success: true,
        data: response.data,
        query,
        format,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error running analytics query:', error);
      return handleAnalyticsError(error, 'Failed to run analytics query');
    }
  },
  
  // ==================== CHARTS & VISUALIZATIONS ====================
  
  /**
   * Get chart data
   */
  getChartData: async (chartType, metric, params = {}) => {
    const cacheKey = getCacheKey('chart_data', { chartType, metric, params });
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/charts/data/', {
        params: {
          chart_type: chartType,
          metric,
          ...params
        }
      });
      
      const result = {
        success: true,
        data: response.data,
        chartType,
        metric,
        params,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching chart data:', error);
      return handleAnalyticsError(error, 'Failed to fetch chart data');
    }
  },
  
  /**
   * Get pre-configured dashboard charts
   */
  getDashboardCharts: async (dashboardType = 'admin') => {
    const cacheKey = getCacheKey('dashboard_charts', { dashboardType });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/analytics/charts/dashboard/', {
        params: { dashboard_type: dashboardType }
      });
      
      const result = {
        success: true,
        data: response.data,
        dashboardType,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, ANALYTICS_CONSTANTS.CACHE_TTL.SHORT);
      return result;
    } catch (error) {
      console.error('❌ Error fetching dashboard charts:', error);
      return handleAnalyticsError(error, 'Failed to fetch dashboard charts');
    }
  },
  
  // ==================== EXPORT & DOWNLOAD ====================
  
  /**
   * Export analytics data
   */
  exportAnalytics: async (analyticsType, format = ANALYTICS_CONSTANTS.EXPORT_FORMAT.CSV, params = {}) => {
    try {
      const response = await api.get(`/analytics/export/${analyticsType}/`, {
        params: {
          format,
          ...params
        },
        responseType: format === 'json' ? 'json' : 'blob'
      });
      
      // Create download link for non-JSON formats
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
        message: `Analytics exported successfully as ${format}`,
        data: format === 'json' ? response.data : null,
        format,
        analyticsType,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error exporting analytics:', error);
      return handleAnalyticsError(error, 'Failed to export analytics');
    }
  },
  
  // ==================== PREDICTIVE ANALYTICS ====================
  
  /**
   * Get predictive analytics
   */
  getPredictiveAnalytics: async (modelType, params = {}) => {
    try {
      const response = await api.post('/analytics/predictive/', {
        model_type: modelType,
        ...params
      });
      
      return {
        success: true,
        data: response.data,
        modelType,
        params,
        timestamp: Date.now(),
        isPredictive: true
      };
    } catch (error) {
      console.error('❌ Error fetching predictive analytics:', error);
      return handleAnalyticsError(error, 'Failed to fetch predictive analytics');
    }
  },
  
  /**
   * Get trends and forecasts
   */
  getTrendsForecast: async (metric, period = ANALYTICS_CONSTANTS.PERIOD.NEXT_QUARTER) => {
    try {
      const response = await api.get('/analytics/trends/forecast/', {
        params: { metric, period }
      });
      
      return {
        success: true,
        data: response.data,
        metric,
        period,
        timestamp: Date.now(),
        isForecast: true
      };
    } catch (error) {
      console.error('❌ Error fetching trends forecast:', error);
      return handleAnalyticsError(error, 'Failed to fetch trends forecast');
    }
  },
  
  // ==================== UTILITY FUNCTIONS ====================
  
  /**
   * Get MIME type for export format
   */
  getMimeType: (format) => {
    const mimeTypes = {
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.CSV]: 'text/csv',
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.EXCEL]: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.PDF]: 'application/pdf',
      [ANALYTICS_CONSTANTS.EXPORT_FORMAT.JSON]: 'application/json'
    };
    
    return mimeTypes[format] || 'application/octet-stream';
  },
  
  /**
   * Format analytics data for display
   */
  formatAnalyticsData: (data, format = 'human') => {
    if (!data) return null;
    
    if (format === 'human') {
      return {
        value: data.value,
        formatted: this.formatNumber(data.value, data.format),
        change: data.change ? `${data.change > 0 ? '+' : ''}${data.change}%` : null,
        trend: data.trend || 'neutral',
        comparison: data.comparison || null,
        metadata: data.metadata || {}
      };
    }
    
    return data;
  },
  
  /**
   * Format number with appropriate suffix
   */
  formatNumber: (num, format = 'default') => {
    if (num === null || num === undefined) return 'N/A';
    
    const absNum = Math.abs(num);
    
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
    
    if (absNum >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    
    if (absNum >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    
    return num.toLocaleString();
  },
  
  /**
   * Calculate growth percentage
   */
  calculateGrowth: (current, previous) => {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  },
  
  /**
   * Get analytics permissions for user role
   */
  getAnalyticsPermissions: (userRole) => {
    const permissions = {
      [ANALYTICS_CONSTANTS.USER_ROLE.ADMIN]: {
        canViewAll: true,
        canExport: true,
        canViewFinancial: true,
        canViewAcademic: true,
        canViewUser: true,
        canViewSystem: true,
        canRunCustomQueries: true
      },
      [ANALYTICS_CONSTANTS.USER_ROLE.HEAD_TEACHER]: {
        canViewAll: false,
        canExport: true,
        canViewFinancial: false,
        canViewAcademic: true,
        canViewUser: true,
        canViewSystem: false,
        canRunCustomQueries: false
      },
      [ANALYTICS_CONSTANTS.USER_ROLE.TEACHER]: {
        canViewAll: false,
        canExport: false,
        canViewFinancial: false,
        canViewAcademic: true,
        canViewUser: true,
        canViewSystem: false,
        canRunCustomQueries: false
      },
      [ANALYTICS_CONSTANTS.USER_ROLE.ACCOUNTANT]: {
        canViewAll: false,
        canExport: true,
        canViewFinancial: true,
        canViewAcademic: false,
        canViewUser: false,
        canViewSystem: false,
        canRunCustomQueries: false
      },
      [ANALYTICS_CONSTANTS.USER_ROLE.STUDENT]: {
        canViewAll: false,
        canExport: false,
        canViewFinancial: false,
        canViewAcademic: true,
        canViewUser: false,
        canViewSystem: false,
        canRunCustomQueries: false
      },
      [ANALYTICS_CONSTANTS.USER_ROLE.PARENT]: {
        canViewAll: false,
        canExport: false,
        canViewFinancial: false,
        canViewAcademic: true,
        canViewUser: false,
        canViewSystem: false,
        canRunCustomQueries: false
      }
    };
    
    return permissions[userRole] || permissions[ANALYTICS_CONSTANTS.USER_ROLE.STUDENT];
  },
  
  /**
   * Get recommended charts for user role
   */
  getRecommendedCharts: (userRole) => {
    const recommendations = {
      [ANALYTICS_CONSTANTS.USER_ROLE.ADMIN]: [
        'revenue_trends',
        'student_growth',
        'attendance_overview',
        'system_performance',
        'fee_collection'
      ],
      [ANALYTICS_CONSTANTS.USER_ROLE.HEAD_TEACHER]: [
        'academic_performance',
        'teacher_workload',
        'student_attendance',
        'grade_distribution'
      ],
      [ANALYTICS_CONSTANTS.USER_ROLE.TEACHER]: [
        'class_performance',
        'student_progress',
        'assignment_completion',
        'attendance_trends'
      ],
      [ANALYTICS_CONSTANTS.USER_ROLE.ACCOUNTANT]: [
        'revenue_breakdown',
        'expense_categories',
        'fee_collection_rate',
        'outstanding_payments'
      ]
    };
    
    return recommendations[userRole] || [];
  },
  
  // ==================== HEALTH & MONITORING ====================
  
  /**
   * Check analytics service health
   */
  healthCheck: async () => {
    try {
      const startTime = Date.now();
      const response = await api.get('/analytics/health/', {
        timeout: 10000
      });
      const endTime = Date.now();
      
      return {
        success: true,
        status: 'healthy',
        responseTime: endTime - startTime,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        success: false,
        status: 'unhealthy',
        message: error.message,
        timestamp: Date.now()
      };
    }
  },
  
  /**
   * Get analytics service status
   */
  getServiceStatus: async () => {
    try {
      const response = await api.get('/analytics/status/');
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        success: false,
        status: 'offline',
        message: error.message,
        timestamp: Date.now()
      };
    }
  },
  
  /**
   * Track analytics event (for user behavior tracking)
   */
  trackEvent: async (eventName, eventData = {}) => {
    try {
      // Use beacon API for better performance if available
      if (navigator.sendBeacon) {
        const data = new FormData();
        data.append('event_name', eventName);
        data.append('event_data', JSON.stringify(eventData));
        data.append('timestamp', Date.now());
        data.append('user_agent', navigator.userAgent);
        
        navigator.sendBeacon('/api/v1/analytics/track-event/', data);
        return { success: true, method: 'beacon' };
      }
      
      // Fallback to regular API call
      await api.post('/analytics/track-event/', {
        event_name: eventName,
        event_data: eventData,
        timestamp: Date.now(),
        user_agent: navigator.userAgent
      });
      
      return { success: true, method: 'api' };
    } catch (error) {
      console.error('❌ Error tracking analytics event:', error);
      return { success: false, error: error.message };
    }
  }
};

export default analyticsAPI;