import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Button, Badge, 
  Alert, Spinner, Modal, Table
} from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  ArrowLeftIcon, DownloadIcon, PrintIcon, EditIcon, DeleteIcon, 
  CheckIcon, FileTextIcon, CalendarIcon, UserIcon 
} from '../../../components/Icons';

const PaymentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchPayment();
  }, [id]);

  const fetchPayment = async () => {
    try {
      setLoading(true);
      const result = await financeAPI.getPaymentById(id);
      if (result.success) {
        setPayment(result.data);
      } else {
        setError(result.error?.message || 'Failed to load payment details');
      }
    } catch (err) {
      setError('Failed to load payment details');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      setActionLoading(true);
      const result = await financeAPI.deletePayment(id);
      if (result.success) {
        navigate('/finance/payments');
      } else {
        setError(result.error?.message || 'Failed to delete payment');
      }
    } catch (err) {
      setError('Failed to delete payment');
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      setActionLoading(true);
      const result = await financeAPI.approvePayment(id);
      if (result.success) {
        fetchPayment(); // Refresh data
      } else {
        setError(result.error?.message || 'Failed to approve payment');
      }
    } catch (err) {
      setError('Failed to approve payment');
    } finally {
      setActionLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-KE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'Completed': return 'success';
      case 'Pending': return 'warning';
      case 'Cancelled': return 'danger';
      case 'Failed': return 'secondary';
      case 'Rejected': return 'danger';
      default: return 'secondary';
    }
  };

  const canEdit = () => {
    return currentUser?.is_accountant && payment?.status === 'Pending';
  };

  const canApprove = () => {
    return currentUser?.is_accountant && payment?.status === 'Pending';
  };

  const canDelete = () => {
    return currentUser?.is_accountant || currentUser?.is_admin;
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading payment details...</p>
        </div>
      </Container>
    );
  }

  if (!payment) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          Payment not found.
        </Alert>
        <Button as={Link} to="/finance/payments" variant="primary">
          <ArrowLeftIcon className="me-2" />
          Back to Payments
        </Button>
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
                <ArrowLeftIcon />
              </Button>
              <div>
                <h1 className="h3 mb-1">Payment Details</h1>
                <p className="text-muted mb-0">{payment.payment_number}</p>
              </div>
            </div>
            <div>
              <Button variant="outline-primary" className="me-2">
                <PrintIcon className="me-2" />
                Print
              </Button>
              <Button variant="outline-secondary" className="me-2">
                <DownloadIcon className="me-2" />
                Export
              </Button>
              {canEdit() && (
                <Button 
                  as={Link}
                  to={`/finance/payments/${id}/edit`}
                  variant="outline-warning" 
                  className="me-2"
                >
                  <EditIcon className="me-2" />
                  Edit
                </Button>
              )}
              {canApprove() && (
                <Button 
                  variant="success" 
                  className="me-2"
                  onClick={handleApprove}
                  disabled={actionLoading}
                >
                  {actionLoading ? (
                    <Spinner animation="border" size="sm" className="me-2" />
                  ) : (
                    <CheckIcon className="me-2" />
                  )}
                  Approve
                </Button>
              )}
              {canDelete() && (
                <Button 
                  variant="outline-danger"
                  onClick={() => setShowDeleteModal(true)}
                  disabled={actionLoading}
                >
                  <DeleteIcon className="me-2" />
                  Delete
                </Button>
              )}
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Row>
        <Col lg={8}>
          {/* Payment Information */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Payment Information</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Payment Number:</strong></td>
                        <td>{payment.payment_number}</td>
                      </tr>
                      <tr>
                        <td><strong>Date:</strong></td>
                        <td>
                          <CalendarIcon className="me-2 text-muted" />
                          {formatDate(payment.date)}
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Status:</strong></td>
                        <td>
                          <Badge bg={getStatusVariant(payment.status)}>
                            {payment.status}
                          </Badge>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Payment Method:</strong></td>
                        <td>{payment.paid_through || 'N/A'}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Amount:</strong></td>
                        <td className="h5 text-primary">
                          {formatCurrency(payment.amount)}
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Purpose:</strong></td>
                        <td>{payment.paid_for_details?.name || payment.purpose || 'N/A'}</td>
                      </tr>
                      <tr>
                        <td><strong>Category:</strong></td>
                        <td>
                          <Badge bg="info">
                            {payment.paid_for_details?.category || payment.category || 'General'}
                          </Badge>
                        </td>
                      </tr>
                      {payment.is_recurring && (
                        <tr>
                          <td><strong>Recurrence:</strong></td>
                          <td>{payment.recurrence_pattern || 'Monthly'}</td>
                        </tr>
                      )}
                    </tbody>
                  </Table>
                </Col>
              </Row>

              {payment.description && (
                <Row className="mt-3">
                  <Col>
                    <strong>Description:</strong>
                    <p className="mt-1 text-muted">{payment.description}</p>
                  </Col>
                </Row>
              )}
            </Card.Body>
          </Card>

          {/* Payee Information */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">
                <UserIcon className="me-2" />
                Payee Information
              </h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <strong>Payee Name:</strong>
                  <p className="text-muted">{payment.paid_to_name || 'N/A'}</p>
                </Col>
                {payment.paid_to_phone && (
                  <Col md={6}>
                    <strong>Phone:</strong>
                    <p className="text-muted">{payment.paid_to_phone}</p>
                  </Col>
                )}
              </Row>
              {payment.paid_to_email && (
                <Row>
                  <Col md={6}>
                    <strong>Email:</strong>
                    <p className="text-muted">{payment.paid_to_email}</p>
                  </Col>
                </Row>
              )}
              {payment.staff_member_details && (
                <Row>
                  <Col>
                    <strong>Staff Member:</strong>
                    <p className="text-muted">
                      {payment.staff_member_details?.get_full_name || payment.staff_member_details?.name || 'N/A'}
                    </p>
                  </Col>
                </Row>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Approval Information */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">
                <CheckIcon className="me-2" />
                Approval Information
              </h6>
            </Card.Header>
            <Card.Body>
              <Table borderless size="sm">
                <tbody>
                  <tr>
                    <td><strong>Processed By:</strong></td>
                    <td className="text-muted">
                      {payment.paid_by_details?.get_full_name || payment.created_by || 'N/A'}
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Processed On:</strong></td>
                    <td className="text-muted">
                      {formatDate(payment.created_at)}
                    </td>
                  </tr>
                  {payment.approved_by_details && (
                    <>
                      <tr>
                        <td><strong>Approved By:</strong></td>
                        <td className="text-muted">
                          {payment.approved_by_details?.get_full_name || payment.approved_by || 'N/A'}
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Approved On:</strong></td>
                        <td className="text-muted">
                          {formatDate(payment.approved_at)}
                        </td>
                      </tr>
                    </>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {/* Supporting Documents */}
          {payment.supporting_document && (
            <Card>
              <Card.Header>
                <h6 className="mb-0">
                  <FileTextIcon className="me-2" />
                  Supporting Document
                </h6>
              </Card.Header>
              <Card.Body>
                <div className="text-center">
                  <FileTextIcon size={48} className="text-muted mb-2" />
                  <p className="small text-muted mb-2">
                    {payment.supporting_document.split('/').pop()}
                  </p>
                  <Button 
                    variant="outline-primary" 
                    size="sm"
                    href={payment.supporting_document}
                    target="_blank"
                  >
                    View Document
                  </Button>
                </div>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to delete payment <strong>{payment.payment_number}</strong>?
          This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowDeleteModal(false)}
            disabled={actionLoading}
          >
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={handleDelete}
            disabled={actionLoading}
          >
            {actionLoading ? (
              <Spinner animation="border" size="sm" className="me-2" />
            ) : (
              <DeleteIcon className="me-2" />
            )}
            Delete Payment
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default PaymentDetail;