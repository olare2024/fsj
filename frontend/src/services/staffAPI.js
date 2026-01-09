import api from './api';

export const staffAPI = {
  // ==================== DASHBOARD & OVERVIEW ====================
  
  getDashboard: async () => {
    try {
      const response = await api.get('/staff/dashboard/');
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

  getStaffOverview: async (params = {}) => {
    try {
      const response = await api.get('/staff/overview/', { params });
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

  // ==================== STUDENT MANAGEMENT ====================

  getStudents: async (params = {}) => {
    try {
      const response = await api.get('/staff/students/', { params });
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

  getStudentById: async (id) => {
    try {
      const response = await api.get(`/staff/students/${id}/`);
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

  createStudent: async (studentData) => {
    try {
      const response = await api.post('/staff/students/', studentData);
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

  updateStudent: async (id, studentData) => {
    try {
      const response = await api.put(`/staff/students/${id}/`, studentData);
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

  transferStudent: async (id, transferData) => {
    try {
      const response = await api.post(`/staff/students/${id}/transfer/`, transferData);
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

  // ==================== ATTENDANCE MANAGEMENT ====================

  getAttendance: async (params = {}) => {
    try {
      const response = await api.get('/staff/attendance/', { params });
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

  markAttendance: async (attendanceData) => {
    try {
      const response = await api.post('/staff/attendance/mark/', attendanceData);
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

  bulkMarkAttendance: async (bulkAttendanceData) => {
    try {
      const response = await api.post('/staff/attendance/bulk-mark/', bulkAttendanceData);
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

  getAttendanceReport: async (params = {}) => {
    try {
      const response = await api.get('/staff/attendance/report/', { params });
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

  // ==================== STUDENT RECORDS ====================

  getStudentRecords: async (studentId, params = {}) => {
    try {
      const response = await api.get(`/staff/students/${studentId}/records/`, { params });
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

  updateStudentRecord: async (studentId, recordData) => {
    try {
      const response = await api.put(`/staff/students/${studentId}/records/`, recordData);
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

  // ==================== ADMISSIONS & ENROLLMENT ====================

  getApplications: async (params = {}) => {
    try {
      const response = await api.get('/staff/admissions/applications/', { params });
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

  getApplicationById: async (id) => {
    try {
      const response = await api.get(`/staff/admissions/applications/${id}/`);
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

  processApplication: async (id, decisionData) => {
    try {
      const response = await api.post(`/staff/admissions/applications/${id}/process/`, decisionData);
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

  createEnrollment: async (enrollmentData) => {
    try {
      const response = await api.post('/staff/admissions/enrollments/', enrollmentData);
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

  // ==================== CLASS MANAGEMENT ====================

  getClasses: async (params = {}) => {
    try {
      const response = await api.get('/staff/classes/', { params });
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

  getClassById: async (id) => {
    try {
      const response = await api.get(`/staff/classes/${id}/`);
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

  getClassStudents: async (classId, params = {}) => {
    try {
      const response = await api.get(`/staff/classes/${classId}/students/`, { params });
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

  assignStudentToClass: async (classId, assignmentData) => {
    try {
      const response = await api.post(`/staff/classes/${classId}/assign-student/`, assignmentData);
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

  // ==================== TIMETABLE MANAGEMENT ====================

  getTimetable: async (params = {}) => {
    try {
      const response = await api.get('/staff/timetable/', { params });
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

  updateTimetable: async (timetableData) => {
    try {
      const response = await api.put('/staff/timetable/', timetableData);
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

  getClassTimetable: async (classId, params = {}) => {
    try {
      const response = await api.get(`/staff/classes/${classId}/timetable/`, { params });
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

  // ==================== COMMUNICATIONS ====================

  sendAnnouncement: async (announcementData) => {
    try {
      const response = await api.post('/staff/communications/announcements/', announcementData);
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

  getAnnouncements: async (params = {}) => {
    try {
      const response = await api.get('/staff/communications/announcements/', { params });
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

  sendParentMessage: async (messageData) => {
    try {
      const response = await api.post('/staff/communications/parent-messages/', messageData);
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

  // ==================== REPORTS & DOCUMENTS ====================

  generateStudentReport: async (reportData) => {
    try {
      const response = await api.post('/staff/reports/student-report/', reportData);
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

  generateClassReport: async (classId, reportData = {}) => {
    try {
      const response = await api.post(`/staff/reports/class-report/${classId}/`, reportData);
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

  generateAttendanceReport: async (reportData = {}) => {
    try {
      const response = await api.post('/staff/reports/attendance-report/', reportData);
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

  downloadReport: async (reportId, format = 'pdf') => {
    try {
      const response = await api.get(`/staff/reports/${reportId}/download/`, {
        params: { format },
        responseType: 'blob'
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

  // ==================== DOCUMENT MANAGEMENT ====================

  uploadStudentDocument: async (studentId, formData, config = {}) => {
    try {
      const response = await api.post(`/staff/students/${studentId}/documents/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        ...config
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
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  getStudentDocuments: async (studentId, params = {}) => {
    try {
      const response = await api.get(`/staff/students/${studentId}/documents/`, { params });
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

  generateStudentID: async (studentId, idData = {}) => {
    try {
      const response = await api.post(`/staff/students/${studentId}/generate-id/`, idData);
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

  // ==================== FEE MANAGEMENT ====================

  getStudentFees: async (studentId, params = {}) => {
    try {
      const response = await api.get(`/staff/students/${studentId}/fees/`, { params });
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

  generateFeeStatement: async (studentId, statementData = {}) => {
    try {
      const response = await api.post(`/staff/students/${studentId}/fee-statement/`, statementData);
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

  // ==================== PARENT MANAGEMENT ====================

  getParents: async (params = {}) => {
    try {
      const response = await api.get('/staff/parents/', { params });
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

  getParentById: async (id) => {
    try {
      const response = await api.get(`/staff/parents/${id}/`);
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

  updateParent: async (id, parentData) => {
    try {
      const response = await api.put(`/staff/parents/${id}/`, parentData);
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

  // ==================== MEETING MANAGEMENT ====================

  scheduleMeeting: async (meetingData) => {
    try {
      const response = await api.post('/staff/meetings/', meetingData);
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

  getMeetings: async (params = {}) => {
    try {
      const response = await api.get('/staff/meetings/', { params });
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

  updateMeeting: async (id, meetingData) => {
    try {
      const response = await api.put(`/staff/meetings/${id}/`, meetingData);
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

  // ==================== BULK OPERATIONS ====================

  bulkImportStudents: async (formData, config = {}) => {
    try {
      const response = await api.post('/staff/students/bulk-import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        ...config
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
          details: error.response?.data?.details,
          status: error.response?.status
        }
      };
    }
  },

  downloadStudentTemplate: async () => {
    try {
      const response = await api.get('/staff/students/download-template/', {
        responseType: 'blob'
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

  // ==================== SETTINGS & CONFIGURATION ====================

  getStaffSettings: async () => {
    try {
      const response = await api.get('/staff/settings/');
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

  updateStaffSettings: async (settingsData) => {
    try {
      const response = await api.put('/staff/settings/', settingsData);
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

  // ==================== TASK MANAGEMENT ====================

  getTasks: async (params = {}) => {
    try {
      const response = await api.get('/staff/tasks/', { params });
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

  createTask: async (taskData) => {
    try {
      const response = await api.post('/staff/tasks/', taskData);
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

  updateTask: async (id, taskData) => {
    try {
      const response = await api.put(`/staff/tasks/${id}/`, taskData);
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

  completeTask: async (id, completionData = {}) => {
    try {
      const response = await api.post(`/staff/tasks/${id}/complete/`, completionData);
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

  // ==================== NOTIFICATIONS ====================

  getNotifications: async (params = {}) => {
    try {
      const response = await api.get('/staff/notifications/', { params });
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

  markNotificationRead: async (notificationId) => {
    try {
      const response = await api.post(`/staff/notifications/${notificationId}/mark-read/`);
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

  // ==================== AUDIT LOGS ====================

  getStaffAuditLogs: async (params = {}) => {
    try {
      const response = await api.get('/staff/audit-logs/', { params });
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

export default staffAPI;