import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, 
  Form, Alert, Spinner, Badge
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  Download, FileText, Filter, BarChart, 
  People, Calendar, Cash
} from 'react-bootstrap-icons';

const DebtReports = () => {
  const { currentUser } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    term: '',
    report_type: 'overdue',
    date_range: 'current_term'
  });

  useEffect(() => {
    fetchDebtReports();
  }, [filters]);

  const fetchDebtReports = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });

      const response = await financeAPI.get(`/debt-reports/?${params}`);
      setReports(response.data);
    } catch (err) {
      setError('Failed to load debt reports');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const generateReport = async (type) => {
    try {
      const response = await financeAPI.get(`/debt-reports/export/?type=${type}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `debt-report-${type}-${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to generate report');
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading debt reports...</p>
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
              <h1 className="h3 mb-1">Debt Reports</h1>
              <p className="text-muted mb-0">Comprehensive debt analysis and reporting</p>
            </div>
            <div>
              <Button 
                as={Link} 
                to="/finance/debts" 
                variant="outline-secondary" 
                className="me-2"
              >
                Back to Debts
              </Button>
              <Button variant="primary">
                <Download className="me-2" />
                Export All Reports
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

      {/* Report Filters */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <h6 className="mb-0">
                <Filter className="me-2" />
                Report Filters
              </h6>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Report Type</Form.Label>
                    <Form.Select
                      value={filters.report_type}
                      onChange={(e) => setFilters({...filters, report_type: e.target.value})}
                    >
                      <option value="overdue">Overdue Debts</option>
                      <option value="all">All Outstanding Debts</option>
                      <option value="term">Term-wise Summary</option>
                      <option value="class">Class-wise Analysis</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Date Range</Form.Label>
                    <Form.Select
                      value={filters.date_range}
                      onChange={(e) => setFilters({...filters, date_range: e.target.value})}
                    >
                      <option value="current_term">Current Term</option>
                      <option value="last_term">Last Term</option>
                      <option value="this_year">This Year</option>
                      <option value="last_year">Last Year</option>
                      <option value="all_time">All Time</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Quick Actions</Form.Label>
                    <div className="d-grid gap-2">
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        onClick={() => generateReport('overdue')}
                      >
                        Export Overdue
                      </Button>
                    </div>
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Summary Statistics */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <BarChart size={24} className="text-primary mb-2" />
              <h4>{reports.summary?.total_debtors || 0}</h4>
              <p className="text-muted mb-0">Total Debtors</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <Cash size={24} className="text-warning mb-2" />
              <h4>{formatCurrency(reports.summary?.total_outstanding || 0)}</h4>
              <p className="text-muted mb-0">Total Outstanding</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <People size={24} className="text-danger mb-2" />
              <h4>{reports.summary?.overdue_count || 0}</h4>
              <p className="text-muted mb-0">Overdue Accounts</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <Calendar size={24} className="text-success mb-2" />
              <h4>{reports.summary?.clear_accounts || 0}</h4>
              <p className="text-muted mb-0">Accounts Clear</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Main Report Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Debt Analysis Report</h5>
              <Badge bg="primary">
                {filters.report_type.replace('_', ' ').toUpperCase()}
              </Badge>
            </Card.Header>
            <Card.Body className="p-0">
              {reports.data && reports.data.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Student Name</th>
                      <th>Admission No.</th>
                      <th>Class</th>
                      <th>Term</th>
                      <th>Total Debt</th>
                      <th>Amount Paid</th>
                      <th>Balance</th>
                      <th>Due Date</th>
                      <th>Status</th>
                      <th>Days Overdue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.data.map((item, index) => (
                      <tr key={index}>
                        <td>
                          <Link to={`/finance/student-debts/${item.student_id}`}>
                            {item.student_name}
                          </Link>
                        </td>
                        <td>{item.admission_number}</td>
                        <td>{item.class_level}</td>
                        <td>{item.term_name}</td>
                        <td>{formatCurrency(item.total_debt)}</td>
                        <td>{formatCurrency(item.amount_paid)}</td>
                        <td>
                          <strong className={
                            item.balance > 0 ? 'text-danger' : 'text-success'
                          }>
                            {formatCurrency(item.balance)}
                          </strong>
                        </td>
                        <td>
                          {item.due_date ? new Date(item.due_date).toLocaleDateString() : 'N/A'}
                        </td>
                        <td>
                          <Badge bg={item.is_overdue ? 'danger' : 'warning'}>
                            {item.is_overdue ? 'Overdue' : 'Pending'}
                          </Badge>
                        </td>
                        <td>
                          {item.overdue_days > 0 ? (
                            <span className="text-danger">{item.overdue_days} days</span>
                          ) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-5">
                  <FileText size={48} className="text-muted mb-3" />
                  <h5>No Data Available</h5>
                  <p className="text-muted">
                    No debt records found for the selected criteria
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Additional Reports */}
      <Row className="mt-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Class-wise Summary</h6>
            </Card.Header>
            <Card.Body>
              {reports.class_summary && reports.class_summary.length > 0 ? (
                <Table size="sm">
                  <thead>
                    <tr>
                      <th>Class</th>
                      <th>Students</th>
                      <th>Total Outstanding</th>
                      <th>Avg. Balance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.class_summary.map((classItem, index) => (
                      <tr key={index}>
                        <td>{classItem.class_level}</td>
                        <td>{classItem.student_count}</td>
                        <td>{formatCurrency(classItem.total_outstanding)}</td>
                        <td>{formatCurrency(classItem.average_balance)}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <p className="text-muted text-center">No class summary available</p>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Term-wise Analysis</h6>
            </Card.Header>
            <Card.Body>
              {reports.term_summary && reports.term_summary.length > 0 ? (
                <Table size="sm">
                  <thead>
                    <tr>
                      <th>Term</th>
                      <th>Total Debt</th>
                      <th>Collected</th>
                      <th>Collection Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.term_summary.map((termItem, index) => (
                      <tr key={index}>
                        <td>{termItem.term_name}</td>
                        <td>{formatCurrency(termItem.total_debt)}</td>
                        <td>{formatCurrency(termItem.amount_collected)}</td>
                        <td>
                          <Badge bg={
                            termItem.collection_rate >= 90 ? 'success' :
                            termItem.collection_rate >= 70 ? 'warning' : 'danger'
                          }>
                            {termItem.collection_rate}%
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <p className="text-muted text-center">No term analysis available</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Export Options */}
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Export Reports</h6>
            </Card.Header>
            <Card.Body>
              <div className="d-flex gap-2 flex-wrap">
                <Button 
                  variant="outline-primary"
                  onClick={() => generateReport('detailed')}
                >
                  <Download className="me-2" />
                  Detailed Debt Report
                </Button>
                <Button 
                  variant="outline-success"
                  onClick={() => generateReport('overdue')}
                >
                  <Download className="me-2" />
                  Overdue Accounts
                </Button>
                <Button 
                  variant="outline-warning"
                  onClick={() => generateReport('summary')}
                >
                  <Download className="me-2" />
                  Summary Report
                </Button>
                <Button 
                  variant="outline-info"
                  onClick={() => generateReport('class_wise')}
                >
                  <Download className="me-2" />
                  Class-wise Report
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default DebtReports;