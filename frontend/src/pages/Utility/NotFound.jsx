import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function NotFound() {
  const location = useLocation();

  const quickLinks = [
    { path: '/', label: 'Home', icon: 'bi-house' },
    { path: '/academics', label: 'Academics', icon: 'bi-journal-bookmark' },
    { path: '/admissions', label: 'Admissions', icon: 'bi-person-plus' },
    { path: '/campus-life', label: 'Campus Life', icon: 'bi-people' },
    { path: '/contact', label: 'Contact', icon: 'bi-telephone' }
  ];

  const popularPages = [
    { path: '/apply', label: 'Apply Now' },
    { path: '/tuition', label: 'Tuition & Fees' },
    { path: '/calendar', label: 'Academic Calendar' },
    { path: '/faculty-directory', label: 'Faculty Directory' },
    { path: '/student-handbook', label: 'Student Handbook' },
    { path: '/safety', label: 'Campus Safety' }
  ];

  return (
    <div className="container-fluid py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8 text-center">
          {/* Error Code */}
          <div className="display-1 fw-bold text-primary mb-3">404</div>
          
          {/* Error Icon */}
          <div className="mb-4">
            <i className="bi bi-exclamation-triangle display-1 text-warning"></i>
          </div>

          {/* Error Message */}
          <h1 className="display-5 fw-bold text-dark mb-3">Page Not Found</h1>
          <p className="fs-5 text-muted mb-4">
            The page you're looking for doesn't exist or has been moved.
          </p>

          {/* Current Path */}
          <div className="alert alert-info mb-4">
            <i className="bi bi-info-circle me-2"></i>
            You tried to access: <code>{location.pathname}</code>
          </div>

          {/* Primary Action */}
          <div className="mb-5">
            <Link to="/" className="btn btn-primary btn-lg me-3">
              <i className="bi bi-house me-2"></i>
              Go Home
            </Link>
            <button 
              className="btn btn-outline-primary btn-lg"
              onClick={() => window.history.back()}
            >
              <i className="bi bi-arrow-left me-2"></i>
              Go Back
            </button>
          </div>

          {/* Quick Links */}
          <div className="card mb-4">
            <div className="card-header bg-light">
              <h5 className="mb-0">Quick Navigation</h5>
            </div>
            <div className="card-body">
              <div className="row g-3">
                {quickLinks.map((link, index) => (
                  <div key={index} className="col-md-4 col-sm-6">
                    <Link 
                      to={link.path} 
                      className="btn btn-outline-secondary w-100 text-start"
                    >
                      <i className={`${link.icon} me-2`}></i>
                      {link.label}
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Popular Pages */}
          <div className="card">
            <div className="card-header bg-light">
              <h5 className="mb-0">Popular Pages</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {popularPages.map((page, index) => (
                  <div key={index} className="col-md-6 mb-2">
                    <Link 
                      to={page.path} 
                      className="text-decoration-none"
                    >
                      <i className="bi bi-arrow-right-short text-primary me-2"></i>
                      {page.label}
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Search Suggestion */}
          <div className="mt-5">
            <p className="text-muted mb-3">Can't find what you're looking for?</p>
            <div className="row justify-content-center">
              <div className="col-md-6">
                <div className="input-group">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search our website..."
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        window.location.href = `/search?q=${e.target.value}`;
                      }
                    }}
                  />
                  <Link 
                    to="/search" 
                    className="btn btn-primary"
                  >
                    <i className="bi bi-search"></i>
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Support */}
          <div className="mt-4">
            <p className="text-muted">
              Still need help?{' '}
              <Link to="/contact" className="text-primary text-decoration-none">
                Contact our support team
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Decorative Elements */}
      <style jsx>{`
        .display-1 {
          font-size: 8rem;
          background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        @media (max-width: 768px) {
          .display-1 {
            font-size: 5rem;
          }
        }
      `}</style>
    </div>
  );
}

export default NotFound;