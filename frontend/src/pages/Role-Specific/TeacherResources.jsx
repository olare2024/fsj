import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function TeacherRole() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('lesson-plans');

  const teachingResources = {
    'lesson-plans': [
      {
        title: 'Mathematics Lesson Templates',
        subject: 'Math',
        grade: '6-8',
        format: 'Google Docs',
        downloads: 245,
        rating: 4.8
      },
      {
        title: 'Science Experiment Guides',
        subject: 'Science',
        grade: '9-12',
        format: 'PDF',
        downloads: 189,
        rating: 4.7
      },
      {
        title: 'Literature Discussion Questions',
        subject: 'English',
        grade: '9-12',
        format: 'Word Doc',
        downloads: 167,
        rating: 4.6
      },
      {
        title: 'History Primary Source Analysis',
        subject: 'Social Studies',
        grade: '10-12',
        format: 'PDF',
        downloads: 134,
        rating: 4.9
      }
    ],
    assessments: [
      {
        title: 'Standardized Test Prep Materials',
        subject: 'All',
        grade: '9-12',
        format: 'PDF',
        downloads: 312,
        rating: 4.7
      },
      {
        title: 'Rubric Templates Collection',
        subject: 'All',
        grade: '6-12',
        format: 'Google Docs',
        downloads: 278,
        rating: 4.8
      },
      {
        title: 'Exit Ticket Templates',
        subject: 'All',
        grade: '6-12',
        format: 'PDF',
        downloads: 195,
        rating: 4.5
      }
    ],
    'classroom-tools': [
      {
        title: 'Behavior Management System',
        subject: 'Classroom Management',
        grade: 'All',
        format: 'PDF Guide',
        downloads: 156,
        rating: 4.6
      },
      {
        title: 'Digital Classroom Setup Guide',
        subject: 'Technology',
        grade: 'All',
        format: 'Online Resource',
        downloads: 223,
        rating: 4.8
      },
      {
        title: 'Parent Communication Templates',
        subject: 'Communication',
        grade: 'All',
        format: 'Email Templates',
        downloads: 189,
        rating: 4.7
      }
    ]
  };

  const professionalDevelopment = [
    {
      title: 'Differentiated Instruction Workshop',
      date: '2024-02-15',
      duration: '2 hours',
      type: 'Virtual',
      seats: 25,
      enrolled: 18
    },
    {
      title: 'Technology Integration Training',
      date: '2024-02-20',
      duration: '3 hours',
      type: 'In-Person',
      seats: 20,
      enrolled: 15
    },
    {
      title: 'Classroom Management Strategies',
      date: '2024-02-25',
      duration: '2.5 hours',
      type: 'Virtual',
      seats: 30,
      enrolled: 22
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Teacher Resources</h1>
          <p className="lead">
            Welcome, {currentUser?.firstName}! Access teaching materials, professional development, and classroom tools.
          </p>
        </div>
        <Link to="/teacher-dashboard" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Dashboard
        </Link>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>5</h3>
              <p className="mb-0">Active Classes</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>42</h3>
              <p className="mb-0">Total Students</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>12</h3>
              <p className="mb-0">Grading Pending</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>3</h3>
              <p className="mb-0">Upcoming Meetings</p>
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
                className={`nav-link ${activeTab === 'lesson-plans' ? 'active' : ''}`}
                onClick={() => setActiveTab('lesson-plans')}
              >
                <i className="bi bi-journal-text me-2"></i>
                Lesson Plans
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'assessments' ? 'active' : ''}`}
                onClick={() => setActiveTab('assessments')}
              >
                <i className="bi bi-clipboard-check me-2"></i>
                Assessments
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'classroom-tools' ? 'active' : ''}`}
                onClick={() => setActiveTab('classroom-tools')}
              >
                <i className="bi bi-tools me-2"></i>
                Classroom Tools
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'professional-dev' ? 'active' : ''}`}
                onClick={() => setActiveTab('professional-dev')}
              >
                <i className="bi bi-mortarboard me-2"></i>
                Professional Development
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Teaching Resources */}
          {['lesson-plans', 'assessments', 'classroom-tools'].includes(activeTab) && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="mb-0">
                  {activeTab === 'lesson-plans' && 'Lesson Plan Resources'}
                  {activeTab === 'assessments' && 'Assessment Materials'}
                  {activeTab === 'classroom-tools' && 'Classroom Management Tools'}
                </h5>
                <button className="btn btn-primary">
                  <i className="bi bi-upload me-2"></i>
                  Share Resource
                </button>
              </div>

              <div className="row g-4">
                {teachingResources[activeTab].map((resource, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100 shadow-sm">
                      <div className="card-body">
                        <div className="d-flex justify-content-between align-items-start mb-3">
                          <span className="badge bg-primary">{resource.subject}</span>
                          <span className="badge bg-secondary">{resource.grade}</span>
                        </div>
                        <h6 className="card-title">{resource.title}</h6>
                        <div className="resource-meta">
                          <small className="text-muted d-block mb-2">
                            Format: {resource.format}
                          </small>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <small className="text-muted me-3">
                                <i className="bi bi-download me-1"></i>
                                {resource.downloads}
                              </small>
                              <small className="text-muted">
                                <i className="bi bi-star-fill text-warning me-1"></i>
                                {resource.rating}
                              </small>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="card-footer">
                        <div className="d-flex gap-2">
                          <button className="btn btn-primary btn-sm flex-fill">
                            <i className="bi bi-download me-1"></i>
                            Download
                          </button>
                          <button className="btn btn-outline-secondary btn-sm">
                            <i className="bi bi-eye"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Professional Development */}
          {activeTab === 'professional-dev' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="mb-0">Professional Development Opportunities</h5>
                <button className="btn btn-primary">
                  <i className="bi bi-calendar-plus me-2"></i>
                  Request Training
                </button>
              </div>

              <div className="row g-4">
                {professionalDevelopment.map((session, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-body">
                        <h6 className="card-title">{session.title}</h6>
                        <div className="session-details">
                          <div className="d-flex align-items-center mb-2">
                            <i className="bi bi-calendar text-primary me-2"></i>
                            <small>{session.date}</small>
                          </div>
                          <div className="d-flex align-items-center mb-2">
                            <i className="bi bi-clock text-primary me-2"></i>
                            <small>{session.duration}</small>
                          </div>
                          <div className="d-flex align-items-center mb-3">
                            <i className="bi bi-geo text-primary me-2"></i>
                            <small>{session.type}</small>
                          </div>
                          
                          <div className="enrollment-progress">
                            <div className="d-flex justify-content-between align-items-center mb-1">
                              <small className="text-muted">Enrollment</small>
                              <small className="text-muted">
                                {session.enrolled}/{session.seats}
                              </small>
                            </div>
                            <div className="progress">
                              <div 
                                className="progress-bar"
                                style={{width: `${(session.enrolled / session.seats) * 100}%`}}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="card-footer">
                        <div className="d-flex gap-2">
                          <button className="btn btn-success btn-sm flex-fill">
                            Enroll Now
                          </button>
                          <button className="btn btn-outline-primary btn-sm">
                            Details
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Access Tools */}
      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Teaching Tools</h5>
            </div>
            <div className="card-body">
              <div className="row g-3">
                <div className="col-6">
                  <Link to="/grade-management" className="text-decoration-none">
                    <div className="card text-center hover-shadow">
                      <div className="card-body">
                        <i className="bi bi-journal-check display-6 text-success mb-2"></i>
                        <h6 className="card-title mb-0">Grade Management</h6>
                      </div>
                    </div>
                  </Link>
                </div>
                <div className="col-6">
                  <Link to="/attendance-management" className="text-decoration-none">
                    <div className="card text-center hover-shadow">
                      <div className="card-body">
                        <i className="bi bi-clipboard-check display-6 text-primary mb-2"></i>
                        <h6 className="card-title mb-0">Attendance</h6>
                      </div>
                    </div>
                  </Link>
                </div>
                <div className="col-6">
                  <Link to="/lesson-planner" className="text-decoration-none">
                    <div className="card text-center hover-shadow">
                      <div className="card-body">
                        <i className="bi bi-calendar-week display-6 text-warning mb-2"></i>
                        <h6 className="card-title mb-0">Lesson Planner</h6>
                      </div>
                    </div>
                  </Link>
                </div>
                <div className="col-6">
                  <Link to="/student-progress" className="text-decoration-none">
                    <div className="card text-center hover-shadow">
                      <div className="card-body">
                        <i className="bi bi-graph-up display-6 text-info mb-2"></i>
                        <h6 className="card-title mb-0">Student Progress</h6>
                      </div>
                    </div>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Recent Activity</h5>
            </div>
            <div className="card-body">
              <div className="list-group list-group-flush">
                <div className="list-group-item d-flex align-items-center">
                  <i className="bi bi-check-circle-fill text-success me-3"></i>
                  <div>
                    <small>Graded Algebra quizzes</small>
                    <div className="text-muted">2 hours ago</div>
                  </div>
                </div>
                <div className="list-group-item d-flex align-items-center">
                  <i className="bi bi-chat-dots-fill text-primary me-3"></i>
                  <div>
                    <small>Parent meeting scheduled</small>
                    <div className="text-muted">Yesterday</div>
                  </div>
                </div>
                <div className="list-group-item d-flex align-items-center">
                  <i className="bi bi-upload text-warning me-3"></i>
                  <div>
                    <small>Uploaded new lesson materials</small>
                    <div className="text-muted">2 days ago</div>
                  </div>
                </div>
                <div className="list-group-item d-flex align-items-center">
                  <i className="bi bi-people-fill text-info me-3"></i>
                  <div>
                    <small>Department meeting attended</small>
                    <div className="text-muted">3 days ago</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TeacherRole;