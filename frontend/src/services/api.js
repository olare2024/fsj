// src/services/api.js - ENHANCED VERSION
import axios from 'axios';

// ==================== API CONFIGURATION ====================
const API_CONFIG = {
  BASE_URL: '/api/v1',
  TIMEOUT: 30000, // Reduced from 30000 to 10000ms for better UX
  MAX_RETRIES: 2,
  RETRY_DELAY: 1000,
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes cache
};

console.log('🚀 Using API Base (via proxy):', API_CONFIG.BASE_URL);
console.log('🔗 Actual backend URL: http://localhost:8000' + API_CONFIG.BASE_URL);

// ==================== GLOBAL CACHE ====================
const apiCache = new Map();
const pendingRequests = new Map();

// ==================== HELPER FUNCTIONS ====================
const getCacheKey = (config) => {
  return `${config.method}:${config.url}:${JSON.stringify(config.params)}:${JSON.stringify(config.data)}`;
};

const getCachedResponse = (cacheKey) => {
  const cached = apiCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < API_CONFIG.CACHE_DURATION) {
    return cached.data;
  }
  return null;
};

const setCachedResponse = (cacheKey, data) => {
  apiCache.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
};

// ==================== AXIOS INSTANCE ====================
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// ==================== ENHANCED REQUEST INTERCEPTOR ====================
api.interceptors.request.use(
  (config) => {
    // Add request ID for tracking
    config.requestId = Date.now() + Math.random().toString(36).substr(2, 9);
    config.startTime = Date.now();
    
    // Add authorization token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Debug logging in development
    if (import.meta.env.DEV) {
      console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        requestId: config.requestId,
        params: config.params,
        data: config.data,
        fullPath: config.baseURL + config.url,
      });
    }
    
    // Handle GET requests with cache
    if (config.method?.toLowerCase() === 'get' && config.useCache !== false) {
      const cacheKey = getCacheKey(config);
      const cachedData = getCachedResponse(cacheKey);
      
      if (cachedData) {
        console.log(`📦 Using cached response for: ${config.url}`);
        
        // Create a fake response object from cache
        const cachedResponse = {
          data: cachedData,
          status: 200,
          statusText: 'OK',
          headers: {},
          config,
          request: {}
        };
        
        // Reject the promise to stop the actual request
        return Promise.reject({
          config,
          response: cachedResponse,
          isFromCache: true
        });
      }
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// ==================== ENHANCED RESPONSE INTERCEPTOR ====================
api.interceptors.response.use(
  (response) => {
    const endTime = Date.now();
    const duration = endTime - response.config.startTime;
    
    // Debug logging
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status} ${response.config.url} (${duration}ms)`, {
        requestId: response.config.requestId,
        data: response.data,
      });
    }
    
    // Cache successful GET responses
    if (response.config.method?.toLowerCase() === 'get' && response.config.useCache !== false) {
      const cacheKey = getCacheKey(response.config);
      setCachedResponse(cacheKey, response.data);
    }
    
    return response;
  },
  async (error) => {
    const endTime = Date.now();
    const duration = endTime - (error.config?.startTime || endTime);
    
    // Handle cached response rejection
    if (error.isFromCache) {
      console.log(`📦 Returning cached data for: ${error.config.url} (${duration}ms)`);
      return Promise.resolve(error.response);
    }
    
    // Enhanced error logging
    if (import.meta.env.DEV) {
      console.error('❌ API Error:', {
        status: error.response?.status,
        url: error.config?.url,
        message: error.message,
        code: error.code,
        duration: `${duration}ms`,
        requestId: error.config?.requestId,
      });
    }
    
    const originalRequest = error.config;
    
    // Handle timeout specifically
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.warn(`⏰ Request timeout for ${originalRequest?.url} (${duration}ms)`);
      
      return Promise.reject({
        ...error,
        isTimeout: true,
        message: `Request timeout. Please check your connection and try again.`,
      });
    }
    
    // Handle 401 - Token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          console.log('🔄 Attempting token refresh...');
          
          // Use a separate axios instance to avoid interceptors
          const refreshResponse = await axios.post(
            'http://localhost:8000/auth/token/refresh/',
            { refresh: refreshToken },
            { timeout: 5000 }
          );
          
          const { access } = refreshResponse.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          
          console.log('✅ Token refreshed successfully');
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError.message);
        // Don't clear tokens here, let AuthContext handle it
      }
    }
    
    // Handle 404 errors
    if (error.response?.status === 404) {
      console.warn(`🔍 Endpoint not found: ${originalRequest?.url}`);
      
      return Promise.reject({
        ...error,
        isNotFound: true,
        message: `The requested resource was not found: ${originalRequest?.url}`,
      });
    }
    
    // Handle 500 errors
    if (error.response?.status >= 500) {
      console.error(`💥 Server error for ${originalRequest?.url}:`, error.response?.status);
      
      return Promise.reject({
        ...error,
        isServerError: true,
        message: 'Server error. Please try again later.',
      });
    }
    
    return Promise.reject(error);
  }
);

// ==================== ENHANCED API UTILITIES ====================
export const apiUtils = {
  getErrorMessage: (error, defaultMessage = 'An error occurred') => {
    // Handle timeout
    if (error.isTimeout) {
      return 'Request timeout. Please check your connection and try again.';
    }
    
    // Handle not found
    if (error.isNotFound) {
      return 'The requested resource was not found.';
    }
    
    // Handle server error
    if (error.isServerError) {
      return 'Server error. Please try again later.';
    }
    
    if (!error.response) {
      if (error.code === 'NETWORK_ERROR' || error.message.includes('Network')) {
        return 'Network error. Please check your internet connection.';
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
    
    if (status === 401) return 'Session expired. Please login again.';
    if (status === 403) return 'You do not have permission to perform this action.';
    if (status === 404) return 'Resource not found.';
    if (status >= 500) return 'Server error. Please try again later.';
    
    return error.message || defaultMessage;
  },

  clearAuth: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('auth_timestamp');
    localStorage.removeItem('last_activity');
    apiCache.clear(); // Clear all cached data
  },

  clearCache: () => {
    apiCache.clear();
    console.log('🧹 API cache cleared');
  },

  testConnection: async () => {
    const tests = [
      {
        name: 'Proxy Connection',
        url: '/',
        method: 'GET',
        timeout: 5000
      },
      {
        name: 'Backend Server',
        url: 'http://localhost:8000/',
        method: 'GET',
        timeout: 5000,
        direct: true
      },
      {
        name: 'Health Check',
        url: '/health/',
        method: 'GET',
        timeout: 5000
      }
    ];

    const results = [];

    for (const test of tests) {
      try {
        console.log(`🧪 Testing ${test.name}...`);
        
        let response;
        if (test.direct) {
          // Test direct connection (bypass proxy)
          response = await axios({
            method: test.method,
            url: test.url,
            timeout: test.timeout
          });
        } else {
          // Test through proxy
          response = await api({
            method: test.method,
            url: test.url,
            timeout: test.timeout
          });
        }

        results.push({
          name: test.name,
          success: true,
          status: response.status,
          time: response.config?.duration || 'N/A'
        });
        
        console.log(`✅ ${test.name}: Success (${response.status})`);
      } catch (error) {
        results.push({
          name: test.name,
          success: false,
          error: error.message,
          code: error.code
        });
        
        console.log(`❌ ${test.name}: Failed - ${error.message}`);
      }
    }

    console.log('\n📊 Connection Test Results:');
    results.forEach(result => {
      if (result.success) {
        console.log(`  ✅ ${result.name}: ${result.status} (${result.time}ms)`);
      } else {
        console.log(`  ❌ ${result.name}: ${result.error}`);
      }
    });

    return results;
  },

  // Enhanced request with retry logic
  requestWithRetry: async (config, options = {}) => {
    const { maxRetries = API_CONFIG.MAX_RETRIES, retryDelay = API_CONFIG.RETRY_DELAY } = options;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        if (attempt > 0) {
          console.log(`🔄 Retry attempt ${attempt} for ${config.url}`);
          await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
        }
        
        const response = await api(config);
        return response;
      } catch (error) {
        // Don't retry on certain errors
        if (error.response?.status === 404 || error.response?.status === 403) {
          throw error;
        }
        
        if (attempt === maxRetries) {
          console.error(`❌ All retries failed for ${config.url}`);
          throw error;
        }
        
        console.log(`⚠️ Request failed (attempt ${attempt + 1}), retrying...`);
      }
    }
  },

  // Get with fallback data
  getWithFallback: async (url, fallbackData = null, options = {}) => {
    try {
      const response = await api.get(url, options);
      return response.data;
    } catch (error) {
      if (fallbackData !== null) {
        console.warn(`⚠️ Using fallback data for ${url}:`, error.message);
        return fallbackData;
      }
      throw error;
    }
  }
};

export default api;