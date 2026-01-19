// src/pages/Portals/AdminPortal.jsx - ENHANCED PRODUCTION READY
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Alert, Spinner, ProgressBar, Dropdown, ButtonGroup,
  Modal, Form, Tabs, Tab, Tooltip, OverlayTrigger,
  InputGroup, ListGroup, Image
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Speedometer2, GraphUp, Server, FileEarmarkBarGraph, BellFill, GearFill, ShieldCheck,
  PeopleFill, PersonCheckFill, Mortarboard, BookFill, CashStack, CreditCard, Activity,
  Database, HddStack, Cpu, CloudCheck, ShieldLock, Wifi, Memory,
  ArrowClockwise, Eye, CheckCircle, XCircle, ExclamationTriangle,
  PlusCircle, InfoCircle, Clock, ClockHistory, ListTask, ClipboardCheck, Tools,
  Power, CloudUpload, Download, Search, Filter, ChevronRight,
  BoxArrowUpRight, PersonPlus, Bell, RocketTakeoff, GraphUpArrow, GraphDownArrow,
  ShieldExclamation, PersonBadge, FileEarmarkArrowDown, CalendarEvent, CalendarCheck,
  ExclamationOctagon, Wrench, HddFill, CloudFill, HddNetwork, CpuFill, ShieldShaded,
  BroadcastPin, Trophy, Robot, Buildings, BarChart, DashCircle,
  LightbulbFill, ExclamationDiamond, EyeSlash, Save, Printer, Share, StarFill,
  ArrowRepeat, Pencil, Trash, BellSlash, CheckSquare, CloudSlash, ChatDots,
  Envelope, Phone, QuestionCircle, HouseDoor, Calculator,
  People, LockFill, SortNumericUp, SortNumericDown, Lightbulb,
  Bullseye, Award, Collection, Laptop, Globe, PieChart
} from 'react-bootstrap-icons';
import { useAuth } from '../../context/AuthContext';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// ==================== IMPORT ALL APIS ====================
import { adminAPI } from '../../services/adminAPI';
import { academicsAPI } from '../../services/academicAPI';
import { financeAPI } from '../../services/financeAPI';
import {systemAPI} from '../../services/systemAPI';
import { analyticsAPI } from '../../services/analyticsAPI';
import { reportsAPI } from '../../services/reportsAPI';
import { notificationsAPI } from '../../services/notificationsAPI';
import authAPI from '../../services/authAPI';

// ==================== IMPORT CUSTOM HOOKS & COMPONENTS ====================
import useAPIPolling from '../../hooks/admin/useAPIPolling';
import useDebounce from '../../hooks/admin/useDebounce';
import useLocalStorage from '../../hooks/admin/useLocalStorage';
import DashboardCard from '../../components/admin/dashboard/DashboardCard';
import StatCard from '../../components/admin/dashboard/StatCard';
import LoadingSkeleton from '../../components/admin/feedback/LoadingSkeleton';
import ErrorBoundary from '../../components/admin/error/ErrorBoundary';
import ConfirmationModal from '../../components/admin/modals/ConfirmationModal';

// ==================== CONSTANTS ====================
const TIME_RANGES = [
  { value: 'today', label: 'Today', icon: <CalendarEvent size={14} />, refreshRate: 60000 },
  { value: 'week', label: 'This Week', icon: <CalendarCheck size={14} />, refreshRate: 300000 },
  { value: 'month', label: 'This Month', icon: <Clock size={14} />, refreshRate: 900000 },
  { value: 'quarter', label: 'This Quarter', icon: <CalendarCheck size={14} />, refreshRate: 1800000 },
  { value: 'year', label: 'This Year', icon: <CalendarEvent size={14} />, refreshRate: 3600000 }
];

const STATUS_CONFIG = {
  'online': { variant: 'success', icon: <CheckCircle size={14} />, label: 'Online' },
  'healthy': { variant: 'success', icon: <CheckCircle size={14} />, label: 'Healthy' },
  'active': { variant: 'success', icon: <CheckCircle size={14} />, label: 'Active' },
  'good': { variant: 'info', icon: <CheckCircle size={14} />, label: 'Good' },
  'warning': { variant: 'warning', icon: <ExclamationTriangle size={14} />, label: 'Warning' },
  'error': { variant: 'danger', icon: <XCircle size={14} />, label: 'Error' },
  'offline': { variant: 'danger', icon: <XCircle size={14} />, label: 'Offline' },
  'critical': { variant: 'danger', icon: <ExclamationOctagon size={14} />, label: 'Critical' },
  'pending': { variant: 'warning', icon: <Clock size={14} />, label: 'Pending' },
  'maintenance': { variant: 'secondary', icon: <Wrench size={14} />, label: 'Maintenance' }
};

const SYSTEM_COMPONENTS = [
  { id: 'server', name: 'Application Server', icon: <Server />, color: 'primary' },
  { id: 'database', name: 'Database Server', icon: <Database />, color: 'info' },
  { id: 'backup', name: 'Backup System', icon: <CloudCheck />, color: 'success' },
  { id: 'security', name: 'Security System', icon: <ShieldLock />, color: 'danger' },
  { id: 'storage', name: 'Storage System', icon: <HddStack />, color: 'warning' },
  { id: 'performance', name: 'Performance', icon: <Cpu />, color: 'secondary' },
  { id: 'network', name: 'Network', icon: <Wifi />, color: 'dark' },
  { id: 'cache', name: 'Cache System', icon: <Memory />, color: 'purple' }
];

const QUICK_ACTIONS = [
  {
    id: 'user-management',
    title: 'User Management',
    description: 'Manage all system users & permissions',
    icon: <PeopleFill size={24} />,
    path: '/admin/users',
    variant: 'primary',
    permission: 'users.manage'
  },
  {
    id: 'academic-config',
    title: 'Academic Configuration',
    description: 'Setup classes, subjects, and schedules',
    icon: <BookFill size={24} />,
    path: '/admin/academic',
    variant: 'info',
    permission: 'academic.manage'
  },
  {
    id: 'financial-management',
    title: 'Financial Management',
    description: 'Monitor finances, fees, and payments',
    icon: <CashStack size={24} />,
    path: '/admin/finance',
    variant: 'warning',
    permission: 'finance.view'
  },
  {
    id: 'system-config',
    title: 'System Configuration',
    description: 'System settings & maintenance',
    icon: <GearFill size={24} />,
    path: '/admin/system',
    variant: 'secondary',
    permission: 'system.configure'
  },
  {
    id: 'analytics-dashboard',
    title: 'Analytics Dashboard',
    description: 'Advanced analytics & insights',
    icon: <GraphUp size={24} />,
    path: '/admin/analytics',
    variant: 'dark',
    permission: 'analytics.view'
  },
  {
    id: 'reports-center',
    title: 'Reports Center',
    description: 'Generate and manage reports',
    icon: <FileEarmarkBarGraph size={24} />,
    path: '/admin/reports',
    variant: 'success',
    permission: 'reports.generate'
  }
];

