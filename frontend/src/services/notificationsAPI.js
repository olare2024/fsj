import api from './api.js';
import authAPI from './authAPI.js';

// ==================== NOTIFICATION CONSTANTS ====================

export const NOTIFICATION_CONSTANTS = {
  // Notification types
  TYPE: {
    SYSTEM: 'system',
    ACADEMIC: 'academic',
    FINANCIAL: 'financial',
    SECURITY: 'security',
    EVENT: 'event',
    ANNOUNCEMENT: 'announcement',
    MESSAGE: 'message',
    ASSIGNMENT: 'assignment',
    GRADE: 'grade',
    ATTENDANCE: 'attendance',
    REMINDER: 'reminder',
    APPROVAL: 'approval',
    ALERT: 'alert',
    WELCOME: 'welcome'
  },
  
  // Priority levels
  PRIORITY: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    URGENT: 'urgent'
  },
  
  // Delivery methods
  DELIVERY: {
    IN_APP: 'in_app',
    EMAIL: 'email',
    SMS: 'sms',
    PUSH: 'push',
    ALL: 'all'
  },
  
  // Status
  STATUS: {
    UNREAD: 'unread',
    READ: 'read',
    ARCHIVED: 'archived',
    DELETED: 'deleted'
  },
  
  // Channels
  CHANNEL: {
    ALL: 'all',
    ADMIN: 'admin',
    TEACHER: 'teacher',
    STUDENT: 'student',
    PARENT: 'parent',
    STAFF: 'staff',
    ACCOUNTANT: 'accountant',
    IT: 'it',
    CUSTOM: 'custom'
  },
  
  // Action types
  ACTION_TYPE: {
    LINK: 'link',
    BUTTON: 'button',
    FORM: 'form',
    CONFIRM: 'confirm',
    DISMISS: 'dismiss'
  },
  
  // Default settings
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
  POLL_INTERVAL: 30000, // 30 seconds
  RETENTION_DAYS: 90,
  
  // Cache settings
  CACHE_TTL: {
    NOTIFICATIONS: 30 * 1000, // 30 seconds
    SETTINGS: 5 * 60 * 1000, // 5 minutes
    STATS: 60 * 1000 // 1 minute
  }
};

// ==================== WEB SOCKET MANAGEMENT ====================

