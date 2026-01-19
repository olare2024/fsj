// frontend/src/pages/Portals/CounselorPortal.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Button, 
  Badge, 
  Alert, 
  Spinner,
  Table,
  ProgressBar,
  Modal,
  Form,
  Dropdown,
  Tabs,
  Tab,
  ListGroup,
  Accordion,
  InputGroup,
  FormControl
} from 'react-bootstrap';
import { 
  Calendar, 
  Clock, 
  Person, 
  Phone, 
  Envelope, 
  Heart, 
  People, 
  FileText, 
  BarChart,
  Bell,
  Search,
  Filter,
  Plus,
  Eye,
  CheckCircle,
  ExclamationTriangle,
  Star,
  StarFill,
  ShieldCheck,
  FileEarmarkMedical,
  Lightbulb,
  ChatDots,
  Book,
  Award,
  CalendarCheck,
  CalendarEvent,
  ClockHistory,
  FileEarmarkBarGraph,
  FileEarmarkSpreadsheet,
  Download,
  Printer,
  Share,
  ThreeDotsVertical,
  ArrowClockwise,
  PersonCheck,
  PersonPlus,
  PersonX,
  HouseDoor,
  Building,
  Journal,
  JournalBookmark,
  ClipboardCheck,
  ClipboardData,
  ClipboardPlus,
  ChatSquareText,
  CalendarEventFill,
  
} from 'react-bootstrap-icons';
import { AuthProvider, useAuth } from '/src/context/AuthContext.jsx';  // ✅ Correct
import counselingAPI  from '../../services/counselingAPI';
import { academicsAPI } from '../../services/academicAPI';
import { format } from 'date-fns';

