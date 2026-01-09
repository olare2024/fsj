import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Button, Badge, 
  ListGroup, ProgressBar, Alert, Spinner
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

const AccountantWorkspace = () => {
  const { currentUser } = useAuth();
  const [workspaceData, setWorkspaceData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchWorkspaceData();
  }, []);

  const fetchWorkspaceData = async () => {
    try {
      const response = await financeAPI.get('/accountant/workspace/');
      setWorkspaceData(response.data);
    } catch (err) {
      setError('Failed to load workspace data');
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

  const getPriorityVariant = (priority) => {
    switch (priority) {
      case 'urgent': return 'danger';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'secondary';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading your workspace...</p>
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
              <h1 className="h3 mb-1">Accountant Workspace</h1>
              <p className="text-muted mb-0">
                Welcome back, {currentUser.first_name}! Here's your financial overview.
              </p>
            </div>
            <div>
              <Button 
                variant="outline-primary" 
                onClick={fetchWorkspaceData}
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

      {/* Quick Stats */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="border-0 bg-primary text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{workspaceData.pending_approvals || 0}</h4>
                  <p className="mb-0">Pending Approvals</p>
                </div>
                <Clock size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-warning text-dark">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{workspaceData.pending_reconciliations || 0}</h4>
                  <p className="mb-0">Pending Reconciliations</p>
                </div>
                <FileText size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-success text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{formatCurrency(workspaceData.today_collection || 0)}</h4>
                  <p className="mb-0">Today's Collection</p>
                </div>
                <DollarSign size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="border-0 bg-info text-white">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4>{workspaceData.overdue_tasks || 0}</h4>
                  <p className="mb-0">Overdue Tasks</p>
                </div>
                <AlertTriangle size={24} />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        {/* Left Column - Tasks & Approvals */}
        <Col lg={8}>
          {/* Pending Approvals */}
          <Card className="mb-4">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">
                <CheckCircle className="me-2" />
                Pending Approvals
              </h5>
              <Badge bg="warning">{workspaceData.pending_approvals || 0}</Badge>
            </Card.Header>
            <Card.Body className="p-0">
              {workspaceData.recent_approvals?.length > 0 ? (
                <ListGroup variant="flush">
                  {workspaceData.recent_approvals.map((approval, index) => (
                    <ListGroup.Item key={index} className="px-3 py-2">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1">{approval.payment_number}</h6>
                          <p className="mb-1 text-muted small">
                            {approval.payee_name} • {formatCurrency(approval.amount)}
                          </p>
                          <small className="text-muted">
                            Requested by {approval.requested_by} • {approval.days_ago} days ago
                          </small>
                        </div>
                        <div className="text-end">
                          <Badge bg={getPriorityVariant(approval.priority)} className="mb-2">
                            {approval.priority}
                          </Badge>
                          <div>
                            <Button 
                              as={Link}
                              to="/finance/accountant/approvals"
                              variant="outline-primary"
                              size="sm"
                            >
                              Review
                            </Button>
                          </div>
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              ) : (
                <div className="text-center py-4">
                  <CheckCircle size={48} className="text-success mb-3" />
                  <h5>All Caught Up!</h5>
                  <p className="text-muted">No pending approvals</p>
                </div>
              )}
            </Card.Body>
            <Card.Footer className="text-center">
              <Button as={Link} to="/finance/accountant/approvals" variant="primary">
                View All Approvals
              </Button>
            </Card.Footer>
          </Card>

          {/* Recent Tasks */}
          <Card className="mb-4">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">
                <Inbox className="me-2" />
                My Tasks
              </h5>
              <Badge bg="info">{workspaceData.my_tasks?.length || 0}</Badge>
            </Card.Header>
            <Card.Body className="p-0">
              {workspaceData.my_tasks?.length > 0 ? (
                <ListGroup variant="flush">
                  {workspaceData.my_tasks.map((task, index) => (
                    <ListGroup.Item key={index} className="px-3 py-2">
                      <div className="d-flex justify-content-between align-items-center">
                        <div className="flex-grow-1">
                          <div className="d-flex justify-content-between align-items-start mb-1">
                            <h6 className="mb-0">{task.title}</h6>
                            <Badge bg={getPriorityVariant(task.priority)}>
                              {task.priority}
                            </Badge>
                          </div>
                          <p className="mb-1 text-muted small">{task.description}</p>
                          <div className="d-flex justify-content-between align-items-center">
                            <small className="text-muted">
                              Due: {new Date(task.due_date).toLocaleDateString()}
                            </small>
                            <small className={
                              task.days_remaining < 0 ? 'text-danger' : 
                              task.days_remaining < 3 ? 'text-warning' : 'text-muted'
                            }>
                              {task.days_remaining < 0 ? 
                                `${Math.abs(task.days_remaining)} days overdue` :
                                `${task.days_remaining} days left`
                              }
                            </small>
                          </div>
                          {task.progress !== undefined && (
                            <ProgressBar 
                              variant={
                                task.progress === 100 ? 'success' :
                                task.progress > 50 ? 'info' : 'warning'
                              }
                              now={task.progress}
                              className="mt-2"
                            />
                          )}
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted">No tasks assigned</p>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Quick Actions */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6} className="mb-3">
                  <Button 
                    as={Link}
                    to="/finance/receipts/create"
                    variant="outline-primary"
                    className="w-100 h-100 py-3"
                  >
                    <DollarSign size={24} className="mb-2" />
                    <br />
                    Record Receipt
                  </Button>
                </Col>
                <Col md={6} className="mb-3">
                  <Button 
                    as={Link}
                    to="/finance/payments/create"
                    variant="outline-success"
                    className="w-100 h-100 py-3"
                  >
                    <FileText size={24} className="mb-2" />
                    <br />
                    Create Payment
                  </Button>
                </Col>
                <Col md={6} className="mb-3">
                  <Button 
                    as={Link}
                    to="/finance/accountant/reconciliation"
                    variant="outline-warning"
                    className="w-100 h-100 py-3"
                  >
                    <RefreshCw size={24} className="mb-2" />
                    <br />
                    Reconcile Accounts
                  </Button>
                </Col>
                <Col md={6} className="mb-3">
                  <Button 
                    as={Link}
                    to="/finance/reports"
                    variant="outline-info"
                    className="w-100 h-100 py-3"
                  >
                    <BarChart size={24} className="mb-2" />
                    <br />
                    Generate Reports
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        {/* Right Column - Metrics & Updates */}
        <Col lg={4}>
          {/* Financial Metrics */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">
                <TrendingUp className="me-2" />
                This Month's Performance
              </h6>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="small">Fee Collection</span>
                  <span className="small">{workspaceData.monthly_metrics?.collection_rate || 0}%</span>
                </div>
                <ProgressBar 
                  variant={
                    workspaceData.monthly_metrics?.collection_rate >= 90 ? 'success' :
                    workspaceData.monthly_metrics?.collection_rate >= 75 ? 'warning' : 'danger'
                  }
                  now={workspaceData.monthly_metrics?.collection_rate || 0}
                />
              </div>

              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="small">Expense Management</span>
                  <span className="small">{workspaceData.monthly_metrics?.expense_ratio || 0}%</span>
                </div>
                <ProgressBar 
                  variant={
                    workspaceData.monthly_metrics?.expense_ratio <= 70 ? 'success' :
                    workspaceData.monthly_metrics?.expense_ratio <= 85 ? 'warning' : 'danger'
                  }
                  now={workspaceData.monthly_metrics?.expense_ratio || 0}
                />
              </div>

              <div className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="small">Approval Efficiency</span>
                  <span className="small">{workspaceData.monthly_metrics?.approval_efficiency || 0}%</span>
                </div>
                <ProgressBar 
                  variant={
                    workspaceData.monthly_metrics?.approval_efficiency >= 90 ? 'success' :
                    workspaceData.monthly_metrics?.approval_efficiency >= 75 ? 'warning' : 'danger'
                  }
                  now={workspaceData.monthly_metrics?.approval_efficiency || 0}
                />
              </div>
            </Card.Body>
          </Card>

          {/* Upcoming Deadlines */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">
                <Calendar className="me-2" />
                Upcoming Deadlines
              </h6>
            </Card.Header>
            <Card.Body className="p-0">
              {workspaceData.upcoming_deadlines?.length > 0 ? (
                <ListGroup variant="flush">
                  {workspaceData.upcoming_deadlines.map((deadline, index) => (
                    <ListGroup.Item key={index} className="px-3 py-2">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1 small">{deadline.title}</h6>
                          <small className="text-muted">
                            Due: {new Date(deadline.due_date).toLocaleDateString()}
                          </small>
                        </div>
                        <Badge bg={
                          deadline.days_remaining < 0 ? 'danger' : 
                          deadline.days_remaining < 3 ? 'warning' : 'info'
                        }>
                          {deadline.days_remaining < 0 ? 
                            'Overdue' : `${deadline.days_remaining}d`
                          }
                        </Badge>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              ) : (
                <div className="text-center py-3">
                  <p className="text-muted small">No upcoming deadlines</p>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Recent Activity */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">Recent Activity</h6>
            </Card.Header>
            <Card.Body className="p-0">
              {workspaceData.recent_activity?.length > 0 ? (
                <ListGroup variant="flush">
                  {workspaceData.recent_activity.map((activity, index) => (
                    <ListGroup.Item key={index} className="px-3 py-2">
                      <div className="d-flex">
                        <div className={`rounded-circle bg-${activity.variant} d-flex align-items-center justify-content-center me-3`} 
                             style={{width: '32px', height: '32px'}}>
                          {activity.icon === 'receipt' && <DollarSign size={16} className="text-white" />}
                          {activity.icon === 'payment' && <FileText size={16} className="text-white" />}
                          {activity.icon === 'approval' && <CheckCircle size={16} className="text-white" />}
                        </div>
                        <div className="flex-grow-1">
                          <p className="mb-1 small">{activity.description}</p>
                          <small className="text-muted">{activity.time_ago}</small>
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              ) : (
                <div className="text-center py-3">
                  <p className="text-muted small">No recent activity</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AccountantWorkspace;