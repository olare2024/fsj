import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function ApplicationStatus() {
  const [applicationId, setApplicationId] = useState('');
  const [lastName, setLastName] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock application data
  const mockApplication = {
    id: 'APP-2024-00123',
    studentName: 'John Smith',
    program: '9th Grade - Regular Admission',
    submittedDate: '2024-01-15',
    status: 'under-review',
    currentStep: 'Document Review',
    nextStep: 'Admission Decision',
    estimatedCompletion: '2024-02-15',
    checklist: [
      { item: 'Application Form', status: 'completed', date: '2024-01-15' },
      { item: 'Transcripts', status: 'completed', date: '2024-01-18' },
      { item: 'Recommendation Letters', status: 'received', date: '2024-01-20' },
      { item: 'Entrance Exam', status: 'scheduled', date: '2024-02-01' },
      { item: 'Interview', status: 'pending', date: 'TBD' },
      { item: 'Final Decision', status: 'pending', date: 'TBD' }
    ],
    contact: {
      advisor: 'Sarah Johnson',
      email: 'admissions@delvok.edu',
      phone: '(555) 123-ADMIT'
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (!applicationId || !lastName) {
      alert('Please enter both Application ID and Last Name');
      return;
    }

    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setSearchResults(mockApplication);
      setIsLoading(false);
    }, 1500);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'submitted': return { class: 'bg-secondary', text: 'Submitted' };
      case 'under-review': return { class: 'bg-warning', text: 'Under Review' };
      case 'documents-requested': return { class: 'bg-info', text: 'Documents Requested' };
      case 'interview-scheduled': return { class: 'bg-primary', text: 'Interview Scheduled' };
      case 'accepted': return { class: 'bg-success', text: 'Accepted' };
      case 'waitlisted': return { class: 'bg-info', text: 'Waitlisted' };
      case 'rejected': return { class: 'bg-danger', text: 'Not Accepted' };
      default: return { class: 'bg-secondary', text: status };
    }
  };

  const getChecklistStatusIcon = (status) => {
    switch (status) {
      case 'completed': return 'bi-check-circle-fill text-success';
      case 'received': return 'bi-check-circle text-success';
      case 'scheduled': return 'bi-calendar-check text-primary';
      case 'pending': return 'bi-clock text-warning';
      case 'missing': return 'bi-exclamation-circle text-danger';
      default: return 'bi-question-circle text-secondary';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Application Status</h1>
          <p className="lead">Check the status of your admission application</p>
        </div>
        <Link to="/admissions" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admissions
        </Link>
      </div>

      {/* Search Section */}
      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Find Your Application</h5>
          <p className="text-muted">
            Enter your Application ID and Last Name to check your application status.
          </p>
          
          <form onSubmit={handleSearch}>
            <div className="row g-3">
              <div className="col-md-6">
                <label htmlFor="applicationId" className="form-label">Application ID</label>
                <input
                  type="text"
                  className="form-control"
                  id="applicationId"
                  placeholder="e.g., APP-2024-00123"
                  value={applicationId}
                  onChange={(e) => setApplicationId(e.target.value)}
                  required
                />
                <div className="form-text">
                  You received this ID when you submitted your application
                </div>
              </div>
              <div className="col-md-6">
                <label htmlFor="lastName" className="form-label">Student's Last Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="lastName"
                  placeholder="Enter last name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="mt-3">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Searching...
                  </>
                ) : (
                  <>
                    <i className="bi bi-search me-2"></i>
                    Check Status
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Application Status Display */}
      {searchResults && (
        <div className="application-details">
          {/* Application Header */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="row align-items-center">
                <div className="col-md-8">
                  <h4 className="card-title">{searchResults.studentName}</h4>
                  <p className="card-text text-muted">
                    Application ID: <strong>{searchResults.id}</strong> • 
                    Program: <strong>{searchResults.program}</strong> • 
                    Submitted: <strong>{searchResults.submittedDate}</strong>
                  </p>
                </div>
                <div className="col-md-4 text-end">
                  {(() => {
                    const statusBadge = getStatusBadge(searchResults.status);
                    return (
                      <span className={`badge ${statusBadge.class} fs-6`}>
                        {statusBadge.text}
                      </span>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>

          <div className="row">
            {/* Left Column - Progress and Checklist */}
            <div className="col-lg-8">
              {/* Progress Bar */}
              <div className="card mb-4">
                <div className="card-header">
                  <h5 className="mb-0">Application Progress</h5>
                </div>
                <div className="card-body">
                  <div className="progress mb-3" style={{height: '20px'}}>
                    <div 
                      className="progress-bar" 
                      style={{width: '60%'}}
                      role="progressbar"
                    >
                      60% Complete
                    </div>
                  </div>
                  <div className="row text-center">
                    <div className="col">
                      <small className="text-muted">Current Step</small>
                      <div className="fw-bold">{searchResults.currentStep}</div>
                    </div>
                    <div className="col">
                      <small className="text-muted">Next Step</small>
                      <div className="fw-bold">{searchResults.nextStep}</div>
                    </div>
                    <div className="col">
                      <small className="text-muted">Est. Completion</small>
                      <div className="fw-bold">{searchResults.estimatedCompletion}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Checklist */}
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0">Application Checklist</h5>
                </div>
                <div className="card-body">
                  <div className="list-group list-group-flush">
                    {searchResults.checklist.map((item, index) => (
                      <div key={index} className="list-group-item d-flex justify-content-between align-items-center">
                        <div className="d-flex align-items-center">
                          <i className={`bi ${getChecklistStatusIcon(item.status)} me-3 fs-5`}></i>
                          <div>
                            <h6 className="mb-1">{item.item}</h6>
                            {item.date && (
                              <small className="text-muted">Completed: {item.date}</small>
                            )}
                          </div>
                        </div>
                        <span className={`badge ${
                          item.status === 'completed' ? 'bg-success' :
                          item.status === 'received' ? 'bg-success' :
                          item.status === 'scheduled' ? 'bg-primary' :
                          item.status === 'pending' ? 'bg-warning' :
                          'bg-danger'
                        }`}>
                          {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Contact and Next Steps */}
            <div className="col-lg-4">
              {/* Contact Information */}
              <div className="card mb-4">
                <div className="card-header">
                  <h5 className="mb-0">Admissions Contact</h5>
                </div>
                <div className="card-body">
                  <div className="d-flex align-items-start mb-3">
                    <i className="bi bi-person text-primary me-3 fs-4"></i>
                    <div>
                      <strong>Admissions Advisor</strong>
                      <div>{searchResults.contact.advisor}</div>
                    </div>
                  </div>
                  <div className="d-flex align-items-start mb-3">
                    <i className="bi bi-envelope text-primary me-3 fs-4"></i>
                    <div>
                      <strong>Email</strong>
                      <div>{searchResults.contact.email}</div>
                    </div>
                  </div>
                  <div className="d-flex align-items-start">
                    <i className="bi bi-telephone text-primary me-3 fs-4"></i>
                    <div>
                      <strong>Phone</strong>
                      <div>{searchResults.contact.phone}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Next Steps */}
              <div className="card mb-4">
                <div className="card-header">
                  <h5 className="mb-0">Next Steps</h5>
                </div>
                <div className="card-body">
                  <div className="alert alert-info">
                    <h6><i className="bi bi-info-circle me-2"></i>What to Expect</h6>
                    <p className="small mb-0">
                      Your application is currently under review. You will be notified via email 
                      when there are updates or if additional information is needed.
                    </p>
                  </div>
                  <div className="d-grid gap-2">
                    <button className="btn btn-outline-primary">
                      <i className="bi bi-question-circle me-2"></i>
                      Ask a Question
                    </button>
                    <button className="btn btn-outline-success">
                      <i className="bi bi-upload me-2"></i>
                      Upload Additional Documents
                    </button>
                  </div>
                </div>
              </div>

              {/* Important Dates */}
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0">Important Dates</h5>
                </div>
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <small>Application Submitted</small>
                    <small className="text-muted">{searchResults.submittedDate}</small>
                  </div>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <small>Decision Date</small>
                    <small className="text-muted">{searchResults.estimatedCompletion}</small>
                  </div>
                  <div className="d-flex justify-content-between align-items-center">
                    <small>Enrollment Deadline</small>
                    <small className="text-muted">2 weeks after acceptance</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="card mt-4">
            <div className="card-header">
              <h5 className="mb-0">Frequently Asked Questions</h5>
            </div>
            <div className="card-body">
              <div className="accordion" id="applicationFAQ">
                <div className="accordion-item">
                  <h2 className="accordion-header">
                    <button className="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                      How long does the application review take?
                    </button>
                  </h2>
                  <div id="faq1" className="accordion-collapse collapse show" data-bs-parent="#applicationFAQ">
                    <div className="accordion-body">
                      The review process typically takes 2-4 weeks after all required documents are received. 
                      During peak periods, it may take slightly longer.
                    </div>
                  </div>
                </div>
                <div className="accordion-item">
                  <h2 className="accordion-header">
                    <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                      Can I update my application after submission?
                    </button>
                  </h2>
                  <div id="faq2" className="accordion-collapse collapse" data-bs-parent="#applicationFAQ">
                    <div className="accordion-body">
                      Yes, you can upload additional documents or request minor updates by contacting 
                      the admissions office. Major changes may require a new application.
                    </div>
                  </div>
                </div>
                <div className="accordion-item">
                  <h2 className="accordion-header">
                    <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                      What if I miss a deadline?
                    </button>
                  </h2>
                  <div id="faq3" className="accordion-collapse collapse" data-bs-parent="#applicationFAQ">
                    <div className="accordion-body">
                      Contact the admissions office immediately. While we cannot guarantee consideration 
                      for late applications, we review them on a case-by-case basis when space is available.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* No Results State */}
      {!searchResults && !isLoading && (
        <div className="card">
          <div className="card-body text-center py-5">
            <i className="bi bi-search display-1 text-muted mb-3"></i>
            <h4>Check Your Application Status</h4>
            <p className="text-muted">
              Enter your Application ID and Last Name above to view your application progress, 
              checklist items, and estimated decision date.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ApplicationStatus;