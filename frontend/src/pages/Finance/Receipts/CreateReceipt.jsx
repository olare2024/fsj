import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Form, Button, Alert, 
  InputGroup, Badge, Table 
} from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { academicsAPI } from '../../../services/academicAPI.js';
import { financeAPI } from '../../../services/financeAPI.js';

const CreateReceipt = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [students, setStudents] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [terms, setTerms] = useState([]);

  const [formData, setFormData] = useState({
    student_id: '',
    term_id: '',
    payer_name: '',
    payer_phone: '',
    payer_email: '',
    paid_for: '',
    amount: '',
    paid_through: 'M-Pesa',
    mpesa_transaction_id: '',
    bank_reference: '',
    bank_name: '',
    notes: '',
    status: 'Completed'
  });

  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (formData.student_id) {
      fetchStudentDetails(formData.student_id);
    }
  }, [formData.student_id]);

  const fetchInitialData = async () => {
    try {
      const [studentsRes, allocationsRes, termsRes] = await Promise.all([
        academicAPI.getStudents(),
        financeAPI.getReceiptAllocations(),
        academicAPI.getTerms()
      ]);
      setStudents(studentsRes.data);
      setAllocations(allocationsRes.data);
      setTerms(termsRes.data);
    } catch (err) {
      setError('Failed to load initial data');
    }
  };

  const fetchStudentDetails = async (studentId) => {
    try {
      const response = await academicAPI.getStudent(studentId);
      setSelectedStudent(response.data);
      
      // Auto-fill payer information if not set
      if (!formData.payer_name && response.data.parent_guardian) {
        setFormData(prev => ({
          ...prev,
          payer_name: `${response.data.parent_guardian.first_name} ${response.data.parent_guardian.last_name}`,
          payer_phone: response.data.parent_guardian.phone_number || ''
        }));
      }
    } catch (err) {
      console.error('Error fetching student details:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await financeAPI.createReceipt(formData);
      setSuccess('Receipt created successfully!');
      setTimeout(() => {
        navigate('/finance/receipts');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create receipt');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Create New Receipt</h1>
              <p className="text-muted mb-0">Record a new payment receipt</p>
            </div>
            <Button 
              variant="outline-secondary" 
              onClick={() => navigate('/finance/receipts')}
            >
              Back to Receipts
            </Button>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Row>
        <Col lg={8}>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Receipt Information</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Student *</Form.Label>
                      <Form.Select
                        value={formData.student_id}
                        onChange={(e) => handleInputChange('student_id', e.target.value)}
                        required
                      >
                        <option value="">Select Student</option>
                        {students.map(student => (
                          <option key={student.id} value={student.id}>
                            {student.full_name} - {student.admission_number}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Term *</Form.Label>
                      <Form.Select
                        value={formData.term_id}
                        onChange={(e) => handleInputChange('term_id', e.target.value)}
                        required
                      >
                        <option value="">Select Term</option>
                        {terms.map(term => (
                          <option key={term.id} value={term.id}>
                            {term.name} - {term.academic_year}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Payer Name *</Form.Label>
                      <Form.Control
                        type="text"
                        value={formData.payer_name}
                        onChange={(e) => handleInputChange('payer_name', e.target.value)}
                        required
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Payer Phone</Form.Label>
                      <Form.Control
                        type="text"
                        value={formData.payer_phone}
                        onChange={(e) => handleInputChange('payer_phone', e.target.value)}
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
                        value={formData.paid_for}
                        onChange={(e) => handleInputChange('paid_for', e.target.value)}
                        required
                      >
                        <option value="">Select Purpose</option>
                        {allocations.map(allocation => (
                          <option key={allocation.id} value={allocation.id}>
                            {allocation.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Amount *</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>KES</InputGroup.Text>
                        <Form.Control
                          type="number"
                          step="0.01"
                          value={formData.amount}
                          onChange={(e) => handleInputChange('amount', e.target.value)}
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
                        value={formData.paid_through}
                        onChange={(e) => handleInputChange('paid_through', e.target.value)}
                        required
                      >
                        <option value="M-Pesa">M-Pesa</option>
                        <option value="Bank Transfer">Bank Transfer</option>
                        <option value="Cash">Cash</option>
                        <option value="Cheque">Cheque</option>
                        <option value="Airtel Money">Airtel Money</option>
                        <option value="Other">Other</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Status</Form.Label>
                      <Form.Select
                        value={formData.status}
                        onChange={(e) => handleInputChange('status', e.target.value)}
                      >
                        <option value="Completed">Completed</option>
                        <option value="Pending">Pending</option>
                        <option value="Cancelled">Cancelled</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>

                {formData.paid_through === 'M-Pesa' && (
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>M-Pesa Transaction ID</Form.Label>
                        <Form.Control
                          type="text"
                          value={formData.mpesa_transaction_id}
                          onChange={(e) => handleInputChange('mpesa_transaction_id', e.target.value)}
                          placeholder="e.g., NLJ7RT25"
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                )}

                {formData.paid_through === 'Bank Transfer' && (
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Bank Reference</Form.Label>
                        <Form.Control
                          type="text"
                          value={formData.bank_reference}
                          onChange={(e) => handleInputChange('bank_reference', e.target.value)}
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Bank Name</Form.Label>
                        <Form.Control
                          type="text"
                          value={formData.bank_name}
                          onChange={(e) => handleInputChange('bank_name', e.target.value)}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                )}

                <Form.Group className="mb-3">
                  <Form.Label>Notes</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => handleInputChange('notes', e.target.value)}
                    placeholder="Additional notes or comments..."
                  />
                </Form.Group>

                <div className="d-flex justify-content-end">
                  <Button 
                    variant="outline-secondary" 
                    className="me-2"
                    onClick={() => navigate('/finance/receipts')}
                  >
                    Cancel
                  </Button>
                  <Button 
                    variant="primary" 
                    type="submit" 
                    disabled={loading}
                  >
                    {loading ? 'Creating...' : 'Create Receipt'}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Student Information Card */}
          {selectedStudent && (
            <Card className="border-0 shadow-sm mb-4">
              <Card.Header className="bg-white border-0 py-3">
                <h6 className="mb-0">Student Information</h6>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <strong>{selectedStudent.full_name}</strong>
                  <br />
                  <small className="text-muted">
                    Admission: {selectedStudent.admission_number}
                  </small>
                </div>
                <div className="mb-2">
                  <small>
                    <strong>Class:</strong> {selectedStudent.class_level}
                  </small>
                </div>
                <div className="mb-2">
                  <small>
                    <strong>Stream:</strong> {selectedStudent.stream || 'N/A'}
                  </small>
                </div>
                {selectedStudent.parent_guardian && (
                  <div className="mt-3">
                    <small className="text-muted">Parent/Guardian</small>
                    <div>
                      <strong>
                        {selectedStudent.parent_guardian.first_name} {selectedStudent.parent_guardian.last_name}
                      </strong>
                    </div>
                    <small className="text-muted">
                      {selectedStudent.parent_guardian.phone_number}
                    </small>
                  </div>
                )}
              </Card.Body>
            </Card>
          )}

          {/* Quick Actions Card */}
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h6 className="mb-0">Quick Actions</h6>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button 
                  variant="outline-primary" 
                  size="sm"
                  onClick={() => navigate('/finance/receipts/bulk-upload')}
                >
                  Bulk Upload Receipts
                </Button>
                <Button 
                  variant="outline-secondary" 
                  size="sm"
                  onClick={() => navigate('/finance/fee-structure')}
                >
                  View Fee Structure
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default CreateReceipt;