const CounselorPortal = () => {
  const { currentUser, loading: authLoading } = useAuth();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Data states
  const [stats, setStats] = useState({
    activeCases: 0,
    sessionsToday: 0,
    pendingFollowups: 0,
    studentsHelped: 0,
    upcomingAppointments: 0,
    crisisCases: 0
  });
  
  const [todaysAppointments, setTodaysAppointments] = useState([]);
  const [upcomingAppointments, setUpcomingAppointments] = useState([]);
  const [activeStudents, setActiveStudents] = useState([]);
  const [recentSessions, setRecentSessions] = useState([]);
  const [emergencyCases, setEmergencyCases] = useState([]);
  const [weeklySchedule, setWeeklySchedule] = useState([]);
  const [counselingResources, setCounselingResources] = useState([]);
  const [studentNotes, setStudentNotes] = useState([]);
  
  // Modal states
  const [showAppointmentModal, setShowAppointmentModal] = useState(false);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [showStudentModal, setShowStudentModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  
  // Form states
  const [newAppointment, setNewAppointment] = useState({
    studentId: '',
    studentName: '',
    date: format(new Date(), 'yyyy-MM-dd'),
    time: format(new Date().setHours(9, 0), 'HH:mm'),
    reason: '',
    type: 'regular',
    urgency: 'medium',
    notes: ''
  });
  
  const [sessionNotes, setSessionNotes] = useState({
    studentId: '',
    sessionDate: format(new Date(), 'yyyy-MM-dd'),
    sessionType: 'individual',
    concerns: [],
    discussionPoints: '',
    actionPlan: '',
    followupDate: '',
    recommendations: '',
    confidentiality: 'confidential'
  });
  
  // Filter states
  const [filters, setFilters] = useState({
    status: 'all',
    urgency: 'all',
    timeRange: 'today',
    category: 'all'
  });
  
  // Search state
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch all counseling data
  const fetchCounselingData = useCallback(async (silentRefresh = false) => {
    try {
      if (!silentRefresh) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      setError('');

      // Fetch all data in parallel for better performance
      const [
        statsData,
        todaysAppts,
        upcomingAppts,
        activeStudentsData,
        recentSessionsData,
        emergencyData,
        weeklyData,
        resourcesData
      ] = await Promise.all([
        counselingAPI.getCounselorStats(),
        counselingAPI.getTodaysAppointments(),
        counselingAPI.getUpcomingAppointments(),
        counselingAPI.getActiveStudents(),
        counselingAPI.getRecentSessions(),
        counselingAPI.getEmergencyCases(),
        counselingAPI.getWeeklySchedule(),
        counselingAPI.getCounselingResources()
      ]);

      // Update state with fetched data
      if (statsData.success) {
        setStats(statsData.data);
      }

      if (todaysAppts.success) {
        setTodaysAppointments(todaysAppts.data);
      }

      if (upcomingAppts.success) {
        setUpcomingAppointments(upcomingAppts.data);
      }

      if (activeStudentsData.success) {
        setActiveStudents(activeStudentsData.data);
      }

      if (recentSessionsData.success) {
        setRecentSessions(recentSessionsData.data);
      }

      if (emergencyData.success) {
        setEmergencyCases(emergencyData.data);
      }

      if (weeklyData.success) {
        setWeeklySchedule(weeklyData.data);
      }

      if (resourcesData.success) {
        setCounselingResources(resourcesData.data);
      }

    } catch (err) {
      console.error('Error fetching counseling data:', err);
      setError('Failed to load counseling data. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading && currentUser) {
      fetchCounselingData();
    }
  }, [authLoading, currentUser, fetchCounselingData]);

  const handleRefresh = () => {
    fetchCounselingData(true);
  };

  const handleCreateAppointment = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const result = await counselingAPI.createAppointment(newAppointment);
      
      if (result.success) {
        setSuccess('Appointment scheduled successfully!');
        setShowAppointmentModal(false);
        setNewAppointment({
          studentId: '',
          studentName: '',
          date: format(new Date(), 'yyyy-MM-dd'),
          time: format(new Date().setHours(9, 0), 'HH:mm'),
          reason: '',
          type: 'regular',
          urgency: 'medium',
          notes: ''
        });
        fetchCounselingData(true);
      } else {
        setError(result.message || 'Failed to schedule appointment');
      }
    } catch (err) {
      setError('Failed to schedule appointment');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSessionNotes = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const result = await counselingAPI.addSessionNotes(sessionNotes);
      
      if (result.success) {
        setSuccess('Session notes added successfully!');
        setShowSessionModal(false);
        setSessionNotes({
          studentId: '',
          sessionDate: format(new Date(), 'yyyy-MM-dd'),
          sessionType: 'individual',
          concerns: [],
          discussionPoints: '',
          actionPlan: '',
          followupDate: '',
          recommendations: '',
          confidentiality: 'confidential'
        });
        fetchCounselingData(true);
      } else {
        setError(result.message || 'Failed to add session notes');
      }
    } catch (err) {
      setError('Failed to add session notes');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkEmergency = async (studentId, isEmergency) => {
    try {
      setLoading(true);
      const result = await counselingAPI.markEmergency(studentId, isEmergency);
      
      if (result.success) {
        setSuccess(isEmergency ? 'Marked as emergency case' : 'Removed from emergency cases');
        fetchCounselingData(true);
      } else {
        setError(result.message || 'Failed to update emergency status');
      }
    } catch (err) {
      setError('Failed to update emergency status');
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async (reportType) => {
    try {
      setLoading(true);
      const result = await counselingAPI.exportReport(reportType);
      
      if (result.success && result.data) {
        // Create download link
        const url = window.URL.createObjectURL(new Blob([result.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `counseling_report_${reportType}_${format(new Date(), 'yyyy-MM-dd')}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        setSuccess(`${reportType} report exported successfully`);
      }
    } catch (err) {
      setError('Failed to export report');
    } finally {
      setLoading(false);
    }
  };

  const handleSendReminder = async (appointmentId) => {
    try {
      setLoading(true);
      const result = await counselingAPI.sendReminder(appointmentId);
      
      if (result.success) {
        setSuccess('Reminder sent successfully!');
      } else {
        setError(result.message || 'Failed to send reminder');
      }
    } catch (err) {
      setError('Failed to send reminder');
    } finally {
      setLoading(false);
    }
  };

  const handleRescheduleAppointment = async (appointmentId, newDate, newTime) => {
    try {
      setLoading(true);
      const result = await counselingAPI.rescheduleAppointment(appointmentId, {
        newDate,
        newTime
      });
      
      if (result.success) {
        setSuccess('Appointment rescheduled successfully!');
        fetchCounselingData(true);
      } else {
        setError(result.message || 'Failed to reschedule appointment');
      }
    } catch (err) {
      setError('Failed to reschedule appointment');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId, reason) => {
    try {
      setLoading(true);
      const result = await counselingAPI.cancelAppointment(appointmentId, reason);
      
      if (result.success) {
        setSuccess('Appointment cancelled successfully!');
        fetchCounselingData(true);
      } else {
        setError(result.message || 'Failed to cancel appointment');
      }
    } catch (err) {
      setError('Failed to cancel appointment');
    } finally {
      setLoading(false);
    }
  };

  // Utility functions
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return format(new Date(dateString), 'MMM dd, yyyy');
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    return format(new Date(`2000-01-01T${timeString}`), 'hh:mm a');
  };

  const formatDateTime = (dateString, timeString) => {
    if (!dateString || !timeString) return 'N/A';
    return format(new Date(`${dateString}T${timeString}`), 'MMM dd, yyyy hh:mm a');
  };

  const getStatusBadge = (status) => {
    const variants = {
      'scheduled': 'primary',
      'confirmed': 'success',
      'pending': 'warning',
      'cancelled': 'danger',
      'completed': 'info',
      'active': 'success',
      'followup': 'warning',
      'resolved': 'success',
      'urgent': 'danger',
      'emergency': 'danger',
      'high': 'danger',
      'medium': 'warning',
      'low': 'info'
    };
    
    return variants[status] || 'secondary';
  };

  const getUrgencyIcon = (urgency) => {
    const icons = {
      'emergency': <ExclamationTriangle className="text-danger" />,
      'high': <ExclamationTriangle className="text-warning" />,
      'medium': <Clock className="text-info" />,
      'low': <CheckCircle className="text-success" />
    };
    
    return icons[urgency] || <Clock className="text-secondary" />;
  };

  const getSessionTypeIcon = (type) => {
    const icons = {
      'individual': <Person />,
      'group': <People />,
      'crisis': <ExclamationTriangle />,
      'academic': <Book />,
      'career': <Award />,
      'family': <HouseDoor />
    };
    
    return icons[type] || <ChatDots />;
  };

  // Quick actions
  const quickActions = [
    {
      title: 'New Appointment',
      description: 'Schedule new counseling session',
      icon: <CalendarCheck size={24} />,
      action: () => setShowAppointmentModal(true),
      color: 'primary',
      variant: 'outline-primary'
    },
    {
      title: 'Session Notes',
      description: 'Add session notes and follow-up',
      icon: <ClipboardPlus size={24} />,
      action: () => setShowSessionModal(true),
      color: 'success',
      variant: 'outline-success'
    },
    {
      title: 'Student Profiles',
      description: 'View and manage student records',
      icon: <PersonCheck size={24} />,
      action: () => setShowStudentModal(true),
      color: 'info',
      variant: 'outline-info'
    },
    {
      title: 'Generate Report',
      description: 'Create counseling reports',
      icon: <FileEarmarkBarGraph size={24} />,
      action: () => setShowReportModal(true),
      color: 'warning',
      variant: 'outline-warning'
    },
    {
      title: 'Emergency Cases',
      description: 'Manage urgent counseling needs',
      icon: <Bell size={24} />,
      action: () => navigate('/counseling/emergency'),
      color: 'danger',
      variant: 'outline-danger'
    },
    {
      title: 'Resources',
      description: 'Access counseling materials',
      icon: <FileEarmarkMedical size={24} />,
      action: () => navigate('/counseling/resources'),
      color: 'secondary',
      variant: 'outline-secondary'
    }
  ];

  // Emergency resources
  const emergencyResources = [
    {
      title: 'Crisis Helpline',
      contact: '1-800-HELP-NOW',
      description: '24/7 Crisis Support',
      icon: <Phone className="text-danger" size={24} />,
      color: 'danger'
    },
    {
      title: 'Student Support',
      contact: 'support@delvok.ac.ke',
      description: 'Email Support Team',
      icon: <Envelope className="text-primary" size={24} />,
      color: 'primary'
    },
    {
      title: 'Health Services',
      contact: 'health@delvok.ac.ke',
      description: 'Medical & Psychological Support',
      icon: <Heart className="text-success" size={24} />,
      color: 'success'
    },
    {
      title: 'Academic Support',
      contact: 'academic@delvok.ac.ke',
      description: 'Academic Counseling',
      icon: <Book className="text-info" size={24} />,
      color: 'info'
    }
  ];

  // Filter appointments based on search and filters
  const filteredAppointments = todaysAppointments.filter(appointment => {
    if (searchTerm && !appointment.studentName.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !appointment.reason.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    if (filters.status !== 'all' && appointment.status !== filters.status) {
      return false;
    }
    
    if (filters.urgency !== 'all' && appointment.urgency !== filters.urgency) {
      return false;
    }
    
    if (filters.category !== 'all' && appointment.type !== filters.category) {
      return false;
    }
    
    return true;
  });

  if (authLoading || loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '70vh' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" size="lg" />
          <p className="mt-3 text-muted">Loading Counselor Portal...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      {/* Header Section */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 bg-gradient-counselor text-white shadow">
            <Card.Body className="py-4">
              <Row className="align-items-center">
                <Col md={8}>
                  <div className="d-flex align-items-center">
                    <div className="me-4">
                      <div 
                        className="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow"
                        style={{ width: 80, height: 80 }}
                      >
                        <Heart size={32} className="text-white" />
                      </div>
                    </div>
                    <div>
                      <h1 className="h2 mb-1">Counselor Portal</h1>
                      <p className="mb-1 opacity-75">
                        Welcome, {currentUser?.first_name || 'Counselor'}! Supporting student wellbeing and success.
                      </p>
                      <small className="opacity-75">
                        {refreshing ? '🔄 Refreshing data...' : `Last updated: ${format(new Date(), 'hh:mm a')}`}
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
                      className="text-primary"
                    >
                      <ArrowClockwise className={`me-2 ${refreshing ? 'spinning' : ''}`} size={16} />
                      Refresh
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-primary"
                      onClick={() => setShowAppointmentModal(true)}
                    >
                      <Plus className="me-2" />
                      New Appointment
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
        <Alert variant="danger" dismissible onClose={() => setError('')} className="mb-4">
          <ExclamationTriangle className="me-2" />
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')} className="mb-4">
          <CheckCircle className="me-2" />
          {success}
        </Alert>
      )}

      {/* Counseling Statistics */}
      <Row className="mb-4">
        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Active Cases</h6>
                  <h2 className="mb-0 text-primary">{stats.activeCases}</h2>
                  <small className="text-muted">Students currently receiving support</small>
                </div>
                <div className="bg-primary bg-opacity-10 p-3 rounded">
                  <People size={24} className="text-primary" />
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
                  <h6 className="card-title text-uppercase text-muted mb-2">Sessions Today</h6>
                  <h2 className="mb-0 text-success">{stats.sessionsToday}</h2>
                  <small className="text-muted">Appointments scheduled</small>
                </div>
                <div className="bg-success bg-opacity-10 p-3 rounded">
                  <CalendarCheck size={24} className="text-success" />
                </div>
              </div>
              {stats.sessionsToday > 0 && (
                <Button 
                  variant="success" 
                  size="sm" 
                  className="mt-2 w-100"
                  onClick={() => document.getElementById('todays-appointments').scrollIntoView()}
                >
                  View Schedule
                </Button>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Pending Follow-ups</h6>
                  <h2 className="mb-0 text-warning">{stats.pendingFollowups}</h2>
                  <small className="text-muted">Requiring follow-up action</small>
                </div>
                <div className="bg-warning bg-opacity-10 p-3 rounded">
                  <ClockHistory size={24} className="text-warning" />
                </div>
              </div>
              {stats.pendingFollowups > 0 && (
                <Button 
                  variant="warning" 
                  size="sm" 
                  className="mt-2 w-100"
                  onClick={() => setFilters({...filters, status: 'followup'})}
                >
                  Review Follow-ups
                </Button>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Emergency Cases</h6>
                  <h2 className="mb-0 text-danger">{stats.crisisCases}</h2>
                  <small className="text-muted">Urgent attention needed</small>
                </div>
                <div className="bg-danger bg-opacity-10 p-3 rounded">
                  <Bell size={24} className="text-danger" />
                </div>
              </div>
              {stats.crisisCases > 0 && (
                <Button 
                  variant="danger" 
                  size="sm" 
                  className="mt-2 w-100"
                  onClick={() => navigate('/counseling/emergency')}
                >
                  View Emergency Cases
                </Button>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <Row className="g-3">
                {quickActions.map((action, index) => (
                  <Col md={4} lg={2} key={index}>
                    <Button 
                      variant={action.variant}
                      className="w-100 h-100 py-3 d-flex flex-column align-items-center"
                      onClick={action.action}
                    >
                      <div className="mb-2">{action.icon}</div>
                      <div className="fw-bold">{action.title}</div>
                      <small className="text-muted text-center">{action.description}</small>
                    </Button>
                  </Col>
                ))}
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4">
        {/* Today's Appointments */}
        <Col xl={6} lg={12}>
          <Card className="border-0 shadow-sm h-100" id="todays-appointments">
            <Card.Header className="bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Today's Appointments</h5>
                <Badge bg="primary" pill>{filteredAppointments.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <InputGroup>
                  <InputGroup.Text>
                    <Search />
                  </InputGroup.Text>
                  <FormControl
                    placeholder="Search appointments..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </InputGroup>
              </div>

              <div className="d-flex flex-wrap gap-2 mb-3">
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm">
                    <Filter className="me-1" />
                    Status: {filters.status === 'all' ? 'All' : filters.status}
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item onClick={() => setFilters({...filters, status: 'all'})}>
                      All Statuses
                    </Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={() => setFilters({...filters, status: 'confirmed'})}>
                      Confirmed
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => setFilters({...filters, status: 'pending'})}>
                      Pending
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => setFilters({...filters, status: 'cancelled'})}>
                      Cancelled
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>

                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm">
                    {getUrgencyIcon(filters.urgency)}
                    <span className="ms-1">
                      Urgency: {filters.urgency === 'all' ? 'All' : filters.urgency}
                    </span>
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item onClick={() => setFilters({...filters, urgency: 'all'})}>
                      All Urgency Levels
                    </Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={() => setFilters({...filters, urgency: 'emergency'})}>
                      Emergency
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => setFilters({...filters, urgency: 'high'})}>
                      High
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => setFilters({...filters, urgency: 'medium'})}>
                      Medium
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => setFilters({...filters, urgency: 'low'})}>
                      Low
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>

              {filteredAppointments.length > 0 ? (
                <div className="list-group list-group-flush">
                  {filteredAppointments.map((appointment, index) => (
                    <div key={index} className="list-group-item border-0 px-0 py-3">
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="d-flex align-items-start">
                          <div className="me-3">
                            <div className="bg-primary bg-opacity-10 p-2 rounded">
                              {getSessionTypeIcon(appointment.type)}
                            </div>
                          </div>
                          <div>
                            <h6 className="mb-1">{appointment.studentName}</h6>
                            <small className="text-muted d-block">
                              <Clock size={12} className="me-1" />
                              {formatTime(appointment.time)} • {appointment.grade || 'N/A'}
                            </small>
                            <p className="mb-1 small">{appointment.reason}</p>
                            <div className="d-flex gap-1 mt-1">
                              <Badge bg={getStatusBadge(appointment.status)}>
                                {appointment.status}
                              </Badge>
                              <Badge bg={getStatusBadge(appointment.urgency)}>
                                {appointment.urgency}
                              </Badge>
                              <Badge bg="info">
                                {appointment.type}
                              </Badge>
                            </div>
                          </div>
                        </div>
                        <div className="d-flex flex-column gap-1">
                          <Button 
                            size="sm" 
                            variant="outline-primary"
                            onClick={() => handleSendReminder(appointment.id)}
                          >
                            <Bell size={12} />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline-success"
                            onClick={() => setShowSessionModal(true)}
                          >
                            <FileText size={12} />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <Calendar size={48} className="text-muted mb-3" />
                  <p className="text-muted mb-0">No appointments scheduled for today</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Active Students & Emergency Resources */}
        <Col xl={6} lg={12}>
          <Row className="g-4">
            {/* Active Students */}
            <Col md={6}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">Active Students</h5>
                    <Badge bg="success" pill>{activeStudents.length}</Badge>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  <div className="list-group list-group-flush">
                    {activeStudents.slice(0, 5).map((student, index) => (
                      <div key={index} className="list-group-item border-0 px-3 py-2">
                        <div className="d-flex align-items-center">
                          <div className="me-3">
                            <div className="rounded-circle bg-primary bg-opacity-10 p-2">
                              <Person size={16} className="text-primary" />
                            </div>
                          </div>
                          <div className="flex-grow-1">
                            <div className="d-flex justify-content-between align-items-center">
                              <h6 className="mb-0">{student.name}</h6>
                              <Badge bg={getStatusBadge(student.status)}>
                                {student.status}
                              </Badge>
                            </div>
                            <small className="text-muted d-block">
                              {student.grade} • Last: {formatDate(student.lastSessionDate)}
                            </small>
                            <small className="text-muted">
                              {student.primaryConcern || 'No specific concern noted'}
                            </small>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    variant="link" 
                    size="sm" 
                    className="text-decoration-none w-100 text-center"
                    onClick={() => setShowStudentModal(true)}
                  >
                    View All Students
                    <Eye className="ms-1" size={14} />
                  </Button>
                </Card.Footer>
              </Card>
            </Col>

            {/* Emergency Resources */}
            <Col md={6}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0 text-danger">Emergency Resources</h5>
                    <ExclamationTriangle className="text-danger" />
                  </div>
                </Card.Header>
                <Card.Body>
                  <div className="row g-3">
                    {emergencyResources.map((resource, index) => (
                      <Col xs={12} key={index}>
                        <div className={`border-start border-${resource.color} border-3 ps-3 py-2`}>
                          <div className="d-flex align-items-center mb-1">
                            {resource.icon}
                            <h6 className="ms-2 mb-0">{resource.title}</h6>
                          </div>
                          <p className="fw-bold mb-1">{resource.contact}</p>
                          <small className="text-muted">{resource.description}</small>
                        </div>
                      </Col>
                    ))}
                  </div>
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Alert variant="danger" className="p-2 mb-0">
                    <div className="d-flex align-items-center">
                      <ExclamationTriangle className="me-2" />
                      <small className="fw-bold">For immediate crisis: Call 911 or emergency services</small>
                    </div>
                  </Alert>
                </Card.Footer>
              </Card>
            </Col>

            {/* Recent Sessions */}
            <Col md={12}>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">Recent Sessions</h5>
                    <Button 
                      size="sm" 
                      variant="outline-primary"
                      onClick={() => setShowSessionModal(true)}
                    >
                      <Plus size={12} className="me-1" />
                      Add Notes
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  <Table hover className="mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Student</th>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentSessions.slice(0, 4).map((session, index) => (
                        <tr key={index}>
                          <td>
                            <div className="d-flex align-items-center">
                              <Person size={16} className="me-2 text-muted" />
                              {session.studentName}
                            </div>
                          </td>
                          <td>
                            <small>{formatDate(session.sessionDate)}</small>
                          </td>
                          <td>
                            <Badge bg="info">{session.sessionType}</Badge>
                          </td>
                          <td>
                            <Badge bg={getStatusBadge(session.status)}>
                              {session.status}
                            </Badge>
                          </td>
                          <td>
                            <Button 
                              size="sm" 
                              variant="outline-primary"
                              onClick={() => {/* View session details */}}
                            >
                              <Eye size={12} />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>

      {/* Weekly Schedule */}
      <Row className="mt-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Weekly Schedule</h5>
            </Card.Header>
            <Card.Body>
              <Row className="g-3">
                {weeklySchedule.map((day, index) => (
                  <Col key={index} xs={12} sm={6} md={2.4} className="mb-3">
                    <Card 
                      className={`h-100 border-0 ${day.sessions > 0 ? 'bg-primary bg-opacity-10' : 'bg-light'}`}
                    >
                      <Card.Body className="text-center">
                        <h6 className="mb-2">{day.day}</h6>
                        <h2 className={`mb-2 ${day.sessions > 0 ? 'text-primary' : 'text-muted'}`}>
                          {day.sessions}
                        </h2>
                        <p className="mb-0 text-muted">Sessions</p>
                        {day.notes && (
                          <small className="text-muted d-block mt-1">{day.notes}</small>
                        )}
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Counseling Resources */}
      <Row className="mt-4">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Counseling Resources</h5>
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm">
                    <Download className="me-1" />
                    Download
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item onClick={() => handleExportReport('monthly')}>
                      Monthly Report
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => handleExportReport('student_cases')}>
                      Student Cases
                    </Dropdown.Item>
                    <Dropdown.Item onClick={() => handleExportReport('session_summary')}>
                      Session Summary
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </Card.Header>
            <Card.Body>
              <Row className="g-3">
                {counselingResources.slice(0, 4).map((resource, index) => (
                  <Col md={3} key={index}>
                    <Card className="h-100 border">
                      <Card.Body className="text-center">
                        <div className="mb-3">
                          {resource.type === 'guide' && <FileEarmarkMedical size={32} className="text-primary" />}
                          {resource.type === 'template' && <FileText size={32} className="text-success" />}
                          {resource.type === 'form' && <ClipboardData size={32} className="text-warning" />}
                          {resource.type === 'reference' && <Book size={32} className="text-info" />}
                        </div>
                        <h6>{resource.title}</h6>
                        <p className="text-muted small mb-2">{resource.description}</p>
                        <Button 
                          variant="outline-primary" 
                          size="sm" 
                          className="w-100"
                          onClick={() => window.open(resource.url, '_blank')}
                        >
                          Access Resource
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Footer */}
      <Row className="mt-4">
        <Col>
          <Card className="border-0 bg-light">
            <Card.Body className="py-2">
              <div className="d-flex justify-content-between align-items-center flex-wrap">
                <small className="text-muted">
                  Counselor Portal v2.0 • Total Students Helped: {stats.studentsHelped}
                </small>
                <div>
                  <small className="text-muted me-3">
                    Last Updated: {format(new Date(), 'PPpp')}
                  </small>
                  <small className="text-success">
                    <CheckCircle size={12} className="me-1" />
                    System Active
                  </small>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Create Appointment Modal */}
      <Modal show={showAppointmentModal} onHide={() => setShowAppointmentModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Schedule New Appointment</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCreateAppointment}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Student</Form.Label>
                  <Form.Select 
                    value={newAppointment.studentId}
                    onChange={(e) => {
                      const student = activeStudents.find(s => s.id === e.target.value);
                      setNewAppointment({
                        ...newAppointment,
                        studentId: e.target.value,
                        studentName: student ? student.name : ''
                      });
                    }}
                    required
                  >
                    <option value="">Select a student</option>
                    {activeStudents.map((student) => (
                      <option key={student.id} value={student.id}>
                        {student.name} - {student.grade}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Session Type</Form.Label>
                  <Form.Select 
                    value={newAppointment.type}
                    onChange={(e) => setNewAppointment({...newAppointment, type: e.target.value})}
                  >
                    <option value="regular">Regular Session</option>
                    <option value="academic">Academic Counseling</option>
                    <option value="career">Career Guidance</option>
                    <option value="crisis">Crisis Intervention</option>
                    <option value="group">Group Session</option>
                    <option value="family">Family Counseling</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={newAppointment.date}
                    onChange={(e) => setNewAppointment({...newAppointment, date: e.target.value})}
                    min={format(new Date(), 'yyyy-MM-dd')}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Time</Form.Label>
                  <Form.Control
                    type="time"
                    value={newAppointment.time}
                    onChange={(e) => setNewAppointment({...newAppointment, time: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Reason for Session</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Brief description of the counseling needs..."
                value={newAppointment.reason}
                onChange={(e) => setNewAppointment({...newAppointment, reason: e.target.value})}
                required
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Urgency Level</Form.Label>
                  <Form.Select 
                    value={newAppointment.urgency}
                    onChange={(e) => setNewAppointment({...newAppointment, urgency: e.target.value})}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="emergency">Emergency</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Additional Notes</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Any special considerations..."
                    value={newAppointment.notes}
                    onChange={(e) => setNewAppointment({...newAppointment, notes: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowAppointmentModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? 'Scheduling...' : 'Schedule Appointment'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Add Session Notes Modal */}
      <Modal show={showSessionModal} onHide={() => setShowSessionModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Add Session Notes</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleAddSessionNotes}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Student</Form.Label>
                  <Form.Select 
                    value={sessionNotes.studentId}
                    onChange={(e) => setSessionNotes({...sessionNotes, studentId: e.target.value})}
                    required
                  >
                    <option value="">Select a student</option>
                    {activeStudents.map((student) => (
                      <option key={student.id} value={student.id}>
                        {student.name} - {student.grade}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Session Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={sessionNotes.sessionDate}
                    onChange={(e) => setSessionNotes({...sessionNotes, sessionDate: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Session Type</Form.Label>
                  <Form.Select 
                    value={sessionNotes.sessionType}
                    onChange={(e) => setSessionNotes({...sessionNotes, sessionType: e.target.value})}
                  >
                    <option value="individual">Individual</option>
                    <option value="group">Group</option>
                    <option value="family">Family</option>
                    <option value="crisis">Crisis</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Confidentiality Level</Form.Label>
                  <Form.Select 
                    value={sessionNotes.confidentiality}
                    onChange={(e) => setSessionNotes({...sessionNotes, confidentiality: e.target.value})}
                  >
                    <option value="confidential">Confidential</option>
                    <option value="restricted">Restricted</option>
                    <option value="shared">Shared (with consent)</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Discussion Points</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Key points discussed during the session..."
                value={sessionNotes.discussionPoints}
                onChange={(e) => setSessionNotes({...sessionNotes, discussionPoints: e.target.value})}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Action Plan</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                placeholder="Recommended actions and next steps..."
                value={sessionNotes.actionPlan}
                onChange={(e) => setSessionNotes({...sessionNotes, actionPlan: e.target.value})}
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Follow-up Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={sessionNotes.followupDate}
                    onChange={(e) => setSessionNotes({...sessionNotes, followupDate: e.target.value})}
                    min={format(new Date(), 'yyyy-MM-dd')}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Recommendations</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Academic, personal, or professional recommendations..."
                    value={sessionNotes.recommendations}
                    onChange={(e) => setSessionNotes({...sessionNotes, recommendations: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowSessionModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save Session Notes'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Custom CSS */}
      <style jsx>{`
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .bg-gradient-counselor {
          background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%);
        }
      `}</style>
    </Container>
  );
};

export default CounselorPortal;