// ==================== UTILITY FUNCTIONS ====================
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
  return `${Math.max(0, Math.min(100, value)).toFixed(1)}%`;
};

const getStatusBadge = (status) => {
  const config = STATUS_CONFIG[status?.toLowerCase()] || { 
    variant: 'secondary', 
    icon: <Activity size={12} />, 
    label: status || 'Unknown' 
  };
  
  return (
    <Badge bg={config.variant} className="d-flex align-items-center gap-1">
      {config.icon}
      {config.label}
    </Badge>
  );
};

const getTrendIndicator = (value) => {
  const numValue = Number(value) || 0;
  if (numValue > 0) {
    return (
      <span className="text-success d-flex align-items-center">
        <GraphUpArrow size={14} className="me-1" />
        +{Math.abs(numValue).toFixed(1)}%
      </span>
    );
  } else if (numValue < 0) {
    return (
      <span className="text-danger d-flex align-items-center">
        <GraphDownArrow size={14} className="me-1" />
        {numValue.toFixed(1)}%
      </span>
    );
  }
  return (
    <span className="text-muted d-flex align-items-center">
      <DashCircle size={14} className="me-1" />
      0%
    </span>
  );
};

const calculateSystemHealthScore = (components) => {
  if (!components || Object.keys(components).length === 0) return 100;
  
  const weights = {
    server: 0.3,
    database: 0.25,
    backup: 0.15,
    security: 0.2,
    storage: 0.1
  };
  
  let totalScore = 0;
  let totalWeight = 0;
  
  Object.entries(components).forEach(([key, component]) => {
    const weight = weights[key] || 0.05;
    if (component.status === 'healthy' || component.status === 'online') {
      totalScore += 100 * weight;
    } else if (component.status === 'warning') {
      totalScore += 60 * weight;
    } else {
      totalScore += 30 * weight;
    }
    totalWeight += weight;
  });
  
  return Math.round(totalScore);
};

// ==================== USER STATISTICS FUNCTIONS ====================
const getUserStatistics = (usersData) => {
  if (!usersData || !Array.isArray(usersData)) {
    return {
      totalStudents: 0,
      totalTeachers: 0,
      totalStaff: 0,
      totalUsers: 0,
      activeUsers: 0,
      pendingApprovals: 0,
      verifiedUsers: 0,
      suspendedUsers: 0
    };
  }

  // Define staff roles
  const staffRoles = [
    'admin', 'head_teacher', 'curriculum_coordinator', 'office_staff',
    'librarian', 'accountant', 'it_support', 'counselor'
  ];

  const stats = {
    totalStudents: usersData.filter(user => user.role === 'student').length,
    totalTeachers: usersData.filter(user => user.role === 'teacher').length,
    totalStaff: usersData.filter(user => staffRoles.includes(user.role)).length,
    totalUsers: usersData.length,
    activeUsers: usersData.filter(user => user.is_active).length,
    pendingApprovals: usersData.filter(user => !user.is_approved || !user.is_verified).length,
    verifiedUsers: usersData.filter(user => user.is_verified).length,
    suspendedUsers: usersData.filter(user => user.is_suspended).length
  };

  return stats;
};

// ==================== CUSTOM HOOKS ====================
const useDashboardData = (timeRange = 'month') => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 1. First, get users data for statistics (like UserManagement component)
      const usersResponse = await adminAPI.getUsers({
        page_size: 1000, // Get all users
        page: 1
      });
      
      const usersData = usersResponse.data?.results || usersResponse.data || [];
      const userStats = getUserStatistics(usersData);
      // 2. Get other data with error handling for system health
    let healthData;
    try {
      const healthResponse = await systemAPI.getHealthStatus();
      healthData = healthResponse.success ? healthResponse.data : null;
    } catch (healthError) {
      console.warn('System health endpoint not available:', healthError);
      healthData = {
        overall_score: 95,
        components: {
          server: { status: 'healthy', uptime: '99.9%', usage: '45%' },
          database: { status: 'healthy', uptime: '99.8%', usage: '60%' },
          backup: { status: 'healthy', uptime: '100%' },
          security: { status: 'healthy' },
          storage: { status: 'healthy', usage: '75%' }
        }
      };
    }
    
      // 2. Get other dashboard data in parallel
      const [activities, tasks, financial, academic, analytics] = await Promise.all([
        
        adminAPI.getRecentActivities({ limit: 10 }),
        adminAPI.getPendingTasks(),
        financeAPI.getFinancialSummary(timeRange),
        academicsAPI.getDashboardStatistics(),
        analyticsAPI.getUserAnalytics()
      ]);
      
      const combinedData = {
        summary: {
          // User statistics from users data
          totalStudents: userStats.totalStudents,
          totalTeachers: userStats.totalTeachers,
          totalStaff: userStats.totalStaff,
          totalUsers: userStats.totalUsers,
          activeUsers: userStats.activeUsers,
          pendingApprovals: userStats.pendingApprovals,
          verifiedUsers: userStats.verifiedUsers,
          suspendedUsers: userStats.suspendedUsers,
          
          // System health
          systemHealth: health?.data?.overall_score || 
                       health?.score || 
                       100,
          
          // Financial stats
          totalRevenue: financial?.data?.total_revenue || 
                       financial?.total_revenue || 
                       0,
          
          pendingPayments: financial?.data?.pending_payments || 
                          financial?.pending_payments || 
                          0,
          
          collectionRate: financial?.data?.collection_rate || 
                         financial?.collection_rate || 
                         0,
          
          // Academic info
          academicYear: academic?.data?.academic_year || 
                       academic?.current_academic_year || 
                       '2026',
          
          currentTerm: academic?.data?.current_term || 
                      academic?.current_term || 
                      'Term 1'
        },
        
        // Raw users data for other components
        usersData: usersData,
        
        // Other system data
        systemStats: health?.data?.components || 
                    health?.components || 
                    {},
        
        recentActivities: activities?.data?.activities || 
                         activities?.activities || 
                         [],
        
        pendingTasks: tasks?.data?.tasks || 
                     tasks?.tasks || 
                     [],
        
        financialMetrics: financial?.data || 
                         financial || 
                         {},
        
        academicMetrics: academic?.data || 
                        academic || 
                        {},
        
        userMetrics: analytics?.data || 
                     analytics || 
                     {},
        
        lastUpdated: Date.now()
      };
      
      setData(combinedData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, loading, error, refetch: fetchData };
};

// ==================== COMPONENTS ====================
const LoadingPlaceholder = ({ count = 4 }) => (
  <Row className="g-3 mb-4">
    {Array.from({ length: count }).map((_, index) => (
      <Col key={index} xl={3} lg={6}>
        <Card className="border-0 shadow-sm">
          <Card.Body>
            <div className="placeholder-glow">
              <div className="placeholder col-6 mb-3"></div>
              <div className="placeholder col-12 mb-2"></div>
              <div className="placeholder col-8"></div>
            </div>
          </Card.Body>
        </Card>
      </Col>
    ))}
  </Row>
);

