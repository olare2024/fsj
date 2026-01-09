import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Alert, Spinner, Modal, ListGroup
} from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  Printer, Download, Search, Filter, // Use Printer instead of Print
  Eye, FileText, Calculator, Clock,
  CheckCircle, XCircle, ArrowLeft, People
} from 'react-bootstrap-icons';

const ChildFeeStatement = () => {
  const { childId } = useParams();
  const { currentUser } = useAuth();
  const [feeStatement, setFeeStatement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  useEffect(() => {
    fetchFeeStatement();
  }, [childId]);

  const fetchFeeStatement = async () => {
    try {
      const response = await financeAPI.get(`/parent/fee-statement/${childId}/`);
      setFeeStatement(response.data);
    } catch (err) {
      setError('Failed to load fee statement');
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

  const generatePDF = async () => {
    try {
      const response = await financeAPI.get(`/parent/fee-statement/${childId}/export/`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `fee-statement-${feeStatement.child.admission_number}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to generate PDF statement');
    }
  };

  const printStatement = () => {
    window.print();
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading fee statement...</p>
        </div>
      </Container>
    );
  }

  if (!feeStatement) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">Fee statement not found</Alert>
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
                <h1 className="h3 mb-1">Fee Statement</h1>
                <p className="text-muted mb-0">
                  {feeStatement.child.name} - {feeStatement.child.admission_number}
                </p>
              </div>
            </div>
            <div>
              <Button variant="outline-primary" className="me-2" onClick={generatePDF}>
                <Download className="me-2" />
                Download PDF
              </Button>
              <Button variant="outline-secondary" className="me-2" onClick={printStatement}>
                <Print className="me-2" />
                Print
              </Button>
              {feeStatement.outstanding_balance > 0 && (
                <Button 
                  variant="primary"
                  as={Link}
                  to="/parent/make-payment"
                >
                  <CreditCard className="me-2" />
                  Make Payment
                </Button>
              )}
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

      <Row>
        <Col lg={8}>
          {/* Student Information */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">
                <Person className="me-2" />
                Student Information
              </h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Student Name:</strong></td>
                        <td>{feeStatement.child.name}</td>
                      </tr>
                      <tr>
                        <td><strong>Admission Number:</strong></td>
                        <td>{feeStatement.child.admission_number}</td>
                      </tr>
                      <tr>
                        <td><strong>Class Level:</strong></td>
                        <td>{feeStatement.child.class_level}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
                <Col md={6}>
                  <Table borderless>
                    <tbody>
                      <tr>
                        <td><strong>Current Term:</strong></td>
                        <td>{feeStatement.current_term}</td>
                      </tr>
                      <tr>
                        <td><strong>Academic Year:</strong></td>
                        <td>{feeStatement.academic_year}</td>
                      </tr>
                      <tr>
                        <td><strong>Fee Status:</strong></td>
                        <td>
                          <Badge bg={
                            feeStatement.fee_status === 'paid' ? 'success' :
                            feeStatement.fee_status === 'partial' ? 'warning' : 'danger'
                          }>
                            {feeStatement.fee_status.toUpperCase()}
                          </Badge>
                        </td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Fee Breakdown */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">
                <Calculator className="me-2" />
                Fee Breakdown - {feeStatement.current_term}
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              <Table responsive>
                <thead className="bg-light">
                  <tr>
                    <th>Fee Component</th>
                    <th className="text-end">Amount (KES)</th>
                    <th className="text-end">Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {feeStatement.fee_breakdown?.map((item, index) => (
                    <tr key={index}>
                      <td>{item.component}</td>
                      <td className="text-end">{formatCurrency(item.amount)}</td>
                      <td className="text-end">{item.percentage}%</td>
                    </tr>
                  ))}
                  <tr className="table-active">
                    <td><strong>Total Fees</strong></td>
                    <td className="text-end">
                      <strong>{formatCurrency(feeStatement.total_fees)}</strong>
                    </td>
                    <td className="text-end">100%</td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {/* Payment History */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">
                <Receipt className="me-2" />
                Payment History
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              {feeStatement.payment_history?.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Date</th>
                      <th>Receipt #</th>
                      <th>Description</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Term</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feeStatement.payment_history.map((payment, index) => (
                      <tr key={index}>
                        <td>{new Date(payment.date).toLocaleDateString()}</td>
                        <td>
                          <strong>{payment.receipt_number}</strong>
                        </td>
                        <td>{payment.description}</td>
                        <td>
                          <strong className="text-success">
                            {formatCurrency(payment.amount)}
                          </strong>
                        </td>
                        <td>
                          <Badge bg="info">{payment.method}</Badge>
                        </td>
                        <td>{payment.term}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted">No payment history found</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Sidebar */}
        <Col lg={4}>
          {/* Summary Card */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">Fee Summary</h6>
            </Card.Header>
            <Card.Body>
              <ListGroup variant="flush">
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Total Fees:</span>
                  <strong>{formatCurrency(feeStatement.total_fees)}</strong>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Total Paid:</span>
                  <strong className="text-success">
                    {formatCurrency(feeStatement.total_paid)}
                  </strong>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Outstanding:</span>
                  <strong className={
                    feeStatement.outstanding_balance > 0 ? 'text-danger' : 'text-success'
                  }>
                    {formatCurrency(feeStatement.outstanding_balance)}
                  </strong>
                </ListGroup.Item>
                {feeStatement.due_date && (
                  <ListGroup.Item className="d-flex justify-content-between align-items-center">
                    <span>Due Date:</span>
                    <span className={
                      new Date(feeStatement.due_date) < new Date() ? 'text-danger' : 'text-muted'
                    }>
                      {new Date(feeStatement.due_date).toLocaleDateString()}
                    </span>
                  </ListGroup.Item>
                )}
              </ListGroup>
              {feeStatement.outstanding_balance > 0 && (
                <div className="mt-3">
                  <Button 
                    variant="primary" 
                    className="w-100"
                    as={Link}
                    to="/parent/make-payment"
                  >
                    <CreditCard className="me-2" />
                    Pay Now
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Term-wise Summary */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">
                <Calendar className="me-2" />
                Term-wise Summary
              </h6>
            </Card.Header>
            <Card.Body className="p-0">
              <ListGroup variant="flush">
                {feeStatement.term_summary?.map((term, index) => (
                  <ListGroup.Item key={index}>
                    <div className="d-flex justify-content-between align-items-center mb-1">
                      <strong>{term.term}</strong>
                      <Badge bg={
                        term.status === 'paid' ? 'success' :
                        term.status === 'partial' ? 'warning' : 'danger'
                      }>
                        {term.status}
                      </Badge>
                    </div>
                    <div className="d-flex justify-content-between small text-muted">
                      <span>Paid: {formatCurrency(term.paid)}</span>
                      <span>Total: {formatCurrency(term.total)}</span>
                    </div>
                    <ProgressBar 
                      variant={
                        term.status === 'paid' ? 'success' :
                        term.status === 'partial' ? 'warning' : 'danger'
                      }
                      now={(term.paid / term.total) * 100}
                      className="mt-1"
                    />
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card.Body>
          </Card>

          {/* Important Dates */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">Important Dates</h6>
            </Card.Header>
            <Card.Body className="p-0">
              <ListGroup variant="flush">
                {feeStatement.important_dates?.map((date, index) => (
                  <ListGroup.Item key={index}>
                    <div className="d-flex justify-content-between align-items-center">
                      <span>{date.description}</span>
                      <small className={
                        new Date(date.date) < new Date() ? 'text-danger' : 'text-muted'
                      }>
                        {new Date(date.date).toLocaleDateString()}
                      </small>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Print Styles */}
      <style>{`
        @media print {
          .btn, .navbar, .footer {
            display: none !important;
          }
          .card {
            border: 1px solid #000 !important;
          }
          .table {
            border: 1px solid #000 !important;
          }
          .table th, .table td {
            border: 1px solid #000 !important;
          }
        }
      `}</style>
    </Container>
  );
};

export default ChildFeeStatement;