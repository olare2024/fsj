import api from './api';

// Utility function for consistent error handling
const handleITError = (error, context = 'IT API') => {
  console.error(`❌ ${context} error:`, error.response?.data || error.message);
  
  if (error.response) {
    const errorData = error.response.data;
    const status = error.response.status;
    
    return {
      success: false,
      message: errorData.detail || 
              errorData.error || 
              errorData.message || 
              `${context} operation failed`,
      errors: errorData.errors || errorData.details,
      status: status,
      requiresReauth: status === 401
    };
  }
  
  if (error.request) {
    return {
      success: false,
      message: 'Network error: Unable to connect to IT services',
      status: 0
    };
  }
  
  return {
    success: false,
    message: error.message || `${context} operation failed`,
    status: 'unknown'
  };
};

export const itAPI = {
  // ==================== USER & AUTHENTICATION ====================
  
  /**
   * Get current IT user profile
   * GET /it/users/me/
   */
  getCurrentUser: async () => {
    try {
      console.log('🔄 Fetching IT user profile...');
      const response = await api.get('/it/users/me/');
      
      return {
        success: true,
        user: response.data,
        message: 'User profile fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Current User');
    }
  },

  /**
   * Get IT staff list
   * GET /it/users/
   */
  getITStaff: async (params = {}) => {
    try {
      const response = await api.get('/it/users/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'IT staff list fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get IT Staff');
    }
  },

  // ==================== IT STATISTICS & OVERVIEW ====================
  
  /**
   * Get IT statistics - Head Teacher Portal calls this
   * GET /it/statistics/
   */
  getITStats: async () => {
    try {
      console.log('📊 Fetching IT statistics...');
      const response = await api.get('/it/statistics/');
      
      return {
        success: true,
        data: response.data,
        message: 'IT statistics fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get IT Stats');
    }
  },

  /**
   * Get IT dashboard overview
   * GET /it/dashboard/
   */
  getDashboardOverview: async () => {
    try {
      const response = await api.get('/it/dashboard/');
      
      return {
        success: true,
        data: response.data,
        message: 'Dashboard overview fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Dashboard Overview');
    }
  },

  /**
   * Get system health status
   * GET /it/system-health/
   */
  getSystemHealth: async () => {
    try {
      const response = await api.get('/it/system-health/');
      
      return {
        success: true,
        data: response.data,
        message: 'System health status fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get System Health');
    }
  },

  // ==================== DEVICE MANAGEMENT ====================
  
  /**
   * Get all devices - Head Teacher Portal calls this
   * GET /it/devices/
   */
  getDevices: async (params = {}) => {
    try {
      console.log('💻 Fetching devices...');
      const response = await api.get('/it/devices/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Devices fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Devices');
    }
  },

  /**
   * Get specific device
   * GET /it/devices/{id}/
   */
  getDevice: async (deviceId) => {
    try {
      const response = await api.get(`/it/devices/${deviceId}/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Device details fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Device');
    }
  },

  /**
   * Register new device - Head Teacher Portal calls this
   * POST /it/devices/
   */
  registerDevice: async (deviceData) => {
    try {
      console.log('➕ Registering new device:', deviceData.name);
      const response = await api.post('/it/devices/', deviceData);
      
      return {
        success: true,
        data: response.data,
        message: 'Device registered successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Register Device');
    }
  },

  /**
   * Update device
   * PUT /it/devices/{id}/
   */
  updateDevice: async (deviceId, deviceData) => {
    try {
      const response = await api.put(`/it/devices/${deviceId}/`, deviceData);
      
      return {
        success: true,
        data: response.data,
        message: 'Device updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Update Device');
    }
  },

  /**
   * Delete device
   * DELETE /it/devices/{id}/
   */
  deleteDevice: async (deviceId) => {
    try {
      const response = await api.delete(`/it/devices/${deviceId}/`);
      
      return {
        success: true,
        message: 'Device deleted successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Delete Device');
    }
  },

  /**
   * Get device types
   * GET /it/device-types/
   */
  getDeviceTypes: async (params = {}) => {
    try {
      const response = await api.get('/it/device-types/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Device Types');
    }
  },

  /**
   * Get device by serial number
   * GET /it/devices/serial/{serialNumber}/
   */
  getDeviceBySerial: async (serialNumber) => {
    try {
      const response = await api.get(`/it/devices/serial/${serialNumber}/`);
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Device By Serial');
    }
  },

  /**
   * Bulk import devices
   * POST /it/devices/bulk-import/
   */
  bulkImportDevices: async (devicesData) => {
    try {
      const response = await api.post('/it/devices/bulk-import/', devicesData);
      
      return {
        success: true,
        data: response.data,
        message: 'Devices imported successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Bulk Import Devices');
    }
  },

  // ==================== SUPPORT TICKETS ====================
  
  /**
   * Get all tickets - Head Teacher Portal calls this
   * GET /it/tickets/
   */
  getTickets: async (params = {}) => {
    try {
      console.log('🎫 Fetching support tickets...');
      const response = await api.get('/it/tickets/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Tickets fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Tickets');
    }
  },

  /**
   * Get specific ticket
   * GET /it/tickets/{id}/
   */
  getTicket: async (ticketId) => {
    try {
      const response = await api.get(`/it/tickets/${ticketId}/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Ticket details fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Ticket');
    }
  },

  /**
   * Create new ticket - Head Teacher Portal calls this
   * POST /it/tickets/
   */
  createTicket: async (ticketData) => {
    try {
      console.log('🎫 Creating new ticket:', ticketData.title);
      const response = await api.post('/it/tickets/', ticketData);
      
      return {
        success: true,
        data: response.data,
        message: 'Ticket created successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Create Ticket');
    }
  },

  /**
   * Update ticket
   * PUT /it/tickets/{id}/
   */
  updateTicket: async (ticketId, ticketData) => {
    try {
      const response = await api.put(`/it/tickets/${ticketId}/`, ticketData);
      
      return {
        success: true,
        data: response.data,
        message: 'Ticket updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Update Ticket');
    }
  },

  /**
   * Assign ticket
   * POST /it/tickets/{id}/assign/
   */
  assignTicket: async (ticketId, assigneeData) => {
    try {
      const response = await api.post(`/it/tickets/${ticketId}/assign/`, assigneeData);
      
      return {
        success: true,
        data: response.data,
        message: 'Ticket assigned successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Assign Ticket');
    }
  },

  /**
   * Resolve ticket
   * POST /it/tickets/{id}/resolve/
   */
  resolveTicket: async (ticketId, resolutionData = {}) => {
    try {
      const response = await api.post(`/it/tickets/${id}/resolve/`, resolutionData);
      
      return {
        success: true,
        data: response.data,
        message: 'Ticket resolved successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Resolve Ticket');
    }
  },

  /**
   * Get ticket categories
   * GET /it/ticket-categories/
   */
  getTicketCategories: async () => {
    try {
      const response = await api.get('/it/ticket-categories/');
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Ticket Categories');
    }
  },

  // ==================== SERVER MANAGEMENT ====================
  
  /**
   * Get all servers - Head Teacher Portal calls this
   * GET /it/servers/
   */
  getServers: async (params = {}) => {
    try {
      console.log('🖥️ Fetching servers...');
      const response = await api.get('/it/servers/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Servers fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Servers');
    }
  },

  /**
   * Get server details
   * GET /it/servers/{id}/
   */
  getServer: async (serverId) => {
    try {
      const response = await api.get(`/it/servers/${serverId}/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Server details fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Server');
    }
  },

  /**
   * Get server metrics
   * GET /it/servers/{id}/metrics/
   */
  getServerMetrics: async (serverId, params = {}) => {
    try {
      const response = await api.get(`/it/servers/${serverId}/metrics/`, { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Server metrics fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Server Metrics');
    }
  },

  /**
   * Restart server
   * POST /it/servers/{id}/restart/
   */
  restartServer: async (serverId) => {
    try {
      const response = await api.post(`/it/servers/${serverId}/restart/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Server restart initiated',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Restart Server');
    }
  },

  /**
   * Get server logs
   * GET /it/servers/{id}/logs/
   */
  getServerLogs: async (serverId, params = {}) => {
    try {
      const response = await api.get(`/it/servers/${serverId}/logs/`, { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Server Logs');
    }
  },

  // ==================== NETWORK MANAGEMENT ====================
  
  /**
   * Get network devices - Head Teacher Portal calls this
   * GET /it/network-devices/
   */
  getNetworkDevices: async (params = {}) => {
    try {
      console.log('🌐 Fetching network devices...');
      const response = await api.get('/it/network-devices/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Network devices fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Network Devices');
    }
  },

  /**
   * Get network status
   * GET /it/network/status/
   */
  getNetworkStatus: async () => {
    try {
      const response = await api.get('/it/network/status/');
      
      return {
        success: true,
        data: response.data,
        message: 'Network status fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Network Status');
    }
  },

  /**
   * Get network topology
   * GET /it/network/topology/
   */
  getNetworkTopology: async () => {
    try {
      const response = await api.get('/it/network/topology/');
      
      return {
        success: true,
        data: response.data,
        message: 'Network topology fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Network Topology');
    }
  },

  /**
   * Get bandwidth usage
   * GET /it/network/bandwidth/
   */
  getBandwidthUsage: async (params = {}) => {
    try {
      const response = await api.get('/it/network/bandwidth/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Bandwidth usage fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Bandwidth Usage');
    }
  },

  // ==================== SECURITY MANAGEMENT ====================
  
  /**
   * Get security alerts - Head Teacher Portal calls this
   * GET /it/security/alerts/
   */
  getSecurityAlerts: async (params = {}) => {
    try {
      console.log('🔐 Fetching security alerts...');
      const response = await api.get('/it/security/alerts/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Security alerts fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Security Alerts');
    }
  },

  /**
   * Resolve security alert - Head Teacher Portal calls this
   * POST /it/security/alerts/{id}/resolve/
   */
  resolveAlert: async (alertId, resolutionData = {}) => {
    try {
      console.log('🛡️ Resolving security alert:', alertId);
      const response = await api.post(`/it/security/alerts/${alertId}/resolve/`, resolutionData);
      
      return {
        success: true,
        data: response.data,
        message: 'Security alert resolved',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Resolve Alert');
    }
  },

  /**
   * Get security scan results
   * GET /it/security/scans/
   */
  getSecurityScans: async (params = {}) => {
    try {
      const response = await api.get('/it/security/scans/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Security Scans');
    }
  },

  /**
   * Run security scan
   * POST /it/security/scans/
   */
  runSecurityScan: async (scanData = {}) => {
    try {
      const response = await api.post('/it/security/scans/', scanData);
      
      return {
        success: true,
        data: response.data,
        message: 'Security scan initiated',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Run Security Scan');
    }
  },

  /**
   * Get firewall rules
   * GET /it/security/firewall/
   */
  getFirewallRules: async (params = {}) => {
    try {
      const response = await api.get('/it/security/firewall/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Firewall Rules');
    }
  },

  // ==================== BACKUP MANAGEMENT ====================
  
  /**
   * Get backup status - Head Teacher Portal calls this
   * GET /it/backups/
   */
  getBackupStatus: async (params = {}) => {
    try {
      console.log('💾 Fetching backup status...');
      const response = await api.get('/it/backups/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Backup status fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Backup Status');
    }
  },

  /**
   * Run backup
   * POST /it/backups/run/
   */
  runBackup: async (backupData = {}) => {
    try {
      const response = await api.post('/it/backups/run/', backupData);
      
      return {
        success: true,
        data: response.data,
        message: 'Backup initiated',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Run Backup');
    }
  },

  /**
   * Restore from backup
   * POST /it/backups/{id}/restore/
   */
  restoreBackup: async (backupId, restoreData = {}) => {
    try {
      const response = await api.post(`/it/backups/${backupId}/restore/`, restoreData);
      
      return {
        success: true,
        data: response.data,
        message: 'Restore initiated',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Restore Backup');
    }
  },

  /**
   * Get backup schedule
   * GET /it/backups/schedule/
   */
  getBackupSchedule: async () => {
    try {
      const response = await api.get('/it/backups/schedule/');
      
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Backup Schedule');
    }
  },

  // ==================== INVENTORY MANAGEMENT ====================
  
  /**
   * Get IT inventory
   * GET /it/inventory/
   */
  getInventory: async (params = {}) => {
    try {
      const response = await api.get('/it/inventory/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Inventory fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Inventory');
    }
  },

  /**
   * Get inventory item
   * GET /it/inventory/{id}/
   */
  getInventoryItem: async (itemId) => {
    try {
      const response = await api.get(`/it/inventory/${itemId}/`);
      
      return {
        success: true,
        data: response.data,
        message: 'Inventory item fetched successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Inventory Item');
    }
  },

  /**
   * Add inventory item
   * POST /it/inventory/
   */
  addInventoryItem: async (itemData) => {
    try {
      const response = await api.post('/it/inventory/', itemData);
      
      return {
        success: true,
        data: response.data,
        message: 'Inventory item added successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Add Inventory Item');
    }
  },

  /**
   * Check inventory stock
   * GET /it/inventory/stock/
   */
  checkStock: async (params = {}) => {
    try {
      const response = await api.get('/it/inventory/stock/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Stock levels checked',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Check Stock');
    }
  },

  // ==================== SOFTWARE LICENSES ====================
  
  /**
   * Get software licenses
   * GET /it/licenses/
   */
  getSoftwareLicenses: async (params = {}) => {
    try {
      const response = await api.get('/it/licenses/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'Software licenses fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Software Licenses');
    }
  },

  /**
   * Check license expiry
   * GET /it/licenses/expiry/
   */
  checkLicenseExpiry: async () => {
    try {
      const response = await api.get('/it/licenses/expiry/');
      
      return {
        success: true,
        data: response.data,
        message: 'License expiry checked',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Check License Expiry');
    }
  },

  // ==================== MONITORING & LOGS ====================
  
  /**
   * Get system logs
   * GET /it/logs/
   */
  getSystemLogs: async (params = {}) => {
    try {
      const response = await api.get('/it/logs/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        message: 'System logs fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get System Logs');
    }
  },

  /**
   * Get monitoring data
   * GET /it/monitoring/
   */
  getMonitoringData: async (params = {}) => {
    try {
      const response = await api.get('/it/monitoring/', { params });
      
      return {
        success: true,
        data: response.data,
        message: 'Monitoring data fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Monitoring Data');
    }
  },

  /**
   * Get audit trail
   * GET /it/audit/
   */
  getAuditTrail: async (params = {}) => {
    try {
      const response = await api.get('/it/audit/', { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Audit Trail');
    }
  },

  // ==================== UTILITIES ====================
  
  /**
   * Search IT resources
   * GET /it/search/
   */
  searchResources: async (query, params = {}) => {
    try {
      const response = await api.get('/it/search/', {
        params: { q: query, ...params }
      });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count || (response.data?.length || 0),
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Search Resources');
    }
  },

  /**
   * Generate IT report
   * POST /it/reports/
   */
  generateReport: async (reportData) => {
    try {
      const response = await api.post('/it/reports/', reportData);
      
      return {
        success: true,
        data: response.data,
        message: 'Report generated successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Generate Report');
    }
  },

  /**
   * Export IT data
   * GET /it/export/
   */
  exportData: async (params = {}) => {
    try {
      const response = await api.get('/it/export/', { 
        params,
        responseType: 'blob'
      });
      
      return {
        success: true,
        data: response.data,
        filename: response.headers['content-disposition']?.split('filename=')[1] || 'it-data.csv',
        message: 'Data exported successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Export Data');
    }
  },

  /**
   * Ping server
   * GET /it/ping/
   */
  pingServer: async (host) => {
    try {
      const response = await api.get('/it/ping/', { params: { host } });
      
      return {
        success: true,
        data: response.data,
        message: 'Ping completed',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Ping Server');
    }
  },

  /**
   * Test connectivity
   * GET /it/test-connectivity/
   */
  testConnectivity: async () => {
    try {
      const response = await api.get('/it/test-connectivity/');
      
      return {
        success: true,
        data: response.data,
        message: 'Connectivity test completed',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Test Connectivity');
    }
  },

  // ==================== BULK OPERATIONS ====================
  
  /**
   * Bulk update devices
   * POST /it/devices/bulk-update/
   */
  bulkUpdateDevices: async (deviceIds, updateData) => {
    try {
      const response = await api.post('/it/devices/bulk-update/', {
        device_ids: deviceIds,
        ...updateData
      });
      
      return {
        success: true,
        data: response.data,
        message: 'Devices updated successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Bulk Update Devices');
    }
  },

  /**
   * Bulk delete devices
   * POST /it/devices/bulk-delete/
   */
  bulkDeleteDevices: async (deviceIds) => {
    try {
      const response = await api.post('/it/devices/bulk-delete/', {
        device_ids: deviceIds
      });
      
      return {
        success: true,
        data: response.data,
        message: 'Devices deleted successfully',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Bulk Delete Devices');
    }
  },

  // ==================== CONFIGURATION ====================
  
  /**
   * Get IT configuration
   * GET /it/config/
   */
  getConfig: async () => {
    try {
      const response = await api.get('/it/config/');
      
      return {
        success: true,
        data: response.data,
        message: 'Configuration fetched',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Get Config');
    }
  },

  /**
   * Update IT configuration
   * PUT /it/config/
   */
  updateConfig: async (configData) => {
    try {
      const response = await api.put('/it/config/', configData);
      
      return {
        success: true,
        data: response.data,
        message: 'Configuration updated',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Update Config');
    }
  },

  // ==================== HEALTH CHECK ====================
  
  /**
   * Health check
   * GET /it/health/
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/it/health/');
      
      return {
        success: true,
        data: response.data,
        message: 'IT services are healthy',
        status: response.status
      };
    } catch (error) {
      return handleITError(error, 'Health Check');
    }
  }
};