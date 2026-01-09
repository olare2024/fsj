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
  Popover
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  // School Management Icons
  Building,
  People,
  PeopleFill,
  PersonCircle,
  PersonBadge,
  PersonLinesFill,
  Book,
  BookFill,
  Journal,
  JournalCode,
  ClipboardData,
  ClipboardCheck,
  CalendarEvent,
  CalendarWeek,
  CalendarMonth,
  Clock,
  ClockHistory,
  GraphUp,
  GraphDown,
  BarChart,
  BarChartFill,
  PieChart,
  PieChartFill,
  FileEarmarkBarGraph,
  FileEarmarkText,
  FileEarmarkCheck,
  FileEarmarkMedical,
  FileEarmarkSpreadsheet,
  FileEarmarkPdf,
  FileEarmarkExcel,
  FileEarmarkWord,
  FileEarmarkRuled,
  FileEarmarkFont,
  FileEarmarkBinary,
  // Communication Icons
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
  Bell,
  BellFill,
  Megaphone,
  MegaphoneFill,
  // Admin Icons
  Gear,
  GearFill,
  GearWide,
  GearWideConnected,
  Tools,
  Wrench,
  Hammer,
  Shield,
  // Navigation & Actions
  ArrowClockwise,
  Download,
  Share,
  Save,
  SaveFill,
  Plus,
  PlusCircle,
  PlusSquare,
  Dash,
  DashCircle,
  DashSquare,
  X,
  XCircle,
  XSquare,
  Check,
  CheckCircle,
  CheckSquare,
  // Status & Indicators
  ExclamationTriangle,
  ExclamationCircle,
  ExclamationDiamond,
  QuestionCircle,
  QuestionDiamond,
  InfoCircle,
  InfoSquare,
  // Miscellaneous
  Search,
  Filter,
  Funnel,
  SortDown,
  SortUp,
  SortAlphaDown,
  SortAlphaUp,
  SortNumericDown,
  SortNumericUp,
  Eye,
  EyeFill,
  EyeSlash,
  EyeSlashFill,
  Pencil,
  PencilFill,
  PencilSquare,

  // People Management
  PersonPlus,
  PersonDash,
  PersonX,
  PersonCheck,
  PersonGear,
  // School Specific
  Award,
  AwardFill,
  Trophy,
  TrophyFill,
  Star,
  StarFill,
  Flag,
  FlagFill,
  Bookmark,
  BookmarkFill,
  Heart,
  HeartFill,
  // New icons
  Clipboard,
  ClipboardCheckFill,
  CalendarCheck,
  CalendarCheckFill,
  CalendarX,
  CalendarXFill,
  CalendarPlus,
  CalendarPlusFill,
  // Dashboard specific
  Speedometer,
  Speedometer2,
  House,
  HouseFill,
  Columns,
  ColumnsGap,
  Grid,
  GridFill,
  LayoutTextWindow,
  LayoutTextWindowReverse,
  // Statistics
  Calculator,
  CalculatorFill,
  Percent,
  // Attendance
  // Finance
  Cash,
  CashStack,
  Coin,
  CreditCard,
  Bank,
  Wallet,
  Wallet2,
  // Time
  Stopwatch,
  StopwatchFill,
  Alarm,
  AlarmFill,
  // Notifications
  BellSlash,
  BellSlashFill
} from 'react-bootstrap-icons';

// Import APIs
import authAPI from '../../services/authAPI';
import {academicAPI} from '../../services/academicAPI';
import staffAPI from '../../services/staffAPI';
import {studentsAPI} from '../../services/studentAPI';
import attendanceAPI from '../../services/attendanceAPI';
import {disciplineAPI} from '../../services/disciplineAPI';
import {reportsAPI} from '../../services/reportsAPI';
import adminAPI from '../../services/adminAPI';

// Utility Functions
const formatNumber = (number) => {
  return new Intl.NumberFormat('en-KE').format(number || 0);
};

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES'
  }).format(amount || 0);
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
    'active': 'success',
    'inactive': 'secondary',
    'pending': 'warning',
    'approved': 'primary',
    'rejected': 'danger',
    'absent': 'danger',
    'present': 'success',
    'late': 'warning',
    'excused': 'info',
    'completed': 'success',
    'in-progress': 'warning',
    'not-started': 'secondary',
    'excellent': 'success',
    'good': 'info',
    'average': 'warning',
    'poor': 'danger'
  };
  return variants[status] || 'secondary';
};

const getPerformanceColor = (percentage) => {
  if (percentage >= 80) return 'success';
  if (percentage >= 60) return 'info';
  if (percentage >= 40) return 'warning';
  return 'danger';
};

