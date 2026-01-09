// teacherAPI.js
import api from './api';

export const teacherAPI = {
  // ==================== TEACHER DASHBOARD ====================
  getDashboard: async () => {
    try {
      const response = await api.get('/teachers/dashboard/teacher/');
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

  getAdminDashboard: async () => {
    try {
      const response = await api.get('/teachers/dashboard/admin/');
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

  // ==================== TEACHER PROFILE ====================
  getMyProfile: async () => {
    try {
      const response = await api.get('/teachers/teacher-profiles/my-profile/');
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

  updateProfile: async (profileData) => {
    try {
      const response = await api.patch('/teachers/teacher-profiles/me/', profileData);
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

  getProfileDashboard: async (teacherId) => {
    try {
      const response = await api.get(`/teachers/teacher-profiles/${teacherId}/dashboard/`);
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

  // ==================== DEPARTMENTS ====================
  getDepartments: async (params = {}) => {
    try {
      const response = await api.get('/teachers/departments/', { params });
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

  getDepartmentTeachers: async (departmentId) => {
    try {
      const response = await api.get(`/teachers/departments/${departmentId}/teachers/`);
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

  // ==================== TEACHER PROFILES (MANAGEMENT) ====================
  getTeachers: async (params = {}) => {
    try {
      const response = await api.get('/teachers/teacher-profiles/', { params });
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

  getTeacherById: async (teacherId) => {
    try {
      const response = await api.get(`/teachers/teacher-profiles/${teacherId}/`);
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

  getTeachersByDepartment: async (departmentId) => {
    try {
      const response = await api.get(`/teachers/by-department/${departmentId}/`);
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

  createTeacher: async (teacherData) => {
    try {
      const response = await api.post('/teachers/teacher-profiles/', teacherData);
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

  bulkCreateTeachers: async (teacherData) => {
    try {
      const response = await api.post('/teachers/teacher-profiles/bulk_create/', teacherData);
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

  // ==================== DOCUMENTS ====================
  getDocuments: async (params = {}) => {
    try {
      const response = await api.get('/teachers/documents/', { params });
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

  uploadDocument: async (documentData) => {
    try {
      const response = await api.post('/teachers/documents/', documentData, {
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

  verifyDocument: async (documentId, verificationData) => {
    try {
      const response = await api.post(`/teachers/documents/${documentId}/verify/`, verificationData);
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

  getExpiringDocuments: async () => {
    try {
      const response = await api.get('/teachers/documents/expiring-soon/');
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

  // ==================== QUALIFICATIONS ====================
  getQualifications: async (params = {}) => {
    try {
      const response = await api.get('/teachers/qualifications/', { params });
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

  addQualification: async (qualificationData) => {
    try {
      const response = await api.post('/teachers/qualifications/', qualificationData);
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

  verifyQualification: async (qualificationId, verificationData) => {
    try {
      const response = await api.post(`/teachers/qualifications/${qualificationId}/verify/`, verificationData);
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

  // ==================== TRAININGS ====================
  getTrainings: async (params = {}) => {
    try {
      const response = await api.get('/teachers/trainings/', { params });
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

  addTraining: async (trainingData) => {
    try {
      const response = await api.post('/teachers/trainings/', trainingData);
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

  completeTraining: async (trainingId, completionData) => {
    try {
      const response = await api.post(`/teachers/trainings/${trainingId}/complete/`, completionData);
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

  getUpcomingTrainings: async () => {
    try {
      const response = await api.get('/teachers/trainings/upcoming/');
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

  // ==================== ASSIGNMENTS ====================
  getAssignments: async (params = {}) => {
    try {
      const response = await api.get('/teachers/assignments/', { params });
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

  approveAssignment: async (assignmentId) => {
    try {
      const response = await api.post(`/teachers/assignments/${assignmentId}/approve/`);
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

  getCurrentAssignments: async () => {
    try {
      const response = await api.get('/teachers/assignments/current/');
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

  // ==================== ATTENDANCE ====================
  getAttendance: async (params = {}) => {
    try {
      const response = await api.get('/teachers/attendance/', { params });
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

  markAttendance: async (attendanceData) => {
    try {
      const response = await api.post('/teachers/attendance/', attendanceData);
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

  bulkUpdateAttendance: async (bulkData) => {
    try {
      const response = await api.post('/teachers/attendance/bulk-update/', bulkData);
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

  getAttendanceReport: async (params = {}) => {
    try {
      const response = await api.get('/teachers/attendance/report/', { params });
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

  getMonthlyAttendanceSummary: async (params = {}) => {
    try {
      const response = await api.get('/teachers/attendance/monthly-summary/', { params });
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

  // ==================== LEAVE MANAGEMENT ====================
  getLeaves: async (params = {}) => {
    try {
      const response = await api.get('/teachers/leaves/', { params });
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

  applyForLeave: async (leaveData) => {
    try {
      const response = await api.post('/teachers/leaves/', leaveData);
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

  submitLeave: async (leaveId) => {
    try {
      const response = await api.post(`/teachers/leaves/${leaveId}/submit/`);
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

  approveLeave: async (leaveId, approvalData = {}) => {
    try {
      const response = await api.post(`/teachers/leaves/${leaveId}/approve/`, approvalData);
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

  rejectLeave: async (leaveId, rejectionData = {}) => {
    try {
      const response = await api.post(`/teachers/leaves/${leaveId}/reject/`, rejectionData);
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

  getPendingLeaves: async () => {
    try {
      const response = await api.get('/teachers/leaves/pending/');
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

  getCurrentLeaves: async () => {
    try {
      const response = await api.get('/teachers/leaves/current/');
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

  // ==================== PERFORMANCE INDICATORS ====================
  getPerformanceIndicators: async (params = {}) => {
    try {
      const response = await api.get('/teachers/performance-indicators/', { params });
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

  createPerformanceIndicator: async (performanceData) => {
    try {
      const response = await api.post('/teachers/performance-indicators/', performanceData);
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

  getPerformanceSummary: async () => {
    try {
      const response = await api.get('/teachers/performance-indicators/summary/');
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

  // ==================== TRANSFERS ====================
  getTransfers: async (params = {}) => {
    try {
      const response = await api.get('/teachers/transfers/', { params });
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

  createTransfer: async (transferData) => {
    try {
      const response = await api.post('/teachers/transfers/', transferData);
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

  approveTransferSending: async (transferId) => {
    try {
      const response = await api.post(`/teachers/transfers/${transferId}/approve-sending/`);
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

  approveTransferReceiving: async (transferId) => {
    try {
      const response = await api.post(`/teachers/transfers/${transferId}/approve-receiving/`);
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

  getPendingTransfers: async () => {
    try {
      const response = await api.get('/teachers/transfers/pending/');
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

  // ==================== REPORTS ====================
  getReports: async (reportType, params = {}) => {
    try {
      const response = await api.get('/teachers/reports/', { params: { type: reportType, ...params } });
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

  exportTeachers: async (params = {}) => {
    try {
      const response = await api.get('/teachers/export/teachers/', { 
        params,
        responseType: 'blob' 
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'teachers_export.csv');
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

  // ==================== PUBLIC TEACHERS ====================
  getPublicTeachers: async (params = {}) => {
    try {
      const response = await api.get('/teachers/public/', { params });
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

  // ==================== NOTIFICATIONS ====================
  sendNotifications: async (notificationData) => {
    try {
      const response = await api.post('/teachers/notifications/send/', notificationData);
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

  // ==================== TSC SYNC ====================
  syncTSCData: async (syncData = {}) => {
    try {
      const response = await api.post('/teachers/sync/tsc/', syncData);
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

  // ==================== STATISTICS ====================
  getTeacherStatistics: async () => {
    try {
      const response = await api.get('/teachers/teacher-profiles/statistics/');
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

  getDepartmentStatistics: async () => {
    try {
      const response = await api.get('/teachers/departments/statistics/');
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

  // ==================== TSC SPECIFIC ====================
  getTSCReport: async (teacherId) => {
    try {
      const response = await api.get(`/teachers/teacher-profiles/${teacherId}/tsc-report/`);
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

  updateTPDModule: async (teacherId, moduleData) => {
    try {
      const response = await api.post(`/teachers/teacher-profiles/${teacherId}/update-tpd/`, moduleData);
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

  markCBCtrained: async (teacherId, trainingData) => {
    try {
      const response = await api.post(`/teachers/teacher-profiles/${teacherId}/mark-cbc-trained/`, trainingData, {
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
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || error.message,
          status: error.response?.status
        }
      };
    }
  },

  // ==================== SEARCH ====================
  searchTeachers: async (searchQuery, params = {}) => {
    try {
      const response = await api.get('/teachers/teacher-profiles/search/', {
        params: { q: searchQuery, ...params }
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

  // ==================== PROFESSIONAL STANDING ====================
  getProfessionalStanding: async (params = {}) => {
    try {
      const response = await api.get('/teachers/professional-standing/', { params });
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

  addProfessionalStanding: async (standingData) => {
    try {
      const response = await api.post('/teachers/professional-standing/', standingData);
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
  }
};