import React, { useState, useEffect, useCallback, useMemo } from 'react';
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
  Modal,
  Form,
  InputGroup,
  Dropdown,
  DropdownButton,
  Accordion,
  Carousel,
  OverlayTrigger,
  Tooltip,
  Popover,
  Pagination
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

// Import Bootstrap icons in batches to avoid issues
import { 
  // IT Icons
  Cpu,
  Hdd,
  Memory,
  Motherboard,
  DeviceHdd,
  DeviceSsd,
  Display,
  Pc,
  PcDisplay,
  PcHorizontal,
  Laptop,
  Phone,
  Tablet,
  Router,
  Wifi,
  Ethernet,
  Signal,
  Cloud,
  CloudArrowDown,
  CloudArrowUp,
  CloudCheck,
  Database,
  DatabaseAdd,
  DatabaseCheck,
  DatabaseFill,
  DatabaseGear,
  DatabaseLock,
  Server,
  HddNetwork,
  HddRack,
  // Security Icons
  Shield,
  ShieldCheck,
  ShieldLock,
  ShieldFillCheck,
  ShieldFill,
  ShieldSlash,
  ShieldExclamation,
  // Network Icons
  Globe,
  Wifi1,
  Wifi2,
  WifiOff,
  RouterFill,
  // Device Icons
  DeviceHddFill,
  DeviceSsdFill,
  PcDisplayHorizontal,
  // Tools
  Tools,
  Wrench,
  WrenchAdjustable,
  Screwdriver,
  Hammer,
  Gear,
  GearFill,
  GearWide,
  GearWideConnected,
  // Status
  CheckCircle,
  CheckCircleFill,
  XCircle,
  XCircleFill,
  ExclamationCircle,
  ExclamationCircleFill,
  QuestionCircle,
  QuestionCircleFill,
  InfoCircle,
  InfoCircleFill,
  // Arrows
  ArrowClockwise,
  ArrowRepeat,
  ArrowCounterclockwise,
  // Actions
  Download,
  Upload,
  CloudDownload,
  CloudUpload,
  Power,
  Plug,
  // People
  Person,
  People,
  PersonBadge,
  PersonCheck,
  PersonDash,
  PersonX,
  // Files
  FileEarmark,
  FileEarmarkBinary,
  FileEarmarkCode,
  FileEarmarkZip,
  FileEarmarkLock,
  FileEarmarkCheck,
  FileEarmarkExcel,
  FileEarmarkText,
  FileEarmarkPdf,
  // Search
  Search,
  Filter,
  Funnel,
  SortDown,
  SortUp,
  // View
  Eye,
  EyeFill,
  EyeSlash,
  EyeSlashFill,
  // Edit
  Pencil,
  PencilFill,
  PencilSquare,
  // Delete
  Trash,
  TrashFill,
  // Add
  Plus,
  PlusCircle,
  PlusSquare,
  // Remove
  Dash,
  DashCircle,
  DashSquare,
  // Time
  Clock,
  ClockHistory,
  Stopwatch,
  StopwatchFill,
  // Calendar
  Calendar,
  CalendarEvent,
  CalendarWeek,
  CalendarMonth,
  CalendarCheck,
  CalendarX,
  // Notification
  Bell,
  BellFill,
  BellSlash,
  BellSlashFill,
  // Communication
  Envelope,
  EnvelopeFill,
  Chat,
  ChatFill,
  ChatLeft,
  ChatLeftFill,
  ChatRight,
  ChatRightFill,
  // Navigation
  House,
  HouseFill,
  Speedometer,
  Speedometer2,
  GraphUp,
  GraphDown,
  BarChart,
  BarChartFill,
  PieChart,
  PieChartFill,
  Activity,
  // Miscellaneous
  Key,
  KeyFill,
  Lock,
  LockFill,
  Unlock,
  UnlockFill,
  Archive,
  ArchiveFill,
  BoxArrowRight,
  BoxArrowLeft,
  BoxArrowUp,
  BoxArrowDown,
  Printer,
  Share,
  Save,
  SaveFill,
  Clipboard,
  ClipboardCheck,
  ClipboardData,
  Bookmark,
  BookmarkFill,
  Star,
  StarFill,
  Heart,
  HeartFill,
  Flag,
  FlagFill,
  Award,
  AwardFill,
  Trophy,
  TrophyFill,
  Calculator,
  CalculatorFill,
  Percent
} from 'react-bootstrap-icons';

