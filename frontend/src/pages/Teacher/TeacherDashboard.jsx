import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function TeacherDashboard() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [todaySchedule, setTodaySchedule] = useState([]);
  const [upcomingAssignments, setUpcomingAssignments] = useState([]);
  const [recentAnnouncements, setRecentAnnouncements] = useState([]);

  // Mock data - in real app, this would come from API
  useEffect(() => {
    // Today's schedule
    setTodaySchedule([
      { time: '8:00-9:00', class: 'Grade 7A', subject: 'Mathematics', room: 'Room 101', curriculum: 'CBC' },
      { time: '9:00-10:00', class: 'Grade 9B', subject: 'Physics', room: 'Science Lab', curriculum: 'IGCSE' },
      { time: '10:30-11:30', class: 'Grade 8C', subject: 'Mathematics', room: 'Room 205', curriculum: 'CBC' },
      { time: '11:30-12:30', class: 'Grade 10A', subject: 'Additional Math', room: 'Room 301', curriculum: 'IGCSE' },
      { time: '2:00-3:00', class: 'Grade 7B', subject: 'Mathematics', room: 'Room 102', curriculum: 'CBC' }
    ]);

    // Upcoming assignments to grade
    setUpcomingAssignments([
      { class: 'Grade 9B', subject: 'Physics', assignment: 'Forces and Motion', dueDate: 'Today', submissions: 28, graded: 15 },
      { class: 'Grade 10A', subject: 'Additional Math', assignment: 'Calculus Worksheet', dueDate: 'Tomorrow', submissions: 32, graded: 0 },
      { class: 'Grade 7A', subject: 'Mathematics', assignment: 'Algebra Basics', dueDate: 'In 2 days', submissions: 35, graded: 20 },
      { class: 'Grade 8C', subject: 'Mathematics', assignment: 'Geometry Quiz', dueDate: 'In 3 days', submissions: 30, graded: 30 }
    ]);

    // Recent announcements
    setRecentAnnouncements([
      { title: 'Staff Meeting', date: '2024-01-15', content: 'Emergency staff meeting tomorrow at 3:00 PM in the conference room.' },
      { title: 'Cambridge Training', date: '2024-01-14', content: 'Cambridge curriculum training session scheduled for next week.' },
      { title: 'CBC Assessment', date: '2024-01-13', content: 'Reminder to complete CBC competency assessments by end of week.' }
    ]);
  }, []);

  const quickStats = [
    { title: 'Total Students', value: '145', icon: 'bi-people', color: 'primary' },
    { title: 'Classes', value: '6', icon: 'bi-journal', color: 'success' },
    { title: 'Pending Grading', value: '67', icon: 'bi-pencil', color: 'warning' },
    { title: 'Attendance Today', value: '92%', icon: 'bi-clipboard-check', color: 'info' }
  ];

  const curriculumResources = [
    { title: 'CBC Teacher Guides', type: 'PDF', subject: 'All Subjects', download: 'Download' },
    { title: 'Cambridge Syllabus', type: 'PDF', subject: 'IGCSE', download: 'View' },
    { title: 'Lesson Plan Templates', type: 'Document', subject: 'Templates', download: 'Download' },
    { title: 'Assessment Rubrics', type: 'Spreadsheet', subject: 'All Subjects', download: 'Download' }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item active">Teacher Dashboard</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">Teacher Dashboard</h1>
              <p className="lead mb-0">Welcome back, {currentUser?.name || 'Teacher'}</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">Today: {new Date().toLocaleDateString()}</div>
              <div className="small text-muted">Dual Curriculum: CBC & Cambridge</div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        {quickStats.map((stat, index) => (
          <div key={index} className="col-md-3 col-sm-6 mb-3">
            <div className="card border-0 bg-light">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <div className="fs-4 fw-bold text-dark">{stat.value}</div>
                    <div className="small text-muted">{stat.title}</div>
                  </div>
                  <div className={`bg-${stat.color} text-white rounded-circle p-3`}>
                    <i className={`${stat.icon} fs-4`}></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Tabs */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <i className="bi bi-speedometer2 me-2"></i>
                Overview
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'schedule' ? 'active' : ''}`}
                onClick={() => setActiveTab('schedule')}
              >
                <i className="bi bi-calendar me-2"></i>
                Schedule
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'grading' ? 'active' : ''}`}
                onClick={() => setActiveTab('grading')}
              >
                <i className="bi bi-pencil me-2"></i>
                Grading
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'resources' ? 'active' : ''}`}
                onClick={() => setActiveTab('resources')}
              >
                <i className="bi bi-folder me-2"></i>
                Resources
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="row">
              <div className="col-md-8">
                <h5>Today's Schedule</h5>
                <div className="card">
                  <div className="card-body">
                    {todaySchedule.map((lesson, index) => (
                      <div key={index} className="d-flex justify-content-between align-items-center border-bottom pb-2 mb-2">
                        <div>
                          <strong>{lesson.time}</strong>
                          <div>{lesson.class} - {lesson.subject}</div>
                          <small className="text-muted">{lesson.room}</small>
                        </div>
                        <span className={`badge ${lesson.curriculum === 'CBC' ? 'bg-success' : 'bg-primary'}`}>
                          {lesson.curriculum}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <h5 className="mt-4">Upcoming Assignments to Grade</h5>
                <div className="card">
                  <div className="card-body">
                    {upcomingAssignments.map((assignment, index) => (
                      <div key={index} className="d-flex justify-content-between align-items-center border-bottom pb-2 mb-2">
                        <div>
                          <strong>{assignment.assignment}</strong>
                          <div>{assignment.class} - {assignment.subject}</div>
                          <small className="text-muted">
                            {assignment.submissions} submissions • {assignment.graded} graded
                          </small>
                        </div>
                        <div className="text-end">
                          <span className={`badge ${assignment.dueDate === 'Today' ? 'bg-warning' : 'bg-secondary'}`}>
                            {assignment.dueDate}
                          </span>
                          <div>
                            <button className="btn btn-primary btn-sm mt-1">
                              Grade Now
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="col-md-4">
                <h5>Quick Actions</h5>
                <div className="d-grid gap-2 mb-4">
                  <Link to="/attendance-management" className="btn btn-outline-primary text-start">
                    <i className="bi bi-clipboard-check me-2"></i>
                    Take Attendance
                  </Link>
                  <Link to="/grade-management" className="btn btn-outline-success text-start">
                    <i className="bi bi-pencil me-2"></i>
                    Enter Grades
                  </Link>
                  <button className="btn btn-outline-info text-start">
                    <i className="bi bi-plus-circle me-2"></i>
                    Create Assignment
                  </button>
                  <button className="btn btn-outline-warning text-start">
                    <i className="bi bi-calendar-event me-2"></i>
                    Schedule Lesson
                  </button>
                </div>

                <h5>Recent Announcements</h5>
                <div className="card">
                  <div className="card-body">
                    {recentAnnouncements.map((announcement, index) => (
                      <div key={index} className="border-bottom pb-2 mb-2">
                        <strong>{announcement.title}</strong>
                        <div className="small text-muted mb-1">
                          {new Date(announcement.date).toLocaleDateString()}
                        </div>
                        <p className="small mb-0">{announcement.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Schedule Tab */}
          {activeTab === 'schedule' && (
            <div>
              <h5>Weekly Schedule</h5>
              <div className="table-responsive">
                <table className="table table-bordered">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Monday</th>
                      <th>Tuesday</th>
                      <th>Wednesday</th>
                      <th>Thursday</th>
                      <th>Friday</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>8:00-9:00</td>
                      <td>Grade 7A Math (CBC)</td>
                      <td>Grade 9B Physics (IGCSE)</td>
                      <td>Grade 7A Math (CBC)</td>
                      <td>Grade 9B Physics (IGCSE)</td>
                      <td>Grade 7A Math (CBC)</td>
                    </tr>
                    <tr>
                      <td>9:00-10:00</td>
                      <td>Grade 8C Math (CBC)</td>
                      <td>Grade 10A Add Math (IGCSE)</td>
                      <td>Grade 8C Math (CBC)</td>
                      <td>Grade 10A Add Math (IGCSE)</td>
                      <td>Grade 8C Math (CBC)</td>
                    </tr>
                    {/* Add more rows as needed */}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Grading Tab */}
          {activeTab === 'grading' && (
            <div>
              <h5>Assignment Grading</h5>
              <div className="row">
                {upcomingAssignments.map((assignment, index) => (
                  <div key={index} className="col-md-6 mb-3">
                    <div className="card">
                      <div className="card-body">
                        <h6>{assignment.assignment}</h6>
                        <p className="small mb-2">{assignment.class} - {assignment.subject}</p>
                        <div className="progress mb-2">
                          <div 
                            className="progress-bar" 
                            style={{width: `${(assignment.graded / assignment.submissions) * 100}%`}}
                          >
                            {Math.round((assignment.graded / assignment.submissions) * 100)}%
                          </div>
                        </div>
                        <div className="d-flex justify-content-between">
                          <small>{assignment.graded}/{assignment.submissions} graded</small>
                          <span className={`badge ${assignment.dueDate === 'Today' ? 'bg-warning' : 'bg-secondary'}`}>
                            {assignment.dueDate}
                          </span>
                        </div>
                        <button className="btn btn-primary btn-sm w-100 mt-2">
                          Grade Assignment
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Resources Tab */}
          {activeTab === 'resources' && (
            <div>
              <h5>Curriculum Resources</h5>
              <div className="row">
                {curriculumResources.map((resource, index) => (
                  <div key={index} className="col-md-6 mb-3">
                    <div className="card">
                      <div className="card-body">
                        <h6>{resource.title}</h6>
                        <div className="d-flex justify-content-between align-items-center">
                          <span className="badge bg-secondary">{resource.type}</span>
                          <small className="text-muted">{resource.subject}</small>
                        </div>
                        <button className="btn btn-outline-primary btn-sm w-100 mt-2">
                          <i className="bi bi-download me-2"></i>
                          {resource.download}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Links Footer */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-body">
              <h6 className="mb-3">Quick Access</h6>
              <div className="row">
                <div className="col-md-3 mb-2">
                  <Link to="/attendance-management" className="btn btn-outline-primary btn-sm w-100">
                    Attendance
                  </Link>
                </div>
                <div className="col-md-3 mb-2">
                  <Link to="/grade-management" className="btn btn-outline-success btn-sm w-100">
                    Gradebook
                  </Link>
                </div>
                <div className="col-md-3 mb-2">
                  <Link to="/timetable" className="btn btn-outline-info btn-sm w-100">
                    Timetable
                  </Link>
                </div>
                <div className="col-md-3 mb-2">
                  <Link to="/reports" className="btn btn-outline-warning btn-sm w-100">
                    Reports
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TeacherDashboard;