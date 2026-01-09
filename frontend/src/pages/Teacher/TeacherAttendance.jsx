import React, { useState, useEffect, useCallback } from 'react';
import {
  Container, Row, Col, Card, Table, Button, Badge,
  Alert, Spinner, Form, Modal, ProgressBar, InputGroup,
  Dropdown, Tabs, Tab, ButtonGroup
} from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import {
  // Using custom icons from Icons.jsx
  CheckCircleIcon, XCircleIcon, ClockIcon, UsersIcon,
  DownloadIcon, UploadIcon, FilterIcon, SearchIcon, SaveIcon,
  BarChartIcon, FileTextIcon, UserCheckIcon, UserXIcon,
  CalendarIcon, StudentIcon, ClassIcon, HistoryIcon,
  TrendingUpIcon, ReportIcon, BookOpenIcon
} from '../../components/Icons';
import { teacherAPI } from '../../services/teacherAPI';
import { attendanceAPI } from '../../services/attendanceAPI';
import { useAuth } from '../../context/AuthContext';

const TeacherAttendance = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [students, setStudents] = useState([]);
  const [attendance, setAttendance] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [attendanceMode, setAttendanceMode] = useState('manual');
  const [bulkStatus, setBulkStatus] = useState('present');
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);

  // Fetch teacher's classes
  useEffect(() => {
    fetchTeacherClasses();
  }, []);

  // Fetch students when class is selected
  useEffect(() => {
    if (selectedClass) {
      fetchClassStudents();
      fetchAttendanceStats();
      fetchAttendanceHistory();
    }
  }, [selectedClass, selectedDate]);

  const fetchTeacherClasses = async () => {
    try {
      const result = await teacherAPI.getClasses();
      if (result.success) {
        setClasses(result.data || []);
        if (result.data.length > 0) {
          setSelectedClass(result.data[0].id);
        }
      } else {
        setError(result.error?.message || 'Failed to load classes');
      }
    } catch (err) {
      console.error('Error fetching classes:', err);
      setError('Failed to load classes');
    }
  };

  const fetchClassStudents = async () => {
    try {
      setLoading(true);
      setError('');
      
      const result = await teacherAPI.getClassStudents(selectedClass);
      if (result.success) {
        setStudents(result.data || []);
        
        // Initialize attendance state or load existing
        const initialAttendance = {};
        result.data.forEach(student => {
          initialAttendance[student.id] = 'present';
        });
        setAttendance(initialAttendance);
        
        // Load existing attendance for the date
        await loadExistingAttendance();
      } else {
        setError(result.error?.message || 'Failed to load students');
      }
    } catch (err) {
      setError('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  const loadExistingAttendance = async () => {
    try {
      const result = await attendanceAPI.getClassAttendance(selectedClass, {
        date: selectedDate
      });
      
      if (result.success && result.data) {
        // Update attendance state with existing data
        const existingAttendance = { ...attendance };
        result.data.forEach(record => {
          if (record.student_id in existingAttendance) {
            existingAttendance[record.student_id] = record.status;
          }
        });
        setAttendance(existingAttendance);
      }
    } catch (err) {
      console.error('Error loading existing attendance:', err);
    }
  };

  const fetchAttendanceStats = async () => {
    try {
      const result = await attendanceAPI.getAttendanceReports({
        class_id: selectedClass,
        date: selectedDate
      });
      
      if (result.success) {
        setStats(result.data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchAttendanceHistory = async () => {
    try {
      const result = await attendanceAPI.getAttendanceReports({
        class_id: selectedClass,
        start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: selectedDate
      });
      
      if (result.success) {
        setHistory(result.data || []);
      }
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleAttendanceChange = (studentId, status) => {
    setAttendance(prev => ({
      ...prev,
      [studentId]: status
    }));
  };

  const handleBulkAction = (status) => {
    const newAttendance = { ...attendance };
    students.forEach(student => {
      newAttendance[student.id] = status;
    });
    setAttendance(newAttendance);
    setBulkStatus(status);
  };

  const submitAttendance = async () => {
    try {
      setSaving(true);
      setError('');

      const attendanceData = {
        class_id: selectedClass,
        date: selectedDate,
        attendance_records: Object.entries(attendance).map(([student_id, status]) => ({
          student_id,
          status,
          marked_by: currentUser.id
        }))
      };

      const result = await attendanceAPI.markAttendance(attendanceData);
      
      if (result.success) {
        setSuccess('Attendance recorded successfully!');
        setTimeout(() => setSuccess(''), 3000);
        fetchAttendanceStats();
        fetchAttendanceHistory();
      } else {
        setError(result.error?.message || 'Failed to save attendance');
      }
    } catch (err) {
      setError('Failed to save attendance');
    } finally {
      setSaving(false);
    }
  };

  const getStatusVariant = (status) => {
    const variants = {
      'present': 'success',
      'absent': 'danger',
      'late': 'warning',
      'excused': 'info'
    };
    return variants[status] || 'secondary';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'present': <CheckCircleIcon className="text-success" size={18} />,
      'absent': <XCircleIcon className="text-danger" size={18} />,
      'late': <ClockIcon className="text-warning" size={18} />,
      'excused': <UserCheckIcon className="text-info" size={18} />
    };
    return icons[status] || <UserXIcon className="text-secondary" size={18} />;
  };

  const exportAttendance = () => {
    // Implementation for exporting attendance data
    console.log('Exporting attendance data...');
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" />
          <p className="mt-3 text-muted">Loading attendance data...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">
                <BookOpenIcon className="me-2" size={24} />
                Take Attendance
              </h1>
              <p className="text-muted mb-0">
                Record and manage student attendance
              </p>
            </div>
            <div className="d-flex gap-2">
              <Button variant="outline-primary" onClick={exportAttendance}>
                <DownloadIcon className="me-2" size={16} />
                Export
              </Button>
              <Button variant="primary" onClick={submitAttendance} disabled={saving}>
                {saving ? <Spinner animation="border" size="sm" /> : <SaveIcon className="me-2" size={16} />}
                Save Attendance
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          <XCircleIcon className="me-2" size={16} />
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          <CheckCircleIcon className="me-2" size={16} />
          {success}
        </Alert>
      )}

      <Row>
        {/* Left Sidebar */}
        <Col lg={3} className="mb-4">
          {/* Class Selection */}
          <Card className="border-0 shadow-sm mb-4">
            <Card.Header className="d-flex align-items-center">
              <ClassIcon className="me-2" size={18} />
              <h6 className="mb-0">Class Selection</h6>
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Select Class</Form.Label>
                <Form.Select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                >
                  {classes.map(classItem => (
                    <option key={classItem.id} value={classItem.id}>
                      {classItem.name} - {classItem.grade_level}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>
                  <CalendarIcon className="me-2" size={16} />
                  Attendance Date
                </Form.Label>
                <Form.Control
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  max={new Date().toISOString().split('T')[0]}
                />
              </Form.Group>

              <Form.Group>
                <Form.Label>
                  <FilterIcon className="me-2" size={16} />
                  Attendance Mode
                </Form.Label>
                <div>
                  <Form.Check
                    type="radio"
                    name="attendanceMode"
                    label="Manual Entry"
                    checked={attendanceMode === 'manual'}
                    onChange={() => setAttendanceMode('manual')}
                    className="mb-2"
                  />
                  <Form.Check
                    type="radio"
                    name="attendanceMode"
                    label="Bulk Action"
                    checked={attendanceMode === 'bulk'}
                    onChange={() => setAttendanceMode('bulk')}
                  />
                </div>
              </Form.Group>
            </Card.Body>
          </Card>

          {/* Quick Stats */}
          {stats && (
            <Card className="border-0 shadow-sm">
              <Card.Header className="d-flex align-items-center">
                <BarChartIcon className="me-2" size={18} />
                <h6 className="mb-0">Today's Summary</h6>
              </Card.Header>
              <Card.Body>
                <div className="text-center mb-3">
                  <CheckCircleIcon className="text-success mb-2" size={24} />
                  <div className="h4 text-primary mb-1">{stats.present_count || 0}</div>
                  <small className="text-muted">Present</small>
                </div>
                <div className="text-center mb-3">
                  <XCircleIcon className="text-danger mb-2" size={24} />
                  <div className="h4 text-danger mb-1">{stats.absent_count || 0}</div>
                  <small className="text-muted">Absent</small>
                </div>
                <div className="text-center mb-3">
                  <ClockIcon className="text-warning mb-2" size={24} />
                  <div className="h4 text-warning mb-1">{stats.late_count || 0}</div>
                  <small className="text-muted">Late</small>
                </div>
                <div className="text-center">
                  <TrendingUpIcon className="text-success mb-2" size={24} />
                  <div className="h4 text-success mb-1">{stats.attendance_rate || 0}%</div>
                  <small className="text-muted">Attendance Rate</small>
                </div>
              </Card.Body>
            </Card>
          )}
        </Col>

        {/* Main Content */}
        <Col lg={9}>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0 d-flex align-items-center">
                  <StudentIcon className="me-2" size={20} />
                  Student Attendance
                  {selectedClass && (
                    <span className="text-muted ms-2">
                      • {students.length} students
                    </span>
                  )}
                </h5>
                {attendanceMode === 'bulk' && (
                  <ButtonGroup size="sm">
                    <Button
                      variant={bulkStatus === 'present' ? 'success' : 'outline-success'}
                      onClick={() => handleBulkAction('present')}
                    >
                      <CheckCircleIcon className="me-1" size={14} />
                      Mark All Present
                    </Button>
                    <Button
                      variant={bulkStatus === 'absent' ? 'danger' : 'outline-danger'}
                      onClick={() => handleBulkAction('absent')}
                    >
                      <XCircleIcon className="me-1" size={14} />
                      Mark All Absent
                    </Button>
                    <Button
                      variant={bulkStatus === 'late' ? 'warning' : 'outline-warning'}
                      onClick={() => handleBulkAction('late')}
                    >
                      <ClockIcon className="me-1" size={14} />
                      Mark All Late
                    </Button>
                  </ButtonGroup>
                )}
              </div>
            </Card.Header>
            <Card.Body className="p-0">
              {students.length > 0 ? (
                <div className="table-responsive">
                  <Table className="mb-0">
                    <thead className="bg-light">
                      <tr>
                        <th>Student</th>
                        <th>Admission No.</th>
                        <th>Grade</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {students.map(student => (
                        <tr key={student.id}>
                          <td>
                            <div className="fw-semibold d-flex align-items-center">
                              <UserCheckIcon className="me-2 text-muted" size={16} />
                              {student.full_name}
                            </div>
                            <small className="text-muted">{student.email}</small>
                          </td>
                          <td>
                            <code>{student.admission_number}</code>
                          </td>
                          <td>
                            <Badge bg="secondary">{student.grade_level}</Badge>
                          </td>
                          <td>
                            <div className="d-flex align-items-center">
                              {getStatusIcon(attendance[student.id])}
                              <Badge bg={getStatusVariant(attendance[student.id])} className="ms-2">
                                {attendance[student.id]}
                              </Badge>
                            </div>
                          </td>
                          <td>
                            <ButtonGroup size="sm">
                              <Button
                                variant={attendance[student.id] === 'present' ? 'success' : 'outline-success'}
                                onClick={() => handleAttendanceChange(student.id, 'present')}
                                title="Mark Present"
                              >
                                <CheckCircleIcon size={14} />
                              </Button>
                              <Button
                                variant={attendance[student.id] === 'absent' ? 'danger' : 'outline-danger'}
                                onClick={() => handleAttendanceChange(student.id, 'absent')}
                                title="Mark Absent"
                              >
                                <XCircleIcon size={14} />
                              </Button>
                              <Button
                                variant={attendance[student.id] === 'late' ? 'warning' : 'outline-warning'}
                                onClick={() => handleAttendanceChange(student.id, 'late')}
                                title="Mark Late"
                              >
                                <ClockIcon size={14} />
                              </Button>
                              <Button
                                variant={attendance[student.id] === 'excused' ? 'info' : 'outline-info'}
                                onClick={() => handleAttendanceChange(student.id, 'excused')}
                                title="Mark Excused"
                              >
                                <UserCheckIcon size={14} />
                              </Button>
                            </ButtonGroup>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-5">
                  <UsersIcon size={48} className="text-muted mb-3" />
                  <h5 className="text-muted">No Students Found</h5>
                  <p className="text-muted">Select a class to view students</p>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Attendance History */}
          {history.length > 0 && (
            <Card className="border-0 shadow-sm mt-4">
              <Card.Header className="d-flex align-items-center">
                <HistoryIcon className="me-2" size={18} />
                <h6 className="mb-0">Recent Attendance</h6>
              </Card.Header>
              <Card.Body>
                <div className="table-responsive">
                  <Table size="sm">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Present</th>
                        <th>Absent</th>
                        <th>Late</th>
                        <th>Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.slice(0, 5).map((record, index) => (
                        <tr key={index}>
                          <td>
                            <div className="d-flex align-items-center">
                              <CalendarIcon className="me-2 text-muted" size={14} />
                              {new Date(record.date).toLocaleDateString()}
                            </div>
                          </td>
                          <td className="text-success">
                            <CheckCircleIcon className="me-1" size={14} />
                            {record.present_count}
                          </td>
                          <td className="text-danger">
                            <XCircleIcon className="me-1" size={14} />
                            {record.absent_count}
                          </td>
                          <td className="text-warning">
                            <ClockIcon className="me-1" size={14} />
                            {record.late_count}
                          </td>
                          <td>
                            <Badge bg={record.attendance_rate >= 90 ? 'success' : 'warning'}>
                              {record.attendance_rate}%
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default TeacherAttendance;