import api from './api';

const handleReportsError = (error, context = 'Reports API') => {
  console.error(`❌ ${context} error:`, error.response?.data || error.message);
  
  if (error.response) {
    return {
      success: false,
      message: error.response.data?.detail || 
              error.response.data?.error || 
              error.response.data?.message || 
              'Report operation failed',
      errors: error.response.data?.errors || error.response.data?.details,
      status: error.response.status
    };
  }
  
  if (error.request) {
    return {
      success: false,
      message: 'Network error: Unable to connect to reporting services',
      status: 0
    };
  }
  
  return {
    success: false,
    message: error.message || 'Report operation failed',
    status: 'unknown'
  };
};

export const reportsAPI = {
  // ==================== REPORT GENERATION ====================
  
  /**
   * Generate Report - Head Teacher Portal calls this
   * POST /reports/generate/
   */
  generateReport: async (reportData) => {
    try {
      console.log('📊 Generating report:', reportData);
      const response = await api.post('/reports/generate/', reportData);
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'Report generated successfully',
        status: response.status,
        report_url: response.data.report_url || response.data.url
      };
    } catch (error) {
      return handleReportsError(error, 'Generate Report');
    }
  },

  /**
   * Generate Academic Report
   * POST /reports/academic/
   */
  generateAcademicReport: async (params = {}) => {
    try {
      const response = await api.post('/reports/academic/', params);
      
      return {
        success: true,
        data: response.data,
        message: 'Academic report generated successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Generate Academic Report');
    }
  },

  /**
   * Generate Attendance Report
   * POST /reports/attendance/
   */
  generateAttendanceReport: async (params = {}) => {
    try {
      const response = await api.post('/reports/attendance/', params);
      
      return {
        success: true,
        data: response.data,
        message: 'Attendance report generated successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Generate Attendance Report');
    }
  },

  /**
   * Generate Discipline Report
   * POST /reports/discipline/
   */
  generateDisciplineReport: async (params = {}) => {
    try {
      const response = await api.post('/reports/discipline/', params);
      
      return {
        success: true,
        data: response.data,
        message: 'Discipline report generated successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Generate Discipline Report');
    }
  },

  /**
   * Generate Staff Performance Report
   * POST /reports/staff/
   */
  generateStaffReport: async (params = {}) => {
    try {
      const response = await api.post('/reports/staff/', params);
      
      return {
        success: true,
        data: response.data,
        message: 'Staff report generated successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Generate Staff Report');
    }
  },

  /**
   * Generate Financial Report
   * POST /reports/financial/
   */
  generateFinancialReport: async (params = {}) => {
    try {
      const response = await api.post('/reports/financial/', params);
      
      return {
        success: true,
        data: response.data,
        message: 'Financial report generated successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Generate Financial Report');
    }
  },

  /**
   * Generate Comprehensive School Report
   * POST /reports/comprehensive/
   */
  generateComprehensiveReport: async (params = {}) => {
    try {
      const response = await api.post('/reports/comprehensive/', params);
      
      return {
        success: true,
        data: response.data,
        message: 'Comprehensive report generated successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Generate Comprehensive Report');
    }
  },

  // ==================== REPORT MANAGEMENT ====================
  
  /**
   * Get Generated Reports
   * GET /reports/
   */
  getReports: async (params = {}) => {
    try {
      const response = await api.get('/reports/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        next: response.data.next,
        previous: response.data.previous,
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Reports');
    }
  },

  /**
   * Get Specific Report
   * GET /reports/{id}/
   */
  getReport: async (reportId) => {
    try {
      const response = await api.get(`/reports/${reportId}/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Report details fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Report');
    }
  },

  /**
   * Download Report
   * GET /reports/{id}/download/
   */
  downloadReport: async (reportId) => {
    try {
      const response = await api.get(`/reports/${reportId}/download/`, {
        responseType: 'blob'
      });
      
      return {
        success: true,
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || `report-${reportId}.pdf`,
        message: 'Report downloaded successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Download Report');
    }
  },

  /**
   * Delete Report
   * DELETE /reports/{id}/
   */
  deleteReport: async (reportId) => {
    try {
      const response = await api.delete(`/reports/${reportId}/`);
      
      return {
        success: true,
        message: 'Report deleted successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Delete Report');
    }
  },

  /**
   * Email Report
   * POST /reports/{id}/email/
   */
  emailReport: async (reportId, emailData = {}) => {
    try {
      const response = await api.post(`/reports/${reportId}/email/`, emailData);
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'Report emailed successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Email Report');
    }
  },

  // ==================== REPORT TEMPLATES ====================
  
  /**
   * Get Report Templates
   * GET /reports/templates/
   */
  getTemplates: async (params = {}) => {
    try {
      const response = await api.get('/reports/templates/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Templates');
    }
  },

  /**
   * Get Template
   * GET /reports/templates/{id}/
   */
  getTemplate: async (templateId) => {
    try {
      const response = await api.get(`/reports/templates/${templateId}/`);
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Template');
    }
  },

  // ==================== REPORT SCHEDULING ====================
  
  /**
   * Schedule Report
   * POST /reports/schedule/
   */
  scheduleReport: async (scheduleData) => {
    try {
      const response = await api.post('/reports/schedule/', scheduleData);
      
      return {
        success: true,
        data: response.data,
        message: 'Report scheduled successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Schedule Report');
    }
  },

  /**
   * Get Scheduled Reports
   * GET /reports/schedules/
   */
  getScheduledReports: async (params = {}) => {
    try {
      const response = await api.get('/reports/schedules/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Scheduled Reports');
    }
  },

  /**
   * Cancel Scheduled Report
   * DELETE /reports/schedules/{id}/
   */
  cancelScheduledReport: async (scheduleId) => {
    try {
      const response = await api.delete(`/reports/schedules/${scheduleId}/`);
      
      return {
        success: true,
        message: 'Report schedule cancelled successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Cancel Scheduled Report');
    }
  },

  // ==================== ANALYTICS & INSIGHTS ====================
  
  /**
   * Get Report Analytics
   * GET /reports/analytics/
   */
  getReportAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/reports/analytics/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Report analytics fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Report Analytics');
    }
  },

  /**
   * Get Most Generated Reports
   * GET /reports/most-generated/
   */
  getMostGeneratedReports: async (params = {}) => {
    try {
      const response = await api.get('/reports/most-generated/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Most generated reports fetched',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Most Generated Reports');
    }
  },

  /**
   * Get Report Usage Statistics
   * GET /reports/usage-stats/
   */
  getUsageStats: async (params = {}) => {
    try {
      const response = await api.get('/reports/usage-stats/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Usage statistics fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Usage Stats');
    }
  },

  // ==================== BULK OPERATIONS ====================
  
  /**
   * Bulk Delete Reports
   * POST /reports/bulk-delete/
   */
  bulkDeleteReports: async (reportIds) => {
    try {
      const response = await api.post('/reports/bulk-delete/', {
        report_ids: reportIds
      });
      
      return {
        success: true,
        data: response.data,
        message: 'Reports deleted successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Bulk Delete Reports');
    }
  },

  /**
   * Bulk Export Reports
   * POST /reports/bulk-export/
   */
  bulkExportReports: async (reportIds, format = 'zip') => {
    try {
      const response = await api.post('/reports/bulk-export/', {
        report_ids: reportIds,
        format: format
      }, {
        responseType: 'blob'
      });
      
      return {
        success: true,
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || `reports-${Date.now()}.${format}`,
        message: 'Reports exported successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Bulk Export Reports');
    }
  },

  // ==================== UTILITIES ====================
  
  /**
   * Get Report Formats
   * GET /reports/formats/
   */
  getReportFormats: async () => {
    try {
      const response = await api.get('/reports/formats/');
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Report Formats');
    }
  },

  /**
   * Validate Report Parameters
   * POST /reports/validate/
   */
  validateReportParams: async (params) => {
    try {
      const response = await api.post('/reports/validate/', params);
      
      return {
        success: true,
        data: response.data,
        message: response.data.message || 'Parameters validated successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Validate Report Params');
    }
  },

  /**
   * Get Report Generation Status
   * GET /reports/{id}/status/
   */
  getReportStatus: async (reportId) => {
    try {
      const response = await api.get(`/reports/${reportId}/status/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Report status fetched',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Report Status');
    }
  },

  /**
   * Get Quick Stats (for dashboard)
   * GET /reports/quick-stats/
   */
  getQuickStats: async () => {
    try {
      const response = await api.get('/reports/quick-stats/');
      
      return {
        success: true,
        data: response.data,
        message: 'Quick stats fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Get Quick Stats');
    }
  },

  /**
   * Search Reports
   * GET /reports/search/
   */
  searchReports: async (query, params = {}) => {
    try {
      const response = await api.get('/reports/search/', {
        params: { q: query, ...params }
      });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        status: response.status
      };
    } catch (error) {
      return handleReportsError(error, 'Search Reports');
    }
  }
};