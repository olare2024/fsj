import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Unauthorized() {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleGoBack = () => {
    navigate(-1);
  };

  const handleLoginAsDifferentUser = () => {
    logout();
    navigate('/login', { state: { from: location } });
  };

  const roleBasedActions = {
    student: [
      { path: '/student-portal', label: 'Student Portal', icon: 'bi-person' },
      { path: '/timetable', label: 'Class Schedule', icon: 'bi-calendar' },
      { path: '/grades', label: 'View Grades', icon: 'bi-journal-text' }
    ],
    parent: [
      { path: '/parent-portal', label: 'Parent Portal', icon: 'bi-people' },
      { path: '/child-progress', label: 'Child Progress', icon: 'bi-graph-up' },
      { path: '/billing', label: 'Fee Statements', icon: 'bi-receipt' }
    ],
    teacher: [
      { path: '/teacher-dashboard', label: 'Teacher Dashboard', icon: 'bi-journal' },
      { path: '/grade-management', label: 'Grade Management', icon: 'bi-pencil' },
      { path: '/attendance-management', label: 'Attendance', icon: 'bi-clipboard-check' }
    ],
    admin: [
      { path: '/admin', label: 'Admin Dashboard', icon: 'bi-speedometer2' },
      { path: '/admin/users', label: 'User Management', icon: 'bi-person-gear' },
      { path: '/admin/analytics', label: 'Analytics', icon: 'bi-graph-up' }
    ]
  };

  const getRoleActions = () => {
    return roleBasedActions[currentUser?.role] || [];
  };

  return (
    <div className="container-fluid py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8 text-center">
          {/* Error Icon */}
          <div className="mb-4">
            <i className="bi bi-shield-exclamation display-1 text-warning"></i>
          </div>

          {/* Error Message */}
          <h1 className="display-4 fw-bold text-dark mb-3">Access Denied</h1>
          <p className="fs-5 text-muted mb-4">
            You don't have permission to access this page.
          </p>

          {/* Current User Info */}
          {currentUser && (
            <div className="alert alert-info mb-4">
              <div className="d-flex align-items-center">
                <i className="bi bi-person-circle me-3 fs-4"></i>
                <div className="text-start">
                  <strong>Logged in as:</strong> {currentUser.name} ({currentUser.role})
                  <br />
                  <small>You need additional permissions to access this resource.</small>
                </div>
              </div>
            </div>
          )}

          {/* Attempted Access */}
          <div className="alert alert-warning mb-4">
            <i className="bi bi-lock me-2"></i>
            <strong>Attempted to access:</strong> {from}
          </div>

          {/* Action Buttons */}
          <div className="mb-5">
            <button 
              onClick={handleGoBack}
              className="btn btn-primary btn-lg me-3"
            >
              <i className="bi bi-arrow-left me-2"></i>
              Go Back
            </button>
            
            <Link to="/" className="btn btn-outline-primary btn-lg me-3">
              <i className="bi bi-house me-2"></i>
              Go Home
            </Link>

            {currentUser && (
              <button 
                onClick={handleLoginAsDifferentUser}
                className="btn btn-outline-secondary btn-lg"
              >
                <i className="bi bi-arrow-left-right me-2"></i>
                Switch Account
              </button>
            )}
          </div>

          {/* Role-Based Suggestions */}
          {currentUser && (
            <div className="card mb-4">
              <div className="card-header bg-light">
                <h5 className="mb-0">Your Accessible Areas</h5>
              </div>
              <div className="card-body">
                <div className="row g-3">
                  {getRoleActions().map((action, index) => (
                    <div key={index} className="col-md-4 col-sm-6">
                      <Link 
                        to={action.path} 
                        className="btn btn-outline-success w-100 text-start"
                      >
                        <i className={`${action.icon} me-2`}></i>
                        {action.label}
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Permission Request */}
          <div className="card">
            <div className="card-header bg-light">
              <h5 className="mb-0">Need Access?</h5>
            </div>
            <div className="card-body">
              <p className="mb-3">
                If you believe you should have access to this page, please contact:
              </p>
              <div className="row">
                <div className="col-md-6 mb-3">
                  <div className="d-flex align-items-center">
                    <i className="bi bi-envelope text-primary me-3 fs-4"></i>
                    <div>
                      <strong>IT Support</strong>
                      <div>support@delvok.ac.ke</div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6 mb-3">
                  <div className="d-flex align-items-center">
                    <i className="bi bi-telephone text-primary me-3 fs-4"></i>
                    <div>
                      <strong>Help Desk</strong>
                      <div>+254 720 123 456</div>
                    </div>
                  </div>
                </div>
              </div>
              <button className="btn btn-outline-primary">
                <i className="bi bi-headset me-2"></i>
                Request Access
              </button>
            </div>
          </div>

          {/* Login Prompt for Non-Authenticated Users */}
          {!currentUser && (
            <div className="card mt-4">
              <div className="card-body">
                <h5 className="card-title">Not Logged In</h5>
                <p className="card-text">
                  You need to be logged in to access this page. Please sign in to continue.
                </p>
                <Link to="/login" className="btn btn-primary">
                  <i className="bi bi-box-arrow-in-right me-2"></i>
                  Login Now
                </Link>
              </div>
            </div>
          )}

          {/* Security Notice */}
          <div className="mt-4">
            <div className="alert alert-warning">
              <i className="bi bi-shield-check me-2"></i>
              <strong>Security Notice:</strong> Unauthorized access attempts are logged for security purposes.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Unauthorized;