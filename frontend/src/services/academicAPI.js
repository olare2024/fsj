// src/services/academicAPI.js
import api from './api';

// ==================== ERROR HANDLING UTILITY ====================

const handleAPIError = (error, defaultMessage = 'An error occurred') => {
  console.error('🔴 Academic API Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
    // Handle specific status codes
    switch (status) {
      case 400:
        return {
          success: false,
          message: serverError.detail || serverError.message || serverError.error || defaultMessage,
          errors: serverError.errors || serverError.details || serverError,
          status: status,
          data: serverError
        };
      
      case 401:
        return {
          success: false,
          message: 'Authentication required. Please login again.',
          status: 401,
          data: serverError,
          requiresReauth: true
        };
      
      case 403:
        return {
          success: false,
          message: 'You do not have permission to perform this action.',
          status: 403,
          data: serverError
        };
      
      case 404:
        return {
          success: false,
          message: serverError.detail || 'Resource not found.',
          status: 404,
          data: serverError
        };
      
      case 429:
        return {
          success: false,
          message: 'Too many requests. Please try again later.',
          status: 429,
          data: serverError,
          retryAfter: error.response.headers['retry-after']
        };
      
      default:
        if (typeof serverError === 'object') {
          return {
            success: false,
            message: serverError.detail || serverError.message || serverError.error || defaultMessage,
            errors: serverError.errors || serverError.details,
            status: status,
            data: serverError
          };
        } else if (typeof serverError === 'string') {
          return {
            success: true,
            message: serverError,
            status: status
          };
        }
    }
  } else if (error.request) {
    return {
      success: false,
      message: 'Network error: Unable to connect to server',
      status: 0
    };
  } else {
    return {
      success: false,
      message: error.message || defaultMessage
    };
  }
  
  return {
    success: false,
    message: defaultMessage
  };
};

// ==================== RESPONSE UTILITIES ====================

const handleBulkResponse = (response, defaultMessage) => {
  if (response.status === 207) {
    // Partial success response
    return {
      success: true,
      data: response.data,
      status: 207,
      isPartialSuccess: true,
      createdCount: response.data.created?.length || 0,
      errorCount: response.data.errors?.length || 0
    };
  }
  
  return {
    success: true,
    data: response.data,
    status: response.status
  };
};

// ==================== ACADEMIC CONSTANTS ====================

export const ASSIGNMENT_CONSTANTS = {
  STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    SUBMITTED: 'submitted',
    LATE: 'late',
    GRADING: 'grading',
    GRADED: 'graded',
    COMPLETED: 'completed',
    OVERDUE: 'overdue',
    MISSING: 'missing',
    CANCELLED: 'cancelled'
  },
  TYPE: {
    HOMEWORK: 'homework',
    QUIZ: 'quiz',
    TEST: 'test',
    PROJECT: 'project',
    EXAM: 'exam',
    ESSAY: 'essay',
    PRESENTATION: 'presentation',
    WORKSHEET: 'worksheet',
    LAB_REPORT: 'lab_report',
    PRACTICE: 'practice'
  },
  PRIORITY: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high'
  },
  SUBMISSION_TYPE: {
    FILE: 'file',
    TEXT: 'text',
    LINK: 'link',
    NONE: 'none'
  },
  GRADING_TYPE: {
    PERCENTAGE: 'percentage',
    POINTS: 'points',
    LETTER_GRADE: 'letter_grade',
    RUBRIC: 'rubric',
    PASS_FAIL: 'pass_fail'
  },
  MAX_SCORE: 100,
  MIN_SCORE: 0,
  DEFAULT_DAYS_TO_SUBMIT: 7,
  LATE_SUBMISSION_PENALTY: 10
};

export const CLASS_CONSTANTS = {
  STATUS: {
    ACTIVE: 'active',
    INACTIVE: 'inactive',
    ARCHIVED: 'archived'
  },
  LEVEL: {
    BEGINNER: 'beginner',
    INTERMEDIATE: 'intermediate',
    ADVANCED: 'advanced'
  },
  TYPE: {
    REGULAR: 'regular',
    HONORS: 'honors',
    AP: 'ap',
    ELECTIVE: 'elective',
    CORE: 'core'
  }
};

