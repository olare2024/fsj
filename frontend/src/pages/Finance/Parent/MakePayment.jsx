import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Form, Button, 
  Alert, Spinner, Modal, ListGroup, InputGroup
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  ArrowLeft, CreditCard, CheckCircle, Shield,
  Phone, Building, QrCode, Receipt
} from 'react-bootstrap-icons';

const MakePayment = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [paymentData, setPaymentData] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const [paymentInfo, setPaymentInfo] = useState({
    child_id: '',
    amount: '',
    payment_method: 'mpesa',
    phone_number: '',
    term: '',
    description: ''
  });

  useEffect(() => {
    fetchPaymentData();
  }, []);

  const fetchPaymentData = async () => {
    try {
      const response = await financeAPI.get('/parent/make-payment/');
      setPaymentData(response.data);
    } catch (err) {
      setError('Failed to load payment information');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPaymentInfo(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const response = await financeAPI.post('/parent/make-payment/', paymentInfo);
      setSuccess('Payment initiated successfully!');
      setShowConfirmModal(false);
      
      // Redirect to payment status page or show success message
      setTimeout(() => {
        navigate('/parent/billing');
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.message || 'Payment failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const validateForm = () => {
    return paymentInfo.child_id && paymentInfo.amount && paymentInfo.payment_method;
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading payment information...</p>
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
                to="/parent/billing" 
                variant="outline-secondary" 
                className="me-3"
              >
                <ArrowLeft />
              </Button>
              <div>
                <h1 className="h3 mb-1">Make Payment</h1>
                <p className="text-muted mb-0">Pay school fees securely online</p>
              </div>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Row>
        <Col lg={8}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Payment Information</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                {/* Select Child */}
                <Form.Group className="mb-3">
                  <Form.Label>Select Child *</Form.Label>
                  <Form.Select
                    name="child_id"
                    value={paymentInfo.child_id}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Choose child...</option>
                    {paymentData.children?.map((child) => (
                      <option key={child.id} value={child.id}>
                        {child.name} - {child.class_level} (Outstanding: {formatCurrency(child.outstanding_balance)})
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                {/* Amount */}
                <Form.Group className="mb-3">
                  <Form.Label>Amount to Pay (KES) *</Form.Label>
                  <InputGroup>
                    <InputGroup.Text>KES</InputGroup.Text>
                    <Form.Control
                      type="number"
                      name="amount"
                      value={paymentInfo.amount}
                      onChange={handleInputChange}
                      placeholder="Enter amount"
                      min="1"
                      step="0.01"
                      required
                    />
                  </InputGroup>
                  <Form.Text className="text-muted">
                    Minimum payment: KES 100
                  </Form.Text>
                </Form.Group>

                {/* Payment Method */}
                <Form.Group className="mb-3">
                  <Form.Label>Payment Method *</Form.Label>
                  <div>
                    <Form.Check
                      type="radio"
                      name="payment_method"
                      value="mpesa"
                      label={
                        <div className="d-flex align-items-center">
                          <Phone className="me-2 text-success" />
                          M-Pesa
                        </div>
                      }
                      checked={paymentInfo.payment_method === 'mpesa'}
                      onChange={handleInputChange}
                      className="mb-2"
                    />
                    <Form.Check
                      type="radio"
                      name="payment_method"
                      value="bank"
                      label={
                        <div className="d-flex align-items-center">
                          <Building className="me-2 text-primary" />
                          Bank Transfer
                        </div>
                      }
                      checked={paymentInfo.payment_method === 'bank'}
                      onChange={handleInputChange}
                      className="mb-2"
                    />
                    <Form.Check
                      type="radio"
                      name="payment_method"
                      value="card"
                      label={
                        <div className="d-flex align-items-center">
                          <CreditCard className="me-2 text-info" />
                          Credit/Debit Card
                        </div>
                      }
                      checked={paymentInfo.payment_method === 'card'}
                      onChange={handleInputChange}
                    />
                  </div>
                </Form.Group>

                {/* M-Pesa Phone Number */}
                {paymentInfo.payment_method === 'mpesa' && (
                  <Form.Group className="mb-3">
                    <Form.Label>M-Pesa Phone Number *</Form.Label>
                    <InputGroup>
                      <InputGroup.Text>+254</InputGroup.Text>
                      <Form.Control
                        type="tel"
                        name="phone_number"
                        value={paymentInfo.phone_number}
                        onChange={handleInputChange}
                        placeholder="7XXXXXXXX"
                        pattern="[17][0-9]{8}"
                        required
                      />
                    </InputGroup>
                    <Form.Text className="text-muted">
                      Enter your M-Pesa registered phone number
                    </Form.Text>
                  </Form.Group>
                )}

                {/* Term Selection */}
                <Form.Group className="mb-3">
                  <Form.Label>Select Term</Form.Label>
                  <Form.Select
                    name="term"
                    value={paymentInfo.term}
                    onChange={handleInputChange}
                  >
                    <option value="">Current Term (Auto-detected)</option>
                    {paymentData.terms?.map((term) => (
                      <option key={term.id} value={term.id}>
                        {term.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                {/* Description */}
                <Form.Group className="mb-4">
                  <Form.Label>Payment Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="description"
                    value={paymentInfo.description}
                    onChange={handleInputChange}
                    placeholder="Optional: Add any notes about this payment..."
                  />
                </Form.Group>

                <div className="d-flex justify-content-between">
                  <Button 
                    as={Link} 
                    to="/parent/billing" 
                    variant="outline-secondary"
                  >
                    Cancel
                  </Button>
                  <Button 
                    type="button"
                    variant="primary"
                    disabled={!validateForm() || submitting}
                    onClick={() => setShowConfirmModal(true)}
                  >
                    {submitting ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <CreditCard className="me-2" />
                        Proceed to Pay
                      </>
                    )}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>

          {/* Payment Security */}
          <Card className="mt-4">
            <Card.Header>
              <h6 className="mb-0">
                <Shield className="me-2 text-success" />
                Secure Payment
              </h6>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={4} className="text-center mb-3">
                  <Shield size={32} className="text-success mb-2" />
                  <h6>SSL Encrypted</h6>
                  <p className="small text-muted mb-0">
                    All transactions are securely encrypted
                  </p>
                </Col>
                <Col md={4} className="text-center mb-3">
                  <CheckCircle size={32} className="text-primary mb-2" />
                  <h6>Instant Confirmation</h6>
                  <p className="small text-muted mb-0">
                    Receive immediate payment confirmation
                  </p>
                </Col>
                <Col md={4} className="text-center mb-3">
                  <Receipt size={32} className="text-warning mb-2" />
                  <h6>Digital Receipt</h6>
                  <p className="small text-muted mb-0">
                    Get receipt emailed instantly
                  </p>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        {/* Sidebar */}
        <Col lg={4}>
          {/* Selected Child Summary */}
          {paymentInfo.child_id && (
            <Card className="mb-4">
              <Card.Header>
                <h6 className="mb-0">Child Summary</h6>
              </Card.Header>
              <Card.Body>
                {paymentData.children?.map(child => 
                  child.id === paymentInfo.child_id && (
                    <div key={child.id}>
                      <h6>{child.name}</h6>
                      <p className="text-muted mb-2">
                        {child.class_level} • {child.admission_number}
                      </p>
                      <ListGroup variant="flush">
                        <ListGroup.Item className="px-0 py-1 d-flex justify-content-between">
                          <span>Total Fees:</span>
                          <span>{formatCurrency(child.total_fees)}</span>
                        </ListGroup.Item>
                        <ListGroup.Item className="px-0 py-1 d-flex justify-content-between">
                          <span>Amount Paid:</span>
                          <span className="text-success">
                            {formatCurrency(child.amount_paid)}
                          </span>
                        </ListGroup.Item>
                        <ListGroup.Item className="px-0 py-1 d-flex justify-content-between">
                          <span>Outstanding:</span>
                          <span className="text-danger">
                            {formatCurrency(child.outstanding_balance)}
                          </span>
                        </ListGroup.Item>
                      </ListGroup>
                    </div>
                  )
                )}
              </Card.Body>
            </Card>
          )}

          {/* Payment Summary */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">Payment Summary</h6>
            </Card.Header>
            <Card.Body>
              {paymentInfo.amount ? (
                <div>
                  <div className="text-center mb-3">
                    <h4 className="text-primary">
                      {formatCurrency(paymentInfo.amount)}
                    </h4>
                    <p className="text-muted mb-0">Payment Amount</p>
                  </div>
                  <ListGroup variant="flush">
                    <ListGroup.Item className="px-0 py-1 d-flex justify-content-between">
                      <span>Method:</span>
                      <span className="text-capitalize">{paymentInfo.payment_method}</span>
                    </ListGroup.Item>
                    {paymentInfo.payment_method === 'mpesa' && paymentInfo.phone_number && (
                      <ListGroup.Item className="px-0 py-1">
                        <span>Phone: +254{paymentInfo.phone_number}</span>
                      </ListGroup.Item>
                    )}
                    <ListGroup.Item className="px-0 py-1 d-flex justify-content-between">
                      <span>Convenience Fee:</span>
                      <span>{formatCurrency(0)}</span>
                    </ListGroup.Item>
                    <ListGroup.Item className="px-0 py-1 d-flex justify-content-between">
                      <strong>Total:</strong>
                      <strong>{formatCurrency(paymentInfo.amount)}</strong>
                    </ListGroup.Item>
                  </ListGroup>
                </div>
              ) : (
                <div className="text-center text-muted">
                  <p>Enter payment amount to see summary</p>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Help Card */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">Need Help?</h6>
            </Card.Header>
            <Card.Body>
              <p className="small text-muted mb-3">
                For payment assistance, contact our finance office:
              </p>
              <div className="small">
                <div className="mb-2">
                  <strong>Phone:</strong><br />
                  +254 700 000000
                </div>
                <div className="mb-2">
                  <strong>Email:</strong><br />
                  finance@school.edu
                </div>
                <div>
                  <strong>Hours:</strong><br />
                  Mon-Fri: 8:00 AM - 5:00 PM
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Confirmation Modal */}
      <Modal show={showConfirmModal} onHide={() => setShowConfirmModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Please confirm your payment details:</p>
          <div className="bg-light p-3 rounded mb-3">
            <strong>Amount: {formatCurrency(paymentInfo.amount)}</strong><br />
            Payment Method: {paymentInfo.payment_method.toUpperCase()}<br />
            {paymentInfo.payment_method === 'mpesa' && (
              <>Phone: +254{paymentInfo.phone_number}<br /></>
            )}
            {paymentData.children?.map(child => 
              child.id === paymentInfo.child_id && (
                <span key={child.id}>
                  Child: {child.name}<br />
                </span>
              )
            )}
          </div>
          <Alert variant="info" className="small">
            <Shield className="me-2" />
            Your payment is secure and encrypted. You will receive a confirmation message upon successful payment.
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowConfirmModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Processing Payment...
              </>
            ) : (
              <>
                <CheckCircle className="me-2" />
                Confirm & Pay
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default MakePayment;