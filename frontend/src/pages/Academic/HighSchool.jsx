import React from 'react';
import { Link } from 'react-router-dom';

function HighSchool() {
  const pathways = [
    {
      track: 'Kenyan CBC - Junior Secondary',
      grades: 'Grade 7-9',
      description: 'Comprehensive Kenyan curriculum with pathway specialization',
      subjects: [
        'Core: English, Kiswahili, Mathematics, Integrated Science, Social Studies, Pre-Technical Studies, Life Skills, Sports',
        'Optional: Agriculture, Home Science, Computer Studies, Performing Arts, Visual Arts, Business Studies, Foreign Languages'
      ],
      examination: 'Grade 9 CBC Summative Assessment'
    },
    {
      track: 'Cambridge Lower Secondary',
      grades: 'Grade 7-8',
      description: 'International curriculum preparing for IGCSE',
      subjects: [
        'Core: English, Mathematics, Science',
        'Options: Global Perspectives, ICT, Art & Design, Physical Education, Music, Foreign Languages'
      ],
      examination: 'Cambridge Lower Secondary Checkpoint'
    },
    {
      track: 'Cambridge IGCSE',
      grades: 'Grade 9-10',
      description: 'Internationally recognized qualification for O-Level',
      subjects: [
        'Compulsory: English, Mathematics, Combined Science',
        'Electives: 4-6 subjects from Sciences, Humanities, Languages, Creative Arts'
      ],
      examination: 'Cambridge IGCSE Examinations'
    }
  ];

  const facilities = [
    {
      name: 'Science Laboratories',
      description: 'Fully equipped labs for Physics, Chemistry, and Biology',
      icon: 'bi-biotech'
    },
    {
      name: 'Computer Labs',
      description: 'Modern computer labs with programming and design software',
      icon: 'bi-pc-display'
    },
    {
      name: 'Library & Resource Center',
      description: 'Extensive collection of books and digital resources',
      icon: 'bi-book'
    },
    {
      name: 'Sports Complex',
      description: 'Olympic-size pool, football pitch, basketball courts',
      icon: 'bi-trophy'
    }
  ];

  const universityPreparation = [
    {
      program: 'Career Counseling',
      description: 'Individualized guidance for university and career choices'
    },
    {
      program: 'University Visits',
      description: 'Regular visits from international and local universities'
    },
    {
      program: 'SAT/ACT Preparation',
      description: 'Test preparation for US university admissions'
    },
    {
      program: 'Application Support',
      description: 'Assistance with university applications worldwide'
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
              <li className="breadcrumb-item active">High School</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-danger">High School</h1>
              <p className="lead mb-0">Grade 7 to Grade 12 - Preparing for Global Opportunities</p>
            </div>
            <div className="badge bg-danger fs-6">
              Ages 13-18 Years
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-danger text-white mb-5">
        <div className="card-body p-5">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="fw-bold mb-3">Excellence in Secondary Education</h2>
              <p className="fs-5 mb-4">
                Delvok Academy High School offers dual pathways through Kenyan CBC Junior Secondary 
                and Cambridge IGCSE programs. Our students graduate prepared for both local and 
                international universities with globally recognized qualifications.
              </p>
              <div className="d-flex gap-3">
                <button className="btn btn-light btn-lg text-danger">
                  View Academic Programs
                </button>
                <button className="btn btn-outline-light btn-lg">
                  Download Prospectus
                </button>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-mortarboard-fill display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Academic Pathways */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Academic Pathways</h3>
          <div className="row g-4">
            {pathways.map((pathway, index) => (
              <div key={index} className="col-lg-4">
                <div className="card h-100 border-danger">
                  <div className="card-header bg-danger text-white">
                    <h5 className="mb-0">{pathway.track}</h5>
                    <small>{pathway.grades}</small>
                  </div>
                  <div className="card-body">
                    <p className="card-text">{pathway.description}</p>
                    
                    <h6 className="mt-4">Subjects Offered:</h6>
                    <ul className="small">
                      {pathway.subjects.map((subject, idx) => (
                        <li key={idx}>{subject}</li>
                      ))}
                    </ul>

                    <div className="mt-4 p-3 bg-light rounded">
                      <strong>Final Examination:</strong>
                      <div>{pathway.examination}</div>
                    </div>
                  </div>
                  <div className="card-footer bg-transparent">
                    <button className="btn btn-outline-danger btn-sm">
                      Detailed Syllabus
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Facilities */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">World-Class Facilities</h3>
          <div className="row g-4">
            {facilities.map((facility, index) => (
              <div key={index} className="col-md-6 col-lg-3">
                <div className="card h-100 text-center">
                  <div className="card-body">
                    <i className={`${facility.icon} display-4 text-danger mb-3`}></i>
                    <h5>{facility.name}</h5>
                    <p className="card-text">{facility.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="row">
        {/* University Preparation */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-danger text-white">
              <h5 className="mb-0">University & Career Preparation</h5>
            </div>
            <div className="card-body">
              {universityPreparation.map((program, index) => (
                <div key={index} className="mb-3">
                  <h6 className="text-danger">{program.program}</h6>
                  <p className="mb-2">{program.description}</p>
                </div>
              ))}
              <div className="mt-4">
                <h6>Recent University Acceptances:</h6>
                <div className="row">
                  <div className="col-md-6">
                    <ul className="small">
                      <li>University of Nairobi</li>
                      <li>Kenyatta University</li>
                      <li>Strathmore University</li>
                    </ul>
                  </div>
                  <div className="col-md-6">
                    <ul className="small">
                      <li>University of Oxford</li>
                      <li>Harvard University</li>
                      <li>University of Toronto</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Academic Calendar */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Academic Calendar 2024</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Term 1: January - March</strong>
                <div className="small text-muted">IGCSE Mock Exams in March</div>
              </div>
              <div className="mb-3">
                <strong>Term 2: May - July</strong>
                <div className="small text-muted">Cambridge Checkpoint in May</div>
              </div>
              <div className="mb-3">
                <strong>Term 3: September - November</strong>
                <div className="small text-muted">IGCSE Final Exams Oct-Nov</div>
              </div>
              <div className="mb-3">
                <strong>Holiday Programs</strong>
                <div className="small text-muted">April, August, December</div>
              </div>
              <button className="btn btn-outline-danger btn-sm w-100">
                Download Full Calendar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HighSchool;