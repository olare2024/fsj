import api from './api';

export const studentsAPI = {
  // ==================== STUDENT DASHBOARD ====================
  getDashboard: async () => {
    try {
      const response = await api.get('/students/dashboard/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status,
          code: error.response?.data?.code
        }
      };
    }
  },

  // ==================== STUDENT PROFILES (ViewSet) ====================
  // GET /api/v1/students/profiles/ - List all student profiles
  listProfiles: async (params = {}) => {
    try {
      const response = await api.get('/students/profiles/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status,
          details: error.response?.data
        }
      };
    }
  },

  // GET /api/v1/students/profiles/{id}/ - Retrieve specific profile
  getProfile: async (profileId) => {
    try {
      const response = await api.get(`/students/profiles/${profileId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/profiles/ - Create student profile
  createProfile: async (profileData) => {
    try {
      const response = await api.post('/students/profiles/', profileData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  // PUT/PATCH /api/v1/students/profiles/{id}/ - Update student profile
  updateProfile: async (profileId, profileData, partial = false) => {
    try {
      const method = partial ? 'patch' : 'put';
      const response = await api[method](`/students/profiles/${profileId}/`, profileData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  // DELETE /api/v1/students/profiles/{id}/ - Delete student profile
  deleteProfile: async (profileId) => {
    try {
      const response = await api.delete(`/students/profiles/${profileId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== STUDENT ENROLLMENTS (ViewSet) ====================
  // GET /api/v1/students/enrollments/ - List all enrollments
  listEnrollments: async (params = {}) => {
    try {
      const response = await api.get('/students/enrollments/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status,
          details: error.response?.data
        }
      };
    }
  },

  // GET /api/v1/students/enrollments/{id}/ - Retrieve specific enrollment
  getEnrollment: async (enrollmentId) => {
    try {
      const response = await api.get(`/students/enrollments/${enrollmentId}/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/enrollments/ - Create enrollment
  createEnrollment: async (enrollmentData) => {
    try {
      const response = await api.post('/students/enrollments/', enrollmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== STUDENT PROFILE CUSTOM ACTIONS ====================
  // GET /api/v1/students/profiles/{id}/enrollments/ - Get student enrollments
  getProfileEnrollments: async (profileId) => {
    try {
      const response = await api.get(`/students/profiles/${profileId}/enrollments/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/profiles/{id}/academic-info/ - Get academic info
  getAcademicInfo: async (profileId) => {
    try {
      const response = await api.get(`/students/profiles/${profileId}/academic-info/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/profiles/{id}/contact-info/ - Get contact info
  getContactInfo: async (profileId) => {
    try {
      const response = await api.get(`/students/profiles/${profileId}/contact-info/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/profiles/{id}/parent-info/ - Get parent info
  getParentInfo: async (profileId) => {
    try {
      const response = await api.get(`/students/profiles/${profileId}/parent-info/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/profiles/{id}/medical-info/ - Get medical info
  getMedicalInfo: async (profileId) => {
    try {
      const response = await api.get(`/students/profiles/${profileId}/medical-info/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/profiles/{id}/generate-report/ - Generate student report
  generateStudentReport: async (profileId) => {
    try {
      const response = await api.get(`/students/profiles/${profileId}/generate-report/`);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/profiles/{id}/update-academic/ - Update academic info
  updateAcademicInfo: async (profileId, academicData) => {
    try {
      const response = await api.post(`/students/profiles/${profileId}/update-academic/`, academicData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/profiles/{id}/update-health/ - Update health info
  updateHealthInfo: async (profileId, healthData) => {
    try {
      const response = await api.post(`/students/profiles/${profileId}/update-health/`, healthData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/profiles/{id}/update-fee-info/ - Update fee info
  updateFeeInfo: async (profileId, feeData) => {
    try {
      const response = await api.post(`/students/profiles/${profileId}/update-fee-info/`, feeData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/profiles/{id}/add-community-service/ - Add community service
  addCommunityService: async (profileId, serviceData) => {
    try {
      const response = await api.post(`/students/profiles/${profileId}/add-community-service/`, serviceData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/profiles/{id}/add-test-score/ - Add test score
  addTestScore: async (profileId, testData) => {
    try {
      const response = await api.post(`/students/profiles/${profileId}/add-test-score/`, testData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/profiles/{id}/promote/ - Promote student
  promoteStudent: async (profileId, promotionData) => {
    try {
      const response = await api.post(`/students/profiles/${profileId}/promote/`, promotionData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== ENROLLMENT CUSTOM ACTIONS ====================
  // POST /api/v1/students/enrollments/bulk-create/ - Bulk create enrollments
  bulkCreateEnrollments: async (enrollmentData) => {
    try {
      const response = await api.post('/students/enrollments/bulk-create/', enrollmentData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/enrollments/{id}/update-status/ - Update enrollment status
  updateEnrollmentStatus: async (enrollmentId, statusData) => {
    try {
      const response = await api.post(`/students/enrollments/${enrollmentId}/update-status/`, statusData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/enrollments/current/ - Get current enrollments
  getCurrentEnrollments: async (params = {}) => {
    try {
      const response = await api.get('/students/enrollments/current/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/enrollments/by-class/ - Get enrollments by class
  getEnrollmentsByClass: async (params = {}) => {
    try {
      const response = await api.get('/students/enrollments/by-class/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== BULK OPERATIONS ====================
  // POST /api/v1/students/profiles/bulk-update/ - Bulk update profiles
  bulkUpdateProfiles: async (bulkData) => {
    try {
      const response = await api.post('/students/profiles/bulk-update/', bulkData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/bulk-promote/ - Bulk promote students
  bulkPromoteStudents: async (promotionData) => {
    try {
      const response = await api.post('/students/bulk-promote/', promotionData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== SEARCH & FILTERING ====================
  // GET /api/v1/students/search/ - Search students
  searchStudents: async (queryParams) => {
    try {
      const response = await api.get('/students/search/', { params: queryParams });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== STATISTICS & REPORTS ====================
  // GET /api/v1/students/statistics/ - Get student statistics
  getStatistics: async () => {
    try {
      const response = await api.get('/students/statistics/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // POST /api/v1/students/generate-report/ - Generate custom report
  generateReport: async (reportData) => {
    try {
      const response = await api.post('/students/generate-report/', reportData);
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== REPORTING ENDPOINTS ====================
  // GET /api/v1/students/reports/demographics/ - Demographics report
  getDemographicsReport: async () => {
    try {
      const response = await api.get('/students/reports/demographics/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/reports/academic-performance/ - Academic performance report
  getAcademicPerformanceReport: async () => {
    try {
      const response = await api.get('/students/reports/academic-performance/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/reports/attendance/ - Attendance report
  getAttendanceReport: async () => {
    try {
      const response = await api.get('/students/reports/attendance/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/reports/financial-status/ - Financial status report
  getFinancialStatusReport: async () => {
    try {
      const response = await api.get('/students/reports/financial-status/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // GET /api/v1/students/reports/cbc-pathways/ - CBC pathway report
  getCBCPathwayReport: async () => {
    try {
      const response = await api.get('/students/reports/cbc-pathways/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== UTILITY FUNCTIONS ====================
  
  // Get current student's profile (for student role)
  getMyProfile: async () => {
    try {
      // Try to get from student dashboard first
      const dashboard = await studentsAPI.getDashboard();
      if (dashboard.success) {
        return {
          success: true,
          data: dashboard.data,
          status: dashboard.status
        };
      }
      
      // Fallback to listing profiles
      const profiles = await studentsAPI.listProfiles();
      if (profiles.success && profiles.data.results && profiles.data.results.length > 0) {
        return {
          success: true,
          data: profiles.data.results[0],
          status: profiles.status
        };
      }
      
      return {
        success: false,
        error: {
          message: 'No profile found',
          status: 404
        }
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.message || 'Failed to get profile',
          status: error.response?.status
        }
      };
    }
  },

  // Search with pagination helper
  searchWithPagination: async (query, page = 1, pageSize = 20, filters = {}) => {
    try {
      const params = {
        q: query,
        page,
        page_size: pageSize,
        ...filters
      };
      
      const response = await api.get('/students/search/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // Export student data
  exportStudentData: async (filters = {}) => {
    try {
      const response = await api.get('/students/export/', {
        params: filters,
        responseType: 'blob' // For file download
      });
      return {
        success: true,
        data: response.data,
        status: response.status,
        fileName: response.headers['content-disposition']?.split('filename=')[1] || 'students_export.csv'
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // Profile completion handler
  completeStudentProfile: async (profileData) => {
    try {
      // Check if profile exists
      const existingProfile = await studentsAPI.getMyProfile();
      
      if (existingProfile.success) {
        // Update existing profile
        return await studentsAPI.updateProfile(existingProfile.data.id, profileData, true);
      } else {
        // Create new profile
        return await studentsAPI.createProfile(profileData);
      }
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.response?.data?.error || error.response?.data?.message || error.message,
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  // Get student summary
  getStudentSummary: async (profileId) => {
    try {
      const [
        profileResponse,
        enrollmentsResponse,
        academicResponse
      ] = await Promise.all([
        studentsAPI.getProfile(profileId),
        studentsAPI.getProfileEnrollments(profileId),
        studentsAPI.getAcademicInfo(profileId)
      ]);

      if (!profileResponse.success || !enrollmentsResponse.success) {
        return {
          success: false,
          error: profileResponse.error || enrollmentsResponse.error
        };
      }

      return {
        success: true,
        data: {
          profile: profileResponse.data,
          enrollments: enrollmentsResponse.data,
          academic: academicResponse.data || {}
        },
        status: 200
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: error.message || 'Failed to get student summary',
          status: error.response?.status
        }
      };
    }
  }
};