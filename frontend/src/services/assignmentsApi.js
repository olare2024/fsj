// services/assignmentsAPI.js - COMPLETE OPTIMIZED VERSION
import api, { apiUtils } from './api';

/**
 * Assignment-related constants for consistent usage across the application
 */
export const ASSIGNMENT_CONSTANTS = {
  STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    IN_PROGRESS: 'in_progress',
    CLOSED: 'closed',
    GRADED: 'graded'
  },
  TYPES: {
    HOMEWORK: 'homework',
    PROJECT: 'project',
    QUIZ: 'quiz',
    EXAM: 'exam',
    PRESENTATION: 'presentation',
    PRACTICAL: 'practical',
    ASSESSMENT: 'assessment'
  },
  DIFFICULTY: {
    EASY: 'easy',
    MEDIUM: 'medium',
    HARD: 'hard',
    ADVANCED: 'advanced'
  },
  SUBMISSION_STATUS: {
    NOT_SUBMITTED: 'not_submitted',
    SUBMITTED: 'submitted',
    LATE: 'late',
    GRADED: 'graded',
    MISSED: 'missed'
  }
};

/**
 * Simple in-memory cache for assignments data
 */
export const assignmentsCache = {
  data: new Map(),
  
  set(key, value, ttl = 60000) { // Default 1 minute TTL
    this.data.set(key, {
      value,
      timestamp: Date.now(),
      ttl
    });
  },
  
  get(key) {
    const item = this.data.get(key);
    if (!item) return null;
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.data.delete(key);
      return null;
    }
    
    return item.value;
  },
  
  delete(key) {
    this.data.delete(key);
  },
  
  clear() {
    this.data.clear();
  },
  
  getStats() {
    return {
      size: this.data.size,
      keys: Array.from(this.data.keys()),
      hits: Array.from(this.data.values()).filter(item => 
        Date.now() - item.timestamp <= item.ttl
      ).length
    };
  }
};

/**
 * Standardized error handler for all API calls
 */
export const handleAPIError = (error) => {
  // Special handling for 500 errors
  if (error.response?.status === 500) {
    return {
      success: false,
      error: {
        message: 'Server error occurred',
        details: 'Internal server error. Please try again later.',
        status: 500,
        code: 'SERVER_ERROR',
        path: error.config?.url
      },
      isServerError: true
    };
  }
  
  // Handle 404 for missing endpoints
  if (error.response?.status === 404) {
    return {
      success: false,
      error: {
        message: 'API endpoint not found',
        details: 'The requested assignment endpoint does not exist',
        status: 404,
        code: 'ENDPOINT_NOT_FOUND',
        path: error.config?.url
      }
    };
  }
  
  return {
    success: false,
    error: {
      message: apiUtils.getErrorMessage(error),
      details: error.response?.data,
      status: error.response?.status,
      code: error.code,
      path: error.config?.url
    }
  };
};

/**
 * Performance monitoring utility
 */
export const performanceMonitor = {
  timers: new Map(),
  
  start(timerName) {
    this.timers.set(timerName, {
      startTime: performance.now(),
      endTime: null,
      duration: null
    });
  },
  
  end(timerName) {
    const timer = this.timers.get(timerName);
    if (timer) {
      timer.endTime = performance.now();
      timer.duration = timer.endTime - timer.startTime;
      return timer.duration;
    }
    return null;
  },
  
  getDuration(timerName) {
    const timer = this.timers.get(timerName);
    return timer?.duration || null;
  },
  
  logSlowResponse(timerName, threshold = 2000) {
    const duration = this.getDuration(timerName);
    if (duration && duration > threshold) {
      console.warn(`⏱️ Slow response detected for ${timerName}: ${duration.toFixed(0)}ms`);
    }
  },
  
  clear() {
    this.timers.clear();
  }
};

/**
 * Helper function to download files from blob responses
 */
export const downloadFileFromBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

/**
 * Main assignments API object with all methods
 */
