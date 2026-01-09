import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Row, Col, Card, Button, Badge, Alert, 
  Table, Modal, Form 
} from 'react-bootstrap';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { PrintIcon, DownloadIcon, EditIcon, ArrowLeftIcon } from '../../../components/Icons';

const ReceiptDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showPrintModal, setShowPrintModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    fetchReceiptDetails();
  }, [id]);

  const fetchReceiptDetails = async () => {
    try {
      const response = await financeAPI.getReceipt(id);
      setReceipt(response.data);
    } catch (err) {
      setError('Failed to load receipt details');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkVerified = async () => {
    try {
      await financeAPI.markReceiptVerified(id);
      fetchReceiptDetails();
    } catch (err) {
      setError('Failed to mark receipt as verified');
    }
  };

  const handlePrint = () => {
    setShowPrintModal(true);
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
      case 'Cancelled': return 'danger';
      case 'Refunded': return 'info';
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

  if (!receipt) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">Receipt not found</Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Page Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div className="d-flex align-items-center">
              <Button
                variant="outline-secondary"
                onClick={() => navigate('/finance/receipts')}
                className="me-3"
              >
                <ArrowLeftIcon />
              </Button>
              <div>
                <h1 className="h3 mb-1">Receipt Details</h1>
                <p className="text-muted mb-0">
                  Receipt #{receipt.receipt_number}
                </p>
              </div>
            </div>
            <div>
              <Button
                variant="outline-primary"
                className="me-2"
                onClick={handlePrint}
              >
                <PrintIcon className="me-2" />
                Print
              </Button>
              <Button
                variant="primary"
                onClick={() => setShowEditModal(true)}
              >
                <EditIcon className="me-2" />
                Edit
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger">{error}</Alert>}

      <Row>
        <Col lg={8}>
          {/* Receipt Information Card */}
          <Card className="border-0 shadow-sm mb-4">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Receipt Information</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Receipt Number:</strong></td>
                        <td>{receipt.receipt_number}</td>
                      </tr>
                      <tr>
                        <td><strong>Date:</strong></td>
                        <td>{new Date(receipt.date).toLocaleDateString()}</td>
                      </tr>
                      <tr>
                        <td><strong>Status:</strong></td>
                        <td>
                          <Badge bg={getStatusVariant(receipt.status)}>
                            {receipt.status}
                          </Badge>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Payment Method:</strong></td>
                        <td>
                          <Badge bg="info">{receipt.paid_through}</Badge>
                        </td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Amount:</strong></td>
                        <td>
                          <h4 className="text-success mb-0">
                            {formatCurrency(receipt.amount)}
                          </h4>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Payment Purpose:</strong></td>
                        <td>{receipt.paid_for_name}</td>
                      </tr>
                      <tr>
                        <td><strong>Received By:</strong></td>
                        <td>{receipt.received_by_name}</td>
                      </tr>
                      {receipt.verified_by && (
                        <tr>
                          <td><strong>Verified By:</strong></td>
                          <td>{receipt.verified_by_name}</td>
                        </tr>
                      )}
                    </tbody>
                  </Table>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Payer Information Card */}
          <Card className="border-0 shadow-sm mb-4">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Payer Information</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <p><strong>Name:</strong> {receipt.payer_name}</p>
                  {receipt.payer_phone && (
                    <p><strong>Phone:</strong> {receipt.payer_phone}</p>
                  )}
                  {receipt.payer_email && (
                    <p><strong>Email:</strong> {receipt.payer_email}</p>
                  )}
                </Col>
                <Col md={6}>
                  <p><strong>Student:</strong> {receipt.student_name}</p>
                  <p><strong>Admission No:</strong> {receipt.admission_number}</p>
                  <p><strong>Class:</strong> {receipt.class_level}</p>
                  <p><strong>Term:</strong> {receipt.term_name}</p>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Payment Details Card */}
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Payment Details</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  {receipt.mpesa_transaction_id && (
                    <p>
                      <strong>M-Pesa Transaction ID:</strong><br />
                      <code>{receipt.mpesa_transaction_id}</code>
                    </p>
                  )}
                  {receipt.bank_reference && (
                    <p>
                      <strong>Bank Reference:</strong><br />
                      <code>{receipt.bank_reference}</code>
                    </p>
                  )}
                  {receipt.bank_name && (
                    <p>
                      <strong>Bank Name:</strong><br />
                      {receipt.bank_name}
                    </p>
                  )}
                </Col>
                <Col md={6}>
                  {receipt.mpesa_confirmation_code && (
                    <p>
                      <strong>M-Pesa Confirmation Code:</strong><br />
                      <code>{receipt.mpesa_confirmation_code}</code>
                    </p>
                  )}
                  {receipt.notes && (
                    <p>
                      <strong>Notes:</strong><br />
                      {receipt.notes}
                    </p>
                  )}
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Actions Card */}
          <Card className="border-0 shadow-sm mb-4">
            <Card.Header className="bg-white border-0 py-3">
              <h6 className="mb-0">Actions</h6>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                {receipt.status === 'Pending' && (
                  <Button
                    variant="success"
                    onClick={handleMarkVerified}
                  >
                    Mark as Verified
                  </Button>
                )}
                <Button
                  variant="outline-primary"
                  onClick={handlePrint}
                >
                  <PrintIcon className="me-2" />
                  Print Receipt
                </Button>
                <Button
                  variant="outline-secondary"
                >
                  <DownloadIcon className="me-2" />
                  Download PDF
                </Button>
                <Button
                  variant="outline-danger"
                  onClick={() => navigate('/finance/receipts')}
                >
                  Back to List
                </Button>
              </div>
            </Card.Body>
          </Card>

          {/* Audit Information Card */}
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h6 className="mb-0">Audit Information</h6>
            </Card.Header>
            <Card.Body>
              <small className="text-muted">
                <div>Created: {new Date(receipt.created_at).toLocaleString()}</div>
                {receipt.updated_at && receipt.updated_at !== receipt.created_at && (
                  <div>Last Updated: {new Date(receipt.updated_at).toLocaleString()}</div>
                )}
                {receipt.verified_at && (
                  <div>Verified: {new Date(receipt.verified_at).toLocaleString()}</div>
                )}
                {receipt.printed_at && (
                  <div>Last Printed: {new Date(receipt.printed_at).toLocaleString()}</div>
                )}
              </small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Print Modal */}
      <Modal show={showPrintModal} onHide={() => setShowPrintModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Print Receipt</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="text-center p-4 border" id="receipt-print">
            <h4>DELVOK SCHOOL</h4>
            <p className="mb-1">Official Receipt</p>
            <hr />
            
            <Row className="text-start">
              <Col md={6}>
                <p><strong>Receipt #:</strong> {receipt.receipt_number}</p>
                <p><strong>Date:</strong> {new Date(receipt.date).toLocaleDateString()}</p>
                <p><strong>Student:</strong> {receipt.student_name}</p>
              </Col>
              <Col md={6}>
                <p><strong>Admission No:</strong> {receipt.admission_number}</p>
                <p><strong>Class:</strong> {receipt.class_level}</p>
                <p><strong>Term:</strong> {receipt.term_name}</p>
              </Col>
            </Row>

            <hr />
            
            <div className="text-center mb-3">
              <h5 className="text-success">{formatCurrency(receipt.amount)}</h5>
              <p>Amount Received</p>
            </div>

            <Table bordered className="mb-3">
              <tbody>
                <tr>
                  <td><strong>Payment Purpose</strong></td>
                  <td>{receipt.paid_for_name}</td>
                </tr>
                <tr>
                  <td><strong>Payment Method</strong></td>
                  <td>{receipt.paid_through}</td>
                </tr>
                <tr>
                  <td><strong>Received From</strong></td>
                  <td>{receipt.payer_name}</td>
                </tr>
                {receipt.mpesa_transaction_id && (
                  <tr>
                    <td><strong>Transaction ID</strong></td>
                    <td>{receipt.mpesa_transaction_id}</td>
                  </tr>
                )}
              </tbody>
            </Table>

            <div className="row mt-4">
              <div className="col-6 text-center">
                <p>___________________</p>
                <p>Cashier's Signature</p>
              </div>
              <div className="col-6 text-center">
                <p>___________________</p>
                <p>Payer's Signature</p>
              </div>
            </div>

            <hr />
            <small className="text-muted">
              This is a computer-generated receipt. No signature is required.
            </small>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPrintModal(false)}>
            Close
          </Button>
          <Button variant="primary" onClick={() => window.print()}>
            Print Now
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default ReceiptDetail;