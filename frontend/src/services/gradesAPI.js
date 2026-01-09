// gradesAPI.js - COMPLETE VERSION
import api from './api';

export const gradesAPI = {
  // ========== MAIN GRADES ENDPOINTS ==========
  
  // Get all student grades
  getGrades: async (params = {}) => {
    try {
      const response = await api.get('/grading/student-grades/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // Get teacher-specific grades
  getTeacherGrades: async (teacherId, params = {}) => {
    try {
      const response = await api.get('/grading/student-grades/', {
        params: {
          ...params,
          graded_by: teacherId
        }
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ========== EXISTING METHODS (keep these) ==========
  
  getByStudent: async (studentId, params = {}) => {
    try {
      const response = await api.get(`/grading/student-grades/?student=${studentId}`, { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  getByClass: async (classId, params = {}) => {
    try {
      const response = await api.get(`/grading/student-grades/?class=${classId}`, { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  create: async (gradeData) => {
    try {
      const response = await api.post('/grading/student-grades/', gradeData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  update: async (gradeId, gradeData) => {
    try {
      const response = await api.put(`/grading/student-grades/${gradeId}/`, gradeData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  delete: async (gradeId) => {
    try {
      const response = await api.delete(`/grading/student-grades/${gradeId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ========== ASSESSMENT ENDPOINTS ==========
  
  getAssessments: async (params = {}) => {
    try {
      const response = await api.get('/grading/assessments/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  createAssessment: async (assessmentData) => {
    try {
      const response = await api.post('/grading/assessments/', assessmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },
  // Get grades by class
getByClass: async (classId, params = {}) => {
  try {
    // Your backend likely needs to filter by class
    const response = await api.get('/grading/student-grades/', {
      params: {
        ...params,
        class: classId // Adjust this based on your backend filter field name
      }
    });
    return {
      success: true,
      data: response.data,
      status: response.status
    };
  } catch (error) {
    return {
      success: false,
      error: {
        message: error.response?.data?.error || error.message,
        status: error.response?.status
      }
    };
  }
},

  // ========== BULK OPERATIONS ==========
  
  bulkCreateGrades: async (gradesData) => {
    try {
      const response = await api.post('/grading/student-grades/bulk_create/', gradesData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // ========== STATISTICS & ANALYTICS ==========
  
  getStatistics: async (params = {}) => {
    try {
      const response = await api.get('/grading/statistics/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  getPerformanceTrends: async (params = {}) => {
    try {
      const response = await api.get('/grading/performance-trends/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ========== DASHBOARD ==========
  
  getDashboard: async () => {
    try {
      const response = await api.get('/grading/dashboard/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ========== GRADING PERIODS ==========
  
  getGradingPeriods: async (params = {}) => {
    try {
      const response = await api.get('/grading/grading-periods/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  getCurrentGradingPeriod: async () => {
    try {
      const response = await api.get('/grading/grading-periods/current/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ========== HELPER METHODS ==========
  
  calculateGrade: async (percentage) => {
    try {
      const response = await api.get('/grading/grading-scales/calculate_grade/', {
        params: { percentage }
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  }
};