import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

// ==================== AXIOS CONFIGURATION ====================

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  withCredentials: false, // Keep this as false for JWT authentication
});

// ==================== INTERCEPTORS ====================

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // REMOVE X-Request-ID header - it's causing CORS issues
    // config.headers['X-Request-ID'] = generateRequestId();
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        baseURL: config.baseURL,
        fullURL: config.baseURL + config.url,
        headers: config.headers
      });
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Enhanced response interceptor with token refresh
api.interceptors.response.use(
  (response) => {
    // Log successful responses in development
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`, response.data);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Log error in development
    if (import.meta.env.DEV) {
      console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        config: error.config
      });
    }

    // Handle token refresh for 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await api.post('/auth/token/refresh/', {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        apiUtils.clearAuth();
        
        // Redirect to login
        if (window.location.pathname !== '/login') {
          window.location.href = '/login?session=expired';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ==================== UTILITY FUNCTIONS ====================

// Helper function to get user-friendly error messages
function getErrorMessage(error, defaultMessage = 'An error occurred') {
  if (!error.response) {
    if (error.code === 'NETWORK_ERROR') {
      return 'Network error. Please check your connection and try again.';
    }
    return 'Unable to connect to server. Please try again.';
  }

  const { data, status } = error.response;
  
  if (status === 400) {
    if (data.detail) return data.detail;
    if (data.message) return data.message;
    if (typeof data === 'string') return data;
    if (data.non_field_errors) return data.non_field_errors[0];
    return 'Invalid input. Please check your data.';
  }
  
  if (status === 401) return 'Authentication required. Please login again.';
  if (status === 403) return 'You do not have permission to perform this action.';
  if (status === 404) return 'Resource not found.';
  if (status >= 500) return 'Server error. Please try again later.';
  
  return error.message || defaultMessage;
}

// ==================== API UTILITIES ====================

export const apiUtils = {
  getErrorMessage,
  
  isTokenExpiring: () => {
    const token = localStorage.getItem('access_token');
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiresIn = payload.exp * 1000 - Date.now();
      return expiresIn < 5 * 60 * 1000; // 5 minutes
    } catch {
      return true;
    }
  },

  clearAuth: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    delete api.defaults.headers.common['Authorization'];
  },

  formatFormData: (data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    return formData;
  },

  downloadFile: (response, filename = 'download') => {
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Standard API response handler
  handleResponse: async (apiCall) => {
    try {
      const response = await apiCall();
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: getErrorMessage(error),
          details: error.response?.data,
          status: error.response?.status
        }
      };
    }
  }
};

// Export the main api instance for custom requests
export default api;