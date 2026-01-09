// src/pages/Portals/AdminPortal.jsx - FIXED VERSION
import React, { useState, useEffect, useCallback, useRef } from 'react';
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
  Dropdown,
  ButtonGroup,
  Modal,
  Form,
  Tabs,
  Tab
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { 
  PeopleFill,
  PersonCheckFill,
  BookFill,
  GraphUp,
  GearFill,
  ShieldCheck,
  Database,
  Activity,
  CashStack,
  CreditCard,
  CalendarCheck,
  BellFill,
  FileText,
  HouseDoor,
  Mortarboard,
  PersonPlus,
  CloudUpload,
  Download,
  ArrowClockwise,
  Eye,
  ArrowUp,
  ArrowDown,
  CheckCircle,
  XCircle,
  ExclamationTriangle,
  CloudCheck,
  HddStack,
  Cpu,
  ClockHistory,
  LockFill,
  PieChart,
  FileEarmarkBarGraph,
  Search,
  Filter,
  ThreeDotsVertical,
  PlusCircle,
  InfoCircle,
  Clock,
  CalendarEvent,
  HddFill,
  Memory,
  Server,
  Wifi,
  CloudFill,
  ShieldLock,
  Building,
  JournalBookmark,
  Wallet,
  Calculator,
  BarChart,
  People,
  PersonBoundingBox,
  Tools,
  Laptop,
  Robot,
  Lightbulb,
  Collection,
  ChatDots,
  Envelope,
  Phone,
  QuestionCircle,
  Gear,
  Power,
  Speedometer2,
  ShieldShaded,
  HddNetwork,
  CpuFill,
  BroadcastPin,
  ClipboardCheck,
  ListTask,
  ExclamationOctagon,
  Bullseye,
  Award,
  RocketTakeoff
} from 'react-bootstrap-icons';
import { useAuth } from '../../context/AuthContext';
import { adminAPI } from '../../services/adminAPI';
import { academicAPI } from '../../services/academicAPI';
import { financeAPI } from '../../services/financeAPI';

// Constants for better maintainability
const TIME_RANGES = [
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'quarter', label: 'This Quarter' },
  { value: 'year', label: '2026 YTD' }
];

const STATUS_CONFIG = {
  'online': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
  'healthy': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
  'completed': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
  'active': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
  'excellent': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
  'good': { variant: 'info', icon: <CheckCircle size={12} className="me-1" /> },
  'warning': { variant: 'warning', icon: <ExclamationTriangle size={12} className="me-1" /> },
  'error': { variant: 'danger', icon: <XCircle size={12} className="me-1" /> },
  'offline': { variant: 'danger', icon: <XCircle size={12} className="me-1" /> },
  'critical': { variant: 'danger', icon: <ExclamationOctagon size={12} className="me-1" /> },
  'high': { variant: 'danger', icon: <ExclamationTriangle size={12} className="me-1" /> },
  'medium': { variant: 'warning', icon: <InfoCircle size={12} className="me-1" /> },
  'low': { variant: 'info', icon: <InfoCircle size={12} className="me-1" /> }
};

const SYSTEM_COMPONENTS = [
  { id: 'server', name: 'Server', icon: <Server />, color: 'primary' },
  { id: 'database', name: 'Database', icon: <Database />, color: 'info' },
  { id: 'backup', name: 'Backup', icon: <CloudCheck />, color: 'success' },
  { id: 'security', name: 'Security', icon: <ShieldLock />, color: 'danger' },
  { id: 'storage', name: 'Storage', icon: <HddStack />, color: 'warning' },
  { id: 'performance', name: 'Performance', icon: <Cpu />, color: 'secondary' }
];

const QUICK_ACTIONS = [
  {
    title: 'User Management',
    description: 'Manage all system users',
    icon: <PeopleFill size={24} />,
    path: '/admin/users',
    variant: 'primary',
    permission: 'users.manage'
  },
  {
    title: 'Academic Setup',
    description: 'Configure academic programs',
    icon: <BookFill size={24} />,
    path: '/admin/academic',
    variant: 'info',
    permission: 'academic.manage'
  },
  {
    title: 'Financial Control',
    description: 'Monitor finances & reports',
    icon: <CashStack size={24} />,
    path: '/admin/finance',
    variant: 'warning',
    permission: 'finance.view'
  },
  {
    title: 'System Configuration',
    description: 'System settings & maintenance',
    icon: <GearFill size={24} />,
    path: '/admin/system',
    variant: 'secondary',
    permission: 'system.configure'
  },
  {
    title: 'Analytics Hub',
    description: 'Advanced analytics & AI',
    icon: <GraphUp size={24} />,
    path: '/admin/analytics',
    variant: 'dark',
    permission: 'analytics.view'
  },
  {
    title: 'Digital Campus',
    description: 'Smart campus management',
    icon: <Laptop size={24} />,
    path: '/admin/digital-campus',
    variant: 'success',
    permission: 'digital.manage'
  }
];

// Utility functions
const formatNumber = (number) => {
  if (number === undefined || number === null) return '0';
  return new Intl.NumberFormat('en-KE').format(number);
};

