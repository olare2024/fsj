import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, Alert, Spinner, Modal, ProgressBar
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  CheckCircle, Clock, ExclamationTriangle, FileText,
  ArrowRepeat, Search, Filter, Download, // Use ArrowRepeat instead of RefreshCw
  Calculator, Bank, CreditCard, Cash,
  Eye, XCircle, Plus, ArrowLeft
} from 'react-bootstrap-icons';

const Reconciliation = () => {
  const { currentUser } = useAuth();
  const [reconciliations, setReconciliations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [showReconcileModal, setShowReconcileModal] = useState(false);
  const [filters, setFilters] = useState({
    status: 'unreconciled',
    type: '',
    date_range: 'current_month'
  });

  useEffect(() => {
    fetchReconciliations();
  }, [filters]);

  const fetchReconciliations = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });

      const response = await financeAPI.get('/reconciliation/');
      setReconciliations(response.data);
    } catch (err) {
      setError('Failed to load reconciliation data');
    } finally {
      setLoading(false);
    }
  };

  const handleReconcile = async (recordId, action) => {
    try {
      await financeAPI.post(`/reconciliation/${recordId}/${action}/`);
      fetchReconciliations();
      setShowReconcileModal(false);
      setSelectedRecord(null);
    } catch (err) {
      setError(`Failed to ${action} record`);
    }
  };

  const handleBulkReconcile = async (recordIds) => {
    try {
      await financeAPI.post('/reconciliation/bulk-reconcile/', {
        record_ids: recordIds
      });
      fetchReconciliations();
    } catch (err) {
      setError('Failed to bulk reconcile records');
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
      case 'reconciled': return 'success';
      case 'unreconciled': return 'warning';
      case 'discrepancy': return 'danger';
      default: return 'secondary';
    }
  };

  const getTypeVariant = (type) => {
    switch (type) {
      case 'receipt': return 'success';
      case 'payment': return 'danger';
      case 'bank_charge': return 'info';
      default: return 'secondary';
    }
  };

  const unreconciledCount = reconciliations.filter(r => r.status === 'unreconciled').length;
  const discrepancyCount = reconciliations.filter(r => r.status === 'discrepancy').length;
  const totalAmount = reconciliations.reduce((sum, record) => sum + parseFloat(record.amount), 0);

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading reconciliation data...</p>
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
                <h1 className="h3 mb-1">Account Reconciliation</h1>
                <p className="text-muted mb-0">
                  Reconcile bank statements with accounting records
                </p>
              </div>
            </div>
            <div>
              <Button 
                variant="outline-primary" 
                onClick={fetchReconciliations}
                disabled={loading}
              >
                <RefreshCw className="me-2" />
                Refresh
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="border-0 bg-warning text-dark">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{unreconciledCount}</h4>
                  <p className="mb-0">Pending Reconciliation</p>
                </div>
                <FileText size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-danger text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{discrepancyCount}</h4>
                  <p className="mb-0">Discrepancies</p>
                </div>
                <XCircle size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-success text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{formatCurrency(totalAmount)}</h4>
                  <p className="mb-0">Total Amount</p>
                </div>
                <Calculator size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-info text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>
                    {reconciliations.length > 0 ? 
                      Math.round((reconciliations.filter(r => r.status === 'reconciled').length / reconciliations.length) * 100) : 0
                    }%
                  </h4>
                  <p className="mb-0">Completion Rate</p>
                </div>
                <CheckCircle size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

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
                      <option value="unreconciled">Unreconciled</option>
                      <option value="reconciled">Reconciled</option>
                      <option value="discrepancy">Discrepancies</option>
                      <option value="">All Status</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Type</Form.Label>
                    <Form.Select
                      value={filters.type}
                      onChange={(e) => setFilters({...filters, type: e.target.value})}
                    >
                      <option value="">All Types</option>
                      <option value="receipt">Receipts</option>
                      <option value="payment">Payments</option>
                      <option value="bank_charge">Bank Charges</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Date Range</Form.Label>
                    <Form.Select
                      value={filters.date_range}
                      onChange={(e) => setFilters({...filters, date_range: e.target.value})}
                    >
                      <option value="current_month">Current Month</option>
                      <option value="last_month">Last Month</option>
                      <option value="current_quarter">Current Quarter</option>
                      <option value="custom">Custom Range</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Quick Actions</Form.Label>
                    <div className="d-grid gap-2">
                      <Button 
                        variant="outline-success"
                        size="sm"
                        onClick={() => handleBulkReconcile(
                          reconciliations.filter(r => r.status === 'unreconciled').map(r => r.id)
                        )}
                        disabled={unreconciledCount === 0}
                      >
                        Reconcile All Clean
                      </Button>
                    </div>
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Reconciliation Progress */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Reconciliation Progress</h6>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span>Overall Progress</span>
                  <span>
                    {reconciliations.filter(r => r.status === 'reconciled').length} / {reconciliations.length}
                  </span>
                </div>
                <ProgressBar 
                  variant="success"
                  now={reconciliations.length > 0 ? 
                    (reconciliations.filter(r => r.status === 'reconciled').length / reconciliations.length * 100) : 0
                  }
                />
              </div>
              <Row>
                <Col md={4}>
                  <div className="text-center p-3 border rounded">
                    <h5 className="text-success">
                      {reconciliations.filter(r => r.status === 'reconciled').length}
                    </h5>
                    <p className="text-muted mb-0">Reconciled</p>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center p-3 border rounded">
                    <h5 className="text-warning">{unreconciledCount}</h5>
                    <p className="text-muted mb-0">Pending</p>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center p-3 border rounded">
                    <h5 className="text-danger">{discrepancyCount}</h5>
                    <p className="text-muted mb-0">Discrepancies</p>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Reconciliation Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Reconciliation Records</h5>
              <span className="text-muted">
                {reconciliations.length} records found
              </span>
            </Card.Header>
            <Card.Body className="p-0">
              {reconciliations.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Date</th>
                      <th>Reference</th>
                      <th>Description</th>
                      <th>Type</th>
                      <th>Amount</th>
                      <th>Bank Amount</th>
                      <th>Difference</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reconciliations.map((record) => (
                      <tr key={record.id}>
                        <td>{new Date(record.date).toLocaleDateString()}</td>
                        <td>
                          <strong>{record.reference}</strong>
                        </td>
                        <td>{record.description}</td>
                        <td>
                          <Badge bg={getTypeVariant(record.type)}>
                            {record.type}
                          </Badge>
                        </td>
                        <td>{formatCurrency(record.amount)}</td>
                        <td>
                          {record.bank_amount ? formatCurrency(record.bank_amount) : 'N/A'}
                        </td>
                        <td>
                          {record.difference !== 0 && (
                            <span className={record.difference > 0 ? 'text-success' : 'text-danger'}>
                              {formatCurrency(record.difference)}
                            </span>
                          )}
                        </td>
                        <td>
                          <Badge bg={getStatusVariant(record.status)}>
                            {record.status}
                          </Badge>
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            {record.status === 'unreconciled' && (
                              <>
                                <Button
                                  variant="outline-success"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedRecord(record);
                                    handleReconcile(record.id, 'reconcile');
                                  }}
                                >
                                  <CheckCircle size={14} />
                                </Button>
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedRecord(record);
                                    setShowReconcileModal(true);
                                  }}
                                >
                                  <XCircle size={14} />
                                </Button>
                              </>
                            )}
                            {record.status === 'reconciled' && (
                              <Button
                                variant="outline-warning"
                                size="sm"
                                onClick={() => handleReconcile(record.id, 'unreconcile')}
                              >
                                Undo
                              </Button>
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
                  <h5>All Records Reconciled!</h5>
                  <p className="text-muted">
                    No pending reconciliation records found for the selected filters
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Discrepancy Modal */}
      <Modal show={showReconcileModal} onHide={() => setShowReconcileModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Report Discrepancy</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Report a discrepancy for this record:</p>
          {selectedRecord && (
            <div className="bg-light p-3 rounded mb-3">
              <strong>Reference: {selectedRecord.reference}</strong><br />
              Record Amount: {formatCurrency(selectedRecord.amount)}<br />
              Type: {selectedRecord.type}<br />
              Date: {new Date(selectedRecord.date).toLocaleDateString()}
            </div>
          )}
          <Form.Group>
            <Form.Label>Discrepancy Amount</Form.Label>
            <Form.Control
              type="number"
              placeholder="Enter bank statement amount"
              step="0.01"
            />
          </Form.Group>
          <Form.Group className="mt-3">
            <Form.Label>Discrepancy Reason</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Explain the discrepancy..."
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowReconcileModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={() => handleReconcile(selectedRecord.id, 'flag-discrepancy')}>
            Report Discrepancy
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Reconciliation;