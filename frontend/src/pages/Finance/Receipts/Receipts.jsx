import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, InputGroup, Alert, Dropdown, Modal 
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { ReceiptIcon, FilterIcon, DownloadIcon, EyeIcon, EditIcon } from '../../../components/Icons';

const Receipts = () => {
  const { currentUser } = useAuth();
  const [receipts, setReceipts] = useState([]);
  const [filteredReceipts, setFilteredReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    status: '',
    paidThrough: '',
    studentName: '',
    receiptNumber: ''
  });

  useEffect(() => {
    fetchReceipts();
  }, []);

  useEffect(() => {
    filterReceipts();
  }, [receipts, filters]);

  const fetchReceipts = async () => {
    try {
      const response = await financeAPI.getReceipts();
      setReceipts(response.data);
    } catch (err) {
      setError('Failed to load receipts');
    } finally {
      setLoading(false);
    }
  };

  const filterReceipts = () => {
    let filtered = receipts;

    if (filters.startDate) {
      filtered = filtered.filter(receipt => 
        new Date(receipt.date) >= new Date(filters.startDate)
      );
    }

    if (filters.endDate) {
      filtered = filtered.filter(receipt => 
        new Date(receipt.date) <= new Date(filters.endDate)
      );
    }

    if (filters.status) {
      filtered = filtered.filter(receipt => receipt.status === filters.status);
    }

    if (filters.paidThrough) {
      filtered = filtered.filter(receipt => receipt.paid_through === filters.paidThrough);
    }

    if (filters.studentName) {
      filtered = filtered.filter(receipt => 
        receipt.student_name.toLowerCase().includes(filters.studentName.toLowerCase())
      );
    }

    if (filters.receiptNumber) {
      filtered = filtered.filter(receipt => 
        receipt.receipt_number.toLowerCase().includes(filters.receiptNumber.toLowerCase())
      );
    }

    setFilteredReceipts(filtered);
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
      status: '',
      paidThrough: '',
      studentName: '',
      receiptNumber: ''
    });
  };

  const handleDeleteReceipt = async () => {
    try {
      await financeAPI.deleteReceipt(selectedReceipt.id);
      setShowDeleteModal(false);
      setSelectedReceipt(null);
      fetchReceipts();
    } catch (err) {
      setError('Failed to delete receipt');
    }
  };

  const handleMarkVerified = async (receiptId) => {
    try {
      await financeAPI.markReceiptVerified(receiptId);
      fetchReceipts();
    } catch (err) {
      setError('Failed to mark receipt as verified');
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
      case 'Completed': return 'success';
      case 'Pending': return 'warning';
      case 'Cancelled': return 'danger';
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

  const exportToExcel = () => {
    // Implement Excel export functionality
    console.log('Exporting receipts to Excel');
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
      {/* Page Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Receipt Management</h1>
              <p className="text-muted mb-0">Manage and track all payment receipts</p>
            </div>
            <div>
              <Button 
                as={Link} 
                to="/finance/receipts/bulk-upload" 
                variant="outline-primary" 
                className="me-2"
              >
                Bulk Upload
              </Button>
              <Button 
                as={Link} 
                to="/finance/receipts/create" 
                variant="primary"
              >
                <ReceiptIcon className="me-2" />
                New Receipt
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

      {/* Filters Card */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h6 className="mb-0">
                  <FilterIcon className="me-2" />
                  Filters
                </h6>
                <div>
                  <Button
                    variant="outline-secondary"
                    size="sm"
                    onClick={() => setShowFilters(!showFilters)}
                    className="me-2"
                  >
                    {showFilters ? 'Hide Filters' : 'Show Filters'}
                  </Button>
                  <Button
                    variant="outline-secondary"
                    size="sm"
                    onClick={clearFilters}
                  >
                    Clear All
                  </Button>
                </div>
              </div>
            </Card.Header>
            {showFilters && (
              <Card.Body>
                <Row>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Start Date</Form.Label>
                      <Form.Control
                        type="date"
                        value={filters.startDate}
                        onChange={(e) => handleFilterChange('startDate', e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>End Date</Form.Label>
                      <Form.Control
                        type="date"
                        value={filters.endDate}
                        onChange={(e) => handleFilterChange('endDate', e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Status</Form.Label>
                      <Form.Select
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                      >
                        <option value="">All Status</option>
                        <option value="Pending">Pending</option>
                        <option value="Completed">Completed</option>
                        <option value="Cancelled">Cancelled</option>
                        <option value="Refunded">Refunded</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Payment Method</Form.Label>
                      <Form.Select
                        value={filters.paidThrough}
                        onChange={(e) => handleFilterChange('paidThrough', e.target.value)}
                      >
                        <option value="">All Methods</option>
                        <option value="M-Pesa">M-Pesa</option>
                        <option value="Bank Transfer">Bank Transfer</option>
                        <option value="Cash">Cash</option>
                        <option value="Cheque">Cheque</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Student Name</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Search by student name"
                        value={filters.studentName}
                        onChange={(e) => handleFilterChange('studentName', e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Receipt Number</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Search by receipt number"
                        value={filters.receiptNumber}
                        onChange={(e) => handleFilterChange('receiptNumber', e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                </Row>
                <div className="d-flex justify-content-between align-items-center">
                  <small className="text-muted">
                    Showing {filteredReceipts.length} of {receipts.length} receipts
                  </small>
                  <Button variant="outline-primary" size="sm" onClick={exportToExcel}>
                    <DownloadIcon className="me-1" />
                    Export Excel
                  </Button>
                </div>
              </Card.Body>
            )}
          </Card>
        </Col>
      </Row>

      {/* Receipts Table */}
      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">All Receipts</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {filteredReceipts.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Receipt #</th>
                      <th>Date</th>
                      <th>Student</th>
                      <th>Payer</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Status</th>
                      <th>Received By</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredReceipts.map((receipt) => (
                      <tr key={receipt.id}>
                        <td>
                          <strong>{receipt.receipt_number}</strong>
                        </td>
                        <td>{new Date(receipt.date).toLocaleDateString()}</td>
                        <td>
                          <div>
                            <strong>{receipt.student_name}</strong>
                            <br />
                            <small className="text-muted">{receipt.admission_number}</small>
                          </div>
                        </td>
                        <td>{receipt.payer_name}</td>
                        <td>
                          <strong>{formatCurrency(receipt.amount)}</strong>
                        </td>
                        <td>
                          <Badge bg={getMethodVariant(receipt.paid_through)}>
                            {receipt.paid_through}
                          </Badge>
                        </td>
                        <td>
                          <Badge bg={getStatusVariant(receipt.status)}>
                            {receipt.status}
                          </Badge>
                        </td>
                        <td>{receipt.received_by_name}</td>
                        <td>
                          <Dropdown>
                            <Dropdown.Toggle variant="outline-primary" size="sm" id="dropdown-basic">
                              Actions
                            </Dropdown.Toggle>
                            <Dropdown.Menu>
                              <Dropdown.Item 
                                as={Link} 
                                to={`/finance/receipts/${receipt.id}`}
                              >
                                <EyeIcon className="me-2" />
                                View Details
                              </Dropdown.Item>
                              <Dropdown.Item 
                                as={Link} 
                                to={`/finance/receipts/${receipt.id}/edit`}
                              >
                                <EditIcon className="me-2" />
                                Edit
                              </Dropdown.Item>
                              {receipt.status === 'Pending' && (
                                <Dropdown.Item 
                                  onClick={() => handleMarkVerified(receipt.id)}
                                >
                                  Mark as Verified
                                </Dropdown.Item>
                              )}
                              <Dropdown.Divider />
                              <Dropdown.Item 
                                className="text-danger"
                                onClick={() => {
                                  setSelectedReceipt(receipt);
                                  setShowDeleteModal(true);
                                }}
                              >
                                Delete Receipt
                              </Dropdown.Item>
                            </Dropdown.Menu>
                          </Dropdown>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No receipts found matching your criteria</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Summary Statistics */}
      <Row className="mt-4">
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h4 className="text-primary">
                {formatCurrency(
                  filteredReceipts.reduce((sum, receipt) => sum + receipt.amount, 0)
                )}
              </h4>
              <p className="text-muted mb-0">Total Amount</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h4 className="text-success">
                {filteredReceipts.filter(r => r.status === 'Completed').length}
              </h4>
              <p className="text-muted mb-0">Completed</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h4 className="text-warning">
                {filteredReceipts.filter(r => r.status === 'Pending').length}
              </h4>
              <p className="text-muted mb-0">Pending</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h4 className="text-danger">
                {filteredReceipts.filter(r => r.status === 'Cancelled').length}
              </h4>
              <p className="text-muted mb-0">Cancelled</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to delete receipt <strong>{selectedReceipt?.receipt_number}</strong>?
          This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteReceipt}>
            Delete Receipt
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Receipts;