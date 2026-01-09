import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function CourseManagement() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('courses');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');

  const courses = [
    {
      id: 'MATH-101',
      name: 'Algebra I',
      department: 'Mathematics',
      credits: 4,
      level: 'Beginner',
      instructor: 'Dr. Sarah Johnson',
      enrolled: 24,
      capacity: 30,
      status: 'active',
      semester: 'Fall 2024'
    },
    {
      id: 'SCI-201',
      name: 'Biology Fundamentals',
      department: 'Science',
      credits: 3,
      level: 'Intermediate',
      instructor: 'Prof. Michael Chen',
      enrolled: 28,
      capacity: 30,
      status: 'active',
      semester: 'Fall 2024'
    },
    {
      id: 'ENG-101',
      name: 'English Composition',
      department: 'English',
      credits: 3,
      level: 'Beginner',
      instructor: 'Dr. Emily Rodriguez',
      enrolled: 22,
      capacity: 25,
      status: 'active',
      semester: 'Fall 2024'
    },
    {
      id: 'HIST-301',
      name: 'World History',
      department: 'Social Studies',
      credits: 4,
      level: 'Advanced',
      instructor: 'Prof. James Wilson',
      enrolled: 18,
      capacity: 20,
      status: 'planning',
      semester: 'Spring 2025'
    },
    {
      id: 'CS-401',
      name: 'Computer Science Principles',
      department: 'Computer Science',
      credits: 4,
      level: 'Advanced',
      instructor: 'Dr. Robert Kim',
      enrolled: 15,
      capacity: 20,
      status: 'active',
      semester: 'Fall 2024'
    }
  ];

  const departments = ['all', 'Mathematics', 'Science', 'English', 'Social Studies', 'Computer Science', 'Arts', 'Physical Education'];

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.instructor.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDepartment = selectedDepartment === 'all' || course.department === selectedDepartment;
    return matchesSearch && matchesDepartment;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active': return { class: 'bg-success', text: 'Active' };
      case 'planning': return { class: 'bg-warning', text: 'Planning' };
      case 'archived': return { class: 'bg-secondary', text: 'Archived' };
      default: return { class: 'bg-secondary', text: status };
    }
  };

  const getLevelBadge = (level) => {
    switch (level) {
      case 'Beginner': return 'bg-info';
      case 'Intermediate': return 'bg-primary';
      case 'Advanced': return 'bg-warning';
      default: return 'bg-secondary';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Course Management</h1>
          <p className="lead">Manage academic courses, curriculum, and course offerings</p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/admin" className="btn btn-outline-primary">
            <i className="bi bi-arrow-left me-2"></i>
            Back to Admin
          </Link>
          <button className="btn btn-primary">
            <i className="bi bi-plus-circle me-2"></i>
            New Course
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>{courses.length}</h3>
              <p className="mb-0">Total Courses</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>{courses.filter(c => c.status === 'active').length}</h3>
              <p className="mb-0">Active Courses</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>{courses.reduce((sum, c) => sum + c.enrolled, 0)}</h3>
              <p className="mb-0">Total Enrolled</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>{departments.length - 1}</h3>
              <p className="mb-0">Departments</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-6">
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search courses by name, code, or instructor..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-4">
              <select
                className="form-select"
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
              >
                {departments.map(dept => (
                  <option key={dept} value={dept}>
                    {dept === 'all' ? 'All Departments' : dept}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-2">
              <button className="btn btn-outline-primary w-100">
                <i className="bi bi-filter me-2"></i>
                Filter
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Courses Table */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Course Catalog</h5>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped table-hover">
              <thead>
                <tr>
                  <th>Course Code</th>
                  <th>Course Name</th>
                  <th>Department</th>
                  <th>Instructor</th>
                  <th>Credits</th>
                  <th>Level</th>
                  <th>Enrollment</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredCourses.map(course => {
                  const statusBadge = getStatusBadge(course.status);
                  const enrollmentPercent = (course.enrolled / course.capacity) * 100;
                  
                  return (
                    <tr key={course.id}>
                      <td>
                        <strong>{course.id}</strong>
                      </td>
                      <td>
                        <div>
                          <div className="fw-bold">{course.name}</div>
                          <small className="text-muted">{course.semester}</small>
                        </div>
                      </td>
                      <td>{course.department}</td>
                      <td>{course.instructor}</td>
                      <td>
                        <span className="badge bg-light text-dark">
                          {course.credits} credits
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getLevelBadge(course.level)}`}>
                          {course.level}
                        </span>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <div className="flex-grow-1 me-3">
                            <div className="progress" style={{height: '6px'}}>
                              <div 
                                className={`progress-bar ${enrollmentPercent >= 90 ? 'bg-danger' : enrollmentPercent >= 75 ? 'bg-warning' : 'bg-success'}`}
                                style={{width: `${enrollmentPercent}%`}}
                              ></div>
                            </div>
                          </div>
                          <small>
                            {course.enrolled}/{course.capacity}
                          </small>
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${statusBadge.class}`}>
                          {statusBadge.text}
                        </span>
                      </td>
                      <td>
                        <div className="btn-group">
                          <button className="btn btn-sm btn-outline-primary">
                            <i className="bi bi-eye"></i>
                          </button>
                          <button className="btn btn-sm btn-outline-warning">
                            <i className="bi bi-pencil"></i>
                          </button>
                          <button className="btn btn-sm btn-outline-danger">
                            <i className="bi bi-archive"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {filteredCourses.length === 0 && (
            <div className="text-center py-5">
              <i className="bi bi-search display-1 text-muted mb-3"></i>
              <h4>No courses found</h4>
              <p className="text-muted">
                Try adjusting your search criteria or browse different departments.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row mt-4">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-journal-plus display-4 text-primary mb-3"></i>
              <h5>Create New Course</h5>
              <p className="text-muted">
                Add a new course to the curriculum
              </p>
              <button className="btn btn-primary">Create Course</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-upload display-4 text-success mb-3"></i>
              <h5>Bulk Import</h5>
              <p className="text-muted">
                Import multiple courses via CSV
              </p>
              <button className="btn btn-success">Import Courses</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-graph-up display-4 text-info mb-3"></i>
              <h5>Course Analytics</h5>
              <p className="text-muted">
                View enrollment trends and statistics
              </p>
              <button className="btn btn-info">View Analytics</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseManagement;