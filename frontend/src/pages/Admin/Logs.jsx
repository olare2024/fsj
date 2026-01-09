import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Logs() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('system');
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState('all');
  const [userFilter, setUserFilter] = useState('all');

  // Mock logs data - in real app, this would come from API
  useEffect(() => {
    const mockLogs = {
      system: [
        {
          id: 1,
          timestamp: '2024-01-15 10:30:25',
          level: 'info',
          module: 'Authentication',
          message: 'User login successful',
          user: 's.mwangi@delvok.ac.ke',
          ip: '192.168.1.100'
        },
        {
          id: 2,
          timestamp: '2024-01-15 10:25:12',
          level: 'warning',
          module: 'Database',
          message: 'Slow query detected',
          user: 'system',
          ip: '127.0.0.1'
        },
        {
          id: 3,
          timestamp: '2024-01-15 09:15:33',
          level: 'error',
          module: 'File System',
          message: 'Failed to upload file: permission denied',
          user: 'r.mutiso@delvok.ac.ke',
          ip: '192.168.1.105'
        }
      ],
      security: [
        {
          id: 4,
          timestamp: '2024-01-15 11:20:15',
          level: 'warning',
          module: 'Security',
          message: 'Multiple failed login attempts',
          user: 'unknown@example.com',
          ip: '203.0.113.25'
        },
        {
          id: 5,
          timestamp: '2024-01-15 08:45:22',
          level: 'info',
          module: 'Security',
          message: 'Password changed successfully',
          user: 'g.mwende@delvok.ac.ke',
          ip: '192.168.1.102'
        }
      ],
      user: [
        {
          id: 6,
          timestamp: '2024-01-15 14:30:45',
          level: 'info',
          module: 'Gradebook',
          message: 'Grades updated for Grade 7A Mathematics',
          user: 'r.mutiso@delvok.ac.ke',
          ip: '192.168.1.105'
        },
        {
          id: 7,
          timestamp: '2024-01-15 13:15:20',
          level: 'info',
          module: 'Attendance',
          message: 'Attendance marked for Grade 9B',
          user: 'd.kimani@delvok.ac.ke',
          ip: '192.168.1.107'
        }
      ],
      admin: [
        {
          id: 8,
          timestamp: '2024-01-15 16:05:33',
          level: 'info',
          module: 'User Management',
          message: 'New user created: sarah.johnson@delvok.ac.ke',
          user: 's.mwangi@delvok.ac.ke',
          ip: '192.168.1.100'
        },
        {
          id: 9,
          timestamp: '2024-01-15 15:40:18',
          level: 'warning',
          module: 'System Settings',
          message: 'Configuration changes made',
          user: 's.mwangi@delvok.ac.ke',
          ip: '192.168.1.100'
        }
      ]
    };

    setLogs(mockLogs);
    setFilteredLogs(mockLogs[activeTab]);
  }, [activeTab]);

  useEffect(() => {
    if (logs[activeTab]) {
      let filtered = logs[activeTab];

      // Apply search filter
      if (searchTerm) {
        filtered = filtered.filter(log =>
          log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.module.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
          log.ip.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }

      // Apply level filter
      if (levelFilter !== 'all') {
        filtered = filtered.filter(log => log.level === levelFilter);
      }

      // Apply user filter
      if (userFilter !== 'all') {
        filtered = filtered.filter(log => log.user === userFilter);
      }

      // Apply date filter
      if (dateFilter) {
        filtered = filtered.filter(log => log.timestamp.startsWith(dateFilter));
      }

      setFilteredLogs(filtered);
    }
  }, [searchTerm, levelFilter, userFilter, dateFilter, logs, activeTab]);

  const getLevelColor = (level) => {
    switch (level) {
      case 'error': return 'danger';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'secondary';
    }
  };

  const getLevelIcon = (level) => {
    switch (level) {
      case 'error': return 'bi-exclamation-triangle';
      case 'warning': return 'bi-exclamation-circle';
      case 'info': return 'bi-info-circle';
      default: return 'bi-info-circle';
    }
  };

  const clearLogs = () => {
    if (window.confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
      setLogs(prev => ({ ...prev, [activeTab]: [] }));
      alert('Logs cleared successfully.');
    }
  };

  const exportLogs = () => {
    // In real app, this would generate and download a file
    alert('Logs exported successfully!');
  };

  const getUniqueUsers = () => {
    if (!logs[activeTab]) return [];
    return [...new Set(logs[activeTab].map(log => log.user))];
  };

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/admin">Admin</Link></li>
              <li className="breadcrumb-item active">System Logs</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">System Logs</h1>
              <p className="lead mb-0">Monitor system activity and security events</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">
                {filteredLogs.length} Log Entries
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="d-flex justify-content-between align-items-center">
            <ul className="nav nav-tabs card-header-tabs">
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'system' ? 'active' : ''}`}
                  onClick={() => setActiveTab('system')}
                >
                  <i className="bi bi-cpu me-2"></i>
                  System Logs
                </button>
              </li>
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'security' ? 'active' : ''}`}
                  onClick={() => setActiveTab('security')}
                >
                  <i className="bi bi-shield-check me-2"></i>
                  Security Logs
                </button>
              </li>
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'user' ? 'active' : ''}`}
                  onClick={() => setActiveTab('user')}
                >
                  <i className="bi bi-people me-2"></i>
                  User Activity
                </button>
              </li>
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'admin' ? 'active' : ''}`}
                  onClick={() => setActiveTab('admin')}
                >
                  <i className="bi bi-gear me-2"></i>
                  Admin Actions
                </button>
              </li>
            </ul>
            <div>
              <button 
                className="btn btn-outline-danger btn-sm me-2"
                onClick={clearLogs}
              >
                <i className="bi bi-trash me-2"></i>
                Clear Logs
              </button>
              <button 
                className="btn btn-outline-primary btn-sm"
                onClick={exportLogs}
              >
                <i className="bi bi-download me-2"></i>
                Export
              </button>
            </div>
          </div>
        </div>

        <div className="card-body">
          {/* Filters */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-2">
              <select 
                className="form-select"
                value={levelFilter}
                onChange={(e) => setLevelFilter(e.target.value)}
              >
                <option value="all">All Levels</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>
            <div className="col-md-2">
              <select 
                className="form-select"
                value={userFilter}
                onChange={(e) => setUserFilter(e.target.value)}
              >
                <option value="all">All Users</option>
                {getUniqueUsers().map(user => (
                  <option key={user} value={user}>{user}</option>
                ))}
              </select>
            </div>
            <div className="col-md-2">
              <input
                type="date"
                className="form-control"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <div className="d-flex gap-2">
                <button 
                  className="btn btn-outline-secondary btn-sm"
                  onClick={() => {
                    setSearchTerm('');
                    setLevelFilter('all');
                    setUserFilter('all');
                    setDateFilter('');
                  }}
                >
                  Clear Filters
                </button>
                <button className="btn btn-outline-info btn-sm">
                  <i className="bi bi-arrow-clockwise me-2"></i>
                  Refresh
                </button>
              </div>
            </div>
          </div>

          {/* Logs Table */}
          <div className="table-responsive">
            <table className="table table-hover">
              <thead className="table-light">
                <tr>
                  <th>Timestamp</th>
                  <th>Level</th>
                  <th>Module</th>
                  <th>Message</th>
                  <th>User</th>
                  <th>IP Address</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map(log => (
                  <tr key={log.id}>
                    <td>
                      <small className="text-muted">{log.timestamp}</small>
                    </td>
                    <td>
                      <span className={`badge bg-${getLevelColor(log.level)}`}>
                        <i className={`bi ${getLevelIcon(log.level)} me-1`}></i>
                        {log.level.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <small className="fw-bold">{log.module}</small>
                    </td>
                    <td>
                      <div className="log-message">
                        {log.message}
                      </div>
                    </td>
                    <td>
                      <small>{log.user}</small>
                    </td>
                    <td>
                      <code>{log.ip}</code>
                    </td>
                    <td>
                      <button className="btn btn-outline-primary btn-sm">
                        <i className="bi bi-search"></i>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredLogs.length === 0 && (
            <div className="text-center py-5">
              <i className="bi bi-journal-x display-1 text-muted"></i>
              <h4 className="mt-3">No logs found</h4>
              <p className="text-muted">
                {searchTerm || levelFilter !== 'all' || userFilter !== 'all' || dateFilter
                  ? 'Try adjusting your filters'
                  : 'No log entries for the selected category'
                }
              </p>
            </div>
          )}

          {/* Pagination */}
          {filteredLogs.length > 0 && (
            <div className="d-flex justify-content-between align-items-center mt-4">
              <div className="small text-muted">
                Showing {filteredLogs.length} of {logs[activeTab]?.length || 0} entries
              </div>
              <nav>
                <ul className="pagination pagination-sm">
                  <li className="page-item disabled">
                    <span className="page-link">Previous</span>
                  </li>
                  <li className="page-item active">
                    <span className="page-link">1</span>
                  </li>
                  <li className="page-item">
                    <a className="page-link" href="#!">2</a>
                  </li>
                  <li className="page-item">
                    <a className="page-link" href="#!">3</a>
                  </li>
                  <li className="page-item">
                    <a className="page-link" href="#!">Next</a>
                  </li>
                </ul>
              </nav>
            </div>
          )}
        </div>
      </div>

      {/* Log Statistics */}
      <div className="row mt-4">
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <div className="display-6 fw-bold text-primary">
                {logs.system?.length || 0}
              </div>
              <div>System Logs</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <div className="display-6 fw-bold text-warning">
                {logs.security?.length || 0}
              </div>
              <div>Security Events</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <div className="display-6 fw-bold text-info">
                {logs.user?.length || 0}
              </div>
              <div>User Actions</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card">
            <div className="card-body text-center">
              <div className="display-6 fw-bold text-success">
                {logs.admin?.length || 0}
              </div>
              <div>Admin Activities</div>
            </div>
          </div>
        </div>
      </div>

      {/* Log Settings */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h6 className="mb-0">Log Settings</h6>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-4">
                  <div className="form-check form-switch mb-3">
                    <input className="form-check-input" type="checkbox" defaultChecked />
                    <label className="form-check-label">Enable System Logging</label>
                  </div>
                  <div className="form-check form-switch mb-3">
                    <input className="form-check-input" type="checkbox" defaultChecked />
                    <label className="form-check-label">Enable Security Logging</label>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="mb-3">
                    <label className="form-label">Log Retention (Days)</label>
                    <input type="number" className="form-control" defaultValue="90" />
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="mb-3">
                    <label className="form-label">Log Level</label>
                    <select className="form-select" defaultValue="info">
                      <option value="error">Error Only</option>
                      <option value="warning">Warning & Error</option>
                      <option value="info">All Messages</option>
                    </select>
                  </div>
                </div>
              </div>
              <button className="btn btn-primary">
                <i className="bi bi-save me-2"></i>
                Save Log Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Logs;