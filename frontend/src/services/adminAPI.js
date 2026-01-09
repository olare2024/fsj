// src/services/adminAPI.js - UPDATED & COMPLETE VERSION
import api from './api';

export const adminAPI = {
  // ==================== DASHBOARD FUNCTIONS ====================
  /**
   * Get Admin Dashboard Data
   * GET /admin/dashboard/
   */
  getDashboardData: async (params = {}) => {
    try {
      const response = await api.get('/admin/dashboard/', { params });
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
   * Get Dashboard Summary (alias for backward compatibility)
   * GET /admin/dashboard/summary/
   */
  getDashboardSummary: async (params = {}) => {
    try {
      const response = await api.get('/admin/dashboard/summary/', { params });
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
   * Get System Analytics
   * GET /admin/analytics/
   */
  getAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/admin/analytics/', { params });
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
   * Get System Health Status
   * GET /admin/system-health/
   */
  getSystemHealth: async () => {
    try {
      const response = await api.get('/admin/system-health/');
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
   * GET /admin/recent-activities/
   */
  getRecentActivities: async (params = {}) => {
    try {
      const response = await api.get('/admin/recent-activities/', { params });
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
   * Get Pending Tasks
   * GET /admin/pending-tasks/
   */
  getPendingTasks: async () => {
    try {
      const response = await api.get('/admin/pending-tasks/');
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
   * Create Announcement
   * POST /admin/announcements/
   */
  createAnnouncement: async (announcementData) => {
    try {
      const response = await api.post('/admin/announcements/', announcementData);
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

  /**
   * Restart System Component
   * POST /admin/system/restart/
   */
  restartSystem: async (component) => {
    try {
      const response = await api.post('/admin/system/restart/', { component });
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
   * Initiate System Backup
   * POST /admin/backup/initiate/
   */
  initiateBackup: async () => {
    try {
      const response = await api.post('/admin/backup/initiate/');
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
   * Toggle Maintenance Mode
   * POST /admin/maintenance/toggle/
   */
  toggleMaintenanceMode: async () => {
    try {
      const response = await api.post('/admin/maintenance/toggle/');
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
   * Run System Diagnostics
   * POST /admin/diagnostics/run/
   */
  runDiagnostics: async () => {
    try {
      const response = await api.post('/admin/diagnostics/run/');
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
   * Get System Logs
   * GET /admin/logs/
   */
  getSystemLogs: async (params = {}) => {
    try {
      const response = await api.get('/admin/logs/', { params });
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
   * Export Reports
   * POST /admin/export-reports/
   */
  exportReport: async (reportType, timeRange) => {
    try {
      const response = await api.post('/admin/export-reports/', {
        report_type: reportType,
        time_range: timeRange
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

  // ==================== USER MANAGEMENT ====================
  /**
   * User Management - Get All Users
   * GET /admin/users/
   */
  getUsers: async (params = {}) => {
    try {
      const response = await api.get('/admin/users/', { params });
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
   * User Management - Get User Details
   * GET /admin/users/{id}/
   */
  getUser: async (userId) => {
    try {
      const response = await api.get(`/admin/users/${userId}/`);
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
   * User Management - Create User
   * POST /admin/users/
   */
  createUser: async (userData) => {
    try {
      const response = await api.post('/admin/users/', userData);
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

  /**
   * User Management - Update User
   * PATCH /admin/users/{id}/
   */
  updateUser: async (userId, userData) => {
    try {
      const response = await api.patch(`/admin/users/${userId}/`, userData);
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

  /**
   * User Management - Delete User
   * DELETE /admin/users/{id}/
   */
  deleteUser: async (userId) => {
    try {
      const response = await api.delete(`/admin/users/${userId}/`);
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
   * User Management - Bulk Actions
   * POST /admin/users/bulk-actions/
   */
  bulkUserActions: async (action, userIds) => {
    try {
      const response = await api.post('/admin/users/bulk-actions/', {
        action: action,
        user_ids: userIds
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

  // ==================== SYSTEM FUNCTIONS ====================
  /**
   * System Settings - Get Settings
   * GET /admin/settings/
   */
  getSystemSettings: async () => {
    try {
      const response = await api.get('/admin/settings/');
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
   * System Settings - Update Settings
   * PATCH /admin/settings/
   */
  updateSystemSettings: async (settingsData) => {
    try {
      const response = await api.patch('/admin/settings/', settingsData);
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

  /**
   * System Maintenance
   * POST /admin/maintenance/
   */
  performMaintenance: async (action) => {
    try {
      const response = await api.post('/admin/maintenance/', { action });
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
   * Backup Management
   * GET /admin/backups/
   */
  getBackups: async () => {
    try {
      const response = await api.get('/admin/backups/');
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
   * Create Backup
   * POST /admin/backups/create/
   */
  createBackup: async () => {
    try {
      const response = await api.post('/admin/backups/create/');
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
   * System Health Check
   * GET /admin/health-check/
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/admin/health-check/');
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
   * Get System Statistics
   * GET /admin/statistics/
   */
  getStatistics: async (params = {}) => {
    try {
      const response = await api.get('/admin/statistics/', { params });
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
   * Get Activity Logs
   * GET /admin/activity-logs/
   */
  getActivityLogs: async (params = {}) => {
    try {
      const response = await api.get('/admin/activity-logs/', { params });
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
   * Clear Cache
   * POST /admin/clear-cache/
   */
  clearCache: async () => {
    try {
      const response = await api.post('/admin/clear-cache/');
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
   * Database Optimization
   * POST /admin/optimize-database/
   */
  optimizeDatabase: async () => {
    try {
      const response = await api.post('/admin/optimize-database/');
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
   * Send System Notification
   * POST /admin/send-notification/
   */
  sendSystemNotification: async (notificationData) => {
    try {
      const response = await api.post('/admin/send-notification/', notificationData);
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

  /**
   * Get User Roles and Permissions
   * GET /admin/roles-permissions/
   */
  getRolesAndPermissions: async () => {
    try {
      const response = await api.get('/admin/roles-permissions/');
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
   * Update User Role
   * PATCH /admin/users/{id}/role/
   */
  updateUserRole: async (userId, roleData) => {
    try {
      const response = await api.patch(`/admin/users/${userId}/role/`, roleData);
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

  /**
   * Get System Alerts
   * GET /admin/alerts/
   */
  getSystemAlerts: async () => {
    try {
      const response = await api.get('/admin/alerts/');
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
   * Dismiss Alert
   * POST /admin/alerts/{id}/dismiss/
   */
  dismissAlert: async (alertId) => {
    try {
      const response = await api.post(`/admin/alerts/${alertId}/dismiss/`);
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
   * Get Audit Trail
   * GET /admin/audit-trail/
   */
  getAuditTrail: async (params = {}) => {
    try {
      const response = await api.get('/admin/audit-trail/', { params });
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
   * Search Users
   * GET /admin/search/users/
   */
  searchUsers: async (query, params = {}) => {
    try {
      const response = await api.get('/admin/search/users/', {
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
  },

  /**
   * Get Dashboard Widgets
   * GET /admin/dashboard-widgets/
   */
  getDashboardWidgets: async () => {
    try {
      const response = await api.get('/admin/dashboard-widgets/');
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
   * Update Dashboard Widgets
   * PATCH /admin/dashboard-widgets/
   */
  updateDashboardWidgets: async (widgetsData) => {
    try {
      const response = await api.patch('/admin/dashboard-widgets/', widgetsData);
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

  /**
   * Get API Usage Statistics
   * GET /admin/api-usage/
   */
  getApiUsage: async (params = {}) => {
    try {
      const response = await api.get('/admin/api-usage/', { params });
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
   * Get Performance Metrics
   * GET /admin/performance-metrics/
   */
  getPerformanceMetrics: async (params = {}) => {
    try {
      const response = await api.get('/admin/performance-metrics/', { params });
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
   * Get Security Logs
   * GET /admin/security-logs/
   */
  getSecurityLogs: async (params = {}) => {
    try {
      const response = await api.get('/admin/security-logs/', { params });
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
   * Get Storage Information
   * GET /admin/storage-info/
   */
  getStorageInfo: async () => {
    try {
      const response = await api.get('/admin/storage-info/');
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
   * Cleanup Temporary Files
   * POST /admin/cleanup-temp/
   */
  cleanupTempFiles: async () => {
    try {
      const response = await api.post('/admin/cleanup-temp/');
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

export default adminAPI;