export const assignmentsAPI = {
  // ==================== PERFORMANCE SETTINGS ====================
  
  enablePerformanceLogging: true,
  
  logPerformance(endpoint, duration, dataSize = null) {
    if (this.enablePerformanceLogging && duration > 100) {
      console.log(`📊 API Performance: ${endpoint} - ${duration.toFixed(0)}ms${dataSize ? `, ${dataSize} items` : ''}`);
    }
  },
  
  // ==================== ASSIGNMENTS CRUD ====================

  /**
   * Get all assignments with optional filtering
   * @param {Object} params - Query parameters for filtering
   * @param {AbortSignal} signal - Optional abort signal for cancellation
   * @returns {Promise<Object>} Standardized response object
   */
  getAssignments: async (params = {}, signal = null) => {
    const timerName = `getAssignments_${JSON.stringify(params)}`;
    performanceMonitor.start(timerName);
    const cacheKey = `assignments_${JSON.stringify(params)}`;
    
    // Check cache first (only for GET requests without certain params)
    if (!params.page && !params.search && !params.student_id) {
      const cached = assignmentsCache.get(cacheKey);
      if (cached) {
        performanceMonitor.end(timerName);
        this.logPerformance('assignments', 0, cached.value.data?.count);
        return {
          ...cached.value,
          fromCache: true,
          responseTimeMs: 0
        };
      }
    }
    
    try {
      const config = signal ? { params, signal } : { params };
      const response = await api.get('/assignments/', config);
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('assignments', duration, response.data?.count);
      performanceMonitor.logSlowResponse(timerName);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        pagination: {
          total: response.data?.count || response.data?.results?.length || 0,
          page: params.page || 1,
          pageSize: params.page_size || 20
        },
        responseTimeMs: duration
      };
      
      // Cache successful result (excluding paginated or search results)
      if (!params.page && !params.search && !params.student_id) {
        assignmentsCache.set(cacheKey, result, 30000); // 30 seconds
      }
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      
      // Handle abort separately
      if (error.name === 'AbortError' || error.message === 'canceled') {
        return {
          success: false,
          error: {
            message: 'Request cancelled',
            code: 'REQUEST_CANCELLED'
          }
        };
      }
      
      return handleAPIError(error);
    }
  },

  /**
   * Get assignments created by the current teacher
   * @param {Object} params - Filter parameters
   * @param {AbortSignal} signal - Optional abort signal
   * @returns {Promise<Object>}
   */
  getMyAssignments: async (params = {}, signal = null) => {
    try {
      const config = signal ? { params, signal } : { params };
      const response = await api.get('/assignments/my-assignments/', config);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        count: response.data?.count || 0
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Get a specific assignment by ID
   * @param {string|number} assignmentId - Assignment ID
   * @returns {Promise<Object>}
   */
  getAssignmentById: async (assignmentId) => {
    const timerName = `getAssignmentById_${assignmentId}`;
    performanceMonitor.start(timerName);
    const cacheKey = `assignment_${assignmentId}`;
    
    // Check cache first
    const cached = assignmentsCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      this.logPerformance('assignmentById', 0);
      return {
        ...cached.value,
        fromCache: true,
        responseTimeMs: 0
      };
    }
    
    try {
      const response = await api.get(`/assignments/${assignmentId}/`);
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('assignmentById', duration);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        responseTimeMs: duration
      };
      
      // Cache for 2 minutes
      assignmentsCache.set(cacheKey, result, 120000);
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  /**
   * Create a new assignment
   * @param {Object} assignmentData - Assignment data
   * @returns {Promise<Object>}
   */
  createAssignment: async (assignmentData) => {
    const timerName = 'createAssignment';
    performanceMonitor.start(timerName);
    
    try {
      const response = await api.post('/assignments/', assignmentData);
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('createAssignment', duration);
      
      // Clear relevant cache
      assignmentsCache.delete('assignments_{}');
      assignmentsCache.delete('assignments_dashboard');
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignment created successfully',
        responseTimeMs: duration
      };
    } catch (error) {
      performanceMonitor.end(timerName);
      
      // Handle validation errors specifically
      if (error.response?.status === 400) {
        return {
          success: false,
          error: {
            message: 'Validation error',
            details: error.response.data,
            status: 400,
            code: 'VALIDATION_ERROR',
            validationErrors: error.response.data
          }
        };
      }
      
      return handleAPIError(error);
    }
  },

  /**
   * Update an existing assignment
   * @param {string|number} assignmentId - Assignment ID
   * @param {Object} assignmentData - Updated assignment data
   * @param {boolean} partial - Whether to use PATCH instead of PUT
   * @returns {Promise<Object>}
   */
  updateAssignment: async (assignmentId, assignmentData, partial = false) => {
    const timerName = `updateAssignment_${assignmentId}`;
    performanceMonitor.start(timerName);
    
    try {
      const method = partial ? 'patch' : 'put';
      const response = await api[method](`/assignments/${assignmentId}/`, assignmentData);
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('updateAssignment', duration);
      
      // Clear cache for this assignment
      assignmentsCache.delete(`assignment_${assignmentId}`);
      assignmentsCache.delete('assignments_{}');
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignment updated successfully',
        responseTimeMs: duration
      };
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  /**
   * Delete an assignment
   * @param {string|number} assignmentId - Assignment ID
   * @returns {Promise<Object>}
   */
  deleteAssignment: async (assignmentId) => {
    const timerName = `deleteAssignment_${assignmentId}`;
    performanceMonitor.start(timerName);
    
    try {
      const response = await api.delete(`/assignments/${assignmentId}/`);
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('deleteAssignment', duration);
      
      // Clear cache for this assignment
      assignmentsCache.delete(`assignment_${assignmentId}`);
      assignmentsCache.delete('assignments_{}');
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignment deleted successfully',
        responseTimeMs: duration
      };
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  // ==================== ASSIGNMENT ACTIONS ====================

  /**
   * Publish an assignment (change status to published)
   * @param {string|number} assignmentId - Assignment ID
   * @returns {Promise<Object>}
   */
  publishAssignment: async (assignmentId) => {
    try {
      const response = await api.post(`/assignments/${assignmentId}/publish/`);
      
      // Clear cache for this assignment
      assignmentsCache.delete(`assignment_${assignmentId}`);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignment published successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Close an assignment (no more submissions allowed)
   * @param {string|number} assignmentId - Assignment ID
   * @returns {Promise<Object>}
   */
  closeAssignment: async (assignmentId) => {
    try {
      const response = await api.post(`/assignments/${assignmentId}/close/`);
      
      // Clear cache for this assignment
      assignmentsCache.delete(`assignment_${assignmentId}`);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignment closed successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Duplicate an existing assignment
   * @param {string|number} assignmentId - Original assignment ID
   * @param {Object} duplicateData - Options for duplication
   * @returns {Promise<Object>}
   */
  duplicateAssignment: async (assignmentId, duplicateData = {}) => {
    try {
      const response = await api.post(
        `/assignments/${assignmentId}/duplicate/`,
        duplicateData
      );
      
      // Clear assignments cache
      assignmentsCache.delete('assignments_{}');
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignment duplicated successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== STATISTICS & DASHBOARD ====================

  /**
   * Get assignment dashboard data
   * @returns {Promise<Object>}
   */
  getDashboard: async () => {
    const timerName = 'getDashboard';
    performanceMonitor.start(timerName);
    const cacheKey = 'assignments_dashboard';
    
    const cached = assignmentsCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      return {
        ...cached.value,
        fromCache: true,
        responseTimeMs: 0
      };
    }
    
    try {
      const response = await api.get('/assignments/dashboard/');
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('dashboard', duration);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        responseTimeMs: duration
      };
      
      // Cache for 1 minute
      assignmentsCache.set(cacheKey, result, 60000);
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  /**
   * Get teacher's assignment statistics
   * @returns {Promise<Object>}
   */
  getTeacherStats: async () => {
    const cacheKey = 'teacher_stats';
    
    const cached = assignmentsCache.get(cacheKey);
    if (cached) {
      return {
        ...cached.value,
        fromCache: true
      };
    }
    
    try {
      const response = await api.get('/assignments/teacher-stats/');
      
      const result = {
        success: true,
        data: response.data,
        status: response.status
      };
      
      assignmentsCache.set(cacheKey, result, 300000); // 5 minutes
      
      return result;
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Get assignment statistics by assignment ID
   * @param {string|number} assignmentId - Assignment ID
   * @returns {Promise<Object>}
   */
  getAssignmentStats: async (assignmentId) => {
    const cacheKey = `assignment_stats_${assignmentId}`;
    
    const cached = assignmentsCache.get(cacheKey);
    if (cached) {
      return {
        ...cached.value,
        fromCache: true
      };
    }
    
    try {
      const response = await api.get(`/assignments/${assignmentId}/stats/`);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status
      };
      
      assignmentsCache.set(cacheKey, result, 30000); // 30 seconds
      
      return result;
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== SUBMISSIONS ====================

  /**
   * Get all submissions for an assignment
   * @param {string|number} assignmentId - Assignment ID
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>}
   */
  getSubmissions: async (assignmentId, params = {}) => {
    const timerName = `getSubmissions_${assignmentId}`;
    performanceMonitor.start(timerName);
    const cacheKey = `submissions_${assignmentId}_${JSON.stringify(params)}`;
    
    // Check cache (but not for search or filter params)
    if (!params.status && !params.search) {
      const cached = assignmentsCache.get(cacheKey);
      if (cached) {
        performanceMonitor.end(timerName);
        return {
          ...cached.value,
          fromCache: true,
          responseTimeMs: 0
        };
      }
    }
    
    try {
      const response = await api.get(`/assignments/${assignmentId}/submissions/`, { params });
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('submissions', duration, response.data?.count);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        responseTimeMs: duration
      };
      
      // Cache if no filters applied
      if (!params.status && !params.search) {
        assignmentsCache.set(cacheKey, result, 30000); // 30 seconds
      }
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  /**
   * Get student's own submissions
   * @returns {Promise<Object>}
   */
  getMySubmissions: async () => {
    const cacheKey = 'my_submissions';
    
    const cached = assignmentsCache.get(cacheKey);
    if (cached) {
      return {
        ...cached.value,
        fromCache: true
      };
    }
    
    try {
      const response = await api.get('/assignments/my-submissions/');
      
      const result = {
        success: true,
        data: response.data,
        status: response.status
      };
      
      assignmentsCache.set(cacheKey, result, 30000); // 30 seconds
      
      return result;
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Submit an assignment (for students)
   * @param {string|number} studentAssignmentId - Student assignment ID
   * @param {Object} submissionData - Submission data
   * @returns {Promise<Object>}
   */
  submitAssignment: async (studentAssignmentId, submissionData) => {
    try {
      const formData = new FormData();
      
      // Handle file uploads
      if (submissionData.attachments) {
        if (Array.isArray(submissionData.attachments)) {
          submissionData.attachments.forEach(file => {
            formData.append('attachments', file);
          });
        } else {
          formData.append('attachments', submissionData.attachments);
        }
      }
      
      // Add text data
      if (submissionData.submission_text) {
        formData.append('submission_text', submissionData.submission_text);
      }
      
      const response = await api.post(
        `/assignments/student-assignments/${studentAssignmentId}/submit/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Clear relevant cache
      assignmentsCache.delete('my_submissions');
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignment submitted successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Grade a single submission (for teachers)
   * @param {string|number} studentAssignmentId - Student assignment ID
   * @param {Object} gradeData - Grade data
   * @returns {Promise<Object>}
   */
  gradeSubmission: async (studentAssignmentId, gradeData) => {
    try {
      const response = await api.post(
        `/assignments/student-assignments/${studentAssignmentId}/grade/`,
        gradeData
      );
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Submission graded successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Bulk grade multiple submissions
   * @param {string|number} assignmentId - Assignment ID
   * @param {Array} grades - Array of grade objects
   * @returns {Promise<Object>}
   */
  bulkGradeSubmissions: async (assignmentId, grades) => {
    try {
      const response = await api.post(
        `/assignments/${assignmentId}/bulk-grade/`,
        { grades }
      );
      
      // Clear submissions cache for this assignment
      assignmentsCache.delete(`submissions_${assignmentId}_`);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: `${grades.length} submissions graded successfully`
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== GRADING IMPORT/EXPORT ====================

  /**
   * Import grades from CSV
   * @param {string|number} assignmentId - Assignment ID
   * @param {File} csvFile - CSV file
   * @returns {Promise<Object>}
   */
  importGrades: async (assignmentId, csvFile) => {
    try {
      const formData = new FormData();
      formData.append('csv_file', csvFile);
      
      const response = await api.post(
        `/assignments/${assignmentId}/import-grades/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Clear cache for this assignment
      assignmentsCache.delete(`submissions_${assignmentId}_`);
      assignmentsCache.delete(`assignment_stats_${assignmentId}`);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Grades imported successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Export grades for an assignment
   * @param {string|number} assignmentId - Assignment ID
   * @returns {Promise<Object>}
   */
  exportGrades: async (assignmentId) => {
    try {
      const response = await api.get(`/assignments/${assignmentId}/export-grades/`, {
        responseType: 'blob'
      });
      
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `grades_assignment_${assignmentId}_${timestamp}.csv`;
      
      downloadFileFromBlob(response.data, filename);
      
      return {
        success: true,
        data: { message: 'Export downloaded successfully' },
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Export assignments to CSV
   * @param {Object} params - Filter parameters for export
   * @returns {Promise<Object>}
   */
  exportAssignments: async (params = {}) => {
    try {
      const response = await api.get('/assignments/export/', {
        params,
        responseType: 'blob'
      });
      
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `assignments_export_${timestamp}.csv`;
      
      downloadFileFromBlob(response.data, filename);
      
      return {
        success: true,
        data: { message: 'Export downloaded successfully' },
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== CATEGORIES ====================

  /**
   * Get all assignment categories
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>}
   */
  getCategories: async (params = {}) => {
    const cacheKey = `categories_${JSON.stringify(params)}`;
    
    const cached = assignmentsCache.get(cacheKey);
    if (cached) {
      return {
        ...cached.value,
        fromCache: true
      };
    }
    
    try {
      const response = await api.get('/assignments/categories/', { params });
      
      const result = {
        success: true,
        data: response.data,
        status: response.status
      };
      
      assignmentsCache.set(cacheKey, result, 300000); // 5 minutes
      
      return result;
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Create a new category
   * @param {Object} categoryData - Category data
   * @returns {Promise<Object>}
   */
  createCategory: async (categoryData) => {
    try {
      const response = await api.post('/assignments/categories/', categoryData);
      
      // Clear categories cache
      assignmentsCache.delete(/^categories_/);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Category created successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== NOTIFICATIONS ====================

  /**
   * Get assignment notifications
   * @param {Object} params - Filter parameters
   * @returns {Promise<Object>}
   */
  getNotifications: async (params = {}) => {
    const cacheKey = `notifications_${JSON.stringify(params)}`;
    
    const cached = assignmentsCache.get(cacheKey);
    if (cached) {
      return {
        ...cached.value,
        fromCache: true
      };
    }
    
    try {
      const response = await api.get('/assignments/notifications/', { params });
      
      const result = {
        success: true,
        data: response.data,
        status: response.status
      };
      
      assignmentsCache.set(cacheKey, result, 30000); // 30 seconds
      
      return result;
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== BULK OPERATIONS ====================

  /**
   * Bulk create assignments
   * @param {Array} assignments - Array of assignment data
   * @returns {Promise<Object>}
   */
  bulkCreateAssignments: async (assignments) => {
    try {
      const response = await api.post('/assignments/bulk-create/', {
        assignments
      });
      
      // Clear assignments cache
      assignmentsCache.delete('assignments_{}');
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Assignments created successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Batch update assignment statuses
   * @param {Array<string>} assignmentIds - Array of assignment IDs
   * @param {string} status - New status
   * @returns {Promise<Object>}
   */
  batchUpdateStatus: async (assignmentIds, status) => {
    try {
      const response = await api.post('/assignments/batch-update-status/', {
        assignment_ids: assignmentIds,
        status
      });
      
      // Clear cache for affected assignments
      assignmentIds.forEach(id => {
        assignmentsCache.delete(`assignment_${id}`);
      });
      assignmentsCache.delete('assignments_{}');
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Statuses updated successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== SEARCH ====================

  /**
   * Search assignments
   * @param {string} query - Search query
   * @param {Object} params - Additional search parameters
   * @returns {Promise<Object>}
   */
  searchAssignments: async (query, params = {}) => {
    try {
      const response = await api.get('/assignments/search/', {
        params: { q: query, ...params }
      });
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== SYSTEM & ADMIN ====================

  /**
   * Health check for assignments module
   * @returns {Promise<Object>}
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/assignments/health-check/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Fix student assignments (admin only)
   * @param {string|number} assignmentId - Assignment ID
   * @returns {Promise<Object>}
   */
  fixStudentAssignments: async (assignmentId) => {
    try {
      const response = await api.post(`/assignments/${assignmentId}/fix-student-assignments/`);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        message: 'Student assignments fixed successfully'
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== CACHE MANAGEMENT ====================

  clearCache: () => {
    assignmentsCache.clear();
    console.log('🧹 Assignments cache cleared');
  },

  getCacheStats: () => {
    return assignmentsCache.getStats();
  },

  // ==================== HELPER FUNCTIONS ====================

  /**
   * Format assignment data for submission
   * @param {Object} data - Raw assignment data
   * @returns {Object} Formatted assignment data
   */
  formatAssignmentData: (data) => {
    const formatted = { ...data };
    
    // Convert dates to ISO string
    if (formatted.due_date) {
      formatted.due_date = new Date(formatted.due_date).toISOString();
    }
    
    if (formatted.available_from) {
      formatted.available_from = new Date(formatted.available_from).toISOString();
    }
    
    // Convert arrays to proper format if needed
    if (formatted.subject_ids && !Array.isArray(formatted.subject_ids)) {
      formatted.subject_ids = [formatted.subject_ids];
    }
    
    if (formatted.class_ids && !Array.isArray(formatted.class_ids)) {
      formatted.class_ids = [formatted.class_ids];
    }
    
    // Ensure numeric fields are numbers
    const numericFields = [
      'total_marks', 'passing_marks', 'estimated_completion_time',
      'late_submission_penalty', 'max_resubmissions', 'max_group_size'
    ];
    
    numericFields.forEach(field => {
      if (formatted[field] !== undefined) {
        formatted[field] = Number(formatted[field]);
      }
    });
    
    // Remove empty strings
    Object.keys(formatted).forEach(key => {
      if (formatted[key] === '') {
        delete formatted[key];
      }
    });
    
    return formatted;
  },

  /**
   * Parse assignment filters for API query
   * @param {Object} filters - Raw filter object from UI
   * @returns {Object} API-compatible filter parameters
   */
  parseAssignmentFilters: (filters) => {
    const params = {};
    
    if (filters.status && filters.status !== 'all') {
      params.status = filters.status;
    }
    
    if (filters.type && filters.type !== 'all') {
      params.assignment_type = filters.type;
    }
    
    if (filters.difficulty && filters.difficulty !== 'all') {
      params.difficulty_level = filters.difficulty;
    }
    
    if (filters.subject && filters.subject !== 'all') {
      params.subject_id = filters.subject;
    }
    
    if (filters.classroom && filters.classroom !== 'all') {
      params.classroom_id = filters.classroom;
    }
    
    if (filters.search) {
      params.search = filters.search;
    }
    
    if (filters.start_date) {
      params.start_date = new Date(filters.start_date).toISOString().split('T')[0];
    }
    
    if (filters.end_date) {
      params.end_date = new Date(filters.end_date).toISOString().split('T')[0];
    }
    
    if (filters.sort_by) {
      params.ordering = filters.sort_order === 'asc' 
        ? filters.sort_by 
        : `-${filters.sort_by}`;
    }
    
    // Pagination
    params.page = filters.page || 1;
    params.page_size = filters.pageSize || 20;
    
    return params;
  }
};

// Export the API instance for direct use
export { api };

export default assignmentsAPI;