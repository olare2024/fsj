import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function ParentResources() {
  const [activeTab, setActiveTab] = useState('academic');

  const resources = {
    academic: [
      {
        title: 'Academic Calendar 2024-2025',
        description: 'Complete school year calendar with holidays and important dates',
        type: 'pdf',
        size: '2.4 MB',
        downloadUrl: '#'
      },
      {
        title: 'Parent Guide to Student Success',
        description: 'Tips and strategies to support your child\'s learning at home',
        type: 'pdf',
        size: '1.8 MB',
        downloadUrl: '#'
      },
      {
        title: 'Curriculum Overview by Grade',
        description: 'Detailed breakdown of what students learn at each grade level',
        type: 'pdf',
        size: '3.1 MB',
        downloadUrl: '#'
      }
    ],
    support: [
      {
        title: 'Counseling Services Guide',
        description: 'Information about school counseling and mental health support',
        type: 'pdf',
        size: '1.2 MB',
        downloadUrl: '#'
      },
      {
        title: 'Parent-Teacher Conference Tips',
        description: 'How to prepare for and make the most of parent-teacher meetings',
        type: 'pdf',
        size: '0.9 MB',
        downloadUrl: '#'
      },
      {
        title: 'Homework Help Resources',
        description: 'Online tools and local tutoring options for homework assistance',
        type: 'pdf',
        size: '1.5 MB',
        downloadUrl: '#'
      }
    ],
    forms: [
      {
        title: 'Student Medical Form',
        description: 'Required health and medical information form',
        type: 'doc',
        size: '0.5 MB',
        downloadUrl: '#'
      },
      {
        title: 'Field Trip Permission Slip',
        description: 'Standard permission form for school field trips',
        type: 'doc',
        size: '0.3 MB',
        downloadUrl: '#'
      },
      {
        title: 'Volunteer Application',
        description: 'Apply to volunteer for school events and activities',
        type: 'doc',
        size: '0.7 MB',
        downloadUrl: '#'
      }
    ]
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Parent Resources</h1>
          <p className="lead">Tools and information to support your child's education</p>
        </div>
        <Link to="/resources" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Resources
        </Link>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>24/7</h3>
              <p className="mb-0">Access</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>50+</h3>
              <p className="mb-0">Resources</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>15</h3>
              <p className="mb-0">Downloadable Forms</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>100%</h3>
              <p className="mb-0">Free Access</p>
            </div>
          </div>
        </div>
      </div>

      {/* Resource Tabs */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'academic' ? 'active' : ''}`}
                onClick={() => setActiveTab('academic')}
              >
                <i className="bi bi-journal me-2"></i>
                Academic Resources
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'support' ? 'active' : ''}`}
                onClick={() => setActiveTab('support')}
              >
                <i className="bi bi-heart me-2"></i>
                Support Services
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'forms' ? 'active' : ''}`}
                onClick={() => setActiveTab('forms')}
              >
                <i className="bi bi-file-earmark me-2"></i>
                Forms & Documents
              </button>
            </li>
          </ul>
        </div>
        <div className="card-body">
          <div className="row g-4">
            {resources[activeTab].map((resource, index) => (
              <div key={index} className="col-md-6 col-lg-4">
                <div className="card h-100 shadow-sm">
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <span className={`badge bg-${resource.type === 'pdf' ? 'danger' : 'primary'}`}>
                        {resource.type.toUpperCase()}
                      </span>
                      <small className="text-muted">{resource.size}</small>
                    </div>
                    <h5 className="card-title">{resource.title}</h5>
                    <p className="card-text text-muted">{resource.description}</p>
                  </div>
                  <div className="card-footer">
                    <div className="d-flex gap-2">
                      <button className="btn btn-primary btn-sm">
                        <i className="bi bi-download me-1"></i>
                        Download
                      </button>
                      <button className="btn btn-outline-secondary btn-sm">
                        <i className="bi bi-eye me-1"></i>
                        Preview
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Additional Help Section */}
      <div className="row mt-5">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Need Additional Help?</h5>
            </div>
            <div className="card-body">
              <div className="row g-4">
                <div className="col-md-6">
                  <div className="d-flex">
                    <i className="bi bi-telephone text-primary fs-4 me-3"></i>
                    <div>
                      <h6>Parent Helpline</h6>
                      <p className="mb-1">(555) 123-4567</p>
                      <small className="text-muted">Mon-Fri, 8AM-4PM</small>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex">
                    <i className="bi bi-envelope text-primary fs-4 me-3"></i>
                    <div>
                      <h6>Email Support</h6>
                      <p className="mb-1">parents@delvok.edu</p>
                      <small className="text-muted">24/7 Response</small>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex">
                    <i className="bi bi-calendar-check text-primary fs-4 me-3"></i>
                    <div>
                      <h6>Schedule Meeting</h6>
                      <p className="mb-1">Meet with Counselors</p>
                      <small className="text-muted">By Appointment</small>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex">
                    <i className="bi bi-people text-primary fs-4 me-3"></i>
                    <div>
                      <h6>Parent Workshops</h6>
                      <p className="mb-1">Monthly Sessions</p>
                      <small className="text-muted">Check Calendar</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-lg-4">
          <div className="card bg-light">
            <div className="card-body text-center">
              <i className="bi bi-megaphone display-4 text-primary mb-3"></i>
              <h5>Stay Connected</h5>
              <p className="text-muted">
                Join our parent newsletter for updates, events, and important announcements.
              </p>
              <div className="input-group mb-3">
                <input
                  type="email"
                  className="form-control"
                  placeholder="Your email address"
                />
                <button className="btn btn-primary">Subscribe</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParentResources;