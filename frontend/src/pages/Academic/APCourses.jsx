import React from 'react';
import { Link } from 'react-router-dom';

function APCourses() {
  const apCourses = [
    {
      subject: 'AP Calculus AB/BC',
      description: 'College-level calculus covering limits, derivatives, integrals, and series',
      prerequisites: 'Advanced Mathematics IGCSE Grade A/B',
      exam: 'May 2024',
      benefits: ['College credit', 'STEM preparation', 'Enhanced problem-solving skills']
    },
    {
      subject: 'AP Biology',
      description: 'In-depth study of biological concepts including biochemistry, genetics, and ecology',
      prerequisites: 'IGCSE Biology Grade A/B',
      exam: 'May 2024',
      benefits: ['Laboratory skills', 'Medical school preparation', 'Research foundation']
    },
    {
      subject: 'AP Chemistry',
      description: 'Comprehensive chemistry course with emphasis on laboratory work and analysis',
      prerequisites: 'IGCSE Chemistry Grade A/B',
      exam: 'May 2024',
      benefits: ['Engineering preparation', 'Research methodology', 'Analytical skills']
    },
    {
      subject: 'AP Physics 1 & 2',
      description: 'Algebra-based physics covering mechanics, electricity, waves, and modern physics',
      prerequisites: 'IGCSE Physics Grade A/B',
      exam: 'May 2024',
      benefits: ['Engineering foundation', 'Problem-solving', 'Scientific reasoning']
    },
    {
      subject: 'AP Computer Science A',
      description: 'Object-oriented programming and problem solving using Java',
      prerequisites: 'IGCSE Computer Science or programming experience',
      exam: 'May 2024',
      benefits: ['Coding skills', 'Software development', 'Algorithm design']
    },
    {
      subject: 'AP English Literature',
      description: 'Advanced literary analysis and critical reading of diverse texts',
      prerequisites: 'IGCSE First Language English Grade A/B',
      exam: 'May 2024',
      benefits: ['Critical thinking', 'Communication skills', 'Cultural awareness']
    }
  ];

  const benefits = [
    {
      title: 'College Credit',
      description: 'Earn college credits while in high school',
      icon: 'bi-cash-coin'
    },
    {
      title: 'University Admission',
      description: 'Strengthen university applications',
      icon: 'bi-trophy'
    },
    {
      title: 'Academic Rigor',
      description: 'Experience college-level coursework',
      icon: 'bi-graph-up'
    },
    {
      title: 'Cost Savings',
      description: 'Reduce college tuition costs',
      icon: 'bi-piggy-bank'
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/academics">Academics</Link></li>
              <li className="breadcrumb-item active">Advanced Placement</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-info">Advanced Placement Program</h1>
              <p className="lead mb-0">College-Level Courses for High School Students</p>
            </div>
            <div className="badge bg-info fs-6">
              College Board Certified
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-info text-white mb-5">
        <div className="card-body p-5">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="fw-bold mb-3">Get a Head Start on College</h2>
              <p className="fs-5 mb-4">
                Delvok Academy is proud to offer Advanced Placement (AP) courses that allow 
                motivated students to pursue college-level studies while still in high school. 
                Our AP program prepares students for success in higher education and beyond.
              </p>
              <div className="d-flex gap-3">
                <button className="btn btn-light btn-lg text-info">
                  Apply for AP Program
                </button>
                <button className="btn btn-outline-light btn-lg">
                  View Course Catalog
                </button>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-award display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* AP Courses Grid */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Available AP Courses</h3>
          <div className="row g-4">
            {apCourses.map((course, index) => (
              <div key={index} className="col-lg-6">
                <div className="card h-100 border-info">
                  <div className="card-header bg-info text-white d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">{course.subject}</h5>
                    <span className="badge bg-light text-info">Exam: {course.exam}</span>
                  </div>
                  <div className="card-body">
                    <p className="card-text">{course.description}</p>
                    
                    <div className="row mt-4">
                      <div className="col-md-6">
                        <h6>Prerequisites:</h6>
                        <p className="small">{course.prerequisites}</p>
                      </div>
                      <div className="col-md-6">
                        <h6>Benefits:</h6>
                        <ul className="small">
                          {course.benefits.map((benefit, idx) => (
                            <li key={idx}>{benefit}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                  <div className="card-footer bg-transparent">
                    <div className="d-flex justify-content-between align-items-center">
                      <small className="text-muted">College Board Approved</small>
                      <button className="btn btn-outline-info btn-sm">
                        Course Details
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Why Take AP Courses?</h3>
          <div className="row g-4">
            {benefits.map((benefit, index) => (
              <div key={index} className="col-md-6 col-lg-3">
                <div className="card h-100 text-center border-info">
                  <div className="card-body">
                    <i className={`${benefit.icon} display-4 text-info mb-3`}></i>
                    <h5>{benefit.title}</h5>
                    <p className="card-text">{benefit.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="row">
        {/* AP Exam Information */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-info text-white">
              <h5 className="mb-0">AP Exam Information</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Exam Dates:</strong>
                <div>May 2024 (Two-week period)</div>
              </div>
              <div className="mb-3">
                <strong>Registration Deadline:</strong>
                <div>November 15, 2023</div>
              </div>
              <div className="mb-3">
                <strong>Exam Fees:</strong>
                <div>$96 per exam (Financial aid available)</div>
              </div>
              <div className="mb-3">
                <strong>Score Reporting:</strong>
                <div>Results available in July 2024</div>
              </div>
              <button className="btn btn-outline-info btn-sm w-100">
                Exam Registration
              </button>
            </div>
          </div>
        </div>

        {/* Success Stories */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Student Success Stories</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Sarah M.</strong>
                <div className="small text-muted">AP Calculus BC Score: 5</div>
                <p className="small mb-0">"The AP program prepared me perfectly for my engineering degree at MIT."</p>
              </div>
              <div className="mb-3">
                <strong>David K.</strong>
                <div className="small text-muted">AP Biology Score: 5</div>
                <p className="small mb-0">"Earning college credit through AP saved me a full semester of tuition."</p>
              </div>
              <div className="mb-3">
                <strong>Grace W.</strong>
                <div className="small text-muted">AP Computer Science Score: 5</div>
                <p className="small mb-0">"The programming skills I gained helped me secure a summer internship at Google."</p>
              </div>
              <button className="btn btn-outline-info btn-sm w-100">
                More Success Stories
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default APCourses;