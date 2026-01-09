import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, Modal, Alert, InputGroup, Dropdown 
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import { financeAPI } from '../../services/financeAPI.js';

const InvoiceManagement = () => {
  const { currentUser } = useAuth();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [generateForm, setGenerateForm] = useState({
    student_id: '',
    term_id: '',
    due_date: '',
    items: [{ description: 'Tuition Fee', amount: 0 }]
  });

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await financeAPI.getInvoices();
      setInvoices(response.data);
    } catch (err) {
      setError('Failed to load invoices');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInvoice = async () => {
    try {
      await financeAPI.generateInvoice(generateForm);
      setSuccess('Invoice generated successfully');
      setShowGenerateModal(false);
      fetchInvoices();
    } catch (err) {
      setError('Failed to generate invoice');
    }
  };

  const handleSendReminder = async (invoiceId) => {
    try {
      await financeAPI.sendInvoiceReminder(invoiceId);
      setSuccess('Reminder sent successfully');
    } catch (err) {
      setError('Failed to send reminder');
    }
  };

  const handleMarkAsPaid = async (invoiceId) => {
    try {
      await financeAPI.markInvoiceAsPaid(invoiceId);
      setSuccess('Invoice marked as paid');
      fetchInvoices();
    } catch (err) {
      setError('Failed to update invoice');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const getStatusVariant = (status, dueDate) => {
    if (status === 'Paid') return 'success';
    if (status === 'Overdue') return 'danger';
    if (new Date(dueDate) < new Date()) return 'danger';
    return 'warning';
  };

  const getStatusText = (status, dueDate) => {
    if (status === 'Paid') return 'Paid';
    if (new Date(dueDate) < new Date()) return 'Overdue';
    return 'Pending';
  };

  const calculateTotal = (items) => {
    return items.reduce((sum, item) => sum + (item.amount || 0), 0);
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
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Invoice Management</h1>
              <p className="text-muted mb-0">Generate and manage student invoices</p>
            </div>
            <Button 
              onClick={() => setShowGenerateModal(true)}
              variant="primary"
            >
              Generate Invoice
            </Button>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert variant="success" dismissible onClose={() => setSuccess('')}>{success}</Alert>}

      {/* Invoice Statistics */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h3 className="text-primary">{invoices.length}</h3>
              <p className="text-muted mb-0">Total Invoices</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h3 className="text-warning">
                {invoices.filter(inv => getStatusText(inv.status, inv.due_date) === 'Pending').length}
              </h3>
              <p className="text-muted mb-0">Pending</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h3 className="text-danger">
                {invoices.filter(inv => getStatusText(inv.status, inv.due_date) === 'Overdue').length}
              </h3>
              <p className="text-muted mb-0">Overdue</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 shadow-sm text-center">
            <Card.Body>
              <h3 className="text-success">
                {invoices.filter(inv => inv.status === 'Paid').length}
              </h3>
              <p className="text-muted mb-0">Paid</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Invoices Table */}
      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">All Invoices</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {invoices.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Invoice #</th>
                      <th>Student</th>
                      <th>Term</th>
                      <th>Due Date</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoices.map((invoice) => (
                      <tr key={invoice.id}>
                        <td>
                          <strong>{invoice.invoice_number}</strong>
                        </td>
                        <td>{invoice.student_name}</td>
                        <td>{invoice.term_name}</td>
                        <td>{new Date(invoice.due_date).toLocaleDateString()}</td>
                        <td>
                          <strong>{formatCurrency(invoice.total_amount)}</strong>
                        </td>
                        <td>
                          <Badge bg={getStatusVariant(invoice.status, invoice.due_date)}>
                            {getStatusText(invoice.status, invoice.due_date)}
                          </Badge>
                        </td>
                        <td>
                          <Dropdown>
                            <Dropdown.Toggle variant="outline-primary" size="sm" id="dropdown-basic">
                              Actions
                            </Dropdown.Toggle>
                            <Dropdown.Menu>
                              <Dropdown.Item 
                                onClick={() => {
                                  setSelectedInvoice(invoice);
                                  setShowPreviewModal(true);
                                }}
                              >
                                View Details
                              </Dropdown.Item>
                              <Dropdown.Item 
                                onClick={() => handleSendReminder(invoice.id)}
                                disabled={invoice.status === 'Paid'}
                              >
                                Send Reminder
                              </Dropdown.Item>
                              <Dropdown.Item 
                                onClick={() => handleMarkAsPaid(invoice.id)}
                                disabled={invoice.status === 'Paid'}
                              >
                                Mark as Paid
                              </Dropdown.Item>
                              <Dropdown.Divider />
                              <Dropdown.Item className="text-danger">
                                Void Invoice
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
                  <p className="text-muted mb-0">No invoices found</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Generate Invoice Modal */}
      <Modal show={showGenerateModal} onHide={() => setShowGenerateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Generate New Invoice</Modal.Title>
        </Modal.Header>
        <Form onSubmit={(e) => { e.preventDefault(); handleGenerateInvoice(); }}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Student</Form.Label>
                  <Form.Select
                    value={generateForm.student_id}
                    onChange={(e) => setGenerateForm({...generateForm, student_id: e.target.value})}
                    required
                  >
                    <option value="">Select Student</option>
                    {/* Populate with students */}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Term</Form.Label>
                  <Form.Select
                    value={generateForm.term_id}
                    onChange={(e) => setGenerateForm({...generateForm, term_id: e.target.value})}
                    required
                  >
                    <option value="">Select Term</option>
                    {/* Populate with terms */}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Due Date</Form.Label>
              <Form.Control
                type="date"
                value={generateForm.due_date}
                onChange={(e) => setGenerateForm({...generateForm, due_date: e.target.value})}
                required
              />
            </Form.Group>

            <h6>Invoice Items</h6>
            {generateForm.items.map((item, index) => (
              <Row key={index} className="mb-2">
                <Col md={7}>
                  <Form.Control
                    type="text"
                    placeholder="Description"
                    value={item.description}
                    onChange={(e) => {
                      const newItems = [...generateForm.items];
                      newItems[index].description = e.target.value;
                      setGenerateForm({...generateForm, items: newItems});
                    }}
                  />
                </Col>
                <Col md={4}>
                  <InputGroup>
                    <InputGroup.Text>KES</InputGroup.Text>
                    <Form.Control
                      type="number"
                      step="0.01"
                      placeholder="Amount"
                      value={item.amount}
                      onChange={(e) => {
                        const newItems = [...generateForm.items];
                        newItems[index].amount = parseFloat(e.target.value) || 0;
                        setGenerateForm({...generateForm, items: newItems});
                      }}
                    />
                  </InputGroup>
                </Col>
                <Col md={1}>
                  {index > 0 && (
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => {
                        const newItems = generateForm.items.filter((_, i) => i !== index);
                        setGenerateForm({...generateForm, items: newItems});
                      }}
                    >
                      ×
                    </Button>
                  )}
                </Col>
              </Row>
            ))}

            <Button
              variant="outline-primary"
              size="sm"
              onClick={() => setGenerateForm({
                ...generateForm,
                items: [...generateForm.items, { description: '', amount: 0 }]
              })}
            >
              Add Item
            </Button>

            <div className="mt-3 p-3 bg-light rounded">
              <strong>Total Amount: {formatCurrency(calculateTotal(generateForm.items))}</strong>
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowGenerateModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Generate Invoice
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Invoice Preview Modal */}
      <Modal show={showPreviewModal} onHide={() => setShowPreviewModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Invoice Details - {selectedInvoice?.invoice_number}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedInvoice && (
            <>
              <Row className="mb-4">
                <Col md={6}>
                  <h6>Student Information</h6>
                  <p className="mb-1"><strong>Name:</strong> {selectedInvoice.student_name}</p>
                  <p className="mb-1"><strong>Admission No:</strong> {selectedInvoice.admission_number}</p>
                  <p className="mb-0"><strong>Class:</strong> {selectedInvoice.class_level}</p>
                </Col>
                <Col md={6} className="text-end">
                  <h6>Invoice Details</h6>
                  <p className="mb-1"><strong>Invoice #:</strong> {selectedInvoice.invoice_number}</p>
                  <p className="mb-1"><strong>Issue Date:</strong> {new Date(selectedInvoice.issue_date).toLocaleDateString()}</p>
                  <p className="mb-0"><strong>Due Date:</strong> {new Date(selectedInvoice.due_date).toLocaleDateString()}</p>
                </Col>
              </Row>

              <Table bordered>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th className="text-end">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedInvoice.items?.map((item, index) => (
                    <tr key={index}>
                      <td>{item.description}</td>
                      <td className="text-end">{formatCurrency(item.amount)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <th>Total</th>
                    <th className="text-end">{formatCurrency(selectedInvoice.total_amount)}</th>
                  </tr>
                </tfoot>
              </Table>

              <div className="mt-3">
                <Badge bg={getStatusVariant(selectedInvoice.status, selectedInvoice.due_date)}>
                  Status: {getStatusText(selectedInvoice.status, selectedInvoice.due_date)}
                </Badge>
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPreviewModal(false)}>
            Close
          </Button>
          <Button variant="primary" onClick={() => window.print()}>
            Print Invoice
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default InvoiceManagement;