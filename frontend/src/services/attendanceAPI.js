import api from './api';

// ==================== ATTENDANCE API ====================

export const attendanceAPI = {
  // ==================== ATTENDANCE RECORDING ====================
  
  // Record attendance (single student)
  recordAttendance: async (attendanceData, signal = null) => {
    try {
      const response = await api.post('/attendance/record/', attendanceData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Bulk attendance recording
  bulkRecordAttendance: async (attendanceData, signal = null) => {
    try {
      const response = await api.post('/attendance/record/bulk/', attendanceData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get/Set class attendance
  getClassAttendance: async (classId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/attendance/record/class/${classId}/`, {
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

  // ==================== ATTENDANCE MANAGEMENT ====================
  
  // Get all attendance records
  getAttendanceRecords: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/records/', {
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

  // Get specific attendance record
  getAttendanceRecord: async (recordId, signal = null) => {
    try {
      const response = await api.get(`/attendance/records/${recordId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update attendance record
  updateAttendanceRecord: async (recordId, attendanceData, signal = null) => {
    try {
      const response = await api.patch(`/attendance/records/${recordId}/`, attendanceData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Delete attendance record
  deleteAttendanceRecord: async (recordId, signal = null) => {
    try {
      const response = await api.delete(`/attendance/records/${recordId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== ATTENDANCE REPORTS ====================
  
  // Get student attendance report
  getStudentAttendanceReport: async (studentId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/attendance/reports/student/${studentId}/`, {
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

  // Get class attendance report
  getClassAttendanceReport: async (classId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/attendance/reports/class/${classId}/`, {
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

  // Get daily attendance report
  getDailyAttendanceReport: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/reports/daily/', {
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

  // Get monthly attendance report
  getMonthlyAttendanceReport: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/reports/monthly/', {
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

  // Get term attendance report
  getTermAttendanceReport: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/reports/term/', {
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

  // ==================== ATTENDANCE STATISTICS ====================
  
  // Get student attendance statistics
  getStudentAttendanceStats: async (studentId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/attendance/stats/student/${studentId}/`, {
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

  // Get class attendance statistics
  getClassAttendanceStats: async (classId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/attendance/stats/class/${classId}/`, {
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

  // Get school-wide attendance statistics
  getSchoolAttendanceStats: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/stats/school/', {
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

  // ==================== TEACHER & STAFF ATTENDANCE ====================
  
  // Get teacher attendance list
  getTeacherAttendance: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/teachers/', {
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

  // Get staff attendance list
  getStaffAttendance: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/staff/', {
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

  // ==================== CALENDAR INTEGRATION ====================
  
  // Get attendance calendar data
  getAttendanceCalendar: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/calendar/', {
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

  // ==================== UTILITY METHODS ====================
  
  // Search attendance records
  searchAttendance: async (query, params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/records/', {
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

  // Filter attendance by date range
  filterAttendanceByDate: async (startDate, endDate, params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/records/', {
        params: { start_date: startDate, end_date: endDate, ...params },
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

  // Export attendance report
  exportAttendanceReport: async (reportType = 'csv', params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/reports/export/', {
        params: { format: reportType, ...params },
        responseType: 'blob',
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status,
        format: reportType
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get attendance summary for dashboard
  getAttendanceSummary: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/summary/', {
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

  // Get attendance alerts (late, absent, etc.)
  getAttendanceAlerts: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/alerts/', {
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

  // Mark attendance alert as resolved
  resolveAttendanceAlert: async (alertId, signal = null) => {
    try {
      const response = await api.post(`/attendance/alerts/${alertId}/resolve/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get attendance trends
  getAttendanceTrends: async (period = 'monthly', params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/trends/', {
        params: { period, ...params },
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

  // Get attendance by status
  getAttendanceByStatus: async (status, params = {}, signal = null) => {
    try {
      const response = await api.get('/attendance/records/', {
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

  // Get attendance patterns
  getAttendancePatterns: async (studentId = null, params = {}, signal = null) => {
    try {
      const url = studentId 
        ? `/attendance/patterns/student/${studentId}/`
        : '/attendance/patterns/';
      
      const response = await api.get(url, {
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

  // ==================== BACKWARD COMPATIBILITY ====================
  
  // Legacy method for backward compatibility
  markAttendance: async (attendanceData, signal = null) => {
    return attendanceAPI.recordAttendance(attendanceData, signal);
  },

  // Legacy bulk attendance
  bulkMarkAttendance: async (attendanceData, signal = null) => {
    return attendanceAPI.bulkRecordAttendance(attendanceData, signal);
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

// ==================== ATTENDANCE CONSTANTS ====================

export const ATTENDANCE_CONSTANTS = {
  // Attendance statuses
  STATUS: {
    PRESENT: 'present',
    ABSENT: 'absent',
    LATE: 'late',
    EXCUSED: 'excused',
    HOLIDAY: 'holiday',
    VACATION: 'vacation',
    SICK_LEAVE: 'sick_leave',
    EMERGENCY_LEAVE: 'emergency_leave'
  },

  // Attendance types
  TYPES: {
    DAILY: 'daily',
    PERIOD: 'period',
    SESSION: 'session',
    EVENT: 'event'
  },

  // Report periods
  REPORT_PERIODS: {
    DAILY: 'daily',
    WEEKLY: 'weekly',
    MONTHLY: 'monthly',
    QUARTERLY: 'quarterly',
    TERM: 'term',
    YEARLY: 'yearly'
  },

  // Attendance patterns
  PATTERNS: {
    REGULAR: 'regular',
    IRREGULAR: 'irregular',
    IMPROVING: 'improving',
    DECLINING: 'declining',
    CONSISTENT: 'consistent'
  },

  // Alert types
  ALERT_TYPES: {
    EXCESSIVE_ABSENCE: 'excessive_absence',
    FREQUENT_LATE: 'frequent_late',
    UNEXCUSED_ABSENCE: 'unexcused_absence',
    PATTERN_CHANGE: 'pattern_change'
  },

  // Export formats
  EXPORT_FORMATS: {
    CSV: 'csv',
    EXCEL: 'excel',
    PDF: 'pdf',
    JSON: 'json'
  }
};

export default attendanceAPI;