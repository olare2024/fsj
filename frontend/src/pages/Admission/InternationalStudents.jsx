import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function InternationalStudents() {
  const [activeSection, setActiveSection] = useState('overview');

  const requirements = [
    {
      category: 'Academic Requirements',
      items: [
        'Official transcripts from previous schools (translated to English)',
        'Minimum GPA equivalent to 3.0 on 4.0 scale',
        'Proof of English proficiency (TOEFL/IELTS)',
        'Standardized test scores (SAT/ACT if applicable)'
      ]
    },
    {
      category: 'Documentation',
      items: [
        'Valid passport copy',
        'Student visa documentation',
        'Financial support verification',
        'Health insurance proof',
        'Immunization records'
      ]
    },
    {
      category: 'Additional Materials',
      items: [
        'Personal statement or essay',
        'Letters of recommendation',
        'Portfolio (for arts programs)',
        'Interview (may be required)'
      ]
    }
  ];

  const supportServices = [
    {
      title: 'Visa Assistance',
      description: 'Help with student visa application process and documentation',
      icon: 'bi-passport'
    },
    {
      title: 'Housing Support',
      description: 'Assistance with on-campus housing or homestay arrangements',
      icon: 'bi-house'
    },
    {
      title: 'Orientation Program',
      description: 'Comprehensive orientation for international students',
      icon: 'bi-compass'
    },
    {
      title: 'Academic Support',
      description: 'ESL classes and academic tutoring available',
      icon: 'bi-journal'
    },
    {
      title: 'Cultural Integration',
      description: 'Activities and programs to help you adjust',
      icon: 'bi-people'
    },
    {
      title: 'Health Services',
      description: 'On-campus health center and insurance guidance',
      icon: 'bi-heart'
    }
  ];

  const deadlines = [
    { term: 'Fall Semester', date: 'April 1', type: 'Priority' },
    { term: 'Fall Semester', date: 'June 1', type: 'Final' },
    { term: 'Spring Semester', date: 'October 1', type: 'Priority' },
    { term: 'Spring Semester', date: 'December 1', type: 'Final' }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>International Students</h1>
          <p className="lead">Join our global community from anywhere in the world</p>
        </div>
        <Link to="/admissions" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admissions
        </Link>
      </div>

      {/* Hero Section */}
      <div className="card bg-primary text-white mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="display-6 fw-bold">Welcome Global Students!</h2>
              <p className="lead mb-0">
                Delvok Academy welcomes students from over 40 countries. Our international community 
                thrives on diversity and cultural exchange.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-globe display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="card mb-4">
        <div className="card-header">
          <ul className="nav nav-pills card-header-pills">
            <li className="nav-item">
              <button
                className={`nav-link ${activeSection === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveSection('overview')}
              >
                <i className="bi bi-info-circle me-2"></i>
                Overview
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeSection === 'requirements' ? 'active' : ''}`}
                onClick={() => setActiveSection('requirements')}
              >
                <i className="bi bi-list-check me-2"></i>
                Requirements
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeSection === 'support' ? 'active' : ''}`}
                onClick={() => setActiveSection('support')}
              >
                <i className="bi bi-heart me-2"></i>
                Support Services
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeSection === 'deadlines' ? 'active' : ''}`}
                onClick={() => setActiveSection('deadlines')}
              >
                <i className="bi bi-calendar me-2"></i>
                Deadlines
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Overview Section */}
          {activeSection === 'overview' && (
            <div>
              <div className="row">
                <div className="col-lg-8">
                  <h4>Why Choose Delvok Academy?</h4>
                  <p>
                    At Delvok Academy, we celebrate diversity and provide a welcoming environment 
                    for international students. Our dedicated International Student Office ensures 
                    your transition is smooth and successful.
                  </p>
                  
                  <div className="row mt-4">
                    <div className="col-md-6">
                      <div className="d-flex mb-3">
                        <i className="bi bi-translate text-primary fs-4 me-3"></i>
                        <div>
                          <h6>English Language Support</h6>
                          <p className="text-muted mb-0">
                            ESL programs and language tutoring available
                          </p>
                        </div>
                      </div>
                      <div className="d-flex mb-3">
                        <i className="bi bi-house-check text-primary fs-4 me-3"></i>
                        <div>
                          <h6>Housing Guarantee</h6>
                          <p className="text-muted mb-0">
                            On-campus housing guaranteed for international students
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="d-flex mb-3">
                        <i className="bi bi-currency-exchange text-primary fs-4 me-3"></i>
                        <div>
                          <h6>Financial Aid</h6>
                          <p className="text-muted mb-0">
                            Merit-based scholarships for international students
                          </p>
                        </div>
                      </div>
                      <div className="d-flex mb-3">
                        <i className="bi bi-briefcase text-primary fs-4 me-3"></i>
                        <div>
                          <h6>Career Support</h6>
                          <p className="text-muted mb-0">
                            Internship opportunities and career counseling
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <h5>Quick Facts</h5>
                      <div className="row text-center mt-4">
                        <div className="col-6">
                          <h3 className="text-primary">40+</h3>
                          <small>Countries Represented</small>
                        </div>
                        <div className="col-6">
                          <h3 className="text-primary">15%</h3>
                          <small>International Students</small>
                        </div>
                      </div>
                      <div className="row text-center mt-3">
                        <div className="col-6">
                          <h3 className="text-primary">98%</h3>
                          <small>Visa Success Rate</small>
                        </div>
                        <div className="col-6">
                          <h3 className="text-primary">24/7</h3>
                          <small>Student Support</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Requirements Section */}
          {activeSection === 'requirements' && (
            <div>
              <h4>Admission Requirements for International Students</h4>
              <p className="text-muted mb-4">
                Please ensure you meet all requirements before applying. Contact our international 
                admissions office if you have any questions.
              </p>

              <div className="row">
                {requirements.map((category, index) => (
                  <div key={index} className="col-md-6 col-lg-4 mb-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h6 className="mb-0">{category.category}</h6>
                      </div>
                      <div className="card-body">
                        <ul className="list-unstyled mb-0">
                          {category.items.map((item, itemIndex) => (
                            <li key={itemIndex} className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="alert alert-info mt-4">
                <h6><i className="bi bi-info-circle me-2"></i>Important Note</h6>
                <p className="mb-0">
                  All documents not in English must be accompanied by certified translations. 
                  Additional requirements may apply for specific programs.
                </p>
              </div>
            </div>
          )}

          {/* Support Services Section */}
          {activeSection === 'support' && (
            <div>
              <h4>International Student Support Services</h4>
              <p className="text-muted mb-4">
                We provide comprehensive support to ensure your success at Delvok Academy.
              </p>

              <div className="row g-4">
                {supportServices.map((service, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100 text-center">
                      <div className="card-body">
                        <i className={`${service.icon} display-4 text-primary mb-3`}></i>
                        <h5>{service.title}</h5>
                        <p className="text-muted">{service.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-5">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Contact International Office</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-flex mb-3">
                        <i className="bi bi-envelope text-primary me-3"></i>
                        <div>
                          <strong>Email</strong>
                          <div>international@delvok.edu</div>
                        </div>
                      </div>
                      <div className="d-flex mb-3">
                        <i className="bi bi-telephone text-primary me-3"></i>
                        <div>
                          <strong>Phone</strong>
                          <div>+1 (555) 123-4567</div>
                        </div>
                      </div>
                      <div className="d-flex">
                        <i className="bi bi-clock text-primary me-3"></i>
                        <div>
                          <strong>Office Hours</strong>
                          <div>Mon-Fri: 8:00 AM - 6:00 PM EST</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Emergency Contact</h5>
                    </div>
                    <div className="card-body">
                      <div className="alert alert-warning">
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        For urgent matters outside office hours
                      </div>
                      <div className="d-flex align-items-center">
                        <i className="bi bi-phone text-danger fs-4 me-3"></i>
                        <div>
                          <strong>24/7 Emergency Line</strong>
                          <div className="h5 mb-0">+1 (555) 911-INTL</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Deadlines Section */}
          {activeSection === 'deadlines' && (
            <div>
              <h4>Application Deadlines</h4>
              <p className="text-muted mb-4">
                Apply early to allow sufficient time for visa processing and travel arrangements.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="card">
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table table-striped">
                          <thead>
                            <tr>
                              <th>Academic Term</th>
                              <th>Deadline</th>
                              <th>Type</th>
                              <th>Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {deadlines.map((deadline, index) => (
                              <tr key={index}>
                                <td>
                                  <strong>{deadline.term}</strong>
                                </td>
                                <td>{deadline.date}</td>
                                <td>
                                  <span className={`badge ${
                                    deadline.type === 'Priority' ? 'bg-warning' : 'bg-primary'
                                  }`}>
                                    {deadline.type}
                                  </span>
                                </td>
                                <td>
                                  <span className="badge bg-success">Open</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="alert alert-info mt-4">
                    <h6><i className="bi bi-lightbulb me-2"></i>Application Tips</h6>
                    <ul className="mb-0">
                      <li>Start your visa application process immediately after acceptance</li>
                      <li>Submit financial documents early to avoid delays</li>
                      <li>Consider time needed for document translation and certification</li>
                    </ul>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-primary text-white">
                    <div className="card-body text-center">
                      <h5>Ready to Apply?</h5>
                      <p>
                        Begin your journey at Delvok Academy today. Our international admissions 
                        team is here to help you every step of the way.
                      </p>
                      <div className="d-grid gap-2">
                        <Link to="/apply" className="btn btn-light">
                          Start Application
                        </Link>
                        <button className="btn btn-outline-light">
                          Request Information
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-body">
                      <h6>Visa Processing Times</h6>
                      <div className="mt-3">
                        <div className="d-flex justify-content-between mb-2">
                          <small>F-1 Student Visa</small>
                          <small>60-90 days</small>
                        </div>
                        <div className="progress mb-3">
                          <div className="progress-bar" style={{width: '75%'}}></div>
                        </div>
                        
                        <div className="d-flex justify-content-between mb-2">
                          <small>Document Processing</small>
                          <small>2-4 weeks</small>
                        </div>
                        <div className="progress">
                          <div className="progress-bar" style={{width: '50%'}}></div>
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

export default InternationalStudents;