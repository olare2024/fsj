import api from './api';

export const dashboardAPI = {
  /**
   * Get Dashboard Data
   * GET /dashboard/
   */
  getDashboardData: async () => {
    try {
      const response = await api.get('/dashboard/');
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

  /**
   * Export Dashboard Data
   * POST /dashboard/export/
   */
  exportDashboard: async () => {
    try {
      const response = await api.post('/dashboard/export/');
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

  /**
   * Get Recent Activities
   * GET /dashboard/activities/
   */
  getRecentActivities: async (limit = 10) => {
    try {
      const response = await api.get('/dashboard/activities/', {
        params: { limit }
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

  /**
   * Get User Statistics
   * GET /dashboard/stats/
   */
  getUserStats: async () => {
    try {
      const response = await api.get('/dashboard/stats/');
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

export default dashboardAPI;