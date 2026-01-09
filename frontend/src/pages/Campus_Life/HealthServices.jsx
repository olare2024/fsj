import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function HealthServices() {
  const [activeTab, setActiveTab] = useState('services');

  const healthServices = [
    {
      name: 'Primary Care',
      description: 'Routine medical care, physical exams, and health maintenance',
      icon: 'bi-heart-pulse',
      hours: 'Mon-Fri: 8:00 AM - 6:00 PM',
      cost: 'Free for students'
    },
    {
      name: 'Mental Health Counseling',
      description: 'Individual and group therapy sessions with licensed counselors',
      icon: 'bi-chat-dots',
      hours: 'Mon-Fri: 9:00 AM - 7:00 PM',
      cost: 'Free for students'
    },
    {
      name: 'Wellness Programs',
      description: 'Health education, stress management, and wellness workshops',
      icon: 'bi-flower1',
      hours: 'Various times',
      cost: 'Free for students'
    },
    {
      name: 'Immunizations',
      description: 'Vaccinations and immunization records management',
      icon: 'bi-shield-check',
      hours: 'Mon-Fri: 9:00 AM - 4:00 PM',
      cost: 'Low cost or free'
    },
    {
      name: 'Sports Medicine',
      description: 'Athletic injury evaluation and rehabilitation',
      icon: 'bi-person-running',
      hours: 'Mon-Fri: 10:00 AM - 5:00 PM',
      cost: 'Free for student athletes'
    },
    {
      name: 'Laboratory Services',
      description: 'Basic lab tests and blood work',
      icon: 'bi-droplet',
      hours: 'Mon-Fri: 8:00 AM - 4:00 PM',
      cost: 'Low cost'
    }
  ];

  const emergencyContacts = [
    {
      name: 'Campus Emergency',
      number: '(555) 911-CAMPUS',
      description: '24/7 campus security and emergency response'
    },
    {
      name: 'Health Center After Hours',
      number: '(555) 123-HEALTH',
      description: 'After-hours medical advice line'
    },
    {
      name: 'Crisis Counseling',
      number: '(555) 456-HOPE',
      description: '24/7 mental health crisis support'
    },
    {
      name: 'Local Hospital',
      number: '(555) 789-EMERG',
      description: 'City General Hospital emergency room'
    }
  ];

  const wellnessResources = [
    {
      category: 'Physical Health',
      resources: [
        'Fitness center access',
        'Nutrition counseling',
        'Sleep health workshops',
        'Substance abuse education'
      ]
    },
    {
      category: 'Mental Health',
      resources: [
        'Stress management workshops',
        'Mindfulness meditation sessions',
        'Support groups',
        'Crisis intervention'
      ]
    },
    {
      category: 'Preventive Care',
      resources: [
        'Annual health screenings',
        'Vaccination clinics',
        'Health risk assessments',
        'Wellness challenges'
      ]
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Health & Wellness Services</h1>
          <p className="lead">Comprehensive healthcare and wellness support for student success</p>
        </div>
        <Link to="/campus-life" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Campus Life
        </Link>
      </div>

      {/* Hero Section */}
      <div className="card bg-info text-white mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="display-6 fw-bold">Your Health Comes First</h2>
              <p className="lead mb-0">
                Our comprehensive health services support your physical and mental well-being, 
                ensuring you can focus on your academic and personal growth.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-heart-pulse display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Emergency Banner */}
      <div className="alert alert-danger mb-4">
        <div className="d-flex align-items-center">
          <i className="bi bi-exclamation-triangle display-6 me-3"></i>
          <div>
            <h5 className="alert-heading mb-1">Medical Emergency?</h5>
            <p className="mb-0">
              For life-threatening emergencies, call <strong>Campus Emergency: (555) 911-CAMPUS</strong> 
              or dial <strong>911</strong> immediately.
            </p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>24/7</h3>
              <p className="mb-0">Emergency Support</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>100%</h3>
              <p className="mb-0">Free Basic Services</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>10+</h3>
              <p className="mb-0">Healthcare Providers</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-secondary text-white">
            <div className="card-body text-center">
              <h3>95%</h3>
              <p className="mb-0">Student Satisfaction</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Tabs */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'services' ? 'active' : ''}`}
                onClick={() => setActiveTab('services')}
              >
                <i className="bi bi-heart me-2"></i>
                Health Services
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'appointments' ? 'active' : ''}`}
                onClick={() => setActiveTab('appointments')}
              >
                <i className="bi bi-calendar me-2"></i>
                Make Appointment
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'wellness' ? 'active' : ''}`}
                onClick={() => setActiveTab('wellness')}
              >
                <i className="bi bi-flower1 me-2"></i>
                Wellness Resources
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'emergency' ? 'active' : ''}`}
                onClick={() => setActiveTab('emergency')}
              >
                <i className="bi bi-telephone me-2"></i>
                Emergency Contacts
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Health Services Tab */}
          {activeTab === 'services' && (
            <div>
              <h4>Our Health Services</h4>
              <p className="text-muted mb-4">
                Comprehensive medical and mental health services tailored to student needs.
              </p>

              <div className="row g-4">
                {healthServices.map((service, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-body text-center">
                        <i className={`${service.icon} display-4 text-primary mb-3`}></i>
                        <h5>{service.name}</h5>
                        <p className="card-text">{service.description}</p>
                        
                        <div className="service-details">
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Hours:</strong>
                            <span>{service.hours}</span>
                          </div>
                          <div className="d-flex justify-content-between">
                            <strong>Cost:</strong>
                            <span className="text-success">{service.cost}</span>
                          </div>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm w-100">
                          Learn More
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Health Insurance</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        All students are required to have health insurance coverage. We offer 
                        an affordable student health insurance plan.
                      </p>
                      <ul>
                        <li>Comprehensive coverage</li>
                        <li>Low student rates</li>
                        <li>On-campus provider network</li>
                        <li>Easy enrollment process</li>
                      </ul>
                      <button className="btn btn-primary">
                        View Insurance Options
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Patient Portal</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Access your health records, communicate with providers, and manage 
                        appointments through our secure patient portal.
                      </p>
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-primary">
                          Login to Portal
                        </button>
                        <button className="btn btn-outline-secondary">
                          Request Medical Records
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Make Appointment Tab */}
          {activeTab === 'appointments' && (
            <div>
              <h4>Schedule an Appointment</h4>
              <p className="text-muted mb-4">
                Book your appointment online or contact our health center directly.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Book Online</h5>
                    </div>
                    <div className="card-body">
                      <form>
                        <div className="row mb-3">
                          <div className="col-md-6">
                            <label className="form-label">Service Type</label>
                            <select className="form-select" required>
                              <option value="">Select service...</option>
                              <option value="primary-care">Primary Care</option>
                              <option value="mental-health">Mental Health Counseling</option>
                              <option value="immunizations">Immunizations</option>
                              <option value="sports-medicine">Sports Medicine</option>
                              <option value="lab-work">Laboratory Services</option>
                            </select>
                          </div>
                          <div className="col-md-6">
                            <label className="form-label">Preferred Provider</label>
                            <select className="form-select">
                              <option value="">Any available provider</option>
                              <option value="dr-smith">Dr. Smith (Primary Care)</option>
                              <option value="dr-johnson">Dr. Johnson (Mental Health)</option>
                              <option value="dr-chen">Dr. Chen (Sports Medicine)</option>
                            </select>
                          </div>
                        </div>

                        <div className="row mb-3">
                          <div className="col-md-6">
                            <label className="form-label">Preferred Date</label>
                            <input type="date" className="form-control" required />
                          </div>
                          <div className="col-md-6">
                            <label className="form-label">Preferred Time</label>
                            <select className="form-select" required>
                              <option value="">Select time...</option>
                              <option value="morning">Morning (8:00 AM - 12:00 PM)</option>
                              <option value="afternoon">Afternoon (12:00 PM - 5:00 PM)</option>
                              <option value="evening">Evening (5:00 PM - 7:00 PM)</option>
                            </select>
                          </div>
                        </div>

                        <div className="mb-3">
                          <label className="form-label">Reason for Visit</label>
                          <textarea 
                            className="form-control" 
                            rows="3" 
                            placeholder="Briefly describe the reason for your appointment..."
                            required
                          ></textarea>
                        </div>

                        <button type="submit" className="btn btn-primary">
                          Check Availability
                        </button>
                      </form>
                    </div>
                  </div>

                  <div className="alert alert-info mt-4">
                    <h6><i className="bi bi-info-circle me-2"></i>Appointment Information</h6>
                    <ul className="mb-0">
                      <li>Same-day appointments available for urgent concerns</li>
                      <li>Please arrive 15 minutes early for paperwork</li>
                      <li>Bring your student ID and insurance card</li>
                      <li>Cancellations require 24-hour notice</li>
                    </ul>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="bi bi-telephone display-4 text-primary mb-3"></i>
                      <h5>Call to Schedule</h5>
                      <p className="text-muted">
                        Prefer to schedule by phone?
                      </p>
                      <div className="h4 text-primary">(555) 123-HEALTH</div>
                      <small className="text-muted">Mon-Fri: 8:00 AM - 6:00 PM</small>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h5 className="mb-0">Walk-In Hours</h5>
                    </div>
                    <div className="card-body">
                      <div className="mb-3">
                        <strong>Primary Care:</strong>
                        <div>Mon-Fri: 1:00 PM - 3:00 PM</div>
                      </div>
                      <div className="mb-3">
                        <strong>Immunizations:</strong>
                        <div>Wed & Fri: 9:00 AM - 11:00 AM</div>
                      </div>
                      <div>
                        <strong>Mental Health:</strong>
                        <div>Urgent walk-ins: Daily 2:00 PM - 4:00 PM</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Wellness Resources Tab */}
          {activeTab === 'wellness' && (
            <div>
              <h4>Wellness & Prevention</h4>
              <p className="text-muted mb-4">
                Resources and programs to support your overall well-being and preventive health.
              </p>

              <div className="row g-4">
                {wellnessResources.map((category, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{category.category}</h5>
                      </div>
                      <div className="card-body">
                        <ul className="list-unstyled">
                          {category.resources.map((resource, idx) => (
                            <li key={idx} className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              {resource}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Upcoming Wellness Events</h5>
                    </div>
                    <div className="card-body">
                      <div className="list-group list-group-flush">
                        <div className="list-group-item d-flex justify-content-between align-items-center">
                          <div>
                            <h6 className="mb-1">Stress Management Workshop</h6>
                            <small className="text-muted">Feb 15, 3:00 PM - Health Center</small>
                          </div>
                          <button className="btn btn-sm btn-outline-primary">Register</button>
                        </div>
                        <div className="list-group-item d-flex justify-content-between align-items-center">
                          <div>
                            <h6 className="mb-1">Nutrition Cooking Demo</h6>
                            <small className="text-muted">Feb 18, 5:00 PM - Commons Kitchen</small>
                          </div>
                          <button className="btn btn-sm btn-outline-primary">Register</button>
                        </div>
                        <div className="list-group-item d-flex justify-content-between align-items-center">
                          <div>
                            <h6 className="mb-1">Sleep Health Seminar</h6>
                            <small className="text-muted">Feb 22, 4:00 PM - Library Auditorium</small>
                          </div>
                          <button className="btn btn-sm btn-outline-primary">Register</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Wellness Resources</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-download me-2"></i>
                          Wellness App Download
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-journal me-2"></i>
                          Self-Care Guides
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-phone me-2"></i>
                          Mental Health Apps
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-people me-2"></i>
                          Support Groups
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Emergency Contacts Tab */}
          {activeTab === 'emergency' && (
            <div>
              <h4>Emergency Contacts & Resources</h4>
              <p className="text-muted mb-4">
                Important contact information for emergencies and urgent health concerns.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Emergency Contacts</h5>
                    </div>
                    <div className="card-body">
                      <div className="row g-4">
                        {emergencyContacts.map((contact, index) => (
                          <div key={index} className="col-md-6">
                            <div className="card h-100 border-primary">
                              <div className="card-body text-center">
                                <h5 className="text-primary">{contact.name}</h5>
                                <div className="h4 text-danger">{contact.number}</div>
                                <p className="text-muted">{contact.description}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h5 className="mb-0">Emergency Procedures</h5>
                    </div>
                    <div className="card-body">
                      <h6>Medical Emergency:</h6>
                      <ol>
                        <li>Call Campus Emergency: (555) 911-CAMPUS</li>
                        <li>Provide your location and nature of emergency</li>
                        <li>Stay with the person if safe to do so</li>
                        <li>Follow dispatcher instructions</li>
                      </ol>

                      <h6>Mental Health Crisis:</h6>
                      <ol>
                        <li>Call Crisis Counseling: (555) 456-HOPE</li>
                        <li>Go to the Health Center during business hours</li>
                        <li>Contact your Resident Advisor after hours</li>
                        <li>Never leave someone in crisis alone</li>
                      </ol>
                    </div>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-danger text-white">
                    <div className="card-body text-center">
                      <i className="bi bi-exclamation-triangle display-4 mb-3"></i>
                      <h5>Emergency Alert System</h5>
                      <p>
                        Ensure you're signed up for our emergency alert system to receive 
                        immediate notifications about campus emergencies.
                      </p>
                      <button className="btn btn-light">
                        Update Alert Preferences
                      </button>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h5 className="mb-0">After-Hours Care</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        For non-emergency medical concerns after hours:
                      </p>
                      <ul className="small">
                        <li>Call Health Center After Hours line</li>
                        <li>Use telehealth services through patient portal</li>
                        <li>Visit urgent care centers (list available)</li>
                        <li>For emergencies, always call 911 first</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default HealthServices;