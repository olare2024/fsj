import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, InputGroup, Alert 
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import { financeAPI } from '../../services/financeAPI.js';

const PaymentHistory = () => {
  const { currentUser } = useAuth();
  const [payments, setPayments] = useState([]);
  const [filteredPayments, setFilteredPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    method: '',
    status: ''
  });

  useEffect(() => {
    fetchPaymentHistory();
  }, []);

  useEffect(() => {
    filterPayments();
  }, [payments, filters]);

  const fetchPaymentHistory = async () => {
    try {
      const response = await financeAPI.getPaymentHistory();
      setPayments(response.data);
    } catch (error) {
      console.error('Error fetching payment history:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterPayments = () => {
    let filtered = payments;

    if (filters.startDate) {
      filtered = filtered.filter(payment => 
        new Date(payment.paid_on) >= new Date(filters.startDate)
      );
    }

    if (filters.endDate) {
      filtered = filtered.filter(payment => 
        new Date(payment.paid_on) <= new Date(filters.endDate)
      );
    }

    if (filters.method) {
      filtered = filtered.filter(payment => 
        payment.method === filters.method
      );
    }

    if (filters.status) {
      filtered = filtered.filter(payment => 
        payment.status === filters.status
      );
    }

    setFilteredPayments(filtered);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      startDate: '',
      endDate: '',
      method: '',
      status: ''
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'Completed': return 'success';
      case 'Pending': return 'warning';
      case 'Failed': return 'danger';
      case 'Refunded': return 'info';
      default: return 'secondary';
    }
  };

  const getMethodVariant = (method) => {
    switch (method) {
      case 'M-Pesa': return 'primary';
      case 'Bank Transfer': return 'info';
      case 'Cash': return 'success';
      case 'Cheque': return 'warning';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Payment History</h1>
              <p className="text-muted mb-0">View and manage all payment transactions</p>
            </div>
            <Button variant="outline-primary" onClick={() => window.print()}>
              Export Report
            </Button>
          </div>
        </Col>
      </Row>

      {/* Filters */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h6 className="mb-0">Filters</h6>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={3}>
                  <Form.Group className="mb-3">
                    <Form.Label>Start Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.startDate}
                      onChange={(e) => handleFilterChange('startDate', e.target.value)}
                    />
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group className="mb-3">
                    <Form.Label>End Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.endDate}
                      onChange={(e) => handleFilterChange('endDate', e.target.value)}
                    />
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group className="mb-3">
                    <Form.Label>Payment Method</Form.Label>
                    <Form.Select
                      value={filters.method}
                      onChange={(e) => handleFilterChange('method', e.target.value)}
                    >
                      <option value="">All Methods</option>
                      <option value="M-Pesa">M-Pesa</option>
                      <option value="Bank Transfer">Bank Transfer</option>
                      <option value="Cash">Cash</option>
                      <option value="Cheque">Cheque</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group className="mb-3">
                    <Form.Label>Status</Form.Label>
                    <Form.Select
                      value={filters.status}
                      onChange={(e) => handleFilterChange('status', e.target.value)}
                    >
                      <option value="">All Status</option>
                      <option value="Completed">Completed</option>
                      <option value="Pending">Pending</option>
                      <option value="Failed">Failed</option>
                      <option value="Refunded">Refunded</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>
              <div className="d-flex justify-content-between">
                <small className="text-muted">
                  Showing {filteredPayments.length} of {payments.length} payments
                </small>
                <Button variant="outline-secondary" size="sm" onClick={clearFilters}>
                  Clear Filters
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Payment History Table */}
      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Payment Transactions</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {filteredPayments.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Payment Date</th>
                      <th>Receipt #</th>
                      <th>Student</th>
                      <th>Description</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Reference</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPayments.map((payment) => (
                      <tr key={payment.id}>
                        <td>
                          {new Date(payment.paid_on).toLocaleDateString()}
                          <br />
                          <small className="text-muted">
                            {new Date(payment.paid_on).toLocaleTimeString()}
                          </small>
                        </td>
                        <td>
                          <strong>{payment.receipt_number}</strong>
                        </td>
                        <td>{payment.student_name}</td>
                        <td>{payment.description}</td>
                        <td>
                          <strong>{formatCurrency(payment.amount)}</strong>
                        </td>
                        <td>
                          <Badge bg={getMethodVariant(payment.method)}>
                            {payment.method}
                          </Badge>
                        </td>
                        <td>
                          <code>{payment.reference}</code>
                        </td>
                        <td>
                          <Badge bg={getStatusVariant(payment.status)}>
                            {payment.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No payments found matching your criteria</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Summary Statistics */}
      <Row className="mt-4">
        <Col md={4}>
          <Card className="border-0 shadow-sm">
            <Card.Body className="text-center">
              <h4 className="text-success">
                {formatCurrency(
                  filteredPayments
                    .filter(p => p.status === 'Completed')
                    .reduce((sum, p) => sum + p.amount, 0)
                )}
              </h4>
              <p className="text-muted mb-0">Total Received</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="border-0 shadow-sm">
            <Card.Body className="text-center">
              <h4 className="text-warning">
                {filteredPayments.filter(p => p.status === 'Pending').length}
              </h4>
              <p className="text-muted mb-0">Pending Payments</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="border-0 shadow-sm">
            <Card.Body className="text-center">
              <h4 className="text-danger">
                {formatCurrency(
                  filteredPayments
                    .filter(p => p.status === 'Failed')
                    .reduce((sum, p) => sum + p.amount, 0)
                )}
              </h4>
              <p className="text-muted mb-0">Failed Payments</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default PaymentHistory;