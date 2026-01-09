import React, { useState, useEffect } from 'react';
import {
  Container, Row, Col, Card, Table, Button, Badge,
  Alert, Spinner, Form, Modal, ProgressBar,
  Dropdown, Tabs, Tab, InputGroup
} from 'react-bootstrap';
import {
  FileTextIcon, DownloadIcon, FilterIcon, CalendarIcon, UsersIcon,
  BarChartIcon, PieChartIcon, TrendingUpIcon, EyeIcon, PrintIcon,
  ReportIcon, DocumentIcon, AnalyticsIcon, ChartIcon,
  StudentIcon, ClassIcon, HistoryIcon, SearchIcon,
  CheckCircleIcon, WarningIcon, ErrorIcon, GraphIcon
} from '../../components/Icons';
import { teacherAPI } from '../../services/teacherAPI';
import { useAuth } from '../../context/AuthContext';

const TeacherReports = () => {
  const { currentUser } = useAuth();
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchTeacherClasses();
  }, []);

  useEffect(() => {
    if (selectedClass) {
      fetchReports();
    }
  }, [selectedClass, dateRange]);

  const fetchTeacherClasses = async () => {
    try {
      const result = await teacherAPI.getClasses();
      if (result.success) {
        setClasses(result.data || []);
        if (result.data.length > 0) {
          setSelectedClass(result.data[0].id);
        }
      }
    } catch (err) {
      console.error('Error fetching classes:', err);
    }
  };

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch various reports data
      const [attendanceResult, gradesResult, assignmentsResult] = await Promise.all([
        teacherAPI.getStatistics(),
        teacherAPI.getAssignmentStatistics(),
        teacherAPI.getAssignments()
      ]);

      const reportsData = [];

      // Attendance Report
      if (attendanceResult.success) {
        reportsData.push({
          id: 'attendance',
          type: 'attendance',
          title: 'Class Attendance Summary',
          description: 'Weekly attendance overview and trends',
          date: new Date().toISOString(),
          data: attendanceResult.data,
          status: 'ready'
        });
      }

      // Grades Report
      if (gradesResult.success) {
        reportsData.push({
          id: 'grades',
          type: 'grades',
          title: 'Academic Performance Report',
          description: 'Student grades and performance analysis',
          date: new Date().toISOString(),
          data: gradesResult.data,
          status: 'ready'
        });
      }

      // Assignments Report
      if (assignmentsResult.success) {
        reportsData.push({
          id: 'assignments',
          type: 'assignments',
          title: 'Assignments Overview',
          description: 'Assignment completion and submission rates',
          date: new Date().toISOString(),
          data: assignmentsResult.data,
          status: 'ready'
        });
      }

      setReports(reportsData);
    } catch (err) {
      setError('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType) => {
    try {
      setGenerating(true);
      
      // Simulate report generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newReport = {
        id: Date.now().toString(),
        type: reportType,
        title: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
        description: `Custom ${reportType} report generated on ${new Date().toLocaleDateString()}`,
        date: new Date().toISOString(),
        status: 'ready'
      };

      setReports(prev => [newReport, ...prev]);
      setSuccess(`${reportType} report generated successfully!`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const downloadReport = (report) => {
    // Simulate download
    console.log('Downloading report:', report);
    setSuccess(`Downloading ${report.title}...`);
    setTimeout(() => setSuccess(''), 2000);
  };

  const getReportIcon = (type) => {
    const icons = {
      attendance: <UsersIcon className="text-primary" size={20} />,
      grades: <BarChartIcon className="text-success" size={20} />,
      assignments: <FileTextIcon className="text-warning" size={20} />,
      behavior: <TrendingUpIcon className="text-info" size={20} />,
      default: <DocumentIcon className="text-secondary" size={20} />
    };
    return icons[type] || icons.default;
  };

  const getStatusVariant = (status) => {
    const variants = {
      ready: 'success',
      generating: 'warning',
      error: 'danger'
    };
    return variants[status] || 'secondary';
  };

  const getStatusIcon = (status) => {
    const icons = {
      ready: <CheckCircleIcon className="text-success" size={14} />,
      generating: <WarningIcon className="text-warning" size={14} />,
      error: <ErrorIcon className="text-danger" size={14} />
    };
    return icons[status] || <CheckCircleIcon className="text-secondary" size={14} />;
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" />
          <p className="mt-3 text-muted">Loading reports...</p>
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
              <h1 className="h3 mb-1 d-flex align-items-center">
                <ReportIcon className="me-2" size={24} />
                Reports & Analytics
              </h1>
              <p className="text-muted mb-0">
                Generate and view comprehensive class reports
              </p>
            </div>
            <Dropdown>
              <Dropdown.Toggle variant="primary" className="d-flex align-items-center">
                <FileTextIcon className="me-2" size={16} />
                Generate Report
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <Dropdown.Item onClick={() => generateReport('attendance')} className="d-flex align-items-center">
                  <UsersIcon className="me-2" size={14} />
                  Attendance Report
                </Dropdown.Item>
                <Dropdown.Item onClick={() => generateReport('grades')} className="d-flex align-items-center">
                  <BarChartIcon className="me-2" size={14} />
                  Grades Report
                </Dropdown.Item>
                <Dropdown.Item onClick={() => generateReport('assignments')} className="d-flex align-items-center">
                  <DocumentIcon className="me-2" size={14} />
                  Assignments Report
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item onClick={() => generateReport('behavior')} className="d-flex align-items-center">
                  <TrendingUpIcon className="me-2" size={14} />
                  Behavior Report
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          <ErrorIcon className="me-2" size={16} />
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          <CheckCircleIcon className="me-2" size={16} />
          {success}
        </Alert>
      )}

      {/* Filters */}
      <Card className="border-0 shadow-sm mb-4">
        <Card.Body>
          <Row>
            <Col md={4}>
              <Form.Group>
                <Form.Label className="d-flex align-items-center">
                  <ClassIcon className="me-2" size={16} />
                  Select Class
                </Form.Label>
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
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label className="d-flex align-items-center">
                  <CalendarIcon className="me-2" size={16} />
                  Start Date
                </Form.Label>
                <Form.Control
                  type="date"
                  value={dateRange.start}
                  onChange={(e) => setDateRange(prev => ({
                    ...prev,
                    start: e.target.value
                  }))}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label className="d-flex align-items-center">
                  <CalendarIcon className="me-2" size={16} />
                  End Date
                </Form.Label>
                <Form.Control
                  type="date"
                  value={dateRange.end}
                  onChange={(e) => setDateRange(prev => ({
                    ...prev,
                    end: e.target.value
                  }))}
                />
              </Form.Group>
            </Col>
            <Col md={2}>
              <Form.Label>&nbsp;</Form.Label>
              <div>
                <Button variant="outline-primary" className="w-100 d-flex align-items-center justify-content-center">
                  <FilterIcon className="me-2" size={16} />
                  Apply
                </Button>
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Row>
        {/* Quick Stats */}
        <Col lg={3} className="mb-4">
          <Card className="border-0 shadow-sm">
            <Card.Header className="d-flex align-items-center">
              <AnalyticsIcon className="me-2" size={18} />
              <h6 className="mb-0">Report Summary</h6>
            </Card.Header>
            <Card.Body>
              <div className="text-center mb-3">
                <FileTextIcon size={24} className="text-primary mb-2" />
                <div className="h4 text-primary mb-1">{reports.length}</div>
                <small className="text-muted">Total Reports</small>
              </div>
              <div className="text-center mb-3">
                <CheckCircleIcon size={24} className="text-success mb-2" />
                <div className="h4 text-success mb-1">
                  {reports.filter(r => r.status === 'ready').length}
                </div>
                <small className="text-muted">Ready</small>
              </div>
              <div className="text-center">
                <WarningIcon size={24} className="text-warning mb-2" />
                <div className="h4 text-warning mb-1">
                  {reports.filter(r => r.status === 'generating').length}
                </div>
                <small className="text-muted">Generating</small>
              </div>
            </Card.Body>
          </Card>

          {/* Report Types */}
          <Card className="border-0 shadow-sm mt-4">
            <Card.Header className="d-flex align-items-center">
              <DocumentIcon className="me-2" size={18} />
              <h6 className="mb-0">Report Types</h6>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button
                  variant="outline-primary"
                  className="text-start d-flex align-items-center"
                  onClick={() => generateReport('attendance')}
                >
                  <UsersIcon className="me-2" size={16} />
                  Attendance
                </Button>
                <Button
                  variant="outline-success"
                  className="text-start d-flex align-items-center"
                  onClick={() => generateReport('grades')}
                >
                  <BarChartIcon className="me-2" size={16} />
                  Grades
                </Button>
                <Button
                  variant="outline-warning"
                  className="text-start d-flex align-items-center"
                  onClick={() => generateReport('assignments')}
                >
                  <FileTextIcon className="me-2" size={16} />
                  Assignments
                </Button>
                <Button
                  variant="outline-info"
                  className="text-start d-flex align-items-center"
                  onClick={() => generateReport('behavior')}
                >
                  <TrendingUpIcon className="me-2" size={16} />
                  Behavior
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Reports List */}
        <Col lg={9}>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white d-flex align-items-center">
              <HistoryIcon className="me-2" size={18} />
              <h5 className="mb-0">Generated Reports</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {reports.length > 0 ? (
                <div className="list-group list-group-flush">
                  {reports.map(report => (
                    <div key={report.id} className="list-group-item">
                      <Row className="align-items-center">
                        <Col md={1} className="text-center">
                          <div className="fs-4">
                            {getReportIcon(report.type)}
                          </div>
                        </Col>
                        <Col md={6}>
                          <h6 className="mb-1">{report.title}</h6>
                          <p className="mb-1 text-muted small">{report.description}</p>
                          <small className="text-muted d-flex align-items-center">
                            <CalendarIcon className="me-1" size={12} />
                            Generated on {new Date(report.date).toLocaleDateString()}
                          </small>
                        </Col>
                        <Col md={2} className="text-center">
                          <Badge bg={getStatusVariant(report.status)} className="d-flex align-items-center justify-content-center">
                            {getStatusIcon(report.status)}
                            <span className="ms-1">{report.status}</span>
                          </Badge>
                        </Col>
                        <Col md={3} className="text-end">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            className="me-2 d-flex align-items-center"
                            onClick={() => downloadReport(report)}
                            disabled={report.status !== 'ready'}
                          >
                            <DownloadIcon size={14} />
                          </Button>
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            className="me-2 d-flex align-items-center"
                          >
                            <EyeIcon size={14} />
                          </Button>
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            className="d-flex align-items-center"
                          >
                            <PrintIcon size={14} />
                          </Button>
                        </Col>
                      </Row>
                      {report.status === 'generating' && (
                        <div className="mt-2">
                          <ProgressBar animated now={100} label="Generating..." />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-5">
                  <FileTextIcon size={48} className="text-muted mb-3" />
                  <h5 className="text-muted">No Reports Generated</h5>
                  <p className="text-muted">
                    Generate your first report using the button above
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Report Preview Section */}
          {reports.length > 0 && (
            <Card className="border-0 shadow-sm mt-4">
              <Card.Header className="d-flex align-items-center">
                <ChartIcon className="me-2" size={18} />
                <h5 className="mb-0">Report Preview</h5>
              </Card.Header>
              <Card.Body>
                <Tabs defaultActiveKey="summary" className="mb-3">
                  <Tab eventKey="summary" title={
                    <span className="d-flex align-items-center">
                      <AnalyticsIcon className="me-2" size={14} />
                      Summary
                    </span>
                  }>
                    <Row>
                      <Col md={6}>
                        <h6 className="d-flex align-items-center">
                          <PieChartIcon className="me-2" size={16} />
                          Attendance Overview
                        </h6>
                        <div className="text-center py-4 text-muted">
                          <PieChartIcon size={32} className="mb-2" />
                          <p>Attendance chart would be displayed here</p>
                        </div>
                      </Col>
                      <Col md={6}>
                        <h6 className="d-flex align-items-center">
                          <BarChartIcon className="me-2" size={16} />
                          Grade Distribution
                        </h6>
                        <div className="text-center py-4 text-muted">
                          <BarChartIcon size={32} className="mb-2" />
                          <p>Grade distribution chart would be displayed here</p>
                        </div>
                      </Col>
                    </Row>
                  </Tab>
                  <Tab eventKey="details" title={
                    <span className="d-flex align-items-center">
                      <FileTextIcon className="me-2" size={14} />
                      Detailed View
                    </span>
                  }>
                    <div className="table-responsive">
                      <Table striped>
                        <thead>
                          <tr>
                            <th>Metric</th>
                            <th>Value</th>
                            <th>Trend</th>
                            <th>Comparison</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td className="d-flex align-items-center">
                              <UsersIcon className="me-2 text-muted" size={14} />
                              Average Attendance
                            </td>
                            <td>94.5%</td>
                            <td>
                              <Badge bg="success" className="d-flex align-items-center">
                                <TrendingUpIcon className="me-1" size={12} />
                                +2.1%
                              </Badge>
                            </td>
                            <td>Above class average</td>
                          </tr>
                          <tr>
                            <td className="d-flex align-items-center">
                              <BarChartIcon className="me-2 text-muted" size={14} />
                              Average Grade
                            </td>
                            <td>82.3%</td>
                            <td>
                              <Badge bg="warning" className="d-flex align-items-center">
                                <TrendingUpIcon className="me-1" size={12} />
                                -1.2%
                              </Badge>
                            </td>
                            <td>Slightly below average</td>
                          </tr>
                          <tr>
                            <td className="d-flex align-items-center">
                              <DocumentIcon className="me-2 text-muted" size={14} />
                              Assignment Completion
                            </td>
                            <td>88.7%</td>
                            <td>
                              <Badge bg="success" className="d-flex align-items-center">
                                <TrendingUpIcon className="me-1" size={12} />
                                +5.4%
                              </Badge>
                            </td>
                            <td>Above target</td>
                          </tr>
                        </tbody>
                      </Table>
                    </div>
                  </Tab>
                </Tabs>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Generating Modal */}
      <Modal show={generating} centered>
        <Modal.Body className="text-center py-4">
          <Spinner animation="border" variant="primary" className="mb-3" />
          <FileTextIcon size={24} className="text-primary mb-2" />
          <h5>Generating Report</h5>
          <p className="text-muted mb-0">Please wait while we generate your report...</p>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default TeacherReports;