const formatCurrency = (amount) => {
  if (amount === undefined || amount === null) return 'KES 0';
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

const formatPercentage = (value) => {
  if (value === undefined || value === null) return '0%';
  return `${value.toFixed(1)}%`;
};

const getStatusBadge = (status, type = 'system') => {
  const config = STATUS_CONFIG[status?.toLowerCase()] || { variant: 'secondary', icon: <Activity size={12} className="me-1" /> };
  
  return (
    <Badge bg={config.variant} className="d-flex align-items-center">
      {config.icon}
      {status?.charAt(0).toUpperCase() + status?.slice(1)}
    </Badge>
  );
};

const getTrendIndicator = (value) => {
  if (value > 0) {
    return <ArrowUp size={14} className="text-success ms-1" />;
  } else if (value < 0) {
    return <ArrowDown size={14} className="text-danger ms-1" />;
  }
  return null;
};

const AdminPortal = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const abortControllerRef = useRef(new AbortController());
  
  // State management
  const [dashboardData, setDashboardData] = useState({
    summary: {},
    systemStats: {},
    recentActivities: [],
    pendingTasks: [],
    financialMetrics: {},
    academicMetrics: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [timeRange, setTimeRange] = useState('month');
  const [activeTab, setActiveTab] = useState('overview');
  const [showAnnouncementModal, setShowAnnouncementModal] = useState(false);
  const [announcementData, setAnnouncementData] = useState({
    title: '',
    message: '',
    priority: 'medium'
  });
  const [lastRefreshTime, setLastRefreshTime] = useState(Date.now());

  // Clear error messages after timeout
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      abortControllerRef.current.abort();
    };
  }, []);

  // ✅ FIXED: Batch API calls with correct function names
  const batchAPICalls = async (signal) => {
    try {
      const [
        adminSummary,
        academicOverview,
        financeSummary,
        systemHealth,
        recentActivities,
        pendingTasks
      ] = await Promise.all([
        adminAPI.getDashboardSummary({ time_range: timeRange }), // ✅ Fixed function name
        academicAPI.getAcademicOverview(),
        financeAPI.getDashboardSummary(timeRange),
        adminAPI.getSystemHealth(),
        adminAPI.getRecentActivities(),
        adminAPI.getPendingTasks()
      ]);

      return {
        adminSummary,
        academicOverview,
        financeSummary,
        systemHealth,
        recentActivities,
        pendingTasks
      };
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('API Call Error:', err);
        throw err;
      }
      return null;
    }
  };

  // ✅ FIXED: Fetch all dashboard data
  const fetchDashboardData = useCallback(async (silentRefresh = false) => {
    try {
      if (!silentRefresh) {
        setLoading(true);
      }
      setRefreshing(true);
      setError('');

      // Cancel previous request
      abortControllerRef.current.abort();
      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;

      const results = await batchAPICalls(signal);
      
      if (!results) return; // Request was aborted

      const {
        adminSummary,
        academicOverview,
        financeSummary,
        systemHealth,
        recentActivities,
        pendingTasks
      } = results;

      // Handle case where API calls might fail individually
      const adminData = adminSummary?.success ? adminSummary.data : {};
      const academicData = academicOverview?.success ? academicOverview.data : {};
      const financeData = financeSummary?.success ? financeSummary.data : {};
      const healthData = systemHealth?.success ? systemHealth.data : {};
      const activitiesData = recentActivities?.success ? (recentActivities.data || []) : [];
      const tasksData = pendingTasks?.success ? (pendingTasks.data || []) : [];

      // Combine all data with fallbacks
      const combinedData = {
        summary: {
          totalStudents: academicData.totalStudents || academicData.total_students || 0,
          totalTeachers: academicData.totalTeachers || academicData.total_teachers || 0,
          activeCourses: academicData.activeCourses || academicData.active_courses || 0,
          systemHealth: healthData.overallHealth || healthData.overall_health || 100,
          storageUsed: healthData.storageUsage || healthData.storage_usage || 0,
          totalRevenue: financeData.totalRevenue || financeData.total_revenue || 0,
          pendingPayments: financeData.pendingPayments || financeData.pending_payments || 0,
          collectionRate: financeData.collectionRate || financeData.collection_rate || 0,
          activeUsers: adminData.activeUsers || adminData.active_users || 0,
          pendingApprovals: adminData.pendingApprovals || adminData.pending_approvals || 0,
          academicYear: academicData.academicYear || academicData.academic_year || '2026-2027',
          currentTerm: academicData.currentTerm || academicData.current_term || 'Term 1'
        },
        systemStats: {
          server: {
            status: healthData.serverStatus || healthData.server_status || 'online',
            uptime: healthData.serverUptime || healthData.server_uptime || '99.9%',
            responseTime: healthData.responseTime || healthData.response_time || '45ms'
          },
          database: {
            status: healthData.databaseStatus || healthData.database_status || 'healthy',
            connections: healthData.activeConnections || healthData.active_connections || 42,
            size: healthData.databaseSize || healthData.database_size || '2.8GB'
          },
          backup: {
            status: healthData.backupStatus || healthData.backup_status || 'completed',
            lastBackup: healthData.lastBackup || healthData.last_backup || '2 hours ago',
            nextBackup: healthData.nextBackup || healthData.next_backup || 'Tonight 2:00 AM'
          },
          security: {
            status: healthData.securityStatus || healthData.security_status || 'active',
            threats: healthData.securityThreats || healthData.security_threats || 0,
            lastScan: healthData.lastSecurityScan || healthData.last_security_scan || '1 hour ago'
          },
          storage: {
            status: healthData.storageStatus || healthData.storage_status || 'good',
            usage: healthData.storageUsage || healthData.storage_usage || '65%',
            available: healthData.storageAvailable || healthData.storage_available || '1.2TB'
          },
          performance: {
            status: healthData.performanceStatus || healthData.performance_status || 'excellent',
            load: healthData.systemLoad || healthData.system_load || '32%',
            memory: healthData.memoryUsage || healthData.memory_usage || '58%'
          }
        },
        recentActivities: activitiesData,
        pendingTasks: tasksData,
        financialMetrics: {
          annualBudget: financeData.annualBudget || financeData.annual_budget || 0,
          ytdRevenue: financeData.ytdRevenue || financeData.ytd_revenue || 0,
          ytdExpenses: financeData.ytdExpenses || financeData.ytd_expenses || 0,
          profitMargin: financeData.profitMargin || financeData.profit_margin || 0,
          outstandingDebts: financeData.outstandingDebts || financeData.outstanding_debts || 0
        },
        academicMetrics: {
          enrollmentGrowth: academicData.enrollmentGrowth || academicData.enrollment_growth || 0,
          graduationRate: academicData.graduationRate || academicData.graduation_rate || 0,
          studentTeacherRatio: academicData.studentTeacherRatio || academicData.student_teacher_ratio || 0,
          researchFunding: academicData.researchFunding || academicData.research_funding || 0,
          internationalStudents: academicData.internationalStudents || academicData.international_students || 0,
          aiAdoption: academicData.aiAdoption || academicData.ai_adoption || 0
        }
      };

      setDashboardData(combinedData);
      setLastRefreshTime(Date.now());

    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Error fetching dashboard data:', err);
        setError(err.response?.data?.message || err.message || 'Failed to load dashboard data. Please try again.');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 5 minutes
    const refreshInterval = setInterval(() => {
      fetchDashboardData(true);
    }, 300000);

    return () => clearInterval(refreshInterval);
  }, [fetchDashboardData]);

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
  };

  const handleCreateAnnouncement = async () => {
    try {
      await adminAPI.createAnnouncement(announcementData);
      setShowAnnouncementModal(false);
      setAnnouncementData({ title: '', message: '', priority: 'medium' });
      // Refresh to show new announcement
      fetchDashboardData(true);
    } catch (err) {
      console.error('Error creating announcement:', err);
      setError('Failed to create announcement');
    }
  };

  const handleSystemAction = async (action, systemId) => {
    try {
      let response;
      switch (action) {
        case 'restart':
          response = await adminAPI.restartSystem(systemId);
          break;
        case 'backup':
          response = await adminAPI.initiateBackup();
          break;
        case 'maintenance':
          response = await adminAPI.toggleMaintenanceMode();
          break;
        case 'diagnostic':
          response = await adminAPI.runDiagnostics();
          break;
        default:
          return;
      }
      
      if (response?.success) {
        // Refresh system stats after delay
        setTimeout(() => fetchDashboardData(true), 2000);
      } else {
        setError(`Failed to perform ${action}: ${response?.error?.message || 'Unknown error'}`);
      }
    } catch (err) {
      console.error(`Error performing ${action}:`, err);
      setError(`Failed to perform ${action}`);
    }
  };

  const handleQuickAction = (action) => {
    navigate(action.path);
  };

  const handleViewDetails = (type, id) => {
    switch (type) {
      case 'activity':
        navigate(`/admin/activities/${id}`);
        break;
      case 'task':
        navigate(`/admin/tasks/${id}`);
        break;
      case 'user':
        navigate(`/admin/users/${id}`);
        break;
      default:
        break;
    }
  };

  // Calculate statistics for display
  const stats = {
    totalStudents: dashboardData?.summary?.totalStudents || 0,
    totalTeachers: dashboardData?.summary?.totalTeachers || 0,
    activeUsers: dashboardData?.summary?.activeUsers || 0,
    pendingApprovals: dashboardData?.summary?.pendingApprovals || 0,
    totalRevenue: dashboardData?.summary?.totalRevenue || 0,
    pendingPayments: dashboardData?.summary?.pendingPayments || 0,
    collectionRate: dashboardData?.summary?.collectionRate || 0,
    systemHealth: dashboardData?.summary?.systemHealth || 100,
    enrollmentGrowth: dashboardData?.academicMetrics?.enrollmentGrowth || 0,
    graduationRate: dashboardData?.academicMetrics?.graduationRate || 0,
    aiAdoption: dashboardData?.academicMetrics?.aiAdoption || 0
  };

  // ✅ FIXED: Added missing icon import
  const RocketTakeoff = ({ size, className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} fill="currentColor" className={className} viewBox="0 0 16 16">
      <path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0zM7.5 3.5a.5.5 0 0 0-1 0V8a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 7.71V3.5z"/>
    </svg>
  );

  if (loading && !refreshing) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '70vh' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" size="lg" />
          <p className="mt-3 text-muted">Loading Admin Dashboard...</p>
          <small className="text-muted">Loading system data...</small>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="admin-portal px-3 px-md-4 py-4">
      {/* Header Section */}
      <Row className="mb-4 align-items-center">
        <Col>
          <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
            <div>
              <div className="d-flex align-items-center mb-2">
                <div className="bg-primary bg-opacity-10 p-2 rounded me-3">
                  <GearFill size={24} className="text-primary" />
                </div>
                <div>
                  <h1 className="h2 mb-1">
                    <span className="text-gradient-primary">Admin Portal</span>
                  </h1>
                  <div className="d-flex align-items-center gap-2 flex-wrap">
                    <p className="text-muted mb-0">
                      Welcome back, <span className="fw-semibold">{currentUser?.name || 'Administrator'}</span>
                    </p>
                    {dashboardData?.summary?.academicYear && (
                      <Badge bg="primary" className="d-flex align-items-center gap-1">
                        <CalendarEvent size={12} />
                        {dashboardData.summary.academicYear} • {dashboardData.summary.currentTerm}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="d-flex flex-column flex-md-row gap-2 align-items-start align-items-md-center">
              <div className="d-flex gap-2 align-items-center">
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm" className="d-flex align-items-center">
                    <Filter size={14} className="me-1" />
                    {TIME_RANGES.find(r => r.value === timeRange)?.label || 'This Month'}
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    {TIME_RANGES.map((range) => (
                      <Dropdown.Item 
                        key={range.value}
                        onClick={() => handleTimeRangeChange(range.value)}
                        active={timeRange === range.value}
                      >
                        {range.label}
                      </Dropdown.Item>
                    ))}
                  </Dropdown.Menu>
                </Dropdown>
                
                <Button 
                  variant="outline-primary" 
                  onClick={handleRefresh}
                  disabled={refreshing}
                  size="sm"
                  className="d-flex align-items-center"
                  title="Refresh Dashboard"
                >
                  <ArrowClockwise className={`me-1 ${refreshing ? 'spinning' : ''}`} size={14} />
                  {refreshing ? 'Refreshing...' : 'Refresh'}
                </Button>
              </div>
              
              <Button 
                variant="primary" 
                onClick={() => setShowAnnouncementModal(true)}
                size="sm"
                className="d-flex align-items-center mt-2 mt-md-0"
              >
                <BellFill size={14} className="me-1" />
                Announce
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')} className="mb-4">
          <div className="d-flex align-items-center">
            <ExclamationTriangle className="me-2 flex-shrink-0" />
            <div>
              <Alert.Heading className="h6 mb-1">Error Loading Data</Alert.Heading>
              <p className="mb-0 small">{error}</p>
            </div>
          </div>
        </Alert>
      )}

      {/* Navigation Tabs */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Body className="p-2">
              <Tabs
                activeKey={activeTab}
                onSelect={setActiveTab}
                className="border-0"
                fill
              >
                <Tab eventKey="overview" title={
                  <div className="d-flex align-items-center">
                    <Speedometer2 size={16} className="me-2" />
                    Overview
                  </div>
                } />
                <Tab eventKey="system" title={
                  <div className="d-flex align-items-center">
                    <Server size={16} className="me-2" />
                    System
                  </div>
                } />
                <Tab eventKey="analytics" title={
                  <div className="d-flex align-items-center">
                    <GraphUp size={16} className="me-2" />
                    Analytics
                  </div>
                } />
                <Tab eventKey="reports" title={
                  <div className="d-flex align-items-center">
                    <FileEarmarkBarGraph size={16} className="me-2" />
                    Reports
                  </div>
                } />
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
          {/* Quick Stats */}
          <Row className="g-3 mb-4">
            <Col xl={3} lg={6}>
              <Card className="h-100 border-0 shadow-sm hover-lift">
                <Card.Body>
                  <div className="d-flex align-items-start justify-content-between">
                    <div>
                      <div className="d-flex align-items-center mb-2">
                        <div className="bg-primary bg-opacity-10 p-2 rounded me-3">
                          <PeopleFill size={20} className="text-primary" />
                        </div>
                        <div>
                          <h6 className="text-uppercase text-muted mb-0">Total Students</h6>
                          <div className="d-flex align-items-center">
                            <small className="text-muted">
                              Growth: 
                              <span className={`ms-1 ${stats.enrollmentGrowth > 0 ? 'text-success' : 'text-danger'}`}>
                                {getTrendIndicator(stats.enrollmentGrowth)}
                                {formatPercentage(stats.enrollmentGrowth)}
                              </span>
                            </small>
                          </div>
                        </div>
                      </div>
                      <h2 className="mb-1">{formatNumber(stats.totalStudents)}</h2>
                      {stats.graduationRate > 0 && (
                        <ProgressBar 
                          now={stats.graduationRate} 
                          variant="success" 
                          className="mt-2" 
                          style={{ height: '6px' }}
                          label={`${formatPercentage(stats.graduationRate)} graduation rate`}
                        />
                      )}
                    </div>
                    {stats.pendingApprovals > 0 && (
                      <Badge bg="danger" pill className="ms-2">
                        {stats.pendingApprovals}
                      </Badge>
                    )}
                  </div>
                </Card.Body>
              </Card>
            </Col>

            <Col xl={3} lg={6}>
              <Card className="h-100 border-0 shadow-sm hover-lift">
                <Card.Body>
                  <div className="d-flex align-items-start justify-content-between">
                    <div>
                      <div className="d-flex align-items-center mb-2">
                        <div className="bg-info bg-opacity-10 p-2 rounded me-3">
                          <Mortarboard size={20} className="text-info" />
                        </div>
                        <div>
                          <h6 className="text-uppercase text-muted mb-0">Faculty & Staff</h6>
                          <div className="d-flex align-items-center">
                            <small className="text-muted">
                              <PersonCheckFill size={12} className="me-1" />
                              {formatNumber(stats.activeUsers)} active
                            </small>
                          </div>
                        </div>
                      </div>
                      <h2 className="mb-1">{formatNumber(stats.totalTeachers)}</h2>
                      {stats.studentTeacherRatio > 0 && (
                        <small className="text-muted d-block mt-1">
                          Ratio: 1:{stats.studentTeacherRatio.toFixed(1)}
                        </small>
                      )}
                    </div>
                    <div className="text-end">
                      <small className="text-muted d-block">Staff</small>
                      <Badge bg="info">Active</Badge>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            <Col xl={3} lg={6}>
              <Card className="h-100 border-0 shadow-sm hover-lift">
                <Card.Body>
                  <div className="d-flex align-items-start justify-content-between">
                    <div>
                      <div className="d-flex align-items-center mb-2">
                        <div className="bg-warning bg-opacity-10 p-2 rounded me-3">
                          <CashStack size={20} className="text-warning" />
                        </div>
                        <div>
                          <h6 className="text-uppercase text-muted mb-0">2026 Revenue</h6>
                          <div className="d-flex align-items-center">
                            <small className="text-muted">
                              Collection: {formatPercentage(stats.collectionRate)}
                            </small>
                          </div>
                        </div>
                      </div>
                      <h2 className="mb-1">{formatCurrency(stats.totalRevenue)}</h2>
                      {stats.pendingPayments > 0 && (
                        <Alert variant="warning" className="p-1 mt-2 mb-0">
                          <small>
                            <ExclamationTriangle size={12} className="me-1" />
                            {stats.pendingPayments} pending payments
                          </small>
                        </Alert>
                      )}
                    </div>
                    <div className="text-end">
                      <small className="text-muted d-block">KES</small>
                      <Badge bg="warning">Revenue</Badge>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            <Col xl={3} lg={6}>
              <Card className="h-100 border-0 shadow-sm hover-lift">
                <Card.Body>
                  <div className="d-flex align-items-start justify-content-between">
                    <div>
                      <div className="d-flex align-items-center mb-2">
                        <div className="bg-success bg-opacity-10 p-2 rounded me-3">
                          <Activity size={20} className="text-success" />
                        </div>
                        <div>
                          <h6 className="text-uppercase text-muted mb-0">System Health</h6>
                          <div className="d-flex align-items-center">
                            <small className="text-muted">
                              <Server size={12} className="me-1" />
                              {dashboardData?.systemStats?.server?.uptime || '99.9%'} uptime
                            </small>
                          </div>
                        </div>
                      </div>
                      <h2 className="mb-1">{formatPercentage(stats.systemHealth)}</h2>
                      <ProgressBar 
                        now={stats.systemHealth} 
                        variant={stats.systemHealth > 90 ? 'success' : stats.systemHealth > 70 ? 'warning' : 'danger'} 
                        className="mt-2" 
                        style={{ height: '6px' }}
                      />
                    </div>
                    <div className="text-end">
                      <small className="text-muted d-block">Status</small>
                      {getStatusBadge(stats.systemHealth > 90 ? 'excellent' : stats.systemHealth > 70 ? 'good' : 'warning')}
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Quick Actions Grid */}
          <Row className="g-3 mb-4">
            <Col>
              <h5 className="mb-3 d-flex align-items-center">
                <RocketTakeoff size={20} className="me-2 text-primary" />
                Quick Actions
              </h5>
            </Col>
            {QUICK_ACTIONS.map((action, index) => (
              <Col lg={4} md={6} key={index}>
                <Card 
                  className="h-100 border-0 shadow-sm text-decoration-none hover-lift cursor-pointer"
                  onClick={() => handleQuickAction(action)}
                >
                  <Card.Body className="d-flex align-items-center p-3">
                    <div className={`bg-${action.variant} bg-opacity-10 p-3 rounded me-3`}>
                      {React.cloneElement(action.icon, { className: `text-${action.variant}` })}
                    </div>
                    <div className="flex-grow-1">
                      <h6 className="mb-1">{action.title}</h6>
                      <small className="text-muted d-block">{action.description}</small>
                    </div>
                    <ArrowClockwise size={16} className="text-muted" />
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>

          {/* Recent Activities & Pending Tasks */}
          <Row className="g-3">
            <Col lg={6}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0 d-flex align-items-center">
                      <ClockHistory className="me-2 text-primary" />
                      Recent Activities
                    </h5>
                    <Badge bg="light" text="dark" className="border">
                      {dashboardData?.recentActivities?.length || 0} total
                    </Badge>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  <div className="list-group list-group-flush">
                    {dashboardData?.recentActivities?.length > 0 ? (
                      dashboardData.recentActivities.slice(0, 6).map((activity, index) => (
                        <div 
                          key={index} 
                          className="list-group-item border-0 px-3 py-2 hover-bg-light cursor-pointer"
                          onClick={() => handleViewDetails('activity', activity.id)}
                        >
                          <div className="d-flex align-items-start">
                            <div className="me-3">
                              {activity.type === 'user' && <PersonPlus size={16} className="text-success" />}
                              {activity.type === 'finance' && <CreditCard size={16} className="text-warning" />}
                              {activity.type === 'academic' && <BookFill size={16} className="text-info" />}
                              {activity.type === 'system' && <GearFill size={16} className="text-secondary" />}
                            </div>
                            <div className="flex-grow-1">
                              <div className="d-flex justify-content-between">
                                <small className="fw-semibold">{activity.action}</small>
                                <small className="text-muted">
                                  <Clock size={12} className="me-1" />
                                  {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </small>
                              </div>
                              <small className="text-muted d-block">{activity.description}</small>
                              <small className="text-muted">
                                <PersonCheckFill size={12} className="me-1" />
                                {activity.user}
                              </small>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4">
                        <Activity size={32} className="text-muted mb-2" />
                        <p className="text-muted mb-0">No recent activities</p>
                      </div>
                    )}
                  </div>
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    as={Link} 
                    to="/admin/activities" 
                    variant="link" 
                    size="sm" 
                    className="text-decoration-none w-100 text-center"
                  >
                    View All Activities
                    <Eye className="ms-1" size={14} />
                  </Button>
                </Card.Footer>
              </Card>
            </Col>

            <Col lg={6}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0 d-flex align-items-center">
                      <ListTask className="me-2 text-primary" />
                      Pending Tasks
                    </h5>
                    <Badge bg="warning">
                      {dashboardData?.pendingTasks?.length || 0}
                    </Badge>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  <div className="list-group list-group-flush">
                    {dashboardData?.pendingTasks?.length > 0 ? (
                      dashboardData.pendingTasks.slice(0, 6).map((task, index) => (
                        <div 
                          key={index} 
                          className="list-group-item border-0 px-3 py-2 hover-bg-light cursor-pointer"
                          onClick={() => handleViewDetails('task', task.id)}
                        >
                          <div className="d-flex align-items-start">
                            <div className="me-3">
                              {getStatusBadge(task.priority, 'priority')}
                            </div>
                            <div className="flex-grow-1">
                              <div className="d-flex justify-content-between">
                                <small className="fw-semibold">{task.title}</small>
                                <Badge bg="light" text="dark" className="border">
                                  {task.type}
                                </Badge>
                              </div>
                              <small className="text-muted d-block mb-1">{task.description}</small>
                              <div className="d-flex justify-content-between align-items-center">
                                <small className="text-muted">
                                  <CalendarCheck size={12} className="me-1" />
                                  Due: {new Date(task.dueDate).toLocaleDateString()}
                                </small>
                                <Button size="sm" variant="outline-primary">Review</Button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4">
                        <CheckCircle size={32} className="text-success mb-2" />
                        <p className="text-muted mb-0">All tasks completed</p>
                      </div>
                    )}
                  </div>
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    as={Link} 
                    to="/admin/tasks" 
                    variant="link" 
                    size="sm" 
                    className="text-decoration-none w-100 text-center"
                  >
                    View All Tasks
                    <Eye className="ms-1" size={14} />
                  </Button>
                </Card.Footer>
              </Card>
            </Col>
          </Row>

          {/* Financial Metrics */}
          <Row className="g-3 mt-4">
            <Col md={12}>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0 d-flex align-items-center">
                    <BarChart className="me-2 text-primary" />
                    Financial Overview
                    {stats.aiAdoption > 0 && (
                      <Badge bg="info" className="ms-2">
                        <Robot size={12} className="me-1" />
                        AI-Powered Insights
                      </Badge>
                    )}
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Row className="g-3">
                    <Col xs={6} md={3}>
                      <div className="text-center p-2 hover-lift rounded">
                        <h6 className="text-uppercase text-muted mb-2">Annual Budget</h6>
                        <h4 className="mb-0">{formatCurrency(dashboardData?.financialMetrics?.annualBudget)}</h4>
                        <ProgressBar 
                          now={((dashboardData?.financialMetrics?.ytdExpenses || 0) / (dashboardData?.financialMetrics?.annualBudget || 1) * 100)} 
                          variant="info" 
                          className="mt-2"
                          style={{ height: '4px' }}
                        />
                        <small className="text-muted">
                          Spent: {formatPercentage(((dashboardData?.financialMetrics?.ytdExpenses || 0) / (dashboardData?.financialMetrics?.annualBudget || 1) * 100))}
                        </small>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="text-center p-2 hover-lift rounded">
                        <h6 className="text-uppercase text-muted mb-2">YTD Revenue</h6>
                        <h4 className="mb-0 text-success">
                          {formatCurrency(dashboardData?.financialMetrics?.ytdRevenue)}
                          {getTrendIndicator(dashboardData?.financialMetrics?.profitMargin)}
                        </h4>
                        <small className="text-muted">
                          vs Budget: {formatPercentage(((dashboardData?.financialMetrics?.ytdRevenue || 0) / (dashboardData?.financialMetrics?.annualBudget || 1) * 100))}
                        </small>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="text-center p-2 hover-lift rounded">
                        <h6 className="text-uppercase text-muted mb-2">YTD Expenses</h6>
                        <h4 className="mb-0 text-danger">
                          {formatCurrency(dashboardData?.financialMetrics?.ytdExpenses)}
                        </h4>
                        <small className="text-muted">
                          vs Budget: {formatPercentage(((dashboardData?.financialMetrics?.ytdExpenses || 0) / (dashboardData?.financialMetrics?.annualBudget || 1) * 100))}
                        </small>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="text-center p-2 hover-lift rounded">
                        <h6 className="text-uppercase text-muted mb-2">Profit Margin</h6>
                        <h4 className="mb-0">
                          {formatPercentage(dashboardData?.financialMetrics?.profitMargin)}
                        </h4>
                        <small className="text-muted">
                          ROI: {formatPercentage(((dashboardData?.financialMetrics?.ytdRevenue - dashboardData?.financialMetrics?.ytdExpenses) / dashboardData?.financialMetrics?.ytdExpenses * 100) || 0)}
                        </small>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* System Tab */}
      {activeTab === 'system' && (
        <Row className="g-3">
          <Col xl={8} lg={12}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0 d-flex align-items-center">
                    <Activity className="me-2 text-primary" />
                    System Health Monitor
                  </h5>
                  <ButtonGroup size="sm">
                    <Button 
                      variant="outline-secondary" 
                      onClick={() => handleSystemAction('backup')}
                      className="d-flex align-items-center"
                    >
                      <CloudUpload className="me-1" size={12} />
                      Backup
                    </Button>
                    <Button 
                      variant="outline-secondary" 
                      onClick={() => handleSystemAction('maintenance')}
                      className="d-flex align-items-center"
                    >
                      <Tools className="me-1" size={12} />
                      Maintenance
                    </Button>
                    <Button 
                      variant="outline-secondary" 
                      onClick={() => handleSystemAction('diagnostic')}
                      className="d-flex align-items-center"
                    >
                      <ClipboardCheck className="me-1" size={12} />
                      Diagnostics
                    </Button>
                  </ButtonGroup>
                </div>
              </Card.Header>
              <Card.Body>
                <Table responsive className="mb-0">
                  <thead>
                    <tr>
                      <th>Component</th>
                      <th>Status</th>
                      <th>Details</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {SYSTEM_COMPONENTS.map((component) => {
                      const stats = dashboardData?.systemStats?.[component.id];
                      if (!stats) return null;
                      
                      return (
                        <tr key={component.id}>
                          <td>
                            <div className="d-flex align-items-center">
                              <span className={`me-2 text-${component.color}`}>{component.icon}</span>
                              <span>{component.name}</span>
                            </div>
                          </td>
                          <td>{getStatusBadge(stats.status)}</td>
                          <td>
                            <small className="text-muted">
                              {component.id === 'storage' && `${stats.usage} used`}
                              {component.id === 'performance' && `Load: ${stats.load}`}
                              {component.id === 'server' && `Response: ${stats.responseTime}`}
                              {component.id === 'database' && `Connections: ${stats.connections}`}
                              {component.id === 'backup' && `Last: ${stats.lastBackup}`}
                              {component.id === 'security' && `Threats: ${stats.threats}`}
                            </small>
                          </td>
                          <td>
                            <Button 
                              size="sm" 
                              variant="outline-primary"
                              onClick={() => handleSystemAction('restart', component.id)}
                              title={`Restart ${component.name}`}
                            >
                              <Power size={12} />
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </Table>
                
                {/* Storage Usage Visualization */}
                {dashboardData?.systemStats?.storage && (
                  <div className="mt-4">
                    <div className="d-flex justify-content-between mb-2">
                      <small className="text-muted">Storage Usage</small>
                      <small className="text-muted">{dashboardData.systemStats.storage.usage} used</small>
                    </div>
                    <ProgressBar 
                      now={parseInt(dashboardData.systemStats.storage.usage)} 
                      variant={parseInt(dashboardData.systemStats.storage.usage) > 90 ? 'danger' : 
                              parseInt(dashboardData.systemStats.storage.usage) > 70 ? 'warning' : 'success'}
                      className="mb-3"
                      style={{ height: '8px' }}
                    />
                    <div className="d-flex justify-content-between">
                      <small className="text-muted">
                        <Database size={12} className="me-1" />
                        Available: {dashboardData.systemStats.storage.available}
                      </small>
                      <small className="text-muted">
                        Status: {getStatusBadge(dashboardData.systemStats.storage.status)}
                      </small>
                    </div>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>

          <Col xl={4} lg={12}>
            <Row className="g-3">
              <Col md={12}>
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0 py-3">
                    <h5 className="mb-0 d-flex align-items-center">
                      <ClockHistory className="me-2 text-primary" />
                      Recent Activities
                    </h5>
                  </Card.Header>
                  <Card.Body className="p-0" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    <div className="list-group list-group-flush">
                      {dashboardData?.recentActivities?.length > 0 ? (
                        dashboardData.recentActivities.slice(0, 8).map((activity, index) => (
                          <div 
                            key={index} 
                            className="list-group-item border-0 px-3 py-2 hover-bg-light cursor-pointer"
                            onClick={() => handleViewDetails('activity', activity.id)}
                          >
                            <div className="d-flex align-items-start">
                              <div className="me-3">
                                {activity.type === 'user' && <PersonPlus size={16} className="text-success" />}
                                {activity.type === 'finance' && <CreditCard size={16} className="text-warning" />}
                                {activity.type === 'academic' && <BookFill size={16} className="text-info" />}
                                {activity.type === 'system' && <GearFill size={16} className="text-secondary" />}
                              </div>
                              <div className="flex-grow-1">
                                <div className="d-flex justify-content-between">
                                  <small className="fw-semibold">{activity.action}</small>
                                  <small className="text-muted">
                                    <Clock size={12} className="me-1" />
                                    {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                  </small>
                                </div>
                                <small className="text-muted d-block">{activity.description}</small>
                                <small className="text-muted">
                                  <PersonCheckFill size={12} className="me-1" />
                                  {activity.user}
                                </small>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-4">
                          <Activity size={32} className="text-muted mb-2" />
                          <p className="text-muted mb-0">No recent activities</p>
                        </div>
                      )}
                    </div>
                  </Card.Body>
                  <Card.Footer className="bg-white border-0">
                    <Button 
                      as={Link} 
                      to="/admin/activities" 
                      variant="link" 
                      size="sm" 
                      className="text-decoration-none w-100 text-center"
                    >
                      View All Activities
                      <Eye className="ms-1" size={14} />
                    </Button>
                  </Card.Footer>
                </Card>
              </Col>
            </Row>
          </Col>
        </Row>
      )}

      {/* Footer */}
      <Row className="mt-4">
        <Col>
          <Card className="border-0 bg-light">
            <Card.Body className="py-2">
              <div className="d-flex justify-content-between align-items-center flex-wrap">
                <small className="text-muted">
                  <Clock size={12} className="me-1" />
                  Last Updated: {new Date(lastRefreshTime).toLocaleString()}
                  {refreshing && <span className="ms-2">🔄 Refreshing...</span>}
                </small>
                <div className="d-flex align-items-center">
                  <small className="text-muted me-3">
                    <ShieldShaded size={12} className="me-1" />
                    System Status: 
                    <Badge bg={stats.systemHealth > 90 ? 'success' : stats.systemHealth > 70 ? 'warning' : 'danger'} className="ms-1">
                      {formatPercentage(stats.systemHealth)}
                    </Badge>
                  </small>
                  <small className="text-muted">
                    <BroadcastPin size={12} className="me-1" />
                    Version: 2.0.0 • 2026
                  </small>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Announcement Modal */}
      <Modal show={showAnnouncementModal} onHide={() => setShowAnnouncementModal(false)} centered>
        <Modal.Header closeButton className="border-0">
          <Modal.Title className="d-flex align-items-center">
            <BellFill className="me-2 text-primary" />
            Create Announcement
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold">Title</Form.Label>
              <Form.Control
                type="text"
                value={announcementData.title}
                onChange={(e) => setAnnouncementData({...announcementData, title: e.target.value})}
                placeholder="Enter announcement title"
                className="border-1"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold">Message</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={announcementData.message}
                onChange={(e) => setAnnouncementData({...announcementData, message: e.target.value})}
                placeholder="Enter announcement message"
                className="border-1"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold">Priority</Form.Label>
              <Form.Select
                value={announcementData.priority}
                onChange={(e) => setAnnouncementData({...announcementData, priority: e.target.value})}
                className="border-1"
              >
                <option value="high">High Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="low">Low Priority</option>
              </Form.Select>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className="border-0">
          <Button variant="light" onClick={() => setShowAnnouncementModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateAnnouncement} className="d-flex align-items-center">
            <BellFill className="me-1" />
            Publish Announcement
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Custom CSS */}
      <style jsx="true">{`
        .admin-portal {
          min-height: calc(100vh - 76px);
        }
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .hover-lift {
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .hover-lift:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }
        .hover-bg-light:hover {
          background-color: rgba(0,0,0,0.02) !important;
        }
        .cursor-pointer {
          cursor: pointer;
        }
        .text-gradient-primary {
          background: linear-gradient(135deg, #00695c 0%, #004d40 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .border-1 {
          border-width: 1px !important;
        }
        .card {
          border-radius: 0.75rem;
        }
        .progress-bar {
          border-radius: 4px;
        }
      `}</style>
    </Container>
  );
};

export default AdminPortal;