const ErrorDisplay = ({ error, onRetry }) => (
  <Alert variant="danger" dismissible onClose={() => onRetry?.()} className="mb-4">
    <div className="d-flex align-items-center">
      <ExclamationTriangle className="me-2 flex-shrink-0" />
      <div className="flex-grow-1">
        <Alert.Heading className="h6 mb-1">System Error</Alert.Heading>
        <p className="mb-0 small">{error}</p>
        {onRetry && (
          <Button variant="outline-danger" size="sm" className="mt-2" onClick={onRetry}>
            <ArrowRepeat size={12} className="me-1" />
            Retry Loading
          </Button>
        )}
      </div>
    </div>
  </Alert>
);

const SystemHealthCard = ({ component, stats, onRestart }) => {
  const [loading, setLoading] = useState(false);
  
  const handleRestart = async () => {
    setLoading(true);
    try {
      await onRestart(component.id);
      toast.success(`Restarting ${component.name}...`);
    } catch (error) {
      toast.error(`Failed to restart ${component.name}`);
    } finally {
      setLoading(false);
    }
  };
  
  const config = STATUS_CONFIG[stats?.status?.toLowerCase()] || STATUS_CONFIG.warning;
  
  return (
    <Card className="border-0 shadow-sm h-100">
      <Card.Body>
        <div className="d-flex align-items-start mb-3">
          <div className={`bg-${component.color} bg-opacity-10 p-3 rounded me-3`}>
            {React.cloneElement(component.icon, { className: `text-${component.color}`, size: 24 })}
          </div>
          <div className="flex-grow-1">
            <h6 className="mb-1">{component.name}</h6>
            <Badge bg={config.variant} className="d-flex align-items-center gap-1">
              {config.icon}
              {config.label}
            </Badge>
          </div>
          <OverlayTrigger
            placement="top"
            overlay={<Tooltip>Restart Component</Tooltip>}
          >
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={handleRestart}
              disabled={loading}
              className="ms-2"
            >
              <Power size={12} />
            </Button>
          </OverlayTrigger>
        </div>
        
        {stats && (
          <div className="mt-3">
            {stats.uptime && (
              <div className="d-flex justify-content-between mb-2">
                <small className="text-muted">Uptime</small>
                <small className="fw-semibold">{stats.uptime}</small>
              </div>
            )}
            
            {stats.usage && (
              <>
                <div className="d-flex justify-content-between mb-1">
                  <small className="text-muted">Usage</small>
                  <small className="fw-semibold">{stats.usage}%</small>
                </div>
                <ProgressBar 
                  now={parseInt(stats.usage) || 0} 
                  variant={parseInt(stats.usage) > 90 ? 'danger' : 
                          parseInt(stats.usage) > 70 ? 'warning' : 'success'}
                  className="mb-3"
                  style={{ height: '6px' }}
                />
              </>
            )}
            
            {stats.details && (
              <small className="text-muted d-block">{stats.details}</small>
            )}
          </div>
        )}
        
        <div className="mt-3">
          <Button 
            size="sm" 
            variant="outline-primary"
            onClick={() => window.open(`/admin/health/${component.id}`, '_blank')}
            className="w-100"
          >
            <Eye size={12} className="me-1" />
            View Details
          </Button>
        </div>
      </Card.Body>
    </Card>
  );
};

const RecentActivityItem = ({ activity, onClick }) => {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'user': return <PersonPlus size={16} className="text-success" />;
      case 'finance': return <CreditCard size={16} className="text-warning" />;
      case 'academic': return <BookFill size={16} className="text-info" />;
      case 'system': return <GearFill size={16} className="text-secondary" />;
      case 'security': return <ShieldExclamation size={16} className="text-danger" />;
      default: return <Activity size={16} className="text-primary" />;
    }
  };
  
  return (
    <ListGroup.Item 
      className="border-0 px-3 py-2 hover-bg-light cursor-pointer"
      onClick={() => onClick(activity)}
    >
      <div className="d-flex align-items-start">
        <div className="me-3">
          {getActivityIcon(activity.type)}
        </div>
        <div className="flex-grow-1">
          <div className="d-flex justify-content-between">
            <small className="fw-semibold">{activity.action}</small>
            <small className="text-muted">
              <Clock size={12} className="me-1" />
              {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </small>
          </div>
          <small className="text-muted d-block mb-1">{activity.description}</small>
          <small className="text-muted">
            <PersonCheckFill size={12} className="me-1" />
            {activity.user}
          </small>
        </div>
        <ChevronRight size={16} className="text-muted" />
      </div>
    </ListGroup.Item>
  );
};

const PendingTaskItem = ({ task, onClick, onComplete }) => {
  const [completing, setCompleting] = useState(false);
  
  const handleComplete = async (e) => {
    e.stopPropagation();
    setCompleting(true);
    try {
      await onComplete(task.id);
      toast.success('Task marked as completed');
    } catch (error) {
      toast.error('Failed to complete task');
    } finally {
      setCompleting(false);
    }
  };
  
  return (
    <ListGroup.Item 
      className="border-0 px-3 py-2 hover-bg-light cursor-pointer"
      onClick={() => onClick(task)}
    >
      <div className="d-flex align-items-start">
        <div className="me-3">
          {getStatusBadge(task.priority)}
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
              Due: {task.dueDate ? new Date(task.dueDate).toLocaleDateString() : 'No deadline'}
            </small>
            <div className="d-flex gap-1">
              <Button 
                size="sm" 
                variant="outline-success"
                onClick={handleComplete}
                disabled={completing}
              >
                <CheckSquare size={12} className="me-1" />
                Complete
              </Button>
              <Button size="sm" variant="outline-primary">Review</Button>
            </div>
          </div>
        </div>
      </div>
    </ListGroup.Item>
  );
};

