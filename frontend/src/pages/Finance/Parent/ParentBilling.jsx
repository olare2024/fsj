import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Alert, Spinner, ProgressBar, Modal
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  CheckCircle, Clock, ExclamationTriangle, FileText,
  BarChart, People, CurrencyDollar, ArrowRepeat,
  GraphUp, Calendar, Inbox, // Use GraphUp instead of TrendingUp
  ExclamationCircle, Cash, Receipt,
  Wallet, CreditCard
} from 'react-bootstrap-icons';

const ParentBilling = () => {
  const { currentUser } = useAuth();
  const [billingData, setBillingData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedChild, setSelectedChild] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      const response = await financeAPI.get('/parent/billing/');
      setBillingData(response.data);
    } catch (err) {
      setError('Failed to load billing information');
    } finally {
      setLoading(false);
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
      case 'paid': return 'success';
      case 'partial': return 'warning';
      case 'overdue': return 'danger';
      case 'pending': return 'info';
      default: return 'secondary';
    }
  };

  const calculateTotalOutstanding = () => {
    if (!billingData.children) return 0;
    return billingData.children.reduce((total, child) => total + child.outstanding_balance, 0);
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading billing information...</p>
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
              <h1 className="h3 mb-1">My Billing & Payments</h1>
              <p className="text-muted mb-0">
                Fee statements and payment history for your children
              </p>
            </div>
            <div>
              <Button variant="primary" as={Link} to="/parent/make-payment">
                <CreditCard className="me-2" />
                Make Payment
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
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{billingData.children?.length || 0}</h4>
                  <p className="mb-0">Children</p>
                </div>
                <Person size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-warning text-dark">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{formatCurrency(calculateTotalOutstanding())}</h4>
                  <p className="mb-0">Total Outstanding</p>
                </div>
                <Calculator size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-success text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>
                    {billingData.children?.filter(child => child.fee_status === 'paid').length || 0}
                  </h4>
                  <p className="mb-0">Fully Paid</p>
                </div>
                <CheckCircle size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-danger text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>
                    {billingData.children?.filter(child => child.fee_status === 'overdue').length || 0}
                  </h4>
                  <p className="mb-0">Overdue</p>
                </div>
                <AlertTriangle size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Children's Fee Summary */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Children's Fee Summary</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {billingData.children?.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Child Name</th>
                      <th>Class</th>
                      <th>Term</th>
                      <th>Total Fees</th>
                      <th>Amount Paid</th>
                      <th>Outstanding</th>
                      <th>Status</th>
                      <th>Due Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {billingData.children.map((child) => (
                      <tr key={child.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            <Person className="me-2 text-muted" />
                            <div>
                              <strong>{child.name}</strong>
                              <div className="text-muted small">
                                Admission: {child.admission_number}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td>{child.class_level}</td>
                        <td>{child.current_term}</td>
                        <td>{formatCurrency(child.total_fees)}</td>
                        <td>
                          <strong className="text-success">
                            {formatCurrency(child.amount_paid)}
                          </strong>
                        </td>
                        <td>
                          <strong className={
                            child.outstanding_balance > 0 ? 'text-danger' : 'text-success'
                          }>
                            {formatCurrency(child.outstanding_balance)}
                          </strong>
                        </td>
                        <td>
                          <Badge bg={getStatusVariant(child.fee_status)}>
                            {child.fee_status.toUpperCase()}
                          </Badge>
                        </td>
                        <td>
                          <div className="d-flex align-items-center">
                            <Clock className={`me-1 ${
                              child.days_until_due < 0 ? 'text-danger' : 
                              child.days_until_due < 7 ? 'text-warning' : 'text-muted'
                            }`} />
                            <span className={
                              child.days_until_due < 0 ? 'text-danger' : 
                              child.days_until_due < 7 ? 'text-warning' : ''
                            }>
                              {child.due_date ? new Date(child.due_date).toLocaleDateString() : 'N/A'}
                            </span>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <Button
                              as={Link}
                              to={`/parent/fee-statement/${child.id}`}
                              variant="outline-primary"
                              size="sm"
                            >
                              <FileText size={14} />
                            </Button>
                            {child.outstanding_balance > 0 && (
                              <Button
                                variant="outline-success"
                                size="sm"
                                onClick={() => {
                                  setSelectedChild(child);
                                  setShowPaymentModal(true);
                                }}
                              >
                                <CreditCard size={14} />
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
                  <Person size={48} className="text-muted mb-3" />
                  <h5>No Children Found</h5>
                  <p className="text-muted">
                    No children are associated with your account
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Payment Progress */}
      {billingData.children?.length > 0 && (
        <Row className="mt-4">
          <Col>
            <Card>
              <Card.Header>
                <h5 className="mb-0">Overall Payment Progress</h5>
              </Card.Header>
              <Card.Body>
                {billingData.children.map((child) => (
                  <div key={child.id} className="mb-3">
                    <div className="d-flex justify-content-between align-items-center mb-1">
                      <span>
                        <strong>{child.name}</strong> - {child.class_level}
                      </span>
                      <span>
                        {Math.round((child.amount_paid / child.total_fees) * 100)}%
                      </span>
                    </div>
                    <ProgressBar 
                      variant={
                        child.fee_status === 'paid' ? 'success' :
                        child.fee_status === 'partial' ? 'warning' : 'danger'
                      }
                      now={(child.amount_paid / child.total_fees) * 100}
                    />
                    <div className="d-flex justify-content-between mt-1">
                      <small className="text-muted">
                        Paid: {formatCurrency(child.amount_paid)}
                      </small>
                      <small className="text-muted">
                        Total: {formatCurrency(child.total_fees)}
                      </small>
                    </div>
                  </div>
                ))}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Recent Payments */}
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Recent Payments</h5>
              <Button variant="outline-primary" size="sm">
                <Download className="me-2" />
                Export History
              </Button>
            </Card.Header>
            <Card.Body className="p-0">
              {billingData.recent_payments?.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Date</th>
                      <th>Child</th>
                      <th>Receipt #</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Term</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {billingData.recent_payments.map((payment, index) => (
                      <tr key={index}>
                        <td>{new Date(payment.date).toLocaleDateString()}</td>
                        <td>{payment.child_name}</td>
                        <td>
                          <strong>{payment.receipt_number}</strong>
                        </td>
                        <td>
                          <strong className="text-success">
                            {formatCurrency(payment.amount)}
                          </strong>
                        </td>
                        <td>
                          <Badge bg="info">{payment.method}</Badge>
                        </td>
                        <td>{payment.term}</td>
                        <td>
                          <Badge bg={payment.status === 'completed' ? 'success' : 'warning'}>
                            {payment.status}
                          </Badge>
                        </td>
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
      </Row>

      {/* Quick Payment Modal */}
      <Modal show={showPaymentModal} onHide={() => setShowPaymentModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Make Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedChild && (
            <div>
              <p>Make payment for:</p>
              <div className="bg-light p-3 rounded mb-3">
                <strong>{selectedChild.name}</strong><br />
                Class: {selectedChild.class_level}<br />
                Outstanding Balance: {formatCurrency(selectedChild.outstanding_balance)}<br />
                Due Date: {selectedChild.due_date ? new Date(selectedChild.due_date).toLocaleDateString() : 'N/A'}
              </div>
              <Button 
                as={Link}
                to="/parent/make-payment"
                variant="primary"
                className="w-100"
                onClick={() => setShowPaymentModal(false)}
              >
                Proceed to Payment
              </Button>
            </div>
          )}
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default ParentBilling;