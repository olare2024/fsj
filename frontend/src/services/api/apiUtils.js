// src/services/api/apiUtils.js

// Utility function to generate unique request ID
export function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Enhanced error handling function
export function handleError(error, defaultMessage = 'An error occurred') {
  console.error('API Error:', error);

  // Network error
  if (!error.response) {
    return {
      success: false,
      error: {
        message: 'Network error. Please check your connection.',
        details: error.message,
        code: 'NETWORK_ERROR'
      }
    };
  }

  const { status, data } = error.response;
  let message = defaultMessage;
  let details = data;
  let validationErrors = {};

  // Handle different HTTP status codes
  switch (status) {
    case 400:
      message = data.message || 'Invalid request data';
      if (data.errors) {
        validationErrors = data.errors;
        message = 'Please fix the validation errors';
      } else if (typeof data === 'object') {
        // Extract field errors
        Object.keys(data).forEach(key => {
          if (Array.isArray(data[key]) && data[key].length > 0) {
            validationErrors[key] = data[key][0];
          } else if (typeof data[key] === 'string') {
            validationErrors[key] = data[key];
          }
        });
        if (Object.keys(validationErrors).length > 0) {
          message = 'Please fix the validation errors';
        }
      }
      break;
    
    case 401:
      message = data.message || 'Authentication required';
      break;
    
    case 403:
      message = data.message || 'You do not have permission to perform this action';
      break;
    
    case 404:
      message = data.message || 'Resource not found';
      break;
    
    case 409:
      message = data.message || 'Conflict occurred';
      break;
    
    case 422:
      message = data.message || 'Validation failed';
      if (data.errors) validationErrors = data.errors;
      break;
    
    case 429:
      message = data.message || 'Too many requests. Please try again later.';
      break;
    
    case 500:
      message = data.message || 'Server error. Please try again later.';
      break;
    
    default:
      message = data.message || data.detail || defaultMessage;
  }

  return {
    success: false,
    error: {
      message,
      details,
      validationErrors,
      status,
      code: data?.code || `HTTP_${status}`
    }
  };
}

// Enhanced API call function
export const makeAPICall = async (url, options = {}) => {
  const requestId = generateRequestId();
  
  try {
    console.log(`API Call [${requestId}]:`, { url, method: options.method || 'GET' });

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();
    
    console.log(`API Response [${requestId}]:`, { 
      status: response.status, 
      ok: response.ok,
      data 
    });

    if (!response.ok) {
      throw {
        response: {
          status: response.status,
          data: data
        }
      };
    }

    return { 
      success: true, 
      data,
      requestId 
    };
  } catch (error) {
    console.error(`API Error [${requestId}]:`, error);
    return handleError(error, 'Request failed');
  }
};

// Helper function to get user-friendly error messages
export function getAuthErrorMessage(error) {
  const result = handleError(error);
  return result.error.message;
}

// Clear authentication data
export function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_data');
  localStorage.removeItem('user');
  sessionStorage.removeItem('auth_token');
}

// Get current user from localStorage
export function getCurrentUser() {
  const userStr = localStorage.getItem('user_data') || localStorage.getItem('user');
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
}

// Check if user is authenticated
export function isAuthenticated() {
  const token = localStorage.getItem('access_token');
  if (!token) return false;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

// Check if token is expiring soon
export function isTokenExpiring() {
  const token = localStorage.getItem('access_token');
  if (!token) return true;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiresIn = payload.exp * 1000 - Date.now();
    return expiresIn < 5 * 60 * 1000; // 5 minutes
  } catch {
    return true;
  }
}

// Get user role
export function getUserRole() {
  const user = getCurrentUser();
  return user?.role || null;
}

// Check if user has specific role
export function hasRole(role) {
  const userRole = getUserRole();
  return userRole === role;
}

// Check if user has any of the specified roles
export function hasAnyRole(roles) {
  const userRole = getUserRole();
  return roles.includes(userRole);
}

// Get appropriate dashboard URL based on user role
export function getDashboardUrl() {
  const user = getCurrentUser();
  if (!user) return '/login';
  
  const role = user.role;
  const dashboardMap = {
    'student': '/student/dashboard',
    'teacher': '/teacher/dashboard',
    'parent': '/parent/dashboard',
    'admin': '/admin/dashboard',
    'staff': '/staff/dashboard',
    'accountant': '/finance/dashboard'
  };
  
  return dashboardMap[role] || '/dashboard';
}

// Store authentication data
export function storeAuthData(tokens, user) {
  if (tokens.access) {
    localStorage.setItem('access_token', tokens.access);
  }
  if (tokens.refresh) {
    localStorage.setItem('refresh_token', tokens.refresh);
  }
  if (user) {
    localStorage.setItem('user_data', JSON.stringify(user));
  }
}

// Initialize authentication state
export async function initializeAuth() {
  const token = localStorage.getItem('access_token');
  if (!token) return null;

  try {
    const userStr = localStorage.getItem('user_data');
    if (userStr) {
      return JSON.parse(userStr);
    }
  } catch (error) {
    clearAuth();
  }
  
  return null;
}

// Export all utilities as a single object for backward compatibility
export const apiUtils = {
  handleError,
  getAuthErrorMessage,
  clearAuth,
  getCurrentUser,
  isAuthenticated,
  getUserRole,
  hasRole,
  hasAnyRole,
  isTokenExpiring,
  getDashboardUrl,
  storeAuthData,
  initializeAuth,
  generateRequestId,
  makeAPICall
};

export default apiUtils;