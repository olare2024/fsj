import api from './api';

// ==================== TIMETABLE API ====================

export const timetableAPI = {
  // ==================== TIMETABLE MANAGEMENT ====================
  
  // Get current/active timetable
  getCurrentTimetable: async (signal = null) => {
    try {
      const response = await api.get('/timetable/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Generate new timetable
  generateTimetable: async (generationData, signal = null) => {
    try {
      const response = await api.post('/timetable/generate/', generationData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Publish timetable
  publishTimetable: async (timetableId, signal = null) => {
    try {
      const response = await api.post(`/timetable/publish/${timetableId}/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Check for timetable conflicts
  checkTimetableConflicts: async (checkData = {}, signal = null) => {
    try {
      const response = await api.post('/timetable/conflicts/check/', checkData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== CLASS TIMETABLES ====================
  getClassTimetable: async (classId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/timetable/class/${classId}/`, {
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

  // ==================== TEACHER TIMETABLES ====================
  getTeacherTimetable: async (teacherId = null, params = {}, signal = null) => {
    try {
      const endpoint = teacherId 
        ? `/timetable/teacher/${teacherId}/`
        : '/timetable/teacher/';
      
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

  // ==================== STUDENT TIMETABLES ====================
  getStudentTimetable: async (studentId = null, params = {}, signal = null) => {
    try {
      const endpoint = studentId 
        ? `/timetable/student/${studentId}/`
        : '/timetable/student/';
      
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

  // ==================== DAILY SCHEDULE ====================
  getDailySchedule: async (date = null, params = {}, signal = null) => {
    try {
      const queryParams = date ? { date, ...params } : params;
      const response = await api.get('/timetable/daily/', {
        params: queryParams,
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

  // ==================== ROOM MANAGEMENT ====================
  
  // Get all rooms
  getRooms: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/rooms/', {
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

  // Get single room details
  getRoom: async (roomId, signal = null) => {
    try {
      const response = await api.get(`/timetable/rooms/${roomId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Create new room
  createRoom: async (roomData, signal = null) => {
    try {
      const response = await api.post('/timetable/rooms/', roomData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update room
  updateRoom: async (roomId, roomData, signal = null) => {
    try {
      const response = await api.put(`/timetable/rooms/${roomId}/`, roomData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Delete room
  deleteRoom: async (roomId, signal = null) => {
    try {
      const response = await api.delete(`/timetable/rooms/${roomId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get room availability
  getRoomAvailability: async (roomId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/timetable/rooms/${roomId}/availability/`, {
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

  // ==================== ROOM BOOKINGS ====================
  
  // Get room bookings
  getRoomBookings: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/bookings/', {
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

  // Create room booking
  createRoomBooking: async (bookingData, signal = null) => {
    try {
      const response = await api.post('/timetable/bookings/', bookingData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update room booking
  updateRoomBooking: async (bookingId, bookingData, signal = null) => {
    try {
      const response = await api.put(`/timetable/bookings/${bookingId}/`, bookingData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Delete room booking
  deleteRoomBooking: async (bookingId, signal = null) => {
    try {
      const response = await api.delete(`/timetable/bookings/${bookingId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== TIMETABLE ADJUSTMENTS ====================
  
  // Get timetable adjustments
  getTimetableAdjustments: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/adjustments/', {
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

  // Get single adjustment
  getTimetableAdjustment: async (adjustmentId, signal = null) => {
    try {
      const response = await api.get(`/timetable/adjustments/${adjustmentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Create adjustment
  createTimetableAdjustment: async (adjustmentData, signal = null) => {
    try {
      const response = await api.post('/timetable/adjustments/', adjustmentData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update adjustment
  updateTimetableAdjustment: async (adjustmentId, adjustmentData, signal = null) => {
    try {
      const response = await api.put(`/timetable/adjustments/${adjustmentId}/`, adjustmentData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Delete adjustment
  deleteTimetableAdjustment: async (adjustmentId, signal = null) => {
    try {
      const response = await api.delete(`/timetable/adjustments/${adjustmentId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== SPECIAL SCHEDULES ====================
  
  // Get special schedules
  getSpecialSchedules: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/special-schedules/', {
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

  // Create special schedule
  createSpecialSchedule: async (scheduleData, signal = null) => {
    try {
      const response = await api.post('/timetable/special-schedules/', scheduleData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update special schedule
  updateSpecialSchedule: async (scheduleId, scheduleData, signal = null) => {
    try {
      const response = await api.put(`/timetable/special-schedules/${scheduleId}/`, scheduleData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Delete special schedule
  deleteSpecialSchedule: async (scheduleId, signal = null) => {
    try {
      const response = await api.delete(`/timetable/special-schedules/${scheduleId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== TEACHER AVAILABILITY ====================
  
  // Get teacher availability
  getTeacherAvailability: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/availability/', {
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

  // Set teacher availability
  setTeacherAvailability: async (availabilityData, signal = null) => {
    try {
      const response = await api.post('/timetable/availability/', availabilityData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update teacher availability
  updateTeacherAvailability: async (availabilityId, availabilityData, signal = null) => {
    try {
      const response = await api.put(`/timetable/availability/${availabilityId}/`, availabilityData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Delete teacher availability
  deleteTeacherAvailability: async (availabilityId, signal = null) => {
    try {
      const response = await api.delete(`/timetable/availability/${availabilityId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== TIMETABLE CONFLICTS ====================
  
  // Get timetable conflicts
  getTimetableConflicts: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/conflicts/', {
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

  // Resolve conflict
  resolveConflict: async (conflictId, resolutionData, signal = null) => {
    try {
      const response = await api.post(`/timetable/conflicts/${conflictId}/resolve/`, resolutionData, { signal });
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
  
  // Export timetable (PDF/Excel)
  exportTimetable: async (exportType = 'pdf', params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/export/', {
        params: { format: exportType, ...params },
        responseType: 'blob',
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status,
        type: exportType
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get timetable statistics
  getTimetableStats: async (signal = null) => {
    try {
      const response = await api.get('/timetable/stats/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get timetable history
  getTimetableHistory: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/history/', {
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

  // Search timetables
  searchTimetables: async (query, params = {}, signal = null) => {
    try {
      const response = await api.get('/timetable/search/', {
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

  // Validate timetable
  validateTimetable: async (timetableData, signal = null) => {
    try {
      const response = await api.post('/timetable/validate/', timetableData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Clone timetable
  cloneTimetable: async (timetableId, cloneData = {}, signal = null) => {
    try {
      const response = await api.post(`/timetable/${timetableId}/clone/`, cloneData, { signal });
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

// Centralized error handler
const handleError = (error) => {
  // Handle abort errors separately
  if (error.name === 'AbortError') {
    return {
      success: false,
      error: {
        message: 'Request cancelled',
        code: 'CANCELLED'
      }
    };
  }

  // Handle network errors
  if (!error.response) {
    return {
      success: false,
      error: {
        message: error.message || 'Network error',
        code: 'NETWORK_ERROR'
      }
    };
  }

  // Handle HTTP errors
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

// Error code mapping
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

// ==================== TIMETABLE TYPES & CONSTANTS ====================

export const TIMETABLE_CONSTANTS = {
  DAYS: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
  PERIOD_TYPES: ['Lecture', 'Practical', 'Tutorial', 'Break', 'Lab', 'Seminar'],
  STATUSES: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    ARCHIVED: 'archived'
  },
  EXPORT_FORMATS: {
    PDF: 'pdf',
    EXCEL: 'excel',
    CSV: 'csv'
  }
};

// Type definitions for TypeScript (optional)
/*
interface TimetablePeriod {
  id: string;
  day: string;
  period: number;
  subject: string;
  teacher: string;
  room: string;
  class: string;
  start_time: string;
  end_time: string;
}

interface Room {
  id: string;
  name: string;
  capacity: number;
  type: string;
  equipment: string[];
  is_active: boolean;
}

interface TimetableConflict {
  id: string;
  type: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  affected_entities: string[];
  created_at: string;
}
*/

export default timetableAPI;