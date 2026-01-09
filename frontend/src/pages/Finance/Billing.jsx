import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, InputGroup, Alert, Modal 
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { financeAPI } from '../../services/financeAPI.js';

const Billing = () => {
  const { currentUser } = useAuth();
  const [billingData, setBillingData] = useState({
    outstandingInvoices: [],
    paymentHistory: [],
    totalOutstanding: 0,
    recentPayments: []
  });
  const [loading, setLoading] = useState(true);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState(0);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      const response = await financeAPI.getBilling();
      setBillingData(response.data);
    } catch (error) {
      console.error('Error fetching billing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMakePayment = (invoice) => {
    setSelectedInvoice(invoice);
    setPaymentAmount(invoice.balance);
    setShowPaymentModal(true);
  };

  const processPayment = async () => {
    try {
      await financeAPI.processPayment({
        invoice_id: selectedInvoice.id,
        amount: paymentAmount,
        method: 'M-Pesa', // Default, can be made dynamic
        reference: `INV${selectedInvoice.id}`
      });
      setShowPaymentModal(false);
      fetchBillingData(); // Refresh data
    } catch (error) {
      console.error('Error processing payment:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const { outstandingInvoices, paymentHistory, totalOutstanding, recentPayments } = billingData;

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
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Billing & Invoices</h1>
              <p className="text-muted mb-0">Manage your invoices and payments</p>
            </div>
          </div>
        </Col>
      </Row>

      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={4}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h3 className="text-primary">{formatCurrency(totalOutstanding)}</h3>
              <p className="text-muted mb-0">Total Outstanding</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h3 className="text-warning">{outstandingInvoices.length}</h3>
              <p className="text-muted mb-0">Pending Invoices</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h3 className="text-success">{recentPayments.length}</h3>
              <p className="text-muted mb-0">Recent Payments</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        {/* Outstanding Invoices */}
        <Col lg={6} className="mb-4">
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Outstanding Invoices</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {outstandingInvoices.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Invoice #</th>
                      <th>Due Date</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {outstandingInvoices.map((invoice) => (
                      <tr key={invoice.id}>
                        <td>
                          <strong>{invoice.invoice_number}</strong>
                        </td>
                        <td>{new Date(invoice.due_date).toLocaleDateString()}</td>
                        <td>{formatCurrency(invoice.balance)}</td>
                        <td>
                          <Badge 
                            bg={
                              new Date(invoice.due_date) < new Date() ? 'danger' : 'warning'
                            }
                          >
                            {new Date(invoice.due_date) < new Date() ? 'Overdue' : 'Pending'}
                          </Badge>
                        </td>
                        <td>
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleMakePayment(invoice)}
                          >
                            Pay Now
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No outstanding invoices</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Recent Payments */}
        <Col lg={6} className="mb-4">
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Recent Payments</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {recentPayments.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentPayments.map((payment) => (
                      <tr key={payment.id}>
                        <td>{new Date(payment.paid_on).toLocaleDateString()}</td>
                        <td>{formatCurrency(payment.amount)}</td>
                        <td>
                          <Badge bg="info">{payment.method}</Badge>
                        </td>
                        <td>
                          <Badge bg="success">Completed</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No recent payments</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Payment History */}
      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Payment History</h5>
                <Button as={Link} to="/payment-history" variant="outline-primary" size="sm">
                  View Full History
                </Button>
              </div>
            </Card.Header>
            <Card.Body className="p-0">
              {paymentHistory.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Payment Date</th>
                      <th>Invoice #</th>
                      <th>Description</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Reference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paymentHistory.map((payment) => (
                      <tr key={payment.id}>
                        <td>{new Date(payment.payment_date).toLocaleDateString()}</td>
                        <td>{payment.invoice_number}</td>
                        <td>{payment.description}</td>
                        <td>{formatCurrency(payment.amount)}</td>
                        <td>
                          <Badge bg="secondary">{payment.method}</Badge>
                        </td>
                        <td>
                          <code>{payment.reference}</code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No payment history available</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Payment Modal */}
      <Modal show={showPaymentModal} onHide={() => setShowPaymentModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Make Payment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedInvoice && (
            <>
              <p>
                You are about to pay invoice <strong>{selectedInvoice.invoice_number}</strong>
              </p>
              <Form.Group className="mb-3">
                <Form.Label>Payment Amount</Form.Label>
                <InputGroup>
                  <InputGroup.Text>KES</InputGroup.Text>
                  <Form.Control
                    type="number"
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(parseFloat(e.target.value) || 0)}
                    max={selectedInvoice.balance}
                  />
                </InputGroup>
                <Form.Text className="text-muted">
                  Outstanding balance: {formatCurrency(selectedInvoice.balance)}
                </Form.Text>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Payment Method</Form.Label>
                <Form.Select>
                  <option value="M-Pesa">M-Pesa</option>
                  <option value="Bank Transfer">Bank Transfer</option>
                  <option value="Cash">Cash</option>
                  <option value="Cheque">Cheque</option>
                </Form.Select>
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPaymentModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={processPayment}>
            Process Payment
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Billing;