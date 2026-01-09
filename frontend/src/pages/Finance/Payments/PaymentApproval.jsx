import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Alert, Spinner, Modal, Form
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  ArrowLeft, CheckCircle, XCircle, Eye, 
  Filter, Download, FileText 
} from 'react-bootstrap-icons';

const PaymentApproval = () => {
  const { currentUser } = useAuth();
  const [pendingPayments, setPendingPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  useEffect(() => {
    fetchPendingPayments();
  }, []);

  const fetchPendingPayments = async () => {
    try {
      const response = await financeAPI.get('/payments/?status=Pending');
      setPendingPayments(response.data);
    } catch (err) {
      setError('Failed to load pending payments');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      await financeAPI.post(`/payments/${selectedPayment.id}/mark_approved/`);
      setShowApproveModal(false);
      setSelectedPayment(null);
      fetchPendingPayments();
    } catch (err) {
      setError('Failed to approve payment');
    }
  };

  const handleReject = async () => {
    try {
      // Implementation for rejecting payment
      // This would typically update payment status to 'Rejected'
      // and create an approval record with rejection reason
      await financeAPI.post(`/payments/${selectedPayment.id}/reject/`, {
        reason: rejectReason
      });
      setShowRejectModal(false);
      setSelectedPayment(null);
      setRejectReason('');
      fetchPendingPayments();
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

  const canApprove = (payment) => {
    return currentUser.is_accountant;
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading pending approvals...</p>
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
                to="/finance/payments" 
                variant="outline-secondary" 
                className="me-3"
              >
                <ArrowLeft />
              </Button>
              <div>
                <h1 className="h3 mb-1">Payment Approvals</h1>
                <p className="text-muted mb-0">
                  Review and approve pending payments ({pendingPayments.length})
                </p>
              </div>
            </div>
            <div>
              <Button variant="outline-primary">
                <Download className="me-2" />
                Export
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* Pending Payments */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Pending Approval</h5>
              <Badge bg="warning" className="fs-6">
                {pendingPayments.length} Payments
              </Badge>
            </Card.Header>
            <Card.Body className="p-0">
              {pendingPayments.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Payment #</th>
                      <th>Date</th>
                      <th>Payee</th>
                      <th>Purpose</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Requested By</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pendingPayments.map((payment) => (
                      <tr key={payment.id}>
                        <td>
                          <strong>{payment.payment_number}</strong>
                        </td>
                        <td>{new Date(payment.date).toLocaleDateString()}</td>
                        <td>
                          <div>
                            <strong>{payment.paid_to_name}</strong>
                            {payment.paid_to_phone && (
                              <div className="text-muted small">{payment.paid_to_phone}</div>
                            )}
                          </div>
                        </td>
                        <td>{payment.paid_for_details?.name}</td>
                        <td>
                          <strong className="text-primary">
                            {formatCurrency(payment.amount)}
                          </strong>
                        </td>
                        <td>
                          <Badge bg="secondary">{payment.paid_through}</Badge>
                        </td>
                        <td>{payment.paid_by_details?.get_full_name}</td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button
                              as={Link}
                              to={`/finance/payments/${payment.id}`}
                              variant="outline-primary"
                              size="sm"
                            >
                              <Eye size={14} />
                            </Button>
                            {canApprove(payment) && (
                              <>
                                <Button
                                  variant="outline-success"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedPayment(payment);
                                    setShowApproveModal(true);
                                  }}
                                >
                                  <CheckCircle size={14} />
                                </Button>
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedPayment(payment);
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
                  <h5>All Caught Up!</h5>
                  <p className="text-muted">No pending payments requiring approval</p>
                  <Button as={Link} to="/finance/payments" variant="primary">
                    Back to Payments
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Summary Stats */}
      {pendingPayments.length > 0 && (
        <Row className="mt-4">
          <Col md={4}>
            <Card className="text-center border-0 bg-light">
              <Card.Body>
                <h3 className="text-warning">
                  {formatCurrency(
                    pendingPayments.reduce((sum, p) => sum + parseFloat(p.amount), 0)
                  )}
                </h3>
                <p className="text-muted mb-0">Total Pending Amount</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="text-center border-0 bg-light">
              <Card.Body>
                <h3 className="text-primary">{pendingPayments.length}</h3>
                <p className="text-muted mb-0">Payments Pending</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="text-center border-0 bg-light">
              <Card.Body>
                <h3 className="text-info">
                  {pendingPayments.filter(p => p.paid_through === 'M-Pesa').length}
                </h3>
                <p className="text-muted mb-0">M-Pesa Payments</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Approve Modal */}
      <Modal show={showApproveModal} onHide={() => setShowApproveModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Approve Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to approve this payment?</p>
          {selectedPayment && (
            <div className="bg-light p-3 rounded">
              <strong>Payment #{selectedPayment.payment_number}</strong><br />
              Payee: {selectedPayment.paid_to_name}<br />
              Amount: {formatCurrency(selectedPayment.amount)}<br />
              Purpose: {selectedPayment.paid_for_details?.name}
            </div>
          )}
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
          {selectedPayment && (
            <div className="bg-light p-3 rounded mb-3">
              <strong>Payment #{selectedPayment.payment_number}</strong><br />
              Amount: {formatCurrency(selectedPayment.amount)}<br />
              Payee: {selectedPayment.paid_to_name}
            </div>
          )}
          <Form.Group>
            <Form.Label>Rejection Reason *</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Enter reason for rejection..."
              required
            />
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

export default PaymentApproval;