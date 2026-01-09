// services/assignmentsAPI.js
import api from './api';

export const ASSIGNMENT_CONSTANTS = {
  STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    CLOSED: 'closed',
    GRADED: 'graded',
    ARCHIVED: 'archived'
  },
  TYPES: {
    HOMEWORK: 'homework',
    CLASSWORK: 'classwork',
    PROJECT: 'project',
    QUIZ: 'quiz',
    TEST: 'test',
    EXAM: 'exam',
    PRACTICAL: 'practical'
  },
  DIFFICULTY: {
    EASY: 'easy',
    MEDIUM: 'medium',
    HARD: 'hard'
  }
};

export const assignmentsAPI = {
  // ==================== ASSIGNMENTS CRUD ====================
  getAssignments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/teachers/assignments/', { 
        params,
        signal
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
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  getMyAssignments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/teachers/assignments/my/', { 
        params,
        signal
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
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  getAssignmentById: async (assignmentId) => {
    try {
      const response = await api.get(`/teachers/assignments/${assignmentId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  createAssignment: async (assignmentData) => {
    try {
      const response = await api.post('/teachers/assignments/', assignmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  updateAssignment: async (assignmentId, assignmentData) => {
    try {
      const response = await api.patch(`/teachers/assignments/${assignmentId}/`, assignmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  deleteAssignment: async (assignmentId) => {
    try {
      const response = await api.delete(`/teachers/assignments/${assignmentId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== ASSIGNMENT ACTIONS ====================
  publishAssignment: async (assignmentId) => {
    try {
      const response = await api.post(`/teachers/assignments/${assignmentId}/publish/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  unpublishAssignment: async (assignmentId) => {
    try {
      const response = await api.post(`/teachers/assignments/${assignmentId}/unpublish/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  closeAssignment: async (assignmentId) => {
    try {
      const response = await api.post(`/teachers/assignments/${assignmentId}/close/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  duplicateAssignment: async (assignmentId, duplicateData = {}) => {
    try {
      const response = await api.post(`/teachers/assignments/${assignmentId}/duplicate/`, duplicateData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== STATISTICS ====================
  getTeacherStats: async () => {
    try {
      const response = await api.get('/teachers/assignments/statistics/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== SUBMISSIONS ====================
  getSubmissions: async (assignmentId, params = {}) => {
    try {
      const response = await api.get(`/teachers/assignments/${assignmentId}/submissions/`, { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  gradeSubmission: async (submissionId, gradeData) => {
    try {
      const response = await api.post(`/teachers/submissions/${submissionId}/grade/`, gradeData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  bulkGradeSubmissions: async (assignmentId, gradeData) => {
    try {
      const response = await api.post(`/teachers/assignments/${assignmentId}/bulk-grade/`, gradeData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== EXPORTS ====================
  exportAssignments: async (format = 'csv', params = {}) => {
    try {
      const response = await api.get(`/teachers/assignments/export/${format}/`, {
        params,
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `assignments_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      return {
        success: true,
        data: { message: 'Export downloaded successfully' },
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== ANALYTICS ====================
  getAssignmentAnalytics: async (assignmentId) => {
    try {
      const response = await api.get(`/teachers/assignments/${assignmentId}/analytics/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== UTILITY ====================
  searchAssignments: async (query, params = {}) => {
    try {
      const response = await api.get('/teachers/assignments/search/', {
        params: { q: query, ...params }
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
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== BULK ACTIONS ====================
  bulkUpdateAssignments: async (assignmentIds, updateData) => {
    try {
      const response = await api.post('/teachers/assignments/bulk-update/', {
        assignment_ids: assignmentIds,
        ...updateData
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
          message: error.response?.data?.detail || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  bulkDeleteAssignments: async (assignmentIds) => {
    try {
      const response = await api.post('/teachers/assignments/bulk-delete/', {
        assignment_ids: assignmentIds
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
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  }
};