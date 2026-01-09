import api from './api';

export const parentAPI = {
  // Parent Dashboard
  getDashboard: async () => {
    try {
      const response = await api.get('/parent/dashboard/');
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

  // Get parent's children
  getChildren: async () => {
    try {
      const response = await api.get('/parent/children/');
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

  // Get specific child details
  getChildById: async (childId) => {
    try {
      const response = await api.get(`/parent/children/${childId}/`);
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

  // Get child's academic performance
  getChildPerformance: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/performance/`, { params });
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

  // Get child's attendance
  getChildAttendance: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/attendance/`, { params });
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

  // Get child's assignments
  getChildAssignments: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/assignments/`, { params });
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

  // Get child's behavior reports
  getChildBehavior: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/behavior/`, { params });
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

  // Get child's timetable
  getChildTimetable: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/timetable/`, { params });
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

  // Get child's teachers
  getChildTeachers: async (childId) => {
    try {
      const response = await api.get(`/parent/children/${childId}/teachers/`);
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

  // Get child's fee information
  getChildFees: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/fees/`, { params });
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

  // Get upcoming events for child
  getChildEvents: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/events/`, { params });
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

  // Get child's progress reports
  getChildProgressReports: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/progress-reports/`, { params });
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

  // Communication with teachers
  getTeacherCommunications: async (childId, params = {}) => {
    try {
      const response = await api.get(`/parent/children/${childId}/communications/`, { params });
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

  sendMessageToTeacher: async (childId, messageData) => {
    try {
      const response = await api.post(`/parent/children/${childId}/send-message/`, messageData);
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

  // Schedule meetings with teachers
  scheduleMeeting: async (meetingData) => {
    try {
      const response = await api.post('/parent/schedule-meeting/', meetingData);
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

  getScheduledMeetings: async (params = {}) => {
    try {
      const response = await api.get('/parent/scheduled-meetings/', { params });
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

  // Parent notifications
  getNotifications: async (params = {}) => {
    try {
      const response = await api.get('/parent/notifications/', { params });
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

  markNotificationAsRead: async (notificationId) => {
    try {
      const response = await api.patch(`/parent/notifications/${notificationId}/mark-read/`);
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

  // Parent settings and preferences
  getPreferences: async () => {
    try {
      const response = await api.get('/parent/preferences/');
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

  updatePreferences: async (preferencesData) => {
    try {
      const response = await api.patch('/parent/preferences/', preferencesData);
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

  // Emergency contacts
  getEmergencyContacts: async () => {
    try {
      const response = await api.get('/parent/emergency-contacts/');
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

  updateEmergencyContacts: async (contactsData) => {
    try {
      const response = await api.put('/parent/emergency-contacts/', contactsData);
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

  // Parent feedback and surveys
  submitFeedback: async (feedbackData) => {
    try {
      const response = await api.post('/parent/feedback/', feedbackData);
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

  getSurveys: async (params = {}) => {
    try {
      const response = await api.get('/parent/surveys/', { params });
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

  submitSurvey: async (surveyId, responses) => {
    try {
      const response = await api.post(`/parent/surveys/${surveyId}/submit/`, { responses });
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
  }
};