const HeadTeacherPortal = () => {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [lastRefreshTime, setLastRefreshTime] = useState(Date.now());
  
  // Dashboard data states
  const [schoolStats, setSchoolStats] = useState({
    totalStudents: 0,
    totalTeachers: 0,
    totalClasses: 0,
    totalSubjects: 0,
    attendanceRate: 0,
    academicPerformance: 0,
    disciplineCases: 0,
    pendingTasks: 0
  });
  
  const [userProfile, setUserProfile] = useState(null);
  const [academicYear, setAcademicYear] = useState('');
  const [term, setTerm] = useState('');
  
  // Detailed data states
  const [students, setStudents] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [attendanceData, setAttendanceData] = useState([]);
  const [academicResults, setAcademicResults] = useState([]);
  const [disciplineCases, setDisciplineCases] = useState([]);
  const [pendingTasks, setPendingTasks] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [reports, setReports] = useState([]);
  const [schoolCalendar, setSchoolCalendar] = useState([]);
  const [staffMeetings, setStaffMeetings] = useState([]);
  const [studentPerformance, setStudentPerformance] = useState([]);
  const [classPerformance, setClassPerformance] = useState([]);
  const [teacherPerformance, setTeacherPerformance] = useState([]);
  
  // Filter states
  const [filters, setFilters] = useState({
    class: 'all',
    term: 'current',
    year: 'current',
    status: 'all',
    category: 'all'
  });
  
  // Modal states
  const [showAnnouncementModal, setShowAnnouncementModal] = useState(false);
  const [showMeetingModal, setShowMeetingModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Form states
  const [announcementForm, setAnnouncementForm] = useState({
    title: '',
    content: '',
    priority: 'normal',
    audience: 'all'
  });
  
  const [meetingForm, setMeetingForm] = useState({
    title: '',
    agenda: '',
    date: '',
    time: '',
    duration: '60',
    participants: [],
    location: 'Staff Room'
  });
  
  const [reportForm, setReportForm] = useState({
    type: 'academic',
    period: 'term',
    format: 'pdf',
    includeDetails: true,
    emailCopy: false
  });

  // Clear messages after timeout
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        if (error) setError('');
        if (success) setSuccess('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  // Fetch all school data
  const fetchSchoolData = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');

      const [
        profileResult,
        statsResult,
        studentsResult,
        teachersResult,
        classesResult,
        attendanceResult,
        academicResult,
        disciplineResult,
        tasksResult,
        announcementsResult,
        calendarResult,
        meetingsResult,
        performanceResult
      ] = await Promise.all([
        authAPI.getCurrentUser(),
        adminAPI.getSchoolStats(),
        studentAPI.getAllStudents({ limit: 50 }),
        staffAPI.getAllTeachers(),
        academicAPI.getAllClasses(),
        attendanceAPI.getSchoolAttendance({ date: new Date().toISOString().split('T')[0] }),
        academicAPI.getTermResults({ term: 'current' }),
        disciplineAPI.getRecentCases({ limit: 20 }),
        adminAPI.getPendingTasks({ role: 'headteacher' }),
        adminAPI.getAnnouncements({ limit: 10 }),
        adminAPI.getSchoolCalendar({ month: new Date().getMonth() + 1 }),
        staffAPI.getStaffMeetings({ upcoming: true }),
        academicAPI.getPerformanceOverview()
      ]);

      // Process results
      if (profileResult.success) setUserProfile(profileResult.user || profileResult.data);
      if (statsResult.success) {
        setSchoolStats(statsResult.data);
        setAcademicYear(statsResult.data.academic_year || '2024');
        setTerm(statsResult.data.current_term || 'Term 1');
      }
      if (studentsResult.success) setStudents(studentsResult.data?.students || studentsResult.data || []);
      if (teachersResult.success) setTeachers(teachersResult.data?.teachers || teachersResult.data || []);
      if (classesResult.success) setClasses(classesResult.data?.classes || classesResult.data || []);
      if (attendanceResult.success) setAttendanceData(attendanceResult.data?.attendance || attendanceResult.data || []);
      if (academicResult.success) setAcademicResults(academicResult.data?.results || academicResult.data || []);
      if (disciplineResult.success) setDisciplineCases(disciplineResult.data?.cases || disciplineResult.data || []);
      if (tasksResult.success) setPendingTasks(tasksResult.data?.tasks || tasksResult.data || []);
      if (announcementsResult.success) setAnnouncements(announcementsResult.data?.announcements || announcementsResult.data || []);
      if (calendarResult.success) setSchoolCalendar(calendarResult.data?.events || calendarResult.data || []);
      if (meetingsResult.success) setStaffMeetings(meetingsResult.data?.meetings || meetingsResult.data || []);
      if (performanceResult.success) {
        setStudentPerformance(performanceResult.data?.student_performance || []);
        setClassPerformance(performanceResult.data?.class_performance || []);
        setTeacherPerformance(performanceResult.data?.teacher_performance || []);
      }

      setLastRefreshTime(Date.now());

    } catch (err) {
      console.error('Error fetching school data:', err);
      setError('Failed to load school data. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading && currentUser) {
      fetchSchoolData();
    }
  }, [authLoading, currentUser, fetchSchoolData]);

  // Refresh function
  const handleRefresh = () => {
    fetchSchoolData(true);
  };

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  // Announcement functions
  const handleCreateAnnouncement = async () => {
    try {
      setLoading(true);
      const result = await adminAPI.createAnnouncement(announcementForm);
      
      if (result.success) {
        setSuccess('Announcement created successfully!');
        setShowAnnouncementModal(false);
        setAnnouncementForm({
          title: '',
          content: '',
          priority: 'normal',
          audience: 'all'
        });
        fetchSchoolData();
      } else {
        setError(result.error?.message || 'Failed to create announcement');
      }
    } catch (err) {
      setError('Failed to create announcement');
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleMeeting = async () => {
    try {
      setLoading(true);
      const result = await staffAPI.scheduleMeeting(meetingForm);
      
      if (result.success) {
        setSuccess('Meeting scheduled successfully!');
        setShowMeetingModal(false);
        setMeetingForm({
          title: '',
          agenda: '',
          date: '',
          time: '',
          duration: '60',
          participants: [],
          location: 'Staff Room'
        });
        fetchSchoolData();
      } else {
        setError(result.error?.message || 'Failed to schedule meeting');
      }
    } catch (err) {
      setError('Failed to schedule meeting');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setLoading(true);
      const result = await reportsAPI.generateReport(reportForm);
      
      if (result.success) {
        setSuccess('Report generated successfully!');
        setShowReportModal(false);
        
        // Add to reports list
        setReports(prev => [{
          id: Date.now(),
          type: reportForm.type,
          period: reportForm.period,
          generated_at: new Date().toISOString(),
          download_url: result.data?.url
        }, ...prev.slice(0, 9)]);
        
        if (reportForm.emailCopy) {
          setSuccess('Report has been sent to your email.');
        }
      } else {
        setError(result.error?.message || 'Failed to generate report');
      }
    } catch (err) {
      setError('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveTask = async (taskId) => {
    try {
      setLoading(true);
      const result = await adminAPI.approveTask(taskId);
      
      if (result.success) {
        setSuccess('Task approved successfully!');
        setPendingTasks(prev => prev.filter(task => task.id !== taskId));
      } else {
        setError(result.error?.message || 'Failed to approve task');
      }
    } catch (err) {
      setError('Failed to approve task');
    } finally {
      setLoading(false);
    }
  };

  const handleResolveDisciplineCase = async (caseId) => {
    try {
      setLoading(true);
      const result = await disciplineAPI.resolveCase(caseId, {
        resolved_by: userProfile?.id,
        resolution: 'Resolved by Head Teacher'
      });
      
      if (result.success) {
        setSuccess('Discipline case resolved!');
        setDisciplineCases(prev => prev.filter(c => c.id !== caseId));
      } else {
        setError(result.error?.message || 'Failed to resolve case');
      }
    } catch (err) {
      setError('Failed to resolve case');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (recipientId, message) => {
    try {
      setLoading(true);
      const result = await adminAPI.sendMessage({
        recipient_id: recipientId,
        message,
        priority: 'normal'
      });
      
      if (result.success) {
        setSuccess('Message sent successfully!');
      } else {
        setError(result.error?.message || 'Failed to send message');
      }
    } catch (err) {
      setError('Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  // Filter data based on search term
  const filteredStudents = useMemo(() => {
    return students.filter(student => 
      searchTerm === '' || 
      student.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.admission_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.class_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [students, searchTerm]);

  const filteredTeachers = useMemo(() => {
    return teachers.filter(teacher => 
      searchTerm === '' || 
      teacher.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      teacher.employee_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      teacher.subject?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [teachers, searchTerm]);

  if (authLoading || (loading && !refreshing)) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3 text-muted">Loading head teacher portal...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Page Header */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 bg-gradient-info text-white shadow">
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
                          alt="Head Teacher avatar"
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div 
                          className="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow"
                          style={{ width: 80, height: 80 }}
                        >
                          <PersonBadge size={32} className="text-white" />
                        </div>
                      )}
                    </div>
                    <div>
                      <h1 className="h2 mb-1">Head Teacher Portal</h1>
                      <p className="mb-1 opacity-75">
                        Welcome, {userProfile?.first_name || 'Head Teacher'}! Manage school operations effectively
                      </p>
                      <small className="opacity-75">
                        Academic Year: {academicYear} • Term: {term} • 
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
                      className="text-info"
                    >
                      <ArrowClockwise className={`me-2 ${refreshing ? 'spinning' : ''}`} size={16} />
                      Refresh
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-info"
                      onClick={() => setShowAnnouncementModal(true)}
                    >
                      <Megaphone className="me-2" />
                      Announce
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-info"
                      onClick={() => setShowMeetingModal(true)}
                    >
                      <CalendarEvent className="me-2" />
                      Schedule
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
          <ExclamationTriangle className="me-2" />
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
                  <h6 className="card-title text-uppercase text-muted mb-2">Total Students</h6>
                  <h2 className="mb-0 text-primary">{formatNumber(schoolStats.totalStudents)}</h2>
                  <small className="text-muted">
                    <Badge bg="success" className="me-1">
                      {schoolStats.attendanceRate}% Attendance
                    </Badge>
                  </small>
                </div>
                <div className="bg-primary bg-opacity-10 p-3 rounded">
                  <People size={24} className="text-primary" />
                </div>
              </div>
              <ProgressBar 
                now={schoolStats.attendanceRate} 
                variant={getPerformanceColor(schoolStats.attendanceRate)} 
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
                  <h6 className="card-title text-uppercase text-muted mb-2">Teaching Staff</h6>
                  <h2 className="mb-0 text-info">{formatNumber(schoolStats.totalTeachers)}</h2>
                  <small className="text-muted">Active: {teachers.filter(t => t.status === 'active').length}</small>
                </div>
                <div className="bg-info bg-opacity-10 p-3 rounded">
                  <PersonBadge size={24} className="text-info" />
                </div>
              </div>
              <Button 
                variant="outline-info" 
                size="sm" 
                className="mt-2 w-100"
                onClick={() => setActiveTab('staff')}
              >
                View Staff
              </Button>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Academic Performance</h6>
                  <h2 className="mb-0 text-success">{schoolStats.academicPerformance}%</h2>
                  <small className="text-muted">School Average</small>
                </div>
                <div className="bg-success bg-opacity-10 p-3 rounded">
                  <TrendUp size={24} className="text-success" />
                </div>
              </div>
              <ProgressBar 
                now={schoolStats.academicPerformance} 
                variant={getPerformanceColor(schoolStats.academicPerformance)} 
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
                  <h6 className="card-title text-uppercase text-muted mb-2">Pending Actions</h6>
                  <h2 className="mb-0 text-warning">{schoolStats.pendingTasks}</h2>
                  <small className="text-muted">Requiring attention</small>
                </div>
                <div className="bg-warning bg-opacity-10 p-3 rounded">
                  <ClipboardCheck size={24} className="text-warning" />
                </div>
              </div>
              {schoolStats.pendingTasks > 0 && (
                <Button 
                  variant="warning" 
                  size="sm" 
                  className="mt-2 w-100"
                  onClick={() => setActiveTab('tasks')}
                >
                  Review Tasks
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
                <Tab eventKey="students" title={
                  <>
                    <People className="me-2" />
                    Students ({students.length})
                  </>
                } />
                <Tab eventKey="staff" title={
                  <>
                    <PersonBadge className="me-2" />
                    Staff ({teachers.length})
                  </>
                } />
                <Tab eventKey="academics" title={
                  <>
                    <Book className="me-2" />
                    Academics
                  </>
                } />
                <Tab eventKey="attendance" title={
                  <>
                    <ClipboardCheck className="me-2" />
                    Attendance
                  </>
                } />
                <Tab eventKey="discipline" title={
                  <>
                    <Shield className="me-2" />
                    Discipline ({disciplineCases.length})
                  </>
                } />
                <Tab eventKey="tasks" title={
                  <>
                    <ClipboardData className="me-2" />
                    Tasks ({pendingTasks.length})
                    {schoolStats.pendingTasks > 0 && (
                      <Badge bg="warning" className="ms-2">{schoolStats.pendingTasks}</Badge>
                    )}
                  </>
                } />
                <Tab eventKey="reports" title={
                  <>
                    <FileEarmarkBarGraph className="me-2" />
                    Reports
                  </>
                } />
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Search and Filters */}
      {activeTab !== 'dashboard' && activeTab !== 'reports' && (
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
                          Class: {filters.class === 'all' ? 'All' : filters.class}
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Item onClick={() => handleFilterChange('class', 'all')}>
                            All Classes
                          </Dropdown.Item>
                          <Dropdown.Divider />
                          {classes.map((cls, index) => (
                            <Dropdown.Item 
                              key={index}
                              onClick={() => handleFilterChange('class', cls.name)}
                            >
                              {cls.name}
                            </Dropdown.Item>
                          ))}
                        </Dropdown.Menu>
                      </Dropdown>

                      <Dropdown>
                        <Dropdown.Toggle variant="outline-secondary" size="sm">
                          <CalendarEvent className="me-2" />
                          Term: {filters.term === 'current' ? 'Current' : filters.term}
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Item onClick={() => handleFilterChange('term', 'current')}>
                            Current Term
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('term', 'previous')}>
                            Previous Term
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('term', 'all')}>
                            All Terms
                          </Dropdown.Item>
                        </Dropdown.Menu>
                      </Dropdown>

                      <Button 
                        variant="outline-secondary" 
                        size="sm"
                        onClick={() => {
                          setFilters({
                            class: 'all',
                            term: 'current',
                            year: 'current',
                            status: 'all',
                            category: 'all'
                          });
                          setSearchTerm('');
                        }}
                      >
                        <ArrowCounterclockwise className="me-2" />
                        Reset
                      </Button>

                      <Button 
                        variant="primary" 
                        size="sm"
                        onClick={() => {
                          if (activeTab === 'students') navigate('/head-teacher/students/add');
                          if (activeTab === 'staff') navigate('/head-teacher/staff/add');
                        }}
                      >
                        <Plus className="me-1" />
                        Add New
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
                    <h5 className="mb-0">School Overview</h5>
                    <div className="d-flex gap-2">
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        onClick={() => setShowReportModal(true)}
                      >
                        <FileEarmarkBarGraph className="me-1" />
                        Generate Report
                      </Button>
                    </div>
                  </div>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <h6 className="text-muted mb-3">Quick Stats</h6>
                      <ListGroup variant="flush">
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Classes</span>
                          <Badge bg="primary">{schoolStats.totalClasses}</Badge>
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Subjects</span>
                          <Badge bg="info">{schoolStats.totalSubjects}</Badge>
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Discipline Cases</span>
                          <Badge bg="warning">{schoolStats.disciplineCases}</Badge>
                        </ListGroup.Item>
                        <ListGroup.Item className="d-flex justify-content-between align-items-center">
                          <span>Student-Teacher Ratio</span>
                          <Badge bg="secondary">
                            {schoolStats.totalStudents}:{schoolStats.totalTeachers}
                          </Badge>
                        </ListGroup.Item>
                      </ListGroup>
                    </Col>
                    <Col md={6}>
                      <h6 className="text-muted mb-3">Performance Trends</h6>
                      <div className="text-center">
                        <PieChart size={80} className="text-success mb-2" />
                        <div className="d-flex justify-content-around mt-3">
                          <div className="text-center">
                            <div className="fw-bold text-success">High</div>
                            <small>{studentPerformance.filter(s => s.grade === 'A').length} Students</small>
                          </div>
                          <div className="text-center">
                            <div className="fw-bold text-info">Average</div>
                            <small>{studentPerformance.filter(s => s.grade === 'B' || s.grade === 'C').length} Students</small>
                          </div>
                          <div className="text-center">
                            <div className="fw-bold text-warning">Low</div>
                            <small>{studentPerformance.filter(s => s.grade === 'D' || s.grade === 'E').length} Students</small>
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
                  <h5 className="mb-0">Upcoming Events</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {schoolCalendar.length > 0 ? (
                    <ListGroup variant="flush">
                      {schoolCalendar.slice(0, 5).map((event, index) => (
                        <ListGroup.Item key={index}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h6 className="mb-1">{event.title}</h6>
                              <small className="text-muted">{event.description}</small>
                            </div>
                            <Badge bg="info">
                              {formatDate(event.date)}
                            </Badge>
                          </div>
                          <small className="text-muted d-block mt-1">
                            <CalendarEvent size={12} className="me-1" />
                            {event.time} • {event.location}
                          </small>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <CalendarEvent size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No upcoming events</p>
                    </div>
                  )}
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="w-100"
                    onClick={() => navigate('/head-teacher/calendar')}
                  >
                    View Full Calendar
                  </Button>
                </Card.Footer>
              </Card>
            </Col>
          </Row>

          <Row>
            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">Recent Announcements</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {announcements.length > 0 ? (
                    <ListGroup variant="flush">
                      {announcements.map((announcement, index) => (
                        <ListGroup.Item key={index}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h6 className="mb-1">{announcement.title}</h6>
                              <small className="text-muted">{announcement.content}</small>
                            </div>
                            <Badge bg={
                              announcement.priority === 'high' ? 'danger' :
                              announcement.priority === 'medium' ? 'warning' : 'info'
                            }>
                              {announcement.priority}
                            </Badge>
                          </div>
                          <div className="d-flex justify-content-between align-items-center mt-2">
                            <small className="text-muted">
                              By {announcement.author} • {formatDateTime(announcement.created_at)}
                            </small>
                            <small className="text-muted">
                              For: {announcement.audience}
                            </small>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <Megaphone size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No announcements yet</p>
                    </div>
                  )}
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    variant="outline-success" 
                    size="sm" 
                    className="w-100"
                    onClick={() => setShowAnnouncementModal(true)}
                  >
                    <Plus className="me-1" />
                    New Announcement
                  </Button>
                </Card.Footer>
              </Card>
            </Col>

            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">Staff Meetings</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {staffMeetings.length > 0 ? (
                    <ListGroup variant="flush">
                      {staffMeetings.slice(0, 5).map((meeting, index) => (
                        <ListGroup.Item key={index}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h6 className="mb-1">{meeting.title}</h6>
                              <small className="text-muted">{meeting.agenda}</small>
                            </div>
                            <Badge bg="primary">
                              {formatDate(meeting.date)}
                            </Badge>
                          </div>
                          <div className="d-flex justify-content-between align-items-center mt-2">
                            <small className="text-muted">
                              <Clock size={12} className="me-1" />
                              {meeting.time} ({meeting.duration} mins)
                            </small>
                            <small className="text-muted">
                              <People size={12} className="me-1" />
                              {meeting.participants?.length || 0} attending
                            </small>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <CalendarEvent size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No scheduled meetings</p>
                    </div>
                  )}
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="w-100"
                    onClick={() => setShowMeetingModal(true)}
                  >
                    <Plus className="me-1" />
                    Schedule Meeting
                  </Button>
                </Card.Footer>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Students Tab */}
      {activeTab === 'students' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Student Management ({students.length})</h5>
                  <div>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      className="me-2"
                      onClick={() => navigate('/head-teacher/students/add')}
                    >
                      <Plus className="me-1" />
                      Add Student
                    </Button>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => navigate('/head-teacher/students/report')}
                    >
                      <FileEarmarkBarGraph className="me-1" />
                      Student Report
                    </Button>
                  </div>
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {filteredStudents.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Admission #</th>
                          <th>Student Name</th>
                          <th>Class</th>
                          <th>Gender</th>
                          <th>Date of Birth</th>
                          <th>Parent Contact</th>
                          <th>Attendance</th>
                          <th>Performance</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredStudents.map((student) => (
                          <tr key={student.id}>
                            <td className="fw-semibold">{student.admission_number}</td>
                            <td>
                              <div className="d-flex align-items-center">
                                {student.avatar && (
                                  <Image 
                                    src={student.avatar} 
                                    roundedCircle 
                                    width={30} 
                                    height={30}
                                    className="me-2"
                                    alt={student.name}
                                  />
                                )}
                                <div>
                                  <div className="fw-bold">{student.name}</div>
                                  <small className="text-muted">{student.email}</small>
                                </div>
                              </div>
                            </td>
                            <td>
                              <Badge bg="primary">{student.class_name}</Badge>
                            </td>
                            <td>{student.gender}</td>
                            <td>
                              <small>{formatDate(student.date_of_birth)}</small>
                            </td>
                            <td>
                              <small>{student.parent_phone}</small>
                            </td>
                            <td>
                              <Badge bg={student.attendance_rate >= 80 ? 'success' : 'warning'}>
                                {student.attendance_rate || 0}%
                              </Badge>
                            </td>
                            <td>
                              <Badge bg={getStatusBadge(student.performance)}>
                                {student.performance || 'N/A'}
                              </Badge>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/head-teacher/students/${student.id}`)}
                                >
                                  <Eye size={12} />
                                </Button>
                                <Button 
                                  variant="outline-info" 
                                  size="sm"
                                  onClick={() => handleSendMessage(student.id, `Message to ${student.name}`)}
                                >
                                  <Chat size={12} />
                                </Button>
                                <Button 
                                  variant="outline-warning" 
                                  size="sm"
                                  onClick={() => navigate(`/head-teacher/students/${student.id}/edit`)}
                                >
                                  <Pencil size={12} />
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
                    <People size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No students found</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Staff Tab */}
      {activeTab === 'staff' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Staff Management ({teachers.length})</h5>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => navigate('/head-teacher/staff/add')}
                  >
                    <Plus className="me-1" />
                    Add Staff
                  </Button>
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {filteredTeachers.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Employee #</th>
                          <th>Staff Name</th>
                          <th>Position</th>
                          <th>Subjects</th>
                          <th>Classes</th>
                          <th>Contact</th>
                          <th>Status</th>
                          <th>Performance</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredTeachers.map((teacher) => (
                          <tr key={teacher.id}>
                            <td className="fw-semibold">{teacher.employee_id}</td>
                            <td>
                              <div className="d-flex align-items-center">
                                {teacher.avatar && (
                                  <Image 
                                    src={teacher.avatar} 
                                    roundedCircle 
                                    width={30} 
                                    height={30}
                                    className="me-2"
                                    alt={teacher.name}
                                  />
                                )}
                                <div>
                                  <div className="fw-bold">{teacher.name}</div>
                                  <small className="text-muted">{teacher.email}</small>
                                </div>
                              </div>
                            </td>
                            <td>
                              <Badge bg="info">{teacher.position}</Badge>
                            </td>
                            <td>
                              <small>{teacher.subject}</small>
                            </td>
                            <td>
                              <small>{teacher.class_assigned}</small>
                            </td>
                            <td>
                              <small>{teacher.phone}</small>
                            </td>
                            <td>
                              <Badge bg={getStatusBadge(teacher.status)}>
                                {teacher.status?.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <Badge bg={teacher.performance_rating >= 4 ? 'success' : 'warning'}>
                                {teacher.performance_rating || 'N/A'} / 5
                              </Badge>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/head-teacher/staff/${teacher.id}`)}
                                >
                                  <Eye size={12} />
                                </Button>
                                <Button 
                                  variant="outline-info" 
                                  size="sm"
                                  onClick={() => handleSendMessage(teacher.id, `Message to ${teacher.name}`)}
                                >
                                  <Chat size={12} />
                                </Button>
                                <Button 
                                  variant="outline-success" 
                                  size="sm"
                                  onClick={() => navigate(`/head-teacher/staff/${teacher.id}/schedule`)}
                                >
                                  <CalendarEvent size={12} />
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
                    <PersonBadge size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No staff members found</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Academics Tab */}
      {activeTab === 'academics' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Academic Performance</h5>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <BarChart size={32} className="text-primary mb-2" />
                        <h4>Class Performance</h4>
                        {classPerformance.length > 0 ? (
                          <Table size="sm">
                            <thead>
                              <tr>
                                <th>Class</th>
                                <th>Average</th>
                                <th>Trend</th>
                              </tr>
                            </thead>
                            <tbody>
                              {classPerformance.map((classPerf, index) => (
                                <tr key={index}>
                                  <td>{classPerf.class_name}</td>
                                  <td className="fw-bold">{classPerf.average_score}%</td>
                                  <td>
                                    {classPerf.trend === 'up' ? (
                                      <TrendUp className="text-success" />
                                    ) : (
                                      <TrendDown className="text-danger" />
                                    )}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        ) : (
                          <p className="text-muted">No data available</p>
                        )}
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <Award size={32} className="text-success mb-2" />
                        <h4>Top Performers</h4>
                        {studentPerformance.filter(s => s.rank <= 5).length > 0 ? (
                          <ListGroup variant="flush">
                            {studentPerformance
                              .filter(s => s.rank <= 5)
                              .map((student, index) => (
                                <ListGroup.Item key={index}>
                                  <div className="d-flex justify-content-between">
                                    <span>{student.name}</span>
                                    <Badge bg="success">{student.grade}</Badge>
                                  </div>
                                </ListGroup.Item>
                              ))}
                          </ListGroup>
                        ) : (
                          <p className="text-muted">No top performers data</p>
                        )}
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <Book size={32} className="text-info mb-2" />
                        <h4>Subject Analysis</h4>
                        {academicResults.length > 0 ? (
                          <div className="text-start">
                            {Array.from(new Set(academicResults.map(r => r.subject_name)))
                              .slice(0, 5)
                              .map((subject, index) => {
                                const subjectResults = academicResults.filter(r => r.subject_name === subject);
                                const average = subjectResults.reduce((sum, r) => sum + (r.score || 0), 0) / subjectResults.length;
                                return (
                                  <div key={index} className="mb-2">
                                    <small>{subject}</small>
                                    <ProgressBar 
                                      now={average} 
                                      variant={getPerformanceColor(average)} 
                                      label={`${average.toFixed(1)}%`}
                                    />
                                  </div>
                                );
                              })}
                          </div>
                        ) : (
                          <p className="text-muted">No subject data</p>
                        )}
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>

                <div className="table-responsive">
                  <Table hover>
                    <thead className="table-light">
                      <tr>
                        <th>Student</th>
                        <th>Class</th>
                        <th>Term</th>
                        <th>Subject</th>
                        <th>Score</th>
                        <th>Grade</th>
                        <th>Teacher</th>
                        <th>Comments</th>
                      </tr>
                    </thead>
                    <tbody>
                      {academicResults.slice(0, 10).map((result, index) => (
                        <tr key={index}>
                          <td>{result.student_name}</td>
                          <td>{result.class_name}</td>
                          <td>{result.term}</td>
                          <td>{result.subject_name}</td>
                          <td className="fw-bold">{result.score}%</td>
                          <td>
                            <Badge bg={getPerformanceColor(result.score)}>
                              {result.grade}
                            </Badge>
                          </td>
                          <td>{result.teacher_name}</td>
                          <td>
                            <small className="text-muted">{result.comments || 'No comments'}</small>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Discipline Tab */}
      {activeTab === 'discipline' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Discipline Cases Management ({disciplineCases.length})</h5>
              </Card.Header>
              <Card.Body className="p-0">
                {disciplineCases.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Case #</th>
                          <th>Student</th>
                          <th>Class</th>
                          <th>Incident Type</th>
                          <th>Date</th>
                          <th>Reported By</th>
                          <th>Severity</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {disciplineCases.map((caseItem) => (
                          <tr key={caseItem.id}>
                            <td className="fw-semibold">{caseItem.case_number}</td>
                            <td>{caseItem.student_name}</td>
                            <td>{caseItem.class_name}</td>
                            <td>
                              <Badge bg={
                                caseItem.incident_type === 'major' ? 'danger' :
                                caseItem.incident_type === 'minor' ? 'warning' : 'info'
                              }>
                                {caseItem.incident_type}
                              </Badge>
                            </td>
                            <td>
                              <small>{formatDate(caseItem.incident_date)}</small>
                            </td>
                            <td>{caseItem.reported_by}</td>
                            <td>
                              <Badge bg={
                                caseItem.severity === 'high' ? 'danger' :
                                caseItem.severity === 'medium' ? 'warning' : 'info'
                              }>
                                {caseItem.severity}
                              </Badge>
                            </td>
                            <td>
                              <Badge bg={getStatusBadge(caseItem.status)}>
                                {caseItem.status?.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/head-teacher/discipline/${caseItem.id}`)}
                                >
                                  View
                                </Button>
                                {caseItem.status === 'pending' && (
                                  <Button 
                                    variant="success" 
                                    size="sm"
                                    onClick={() => handleResolveDisciplineCase(caseItem.id)}
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
                    <Shield size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No discipline cases reported</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Pending Tasks & Approvals ({pendingTasks.length})</h5>
              </Card.Header>
              <Card.Body>
                {pendingTasks.length > 0 ? (
                  <Accordion>
                    {pendingTasks.map((task, index) => (
                      <Accordion.Item eventKey={index.toString()} key={index}>
                        <Accordion.Header>
                          <div className="d-flex justify-content-between align-items-center w-100">
                            <div>
                              <h6 className="mb-0">{task.title}</h6>
                              <small className="text-muted">
                                Assigned to: {task.assigned_to} • Due: {formatDate(task.due_date)}
                              </small>
                            </div>
                            <Badge bg={getStatusBadge(task.priority)} className="me-2">
                              {task.priority}
                            </Badge>
                          </div>
                        </Accordion.Header>
                        <Accordion.Body>
                          <p>{task.description}</p>
                          <div className="d-flex justify-content-between align-items-center">
                            <small className="text-muted">
                              Created: {formatDateTime(task.created_at)} • 
                              Category: {task.category}
                            </small>
                            <div className="d-flex gap-2">
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => window.open(task.attachment_url, '_blank')}
                                disabled={!task.attachment_url}
                              >
                                View Attachment
                              </Button>
                              <Button 
                                variant="success" 
                                size="sm"
                                onClick={() => handleApproveTask(task.id)}
                              >
                                Approve
                              </Button>
                              <Button 
                                variant="danger" 
                                size="sm"
                                onClick={() => navigate(`/head-teacher/tasks/${task.id}/reject`)}
                              >
                                Reject
                              </Button>
                            </div>
                          </div>
                        </Accordion.Body>
                      </Accordion.Item>
                    ))}
                  </Accordion>
                ) : (
                  <div className="text-center py-5">
                    <ClipboardCheck size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No pending tasks</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Reports Tab */}
      {activeTab === 'reports' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Reports & Analytics</h5>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <FileEarmarkBarGraph size={48} className="text-primary mb-3" />
                        <h6>Academic Report</h6>
                        <p className="text-muted small">Term-wise performance analysis</p>
                        <Button 
                          variant="outline-primary" 
                          size="sm"
                          className="w-100"
                          onClick={() => navigate('/head-teacher/reports/academic')}
                        >
                          Generate
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <ClipboardCheck size={48} className="text-success mb-3" />
                        <h6>Attendance Report</h6>
                        <p className="text-muted small">Student & staff attendance analysis</p>
                        <Button 
                          variant="outline-success" 
                          size="sm"
                          className="w-100"
                          onClick={() => navigate('/head-teacher/reports/attendance')}
                        >
                          Generate
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <Shield size={48} className="text-warning mb-3" />
                        <h6>Discipline Report</h6>
                        <p className="text-muted small">Discipline cases and trends</p>
                        <Button 
                          variant="outline-warning" 
                          size="sm"
                          className="w-100"
                          onClick={() => navigate('/head-teacher/reports/discipline')}
                        >
                          Generate
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>

                {reports.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover>
                      <thead className="table-light">
                        <tr>
                          <th>Report Name</th>
                          <th>Type</th>
                          <th>Generated Date</th>
                          <th>Period</th>
                          <th>Size</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reports.map((report, index) => (
                          <tr key={index}>
                            <td className="fw-semibold">
                              {report.type.replace('_', ' ')} Report
                            </td>
                            <td>
                              <Badge bg="info">{report.type}</Badge>
                            </td>
                            <td>{formatDate(report.generated_at)}</td>
                            <td>{report.period}</td>
                            <td>
                              <small className="text-muted">{report.size || 'N/A'}</small>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => window.open(report.download_url, '_blank')}
                                >
                                  <Eye size={12} />
                                </Button>
                                <Button 
                                  variant="outline-success" 
                                  size="sm"
                                  onClick={() => window.open(report.download_url, '_blank')}
                                >
                                  <Download size={12} />
                                </Button>
                                <Button 
                                  variant="outline-info" 
                                  size="sm"
                                  onClick={() => handleSendMessage(userProfile?.id, `Sharing ${report.type} report`)}
                                >
                                  <Share size={12} />
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
                    <FileEarmarkBarGraph size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No reports generated yet</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Announcement Modal */}
      <Modal show={showAnnouncementModal} onHide={() => setShowAnnouncementModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create Announcement</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Title</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="Enter announcement title"
                value={announcementForm.title}
                onChange={(e) => setAnnouncementForm({...announcementForm, title: e.target.value})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Content</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={4}
                placeholder="Enter announcement details"
                value={announcementForm.content}
                onChange={(e) => setAnnouncementForm({...announcementForm, content: e.target.value})}
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Priority</Form.Label>
                  <Form.Select 
                    value={announcementForm.priority}
                    onChange={(e) => setAnnouncementForm({...announcementForm, priority: e.target.value})}
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Audience</Form.Label>
                  <Form.Select 
                    value={announcementForm.audience}
                    onChange={(e) => setAnnouncementForm({...announcementForm, audience: e.target.value})}
                  >
                    <option value="all">All (Students, Staff, Parents)</option>
                    <option value="students">Students Only</option>
                    <option value="staff">Staff Only</option>
                    <option value="parents">Parents Only</option>
                    <option value="teachers">Teachers Only</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAnnouncementModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateAnnouncement} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Publish Announcement'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Meeting Schedule Modal */}
      <Modal show={showMeetingModal} onHide={() => setShowMeetingModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Schedule Staff Meeting</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Meeting Title</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="Enter meeting title"
                    value={meetingForm.title}
                    onChange={(e) => setMeetingForm({...meetingForm, title: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Duration (minutes)</Form.Label>
                  <Form.Control 
                    type="number" 
                    placeholder="60"
                    value={meetingForm.duration}
                    onChange={(e) => setMeetingForm({...meetingForm, duration: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Agenda</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={3}
                placeholder="Enter meeting agenda"
                value={meetingForm.agenda}
                onChange={(e) => setMeetingForm({...meetingForm, agenda: e.target.value})}
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Date</Form.Label>
                  <Form.Control 
                    type="date"
                    value={meetingForm.date}
                    onChange={(e) => setMeetingForm({...meetingForm, date: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Time</Form.Label>
                  <Form.Control 
                    type="time"
                    value={meetingForm.time}
                    onChange={(e) => setMeetingForm({...meetingForm, time: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Location</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="Enter meeting location"
                value={meetingForm.location}
                onChange={(e) => setMeetingForm({...meetingForm, location: e.target.value})}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowMeetingModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleScheduleMeeting} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Schedule Meeting'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Report Generation Modal */}
      <Modal show={showReportModal} onHide={() => setShowReportModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Generate Report</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Report Type</Form.Label>
              <Form.Select 
                value={reportForm.type}
                onChange={(e) => setReportForm({...reportForm, type: e.target.value})}
              >
                <option value="academic">Academic Performance</option>
                <option value="attendance">Attendance Analysis</option>
                <option value="discipline">Discipline Cases</option>
                <option value="staff">Staff Performance</option>
                <option value="financial">Financial Summary</option>
                <option value="comprehensive">Comprehensive School Report</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Period</Form.Label>
              <Form.Select 
                value={reportForm.period}
                onChange={(e) => setReportForm({...reportForm, period: e.target.value})}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="term">Term</option>
                <option value="yearly">Yearly</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Format</Form.Label>
              <Form.Select 
                value={reportForm.format}
                onChange={(e) => setReportForm({...reportForm, format: e.target.value})}
              >
                <option value="pdf">PDF Document</option>
                <option value="excel">Excel Spreadsheet</option>
                <option value="word">Word Document</option>
              </Form.Select>
            </Form.Group>
            <Form.Check 
              type="checkbox"
              label="Include detailed analysis"
              checked={reportForm.includeDetails}
              onChange={(e) => setReportForm({...reportForm, includeDetails: e.target.checked})}
              className="mb-3"
            />
            <Form.Check 
              type="checkbox"
              label="Send copy to my email"
              checked={reportForm.emailCopy}
              onChange={(e) => setReportForm({...reportForm, emailCopy: e.target.checked})}
            />
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowReportModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleGenerateReport} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Generate Report'}
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
                  Head Teacher Portal v2.0 • Academic Year: {academicYear} • Term: {term}
                </small>
                <div>
                  <small className="text-muted me-3">
                    Last Refresh: {new Date(lastRefreshTime).toLocaleString()}
                  </small>
                  <small className="text-muted">
                    School Status: <Badge bg="success">Operational</Badge>
                  </small>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Custom CSS */}
      <style jsx>{`
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .bg-gradient-info {
          background: linear-gradient(135deg, #0dcaf0 0%, #0aa2c0 100%);
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
      `}</style>
    </Container>
  );
};

export default HeadTeacherPortal;