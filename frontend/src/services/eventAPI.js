// src/services/eventAPI.js
import api from './api';

export const eventAPI = {
  // ==================== EVENT MANAGEMENT ====================

  // Get all events with filtering and pagination
  getEvents: async (params = {}) => {
    try {
      const response = await api.get('/events/events/', { params });
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

  // Get specific event by ID
  getEventById: async (eventId) => {
    try {
      const response = await api.get(`/events/events/${eventId}/`);
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

  // Get event by slug
  getEventBySlug: async (slug) => {
    try {
      const response = await api.get(`/events/events/slug/${slug}/`);
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

  // Create new event
  createEvent: async (eventData) => {
    try {
      const response = await api.post('/events/events/', eventData);
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

  // Update event
  updateEvent: async (eventId, eventData) => {
    try {
      const response = await api.patch(`/events/events/${eventId}/`, eventData);
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

  // Delete event
  deleteEvent: async (eventId) => {
    try {
      const response = await api.delete(`/events/events/${eventId}/`);
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

  // ==================== EVENT FILTERING ====================

  // Get upcoming events
  getUpcomingEvents: async (params = {}) => {
    try {
      const response = await api.get('/events/events/upcoming/', { params });
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

  // Get ongoing events
  getOngoingEvents: async (params = {}) => {
    try {
      const response = await api.get('/events/events/ongoing/', { params });
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

  // Get past events
  getPastEvents: async (params = {}) => {
    try {
      const response = await api.get('/events/events/past/', { params });
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

  // Get featured events
  getFeaturedEvents: async (params = {}) => {
    try {
      const response = await api.get('/events/events/featured/', { params });
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

  // Get events by type
  getEventsByType: async (eventType, params = {}) => {
    try {
      const response = await api.get(`/events/events/type/${eventType}/`, { params });
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

  // ==================== EVENT REGISTRATION ====================

  // Register for an event
  registerForEvent: async (eventId, registrationData = {}) => {
    try {
      const response = await api.post(`/events/events/${eventId}/register/`, registrationData);
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

  // Get user's event registrations
  getMyRegistrations: async (params = {}) => {
    try {
      const response = await api.get('/events/registrations/', { params });
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

  // Get specific registration
  getRegistration: async (registrationId) => {
    try {
      const response = await api.get(`/events/registrations/${registrationId}/`);
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

  // Update registration
  updateRegistration: async (registrationId, registrationData) => {
    try {
      const response = await api.patch(`/events/registrations/${registrationId}/`, registrationData);
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

  // Cancel registration
  cancelRegistration: async (registrationId) => {
    try {
      const response = await api.patch(`/events/registrations/${registrationId}/`, { status: 'cancelled' });
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

  // Check-in for event
  checkIn: async (registrationId) => {
    try {
      const response = await api.post(`/events/registrations/${registrationId}/check-in/`);
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

  // ==================== EVENT REGISTRATION MANAGEMENT (Admin/Coordinator) ====================

  // Get all registrations for an event
  getEventRegistrations: async (eventId, params = {}) => {
    try {
      const response = await api.get(`/events/events/${eventId}/registrations/`, { params });
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

  // Update registration status (admin/coordinator only)
  updateRegistrationStatus: async (registrationId, statusData) => {
    try {
      const response = await api.patch(`/events/registrations/${registrationId}/status/`, statusData);
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

  // Bulk update registrations
  bulkUpdateRegistrations: async (eventId, updateData) => {
    try {
      const response = await api.post(`/events/events/${eventId}/bulk-update-registrations/`, updateData);
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

  // ==================== EVENT CATEGORIES ====================

  // Get all event categories
  getCategories: async (params = {}) => {
    try {
      const response = await api.get('/events/categories/', { params });
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

  // Create category (admin only)
  createCategory: async (categoryData) => {
    try {
      const response = await api.post('/events/categories/', categoryData);
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

  // Update category (admin only)
  updateCategory: async (categoryId, categoryData) => {
    try {
      const response = await api.patch(`/events/categories/${categoryId}/`, categoryData);
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

  // ==================== EVENT FEEDBACK ====================

  // Submit event feedback
  submitFeedback: async (eventId, feedbackData) => {
    try {
      const response = await api.post(`/events/events/${eventId}/feedback/`, feedbackData);
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

  // Get event feedback
  getEventFeedback: async (eventId, params = {}) => {
    try {
      const response = await api.get(`/events/events/${eventId}/feedback/`, { params });
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

  // Get user's feedback
  getMyFeedback: async (params = {}) => {
    try {
      const response = await api.get('/events/feedback/', { params });
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

  // Mark feedback as helpful
  markFeedbackHelpful: async (feedbackId) => {
    try {
      const response = await api.post(`/events/feedback/${feedbackId}/mark-helpful/`);
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

  // ==================== EVENT REMINDERS ====================

  // Get event reminders
  getReminders: async (params = {}) => {
    try {
      const response = await api.get('/events/reminders/', { params });
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

  // Create reminder (admin/coordinator only)
  createReminder: async (reminderData) => {
    try {
      const response = await api.post('/events/reminders/', reminderData);
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

  // ==================== EVENT ATTACHMENTS ====================

  // Get event attachments
  getEventAttachments: async (eventId, params = {}) => {
    try {
      const response = await api.get(`/events/events/${eventId}/attachments/`, { params });
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

  // Upload attachment (admin/coordinator only)
  uploadAttachment: async (eventId, formData) => {
    try {
      const response = await api.post(`/events/events/${eventId}/attachments/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
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

  // Download attachment
  downloadAttachment: async (attachmentId) => {
    try {
      const response = await api.post(`/events/attachments/${attachmentId}/download/`);
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

  // ==================== EVENT ACTIONS (Admin/Coordinator) ====================

  // Approve event (admin only)
  approveEvent: async (eventId) => {
    try {
      const response = await api.post(`/events/events/${eventId}/approve/`);
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

  // Publish event
  publishEvent: async (eventId) => {
    try {
      const response = await api.post(`/events/events/${eventId}/publish/`);
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

  // Cancel event
  cancelEvent: async (eventId, reason = '') => {
    try {
      const response = await api.post(`/events/events/${eventId}/cancel/`, { reason });
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

  // Feature event (admin only)
  featureEvent: async (eventId, featured = true) => {
    try {
      const response = await api.patch(`/events/events/${eventId}/`, { is_featured: featured });
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

  // ==================== EVENT STATISTICS & ANALYTICS ====================

  // Get event statistics
  getEventStats: async (eventId) => {
    try {
      const response = await api.get(`/events/events/${eventId}/statistics/`);
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

  // Get overall events statistics (admin only)
  getEventsStatistics: async (params = {}) => {
    try {
      const response = await api.get('/events/statistics/', { params });
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

  // Export event data (admin only)
  exportEvents: async (params = {}) => {
    try {
      const response = await api.get('/events/export/', { 
        params,
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

  // ==================== EVENT CALENDAR INTEGRATION ====================

  // Get events for calendar view
  getCalendarEvents: async (params = {}) => {
    try {
      const response = await api.get('/events/calendar/', { params });
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

  // Export event to personal calendar
  exportToCalendar: async (eventId, calendarType = 'google') => {
    try {
      const response = await api.get(`/events/events/${eventId}/export-calendar/${calendarType}/`);
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

  // ==================== EVENT SEARCH ====================

  // Search events
  searchEvents: async (query, params = {}) => {
    try {
      const response = await api.get('/events/search/', { 
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
          message: error.response?.data?.error || error.message,
          status: error.response?.status
        }
      };
    }
  }
};

export default eventAPI;