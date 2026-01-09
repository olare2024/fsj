import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Careers() {
  const [activeCategory, setActiveCategory] = useState('all');

  const jobCategories = [
    { id: 'all', name: 'All Positions', count: 8 },
    { id: 'teaching', name: 'Teaching', count: 5 },
    { id: 'administration', name: 'Administration', count: 2 },
    { id: 'support', name: 'Support Staff', count: 1 }
  ];

  const currentOpenings = [
    {
      id: 1,
      title: 'IGCSE Mathematics Teacher',
      department: 'High School - Cambridge Program',
      type: 'Full-time',
      category: 'teaching',
      location: 'Nairobi, Kenya',
      deadline: '2024-03-15',
      description: 'We are seeking an experienced IGCSE Mathematics teacher to join our Cambridge program team.',
      requirements: [
        'Bachelor of Education in Mathematics or related field',
        'Minimum 5 years teaching IGCSE Mathematics',
        'Cambridge International certification preferred',
        'Experience with diverse learning styles'
      ],
      responsibilities: [
        'Teach IGCSE Mathematics to Grades 9-11',
        'Develop engaging lesson plans and assessments',
        'Participate in curriculum development',
        'Provide academic support to students'
      ]
    },
    {
      id: 2,
      title: 'CBC Lower Primary Teacher',
      department: 'Elementary School - CBC Program',
      type: 'Full-time',
      category: 'teaching',
      location: 'Nairobi, Kenya',
      deadline: '2024-03-20',
      description: 'Join our elementary team to deliver the Kenyan CBC curriculum to Grade 1-3 students.',
      requirements: [
        'Diploma in Early Childhood Education',
        'Registered with Teachers Service Commission',
        'Minimum 3 years CBC teaching experience',
        'Strong understanding of competency-based assessment'
      ],
      responsibilities: [
        'Implement CBC curriculum for lower primary',
        'Create inclusive learning environment',
        'Assess student progress using CBC tools',
        'Collaborate with parents and staff'
      ]
    },
    {
      id: 3,
      title: 'Science Laboratory Technician',
      department: 'Science Department',
      type: 'Full-time',
      category: 'support',
      location: 'Nairobi, Kenya',
      deadline: '2024-03-10',
      description: 'Support our science department in maintaining laboratories and assisting with practical sessions.',
      requirements: [
        'Diploma in Laboratory Technology',
        'Experience in educational laboratory setting',
        'Knowledge of safety protocols',
        'Ability to maintain scientific equipment'
      ],
      responsibilities: [
        'Prepare laboratory materials for classes',
        'Maintain laboratory equipment',
        'Ensure safety standards are met',
        'Assist teachers during practical sessions'
      ]
    },
    {
      id: 4,
      title: 'Admissions Officer',
      department: 'Administration',
      type: 'Full-time',
      category: 'administration',
      location: 'Nairobi, Kenya',
      deadline: '2024-03-25',
      description: 'Join our admissions team to help families navigate the enrollment process.',
      requirements: [
        'Bachelor\'s degree in related field',
        'Experience in school admissions or customer service',
        'Excellent communication skills',
        'Knowledge of Kenyan and international curricula'
      ],
      responsibilities: [
        'Process student applications',
        'Conduct school tours and interviews',
        'Maintain applicant records',
        'Coordinate with academic departments'
      ]
    }
  ];

  const benefits = [
    {
      title: 'Competitive Salary',
      description: 'Attractive compensation package with performance bonuses',
      icon: 'bi-cash-coin'
    },
    {
      title: 'Professional Development',
      description: 'Continuous training and international certification opportunities',
      icon: 'bi-journal-bookmark'
    },
    {
      title: 'Health Insurance',
      description: 'Comprehensive medical coverage for you and your family',
      icon: 'bi-heart-pulse'
    },
    {
      title: 'Housing Allowance',
      description: 'Support for accommodation near the school campus',
      icon: 'bi-house'
    },
    {
      title: 'Children\'s Education',
      description: 'Tuition discount for staff children attending Delvok Academy',
      icon: 'bi-mortarboard'
    },
    {
      title: 'Retirement Plan',
      description: 'Pension scheme and retirement benefits',
      icon: 'bi-piggy-bank'
    }
  ];

  const filteredJobs = currentOpenings.filter(job => 
    activeCategory === 'all' || job.category === activeCategory
  );

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/about">About</Link></li>
              <li className="breadcrumb-item active">Careers</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Join Our Team</h1>
            <p className="lead mb-0">Build Your Career at Delvok Academy</p>
            <div className="mt-3">
              <span className="badge bg-success fs-6">{currentOpenings.length} Current Openings</span>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-primary text-white mb-5">
        <div className="card-body p-5 text-center">
          <h2 className="display-5 fw-bold mb-3">Shape the Future of Education</h2>
          <p className="fs-5 mb-4">
            At Delvok Academy, we're not just hiring employees - we're seeking passionate educators 
            and professionals who share our vision for dual-curriculum excellence and student success.
          </p>
          <button className="btn btn-light btn-lg">
            Why Work With Us?
          </button>
        </div>
      </div>

      {/* Job Categories */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <h5 className="mb-3">Browse Opportunities</h5>
              <div className="d-flex flex-wrap gap-3">
                {jobCategories.map(category => (
                  <button
                    key={category.id}
                    className={`btn ${activeCategory === category.id ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setActiveCategory(category.id)}
                  >
                    {category.name} <span className="badge bg-light text-dark ms-1">{category.count}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Current Openings */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Current Job Openings</h3>
          {filteredJobs.length === 0 ? (
            <div className="card">
              <div className="card-body text-center py-5">
                <i className="bi bi-briefcase display-1 text-muted"></i>
                <h4 className="mt-3">No openings in this category</h4>
                <p className="text-muted">
                  Check back later or browse all positions.
                </p>
                <button 
                  className="btn btn-primary"
                  onClick={() => setActiveCategory('all')}
                >
                  View All Positions
                </button>
              </div>
            </div>
          ) : (
            <div className="row g-4">
              {filteredJobs.map(job => (
                <div key={job.id} className="col-lg-6">
                  <div className="card h-100 job-listing">
                    <div className="card-header bg-light d-flex justify-content-between align-items-center">
                      <h5 className="mb-0">{job.title}</h5>
                      <span className="badge bg-primary">{job.type}</span>
                    </div>
                    <div className="card-body">
                      <div className="row mb-3">
                        <div className="col-md-6">
                          <strong>Department:</strong>
                          <div>{job.department}</div>
                        </div>
                        <div className="col-md-6">
                          <strong>Location:</strong>
                          <div>{job.location}</div>
                        </div>
                      </div>
                      
                      <p className="card-text">{job.description}</p>
                      
                      <h6>Key Requirements:</h6>
                      <ul className="small">
                        {job.requirements.slice(0, 3).map((req, idx) => (
                          <li key={idx}>{req}</li>
                        ))}
                      </ul>

                      <div className="application-deadline mt-3 p-3 bg-warning rounded">
                        <i className="bi bi-clock me-2"></i>
                        <strong>Application Deadline:</strong> {new Date(job.deadline).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="card-footer bg-transparent">
                      <div className="d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          Posted: {new Date().toLocaleDateString()}
                        </small>
                        <button 
                          className="btn btn-primary btn-sm"
                          data-bs-toggle="modal"
                          data-bs-target={`#jobModal${job.id}`}
                        >
                          View Details & Apply
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Job Modal */}
                  <div className="modal fade" id={`jobModal${job.id}`} tabIndex="-1">
                    <div className="modal-dialog modal-lg">
                      <div className="modal-content">
                        <div className="modal-header">
                          <h5 className="modal-title">{job.title}</h5>
                          <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div className="modal-body">
                          <div className="row mb-4">
                            <div className="col-md-6">
                              <strong>Department:</strong>
                              <div>{job.department}</div>
                            </div>
                            <div className="col-md-6">
                              <strong>Type:</strong>
                              <div>{job.type}</div>
                            </div>
                          </div>
                          
                          <h6>Job Description</h6>
                          <p>{job.description}</p>
                          
                          <h6>Responsibilities</h6>
                          <ul>
                            {job.responsibilities.map((resp, idx) => (
                              <li key={idx}>{resp}</li>
                            ))}
                          </ul>
                          
                          <h6>Requirements</h6>
                          <ul>
                            {job.requirements.map((req, idx) => (
                              <li key={idx}>{req}</li>
                            ))}
                          </ul>
                          
                          <div className="alert alert-info">
                            <strong>Application Deadline:</strong> {new Date(job.deadline).toLocaleDateString()}
                          </div>
                        </div>
                        <div className="modal-footer">
                          <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                          <button type="button" className="btn btn-primary">Apply Now</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Benefits Section */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Why Work at Delvok Academy?</h3>
          <div className="row g-4">
            {benefits.map((benefit, index) => (
              <div key={index} className="col-md-6 col-lg-4">
                <div className="card h-100 text-center border-0 shadow-sm">
                  <div className="card-body">
                    <i className={`${benefit.icon} display-4 text-primary mb-3`}></i>
                    <h5>{benefit.title}</h5>
                    <p className="card-text">{benefit.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Application Process */}
      <div className="row">
        <div className="col-lg-8 mx-auto">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h4 className="mb-0">Application Process</h4>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <h6>1. Submit Application</h6>
                  <p className="small">
                    Complete the online application form and upload your CV, cover letter, 
                    and relevant certificates.
                  </p>
                </div>
                <div className="col-md-6">
                  <h6>2. Initial Screening</h6>
                  <p className="small">
                    Our HR team reviews applications and contacts shortlisted candidates 
                    within 2 weeks.
                  </p>
                </div>
              </div>
              <div className="row mt-3">
                <div className="col-md-6">
                  <h6>3. Interviews & Demo Lessons</h6>
                  <p className="small">
                    Selected candidates participate in interviews and teaching demonstrations 
                    (for teaching positions).
                  </p>
                </div>
                <div className="col-md-6">
                  <h6>4. Final Selection</h6>
                  <p className="small">
                    Successful candidates receive offer letters and begin onboarding process.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contact HR */}
      <div className="row mt-5">
        <div className="col-12 text-center">
          <div className="card bg-light">
            <div className="card-body py-5">
              <h3 className="mb-3">Questions About Careers?</h3>
              <p className="fs-5 mb-4">
                Contact our Human Resources department for more information.
              </p>
              <div className="row justify-content-center">
                <div className="col-md-4">
                  <div className="mb-3">
                    <i className="bi bi-envelope text-primary me-2"></i>
                    careers@delvok.ac.ke
                  </div>
                  <div className="mb-3">
                    <i className="bi bi-telephone text-primary me-2"></i>
                    +254 720 123 456
                  </div>
                </div>
              </div>
              <button className="btn btn-primary btn-lg mt-3">
                Contact HR Department
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Careers;