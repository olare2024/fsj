import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, Modal, Alert, InputGroup 
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import { financeAPI } from '../../services/financeAPI.js';

const FeeStructure = () => {
  const { currentUser } = useAuth();
  const [feeStructures, setFeeStructures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingFee, setEditingFee] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    curriculum: 'cbc',
    grade_level: '',
    term: '',
    tuition_fee: 0,
    activity_fee: 0,
    examination_fee: 0,
    boarding_fee: 0,
    transport_fee: 0,
    medical_fee: 0,
    development_fee: 0,
    caution_money: 0,
    late_payment_penalty: 0,
    discount_percentage: 0,
    effective_from: '',
    effective_to: ''
  });

  useEffect(() => {
    fetchFeeStructures();
  }, []);

  const fetchFeeStructures = async () => {
    try {
      const response = await financeAPI.getFeeStructures();
      setFeeStructures(response.data);
    } catch (err) {
      setError('Failed to load fee structures');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingFee) {
        await financeAPI.updateFeeStructure(editingFee.id, formData);
        setSuccess('Fee structure updated successfully');
      } else {
        await financeAPI.createFeeStructure(formData);
        setSuccess('Fee structure created successfully');
      }
      setShowModal(false);
      setEditingFee(null);
      setFormData({
        name: '',
        curriculum: 'cbc',
        grade_level: '',
        term: '',
        tuition_fee: 0,
        activity_fee: 0,
        examination_fee: 0,
        boarding_fee: 0,
        transport_fee: 0,
        medical_fee: 0,
        development_fee: 0,
        caution_money: 0,
        late_payment_penalty: 0,
        discount_percentage: 0,
        effective_from: '',
        effective_to: ''
      });
      fetchFeeStructures();
    } catch (err) {
      setError('Failed to save fee structure');
    }
  };

  const handleEdit = (feeStructure) => {
    setEditingFee(feeStructure);
    setFormData({
      name: feeStructure.name,
      curriculum: feeStructure.curriculum,
      grade_level: feeStructure.grade_level,
      term: feeStructure.term,
      tuition_fee: feeStructure.tuition_fee,
      activity_fee: feeStructure.activity_fee,
      examination_fee: feeStructure.examination_fee,
      boarding_fee: feeStructure.boarding_fee,
      transport_fee: feeStructure.transport_fee,
      medical_fee: feeStructure.medical_fee,
      development_fee: feeStructure.development_fee,
      caution_money: feeStructure.caution_money,
      late_payment_penalty: feeStructure.late_payment_penalty,
      discount_percentage: feeStructure.discount_percentage,
      effective_from: feeStructure.effective_from,
      effective_to: feeStructure.effective_to
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this fee structure?')) {
      try {
        await financeAPI.deleteFeeStructure(id);
        setSuccess('Fee structure deleted successfully');
        fetchFeeStructures();
      } catch (err) {
        setError('Failed to delete fee structure');
      }
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const calculateTotal = (fee) => {
    return fee.tuition_fee + fee.activity_fee + fee.examination_fee + 
           fee.boarding_fee + fee.transport_fee + fee.medical_fee + 
           fee.development_fee + fee.caution_money;
  };

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Fee Structures</h1>
              <p className="text-muted mb-0">Manage school fee structures and components</p>
            </div>
            <Button 
              onClick={() => {
                setEditingFee(null);
                setShowModal(true);
              }}
              variant="primary"
            >
              Add Fee Structure
            </Button>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert variant="success" dismissible onClose={() => setSuccess('')}>{success}</Alert>}

      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">All Fee Structures</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {loading ? (
                <div className="text-center py-4">
                  <div className="spinner-border" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              ) : feeStructures.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Name</th>
                      <th>Curriculum</th>
                      <th>Grade Level</th>
                      <th>Term</th>
                      <th>Total Fees</th>
                      <th>Status</th>
                      <th>Effective From</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feeStructures.map((fee) => (
                      <tr key={fee.id}>
                        <td>
                          <strong>{fee.name}</strong>
                        </td>
                        <td>
                          <Badge bg="info" className="text-uppercase">
                            {fee.curriculum}
                          </Badge>
                        </td>
                        <td>{fee.grade_level_display}</td>
                        <td>{fee.term_name}</td>
                        <td>
                          <strong>{formatCurrency(calculateTotal(fee))}</strong>
                        </td>
                        <td>
                          <Badge bg={fee.is_active ? 'success' : 'secondary'}>
                            {fee.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </td>
                        <td>{new Date(fee.effective_from).toLocaleDateString()}</td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            className="me-1"
                            onClick={() => handleEdit(fee)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleDelete(fee.id)}
                          >
                            Delete
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No fee structures found</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Add/Edit Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingFee ? 'Edit Fee Structure' : 'Add New Fee Structure'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Structure Name</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Curriculum</Form.Label>
                  <Form.Select
                    value={formData.curriculum}
                    onChange={(e) => setFormData({...formData, curriculum: e.target.value})}
                  >
                    <option value="cbc">CBC</option>
                    <option value="8-4-4">8-4-4</option>
                    <option value="igcse">IGCSE</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Grade Level</Form.Label>
                  <Form.Select
                    value={formData.grade_level}
                    onChange={(e) => setFormData({...formData, grade_level: e.target.value})}
                    required
                  >
                    <option value="">Select Grade Level</option>
                    {/* Add grade level options based on curriculum */}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Term</Form.Label>
                  <Form.Select
                    value={formData.term}
                    onChange={(e) => setFormData({...formData, term: e.target.value})}
                    required
                  >
                    <option value="">Select Term</option>
                    {/* Add term options */}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <h6 className="mb-3">Fee Components</h6>
            <Row>
              {[
                { name: 'tuition_fee', label: 'Tuition Fee' },
                { name: 'activity_fee', label: 'Activity Fee' },
                { name: 'examination_fee', label: 'Examination Fee' },
                { name: 'boarding_fee', label: 'Boarding Fee' },
                { name: 'transport_fee', label: 'Transport Fee' },
                { name: 'medical_fee', label: 'Medical Fee' },
                { name: 'development_fee', label: 'Development Fee' },
                { name: 'caution_money', label: 'Caution Money' },
              ].map((field) => (
                <Col md={6} key={field.name}>
                  <Form.Group className="mb-3">
                    <Form.Label>{field.label}</Form.Label>
                    <InputGroup>
                      <InputGroup.Text>KES</InputGroup.Text>
                      <Form.Control
                        type="number"
                        step="0.01"
                        value={formData[field.name]}
                        onChange={(e) => setFormData({...formData, [field.name]: parseFloat(e.target.value) || 0})}
                      />
                    </InputGroup>
                  </Form.Group>
                </Col>
              ))}
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Late Payment Penalty</Form.Label>
                  <InputGroup>
                    <InputGroup.Text>KES</InputGroup.Text>
                    <Form.Control
                      type="number"
                      step="0.01"
                      value={formData.late_payment_penalty}
                      onChange={(e) => setFormData({...formData, late_payment_penalty: parseFloat(e.target.value) || 0})}
                    />
                  </InputGroup>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Discount Percentage</Form.Label>
                  <InputGroup>
                    <Form.Control
                      type="number"
                      step="0.01"
                      value={formData.discount_percentage}
                      onChange={(e) => setFormData({...formData, discount_percentage: parseFloat(e.target.value) || 0})}
                    />
                    <InputGroup.Text>%</InputGroup.Text>
                  </InputGroup>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Effective From</Form.Label>
                  <Form.Control
                    type="date"
                    value={formData.effective_from}
                    onChange={(e) => setFormData({...formData, effective_from: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Effective To</Form.Label>
                  <Form.Control
                    type="date"
                    value={formData.effective_to}
                    onChange={(e) => setFormData({...formData, effective_to: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              {editingFee ? 'Update' : 'Create'} Fee Structure
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default FeeStructure;