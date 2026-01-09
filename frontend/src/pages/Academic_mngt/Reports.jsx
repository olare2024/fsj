import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Button, Form, Dropdown } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Reports = () => {
  const { currentUser } = useAuth();
  const [reports, setReports] = useState([]);
  const [selectedReportType, setSelectedReportType] = useState('academic');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      setLoading(true);
      
      const mockReports = currentUser.role === 'student' 
        ? [
            {
              id: 1,
              name: 'Term 1 Report Card',
              type: 'Academic',
              date: '2024-01-30',
              status: 'Published',
              downloadUrl: '#'
            },
            {
              id: 2,
              name: 'Attendance Summary',
              type: 'Attendance',
              date: '2024-01-25',
              status: 'Published',
              downloadUrl: '#'
            },
            {
              id: 3,
              name: 'Progress Report',
              type: 'Progress',
              date: '2024-01-20',
              status: 'Published',
              downloadUrl: '#'
            },
          ]
        : [
            // Teacher/Admin view
            {
              id: 1,
              student: 'John Doe',
              report: 'Term 1 Report Card',
              type: 'Academic',
              date: '2024-01-30',
              status: 'Published'
            },
            {
              id: 2,
              student: 'Jane Smith',
              report: 'Term 1 Report Card',
              type: 'Academic',
              date: '2024-01-30',
              status: 'Published'
            },
            {
              id: 3,
              student: 'Mike Johnson',
              report: 'Attendance Summary',
              type: 'Attendance',
              date: '2024-01-25',
              status: 'Draft'
            },
          ];

      setTimeout(() => {
        setReports(mockReports);
        setLoading(false);
      }, 1000);
    };

    fetchReports();
  }, [currentUser.role]);

  const getStatusBadge = (status) => {
    switch(status) {
      case 'Published': return <Badge bg="success">Published</Badge>;
      case 'Draft': return <Badge bg="warning">Draft</Badge>;
      case 'Pending': return <Badge bg="info">Pending</Badge>;
      default: return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  const getTypeBadge = (type) => {
    switch(type) {
      case 'Academic': return <Badge bg="primary">Academic</Badge>;
      case 'Attendance': return <Badge bg="info">Attendance</Badge>;
      case 'Progress': return <Badge bg="success">Progress</Badge>;
      case 'Behavioral': return <Badge bg="warning">Behavioral</Badge>;
      default: return <Badge bg="secondary">Other</Badge>;
    }
  };

  const filteredReports = reports.filter(report => 
    selectedReportType === 'all' || report.type.toLowerCase().includes(selectedReportType.toLowerCase())
  );

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading reports...</span>
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
            <h2>Academic Reports</h2>
            <div className="d-flex gap-2">
              <Form.Select 
                style={{ width: '200px' }} 
                value={selectedReportType}
                onChange={(e) => setSelectedReportType(e.target.value)}
              >
                <option value="all">All Reports</option>
                <option value="academic">Academic</option>
                <option value="attendance">Attendance</option>
                <option value="progress">Progress</option>
                <option value="behavioral">Behavioral</option>
              </Form.Select>
              
              {currentUser.role !== 'student' && (
                <Dropdown>
                  <Dropdown.Toggle variant="primary">
                    <i className="bi bi-plus-circle"></i> Generate Report
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item>Class Performance Report</Dropdown.Item>
                    <Dropdown.Item>Attendance Summary</Dropdown.Item>
                    <Dropdown.Item>Progress Report</Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item>Custom Report</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              )}
            </div>
          </div>

          <Card>
            <Card.Header>
              <h5 className="mb-0">
                {currentUser.role === 'student' ? 'My Reports' : 'Student Reports'}
              </h5>
            </Card.Header>
            <Card.Body>
              <Table responsive striped hover>
                <thead>
                  <tr>
                    {currentUser.role !== 'student' && <th>Student</th>}
                    <th>Report Name</th>
                    <th>Type</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReports.map((report) => (
                    <tr key={report.id}>
                      {currentUser.role !== 'student' && (
                        <td><strong>{report.student}</strong></td>
                      )}
                      <td>
                        <div>
                          <strong>{currentUser.role === 'student' ? report.name : report.report}</strong>
                        </div>
                      </td>
                      <td>{getTypeBadge(report.type)}</td>
                      <td>{report.date}</td>
                      <td>{getStatusBadge(report.status)}</td>
                      <td>
                        <div className="d-flex gap-2">
                          <Button variant="outline-primary" size="sm">
                            <i className="bi bi-eye"></i> View
                          </Button>
                          <Button variant="outline-success" size="sm">
                            <i className="bi bi-download"></i> Download
                          </Button>
                          {currentUser.role !== 'student' && report.status === 'Draft' && (
                            <Button variant="outline-warning" size="sm">
                              <i className="bi bi-send"></i> Publish
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {currentUser.role === 'student' && (
            <Row className="mt-4">
              <Col md={8}>
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Report Statistics</h6>
                  </Card.Header>
                  <Card.Body>
                    <Row>
                      <Col md={6}>
                        <div className="d-flex justify-content-between mb-2">
                          <span>Total Reports:</span>
                          <strong>12</strong>
                        </div>
                        <div className="d-flex justify-content-between mb-2">
                          <span>Academic Reports:</span>
                          <Badge bg="primary">8</Badge>
                        </div>
                        <div className="d-flex justify-content-between">
                          <span>Attendance Reports:</span>
                          <Badge bg="info">3</Badge>
                        </div>
                      </Col>
                      <Col md={6}>
                        <div className="d-flex justify-content-between mb-2">
                          <span>Progress Reports:</span>
                          <Badge bg="success">4</Badge>
                        </div>
                        <div className="d-flex justify-content-between mb-2">
                          <span>Latest Report:</span>
                          <small>2024-01-30</small>
                        </div>
                        <div className="d-flex justify-content-between">
                          <span>Average Grade:</span>
                          <Badge bg="success">B+</Badge>
                        </div>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}

          {currentUser.role === 'teacher' && (
            <Row className="mt-4">
              <Col md={6}>
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Quick Actions</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="d-grid gap-2">
                      <Button variant="outline-primary">
                        Generate Class Performance Report
                      </Button>
                      <Button variant="outline-info">
                        Create Attendance Summary
                      </Button>
                      <Button variant="outline-success">
                        Export Grade Sheets
                      </Button>
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

export default Reports;