import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { financeAPI } from '../../services/financeAPI.js';
import { 
  ArrowLeft, Cash, CreditCard, GraphUp, 
  Clock, CheckCircle, ExclamationTriangle, People,
  FileText, Calculator, ArrowUp, ArrowDown,
  Download, Filter, Calendar, BarChart,
  Receipt, Wallet, Bank, ArrowClockwise,
  Eye, Search, Plus, ShieldCheck
} from 'react-bootstrap-icons';

// Custom hook for dashboard data
const useDashboardData = (timeRange) => {
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await financeAPI.get('/finance/dashboard/', {
        params: { period: timeRange },
        timeout: 10000
      });
      setDashboardData(response.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.error || err.response?.data?.message || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return { dashboardData, loading, error, refetch: fetchDashboardData };
};

// Custom hook for quick stats calculation - FIXED to match actual API structure
const useQuickStats = (dashboardData) => {
  return useMemo(() => {
    const stats = {
      collectionRate: dashboardData.metrics?.collection_rate || 0,
      pendingApprovals: dashboardData.metrics?.pending_approvals || 0,
      overduePayments: dashboardData.metrics?.overdue_debts || 0,
      totalDebtors: dashboardData.metrics?.total_debtors || 0,
      reconciliationTasks: 0,
      totalStudents: 0,
      activeAccounts: 0
    };
    return stats;
  }, [dashboardData]);
};

// Loading component
const DashboardLoading = () => (
  <div className="container-fluid py-4">
    <div className="text-center py-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      <p className="mt-3 text-muted">Loading your dashboard...</p>
    </div>
  </div>
);

// Error component
const DashboardError = ({ error, onRetry }) => (
  <div className="container-fluid py-4">
    <div className="text-center py-5">
      <ExclamationTriangle size={48} className="text-danger mb-3" />
      <h4>Unable to Load Dashboard</h4>
      <p className="text-muted mb-4">{error}</p>
      <button className="btn btn-primary" onClick={onRetry}>
        <ArrowClockwise className="me-2" />
        Try Again
      </button>
    </div>
  </div>
);

// Financial Metrics Card Component
const FinancialMetricCard = ({ metric, formatCurrency, formatNumber, getTrendIcon }) => (
  <div className="col-xl-3 col-md-6 mb-3">
    <div className="card border-0 shadow-sm h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start">
          <div className="flex-grow-1">
            <h6 className="card-title text-muted mb-2">{metric.title}</h6>
            <h3 className="mb-1">
              {metric.format === 'currency' ? formatCurrency(metric.value) : formatNumber(metric.value)}
            </h3>
            <div className="d-flex align-items-center flex-wrap">
              {getTrendIcon(metric.change)}
              <small className={`ms-1 ${metric.change > 0 ? 'text-success' : metric.change < 0 ? 'text-danger' : 'text-muted'}`}>
                {metric.change > 0 ? '+' : ''}{metric.change}%
              </small>
              <small className="text-muted ms-2">vs previous period</small>
            </div>
          </div>
          <div className={`bg-${metric.color}-subtle rounded p-3 flex-shrink-0 ms-3`}>
            <metric.icon size={24} className={`text-${metric.color}`} />
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Quick Action Card Component
const QuickActionCard = ({ action }) => (
  <div className="col-6 col-md-4">
    <Link to={action.link} className="text-decoration-none">
      <div className="card h-100 border-0 shadow-sm-hover text-center transition-all quick-action-card">
        <div className="card-body p-3">
          <div className={`icon-wrapper bg-${action.color}-subtle mb-3`}>
            <action.icon size={20} className={`text-${action.color}`} />
          </div>
          <h6 className="card-title mb-1 fw-semibold text-dark">{action.title}</h6>
          <small className="text-muted">{action.description}</small>
        </div>
      </div>
    </Link>
  </div>
);

// Transaction Item Component
const TransactionItem = ({ transaction, formatCurrency, getStatusVariant }) => (
  <div className="list-group-item px-3 py-3">
    <div className="d-flex justify-content-between align-items-start">
      <div className="d-flex align-items-center flex-grow-1">
        <div className={`bg-${transaction.type === 'receipt' ? 'success' : 'danger'}-subtle rounded p-2 me-3 flex-shrink-0`}>
          {transaction.type === 'receipt' ? (
            <Receipt size={20} className="text-success" />
          ) : (
            <CreditCard size={20} className="text-danger" />
          )}
        </div>
        <div className="flex-grow-1">
          <h6 className="mb-1 fw-semibold">{transaction.description}</h6>
          <p className="text-muted mb-1 small">
            {transaction.reference} • {new Date(transaction.date).toLocaleDateString()}
          </p>
          <span className={`badge bg-${getStatusVariant(transaction.status)}`}>
            {transaction.status}
          </span>
        </div>
      </div>
      <div className="text-end flex-shrink-0 ms-3">
        <div className={`fw-bold ${transaction.type === 'receipt' ? 'text-success' : 'text-danger'}`}>
          {transaction.type === 'receipt' ? '+' : '-'}{formatCurrency(transaction.amount)}
        </div>
        <small className="text-muted">{transaction.method}</small>
      </div>
    </div>
  </div>
);

function AccountantDashboard() {
  const { currentUser } = useAuth();
  const [timeRange, setTimeRange] = useState('today');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  
  const { dashboardData, loading, error, refetch } = useDashboardData(timeRange);
  const quickStats = useQuickStats(dashboardData);

  // Quick Actions Configuration
  const quickActions = useMemo(() => [
    {
      title: 'Record Receipt',
      icon: Receipt,
      link: '/finance/receipts/create',
      color: 'success',
      description: 'Record student payments'
    },
    {
      title: 'Process Payment',
      icon: CreditCard,
      link: '/finance/payments/create',
      color: 'primary',
      description: 'Make school payments'
    },
    {
      title: 'Approve Payments',
      icon: ShieldCheck,
      link: '/finance/accountant/approvals',
      color: 'warning',
      description: 'Review pending approvals'
    },
    {
      title: 'Reconcile Accounts',
      icon: Calculator,
      link: '/finance/accountant/reconciliation',
      color: 'info',
      description: 'Bank reconciliation'
    },
    {
      title: 'Generate Reports',
      icon: BarChart,
      link: '/finance/reports',
      color: 'secondary',
      description: 'Financial reports'
    },
    {
      title: 'Manage Fees',
      icon: Wallet,
      link: '/finance/fee-structure',
      color: 'danger',
      description: 'Fee structure management'
    }
  ], []);

  // Financial Metrics Calculation - FIXED to match actual API structure
  const financialMetrics = useMemo(() => [
    {
      title: 'Today\'s Revenue',
      value: dashboardData.today?.receipts_total || 0,
      change: 0,
      icon: Cash,
      color: 'success',
      format: 'currency'
    },
    {
      title: 'Today\'s Expenses',
      value: dashboardData.today?.payments_total || 0,
      change: 0,
      icon: CreditCard,
      color: 'danger',
      format: 'currency'
    },
    {
      title: 'Net Cash Flow',
      value: (dashboardData.today?.receipts_total || 0) - (dashboardData.today?.payments_total || 0),
      change: 0,
      icon: GraphUp,
      color: 'primary',
      format: 'currency'
    },
    {
      title: 'Outstanding Fees',
      value: dashboardData.metrics?.total_outstanding_fees || 0,
      change: 0,
      icon: ExclamationTriangle,
      color: 'warning',
      format: 'currency'
    }
  ], [dashboardData]);

  // Filtered transactions - FIXED to handle actual API structure
  const filteredTransactions = useMemo(() => {
    const transactions = dashboardData.recent_activity?.receipts || [];
    
    return transactions.filter(transaction => {
      const matchesSearch = transaction.payer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          transaction.receipt_number?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = filterStatus === 'all' || transaction.status === filterStatus;
      return matchesSearch && matchesStatus;
    }).slice(0, 10);
  }, [dashboardData.recent_activity, searchTerm, filterStatus]);

  // Mock data for pending tasks (you can replace with actual data when available)
  const pendingTasks = useMemo(() => [
    {
      title: 'Review Overdue Payments',
      description: `${quickStats.overduePayments} students have overdue payments`,
      priority: 'high',
      dueDate: new Date(),
      link: '/finance/debts/overdue'
    },
    {
      title: 'Monthly Expense Report',
      description: 'Generate monthly expense summary',
      priority: 'medium',
      dueDate: new Date(Date.now() + 86400000),
      link: '/finance/reports/expenses'
    }
  ], [quickStats.overduePayments]);

  // Mock data for pending approvals
  const pendingApprovals = useMemo(() => [
    {
      paymentNumber: 'PAY-2024-001',
      payeeName: 'John Supplies Ltd',
      amount: 150000,
      requestedBy: 'James Kariuki',
      priority: 'high'
    },
    {
      paymentNumber: 'PAY-2024-002',
      payeeName: 'Water Services Board',
      amount: 75000,
      requestedBy: 'Mary Wanjiku',
      priority: 'medium'
    }
  ], []);

  // Utility functions
  const getTrendIcon = (change) => {
    if (change > 0) return <ArrowUp className="text-success" size={16} />;
    if (change < 0) return <ArrowDown className="text-danger" size={16} />;
    return <span className="text-muted">-</span>;
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

  const getStatusVariant = (status) => {
    const variants = {
      'completed': 'success',
      'pending': 'warning',
      'overdue': 'danger',
      'reconciled': 'info',
      'approved': 'success',
      'rejected': 'danger'
    };
    return variants[status] || 'secondary';
  };

  // Handle loading and error states
  if (loading) return <DashboardLoading />;
  if (error) return <DashboardError error={error} onRetry={refetch} />;

  return (
    <div className="container-fluid py-4">
      {/* Header Section */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 mb-2">Finance Dashboard</h1>
          <p className="lead text-muted mb-0">
            Welcome back, {currentUser?.firstName || 'Accountant'}! Here's your financial overview.
          </p>
          <small className="text-muted">
            Last updated: {new Date().toLocaleTimeString()}
          </small>
        </div>
        <div className="d-flex gap-2 align-items-center">
          <div className="input-group input-group-sm" style={{width: '200px'}}>
            <span className="input-group-text bg-transparent">
              <Search size={14} />
            </span>
            <input
              type="text"
              className="form-control form-control-sm"
              placeholder="Search transactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select 
            className="form-select form-select-sm w-auto"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <button 
            className="btn btn-outline-primary btn-sm"
            onClick={refetch}
            disabled={loading}
            title="Refresh data"
          >
            <ArrowClockwise size={16} className={loading ? 'spinning' : ''} />
          </button>
          <Link to="/finance" className="btn btn-outline-secondary btn-sm">
            <ArrowLeft className="me-1" />
            Back to Finance
          </Link>
        </div>
      </div>

      {/* Financial Metrics */}
      <div className="row mb-4">
        {financialMetrics.map((metric, index) => (
          <FinancialMetricCard
            key={index}
            metric={metric}
            formatCurrency={formatCurrency}
            formatNumber={formatNumber}
            getTrendIcon={getTrendIcon}
          />
        ))}
      </div>

      <div className="row">
        {/* Left Column - Main Content */}
        <div className="col-lg-8">
          {/* Quick Actions */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold">Quick Actions</h5>
            </div>
            <div className="card-body">
              <div className="row g-3">
                {quickActions.map((action, index) => (
                  <QuickActionCard key={index} action={action} />
                ))}
              </div>
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
              <h5 className="mb-0 fw-semibold">Recent Transactions</h5>
              <div className="d-flex gap-2 align-items-center">
                <select 
                  className="form-select form-select-sm"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="pending">Pending</option>
                  <option value="overdue">Overdue</option>
                </select>
                <Link to="/finance/receipts" className="btn btn-sm btn-outline-primary">
                  <Eye className="me-1" />
                  View All
                </Link>
              </div>
            </div>
            <div className="card-body p-0">
              {filteredTransactions.length > 0 ? (
                <div className="list-group list-group-flush">
                  {filteredTransactions.map((transaction, index) => (
                    <TransactionItem
                      key={index}
                      transaction={{
                        ...transaction,
                        type: 'receipt',
                        description: `Payment from ${transaction.payer_name}`,
                        reference: transaction.receipt_number,
                        method: transaction.paid_through,
                        status: transaction.status,
                        date: transaction.date || transaction.created_at
                      }}
                      formatCurrency={formatCurrency}
                      getStatusVariant={getStatusVariant}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <FileText size={48} className="text-muted mb-3" />
                  <h5>No Transactions Found</h5>
                  <p className="text-muted">
                    {searchTerm || filterStatus !== 'all' 
                      ? 'Try adjusting your search or filter criteria'
                      : 'Transactions will appear here as they occur.'
                    }
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Financial Overview Cards */}
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold">Financial Overview</h5>
            </div>
            <div className="card-body">
              <div className="row text-center">
                <div className="col-md-4 mb-3">
                  <div className="p-3 border rounded h-100">
                    <h6 className="text-muted mb-2">Revenue Trend</h6>
                    <BarChart size={48} className="text-success mb-2" />
                    <p className="mb-1 fw-bold">{quickStats.collectionRate}% Collection Rate</p>
                    <small className="text-muted">Fee collection efficiency</small>
                  </div>
                </div>
                <div className="col-md-4 mb-3">
                  <div className="p-3 border rounded h-100">
                    <h6 className="text-muted mb-2">Expense Analysis</h6>
                    <Calculator size={48} className="text-warning mb-2" />
                    <p className="mb-1 fw-bold">
                      {dashboardData.today?.payments_count || 0} Payments Today
                    </p>
                    <small className="text-muted">This period</small>
                  </div>
                </div>
                <div className="col-md-4 mb-3">
                  <div className="p-3 border rounded h-100">
                    <h6 className="text-muted mb-2">Debt Status</h6>
                    <ExclamationTriangle size={48} className="text-danger mb-2" />
                    <p className="mb-1 fw-bold">
                      {quickStats.overduePayments} Overdue
                    </p>
                    <small className="text-muted">Accounts requiring attention</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Sidebar */}
        <div className="col-lg-4">
          {/* Pending Tasks */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold">
                <Clock className="me-2" />
                Pending Tasks ({pendingTasks.length})
              </h5>
            </div>
            <div className="card-body p-0">
              {pendingTasks.length > 0 ? (
                <div className="list-group list-group-flush">
                  {pendingTasks.map((task, index) => (
                    <div key={index} className="list-group-item px-3 py-3 border-0">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <h6 className="mb-0 fw-semibold">{task.title}</h6>
                        <span className={`badge bg-${getStatusVariant(task.priority)}`}>
                          {task.priority}
                        </span>
                      </div>
                      <p className="text-muted small mb-2">{task.description}</p>
                      <div className="d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          <Clock size={12} className="me-1" />
                          Due: {new Date(task.dueDate).toLocaleDateString()}
                        </small>
                        <Link to={task.link} className="btn btn-sm btn-outline-primary">
                          Handle
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <CheckCircle size={48} className="text-success mb-3" />
                  <h5>All Caught Up!</h5>
                  <p className="text-muted">No pending tasks at the moment.</p>
                </div>
              )}
            </div>
          </div>

          {/* Approval Queue */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
              <h5 className="mb-0 fw-semibold">Approval Queue</h5>
              <span className="badge bg-warning">{pendingApprovals.length}</span>
            </div>
            <div className="card-body">
              {pendingApprovals.length > 0 ? (
                <div className="list-group list-group-flush">
                  {pendingApprovals.map((approval, index) => (
                    <div key={index} className="list-group-item px-0 py-2 border-0">
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 className="mb-1 fw-semibold">{approval.paymentNumber}</h6>
                          <p className="text-muted small mb-1">
                            {approval.payeeName} • {formatCurrency(approval.amount)}
                          </p>
                          <small className="text-muted">
                            Requested by {approval.requestedBy}
                          </small>
                        </div>
                        <span className={`badge bg-${approval.priority === 'high' ? 'danger' : 'warning'}`}>
                          {approval.priority}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-3">
                  <CheckCircle size={32} className="text-success mb-2" />
                  <p className="text-muted small mb-0">No pending approvals</p>
                </div>
              )}
              {pendingApprovals.length > 0 && (
                <div className="text-center mt-3">
                  <Link to="/finance/accountant/approvals" className="btn btn-sm btn-warning">
                    Review All Approvals ({pendingApprovals.length})
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* System Alerts */}
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold">
                <ExclamationTriangle className="me-2" />
                System Alerts
              </h5>
            </div>
            <div className="card-body">
              <div className="alert alert-warning py-2 mb-2">
                <div className="d-flex align-items-center">
                  <ExclamationTriangle size={16} className="me-2 flex-shrink-0" />
                  <div className="flex-grow-1">
                    <small className="fw-semibold">High Overdue Payments</small>
                    <br />
                    <small>{quickStats.overduePayments} accounts are overdue</small>
                  </div>
                </div>
              </div>
              <div className="alert alert-info py-2">
                <div className="d-flex align-items-center">
                  <ExclamationTriangle size={16} className="me-2 flex-shrink-0" />
                  <div className="flex-grow-1">
                    <small className="fw-semibold">Monthly Report Due</small>
                    <br />
                    <small>Monthly financial report is due in 3 days</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Reports */}
          <div className="card shadow-sm border-0 mt-4">
            <div className="card-header bg-white border-0 py-3">
              <h6 className="mb-0 fw-semibold">Quick Reports</h6>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-primary btn-sm text-start d-flex align-items-center">
                  <Download className="me-2 flex-shrink-0" />
                  <span>Daily Collection Report</span>
                </button>
                <button className="btn btn-outline-success btn-sm text-start d-flex align-items-center">
                  <Download className="me-2 flex-shrink-0" />
                  <span>Expense Summary</span>
                </button>
                <button className="btn btn-outline-warning btn-sm text-start d-flex align-items-center">
                  <Download className="me-2 flex-shrink-0" />
                  <span>Debtors List</span>
                </button>
                <button className="btn btn-outline-info btn-sm text-start d-flex align-items-center">
                  <Download className="me-2 flex-shrink-0" />
                  <span>Bank Reconciliation</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom CSS */}
      <style jsx>{`
        .shadow-sm-hover:hover {
          box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
          transform: translateY(-2px);
        }
        .transition-all {
          transition: all 0.2s ease-in-out;
        }
        .quick-action-card .icon-wrapper {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto;
        }
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default AccountantDashboard;