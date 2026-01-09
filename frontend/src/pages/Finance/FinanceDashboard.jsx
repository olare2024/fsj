import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { financeAPI } from '../../services/financeAPI.js';
import { 
  ReceiptIcon, 
  PaymentIcon, 
  DebtIcon, 
  RevenueIcon,
  TrendingUpIcon,
  TrendingDownIcon
} from '../../components/Icons';
import { ArrowClockwise, FileText, People, Calculator } from 'react-bootstrap-icons';

const FinanceDashboard = () => {
  const { currentUser } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');

      const response = await financeAPI.getDashboard();
      
      if (response.success) {
        console.log('📊 Dashboard API Response:', response.data);
        setDashboardData(response.data);
      } else {
        setError(response.error?.message || 'Failed to load dashboard data');
        console.error('API Error:', response.error);
      }
    } catch (err) {
      setError('An unexpected error occurred while fetching dashboard data');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();

    // Optional: Set up auto-refresh every 5 minutes
    const refreshInterval = setInterval(() => {
      fetchDashboardData(true);
    }, 5 * 60 * 1000);

    return () => {
      clearInterval(refreshInterval);
    };
  }, [fetchDashboardData]);

  const handleRefresh = () => {
    fetchDashboardData(true);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount || 0);
  };

  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-KE').format(number || 0);
  };

  // Safe data extraction with fallbacks based on actual API structure
  const summary = dashboardData?.summary || dashboardData?.metrics || {
    totalRevenue: dashboardData?.today?.receipts_total || 0,
    totalExpenses: dashboardData?.today?.payments_total || 0,
    netIncome: (dashboardData?.today?.receipts_total || 0) - (dashboardData?.today?.payments_total || 0),
    pendingReceipts: dashboardData?.metrics?.pending_receipts || 0,
    pendingApprovals: dashboardData?.metrics?.pending_approvals || 0,
    overdueDebts: dashboardData?.metrics?.overdue_debts || dashboardData?.metrics?.total_overdue || 0,
    collectionRate: dashboardData?.metrics?.collection_rate || 0,
    totalStudents: dashboardData?.metrics?.total_students || 0
  };

  const recentReceipts = dashboardData?.recent_activity?.receipts || 
                        dashboardData?.recent_receipts || 
                        dashboardData?.receipts || 
                        [];

  const pendingPayments = dashboardData?.pending_approvals || 
                         dashboardData?.pending_payments || 
                         [];

  const financialMetrics = dashboardData?.financial_metrics || {
    revenueGrowth: 0,
    expenseGrowth: 0,
    collectionEfficiency: summary.collectionRate || 0
  };

  if (loading && !refreshing) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3 text-muted">Loading your finance dashboard...</p>
        </div>
      </Container>
    );
  }

  if (error && !dashboardData) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          <Alert.Heading>Unable to Load Dashboard</Alert.Heading>
          {error}
          <div className="mt-3">
            <Button variant="primary" onClick={handleRefresh}>
              <ArrowClockwise className="me-2" />
              Try Again
            </Button>
          </div>
        </Alert>
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
              <h1 className="h3 mb-1">Finance Dashboard</h1>
              <p className="text-muted mb-0">
                Welcome back, {currentUser?.first_name || currentUser?.firstName || 'User'}
              </p>
              <small className="text-muted">
                Last updated: {new Date().toLocaleTimeString()}
                {refreshing && <span className="ms-2">🔄 Refreshing...</span>}
              </small>
            </div>
            <div className="d-flex gap-2">
              <Button 
                variant="outline-secondary" 
                onClick={handleRefresh}
                disabled={refreshing}
                title="Refresh data"
              >
                <ArrowClockwise className={`me-2 ${refreshing ? 'spinning' : ''}`} size={16} />
                Refresh
              </Button>
              <Button as={Link} to="/finance/receipts/create" variant="primary" className="me-2">
                <ReceiptIcon className="me-2" />
                New Receipt
              </Button>
              <Button as={Link} to="/finance/payments/create" variant="outline-primary">
                <PaymentIcon className="me-2" />
                New Payment
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="warning" dismissible onClose={() => setError('')}>
          <Alert.Heading>Partial Data Loaded</Alert.Heading>
          {error} - Showing available data.
        </Alert>
      )}

      {/* Summary Cards */}
      <Row className="mb-4">
        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Total Revenue</h6>
                  <h3 className="mb-0 text-success">{formatCurrency(summary.totalRevenue)}</h3>
                  <small className="text-success">
                    <TrendingUpIcon className="me-1" />
                    {financialMetrics.revenueGrowth > 0 ? '+' : ''}{financialMetrics.revenueGrowth || 0}% from last period
                  </small>
                </div>
                <div className="bg-success bg-opacity-10 p-3 rounded">
                  <RevenueIcon size={24} className="text-success" />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Total Expenses</h6>
                  <h3 className="mb-0 text-danger">{formatCurrency(summary.totalExpenses)}</h3>
                  <small className={financialMetrics.expenseGrowth > 0 ? 'text-danger' : 'text-success'}>
                    {financialMetrics.expenseGrowth > 0 ? <TrendingUpIcon /> : <TrendingDownIcon />}
                    {financialMetrics.expenseGrowth > 0 ? '+' : ''}{financialMetrics.expenseGrowth || 0}% from last period
                  </small>
                </div>
                <div className="bg-danger bg-opacity-10 p-3 rounded">
                  <PaymentIcon size={24} className="text-danger" />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Net Income</h6>
                  <h3 className={`mb-0 ${summary.netIncome >= 0 ? 'text-success' : 'text-danger'}`}>
                    {formatCurrency(summary.netIncome)}
                  </h3>
                  <small className="text-muted">Revenue minus expenses</small>
                </div>
                <div className={`bg-${summary.netIncome >= 0 ? 'success' : 'danger'} bg-opacity-10 p-3 rounded`}>
                  <RevenueIcon size={24} className={`text-${summary.netIncome >= 0 ? 'success' : 'danger'}`} />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Collection Rate</h6>
                  <h3 className="mb-0 text-info">{summary.collectionRate || 0}%</h3>
                  <small className="text-muted">
                    {summary.totalStudents || 0} total students
                  </small>
                </div>
                <div className="bg-info bg-opacity-10 p-3 rounded">
                  <People size={24} className="text-info" />
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Second Row of Metrics */}
      <Row className="mb-4">
        <Col xl={2} lg={4} md={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="bg-warning bg-opacity-10 p-3 rounded-circle d-inline-flex mb-3">
                <ReceiptIcon size={20} className="text-warning" />
              </div>
              <h4 className="text-warning">{summary.pendingReceipts}</h4>
              <p className="text-muted mb-0 small">Pending Receipts</p>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={2} lg={4} md={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="bg-primary bg-opacity-10 p-3 rounded-circle d-inline-flex mb-3">
                <PaymentIcon size={20} className="text-primary" />
              </div>
              <h4 className="text-primary">{summary.pendingApprovals}</h4>
              <p className="text-muted mb-0 small">Pending Approvals</p>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={2} lg={4} md={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="bg-danger bg-opacity-10 p-3 rounded-circle d-inline-flex mb-3">
                <DebtIcon size={20} className="text-danger" />
              </div>
              <h4 className="text-danger">{summary.overdueDebts}</h4>
              <p className="text-muted mb-0 small">Overdue Debts</p>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={2} lg={4} md={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="bg-success bg-opacity-10 p-3 rounded-circle d-inline-flex mb-3">
                <Calculator size={20} className="text-success" />
              </div>
              <h4 className="text-success">{recentReceipts.length}</h4>
              <p className="text-muted mb-0 small">Recent Transactions</p>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={2} lg={4} md={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="bg-info bg-opacity-10 p-3 rounded-circle d-inline-flex mb-3">
                <FileText size={20} className="text-info" />
              </div>
              <h4 className="text-info">{pendingPayments.length}</h4>
              <p className="text-muted mb-0 small">Awaiting Review</p>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={2} lg={4} md={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="bg-secondary bg-opacity-10 p-3 rounded-circle d-inline-flex mb-3">
                <TrendingUpIcon size={20} className="text-secondary" />
              </div>
              <h4 className="text-secondary">
                {dashboardData?.today?.receipts_count || 0}
              </h4>
              <p className="text-muted mb-0 small">Today's Transactions</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        {/* Recent Receipts */}
        <Col lg={6} className="mb-4">
          <Card className="border-0 shadow-sm h-100">
            <Card.Header className="bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Recent Transactions</h5>
                <div>
                  <Badge bg="light" text="dark" className="me-2">
                    {recentReceipts.length}
                  </Badge>
                  <Button as={Link} to="/finance/receipts" variant="outline-primary" size="sm">
                    View All
                  </Button>
                </div>
              </div>
            </Card.Header>
            <Card.Body className="p-0">
              {recentReceipts.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Receipt #</th>
                      <th>Student/Payer</th>
                      <th>Amount</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentReceipts.slice(0, 5).map((receipt) => (
                      <tr key={receipt.id}>
                        <td>
                          <Link 
                            to={`/finance/receipts/${receipt.id}`} 
                            className="text-decoration-none fw-semibold"
                          >
                            {receipt.receipt_number || receipt.reference_number || `RCP-${receipt.id}`}
                          </Link>
                        </td>
                        <td>{receipt.student_name || receipt.payer_name || receipt.paid_by || 'N/A'}</td>
                        <td className="fw-semibold text-success">{formatCurrency(receipt.amount)}</td>
                        <td>
                          <Badge 
                            bg={
                              receipt.status === 'completed' || receipt.status === 'Completed' ? 'success' :
                              receipt.status === 'pending' || receipt.status === 'Pending' ? 'warning' : 
                              receipt.status === 'verified' ? 'info' : 'secondary'
                            }
                          >
                            {receipt.status || 'Unknown'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-5">
                  <ReceiptIcon size={48} className="text-muted mb-3" />
                  <p className="text-muted mb-2">No recent transactions found</p>
                  <Button as={Link} to="/finance/receipts/create" variant="outline-primary" size="sm">
                    Create First Receipt
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Pending Approvals */}
        <Col lg={6} className="mb-4">
          <Card className="border-0 shadow-sm h-100">
            <Card.Header className="bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Pending Approvals</h5>
                <div>
                  <Badge bg="warning" className="me-2">
                    {pendingPayments.length}
                  </Badge>
                  <Button as={Link} to="/finance/payments/approval" variant="outline-primary" size="sm">
                    View All
                  </Button>
                </div>
              </div>
            </Card.Header>
            <Card.Body className="p-0">
              {pendingPayments.length > 0 ? (
                <Table responsive className="mb-0">
                  <thead className="bg-light">
                    <tr>
                      <th>Payment #</th>
                      <th>Payee</th>
                      <th>Amount</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pendingPayments.slice(0, 5).map((payment) => (
                      <tr key={payment.id}>
                        <td className="fw-semibold">
                          {payment.payment_number || payment.reference_number || `PAY-${payment.id}`}
                        </td>
                        <td>{payment.paid_to_name || payment.payee_name || payment.vendor || 'N/A'}</td>
                        <td className="fw-semibold text-danger">
                          {formatCurrency(payment.amount)}
                        </td>
                        <td>
                          <Button 
                            as={Link} 
                            to={`/finance/payments/${payment.id}`}
                            variant="outline-primary" 
                            size="sm"
                          >
                            Review
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-5">
                  <PaymentIcon size={48} className="text-muted mb-3" />
                  <p className="text-muted mb-0">No pending approvals</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={3} className="text-center mb-3">
                  <Button 
                    as={Link} 
                    to="/finance/receipts/bulk-upload" 
                    variant="outline-primary" 
                    className="w-100 h-100 py-3 d-flex flex-column align-items-center"
                  >
                    <ReceiptIcon size={32} className="mb-2" />
                    <div>Bulk Upload</div>
                    <small className="text-muted">Multiple receipts</small>
                  </Button>
                </Col>
                <Col md={3} className="text-center mb-3">
                  <Button 
                    as={Link} 
                    to="/finance/reports" 
                    variant="outline-primary" 
                    className="w-100 h-100 py-3 d-flex flex-column align-items-center"
                  >
                    <RevenueIcon size={32} className="mb-2" />
                    <div>Generate Reports</div>
                    <small className="text-muted">Financial reports</small>
                  </Button>
                </Col>
                <Col md={3} className="text-center mb-3">
                  <Button 
                    as={Link} 
                    to="/finance/debts" 
                    variant="outline-primary" 
                    className="w-100 h-100 py-3 d-flex flex-column align-items-center"
                  >
                    <DebtIcon size={32} className="mb-2" />
                    <div>Debt Management</div>
                    <small className="text-muted">View debt reports</small>
                  </Button>
                </Col>
                <Col md={3} className="text-center mb-3">
                  <Button 
                    as={Link} 
                    to="/finance/accountant/reconciliation" 
                    variant="outline-primary" 
                    className="w-100 h-100 py-3 d-flex flex-column align-items-center"
                  >
                    <PaymentIcon size={32} className="mb-2" />
                    <div>Reconciliation</div>
                    <small className="text-muted">Account reconciliation</small>
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* System Status */}
      {dashboardData && (
        <Row className="mt-4">
          <Col>
            <Card className="border-0 bg-light">
              <Card.Body className="py-2">
                <div className="d-flex justify-content-between align-items-center">
                  <small className="text-muted">
                    System Status: <Badge bg="success">Operational</Badge>
                  </small>
                  <small className="text-muted">
                    Data as of: {new Date().toLocaleString()}
                  </small>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Custom CSS for spinning animation */}
      <style jsx>{`
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Container>
  );
};

export default FinanceDashboard;