class NotificationWebSocket {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
    this.isConnected = false;
  }

  connect() {
    if (this.socket) return;
    
    const token = authAPI.getToken();
    if (!token) {
      console.log('🔐 No token available for WebSocket connection');
      return;
    }

    // For local development, use ws:// instead of wss://
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/notifications/?token=${token}`;
    
    try {
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = () => {
        console.log('🔌 WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connected', { connected: true });
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('message', data);
          
          // Handle specific message types
          if (data.type === 'notification') {
            this.emit('new_notification', data.notification);
          } else if (data.type === 'notification_count') {
            this.emit('count_update', data.count);
          }
        } catch (error) {
          console.error('❌ WebSocket message parsing error:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.socket = null;
        this.emit('disconnected', { code: event.code, reason: event.reason });
        
        // Attempt reconnection
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++;
            this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000);
            console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            this.connect();
          }, this.reconnectDelay);
        }
      };

      this.socket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
      return true;
    }
    return false;
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }

  getConnectionStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      readyState: this.socket ? this.socket.readyState : WebSocket.CLOSED
    };
  }
}

// Create singleton instance
const notificationWebSocket = new NotificationWebSocket();

// ==================== CACHE MANAGEMENT ====================

const notificationsCache = new Map();
const cacheTimeouts = new Map();

const getCacheKey = (endpoint, params = {}) => {
  const paramString = JSON.stringify(params);
  return `${endpoint}_${paramString}`;
};

const setCache = (key, data, ttl = NOTIFICATION_CONSTANTS.CACHE_TTL.NOTIFICATIONS) => {
  notificationsCache.set(key, {
    data,
    timestamp: Date.now(),
    ttl
  });
  
  // Clear existing timeout if any
  if (cacheTimeouts.has(key)) {
    clearTimeout(cacheTimeouts.get(key));
  }
  
  // Set new timeout for auto-cleanup
  const timeout = setTimeout(() => {
    notificationsCache.delete(key);
    cacheTimeouts.delete(key);
  }, ttl);
  
  cacheTimeouts.set(key, timeout);
};

const getCache = (key) => {
  const cached = notificationsCache.get(key);
  if (!cached) return null;
  
  const isExpired = Date.now() - cached.timestamp > cached.ttl;
  if (isExpired) {
    notificationsCache.delete(key);
    if (cacheTimeouts.has(key)) {
      clearTimeout(cacheTimeouts.get(key));
      cacheTimeouts.delete(key);
    }
    return null;
  }
  
  return cached.data;
};

const clearCache = (pattern = null) => {
  if (!pattern) {
    notificationsCache.clear();
    cacheTimeouts.forEach(timeout => clearTimeout(timeout));
    cacheTimeouts.clear();
  } else {
    for (const [key] of notificationsCache) {
      if (key.includes(pattern)) {
        notificationsCache.delete(key);
        if (cacheTimeouts.has(key)) {
          clearTimeout(cacheTimeouts.get(key));
          cacheTimeouts.delete(key);
        }
      }
    }
  }
};

// ==================== ERROR HANDLER ====================

const handleNotificationError = (error, defaultMessage = 'Notification error occurred') => {
  console.error('🔔 Notification API Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
    // Handle specific status codes
    switch (status) {
      case 400:
        return {
          success: false,
          message: serverError.detail || serverError.message || 'Invalid notification request',
          errors: serverError.errors || serverError.details,
          status: 400,
          data: serverError
        };
      
      case 401:
        return {
          success: false,
          message: 'Authentication required for notifications',
          status: 401,
          requiresAuth: true
        };
      
      case 403:
        return {
          success: false,
          message: 'You do not have permission to access notifications',
          status: 403,
          forbidden: true
        };
      
      case 429:
        return {
          success: false,
          message: 'Too many notification requests. Please try again later.',
          status: 429,
          rateLimited: true
        };
      
      default:
        return {
          success: false,
          message: serverError.detail || serverError.message || defaultMessage,
          status: status,
          data: serverError
        };
    }
  } else if (error.request) {
    return {
      success: false,
      message: 'Unable to connect to notification service. Please check your internet connection.',
      status: 0,
      networkError: true
    };
  } else if (error.code === 'ECONNABORTED') {
    return {
      success: false,
      message: 'Notification request timed out. Please try again.',
      status: -1,
      timeout: true
    };
  } else {
    return {
      success: false,
      message: error.message || defaultMessage,
      status: -1
    };
  }
};

// ==================== NOTIFICATION API ====================

export const notificationsAPI = {
  // ==================== WEBSOCKET MANAGEMENT ====================
  
  ws: notificationWebSocket,
  
  connectWebSocket: () => {
    if (authAPI.isAuthenticated()) {
      notificationWebSocket.connect();
    }
  },
  
  disconnectWebSocket: () => {
    notificationWebSocket.disconnect();
  },
  
  getWebSocketStatus: () => {
    return notificationWebSocket.getConnectionStatus();
  },
  
  onWebSocketEvent: (event, callback) => {
    notificationWebSocket.on(event, callback);
  },
  
  offWebSocketEvent: (event, callback) => {
    notificationWebSocket.off(event, callback);
  },
  
  // ==================== CACHE MANAGEMENT ====================
  
  clearCache,
  
  getCacheStats: () => {
    return {
      size: notificationsCache.size,
      timeouts: cacheTimeouts.size,
      keys: Array.from(notificationsCache.keys()),
      entries: Array.from(notificationsCache.entries()).map(([key, value]) => ({
        key,
        timestamp: new Date(value.timestamp).toISOString(),
        age: Date.now() - value.timestamp,
        ttl: value.ttl,
        expiresIn: value.ttl - (Date.now() - value.timestamp)
      }))
    };
  },
  
  // ==================== NOTIFICATION RETRIEVAL ====================
  
  /**
   * Get all notifications with pagination
   */
  getAll: async (params = {}) => {
    const cacheKey = getCacheKey('all_notifications', params);
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      console.log('📦 Serving notifications from cache');
      return cached;
    }
    
    try {
      console.log('🔔 Fetching notifications with params:', params);
      
      // Correct endpoint: /notifications/notifications/ (not /notifications/)
      const response = await api.get('/notifications/notifications/', { params });
      console.log('✅ Notifications fetched:', response.data);
      
      // Handle both list view (with results) and detail view
      const notifications = response.data.results || response.data;
      const count = response.data.count || (Array.isArray(notifications) ? notifications.length : 1);
      
      const result = {
        success: true,
        data: notifications,
        count: count,
        unread_count: response.data.unread_count || 0,
        pagination: {
          page: response.data.page || 1,
          pages: response.data.pages || 1,
          page_size: response.data.page_size || NOTIFICATION_CONSTANTS.DEFAULT_LIMIT,
          has_next: response.data.has_next || false,
          has_previous: response.data.has_previous || false,
          next: response.data.next,
          previous: response.data.previous
        },
        timestamp: Date.now(),
        responseTime: response.config.metadata?.responseTime || null
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching notifications:', error);
      return handleNotificationError(error, 'Failed to fetch notifications');
    }
  },
  
  /**
   * Get unread notifications
   */
  getUnread: async (params = {}) => {
    const unreadParams = {
      status: NOTIFICATION_CONSTANTS.STATUS.UNREAD,
      ordering: '-created_at',
      ...params
    };
    
    return notificationsAPI.getAll(unreadParams);
  },
  
  /**
   * Get recent notifications
   */
  getRecent: async (limit = 10) => {
    const recentParams = {
      limit,
      ordering: '-created_at'
    };
    
    return notificationsAPI.getAll(recentParams);
  },
  
  /**
   * Get notification by ID
   */
  getById: async (notificationId) => {
    const cacheKey = getCacheKey(`notification_${notificationId}`);
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      console.log('🔔 Fetching notification:', notificationId);
      
      // Correct endpoint: /notifications/notifications/{id}/
      const response = await api.get(`/notifications/notifications/${notificationId}/`);
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching notification:', error);
      return handleNotificationError(error, 'Failed to fetch notification');
    }
  },
  
  /**
   * Get notifications by type
   */
  getByType: async (type, params = {}) => {
    const typeParams = {
      type,
      ...params
    };
    
    return notificationsAPI.getAll(typeParams);
  },
  
  /**
   * Get notifications by channel
   */
  getByChannel: async (channel, params = {}) => {
    const channelParams = {
      channel,
      ...params
    };
    
    return notificationsAPI.getAll(channelParams);
  },
  
  // ==================== NOTIFICATION MANAGEMENT ====================
  
  /**
   * Mark notification as read
   */
  markAsRead: async (notificationId) => {
    try {
      console.log('🔔 Marking notification as read:', notificationId);
      
      // Correct endpoint: /notifications/notifications/{id}/mark-read/
      const response = await api.post(`/notifications/notifications/${notificationId}/mark-read/`);
      
      // Clear relevant cache
      clearCache('all_notifications');
      clearCache(`notification_${notificationId}`);
      
      // Emit WebSocket event
      if (notificationWebSocket.isConnected) {
        notificationWebSocket.send({
          type: 'notification_read',
          notification_id: notificationId
        });
      }
      
      return {
        success: true,
        message: response.data.message || 'Notification marked as read',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error marking notification as read:', error);
      return handleNotificationError(error, 'Failed to mark notification as read');
    }
  },
  
  /**
   * Mark all notifications as read
   */
  markAllAsRead: async () => {
    try {
      console.log('🔔 Marking all notifications as read');
      
      // Correct endpoint: /notifications/notifications/mark-all-read/
      const response = await api.post('/notifications/notifications/mark-all-read/');
      
      // Clear cache
      clearCache('all_notifications');
      
      // Emit WebSocket event
      if (notificationWebSocket.isConnected) {
        notificationWebSocket.send({
          type: 'all_notifications_read'
        });
      }
      
      return {
        success: true,
        message: response.data.message || 'All notifications marked as read',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error marking all notifications as read:', error);
      return handleNotificationError(error, 'Failed to mark all notifications as read');
    }
  },
  
  /**
   * Archive notification
   */
  archive: async (notificationId) => {
    try {
      console.log('🔔 Archiving notification:', notificationId);
      
      // Correct endpoint: /notifications/notifications/{id}/archive/
      const response = await api.post(`/notifications/notifications/${notificationId}/archive/`);
      
      // Clear cache
      clearCache('all_notifications');
      clearCache(`notification_${notificationId}`);
      
      return {
        success: true,
        message: response.data.message || 'Notification archived',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error archiving notification:', error);
      return handleNotificationError(error, 'Failed to archive notification');
    }
  },
  
  /**
   * Delete notification
   */
  delete: async (notificationId) => {
    try {
      console.log('🔔 Deleting notification:', notificationId);
      
      // Correct endpoint: /notifications/notifications/{id}/
      const response = await api.delete(`/notifications/notifications/${notificationId}/`);
      
      // Clear cache
      clearCache('all_notifications');
      clearCache(`notification_${notificationId}`);
      
      return {
        success: true,
        message: response.data.message || 'Notification deleted',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error deleting notification:', error);
      return handleNotificationError(error, 'Failed to delete notification');
    }
  },
  
  // ==================== NOTIFICATION CREATION ====================
  
  /**
   * Create notification
   */
  create: async (notificationData) => {
    try {
      console.log('🔔 Creating notification:', notificationData.title);
      
      // Validate required fields
      const requiredFields = ['title', 'message', 'type', 'channel'];
      const missingFields = requiredFields.filter(field => !notificationData[field]);
      
      if (missingFields.length > 0) {
        return {
          success: false,
          message: `Missing required fields: ${missingFields.join(', ')}`,
          missingFields
        };
      }
      
      // Correct endpoint: /notifications/notifications/
      const response = await api.post('/notifications/notifications/', notificationData);
      
      // Clear cache
      clearCache('all_notifications');
      
      // Emit WebSocket event
      if (notificationWebSocket.isConnected) {
        notificationWebSocket.send({
          type: 'new_notification',
          notification: response.data
        });
      }
      
      return {
        success: true,
        message: 'Notification created successfully',
        data: response.data,
        id: response.data.id,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error creating notification:', error);
      return handleNotificationError(error, 'Failed to create notification');
    }
  },
  
  /**
   * Create bulk notifications
   */
  createBulk: async (bulkData) => {
    try {
      console.log('🔔 Creating bulk notifications');
      
      // Correct endpoint: /notifications/notifications/create-bulk/
      const response = await api.post('/notifications/notifications/create-bulk/', bulkData);
      
      // Clear cache
      clearCache('all_notifications');
      
      return {
        success: true,
        message: response.data.message || 'Bulk notifications created',
        data: response.data,
        notifications_created: response.data.notifications_created || 0,
        sent_count: response.data.sent_count || 0,
        failed_count: response.data.failed_count || 0,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error creating bulk notifications:', error);
      return handleNotificationError(error, 'Failed to create bulk notifications');
    }
  },
  
  /**
   * Create notification from template
   */
  createFromTemplate: async (templateName, userId, context = {}) => {
    try {
      console.log('🔔 Creating notification from template:', templateName);
      
      // Correct endpoint: /notifications/notifications/create-from-template/
      const response = await api.post('/notifications/notifications/create-from-template/', {
        template_name: templateName,
        user_id: userId,
        context: context
      });
      
      // Clear cache
      clearCache('all_notifications');
      
      return {
        success: true,
        message: response.data.message || 'Notification created from template',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error creating notification from template:', error);
      return handleNotificationError(error, 'Failed to create notification from template');
    }
  },
  
  /**
   * Create system notification
   */
  createSystemNotification: async (title, message, priority = NOTIFICATION_CONSTANTS.PRIORITY.MEDIUM) => {
    return notificationsAPI.create({
      title,
      message,
      type: NOTIFICATION_CONSTANTS.TYPE.SYSTEM,
      channel: NOTIFICATION_CONSTANTS.CHANNEL.ALL,
      priority,
      delivery_method: NOTIFICATION_CONSTANTS.DELIVERY.IN_APP
    });
  },
  
  // ==================== NOTIFICATION SETTINGS ====================
  
  /**
   * Get user notification settings
   */
  getSettings: async () => {
    const cacheKey = 'notification_settings';
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      console.log('🔔 Getting notification settings');
      
      const response = await api.get('/notifications/settings/');
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, NOTIFICATION_CONSTANTS.CACHE_TTL.SETTINGS);
      return result;
    } catch (error) {
      console.error('❌ Error getting notification settings:', error);
      return handleNotificationError(error, 'Failed to get notification settings');
    }
  },
  
  /**
   * Update notification settings
   */
  updateSettings: async (settingsData) => {
    try {
      console.log('🔔 Updating notification settings');
      
      const response = await api.put('/notifications/settings/', settingsData);
      
      // Clear cache
      clearCache('notification_settings');
      
      return {
        success: true,
        message: 'Notification settings updated successfully',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error updating notification settings:', error);
      return handleNotificationError(error, 'Failed to update notification settings');
    }
  },
  
  /**
   * Get notification preferences
   */
  getPreferences: async () => {
    try {
      const response = await api.get('/notifications/preferences/');
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting notification preferences:', error);
      return handleNotificationError(error, 'Failed to get notification preferences');
    }
  },
  
  /**
   * Update notification preferences
   */
  updatePreferences: async (preferencesData) => {
    try {
      const response = await api.put('/notifications/preferences/', preferencesData);
      
      return {
        success: true,
        message: 'Notification preferences updated successfully',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error updating notification preferences:', error);
      return handleNotificationError(error, 'Failed to update notification preferences');
    }
  },
  
  // ==================== NOTIFICATION STATISTICS ====================
  
  /**
   * Get notification statistics
   */
  getStats: async (params = {}) => {
    const cacheKey = getCacheKey('notification_stats', params);
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      console.log('📊 Getting notification statistics');
      
      const response = await api.get('/notifications/stats/', { params });
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, NOTIFICATION_CONSTANTS.CACHE_TTL.STATS);
      return result;
    } catch (error) {
      console.error('❌ Error getting notification statistics:', error);
      return handleNotificationError(error, 'Failed to get notification statistics');
    }
  },
  
  /**
   * Get unread count
   */
  getUnreadCount: async () => {
    try {
      const response = await api.get('/notifications/unread-count/');
      
      return {
        success: true,
        data: response.data,
        count: response.data.count || 0,
        urgent_count: response.data.urgent_count || 0,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting unread count:', error);
      return handleNotificationError(error, 'Failed to get unread count');
    }
  },
  
  // ==================== TEMPLATE MANAGEMENT ====================
  
  /**
   * Get notification templates
   */
  getTemplates: async () => {
    try {
      const response = await api.get('/notifications/templates/');
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting notification templates:', error);
      return handleNotificationError(error, 'Failed to get notification templates');
    }
  },
  
  /**
   * Get template by ID
   */
  getTemplateById: async (templateId) => {
    try {
      const response = await api.get(`/notifications/templates/${templateId}/`);
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting notification template:', error);
      return handleNotificationError(error, 'Failed to get notification template');
    }
  },
  
  /**
   * Create notification template
   */
  createTemplate: async (templateData) => {
    try {
      const response = await api.post('/notifications/templates/', templateData);
      
      return {
        success: true,
        message: 'Notification template created successfully',
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error creating notification template:', error);
      return handleNotificationError(error, 'Failed to create notification template');
    }
  },
  
  /**
   * Preview template
   */
  previewTemplate: async (templateId, context = {}) => {
    try {
      const response = await api.post(`/notifications/templates/${templateId}/preview/`, { context });
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error previewing template:', error);
      return handleNotificationError(error, 'Failed to preview template');
    }
  },
  
  // ==================== UTILITY FUNCTIONS ====================
  
  /**
   * Format notification for display
   */
  formatNotification: (notification) => {
    if (!notification) return null;
    
    const formatted = {
      id: notification.id,
      title: notification.title,
      message: notification.message,
      type: notification.type,
      channel: notification.channel,
      priority: notification.priority || NOTIFICATION_CONSTANTS.PRIORITY.MEDIUM,
      status: notification.status || NOTIFICATION_CONSTANTS.STATUS.UNREAD,
      delivery_method: notification.delivery_method || NOTIFICATION_CONSTANTS.DELIVERY.IN_APP,
      actions: notification.actions || [],
      metadata: notification.metadata || {},
      data: notification.data || {},
      created_at: notification.created_at ? new Date(notification.created_at) : null,
      updated_at: notification.updated_at ? new Date(notification.updated_at) : null,
      read_at: notification.read_at ? new Date(notification.read_at) : null,
      expires_at: notification.expires_at ? new Date(notification.expires_at) : null,
      is_expired: notification.is_expired || false,
      user_email: notification.user_email,
      user_full_name: notification.user_full_name,
      time_ago: notification.time_ago
    };
    
    // Add type-specific formatting
    formatted.icon = notificationsAPI.getNotificationIcon(formatted.type);
    formatted.color = notificationsAPI.getNotificationColor(formatted.priority);
    formatted.badge = notificationsAPI.getNotificationBadge(formatted.type);
    formatted.time_ago = notificationsAPI.formatTimeAgo(formatted.created_at);
    
    return formatted;
  },
  
  /**
   * Get notification icon
   */
  getNotificationIcon: (type) => {
    const iconMap = {
      [NOTIFICATION_CONSTANTS.TYPE.SYSTEM]: 'bi-gear',
      [NOTIFICATION_CONSTANTS.TYPE.ACADEMIC]: 'bi-mortarboard',
      [NOTIFICATION_CONSTANTS.TYPE.FINANCIAL]: 'bi-cash',
      [NOTIFICATION_CONSTANTS.TYPE.SECURITY]: 'bi-shield',
      [NOTIFICATION_CONSTANTS.TYPE.EVENT]: 'bi-calendar-event',
      [NOTIFICATION_CONSTANTS.TYPE.ANNOUNCEMENT]: 'bi-megaphone',
      [NOTIFICATION_CONSTANTS.TYPE.MESSAGE]: 'bi-chat',
      [NOTIFICATION_CONSTANTS.TYPE.ASSIGNMENT]: 'bi-journal-text',
      [NOTIFICATION_CONSTANTS.TYPE.GRADE]: 'bi-journal-check',
      [NOTIFICATION_CONSTANTS.TYPE.ATTENDANCE]: 'bi-clipboard-check',
      [NOTIFICATION_CONSTANTS.TYPE.REMINDER]: 'bi-alarm',
      [NOTIFICATION_CONSTANTS.TYPE.APPROVAL]: 'bi-check-circle',
      [NOTIFICATION_CONSTANTS.TYPE.ALERT]: 'bi-exclamation-triangle',
      [NOTIFICATION_CONSTANTS.TYPE.WELCOME]: 'bi-emoji-smile'
    };
    
    return iconMap[type] || 'bi-bell';
  },
  
  /**
   * Get notification color
   */
  getNotificationColor: (priority) => {
    const colorMap = {
      [NOTIFICATION_CONSTANTS.PRIORITY.URGENT]: 'danger',
      [NOTIFICATION_CONSTANTS.PRIORITY.HIGH]: 'warning',
      [NOTIFICATION_CONSTANTS.PRIORITY.MEDIUM]: 'info',
      [NOTIFICATION_CONSTANTS.PRIORITY.LOW]: 'secondary'
    };
    
    return colorMap[priority] || 'info';
  },
  
  /**
   * Get notification badge text
   */
  getNotificationBadge: (type) => {
    const badgeMap = {
      [NOTIFICATION_CONSTANTS.TYPE.SYSTEM]: 'System',
      [NOTIFICATION_CONSTANTS.TYPE.ACADEMIC]: 'Academic',
      [NOTIFICATION_CONSTANTS.TYPE.FINANCIAL]: 'Financial',
      [NOTIFICATION_CONSTANTS.TYPE.SECURITY]: 'Security',
      [NOTIFICATION_CONSTANTS.TYPE.EVENT]: 'Event',
      [NOTIFICATION_CONSTANTS.TYPE.ANNOUNCEMENT]: 'Announcement',
      [NOTIFICATION_CONSTANTS.TYPE.MESSAGE]: 'Message',
      [NOTIFICATION_CONSTANTS.TYPE.ASSIGNMENT]: 'Assignment',
      [NOTIFICATION_CONSTANTS.TYPE.GRADE]: 'Grade',
      [NOTIFICATION_CONSTANTS.TYPE.ATTENDANCE]: 'Attendance',
      [NOTIFICATION_CONSTANTS.TYPE.REMINDER]: 'Reminder',
      [NOTIFICATION_CONSTANTS.TYPE.APPROVAL]: 'Approval',
      [NOTIFICATION_CONSTANTS.TYPE.ALERT]: 'Alert',
      [NOTIFICATION_CONSTANTS.TYPE.WELCOME]: 'Welcome'
    };
    
    return badgeMap[type] || 'Notification';
  },
  
  /**
   * Format time ago
   */
  formatTimeAgo: (date) => {
    if (!date) return 'Unknown time';
    
    if (typeof date === 'string') {
      date = new Date(date);
    }
    
    const now = new Date();
    const diff = now - date;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 30) return `${days}d ago`;
    
    return date.toLocaleDateString();
  },
  
  /**
   * Parse notification actions
   */
  parseNotificationActions: (actions) => {
    if (!Array.isArray(actions)) return [];
    
    return actions.map(action => ({
      type: action.type || NOTIFICATION_CONSTANTS.ACTION_TYPE.BUTTON,
      label: action.label || 'Action',
      url: action.url || action.path || action.link,
      method: action.method || 'GET',
      data: action.data || {},
      confirm: action.confirm || false,
      confirmMessage: action.confirm_message || 'Are you sure?'
    }));
  },
  
  /**
   * Handle notification action
   */
  handleNotificationAction: async (action, notificationId) => {
    try {
      if (action.confirm) {
        const confirmed = window.confirm(action.confirmMessage);
        if (!confirmed) return { success: false, message: 'Action cancelled' };
      }
      
      switch (action.type) {
        case NOTIFICATION_CONSTANTS.ACTION_TYPE.LINK:
          if (action.url) {
            window.location.href = action.url;
          }
          return { success: true, message: 'Navigation triggered' };
          
        case NOTIFICATION_CONSTANTS.ACTION_TYPE.BUTTON:
          // Handle button action (could be API call)
          if (action.url && action.method === 'POST') {
            const response = await api.post(action.url, action.data);
            return {
              success: true,
              message: 'Action completed',
              data: response.data
            };
          }
          return { success: true, message: 'Button action handled' };
          
        case NOTIFICATION_CONSTANTS.ACTION_TYPE.CONFIRM:
          // Mark notification as read after confirmation
          await notificationsAPI.markAsRead(notificationId);
          return { success: true, message: 'Notification confirmed' };
          
        default:
          return { success: false, message: 'Unknown action type' };
      }
    } catch (error) {
      console.error('❌ Error handling notification action:', error);
      return { success: false, message: 'Failed to handle notification action', error: error.message };
    }
  },
  
  /**
   * Check if notification is expired
   */
  isNotificationExpired: (notification) => {
    if (!notification.expires_at) return false;
    
    const expiresAt = typeof notification.expires_at === 'string' 
      ? new Date(notification.expires_at) 
      : notification.expires_at;
    
    const now = new Date();
    return now > expiresAt;
  },
  
  /**
   * Check if notification should be shown
   */
  shouldShowNotification: (notification, userSettings = {}) => {
    // Check if expired
    if (notificationsAPI.isNotificationExpired(notification)) {
      return false;
    }
    
    // Check if already read
    if (notification.status === NOTIFICATION_CONSTANTS.STATUS.READ) {
      return false;
    }
    
    // Check user preferences
    if (userSettings[notification.type] === false) {
      return false;
    }
    
    // Check delivery method
    if (notification.delivery_method !== NOTIFICATION_CONSTANTS.DELIVERY.IN_APP) {
      return false;
    }
    
    return true;
  },
  
  /**
   * Generate notification summary
   */
  generateNotificationSummary: (notifications) => {
    const summary = {
      total: notifications.length,
      unread: notifications.filter(n => n.status === NOTIFICATION_CONSTANTS.STATUS.UNREAD).length,
      byType: {},
      byPriority: {},
      recent: notifications.slice(0, 5)
    };
    
    // Count by type
    notifications.forEach(notification => {
      summary.byType[notification.type] = (summary.byType[notification.type] || 0) + 1;
      summary.byPriority[notification.priority] = (summary.byPriority[notification.priority] || 0) + 1;
    });
    
    return summary;
  },
  
  // ==================== POLLING & REAL-TIME UPDATES ====================
  
  /**
   * Start notification polling
   */
  startPolling: (interval = NOTIFICATION_CONSTANTS.POLL_INTERVAL, callback) => {
    let pollingInterval = null;
    
    const poll = async () => {
      try {
        const result = await notificationsAPI.getUnreadCount();
        if (result.success && callback) {
          callback(result);
        }
      } catch (error) {
        console.error('❌ Polling error:', error);
      }
    };
    
    // Start polling
    pollingInterval = setInterval(poll, interval);
    
    // Initial poll
    poll();
    
    return {
      stop: () => {
        if (pollingInterval) {
          clearInterval(pollingInterval);
          pollingInterval = null;
        }
      }
    };
  },
  
  // ==================== TEST FUNCTIONS ====================
  
  /**
   * Test notification functionality
   */
  testNotification: async () => {
    try {
      // Create test notification
      const testNotification = {
        title: 'Test Notification',
        message: 'This is a test notification from the system.',
        type: NOTIFICATION_CONSTANTS.TYPE.SYSTEM,
        channel: NOTIFICATION_CONSTANTS.CHANNEL.ALL,
        priority: NOTIFICATION_CONSTANTS.PRIORITY.LOW,
        delivery_method: NOTIFICATION_CONSTANTS.DELIVERY.IN_APP
      };
      
      const result = await notificationsAPI.create(testNotification);
      
      return {
        success: result.success,
        message: result.message,
        notification_id: result.id,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        success: false,
        message: 'Test notification failed',
        error: error.message,
        timestamp: Date.now()
      };
    }
  },
  
  /**
   * Get API endpoints
   */
  getEndpoints: () => {
    return {
      notifications: '/notifications/notifications/',
      unread: '/notifications/notifications/unread/',
      recent: '/notifications/notifications/recent/',
      settings: '/notifications/settings/',
      preferences: '/notifications/preferences/',
      stats: '/notifications/stats/',
      unreadCount: '/notifications/unread-count/',
      templates: '/notifications/templates/',
      markAllRead: '/notifications/notifications/mark-all-read/'
    };
  }
};

export default notificationsAPI;