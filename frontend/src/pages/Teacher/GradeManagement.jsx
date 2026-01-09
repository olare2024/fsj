import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function GradeManagement() {
  const { currentUser } = useAuth();
  const [activeClass, setActiveClass] = useState('grade7a-math');
  const [students, setStudents] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [grades, setGrades] = useState({});

  const teacherClasses = [
    { id: 'grade7a-math', name: 'Grade 7A Mathematics', curriculum: 'CBC', students: 35 },
    { id: 'grade8c-math', name: 'Grade 8C Mathematics', curriculum: 'CBC', students: 30 },
    { id: 'grade9b-physics', name: 'Grade 9B Physics', curriculum: 'IGCSE', students: 28 },
    { id: 'grade10a-addmath', name: 'Grade 10A Additional Math', curriculum: 'IGCSE', students: 32 }
  ];

  // Mock data - in real app, this would come from API
  useEffect(() => {
    // Mock students data
    const mockStudents = Array.from({ length: teacherClasses.find(c => c.id === activeClass)?.students || 30 }, (_, i) => ({
      id: i + 1,
      name: `Student ${i + 1}`,
      admission: `DEL${1000 + i}`,
      average: Math.floor(Math.random() * 30) + 70
    }));

    // Mock assignments
    const mockAssignments = [
      { id: 1, name: 'Algebra Basics', type: 'Homework', maxScore: 20, weight: 10, dueDate: '2024-01-10' },
      { id: 2, name: 'Geometry Quiz', type: 'Quiz', maxScore: 15, weight: 15, dueDate: '2024-01-15' },
      { id: 3, name: 'Mid-Term Exam', type: 'Exam', maxScore: 100, weight: 30, dueDate: '2024-01-25' },
      { id: 4, name: 'Problem Solving', type: 'Project', maxScore: 25, weight: 20, dueDate: '2024-02-01' }
    ];

    // Mock grades
    const mockGrades = {};
    mockStudents.forEach(student => {
      mockGrades[student.id] = {};
      mockAssignments.forEach(assignment => {
        mockGrades[student.id][assignment.id] = Math.floor(Math.random() * assignment.maxScore);
      });
    });

    setStudents(mockStudents);
    setAssignments(mockAssignments);
    setGrades(mockGrades);
  }, [activeClass]);

  const handleGradeChange = (studentId, assignmentId, value) => {
    setGrades(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [assignmentId]: value === '' ? '' : Math.min(Number(value), assignments.find(a => a.id === assignmentId)?.maxScore || 100)
      }
    }));
  };

  const calculateStudentAverage = (studentId) => {
    const studentGrades = grades[studentId];
    if (!studentGrades) return 0;

    let totalWeighted = 0;
    let totalWeight = 0;

    assignments.forEach(assignment => {
      const grade = studentGrades[assignment.id];
      if (grade !== undefined && grade !== '') {
        const percentage = (grade / assignment.maxScore) * 100;
        totalWeighted += percentage * assignment.weight;
        totalWeight += assignment.weight;
      }
    });

    return totalWeight > 0 ? (totalWeighted / totalWeight).toFixed(1) : 0;
  };

  const getGradeColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 70) return 'primary';
    if (percentage >= 60) return 'warning';
    return 'danger';
  };

  const saveGrades = () => {
    // In real app, this would make an API call
    alert('Grades saved successfully!');
  };

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/teacher-dashboard">Teacher</Link></li>
              <li className="breadcrumb-item active">Grade Management</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">Grade Management</h1>
              <p className="lead mb-0">Manage student grades and assessments</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">
                {teacherClasses.find(c => c.id === activeClass)?.curriculum}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Class Selection */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <h5 className="mb-3">Select Class</h5>
              <div className="d-flex flex-wrap gap-3">
                {teacherClasses.map(classItem => (
                  <button
                    key={classItem.id}
                    className={`btn ${activeClass === classItem.id ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setActiveClass(classItem.id)}
                  >
                    {classItem.name}
                    <span className="badge bg-light text-dark ms-2">{classItem.students}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gradebook */}
      <div className="card">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            {teacherClasses.find(c => c.id === activeClass)?.name} - Gradebook
          </h5>
          <div>
            <button className="btn btn-light btn-sm me-2" onClick={saveGrades}>
              <i className="bi bi-save me-1"></i>
              Save Grades
            </button>
            <button className="btn btn-outline-light btn-sm">
              <i className="bi bi-download me-1"></i>
              Export
            </button>
          </div>
        </div>
        
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th rowSpan="2" className="align-middle">Student</th>
                  <th rowSpan="2" className="align-middle">Admission</th>
                  {assignments.map(assignment => (
                    <th key={assignment.id} className="text-center">
                      <div>{assignment.name}</div>
                      <small className="text-muted">
                        {assignment.type} • {assignment.maxScore} pts • {assignment.weight}%
                      </small>
                    </th>
                  ))}
                  <th rowSpan="2" className="align-middle text-center">Average</th>
                </tr>
              </thead>
              <tbody>
                {students.map(student => (
                  <tr key={student.id}>
                    <td className="fw-bold">{student.name}</td>
                    <td className="text-muted">{student.admission}</td>
                    {assignments.map(assignment => (
                      <td key={assignment.id} className="text-center">
                        <input
                          type="number"
                          className="form-control form-control-sm"
                          min="0"
                          max={assignment.maxScore}
                          value={grades[student.id]?.[assignment.id] || ''}
                          onChange={(e) => handleGradeChange(student.id, assignment.id, e.target.value)}
                          style={{width: '70px', display: 'inline-block'}}
                        />
                        <small className="text-muted d-block">
                          {grades[student.id]?.[assignment.id] ? 
                            `${((grades[student.id][assignment.id] / assignment.maxScore) * 100).toFixed(1)}%` : 
                            '-'
                          }
                        </small>
                      </td>
                    ))}
                    <td className="text-center">
                      <span className={`badge bg-${getGradeColor(calculateStudentAverage(student.id))}`}>
                        {calculateStudentAverage(student.id)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Assessment Tools */}
      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Add New Assessment</h6>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">Assessment Name</label>
                <input type="text" className="form-control" placeholder="Enter assessment name" />
              </div>
              <div className="row">
                <div className="col-md-6">
                  <label className="form-label">Type</label>
                  <select className="form-select">
                    <option>Homework</option>
                    <option>Quiz</option>
                    <option>Exam</option>
                    <option>Project</option>
                    <option>Classwork</option>
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label">Max Score</label>
                  <input type="number" className="form-control" placeholder="100" />
                </div>
              </div>
              <div className="row mt-2">
                <div className="col-md-6">
                  <label className="form-label">Weight (%)</label>
                  <input type="number" className="form-control" placeholder="10" />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Due Date</label>
                  <input type="date" className="form-control" />
                </div>
              </div>
              <button className="btn btn-primary w-100 mt-3">
                Create Assessment
              </button>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Class Statistics</h6>
            </div>
            <div className="card-body">
              <div className="row text-center">
                <div className="col-4">
                  <div className="display-6 fw-bold text-primary">
                    {students.length}
                  </div>
                  <small className="text-muted">Students</small>
                </div>
                <div className="col-4">
                  <div className="display-6 fw-bold text-success">
                    {assignments.length}
                  </div>
                  <small className="text-muted">Assessments</small>
                </div>
                <div className="col-4">
                  <div className="display-6 fw-bold text-info">
                    {(() => {
                      const total = students.reduce((sum, student) => sum + parseFloat(calculateStudentAverage(student.id)), 0);
                      return (total / students.length).toFixed(1);
                    })()}%
                  </div>
                  <small className="text-muted">Class Average</small>
                </div>
              </div>
              
              <div className="mt-3">
                <h6>Grade Distribution</h6>
                <div className="small">
                  <div className="d-flex justify-content-between">
                    <span>A (80-100%)</span>
                    <span>
                      {students.filter(s => calculateStudentAverage(s.id) >= 80).length} students
                    </span>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>B (70-79%)</span>
                    <span>
                      {students.filter(s => calculateStudentAverage(s.id) >= 70 && calculateStudentAverage(s.id) < 80).length} students
                    </span>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>C (60-69%)</span>
                    <span>
                      {students.filter(s => calculateStudentAverage(s.id) >= 60 && calculateStudentAverage(s.id) < 70).length} students
                    </span>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>D (Below 60%)</span>
                    <span>
                      {students.filter(s => calculateStudentAverage(s.id) < 60).length} students
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Curriculum Specific Tools */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h6 className="mb-0">
                {teacherClasses.find(c => c.id === activeClass)?.curriculum === 'CBC' ? 
                 'CBC Competency Assessment' : 'Cambridge Grade Analysis'}
              </h6>
            </div>
            <div className="card-body">
              {teacherClasses.find(c => c.id === activeClass)?.curriculum === 'CBC' ? (
                <div>
                  <p className="mb-3">
                    Use the CBC competency-based assessment tools to evaluate student progress against specific competencies.
                  </p>
                  <div className="row">
                    <div className="col-md-4">
                      <button className="btn btn-outline-success w-100 mb-2">
                        <i className="bi bi-clipboard-data me-2"></i>
                        Competency Rubrics
                      </button>
                    </div>
                    <div className="col-md-4">
                      <button className="btn btn-outline-success w-100 mb-2">
                        <i className="bi bi-graph-up me-2"></i>
                        Progress Tracking
                      </button>
                    </div>
                    <div className="col-md-4">
                      <button className="btn btn-outline-success w-100 mb-2">
                        <i className="bi bi-file-text me-2"></i>
                        Generate Reports
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  <p className="mb-3">
                    Cambridge IGCSE grade analysis and prediction tools for university preparation.
                  </p>
                  <div className="row">
                    <div className="col-md-4">
                      <button className="btn btn-outline-primary w-100 mb-2">
                        <i className="bi bi-award me-2"></i>
                        Grade Prediction
                      </button>
                    </div>
                    <div className="col-md-4">
                      <button className="btn btn-outline-primary w-100 mb-2">
                        <i className="bi bi-bullseye me-2"></i>
                        Target Setting
                      </button>
                    </div>
                    <div className="col-md-4">
                      <button className="btn btn-outline-primary w-100 mb-2">
                        <i className="bi bi-arrow-up-right me-2"></i>
                        University Pathways
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GradeManagement;