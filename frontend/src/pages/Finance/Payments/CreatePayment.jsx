import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Form, Button, 
  Alert, InputGroup, Modal
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { ArrowLeft, Save, Upload } from 'react-bootstrap-icons';

const CreatePayment = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [paymentAllocations, setPaymentAllocations] = useState([]);
  const [showSupportingModal, setShowSupportingModal] = useState(false);

  const [formData, setFormData] = useState({
    paid_to_name: '',
    paid_to_phone: '',
    paid_to_email: '',
    paid_for: '',
    amount: '',
    paid_through: 'Cash',
    description: '',
    supporting_document: null,
    is_recurring: false,
    recurrence_pattern: ''
  });

  useEffect(() => {
    fetchPaymentAllocations();
  }, []);

  const fetchPaymentAllocations = async () => {
    try {
      const response = await financeAPI.get('/payment-allocations/?active=true');
      setPaymentAllocations(response.data);
    } catch (err) {
      console.error('Error fetching payment allocations:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : 
              type === 'file' ? files[0] : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const submitData = new FormData();
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== '') {
          submitData.append(key, formData[key]);
        }
      });

      await financeAPI.post('/payments/', submitData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setSuccess('Payment created successfully!');
      setTimeout(() => {
        navigate('/finance/payments');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create payment');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    return formData.paid_to_name && formData.paid_for && formData.amount;
  };

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
                <h1 className="h3 mb-1">Create New Payment</h1>
                <p className="text-muted mb-0">Record a new expenditure payment</p>
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
              <h5 className="mb-0">Payment Details</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Payee Name *</Form.Label>
                      <Form.Control
                        type="text"
                        name="paid_to_name"
                        value={formData.paid_to_name}
                        onChange={handleInputChange}
                        placeholder="Enter payee full name"
                        required
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Phone Number</Form.Label>
                      <Form.Control
                        type="tel"
                        name="paid_to_phone"
                        value={formData.paid_to_phone}
                        onChange={handleInputChange}
                        placeholder="+254..."
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Payment Purpose *</Form.Label>
                      <Form.Select
                        name="paid_for"
                        value={formData.paid_for}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="">Select purpose</option>
                        {paymentAllocations.map(allocation => (
                          <option key={allocation.id} value={allocation.id}>
                            {allocation.name} ({allocation.category})
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Amount (KES) *</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>KES</InputGroup.Text>
                        <Form.Control
                          type="number"
                          name="amount"
                          value={formData.amount}
                          onChange={handleInputChange}
                          placeholder="0.00"
                          min="0"
                          step="0.01"
                          required
                        />
                      </InputGroup>
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Payment Method *</Form.Label>
                      <Form.Select
                        name="paid_through"
                        value={formData.paid_through}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="Cash">Cash</option>
                        <option value="M-Pesa">M-Pesa</option>
                        <option value="Bank Transfer">Bank Transfer</option>
                        <option value="Cheque">Cheque</option>
                        <option value="Airtel Money">Airtel Money</option>
                        <option value="Other">Other</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Email</Form.Label>
                      <Form.Control
                        type="email"
                        name="paid_to_email"
                        value={formData.paid_to_email}
                        onChange={handleInputChange}
                        placeholder="payee@example.com"
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Form.Group className="mb-3">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder="Detailed description of this payment..."
                  />
                </Form.Group>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Check
                        type="checkbox"
                        name="is_recurring"
                        label="This is a recurring payment"
                        checked={formData.is_recurring}
                        onChange={handleInputChange}
                      />
                    </Form.Group>
                  </Col>
                  {formData.is_recurring && (
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Recurrence Pattern</Form.Label>
                        <Form.Select
                          name="recurrence_pattern"
                          value={formData.recurrence_pattern}
                          onChange={handleInputChange}
                        >
                          <option value="">Select pattern</option>
                          <option value="monthly">Monthly</option>
                          <option value="quarterly">Quarterly</option>
                          <option value="yearly">Yearly</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  )}
                </Row>

                <Form.Group className="mb-4">
                  <Form.Label>Supporting Document</Form.Label>
                  <Form.Control
                    type="file"
                    name="supporting_document"
                    onChange={handleInputChange}
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  />
                  <Form.Text className="text-muted">
                    Upload invoice, receipt, or other supporting document (PDF, images, Word)
                  </Form.Text>
                </Form.Group>

                <div className="d-flex justify-content-between">
                  <Button 
                    as={Link} 
                    to="/finance/payments" 
                    variant="outline-secondary"
                  >
                    Cancel
                  </Button>
                  <Button 
                    type="submit" 
                    variant="primary" 
                    disabled={!validateForm() || loading}
                  >
                    {loading ? 'Creating...' : (
                      <>
                        <Save className="me-2" />
                        Create Payment
                      </>
                    )}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Quick Help Card */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">Payment Guidelines</h6>
            </Card.Header>
            <Card.Body>
              <ul className="small text-muted">
                <li>Ensure payee details are accurate</li>
                <li>Select appropriate payment purpose</li>
                <li>Attach supporting documents for audit trail</li>
                <li>Recurring payments will auto-generate future payments</li>
                <li>All payments require approval if over threshold</li>
              </ul>
            </Card.Body>
          </Card>

          {/* Payment Summary Card */}
          <Card className="mt-3">
            <Card.Header>
              <h6 className="mb-0">Payment Summary</h6>
            </Card.Header>
            <Card.Body>
              {formData.amount && (
                <div className="text-center">
                  <h4 className="text-primary">
                    KES {parseFloat(formData.amount).toLocaleString()}
                  </h4>
                  <p className="text-muted mb-1">
                    {paymentAllocations.find(a => a.id == formData.paid_for)?.name || 'No purpose selected'}
                  </p>
                  <small className="text-muted">
                    Method: {formData.paid_through}
                  </small>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default CreatePayment;