export const SUBJECT_CONSTANTS = {
  CATEGORY: {
    CORE: 'core',
    ELECTIVE: 'elective',
    LANGUAGE: 'language',
    SCIENCE: 'science',
    MATH: 'math',
    HUMANITIES: 'humanities',
    ARTS: 'arts',
    PHYSICAL_EDUCATION: 'physical_education',
    TECHNOLOGY: 'technology'
  },
  DIFFICULTY: {
    BASIC: 'basic',
    STANDARD: 'standard',
    ADVANCED: 'advanced'
  }
};

export const ENROLLMENT_CONSTANTS = {
  STATUS: {
    ACTIVE: 'active',
    INACTIVE: 'inactive',
    DROPPED: 'dropped',
    COMPLETED: 'completed',
    PENDING: 'pending'
  },
  TYPE: {
    FULL_TIME: 'full_time',
    PART_TIME: 'part_time',
    AUDIT: 'audit',
    HOMESCHOOL: 'homeschool'
  }
};

export const ACADEMIC_YEAR_CONSTANTS = {
  STATUS: {
    UPCOMING: 'upcoming',
    CURRENT: 'current',
    PAST: 'past',
    ARCHIVED: 'archived'
  }
};

// ==================== QUERY PARAMETER BUILDERS ====================

const buildQueryParams = (params = {}) => {
  const queryParams = { ...params };
  
  // Remove undefined/null values
  Object.keys(queryParams).forEach(key => {
    if (queryParams[key] === undefined || queryParams[key] === null) {
      delete queryParams[key];
    }
  });
  
  return queryParams;
};

// ==================== ACADEMIC API ====================

