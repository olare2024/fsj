import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Departments() {
  const [activeDepartment, setActiveDepartment] = useState('languages');

  const departments = {
    languages: {
      name: 'Languages Department',
      description: 'Developing communication skills in multiple languages for global citizenship',
      head: 'Dr. Miriam Wanjiku',
      programs: ['English Language', 'Kiswahili', 'French', 'German', 'Chinese Mandarin'],
      features: [
        'Bilingual immersion programs',
        'International language certifications',
        'Debate and public speaking',
        'Creative writing workshops',
        'Cultural exchange programs'
      ],
      achievements: [
        '100% pass rate in IGCSE English',
        'National debate competition winners',
        'International language Olympiad participants',
        'Student publishing opportunities'
      ]
    },
    sciences: {
      name: 'Sciences Department',
      description: 'Fostering scientific inquiry and innovation through hands-on learning',
      head: 'Dr. James Kariuki',
      programs: ['Biology', 'Chemistry', 'Physics', 'Environmental Science', 'Computer Science'],
      features: [
        'State-of-the-art laboratories',
        'Research project opportunities',
        'Science fair participation',
        'Industry partnerships',
        'STEM career guidance'
      ],
      achievements: [
        'National science fair winners',
        'University research collaborations',
        'International science Olympiads',
        'Patent applications by students'
      ]
    },
    mathematics: {
      name: 'Mathematics Department',
      description: 'Building strong mathematical foundations and problem-solving skills',
      head: 'Prof. Robert Mutiso',
      programs: ['Core Mathematics', 'Additional Mathematics', 'Statistics', 'Further Mathematics'],
      features: [
        'Problem-solving strategies',
        'Mathematics competitions',
        'Real-world applications',
        'Technology integration',
        'Individualized support'
      ],
      achievements: [
        'Top IGCSE Mathematics results',
        'International Math Olympiad medals',
        'University mathematics scholarships',
        'Research paper publications'
      ]
    },
    humanities: {
      name: 'Humanities Department',
      description: 'Exploring human experiences, cultures, and societies through multiple perspectives',
      head: 'Mrs. Grace Mwende',
      programs: ['History', 'Geography', 'Business Studies', 'Economics', 'Global Perspectives'],
      features: [
        'Critical thinking development',
        'Research methodology training',
        'Model United Nations',
        'Community service projects',
        'Cultural studies'
      ],
      achievements: [
        'Model UN conference awards',
        'National history competition winners',
        'Business plan competition success',
        'University scholarships in humanities'
      ]
    },
    creative: {
      name: 'Creative Arts Department',
      description: 'Nurturing artistic expression and creative talents across multiple disciplines',
      head: 'Mr. David Omondi',
      programs: ['Visual Arts', 'Music', 'Drama', 'Dance', 'Media Studies'],
      features: [
        'Professional studio spaces',
        'Performance opportunities',
        'Art exhibitions',
        'Industry workshops',
        'Portfolio development'
      ],
      achievements: [
        'National music festival awards',
        'Art exhibition sales',
        'Theater productions',
        'Media competition winners'
      ]
    },
    physical: {
      name: 'Physical Education Department',
      description: 'Promoting physical fitness, sports excellence, and healthy lifestyles',
      head: 'Coach Sarah Adhiambo',
      programs: ['Physical Education', 'Sports Science', 'Health Education', 'Recreation'],
      features: [
        'Modern sports facilities',
        'Professional coaching',
        'Fitness assessment',
        'Sports psychology',
        'Nutrition guidance'
      ],
      achievements: [
        'National sports championships',
        'Athletic scholarships',
        'International competitions',
        'Sports science research'
      ]
    }
  };

  const departmentStats = [
    { metric: '50+', label: 'Qualified Teachers' },
    { metric: '15+', label: 'Specialized Labs' },
    { metric: '95%', label: 'University Acceptance' },
    { metric: '25+', label: 'National Awards' }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/academics">Academics</Link></li>
              <li className="breadcrumb-item active">Departments</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Academic Departments</h1>
            <p className="lead mb-0">Specialized Learning Areas with Expert Faculty</p>
            <div className="mt-3">
              <span className="badge bg-primary fs-6">Cross-Curricular Integration</span>
            </div>
          </div>
        </div>
      </div>

      {/* Department Statistics */}
      <div className="row mb-5">
        <div className="col-12">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <div className="row text-center">
                {departmentStats.map((stat, index) => (
                  <div key={index} className="col-md-3 col-6 mb-3">
                    <div className="display-4 fw-bold">{stat.metric}</div>
                    <div className="fs-5">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Department Navigation */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <div className="d-flex flex-wrap gap-2">
                {Object.keys(departments).map(deptKey => (
                  <button
                    key={deptKey}
                    className={`btn ${activeDepartment === deptKey ? 'btn-primary' : 'btn-outline-primary'} btn-sm`}
                    onClick={() => setActiveDepartment(deptKey)}
                  >
                    {departments[deptKey].name.split(' ')[0]}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Department Details */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h3 className="mb-0">{departments[activeDepartment].name}</h3>
              <p className="mb-0 mt-2">{departments[activeDepartment].description}</p>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-8">
                  <div className="mb-4">
                    <h5>Department Head</h5>
                    <p className="mb-0">
                      <i className="bi bi-person me-2"></i>
                      {departments[activeDepartment].head}
                    </p>
                  </div>

                  <h5>Programs Offered</h5>
                  <div className="row mb-4">
                    {departments[activeDepartment].programs.map((program, index) => (
                      <div key={index} className="col-md-6 mb-2">
                        <i className="bi bi-check-circle text-success me-2"></i>
                        {program}
                      </div>
                    ))}
                  </div>

                  <h5>Key Features</h5>
                  <ul className="mb-4">
                    {departments[activeDepartment].features.map((feature, index) => (
                      <li key={index} className="mb-2">{feature}</li>
                    ))}
                  </ul>

                  <h5>Recent Achievements</h5>
                  <ul>
                    {departments[activeDepartment].achievements.map((achievement, index) => (
                      <li key={index} className="mb-2">
                        <i className="bi bi-trophy text-warning me-2"></i>
                        {achievement}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="col-md-4">
                  <div className="card">
                    <div className="card-header">
                      <h6 className="mb-0">Department Resources</h6>
                    </div>
                    <div className="card-body">
                      <div className="mb-3">
                        <h6>Facilities</h6>
                        <ul className="small">
                          <li>Specialized classrooms</li>
                          <li>Modern equipment</li>
                          <li>Research materials</li>
                          <li>Digital resources</li>
                        </ul>
                      </div>
                      <div className="mb-3">
                        <h6>Student Support</h6>
                        <ul className="small">
                          <li>Individual tutoring</li>
                          <li>Study groups</li>
                          <li>Career guidance</li>
                          <li>University preparation</li>
                        </ul>
                      </div>
                      <button className="btn btn-outline-primary btn-sm w-100">
                        View Department Gallery
                      </button>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h6 className="mb-0">Contact Department</h6>
                    </div>
                    <div className="card-body">
                      <div className="small">
                        <div className="mb-2">
                          <i className="bi bi-envelope me-2"></i>
                          {activeDepartment}@delvok.ac.ke
                        </div>
                        <div className="mb-2">
                          <i className="bi bi-telephone me-2"></i>
                          Ext. {Object.keys(departments).indexOf(activeDepartment) + 100}
                        </div>
                        <div className="mb-2">
                          <i className="bi bi-clock me-2"></i>
                          Office Hours: 8:00 AM - 4:00 PM
                        </div>
                      </div>
                      <button className="btn btn-primary btn-sm w-100 mt-2">
                        Schedule Meeting
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cross-Department Collaboration */}
      <div className="row mt-5">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h4 className="mb-0">Interdepartmental Collaboration</h4>
            </div>
            <div className="card-body">
              <div className="row g-4">
                <div className="col-md-4">
                  <div className="card h-100">
                    <div className="card-body text-center">
                      <i className="bi bi-arrow-left-right display-4 text-success mb-3"></i>
                      <h5>Integrated Projects</h5>
                      <p className="card-text">
                        Cross-disciplinary projects combining multiple subject areas for real-world problem solving.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="card h-100">
                    <div className="card-body text-center">
                      <i className="bi bi-people display-4 text-success mb-3"></i>
                      <h5>Team Teaching</h5>
                      <p className="card-text">
                        Collaborative teaching approaches where multiple departments contribute to single topics.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="card h-100">
                    <div className="card-body text-center">
                      <i className="bi bi-lightbulb display-4 text-success mb-3"></i>
                      <h5>Innovation Labs</h5>
                      <p className="card-text">
                        Special initiatives where different departments work together on innovative educational projects.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Department Events */}
      <div className="row mt-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Upcoming Department Events</h3>
          <div className="row g-4">
            <div className="col-md-6 col-lg-3">
              <div className="card">
                <div className="card-header bg-warning text-dark">
                  <h6 className="mb-0">Science Fair</h6>
                </div>
                <div className="card-body">
                  <p className="small mb-2">
                    <i className="bi bi-calendar me-2"></i>
                    March 15, 2024
                  </p>
                  <p className="small mb-0">
                    Annual science exhibition featuring student research projects.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="card">
                <div className="card-header bg-info text-white">
                  <h6 className="mb-0">Math Olympiad</h6>
                </div>
                <div className="card-body">
                  <p className="small mb-2">
                    <i className="bi bi-calendar me-2"></i>
                    April 5, 2024
                  </p>
                  <p className="small mb-0">
                    Inter-school mathematics competition and problem-solving challenge.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="card">
                <div className="card-header bg-success text-white">
                  <h6 className="mb-0">Language Festival</h6>
                </div>
                <div className="card-body">
                  <p className="small mb-2">
                    <i className="bi bi-calendar me-2"></i>
                    May 20, 2024
                  </p>
                  <p className="small mb-0">
                    Multicultural celebration featuring performances in multiple languages.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="card">
                <div className="card-header bg-primary text-white">
                  <h6 className="mb-0">Arts Exhibition</h6>
                </div>
                <div className="card-body">
                  <p className="small mb-2">
                    <i className="bi bi-calendar me-2"></i>
                    June 10, 2024
                  </p>
                  <p className="small mb-0">
                    Showcase of student artwork, music, drama, and creative writing.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Departments;