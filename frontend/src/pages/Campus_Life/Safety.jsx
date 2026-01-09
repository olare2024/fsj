import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Safety() {
  const [activeTab, setActiveTab] = useState('security');

  const securityServices = [
    {
      service: '24/7 Patrol',
      description: 'Campus security officers patrol all areas 24 hours a day',
      icon: 'bi-shield-check',
      contact: 'Emergency: (555) 911-CAMPUS'
    },
    {
      service: 'Emergency Phones',
      description: 'Blue light emergency phones located throughout campus',
      icon: 'bi-telephone',
      contact: 'Direct connection to security'
    },
    {
      service: 'Security Escorts',
      description: 'Walking escorts available any time of day or night',
      icon: 'bi-person-walking',
      contact: 'Call: (555) 123-ESCORT'
    },
    {
      service: 'Vehicle Assistance',
      description: 'Jump starts, lockouts, and tire changes',
      icon: 'bi-truck',
      contact: 'Call: (555) 456-ROADS'
    }
  ];

  const emergencyProcedures = [
    {
      emergency: 'Medical Emergency',
      steps: [
        'Call Campus Emergency: (555) 911-CAMPUS',
        'Provide exact location and nature of emergency',
        'Stay with the person if safe',
        'Follow dispatcher instructions'
      ],
      icon: 'bi-heart-pulse'
    },
    {
      emergency: 'Fire Emergency',
      steps: [
        'Activate nearest fire alarm',
        'Evacuate building immediately',
        'Call Campus Emergency',
        'Assemble at designated safe area'
      ],
      icon: 'bi-fire'
    },
    {
      emergency: 'Severe Weather',
      steps: [
        'Seek shelter in basement or interior room',
        'Stay away from windows',
        'Monitor emergency alerts',
        'Wait for all-clear signal'
      ],
      icon: 'bi-cloud-lightning-rain'
    },
    {
      emergency: 'Security Threat',
      steps: [
        'Run - Hide - Fight (in that order)',
        'Lock and barricade doors',
        'Silence phones',
        'Call emergency when safe'
      ],
      icon: 'bi-shield-exclamation'
    }
  ];

  const safetyResources = [
    {
      resource: 'Campus Safety App',
      description: 'Emergency alerts, safety tools, and resources',
      features: ['Emergency button', 'Friend walk', 'Safety map', 'Alert notifications'],
      download: 'Available on App Store and Google Play'
    },
    {
      resource: 'Self-Defense Classes',
      description: 'Free classes taught by certified instructors',
      schedule: 'Weekly sessions, various times',
      location: 'Campus Recreation Center',
      registration: 'Required - limited spots'
    },
    {
      resource: 'Safety Workshops',
      description: 'Educational sessions on various safety topics',
      topics: ['Personal safety', 'Cybersecurity', 'Travel safety', 'Dorm security'],
      schedule: 'Monthly workshops'
    }
  ];

  const crimePrevention = [
    {
      area: 'Personal Safety',
      tips: [
        'Be aware of your surroundings',
        'Walk in well-lit areas at night',
        'Use the buddy system',
        'Trust your instincts'
      ]
    },
    {
      area: 'Dorm Security',
      tips: [
        'Always lock your door',
        'Don\'t prop exterior doors open',
        'Report suspicious activity',
        'Know emergency exits'
      ]
    },
    {
      area: 'Property Protection',
      tips: [
        'Engrave valuable items',
        'Use quality locks',
        'Don\'t leave belongings unattended',
        'Register bikes and electronics'
      ]
    }
  ];

  // Enhanced training data
  const safetyTraining = [
    {
      title: 'Active Shooter Response',
      duration: '2 hours',
      frequency: 'Monthly',
      audience: 'All campus members',
      description: 'Learn Run-Hide-Fight principles and survival strategies'
    },
    {
      title: 'First Aid & CPR',
      duration: '4 hours',
      frequency: 'Quarterly',
      audience: 'Students, Faculty, Staff',
      description: 'Certified training in emergency first response'
    },
    {
      title: 'Emergency Preparedness',
      duration: '3 hours',
      frequency: 'Semesterly',
      audience: 'All campus members',
      description: 'Comprehensive disaster response training'
    },
    {
      title: 'Cybersecurity Awareness',
      duration: '1.5 hours',
      frequency: 'Monthly',
      audience: 'Students, Faculty, Staff',
      description: 'Protecting personal and institutional data'
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Campus Safety & Security</h1>
          <p className="lead">Your safety is our top priority - comprehensive protection for our campus community</p>
        </div>
        <Link to="/campus-life" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Campus Life
        </Link>
      </div>

      {/* Emergency Banner */}
      <div className="alert alert-danger mb-4">
        <div className="d-flex align-items-center">
          <i className="bi bi-exclamation-triangle display-6 me-3"></i>
          <div>
            <h5 className="alert-heading mb-1">Emergency Contact</h5>
            <p className="mb-0">
              For immediate assistance, call <strong>Campus Emergency: (555) 911-CAMPUS</strong> 
              or dial <strong>911</strong> for life-threatening situations.
            </p>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-primary text-white mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="display-6 fw-bold">Safe Campus Community</h2>
              <p className="lead mb-0">
                We're committed to maintaining a secure environment through proactive measures, 
                rapid response, and comprehensive safety education.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-shield-check display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>24/7</h3>
              <p className="mb-0">Security Monitoring</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>50+</h3>
              <p className="mb-0">Emergency Phones</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3> 2min </h3>
              <p className="mb-0">Average Response Time</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-secondary text-white">
            <div className="card-body text-center">
              <h3>100%</h3>
              <p className="mb-0">Trained Staff</p>
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
                className={`nav-link ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                <i className="bi bi-shield-check me-2"></i>
                Security Services
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'emergency' ? 'active' : ''}`}
                onClick={() => setActiveTab('emergency')}
              >
                <i className="bi bi-exclamation-triangle me-2"></i>
                Emergency Procedures
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'resources' ? 'active' : ''}`}
                onClick={() => setActiveTab('resources')}
              >
                <i className="bi bi-tools me-2"></i>
                Safety Resources
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'prevention' ? 'active' : ''}`}
                onClick={() => setActiveTab('prevention')}
              >
                <i className="bi bi-lightbulb me-2"></i>
                Crime Prevention
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Security Services Tab */}
          {activeTab === 'security' && (
            <div>
              <h4>Security Services</h4>
              <p className="text-muted mb-4">
                Comprehensive security measures to protect our campus community.
              </p>

              <div className="row g-4">
                {securityServices.map((service, index) => (
                  <div key={index} className="col-md-6 col-lg-3">
                    <div className="card h-100 text-center">
                      <div className="card-body">
                        <i className={`${service.icon} display-4 text-primary mb-3`}></i>
                        <h5>{service.service}</h5>
                        <p className="card-text">{service.description}</p>
                        <div className="contact-info">
                          <strong>{service.contact}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Security Technology</h5>
                    </div>
                    <div className="card-body">
                      <ul>
                        <li>500+ security cameras campus-wide</li>
                        <li>Electronic access control on all buildings</li>
                        <li>Automated emergency notification system</li>
                        <li>License plate recognition at entrances</li>
                        <li>Panic buttons in offices and classrooms</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Security Office</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-flex mb-3">
                        <i className="bi bi-geo-alt text-primary me-3"></i>
                        <div>
                          <strong>Location</strong>
                          <div>Building A, Room 101</div>
                        </div>
                      </div>
                      <div className="d-flex mb-3">
                        <i className="bi bi-clock text-primary me-3"></i>
                        <div>
                          <strong>Office Hours</strong>
                          <div>24/7 Operations Center</div>
                        </div>
                      </div>
                      <div className="d-flex">
                        <i className="bi bi-person text-primary me-3"></i>
                        <div>
                          <strong>Security Director</strong>
                          <div>Chief Michael Rodriguez</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Emergency Procedures Tab */}
          {activeTab === 'emergency' && (
            <div>
              <h4>Emergency Procedures</h4>
              <p className="text-muted mb-4">
                Know what to do in case of an emergency on campus.
              </p>

              <div className="row g-4">
                {emergencyProcedures.map((procedure, index) => (
                  <div key={index} className="col-lg-6">
                    <div className="card h-100">
                      <div className="card-header d-flex align-items-center">
                        <i className={`${procedure.icon} text-danger me-3 fs-4`}></i>
                        <h5 className="mb-0">{procedure.emergency}</h5>
                      </div>
                      <div className="card-body">
                        <ol>
                          {procedure.steps.map((step, stepIndex) => (
                            <li key={stepIndex} className="mb-2">{step}</li>
                          ))}
                        </ol>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="bi bi-megaphone display-4 text-warning mb-3"></i>
                      <h5>Emergency Alert System</h5>
                      <p>
                        Ensure you're signed up to receive emergency alerts via text, email, and app notifications.
                      </p>
                      <button className="btn btn-warning">
                        Update Alert Preferences
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Emergency Assembly Areas</h5>
                    </div>
                    <div className="card-body">
                      <ul>
                        <li><strong>North Campus:</strong> Library Plaza</li>
                        <li><strong>South Campus:</strong> Student Center Lawn</li>
                        <li><strong>East Campus:</strong> Sports Field</li>
                        <li><strong>West Campus:</strong> Dining Hall Parking Lot</li>
                      </ul>
                      <button className="btn btn-outline-primary">
                        View Emergency Map
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Safety Resources Tab */}
          {activeTab === 'resources' && (
            <div>
              <h4>Safety Resources</h4>
              <p className="text-muted mb-4">
                Tools and programs to enhance personal safety and security awareness.
              </p>

              <div className="row g-4">
                {safetyResources.map((resource, index) => (
                  <div key={index} className="col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{resource.resource}</h5>
                      </div>
                      <div className="card-body">
                        <p className="card-text">{resource.description}</p>
                        
                        {resource.features && (
                          <>
                            <h6>Features:</h6>
                            <ul className="small">
                              {resource.features.map((feature, idx) => (
                                <li key={idx}>{feature}</li>
                              ))}
                            </ul>
                          </>
                        )}

                        {resource.download && (
                          <div className="mt-3">
                            <strong>Download:</strong>
                            <div>{resource.download}</div>
                          </div>
                        )}

                        {resource.schedule && (
                          <div className="mt-2">
                            <strong>Schedule:</strong>
                            <div>{resource.schedule}</div>
                          </div>
                        )}

                        {resource.registration && (
                          <div className="mt-2">
                            <strong>Registration:</strong>
                            <div>{resource.registration}</div>
                          </div>
                        )}
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm">
                          Learn More
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-4">
                <div className="col-md-12">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Safety Training Programs</h5>
                    </div>
                    <div className="card-body">
                      <div className="row">
                        {safetyTraining.map((training, index) => (
                          <div key={index} className="col-md-6 col-lg-3 mb-3">
                            <div className="card h-100">
                              <div className="card-body">
                                <h6 className="card-title">{training.title}</h6>
                                <p className="card-text small">{training.description}</p>
                                <div className="small text-muted">
                                  <div><strong>Duration:</strong> {training.duration}</div>
                                  <div><strong>Frequency:</strong> {training.frequency}</div>
                                  <div><strong>Audience:</strong> {training.audience}</div>
                                </div>
                              </div>
                              <div className="card-footer">
                                <button className="btn btn-outline-primary btn-sm w-100">
                                  Register
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Safety Equipment Loan Program</h5>
                    </div>
                    <div className="card-body">
                      <p>Free safety equipment available for checkout:</p>
                      <ul>
                        <li>Personal safety alarms</li>
                        <li>Flashlights and reflective gear</li>
                        <li>First aid kits</li>
                        <li>Bike lights and helmets</li>
                      </ul>
                      <button className="btn btn-outline-primary">
                        Browse Equipment
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Safety Resource Center</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-flex mb-3">
                        <i className="bi bi-geo-alt text-primary me-3"></i>
                        <div>
                          <strong>Location</strong>
                          <div>Student Union, Room 205</div>
                        </div>
                      </div>
                      <div className="d-flex mb-3">
                        <i className="bi bi-clock text-primary me-3"></i>
                        <div>
                          <strong>Hours</strong>
                          <div>Mon-Fri: 9AM-5PM</div>
                        </div>
                      </div>
                      <div className="d-flex">
                        <i className="bi bi-telephone text-primary me-3"></i>
                        <div>
                          <strong>Contact</strong>
                          <div>(555) 789-SAFE</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Crime Prevention Tab */}
          {activeTab === 'prevention' && (
            <div>
              <h4>Crime Prevention</h4>
              <p className="text-muted mb-4">
                Proactive measures to help prevent crime and enhance personal safety.
              </p>

              <div className="row g-4">
                {crimePrevention.map((category, index) => (
                  <div key={index} className="col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{category.area}</h5>
                      </div>
                      <div className="card-body">
                        <ul className="list-unstyled">
                          {category.tips.map((tip, tipIndex) => (
                            <li key={tipIndex} className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              {tip}
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
                  <div className="card bg-light">
                    <div className="card-body">
                      <h5>Property Registration</h5>
                      <p>Register your valuable items with campus security for enhanced protection and recovery:</p>
                      <ul>
                        <li>Laptops and electronics</li>
                        <li>Bicycles</li>
                        <li>Mobile devices</li>
                        <li>Other valuable items</li>
                      </ul>
                      <button className="btn btn-primary">
                        Register Property
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Security Assessments</h5>
                    </div>
                    <div className="card-body">
                      <p>Request a free security assessment for your living or workspace:</p>
                      <ul>
                        <li>Dorm room security review</li>
                        <li>Office safety assessment</li>
                        <li>Personal safety consultation</li>
                        <li>Travel safety planning</li>
                      </ul>
                      <button className="btn btn-outline-primary">
                        Request Assessment
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="row mt-4">
                <div className="col-12">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">See Something, Say Something</h5>
                    </div>
                    <div className="card-body">
                      <div className="row">
                        <div className="col-md-8">
                          <p>
                            Report suspicious activity immediately. Your vigilance helps keep our campus safe.
                          </p>
                          <div className="row">
                            <div className="col-md-6">
                              <div className="d-flex align-items-center mb-3">
                                <i className="bi bi-telephone text-danger me-3 fs-4"></i>
                                <div>
                                  <strong>Emergency</strong>
                                  <div>(555) 911-CAMPUS</div>
                                </div>
                              </div>
                            </div>
                            <div className="col-md-6">
                              <div className="d-flex align-items-center mb-3">
                                <i className="bi bi-chat-text text-primary me-3 fs-4"></i>
                                <div>
                                  <strong>Anonymous Tip Line</strong>
                                  <div>(555) 789-TIPS</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="col-md-4 text-center">
                          <i className="bi bi-eye display-4 text-primary opacity-50"></i>
                        </div>
                      </div>
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

export default Safety;