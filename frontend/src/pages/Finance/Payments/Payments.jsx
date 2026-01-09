import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, InputGroup, Alert, Dropdown, Modal, Spinner
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  Plus, Search, Download, Eye, Pencil, 
  Trash, CheckCircle, ThreeDotsVertical, FileText 
} from 'react-bootstrap-icons';

const Payments = () => {
  const { currentUser } = useAuth();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    paid_through: '',
    search: '',
    start_date: '',
    end_date: ''
  });
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    fetchPayments();
  }, [filters]);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });

      const result = await financeAPI.getPayments(params.toString());
      if (result.success) {
        setPayments(result.data);
      } else {
        setError(result.error?.message || 'Failed to load payments');
      }
    } catch (err) {
      setError('Failed to load payments');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovePayment = async () => {
    try {
      const result = await financeAPI.approvePayment(selectedPayment.id);
      if (result.success) {
        setShowApproveModal(false);
        setSelectedPayment(null);
        fetchPayments();
      } else {
        setError(result.error?.message || 'Failed to approve payment');
      }
    } catch (err) {
      setError('Failed to approve payment');
    }
  };

  const handleDeletePayment = async () => {
    try {
      const result = await financeAPI.deletePayment(selectedPayment.id);
      if (result.success) {
        setShowDeleteModal(false);
        setSelectedPayment(null);
        fetchPayments();
      } else {
        setError(result.error?.message || 'Failed to delete payment');
      }
    } catch (err) {
      setError('Failed to delete payment');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount || 0);
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'Completed': return 'success';
      case 'Pending': return 'warning';
      case 'Cancelled': return 'danger';
      case 'Failed': return 'secondary';
      default: return 'info';
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

  const canApprove = (payment) => {
    return currentUser?.is_accountant && payment.status === 'Pending';
  };

  const pendingCount = payments.filter(p => p.status === 'Pending').length;

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading payments...</p>
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
              <h1 className="h3 mb-1">Payment Management</h1>
              <p className="text-muted mb-0">Manage school expenditures and vendor payments</p>
            </div>
            <div>
              {pendingCount > 0 && (
                <Button 
                  as={Link} 
                  to="/finance/payments/approval" 
                  variant="outline-warning" 
                  className="me-2"
                >
                  <CheckCircle className="me-2" />
                  Pending Approvals ({pendingCount})
                </Button>
              )}
              <Button 
                as={Link} 
                to="/finance/payments/create" 
                variant="primary"
              >
                <Plus className="me-2" />
                New Payment
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Row>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Status</Form.Label>
                    <Form.Select
                      value={filters.status}
                      onChange={(e) => setFilters({...filters, status: e.target.value})}
                    >
                      <option value="">All Status</option>
                      <option value="Pending">Pending</option>
                      <option value="Completed">Completed</option>
                      <option value="Cancelled">Cancelled</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Payment Method</Form.Label>
                    <Form.Select
                      value={filters.paid_through}
                      onChange={(e) => setFilters({...filters, paid_through: e.target.value})}
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
                  <Form.Group>
                    <Form.Label>From Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.start_date}
                      onChange={(e) => setFilters({...filters, start_date: e.target.value})}
                    />
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>To Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.end_date}
                      onChange={(e) => setFilters({...filters, end_date: e.target.value})}
                    />
                  </Form.Group>
                </Col>
              </Row>
              <Row className="mt-2">
                <Col md={8}>
                  <Form.Group>
                    <Form.Label>Search</Form.Label>
                    <InputGroup>
                      <Form.Control
                        type="text"
                        placeholder="Search by payee name, payment number..."
                        value={filters.search}
                        onChange={(e) => setFilters({...filters, search: e.target.value})}
                      />
                      <Button variant="outline-secondary">
                        <Search />
                      </Button>
                    </InputGroup>
                  </Form.Group>
                </Col>
                <Col md={4} className="d-flex align-items-end">
                  <Button 
                    variant="outline-primary" 
                    className="w-100"
                    onClick={() => {
                      // Add export functionality here
                      console.log('Export payments');
                    }}
                  >
                    <Download className="me-2" />
                    Export
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Payments Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Payments</h5>
              <span className="text-muted">{payments.length} records found</span>
            </Card.Header>
            <Card.Body className="p-0">
              <Table responsive hover>
                <thead className="bg-light">
                  <tr>
                    <th>Payment #</th>
                    <th>Date</th>
                    <th>Payee</th>
                    <th>Purpose</th>
                    <th>Amount</th>
                    <th>Method</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((payment) => (
                    <tr key={payment.id}>
                      <td>
                        <strong>{payment.payment_number}</strong>
                      </td>
                      <td>
                        {payment.date ? new Date(payment.date).toLocaleDateString() : 'N/A'}
                      </td>
                      <td>
                        <div>
                          <strong>{payment.paid_to_name || 'N/A'}</strong>
                          {payment.paid_to_phone && (
                            <div className="text-muted small">{payment.paid_to_phone}</div>
                          )}
                        </div>
                      </td>
                      <td>{payment.paid_for_details?.name || payment.purpose || 'N/A'}</td>
                      <td>
                        <strong>{formatCurrency(payment.amount)}</strong>
                      </td>
                      <td>
                        <Badge bg={getMethodVariant(payment.paid_through)}>
                          {payment.paid_through || 'N/A'}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg={getStatusVariant(payment.status)}>
                          {payment.status || 'N/A'}
                        </Badge>
                      </td>
                      <td>
                        <Dropdown>
                          <Dropdown.Toggle 
                            variant="outline-primary" 
                            size="sm"
                            id={`dropdown-${payment.id}`}
                          >
                            <ThreeDotsVertical size={14} />
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            <Dropdown.Item 
                              as={Link} 
                              to={`/finance/payments/${payment.id}`}
                            >
                              <Eye className="me-2" />
                              View Details
                            </Dropdown.Item>
                            <Dropdown.Item 
                              as={Link} 
                              to={`/finance/payments/${payment.id}/edit`}
                            >
                              <Pencil className="me-2" />
                              Edit
                            </Dropdown.Item>
                            {canApprove(payment) && (
                              <Dropdown.Item 
                                onClick={() => {
                                  setSelectedPayment(payment);
                                  setShowApproveModal(true);
                                }}
                              >
                                <CheckCircle className="me-2" />
                                Approve
                              </Dropdown.Item>
                            )}
                            <Dropdown.Divider />
                            <Dropdown.Item 
                              className="text-danger"
                              onClick={() => {
                                setSelectedPayment(payment);
                                setShowDeleteModal(true);
                              }}
                            >
                              <Trash className="me-2" />
                              Delete
                            </Dropdown.Item>
                          </Dropdown.Menu>
                        </Dropdown>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {payments.length === 0 && (
                <div className="text-center py-5">
                  <FileText size={48} className="text-muted mb-3" />
                  <p className="text-muted">No payments found</p>
                  <Button 
                    as={Link} 
                    to="/finance/payments/create" 
                    variant="primary"
                    className="mt-2"
                  >
                    <Plus className="me-2" />
                    Create First Payment
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Summary Cards */}
      <Row className="mt-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-primary">
                {formatCurrency(payments.reduce((sum, p) => sum + (parseFloat(p.amount) || 0), 0))}
              </h3>
              <p className="text-muted mb-0">Total Amount</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-success">
                {payments.filter(p => p.status === 'Completed').length}
              </h3>
              <p className="text-muted mb-0">Completed</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-warning">{pendingCount}</h3>
              <p className="text-muted mb-0">Pending</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-danger">
                {payments.filter(p => p.status === 'Cancelled').length}
              </h3>
              <p className="text-muted mb-0">Cancelled</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modals */}
      <Modal show={showApproveModal} onHide={() => setShowApproveModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Approve Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to approve payment <strong>{selectedPayment?.payment_number}</strong>?
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowApproveModal(false)}>
            Cancel
          </Button>
          <Button variant="success" onClick={handleApprovePayment}>
            Approve Payment
          </Button>
        </Modal.Footer>
      </Modal>

      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Delete Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to delete payment <strong>{selectedPayment?.payment_number}</strong>?
          This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeletePayment}>
            Delete Payment
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Payments;