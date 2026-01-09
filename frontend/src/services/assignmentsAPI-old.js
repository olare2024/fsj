import api from './api';

// ==================== ERROR HANDLER ====================
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

// ==================== ASSIGNMENTS API ====================

export const assignmentsAPI = {
  // ==================== ASSIGNMENT MANAGEMENT ====================
  
  getAssignments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/', {
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

  getAssignment: async (assignmentId, signal = null) => {
    try {
      const response = await api.get(`/assignments/assignments/${assignmentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // FIXED: createAssignment with better error handling
  createAssignment: async (assignmentData) => {
    try {
      console.log('📝 Creating assignment:', assignmentData);
      
      // Process data to ensure proper formats
      const processedData = { ...assignmentData };
      
      // Ensure UUID fields are strings
      const uuidFields = ['academic_year', 'term', 'subject', 'classroom', 'teacher', 'stream', 'category'];
      uuidFields.forEach(field => {
        if (processedData[field] && typeof processedData[field] !== 'string') {
          processedData[field] = String(processedData[field]);
        }
      });
      
      // Ensure numeric fields are numbers
      const numericFields = ['total_marks', 'passing_marks', 'estimated_completion_time', 
                            'late_submission_penalty', 'max_resubmissions', 'max_group_size'];
      numericFields.forEach(field => {
        if (processedData[field] !== undefined && processedData[field] !== null) {
          processedData[field] = Number(processedData[field]);
        }
      });
      
      // Ensure boolean fields are booleans
      const booleanFields = ['allow_late_submission', 'allow_resubmission', 'require_approval', 'is_group_assignment'];
      booleanFields.forEach(field => {
        if (processedData[field] !== undefined && processedData[field] !== null) {
          processedData[field] = Boolean(processedData[field]);
        }
      });
      
      console.log('📤 Sending processed data:', processedData);
      
      const response = await api.post('/assignments/assignments/', processedData);
      console.log('✅ Assignment created:', response.data);
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error creating assignment:', error);
      console.error('Error response:', error.response?.data);
      
      let errorMessage = 'Failed to create assignment';
      let errorDetails = null;
      
      if (error.response?.data) {
        const errorData = error.response.data;
        errorDetails = errorData;
        
        // Parse Django error response
        if (typeof errorData === 'object') {
          console.log('Error data object:', errorData);
          
          // Build user-friendly error messages
          const fieldErrors = [];
          
          // Check for common field errors
          const fieldMapping = {
            'academic_year': 'Academic Year',
            'term': 'Term',
            'subject': 'Subject',
            'classroom': 'Class',
            'teacher': 'Teacher',
            'title': 'Title',
            'due_date': 'Due Date'
          };
          
          for (const [field, messages] of Object.entries(errorData)) {
            const fieldName = fieldMapping[field] || field.replace(/_/g, ' ');
            
            if (Array.isArray(messages)) {
              const cleanMessage = messages[0].replace(/This field |Invalid pk |Expected a /gi, '');
              fieldErrors.push(`${fieldName}: ${cleanMessage}`);
            } else if (typeof messages === 'string') {
              fieldErrors.push(`${fieldName}: ${messages}`);
            }
          }
          
          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors.join('; ');
          } else if (errorData.non_field_errors) {
            if (Array.isArray(errorData.non_field_errors)) {
              errorMessage = errorData.non_field_errors[0];
            } else {
              errorMessage = errorData.non_field_errors;
            }
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          }
          
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      }
      
      return {
        success: false,
        error: {
          message: errorMessage,
          details: errorDetails,
          status: error.response?.status,
          statusText: error.response?.statusText
        }
      };
    }
  },

  updateAssignment: async (assignmentId, assignmentData, signal = null) => {
    try {
      const response = await api.patch(`/assignments/assignments/${assignmentId}/`, assignmentData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  deleteAssignment: async (assignmentId, signal = null) => {
    try {
      const response = await api.delete(`/assignments/assignments/${assignmentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  publishAssignment: async (assignmentId, signal = null) => {
    try {
      const response = await api.post(`/assignments/assignments/${assignmentId}/publish/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  unpublishAssignment: async (assignmentId, signal = null) => {
    try {
      const response = await api.post(`/assignments/assignments/${assignmentId}/unpublish/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  closeAssignment: async (assignmentId, signal = null) => {
    try {
      const response = await api.post(`/assignments/assignments/${assignmentId}/close/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  duplicateAssignment: async (assignmentId, duplicateData = {}, signal = null) => {
    try {
      const response = await api.post(`/assignments/assignments/${assignmentId}/duplicate/`, duplicateData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  getAssignmentStats: async (assignmentId, signal = null) => {
    try {
      const response = await api.get(`/assignments/assignments/${assignmentId}/stats/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  getAssignmentAnalytics: async (assignmentId, signal = null) => {
    try {
      const response = await api.get(`/assignments/assignments/${assignmentId}/analytics/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  getAssignmentSubmissions: async (assignmentId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/assignments/assignments/${assignmentId}/submissions/`, {
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

  uploadAssignmentAttachment: async (assignmentId, fileData, signal = null) => {
    try {
      const response = await api.post(`/assignments/assignments/${assignmentId}/upload-attachment/`, fileData, {
        headers: { 'Content-Type': 'multipart/form-data' },
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

  // ==================== STUDENT ASSIGNMENTS ====================
  
  getStudentAssignments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/', {
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

  getStudentAssignment: async (studentAssignmentId, signal = null) => {
    try {
      const response = await api.get(`/assignments/student-assignments/${studentAssignmentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  submitAssignment: async (studentAssignmentId, submissionData, signal = null) => {
    try {
      const response = await api.post(`/assignments/student-assignments/${studentAssignmentId}/submit/`, submissionData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  gradeAssignment: async (studentAssignmentId, gradeData, signal = null) => {
    try {
      const response = await api.post(`/assignments/student-assignments/${studentAssignmentId}/grade/`, gradeData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  allowResubmission: async (studentAssignmentId, feedback = '', signal = null) => {
    try {
      const response = await api.post(`/assignments/student-assignments/${studentAssignmentId}/allow-resubmission/`, 
        { feedback }, 
        { signal }
      );
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  returnForRevision: async (studentAssignmentId, feedback = '', signal = null) => {
    try {
      const response = await api.post(`/assignments/student-assignments/${studentAssignmentId}/return-for-revision/`, 
        { feedback }, 
        { signal }
      );
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  getSubmissionHistory: async (studentAssignmentId, signal = null) => {
    try {
      const response = await api.get(`/assignments/student-assignments/${studentAssignmentId}/submission-history/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  uploadSubmissionAttachment: async (studentAssignmentId, fileData, signal = null) => {
    try {
      const response = await api.post(`/assignments/student-assignments/${studentAssignmentId}/upload-attachment/`, fileData, {
        headers: { 'Content-Type': 'multipart/form-data' },
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

  // ==================== ASSIGNMENT CATEGORIES ====================
  
  getCategories: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/categories/', {
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

  getCategory: async (categoryId, signal = null) => {
    try {
      const response = await api.get(`/assignments/categories/${categoryId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  createCategory: async (categoryData, signal = null) => {
    try {
      const response = await api.post('/assignments/categories/', categoryData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  updateCategory: async (categoryId, categoryData, signal = null) => {
    try {
      const response = await api.patch(`/assignments/categories/${categoryId}/`, categoryData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  deleteCategory: async (categoryId, signal = null) => {
    try {
      const response = await api.delete(`/assignments/categories/${categoryId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== GRADE SCALES ====================
  
  getGradeScales: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/grade-scales/', {
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

  getGradeScale: async (gradeScaleId, signal = null) => {
    try {
      const response = await api.get(`/assignments/grade-scales/${gradeScaleId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== ASSIGNMENT GROUPS ====================
  
  getGroups: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/groups/', {
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

  getGroup: async (groupId, signal = null) => {
    try {
      const response = await api.get(`/assignments/groups/${groupId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  createGroup: async (groupData, signal = null) => {
    try {
      const response = await api.post('/assignments/groups/', groupData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  updateGroup: async (groupId, groupData, signal = null) => {
    try {
      const response = await api.patch(`/assignments/groups/${groupId}/`, groupData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  deleteGroup: async (groupId, signal = null) => {
    try {
      const response = await api.delete(`/assignments/groups/${groupId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== GROUP MEMBERSHIPS ====================
  
  getGroupMemberships: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/group-memberships/', {
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

  addStudentToGroup: async (groupMembershipData, signal = null) => {
    try {
      const response = await api.post('/assignments/group-memberships/', groupMembershipData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  removeStudentFromGroup: async (membershipId, signal = null) => {
    try {
      const response = await api.delete(`/assignments/group-memberships/${membershipId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== COMMENTS ====================
  
  getComments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/comments/', {
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

  getComment: async (commentId, signal = null) => {
    try {
      const response = await api.get(`/assignments/comments/${commentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  addComment: async (commentData, signal = null) => {
    try {
      const response = await api.post('/assignments/comments/', commentData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  updateComment: async (commentId, commentData, signal = null) => {
    try {
      const response = await api.patch(`/assignments/comments/${commentId}/`, commentData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  deleteComment: async (commentId, signal = null) => {
    try {
      const response = await api.delete(`/assignments/comments/${commentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  getAssignmentComments: async (assignmentId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/assignments/assignments/${assignmentId}/comments/`, {
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

  // ==================== DASHBOARD & ANALYTICS ====================
  
  getDashboard: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/dashboard/', {
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

  getTeacherStats: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/teacher-stats/', {
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

  getStudentProgress: async (studentId = null, params = {}, signal = null) => {
    try {
      const endpoint = studentId 
        ? `/assignments/student-progress/${studentId}/`
        : '/assignments/student-progress/';
      
      const response = await api.get(endpoint, {
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

  // ==================== COLLECTION ENDPOINTS ====================
  
  getMyAssignments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/my-assignments/', {
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

  getUpcomingAssignments: async (days = 7, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/upcoming/', {
        params: { days, ...params },
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

  getOverdueAssignments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/overdue/', {
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

  getAssignmentNotifications: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/notifications/', {
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

  getPendingGrading: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/pending-grading/', {
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

  getMySubmissions: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/my-submissions/', {
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

  getStudentAssignmentsByAssignment: async (assignmentId, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/by-assignment/', {
        params: { assignment_id: assignmentId, ...params },
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

  getStudentAssignmentsByStudent: async (studentId, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/by-student/', {
        params: { student_id: studentId, ...params },
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

  getStudentAssignmentsByStatus: async (status, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/by-status/', {
        params: { status, ...params },
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

  getLateSubmissions: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/late-submissions/', {
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

  // ==================== SEARCH & FILTER ====================
  
  searchAssignments: async (query, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/', {
        params: { search: query, ...params },
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

  filterAssignments: async (filters = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/', {
        params: filters,
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

  getAssignmentsByStatus: async (status, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/', {
        params: { status, ...params },
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

  getAssignmentsByClass: async (classId, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/', {
        params: { classroom: classId, ...params },
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

  getAssignmentsBySubject: async (subjectId, params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/', {
        params: { subject: subjectId, ...params },
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
  
  bulkCreateAssignments: async (assignmentsData, signal = null) => {
    try {
      const response = await api.post('/assignments/assignments/bulk-create/', assignmentsData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  bulkGradeAssignments: async (gradingData, signal = null) => {
    try {
      const response = await api.post('/assignments/student-assignments/bulk-grade/', gradingData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  bulkUpdateAssignments: async (updateData, signal = null) => {
    try {
      const response = await api.post('/assignments/assignments/bulk-update/', updateData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== EXPORT & IMPORT ====================
  
  exportAssignments: async (format = 'csv', params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/assignments/export/', {
        params: { format, ...params },
        responseType: 'blob',
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status,
        format: format
      };
    } catch (error) {
      return handleError(error);
    }
  },

  exportGrades: async (format = 'csv', params = {}, signal = null) => {
    try {
      const response = await api.get('/assignments/student-assignments/export-grades/', {
        params: { format, ...params },
        responseType: 'blob',
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status,
        format: format
      };
    } catch (error) {
      return handleError(error);
    }
  },

  importGrades: async (fileData, signal = null) => {
    try {
      const response = await api.post('/assignments/student-assignments/import-grades/', fileData, {
        headers: { 'Content-Type': 'multipart/form-data' },
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

  // ==================== COMPATIBILITY LAYER ====================
  
  getStudentAssignmentsOld: async (studentId, params = {}, signal = null) => {
    return assignmentsAPI.getStudentAssignmentsByStudent(studentId, params, signal);
  },

  submitAssignmentOld: async (assignmentId, submissionData, signal = null) => {
    return assignmentsAPI.submitAssignment(assignmentId, submissionData, signal);
  }
};

// ==================== ASSIGNMENT CONSTANTS ====================

export const ASSIGNMENT_CONSTANTS = {
  TYPES: {
    HOMEWORK: 'homework',
    CLASSWORK: 'classwork',
    PROJECT: 'project',
    QUIZ: 'quiz',
    TEST: 'test',
    EXAM: 'exam',
    PRACTICAL: 'practical',
    PRESENTATION: 'presentation',
    RESEARCH: 'research',
    REVISION: 'revision',
    ASSESSMENT: 'assessment'
  },

  STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    IN_PROGRESS: 'in_progress',
    CLOSED: 'closed',
    GRADED: 'graded',
    ARCHIVED: 'archived'
  },

  STUDENT_STATUS: {
    NOT_SUBMITTED: 'not_submitted',
    SUBMITTED: 'submitted',
    LATE: 'late',
    GRADED: 'graded',
    RETURNED: 'returned',
    RESUBMITTED: 'resubmitted'
  },

  DIFFICULTY: {
    EASY: 'easy',
    MEDIUM: 'medium',
    HARD: 'hard',
    CHALLENGING: 'challenging'
  },

  CURRICULUM: {
    CBC: 'cbc',
    EIGHT_FOUR_FOUR: '8-4-4',
    IGCSE: 'igcse'
  },

  CORE_COMPETENCIES: {
    COMMUNICATION: 'communication',
    CRITICAL_THINKING: 'critical_thinking',
    CREATIVITY: 'creativity',
    CITIZENSHIP: 'citizenship',
    LEARNING_TO_LEARN: 'learning_to_learn',
    SELF_EFFICACY: 'self_efficacy',
    DIGITAL_LITERACY: 'digital_literacy'
  },

  PRIORITY: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    CRITICAL: 'critical'
  },

  FILE_TYPES: {
    PDF: 'pdf',
    DOC: 'doc',
    DOCX: 'docx',
    PPT: 'ppt',
    PPTX: 'pptx',
    XLS: 'xls',
    XLSX: 'xlsx',
    IMAGE: 'image',
    VIDEO: 'video',
    AUDIO: 'audio',
    ZIP: 'zip',
    OTHER: 'other'
  },

  GROUP_ROLES: {
    MEMBER: 'member',
    CO_LEADER: 'co_leader',
    RESEARCHER: 'researcher',
    WRITER: 'writer',
    PRESENTER: 'presenter'
  },

  COMMENT_TYPES: {
    GENERAL: 'general',
    FEEDBACK: 'feedback',
    CORRECTION: 'correction',
    QUESTION: 'question',
    CLARIFICATION: 'clarification'
  },

  EXPORT_FORMATS: {
    CSV: 'csv',
    EXCEL: 'excel',
    PDF: 'pdf'
  },

  NOTIFICATION_TYPES: {
    UPCOMING_DEADLINE: 'upcoming_deadline',
    OVERDUE: 'overdue',
    PENDING_GRADING: 'pending_grading',
    UPCOMING_DEADLINE_TEACHER: 'upcoming_deadline_teacher'
  }
};

// ==================== UTILITY FUNCTIONS ====================

export const formatAssignmentDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const calculateDaysUntilDue = (dueDate) => {
  const now = new Date();
  const due = new Date(dueDate);
  const diffTime = due - now;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

export const isAssignmentOverdue = (dueDate) => {
  const now = new Date();
  const due = new Date(dueDate);
  return now > due;
};

export const getStatusColor = (status) => {
  const colors = {
    draft: 'gray',
    published: 'green',
    in_progress: 'blue',
    closed: 'orange',
    graded: 'purple',
    archived: 'gray',
    not_submitted: 'red',
    submitted: 'blue',
    late: 'orange',
    returned: 'yellow',
    resubmitted: 'teal'
  };
  return colors[status] || 'gray';
};

export const calculateGrade = (percentage) => {
  if (percentage >= 80) return { grade: 'A', points: 4.0, color: 'green' };
  if (percentage >= 75) return { grade: 'A-', points: 3.7, color: 'green' };
  if (percentage >= 70) return { grade: 'B+', points: 3.3, color: 'blue' };
  if (percentage >= 65) return { grade: 'B', points: 3.0, color: 'blue' };
  if (percentage >= 60) return { grade: 'B-', points: 2.7, color: 'blue' };
  if (percentage >= 55) return { grade: 'C+', points: 2.3, color: 'yellow' };
  if (percentage >= 50) return { grade: 'C', points: 2.0, color: 'yellow' };
  if (percentage >= 45) return { grade: 'C-', points: 1.7, color: 'yellow' };
  if (percentage >= 40) return { grade: 'D+', points: 1.3, color: 'orange' };
  if (percentage >= 35) return { grade: 'D', points: 1.0, color: 'orange' };
  return { grade: 'E', points: 0.0, color: 'red' };
};

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default assignmentsAPI;