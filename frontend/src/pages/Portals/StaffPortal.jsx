// frontend/src/pages/Portals/StaffPortal.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { staffAPI } from '../../services/staffAPI';

const StaffPortal = () => {
  const { currentUser, getFullName } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Mock API function - replace with actual API
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // Replace with actual API call
      const mockData = {
        staff_stats: [
          { title: 'Pending Tasks', value: 8, color: 'warning', icon: '📋' },
          { title: 'Completed Today', value: 12, color: 'success', icon: '✅' },
          { title: 'Students Assisted', value: 25, color: 'primary', icon: '👥' },
          { title: 'Documents Processed', value: 18, color: 'info', icon: '📄' }
        ],
        recent_activities: [
          { id: 1, type: 'student_registration', student: 'John Mutisya', time: '2 hours ago', status: 'completed' },
          { id: 2, type: 'fee_payment', student: 'Mary Achieng', time: '3 hours ago', status: 'completed' },
          { id: 3, type: 'document_request', student: 'Peter Omondi', time: '4 hours ago', status: 'pending' },
          { id: 4, type: 'clearance', student: 'Sarah Wanjiku', time: '5 hours ago', status: 'in-progress' }
        ],
        upcoming_tasks: [
          { id: 1, title: 'Process fee payments', priority: 'high', due: 'Today 2:00 PM' },
          { id: 2, title: 'Update student records', priority: 'medium', due: 'Tomorrow 9:00 AM' },
          { id: 3, title: 'Prepare monthly report', priority: 'low', due: 'End of week' }
        ],
        quick_links: [
          { title: 'Student Records', path: '/students', icon: '👨‍🎓', description: 'Manage student information' },
          { title: 'Fee Management', path: '/finance/payments', icon: '💰', description: 'Process payments and receipts' },
          { title: 'Document Center', path: '/documents', icon: '📑', description: 'Manage school documents' },
          { title: 'Attendance', path: '/attendance', icon: '📊', description: 'View and manage attendance' },
          { title: 'Communication', path: '/communication', icon: '💬', description: 'Send announcements' },
          { title: 'Reports', path: '/reports', icon: '📈', description: 'Generate reports' }
        ]
      };
      
      setDashboardData(mockData);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error loading staff dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const staffStats = dashboardData?.staff_stats || [];
  const recentActivities = dashboardData?.recent_activities || [];
  const upcomingTasks = dashboardData?.upcoming_tasks || [];
  const quickLinks = dashboardData?.quick_links || [];

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: { class: 'bg-success', text: 'Completed' },
      pending: { class: 'bg-warning', text: 'Pending' },
      'in-progress': { class: 'bg-info', text: 'In Progress' },
      high: { class: 'bg-danger', text: 'High' },
      medium: { class: 'bg-warning', text: 'Medium' },
      low: { class: 'bg-info', text: 'Low' }
    };
    
    const config = statusConfig[status] || { class: 'bg-secondary', text: status };
    return `<span class="badge ${config.class}">${config.text}</span>`;
  };

  const getActivityIcon = (type) => {
    const icons = {
      student_registration: '👨‍🎓',
      fee_payment: '💰',
      document_request: '📄',
      clearance: '✅',
      default: '📋'
    };
    return icons[type] || icons.default;
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 text-muted">Loading Staff Portal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      {/* Header Section */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Staff Portal</h1>
              <p className="text-muted mb-0">
                Welcome, {getFullName()}! Administrative support and management.
              </p>
            </div>
            <div className="d-flex align-items-center gap-3">
              <span className="badge bg-primary">
                <i className="fas fa-user-tie me-1"></i>
                Office Staff
              </span>
              <button className="btn btn-outline-primary btn-sm">
                <i className="fas fa-bell me-1"></i>
                Notifications
              </button>
            </div>
          </div>
          <hr />
        </div>
      </div>

      {error && (
        <div className="row mb-4">
          <div className="col-12">
            <div className="alert alert-warning alert-dismissible fade show" role="alert">
              <i className="fas fa-exclamation-triangle me-2"></i>
              {error}
              <button type="button" className="btn-close" onClick={() => setError(null)}></button>
            </div>
          </div>
        </div>
      )}

      {/* Staff Statistics */}
      <div className="row mb-4">
        {staffStats.map((stat, index) => (
          <div key={index} className="col-12 col-sm-6 col-lg-3 mb-3">
            <div className={`card border-${stat.color} h-100`}>
              <div className="card-body text-center">
                <div className="mb-2" style={{ fontSize: '2rem' }}>
                  {stat.icon}
                </div>
                <h2 className={`text-${stat.color}`}>{stat.value}</h2>
                <p className="text-muted mb-0">{stat.title}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="row">
        {/* Quick Actions */}
        <div className="col-12 col-lg-8 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h5 className="card-title mb-0">Quick Actions</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {quickLinks.map((link, index) => (
                  <div key={index} className="col-12 col-sm-6 col-md-4 mb-3">
                    <button
                      className="btn btn-outline-primary w-100 h-100 p-3 text-start"
                      onClick={() => window.location.href = link.path}
                    >
                      <div className="d-flex align-items-center">
                        <span className="me-3" style={{ fontSize: '1.5rem' }}>
                          {link.icon}
                        </span>
                        <div>
                          <div className="fw-bold">{link.title}</div>
                          <small className="text-muted">{link.description}</small>
                        </div>
                      </div>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Upcoming Tasks */}
        <div className="col-12 col-lg-4 mb-4">
          <div className="card h-100">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Upcoming Tasks</h5>
              <span className="badge bg-primary">{upcomingTasks.length}</span>
            </div>
            <div className="card-body">
              {upcomingTasks.length > 0 ? (
                <div className="list-group list-group-flush">
                  {upcomingTasks.map((task, index) => (
                    <div key={task.id} className="list-group-item d-flex justify-content-between align-items-start">
                      <div className="flex-grow-1">
                        <div className="fw-bold">{task.title}</div>
                        <small className="text-muted">Due: {task.due}</small>
                      </div>
                      <span 
                        dangerouslySetInnerHTML={{ 
                          __html: getStatusBadge(task.priority) 
                        }} 
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <div className="text-muted mb-2">No upcoming tasks</div>
                  <small className="text-muted">All tasks are completed!</small>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Recent Activities</h5>
              <button className="btn btn-sm btn-outline-primary">
                View All
              </button>
            </div>
            <div className="card-body p-0">
              {recentActivities.length > 0 ? (
                <div className="list-group list-group-flush">
                  {recentActivities.map((activity, index) => (
                    <div key={activity.id} className="list-group-item">
                      <div className="d-flex align-items-center">
                        <div className="flex-shrink-0 me-3" style={{ fontSize: '1.5rem' }}>
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-grow-1">
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <span className="fw-bold">{activity.student}</span>
                              <small className="text-muted ms-2">
                                {activity.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </small>
                            </div>
                            <span 
                              dangerouslySetInnerHTML={{ 
                                __html: getStatusBadge(activity.status) 
                              }} 
                            />
                          </div>
                          <small className="text-muted">{activity.time}</small>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-5">
                  <div className="text-muted mb-2">No recent activities</div>
                  <small className="text-muted">Activities will appear here as you work</small>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Daily Summary */}
      <div className="row mt-4">
        <div className="col-12 col-md-6 mb-3">
          <div className="card bg-light">
            <div className="card-body">
              <h6 className="card-title text-primary">
                <i className="fas fa-chart-line me-2"></i>
                Today's Summary
              </h6>
              <div className="row text-center">
                <div className="col-4">
                  <div className="border-end">
                    <div className="h5 text-success">12</div>
                    <small className="text-muted">Completed</small>
                  </div>
                </div>
                <div className="col-4">
                  <div className="border-end">
                    <div className="h5 text-warning">3</div>
                    <small className="text-muted">Pending</small>
                  </div>
                </div>
                <div className="col-4">
                  <div>
                    <div className="h5 text-info">2</div>
                    <small className="text-muted">In Progress</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-md-6 mb-3">
          <div className="card bg-light">
            <div className="card-body">
              <h6 className="card-title text-primary">
                <i className="fas fa-clock me-2"></i>
                Quick Tools
              </h6>
              <div className="d-flex gap-2">
                <button className="btn btn-sm btn-outline-primary flex-fill">
                  <i className="fas fa-print me-1"></i>
                  Print Reports
                </button>
                <button className="btn btn-sm btn-outline-success flex-fill">
                  <i className="fas fa-download me-1"></i>
                  Export Data
                </button>
                <button className="btn btn-sm btn-outline-info flex-fill">
                  <i className="fas fa-sync me-1"></i>
                  Refresh
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Office Hours & Contact */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card border-primary">
            <div className="card-header bg-primary bg-opacity-10">
              <h5 className="card-title mb-0 text-primary">
                <i className="fas fa-info-circle me-2"></i>
                Office Information
              </h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-12 col-md-4 text-center mb-3">
                  <div className="p-3">
                    <i className="fas fa-clock text-primary fs-2 mb-2"></i>
                    <h6>Office Hours</h6>
                    <p className="mb-1">Mon - Fri: 8:00 AM - 5:00 PM</p>
                    <p className="mb-0">Sat: 9:00 AM - 1:00 PM</p>
                  </div>
                </div>
                <div className="col-12 col-md-4 text-center mb-3">
                  <div className="p-3">
                    <i className="fas fa-phone text-success fs-2 mb-2"></i>
                    <h6>Contact</h6>
                    <p className="mb-1">Phone: +254-XXX-XXXX</p>
                    <p className="mb-0">Email: office@delvok.ac.ke</p>
                  </div>
                </div>
                <div className="col-12 col-md-4 text-center mb-3">
                  <div className="p-3">
                    <i className="fas fa-map-marker-alt text-danger fs-2 mb-2"></i>
                    <h6>Location</h6>
                    <p className="mb-0">Main Administration Building</p>
                    <small className="text-muted">Ground Floor, Room 101</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body py-2">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <span className="badge bg-success me-2">
                    <i className="fas fa-circle me-1"></i>
                    System Online
                  </span>
                  <small className="text-muted">Last updated: {new Date().toLocaleTimeString()}</small>
                </div>
                <div>
                  <small className="text-muted">
                    <i className="fas fa-user me-1"></i>
                    Logged in as: {currentUser?.email}
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffPortal;