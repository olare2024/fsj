/**
 * Utility functions for the application
 */

// Format currency
export const formatCurrency = (amount, currency = 'KES', locale = 'en-KE') => {
  if (typeof amount !== 'number' || isNaN(amount)) {
    return 'KES 0.00';
  }
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

// Format date
export const formatDate = (date, format = 'short') => {
  if (!date) return 'N/A';
  
  const d = new Date(date);
  
  if (isNaN(d.getTime())) {
    return 'Invalid Date';
  }
  
  if (format === 'short') {
    return d.toLocaleDateString('en-KE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } else if (format === 'long') {
    return d.toLocaleDateString('en-KE', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } else if (format === 'iso') {
    return d.toISOString().split('T')[0];
  } else if (format === 'time') {
    return d.toLocaleTimeString('en-KE', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  return d.toLocaleDateString();
};

// Format date and time
export const formatDateTime = (date) => {
  if (!date) return 'N/A';
  
  const d = new Date(date);
  
  if (isNaN(d.getTime())) {
    return 'Invalid Date';
  }
  
  return d.toLocaleString('en-KE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Format number
export const formatNumber = (num, decimals = 2) => {
  if (typeof num !== 'number' || isNaN(num)) {
    return '0';
  }
  
  return num.toLocaleString('en-KE', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

// Generate unique ID
export const generateId = (length = 8) => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// Debounce function
export const debounce = (func, wait, immediate = false) => {
  let timeout;
  return function executedFunction(...args) {
    const context = this;
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

// Throttle function
export const throttle = (func, limit) => {
  let inThrottle;
  return function(...args) {
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Deep clone object
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  
  const clonedObj = {};
  for (let key in obj) {
    if (obj.hasOwnProperty(key)) {
      clonedObj[key] = deepClone(obj[key]);
    }
  }
  return clonedObj;
};

// Safe JSON parse
export const safeJsonParse = (str, defaultValue = null) => {
  try {
    return JSON.parse(str);
  } catch (e) {
    return defaultValue;
  }
};

// Get query parameters
export const getQueryParams = () => {
  if (typeof window === 'undefined') return {};
  
  const params = new URLSearchParams(window.location.search);
  const result = {};
  
  for (const [key, value] of params) {
    result[key] = value;
  }
  
  return result;
};

// Set query parameters
export const setQueryParams = (params) => {
  if (typeof window === 'undefined') return;
  
  const url = new URL(window.location);
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined) {
      url.searchParams.delete(key);
    } else {
      url.searchParams.set(key, String(value));
    }
  });
  
  window.history.pushState({}, '', url.toString());
};

// Remove null/undefined values from object
export const cleanObject = (obj) => {
  const cleaned = { ...obj };
  Object.keys(cleaned).forEach(key => {
    if (cleaned[key] === null || cleaned[key] === undefined) {
      delete cleaned[key];
    }
  });
  return cleaned;
};

// Delay/pause function
export const sleep = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Download file
export const downloadFile = (content, fileName, contentType = 'text/plain') => {
  const blob = new Blob([content], { type: contentType });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

// Copy to clipboard
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Clipboard error:', err);
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return true;
  }
};

// Validate email
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validate Kenyan phone number
export const isValidKenyanPhone = (phone) => {
  const phoneRegex = /^(?:\+?254|0)?[17]\d{8}$/;
  return phoneRegex.test(phone.replace(/\s+/g, ''));
};

// Generate random number in range
export const randomInRange = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

// Truncate string
export const truncateString = (str, maxLength = 50, suffix = '...') => {
  if (!str || str.length <= maxLength) return str;
  return str.substring(0, maxLength - suffix.length) + suffix;
};

// Capitalize first letter of each word
export const capitalizeWords = (str) => {
  if (!str) return '';
  return str.split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

// Format file size
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Calculate percentage
export const calculatePercentage = (part, total) => {
  if (total === 0) return 0;
  return Math.round((part / total) * 100);
};

// Get initials from name
export const getInitials = (name) => {
  if (!name) return '';
  return name.split(' ')
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2);
};

// Check if value is empty
export const isEmpty = (value) => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

// Sort array by property
export const sortByProperty = (array, property, direction = 'asc') => {
  const sortedArray = [...array];
  sortedArray.sort((a, b) => {
    let aValue = a[property];
    let bValue = b[property];
    
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }
    
    if (aValue < bValue) return direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return direction === 'asc' ? 1 : -1;
    return 0;
  });
  
  return sortedArray;
};

// Group array by property
export const groupBy = (array, property) => {
  return array.reduce((groups, item) => {
    const key = item[property];
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {});
};

// Filter array by search term
export const filterBySearch = (array, searchTerm, properties = []) => {
  if (!searchTerm) return array;
  
  const term = searchTerm.toLowerCase();
  return array.filter(item => {
    return properties.some(property => {
      const value = item[property];
      if (value && typeof value === 'string') {
        return value.toLowerCase().includes(term);
      }
      return false;
    });
  });
};

// Get current school term based on date
export const getCurrentTerm = () => {
  const now = new Date();
  const month = now.getMonth() + 1; // 1-12
  
  if (month >= 1 && month <= 4) return 'Term 1';
  if (month >= 5 && month <= 8) return 'Term 2';
  return 'Term 3';
};

// Get current academic year
export const getAcademicYear = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  
  if (month >= 9) {
    return `${year}/${year + 1}`;
  } else {
    return `${year - 1}/${year}`;
  }
};

// Parse M-Pesa message for amount and phone
export const parseMpesaMessage = (message) => {
  if (!message) return null;
  
  const amountMatch = message.match(/Ksh(\d+(?:,\d+)*(?:\.\d+)?)/);
  const phoneMatch = message.match(/from (\d+)/);
  
  return {
    amount: amountMatch ? parseFloat(amountMatch[1].replace(/,/g, '')) : null,
    phone: phoneMatch ? phoneMatch[1] : null
  };
};

// Calculate due date
export const calculateDueDate = (startDate, daysToAdd) => {
  const date = new Date(startDate);
  date.setDate(date.getDate() + daysToAdd);
  return date;
};

// Check if date is in the past
export const isPastDue = (date) => {
  const dueDate = new Date(date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return dueDate < today;
};

// Format time ago
export const timeAgo = (date) => {
  const now = new Date();
  const past = new Date(date);
  const diffInSeconds = Math.floor((now - past) / 1000);
  
  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  };
  
  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(diffInSeconds / secondsInUnit);
    if (interval >= 1) {
      return `${interval} ${unit}${interval === 1 ? '' : 's'} ago`;
    }
  }
  
  return 'just now';
};

// Generate receipt number
export const generateReceiptNumber = (prefix = 'REC', sequence = 0) => {
  const now = new Date();
  const year = now.getFullYear().toString().slice(-2);
  const month = (now.getMonth() + 1).toString().padStart(2, '0');
  const seq = sequence.toString().padStart(4, '0');
  return `${prefix}-${year}${month}-${seq}`;
};

// Generate invoice number
export const generateInvoiceNumber = (prefix = 'INV', sequence = 0) => {
  const now = new Date();
  const year = now.getFullYear();
  const seq = sequence.toString().padStart(5, '0');
  return `${prefix}-${year}-${seq}`;
};

// Default export
export default {
  formatCurrency,
  formatDate,
  formatDateTime,
  formatNumber,
  generateId,
  debounce,
  throttle,
  deepClone,
  safeJsonParse,
  getQueryParams,
  setQueryParams,
  cleanObject,
  sleep,
  downloadFile,
  copyToClipboard,
  isValidEmail,
  isValidKenyanPhone,
  randomInRange,
  truncateString,
  capitalizeWords,
  formatFileSize,
  calculatePercentage,
  getInitials,
  isEmpty,
  sortByProperty,
  groupBy,
  filterBySearch,
  getCurrentTerm,
  getAcademicYear,
  parseMpesaMessage,
  calculateDueDate,
  isPastDue,
  timeAgo,
  generateReceiptNumber,
  generateInvoiceNumber
};