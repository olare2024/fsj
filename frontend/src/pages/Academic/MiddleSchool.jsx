import React from 'react';
import { Link } from 'react-router-dom';

function MiddleSchool() {
  const gradeLevels = [
    {
      grade: 'Grade 4-5',
      age: '9-11 years',
      focus: 'Developing critical thinking and independent learning skills',
      subjects: ['English', 'Kiswahili', 'Mathematics', 'Science', 'Social Studies', 'CRE/IRE/HRE', 'Creative Arts', 'Physical Education'],
      curriculum: ['CBC - Upper Primary', 'Cambridge Primary'],
      exams: ['Cambridge Primary Checkpoint']
    },
    {
      grade: 'Grade 6',
      age: '11-12 years',
      focus: 'Preparation for secondary education and specialization',
      subjects: ['English', 'Kiswahili', 'Mathematics', 'Integrated Science', 'Social Studies', 'Religious Education', 'Agriculture', 'Home Science', 'Business Studies'],
      curriculum: ['CBC - Upper Primary', 'Cambridge Lower Secondary Introduction'],
      exams: ['Kenya Primary School Education Assessment (KPSEA)']
    }
  ];

  const programHighlights = [
    {
      title: 'Cambridge Lower Secondary',
      description: 'International curriculum with global recognition and benchmarking',
      icon: 'bi-globe'
    },
    {
      title: 'STEAM Integration',
      description: 'Science, Technology, Engineering, Arts, and Mathematics focus',
      icon: 'bi-cpu'
    },
    {
      title: 'Leadership Development',
      description: 'Student council, clubs, and leadership opportunities',
      icon: 'bi-award'
    },
    {
      title: 'Digital Literacy',
      description: 'Technology integration across all subjects',
      icon: 'bi-laptop'
    }
  ];

  const extracurricular = [
    {
      category: 'Sports',
      activities: ['Football', 'Basketball', 'Swimming', 'Athletics', 'Volleyball']
    },
    {
      category: 'Clubs',
      activities: ['Science Club', 'Debate Club', 'Drama Club', 'Music Club', 'Environmental Club']
    },
    {
      category: 'Competitions',
      activities: ['Math Olympiad', 'Science Fair', 'Spelling Bee', 'Music Festival', 'Sports Day']
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
              <li className="breadcrumb-item active">Middle School</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-success">Middle School</h1>
              <p className="lead mb-0">Grade 4 to Grade 6 - Developing Independent Learners</p>
            </div>
            <div className="badge bg-success fs-6">
              Ages 9-12 Years
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-success text-white mb-5">
        <div className="card-body p-5">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="fw-bold mb-3">Building Bridges to Secondary Education</h2>
              <p className="fs-5 mb-4">
                Our Middle School program prepares students for the transition to secondary education 
                through a balanced curriculum that combines Kenyan CBC with Cambridge Lower Secondary. 
                We focus on developing critical thinking, creativity, and independent learning skills.
              </p>
              <div className="d-flex gap-3">
                <button className="btn btn-light btn-lg text-success">
                  View Curriculum Details
                </button>
                <button className="btn btn-outline-light btn-lg">
                  Meet Our Teachers
                </button>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-journals display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Grade Levels */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Academic Program</h3>
          <div className="row g-4">
            {gradeLevels.map((level, index) => (
              <div key={index} className="col-lg-6">
                <div className="card h-100 border-success">
                  <div className="card-header bg-success text-white d-flex justify-content-between align-items-center">
                    <div>
                      <h5 className="mb-0">{level.grade}</h5>
                      <small>{level.age}</small>
                    </div>
                    <div className="badge bg-light text-success">
                      {level.curriculum.length} Curricula
                    </div>
                  </div>
                  <div className="card-body">
                    <p className="card-text fst-italic">{level.focus}</p>
                    
                    <h6 className="mt-4">Core Subjects:</h6>
                    <div className="row">
                      {level.subjects.map((subject, idx) => (
                        <div key={idx} className="col-md-6">
                          <i className="bi bi-check-circle text-success me-2"></i>
                          {subject}
                        </div>
                      ))}
                    </div>

                    <div className="row mt-4">
                      <div className="col-md-6">
                        <h6>Curriculum:</h6>
                        <div className="d-flex flex-wrap gap-2">
                          {level.curriculum.map((curr, idx) => (
                            <span key={idx} className="badge bg-success">{curr}</span>
                          ))}
                        </div>
                      </div>
                      <div className="col-md-6">
                        <h6>Assessments:</h6>
                        <div className="d-flex flex-wrap gap-2">
                          {level.exams.map((exam, idx) => (
                            <span key={idx} className="badge bg-warning text-dark">{exam}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Program Highlights */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Program Highlights</h3>
          <div className="row g-4">
            {programHighlights.map((highlight, index) => (
              <div key={index} className="col-md-6 col-lg-3">
                <div className="card h-100 text-center border-success">
                  <div className="card-body">
                    <i className={`${highlight.icon} display-4 text-success mb-3`}></i>
                    <h5>{highlight.title}</h5>
                    <p className="card-text">{highlight.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="row">
        {/* Extracurricular Activities */}
        <div className="col-md-8">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">Beyond the Classroom</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {extracurricular.map((category, index) => (
                  <div key={index} className="col-md-4">
                    <h6 className="text-success">{category.category}</h6>
                    <ul className="list-unstyled">
                      {category.activities.map((activity, idx) => (
                        <li key={idx} className="mb-2">
                          <i className="bi bi-arrow-right-circle text-success me-2"></i>
                          {activity}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Assessment Info */}
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Assessment Framework</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Cambridge Primary Checkpoint</strong>
                <div className="small text-muted">Grade 5 - External Benchmarking</div>
              </div>
              <div className="mb-3">
                <strong>KPSEA</strong>
                <div className="small text-muted">Grade 6 - National Assessment</div>
              </div>
              <div className="mb-3">
                <strong>Continuous Assessment</strong>
                <div className="small text-muted">Termly evaluations and projects</div>
              </div>
              <button className="btn btn-outline-success btn-sm w-100">
                Assessment Calendar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MiddleSchool;