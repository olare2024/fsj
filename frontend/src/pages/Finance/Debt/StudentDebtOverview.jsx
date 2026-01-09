import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Alert, Spinner, ProgressBar, Modal
} from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  ArrowLeftIcon, DownloadIcon, SendIcon, FileTextIcon, 
  UserIcon, CalendarIcon, CreditCardIcon, HistoryIcon 
} from '../../../components/Icons';

const StudentDebtOverview = () => {
  const { studentId } = useParams();
  const { currentUser } = useAuth();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showReminderModal, setShowReminderModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchStudentDebtOverview();
  }, [studentId]);

  const fetchStudentDebtOverview = async () => {
    try {
      setLoading(true);
      const result = await financeAPI.getStudentDebts({ student: studentId });
      if (result.success) {
        setStudent(result.data);
      } else {
        setError(result.error?.message || 'Failed to load student debt overview');
      }
    } catch (err) {
      setError('Failed to load student debt overview');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendReminder = async (type = 'sms') => {
    try {
      setActionLoading(true);
      const result = await financeAPI.sendDebtReminder(studentId, { type });
      if (result.success) {
        setShowReminderModal(false);
        // Show success message
      } else {
        setError(result.error?.message || 'Failed to send reminder');
      }
    } catch (err) {
      setError('Failed to send reminder');
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
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading student debt overview...</p>
        </div>
      </Container>
    );
  }

  if (!student) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">Student not found</Alert>
        <Button as={Link} to="/finance/debts" variant="primary">
          <ArrowLeftIcon className="me-2" />
          Back to Debts
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
                to="/finance/debts" 
                variant="outline-secondary" 
                className="me-3"
              >
                <ArrowLeftIcon />
              </Button>
              <div>
                <h1 className="h3 mb-1">Student Debt Overview</h1>
                <p className="text-muted mb-0">
                  {student.full_name || student.name} - {student.admission_number || student.id}
                </p>
              </div>
            </div>
            <div>
              <Button 
                variant="outline-warning" 
                className="me-2"
                onClick={() => setShowReminderModal(true)}
                disabled={actionLoading}
              >
                <SendIcon className="me-2" />
                Send Reminder
              </Button>
              <Button variant="outline-primary">
                <DownloadIcon className="me-2" />
                Export Statement
              </Button>
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
          {/* Student Information */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">
                <UserIcon className="me-2" />
                Student Information
              </h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Full Name:</strong></td>
                        <td>{student.full_name || student.name || 'N/A'}</td>
                      </tr>
                      <tr>
                        <td><strong>Admission Number:</strong></td>
                        <td>{student.admission_number || student.id}</td>
                      </tr>
                      <tr>
                        <td><strong>Class Level:</strong></td>
                        <td>{student.class_level || student.class || 'N/A'}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Total Debt:</strong></td>
                        <td className="h5 text-danger">
                          {formatCurrency(student.total_debt || student.outstanding_balance)}
                        </td>
                      </tr>
                      <tr>
                        <td><strong>Unpaid Terms:</strong></td>
                        <td>
                          <Badge bg="warning">
                            {student.unpaid_debts?.length || student.outstanding_items?.length || 0}
                          </Badge>
                        </td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Unpaid Debts */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">
                <CreditCardIcon className="me-2" />
                Outstanding Balances
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              {student.unpaid_debts && student.unpaid_debts.length > 0 ? (
                <Table responsive>
                  <thead className="bg-light">
                    <tr>
                      <th>Term</th>
                      <th>Total Amount</th>
                      <th>Amount Paid</th>
                      <th>Balance</th>
                      <th>Due Date</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {student.unpaid_debts.map((debt) => (
                      <tr key={debt.id}>
                        <td>{debt.term_name || debt.term || 'N/A'}</td>
                        <td>{formatCurrency(debt.amount_added || debt.total_amount)}</td>
                        <td>{formatCurrency(debt.amount_paid || 0)}</td>
                        <td>
                          <strong className="text-danger">
                            {formatCurrency(debt.balance || debt.amount_due)}
                          </strong>
                        </td>
                        <td>
                          {formatDate(debt.due_date)}
                        </td>
                        <td>
                          <Badge bg={debt.is_overdue ? 'danger' : 'warning'}>
                            {debt.is_overdue ? 'Overdue' : 'Pending'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <FileTextIcon size={48} className="text-success mb-3" />
                  <h5>All Clear!</h5>
                  <p className="text-muted">No outstanding balances</p>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Recent Payments */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">
                <HistoryIcon className="me-2" />
                Recent Payment History
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              {student.recent_payments && student.recent_payments.length > 0 ? (
                <Table responsive>
                  <thead className="bg-light">
                    <tr>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Reference</th>
                      <th>Term</th>
                    </tr>
                  </thead>
                  <tbody>
                    {student.recent_payments.map((payment) => (
                      <tr key={payment.id}>
                        <td>{formatDate(payment.paid_on || payment.date)}</td>
                        <td>
                          <strong className="text-success">
                            {formatCurrency(payment.amount)}
                          </strong>
                        </td>
                        <td>
                          <Badge bg="info">{payment.method || 'N/A'}</Badge>
                        </td>
                        <td>{payment.reference || 'N/A'}</td>
                        <td>{payment.term_name || payment.term || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted">No recent payments found</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Debt Summary */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">Debt Summary</h6>
            </Card.Header>
            <Card.Body>
              <div className="text-center">
                <h3 className="text-primary">
                  {formatCurrency(student.total_debt || student.outstanding_balance)}
                </h3>
                <p className="text-muted">Total Outstanding Balance</p>
                
                <div className="mt-4">
                  <div className="d-flex justify-content-between mb-1">
                    <span>Payment Progress</span>
                    <span>
                      {student.unpaid_debts && student.total_debt > 0 ? 
                        Math.round((student.total_debt - student.unpaid_debts.reduce((sum, d) => sum + (parseFloat(d.balance) || 0), 0)) / student.total_debt * 100) : 0
                      }%
                    </span>
                  </div>
                  <ProgressBar 
                    variant="success"
                    now={student.unpaid_debts && student.total_debt > 0 ? 
                      ((student.total_debt - student.unpaid_debts.reduce((sum, d) => sum + (parseFloat(d.balance) || 0), 0)) / student.total_debt * 100) : 0
                    }
                  />
                </div>
              </div>
            </Card.Body>
          </Card>

          {/* Quick Actions */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">Quick Actions</h6>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button 
                  variant="outline-primary"
                  as={Link}
                  to={`/finance/receipts/create?student=${studentId}`}
                >
                  Record Payment
                </Button>
                <Button 
                  variant="outline-warning"
                  onClick={() => setShowReminderModal(true)}
                  disabled={actionLoading}
                >
                  Send Reminder
                </Button>
                <Button variant="outline-info">
                  Print Statement
                </Button>
                <Button 
                  variant="outline-secondary"
                  as={Link}
                  to={`/finance/students/${studentId}/payments`}
                >
                  View Full History
                </Button>
              </div>
            </Card.Body>
          </Card>

          {/* Contact Information */}
          <Card className="mt-3">
            <Card.Header>
              <h6 className="mb-0">Parent/Guardian Contact</h6>
            </Card.Header>
            <Card.Body>
              <p className="small text-muted mb-2">
                Contact information for fee reminders
              </p>
              <div className="bg-light p-2 rounded">
                <small>
                  <strong>Parent Name:</strong> {student.parent_name || 'N/A'}<br />
                  <strong>Phone:</strong> {student.parent_phone || 'N/A'}<br />
                  <strong>Email:</strong> {student.parent_email || 'N/A'}
                </small>
              </div>
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
          <p>Send payment reminder to parent/guardian of:</p>
          <div className="bg-light p-3 rounded mb-3">
            <strong>{student.full_name || student.name}</strong><br />
            Admission: {student.admission_number || student.id}<br />
            Outstanding Balance: {formatCurrency(student.total_debt || student.outstanding_balance)}
          </div>
          <div className="d-grid gap-2">
            <Button 
              variant="outline-primary"
              onClick={() => handleSendReminder('sms')}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <Spinner animation="border" size="sm" className="me-2" />
              ) : (
                'Send SMS Reminder'
              )}
            </Button>
            <Button 
              variant="outline-info"
              onClick={() => handleSendReminder('email')}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <Spinner animation="border" size="sm" className="me-2" />
              ) : (
                'Send Email Reminder'
              )}
            </Button>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowReminderModal(false)}
            disabled={actionLoading}
          >
            Cancel
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default StudentDebtOverview;