import React from 'react';
import { Link } from 'react-router-dom';

function HonorsProgram() {
  const programTracks = [
    {
      track: 'STEM Honors',
      focus: 'Science, Technology, Engineering, and Mathematics',
      requirements: ['A* in IGCSE Mathematics and Sciences', '90%+ in school exams', 'Teacher recommendation'],
      benefits: ['Research opportunities', 'Mentorship from university professors', 'Advanced laboratory access'],
      projects: ['Science fair projects', 'Research papers', 'Innovation challenges']
    },
    {
      track: 'Humanities Honors',
      focus: 'Literature, History, Philosophy, and Social Sciences',
      requirements: ['A* in IGCSE English and Humanities', 'Outstanding writing samples', 'Teacher recommendation'],
      benefits: ['Writing workshops', 'Debate and public speaking', 'Cultural exchange programs'],
      projects: ['Research papers', 'Creative writing portfolio', 'Social impact projects']
    },
    {
      track: 'Global Leadership',
      focus: 'International relations, Business, and Leadership',
      requirements: ['Demonstrated leadership experience', 'Strong academic record', 'Community service involvement'],
      benefits: ['Model UN participation', 'Entrepreneurship training', 'International conferences'],
      projects: ['Social entrepreneurship ventures', 'Leadership initiatives', 'Community development projects']
    }
  ];

  const admissionProcess = [
    {
      step: '1. Application',
      description: 'Submit online application with academic records',
      deadline: 'Rolling admissions'
    },
    {
      step: '2. Testing',
      description: 'Take honors program entrance examination',
      deadline: 'Scheduled individually'
    },
    {
      step: '3. Interview',
      description: 'Panel interview with program directors',
      deadline: 'Within 2 weeks of testing'
    },
    {
      step: '4. Decision',
      description: 'Admission decision and program placement',
      deadline: 'Within 1 week of interview'
    }
  ];

  const alumniAchievements = [
    {
      name: 'Dr. Amina Juma',
      program: 'STEM Honors 2015',
      achievement: 'PhD in Biomedical Engineering, MIT',
      current: 'Research Scientist at Johns Hopkins'
    },
    {
      name: 'Mark Chen',
      program: 'Humanities Honors 2016',
      achievement: 'Rhodes Scholar, Oxford University',
      current: 'Foreign Service Officer'
    },
    {
      name: 'Sarah Omondi',
      program: 'Global Leadership 2017',
      achievement: 'Youngest Kenyan UN Delegate',
      current: 'Social Entrepreneur'
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
              <li className="breadcrumb-item active">Honors Program</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-warning">Honors Program</h1>
              <p className="lead mb-0">For Exceptionally Motivated and Gifted Students</p>
            </div>
            <div className="badge bg-warning text-dark fs-6">
              By Invitation Only
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-warning text-dark mb-5">
        <div className="card-body p-5">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="fw-bold mb-3">Excellence Beyond the Classroom</h2>
              <p className="fs-5 mb-4">
                The Delvok Academy Honors Program challenges exceptionally motivated students 
                through advanced coursework, research opportunities, and leadership development. 
                Our program nurtures intellectual curiosity and prepares students for top universities worldwide.
              </p>
              <div className="d-flex gap-3">
                <button className="btn btn-dark btn-lg">
                  Program Brochure
                </button>
                <button className="btn btn-outline-dark btn-lg">
                  Nominate a Student
                </button>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-stars display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Program Tracks */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Honors Program Tracks</h3>
          <div className="row g-4">
            {programTracks.map((track, index) => (
              <div key={index} className="col-lg-4">
                <div className="card h-100 border-warning">
                  <div className="card-header bg-warning text-dark">
                    <h5 className="mb-0">{track.track}</h5>
                    <small>{track.focus}</small>
                  </div>
                  <div className="card-body">
                    <h6>Admission Requirements:</h6>
                    <ul className="small mb-3">
                      {track.requirements.map((req, idx) => (
                        <li key={idx}>{req}</li>
                      ))}
                    </ul>

                    <h6>Program Benefits:</h6>
                    <ul className="small mb-3">
                      {track.benefits.map((benefit, idx) => (
                        <li key={idx}>{benefit}</li>
                      ))}
                    </ul>

                    <h6>Capstone Projects:</h6>
                    <ul className="small">
                      {track.projects.map((project, idx) => (
                        <li key={idx}>{project}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="card-footer bg-transparent">
                    <button className="btn btn-outline-warning btn-sm w-100">
                      Track Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="row mb-5">
        {/* Admission Process */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-warning text-dark">
              <h5 className="mb-0">Admission Process</h5>
            </div>
            <div className="card-body">
              {admissionProcess.map((step, index) => (
                <div key={index} className="mb-4">
                  <div className="d-flex align-items-start">
                    <div className="bg-warning text-dark rounded-circle p-2 me-3">
                      <strong>{step.step.split('.')[0]}</strong>
                    </div>
                    <div>
                      <h6 className="mb-1">{step.step}</h6>
                      <p className="mb-1">{step.description}</p>
                      <small className="text-muted">Deadline: {step.deadline}</small>
                    </div>
                  </div>
                </div>
              ))}
              <div className="alert alert-info">
                <strong>Note:</strong> Students may be nominated by teachers or self-nominate 
                with supporting documentation.
              </div>
            </div>
          </div>
        </div>

        {/* Program Features */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Program Features</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <h6 className="text-warning">Advanced Coursework</h6>
                <p className="small mb-0">University-level courses and seminars</p>
              </div>
              <div className="mb-3">
                <h6 className="text-warning">Research Mentorship</h6>
                <p className="small mb-0">One-on-one guidance from faculty mentors</p>
              </div>
              <div className="mb-3">
                <h6 className="text-warning">Leadership Development</h6>
                <p className="small mb-0">Executive skills training and workshops</p>
              </div>
              <div className="mb-3">
                <h6 className="text-warning">Global Network</h6>
                <p className="small mb-0">Connections with honors programs worldwide</p>
              </div>
              <div className="mb-3">
                <h6 className="text-warning">University Preparation</h6>
                <p className="small mb-0">Dedicated counseling for top universities</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alumni Success */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-warning text-dark">
              <h5 className="mb-0">Honors Program Alumni</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {alumniAchievements.map((alumni, index) => (
                  <div key={index} className="col-md-4 mb-4">
                    <div className="text-center">
                      <div className="bg-warning rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                           style={{width: '80px', height: '80px'}}>
                        <i className="bi bi-person-fill display-6 text-dark"></i>
                      </div>
                      <h6 className="mb-1">{alumni.name}</h6>
                      <small className="text-muted d-block mb-2">{alumni.program}</small>
                      <p className="small mb-1">{alumni.achievement}</p>
                      <small className="text-muted">{alumni.current}</small>
                    </div>
                  </div>
                ))}
              </div>
              <div className="text-center mt-4">
                <button className="btn btn-outline-warning">
                  View More Alumni Stories
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HonorsProgram;