// Import any missing icons separately if needed


import  {itAPI}  from '../../services/itAPI';

// Utility Functions
const formatNumber = (number) => {
  return new Intl.NumberFormat('en-KE').format(number || 0);
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
};

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getStatusBadge = (status) => {
  const variants = {
    'online': 'success',
    'offline': 'danger',
    'maintenance': 'warning',
    'active': 'success',
    'inactive': 'secondary',
    'pending': 'warning',
    'resolved': 'success',
    'open': 'danger',
    'in-progress': 'info',
    'high': 'danger',
    'medium': 'warning',
    'low': 'info',
    'critical': 'dark',
    'operational': 'success',
    'degraded': 'warning',
    'down': 'danger'
  };
  return variants[status] || 'secondary';
};

const ITPortal = () => {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [lastRefreshTime, setLastRefreshTime] = useState(Date.now());
  
  // IT Statistics
  const [itStats, setItStats] = useState({
    totalDevices: 0,
    onlineDevices: 0,
    offlineDevices: 0,
    pendingTickets: 0,
    resolvedTickets: 0,
    networkUptime: 0,
    serverHealth: 0,
    securityAlerts: 0
  });
  
  const [userProfile, setUserProfile] = useState(null);
  
  // Data states
  const [devices, setDevices] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [servers, setServers] = useState([]);
  const [networkDevices, setNetworkDevices] = useState([]);
  const [softwareLicenses, setSoftwareLicenses] = useState([]);
  const [securityAlerts, setSecurityAlerts] = useState([]);
  const [backupStatus, setBackupStatus] = useState([]);
  const [systemLogs, setSystemLogs] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [users, setUsers] = useState([]);
  const [monitoring, setMonitoring] = useState([]);
  
  // Filter states
  const [filters, setFilters] = useState({
    status: 'all',
    category: 'all',
    priority: 'all',
    location: 'all'
  });
  
  // Modal states
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [showDeviceModal, setShowDeviceModal] = useState(false);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Form states
  const [ticketForm, setTicketForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: 'hardware',
    assigned_to: '',
    device_id: ''
  });
  
  const [deviceForm, setDeviceForm] = useState({
    name: '',
    type: 'computer',
    serial_number: '',
    mac_address: '',
    ip_address: '',
    location: '',
    assigned_to: '',
    status: 'active',
    specifications: ''
  });

  // Clear messages
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        if (error) setError('');
        if (success) setSuccess('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  // Fetch IT data
  const fetchITData = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');

      // Get user profile
      const userResponse = await itAPI.getCurrentUser();
      if (userResponse.success) {
        setUserProfile(userResponse.user || userResponse.data);
      }

      // Fetch all IT data in parallel
      const [
        statsResponse,
        devicesResponse,
        ticketsResponse,
        serversResponse,
        networkResponse,
        securityResponse,
        backupResponse
      ] = await Promise.all([
        itAPI.getITStats(),
        itAPI.getDevices(),
        itAPI.getTickets(),
        itAPI.getServers(),
        itAPI.getNetworkDevices(),
        itAPI.getSecurityAlerts(),
        itAPI.getBackupStatus()
      ]);

      // Process responses
      if (statsResponse.success) setItStats(statsResponse.data);
      if (devicesResponse.success) setDevices(devicesResponse.data?.devices || devicesResponse.data || []);
      if (ticketsResponse.success) setTickets(ticketsResponse.data?.tickets || ticketsResponse.data || []);
      if (serversResponse.success) setServers(serversResponse.data?.servers || serversResponse.data || []);
      if (networkResponse.success) setNetworkDevices(networkResponse.data?.devices || networkResponse.data || []);
      if (securityResponse.success) setSecurityAlerts(securityResponse.data?.alerts || securityResponse.data || []);
      if (backupResponse.success) setBackupStatus(backupResponse.data?.backups || backupResponse.data || []);

      setLastRefreshTime(Date.now());

    } catch (err) {
      console.error('Error fetching IT data:', err);
      setError('Failed to load IT data. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading && currentUser) {
      fetchITData();
    }
  }, [authLoading, currentUser, fetchITData]);

  // Refresh function
  const handleRefresh = () => {
    fetchITData(true);
  };

  // Create ticket
  const handleCreateTicket = async () => {
    try {
      setLoading(true);
      const result = await itAPI.createTicket(ticketForm);
      
      if (result.success) {
        setSuccess('Ticket created successfully!');
        setShowTicketModal(false);
        setTicketForm({
          title: '',
          description: '',
          priority: 'medium',
          category: 'hardware',
          assigned_to: '',
          device_id: ''
        });
        fetchITData();
      } else {
        setError(result.error?.message || 'Failed to create ticket');
      }
    } catch (err) {
      setError('Failed to create ticket');
    } finally {
      setLoading(false);
    }
  };

  // Register device
  const handleRegisterDevice = async () => {
    try {
      setLoading(true);
      const result = await itAPI.registerDevice(deviceForm);
      
      if (result.success) {
        setSuccess('Device registered successfully!');
        setShowDeviceModal(false);
        setDeviceForm({
          name: '',
          type: 'computer',
          serial_number: '',
          mac_address: '',
          ip_address: '',
          location: '',
          assigned_to: '',
          status: 'active',
          specifications: ''
        });
        fetchITData();
      } else {
        setError(result.error?.message || 'Failed to register device');
      }
    } catch (err) {
      setError('Failed to register device');
    } finally {
      setLoading(false);
    }
  };

  // Resolve alert
  const handleResolveAlert = async (alertId) => {
    try {
      setLoading(true);
      const result = await itAPI.resolveAlert(alertId);
      
      if (result.success) {
        setSuccess('Alert resolved!');
        setSecurityAlerts(prev => prev.filter(alert => alert.id !== alertId));
      } else {
        setError(result.error?.message || 'Failed to resolve alert');
      }
    } catch (err) {
      setError('Failed to resolve alert');
    } finally {
      setLoading(false);
    }
  };

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  // Filtered data
  const filteredDevices = useMemo(() => {
    return devices.filter(device => {
      const matchesSearch = searchTerm === '' || 
        device.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.serial_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        device.ip_address?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesFilter = filters.status === 'all' || device.status === filters.status;
      const matchesCategory = filters.category === 'all' || device.type === filters.category;
      
      return matchesSearch && matchesFilter && matchesCategory;
    });
  }, [devices, searchTerm, filters]);

  const filteredTickets = useMemo(() => {
    return tickets.filter(ticket => {
      const matchesSearch = searchTerm === '' || 
        ticket.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.ticket_number?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesPriority = filters.priority === 'all' || ticket.priority === filters.priority;
      const matchesStatus = filters.status === 'all' || ticket.status === filters.status;
      
      return matchesSearch && matchesPriority && matchesStatus;
    });
  }, [tickets, searchTerm, filters]);

  if (authLoading || (loading && !refreshing)) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3 text-muted">Loading IT portal...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Page Header */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 bg-gradient-dark text-white shadow">
            <Card.Body className="py-4">
              <Row className="align-items-center">
                <Col md={8}>
                  <div className="d-flex align-items-center">
                    <div className="me-4">
                      {userProfile?.avatar ? (
                        <Image 
                          src={userProfile.avatar} 
                          roundedCircle 
                          width={80} 
                          height={80}
                          className="border border-3 border-white shadow"
                          alt="IT Manager avatar"
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div 
                          className="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow"
                          style={{ width: 80, height: 80 }}
                        >
                          <Cpu size={32} className="text-white" />
                        </div>
                      )}
                    </div>
                    <div>
                      <h1 className="h2 mb-1">IT Management Portal</h1>
                      <p className="mb-1 opacity-75">
                        Welcome, {userProfile?.first_name || 'IT Manager'}! Manage technology infrastructure
                      </p>
                      <small className="opacity-75">
                        Last updated: {new Date(lastRefreshTime).toLocaleTimeString()}
                        {refreshing && <span className="ms-2">🔄 Refreshing...</span>}
                      </small>
                    </div>
                  </div>
                </Col>
                <Col md={4} className="text-end">
                  <div className="d-flex gap-2 justify-content-end flex-wrap">
                    <Button 
                      variant="light" 
                      onClick={handleRefresh}
                      disabled={refreshing}
                      className="text-dark"
                    >
                      <ArrowClockwise className={`me-2 ${refreshing ? 'spinning' : ''}`} size={16} />
                      Refresh
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-dark"
                      onClick={() => setShowTicketModal(true)}
                    >
                      <Plus className="me-2" />
                      New Ticket
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-dark"
                      onClick={() => setShowDeviceModal(true)}
                    >
                      <Pc className="me-2" />
                      Add Device
                    </Button>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Error/Success Alerts */}
      {error && (
        <Alert variant="warning" dismissible onClose={() => setError('')}>
          <ExclamationCircle className="me-2" />
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          <CheckCircle className="me-2" />
          {success}
        </Alert>
      )}

      {/* Quick Stats */}
      <Row className="mb-4">
        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Total Devices</h6>
                  <h2 className="mb-0 text-primary">{formatNumber(itStats.totalDevices)}</h2>
                  <small className="text-muted">
                    <Badge bg="success" className="me-1">
                      {itStats.onlineDevices} Online
                    </Badge>
                    <Badge bg="danger" className="me-1">
                      {itStats.offlineDevices} Offline
                    </Badge>
                  </small>
                </div>
                <div className="bg-primary bg-opacity-10 p-3 rounded">
                  <Pc size={24} className="text-primary" />
                </div>
              </div>
              <ProgressBar className="mt-2">
                <ProgressBar 
                  variant="success" 
                  now={(itStats.onlineDevices / itStats.totalDevices) * 100 || 0} 
                  key={1} 
                />
                <ProgressBar 
                  variant="danger" 
                  now={(itStats.offlineDevices / itStats.totalDevices) * 100 || 0} 
                  key={2} 
                />
              </ProgressBar>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Tickets</h6>
                  <h2 className="mb-0 text-info">{formatNumber(itStats.pendingTickets)}</h2>
                  <small className="text-muted">
                    Pending: {itStats.pendingTickets} • Resolved: {itStats.resolvedTickets}
                  </small>
                </div>
                <div className="bg-info bg-opacity-10 p-3 rounded">
                  <ClipboardData size={24} className="text-info" />
                </div>
              </div>
              <Button 
                variant="outline-info" 
                size="sm" 
                className="mt-2 w-100"
                onClick={() => setActiveTab('tickets')}
              >
                View Tickets
              </Button>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Network Uptime</h6>
                  <h2 className="mb-0 text-success">{itStats.networkUptime}%</h2>
                  <small className="text-muted">Server Health: {itStats.serverHealth}%</small>
                </div>
                <div className="bg-success bg-opacity-10 p-3 rounded">
                  <Wifi size={24} className="text-success" />
                </div>
              </div>
              <ProgressBar 
                now={itStats.networkUptime} 
                variant={itStats.networkUptime >= 99 ? 'success' : itStats.networkUptime >= 95 ? 'warning' : 'danger'} 
                className="mt-2"
              />
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Security Alerts</h6>
                  <h2 className="mb-0 text-warning">{itStats.securityAlerts}</h2>
                  <small className="text-muted">Requiring attention</small>
                </div>
                <div className="bg-warning bg-opacity-10 p-3 rounded">
                  <ShieldExclamation size={24} className="text-warning" />
                </div>
              </div>
              {itStats.securityAlerts > 0 && (
                <Button 
                  variant="warning" 
                  size="sm" 
                  className="mt-2 w-100"
                  onClick={() => setActiveTab('security')}
                >
                  Review Alerts
                </Button>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Navigation Tabs */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Body className="py-2">
              <Tabs
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                className="border-0"
                fill
              >
                <Tab eventKey="dashboard" title={
                  <>
                    <Speedometer2 className="me-2" />
                    Dashboard
                  </>
                } />
                <Tab eventKey="devices" title={
                  <>
                    <Pc className="me-2" />
                    Devices ({devices.length})
                  </>
                } />
                <Tab eventKey="tickets" title={
                  <>
                    <ClipboardData className="me-2" />
                    Tickets ({tickets.length})
                    {itStats.pendingTickets > 0 && (
                      <Badge bg="warning" className="ms-2">{itStats.pendingTickets}</Badge>
                    )}
                  </>
                } />
                <Tab eventKey="servers" title={
                  <>
                    <Server className="me-2" />
                    Servers ({servers.length})
                  </>
                } />
                <Tab eventKey="network" title={
                  <>
                    <Wifi className="me-2" />
                    Network ({networkDevices.length})
                  </>
                } />
                <Tab eventKey="security" title={
                  <>
                    <Shield className="me-2" />
                    Security ({securityAlerts.length})
                  </>
                } />
                <Tab eventKey="backup" title={
                  <>
                    <Database className="me-2" />
                    Backup
                  </>
                } />
                <Tab eventKey="inventory" title={
                  <>
                    <Clipboard className="me-2" />
                    Inventory
                  </>
                } />
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Search and Filters */}
      {activeTab !== 'dashboard' && (
        <Row className="mb-4">
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Body className="py-2">
                <Row className="align-items-center">
                  <Col md={4}>
                    <InputGroup>
                      <InputGroup.Text>
                        <Search />
                      </InputGroup.Text>
                      <Form.Control
                        type="text"
                        placeholder={`Search ${activeTab}...`}
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
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'all')}>
                            All Status
                          </Dropdown.Item>
                          <Dropdown.Divider />
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'online')}>
                            Online
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'offline')}>
                            Offline
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'maintenance')}>
                            Maintenance
                          </Dropdown.Item>
                        </Dropdown.Menu>
                      </Dropdown>

                      {activeTab === 'tickets' && (
                        <Dropdown>
                          <Dropdown.Toggle variant="outline-secondary" size="sm">
                            <ExclamationCircle className="me-2" />
                            Priority: {filters.priority === 'all' ? 'All' : filters.priority}
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            <Dropdown.Item onClick={() => handleFilterChange('priority', 'all')}>
                              All Priorities
                            </Dropdown.Item>
                            <Dropdown.Divider />
                            <Dropdown.Item onClick={() => handleFilterChange('priority', 'high')}>
                              High
                            </Dropdown.Item>
                            <Dropdown.Item onClick={() => handleFilterChange('priority', 'medium')}>
                              Medium
                            </Dropdown.Item>
                            <Dropdown.Item onClick={() => handleFilterChange('priority', 'low')}>
                              Low
                            </Dropdown.Item>
                          </Dropdown.Menu>
                        </Dropdown>
                      )}

                      <Button 
                        variant="outline-secondary" 
                        size="sm"
                        onClick={() => {
                          setFilters({
                            status: 'all',
                            category: 'all',
                            priority: 'all',
                            location: 'all'
                          });
                          setSearchTerm('');
                        }}
                      >
                        <ArrowCounterclockwise className="me-2" />
                        Reset
                      </Button>
                    </div>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <>
          <Row className="mb-4">
            <Col lg={8} className="mb-4">
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">System Overview</h5>
                    <div className="d-flex gap-2">
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        onClick={handleRefresh}
                      >
                        <ArrowClockwise className="me-1" />
                        Refresh Data
                      </Button>
                    </div>
                  </div>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <h6 className="text-muted mb-3">System Health</h6>
                      <ListGroup variant="flush">
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Network Status</span>
                          <Badge bg={itStats.networkUptime >= 99 ? 'success' : 'warning'}>
                            {itStats.networkUptime}% Uptime
                          </Badge>
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Server Health</span>
                          <Badge bg={itStats.serverHealth >= 90 ? 'success' : 'warning'}>
                            {itStats.serverHealth}%
                          </Badge>
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Security Status</span>
                          <Badge bg={itStats.securityAlerts === 0 ? 'success' : 'danger'}>
                            {itStats.securityAlerts} Alerts
                          </Badge>
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Backup Status</span>
                          <Badge bg="info">
                            {backupStatus.filter(b => b.status === 'success').length} Successful
                          </Badge>
                        </ListGroup.Item>
                      </ListGroup>
                    </Col>
                    <Col md={6}>
                      <h6 className="text-muted mb-3">Device Distribution</h6>
                      <div className="text-center">
                        <PieChart size={80} className="text-primary mb-2" />
                        <div className="d-flex justify-content-around mt-3">
                          <div className="text-center">
                            <div className="fw-bold text-success">Computers</div>
                            <small>{devices.filter(d => d.type === 'computer').length}</small>
                          </div>
                          <div className="text-center">
                            <div className="fw-bold text-info">Printers</div>
                            <small>{devices.filter(d => d.type === 'printer').length}</small>
                          </div>
                          <div className="text-center">
                            <div className="fw-bold text-warning">Network</div>
                            <small>{networkDevices.length}</small>
                          </div>
                        </div>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>

            <Col lg={4} className="mb-4">
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">Recent Security Alerts</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {securityAlerts.length > 0 ? (
                    <ListGroup variant="flush">
                      {securityAlerts.slice(0, 5).map((alert, index) => (
                        <ListGroup.Item key={index}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h6 className="mb-1">{alert.title}</h6>
                              <small className="text-muted">{alert.description}</small>
                            </div>
                            <Badge bg={alert.severity === 'high' ? 'danger' : 'warning'}>
                              {alert.severity}
                            </Badge>
                          </div>
                          <div className="d-flex justify-content-between align-items-center mt-2">
                            <small className="text-muted">
                              <Clock size={12} className="me-1" />
                              {formatDateTime(alert.created_at)}
                            </small>
                            <Button 
                              size="sm" 
                              variant="outline-success"
                              onClick={() => handleResolveAlert(alert.id)}
                            >
                              Resolve
                            </Button>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <ShieldCheck size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No security alerts</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row>
            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">Recent Tickets</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {tickets.slice(0, 5).length > 0 ? (
                    <ListGroup variant="flush">
                      {tickets.slice(0, 5).map((ticket, index) => (
                        <ListGroup.Item key={index}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h6 className="mb-1">{ticket.title}</h6>
                              <small className="text-muted">{ticket.description?.substring(0, 100)}...</small>
                            </div>
                            <Badge bg={
                              ticket.priority === 'high' ? 'danger' :
                              ticket.priority === 'medium' ? 'warning' : 'info'
                            }>
                              {ticket.priority}
                            </Badge>
                          </div>
                          <div className="d-flex justify-content-between align-items-center mt-2">
                            <small className="text-muted">
                              #{ticket.ticket_number} • {formatDate(ticket.created_at)}
                            </small>
                            <Badge bg={getStatusBadge(ticket.status)}>
                              {ticket.status}
                            </Badge>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <ClipboardData size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No recent tickets</p>
                    </div>
                  )}
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="w-100"
                    onClick={() => setActiveTab('tickets')}
                  >
                    View All Tickets
                  </Button>
                </Card.Footer>
              </Card>
            </Col>

            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">Server Status</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {servers.length > 0 ? (
                    <ListGroup variant="flush">
                      {servers.slice(0, 5).map((server, index) => (
                        <ListGroup.Item key={index}>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h6 className="mb-1">{server.name}</h6>
                              <small className="text-muted">
                                {server.ip_address} • CPU: {server.cpu_usage}% • RAM: {server.ram_usage}%
                              </small>
                            </div>
                            <div className="d-flex align-items-center gap-2">
                              <Badge bg={server.status === 'online' ? 'success' : 'danger'}>
                                {server.status}
                              </Badge>
                              <div className={`p-1 rounded ${server.status === 'online' ? 'bg-success bg-opacity-25' : 'bg-danger bg-opacity-25'}`}>
                                <div style={{
                                  width: '8px',
                                  height: '8px',
                                  borderRadius: '50%',
                                  backgroundColor: server.status === 'online' ? '#198754' : '#dc3545',
                                  animation: server.status === 'online' ? 'pulse 2s infinite' : 'none'
                                }}></div>
                              </div>
                            </div>
                          </div>
                          <ProgressBar className="mt-2">
                            <ProgressBar 
                              variant={server.cpu_usage > 80 ? 'danger' : server.cpu_usage > 60 ? 'warning' : 'success'}
                              now={server.cpu_usage} 
                              key={1} 
                              label={`CPU: ${server.cpu_usage}%`}
                            />
                          </ProgressBar>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <Server size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No servers configured</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Devices Tab */}
      {activeTab === 'devices' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Device Management ({devices.length})</h5>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => setShowDeviceModal(true)}
                  >
                    <Plus className="me-1" />
                    Add Device
                  </Button>
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {filteredDevices.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Device Name</th>
                          <th>Type</th>
                          <th>Serial #</th>
                          <th>IP Address</th>
                          <th>MAC Address</th>
                          <th>Location</th>
                          <th>Assigned To</th>
                          <th>Status</th>
                          <th>Last Seen</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredDevices.map((device) => (
                          <tr key={device.id}>
                            <td>
                              <div className="d-flex align-items-center">
                                <div className="me-2">
                                  {device.type === 'computer' && <Pc size={20} className="text-primary" />}
                                  {device.type === 'laptop' && <Laptop size={20} className="text-info" />}
                                  {device.type === 'printer' && <Printer size={20} className="text-warning" />}
                                  {device.type === 'server' && <Server size={20} className="text-success" />}
                                  {device.type === 'network' && <Router size={20} className="text-secondary" />}
                                </div>
                                <div className="fw-bold">{device.name}</div>
                              </div>
                            </td>
                            <td>
                              <Badge bg="primary" className="text-capitalize">
                                {device.type}
                              </Badge>
                            </td>
                            <td>
                              <small className="font-monospace">{device.serial_number}</small>
                            </td>
                            <td>
                              <code>{device.ip_address}</code>
                            </td>
                            <td>
                              <small className="font-monospace">{device.mac_address}</small>
                            </td>
                            <td>{device.location}</td>
                            <td>
                              {device.assigned_to ? (
                                <Badge bg="info">{device.assigned_to}</Badge>
                              ) : (
                                <span className="text-muted">Unassigned</span>
                              )}
                            </td>
                            <td>
                              <Badge bg={getStatusBadge(device.status)}>
                                {device.status?.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <small className="text-muted">
                                {device.last_seen ? formatDateTime(device.last_seen) : 'Never'}
                              </small>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/it/devices/${device.id}`)}
                                >
                                  <Eye size={12} />
                                </Button>
                                <Button 
                                  variant="outline-warning" 
                                  size="sm"
                                  onClick={() => navigate(`/it/devices/${device.id}/edit`)}
                                >
                                  <Pencil size={12} />
                                </Button>
                                <Button 
                                  variant="outline-danger" 
                                  size="sm"
                                  onClick={() => {
                                    if (window.confirm('Delete this device?')) {
                                      // Handle delete
                                    }
                                  }}
                                >
                                  <Trash size={12} />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-5">
                    <Pc size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No devices found</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Tickets Tab */}
      {activeTab === 'tickets' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Support Tickets ({tickets.length})</h5>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => setShowTicketModal(true)}
                  >
                    <Plus className="me-1" />
                    New Ticket
                  </Button>
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {filteredTickets.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Ticket #</th>
                          <th>Title</th>
                          <th>Category</th>
                          <th>Priority</th>
                          <th>Submitted By</th>
                          <th>Assigned To</th>
                          <th>Created</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredTickets.map((ticket) => (
                          <tr key={ticket.id}>
                            <td className="fw-semibold">
                              <code>{ticket.ticket_number}</code>
                            </td>
                            <td>
                              <div className="fw-bold">{ticket.title}</div>
                              <small className="text-muted">{ticket.description?.substring(0, 50)}...</small>
                            </td>
                            <td>
                              <Badge bg="info">{ticket.category}</Badge>
                            </td>
                            <td>
                              <Badge bg={
                                ticket.priority === 'high' ? 'danger' :
                                ticket.priority === 'medium' ? 'warning' : 'info'
                              }>
                                {ticket.priority}
                              </Badge>
                            </td>
                            <td>{ticket.submitted_by}</td>
                            <td>
                              {ticket.assigned_to ? (
                                <Badge bg="primary">{ticket.assigned_to}</Badge>
                              ) : (
                                <span className="text-muted">Unassigned</span>
                              )}
                            </td>
                            <td>
                              <small>{formatDate(ticket.created_at)}</small>
                            </td>
                            <td>
                              <Badge bg={getStatusBadge(ticket.status)}>
                                {ticket.status?.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/it/tickets/${ticket.id}`)}
                                >
                                  View
                                </Button>
                                {ticket.status === 'open' && (
                                  <Button 
                                    variant="success" 
                                    size="sm"
                                    onClick={() => {
                                      // Handle resolve
                                    }}
                                  >
                                    Resolve
                                  </Button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-5">
                    <ClipboardData size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No tickets found</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Security Alerts ({securityAlerts.length})</h5>
              </Card.Header>
              <Card.Body className="p-0">
                {securityAlerts.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Alert</th>
                          <th>Description</th>
                          <th>Severity</th>
                          <th>Source</th>
                          <th>Detected</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {securityAlerts.map((alert) => (
                          <tr key={alert.id}>
                            <td>
                              <div className="fw-bold">{alert.title}</div>
                            </td>
                            <td>
                              <small className="text-muted">{alert.description}</small>
                            </td>
                            <td>
                              <Badge bg={
                                alert.severity === 'critical' ? 'dark' :
                                alert.severity === 'high' ? 'danger' :
                                alert.severity === 'medium' ? 'warning' : 'info'
                              }>
                                {alert.severity.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <small>{alert.source}</small>
                            </td>
                            <td>
                              <small>{formatDateTime(alert.detected_at)}</small>
                            </td>
                            <td>
                              <Badge bg={getStatusBadge(alert.status)}>
                                {alert.status?.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/it/security/${alert.id}`)}
                                >
                                  Details
                                </Button>
                                {alert.status === 'open' && (
                                  <Button 
                                    variant="success" 
                                    size="sm"
                                    onClick={() => handleResolveAlert(alert.id)}
                                  >
                                    Resolve
                                  </Button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-5">
                    <ShieldCheck size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No security alerts</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Ticket Creation Modal */}
      <Modal show={showTicketModal} onHide={() => setShowTicketModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create Support Ticket</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Title</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="Brief description of the issue"
                value={ticketForm.title}
                onChange={(e) => setTicketForm({...ticketForm, title: e.target.value})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={4}
                placeholder="Detailed description of the issue"
                value={ticketForm.description}
                onChange={(e) => setTicketForm({...ticketForm, description: e.target.value})}
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Priority</Form.Label>
                  <Form.Select 
                    value={ticketForm.priority}
                    onChange={(e) => setTicketForm({...ticketForm, priority: e.target.value})}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select 
                    value={ticketForm.category}
                    onChange={(e) => setTicketForm({...ticketForm, category: e.target.value})}
                  >
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="network">Network</option>
                    <option value="security">Security</option>
                    <option value="other">Other</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowTicketModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateTicket} disabled={loading || !ticketForm.title}>
            {loading ? <Spinner size="sm" /> : 'Create Ticket'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Device Registration Modal */}
      <Modal show={showDeviceModal} onHide={() => setShowDeviceModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Register New Device</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Device Name</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="e.g., Admin Computer"
                    value={deviceForm.name}
                    onChange={(e) => setDeviceForm({...deviceForm, name: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Device Type</Form.Label>
                  <Form.Select 
                    value={deviceForm.type}
                    onChange={(e) => setDeviceForm({...deviceForm, type: e.target.value})}
                  >
                    <option value="computer">Computer</option>
                    <option value="laptop">Laptop</option>
                    <option value="printer">Printer</option>
                    <option value="server">Server</option>
                    <option value="network">Network Device</option>
                    <option value="phone">Phone</option>
                    <option value="tablet">Tablet</option>
                    <option value="other">Other</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Serial Number</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="Device serial number"
                    value={deviceForm.serial_number}
                    onChange={(e) => setDeviceForm({...deviceForm, serial_number: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>MAC Address</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="00:11:22:33:44:55"
                    value={deviceForm.mac_address}
                    onChange={(e) => setDeviceForm({...deviceForm, mac_address: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>IP Address</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="192.168.1.100"
                    value={deviceForm.ip_address}
                    onChange={(e) => setDeviceForm({...deviceForm, ip_address: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Location</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="e.g., Admin Office"
                    value={deviceForm.location}
                    onChange={(e) => setDeviceForm({...deviceForm, location: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeviceModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleRegisterDevice} disabled={loading || !deviceForm.name}>
            {loading ? <Spinner size="sm" /> : 'Register Device'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Footer */}
      <Row className="mt-4">
        <Col>
          <Card className="border-0 bg-light">
            <Card.Body className="py-2">
              <div className="d-flex justify-content-between align-items-center">
                <small className="text-muted">
                  IT Portal v1.0 • System Uptime: {itStats.networkUptime}%
                </small>
                <div>
                  <small className="text-muted me-3">
                    Last Refresh: {new Date(lastRefreshTime).toLocaleString()}
                  </small>
                  <small className="text-muted">
                    Status: <Badge bg={itStats.serverHealth >= 90 ? 'success' : 'warning'}>
                      {itStats.serverHealth >= 90 ? 'Healthy' : 'Degraded'}
                    </Badge>
                  </small>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Custom CSS */}
      <style jsx>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .bg-gradient-dark {
          background: linear-gradient(135deg, #343a40 0%, #212529 100%);
        }
        .table-responsive {
          max-height: 500px;
          overflow-y: auto;
        }
        .card {
          transition: transform 0.2s;
        }
        .card:hover {
          transform: translateY(-2px);
        }
        code {
          font-size: 0.875em;
          background: #f8f9fa;
          padding: 2px 4px;
          border-radius: 3px;
        }
      `}</style>
    </Container>
  );
};

export default ITPortal;