// src/pages/Portals/AdminPortal.jsx
import React, { useState, useEffect, useCallback } from 'react';
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
  Form
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
  GraduationCap,
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
  Power
} from 'react-bootstrap-icons';
import { useAuth } from '../../context/AuthContext';
import { adminAPI } from '../../services/adminAPI';
import { academicAPI } from '../../services/academicAPI';
import { financeAPI } from '../../services/financeAPI';


const AdminPortal = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  // State management
  const [dashboardData, setDashboardData] = useState(null);
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

  // Fetch all dashboard data
  const fetchDashboardData = useCallback(async (silentRefresh = false) => {
    try {
      if (!silentRefresh) {
        setLoading(true);
      }
      setRefreshing(true);
      setError('');

      // Fetch data from all APIs in parallel
      const [
        adminSummary,
        academicOverview,
        financeSummary,
        systemHealth,
        recentActivities,
        pendingTasks
      ] = await Promise.all([
        adminAPI.getDashboardSummary(timeRange),
        academicAPI.getOverview(),
        financeAPI.getDashboardSummary(timeRange),
        adminAPI.getSystemHealth(),
        adminAPI.getRecentActivities(),
        adminAPI.getPendingTasks()
      ]);

      // Combine all data
      const combinedData = {
        summary: {
          totalStudents: academicOverview.data?.totalStudents || 0,
          totalTeachers: academicOverview.data?.totalTeachers || 0,
          activeCourses: academicOverview.data?.activeCourses || 0,
          systemHealth: systemHealth.data?.overallHealth || 100,
          storageUsed: systemHealth.data?.storageUsage || 0,
          totalRevenue: financeSummary.data?.totalRevenue || 0,
          pendingPayments: financeSummary.data?.pendingPayments || 0,
          collectionRate: financeSummary.data?.collectionRate || 0,
          activeUsers: adminSummary.data?.activeUsers || 0,
          pendingApprovals: adminSummary.data?.pendingApprovals || 0,
          academicYear: academicOverview.data?.academicYear || '2026-2027',
          currentTerm: academicOverview.data?.currentTerm || 'Term 1'
        },
        systemStats: {
          server: {
            status: systemHealth.data?.serverStatus || 'online',
            uptime: systemHealth.data?.serverUptime || '99.9%',
            responseTime: systemHealth.data?.responseTime || '45ms'
          },
          database: {
            status: systemHealth.data?.databaseStatus || 'healthy',
            connections: systemHealth.data?.activeConnections || 42,
            size: systemHealth.data?.databaseSize || '2.8GB'
          },
          backup: {
            status: systemHealth.data?.backupStatus || 'completed',
            lastBackup: systemHealth.data?.lastBackup || '2 hours ago',
            nextBackup: systemHealth.data?.nextBackup || 'Tonight 2:00 AM'
          },
          security: {
            status: systemHealth.data?.securityStatus || 'active',
            threats: systemHealth.data?.securityThreats || 0,
            lastScan: systemHealth.data?.lastSecurityScan || '1 hour ago'
          },
          storage: {
            status: systemHealth.data?.storageStatus || 'good',
            usage: systemHealth.data?.storageUsage || '65%',
            available: systemHealth.data?.storageAvailable || '1.2TB'
          },
          performance: {
            status: systemHealth.data?.performanceStatus || 'excellent',
            load: systemHealth.data?.systemLoad || '32%',
            memory: systemHealth.data?.memoryUsage || '58%'
          }
        },
        recentActivities: recentActivities.data || [],
        pendingTasks: pendingTasks.data || [],
        financialMetrics: {
          annualBudget: financeSummary.data?.annualBudget || 0,
          ytdRevenue: financeSummary.data?.ytdRevenue || 0,
          ytdExpenses: financeSummary.data?.ytdExpenses || 0,
          profitMargin: financeSummary.data?.profitMargin || 0,
          outstandingDebts: financeSummary.data?.outstandingDebts || 0
        },
        academicMetrics: {
          enrollmentGrowth: academicOverview.data?.enrollmentGrowth || 0,
          graduationRate: academicOverview.data?.graduationRate || 0,
          studentTeacherRatio: academicOverview.data?.studentTeacherRatio || 0,
          researchFunding: academicOverview.data?.researchFunding || 0,
          internationalStudents: academicOverview.data?.internationalStudents || 0,
          aiAdoption: academicOverview.data?.aiAdoption || 0
        }
      };

      setDashboardData(combinedData);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.message || 'Failed to load dashboard data. Please try again.');
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
        default:
          return;
      }
      
      if (response.success) {
        // Refresh system stats
        fetchDashboardData(true);
      }
    } catch (err) {
      console.error(`Error performing ${action}:`, err);
      setError(`Failed to perform ${action}`);
    }
  };

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
    const statusConfig = {
      'online': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
      'healthy': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
      'completed': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
      'active': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
      'excellent': { variant: 'success', icon: <CheckCircle size={12} className="me-1" /> },
      'good': { variant: 'info', icon: <CheckCircle size={12} className="me-1" /> },
      'warning': { variant: 'warning', icon: <ExclamationTriangle size={12} className="me-1" /> },
      'error': { variant: 'danger', icon: <XCircle size={12} className="me-1" /> },
      'offline': { variant: 'danger', icon: <XCircle size={12} className="me-1" /> },
      'high': { variant: 'danger', icon: <ExclamationTriangle size={12} className="me-1" /> },
      'medium': { variant: 'warning', icon: <InfoCircle size={12} className="me-1" /> },
      'low': { variant: 'info', icon: <InfoCircle size={12} className="me-1" /> }
    };

    const config = statusConfig[status?.toLowerCase()] || { variant: 'secondary', icon: <Activity size={12} className="me-1" /> };
    
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

  const quickActions = [
    {
      title: 'User Management',
      description: 'Manage all system users',
      icon: <PeopleFill size={24} />,
      path: '/admin/users',
      variant: 'primary',
      badge: dashboardData?.summary?.pendingApprovals || 0,
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
      badge: dashboardData?.summary?.pendingPayments || 0,
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

  const systemHealthItems = dashboardData?.systemStats ? Object.entries(dashboardData.systemStats).map(([key, stat]) => ({
    id: key,
    name: key.charAt(0).toUpperCase() + key.slice(1),
    icon: key === 'server' ? <Server /> : 
           key === 'database' ? <Database /> : 
           key === 'backup' ? <CloudCheck /> : 
           key === 'security' ? <ShieldLock /> : 
           key === 'storage' ? <HddStack /> : <Cpu />,
    status: stat.status,
    details: stat
  })) : [];

  if (loading && !refreshing) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '70vh' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" size="lg" />
          <p className="mt-3 text-muted">Loading Admin Dashboard...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="admin-portal">
      {/* Header Section */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
            <div>
              <h1 className="h2 mb-1">
                <GearFill className="me-2 text-primary" />
                Admin Portal
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
                {dashboardData?.summary?.systemHealth && (
                  <Badge bg={dashboardData.summary.systemHealth > 90 ? 'success' : 'warning'} className="d-flex align-items-center gap-1">
                    <ShieldCheck size={12} />
                    System: {dashboardData.summary.systemHealth}%
                  </Badge>
                )}
              </div>
            </div>
            
            <div className="d-flex gap-2 align-items-center">
              <Dropdown>
                <Dropdown.Toggle variant="outline-secondary" size="sm">
                  <Filter size={14} className="me-1" />
                  {timeRange === 'week' ? 'This Week' : 
                   timeRange === 'month' ? 'This Month' : 
                   timeRange === 'quarter' ? 'This Quarter' : '2026 YTD'}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={() => handleTimeRangeChange('week')}>This Week</Dropdown.Item>
                  <Dropdown.Item onClick={() => handleTimeRangeChange('month')}>This Month</Dropdown.Item>
                  <Dropdown.Item onClick={() => handleTimeRangeChange('quarter')}>This Quarter</Dropdown.Item>
                  <Dropdown.Item onClick={() => handleTimeRangeChange('year')}>2026 YTD</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              
              <Button 
                variant="outline-primary" 
                onClick={handleRefresh}
                disabled={refreshing}
                size="sm"
                className="d-flex align-items-center"
              >
                <ArrowClockwise className={refreshing ? 'spinning' : ''} size={14} />
              </Button>
              
              <Button 
                variant="primary" 
                onClick={() => setShowAnnouncementModal(true)}
                size="sm"
                className="d-flex align-items-center"
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
          <Alert.Heading className="h6">
            <ExclamationTriangle className="me-2" />
            Error Loading Data
          </Alert.Heading>
          <p className="mb-0 small">{error}</p>
        </Alert>
      )}

      {/* Quick Stats */}
      <Row className="g-3 mb-4">
        <Col xl={3} lg={6}>
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-start justify-content-between">
                <div>
                  <div className="d-flex align-items-center mb-2">
                    <div className="bg-primary bg-opacity-10 p-2 rounded me-3">
                      <PeopleFill size={20} className="text-primary" />
                    </div>
                    <h6 className="text-uppercase text-muted mb-0">Total Students</h6>
                  </div>
                  <h2 className="mb-1">{formatNumber(dashboardData?.summary?.totalStudents)}</h2>
                  <div className="d-flex align-items-center">
                    <small className="text-muted">
                      Enrollment: 
                      <span className={`ms-1 ${dashboardData?.academicMetrics?.enrollmentGrowth > 0 ? 'text-success' : 'text-danger'}`}>
                        {getTrendIndicator(dashboardData?.academicMetrics?.enrollmentGrowth)}
                        {formatPercentage(dashboardData?.academicMetrics?.enrollmentGrowth)}
                      </span>
                    </small>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6}>
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-start justify-content-between">
                <div>
                  <div className="d-flex align-items-center mb-2">
                    <div className="bg-info bg-opacity-10 p-2 rounded me-3">
                      <GraduationCap size={20} className="text-info" />
                    </div>
                    <h6 className="text-uppercase text-muted mb-0">Faculty & Staff</h6>
                  </div>
                  <h2 className="mb-1">{formatNumber(dashboardData?.summary?.totalTeachers)}</h2>
                  <div className="d-flex align-items-center">
                    <small className="text-muted">
                      <PersonCheckFill size={12} className="me-1" />
                      {formatNumber(dashboardData?.summary?.activeUsers)} active
                    </small>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6}>
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-start justify-content-between">
                <div>
                  <div className="d-flex align-items-center mb-2">
                    <div className="bg-warning bg-opacity-10 p-2 rounded me-3">
                      <CashStack size={20} className="text-warning" />
                    </div>
                    <h6 className="text-uppercase text-muted mb-0">2026 Revenue</h6>
                  </div>
                  <h2 className="mb-1">{formatCurrency(dashboardData?.summary?.totalRevenue)}</h2>
                  <div className="d-flex align-items-center">
                    <small className="text-muted">
                      Collection: {formatPercentage(dashboardData?.summary?.collectionRate)}
                      {dashboardData?.summary?.pendingPayments > 0 && (
                        <Badge bg="danger" className="ms-2">
                          {dashboardData.summary.pendingPayments} pending
                        </Badge>
                      )}
                    </small>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6}>
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-start justify-content-between">
                <div>
                  <div className="d-flex align-items-center mb-2">
                    <div className="bg-success bg-opacity-10 p-2 rounded me-3">
                      <Activity size={20} className="text-success" />
                    </div>
                    <h6 className="text-uppercase text-muted mb-0">Performance</h6>
                  </div>
                  <h2 className="mb-1">{formatPercentage(dashboardData?.summary?.systemHealth)}</h2>
                  <div className="d-flex align-items-center">
                    <small className="text-muted">
                      <Server size={12} className="me-1" />
                      {dashboardData?.systemStats?.server?.uptime || '99.9%'} uptime
                    </small>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions Grid */}
      <Row className="g-3 mb-4">
        {quickActions.map((action, index) => (
          <Col lg={4} md={6} key={index}>
            <Card 
              as={Link} 
              to={action.path}
              className="h-100 border-0 shadow-sm text-decoration-none hover-lift"
            >
              <Card.Body className="d-flex align-items-center p-3">
                <div className={`bg-${action.variant} bg-opacity-10 p-3 rounded me-3`}>
                  {action.icon}
                </div>
                <div className="flex-grow-1">
                  <h6 className="mb-1">{action.title}</h6>
                  <small className="text-muted d-block">{action.description}</small>
                </div>
                {action.badge > 0 && (
                  <Badge bg="danger" pill>{action.badge}</Badge>
                )}
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      <Row className="g-3">
        {/* System Health */}
        <Col xl={6} lg={12}>
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
                  >
                    <CloudUpload className="me-1" size={12} />
                    Backup
                  </Button>
                  <Button 
                    variant="outline-secondary" 
                    onClick={() => handleSystemAction('maintenance')}
                  >
                    <Tools className="me-1" size={12} />
                    Maintenance
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
                  {systemHealthItems.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <div className="d-flex align-items-center">
                          <span className="me-2 text-primary">{item.icon}</span>
                          <span>{item.name}</span>
                        </div>
                      </td>
                      <td>{getStatusBadge(item.status)}</td>
                      <td>
                        <small className="text-muted">
                          {item.id === 'storage' && `${item.details.usage} used`}
                          {item.id === 'performance' && `Load: ${item.details.load}`}
                          {item.id === 'server' && `Response: ${item.details.responseTime}`}
                          {item.id === 'database' && `Connections: ${item.details.connections}`}
                          {item.id === 'backup' && `Last: ${item.details.lastBackup}`}
                          {item.id === 'security' && `Threats: ${item.details.threats}`}
                        </small>
                      </td>
                      <td>
                        <Button 
                          size="sm" 
                          variant="outline-primary"
                          onClick={() => handleSystemAction('restart', item.id)}
                        >
                          <Power size={12} />
                        </Button>
                      </td>
                    </tr>
                  ))}
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
                    variant={parseInt(dashboardData.systemStats.storage.usage) > 90 ? 'danger' : 'success'}
                    className="mb-3"
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

        {/* Recent Activities & Pending Tasks */}
        <Col xl={6} lg={12}>
          <Row className="g-3">
            <Col md={6}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0 d-flex align-items-center">
                    <ClockHistory className="me-2 text-primary" />
                    Recent Activities
                  </h5>
                </Card.Header>
                <Card.Body className="p-0">
                  <div className="list-group list-group-flush">
                    {dashboardData?.recentActivities?.length > 0 ? (
                      dashboardData.recentActivities.slice(0, 5).map((activity, index) => (
                        <div 
                          key={index} 
                          className="list-group-item border-0 px-3 py-2 hover-bg-light"
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
                    className="text-decoration-none"
                  >
                    View All Activities
                    <Eye className="ms-1" size={14} />
                  </Button>
                </Card.Footer>
              </Card>
            </Col>

            <Col md={6}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0 d-flex align-items-center">
                    <FileText className="me-2 text-primary" />
                    Pending Tasks
                  </h5>
                </Card.Header>
                <Card.Body className="p-0">
                  <div className="list-group list-group-flush">
                    {dashboardData?.pendingTasks?.length > 0 ? (
                      dashboardData.pendingTasks.slice(0, 5).map((task, index) => (
                        <div 
                          key={index} 
                          className="list-group-item border-0 px-3 py-2 hover-bg-light"
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
                    className="text-decoration-none"
                  >
                    View All Tasks
                    <Eye className="ms-1" size={14} />
                  </Button>
                </Card.Footer>
              </Card>
            </Col>

            {/* Financial Metrics */}
            <Col md={12}>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0 d-flex align-items-center">
                    <BarChart className="me-2 text-primary" />
                    Financial Overview
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Row className="g-3">
                    <Col xs={6} md={3}>
                      <div className="text-center">
                        <h6 className="text-uppercase text-muted mb-2">Annual Budget</h6>
                        <h4 className="mb-0">{formatCurrency(dashboardData?.financialMetrics?.annualBudget)}</h4>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="text-center">
                        <h6 className="text-uppercase text-muted mb-2">YTD Revenue</h6>
                        <h4 className="mb-0 text-success">
                          {formatCurrency(dashboardData?.financialMetrics?.ytdRevenue)}
                        </h4>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="text-center">
                        <h6 className="text-uppercase text-muted mb-2">YTD Expenses</h6>
                        <h4 className="mb-0 text-danger">
                          {formatCurrency(dashboardData?.financialMetrics?.ytdExpenses)}
                        </h4>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="text-center">
                        <h6 className="text-uppercase text-muted mb-2">Profit Margin</h6>
                        <h4 className="mb-0">
                          {formatPercentage(dashboardData?.financialMetrics?.profitMargin)}
                        </h4>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>

      {/* Announcement Modal */}
      <Modal show={showAnnouncementModal} onHide={() => setShowAnnouncementModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create Announcement</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                value={announcementData.title}
                onChange={(e) => setAnnouncementData({...announcementData, title: e.target.value})}
                placeholder="Enter announcement title"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Message</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={announcementData.message}
                onChange={(e) => setAnnouncementData({...announcementData, message: e.target.value})}
                placeholder="Enter announcement message"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Priority</Form.Label>
              <Form.Select
                value={announcementData.priority}
                onChange={(e) => setAnnouncementData({...announcementData, priority: e.target.value})}
              >
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </Form.Select>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAnnouncementModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateAnnouncement}>
            Publish Announcement
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Custom CSS */}
      <style jsx="true">{`
        .admin-portal {
          padding: 20px;
          background-color: #f8f9fa;
          min-height: calc(100vh - 76px);
        }
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .hover-lift:hover {
          transform: translateY(-2px);
          transition: transform 0.2s ease;
        }
        .hover-bg-light:hover {
          background-color: rgba(0,0,0,0.03) !important;
        }
      `}</style>
    </Container>
  );
};

export default AdminPortal;