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
  Nav,
  Image,
  ListGroup,
  Tabs,
  Tab,
  Modal,
  Form
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  People, 
  Book, 
  CalendarCheck, 
  CreditCard, 
  Clock, 
  Chat, 
  CalendarEvent, 
  GraphUp,
  ArrowClockwise,
  PersonCircle,
  Download,
  Bell,
  ExclamationTriangle,
  CheckCircle,
  FileText,
  Award,
  BarChart,
  Receipt,
  Mailbox,
  Phone,
  FileEarmarkText,
  FileEarmarkBarGraph,
  PersonBadge,
  ClockHistory,
  FileEarmarkArrowDown,
  FileEarmarkCheck,
  ShieldCheck,
  Wallet,
  Journal
} from 'react-bootstrap-icons';

// Import APIs
import authAPI from '../../services/authAPI';
import {parentAPI} from '../../services/parentAPI';
import { academicAPI } from '../../services/academicAPI';
import { attendanceAPI } from '../../services/attendanceAPI';
import {financeAPI} from '../../services/financeAPI';
import { assignmentsAPI } from '../../services/assignmentsAPI';
import timetableAPI from '../../services/timetableAPI';
import downloadsAPI from '../../services/downloadsAPI';

const ParentPortal = () => {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // State for parent data
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [academicProgress, setAcademicProgress] = useState({});
  const [attendanceData, setAttendanceData] = useState({});
  const [feeData, setFeeData] = useState({});
  const [timetable, setTimetable] = useState([]);
  const [schoolEvents, setSchoolEvents] = useState([]);
  const [teacherCommunications, setTeacherCommunications] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [recentAssignments, setRecentAssignments] = useState([]);
  const [studentPortfolio, setStudentPortfolio] = useState({});
  const [emergencyContacts, setEmergencyContacts] = useState([]);
  const [parentPreferences, setParentPreferences] = useState({});
  
  // Modal states
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [showMeetingModal, setShowMeetingModal] = useState(false);
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  
  // Stats
  const [stats, setStats] = useState({
    totalChildren: 0,
    averageGrade: 0,
    attendanceRate: 0,
    pendingFees: 0,
    totalNotifications: 0,
    pendingAssignments: 0,
    upcomingEvents: 0,
    unreadMessages: 0
  });

  const [userProfile, setUserProfile] = useState(null);

  // Helper for error handling
  const handleAPIError = (error, context = '') => {
    console.error(`Parent API Error (${context}):`, error);
    return {
      success: false,
      message: error.response?.data?.error || error.message || 'An error occurred'
    };
  };

  // Fetch all parent data
  const fetchParentData = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');

      // 1. Get parent profile
      const profileResult = await authAPI.getCurrentUser();
      if (profileResult.success) {
        setUserProfile(profileResult.user || profileResult.data);
      }

      // 2. Get children
      const childrenResult = await parentAPI.getChildren();
      if (childrenResult.success) {
        const childrenData = childrenResult.data?.children || childrenResult.data || [];
        setChildren(childrenData);
        if (childrenData.length > 0 && !selectedChild) {
          setSelectedChild(childrenData[0]);
        }
      }

      // 3. If child is selected, fetch child-specific data
      if (selectedChild) {
        const childId = selectedChild.id || selectedChild.student_id;
        
        // Fetch child academic progress
        const progressResult = await parentAPI.getChildPerformance(childId);
        if (progressResult.success) {
          setAcademicProgress(progressResult.data);
        }

        // Fetch attendance
        const attendanceResult = await parentAPI.getChildAttendance(childId);
        if (attendanceResult.success) {
          setAttendanceData(attendanceResult.data);
        }

        // Fetch fee information
        const feesResult = await parentAPI.getChildFees(childId);
        if (feesResult.success) {
          setFeeData(feesResult.data);
        }

        // Fetch timetable
        const timetableResult = await parentAPI.getChildTimetable(childId);
        if (timetableResult.success) {
          setTimetable(timetableResult.data?.timetable || timetableResult.data || []);
        }

        // Fetch assignments
        const assignmentsResult = await parentAPI.getChildAssignments(childId);
        if (assignmentsResult.success) {
          setRecentAssignments(assignmentsResult.data?.assignments || assignmentsResult.data || []);
        }

        // Fetch child's teachers
        const teachersResult = await parentAPI.getChildTeachers(childId);
        if (teachersResult.success) {
          // Store teachers for messaging
          setTeacherCommunications(teachersResult.data?.teachers || teachersResult.data || []);
        }

        // Fetch child portfolio
        const portfolioResult = await parentAPI.getChildProgressReports(childId);
        if (portfolioResult.success) {
          setStudentPortfolio(portfolioResult.data);
        }
      }

      // 4. Fetch school events
      const eventsResult = await parentAPI.getChildEvents(selectedChild?.id);
      if (eventsResult.success) {
        setSchoolEvents(eventsResult.data?.events || eventsResult.data || []);
      }

      // 5. Fetch notifications
      const notificationsResult = await parentAPI.getNotifications();
      if (notificationsResult.success) {
        setNotifications(notificationsResult.data?.notifications || notificationsResult.data || []);
      }

      // 6. Fetch emergency contacts
      const contactsResult = await parentAPI.getEmergencyContacts();
      if (contactsResult.success) {
        setEmergencyContacts(contactsResult.data?.contacts || contactsResult.data || []);
      }

      // 7. Fetch preferences
      const preferencesResult = await parentAPI.getPreferences();
      if (preferencesResult.success) {
        setParentPreferences(preferencesResult.data?.preferences || preferencesResult.data || {});
      }

      // 8. Calculate statistics
      const totalChildren = children.length;
      const averageGrade = academicProgress.average_score || 0;
      const attendanceRate = attendanceData.attendance_rate || 0;
      const pendingFees = feeData.pending_amount || 0;
      const totalNotifications = notifications.filter(n => !n.read).length;
      const pendingAssignments = recentAssignments.filter(a => 
        a.status === 'pending' || a.status === 'submitted'
      ).length;
      const upcomingEvents = schoolEvents.filter(e => 
        new Date(e.date || e.start_date) > new Date()
      ).length;
      const unreadMessages = teacherCommunications.filter(c => !c.read).length;

      setStats({
        totalChildren,
        averageGrade,
        attendanceRate,
        pendingFees,
        totalNotifications,
        pendingAssignments,
        upcomingEvents,
        unreadMessages
      });

    } catch (err) {
      setError('Failed to load parent data. Please try again.');
      console.error('Error fetching parent data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [selectedChild, children.length]);

  useEffect(() => {
    if (!authLoading && currentUser) {
      fetchParentData();
    }
  }, [authLoading, currentUser, fetchParentData]);

  // Handle child selection
  const handleChildSelect = (child) => {
    setSelectedChild(child);
  };

  // Refresh function
  const handleRefresh = () => {
    fetchParentData(true);
  };

  // Send message to teacher
  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedTeacher) return;

    try {
      setLoading(true);
      const result = await parentAPI.sendMessageToTeacher(
        selectedChild.id, 
        {
          teacher_id: selectedTeacher.id,
          message: newMessage,
          priority: 'normal'
        }
      );

      if (result.success) {
        setSuccess('Message sent successfully!');
        setNewMessage('');
        setShowMessageModal(false);
        setSelectedTeacher(null);
      } else {
        setError(result.error?.message || 'Failed to send message');
      }
    } catch (err) {
      setError('Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  // Schedule meeting
  const handleScheduleMeeting = async (meetingData) => {
    try {
      setLoading(true);
      const result = await parentAPI.scheduleMeeting(meetingData);
      
      if (result.success) {
        setSuccess('Meeting scheduled successfully!');
        setShowMeetingModal(false);
      } else {
        setError(result.error?.message || 'Failed to schedule meeting');
      }
    } catch (err) {
      setError('Failed to schedule meeting');
    } finally {
      setLoading(false);
    }
  };

  // Mark notification as read
  const handleMarkNotificationRead = async (notificationId) => {
    try {
      const result = await parentAPI.markNotificationAsRead(notificationId);
      if (result.success) {
        setNotifications(prev => 
          prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
        );
      }
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  // Update preferences
  const handleUpdatePreferences = async (updates) => {
    try {
      setLoading(true);
      const result = await parentAPI.updatePreferences(updates);
      
      if (result.success) {
        setSuccess('Preferences updated successfully!');
        setParentPreferences(prev => ({ ...prev, ...updates }));
      } else {
        setError(result.error?.message || 'Failed to update preferences');
      }
    } catch (err) {
      setError('Failed to update preferences');
    } finally {
      setLoading(false);
    }
  };

  // Export child report
  const handleExportReport = async (reportType) => {
    try {
      setLoading(true);
      const result = await parentAPI.exportReport(reportType, { 
        child_id: selectedChild.id 
      });
      
      if (result.success && result.data) {
        // Create download link
        const url = window.URL.createObjectURL(new Blob([result.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${reportType}_report_${selectedChild.name}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        setSuccess('Report downloaded successfully!');
      }
    } catch (err) {
      setError('Failed to export report');
    } finally {
      setLoading(false);
    }
  };

  // Utility functions
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

  const getGradeColor = (grade) => {
    if (grade >= 80) return 'success';
    if (grade >= 60) return 'warning';
    return 'danger';
  };

  if (authLoading || (loading && !refreshing)) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3 text-muted">Loading parent portal...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Page Header */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 bg-gradient-primary text-white shadow">
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
                          alt="Parent avatar"
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div 
                          className="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow"
                          style={{ width: 80, height: 80 }}
                        >
                          <PersonCircle size={32} className="text-white" />
                        </div>
                      )}
                    </div>
                    <div>
                      <h1 className="h2 mb-1">Welcome, {userProfile?.first_name || 'Parent'}! 👨‍👩‍👧‍👦</h1>
                      <p className="mb-1 opacity-75">
                        Your gateway to your child's educational journey
                      </p>
                      <small className="opacity-75">
                        {children.length} child{children.length !== 1 ? 'ren' : ''} enrolled • Last updated: {new Date().toLocaleTimeString()}
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
                      className="text-primary"
                    >
                      <ArrowClockwise className={`me-2 ${refreshing ? 'spinning' : ''}`} size={16} />
                      Refresh
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-primary"
                      onClick={() => setShowMessageModal(true)}
                    >
                      <Chat className="me-2" />
                      Message Teacher
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

      {/* Child Selection */}
      {children.length > 0 && (
        <Row className="mb-4">
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Body className="py-2">
                <div className="d-flex align-items-center">
                  <h6 className="mb-0 me-3">Select Child:</h6>
                  <div className="d-flex flex-wrap gap-2">
                    {children.map((child) => (
                      <Button
                        key={child.id}
                        variant={selectedChild?.id === child.id ? "primary" : "outline-primary"}
                        size="sm"
                        onClick={() => handleChildSelect(child)}
                      >
                        <PersonBadge className="me-2" />
                        {child.first_name} {child.last_name}
                        {child.grade_level && (
                          <Badge bg="secondary" className="ms-2">
                            {child.grade_level}
                          </Badge>
                        )}
                      </Button>
                    ))}
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

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
                    <GraphUp className="me-2" />
                    Dashboard
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
                    <CalendarCheck className="me-2" />
                    Attendance
                  </>
                } />
                <Tab eventKey="fees" title={
                  <>
                    <CreditCard className="me-2" />
                    Fees {stats.pendingFees > 0 && (
                      <Badge bg="danger" className="ms-1">{formatNumber(stats.pendingFees)}</Badge>
                    )}
                  </>
                } />
                <Tab eventKey="assignments" title={
                  <>
                    <Journal className="me-2" />
                    Assignments {stats.pendingAssignments > 0 && (
                      <Badge bg="warning" className="ms-1">{stats.pendingAssignments}</Badge>
                    )}
                  </>
                } />
                <Tab eventKey="timetable" title={
                  <>
                    <Clock className="me-2" />
                    Timetable
                  </>
                } />
                <Tab eventKey="communications" title={
                  <>
                    <Chat className="me-2" />
                    Messages {stats.unreadMessages > 0 && (
                      <Badge bg="danger" className="ms-1">{stats.unreadMessages}</Badge>
                    )}
                  </>
                } />
                <Tab eventKey="events" title={
                  <>
                    <CalendarEvent className="me-2" />
                    Events {stats.upcomingEvents > 0 && (
                      <Badge bg="success" className="ms-1">{stats.upcomingEvents}</Badge>
                    )}
                  </>
                } />
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && selectedChild && (
        <>
          {/* Stats Cards */}
          <Row className="mb-4">
            <Col xl={3} lg={6} className="mb-3">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 className="card-title text-uppercase text-muted mb-2">Overall Grade</h6>
                      <h2 className="mb-0 text-primary">{stats.averageGrade}%</h2>
                      <small className="text-muted">Current average</small>
                    </div>
                    <div className="bg-primary bg-opacity-10 p-3 rounded">
                      <Award size={24} className="text-primary" />
                    </div>
                  </div>
                  <ProgressBar 
                    now={stats.averageGrade} 
                    variant={getGradeColor(stats.averageGrade)}
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
                      <h6 className="card-title text-uppercase text-muted mb-2">Attendance Rate</h6>
                      <h2 className="mb-0 text-success">{stats.attendanceRate}%</h2>
                      <small className="text-muted">This term</small>
                    </div>
                    <div className="bg-success bg-opacity-10 p-3 rounded">
                      <CalendarCheck size={24} className="text-success" />
                    </div>
                  </div>
                  <ProgressBar 
                    now={stats.attendanceRate} 
                    variant={stats.attendanceRate >= 90 ? 'success' : 'warning'}
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
                      <h6 className="card-title text-uppercase text-muted mb-2">Pending Fees</h6>
                      <h2 className="mb-0 text-warning">{formatCurrency(stats.pendingFees)}</h2>
                      <small className="text-muted">Balance due</small>
                    </div>
                    <div className="bg-warning bg-opacity-10 p-3 rounded">
                      <CreditCard size={24} className="text-warning" />
                    </div>
                  </div>
                  {stats.pendingFees > 0 && (
                    <Button 
                      variant="warning" 
                      size="sm" 
                      className="mt-2 w-100"
                      onClick={() => navigate('/parent/payments')}
                    >
                      Pay Now
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
                      <h6 className="card-title text-uppercase text-muted mb-2">Notifications</h6>
                      <h2 className="mb-0 text-info">{stats.totalNotifications}</h2>
                      <small className="text-muted">Unread messages</small>
                    </div>
                    <div className="bg-info bg-opacity-10 p-3 rounded">
                      <Bell size={24} className="text-info" />
                    </div>
                  </div>
                  {stats.totalNotifications > 0 && (
                    <Button 
                      variant="info" 
                      size="sm" 
                      className="mt-2 w-100"
                      onClick={() => setActiveTab('communications')}
                    >
                      View Messages
                    </Button>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row>
            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">
                      <Book className="me-2 text-primary" />
                      Academic Progress
                    </h5>
                    <Button 
                      variant="outline-primary" 
                      size="sm"
                      onClick={() => handleExportReport('academic')}
                    >
                      <Download size={12} className="me-1" />
                      Export
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  {academicProgress.subjects?.length > 0 ? (
                    <Table responsive className="mb-0">
                      <thead className="bg-light">
                        <tr>
                          <th>Subject</th>
                          <th>Teacher</th>
                          <th>Grade</th>
                          <th>Progress</th>
                        </tr>
                      </thead>
                      <tbody>
                        {academicProgress.subjects.slice(0, 5).map((subject, index) => (
                          <tr key={index}>
                            <td className="fw-semibold">{subject.name}</td>
                            <td>{subject.teacher || 'N/A'}</td>
                            <td>
                              <Badge bg={getGradeColor(subject.score)}>
                                {subject.score || 'N/A'}%
                              </Badge>
                            </td>
                            <td>
                              <ProgressBar 
                                now={subject.score || 0} 
                                variant={getGradeColor(subject.score)}
                                style={{ height: '6px' }}
                              />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  ) : (
                    <div className="text-center py-5">
                      <p className="text-muted mb-0">No academic data available</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>

            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">
                      <Journal className="me-2 text-warning" />
                      Recent Assignments
                    </h5>
                    <Button 
                      variant="outline-warning" 
                      size="sm"
                      onClick={() => setActiveTab('assignments')}
                    >
                      View All
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  {recentAssignments.length > 0 ? (
                    <Table responsive className="mb-0">
                      <thead className="bg-light">
                        <tr>
                          <th>Assignment</th>
                          <th>Subject</th>
                          <th>Due Date</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentAssignments.slice(0, 5).map((assignment) => (
                          <tr key={assignment.id}>
                            <td className="fw-semibold">{assignment.title}</td>
                            <td>{assignment.subject_name || assignment.subject}</td>
                            <td>
                              <Badge bg={new Date(assignment.due_date) < new Date() ? 'danger' : 'primary'}>
                                {formatDate(assignment.due_date)}
                              </Badge>
                            </td>
                            <td>
                              <Badge bg={
                                assignment.status === 'submitted' ? 'success' :
                                assignment.status === 'overdue' ? 'danger' :
                                assignment.status === 'graded' ? 'info' : 'warning'
                              }>
                                {assignment.status || 'Pending'}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  ) : (
                    <div className="text-center py-5">
                      <p className="text-muted mb-0">No recent assignments</p>
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
                  <h5 className="mb-0">
                    <CalendarEvent className="me-2 text-success" />
                    Upcoming School Events
                  </h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {schoolEvents.filter(e => new Date(e.date) > new Date()).length > 0 ? (
                    <ListGroup variant="flush">
                      {schoolEvents
                        .filter(e => new Date(e.date) > new Date())
                        .slice(0, 5)
                        .map((event, index) => (
                          <ListGroup.Item key={index} className="d-flex justify-content-between align-items-center">
                            <div>
                              <h6 className="mb-1">{event.title}</h6>
                              <small className="text-muted">{event.description}</small>
                            </div>
                            <div className="text-end">
                              <div className="fw-bold">{formatDate(event.date)}</div>
                              <small className="text-muted">{event.time || 'All day'}</small>
                            </div>
                          </ListGroup.Item>
                        ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <p className="text-muted mb-0">No upcoming events</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>

            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">
                    <ClockHistory className="me-2 text-secondary" />
                    Quick Actions
                  </h5>
                </Card.Header>
                <Card.Body>
                  <div className="d-grid gap-2">
                    <Button 
                      variant="outline-primary" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => setActiveTab('communications')}
                    >
                      <Chat className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">Contact Teachers</div>
                        <small className="text-muted">Send message to school staff</small>
                      </div>
                    </Button>
                    <Button 
                      variant="outline-success" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => handleExportReport('progress')}
                    >
                      <FileEarmarkBarGraph className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">Download Report</div>
                        <small className="text-muted">Export child's progress report</small>
                      </div>
                    </Button>
                    <Button 
                      variant="outline-warning" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => setActiveTab('fees')}
                    >
                      <Wallet className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">Make Payment</div>
                        <small className="text-muted">Pay school fees online</small>
                      </div>
                    </Button>
                    <Button 
                      variant="outline-info" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => navigate('/parent/settings')}
                    >
                      <ShieldCheck className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">Update Settings</div>
                        <small className="text-muted">Manage notifications and preferences</small>
                      </div>
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Academics Tab */}
      {activeTab === 'academics' && selectedChild && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Academic Performance</h5>
                  <div>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      className="me-2"
                      onClick={() => handleExportReport('academic')}
                    >
                      <Download className="me-1" />
                      Export Report
                    </Button>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => navigate(`/parent/report-card/${selectedChild.id}`)}
                    >
                      View Report Card
                    </Button>
                  </div>
                </div>
              </Card.Header>
              <Card.Body>
                {academicProgress.subjects?.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Subject</th>
                          <th>Teacher</th>
                          <th>Term 1</th>
                          <th>Term 2</th>
                          <th>Term 3</th>
                          <th>Average</th>
                          <th>Grade</th>
                          <th>Remarks</th>
                        </tr>
                      </thead>
                      <tbody>
                        {academicProgress.subjects.map((subject, index) => (
                          <tr key={index}>
                            <td className="fw-semibold">{subject.name}</td>
                            <td>{subject.teacher || 'N/A'}</td>
                            <td>{subject.term1_score || '-'}</td>
                            <td>{subject.term2_score || '-'}</td>
                            <td>{subject.term3_score || '-'}</td>
                            <td>
                              <Badge bg={getGradeColor(subject.average_score)}>
                                {subject.average_score || 0}%
                              </Badge>
                            </td>
                            <td>{subject.grade || 'N/A'}</td>
                            <td>
                              <small className={
                                subject.remarks?.toLowerCase().includes('excellent') ? 'text-success' :
                                subject.remarks?.toLowerCase().includes('good') ? 'text-primary' :
                                subject.remarks?.toLowerCase().includes('improve') ? 'text-warning' : 'text-muted'
                              }>
                                {subject.remarks || 'No remarks'}
                              </small>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-5">
                    <Book size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-2">No academic data available</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Attendance Tab */}
      {activeTab === 'attendance' && selectedChild && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Attendance Records</h5>
                  <Button 
                    variant="outline-primary" 
                    size="sm"
                    onClick={() => handleExportReport('attendance')}
                  >
                    <Download className="me-1" />
                    Export
                  </Button>
                </div>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={3}>
                    <Card className="text-center bg-success text-white">
                      <Card.Body>
                        <h4 className="mb-0">{stats.attendanceRate}%</h4>
                        <small>Attendance Rate</small>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={3}>
                    <Card className="text-center bg-primary text-white">
                      <Card.Body>
                        <h4 className="mb-0">{attendanceData.days_present || 0}</h4>
                        <small>Days Present</small>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={3}>
                    <Card className="text-center bg-warning text-dark">
                      <Card.Body>
                        <h4 className="mb-0">{attendanceData.days_absent || 0}</h4>
                        <small>Days Absent</small>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={3}>
                    <Card className="text-center bg-info text-white">
                      <Card.Body>
                        <h4 className="mb-0">{attendanceData.late_arrivals || 0}</h4>
                        <small>Late Arrivals</small>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>

                {attendanceData.records?.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover>
                      <thead className="table-light">
                        <tr>
                          <th>Date</th>
                          <th>Day</th>
                          <th>Status</th>
                          <th>Check-in Time</th>
                          <th>Check-out Time</th>
                          <th>Remarks</th>
                        </tr>
                      </thead>
                      <tbody>
                        {attendanceData.records.slice(0, 20).map((record, index) => (
                          <tr key={index}>
                            <td>{formatDate(record.date)}</td>
                            <td>{new Date(record.date).toLocaleDateString('en-KE', { weekday: 'short' })}</td>
                            <td>
                              <Badge bg={
                                record.status === 'present' ? 'success' :
                                record.status === 'absent' ? 'danger' :
                                record.status === 'late' ? 'warning' : 'secondary'
                              }>
                                {record.status?.toUpperCase() || 'UNKNOWN'}
                              </Badge>
                            </td>
                            <td>{record.check_in_time || 'N/A'}</td>
                            <td>{record.check_out_time || 'N/A'}</td>
                            <td>
                              <small className="text-muted">{record.remarks || '-'}</small>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-5">
                    <CalendarCheck size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No attendance records available</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Fees Tab */}
      {activeTab === 'fees' && selectedChild && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Fee Statement</h5>
                  <div>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      className="me-2"
                      onClick={() => handleExportReport('fees')}
                    >
                      <Download className="me-1" />
                      Statement
                    </Button>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => navigate('/parent/payments')}
                    >
                      <CreditCard className="me-1" />
                      Make Payment
                    </Button>
                  </div>
                </div>
              </Card.Header>
              <Card.Body>
                <Alert variant="info" className="mb-4">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 className="mb-1">Current Balance Due</h6>
                      <h3 className="text-success mb-0">{formatCurrency(feeData.balance_due || 0)}</h3>
                      <small className="text-muted">Due Date: {formatDate(feeData.due_date)}</small>
                    </div>
                    {feeData.balance_due > 0 && (
                      <Button variant="warning" size="lg">
                        Pay Now
                      </Button>
                    )}
                  </div>
                </Alert>

                <div className="table-responsive">
                  <Table hover className="mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Invoice #</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Due Date</th>
                        <th>Status</th>
                        <th>Payment Date</th>
                        <th>Receipt</th>
                      </tr>
                    </thead>
                    <tbody>
                      {feeData.invoices?.map((invoice, index) => (
                        <tr key={index}>
                          <td>{invoice.invoice_number}</td>
                          <td>{invoice.description}</td>
                          <td className="fw-semibold">{formatCurrency(invoice.amount)}</td>
                          <td>{formatDate(invoice.due_date)}</td>
                          <td>
                            <Badge bg={invoice.status === 'paid' ? 'success' : 'warning'}>
                              {invoice.status?.toUpperCase()}
                            </Badge>
                          </td>
                          <td>{invoice.payment_date ? formatDate(invoice.payment_date) : '-'}</td>
                          <td>
                            {invoice.receipt_url && (
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => window.open(invoice.receipt_url, '_blank')}
                              >
                                View
                              </Button>
                            )}
                          </td>
                        </tr>
                      )) || (
                        <tr>
                          <td colSpan="7" className="text-center py-4">
                            <p className="text-muted mb-0">No fee records available</p>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </Table>
                </div>

                <div className="mt-4">
                  <h6>Payment History</h6>
                  {feeData.payments?.length > 0 ? (
                    <ListGroup variant="flush">
                      {feeData.payments.slice(0, 5).map((payment, index) => (
                        <ListGroup.Item key={index} className="d-flex justify-content-between align-items-center">
                          <div>
                            <div className="fw-bold">{payment.description}</div>
                            <small className="text-muted">Ref: {payment.reference}</small>
                          </div>
                          <div className="text-end">
                            <div className="text-success">{formatCurrency(payment.amount)}</div>
                            <small className="text-muted">{formatDate(payment.date)}</small>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <p className="text-muted">No payment history available</p>
                  )}
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Assignments Tab */}
      {activeTab === 'assignments' && selectedChild && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Assignments & Homework</h5>
              </Card.Header>
              <Card.Body>
                {recentAssignments.length > 0 ? (
                  <Table responsive hover>
                    <thead className="table-light">
                      <tr>
                        <th>Assignment</th>
                        <th>Subject</th>
                        <th>Teacher</th>
                        <th>Assigned Date</th>
                        <th>Due Date</th>
                        <th>Status</th>
                        <th>Grade</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentAssignments.map((assignment) => (
                        <tr key={assignment.id}>
                          <td className="fw-semibold">{assignment.title}</td>
                          <td>{assignment.subject_name || assignment.subject}</td>
                          <td>{assignment.teacher_name || assignment.teacher}</td>
                          <td>{formatDate(assignment.assigned_date)}</td>
                          <td>
                            <Badge bg={new Date(assignment.due_date) < new Date() ? 'danger' : 'primary'}>
                              {formatDate(assignment.due_date)}
                            </Badge>
                          </td>
                          <td>
                            <Badge bg={
                              assignment.status === 'submitted' ? 'success' :
                              assignment.status === 'graded' ? 'info' :
                              assignment.status === 'overdue' ? 'danger' : 'warning'
                            }>
                              {assignment.status?.toUpperCase()}
                            </Badge>
                          </td>
                          <td>
                            {assignment.grade ? (
                              <Badge bg={getGradeColor(assignment.grade)}>
                                {assignment.grade}%
                              </Badge>
                            ) : (
                              <span className="text-muted">Pending</span>
                            )}
                          </td>
                          <td>
                            <Button 
                              variant="outline-primary" 
                              size="sm"
                              onClick={() => navigate(`/parent/assignments/${assignment.id}`)}
                            >
                              View
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                ) : (
                  <div className="text-center py-5">
                    <Journal size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No assignments available</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Timetable Tab */}
      {activeTab === 'timetable' && selectedChild && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">School Timetable</h5>
              </Card.Header>
              <Card.Body>
                {timetable.length > 0 ? (
                  <div className="table-responsive">
                    <Table className="table-bordered">
                      <thead className="table-primary">
                        <tr>
                          <th>Time</th>
                          <th>Monday</th>
                          <th>Tuesday</th>
                          <th>Wednesday</th>
                          <th>Thursday</th>
                          <th>Friday</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Array.from({ length: 8 }).map((_, period) => (
                          <tr key={period}>
                            <td className="fw-semibold bg-light">Period {period + 1}</td>
                            {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map((day) => {
                              const classItem = timetable.find(
                                t => t.day?.toLowerCase() === day.toLowerCase() && t.period === period + 1
                              );
                              return (
                                <td key={day}>
                                  {classItem ? (
                                    <>
                                      <div className="fw-bold">{classItem.subject}</div>
                                      <small className="text-muted">{classItem.teacher}</small>
                                      <br />
                                      <small className="text-muted">{classItem.room}</small>
                                    </>
                                  ) : (
                                    <span className="text-muted">Free</span>
                                  )}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-5">
                    <Clock size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">Timetable not available</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Communications Tab */}
      {activeTab === 'communications' && (
        <Row>
          <Col lg={8} className="mb-4">
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Messages from School</h5>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => setShowMessageModal(true)}
                  >
                    <Chat className="me-1" />
                    New Message
                  </Button>
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {teacherCommunications.length > 0 ? (
                  <ListGroup variant="flush">
                    {teacherCommunications.map((message, index) => (
                      <ListGroup.Item 
                        key={index} 
                        className={`p-3 ${!message.read ? 'bg-light' : ''}`}
                        onClick={() => handleMarkNotificationRead(message.id)}
                        style={{ cursor: 'pointer' }}
                      >
                        <div className="d-flex justify-content-between align-items-start">
                          <div>
                            <div className="d-flex align-items-center mb-1">
                              <div className="me-2">
                                {message.sender_avatar ? (
                                  <Image 
                                    src={message.sender_avatar} 
                                    roundedCircle 
                                    width={40} 
                                    height={40}
                                    className="border"
                                  />
                                ) : (
                                  <div 
                                    className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center"
                                    style={{ width: 40, height: 40 }}
                                  >
                                    <PersonCircle size={20} />
                                  </div>
                                )}
                              </div>
                              <div>
                                <h6 className="mb-0">{message.sender_name}</h6>
                                <small className="text-muted">{message.sender_role || 'Teacher'}</small>
                              </div>
                            </div>
                            <p className="mb-1 mt-2">{message.message}</p>
                          </div>
                          <div className="text-end">
                            <small className="text-muted">{formatDate(message.date)}</small>
                            {!message.read && (
                              <Badge bg="danger" className="ms-2">New</Badge>
                            )}
                          </div>
                        </div>
                        {message.attachments?.length > 0 && (
                          <div className="mt-2">
                            <small className="text-muted">Attachments:</small>
                            {message.attachments.map((file, idx) => (
                              <Button 
                                key={idx} 
                                variant="outline-secondary" 
                                size="sm" 
                                className="ms-2"
                                onClick={() => window.open(file.url, '_blank')}
                              >
                                <FileEarmarkArrowDown className="me-1" />
                                {file.name}
                              </Button>
                            ))}
                          </div>
                        )}
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                ) : (
                  <div className="text-center py-5">
                    <Chat size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No messages available</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
          
          <Col lg={4} className="mb-4">
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Emergency Contacts</h5>
              </Card.Header>
              <Card.Body>
                {emergencyContacts.length > 0 ? (
                  <ListGroup variant="flush">
                    {emergencyContacts.map((contact, index) => (
                      <ListGroup.Item key={index}>
                        <div className="d-flex justify-content-between align-items-center">
                          <div>
                            <h6 className="mb-1">{contact.name}</h6>
                            <small className="text-muted">{contact.relationship}</small>
                          </div>
                          <Button 
                            variant="outline-primary" 
                            size="sm"
                            href={`tel:${contact.phone}`}
                          >
                            <Phone size={14} />
                          </Button>
                        </div>
                        <div className="mt-2">
                          <small className="text-muted">Phone: {contact.phone}</small>
                          {contact.email && (
                            <div>
                              <small className="text-muted">Email: {contact.email}</small>
                            </div>
                          )}
                        </div>
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                ) : (
                  <p className="text-muted">No emergency contacts available</p>
                )}
              </Card.Body>
            </Card>

            <Card className="border-0 shadow-sm mt-4">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Child's Teachers</h5>
              </Card.Header>
              <Card.Body>
                {selectedChild?.teachers?.length > 0 ? (
                  <ListGroup variant="flush">
                    {selectedChild.teachers.map((teacher, index) => (
                      <ListGroup.Item key={index}>
                        <div className="d-flex justify-content-between align-items-center">
                          <div>
                            <h6 className="mb-1">{teacher.name}</h6>
                            <small className="text-muted">{teacher.subject}</small>
                          </div>
                          <Button 
                            variant="outline-primary" 
                            size="sm"
                            onClick={() => {
                              setSelectedTeacher(teacher);
                              setShowMessageModal(true);
                            }}
                          >
                            <Chat size={14} />
                          </Button>
                        </div>
                        <div className="mt-2">
                          <small className="text-muted">Email: {teacher.email}</small>
                          {teacher.phone && (
                            <div>
                              <small className="text-muted">Phone: {teacher.phone}</small>
                            </div>
                          )}
                        </div>
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                ) : (
                  <p className="text-muted">No teacher information available</p>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Events Tab */}
      {activeTab === 'events' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">School Calendar & Events</h5>
              </Card.Header>
              <Card.Body>
                {schoolEvents.length > 0 ? (
                  <Row>
                    {schoolEvents.map((event, index) => (
                      <Col md={6} lg={4} className="mb-3" key={index}>
                        <Card className="h-100 border">
                          <Card.Body>
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              <Badge bg={
                                event.type === 'academic' ? 'primary' :
                                event.type === 'sports' ? 'success' :
                                event.type === 'cultural' ? 'warning' :
                                event.type === 'holiday' ? 'info' : 'secondary'
                              }>
                                {event.type?.toUpperCase() || 'EVENT'}
                              </Badge>
                              <small className="text-muted">{formatDate(event.date)}</small>
                            </div>
                            <h6 className="card-title">{event.title}</h6>
                            <p className="card-text text-muted small mb-2">{event.description}</p>
                            <div className="d-flex justify-content-between text-muted small">
                              <span>
                                <Clock size={12} className="me-1" />
                                {event.time || 'All day'}
                              </span>
                              <span>{event.venue || 'School'}</span>
                            </div>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                ) : (
                  <div className="text-center py-5">
                    <CalendarEvent size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No upcoming events</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Send Message Modal */}
      <Modal show={showMessageModal} onHide={() => setShowMessageModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Send Message to Teacher</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Select Teacher</Form.Label>
              <Form.Select 
                value={selectedTeacher?.id || ''}
                onChange={(e) => {
                  const teacher = teacherCommunications.find(t => t.id === e.target.value);
                  setSelectedTeacher(teacher);
                }}
              >
                <option value="">Choose a teacher...</option>
                {teacherCommunications.map((teacher) => (
                  <option key={teacher.id} value={teacher.id}>
                    {teacher.name} - {teacher.subject}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Message</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message here..."
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowMessageModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || !selectedTeacher}
          >
            Send Message
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Schedule Meeting Modal */}
      <Modal show={showMeetingModal} onHide={() => setShowMeetingModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Schedule Meeting</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Meeting Date</Form.Label>
              <Form.Control type="date" required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Meeting Time</Form.Label>
              <Form.Control type="time" required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Purpose</Form.Label>
              <Form.Control as="textarea" rows={3} placeholder="Reason for the meeting..." />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Preferred Mode</Form.Label>
              <Form.Select>
                <option value="in-person">In-Person</option>
                <option value="online">Online (Zoom/Teams)</option>
                <option value="phone">Phone Call</option>
              </Form.Select>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowMeetingModal(false)}>
            Cancel
          </Button>
          <Button variant="primary">Schedule Meeting</Button>
        </Modal.Footer>
      </Modal>

      {/* Footer */}
      <Row className="mt-4">
        <Col>
          <Card className="border-0 bg-light">
            <Card.Body className="py-2">
              <div className="d-flex justify-content-between align-items-center">
                <small className="text-muted">
                  Parent Portal v2.0 • Last updated: {new Date().toLocaleString()}
                </small>
                <div>
                  <small className="text-muted me-3">
                    <Phone size={12} className="me-1" />
                    School Hotline: 0712 345 678
                  </small>
                  <small className="text-muted">
                    <Mailbox size={12} className="me-1" />
                    Email: info@school.edu
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
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .bg-gradient-primary {
          background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        }
      `}</style>
    </Container>
  );
};

export default ParentPortal;