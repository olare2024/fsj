import api from './api';

// ==================== LEARNING MANAGEMENT SYSTEM API ====================

export const notesAPI = {
  // ==================== CONTENT TYPES ====================
  
  // Get all content categories
  getCategories: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/categories/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get content by category
  getContentByCategory: async (categoryId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/notes/categories/${categoryId}/contents/`, {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get all tags
  getTags: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/tags/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== CONTENT ENDPOINTS ====================
  
  // Get text content
  getTextContent: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/text-content/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get video content
  getVideoContent: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/video-content/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get audio content
  getAudioContent: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/audio-content/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get PDF content
  getPDFContent: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/pdf-content/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get presentation content
  getPresentationContent: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/presentation-content/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get quiz content
  getQuizContent: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/quiz-content/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get assignment content
  getAssignmentContent: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/assignment-content/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get content by ID (generic endpoint)
  getContent: async (contentId, signal = null) => {
    try {
      // First try to get from specific endpoint, fallback to generic
      const response = await api.get(`/notes/content/${contentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== MODULE ENDPOINTS ====================
  
  // Get all learning modules
  getModules: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/modules/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get module by ID
  getModule: async (moduleId, signal = null) => {
    try {
      const response = await api.get(`/notes/modules/${moduleId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get module contents
  getModuleContents: async (moduleId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/notes/modules/${moduleId}/contents/`, {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get module analytics
  getModuleAnalytics: async (moduleId, signal = null) => {
    try {
      const response = await api.get(`/notes/modules/${moduleId}/analytics/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get my progress in a module
  getModuleProgress: async (moduleId, signal = null) => {
    try {
      const response = await api.get(`/notes/modules/${moduleId}/my-progress/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Enroll in a module
  enrollInModule: async (moduleId, signal = null) => {
    try {
      const response = await api.post(`/notes/modules/${moduleId}/enroll/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== ENROLLMENT ENDPOINTS ====================
  
  // Get my enrollments
  getMyEnrollments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/enrollments/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== PROGRESS ENDPOINTS ====================
  
  // Get content progress
  getContentProgress: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/content-progress/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update content progress
  updateContentProgress: async (contentId, progressData, signal = null) => {
    try {
      const response = await api.post(`/notes/content/${contentId}/update-progress/`, progressData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Bulk update progress
  bulkUpdateProgress: async (progressData, signal = null) => {
    try {
      const response = await api.post('/notes/content-progress/bulk-update/', progressData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== QUESTIONS & QUIZZES ====================
  
  // Get questions
  getQuestions: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/questions/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get quiz attempts
  getQuizAttempts: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/quiz-attempts/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Submit quiz answers
  submitQuizAnswers: async (attemptId, answersData, signal = null) => {
    try {
      const response = await api.post(`/notes/quiz-attempts/${attemptId}/submit-answers/`, answersData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== USER INTERACTION ENDPOINTS ====================
  
  // Get content notes
  getContentNotes: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/content-notes/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get content ratings
  getContentRatings: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/content-ratings/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== DASHBOARD ENDPOINTS ====================
  
  // Get student dashboard
  getStudentDashboard: async (signal = null) => {
    try {
      const response = await api.get('/notes/dashboard/student/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== SEARCH ENDPOINTS ====================
  
  // Advanced search
  searchContent: async (query, params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/search/', {
        params: { q: query, ...params },
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== ANALYTICS ENDPOINTS ====================
  
  // Get analytics
  getAnalytics: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/analytics/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get content analytics
  getContentAnalytics: async (contentId, signal = null) => {
    try {
      const response = await api.get(`/notes/content/${contentId}/analytics/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== RECOMMENDATION ENDPOINTS ====================
  
  // Get recommendations
  getRecommendations: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/notes/recommendations/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== BULK OPERATIONS ====================
  
  // Bulk operations
  bulkOperations: async (operationData, signal = null) => {
    try {
      const response = await api.post('/notes/bulk-operations/', operationData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== CONTENT MANAGEMENT ====================
  
  // Publish content
  publishContent: async (contentId, signal = null) => {
    try {
      const response = await api.post(`/notes/content/${contentId}/publish/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Unpublish content
  unpublishContent: async (contentId, signal = null) => {
    try {
      const response = await api.post(`/notes/content/${contentId}/unpublish/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== HEALTH CHECK ====================
  
  // Health check
  healthCheck: async (signal = null) => {
    try {
      const response = await api.get('/notes/health/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== BACKWARD COMPATIBILITY (for existing code) ====================
  
  // Get assignments (compatibility layer)
  getAssignments: async (params = {}, signal = null) => {
    return notesAPI.getAssignmentContent(params, signal);
  },

  // Get assignment by ID (compatibility layer)
  getAssignment: async (assignmentId, signal = null) => {
    return notesAPI.getContent(assignmentId, signal);
  },

  // Get submissions (compatibility layer - maps to quiz attempts)
  getSubmissions: async (params = {}, signal = null) => {
    return notesAPI.getQuizAttempts(params, signal);
  },

  // Get student assignments (compatibility layer)
  getStudentAssignments: async (params = {}, signal = null) => {
    return notesAPI.getAssignmentContent({
      ...params,
      student_view: true
    }, signal);
  },

  // Get teacher assignments (compatibility layer)
  getTeacherAssignments: async (params = {}, signal = null) => {
    return notesAPI.getAssignmentContent({
      ...params,
      teacher_view: true
    }, signal);
  },

  // Get notes (compatibility layer - maps to content notes)
  getNotes: async (params = {}, signal = null) => {
    return notesAPI.getContentNotes(params, signal);
  },

  // Get my notes (compatibility layer)
  getMyNotes: async (params = {}, signal = null) => {
    return notesAPI.getContentNotes({
      ...params,
      my_notes: true
    }, signal);
  },

  // Create note (compatibility layer)
  createNote: async (noteData, signal = null) => {
    try {
      const response = await api.post('/notes/content-notes/', noteData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  }
};

// ==================== HELPER FUNCTIONS ====================

const handleError = (error) => {
  if (error.name === 'AbortError') {
    return {
      success: false,
      error: {
        message: 'Request cancelled',
        code: 'CANCELLED'
      }
    };
  }

  if (!error.response) {
    return {
      success: false,
      error: {
        message: error.message || 'Network error',
        code: 'NETWORK_ERROR'
      }
    };
  }

  return {
    success: false,
    error: {
      message: error.response?.data?.error || error.response?.data?.detail || error.message,
      details: error.response?.data?.details || error.response?.data,
      status: error.response?.status,
      code: getErrorCode(error.response?.status)
    }
  };
};

const getErrorCode = (status) => {
  const codes = {
    400: 'VALIDATION_ERROR',
    401: 'UNAUTHORIZED',
    403: 'FORBIDDEN',
    404: 'NOT_FOUND',
    409: 'CONFLICT',
    422: 'UNPROCESSABLE_ENTITY',
    500: 'SERVER_ERROR'
  };
  return codes[status] || 'UNKNOWN_ERROR';
};

// ==================== CONSTANTS ====================

export const NOTES_CONSTANTS = {
  CONTENT_TYPES: {
    TEXT: 'text',
    VIDEO: 'video',
    AUDIO: 'audio',
    PDF: 'pdf',
    PRESENTATION: 'presentation',
    INTERACTIVE: 'interactive',
    QUIZ: 'quiz',
    ASSIGNMENT: 'assignment',
    LINK: 'link',
    FILE: 'file'
  },
  
  DIFFICULTY_LEVELS: {
    BEGINNER: 'beginner',
    INTERMEDIATE: 'intermediate',
    ADVANCED: 'advanced',
    EXPERT: 'expert'
  },
  
  MODULE_STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    ARCHIVED: 'archived'
  },
  
  ENROLLMENT_STATUS: {
    ACTIVE: 'active',
    COMPLETED: 'completed',
    DROPPED: 'dropped'
  },
  
  PROGRESS_STATUS: {
    NOT_STARTED: 'not_started',
    IN_PROGRESS: 'in_progress',
    COMPLETED: 'completed'
  },
  
  QUESTION_TYPES: {
    MULTIPLE_CHOICE: 'multiple_choice',
    TRUE_FALSE: 'true_false',
    SHORT_ANSWER: 'short_answer',
    ESSAY: 'essay',
    FILL_BLANK: 'fill_blank',
    MATCHING: 'matching',
    ORDERING: 'ordering'
  },
  
  QUIZ_STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    CLOSED: 'closed'
  },
  
  ATTEMPT_STATUS: {
    IN_PROGRESS: 'in_progress',
    SUBMITTED: 'submitted',
    GRADED: 'graded'
  },
  
  NOTE_TYPES: {
    PERSONAL: 'personal',
    HIGHLIGHT: 'highlight',
    QUESTION: 'question',
    SUMMARY: 'summary'
  },
  
  RATING_VALUES: {
    ONE: 1,
    TWO: 2,
    THREE: 3,
    FOUR: 4,
    FIVE: 5
  }
};

export default notesAPI;