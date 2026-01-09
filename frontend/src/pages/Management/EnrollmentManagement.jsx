import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function EnrollmentManagement() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('applications');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');

  const applications = [
    {
      id: 'APP-001',
      studentName: 'John Smith',
      gradeLevel: '9th Grade',
      appliedDate: '2024-01-15',
      status: 'pending',
      priority: 'high',
      program: 'Regular Admission',
      contact: 'john.smith@email.com'
    },
    {
      id: 'APP-002',
      studentName: 'Sarah Johnson',
      gradeLevel: '10th Grade',
      appliedDate: '2024-01-14',
      status: 'under-review',
      priority: 'medium',
      program: 'Honors Program',
      contact: 'sarah.j@email.com'
    },
    {
      id: 'APP-003',
      studentName: 'Michael Brown',
      gradeLevel: '11th Grade',
      appliedDate: '2024-01-12',
      status: 'accepted',
      priority: 'low',
      program: 'Transfer Student',
      contact: 'm.brown@email.com'
    },
    {
      id: 'APP-004',
      studentName: 'Emily Davis',
      gradeLevel: '9th Grade',
      appliedDate: '2024-01-10',
      status: 'rejected',
      priority: 'medium',
      program: 'Regular Admission',
      contact: 'emily.davis@email.com'
    },
    {
      id: 'APP-005',
      studentName: 'David Wilson',
      gradeLevel: '12th Grade',
      appliedDate: '2024-01-08',
      status: 'waitlisted',
      priority: 'low',
      program: 'International Student',
      contact: 'd.wilson@email.com'
    }
  ];

  const enrollmentStats = {
    totalApplications: 156,
    pendingReview: 23,
    accepted: 89,
    enrolled: 67,
    acceptanceRate: '57%'
  };

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.studentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === 'all' || app.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending': return { class: 'bg-warning', text: 'Pending' };
      case 'under-review': return { class: 'bg-info', text: 'Under Review' };
      case 'accepted': return { class: 'bg-success', text: 'Accepted' };
      case 'rejected': return { class: 'bg-danger', text: 'Rejected' };
      case 'waitlisted': return { class: 'bg-secondary', text: 'Waitlisted' };
      default: return { class: 'bg-secondary', text: status };
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high': return 'bg-danger';
      case 'medium': return 'bg-warning';
      case 'low': return 'bg-success';
      default: return 'bg-secondary';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Enrollment Management</h1>
          <p className="lead">Manage student applications, admissions, and enrollment processes</p>
        </div>
        <Link to="/admin" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admin
        </Link>
      </div>

      {/* Enrollment Statistics */}
      <div className="row mb-4">
        <div className="col-md-2">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>{enrollmentStats.totalApplications}</h3>
              <p className="mb-0">Applications</p>
            </div>
          </div>
        </div>
        <div className="col-md-2">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>{enrollmentStats.pendingReview}</h3>
              <p className="mb-0">Pending</p>
            </div>
          </div>
        </div>
        <div className="col-md-2">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>{enrollmentStats.accepted}</h3>
              <p className="mb-0">Accepted</p>
            </div>
          </div>
        </div>
        <div className="col-md-2">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>{enrollmentStats.enrolled}</h3>
              <p className="mb-0">Enrolled</p>
            </div>
          </div>
        </div>
        <div className="col-md-2">
          <div className="card bg-secondary text-white">
            <div className="card-body text-center">
              <h3>{enrollmentStats.acceptanceRate}</h3>
              <p className="mb-0">Acceptance Rate</p>
            </div>
          </div>
        </div>
        <div className="col-md-2">
          <div className="card bg-dark text-white">
            <div className="card-body text-center">
              <h3>45</h3>
              <p className="mb-0">Capacity Left</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="card mb-4">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'applications' ? 'active' : ''}`}
                onClick={() => setActiveTab('applications')}
              >
                <i className="bi bi-inbox me-2"></i>
                Applications
                <span className="badge bg-primary ms-2">{applications.length}</span>
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'enrolled' ? 'active' : ''}`}
                onClick={() => setActiveTab('enrolled')}
              >
                <i className="bi bi-people me-2"></i>
                Enrolled Students
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'reports' ? 'active' : ''}`}
                onClick={() => setActiveTab('reports')}
              >
                <i className="bi bi-graph-up me-2"></i>
                Enrollment Reports
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Applications Tab */}
          {activeTab === 'applications' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="mb-0">Student Applications</h5>
                <div className="d-flex gap-2">
                  <button className="btn btn-success">
                    <i className="bi bi-download me-2"></i>
                    Export
                  </button>
                  <button className="btn btn-primary">
                    <i className="bi bi-plus-circle me-2"></i>
                    New Application
                  </button>
                </div>
              </div>

              {/* Search and Filter */}
              <div className="row g-3 mb-4">
                <div className="col-md-6">
                  <div className="input-group">
                    <span className="input-group-text">
                      <i className="bi bi-search"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search applications by student name or ID..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="col-md-4">
                  <select
                    className="form-select"
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                  >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="under-review">Under Review</option>
                    <option value="accepted">Accepted</option>
                    <option value="rejected">Rejected</option>
                    <option value="waitlisted">Waitlisted</option>
                  </select>
                </div>
                <div className="col-md-2">
                  <button className="btn btn-outline-primary w-100">
                    <i className="bi bi-funnel me-2"></i>
                    Filter
                  </button>
                </div>
              </div>

              {/* Applications Table */}
              <div className="table-responsive">
                <table className="table table-striped table-hover">
                  <thead>
                    <tr>
                      <th>Application ID</th>
                      <th>Student Name</th>
                      <th>Grade Level</th>
                      <th>Program</th>
                      <th>Applied Date</th>
                      <th>Status</th>
                      <th>Priority</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredApplications.map(app => {
                      const statusBadge = getStatusBadge(app.status);
                      return (
                        <tr key={app.id}>
                          <td>
                            <strong>{app.id}</strong>
                          </td>
                          <td>
                            <div>
                              <div className="fw-bold">{app.studentName}</div>
                              <small className="text-muted">{app.contact}</small>
                            </div>
                          </td>
                          <td>{app.gradeLevel}</td>
                          <td>{app.program}</td>
                          <td>{app.appliedDate}</td>
                          <td>
                            <span className={`badge ${statusBadge.class}`}>
                              {statusBadge.text}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${getPriorityBadge(app.priority)}`}>
                              {app.priority}
                            </span>
                          </td>
                          <td>
                            <div className="btn-group">
                              <button className="btn btn-sm btn-outline-primary">
                                <i className="bi bi-eye"></i>
                              </button>
                              <button className="btn btn-sm btn-outline-warning">
                                <i className="bi bi-pencil"></i>
                              </button>
                              <button className="btn btn-sm btn-outline-info">
                                <i className="bi bi-chat"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {filteredApplications.length === 0 && (
                <div className="text-center py-5">
                  <i className="bi bi-search display-1 text-muted mb-3"></i>
                  <h4>No applications found</h4>
                  <p className="text-muted">
                    Try adjusting your search criteria or filter settings.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Enrolled Students Tab */}
          {activeTab === 'enrolled' && (
            <div>
              <h5 className="mb-4">Enrolled Students</h5>
              <div className="alert alert-info">
                <i className="bi bi-info-circle me-2"></i>
                This section shows all currently enrolled students. Use the search and filters to find specific students.
              </div>
              {/* Enrolled students content would go here */}
            </div>
          )}

          {/* Reports Tab */}
          {activeTab === 'reports' && (
            <div>
              <h5 className="mb-4">Enrollment Reports & Analytics</h5>
              <div className="row">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">Application Trends</h6>
                      <p className="text-muted">Monthly application statistics</p>
                      {/* Chart would go here */}
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">Enrollment by Grade</h6>
                      <p className="text-muted">Distribution across grade levels</p>
                      {/* Chart would go here */}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-send-check display-4 text-primary mb-3"></i>
              <h5>Send Decisions</h5>
              <p className="text-muted">
                Send acceptance/rejection letters to applicants
              </p>
              <button className="btn btn-primary">Send Notifications</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-calendar-check display-4 text-success mb-3"></i>
              <h5>Admission Events</h5>
              <p className="text-muted">
                Schedule interviews and campus tours
              </p>
              <button className="btn btn-success">Manage Events</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-gear display-4 text-warning mb-3"></i>
              <h5>Enrollment Settings</h5>
              <p className="text-muted">
                Configure enrollment periods and requirements
              </p>
              <button className="btn btn-warning">Configure</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EnrollmentManagement;