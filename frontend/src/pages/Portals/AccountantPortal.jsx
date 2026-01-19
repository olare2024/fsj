import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Table,
  Button,
  Badge,
  Alert,
  Spinner,
  ProgressBar,
  Nav,
  Image,
  ListGroup,
  Tabs,
  Tab,
  Form,
  InputGroup,
  Dropdown,
  DropdownButton,
  Accordion,
  Modal,
  OverlayTrigger,
  Tooltip,
  Toast,
  ToastContainer,
  Pagination,
  Placeholder
} from 'react-bootstrap';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  CashCoin,
  Receipt,
  FileEarmarkBarGraph,
  Bank,
  People,
  CalendarEvent,
  ArrowClockwise,
  Download,
  Bell,
  ExclamationTriangle,
  CheckCircle,
  FileText,
  GraphUp,
  CreditCard,
  Wallet2,
  Calculator,
  FileEarmarkExcel,
  FileEarmarkPdf,
  PieChart,
  BarChart,
  ArrowUpRight,
  CashStack,
  CloudArrowUp,
  CloudArrowDown,
  Eye,
  Plus,
  Search,
  Filter,
  SortDown,
  SortUp,
  Gear,
  ShieldCheck,
  Database,
  HddNetwork,
  Safe,
  Lock,
  Unlock,
  Wrench,
  Funnel,
  SortAlphaDown,
  SortAlphaUp,
  SortNumericDown,
  SortNumericUp,
  ClockHistory,
  FileEarmarkCheck,
  FileEarmarkSpreadsheet,
  FileEarmarkBinary,
  CurrencyExchange,
  Building,
  CreditCard2Front,
  FileArrowDown,
  FileArrowUp,
  Sliders,
  ArrowCounterclockwise,
  ArrowsFullscreen,
  ArrowLeftRight,
  ArrowBarDown,
  ArrowBarUp,
  BarChartSteps,
  BarChartLine,
  GraphUpArrow,
  GraphDownArrow,
  CurrencyDollar,
  Cash,
  BoxArrowDown,
  BoxArrowUp,
  BoxSeam,
  Printer,
  Share,
  Star,
  StarFill,
  Bookmark,
  Flag,
  QuestionCircle,
  InfoCircle,
  XCircle,
  Check2Circle,
  DashCircle,
  PlusCircle,
  ExclamationCircle,
  GearWideConnected,
  GearWide,
  PersonCircle,
  ThreeDotsVertical,
  PencilSquare,
  Trash,
  Copy,
  Clipboard,
  ClipboardCheck,
  Clock,
  Calendar,
  CalendarWeek,
  CalendarMonth,
  CalendarDate,
  Stopwatch,
  Hourglass,
  HourglassSplit,
  HourglassBottom,
  Alarm,
  BellFill,
  Envelope,
  EnvelopeFill,
  Chat,
  ChatFill,
  ChatLeft,
  ChatLeftFill,
  ChatRight,
  ChatRightFill,
  ChatSquare,
  ChatSquareFill,
  ChatDots,
  ChatDotsFill,
  Telephone,
  TelephoneFill,
  Phone,
  PhoneFill,
  PhoneVibrate,
  PhoneVibrateFill,
  GraphDown,
  Wallet,
  WalletFill,
  CreditCardFill,
  Safe2,
  SafeFill,
  PiggyBank,
  PiggyBankFill,
  Coin,
  CheckLg,
  XLg,
  DashLg,
  PlusLg,
  ArrowRight,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  ChevronRight,
  ChevronLeft,
  ChevronUp,
  ChevronDown,
  CaretRight,
  CaretLeft,
  CaretUp,
  CaretDown,
  List,
  ListNested,
  Grid,
  Grid3x3,
  Grid3x3Gap,
  Grid3x3GapFill,
  LayoutSidebar,
  LayoutSidebarReverse,
  LayoutSplit,
  LayoutTextSidebar,
  LayoutTextSidebarReverse,
  LayoutTextWindow,
  LayoutThreeColumns,
  LayoutWtf,
  Circle,
  CircleFill,
  Square,
  SquareFill,
  Pentagon,
  PentagonFill,
  Hexagon,
  HexagonFill,
  Octagon,
  OctagonFill,
  Lightning,
  LightningFill,
  Rocket,
  RocketFill,
  Speedometer,
  Speedometer2,
  Trophy,
  TrophyFill,
  Award,
  AwardFill,
  Gift,
  GiftFill,
  Heart,
  HeartFill,
  HeartHalf,
  Heartbreak,
  HeartbreakFill,
  House,
  HouseFill,
  DoorOpen,
  DoorOpenFill,
  DoorClosed,
  DoorClosedFill,
  Person,
  PersonFill,
  PersonPlus,
 BoxArrowRight,  // Make sure this is imported

  FileFill,
  FileEarmark,
 
} from 'react-bootstrap-icons';

// Import APIs
import { financeAPI, fetchDashboardData, financeHelpers } from '../../services/financeAPI';
import authAPI from '../../services/authAPI';
import adminAPI from '../../services/adminAPI';
import { academicsAPI } from '../../services/academicAPI';

// Import components
import LoadingOverlay from '../../components/LoadingOverlay';
import ErrorBoundary from '../../components/ErrorBoundary';

// Import utilities
import {
  formatCurrency,
  formatDate,
  formatDateTime,
  formatNumber,
  generateId,
  debounce,
  throttle
} from '../../utils/helpers';

// ==================== CONSTANTS ====================
const DATE_RANGES = [
  { value: 'today', label: 'Today', icon: <CalendarDate /> },
  { value: 'yesterday', label: 'Yesterday', icon: <Calendar /> },
  { value: 'week', label: 'This Week', icon: <CalendarWeek /> },
  { value: 'month', label: 'This Month', icon: <CalendarMonth /> },
  { value: 'quarter', label: 'This Quarter', icon: <Calendar /> },
  { value: 'year', label: 'This Year', icon: <Calendar /> },
  { value: 'custom', label: 'Custom Range', icon: <CalendarEvent /> }
];

const PAYMENT_METHODS = [
  { value: 'mpesa', label: 'M-Pesa', icon: <CurrencyExchange />, color: '#00A300' },
  { value: 'bank_transfer', label: 'Bank Transfer', icon: <Bank />, color: '#0056B3' },
  { value: 'cash', label: 'Cash', icon: <Cash />, color: '#28A745' },
  { value: 'cheque', label: 'Cheque', icon: <FileText />, color: '#6C757D' },
  { value: 'card', label: 'Card', icon: <CreditCard />, color: '#DC3545' }
];

const STATUS_CONFIG = {
  pending: { variant: 'warning', icon: <Clock />, label: 'Pending' },
  verified: { variant: 'info', icon: <Check2Circle />, label: 'Verified' },
  reconciled: { variant: 'success', icon: <CheckCircle />, label: 'Reconciled' },
  cancelled: { variant: 'danger', icon: <XCircle />, label: 'Cancelled' },
  overdue: { variant: 'danger', icon: <ExclamationTriangle />, label: 'Overdue' },
  paid: { variant: 'success', icon: <CheckCircle />, label: 'Paid' },
  approved: { variant: 'primary', icon: <ShieldCheck />, label: 'Approved' },
  active: { variant: 'success', icon: <CheckCircle />, label: 'Active' },
  inactive: { variant: 'secondary', icon: <DashCircle />, label: 'Inactive' },
  draft: { variant: 'secondary', icon: <FileEarmark />, label: 'Draft' },
  published: { variant: 'success', icon: <CheckCircle />, label: 'Published' }
};

// ==================== VIEW COMPONENTS ====================

// Reconciliation View Component
const ReconciliationView = ({ dashboardData, receipts }) => {
  const [reconciliationData, setReconciliationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchReconciliationData();
  }, [filter]);

  const fetchReconciliationData = async () => {
    setLoading(true);
    try {
      // Fetch bank reconciliation
      const bankResult = await financeAPI.bankReconciliation();
      // Fetch M-Pesa reconciliation
      const mpesaResult = await financeAPI.mpesaReconciliation();
      
      if (bankResult.success && mpesaResult.success) {
        setReconciliationData({
          bank: bankResult.data,
          mpesa: mpesaResult.data,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Failed to fetch reconciliation data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderReconciliationCard = (title, data, icon, type) => {
    if (!data) return null;
    
    return (
      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-0">
          <div className="d-flex justify-content-between align-items-center">
            <div className="d-flex align-items-center gap-2">
              {icon}
              <h5 className="mb-0">{title}</h5>
            </div>
            <Badge bg={data.status === 'pending' ? 'warning' : 'success'}>
              {data.status}
            </Badge>
          </div>
        </Card.Header>
        <Card.Body>
          <Row className="g-2">
            <Col md={6}>
              <div className="d-flex align-items-center gap-2 mb-2">
                <span className="text-muted">System Balance:</span>
                <strong className="text-primary">
                  {financeHelpers.formatCurrency(data.system_balance)}
                </strong>
              </div>
              <div className="d-flex align-items-center gap-2 mb-2">
                <span className="text-muted">Statement Balance:</span>
                <strong className="text-success">
                  {financeHelpers.formatCurrency(data.statement_balance)}
                </strong>
              </div>
            </Col>
            <Col md={6}>
              <div className="d-flex align-items-center gap-2 mb-2">
                <span className="text-muted">Variance:</span>
                <strong className={`${data.variance < 0 ? 'text-danger' : 'text-warning'}`}>
                  {financeHelpers.formatCurrency(Math.abs(data.variance))}
                  {data.variance < 0 ? ' Short' : ' Excess'}
                </strong>
              </div>
              <div className="d-flex align-items-center gap-2">
                <span className="text-muted">Matched Transactions:</span>
                <Badge bg="info">
                  {data.matched_transactions?.length || 0}
                </Badge>
              </div>
            </Col>
          </Row>
          
          {data.unmatched_transactions?.length > 0 && (
            <div className="mt-3">
              <small className="text-danger">
                <ExclamationTriangle size={12} className="me-1" />
                {data.unmatched_transactions.length} unmatched transactions
              </small>
            </div>
          )}
        </Card.Body>
        <Card.Footer className="bg-white border-0">
          <div className="d-flex justify-content-end gap-2">
            <Button variant="outline-primary" size="sm">
              <Eye size={12} className="me-1" />
              View Details
            </Button>
            <Button variant="warning" size="sm">
              <Calculator size={12} className="me-1" />
              Reconcile Now
            </Button>
          </div>
        </Card.Footer>
      </Card>
    );
  };

  return (
    <div className="reconciliation-view">
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4 className="mb-0">Financial Reconciliation</h4>
                  <small className="text-muted">
                    Last updated: {reconciliationData?.timestamp ? 
                      formatDateTime(reconciliationData.timestamp) : 'Never'}
                  </small>
                </div>
                <div className="d-flex gap-2">
                  <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" size="sm">
                      <Filter className="me-1" />
                      Filter: {filter === 'all' ? 'All' : filter}
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      <Dropdown.Item onClick={() => setFilter('all')}>All</Dropdown.Item>
                      <Dropdown.Item onClick={() => setFilter('pending')}>Pending</Dropdown.Item>
                      <Dropdown.Item onClick={() => setFilter('completed')}>Completed</Dropdown.Item>
                    </Dropdown.Menu>
                  </Dropdown>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={fetchReconciliationData}
                    disabled={loading}
                  >
                    <ArrowClockwise className={loading ? 'spinning' : ''} />
                  </Button>
                </div>
              </div>
            </Card.Header>
          </Card>
        </Col>
      </Row>

      {loading ? (
        <Row>
          <Col>
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2 text-muted">Loading reconciliation data...</p>
            </div>
          </Col>
        </Row>
      ) : reconciliationData ? (
        <Row className="g-3">
          <Col lg={6}>
            {renderReconciliationCard(
              'Bank Reconciliation',
              reconciliationData.bank,
              <Bank size={20} />,
              'bank'
            )}
          </Col>
          <Col lg={6}>
            {renderReconciliationCard(
              'M-Pesa Reconciliation',
              reconciliationData.mpesa,
              <CurrencyExchange size={20} />,
              'mpesa'
            )}
          </Col>
        </Row>
      ) : (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Body className="text-center py-5">
                <Calculator size={48} className="text-muted mb-3" />
                <h5>No Reconciliation Data</h5>
                <p className="text-muted mb-0">
                  Click refresh or run reconciliation to generate data
                </p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

// Analytics View Component
const AnalyticsView = ({ receipts, payments, debts }) => {
  const [timeRange, setTimeRange] = useState('month');
  const [chartType, setChartType] = useState('bar');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const [revenueTrends, expenseTrends, collectionEfficiency] = await Promise.all([
        financeAPI.getRevenueTrends({ period: timeRange }),
        financeAPI.getExpenseTrends({ period: timeRange }),
        financeAPI.getCollectionEfficiency({ period: timeRange })
      ]);

      if (revenueTrends.success && expenseTrends.success && collectionEfficiency.success) {
        setAnalyticsData({
          revenue: revenueTrends.data,
          expenses: expenseTrends.data,
          collection: collectionEfficiency.data,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderAnalyticsCard = (title, value, change, icon, color) => (
    <Card className="border-0 shadow-sm">
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h6 className="text-uppercase text-muted mb-2">{title}</h6>
            <h2 className={`mb-1 text-${color}`}>{value}</h2>
            {change && (
              <small className={`d-flex align-items-center gap-1 ${change >= 0 ? 'text-success' : 'text-danger'}`}>
                {change >= 0 ? <ArrowUpRight /> : <GraphDown />}
                {Math.abs(change)}% from last period
              </small>
            )}
          </div>
          <div className={`bg-${color} bg-opacity-10 p-3 rounded`}>
            {React.cloneElement(icon, { size: 24, className: `text-${color}` })}
          </div>
        </div>
      </Card.Body>
    </Card>
  );

  const renderChartPlaceholder = () => (
    <Card className="border-0 shadow-sm">
      <Card.Header className="bg-white border-0">
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Revenue vs Expenses</h5>
          <Dropdown>
            <Dropdown.Toggle variant="outline-secondary" size="sm">
              {chartType === 'bar' ? 'Bar Chart' : 'Line Chart'}
            </Dropdown.Toggle>
            <Dropdown.Menu>
              <Dropdown.Item onClick={() => setChartType('bar')}>
                <BarChart className="me-2" /> Bar Chart
              </Dropdown.Item>
              <Dropdown.Item onClick={() => setChartType('line')}>
                <GraphUp className="me-2" /> Line Chart
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
      </Card.Header>
      <Card.Body className="text-center py-5">
        {chartType === 'bar' ? <BarChart size={48} /> : <GraphUp size={48} />}
        <p className="mt-3 text-muted mb-0">
          Chart visualization would appear here with real data
        </p>
      </Card.Body>
    </Card>
  );

  return (
    <div className="analytics-view">
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4 className="mb-0">Financial Analytics</h4>
                  <small className="text-muted">
                    Insights and trends based on actual transaction data
                  </small>
                </div>
                <div className="d-flex gap-2">
                  <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" size="sm">
                      <CalendarEvent className="me-1" />
                      {DATE_RANGES.find(r => r.value === timeRange)?.label}
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      {DATE_RANGES.map(range => (
                        <Dropdown.Item 
                          key={range.value}
                          onClick={() => setTimeRange(range.value)}
                        >
                          <span className="me-2">{range.icon}</span>
                          {range.label}
                        </Dropdown.Item>
                      ))}
                    </Dropdown.Menu>
                  </Dropdown>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={fetchAnalyticsData}
                    disabled={loading}
                  >
                    <ArrowClockwise className={loading ? 'spinning' : ''} />
                  </Button>
                </div>
              </div>
            </Card.Header>
          </Card>
        </Col>
      </Row>

      {loading ? (
        <Row>
          <Col>
            <div className="text-center py-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2 text-muted">Loading analytics data...</p>
            </div>
          </Col>
        </Row>
      ) : analyticsData ? (
        <>
          <Row className="g-3 mb-4">
            <Col md={4}>
              {renderAnalyticsCard(
                'Total Revenue',
                financeHelpers.formatCurrency(analyticsData.revenue.total || 0),
                analyticsData.revenue.change || 0,
                <CashCoin />,
                'success'
              )}
            </Col>
            <Col md={4}>
              {renderAnalyticsCard(
                'Total Expenses',
                financeHelpers.formatCurrency(analyticsData.expenses.total || 0),
                analyticsData.expenses.change || 0,
                <CreditCard />,
                'danger'
              )}
            </Col>
            <Col md={4}>
              {renderAnalyticsCard(
                'Collection Rate',
                `${analyticsData.collection.rate || 0}%`,
                analyticsData.collection.change || 0,
                <Calculator />,
                'primary'
              )}
            </Col>
          </Row>

          <Row className="g-3">
            <Col lg={8}>
              {renderChartPlaceholder()}
            </Col>
            <Col lg={4}>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0">
                  <h5 className="mb-0">Key Metrics</h5>
                </Card.Header>
                <Card.Body>
                  <ListGroup variant="flush">
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                      <span className="text-muted">Avg. Transaction</span>
                      <strong>{financeHelpers.formatCurrency(analyticsData.revenue.average || 0)}</strong>
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                      <span className="text-muted">Payment Success Rate</span>
                      <strong>{analyticsData.collection.payment_success_rate || 0}%</strong>
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                      <span className="text-muted">Revenue Growth</span>
                      <Badge bg={analyticsData.revenue.growth >= 0 ? 'success' : 'danger'}>
                        {analyticsData.revenue.growth || 0}%
                      </Badge>
                    </ListGroup.Item>
                    <ListGroup.Item className="d-flex justify-content-between align-items-center">
                      <span className="text-muted">Expense Efficiency</span>
                      <Badge bg="info">
                        {analyticsData.expenses.efficiency || 0}%
                      </Badge>
                    </ListGroup.Item>
                  </ListGroup>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      ) : (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Body className="text-center py-5">
                <GraphUp size={48} className="text-muted mb-3" />
                <h5>No Analytics Data</h5>
                <p className="text-muted mb-3">
                  Click refresh to generate analytics from transaction data
                </p>
                <Button variant="primary" onClick={fetchAnalyticsData}>
                  <ArrowClockwise className="me-2" />
                  Generate Analytics
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

// System View Component
const SystemView = ({ systemStats, auditLogs, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('audit');

  const fetchSystemData = async () => {
    setLoading(true);
    try {
      // Fetch audit logs from admin API
      const result = await adminAPI.getAuditTrail({ limit: 20 });
      if (result.success) {
        // Update audit logs in parent component
        // This would be handled through props
      }
    } catch (error) {
      console.error('Failed to fetch system data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderSystemMetric = (title, value, icon, color) => (
    <Col md={4}>
      <Card className="border-0 shadow-sm">
        <Card.Body>
          <div className="d-flex align-items-center gap-3">
            <div className={`bg-${color} bg-opacity-10 p-2 rounded`}>
              {React.cloneElement(icon, { size: 20, className: `text-${color}` })}
            </div>
            <div>
              <h6 className="text-muted mb-0">{title}</h6>
              <h4 className="mb-0">{value}</h4>
            </div>
          </div>
        </Card.Body>
      </Card>
    </Col>
  );

  return (
    <div className="system-view">
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4 className="mb-0">System Status & Monitoring</h4>
                  <small className="text-muted">
                    Real-time system metrics and audit logs
                  </small>
                </div>
                <Button 
                  variant="outline-primary" 
                  size="sm"
                  onClick={onRefresh}
                  disabled={loading}
                >
                  <ArrowClockwise className={loading ? 'spinning' : ''} />
                </Button>
              </div>
            </Card.Header>
          </Card>
        </Col>
      </Row>

      <Row className="g-3 mb-4">
        {renderSystemMetric(
          'System Uptime',
          systemStats?.uptime || 'N/A',
          <Clock />,
          'success'
        )}
        {renderSystemMetric(
          'Response Time',
          systemStats?.response_time || 'N/A',
          <Speedometer />,
          'info'
        )}
        {renderSystemMetric(
          'Active Users',
          systemStats?.active_users || '0',
          <People />,
          'primary'
        )}
        {renderSystemMetric(
          'Storage Used',
          systemStats?.storage_used || '0%',
          <Database />,
          'warning'
        )}
        {renderSystemMetric(
          'Last Backup',
          systemStats?.last_backup || 'Never',
          <CloudArrowUp />,
          'secondary'
        )}
        {renderSystemMetric(
          'Pending Tasks',
          systemStats?.pending_tasks || '0',
          <ClipboardCheck />,
          'danger'
        )}
      </Row>

      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0">
              <Tabs
                activeKey={activeTab}
                onSelect={setActiveTab}
                className="border-0"
              >
                <Tab eventKey="audit" title="Audit Logs" />
                <Tab eventKey="errors" title="Error Logs" />
                <Tab eventKey="api" title="API Status" />
              </Tabs>
            </Card.Header>
            <Card.Body>
              {activeTab === 'audit' && (
                <div className="table-responsive">
                  <Table hover>
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>User</th>
                        <th>Action</th>
                        <th>Entity</th>
                        <th>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditLogs.length > 0 ? (
                        auditLogs.map(log => (
                          <tr key={log.id}>
                            <td>
                              <small>{formatDateTime(log.timestamp)}</small>
                            </td>
                            <td>
                              <div className="d-flex align-items-center gap-2">
                                <Person size={12} />
                                <span>{log.user_name}</span>
                              </div>
                            </td>
                            <td>
                              <Badge bg="info">{log.action}</Badge>
                            </td>
                            <td>
                              <small>{log.module}</small>
                            </td>
                            <td>
                              <small className="text-muted">{log.details}</small>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="5" className="text-center py-4">
                            <Clock size={32} className="text-muted mb-2" />
                            <p className="text-muted mb-0">No audit logs available</p>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </Table>
                </div>
              )}
              
              {activeTab === 'errors' && (
                <div className="text-center py-5">
                  <ExclamationTriangle size={48} className="text-muted mb-3" />
                  <h5>No Recent Errors</h5>
                  <p className="text-muted mb-0">
                    System is running smoothly with no errors reported
                  </p>
                </div>
              )}
              
              {activeTab === 'api' && (
                <div>
                  <Row className="g-3">
                    <Col md={6}>
                      <Card className="border border-success">
                        <Card.Body>
                          <div className="d-flex align-items-center justify-content-between">
                            <div>
                              <h6 className="text-success mb-0">Finance API</h6>
                              <small className="text-muted">/finance/*</small>
                            </div>
                            <Badge bg="success">Healthy</Badge>
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={6}>
                      <Card className="border border-success">
                        <Card.Body>
                          <div className="d-flex align-items-center justify-content-between">
                            <div>
                              <h6 className="text-success mb-0">Academic API</h6>
                              <small className="text-muted">/academics/*</small>
                            </div>
                            <Badge bg="success">Healthy</Badge>
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// ==================== SUB-COMPONENTS ====================

// Dashboard View Component
const DashboardView = ({ data, receipts, payments, debts, onRefresh, refreshing, onGenerateReport, onNavigate }) => {
  const renderStatCard = (title, value, icon, color, subtitle = '', trend = null) => (
    <Card className="border-0 shadow-sm h-100">
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h6 className="text-uppercase text-muted mb-2">{title}</h6>
            <h2 className="mb-1" style={{ color: `var(--bs-${color})` }}>{value}</h2>
            {subtitle && <small className="text-muted">{subtitle}</small>}
            {trend && (
              <small className={`d-flex align-items-center gap-1 ${trend.value >= 0 ? 'text-success' : 'text-danger'}`}>
                {trend.value >= 0 ? <ArrowUpRight /> : <GraphDown />}
                {Math.abs(trend.value)}% {trend.label}
              </small>
            )}
          </div>
          <div className={`bg-${color} bg-opacity-10 p-3 rounded`}>
            {React.cloneElement(icon, { size: 24, className: `text-${color}` })}
          </div>
        </div>
      </Card.Body>
    </Card>
  );

  return (
    <div className="dashboard-view">
      {/* Quick Stats */}
      <Row className="g-3 mb-4">
        <Col xl={3} lg={6}>
          {renderStatCard(
            'Total Revenue',
            formatCurrency(data?.total_income || 0),
            <ArrowUpRight />,
            'success',
            'This month'
          )}
        </Col>
        <Col xl={3} lg={6}>
          {renderStatCard(
            'Net Balance',
            formatCurrency(data?.net_balance || 0),
            <CashStack />,
            'primary',
            'Revenue - Expenses'
          )}
        </Col>
        <Col xl={3} lg={6}>
          {renderStatCard(
            'Pending Receipts',
            data?.pending_receipts || 0,
            <FileEarmarkCheck />,
            'warning',
            'Awaiting verification'
          )}
        </Col>
        <Col xl={3} lg={6}>
          {renderStatCard(
            'Overdue Debts',
            data?.overdue_debts || 0,
            <ExclamationTriangle />,
            'danger',
            'Requiring attention'
          )}
        </Col>
      </Row>

      {/* Charts and Recent Activity */}
      <Row className="g-3 mb-4">
        <Col lg={8}>
          <Card className="border-0 shadow-sm h-100">
            <Card.Header className="bg-white border-0">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Recent Transactions</h5>
                <Button variant="link" size="sm" onClick={onRefresh} disabled={refreshing}>
                  <ArrowClockwise className={refreshing ? 'spinning' : ''} />
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              {receipts.length > 0 ? (
                <div className="table-responsive">
                  <Table hover>
                    <thead>
                      <tr>
                        <th>Receipt #</th>
                        <th>Student</th>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {receipts.slice(0, 5).map(receipt => (
                        <tr key={receipt.id}>
                          <td className="fw-semibold">{receipt.receipt_number}</td>
                          <td>{receipt.student_name}</td>
                          <td>{formatDate(receipt.date)}</td>
                          <td className="text-success">{formatCurrency(receipt.amount)}</td>
                          <td>
                            <Badge bg={
                              receipt.status === 'pending' ? 'warning' :
                              receipt.status === 'verified' ? 'info' : 'success'
                            }>
                              {receipt.status}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-5">
                  <Receipt size={48} className="text-muted mb-3" />
                  <p className="text-muted">No recent transactions</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="border-0 shadow-sm h-100">
            <Card.Header className="bg-white border-0">
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button variant="outline-primary" className="text-start" onClick={() => onNavigate('receipts')}>
                  <Plus className="me-2" />
                  Create New Receipt
                </Button>
                <Button variant="outline-success" className="text-start" onClick={() => onGenerateReport('daily')}>
                  <FileEarmarkBarGraph className="me-2" />
                  Generate Daily Report
                </Button>
                <Button variant="outline-warning" className="text-start" onClick={() => onNavigate('reconciliation')}>
                  <Calculator className="me-2" />
                  Run Reconciliation
                </Button>
                <Button variant="outline-info" className="text-start" onClick={() => onNavigate('analytics')}>
                  <GraphUp className="me-2" />
                  View Analytics
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// Receipts View Component
const ReceiptsView = ({ 
  receipts, 
  totalReceipts, 
  pagination, 
  setPagination,
  filters, 
  setFilters,
  searchTerm,
  setSearchTerm,
  onVerify,
  onExport,
  onView,
  onEdit,
  onRefresh 
}) => {
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' });

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  return (
    <div className="receipts-view">
      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-0 py-3">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h4 className="mb-0">Receipts Management</h4>
              <small className="text-muted">{totalReceipts} receipts found</small>
            </div>
            <div className="d-flex gap-2">
              <Button variant="outline-primary" onClick={onRefresh}>
                <ArrowClockwise />
              </Button>
              <Button variant="primary" onClick={onExport}>
                <Download className="me-1" />
                Export
              </Button>
            </div>
          </div>
        </Card.Header>
        
        <Card.Body className="p-0">
          {/* Filters */}
          <div className="p-3 border-bottom">
            <Row className="g-2">
              <Col md={4}>
                <InputGroup>
                  <InputGroup.Text>
                    <Search />
                  </InputGroup.Text>
                  <Form.Control
                    type="text"
                    placeholder="Search receipts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </InputGroup>
              </Col>
              <Col md={8}>
                <div className="d-flex flex-wrap gap-2 justify-content-end">
                  <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" size="sm">
                      <Filter className="me-2" />
                      Status: {filters.status === 'all' ? 'All' : filters.status}
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      <Dropdown.Item onClick={() => setFilters(prev => ({ ...prev, status: 'all' }))}>
                        All Statuses
                      </Dropdown.Item>
                      <Dropdown.Divider />
                      {['pending', 'verified', 'reconciled', 'cancelled'].map(status => (
                        <Dropdown.Item 
                          key={status}
                          onClick={() => setFilters(prev => ({ ...prev, status }))}
                        >
                          {status.charAt(0).toUpperCase() + status.slice(1)}
                        </Dropdown.Item>
                      ))}
                    </Dropdown.Menu>
                  </Dropdown>

                  <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" size="sm">
                      <CalendarEvent className="me-2" />
                      {DATE_RANGES.find(r => r.value === filters.dateRange)?.label}
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      {DATE_RANGES.map(range => (
                        <Dropdown.Item 
                          key={range.value}
                          onClick={() => setFilters(prev => ({ ...prev, dateRange: range.value }))}
                        >
                          <span className="me-2">{range.icon}</span>
                          {range.label}
                        </Dropdown.Item>
                      ))}
                    </Dropdown.Menu>
                  </Dropdown>

                  <Button 
                    variant="outline-secondary" 
                    size="sm"
                    onClick={() => {
                      setFilters({
                        status: 'all',
                        dateRange: 'month',
                        paymentMethod: 'all',
                        category: 'all'
                      });
                      setSearchTerm('');
                    }}
                  >
                    <ArrowCounterclockwise />
                  </Button>
                </div>
              </Col>
            </Row>
          </div>

          {/* Receipts Table */}
          <div className="table-responsive">
            <Table hover className="mb-0">
              <thead className="table-light">
                <tr>
                  <th style={{ width: '120px' }}>
                    <Button 
                      variant="link" 
                      className="text-dark p-0"
                      onClick={() => handleSort('receipt_number')}
                    >
                      Receipt #
                      {sortConfig.key === 'receipt_number' && (
                        sortConfig.direction === 'asc' ? <SortUp /> : <SortDown />
                      )}
                    </Button>
                  </th>
                  <th>
                    <Button 
                      variant="link" 
                      className="text-dark p-0"
                      onClick={() => handleSort('student_name')}
                    >
                      Student
                      {sortConfig.key === 'student_name' && (
                        sortConfig.direction === 'asc' ? <SortAlphaUp /> : <SortAlphaDown />
                      )}
                    </Button>
                  </th>
                  <th>
                    <Button 
                      variant="link" 
                      className="text-dark p-0"
                      onClick={() => handleSort('date')}
                    >
                      Date
                      {sortConfig.key === 'date' && (
                        sortConfig.direction === 'asc' ? <SortUp /> : <SortDown />
                      )}
                    </Button>
                  </th>
                  <th>
                    <Button 
                      variant="link" 
                      className="text-dark p-0"
                      onClick={() => handleSort('amount')}
                    >
                      Amount
                      {sortConfig.key === 'amount' && (
                        sortConfig.direction === 'asc' ? <SortNumericUp /> : <SortNumericDown />
                      )}
                    </Button>
                  </th>
                  <th>Payment Method</th>
                  <th>Status</th>
                  <th style={{ width: '100px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {receipts.length > 0 ? (
                  receipts.map(receipt => (
                    <tr key={receipt.id}>
                      <td className="fw-semibold">{receipt.receipt_number}</td>
                      <td>
                        <div>{receipt.student_name}</div>
                        <small className="text-muted">{receipt.class_name}</small>
                      </td>
                      <td>
                        <small>{formatDate(receipt.date)}</small>
                      </td>
                      <td className="fw-bold text-success">
                        {formatCurrency(receipt.amount)}
                      </td>
                      <td>
                        <div className="d-flex align-items-center gap-2">
                          {receipt.payment_method === 'mpesa' && <CurrencyExchange />}
                          {receipt.payment_method === 'bank_transfer' && <Bank />}
                          {receipt.payment_method === 'cash' && <Cash />}
                          {receipt.payment_method === 'cheque' && <FileText />}
                          {receipt.payment_method === 'card' && <CreditCard />}
                          <span>{receipt.payment_method}</span>
                        </div>
                      </td>
                      <td>
                        <Badge bg={
                          receipt.status === 'pending' ? 'warning' :
                          receipt.status === 'verified' ? 'info' :
                          receipt.status === 'reconciled' ? 'success' : 'danger'
                        }>
                          {receipt.status}
                        </Badge>
                      </td>
                      <td>
                        <div className="d-flex gap-1">
                          <OverlayTrigger overlay={<Tooltip>View</Tooltip>}>
                            <Button variant="outline-primary" size="sm" onClick={() => onView(receipt.id)}>
                              <Eye size={12} />
                            </Button>
                          </OverlayTrigger>
                          {receipt.status === 'pending' && (
                            <OverlayTrigger overlay={<Tooltip>Verify</Tooltip>}>
                              <Button variant="success" size="sm" onClick={() => onVerify(receipt.id)}>
                                <CheckCircle size={12} />
                              </Button>
                            </OverlayTrigger>
                          )}
                          <OverlayTrigger overlay={<Tooltip>Edit</Tooltip>}>
                            <Button variant="outline-warning" size="sm" onClick={() => onEdit(receipt.id)}>
                              <PencilSquare size={12} />
                            </Button>
                          </OverlayTrigger>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="text-center py-5">
                      <Receipt size={48} className="text-muted mb-3" />
                      <p className="text-muted">No receipts found</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>

          {/* Pagination */}
          {totalReceipts > pagination.itemsPerPage && (
            <div className="p-3 border-top">
              <div className="d-flex justify-content-between align-items-center">
                <small className="text-muted">
                  Showing {((pagination.currentPage - 1) * pagination.itemsPerPage) + 1} to{' '}
                  {Math.min(pagination.currentPage * pagination.itemsPerPage, totalReceipts)} of {totalReceipts} receipts
                </small>
                <Pagination className="mb-0">
                  <Pagination.Prev 
                    onClick={() => setPagination(prev => ({ ...prev, currentPage: prev.currentPage - 1 }))}
                    disabled={pagination.currentPage === 1}
                  />
                  {[...Array(Math.ceil(totalReceipts / pagination.itemsPerPage))].map((_, i) => (
                    <Pagination.Item
                      key={i + 1}
                      active={i + 1 === pagination.currentPage}
                      onClick={() => setPagination(prev => ({ ...prev, currentPage: i + 1 }))}
                    >
                      {i + 1}
                    </Pagination.Item>
                  ))}
                  <Pagination.Next
                    onClick={() => setPagination(prev => ({ ...prev, currentPage: prev.currentPage + 1 }))}
                    disabled={pagination.currentPage === Math.ceil(totalReceipts / pagination.itemsPerPage)}
                  />
                </Pagination>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

// Payments View Component
const PaymentsView = ({ payments, onApprove, onExport }) => (
  <div className="payments-view">
    <Card className="border-0 shadow-sm">
      <Card.Header className="bg-white border-0 py-3">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h4 className="mb-0">Payments Management</h4>
            <small className="text-muted">{payments.length} payments</small>
          </div>
          <div className="d-flex gap-2">
            <Button variant="primary" onClick={onExport}>
              <Download className="me-1" />
              Export
            </Button>
          </div>
        </div>
      </Card.Header>
      
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Payment #</th>
                <th>Vendor</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Category</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {payments.length > 0 ? (
                payments.map(payment => (
                  <tr key={payment.id}>
                    <td className="fw-semibold">{payment.payment_number}</td>
                    <td>{payment.vendor_name}</td>
                    <td>
                      <small>{formatDate(payment.date)}</small>
                    </td>
                    <td className="fw-bold text-danger">
                      {formatCurrency(payment.amount)}
                    </td>
                    <td>
                      <Badge bg="info">{payment.category}</Badge>
                    </td>
                    <td>
                      <Badge bg={
                        payment.status === 'pending' ? 'warning' :
                        payment.status === 'approved' ? 'info' :
                        payment.status === 'paid' ? 'success' : 'danger'
                      }>
                        {payment.status}
                      </Badge>
                    </td>
                    <td>
                      <div className="d-flex gap-1">
                        {payment.status === 'pending' && (
                          <Button variant="success" size="sm" onClick={() => onApprove(payment.id)}>
                            <CheckCircle size={12} className="me-1" />
                            Approve
                          </Button>
                        )}
                        <Button variant="outline-primary" size="sm">
                          <Eye size={12} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="text-center py-5">
                    <CreditCard size={48} className="text-muted mb-3" />
                    <p className="text-muted">No payments found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </div>
      </Card.Body>
    </Card>
  </div>
);

// Debts View Component
const DebtsView = ({ debts, dashboardData, onExport }) => (
  <div className="debts-view">
    <Card className="border-0 shadow-sm">
      <Card.Header className="bg-white border-0 py-3">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h4 className="mb-0">Debts Management</h4>
            <small className="text-muted">
              {debts.length} students with outstanding balances • 
              {dashboardData?.overdue_debts && ` ${dashboardData.overdue_debts} overdue`}
            </small>
          </div>
          <div className="d-flex gap-2">
            <Button variant="primary" onClick={onExport}>
              <Download className="me-1" />
              Export
            </Button>
          </div>
        </div>
      </Card.Header>
      
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Student</th>
                <th>Parent</th>
                <th>Class</th>
                <th>Amount Due</th>
                <th>Amount Paid</th>
                <th>Balance</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {debts.length > 0 ? (
                debts.map(debt => (
                  <tr key={debt.id} className={debt.status === 'overdue' ? 'table-danger' : ''}>
                    <td className="fw-semibold">{debt.student_name}</td>
                    <td>{debt.parent_name}</td>
                    <td>
                      <Badge bg="secondary">{debt.class_name}</Badge>
                    </td>
                    <td className="fw-bold">{formatCurrency(debt.amount_due)}</td>
                    <td className="text-success">{formatCurrency(debt.amount_paid)}</td>
                    <td className={`fw-bold ${debt.balance > 0 ? 'text-danger' : 'text-success'}`}>
                      {formatCurrency(debt.balance)}
                    </td>
                    <td>
                      <div>
                        <small>{formatDate(debt.due_date)}</small>
                        {debt.status === 'overdue' && debt.days_overdue > 0 && (
                          <div className="text-danger">
                            <small>{debt.days_overdue} days overdue</small>
                          </div>
                        )}
                      </div>
                    </td>
                    <td>
                      <Badge bg={
                        debt.status === 'overdue' ? 'danger' :
                        debt.status === 'pending' ? 'warning' :
                        debt.status === 'partial' ? 'info' : 'success'
                      }>
                        {debt.status}
                      </Badge>
                    </td>
                    <td>
                      <div className="d-flex gap-1">
                        <Button variant="outline-primary" size="sm">
                          <Eye size={12} />
                        </Button>
                        <Button variant="outline-success" size="sm">
                          <CashCoin size={12} />
                        </Button>
                        <Button variant="outline-warning" size="sm">
                          <Bell size={12} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="9" className="text-center py-5">
                    <Wallet2 size={48} className="text-muted mb-3" />
                    <p className="text-muted">No outstanding debts found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </div>
      </Card.Body>
    </Card>
  </div>
);

// Fee Structures View Component
const FeeStructuresView = ({ feeStructures, onExport }) => (
  <div className="fee-structures-view">
    <Card className="border-0 shadow-sm">
      <Card.Header className="bg-white border-0 py-3">
        <div className="d-flex justify-content-between align-items-center">
          <div>
            <h4 className="mb-0">Fee Structures Management</h4>
            <small className="text-muted">{feeStructures.length} fee structures</small>
          </div>
          <div className="d-flex gap-2">
            <Button variant="primary" onClick={onExport}>
              <Download className="me-1" />
              Export
            </Button>
            <Button variant="success">
              <Plus className="me-1" />
              New Structure
            </Button>
          </div>
        </div>
      </Card.Header>
      
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table hover className="mb-0">
            <thead className="table-light">
              <tr>
                <th>Fee Structure</th>
                <th>Academic Year</th>
                <th>Curriculum</th>
                <th>Total Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {feeStructures.length > 0 ? (
                feeStructures.map(structure => (
                  <tr key={structure.id}>
                    <td className="fw-semibold">{structure.name}</td>
                    <td>{structure.academic_year}</td>
                    <td>
                      <Badge bg="info">{structure.curriculum_type}</Badge>
                    </td>
                    <td className="fw-bold">{formatCurrency(structure.total_amount)}</td>
                    <td>
                      <Badge bg={
                        structure.status === 'active' ? 'success' :
                        structure.status === 'draft' ? 'warning' : 'secondary'
                      }>
                        {structure.status}
                      </Badge>
                    </td>
                    <td>
                      <div className="d-flex gap-1">
                        <Button variant="outline-primary" size="sm">
                          <Eye size={12} />
                        </Button>
                        <Button variant="outline-warning" size="sm">
                          <PencilSquare size={12} />
                        </Button>
                        <Button variant="outline-danger" size="sm">
                          <Trash size={12} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="text-center py-5">
                    <CashCoin size={48} className="text-muted mb-3" />
                    <p className="text-muted">No fee structures found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </div>
      </Card.Body>
    </Card>
  </div>
);

// Reports View Component
const ReportsView = ({ reports, onGenerateReport }) => {
  const [reportType, setReportType] = useState('daily');
  
  return (
    <div className="reports-view">
      <Row className="g-3">
        <Col lg={8}>
          <Card className="border-0 shadow-sm h-100">
            <Card.Header className="bg-white border-0">
              <h5 className="mb-0">Available Reports</h5>
            </Card.Header>
            <Card.Body>
              <div className="table-responsive">
                <Table hover>
                  <thead>
                    <tr>
                      <th>Report Name</th>
                      <th>Period</th>
                      <th>Generated By</th>
                      <th>Date Generated</th>
                      <th>Size</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.length > 0 ? (
                      reports.map(report => (
                        <tr key={report.id}>
                          <td className="fw-semibold">
                            <div className="d-flex align-items-center gap-2">
                              {report.type === 'daily' && <FileEarmarkBarGraph />}
                              {report.type === 'fee_collection' && <CashCoin />}
                              {report.type === 'expenditure' && <CreditCard />}
                              {report.type === 'quarterly' && <FileEarmarkBarGraph />}
                              {report.name}
                            </div>
                          </td>
                          <td>{report.period}</td>
                          <td>{report.generated_by}</td>
                          <td>
                            <small>{formatDate(report.date_generated)}</small>
                          </td>
                          <td>
                            <Badge bg="secondary">{report.size}</Badge>
                          </td>
                          <td>
                            <div className="d-flex gap-1">
                              <Button variant="outline-primary" size="sm">
                                <Eye size={12} />
                              </Button>
                              <Button variant="outline-success" size="sm">
                                <Download size={12} />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="6" className="text-center py-5">
                          <FileEarmarkBarGraph size={48} className="text-muted mb-3" />
                          <p className="text-muted">No reports generated yet</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={4}>
          <Card className="border-0 shadow-sm h-100">
            <Card.Header className="bg-white border-0">
              <h5 className="mb-0">Generate New Report</h5>
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Report Type</Form.Label>
                  <Form.Select 
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                  >
                    <option value="daily">Daily Report</option>
                    <option value="fee_collection">Fee Collection Report</option>
                    <option value="expenditure">Expenditure Report</option>
                    <option value="quarterly">Quarterly Report</option>
                    <option value="annual">Annual Report</option>
                  </Form.Select>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Date Range</Form.Label>
                  <Form.Select>
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month" selected>This Month</option>
                    <option value="quarter">This Quarter</option>
                    <option value="year">This Year</option>
                    <option value="custom">Custom Range</option>
                  </Form.Select>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Format</Form.Label>
                  <div className="d-flex gap-2">
                    {['excel', 'pdf', 'csv'].map(format => (
                      <Form.Check
                        key={format}
                        type="radio"
                        name="format"
                        label={format.toUpperCase()}
                        defaultChecked={format === 'excel'}
                      />
                    ))}
                  </div>
                </Form.Group>
                
                <div className="d-grid">
                  <Button 
                    variant="primary" 
                    onClick={() => onGenerateReport(reportType)}
                  >
                    <FileEarmarkBarGraph className="me-2" />
                    Generate Report
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// ==================== CREATE RECEIPT FORM COMPONENT ====================
const CreateReceiptForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    student_id: '',
    amount: '',
    payment_method: 'mpesa',
    description: '',
    date: new Date().toISOString().split('T')[0]
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Row className="g-3">
        <Col md={6}>
          <Form.Group>
            <Form.Label>Student</Form.Label>
            <Form.Control
              type="text"
              placeholder="Select student..."
              required
              value={formData.student_id}
              onChange={(e) => setFormData(prev => ({ ...prev, student_id: e.target.value }))}
            />
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group>
            <Form.Label>Amount (KES)</Form.Label>
            <Form.Control
              type="number"
              placeholder="0.00"
              required
              min="0"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
            />
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group>
            <Form.Label>Payment Method</Form.Label>
            <Form.Select
              value={formData.payment_method}
              onChange={(e) => setFormData(prev => ({ ...prev, payment_method: e.target.value }))}
            >
              {PAYMENT_METHODS.map(method => (
                <option key={method.value} value={method.value}>
                  {method.label}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group>
            <Form.Label>Date</Form.Label>
            <Form.Control
              type="date"
              value={formData.date}
              onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
              required
            />
          </Form.Group>
        </Col>
        <Col md={12}>
          <Form.Group>
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Enter description..."
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            />
          </Form.Group>
        </Col>
      </Row>
      <div className="d-flex justify-content-end gap-2 mt-4">
        <Button variant="secondary" type="button">
          Cancel
        </Button>
        <Button variant="primary" type="submit">
          Create Receipt
        </Button>
      </div>
    </Form>
  );
};

// ==================== PORTAL SETTINGS COMPONENT ====================
const PortalSettings = ({ onClose }) => {
  const [settings, setSettings] = useState({
    autoRefresh: true,
    notifications: true,
    compactView: false,
    darkMode: false,
    showAnalytics: true
  });

  const handleSave = () => {
    localStorage.setItem('accountant_settings', JSON.stringify(settings));
    onClose();
  };

  return (
    <Form>
      <Form.Group className="mb-3">
        <Form.Check
          type="switch"
          label="Auto Refresh Data"
          checked={settings.autoRefresh}
          onChange={(e) => setSettings(prev => ({ ...prev, autoRefresh: e.target.checked }))}
        />
        <Form.Text className="text-muted">
          Automatically refresh data every 5 minutes.
        </Form.Text>
      </Form.Group>
      
      <Form.Group className="mb-3">
        <Form.Check
          type="switch"
          label="Enable Notifications"
          checked={settings.notifications}
          onChange={(e) => setSettings(prev => ({ ...prev, notifications: e.target.checked }))}
        />
      </Form.Group>
      
      <Form.Group className="mb-3">
        <Form.Check
          type="switch"
          label="Compact View"
          checked={settings.compactView}
          onChange={(e) => setSettings(prev => ({ ...prev, compactView: e.target.checked }))}
        />
      </Form.Group>
      
      <Form.Group className="mb-3">
        <Form.Check
          type="switch"
          label="Dark Mode"
          checked={settings.darkMode}
          onChange={(e) => setSettings(prev => ({ ...prev, darkMode: e.target.checked }))}
        />
      </Form.Group>
      
      <Form.Group className="mb-3">
        <Form.Check
          type="switch"
          label="Show Analytics Dashboard"
          checked={settings.showAnalytics}
          onChange={(e) => setSettings(prev => ({ ...prev, showAnalytics: e.target.checked }))}
        />
      </Form.Group>
      
      <div className="d-flex justify-content-end gap-2">
        <Button variant="secondary" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSave}>
          Save Settings
        </Button>
      </div>
    </Form>
  );
};

// ==================== MAIN COMPONENT ====================
const AccountantPortal = () => {
  const { currentUser, loading: authLoading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const abortControllerRef = useRef(new AbortController());
  
  // State
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [errors, setErrors] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [lastRefreshTime, setLastRefreshTime] = useState(Date.now());
  
  // UI State
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Filter and Search State
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'month',
    paymentMethod: 'all',
    category: 'all',
    sortBy: 'date',
    sortOrder: 'desc'
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    itemsPerPage: 10,
    totalItems: 0
  });
  
  // Data State
  const [dashboardData, setDashboardData] = useState(null);
  const [receipts, setReceipts] = useState([]);
  const [payments, setPayments] = useState([]);
  const [debts, setDebts] = useState([]);
  const [feeStructures, setFeeStructures] = useState([]);
  const [reports, setReports] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [systemStats, setSystemStats] = useState({});

  // Initialize
  useEffect(() => {
    initializePortal();
    return () => {
      abortControllerRef.current.abort();
    };
  }, []);

  // Handle tab changes from URL
  useEffect(() => {
    const tab = location.hash.replace('#', '') || 'dashboard';
    setActiveTab(tab);
  }, [location]);

  // Initialize portal
  const initializePortal = async () => {
    try {
      setLoading(true);
      
      // Load user profile
      await loadUserProfile();
      
      // Load initial data
      await loadInitialData();
      
    } catch (error) {
      addError('Failed to initialize portal', error);
    } finally {
      setLoading(false);
    }
  };

  // Load user profile
  const loadUserProfile = async () => {
    try {
      const result = await authAPI.getCurrentUser();
      if (result.success) {
        setUserProfile(result.user || result.data);
      } else {
        throw new Error(result.error?.message || 'Failed to load profile');
      }
    } catch (error) {
      addError('Failed to load user profile', error);
      // Create basic profile from auth context
      setUserProfile({
        id: currentUser?.id || 'acc-001',
        first_name: currentUser?.first_name || 'Accountant',
        last_name: currentUser?.last_name || 'User',
        email: currentUser?.email || 'accountant@delvok.ac.ke',
        role: 'accountant',
        department: 'Finance',
        avatar: null,
        last_login: new Date().toISOString()
      });
    }
  };

  // Load initial data
  const loadInitialData = async () => {
    try {
      // Load dashboard data
      const dashboardResult = await financeAPI.getDashboard();
      if (dashboardResult.success) {
        setDashboardData(dashboardResult.data);
      }

      // Load receipts
      const receiptsResult = await financeAPI.getReceipts({ limit: 50 });
      if (receiptsResult.success) {
        setReceipts(receiptsResult.data.results || receiptsResult.data);
      }

      // Load payments
      const paymentsResult = await financeAPI.getPayments({ limit: 30 });
      if (paymentsResult.success) {
        setPayments(paymentsResult.data.results || paymentsResult.data);
      }

      // Load debts
      const debtsResult = await financeAPI.getDebtRecords({ limit: 20 });
      if (debtsResult.success) {
        setDebts(debtsResult.data.results || debtsResult.data);
      }

      // Load fee structures
      const feeResult = await financeAPI.getCurrentFeeStructures();
      if (feeResult.success) {
        setFeeStructures(feeResult.data.results || feeResult.data);
      }

      // Load financial reports
      const reportsResult = await financeAPI.getFinancialReports();
      if (reportsResult.success) {
        setReports(reportsResult.data.results || reportsResult.data);
      }

      // Load audit logs
      const auditResult = await adminAPI.getAuditTrail({ limit: 20 });
      if (auditResult.success) {
        setAuditLogs(auditResult.data.results || auditResult.data);
      }

      // Load system statistics
      const statsResult = await adminAPI.getSystemStats();
      if (statsResult.success) {
        setSystemStats(statsResult.data);
      }

      setLastRefreshTime(Date.now());
      addNotification('Portal initialized successfully', 'success');
      
    } catch (error) {
      addError('Failed to load initial data', error);
    }
  };

  // Refresh data
  const refreshData = useCallback(async () => {
    if (refreshing) return;
    
    setRefreshing(true);
    try {
      await loadInitialData();
      setLastRefreshTime(Date.now());
      addNotification('Data refreshed successfully', 'success');
    } catch (error) {
      addError('Refresh failed', error);
    } finally {
      setRefreshing(false);
    }
  }, [refreshing]);

  // Error handling
  const addError = (message, error = null) => {
    console.error(message, error);
    const errorId = generateId();
    setErrors(prev => [...prev, {
      id: errorId,
      message,
      details: error?.message,
      timestamp: new Date().toISOString()
    }]);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      setErrors(prev => prev.filter(err => err.id !== errorId));
    }, 10000);
  };

  const addNotification = (message, type = 'info') => {
    const notificationId = generateId();
    setNotifications(prev => [...prev, {
      id: notificationId,
      message,
      type,
      timestamp: new Date().toISOString()
    }]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
    }, 5000);
  };


// Continue from where it was cut off...

// Filter and search functions
const filteredReceipts = useMemo(() => {
  let filtered = receipts;
  
  // Apply search filter
  if (searchTerm.trim()) {
    const term = searchTerm.toLowerCase();
    filtered = filtered.filter(receipt =>
      receipt.receipt_number?.toLowerCase().includes(term) ||
      receipt.student_name?.toLowerCase().includes(term) ||
      receipt.class_name?.toLowerCase().includes(term)
    );
  }
  
  // Apply status filter
  if (filters.status !== 'all') {
    filtered = filtered.filter(receipt => receipt.status === filters.status);
  }
  
  // Apply date range filter
  const now = new Date();
  let startDate = new Date();
  
  switch (filters.dateRange) {
    case 'today':
      startDate.setHours(0, 0, 0, 0);
      break;
    case 'yesterday':
      startDate.setDate(startDate.getDate() - 1);
      startDate.setHours(0, 0, 0, 0);
      const yesterdayEnd = new Date(startDate);
      yesterdayEnd.setHours(23, 59, 59, 999);
      filtered = filtered.filter(receipt => {
        const receiptDate = new Date(receipt.date);
        return receiptDate >= startDate && receiptDate <= yesterdayEnd;
      });
      return filtered;
    case 'week':
      startDate.setDate(startDate.getDate() - 7);
      break;
    case 'month':
      startDate.setMonth(startDate.getMonth() - 1);
      break;
    case 'quarter':
      startDate.setMonth(startDate.getMonth() - 3);
      break;
    case 'year':
      startDate.setFullYear(startDate.getFullYear() - 1);
      break;
    case 'custom':
      // Custom date range would be handled separately
      break;
  }
  
  if (filters.dateRange !== 'all' && filters.dateRange !== 'custom') {
    filtered = filtered.filter(receipt => {
      const receiptDate = new Date(receipt.date);
      return receiptDate >= startDate && receiptDate <= now;
    });
  }
  
  // Apply payment method filter
  if (filters.paymentMethod !== 'all') {
    filtered = filtered.filter(receipt => 
      receipt.payment_method === filters.paymentMethod
    );
  }
  
  // Apply sorting
  filtered.sort((a, b) => {
    let aValue = a[filters.sortBy];
    let bValue = b[filters.sortBy];
    
    if (filters.sortBy === 'date') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    }
    
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }
    
    if (aValue < bValue) return filters.sortOrder === 'asc' ? -1 : 1;
    if (aValue > bValue) return filters.sortOrder === 'asc' ? 1 : -1;
    return 0;
  });
  
  return filtered;
}, [receipts, searchTerm, filters]);

// Calculate paginated data
const paginatedReceipts = useMemo(() => {
  const startIndex = (pagination.currentPage - 1) * pagination.itemsPerPage;
  return filteredReceipts.slice(startIndex, startIndex + pagination.itemsPerPage);
}, [filteredReceipts, pagination.currentPage, pagination.itemsPerPage]);

// Update total items when filtered data changes
useEffect(() => {
  setPagination(prev => ({
    ...prev,
    totalItems: filteredReceipts.length,
    currentPage: prev.currentPage > Math.ceil(filteredReceipts.length / prev.itemsPerPage) 
      ? 1 
      : prev.currentPage
  }));
}, [filteredReceipts]);

// Export functions
const handleExport = useCallback(async (type, format = 'excel') => {
  try {
    setLoading(true);
    const result = await financeAPI.exportData(type, format, {
      filters,
      dateRange: filters.dateRange,
      searchTerm
    });
    
    if (result.success) {
      // Create download link
      const blob = new Blob([result.data], { 
        type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export-${type}-${format}-${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      addNotification(`${type} exported successfully as ${format.toUpperCase()}`, 'success');
    }
  } catch (error) {
    addError(`Failed to export ${type}`, error);
  } finally {
    setLoading(false);
  }
}, [filters, searchTerm]);

// Verify receipt
const handleVerifyReceipt = useCallback(async (receiptId) => {
  try {
    const result = await financeAPI.verifyReceipt(receiptId);
    if (result.success) {
      // Update local state
      setReceipts(prev => prev.map(receipt =>
        receipt.id === receiptId 
          ? { ...receipt, status: 'verified', verified_at: new Date().toISOString() }
          : receipt
      ));
      
      // Update dashboard stats
      if (dashboardData) {
        setDashboardData(prev => ({
          ...prev,
          pending_receipts: Math.max(0, (prev.pending_receipts || 0) - 1),
          verified_receipts: (prev.verified_receipts || 0) + 1
        }));
      }
      
      addNotification('Receipt verified successfully', 'success');
    }
  } catch (error) {
    addError('Failed to verify receipt', error);
  }
}, [dashboardData]);

// Create new receipt
const handleCreateReceipt = useCallback(async (formData) => {
  try {
    const result = await financeAPI.createReceipt(formData);
    if (result.success) {
      // Add to local state
      setReceipts(prev => [result.data, ...prev]);
      
      // Update dashboard
      if (dashboardData) {
        setDashboardData(prev => ({
          ...prev,
          total_income: (prev.total_income || 0) + parseFloat(formData.amount),
          pending_receipts: (prev.pending_receipts || 0) + 1
        }));
      }
      
      setShowCreateModal(false);
      addNotification('Receipt created successfully', 'success');
    }
  } catch (error) {
    addError('Failed to create receipt', error);
  }
}, [dashboardData]);

// Generate report
const handleGenerateReport = useCallback(async (reportType) => {
  try {
    const result = await financeAPI.generateReport(reportType, {
      dateRange: filters.dateRange,
      format: 'pdf'
    });
    
    if (result.success) {
      // Add to reports list
      setReports(prev => [{
        id: generateId(),
        name: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
        type: reportType,
        period: filters.dateRange,
        generated_by: userProfile?.first_name + ' ' + userProfile?.last_name,
        date_generated: new Date().toISOString(),
        size: result.data.size || '1.2MB'
      }, ...prev]);
      
      addNotification(`${reportType} report generated successfully`, 'success');
    }
  } catch (error) {
    addError(`Failed to generate ${reportType} report`, error);
  }
}, [filters.dateRange, userProfile]);

// Navigation handler
const handleNavigate = useCallback((tab) => {
  setActiveTab(tab);
  navigate(`#${tab}`);
}, [navigate]);

// Logout handler
const handleLogout = useCallback(async () => {
  try {
    await logout();
    navigate('/login');
  } catch (error) {
    addError('Logout failed', error);
  }
}, [logout, navigate]);

// Auto-refresh (every 5 minutes)
useEffect(() => {
  if (!userProfile?.settings?.autoRefresh) return;
  
  const interval = setInterval(() => {
    if (document.visibilityState === 'visible') {
      refreshData();
    }
  }, 5 * 60 * 1000); // 5 minutes
  
  return () => clearInterval(interval);
}, [refreshData, userProfile?.settings?.autoRefresh]);

// Handle online/offline status
useEffect(() => {
  const handleOnline = () => {
    addNotification('You are back online', 'success');
    refreshData(); // Refresh data when coming back online
  };
  
  const handleOffline = () => {
    addNotification('You are offline. Some features may be limited.', 'warning');
  };
  
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  
  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
}, [refreshData]);

// Keyboard shortcuts
useEffect(() => {
  const handleKeyDown = (e) => {
    // Ctrl/Cmd + R to refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
      e.preventDefault();
      if (!refreshing) {
        refreshData();
      }
    }
    
    // Ctrl/Cmd + N to create new receipt
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault();
      if (activeTab === 'receipts') {
        setShowCreateModal(true);
      }
    }
    
    // Esc to close modals
    if (e.key === 'Escape') {
      if (showCreateModal) setShowCreateModal(false);
      if (showSettings) setShowSettings(false);
      if (showExportModal) setShowExportModal(false);
    }
  };
  
  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, [refreshing, refreshData, activeTab, showCreateModal, showSettings, showExportModal]);

// Render current view
const renderCurrentView = () => {
  switch (activeTab) {
    case 'dashboard':
      return (
        <DashboardView
          data={dashboardData}
          receipts={receipts.slice(0, 5)}
          payments={payments.slice(0, 5)}
          debts={debts.slice(0, 5)}
          onRefresh={refreshData}
          refreshing={refreshing}
          onGenerateReport={handleGenerateReport}
          onNavigate={handleNavigate}
        />
      );
      
    case 'receipts':
      return (
        <ReceiptsView
          receipts={paginatedReceipts}
          totalReceipts={filteredReceipts.length}
          pagination={pagination}
          setPagination={setPagination}
          filters={filters}
          setFilters={setFilters}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          onVerify={handleVerifyReceipt}
          onExport={() => handleExport('receipts')}
          onView={(id) => {
            setSelectedItem(id);
            // Navigate to receipt detail view
            navigate(`/receipts/${id}`);
          }}
          onEdit={(id) => {
            setSelectedItem(id);
            // Implement edit functionality
          }}
          onRefresh={refreshData}
        />
      );
      
    case 'payments':
      return (
        <PaymentsView
          payments={payments}
          onApprove={async (id) => {
            try {
              const result = await financeAPI.approvePayment(id);
              if (result.success) {
                setPayments(prev => prev.map(payment =>
                  payment.id === id 
                    ? { ...payment, status: 'approved' }
                    : payment
                ));
                addNotification('Payment approved', 'success');
              }
            } catch (error) {
              addError('Failed to approve payment', error);
            }
          }}
          onExport={() => handleExport('payments')}
        />
      );
      
    case 'debts':
      return (
        <DebtsView
          debts={debts}
          dashboardData={dashboardData}
          onExport={() => handleExport('debts')}
        />
      );
      
    case 'reconciliation':
      return (
        <ReconciliationView
          dashboardData={dashboardData}
          receipts={receipts}
        />
      );
      
    case 'analytics':
      return (
        <AnalyticsView
          receipts={receipts}
          payments={payments}
          debts={debts}
        />
      );
      
    case 'fee-structures':
      return (
        <FeeStructuresView
          feeStructures={feeStructures}
          onExport={() => handleExport('fee-structures')}
        />
      );
      
    case 'reports':
      return (
        <ReportsView
          reports={reports}
          onGenerateReport={handleGenerateReport}
        />
      );
      
    case 'system':
      return (
        <SystemView
          systemStats={systemStats}
          auditLogs={auditLogs}
          onRefresh={refreshData}
        />
      );
      
    default:
      return (
        <Alert variant="warning">
          <h4>View Not Found</h4>
          <p>The requested view "{activeTab}" does not exist.</p>
        </Alert>
      );
  }
};

// If auth is still loading, show loading overlay
if (authLoading) {
  return <LoadingOverlay message="Checking authentication..." />;
}

// If no user, redirect to login
if (!currentUser) {
  navigate('/login');
  return null;
}

// Main render
return (
  <ErrorBoundary>
    <Container fluid className="p-0 accountant-portal">
      <LoadingOverlay show={loading && !refreshing} message="Loading portal..." />
      
      {/* Header */}
      <header className="sticky-top bg-white shadow-sm border-bottom z-3">
        <div className="d-flex align-items-center justify-content-between px-3 py-2">
          {/* Left side: Logo and title */}
          <div className="d-flex align-items-center gap-3">
            <Button
              variant="link"
              className="text-dark"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            >
              <List size={20} />
            </Button>
            
            <div className="d-flex align-items-center gap-2">
              <Image
                src="/logo.png"
                alt="School Logo"
                width={32}
                height={32}
                rounded
              />
              <div>
                <h5 className="mb-0">Delvok Academy</h5>
                <small className="text-muted">Accountant Portal</small>
              </div>
            </div>
          </div>
          
          {/* Center: Search */}
          <div className="flex-grow-1 mx-4" style={{ maxWidth: '400px' }}>
            <InputGroup>
              <InputGroup.Text>
                <Search />
              </InputGroup.Text>
              <Form.Control
                type="search"
                placeholder="Search receipts, students, payments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && searchTerm.trim()) {
                    setActiveTab('receipts');
                  }
                }}
              />
            </InputGroup>
          </div>
          
          {/* Right side: User actions */}
          <div className="d-flex align-items-center gap-2">
            {/* Refresh button */}
            <OverlayTrigger overlay={<Tooltip>Refresh Data</Tooltip>}>
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={refreshData}
                disabled={refreshing}
              >
                <ArrowClockwise className={refreshing ? 'spinning' : ''} />
              </Button>
            </OverlayTrigger>
            
            {/* Notifications */}
            <Dropdown show={showNotifications} onToggle={setShowNotifications}>
              <Dropdown.Toggle as={Button} variant="outline-secondary" size="sm">
                <div className="position-relative">
                  <Bell />
                  {notifications.length > 0 && (
                    <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                      {notifications.length}
                    </span>
                  )}
                </div>
              </Dropdown.Toggle>
              <Dropdown.Menu className="p-0" style={{ width: '300px' }}>
                <div className="p-2 border-bottom">
                  <div className="d-flex justify-content-between align-items-center">
                    <h6 className="mb-0">Notifications</h6>
                    {notifications.length > 0 && (
                      <Button
                        variant="link"
                        size="sm"
                        onClick={() => setNotifications([])}
                      >
                        Clear all
                      </Button>
                    )}
                  </div>
                </div>
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                  {notifications.length > 0 ? (
                    notifications.map(notif => (
                      <Dropdown.Item key={notif.id} className="border-bottom">
                        <div className="d-flex align-items-start gap-2">
                          <div className={`text-${notif.type}`}>
                            {notif.type === 'success' && <CheckCircle />}
                            {notif.type === 'error' && <ExclamationTriangle />}
                            {notif.type === 'warning' && <ExclamationCircle />}
                            {notif.type === 'info' && <InfoCircle />}
                          </div>
                          <div className="flex-grow-1">
                            <small>{notif.message}</small>
                            <div className="text-muted">
                              <small>{formatDateTime(notif.timestamp, true)}</small>
                            </div>
                          </div>
                          <Button
                            variant="link"
                            size="sm"
                            className="text-muted"
                            onClick={(e) => {
                              e.stopPropagation();
                              setNotifications(prev => 
                                prev.filter(n => n.id !== notif.id)
                              );
                            }}
                          >
                            <XLg size={12} />
                          </Button>
                        </div>
                      </Dropdown.Item>
                    ))
                  ) : (
                    <div className="text-center py-3">
                      <Bell size={24} className="text-muted mb-2" />
                      <p className="text-muted mb-0">No notifications</p>
                    </div>
                  )}
                </div>
              </Dropdown.Menu>
            </Dropdown>
            
            {/* Settings */}
            <OverlayTrigger overlay={<Tooltip>Settings</Tooltip>}>
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={() => setShowSettings(true)}
              >
                <Gear />
              </Button>
            </OverlayTrigger>
            
            {/* User dropdown */}
            <Dropdown>
              <Dropdown.Toggle as={Button} variant="link" className="text-dark">
                <div className="d-flex align-items-center gap-2">
                  <div className={`rounded-circle bg-primary text-white d-flex align-items-center justify-content-center`} 
                       style={{ width: '32px', height: '32px' }}>
                    {userProfile?.first_name?.[0] || 'A'}
                    {userProfile?.last_name?.[0] || ''}
                  </div>
                  <div className="d-none d-md-block text-start">
                    <small className="d-block">
                      {userProfile?.first_name} {userProfile?.last_name}
                    </small>
                    <small className="text-muted">Accountant</small>
                  </div>
                </div>
              </Dropdown.Toggle>
              <Dropdown.Menu align="end">
                <Dropdown.Header>
                  Signed in as <strong>{userProfile?.email}</strong>
                </Dropdown.Header>
                <Dropdown.Item onClick={() => navigate('/profile')}>
                  <PersonCircle className="me-2" />
                  My Profile
                </Dropdown.Item>
                <Dropdown.Item onClick={() => setShowSettings(true)}>
                  <GearWide className="me-2" />
                  Settings
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item onClick={handleLogout}>
                  <BoxArrowRight className="me-2" />
                  Logout
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </div>
        </div>
        
        {/* Tabs navigation */}
        <Nav variant="tabs" className="px-3 border-0">
          {[
            { key: 'dashboard', label: 'Dashboard', icon: <Speedometer2 /> },
            { key: 'receipts', label: 'Receipts', icon: <Receipt /> },
            { key: 'payments', label: 'Payments', icon: <CreditCard /> },
            { key: 'debts', label: 'Debts', icon: <Wallet2 /> },
            { key: 'reconciliation', label: 'Reconciliation', icon: <Calculator /> },
            { key: 'analytics', label: 'Analytics', icon: <GraphUp /> },
            { key: 'fee-structures', label: 'Fee Structures', icon: <CashCoin /> },
            { key: 'reports', label: 'Reports', icon: <FileEarmarkBarGraph /> },
            { key: 'system', label: 'System', icon: <Gear /> }
          ].map(tab => (
            <Nav.Item key={tab.key}>
              <Nav.Link
                active={activeTab === tab.key}
                onClick={() => handleNavigate(tab.key)}
                className="d-flex align-items-center gap-1"
              >
                {tab.icon}
                <span className="d-none d-md-inline">{tab.label}</span>
              </Nav.Link>
            </Nav.Item>
          ))}
        </Nav>
      </header>
      
      {/* Main content */}
      <Container fluid className="mt-3">
        {/* Error toasts */}
        <ToastContainer position="top-end" className="p-3">
          {errors.map(error => (
            <Toast
              key={error.id}
              bg="danger"
              onClose={() => setErrors(prev => prev.filter(e => e.id !== error.id))}
              delay={10000}
              autohide
            >
              <Toast.Header>
                <ExclamationTriangle className="me-2" />
                <strong className="me-auto">Error</strong>
                <small>{formatDateTime(error.timestamp, true)}</small>
              </Toast.Header>
              <Toast.Body className="text-white">
                <div>{error.message}</div>
                {error.details && (
                  <small className="opacity-75">{error.details}</small>
                )}
              </Toast.Body>
            </Toast>
          ))}
        </ToastContainer>
        
        {/* Last refresh indicator */}
        {lastRefreshTime && (
          <Row className="mb-2">
            <Col>
              <small className="text-muted d-flex align-items-center gap-1">
                <Clock size={12} />
                Last updated: {formatDateTime(lastRefreshTime, true)}
              </small>
            </Col>
          </Row>
        )}
        
        {/* Render current view */}
        {renderCurrentView()}
        
        {/* Quick stats footer */}
        <Row className="mt-4">
          <Col>
            <Card className="border-0 bg-light">
              <Card.Body className="py-2">
                <div className="d-flex justify-content-between align-items-center">
                  <div className="d-flex align-items-center gap-4">
                    <div className="text-center">
                      <small className="text-muted d-block">Today's Collection</small>
                      <strong className="text-success">
                        {formatCurrency(
                          receipts
                            .filter(r => new Date(r.date).toDateString() === new Date().toDateString())
                            .reduce((sum, r) => sum + (parseFloat(r.amount) || 0), 0)
                        )}
                      </strong>
                    </div>
                    <div className="text-center">
                      <small className="text-muted d-block">Pending Verification</small>
                      <strong className="text-warning">
                        {receipts.filter(r => r.status === 'pending').length}
                      </strong>
                    </div>
                    <div className="text-center">
                      <small className="text-muted d-block">System Status</small>
                      <Badge bg="success">
                        <CheckCircle size={12} className="me-1" />
                        Online
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <small className="text-muted">
                      Portal v1.0 • {new Date().getFullYear()} Delvok Academy
                    </small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
      
      {/* Modals */}
      
      {/* Settings Modal */}
      <Modal show={showSettings} onHide={() => setShowSettings(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Portal Settings</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <PortalSettings onClose={() => setShowSettings(false)} />
        </Modal.Body>
      </Modal>
      
      {/* Create Receipt Modal */}
      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create New Receipt</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <CreateReceiptForm onSubmit={handleCreateReceipt} />
        </Modal.Body>
      </Modal>
      
      {/* Export Modal */}
      <Modal show={showExportModal} onHide={() => setShowExportModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Export Data</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Export Type</Form.Label>
              <Form.Select>
                <option value="receipts">Receipts</option>
                <option value="payments">Payments</option>
                <option value="debts">Debts</option>
                <option value="fee-structures">Fee Structures</option>
                <option value="reports">Reports</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Format</Form.Label>
              <div>
                <Form.Check
                  type="radio"
                  name="format"
                  label="Excel (.xlsx)"
                  value="excel"
                  defaultChecked
                />
                <Form.Check
                  type="radio"
                  name="format"
                  label="PDF (.pdf)"
                  value="pdf"
                />
                <Form.Check
                  type="radio"
                  name="format"
                  label="CSV (.csv)"
                  value="csv"
                />
              </div>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Date Range</Form.Label>
              <Form.Select>
                <option value="all">All Data</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
                <option value="year">This Year</option>
                <option value="custom">Custom Range</option>
              </Form.Select>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowExportModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={() => {
            setShowExportModal(false);
            handleExport('receipts', 'excel');
          }}>
            <Download className="me-2" />
            Export
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  </ErrorBoundary>
);
};

export default AccountantPortal;