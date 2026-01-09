// financeAPI.js - Complete Rewrite
import api from './api';

/**
 * Finance API Client for Delvok Academy
 * Completely rewritten to match Django URL patterns
 */

const API_PREFIX = '/finance';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// ==================== CACHE SYSTEM ====================

const financeCache = {
  set: (key, data, duration = CACHE_DURATION) => {
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
        duration,
        version: '1.0'
      };
      localStorage.setItem(`finance_${key}`, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Cache set failed:', error);
    }
  },

  get: (key) => {
    try {
      const cached = localStorage.getItem(`finance_${key}`);
      if (!cached) return null;

      const { data, timestamp, duration, version } = JSON.parse(cached);
      
      // Check if expired
      if (Date.now() - timestamp > duration) {
        localStorage.removeItem(`finance_${key}`);
        return null;
      }
      
      return data;
    } catch (error) {
      console.warn('Cache get failed:', error);
      return null;
    }
  },

  clear: (pattern = null) => {
    try {
      if (pattern) {
        Object.keys(localStorage).forEach(key => {
          if (key.startsWith(`finance_${pattern}`)) {
            localStorage.removeItem(key);
          }
        });
      } else {
        // Clear all finance cache
        Object.keys(localStorage).forEach(key => {
          if (key.startsWith('finance_')) {
            localStorage.removeItem(key);
          }
        });
      }
    } catch (error) {
      console.warn('Cache clear failed:', error);
    }
  },

  generateKey: (endpoint, params = {}) => {
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${params[key]}`)
      .join('&');
    return `${endpoint}_${sortedParams}`.replace(/[^a-zA-Z0-9]/g, '_');
  }
};

// ==================== RETRY LOGIC ====================

const retryRequest = async (requestFn, retries = MAX_RETRIES) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (i + 1)));
    }
  }
};

// ==================== RESPONSE HANDLER ====================

const handleResponse = (response, cacheKey = null, shouldCache = true) => {
  if (shouldCache && cacheKey) {
    financeCache.set(cacheKey, response.data);
  }
  
  return {
    success: true,
    data: response.data,
    status: response.status,
    headers: response.headers,
    timestamp: Date.now()
  };
};

const handleError = (error, endpoint) => {
  console.error(`Finance API Error [${endpoint}]:`, {
    status: error.response?.status,
    data: error.response?.data,
    message: error.message
  });

  let userMessage = 'An unexpected error occurred';
  let errorType = 'unknown';

  if (!error.response) {
    userMessage = 'Network error. Please check your connection.';
    errorType = 'network';
  } else if (error.response.status === 400) {
    userMessage = 'Invalid request. Please check your data.';
    errorType = 'validation';
  } else if (error.response.status === 401) {
    userMessage = 'Session expired. Please login again.';
    errorType = 'auth';
  } else if (error.response.status === 403) {
    userMessage = 'You do not have permission for this action.';
    errorType = 'permission';
  } else if (error.response.status === 404) {
    userMessage = 'Resource not found.';
    errorType = 'not_found';
  } else if (error.response.status >= 500) {
    userMessage = 'Server error. Please try again later.';
    errorType = 'server';
  }

  return {
    success: false,
    error: {
      message: userMessage,
      details: error.response?.data || error.message,
      status: error.response?.status,
      type: errorType,
      endpoint
    }
  };
};

// ==================== API ENDPOINTS ====================

export const financeAPI = {
  // ==================== DASHBOARD & OVERVIEW ====================
  getDashboard: async (useCache = true) => {
    const endpoint = 'dashboard';
    const cacheKey = financeCache.generateKey(endpoint);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getFinancialSummary: async (period = 'month', useCache = true) => {
    const endpoint = 'summary';
    const params = { period };
    const cacheKey = financeCache.generateKey(endpoint, params);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getDebtSummary: async (useCache = true) => {
    const endpoint = 'debt-summary';
    const cacheKey = financeCache.generateKey(endpoint);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== RECEIPTS MANAGEMENT ====================
  getReceipts: async (params = {}, useCache = false) => {
    const endpoint = 'receipts';
    
    // Don't cache paginated results
    const shouldCache = !params.page && !params.offset && useCache;
    const cacheKey = shouldCache ? financeCache.generateKey(endpoint, params) : null;
    
    if (shouldCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response, cacheKey, shouldCache);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getReceiptById: async (id, useCache = true) => {
    const endpoint = `receipts/${id}`;
    const cacheKey = financeCache.generateKey(endpoint);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  createReceipt: async (receiptData) => {
    const endpoint = 'receipts';
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, receiptData)
      );
      financeCache.clear('receipts'); // Clear receipts cache
      financeCache.clear('dashboard'); // Clear dashboard cache
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  updateReceipt: async (id, receiptData) => {
    const endpoint = `receipts/${id}`;
    try {
      const response = await retryRequest(() => 
        api.patch(`${API_PREFIX}/${endpoint}/`, receiptData)
      );
      financeCache.clear(`receipts_${id}`);
      financeCache.clear('receipts');
      financeCache.clear('dashboard');
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  verifyReceipt: async (id) => {
    const endpoint = `receipts/${id}/verify`;
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`)
      );
      financeCache.clear(`receipts_${id}`);
      financeCache.clear('receipts');
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  markReceiptPrinted: async (id) => {
    const endpoint = `receipts/${id}/mark-printed`;
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`)
      );
      financeCache.clear(`receipts_${id}`);
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getDailyReceiptSummary: async (date = null) => {
    const endpoint = 'receipts/daily-summary';
    const params = date ? { date } : {};
    const cacheKey = financeCache.generateKey(endpoint, params);
    
    const cached = financeCache.get(cacheKey);
    if (cached) {
      return {
        success: true,
        data: cached,
        cached: true,
        timestamp: Date.now()
      };
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== PAYMENTS MANAGEMENT ====================
  getPayments: async (params = {}, useCache = false) => {
    const endpoint = 'payments';
    
    const shouldCache = !params.page && !params.offset && useCache;
    const cacheKey = shouldCache ? financeCache.generateKey(endpoint, params) : null;
    
    if (shouldCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response, cacheKey, shouldCache);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  createPayment: async (paymentData) => {
    const endpoint = 'payments';
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, paymentData)
      );
      financeCache.clear('payments');
      financeCache.clear('dashboard');
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  approvePayment: async (id, approvalData = {}) => {
    const endpoint = `payments/${id}/approve`;
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, approvalData)
      );
      financeCache.clear(`payments_${id}`);
      financeCache.clear('payments');
      financeCache.clear('dashboard');
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // Add to your financeAPI object:

// For reconciliation
getReceiptAllocations: async (params = {}) => {
  try {
    const response = await api.get(`${API_PREFIX}/receipt-allocations/`, { params });
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'receipt-allocations');
  }
},

// Get debts by status
getDebts: async (params = {}) => {
  try {
    // This should call /finance/debt-records/ with params
    const response = await api.get(`${API_PREFIX}/debt-records/`, { params });
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'debt-records');
  }
},

// Daily summary
getDailySummary: async (date = null) => {
  try {
    const params = date ? { date } : {};
    const response = await api.get(`${API_PREFIX}/daily-summary/`, { params });
    return handleResponse(response);
  } catch (error) {
    return handleError(error, 'daily-summary');
  }
},

// Verification methods
verifyReceipt: async (id) => {
  try {
    const response = await api.post(`${API_PREFIX}/receipts/${id}/verify/`);
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `receipts/${id}/verify`);
  }
},

reconcileReceipt: async (id) => {
  try {
    const response = await api.post(`${API_PREFIX}/receipts/${id}/reconcile/`);
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `receipts/${id}/reconcile`);
  }
},

approvePayment: async (id, approvalData = {}) => {
  try {
    const response = await api.post(`${API_PREFIX}/payments/${id}/approve/`, approvalData);
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `payments/${id}/approve`);
  }
},

markPaymentAsPaid: async (id) => {
  try {
    const response = await api.post(`${API_PREFIX}/payments/${id}/mark-as-paid/`);
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `payments/${id}/mark-as-paid`);
  }
},

applyPaymentToDebt: async (id, paymentData) => {
  try {
    const response = await api.post(`${API_PREFIX}/debt-records/${id}/apply-payment/`, paymentData);
    return handleResponse(response);
  } catch (error) {
    return handleError(error, `debt-records/${id}/apply-payment`);
  }
},

  getExpenditureSummary: async (params = {}) => {
    const endpoint = 'payments/expenditure-summary';
    const cacheKey = financeCache.generateKey(endpoint, params);
    
    const cached = financeCache.get(cacheKey);
    if (cached) {
      return {
        success: true,
        data: cached,
        cached: true,
        timestamp: Date.now()
      };
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== DEBT MANAGEMENT ====================
  getDebtRecords: async (params = {}) => {
    const endpoint = 'debt-records';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  applyPaymentToDebt: async (id, paymentData) => {
    const endpoint = `debt-records/${id}/apply-payment`;
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, paymentData)
      );
      financeCache.clear('debt');
      financeCache.clear('dashboard');
      financeCache.clear('debt-summary');
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getDebtsByClass: async (params = {}) => {
    const endpoint = 'debt-records/by-class';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== FEE STRUCTURES ====================
  getFeeStructures: async (params = {}, useCache = true) => {
    const endpoint = 'fee-structures';
    const cacheKey = financeCache.generateKey(endpoint, params);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getCurrentFeeStructures: async (useCache = true) => {
    const endpoint = 'fee-structures/current';
    const cacheKey = financeCache.generateKey(endpoint);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  createFeeStructure: async (feeData) => {
    const endpoint = 'fee-structures';
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, feeData)
      );
      financeCache.clear('fee-structures');
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== REPORTS ====================
  getFeeCollectionReport: async (params = {}) => {
    const endpoint = 'reports/fee-collection';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getExpenditureReport: async (params = {}) => {
    const endpoint = 'reports/expenditure';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getFinancialReports: async (params = {}) => {
    const endpoint = 'financial-reports';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== UTILITIES ====================
  getPaymentMethods: async (useCache = true) => {
    const endpoint = 'payment-methods';
    const cacheKey = financeCache.generateKey(endpoint);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getFeeCategories: async (useCache = true) => {
    const endpoint = 'fee-categories';
    const cacheKey = financeCache.generateKey(endpoint);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getFinancialYear: async (useCache = true) => {
    const endpoint = 'financial-year';
    const cacheKey = financeCache.generateKey(endpoint);
    
    if (useCache) {
      const cached = financeCache.get(cacheKey);
      if (cached) {
        return {
          success: true,
          data: cached,
          cached: true,
          timestamp: Date.now()
        };
      }
    }

    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response, cacheKey);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== BULK OPERATIONS ====================
  bulkApplyPayments: async (bulkData) => {
    const endpoint = 'bulk-apply-payments';
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, bulkData)
      );
      financeCache.clear('dashboard');
      financeCache.clear('debt');
      financeCache.clear('receipts');
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  exportFinancialData: async (exportType = 'receipts', format = 'json', params = {}) => {
    const endpoint = 'export-data';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, {
          params: { type: exportType, format, ...params },
          responseType: 'blob'
        })
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `finance_${exportType}_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return {
        success: true,
        message: 'Export downloaded successfully'
      };
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== STUDENT PORTAL ====================
  getStudentFinancialPortal: async () => {
    const endpoint = 'student-portal';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== ANALYTICS ====================
  getRevenueTrends: async (params = {}) => {
    const endpoint = 'analytics/revenue-trends';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getCollectionEfficiency: async (params = {}) => {
    const endpoint = 'analytics/collection-efficiency';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  getTopDebtors: async (params = {}) => {
    const endpoint = 'analytics/top-debtors';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== RECONCILIATION ====================
  bankReconciliation: async (params = {}) => {
    const endpoint = 'reconciliation/bank';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  mpesaReconciliation: async (params = {}) => {
    const endpoint = 'reconciliation/mpesa';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`, { params })
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== CACHE MANAGEMENT ====================
  clearCache: (pattern = null) => financeCache.clear(pattern),
  
  // ==================== HEALTH CHECK ====================
  checkAPIHealth: async () => {
    try {
      const endpoints = ['dashboard', 'summary', 'receipts'];
      const results = [];
      
      for (const endpoint of endpoints) {
        try {
          await api.head(`${API_PREFIX}/${endpoint}/`);
          results.push({ endpoint, status: 'healthy' });
        } catch (error) {
          results.push({ 
            endpoint, 
            status: 'unhealthy',
            error: error.message 
          });
        }
      }
      
      return {
        success: true,
        data: results,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: 'API health check failed',
          details: error.message
        }
      };
    }
  },

  // ==================== MOCK DATA FOR DEVELOPMENT ====================
  getMockDashboardData: () => {
    const today = new Date().toISOString().split('T')[0];
    return {
      id: `mock_${Date.now()}`,
      dashboard_date: today,
      total_receipts_today: '0.00',
      total_receipts_today_formatted: 'KSh 0.00',
      total_payments_today: '0.00',
      total_payments_today_formatted: 'KSh 0.00',
      total_debt: '0.00',
      total_debt_formatted: 'KSh 0.00',
      pending_payments: '0',
      pending_approvals: '0',
      overdue_debts: '0',
      daily_target: '0.00',
      target_achievement: '0.00',
      daily_transactions: 0,
      cash_balance: '0.00',
      bank_balance: '0.00',
      mpesa_balance: '0.00',
      greeting: 'Good day, Accountant',
      todays_date: today,
      user_role: 'accountant',
      quick_actions: [
        { id: 1, title: 'Record Payment', icon: '💳', path: '/finance/receipts/create' },
        { id: 2, title: 'View Reports', icon: '📊', path: '/finance/reports' },
        { id: 3, title: 'Reconcile', icon: '⚖️', path: '/finance/reconciliation' },
        { id: 4, title: 'Check Debt', icon: '💰', path: '/finance/debts' }
      ]
    };
  },

  // ==================== BATCH OPERATIONS ====================
  batchGenerateStatements: async (params = {}) => {
    const endpoint = 'batch/generate-statements';
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, params)
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== UTILITY FUNCTIONS ====================
  generateReceiptNumber: async () => {
    const endpoint = 'utils/generate-receipt-number';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  generatePaymentNumber: async () => {
    const endpoint = 'utils/generate-payment-number';
    try {
      const response = await retryRequest(() => 
        api.get(`${API_PREFIX}/${endpoint}/`)
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  },

  // ==================== NOTIFICATIONS ====================
  sendFeeReminders: async (reminderData) => {
    const endpoint = 'notifications/fee-reminders';
    try {
      const response = await retryRequest(() => 
        api.post(`${API_PREFIX}/${endpoint}/`, reminderData)
      );
      return handleResponse(response);
    } catch (error) {
      return handleError(error, endpoint);
    }
  }
};

// ==================== HELPER FUNCTIONS ====================

export const financeHelpers = {
  formatCurrency: (amount, currency = 'KES') => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  },

  formatDate: (dateString, format = 'full') => {
    const date = new Date(dateString);
    const options = {
      full: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      },
      date: {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      },
      short: {
        month: 'short',
        day: 'numeric'
      }
    };
    
    return date.toLocaleDateString('en-KE', options[format] || options.date);
  },

  calculatePercentage: (value, total) => {
    if (!total) return 0;
    return Math.round((value / total) * 100);
  },

  getStatusColor: (status) => {
    const colors = {
      paid: 'green',
      pending: 'yellow',
      overdue: 'red',
      approved: 'blue',
      rejected: 'gray',
      partial: 'orange'
    };
    return colors[status] || 'gray';
  },

  validateReceiptData: (data) => {
    const errors = [];
    
    if (!data.student_id) errors.push('Student is required');
    if (!data.amount || data.amount <= 0) errors.push('Valid amount is required');
    if (!data.payment_method) errors.push('Payment method is required');
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
};

// ==================== DASHBOARD DATA FETCHER ====================

export const fetchDashboardData = async (options = {}) => {
  const {
    useCache = true,
    useMock = false,
    includeDetails = true
  } = options;

  if (useMock) {
    return {
      success: true,
      data: financeAPI.getMockDashboardData(),
      cached: false,
      timestamp: Date.now()
    };
  }

  try {
    // Fetch dashboard data
    const dashboard = await financeAPI.getDashboard(useCache);
    
    if (!dashboard.success) {
      throw new Error('Failed to fetch dashboard');
    }

    const promises = [];
    
    if (includeDetails) {
      promises.push(
        financeAPI.getFinancialSummary('today', useCache),
        financeAPI.getDebtSummary(useCache),
        financeAPI.getReceipts({ limit: 5, ordering: '-date' }, false)
      );
    }

    const [summary, debts, receipts] = await Promise.allSettled(promises);

    return {
      ...dashboard,
      details: {
        summary: summary.status === 'fulfilled' ? summary.value : null,
        debts: debts.status === 'fulfilled' ? debts.value : null,
        recentReceipts: receipts.status === 'fulfilled' ? receipts.value : null
      }
    };
  } catch (error) {
    console.error('Dashboard fetch error:', error);
    return {
      success: false,
      error: {
        message: 'Failed to load dashboard data',
        details: error.message
      },
      data: financeAPI.getMockDashboardData(), // Fallback to mock data
      cached: false
    };
  }
};

// ==================== API MONITORING ====================

let requestCount = 0;
let errorCount = 0;

const apiMonitor = {
  trackRequest: () => requestCount++,
  trackError: () => errorCount++,
  getStats: () => ({
    requestCount,
    errorCount,
    errorRate: requestCount > 0 ? (errorCount / requestCount) * 100 : 0
  }),
  reset: () => {
    requestCount = 0;
    errorCount = 0;
  }
};

// ==================== EXPORT DEFAULT ====================

export default financeAPI;