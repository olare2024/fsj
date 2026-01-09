import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, Alert, Spinner, Modal, InputGroup
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  CheckCircle, Clock, ExclamationTriangle, FileText, // Use ExclamationTriangle instead of AlertTriangle
  Eye, XCircle, Filter, Search,
  ArrowLeft, Download, People, CurrencyDollar
} from 'react-bootstrap-icons';

const FinancialApprovals = () => {
  const { currentUser } = useAuth();
  const [approvals, setApprovals] = useState([]);
  const [filteredApprovals, setFilteredApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [filters, setFilters] = useState({
    status: 'pending',
    priority: '',
    search: ''
  });

  useEffect(() => {
    fetchApprovals();
  }, []);

  useEffect(() => {
    filterApprovals();
  }, [approvals, filters]);

  const fetchApprovals = async () => {
    try {
      const response = await financeAPI.get('/financial-approvals/');
      setApprovals(response.data);
    } catch (err) {
      setError('Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  const filterApprovals = () => {
    let filtered = approvals;

    if (filters.status) {
      filtered = filtered.filter(approval => approval.status === filters.status);
    }

    if (filters.priority) {
      filtered = filtered.filter(approval => approval.priority === filters.priority);
    }

    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filtered = filtered.filter(approval => 
        approval.payment_number.toLowerCase().includes(searchTerm) ||
        approval.payee_name.toLowerCase().includes(searchTerm) ||
        approval.requested_by.toLowerCase().includes(searchTerm)
      );
    }

    setFilteredApprovals(filtered);
  };

  const handleApprove = async () => {
    try {
      await financeAPI.post(`/financial-approvals/${selectedApproval.id}/approve/`);
      setShowApproveModal(false);
      setSelectedApproval(null);
      fetchApprovals();
    } catch (err) {
      setError('Failed to approve payment');
    }
  };

  const handleReject = async () => {
    try {
      await financeAPI.post(`/financial-approvals/${selectedApproval.id}/reject/`, {
        reason: rejectReason
      });
      setShowRejectModal(false);
      setSelectedApproval(null);
      setRejectReason('');
      fetchApprovals();
    } catch (err) {
      setError('Failed to reject payment');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'rejected': return 'danger';
      case 'pending': return 'warning';
      case 'requires_attention': return 'info';
      default: return 'secondary';
    }
  };

  const getPriorityVariant = (priority) => {
    switch (priority) {
      case 'urgent': return 'danger';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'secondary';
      default: return 'secondary';
    }
  };

  const canApprove = (approval) => {
    return currentUser.is_accountant && approval.status === 'pending';
  };

  const pendingCount = approvals.filter(a => a.status === 'pending').length;
  const urgentCount = approvals.filter(a => a.priority === 'urgent' && a.status === 'pending').length;

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading approvals...</p>
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
            <div className="d-flex align-items-center">
              <Button 
                as={Link} 
                to="/finance/accountant/workspace" 
                variant="outline-secondary" 
                className="me-3"
              >
                <ArrowLeft />
              </Button>
              <div>
                <h1 className="h3 mb-1">Financial Approvals</h1>
                <p className="text-muted mb-0">
                  Review and approve pending payments and expenses
                </p>
              </div>
            </div>
            <div>
              {urgentCount > 0 && (
                <Badge bg="danger" className="me-2 fs-6">
                  {urgentCount} Urgent
                </Badge>
              )}
              <Badge bg="warning" className="fs-6">
                {pendingCount} Pending
              </Badge>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

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
                      <option value="pending">Pending</option>
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                      <option value="requires_attention">Requires Attention</option>
                      <option value="">All Status</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Priority</Form.Label>
                    <Form.Select
                      value={filters.priority}
                      onChange={(e) => setFilters({...filters, priority: e.target.value})}
                    >
                      <option value="">All Priorities</option>
                      <option value="urgent">Urgent</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Search</Form.Label>
                    <InputGroup>
                      <Form.Control
                        type="text"
                        placeholder="Search by payment number, payee name..."
                        value={filters.search}
                        onChange={(e) => setFilters({...filters, search: e.target.value})}
                      />
                      <Button variant="outline-secondary">
                        <Search />
                      </Button>
                    </InputGroup>
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Approvals Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Approval Requests</h5>
              <span className="text-muted">
                Showing {filteredApprovals.length} of {approvals.length} approvals
              </span>
            </Card.Header>
            <Card.Body className="p-0">
              {filteredApprovals.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Payment #</th>
                      <th>Payee</th>
                      <th>Amount</th>
                      <th>Purpose</th>
                      <th>Requested By</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Days Pending</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredApprovals.map((approval) => (
                      <tr key={approval.id}>
                        <td>
                          <strong>{approval.payment_number}</strong>
                        </td>
                        <td>
                          <div>
                            <strong>{approval.payee_name}</strong>
                            {approval.payee_phone && (
                              <div className="text-muted small">{approval.payee_phone}</div>
                            )}
                          </div>
                        </td>
                        <td>
                          <strong className="text-primary">
                            {formatCurrency(approval.amount)}
                          </strong>
                        </td>
                        <td>{approval.purpose}</td>
                        <td>{approval.requested_by}</td>
                        <td>
                          <Badge bg={getPriorityVariant(approval.priority)}>
                            {approval.priority}
                          </Badge>
                        </td>
                        <td>
                          <Badge bg={getStatusVariant(approval.status)}>
                            {approval.status.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td>
                          <div className="d-flex align-items-center">
                            <Clock className={`me-1 ${approval.days_pending > 7 ? 'text-danger' : 'text-warning'}`} />
                            <span className={approval.days_pending > 7 ? 'text-danger' : ''}>
                              {approval.days_pending} days
                            </span>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <Button
                              as={Link}
                              to={`/finance/payments/${approval.payment_id}`}
                              variant="outline-primary"
                              size="sm"
                            >
                              <Eye size={14} />
                            </Button>
                            {canApprove(approval) && (
                              <>
                                <Button
                                  variant="outline-success"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedApproval(approval);
                                    setShowApproveModal(true);
                                  }}
                                >
                                  <CheckCircle size={14} />
                                </Button>
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedApproval(approval);
                                    setShowRejectModal(true);
                                  }}
                                >
                                  <XCircle size={14} />
                                </Button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-5">
                  <CheckCircle size={48} className="text-success mb-3" />
                  <h5>No Approvals Found</h5>
                  <p className="text-muted">
                    No approval requests match your current filters
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Approval Statistics */}
      <Row className="mt-4">
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h4 className="text-warning">{pendingCount}</h4>
              <p className="text-muted mb-0">Pending Approval</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h4 className="text-success">
                {approvals.filter(a => a.status === 'approved').length}
              </h4>
              <p className="text-muted mb-0">Approved</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h4 className="text-danger">
                {approvals.filter(a => a.status === 'rejected').length}
              </h4>
              <p className="text-muted mb-0">Rejected</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h4 className="text-info">
                {approvals.filter(a => a.status === 'requires_attention').length}
              </h4>
              <p className="text-muted mb-0">Needs Attention</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Approve Modal */}
      <Modal show={showApproveModal} onHide={() => setShowApproveModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Approve Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to approve this payment?</p>
          {selectedApproval && (
            <div className="bg-light p-3 rounded">
              <strong>Payment #{selectedApproval.payment_number}</strong><br />
              Payee: {selectedApproval.payee_name}<br />
              Amount: {formatCurrency(selectedApproval.amount)}<br />
              Purpose: {selectedApproval.purpose}<br />
              Priority: <Badge bg={getPriorityVariant(selectedApproval.priority)}>
                {selectedApproval.priority}
              </Badge>
            </div>
          )}
          <Form.Group className="mt-3">
            <Form.Label>Approval Notes (Optional)</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Add any notes about this approval..."
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowApproveModal(false)}>
            Cancel
          </Button>
          <Button variant="success" onClick={handleApprove}>
            <CheckCircle className="me-2" />
            Approve Payment
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Reject Modal */}
      <Modal show={showRejectModal} onHide={() => setShowRejectModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Reject Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Please provide a reason for rejecting this payment:</p>
          {selectedApproval && (
            <div className="bg-light p-3 rounded mb-3">
              <strong>Payment #{selectedApproval.payment_number}</strong><br />
              Amount: {formatCurrency(selectedApproval.amount)}<br />
              Payee: {selectedApproval.payee_name}
            </div>
          )}
          <Form.Group>
            <Form.Label>Rejection Reason *</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Enter detailed reason for rejection..."
              required
            />
            <Form.Text className="text-muted">
              This reason will be recorded in the audit trail and shared with the requester.
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowRejectModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={handleReject}
            disabled={!rejectReason.trim()}
          >
            <XCircle className="me-2" />
            Reject Payment
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default FinancialApprovals;