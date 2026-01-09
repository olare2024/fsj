import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function ChildProgress() {
  const { currentUser } = useAuth();
  const [activeChild, setActiveChild] = useState('child1');
  const [activeTab, setActiveTab] = useState('overview');
  const [children, setChildren] = useState([]);
  const [academicData, setAcademicData] = useState({});
  const [attendanceData, setAttendanceData] = useState({});

  // Mock data - in real app, this would come from API
  useEffect(() => {
    // Mock children data
    const mockChildren = [
      {
        id: 'child1',
        name: 'Sarah Johnson',
        grade: 'Grade 7A',
        curriculum: 'CBC',
        admission: 'DEL2024001',
        photo: '/images/students/sarah.jpg'
      },
      {
        id: 'child2', 
        name: 'David Johnson',
        grade: 'Grade 9B',
        curriculum: 'IGCSE',
        admission: 'DEL2024002',
        photo: '/images/students/david.jpg'
      }
    ];

    // Mock academic data
    const mockAcademicData = {
      child1: {
        overallAverage: 78.5,
        term: 'Term 1 2024',
        subjects: [
          { name: 'Mathematics', grade: 82, teacher: 'Mr. Robert Mutiso', trend: 'up' },
          { name: 'English', grade: 76, teacher: 'Mrs. Grace Mwende', trend: 'stable' },
          { name: 'Science', grade: 85, teacher: 'Dr. James Kariuki', trend: 'up' },
          { name: 'Social Studies', grade: 71, teacher: 'Mrs. Amina Hassan', trend: 'down' },
          { name: 'Kiswahili', grade: 80, teacher: 'Mr. James Ochieng', trend: 'stable' }
        ],
        competencies: [
          { area: 'Communication', level: 'Proficient', progress: 85 },
          { area: 'Critical Thinking', level: 'Developing', progress: 70 },
          { area: 'Creativity', level: 'Proficient', progress: 88 },
          { area: 'Collaboration', level: 'Advanced', progress: 92 }
        ]
      },
      child2: {
        overallAverage: 85.2,
        term: 'Term 1 2024',
        subjects: [
          { name: 'Physics', grade: 88, teacher: 'Dr. David Kimani', trend: 'up' },
          { name: 'Chemistry', grade: 82, teacher: 'Prof. Sarah Mwangi', trend: 'stable' },
          { name: 'Mathematics', grade: 90, teacher: 'Mr. Robert Mutiso', trend: 'up' },
          { name: 'English', grade: 81, teacher: 'Mrs. Grace Mwende', trend: 'stable' },
          { name: 'Computer Science', grade: 85, teacher: 'Ms. Linda Chebet', trend: 'up' }
        ],
        predictions: [
          { subject: 'Physics', predictedGrade: 'A', confidence: 'High' },
          { subject: 'Chemistry', predictedGrade: 'A-', confidence: 'Medium' },
          { subject: 'Mathematics', predictedGrade: 'A*', confidence: 'High' },
          { subject: 'English', predictedGrade: 'B+', confidence: 'Medium' }
        ]
      }
    };

    // Mock attendance data
    const mockAttendanceData = {
      child1: {
        overall: 94,
        term: {
          present: 45,
          absent: 2,
          late: 3,
          excused: 1
        },
        recent: [
          { date: '2024-01-15', status: 'Present', subject: 'All' },
          { date: '2024-01-14', status: 'Late', subject: 'Mathematics' },
          { date: '2024-01-13', status: 'Present', subject: 'All' },
          { date: '2024-01-12', status: 'Absent', subject: 'All' },
          { date: '2024-01-11', status: 'Present', subject: 'All' }
        ]
      },
      child2: {
        overall: 98,
        term: {
          present: 48,
          absent: 0,
          late: 1,
          excused: 1
        },
        recent: [
          { date: '2024-01-15', status: 'Present', subject: 'All' },
          { date: '2024-01-14', status: 'Present', subject: 'All' },
          { date: '2024-01-13', status: 'Excused', subject: 'Physics' },
          { date: '2024-01-12', status: 'Present', subject: 'All' },
          { date: '2024-01-11', status: 'Present', subject: 'All' }
        ]
      }
    };

    setChildren(mockChildren);
    setAcademicData(mockAcademicData);
    setAttendanceData(mockAttendanceData);
  }, []);

  const getGradeColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 70) return 'primary';
    if (percentage >= 60) return 'warning';
    return 'danger';
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return 'bi-arrow-up-circle text-success';
      case 'down': return 'bi-arrow-down-circle text-danger';
      default: return 'bi-dash-circle text-secondary';
    }
  };

  const currentChild = children.find(child => child.id === activeChild);
  const currentAcademic = academicData[activeChild];
  const currentAttendance = attendanceData[activeChild];

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/parent-dashboard">Parent</Link></li>
              <li className="breadcrumb-item active">Child Progress</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">Child Progress Tracking</h1>
              <p className="lead mb-0">Monitor your child's academic performance and attendance</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">
                {currentChild?.curriculum} Curriculum
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Child Selection */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <h5 className="mb-3">Select Child</h5>
              <div className="d-flex flex-wrap gap-3">
                {children.map(child => (
                  <button
                    key={child.id}
                    className={`btn ${activeChild === child.id ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setActiveChild(child.id)}
                  >
                    <div className="d-flex align-items-center">
                      <div className="child-avatar bg-light rounded-circle d-flex align-items-center justify-content-center me-2"
                           style={{width: '40px', height: '40px'}}>
                        <i className="bi bi-person text-muted"></i>
                      </div>
                      <div className="text-start">
                        <div className="fw-bold">{child.name}</div>
                        <small>{child.grade} • {child.curriculum}</small>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {currentChild && currentAcademic && (
        <>
          {/* Quick Stats */}
          <div className="row mb-4">
            <div className="col-md-3 col-6 mb-3">
              <div className="card border-0 bg-success text-white">
                <div className="card-body text-center">
                  <div className="display-6 fw-bold">{currentAcademic.overallAverage}%</div>
                  <div>Overall Average</div>
                </div>
              </div>
            </div>
            <div className="col-md-3 col-6 mb-3">
              <div className="card border-0 bg-primary text-white">
                <div className="card-body text-center">
                  <div className="display-6 fw-bold">{currentAttendance?.overall}%</div>
                  <div>Attendance Rate</div>
                </div>
              </div>
            </div>
            <div className="col-md-3 col-6 mb-3">
              <div className="card border-0 bg-info text-white">
                <div className="card-body text-center">
                  <div className="display-6 fw-bold">
                    {currentAcademic.subjects?.filter(s => s.grade >= 80).length || 0}
                  </div>
                  <div>Subjects A/A+</div>
                </div>
              </div>
            </div>
            <div className="col-md-3 col-6 mb-3">
              <div className="card border-0 bg-warning text-white">
                <div className="card-body text-center">
                  <div className="display-6 fw-bold">
                    {currentAcademic.competencies?.filter(c => c.level === 'Proficient' || c.level === 'Advanced').length || 0}
                  </div>
                  <div>Strong Competencies</div>
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
                    className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                  >
                    <i className="bi bi-speedometer2 me-2"></i>
                    Overview
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${activeTab === 'academics' ? 'active' : ''}`}
                    onClick={() => setActiveTab('academics')}
                  >
                    <i className="bi bi-journal-text me-2"></i>
                    Academic Performance
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${activeTab === 'attendance' ? 'active' : ''}`}
                    onClick={() => setActiveTab('attendance')}
                  >
                    <i className="bi bi-clipboard-check me-2"></i>
                    Attendance
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${activeTab === 'reports' ? 'active' : ''}`}
                    onClick={() => setActiveTab('reports')}
                  >
                    <i className="bi bi-graph-up me-2"></i>
                    Reports
                  </button>
                </li>
              </ul>
            </div>

            <div className="card-body">
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="row">
                  <div className="col-md-6">
                    <h5>Recent Academic Performance</h5>
                    <div className="card">
                      <div className="card-body">
                        {currentAcademic.subjects?.slice(0, 3).map((subject, index) => (
                          <div key={index} className="d-flex justify-content-between align-items-center border-bottom pb-2 mb-2">
                            <div>
                              <strong>{subject.name}</strong>
                              <div className="small text-muted">{subject.teacher}</div>
                            </div>
                            <div className="text-end">
                              <span className={`badge bg-${getGradeColor(subject.grade)}`}>
                                {subject.grade}%
                              </span>
                              <div>
                                <i className={`bi ${getTrendIcon(subject.trend)}`}></i>
                              </div>
                            </div>
                          </div>
                        ))}
                        <Link to="#" className="btn btn-outline-primary btn-sm w-100">
                          View All Subjects
                        </Link>
                      </div>
                    </div>

                    {currentChild.curriculum === 'CBC' && currentAcademic.competencies && (
                      <>
                        <h5 className="mt-4">Key Competencies</h5>
                        <div className="card">
                          <div className="card-body">
                            {currentAcademic.competencies.map((competency, index) => (
                              <div key={index} className="mb-3">
                                <div className="d-flex justify-content-between mb-1">
                                  <span>{competency.area}</span>
                                  <span className="badge bg-secondary">{competency.level}</span>
                                </div>
                                <div className="progress">
                                  <div 
                                    className="progress-bar" 
                                    style={{width: `${competency.progress}%`}}
                                  >
                                    {competency.progress}%
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    )}
                  </div>

                  <div className="col-md-6">
                    <h5>Attendance Summary</h5>
                    <div className="card">
                      <div className="card-body">
                        <div className="row text-center mb-3">
                          <div className="col-4">
                            <div className="text-success fw-bold">{currentAttendance?.term?.present}</div>
                            <small>Present</small>
                          </div>
                          <div className="col-4">
                            <div className="text-danger fw-bold">{currentAttendance?.term?.absent}</div>
                            <small>Absent</small>
                          </div>
                          <div className="col-4">
                            <div className="text-warning fw-bold">{currentAttendance?.term?.late}</div>
                            <small>Late</small>
                          </div>
                        </div>
                        
                        <h6>Recent Attendance</h6>
                        {currentAttendance?.recent?.map((record, index) => (
                          <div key={index} className="d-flex justify-content-between border-bottom pb-1 mb-1">
                            <span>{new Date(record.date).toLocaleDateString()}</span>
                            <span className={`badge ${
                              record.status === 'Present' ? 'bg-success' :
                              record.status === 'Absent' ? 'bg-danger' :
                              record.status === 'Late' ? 'bg-warning' : 'bg-info'
                            }`}>
                              {record.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <h5 className="mt-4">Upcoming Events</h5>
                    <div className="card">
                      <div className="card-body">
                        <div className="d-flex justify-content-between border-bottom pb-2 mb-2">
                          <div>
                            <strong>Parent-Teacher Meeting</strong>
                            <div className="small text-muted">January 25, 2024</div>
                          </div>
                          <button className="btn btn-primary btn-sm">RSVP</button>
                        </div>
                        <div className="d-flex justify-content-between border-bottom pb-2 mb-2">
                          <div>
                            <strong>Science Fair</strong>
                            <div className="small text-muted">February 15, 2024</div>
                          </div>
                          <button className="btn btn-outline-primary btn-sm">Details</button>
                        </div>
                        <div className="d-flex justify-content-between">
                          <div>
                            <strong>Term 1 Exams</strong>
                            <div className="small text-muted">March 1-10, 2024</div>
                          </div>
                          <button className="btn btn-outline-primary btn-sm">Schedule</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Academics Tab */}
              {activeTab === 'academics' && (
                <div>
                  <h5>Subject Performance - {currentAcademic.term}</h5>
                  <div className="table-responsive">
                    <table className="table table-bordered">
                      <thead className="table-light">
                        <tr>
                          <th>Subject</th>
                          <th>Teacher</th>
                          <th>Grade</th>
                          <th>Trend</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {currentAcademic.subjects?.map((subject, index) => (
                          <tr key={index}>
                            <td className="fw-bold">{subject.name}</td>
                            <td>{subject.teacher}</td>
                            <td>
                              <span className={`badge bg-${getGradeColor(subject.grade)}`}>
                                {subject.grade}%
                              </span>
                            </td>
                            <td>
                              <i className={`bi ${getTrendIcon(subject.trend)}`}></i>
                            </td>
                            <td>
                              <button className="btn btn-outline-primary btn-sm">
                                Details
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {currentChild.curriculum === 'IGCSE' && currentAcademic.predictions && (
                    <>
                      <h5 className="mt-4">IGCSE Grade Predictions</h5>
                      <div className="row">
                        {currentAcademic.predictions.map((prediction, index) => (
                          <div key={index} className="col-md-3 mb-3">
                            <div className="card text-center">
                              <div className="card-body">
                                <h6>{prediction.subject}</h6>
                                <div className="display-6 fw-bold text-primary">
                                  {prediction.predictedGrade}
                                </div>
                                <span className={`badge ${
                                  prediction.confidence === 'High' ? 'bg-success' : 'bg-warning'
                                }`}>
                                  {prediction.confidence} Confidence
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Attendance Tab */}
              {activeTab === 'attendance' && currentAttendance && (
                <div>
                  <h5>Attendance Details - {currentAcademic.term}</h5>
                  <div className="row">
                    <div className="col-md-8">
                      <div className="card">
                        <div className="card-body">
                          <div className="table-responsive">
                            <table className="table table-bordered">
                              <thead className="table-light">
                                <tr>
                                  <th>Date</th>
                                  <th>Status</th>
                                  <th>Subject/Period</th>
                                  <th>Notes</th>
                                </tr>
                              </thead>
                              <tbody>
                                {currentAttendance.recent?.map((record, index) => (
                                  <tr key={index}>
                                    <td>{new Date(record.date).toLocaleDateString()}</td>
                                    <td>
                                      <span className={`badge ${
                                        record.status === 'Present' ? 'bg-success' :
                                        record.status === 'Absent' ? 'bg-danger' :
                                        record.status === 'Late' ? 'bg-warning' : 'bg-info'
                                      }`}>
                                        {record.status}
                                      </span>
                                    </td>
                                    <td>{record.subject}</td>
                                    <td>
                                      <button className="btn btn-outline-secondary btn-sm">
                                        View Notes
                                      </button>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="card">
                        <div className="card-header bg-primary text-white">
                          <h6 className="mb-0">Attendance Summary</h6>
                        </div>
                        <div className="card-body">
                          <div className="text-center mb-3">
                            <div className="display-4 fw-bold text-primary">
                              {currentAttendance.overall}%
                            </div>
                            <div>Overall Attendance Rate</div>
                          </div>
                          
                          <div className="mb-3">
                            <strong>Term Statistics:</strong>
                            <div className="small">
                              <div>Present: {currentAttendance.term.present} days</div>
                              <div>Absent: {currentAttendance.term.absent} days</div>
                              <div>Late: {currentAttendance.term.late} days</div>
                              <div>Excused: {currentAttendance.term.excused} days</div>
                            </div>
                          </div>
                          
                          <button className="btn btn-outline-primary btn-sm w-100">
                            Download Report
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Reports Tab */}
              {activeTab === 'reports' && (
                <div>
                  <h5>Progress Reports</h5>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <div className="card">
                        <div className="card-body text-center">
                          <i className="bi bi-file-text display-4 text-primary mb-3"></i>
                          <h5>Term Report</h5>
                          <p className="card-text">
                            Comprehensive term report including academic performance and teacher comments.
                          </p>
                          <button className="btn btn-primary">
                            Download Term Report
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6 mb-3">
                      <div className="card">
                        <div className="card-body text-center">
                          <i className="bi bi-graph-up display-4 text-success mb-3"></i>
                          <h5>Progress Analysis</h5>
                          <p className="card-text">
                            Detailed analysis of academic progress and growth over time.
                          </p>
                          <button className="btn btn-success">
                            View Progress Analysis
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <div className="card">
                        <div className="card-body text-center">
                          <i className="bi bi-clipboard-data display-4 text-warning mb-3"></i>
                          <h5>Attendance Report</h5>
                          <p className="card-text">
                            Detailed attendance report with patterns and trends analysis.
                          </p>
                          <button className="btn btn-warning">
                            Download Attendance Report
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6 mb-3">
                      <div className="card">
                        <div className="card-body text-center">
                          <i className="bi bi-person-check display-4 text-info mb-3"></i>
                          <h5>Teacher Feedback</h5>
                          <p className="card-text">
                            Consolidated feedback from all subject teachers.
                          </p>
                          <button className="btn btn-info">
                            View Teacher Feedback
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="row mt-4">
            <div className="col-12">
              <div className="card bg-light">
                <div className="card-body">
                  <h6 className="mb-3">Quick Actions</h6>
                  <div className="row">
                    <div className="col-md-3 mb-2">
                      <Link to="/parent-meetings" className="btn btn-outline-primary btn-sm w-100">
                        Schedule Meeting
                      </Link>
                    </div>
                    <div className="col-md-3 mb-2">
                      <button className="btn btn-outline-success btn-sm w-100">
                        Contact Teacher
                      </button>
                    </div>
                    <div className="col-md-3 mb-2">
                      <button className="btn btn-outline-info btn-sm w-100">
                        Request Report
                      </button>
                    </div>
                    <div className="col-md-3 mb-2">
                      <button className="btn btn-outline-warning btn-sm w-100">
                        Set Goals
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ChildProgress;