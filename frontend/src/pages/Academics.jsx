import React from 'react';
import { Link } from 'react-router-dom';

function Academics() {
  const programs = [
    {
      level: 'Lower Primary',
      grades: 'Grades 1-3',
      focus: 'Foundational Skills',
      subjects: ['Literacy', 'Numeracy', 'Environmental', 'Creative Arts'],
      color: 'primary'
    },
    {
      level: 'Upper Primary',
      grades: 'Grades 4-6',
      focus: 'Skill Development',
      subjects: ['Science', 'Social Studies', 'Agriculture', 'Home Science'],
      color: 'success'
    },
    {
      level: 'Junior Secondary',
      grades: 'Grades 7-9',
      focus: 'Career Exploration',
      subjects: ['Pre-Technical', 'Business', 'Agriculture', 'Sports'],
      color: 'warning'
    },
    {
      level: 'Senior Secondary',
      grades: 'Grades 10-12',
      focus: 'Specialization',
      subjects: ['STEM', 'Social Sciences', 'Arts', 'Technical'],
      color: 'info'
    }
  ];

  return (
    <div className="academics-page">
      {/* Hero Section */}
      <section className="academics-hero bg-dark text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">Academic Programs</h1>
              <p className="lead fs-4">
                Comprehensive CBC Education from Foundation to Specialization
              </p>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">📚</div>
            </div>
          </div>
        </div>
      </section>

      {/* Programs Overview */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center display-6 fw-bold text-primary mb-5">Our Academic Programs</h2>
          <div className="row g-4">
            {programs.map((program, index) => (
              <div key={index} className="col-lg-6">
                <div className={`card program-card border-${program.color} h-100 shadow-sm`}>
                  <div className="card-header bg-white border-bottom-0 pb-0">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h4 className={`text-${program.color} fw-bold`}>{program.level}</h4>
                        <h6 className="text-muted">{program.grades}</h6>
                      </div>
                      <span className={`badge bg-${program.color} fs-6`}>{program.focus}</span>
                    </div>
                  </div>
                  <div className="card-body">
                    <p className="card-text mb-3">
                      Our {program.level} program focuses on {program.focus.toLowerCase()} 
                      through engaging and practical learning experiences.
                    </p>
                    <div className="mb-3">
                      <strong>Core Subjects:</strong>
                      <div className="mt-2">
                        {program.subjects.map((subject, idx) => (
                          <span key={idx} className="badge bg-light text-dark border me-1 mb-1">
                            {subject}
                          </span>
                        ))}
                      </div>
                    </div>
                    <Link to="/subjects" className={`btn btn-outline-${program.color}`}>
                      View Subjects <i className="bi bi-arrow-right ms-1"></i>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CBC Information */}
      <section className="py-5 bg-light">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6">
              <h2 className="display-6 fw-bold text-primary mb-4">Competency Based Curriculum</h2>
              <p className="lead mb-4">
                Our CBC approach focuses on developing practical skills and competencies 
                beyond traditional academic knowledge.
              </p>
              <div className="competencies">
                {[
                  'Communication & Collaboration',
                  'Critical Thinking & Problem Solving',
                  'Creativity & Imagination',
                  'Digital Literacy',
                  'Learning to Learn',
                  'Self-Efficacy'
                ].map((competency, index) => (
                  <div key={index} className="d-flex align-items-center mb-3">
                    <i className="bi bi-check-circle-fill text-success me-3 fs-5"></i>
                    <span className="fs-6">{competency}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="col-lg-6">
              <div className="cbc-image text-center">
                <div className="image-placeholder bg-primary rounded p-5 text-white">
                  <i className="bi bi-mortarboard display-1"></i>
                  <p className="mt-3">CBC Learning in Action</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Academic Calendar */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center display-6 fw-bold text-primary mb-5">Academic Calendar 2024</h2>
          <div className="row">
            <div className="col-lg-8 mx-auto">
              <div className="card shadow-sm border-0">
                <div className="card-body">
                  <div className="table-responsive">
                    <table className="table table-hover">
                      <thead className="table-primary">
                        <tr>
                          <th>Term</th>
                          <th>Duration</th>
                          <th>Key Events</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Term 1</td>
                          <td>Jan 8 - Apr 5</td>
                          <td>Opening Day, Sports Day, Mid-term Break</td>
                        </tr>
                        <tr>
                          <td>Term 2</td>
                          <td>May 6 - Aug 2</td>
                          <td>Science Fair, Parents Day, Half-term Break</td>
                        </tr>
                        <tr>
                          <td>Term 3</td>
                          <td>Sep 2 - Nov 29</td>
                          <td>Cultural Day, Prize Giving, Closing Day</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <style jsx>{`
        .academics-hero {
          background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        }
        
        .program-card {
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .program-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
        }
        
        .image-placeholder {
          min-height: 300px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </div>
  );
}

export default Academics;