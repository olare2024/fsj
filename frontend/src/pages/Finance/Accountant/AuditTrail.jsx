import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Form, Alert, Spinner, Modal, InputGroup
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { 
  ArrowLeft, Search, Filter, Download, Eye,
  FileText, Person, Calendar, Shield
} from 'react-bootstrap-icons';

const AuditTrail = () => {
  const { currentUser } = useAuth();
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [filters, setFilters] = useState({
    action: '',
    module: '',
    user: '',
    start_date: '',
    end_date: '',
    search: ''
  });

  useEffect(() => {
    fetchAuditLogs();
  }, [filters]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });

      const response = await financeAPI.get('/audit-trail/');
      setAuditLogs(response.data);
    } catch (err) {
      setError('Failed to load audit trail');
    } finally {
      setLoading(false);
    }
  };

  const exportAuditLogs = async () => {
    try {
      const response = await financeAPI.get('/audit-trail/export/', {
        responseType: 'blob',
        params: filters
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit-trail-${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to export audit trail');
    }
  };

  const getActionVariant = (action) => {
    switch (action) {
      case 'create': return 'success';
      case 'update': return 'warning';
      case 'delete': return 'danger';
      case 'approve': return 'info';
      case 'reject': return 'secondary';
      default: return 'primary';
    }
  };

  const getModuleVariant = (module) => {
    switch (module) {
      case 'receipt': return 'success';
      case 'payment': return 'danger';
      case 'debt': return 'warning';
      case 'fee_structure': return 'info';
      case 'approval': return 'primary';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading audit trail...</p>
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
                <h1 className="h3 mb-1">Financial Audit Trail</h1>
                <p className="text-muted mb-0">
                  Comprehensive record of all financial transactions and changes
                </p>
              </div>
            </div>
            <div>
              <Button variant="outline-primary" onClick={exportAuditLogs}>
                <Download className="me-2" />
                Export CSV
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

      {/* Filters */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <h6 className="mb-0">
                <Filter className="me-2" />
                Audit Filters
              </h6>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Action</Form.Label>
                    <Form.Select
                      value={filters.action}
                      onChange={(e) => setFilters({...filters, action: e.target.value})}
                    >
                      <option value="">All Actions</option>
                      <option value="create">Create</option>
                      <option value="update">Update</option>
                      <option value="delete">Delete</option>
                      <option value="approve">Approve</option>
                      <option value="reject">Reject</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Module</Form.Label>
                    <Form.Select
                      value={filters.module}
                      onChange={(e) => setFilters({...filters, module: e.target.value})}
                    >
                      <option value="">All Modules</option>
                      <option value="receipt">Receipt</option>
                      <option value="payment">Payment</option>
                      <option value="debt">Debt</option>
                      <option value="fee_structure">Fee Structure</option>
                      <option value="approval">Approval</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Start Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.start_date}
                      onChange={(e) => setFilters({...filters, start_date: e.target.value})}
                    />
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>End Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={filters.end_date}
                      onChange={(e) => setFilters({...filters, end_date: e.target.value})}
                    />
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group>
                    <Form.Label>Search</Form.Label>
                    <InputGroup>
                      <Form.Control
                        type="text"
                        placeholder="Search by description, user..."
                        value={filters.search}
                        onChange={(e) => setFilters({...filters, search: e.target.value})}
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

      {/* Summary Statistics */}
      <Row className="mb-4">
        <Col md={2}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h5>{auditLogs.length}</h5>
              <p className="text-muted mb-0">Total Logs</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h5 className="text-success">
                {auditLogs.filter(log => log.action === 'create').length}
              </h5>
              <p className="text-muted mb-0">Created</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h5 className="text-warning">
                {auditLogs.filter(log => log.action === 'update').length}
              </h5>
              <p className="text-muted mb-0">Updated</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h5 className="text-danger">
                {auditLogs.filter(log => log.action === 'delete').length}
              </h5>
              <p className="text-muted mb-0">Deleted</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h5 className="text-info">
                {auditLogs.filter(log => log.action === 'approve').length}
              </h5>
              <p className="text-muted mb-0">Approved</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={2}>
          <Card className="text-center border-0 bg-light">
            <Card.Body>
              <h5 className="text-primary">
                {new Set(auditLogs.map(log => log.user_id)).size}
              </h5>
              <p className="text-muted mb-0">Unique Users</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Audit Logs Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Audit Logs</h5>
              <span className="text-muted">
                {auditLogs.length} records found
              </span>
            </Card.Header>
            <Card.Body className="p-0">
              {auditLogs.length > 0 ? (
                <Table responsive hover>
                  <thead className="bg-light">
                    <tr>
                      <th>Timestamp</th>
                      <th>User</th>
                      <th>Action</th>
                      <th>Module</th>
                      <th>Record ID</th>
                      <th>Description</th>
                      <th>IP Address</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log) => (
                      <tr key={log.id}>
                        <td>
                          <div>
                            <div>{new Date(log.timestamp).toLocaleDateString()}</div>
                            <small className="text-muted">
                              {new Date(log.timestamp).toLocaleTimeString()}
                            </small>
                          </div>
                        </td>
                        <td>
                          <div className="d-flex align-items-center">
                            <Person className="me-2 text-muted" />
                            <div>
                              <div>{log.user_name}</div>
                              <small className="text-muted">{log.user_role}</small>
                            </div>
                          </div>
                        </td>
                        <td>
                          <Badge bg={getActionVariant(log.action)}>
                            {log.action.toUpperCase()}
                          </Badge>
                        </td>
                        <td>
                          <Badge bg={getModuleVariant(log.module)}>
                            {log.module.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td>
                          <code>{log.record_id}</code>
                        </td>
                        <td>
                          <div className="text-truncate" style={{maxWidth: '200px'}}>
                            {log.description}
                          </div>
                        </td>
                        <td>
                          <small className="text-muted">{log.ip_address}</small>
                        </td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => {
                              setSelectedLog(log);
                              setShowDetailModal(true);
                            }}
                          >
                            <Eye size={14} />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-5">
                  <Shield size={48} className="text-muted mb-3" />
                  <h5>No Audit Logs Found</h5>
                  <p className="text-muted">
                    No audit records match your current filters
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Log Detail Modal */}
      <Modal show={showDetailModal} onHide={() => setShowDetailModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Audit Log Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedLog && (
            <Row>
              <Col md={6}>
                <h6>Basic Information</h6>
                <Table size="sm" borderless>
                  <tbody>
                    <tr>
                      <td><strong>Timestamp:</strong></td>
                      <td>{new Date(selectedLog.timestamp).toLocaleString()}</td>
                    </tr>
                    <tr>
                      <td><strong>User:</strong></td>
                      <td>{selectedLog.user_name} ({selectedLog.user_role})</td>
                    </tr>
                    <tr>
                      <td><strong>Action:</strong></td>
                      <td>
                        <Badge bg={getActionVariant(selectedLog.action)}>
                          {selectedLog.action.toUpperCase()}
                        </Badge>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>Module:</strong></td>
                      <td>
                        <Badge bg={getModuleVariant(selectedLog.module)}>
                          {selectedLog.module.replace('_', ' ')}
                        </Badge>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>Record ID:</strong></td>
                      <td><code>{selectedLog.record_id}</code></td>
                    </tr>
                  </tbody>
                </Table>
              </Col>
              <Col md={6}>
                <h6>Technical Details</h6>
                <Table size="sm" borderless>
                  <tbody>
                    <tr>
                      <td><strong>IP Address:</strong></td>
                      <td>{selectedLog.ip_address}</td>
                    </tr>
                    <tr>
                      <td><strong>User Agent:</strong></td>
                      <td>
                        <small className="text-muted">
                          {selectedLog.user_agent}
                        </small>
                      </td>
                    </tr>
                  </tbody>
                </Table>
              </Col>
              <Col md={12} className="mt-3">
                <h6>Description</h6>
                <Card>
                  <Card.Body>
                    <p className="mb-0">{selectedLog.description}</p>
                  </Card.Body>
                </Card>
              </Col>
              {selectedLog.old_values && (
                <Col md={6} className="mt-3">
                  <h6>Old Values</h6>
                  <Card>
                    <Card.Body>
                      <pre className="mb-0 small">
                        {JSON.stringify(selectedLog.old_values, null, 2)}
                      </pre>
                    </Card.Body>
                  </Card>
                </Col>
              )}
              {selectedLog.new_values && (
                <Col md={6} className="mt-3">
                  <h6>New Values</h6>
                  <Card>
                    <Card.Body>
                      <pre className="mb-0 small">
                        {JSON.stringify(selectedLog.new_values, null, 2)}
                      </pre>
                    </Card.Body>
                  </Card>
                </Col>
              )}
            </Row>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default AuditTrail;