export const academicAPI = {
  // ==================== ACADEMIC YEARS ====================
  getAcademicYears: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/academic-years/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic years');
    }
  },

  getAcademicYear: async (academicYearId) => {
    try {
      const response = await api.get(`/academics/academic-years/${academicYearId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic year');
    }
  },

  getCurrentAcademicYear: async () => {
    try {
      const response = await api.get('/academics/academic-years/current/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch current academic year');
    }
  },

  setCurrentAcademicYear: async (academicYearId) => {
    try {
      const response = await api.post(`/academics/academic-years/${academicYearId}/set_current/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to set current academic year');
    }
  },

  getAcademicYearStatistics: async (academicYearId) => {
    try {
      const response = await api.get(`/academics/academic-years/${academicYearId}/statistics/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic year statistics');
    }
  },

  createAcademicYear: async (academicYearData) => {
    try {
      const response = await api.post('/academics/academic-years/', academicYearData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create academic year');
    }
  },

  updateAcademicYear: async (academicYearId, academicYearData) => {
    try {
      const response = await api.put(`/academics/academic-years/${academicYearId}/`, academicYearData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update academic year');
    }
  },

  patchAcademicYear: async (academicYearId, academicYearData) => {
    try {
      const response = await api.patch(`/academics/academic-years/${academicYearId}/`, academicYearData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update academic year');
    }
  },

  deleteAcademicYear: async (academicYearId) => {
    try {
      const response = await api.delete(`/academics/academic-years/${academicYearId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete academic year');
    }
  },

  // ==================== ACADEMIC TERMS ====================
  getAcademicTerms: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/academic-terms/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic terms');
    }
  },

  getAcademicTerm: async (termId) => {
    try {
      const response = await api.get(`/academics/academic-terms/${termId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic term');
    }
  },

  setCurrentAcademicTerm: async (termId) => {
    try {
      const response = await api.post(`/academics/academic-terms/${termId}/set_current/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to set current academic term');
    }
  },

  getAcademicTermEvents: async (termId) => {
    try {
      const response = await api.get(`/academics/academic-terms/${termId}/events/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic term events');
    }
  },

  getAcademicTermProgress: async (termId) => {
    try {
      const response = await api.get(`/academics/academic-terms/${termId}/progress/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic term progress');
    }
  },

  createAcademicTerm: async (termData) => {
    try {
      const response = await api.post('/academics/academic-terms/', termData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create academic term');
    }
  },

  updateAcademicTerm: async (termId, termData) => {
    try {
      const response = await api.put(`/academics/academic-terms/${termId}/`, termData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update academic term');
    }
  },

  patchAcademicTerm: async (termId, termData) => {
    try {
      const response = await api.patch(`/academics/academic-terms/${termId}/`, termData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update academic term');
    }
  },

  deleteAcademicTerm: async (termId) => {
    try {
      const response = await api.delete(`/academics/academic-terms/${termId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete academic term');
    }
  },

  // ==================== SUBJECTS ====================
  getSubjects: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/subjects/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subjects');
    }
  },

  getSubject: async (subjectId) => {
    try {
      const response = await api.get(`/academics/subjects/${subjectId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subject');
    }
  },

  getSubjectTeachers: async (subjectId, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get(`/academics/subjects/${subjectId}/teachers/`, { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subject teachers');
    }
  },

  getSubjectCategories: async () => {
    try {
      const response = await api.get('/academics/subjects/categories/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subject categories');
    }
  },

  getSubjectsByCurriculum: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/subjects/by_curriculum/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subjects by curriculum');
    }
  },

  getSubjectSyllabus: async (subjectId, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get(`/academics/subjects/${subjectId}/syllabus/`, { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subject syllabus');
    }
  },

  getSubjectAssignments: async (subjectId, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get(`/academics/subjects/${subjectId}/assignments/`, { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subject assignments');
    }
  },

  createSubject: async (subjectData) => {
    try {
      const response = await api.post('/academics/subjects/', subjectData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create subject');
    }
  },

  updateSubject: async (subjectId, subjectData) => {
    try {
      const response = await api.put(`/academics/subjects/${subjectId}/`, subjectData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update subject');
    }
  },

  patchSubject: async (subjectId, subjectData) => {
    try {
      const response = await api.patch(`/academics/subjects/${subjectId}/`, subjectData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update subject');
    }
  },

  deleteSubject: async (subjectId) => {
    try {
      const response = await api.delete(`/academics/subjects/${subjectId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete subject');
    }
  },

  // ==================== CLASSES ====================
  getClasses: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/classes/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch classes');
    }
  },

  getClass: async (classId) => {
    try {
      const response = await api.get(`/academics/classes/${classId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch class');
    }
  },

  getClassStudents: async (classId, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get(`/academics/classes/${classId}/students/`, { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch class students');
    }
  },

  getClassSubjects: async (classId, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get(`/academics/classes/${classId}/subjects/`, { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch class subjects');
    }
  },

  getClassTimetable: async (classId) => {
    try {
      const response = await api.get(`/academics/classes/${classId}/timetable/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch class timetable');
    }
  },

  getClassStatistics: async (classId) => {
    try {
      const response = await api.get(`/academics/classes/${classId}/statistics/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch class statistics');
    }
  },

  assignClassTeacher: async (classId, teacherId) => {
    try {
      const response = await api.post(`/academics/classes/${classId}/assign_class_teacher/`, {
        teacher_id: teacherId
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to assign class teacher');
    }
  },

  createClass: async (classData) => {
    try {
      const response = await api.post('/academics/classes/', classData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create class');
    }
  },

  updateClass: async (classId, classData) => {
    try {
      const response = await api.put(`/academics/classes/${classId}/`, classData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update class');
    }
  },

  patchClass: async (classId, classData) => {
    try {
      const response = await api.patch(`/academics/classes/${classId}/`, classData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update class');
    }
  },

  deleteClass: async (classId) => {
    try {
      const response = await api.delete(`/academics/classes/${classId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete class');
    }
  },

  // ==================== SUBJECT ASSIGNMENTS ====================
  getSubjectAssignments: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/subject-assignments/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subject assignments');
    }
  },

  getSubjectAssignment: async (assignmentId) => {
    try {
      const response = await api.get(`/academics/subject-assignments/${assignmentId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch subject assignment');
    }
  },

  bulkAssignSubjects: async (assignmentData) => {
    try {
      const response = await api.post('/academics/subject-assignments/bulk_assign/', assignmentData);
      return handleBulkResponse(response, 'Failed to bulk assign subjects');
    } catch (error) {
      return handleAPIError(error, 'Failed to bulk assign subjects');
    }
  },

  getTeacherWorkload: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/subject-assignments/teacher_workload/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch teacher workload');
    }
  },

  getAssignmentsByTeacher: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/subject-assignments/by_teacher/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch assignments by teacher');
    }
  },

  createSubjectAssignment: async (assignmentData) => {
    try {
      const response = await api.post('/academics/subject-assignments/', assignmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create subject assignment');
    }
  },

  updateSubjectAssignment: async (assignmentId, assignmentData) => {
    try {
      const response = await api.put(`/academics/subject-assignments/${assignmentId}/`, assignmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update subject assignment');
    }
  },

  patchSubjectAssignment: async (assignmentId, assignmentData) => {
    try {
      const response = await api.patch(`/academics/subject-assignments/${assignmentId}/`, assignmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update subject assignment');
    }
  },

  deleteSubjectAssignment: async (assignmentId) => {
    try {
      const response = await api.delete(`/academics/subject-assignments/${assignmentId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete subject assignment');
    }
  },

  // ==================== STUDENT ENROLLMENTS ====================
  getEnrollments: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/student-enrollments/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch enrollments');
    }
  },

  getEnrollment: async (enrollmentId) => {
    try {
      const response = await api.get(`/academics/student-enrollments/${enrollmentId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch enrollment');
    }
  },

  bulkEnrollStudents: async (enrollmentData) => {
    try {
      const response = await api.post('/academics/student-enrollments/bulk_enroll/', enrollmentData);
      return handleBulkResponse(response, 'Failed to bulk enroll students');
    } catch (error) {
      return handleAPIError(error, 'Failed to bulk enroll students');
    }
  },

  exportEnrollmentsCSV: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/enrollments/export-csv/', {
        params: queryParams,
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `enrollments_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return {
        success: true,
        message: 'Export completed successfully',
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to export enrollments');
    }
  },

  getEnrollmentReport: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/student-enrollments/report/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch enrollment report');
    }
  },

  getActiveEnrollments: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/student-enrollments/active/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch active enrollments');
    }
  },

  createEnrollment: async (enrollmentData) => {
    try {
      const response = await api.post('/academics/student-enrollments/', enrollmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create enrollment');
    }
  },

  updateEnrollment: async (enrollmentId, enrollmentData) => {
    try {
      const response = await api.put(`/academics/student-enrollments/${enrollmentId}/`, enrollmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update enrollment');
    }
  },

  patchEnrollment: async (enrollmentId, enrollmentData) => {
    try {
      const response = await api.patch(`/academics/student-enrollments/${enrollmentId}/`, enrollmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update enrollment');
    }
  },

  deleteEnrollment: async (enrollmentId) => {
    try {
      const response = await api.delete(`/academics/student-enrollments/${enrollmentId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete enrollment');
    }
  },

  // ==================== LESSON PLANS ====================
  getLessonPlans: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/lesson-plans/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch lesson plans');
    }
  },

  getLessonPlan: async (lessonPlanId) => {
    try {
      const response = await api.get(`/academics/lesson-plans/${lessonPlanId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch lesson plan');
    }
  },

  getUpcomingLessonPlans: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/lesson-plans/upcoming/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch upcoming lesson plans');
    }
  },

  getWeeklyLessonPlans: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/lesson-plans/weekly/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch weekly lesson plans');
    }
  },

  markLessonPlanCompleted: async (lessonPlanId, completionData = {}) => {
    try {
      const response = await api.post(`/academics/lesson-plans/${lessonPlanId}/mark_completed/`, completionData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to mark lesson plan as completed');
    }
  },

  createLessonPlan: async (lessonPlanData) => {
    try {
      const response = await api.post('/academics/lesson-plans/', lessonPlanData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create lesson plan');
    }
  },

  updateLessonPlan: async (lessonPlanId, lessonPlanData) => {
    try {
      const response = await api.put(`/academics/lesson-plans/${lessonPlanId}/`, lessonPlanData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update lesson plan');
    }
  },

  patchLessonPlan: async (lessonPlanId, lessonPlanData) => {
    try {
      const response = await api.patch(`/academics/lesson-plans/${lessonPlanId}/`, lessonPlanData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update lesson plan');
    }
  },

  deleteLessonPlan: async (lessonPlanId) => {
    try {
      const response = await api.delete(`/academics/lesson-plans/${lessonPlanId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete lesson plan');
    }
  },

  // ==================== SYLLABUS ====================
  getSyllabi: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/syllabi/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch syllabi');
    }
  },

  getSyllabus: async (syllabusId) => {
    try {
      const response = await api.get(`/academics/syllabi/${syllabusId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch syllabus');
    }
  },

  markTopicCompleted: async (syllabusId, topicData) => {
    try {
      const response = await api.post(`/academics/syllabi/${syllabusId}/mark_topic_completed/`, topicData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to mark topic as completed');
    }
  },

  getSyllabusProgress: async (syllabusId) => {
    try {
      const response = await api.get(`/academics/syllabi/${syllabusId}/progress/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch syllabus progress');
    }
  },

  createSyllabus: async (syllabusData) => {
    try {
      const response = await api.post('/academics/syllabi/', syllabusData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create syllabus');
    }
  },

  updateSyllabus: async (syllabusId, syllabusData) => {
    try {
      const response = await api.put(`/academics/syllabi/${syllabusId}/`, syllabusData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update syllabus');
    }
  },

  patchSyllabus: async (syllabusId, syllabusData) => {
    try {
      const response = await api.patch(`/academics/syllabi/${syllabusId}/`, syllabusData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update syllabus');
    }
  },

  deleteSyllabus: async (syllabusId) => {
    try {
      const response = await api.delete(`/academics/syllabi/${syllabusId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete syllabus');
    }
  },

  // ==================== ACADEMIC EVENTS ====================
  getAcademicEvents: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/academic-events/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic events');
    }
  },

  getAcademicEvent: async (eventId) => {
    try {
      const response = await api.get(`/academics/academic-events/${eventId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic event');
    }
  },

  getUpcomingEvents: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/academic-events/upcoming/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch upcoming events');
    }
  },

  getCalendarEvents: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/academic-events/calendar/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch calendar events');
    }
  },

  createAcademicEvent: async (eventData) => {
    try {
      const response = await api.post('/academics/academic-events/', eventData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to create academic event');
    }
  },

  updateAcademicEvent: async (eventId, eventData) => {
    try {
      const response = await api.put(`/academics/academic-events/${eventId}/`, eventData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update academic event');
    }
  },

  patchAcademicEvent: async (eventId, eventData) => {
    try {
      const response = await api.patch(`/academics/academic-events/${eventId}/`, eventData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to update academic event');
    }
  },

  deleteAcademicEvent: async (eventId) => {
    try {
      const response = await api.delete(`/academics/academic-events/${eventId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to delete academic event');
    }
  },

  // ==================== DASHBOARD & ANALYTICS ====================
  getAcademicDashboard: async () => {
    try {
      const response = await api.get('/academics/dashboard/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic dashboard');
    }
  },

  getClassStatistics: async () => {
    try {
      const response = await api.get('/academics/statistics/classes/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch class statistics');
    }
  },

  getTeacherWorkloadStatistics: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/statistics/teacher-workload/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch teacher workload statistics');
    }
  },

  // ==================== SEARCH ====================
  academicSearch: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/search/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to perform academic search');
    }
  },

  // ==================== UTILITY ENDPOINTS ====================
  getAcademicOverview: async () => {
    try {
      const response = await api.get('/academics/overview/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic overview');
    }
  },

  getAcademicCalendar: async (params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get('/academics/calendar/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to fetch academic calendar');
    }
  },

  // ==================== BATCH OPERATIONS ====================
  bulkUpdateEnrollments: async (updateData) => {
    try {
      const response = await api.post('/academics/student-enrollments/bulk_update/', updateData);
      return handleBulkResponse(response, 'Failed to bulk update enrollments');
    } catch (error) {
      return handleAPIError(error, 'Failed to bulk update enrollments');
    }
  },

  bulkDeleteEnrollments: async (enrollmentIds) => {
    try {
      const response = await api.post('/academics/student-enrollments/bulk_delete/', { ids: enrollmentIds });
      return handleBulkResponse(response, 'Failed to bulk delete enrollments');
    } catch (error) {
      return handleAPIError(error, 'Failed to bulk delete enrollments');
    }
  },

  // ==================== HEALTH & VALIDATION ====================
  validateAcademicData: async (dataType, data) => {
    try {
      const response = await api.post('/academics/validate/', {
        data_type: dataType,
        data: data
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to validate academic data');
    }
  },

  checkAcademicHealth: async () => {
    try {
      const response = await api.get('/academics/health/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to check academic health');
    }
  },

  // ==================== CACHE MANAGEMENT ====================
  clearAcademicCache: async (cacheType = 'all') => {
    try {
      const response = await api.post('/academics/clear_cache/', { cache_type: cacheType });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to clear academic cache');
    }
  },

  // ==================== SYNCHRONIZATION ====================
  syncAcademicData: async (syncType, params = {}) => {
    try {
      const response = await api.post('/academics/sync/', {
        sync_type: syncType,
        ...params
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to sync academic data');
    }
  },

  getSyncStatus: async (syncId) => {
    try {
      const response = await api.get(`/academics/sync/${syncId}/status/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to get sync status');
    }
  },

  // ==================== EXPORT/IMPORT ====================
  exportAcademicData: async (exportType, params = {}) => {
    try {
      const queryParams = buildQueryParams(params);
      const response = await api.get(`/academics/export/${exportType}/`, {
        params: queryParams,
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `academic_export_${exportType}_${new Date().toISOString().split('T')[0]}.${exportType}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return {
        success: true,
        message: 'Export completed successfully',
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to export academic data');
    }
  },

  importAcademicData: async (file, importType) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('import_type', importType);
      
      const response = await api.post('/academics/import/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error, 'Failed to import academic data');
    }
  },

  // ==================== BACKWARD COMPATIBILITY ====================
  // These methods are kept for backward compatibility
  // They now call the new ViewSet endpoints
  
  getSubjectsList: async (params = {}) => {
    return academicAPI.getSubjects(params);
  },

  getClassesList: async (params = {}) => {
    return academicAPI.getClasses(params);
  },

  getEnrollmentsList: async (params = {}) => {
    return academicAPI.getEnrollments(params);
  },

  getLessonPlansList: async (params = {}) => {
    return academicAPI.getLessonPlans(params);
  },

  getSyllabiList: async (params = {}) => {
    return academicAPI.getSyllabi(params);
  },

  getAcademicEventsList: async (params = {}) => {
    return academicAPI.getAcademicEvents(params);
  }
};

// ==================== HELPER FUNCTIONS ====================

export const formatAcademicYear = (year) => {
  if (!year) return '';
  
  if (typeof year === 'object') {
    return `${year.start_date?.split('-')[0] || ''}-${year.end_date?.split('-')[0] || ''}`;
  }
  
  return year;
};

export const getStatusColor = (status) => {
  const colors = {
    active: 'green',
    inactive: 'gray',
    draft: 'yellow',
    published: 'blue',
    completed: 'green',
    pending: 'yellow',
    archived: 'gray',
    upcoming: 'purple',
    current: 'blue',
    past: 'gray'
  };
  
  return colors[status] || 'gray';
};

export const calculateOccupancyRate = (currentStrength, capacity) => {
  if (!capacity || capacity === 0) return 0;
  return Math.round((currentStrength / capacity) * 100);
};

export const formatDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return '';
  
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  const startStr = start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const endStr = end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  
  return `${startStr} - ${endStr}`;
};

// ==================== HOOKS (for React) ====================

export const useAcademicAPI = () => {
  return {
    ...academicAPI,
    constants: {
      ASSIGNMENT_CONSTANTS,
      CLASS_CONSTANTS,
      SUBJECT_CONSTANTS,
      ENROLLMENT_CONSTANTS,
      ACADEMIC_YEAR_CONSTANTS
    },
    helpers: {
      formatAcademicYear,
      getStatusColor,
      calculateOccupancyRate,
      formatDateRange
    }
  };
};

export default academicAPI;