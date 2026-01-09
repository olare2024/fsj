import api from './api';

// ==================== DOWNLOADS API ====================

export const downloadsAPI = {
  // ==================== CATEGORIES ====================
  getCategories: async () => {
    try {
      const response = await api.get('/downloads/categories/');
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

  createCategory: async (categoryData) => {
    try {
      const response = await api.post('/downloads/categories/', categoryData);
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

  updateCategory: async (id, categoryData) => {
    try {
      const response = await api.put(`/downloads/categories/${id}/`, categoryData);
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

  deleteCategory: async (id) => {
    try {
      const response = await api.delete(`/downloads/categories/${id}/`);
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

  // ==================== FILES ====================
  getFiles: async (params = {}) => {
    try {
      const response = await api.get('/downloads/files/', { params });
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

  getFileById: async (id) => {
    try {
      const response = await api.get(`/downloads/files/${id}/`);
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

  createFile: async (fileData, config = {}) => {
    try {
      const response = await api.post('/downloads/files/', fileData, {
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

  updateFile: async (id, fileData) => {
    try {
      const response = await api.patch(`/downloads/files/${id}/`, fileData);
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

  deleteFile: async (id) => {
    try {
      const response = await api.delete(`/downloads/files/${id}/`);
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

  // ==================== DOWNLOAD OPERATIONS ====================
  downloadFile: async (fileId) => {
    try {
      const response = await api.post(`/downloads/files/${fileId}/download/`, {}, {
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

  getPopularDownloads: async () => {
    try {
      const response = await api.get('/downloads/files/popular/');
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

  // ==================== DOWNLOAD HISTORY ====================
  getDownloadHistory: async (params = {}) => {
    try {
      const response = await api.get('/downloads/history/', { params });
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

  getFileDownloadHistory: async (fileId) => {
    try {
      const response = await api.get(`/downloads/files/${fileId}/download-history/`);
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

  clearDownloadHistory: async () => {
    try {
      const response = await api.delete('/downloads/history/clear/');
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

  // ==================== RATINGS ====================
  rateFile: async (fileId, rating) => {
    try {
      const response = await api.post('/downloads/ratings/', {
        file: fileId,
        rating: rating
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

  updateFileRating: async (ratingId, rating) => {
    try {
      const response = await api.put(`/downloads/ratings/${ratingId}/`, { rating });
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

  getUserRatings: async () => {
    try {
      const response = await api.get('/downloads/ratings/');
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

  deleteRating: async (ratingId) => {
    try {
      const response = await api.delete(`/downloads/ratings/${ratingId}/`);
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

  // ==================== STATISTICS & ANALYTICS ====================
  getDownloadStats: async () => {
    try {
      const response = await api.get('/downloads/files/stats/');
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

  getCategoryStats: async () => {
    try {
      const response = await api.get('/downloads/categories/stats/');
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

  getUserDownloadStats: async () => {
    try {
      const response = await api.get('/downloads/history/stats/');
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

  // ==================== BULK OPERATIONS ====================
  bulkUploadFiles: async (formData, config = {}) => {
    try {
      const response = await api.post('/downloads/files/bulk-upload/', formData, {
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

  bulkDeleteFiles: async (fileIds) => {
    try {
      const response = await api.post('/downloads/files/bulk-delete/', {
        file_ids: fileIds
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

  exportDownloadHistory: async (params = {}) => {
    try {
      const response = await api.get('/downloads/history/export/', {
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

  // ==================== SEARCH & FILTERS ====================
  searchFiles: async (query, filters = {}) => {
    try {
      const response = await api.get('/downloads/files/search/', {
        params: { q: query, ...filters }
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

  getFileTypes: async () => {
    try {
      const response = await api.get('/downloads/files/file-types/');
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

  // ==================== UTILITY FUNCTIONS ====================
  checkFileAccess: async (fileId) => {
    try {
      const response = await api.get(`/downloads/files/${fileId}/check-access/`);
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

  generateDownloadLink: async (fileId, expiresIn = 3600) => {
    try {
      const response = await api.post(`/downloads/files/${fileId}/generate-link/`, {
        expires_in: expiresIn
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

  // ==================== ADMIN OPERATIONS ====================
  getAdminStats: async () => {
    try {
      const response = await api.get('/downloads/admin/stats/');
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

  getSystemUsage: async (period = '30d') => {
    try {
      const response = await api.get('/downloads/admin/usage/', {
        params: { period }
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

export default downloadsAPI;