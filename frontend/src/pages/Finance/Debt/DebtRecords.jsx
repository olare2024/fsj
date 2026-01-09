import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, InputGroup, Alert, Dropdown, Modal, Spinner
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  Search, Filter, Download, Eye, Send, 
  ExclamationTriangle, FileText, Person, Calendar
} from 'react-bootstrap-icons';

const DebtRecords = () => {
  const { currentUser } = useAuth();
  const [debts, setDebts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    is_overdue: '',
    student_name: '',
    term: '',
    from_due_date: '',
    to_due_date: ''
  });
  const [selectedDebt, setSelectedDebt] = useState(null);
  const [showReminderModal, setShowReminderModal] = useState(false);
  const [reminderType, setReminderType] = useState('sms');

  useEffect(() => {
    fetchDebts();
  }, [filters]);

  const fetchDebts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });

      const response = await financeAPI.get(`/debt-records/?${params}`);
      setDebts(response.data);
    } catch (err) {
      setError('Failed to load debt records');
    } finally {
      setLoading(false);
    }
  };

  const handleSendReminder = async () => {
    try {
      await financeAPI.post(`/debt-records/${selectedDebt.id}/send_reminder/`, {
        reminder_type: reminderType
      });
      setShowReminderModal(false);
      setSelectedDebt(null);
      fetchDebts();
    } catch (err) {
      setError('Failed to send reminder');
    }
  };

  const handleApplyPenalty = async (debtId) => {
    try {
      await financeAPI.post(`/debt-records/${debtId}/apply_late_penalty/`);
      fetchDebts();
    } catch (err) {
      setError('Failed to apply late penalty');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const getOverdueStatus = (debt) => {
    if (debt.is_overdue) return 'danger';
    if (debt.balance > 0 && !debt.is_overdue) return 'warning';
    return 'success';
  };

  const getOverdueText = (debt) => {
    if (debt.is_overdue) return `Overdue by ${debt.overdue_days} days`;
    if (debt.balance > 0) return 'Pending';
    return 'Paid';
  };

  const totalOutstanding = debts.reduce((sum, debt) => sum + parseFloat(debt.balance), 0);
  const overdueCount = debts.filter(d => d.is_overdue).length;
  const pendingCount = debts.filter(d => d.balance > 0 && !d.is_overdue).length;

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading debt records...</p>
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
            <div>
              <h1 className="h3 mb-1">Debt Management</h1>
              <p className="text-muted mb-0">Monitor and manage student fee balances</p>
            </div>
            <div>
              <Button 
                as={Link} 
                to="/finance/debt-reports" 
                variant="outline-primary" 
                className="me-2"
              >
                Debt Reports
              </Button>
              <Button variant="primary">
                <Download className="me-2" />
                Export Debtors
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="border-0 bg-primary text-white">
            <Card.Body>
              <h4>{formatCurrency(totalOutstanding)}</h4>
              <p className="mb-0">Total Outstanding</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-warning text-dark">
            <Card.Body>
              <h4>{pendingCount}</h4>
              <p className="mb-0">Pending Payments</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-danger text-white">
            <Card.Body>
              <h4>{overdueCount}</h4>
              <p className="mb-0">Overdue Accounts</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-success text-white">
            <Card.Body>
              <h4>{debts.length - pendingCount - overdueCount}</h4>
              <p className="mb-0">Accounts Clear</p>
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
                    <Form.Label>Overdue Status</Form.Label>
                    <Form.Select
                      value={filters.is_overdue}
                      onChange={(e) => setFilters({...filters, is_overdue: e.target.value})}
                    >
                      <option value="">All Status</option>
                      <option value="true">Overdue Only</option>
                      <option value="false">Not Overdue</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>From Due Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.from_due_date}
                      onChange={(e) => setFilters({...filters, from_due_date: e.target.value})}
                    />
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>To Due Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.to_due_date}
                      onChange={(e) => setFilters({...filters, to_due_date: e.target.value})}
                    />
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Search Student</Form.Label>
                    <InputGroup>
                      <Form.Control
                        type="text"
                        placeholder="Student name..."
                        value={filters.student_name}
                        onChange={(e) => setFilters({...filters, student_name: e.target.value})}
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

      {/* Debt Records Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Student Debt Records</h5>
              <span className="text-muted">{debts.length} records found</span>
            </Card.Header>
            <Card.Body className="p-0">
              <Table responsive hover>
                <thead className="bg-light">
                  <tr>
                    <th>Student</th>
                    <th>Admission No.</th>
                    <th>Term</th>
                    <th>Total Debt</th>
                    <th>Amount Paid</th>
                    <th>Balance</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {debts.map((debt) => (
                    <tr key={debt.id}>
                      <td>
                        <div>
                          <strong>{debt.student_details?.user?.get_full_name}</strong>
                          <div className="text-muted small">
                            Class: {debt.student_details?.grade_level}
                          </div>
                        </div>
                      </td>
                      <td>{debt.student_details?.admission_number}</td>
                      <td>{debt.term_details?.name}</td>
                      <td>{formatCurrency(debt.amount_added)}</td>
                      <td>{formatCurrency(debt.amount_paid)}</td>
                      <td>
                        <strong className={
                          debt.balance > 0 ? 'text-danger' : 'text-success'
                        }>
                          {formatCurrency(debt.balance)}
                        </strong>
                      </td>
                      <td>
                        {debt.due_date ? new Date(debt.due_date).toLocaleDateString() : 'N/A'}
                      </td>
                      <td>
                        <Badge bg={getOverdueStatus(debt)}>
                          {getOverdueText(debt)}
                        </Badge>
                      </td>
                      <td>
                        <Dropdown>
                          <Dropdown.Toggle variant="outline-primary" size="sm">
                            Actions
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            <Dropdown.Item 
                              as={Link} 
                              to={`/finance/student-debts/${debt.student}`}
                            >
                              <Eye className="me-2" />
                              View Details
                            </Dropdown.Item>
                            <Dropdown.Item
                              onClick={() => {
                                setSelectedDebt(debt);
                                setShowReminderModal(true);
                              }}
                            >
                              <Send className="me-2" />
                              Send Reminder
                            </Dropdown.Item>
                            {debt.is_overdue && (
                              <Dropdown.Item
                                onClick={() => handleApplyPenalty(debt.id)}
                              >
                                <ExclamationTriangle className="me-2" />
                                Apply Late Penalty
                              </Dropdown.Item>
                            )}
                          </Dropdown.Menu>
                        </Dropdown>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {debts.length === 0 && (
                <div className="text-center py-5">
                  <FileText size={48} className="text-muted mb-3" />
                  <p className="text-muted">No debt records found</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Reminder Modal */}
      <Modal show={showReminderModal} onHide={() => setShowReminderModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Send Payment Reminder</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Send payment reminder for:</p>
          {selectedDebt && (
            <div className="bg-light p-3 rounded mb-3">
              <strong>{selectedDebt.student_details?.user?.get_full_name}</strong><br />
              Admission: {selectedDebt.student_details?.admission_number}<br />
              Balance: {formatCurrency(selectedDebt.balance)}<br />
              Term: {selectedDebt.term_details?.name}
            </div>
          )}
          <Form.Group>
            <Form.Label>Reminder Type</Form.Label>
            <Form.Select
              value={reminderType}
              onChange={(e) => setReminderType(e.target.value)}
            >
              <option value="sms">SMS Reminder</option>
              <option value="email">Email Reminder</option>
            </Form.Select>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowReminderModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSendReminder}>
            <Send className="me-2" />
            Send Reminder
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default DebtRecords;