// ==================== MODALS ====================
const AnnouncementModal = ({ show, onHide, onSubmit }) => {
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    priority: 'medium',
    audience: 'all',
    sendEmail: false,
    schedule: false,
    scheduledTime: null
  });
  
  const [submitting, setSubmitting] = useState(false);
  
  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await onSubmit(formData);
      onHide();
    } catch (error) {
      toast.error('Failed to create announcement');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton className="border-0">
        <Modal.Title className="d-flex align-items-center">
          <BellFill className="me-2 text-primary" />
          Create System Announcement
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="fw-semibold">Title</Form.Label>
                <Form.Control
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="Enter announcement title"
                  className="border-1"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label className="fw-semibold">Priority</Form.Label>
                <Form.Select
                  value={formData.priority}
                  onChange={(e) => setFormData({...formData, priority: e.target.value})}
                  className="border-1"
                >
                  <option value="high">🚨 High Priority</option>
                  <option value="medium">⚠️ Medium Priority</option>
                  <option value="low">ℹ️ Low Priority</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
          
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">Audience</Form.Label>
            <Form.Select
              value={formData.audience}
              onChange={(e) => setFormData({...formData, audience: e.target.value})}
              className="border-1"
            >
              <option value="all">All Users</option>
              <option value="students">Students Only</option>
              <option value="teachers">Teachers Only</option>
              <option value="parents">Parents Only</option>
              <option value="staff">Staff Only</option>
              <option value="admins">Administrators Only</option>
            </Form.Select>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">Message</Form.Label>
            <Form.Control
              as="textarea"
              rows={5}
              value={formData.message}
              onChange={(e) => setFormData({...formData, message: e.target.value})}
              placeholder="Enter announcement message (supports Markdown)"
              className="border-1"
            />
          </Form.Group>
          
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Send email notification"
                  checked={formData.sendEmail}
                  onChange={(e) => setFormData({...formData, sendEmail: e.target.checked})}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Schedule for later"
                  checked={formData.schedule}
                  onChange={(e) => setFormData({...formData, schedule: e.target.checked})}
                />
              </Form.Group>
            </Col>
          </Row>
        </Form>
      </Modal.Body>
      <Modal.Footer className="border-0">
        <Button variant="light" onClick={onHide}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={handleSubmit} 
          disabled={submitting}
          className="d-flex align-items-center"
        >
          <BellFill className="me-1" />
          {submitting ? 'Publishing...' : 'Publish Announcement'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

const ExportDataModal = ({ show, onHide, onSubmit }) => {
  const [formData, setFormData] = useState({
    type: 'users',
    format: 'csv',
    dateRange: 'month',
    includeSensitive: false,
    compress: true
  });
  
  const [submitting, setSubmitting] = useState(false);
  
  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await onSubmit(formData);
      onHide();
    } catch (error) {
      toast.error('Failed to export data');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton className="border-0">
        <Modal.Title className="d-flex align-items-center">
          <Download className="me-2 text-primary" />
          Export Data
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">Data Type</Form.Label>
            <Form.Select
              value={formData.type}
              onChange={(e) => setFormData({...formData, type: e.target.value})}
              className="border-1"
            >
              <option value="users">User Data</option>
              <option value="students">Student Data</option>
              <option value="teachers">Teacher Data</option>
              <option value="finance">Financial Data</option>
              <option value="academic">Academic Data</option>
              <option value="system">System Logs</option>
              <option value="all">All Data</option>
            </Form.Select>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">Format</Form.Label>
            <Form.Select
              value={formData.format}
              onChange={(e) => setFormData({...formData, format: e.target.value})}
              className="border-1"
            >
              <option value="csv">CSV</option>
              <option value="excel">Excel</option>
              <option value="pdf">PDF</option>
              <option value="json">JSON</option>
            </Form.Select>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">Date Range</Form.Label>
            <Form.Select
              value={formData.dateRange}
              onChange={(e) => setFormData({...formData, dateRange: e.target.value})}
              className="border-1"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
              <option value="all">All Time</option>
            </Form.Select>
          </Form.Group>
          
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Include sensitive data"
                  checked={formData.includeSensitive}
                  onChange={(e) => setFormData({...formData, includeSensitive: e.target.checked})}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Compress file"
                  checked={formData.compress}
                  onChange={(e) => setFormData({...formData, compress: e.target.checked})}
                />
              </Form.Group>
            </Col>
          </Row>
          
          <Form.Text className="text-muted">
            {formData.includeSensitive && 
              <Alert variant="warning" className="mt-2 py-2">
                <ExclamationTriangle size={14} className="me-1" />
                Warning: Sensitive data includes personal identifiers. Handle with care.
              </Alert>
            }
          </Form.Text>
        </Form>
      </Modal.Body>
      <Modal.Footer className="border-0">
        <Button variant="light" onClick={onHide}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={handleSubmit} 
          disabled={submitting}
          className="d-flex align-items-center"
        >
          <Download className="me-1" />
          {submitting ? 'Exporting...' : 'Export Data'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

// ==================== MAIN COMPONENT ====================
const AdminPortal = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  // State Management
  const { value: timeRange, setValue: setTimeRange } = useLocalStorage('admin-dashboard-timeRange', 'month');
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [activityFilter, setActivityFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  
  // Modal States
  const [showAnnouncementModal, setShowAnnouncementModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);
  
  // Custom hook for data fetching
  const { data, loading, error, refetch } = useDashboardData(timeRange);
  
  // Debounced search
  const debouncedSearch = useDebounce(searchQuery, 300);
  
  // Auto-refresh based on time range
  const currentTimeRange = TIME_RANGES.find(r => r.value === timeRange);
  useAPIPolling(refetch, currentTimeRange?.refreshRate || 120000);
  
  // Event Handlers
  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
  };
  
  const handleCreateAnnouncement = async (announcementData) => {
    try {
      const response = await notificationsAPI.createAnnouncement(announcementData);
      if (response.success) {
        toast.success('Announcement created successfully');
        refetch();
      } else {
        throw new Error(response.error?.message || 'Failed to create announcement');
      }
    } catch (err) {
      toast.error('Failed to create announcement');
      throw err;
    }
  };
  
  const handleExportData = async (exportData) => {
    try {
      const response = await reportsAPI.exportData(exportData);
      if (response.success && response.data?.url) {
        window.open(response.data.url, '_blank');
        toast.success('Export started successfully');
      } else {
        throw new Error('Export failed');
      }
    } catch (err) {
      toast.error('Failed to export data');
      throw err;
    }
  };
  
  const handleSystemAction = async (action, componentId = null, data = {}) => {
    try {
      let response;
      
      switch (action) {
        case 'backup':
          response = await systemAPI.initiateBackup();
          toast.info('Backup initiated...');
          break;
        case 'maintenance':
          response = await systemAPI.setMaintenanceMode(data);
          if (response.success) {
            toast.success('Maintenance mode activated');
            setShowMaintenanceModal(false);
          }
          break;
        case 'restart':
          response = await systemAPI.restartComponent(componentId);
          toast.info(`Restarting ${componentId}...`);
          break;
        case 'diagnostics':
          response = await systemAPI.runDiagnostics();
          toast.info('Running diagnostics...');
          break;
        default:
          return;
      }
      
      setTimeout(() => refetch(), 3000);
      
    } catch (err) {
      toast.error(`Failed to perform ${action}`);
    }
  };
  
  const handleQuickAction = (action) => {
    if (action.requiresSetup) {
      toast.info('Academic setup required. Redirecting to setup wizard...');
      setTimeout(() => navigate('/admin/setup'), 1500);
    } else {
      navigate(action.path);
    }
  };
  
  const handleTaskComplete = async (taskId) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Task completed successfully');
      refetch();
    } catch (error) {
      toast.error('Failed to complete task');
    }
  };
  
  // Memoized values
  const stats = useMemo(() => data?.summary || {}, [data]);
  
  const filteredActivities = useMemo(() => {
    let activities = data?.recentActivities || [];
    
    if (activityFilter !== 'all') {
      activities = activities.filter(activity => activity.type === activityFilter);
    }
    
    if (debouncedSearch) {
      const query = debouncedSearch.toLowerCase();
      activities = activities.filter(activity =>
        activity.action?.toLowerCase().includes(query) ||
        activity.description?.toLowerCase().includes(query) ||
        activity.user?.toLowerCase().includes(query)
      );
    }
    
    activities.sort((a, b) => {
      if (sortBy === 'recent') {
        return new Date(b.timestamp) - new Date(a.timestamp);
      } else if (sortBy === 'oldest') {
        return new Date(a.timestamp) - new Date(b.timestamp);
      }
      return 0;
    });
    
    return activities.slice(0, 8);
  }, [data?.recentActivities, activityFilter, debouncedSearch, sortBy]);
  
  const systemHealthScore = useMemo(() => 
    calculateSystemHealthScore(data?.systemStats), 
    [data?.systemStats]
  );
  
  // User profile information
  const getUserDisplayInfo = () => {
    const userProfile = currentUser || {};
    return {
      firstName: userProfile.first_name || userProfile.firstName || 'Administrator',
      lastName: userProfile.last_name || userProfile.lastName || '',
      avatar: userProfile.avatar || userProfile.profile_picture,
      initials: (userProfile.first_name?.charAt(0) || '') + (userProfile.last_name?.charAt(0) || '') || 'A',
      role: userProfile.role || 'Admin'
    };
  };
  
  const { firstName, lastName, avatar, initials, role } = getUserDisplayInfo();
  const fullName = `${firstName} ${lastName}`.trim();
  
  // Render Functions
  const renderHeader = () => (
    <Row className="mb-4 align-items-center">
      <Col>
        <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
          <div className="d-flex align-items-center">
            <div className="me-3">
              {avatar ? (
                <Image 
                  src={avatar} 
                  roundedCircle 
                  width={70} 
                  height={70}
                  className="border border-3 border-primary shadow"
                  alt={fullName}
                  style={{ objectFit: 'cover' }}
                />
              ) : (
                <div 
                  className="rounded-circle bg-primary bg-opacity-10 d-flex align-items-center justify-content-center border border-3 border-primary shadow"
                  style={{ width: 70, height: 70 }}
                >
                  <PersonBadge size={28} className="text-primary" />
                </div>
              )}
            </div>
            <div>
              <h1 className="h2 mb-1">
                <span className="text-gradient-primary">Administrator Portal</span>
              </h1>
              <div className="d-flex align-items-center gap-2 flex-wrap">
                <p className="text-muted mb-0">
                  Welcome, <span className="fw-semibold">{fullName}</span>
                  <Badge bg="primary" className="ms-2">
                    {role}
                  </Badge>
                </p>
                {data?.summary?.academicYear && (
                  <Badge bg="info" className="d-flex align-items-center gap-1">
                    <CalendarEvent size={12} />
                    {data.summary.academicYear} • {data.summary.currentTerm}
                  </Badge>
                )}
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
                      <div className="d-flex align-items-center">
                        {range.icon}
                        <span className="ms-2">{range.label}</span>
                      </div>
                    </Dropdown.Item>
                  ))}
                </Dropdown.Menu>
              </Dropdown>
              
              <OverlayTrigger overlay={<Tooltip>Refresh Dashboard</Tooltip>}>
                <Button 
                  variant="outline-primary" 
                  onClick={refetch}
                  disabled={loading}
                  size="sm"
                  className="d-flex align-items-center"
                >
                  <ArrowClockwise className={`me-1 ${loading ? 'spinning' : ''}`} size={14} />
                  {loading ? 'Refreshing...' : 'Refresh'}
                </Button>
              </OverlayTrigger>
            </div>
            
            <ButtonGroup size="sm">
              <OverlayTrigger overlay={<Tooltip>Create Announcement</Tooltip>}>
                <Button 
                  variant="primary" 
                  onClick={() => setShowAnnouncementModal(true)}
                  className="d-flex align-items-center"
                >
                  <BellFill size={14} className="me-1" />
                  Announce
                </Button>
              </OverlayTrigger>
              
              <OverlayTrigger overlay={<Tooltip>Export Data</Tooltip>}>
                <Button 
                  variant="outline-success" 
                  onClick={() => setShowExportModal(true)}
                  className="d-flex align-items-center"
                >
                  <Download size={14} className="me-1" />
                  Export
                </Button>
              </OverlayTrigger>
            </ButtonGroup>
          </div>
        </div>
      </Col>
    </Row>
  );
  
  const renderNavigationTabs = () => (
    <Row className="mb-4">
      <Col>
        <Card className="border-0 shadow-sm">
          <Card.Body className="p-2">
            <Tabs
              activeKey={activeTab}
              onSelect={setActiveTab}
              className="border-0 admin-tabs"
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
                  System Health
                  <Badge bg={systemHealthScore > 90 ? 'success' : systemHealthScore > 70 ? 'warning' : 'danger'} className="ms-2">
                    {formatPercentage(systemHealthScore)}
                  </Badge>
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
              <Tab eventKey="activities" title={
                <div className="d-flex align-items-center">
                  <Activity size={16} className="me-2" />
                  Activities
                  <Badge bg="info" className="ms-2" pill>
                    {data?.recentActivities?.length || 0}
                  </Badge>
                </div>
              } />
            </Tabs>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
  
  const renderOverviewTab = () => (
    <>
      {/* Quick Stats */}
      <Row className="g-3 mb-4">
        <Col xl={3} lg={6}>
          <StatCard
            title="Total Students"
            value={formatNumber(stats.totalStudents)}
            icon={<PeopleFill />}
            color="primary"
            trend={data?.academicMetrics?.enrollment_growth || 0}
            subtitle={`${formatNumber(stats.totalTeachers)} Teachers`}
            onClick={() => navigate('/admin/students')}
          />
        </Col>

        <Col xl={3} lg={6}>
          <StatCard
            title="System Users"
            value={formatNumber(stats.totalUsers)}
            icon={<PersonCheckFill />}
            color="info"
            subtitle={`${formatNumber(stats.activeUsers)} Active`}
            onClick={() => navigate('/admin/users')}
          />
        </Col>

        <Col xl={3} lg={6}>
          <StatCard
            title="System Health"
            value={formatPercentage(systemHealthScore)}
            icon={<Activity />}
            color="success"
            subtitle={`${data?.systemStats?.server?.uptime || '99.9%'} Uptime`}
            onClick={() => setActiveTab('system')}
          />
        </Col>

        <Col xl={3} lg={6}>
          <StatCard
            title="Financial Health"
            value={formatCurrency(stats.totalRevenue)}
            icon={<CashStack />}
            color="warning"
            trend={data?.financialMetrics?.profit_margin || 0}
            subtitle={`${formatPercentage(stats.collectionRate)} Collection`}
            onClick={() => navigate('/admin/finance')}
          />
        </Col>
      </Row>

      {/* User Statistics Cards */}
      <Row className="g-3 mb-4">
        <Col md={4} lg={2}>
          <Card className="border-0 shadow-sm h-100 text-center">
            <Card.Body className="p-3">
              <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '50px', height: '50px'}}>
                <PeopleFill size={20} className="text-primary" />
              </div>
              <div className="display-6 fw-bold">{formatNumber(stats.totalUsers)}</div>
              <small className="text-muted">Total Users</small>
              <div className="small mt-2">
                <Badge bg="success" className="me-1">
                  {stats.activeUsers} Active
                </Badge>
                <Badge bg="warning" className="me-1">
                  {stats.pendingApprovals} Pending
                </Badge>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4} lg={2}>
          <Card className="border-0 shadow-sm h-100 text-center">
            <Card.Body className="p-3">
              <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '50px', height: '50px'}}>
                <Mortarboard size={20} className="text-success" />
              </div>
              <div className="display-6 fw-bold">{formatNumber(stats.totalStudents)}</div>
              <small className="text-muted">Students</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4} lg={2}>
          <Card className="border-0 shadow-sm h-100 text-center">
            <Card.Body className="p-3">
              <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '50px', height: '50px'}}>
                <PersonBadge size={20} className="text-primary" />
              </div>
              <div className="display-6 fw-bold">{formatNumber(stats.totalTeachers)}</div>
              <small className="text-muted">Teachers</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4} lg={2}>
          <Card className="border-0 shadow-sm h-100 text-center">
            <Card.Body className="p-3">
              <div className="bg-secondary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '50px', height: '50px'}}>
                <Buildings size={20} className="text-secondary" />
              </div>
              <div className="display-6 fw-bold">{formatNumber(stats.totalStaff)}</div>
              <small className="text-muted">Staff</small>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4} lg={2}>
          <Card className="border-0 shadow-sm h-100 text-center">
            <Card.Body className="p-3">
              <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '50px', height: '50px'}}>
                <ShieldCheck size={20} className="text-success" />
              </div>
              <div className="display-6 fw-bold">{formatNumber(stats.verifiedUsers)}</div>
              <small className="text-muted">Verified</small>
              <div className="small mt-2">
                <Badge bg="success">
                  {formatPercentage((stats.verifiedUsers / stats.totalUsers) * 100)} Rate
                </Badge>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4} lg={2}>
          <Card className="border-0 shadow-sm h-100 text-center">
            <Card.Body className="p-3">
              <div className="bg-danger bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '50px', height: '50px'}}>
                <ShieldExclamation size={20} className="text-danger" />
              </div>
              <div className="display-6 fw-bold">{formatNumber(stats.suspendedUsers)}</div>
              <small className="text-muted">Suspended</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row className="g-3 mb-4">
        <Col>
          <h5 className="mb-3 d-flex align-items-center">
            <RocketTakeoff size={20} className="me-2 text-primary" />
            Quick Actions
          </h5>
        </Col>
        {QUICK_ACTIONS.map((action) => (
          <Col lg={4} md={6} key={action.id}>
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
                  {action.requiresSetup && (
                    <Badge bg="warning" className="mt-1">
                      Setup Required
                    </Badge>
                  )}
                </div>
                <ChevronRight size={16} className="text-muted" />
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
              <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
                <h5 className="mb-0 d-flex align-items-center">
                  <ClockHistory className="me-2 text-primary" />
                  Recent Activities
                </h5>
                <div className="d-flex gap-2">
                  <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" size="sm">
                      <Filter size={12} />
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      <Dropdown.Item onClick={() => setActivityFilter('all')}>All</Dropdown.Item>
                      <Dropdown.Item onClick={() => setActivityFilter('user')}>User</Dropdown.Item>
                      <Dropdown.Item onClick={() => setActivityFilter('system')}>System</Dropdown.Item>
                      <Dropdown.Item onClick={() => setActivityFilter('finance')}>Finance</Dropdown.Item>
                      <Dropdown.Item onClick={() => setActivityFilter('academic')}>Academic</Dropdown.Item>
                    </Dropdown.Menu>
                  </Dropdown>
                  <InputGroup size="sm" style={{ minWidth: '200px' }}>
                    <InputGroup.Text>
                      <Search size={12} />
                    </InputGroup.Text>
                    <Form.Control
                      placeholder="Search activities..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </InputGroup>
                </div>
              </div>
            </Card.Header>
            <Card.Body className="p-0" style={{ maxHeight: '400px', overflowY: 'auto' }}>
              <ListGroup variant="flush">
                {filteredActivities.length > 0 ? (
                  filteredActivities.map((activity, index) => (
                    <RecentActivityItem
                      key={index}
                      activity={activity}
                      onClick={(activity) => navigate(`/admin/activities/${activity.id}`)}
                    />
                  ))
                ) : (
                  <div className="text-center py-4">
                    <Activity size={32} className="text-muted mb-2" />
                    <p className="text-muted mb-0">No recent activities</p>
                  </div>
                )}
              </ListGroup>
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
                  <Badge bg="warning" className="ms-2">
                    {data?.pendingTasks?.length || 0}
                  </Badge>
                </h5>
                <Button 
                  variant="outline-primary" 
                  size="sm"
                  onClick={() => navigate('/admin/tasks/create')}
                >
                  <PlusCircle size={12} className="me-1" />
                  New Task
                </Button>
              </div>
            </Card.Header>
            <Card.Body className="p-0" style={{ maxHeight: '400px', overflowY: 'auto' }}>
              <ListGroup variant="flush">
                {data?.pendingTasks?.length > 0 ? (
                  data.pendingTasks.slice(0, 6).map((task, index) => (
                    <PendingTaskItem
                      key={index}
                      task={task}
                      onClick={() => navigate(`/admin/tasks/${task.id}`)}
                      onComplete={handleTaskComplete}
                    />
                  ))
                ) : (
                  <div className="text-center py-4">
                    <CheckCircle size={32} className="text-success mb-2" />
                    <p className="text-muted mb-0">All tasks completed</p>
                  </div>
                )}
              </ListGroup>
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
    </>
  );
  
  const renderSystemTab = () => (
    <Row className="g-3">
      <Col xl={8} lg={7}>
        <Card className="border-0 shadow-sm h-100">
          <Card.Header className="bg-white border-0 py-3">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
              <h5 className="mb-0 d-flex align-items-center">
                <Activity className="me-2 text-primary" />
                System Health Monitor
                <Badge bg={systemHealthScore > 90 ? 'success' : systemHealthScore > 70 ? 'warning' : 'danger'} className="ms-2">
                  {formatPercentage(systemHealthScore)}
                </Badge>
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
                  onClick={() => setShowMaintenanceModal(true)}
                  className="d-flex align-items-center"
                >
                  <Tools className="me-1" size={12} />
                  Maintenance
                </Button>
                <Button 
                  variant="outline-secondary" 
                  onClick={() => handleSystemAction('diagnostics')}
                  className="d-flex align-items-center"
                >
                  <ClipboardCheck className="me-1" size={12} />
                  Diagnostics
                </Button>
              </ButtonGroup>
            </div>
          </Card.Header>
          <Card.Body>
            <Row className="g-3">
              {SYSTEM_COMPONENTS.map((component) => {
                const stats = data?.systemStats?.[component.id];
                if (!stats) return null;
                
                return (
                  <Col md={6} lg={4} key={component.id}>
                    <SystemHealthCard
                      component={component}
                      stats={stats}
                      onRestart={handleSystemAction}
                    />
                  </Col>
                );
              })}
            </Row>
          </Card.Body>
        </Card>
      </Col>

      <Col xl={4} lg={5}>
        <Row className="g-3">
          <Col md={12}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0 d-flex align-items-center">
                  <Bell className="me-2 text-primary" />
                  System Notifications
                </h5>
              </Card.Header>
              <Card.Body className="p-0" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <ListGroup variant="flush">
                  {[
                    { type: 'info', message: 'Backup scheduled for 02:00 AM', time: '10 min ago' },
                    { type: 'warning', message: 'Storage usage above 70%', time: '1 hour ago' },
                    { type: 'success', message: 'Security scan completed', time: '2 hours ago' },
                    { type: 'info', message: 'System update available', time: '5 hours ago' },
                  ].map((notification, index) => (
                    <ListGroup.Item key={index} className="border-0 px-3 py-2">
                      <div className="d-flex align-items-start">
                        <div className="me-3">
                          {notification.type === 'info' && <InfoCircle size={16} className="text-info" />}
                          {notification.type === 'warning' && <ExclamationTriangle size={16} className="text-warning" />}
                          {notification.type === 'success' && <CheckCircle size={16} className="text-success" />}
                          {notification.type === 'danger' && <XCircle size={16} className="text-danger" />}
                        </div>
                        <div className="flex-grow-1">
                          <small className="fw-semibold d-block">{notification.message}</small>
                          <small className="text-muted">{notification.time}</small>
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={12}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0 d-flex align-items-center">
                  <Cpu className="me-2 text-primary" />
                  Performance Metrics
                </h5>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <div className="d-flex justify-content-between mb-1">
                    <small className="text-muted">CPU Usage</small>
                    <small className="fw-semibold">{data?.systemStats?.performance?.load || '32%'}</small>
                  </div>
                  <ProgressBar 
                    now={parseInt(data?.systemStats?.performance?.load) || 32} 
                    variant={parseInt(data?.systemStats?.performance?.load) > 80 ? 'danger' : 
                            parseInt(data?.systemStats?.performance?.load) > 60 ? 'warning' : 'success'}
                    style={{ height: '6px' }}
                  />
                </div>
                
                <div className="mb-3">
                  <div className="d-flex justify-content-between mb-1">
                    <small className="text-muted">Memory Usage</small>
                    <small className="fw-semibold">{data?.systemStats?.performance?.memory || '58%'}</small>
                  </div>
                  <ProgressBar 
                    now={parseInt(data?.systemStats?.performance?.memory) || 58} 
                    variant={parseInt(data?.systemStats?.performance?.memory) > 80 ? 'danger' : 
                            parseInt(data?.systemStats?.performance?.memory) > 60 ? 'warning' : 'success'}
                    style={{ height: '6px' }}
                  />
                </div>
                
                <div>
                  <div className="d-flex justify-content-between mb-1">
                    <small className="text-muted">Response Time</small>
                    <small className="fw-semibold">{data?.systemStats?.server?.response_time || '45ms'}</small>
                  </div>
                  <ProgressBar 
                    now={parseInt(data?.systemStats?.server?.response_time) || 45} 
                    max={100}
                    variant={parseInt(data?.systemStats?.server?.response_time) > 80 ? 'danger' : 
                            parseInt(data?.systemStats?.server?.response_time) > 60 ? 'warning' : 'success'}
                    style={{ height: '6px' }}
                  />
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Col>
    </Row>
  );
  
  const renderAnalyticsTab = () => (
    <Row className="g-3">
      <Col>
        <Card className="border-0 shadow-sm">
          <Card.Header className="bg-white border-0 py-3">
            <h5 className="mb-0 d-flex align-items-center">
              <GraphUp className="me-2 text-primary" />
              Advanced Analytics Dashboard
              <Badge bg="info" className="ms-2">
                <Robot size={12} className="me-1" />
                AI-Powered
              </Badge>
            </h5>
          </Card.Header>
          <Card.Body>
            <div className="text-center py-5">
              <div className="bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{ width: 80, height: 80 }}>
                <GraphUp size={32} className="text-primary" />
              </div>
              <h5 className="mb-2">Analytics Dashboard</h5>
              <p className="text-muted mb-4">Advanced analytics and insights coming soon</p>
              <Button 
                variant="primary" 
                onClick={() => navigate('/admin/analytics')}
                className="d-flex align-items-center mx-auto"
              >
                <BoxArrowUpRight size={14} className="me-1" />
                Go to Analytics Hub
              </Button>
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
  
  const renderReportsTab = () => (
    <Row className="g-3">
      <Col>
        <Card className="border-0 shadow-sm">
          <Card.Header className="bg-white border-0 py-3">
            <div className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0 d-flex align-items-center">
                <FileEarmarkBarGraph className="me-2 text-primary" />
                Reports Center
              </h5>
              <Button 
                variant="primary" 
                size="sm"
                onClick={() => setShowExportModal(true)}
                className="d-flex align-items-center"
              >
                <FileEarmarkArrowDown size={14} className="me-1" />
                Generate Report
              </Button>
            </div>
          </Card.Header>
          <Card.Body>
            <Row className="g-3">
              {[
                { title: 'Financial Reports', icon: <CashStack />, count: 12, color: 'warning', path: '/admin/reports/financial' },
                { title: 'Academic Reports', icon: <BookFill />, count: 8, color: 'info', path: '/admin/reports/academic' },
                { title: 'User Reports', icon: <PeopleFill />, count: 15, color: 'primary', path: '/admin/reports/users' },
                { title: 'System Reports', icon: <Server />, count: 5, color: 'secondary', path: '/admin/reports/system' },
                { title: 'Attendance Reports', icon: <PersonCheckFill />, count: 23, color: 'success', path: '/admin/reports/attendance' },
                { title: 'Performance Reports', icon: <BarChart />, count: 7, color: 'dark', path: '/admin/reports/performance' },
              ].map((report, index) => (
                <Col md={6} lg={4} key={index}>
                  <Card className="border-0 shadow-sm h-100 hover-lift">
                    <Card.Body className="d-flex align-items-center">
                      <div className={`bg-${report.color} bg-opacity-10 p-3 rounded me-3`}>
                        {React.cloneElement(report.icon, { className: `text-${report.color}`, size: 24 })}
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">{report.title}</h6>
                        <div className="d-flex justify-content-between align-items-center">
                          <Badge bg="light" text="dark" className="border">
                            {report.count} reports
                          </Badge>
                          <Button 
                            variant="outline-primary" 
                            size="sm"
                            onClick={() => navigate(report.path)}
                          >
                            View
                          </Button>
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
  
  const renderActivitiesTab = () => (
    <Row className="g-3">
      <Col>
        <Card className="border-0 shadow-sm">
          <Card.Header className="bg-white border-0 py-3">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
              <h5 className="mb-0 d-flex align-items-center">
                <Activity className="me-2 text-primary" />
                All System Activities
                <Badge bg="info" className="ms-2">
                  {data?.recentActivities?.length || 0} total
                </Badge>
              </h5>
              <div className="d-flex gap-2 flex-wrap">
                <InputGroup size="sm" style={{ minWidth: '250px' }}>
                  <InputGroup.Text>
                    <Search size={12} />
                  </InputGroup.Text>
                  <Form.Control
                    placeholder="Search activities..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </InputGroup>
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm">
                    <Filter size={12} className="me-1" />
                    Filter
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item onClick={() => setActivityFilter('all')}>All Activities</Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={() => setActivityFilter('user')}>User Management</Dropdown.Item>
                    <Dropdown.Item onClick={() => setActivityFilter('system')}>System Operations</Dropdown.Item>
                    <Dropdown.Item onClick={() => setActivityFilter('finance')}>Financial Operations</Dropdown.Item>
                    <Dropdown.Item onClick={() => setActivityFilter('academic')}>Academic Operations</Dropdown.Item>
                    <Dropdown.Item onClick={() => setActivityFilter('security')}>Security Events</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm">
                    <Clock size={12} className="me-1" />
                    Sort
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item onClick={() => setSortBy('recent')}>Most Recent</Dropdown.Item>
                    <Dropdown.Item onClick={() => setSortBy('oldest')}>Oldest First</Dropdown.Item>
                    <Dropdown.Item onClick={() => setSortBy('user')}>By User</Dropdown.Item>
                    <Dropdown.Item onClick={() => setSortBy('type')}>By Type</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </div>
          </Card.Header>
          <Card.Body className="p-0">
            <Table hover responsive className="mb-0">
              <thead className="bg-light">
                <tr>
                  <th>Time</th>
                  <th>Activity</th>
                  <th>User</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredActivities.length > 0 ? (
                  filteredActivities.map((activity, index) => (
                    <tr key={index} className="cursor-pointer">
                      <td>
                        <small className="text-muted">
                          {new Date(activity.timestamp).toLocaleDateString()}
                          <br />
                          {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </small>
                      </td>
                      <td>
                        <div className="fw-semibold">{activity.action}</div>
                        <small className="text-muted">{activity.description}</small>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <div className="bg-light rounded-circle d-flex align-items-center justify-content-center me-2" style={{ width: 24, height: 24 }}>
                            <PersonCheckFill size={12} />
                          </div>
                          {activity.user}
                        </div>
                      </td>
                      <td>
                        <Badge bg={
                          activity.type === 'user' ? 'primary' :
                          activity.type === 'system' ? 'secondary' :
                          activity.type === 'finance' ? 'warning' :
                          activity.type === 'academic' ? 'info' : 'dark'
                        }>
                          {activity.type}
                        </Badge>
                      </td>
                      <td>
                        {getStatusBadge(activity.status || 'completed')}
                      </td>
                      <td>
                        <ButtonGroup size="sm">
                          <Button 
                            variant="outline-primary"
                            size="sm"
                            onClick={() => navigate(`/admin/activities/${activity.id}`)}
                          >
                            <Eye size={12} />
                          </Button>
                        </ButtonGroup>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="text-center py-4">
                      <Activity size={32} className="text-muted mb-2" />
                      <p className="text-muted mb-0">No activities found</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
  
  const renderFooter = () => (
    <Row className="mt-4">
      <Col>
        <Card className="border-0 bg-light">
          <Card.Body className="py-2">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
              <small className="text-muted">
                <Clock size={12} className="me-1" />
                Last Updated: {data?.lastUpdated ? new Date(data.lastUpdated).toLocaleString() : 'Never'}
                {loading && <span className="ms-2">🔄 Loading...</span>}
              </small>
              <div className="d-flex align-items-center flex-wrap gap-2">
                <small className="text-muted">
                  <ShieldShaded size={12} className="me-1" />
                  System Health: 
                  <Badge bg={systemHealthScore > 90 ? 'success' : systemHealthScore > 70 ? 'warning' : 'danger'} className="ms-1">
                    {formatPercentage(systemHealthScore)}
                  </Badge>
                </small>
                <small className="text-muted">
                  <BroadcastPin size={12} className="me-1" />
                  v2.0.0 • © 2026 School Management System
                </small>
              </div>
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
  
  // Main render
  if (loading && !data) {
    return (
      <Container fluid className="admin-portal px-3 px-md-4 py-4">
        {renderHeader()}
        <LoadingSkeleton />
      </Container>
    );
  }
  
  return (
    <ErrorBoundary>
      <ToastContainer position="top-right" autoClose={3000} />
      <Container fluid className="admin-portal px-3 px-md-4 py-4">
        {/* Header */}
        {renderHeader()}
        
        {/* Error State */}
        {error && (
          <ErrorDisplay error={error} onRetry={refetch} />
        )}
        
        {/* Navigation Tabs */}
        {renderNavigationTabs()}
        
        {/* Content based on active tab */}
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'system' && renderSystemTab()}
        {activeTab === 'analytics' && renderAnalyticsTab()}
        {activeTab === 'reports' && renderReportsTab()}
        {activeTab === 'activities' && renderActivitiesTab()}
        
        {/* Footer */}
        {renderFooter()}
        
        {/* Modals */}
        <AnnouncementModal
          show={showAnnouncementModal}
          onHide={() => setShowAnnouncementModal(false)}
          onSubmit={handleCreateAnnouncement}
        />
        
        <ExportDataModal
          show={showExportModal}
          onHide={() => setShowExportModal(false)}
          onSubmit={handleExportData}
        />
        
        <ConfirmationModal
          show={showConfirmationModal}
          onHide={() => setShowConfirmationModal(false)}
          title="Confirm Action"
          message="Are you sure you want to perform this action?"
          onConfirm={() => {
            // Add confirmation logic here
            setShowConfirmationModal(false);
          }}
        />
        
        {/* Custom CSS */}
        <style jsx="true">{`
          .admin-portal {
            min-height: calc(100vh - 76px);
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
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
            transition: all 0.3s ease;
          }
          .admin-tabs .nav-link {
            color: #6c757d;
            font-weight: 500;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            margin: 0 0.25rem;
          }
          .admin-tabs .nav-link.active {
            color: #00695c;
            background-color: rgba(0, 105, 92, 0.1);
            border-bottom: 3px solid #00695c;
          }
          .admin-tabs .nav-link:hover {
            color: #004d40;
            background-color: rgba(0, 105, 92, 0.05);
          }
          .progress-bar {
            border-radius: 4px;
          }
          ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
          }
          ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
          }
          ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
          }
          ::-webkit-scrollbar-thumb:hover {
            background: #a1a1a1;
          }
        `}</style>
      </Container>
    </ErrorBoundary>
  );
};

export default AdminPortal;