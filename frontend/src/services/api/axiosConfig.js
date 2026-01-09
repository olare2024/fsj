import axios from 'axios';
import { generateRequestId, getAuthErrorMessage, clearAuth } from './apiUtils';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  withCredentials: false,
});

// ==================== INTERCEPTORS ====================

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = generateRequestId();
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.params || '');
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
        message: error.message
      });
    }

    // Handle token refresh for 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await api.post('/auth/jwt/refresh/', {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        clearAuth();
        
        // Redirect to login
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    // Handle network errors
    if (!error.response) {
      console.error('🌐 Network Error:', error.message);
    }

    // Handle server errors
    if (error.response?.status >= 500) {
      console.error('🚨 Server Error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

export default api;