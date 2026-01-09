import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function ClassManagement() {
  const { currentUser } = useAuth();
  const [selectedSemester, setSelectedSemester] = useState('fall-2024');
  const [selectedTeacher, setSelectedTeacher] = useState('all');

  const classes = [
    {
      id: 'CLS-001',
      course: 'Algebra I',
      courseCode: 'MATH-101',
      teacher: 'Dr. Sarah Johnson',
      room: 'Room 201',
      schedule: 'Mon, Wed, Fri 9:00-10:00 AM',
      students: 24,
      capacity: 30,
      status: 'active'
    },
    {
      id: 'CLS-002',
      course: 'Biology Fundamentals',
      courseCode: 'SCI-201',
      teacher: 'Prof. Michael Chen',
      room: 'Science Lab 105',
      schedule: 'Tue, Thu 10:00-11:30 AM',
      students: 28,
      capacity: 30,
      status: 'active'
    },
    {
      id: 'CLS-003',
      course: 'English Composition',
      courseCode: 'ENG-101',
      teacher: 'Dr. Emily Rodriguez',
      room: 'Room 305',
      schedule: 'Mon, Wed, Fri 11:00-12:00 PM',
      students: 22,
      capacity: 25,
      status: 'active'
    },
    {
      id: 'CLS-004',
      course: 'Computer Science Principles',
      courseCode: 'CS-401',
      teacher: 'Dr. Robert Kim',
      room: 'Computer Lab 102',
      schedule: 'Tue, Thu 1:00-2:30 PM',
      students: 15,
      capacity: 20,
      status: 'active'
    },
    {
      id: 'CLS-005',
      course: 'World History',
      courseCode: 'HIST-301',
      teacher: 'Prof. James Wilson',
      room: 'Room 410',
      schedule: 'Mon, Wed 2:00-3:30 PM',
      students: 18,
      capacity: 20,
      status: 'planning'
    }
  ];

  const teachers = ['all', 'Dr. Sarah Johnson', 'Prof. Michael Chen', 'Dr. Emily Rodriguez', 'Dr. Robert Kim', 'Prof. James Wilson'];

  const filteredClasses = classes.filter(cls => {
    const matchesTeacher = selectedTeacher === 'all' || cls.teacher === selectedTeacher;
    return matchesTeacher;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active': return 'bg-success';
      case 'planning': return 'bg-warning';
      case 'cancelled': return 'bg-danger';
      default: return 'bg-secondary';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Class Management</h1>
          <p className="lead">Manage class sections, schedules, and room assignments</p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/admin" className="btn btn-outline-primary">
            <i className="bi bi-arrow-left me-2"></i>
            Back to Admin
          </Link>
          <button className="btn btn-primary">
            <i className="bi bi-plus-circle me-2"></i>
            New Class
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-4">
              <label className="form-label">Semester</label>
              <select
                className="form-select"
                value={selectedSemester}
                onChange={(e) => setSelectedSemester(e.target.value)}
              >
                <option value="fall-2024">Fall 2024</option>
                <option value="spring-2024">Spring 2024</option>
                <option value="fall-2023">Fall 2023</option>
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Teacher</label>
              <select
                className="form-select"
                value={selectedTeacher}
                onChange={(e) => setSelectedTeacher(e.target.value)}
              >
                {teachers.map(teacher => (
                  <option key={teacher} value={teacher}>
                    {teacher === 'all' ? 'All Teachers' : teacher}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Actions</label>
              <div className="d-flex gap-2">
                <button className="btn btn-outline-primary flex-fill">
                  <i className="bi bi-filter me-2"></i>
                  Apply Filters
                </button>
                <button className="btn btn-outline-secondary">
                  <i className="bi bi-arrow-clockwise"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Classes Grid */}
      <div className="row g-4">
        {filteredClasses.map(cls => {
          const enrollmentPercent = (cls.students / cls.capacity) * 100;
          
          return (
            <div key={cls.id} className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h6 className="mb-0">{cls.courseCode}</h6>
                  <span className={`badge ${getStatusBadge(cls.status)}`}>
                    {cls.status}
                  </span>
                </div>
                <div className="card-body">
                  <h5 className="card-title">{cls.course}</h5>
                  <p className="card-text text-muted">{cls.teacher}</p>
                  
                  <div className="class-details">
                    <div className="d-flex align-items-center mb-2">
                      <i className="bi bi-geo-alt text-primary me-2"></i>
                      <span>{cls.room}</span>
                    </div>
                    <div className="d-flex align-items-center mb-3">
                      <i className="bi bi-clock text-primary me-2"></i>
                      <span>{cls.schedule}</span>
                    </div>
                    
                    <div className="enrollment-section">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <span className="text-muted">Enrollment</span>
                        <span className="fw-bold">
                          {cls.students}/{cls.capacity}
                        </span>
                      </div>
                      <div className="progress mb-3">
                        <div 
                          className={`progress-bar ${enrollmentPercent >= 90 ? 'bg-danger' : enrollmentPercent >= 75 ? 'bg-warning' : 'bg-success'}`}
                          style={{width: `${enrollmentPercent}%`}}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="card-footer">
                  <div className="d-flex gap-2">
                    <button className="btn btn-primary btn-sm flex-fill">
                      <i className="bi bi-people me-1"></i>
                      Roster
                    </button>
                    <button className="btn btn-outline-warning btn-sm">
                      <i className="bi bi-pencil"></i>
                    </button>
                    <button className="btn btn-outline-info btn-sm">
                      <i className="bi bi-calendar"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="row mt-5">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Class Scheduling</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-calendar-plus me-2"></i>
                  Create Class Schedule
                </button>
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-arrow-left-right me-2"></i>
                  Room Assignment
                </button>
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-clock me-2"></i>
                  Time Conflict Check
                </button>
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-calendar-week me-2"></i>
                  Generate Timetable
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Class Operations</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-person-plus me-2"></i>
                  Add Students to Class
                </button>
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-people me-2"></i>
                  Manage Class Rosters
                </button>
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-graph-up me-2"></i>
                  Class Performance
                </button>
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-archive me-2"></i>
                  Archive Classes
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ClassManagement;