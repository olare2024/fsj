import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function TransferStudents() {
  const [activeTab, setActiveTab] = useState('process');

  const transferInfo = {
    credits: [
      {
        subject: 'Mathematics',
        maxCredits: 8,
        requirements: 'C grade or better, equivalent course content'
      },
      {
        subject: 'Sciences',
        maxCredits: 8,
        requirements: 'Lab courses with C grade or better'
      },
      {
        subject: 'Humanities',
        maxCredits: 6,
        requirements: 'C grade or better, accredited institution'
      },
      {
        subject: 'Social Sciences',
        maxCredits: 6,
        requirements: 'C grade or better, accredited institution'
      },
      {
        subject: 'Electives',
        maxCredits: 12,
        requirements: 'Course-by-course evaluation'
      }
    ],
    deadlines: [
      { term: 'Fall Transfer', date: 'July 1', status: 'Open' },
      { term: 'Spring Transfer', date: 'December 1', status: 'Open' },
      { term: 'Summer Transfer', date: 'April 1', status: 'Open' }
    ],
    requirements: [
      'Minimum 2.5 GPA from current institution',
      'Good academic standing at previous school',
      'Official transcripts from all colleges attended',
      'High school transcript (if fewer than 24 college credits)',
      'Course descriptions/syllabi for credit evaluation'
    ]
  };

  const articulationAgreements = [
    {
      institution: 'City Community College',
      programs: ['Business Administration', 'Computer Science', 'Liberal Arts'],
      benefits: 'Guanteed admission, maximum credit transfer'
    },
    {
      institution: 'State Technical College',
      programs: ['Engineering Technology', 'Information Systems'],
      benefits: 'Seamless transfer pathways, scholarship opportunities'
    },
    {
      institution: 'Regional University',
      programs: ['All programs'],
      benefits: 'Dual admission program, academic advising'
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Transfer Students</h1>
          <p className="lead">Continue your educational journey at Delvok Academy</p>
        </div>
        <Link to="/admissions" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admissions
        </Link>
      </div>

      {/* Hero Section */}
      <div className="card bg-gradient-primary text-white mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="display-6 fw-bold">Welcome Transfer Students!</h2>
              <p className="lead mb-0">
                Your credits matter. We make transferring simple and maximize your previous coursework 
                toward your Delvok Academy degree.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-arrow-left-right display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>85%</h3>
              <p className="mb-0">Average Credit Transfer</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>200+</h3>
              <p className="mb-0">Transfer Students/Yr</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>95%</h3>
              <p className="mb-0">Graduation Rate</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>15</h3>
              <p className="mb-0">Partner Institutions</p>
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
                className={`nav-link ${activeTab === 'process' ? 'active' : ''}`}
                onClick={() => setActiveTab('process')}
              >
                <i className="bi bi-gear me-2"></i>
                Transfer Process
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'credits' ? 'active' : ''}`}
                onClick={() => setActiveTab('credits')}
              >
                <i className="bi bi-journal-check me-2"></i>
                Credit Transfer
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'agreements' ? 'active' : ''}`}
                onClick={() => setActiveTab('agreements')}
              >
                <i className="bi bi-handshake me-2"></i>
                Articulation Agreements
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'resources' ? 'active' : ''}`}
                onClick={() => setActiveTab('resources')}
              >
                <i className="bi bi-tools me-2"></i>
                Resources
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Transfer Process Tab */}
          {activeTab === 'process' && (
            <div>
              <h4>Transfer Admission Process</h4>
              <p className="text-muted mb-4">
                Follow these steps to successfully transfer to Delvok Academy.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="steps">
                    <div className="step">
                      <div className="step-number">1</div>
                      <div className="step-content">
                        <h5>Submit Application</h5>
                        <p>
                          Complete the online transfer application and pay the application fee. 
                          Make sure to indicate you're applying as a transfer student.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">2</div>
                      <div className="step-content">
                        <h5>Send Official Transcripts</h5>
                        <p>
                          Request official transcripts from all colleges and universities you've attended. 
                          If you have fewer than 24 college credits, include your high school transcript.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">3</div>
                      <div className="step-content">
                        <h5>Credit Evaluation</h5>
                        <p>
                          Our registrar's office will evaluate your transcripts and determine which 
                          credits will transfer toward your Delvok Academy degree.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">4</div>
                      <div className="step-content">
                        <h5>Receive Decision</h5>
                        <p>
                          You'll receive an admission decision within 2-4 weeks of submitting 
                          all required documents.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">5</div>
                      <div className="step-content">
                        <h5>Enroll & Register</h5>
                        <p>
                          Once accepted, complete enrollment paperwork and register for classes 
                          with your academic advisor.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-light">
                    <div className="card-header">
                      <h5 className="mb-0">Application Checklist</h5>
                    </div>
                    <div className="card-body">
                      <div className="form-check mb-3">
                        <input className="form-check-input" type="checkbox" id="check1" />
                        <label className="form-check-label" htmlFor="check1">
                          Completed online application
                        </label>
                      </div>
                      <div className="form-check mb-3">
                        <input className="form-check-input" type="checkbox" id="check2" />
                        <label className="form-check-label" htmlFor="check2">
                          Application fee payment
                        </label>
                      </div>
                      <div className="form-check mb-3">
                        <input className="form-check-input" type="checkbox" id="check3" />
                        <label className="form-check-label" htmlFor="check3">
                          Official college transcripts
                        </label>
                      </div>
                      <div className="form-check mb-3">
                        <input className="form-check-input" type="checkbox" id="check4" />
                        <label className="form-check-label" htmlFor="check4">
                          High school transcript (if applicable)
                        </label>
                      </div>
                      <div className="form-check">
                        <input className="form-check-input" type="checkbox" id="check5" />
                        <label className="form-check-label" htmlFor="check5">
                          Course descriptions/syllabi
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Credit Transfer Tab */}
          {activeTab === 'credits' && (
            <div>
              <h4>Credit Transfer Policies</h4>
              <p className="text-muted mb-4">
                Understand how your previous coursework will transfer to Delvok Academy.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="card mb-4">
                    <div className="card-header">
                      <h5 className="mb-0">Transfer Credit Limits by Subject</h5>
                    </div>
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table table-striped">
                          <thead>
                            <tr>
                              <th>Subject Area</th>
                              <th>Maximum Transfer Credits</th>
                              <th>Requirements</th>
                            </tr>
                          </thead>
                          <tbody>
                            {transferInfo.credits.map((subject, index) => (
                              <tr key={index}>
                                <td>
                                  <strong>{subject.subject}</strong>
                                </td>
                                <td>{subject.maxCredits} credits</td>
                                <td>
                                  <small>{subject.requirements}</small>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">General Transfer Policies</h5>
                    </div>
                    <div className="card-body">
                      <ul className="list-unstyled">
                        {transferInfo.requirements.map((requirement, index) => (
                          <li key={index} className="mb-3">
                            <i className="bi bi-check-circle text-success me-2"></i>
                            {requirement}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-primary text-white mb-4">
                    <div className="card-body text-center">
                      <h5>Transfer Credit Calculator</h5>
                      <p>
                        Estimate how your credits will transfer before you apply.
                      </p>
                      <button className="btn btn-light">
                        Use Calculator
                      </button>
                    </div>
                  </div>

                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Application Deadlines</h5>
                    </div>
                    <div className="card-body">
                      {transferInfo.deadlines.map((deadline, index) => (
                        <div key={index} className="d-flex justify-content-between align-items-center mb-3">
                          <div>
                            <strong>{deadline.term}</strong>
                            <div className="text-muted">Due: {deadline.date}</div>
                          </div>
                          <span className="badge bg-success">{deadline.status}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Articulation Agreements Tab */}
          {activeTab === 'agreements' && (
            <div>
              <h4>Articulation Agreements</h4>
              <p className="text-muted mb-4">
                We have formal transfer agreements with these institutions to ensure smooth credit transfer.
              </p>

              <div className="row g-4">
                {articulationAgreements.map((agreement, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{agreement.institution}</h5>
                      </div>
                      <div className="card-body">
                        <h6>Participating Programs:</h6>
                        <ul className="mb-3">
                          {agreement.programs.map((program, progIndex) => (
                            <li key={progIndex}>{program}</li>
                          ))}
                        </ul>
                        <h6>Benefits:</h6>
                        <p className="text-muted">{agreement.benefits}</p>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm">
                          View Agreement Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="alert alert-info mt-4">
                <h6><i className="bi bi-info-circle me-2"></i>Don't See Your School?</h6>
                <p className="mb-0">
                  We accept transfer credits from all regionally accredited institutions. 
                  Contact our transfer coordinator to discuss your specific situation.
                </p>
              </div>
            </div>
          )}

          {/* Resources Tab */}
          {activeTab === 'resources' && (
            <div>
              <h4>Transfer Student Resources</h4>
              <p className="text-muted mb-4">
                Tools and support to help you succeed in your transfer journey.
              </p>

              <div className="row">
                <div className="col-md-6">
                  <div className="card mb-4">
                    <div className="card-header">
                      <h5 className="mb-0">Academic Resources</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-calculator me-2"></i>
                          Credit Transfer Calculator
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-journal me-2"></i>
                          Course Equivalency Guide
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-person me-2"></i>
                          Meet with Transfer Advisor
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          <i className="bi bi-book me-2"></i>
                          Academic Planning Worksheet
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card mb-4">
                    <div className="card-header">
                      <h5 className="mb-0">Support Services</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-success text-start">
                          <i className="bi bi-people me-2"></i>
                          Transfer Student Orientation
                        </button>
                        <button className="btn btn-outline-success text-start">
                          <i className="bi bi-house me-2"></i>
                          Housing Assistance
                        </button>
                        <button className="btn btn-outline-success text-start">
                          <i className="bi bi-cash-coin me-2"></i>
                          Financial Aid Counseling
                        </button>
                        <button className="btn btn-outline-success text-start">
                          <i className="bi bi-briefcase me-2"></i>
                          Career Services
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0">Contact Transfer Office</h5>
                </div>
                <div className="card-body">
                  <div className="row">
                    <div className="col-md-4">
                      <div className="text-center">
                        <i className="bi bi-person-circle display-4 text-primary mb-3"></i>
                        <h6>Transfer Coordinator</h6>
                        <p className="text-muted">Sarah Johnson</p>
                        <button className="btn btn-primary btn-sm">
                          Schedule Appointment
                        </button>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="text-center">
                        <i className="bi bi-envelope display-4 text-success mb-3"></i>
                        <h6>Email</h6>
                        <p className="text-muted">transfer@delvok.edu</p>
                        <button className="btn btn-success btn-sm">
                          Send Email
                        </button>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="text-center">
                        <i className="bi bi-telephone display-4 text-info mb-3"></i>
                        <h6>Phone</h6>
                        <p className="text-muted">(555) 123-TRANS</p>
                        <button className="btn btn-info btn-sm">
                          Call Now
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .steps {
          position: relative;
          padding-left: 30px;
        }
        .step {
          position: relative;
          margin-bottom: 2rem;
        }
        .step-number {
          position: absolute;
          left: -30px;
          top: 0;
          width: 40px;
          height: 40px;
          background: var(--bs-primary);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
        }
        .step:not(:last-child):after {
          content: '';
          position: absolute;
          left: -11px;
          top: 40px;
          bottom: -2rem;
          width: 2px;
          background: var(--bs-primary);
          opacity: 0.3;
        }
      `}</style>
    </div>
  );
}

export default TransferStudents;