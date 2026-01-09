import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Grades() {
  const { currentUser } = useAuth();
  const [selectedSemester, setSelectedSemester] = useState('fall-2024');

  const gradeData = {
    'fall-2024': [
      { subject: 'Mathematics', grade: 'A-', percentage: 92, teacher: 'Mr. Johnson' },
      { subject: 'Science', grade: 'B+', percentage: 88, teacher: 'Dr. Smith' },
      { subject: 'English', grade: 'A', percentage: 95, teacher: 'Ms. Davis' },
      { subject: 'History', grade: 'B', percentage: 85, teacher: 'Mr. Wilson' }
    ],
    'spring-2024': [
      { subject: 'Mathematics', grade: 'B+', percentage: 89, teacher: 'Mr. Johnson' },
      { subject: 'Science', grade: 'A-', percentage: 91, teacher: 'Dr. Smith' },
      { subject: 'English', grade: 'A', percentage: 94, teacher: 'Ms. Davis' }
    ]
  };

  const currentGrades = gradeData[selectedSemester] || [];

  const calculateGPA = (grades) => {
    const gradePoints = {
      'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
      'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0
    };
    
    const totalPoints = grades.reduce((sum, course) => {
      return sum + (gradePoints[course.grade] || 0);
    }, 0);
    
    return (totalPoints / grades.length).toFixed(2);
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Academic Grades</h1>
          <p className="lead">Track your academic performance</p>
        </div>
        <Link to="/dashboard" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Dashboard
        </Link>
      </div>

      {/* GPA Summary */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>{calculateGPA(currentGrades)}</h3>
              <p className="mb-0">Current GPA</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>{currentGrades.filter(g => g.grade === 'A' || g.grade === 'A-').length}</h3>
              <p className="mb-0">A Grades</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>{currentGrades.length}</h3>
              <p className="mb-0">Total Courses</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>92%</h3>
              <p className="mb-0">Overall Average</p>
            </div>
          </div>
        </div>
      </div>

      {/* Semester Selector */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-6">
              <label className="form-label">Select Semester:</label>
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
            <div className="col-md-6 text-end">
              <button className="btn btn-outline-primary">
                <i className="bi bi-download me-2"></i>
                Download Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Grades Table */}
      <div className="card">
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Teacher</th>
                  <th>Grade</th>
                  <th>Percentage</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {currentGrades.map((course, index) => (
                  <tr key={index}>
                    <td>
                      <strong>{course.subject}</strong>
                    </td>
                    <td>{course.teacher}</td>
                    <td>
                      <span className={`badge bg-${getGradeColor(course.grade)}`}>
                        {course.grade}
                      </span>
                    </td>
                    <td>{course.percentage}%</td>
                    <td>
                      <span className={`badge bg-${course.percentage >= 90 ? 'success' : course.percentage >= 80 ? 'warning' : 'danger'}`}>
                        {course.percentage >= 90 ? 'Excellent' : course.percentage >= 80 ? 'Good' : 'Needs Improvement'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function getGradeColor(grade) {
  if (grade.includes('A')) return 'success';
  if (grade.includes('B')) return 'info';
  if (grade.includes('C')) return 'warning';
  return 'danger';
}

export default Grades;