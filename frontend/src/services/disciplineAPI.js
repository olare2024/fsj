import api from './api';

const handleDisciplineError = (error, context = 'Discipline API') => {
  console.error(`❌ ${context} error:`, error.response?.data || error.message);
  
  if (error.response) {
    return {
      success: false,
      message: error.response.data?.detail || 
              error.response.data?.error || 
              error.response.data?.message || 
              'Discipline operation failed',
      errors: error.response.data?.errors || error.response.data?.details,
      status: error.response.status
    };
  }
  
  if (error.request) {
    return {
      success: false,
      message: 'Network error: Unable to connect to discipline services',
      status: 0
    };
  }
  
  return {
    success: false,
    message: error.message || 'Discipline operation failed',
    status: 'unknown'
  };
};

export const disciplineAPI = {
  // ==================== DISCIPLINE CASES ====================
  
  /**
   * Get Recent Cases - Head Teacher Portal calls this
   * GET /discipline/cases/?limit=20&status=pending
   */
  getRecentCases: async (params = {}) => {
    try {
      const defaultParams = { limit: 20, status: 'pending', ...params };
      const response = await api.get('/discipline/cases/', { params: defaultParams });
      
      console.log('📋 Recent discipline cases fetched:', response.data?.count || response.data?.length || 0);
      
      return {
        success: true,
        data: response.data.results || response.data.cases || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Discipline cases fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Recent Cases');
    }
  },

  /**
   * Get All Discipline Cases with filtering
   * GET /discipline/cases/
   */
  getAllCases: async (params = {}) => {
    try {
      const response = await api.get('/discipline/cases/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        next: response.data.next,
        previous: response.data.previous,
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get All Cases');
    }
  },

  /**
   * Get Specific Case
   * GET /discipline/cases/{id}/
   */
  getCase: async (caseId) => {
    try {
      const response = await api.get(`/discipline/cases/${caseId}/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Case details fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Case');
    }
  },

  /**
   * Resolve Case - Head Teacher Portal calls this
   * POST /discipline/cases/{id}/resolve/
   */
  resolveCase: async (caseId, resolutionData) => {
    try {
      console.log('🔨 Resolving discipline case:', caseId, resolutionData);
      const response = await api.post(`/discipline/cases/${caseId}/resolve/`, resolutionData);
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'Case resolved successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Resolve Case');
    }
  },

  /**
   * Create New Case
   * POST /discipline/cases/
   */
  createCase: async (caseData) => {
    try {
      const response = await api.post('/discipline/cases/', caseData);
      
      return {
        success: true,
        data: response.data,
        message: 'Discipline case created successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Create Case');
    }
  },

  /**
   * Update Case
   * PUT /discipline/cases/{id}/
   */
  updateCase: async (caseId, caseData) => {
    try {
      const response = await api.put(`/discipline/cases/${caseId}/`, caseData);
      
      return {
        success: true,
        data: response.data,
        message: 'Case updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Update Case');
    }
  },

  /**
   * Delete Case
   * DELETE /discipline/cases/{id}/
   */
  deleteCase: async (caseId) => {
    try {
      const response = await api.delete(`/discipline/cases/${caseId}/`);
      
      return {
        success: true,
        message: 'Case deleted successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Delete Case');
    }
  },

  // ==================== DISCIPLINE TYPES ====================
  
  /**
   * Get Discipline Types/Offenses
   * GET /discipline/types/
   */
  getDisciplineTypes: async (params = {}) => {
    try {
      const response = await api.get('/discipline/types/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Discipline Types');
    }
  },

  /**
   * Get Specific Discipline Type
   * GET /discipline/types/{id}/
   */
  getDisciplineType: async (typeId) => {
    try {
      const response = await api.get(`/discipline/types/${typeId}/`);
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Discipline Type');
    }
  },

  // ==================== DISCIPLINE ACTIONS ====================
  
  /**
   * Get Available Actions
   * GET /discipline/actions/
   */
  getActions: async (params = {}) => {
    try {
      const response = await api.get('/discipline/actions/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Actions');
    }
  },

  /**
   * Apply Action to Case
   * POST /discipline/cases/{id}/actions/
   */
  applyAction: async (caseId, actionData) => {
    try {
      const response = await api.post(`/discipline/cases/${caseId}/actions/`, actionData);
      
      return {
        success: true,
        data: response.data,
        message: 'Action applied successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Apply Action');
    }
  },

  // ==================== REPORTS & STATISTICS ====================
  
  /**
   * Get Discipline Statistics
   * GET /discipline/statistics/
   */
  getStatistics: async (params = {}) => {
    try {
      const response = await api.get('/discipline/statistics/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Statistics fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Statistics');
    }
  },

  /**
   * Get Cases by Student
   * GET /discipline/students/{studentId}/cases/
   */
  getStudentCases: async (studentId, params = {}) => {
    try {
      const response = await api.get(`/discipline/students/${studentId}/cases/`, { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Student Cases');
    }
  },

  /**
   * Get Cases by Class
   * GET /discipline/classes/{classId}/cases/
   */
  getClassCases: async (classId, params = {}) => {
    try {
      const response = await api.get(`/discipline/classes/${classId}/cases/`, { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Class Cases');
    }
  },

  /**
   * Get Monthly Trend
   * GET /discipline/trends/monthly/
   */
  getMonthlyTrend: async (params = {}) => {
    try {
      const response = await api.get('/discipline/trends/monthly/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Monthly trend fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Monthly Trend');
    }
  },

  // ==================== BULK OPERATIONS ====================
  
  /**
   * Bulk Update Cases
   * POST /discipline/cases/bulk-update/
   */
  bulkUpdateCases: async (caseIds, updateData) => {
    try {
      const response = await api.post('/discipline/cases/bulk-update/', {
        case_ids: caseIds,
        ...updateData
      });
      
      return {
        success: true,
        data: response.data,
        message: 'Cases updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Bulk Update Cases');
    }
  },

  /**
   * Export Cases
   * GET /discipline/cases/export/
   */
  exportCases: async (params = {}) => {
    try {
      const response = await api.get('/discipline/cases/export/', { 
        params,
        responseType: 'blob'
      });
      
      return {
        success: true,
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || 'discipline-cases.csv',
        message: 'Cases exported successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Export Cases');
    }
  },

  // ==================== UTILITIES ====================
  
  /**
   * Search Cases
   * GET /discipline/cases/search/
   */
  searchCases: async (query, params = {}) => {
    try {
      const response = await api.get('/discipline/cases/search/', {
        params: { q: query, ...params }
      });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Search Cases');
    }
  },

  /**
   * Get Dashboard Overview
   * GET /discipline/dashboard/
   */
  getDashboardOverview: async () => {
    try {
      const response = await api.get('/discipline/dashboard/');
      
      return {
        success: true,
        data: response.data,
        message: 'Dashboard overview fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Dashboard Overview');
    }
  },

  /**
   * Get Case Status Counts
   * GET /discipline/cases/status-counts/
   */
  getStatusCounts: async () => {
    try {
      const response = await api.get('/discipline/cases/status-counts/');
      
      return {
        success: true,
        data: response.data,
        message: 'Status counts fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Get Status Counts');
    }
  },

  // ==================== NOTIFICATIONS ====================
  
  /**
   * Notify Parents/Guardians
   * POST /discipline/cases/{id}/notify/
   */
  notifyStakeholders: async (caseId, notificationData = {}) => {
    try {
      const response = await api.post(`/discipline/cases/${caseId}/notify/`, notificationData);
      
      return {
        success: true,
        data: response.data,
        message: 'Stakeholders notified successfully',
        status: response.status
      };
    } catch (error) {
      return handleDisciplineError(error, 'Notify Stakeholders');
    }
  }
};