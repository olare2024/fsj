import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function AttendanceManagement() {
  const { currentUser } = useAuth();
  const [activeClass, setActiveClass] = useState('grade7a-math');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [attendance, setAttendance] = useState({});
  const [students, setStudents] = useState([]);

  const teacherClasses = [
    { id: 'grade7a-math', name: 'Grade 7A Mathematics', curriculum: 'CBC', students: 35 },
    { id: 'grade8c-math', name: 'Grade 8C Mathematics', curriculum: 'CBC', students: 30 },
    { id: 'grade9b-physics', name: 'Grade 9B Physics', curriculum: 'IGCSE', students: 28 },
    { id: 'grade10a-addmath', name: 'Grade 10A Additional Math', curriculum: 'IGCSE', students: 32 }
  ];

  const attendanceCodes = {
    present: { code: 'P', label: 'Present', color: 'success' },
    absent: { code: 'A', label: 'Absent', color: 'danger' },
    late: { code: 'L', label: 'Late', color: 'warning' },
    excused: { code: 'E', label: 'Excused', color: 'info' },
    medical: { code: 'M', label: 'Medical', color: 'secondary' }
  };

  // Mock data - in real app, this would come from API
  useEffect(() => {
    const mockStudents = Array.from({ length: teacherClasses.find(c => c.id === activeClass)?.students || 30 }, (_, i) => ({
      id: i + 1,
      name: `Student ${i + 1}`,
      admission: `DEL${1000 + i}`,
      photo: `/images/students/student${i + 1}.jpg`
    }));

    // Initialize attendance with random values for demo
    const initialAttendance = {};
    mockStudents.forEach(student => {
      initialAttendance[student.id] = Math.random() > 0.2 ? 'present' : 
                                     Math.random() > 0.5 ? 'absent' : 'present';
    });

    setStudents(mockStudents);
    setAttendance(initialAttendance);
  }, [activeClass, selectedDate]);

  const handleAttendanceChange = (studentId, status) => {
    setAttendance(prev => ({
      ...prev,
      [studentId]: status
    }));
  };

  const saveAttendance = () => {
    // In real app, this would make an API call
    const presentCount = Object.values(attendance).filter(status => status === 'present').length;
    const totalCount = students.length;
    const attendanceRate = ((presentCount / totalCount) * 100).toFixed(1);

    alert(`Attendance saved successfully!\nAttendance Rate: ${attendanceRate}%`);
  };

  const getAttendanceStats = () => {
    const present = Object.values(attendance).filter(status => status === 'present').length;
    const absent = Object.values(attendance).filter(status => status === 'absent').length;
    const late = Object.values(attendance).filter(status => status === 'late').length;
    const excused = Object.values(attendance).filter(status => status === 'excused').length;
    const medical = Object.values(attendance).filter(status => status === 'medical').length;
    const total = students.length;

    return { present, absent, late, excused, medical, total };
  };

  const stats = getAttendanceStats();

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/teacher-dashboard">Teacher</Link></li>
              <li className="breadcrumb-item active">Attendance Management</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">Attendance Management</h1>
              <p className="lead mb-0">Track and manage student attendance</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">
                {teacherClasses.find(c => c.id === activeClass)?.curriculum}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="row mb-4">
        <div className="col-md-8">
          <div className="card">
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <label className="form-label">Select Class</label>
                  <select 
                    className="form-select"
                    value={activeClass}
                    onChange={(e) => setActiveClass(e.target.value)}
                  >
                    {teacherClasses.map(classItem => (
                      <option key={classItem.id} value={classItem.id}>
                        {classItem.name} ({classItem.students} students)
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label">Date</label>
                  <input
                    type="date"
                    className="form-control"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <div className="display-4 fw-bold">
                {((stats.present / stats.total) * 100).toFixed(1)}%
              </div>
              <div>Attendance Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Attendance Statistics */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Attendance Summary</h6>
            </div>
            <div className="card-body">
              <div className="row text-center">
                <div className="col-md-2 col-4 mb-3">
                  <div className={`bg-${attendanceCodes.present.color} text-white rounded-circle p-3 mx-auto`} style={{width: '80px', height: '80px'}}>
                    <div className="fs-4 fw-bold">{stats.present}</div>
                  </div>
                  <div className="mt-2">{attendanceCodes.present.label}</div>
                </div>
                <div className="col-md-2 col-4 mb-3">
                  <div className={`bg-${attendanceCodes.absent.color} text-white rounded-circle p-3 mx-auto`} style={{width: '80px', height: '80px'}}>
                    <div className="fs-4 fw-bold">{stats.absent}</div>
                  </div>
                  <div className="mt-2">{attendanceCodes.absent.label}</div>
                </div>
                <div className="col-md-2 col-4 mb-3">
                  <div className={`bg-${attendanceCodes.late.color} text-white rounded-circle p-3 mx-auto`} style={{width: '80px', height: '80px'}}>
                    <div className="fs-4 fw-bold">{stats.late}</div>
                  </div>
                  <div className="mt-2">{attendanceCodes.late.label}</div>
                </div>
                <div className="col-md-2 col-4 mb-3">
                  <div className={`bg-${attendanceCodes.excused.color} text-white rounded-circle p-3 mx-auto`} style={{width: '80px', height: '80px'}}>
                    <div className="fs-4 fw-bold">{stats.excused}</div>
                  </div>
                  <div className="mt-2">{attendanceCodes.excused.label}</div>
                </div>
                <div className="col-md-2 col-4 mb-3">
                  <div className={`bg-${attendanceCodes.medical.color} text-white rounded-circle p-3 mx-auto`} style={{width: '80px', height: '80px'}}>
                    <div className="fs-4 fw-bold">{stats.medical}</div>
                  </div>
                  <div className="mt-2">{attendanceCodes.medical.label}</div>
                </div>
                <div className="col-md-2 col-4 mb-3">
                  <div className="bg-dark text-white rounded-circle p-3 mx-auto" style={{width: '80px', height: '80px'}}>
                    <div className="fs-4 fw-bold">{stats.total}</div>
                  </div>
                  <div className="mt-2">Total</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Attendance Recording */}
      <div className="card">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            {teacherClasses.find(c => c.id === activeClass)?.name} - Attendance for {new Date(selectedDate).toLocaleDateString()}
          </h5>
          <div>
            <button className="btn btn-light btn-sm me-2" onClick={saveAttendance}>
              <i className="bi bi-save me-1"></i>
              Save Attendance
            </button>
            <button className="btn btn-outline-light btn-sm">
              <i className="bi bi-printer me-1"></i>
              Print
            </button>
          </div>
        </div>
        
        <div className="card-body">
          <div className="row g-3">
            {students.map(student => (
              <div key={student.id} className="col-md-6 col-lg-4">
                <div className="card attendance-student-card">
                  <div className="card-body">
                    <div className="d-flex align-items-center mb-3">
                      <div className="student-avatar bg-light rounded-circle d-flex align-items-center justify-content-center me-3"
                           style={{width: '50px', height: '50px'}}>
                        <i className="bi bi-person fs-4 text-muted"></i>
                      </div>
                      <div>
                        <h6 className="mb-0">{student.name}</h6>
                        <small className="text-muted">{student.admission}</small>
                      </div>
                    </div>
                    
                    <div className="attendance-buttons">
                      <div className="btn-group w-100" role="group">
                        {Object.entries(attendanceCodes).map(([key, code]) => (
                          <button
                            key={key}
                            type="button"
                            className={`btn btn-outline-${code.color} btn-sm ${
                              attendance[student.id] === key ? 'active' : ''
                            }`}
                            onClick={() => handleAttendanceChange(student.id, key)}
                          >
                            {code.code}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mt-2 text-center">
                      <small className={`text-${attendanceCodes[attendance[student.id]]?.color || 'muted'}`}>
                        {attendanceCodes[attendance[student.id]]?.label || 'Not Marked'}
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Quick Actions</h6>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-check-all me-2"></i>
                  Mark All Present
                </button>
                <button className="btn btn-outline-secondary text-start">
                  <i className="bi bi-arrow-clockwise me-2"></i>
                  Reset All
                </button>
                <button className="btn btn-outline-info text-start">
                  <i className="bi bi-clock-history me-2"></i>
                  View Attendance History
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Attendance Reports</h6>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-file-earmark-text me-2"></i>
                  Generate Class Report
                </button>
                <button className="btn btn-outline-warning text-start">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  Absence Alerts
                </button>
                <button className="btn btn-outline-danger text-start">
                  <i className="bi bi-graph-up me-2"></i>
                  Trend Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Curriculum Specific Features */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h6 className="mb-0">
                {teacherClasses.find(c => c.id === activeClass)?.curriculum === 'CBC' ? 
                 'CBC Attendance Integration' : 'Cambridge Attendance Requirements'}
              </h6>
            </div>
            <div className="card-body">
              {teacherClasses.find(c => c.id === activeClass)?.curriculum === 'CBC' ? (
                <div className="row">
                  <div className="col-md-8">
                    <h6>CBC Competency Tracking</h6>
                    <p className="small mb-3">
                      Attendance data is integrated with CBC competency tracking. Absences may affect 
                      competency assessment completion and require make-up sessions.
                    </p>
                    <ul className="small">
                      <li>Automatic competency progress updates</li>
                      <li>Make-up session scheduling</li>
                      <li>Parent notification system</li>
                      <li>Ministry of Education compliance</li>
                    </ul>
                  </div>
                  <div className="col-md-4">
                    <button className="btn btn-success w-100 mb-2">
                      <i className="bi bi-shield-check me-2"></i>
                      CBC Compliance
                    </button>
                    <button className="btn btn-outline-success w-100">
                      <i className="bi bi-person-check me-2"></i>
                      Competency Make-up
                    </button>
                  </div>
                </div>
              ) : (
                <div className="row">
                  <div className="col-md-8">
                    <h6>Cambridge Attendance Requirements</h6>
                    <p className="small mb-3">
                      Cambridge International requires minimum attendance rates for examination eligibility. 
                      Track and maintain compliance with Cambridge regulations.
                    </p>
                    <ul className="small">
                      <li>Minimum 85% attendance for exam entry</li>
                      <li>Medical absence documentation</li>
                      <li>Examination officer reports</li>
                      <li>University reference requirements</li>
                    </ul>
                  </div>
                  <div className="col-md-4">
                    <button className="btn btn-primary w-100 mb-2">
                      <i className="bi bi-award me-2"></i>
                      Exam Eligibility
                    </button>
                    <button className="btn btn-outline-primary w-100">
                      <i className="bi bi-file-medical me-2"></i>
                      Medical Records
                    </button>
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

export default AttendanceManagement;