import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Form, Button } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Attendance = () => {
  const { currentUser } = useAuth();
  const [attendance, setAttendance] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [loading, setLoading] = useState(true);

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  useEffect(() => {
    const fetchAttendance = async () => {
      setLoading(true);
      
      const mockAttendance = currentUser.role === 'student'
        ? [
            { date: '2024-01-15', status: 'Present', timeIn: '07:45 AM', timeOut: '03:30 PM' },
            { date: '2024-01-16', status: 'Present', timeIn: '07:50 AM', timeOut: '03:25 PM' },
            { date: '2024-01-17', status: 'Absent', timeIn: '-', timeOut: '-', reason: 'Sick' },
            { date: '2024-01-18', status: 'Late', timeIn: '08:15 AM', timeOut: '03:30 PM', reason: 'Traffic' },
            { date: '2024-01-19', status: 'Present', timeIn: '07:55 AM', timeOut: '03:28 PM' },
          ]
        : [
            // Teacher view
            { student: 'John Doe', present: 18, absent: 2, late: 1, percentage: '90%' },
            { student: 'Jane Smith', present: 20, absent: 0, late: 1, percentage: '95%' },
            { student: 'Mike Johnson', present: 17, absent: 3, late: 1, percentage: '85%' },
          ];

      setTimeout(() => {
        setAttendance(mockAttendance);
        setLoading(false);
      }, 1000);
    };

    fetchAttendance();
  }, [currentUser, selectedMonth]);

  const getStatusBadge = (status) => {
    switch(status) {
      case 'Present': return <Badge bg="success">Present</Badge>;
      case 'Absent': return <Badge bg="danger">Absent</Badge>;
      case 'Late': return <Badge bg="warning">Late</Badge>;
      default: return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading attendance...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2>Attendance Records</h2>
            <Form.Select 
              style={{ width: '200px' }} 
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
            >
              {months.map((month, index) => (
                <option key={index} value={index}>{month} 2024</option>
              ))}
            </Form.Select>
          </div>

          <Card>
            <Card.Header>
              <h5 className="mb-0">
                {currentUser.role === 'student' ? 'My Attendance' : 'Class Attendance'} - {months[selectedMonth]}
              </h5>
            </Card.Header>
            <Card.Body>
              {currentUser.role === 'student' ? (
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Status</th>
                      <th>Time In</th>
                      <th>Time Out</th>
                      <th>Remarks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendance.map((record, index) => (
                      <tr key={index}>
                        <td>{record.date}</td>
                        <td>{getStatusBadge(record.status)}</td>
                        <td>{record.timeIn}</td>
                        <td>{record.timeOut}</td>
                        <td>{record.reason || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      <th>Student Name</th>
                      <th>Present Days</th>
                      <th>Absent Days</th>
                      <th>Late Days</th>
                      <th>Attendance %</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendance.map((student, index) => (
                      <tr key={index}>
                        <td><strong>{student.student}</strong></td>
                        <td><Badge bg="success">{student.present}</Badge></td>
                        <td><Badge bg="danger">{student.absent}</Badge></td>
                        <td><Badge bg="warning">{student.late}</Badge></td>
                        <td><Badge bg="info">{student.percentage}</Badge></td>
                        <td>
                          <Button variant="outline-primary" size="sm">
                            View Details
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>

          {currentUser.role === 'student' && (
            <Row className="mt-4">
              <Col md={6}>
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Attendance Summary</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Total School Days:</span>
                      <strong>21</strong>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Days Present:</span>
                      <Badge bg="success">18</Badge>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Days Absent:</span>
                      <Badge bg="danger">2</Badge>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span>Attendance Rate:</span>
                      <Badge bg="primary">85.7%</Badge>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Attendance;