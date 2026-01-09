import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  Container, Row, Col, Card, Button, Badge, 
  Table, Spinner, Alert, ProgressBar, Image, Nav,
  Tabs, Tab, ListGroup, Modal, Form,
  Dropdown, DropdownButton, InputGroup, FormControl
} from 'react-bootstrap';
import {
  House, Clock, Journal, GraphUp, Folder,
  Book, People, Person, CheckCircle, ExclamationTriangle,
  Calendar, FileText, Award, Download,
  ArrowClockwise, Bell, Bookmark, Star,
  Search, Filter, SortAlphaDown, PersonBadge,
  ChatDots, Eye, Share, Pin,
  CalendarWeek, Calculator, Globe, BookmarkCheck,
  ArrowRight, ChevronRight, ClockHistory,
  FileEarmarkPdf, FileEarmarkWord, FileEarmarkExcel,
  PlayBtn, Headphones, CameraVideo, FileEarmarkMedical,
  JournalText, CardText, CardHeading, JournalBookmark,
  JournalCheck, JournalPlus, JournalRichtext, Clipboard,
  ClipboardCheck, ClipboardData, ClipboardPlus,
  FileEarmark, FileEarmarkArrowDown, FileEarmarkArrowUp
} from "react-bootstrap-icons";


// ==================== IMPORT ALL APIS ====================
import authAPI from '../../services/authAPI';
import notesAPI from '../../services/notesAPI';
import libraryAPI from '../../services/libraryAPI';
import timetableAPI from '../../services/timetableAPI';
import {gradesAPI} from '../../services/gradesAPI';
import {attendanceAPI} from '../../services/attendanceAPI';
import assignmentsAPI from '../../services/assignmentsAPI';
import {academicAPI} from '../../services/academicAPI';
import downloadsAPI from '../../services/downloadsAPI';

// REMOVED custom icon imports - replaced with React Bootstrap icons
// import { 
//   SubjectIcon, 
//   AssignmentIcon, 
//   GradeIcon, 
//   AttendanceIcon,
//   LibraryIcon, 
//   ResourceIcon,
//   TimetableIcon,
//   NotesIcon
// } from '../../components/Icons';

function StudentPortal() {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('dashboard');
  const [studentData, setStudentData] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  
  // Data states
  const [timetableData, setTimetableData] = useState([]);
  const [assignmentsData, setAssignmentsData] = useState([]);
  const [gradesData, setGradesData] = useState([]);
  const [attendanceData, setAttendanceData] = useState([]);
  const [libraryData, setLibraryData] = useState([]);
  const [resourcesData, setResourcesData] = useState([]);
  const [notesData, setNotesData] = useState([]);
  const [academicInfo, setAcademicInfo] = useState({});
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  
  // UI states
  const [showAssignmentModal, setShowAssignmentModal] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('due_date');
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  // Comprehensive stats
  const [stats, setStats] = useState({
    activeClasses: 0,
    pendingAssignments: 0,
    averageGrade: 0,
    attendanceRate: 0,
    borrowedBooks: 0,
    upcomingExams: 0,
    completedAssignments: 0,
    notesCount: 0
  });

  // Helper function for consistent error handling
  const handleAPIError = (error, context = '') => {
    console.error(`API Error in ${context}:`, error);
    return {
      success: false,
      message: error.response?.data?.error || error.message || 'An error occurred'
    };
  };

  // Enhanced data fetching
  const fetchStudentData = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      // 1. Get user profile
      const profileResult = await authAPI.getCurrentUser();
      if (profileResult.success) {
        setUserProfile(profileResult.user || profileResult.data);
      }

      // 2. Get academic info
      const academicYearResult = await academicAPI.getCurrentAcademicYear();
      if (academicYearResult.success) {
        setAcademicInfo(prev => ({ ...prev, academicYear: academicYearResult.data }));
      }

      // 3. Get timetable
      const timetableResult = await timetableAPI.getStudentTimetable();
      if (timetableResult.success) {
        const timetable = timetableResult.data?.schedule || timetableResult.data || [];
        setTimetableData(timetable);
        
        // Extract today's schedule
        const today = new Date().toLocaleDateString('en-KE', { weekday: 'long' });
        const todaySchedule = timetable.filter(item => 
          item.day?.toLowerCase() === today.toLowerCase()
        );
        setUpcomingEvents(todaySchedule);
      }

      // 4. Get assignments (using notesAPI for LMS assignments)
      const assignmentsResult = await notesAPI.getStudentAssignments();
      if (assignmentsResult.success) {
        setAssignmentsData(assignmentsResult.data?.assignments || assignmentsResult.data || []);
      }

      // 5. Get grades
      const gradesResult = await gradesAPI.getGrades({ student_id: currentUser?.id });
      if (gradesResult.success) {
        setGradesData(gradesResult.data?.grades || gradesResult.data || []);
      }

      // 6. Get attendance
      const attendanceResult = await attendanceAPI.getAttendanceRecords({ student_id: currentUser?.id });
      if (attendanceResult.success) {
        setAttendanceData(attendanceResult.data?.records || attendanceResult.data || []);
      }

      // 7. Get library data
      const libraryResult = await libraryAPI.getUserCurrentBorrows();
      if (libraryResult.success) {
        setLibraryData(libraryResult.data?.books || libraryResult.data || []);
      }

      // 8. Get resources
      const resourcesResult = await downloadsAPI.getFiles({ category: 'student_resources' });
      if (resourcesResult.success) {
        setResourcesData(resourcesResult.data?.files || resourcesResult.data || []);
      }

      // 9. Get notes
      const notesResult = await notesAPI.getMyNotes();
      if (notesResult.success) {
        setNotesData(notesResult.data?.notes || notesResult.data || []);
      }

      // 10. Get notifications
      const notificationsResult = await notesAPI.getAssignmentNotifications();
      if (notificationsResult.success) {
        setNotifications(notificationsResult.data?.notifications || notificationsResult.data || []);
      }

      // Calculate comprehensive statistics
      const activeClasses = new Set(timetableData.map(item => item.subject)).size;
      const pendingAssignments = assignmentsData.filter(a => 
        a.status === 'pending' || a.status === 'assigned' || a.status === 'draft'
      ).length;
      const completedAssignments = assignmentsData.filter(a => 
        a.status === 'submitted' || a.status === 'graded'
      ).length;
      
      const averageGrade = gradesData.length > 0 
        ? gradesData.reduce((sum, grade) => sum + (grade.score || grade.grade || 0), 0) / gradesData.length 
        : 0;

      const totalAttendance = attendanceData.length;
      const presentDays = attendanceData.filter(a => a.status === 'present').length;
      const attendanceRate = totalAttendance > 0 ? Math.round((presentDays / totalAttendance) * 100) : 0;

      const borrowedBooks = libraryData.length;
      const upcomingExams = assignmentsData.filter(a => 
        a.type === 'exam' && new Date(a.due_date) > new Date()
      ).length;

      setStats({
        activeClasses,
        pendingAssignments,
        averageGrade: Math.round(averageGrade),
        attendanceRate,
        borrowedBooks,
        upcomingExams,
        completedAssignments,
        notesCount: notesData.length
      });

    } catch (err) {
      console.error('Error fetching student data:', err);
      setError('Unable to load student portal data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [currentUser?.id]);

  useEffect(() => {
    if (!authLoading && currentUser) {
      fetchStudentData();
    }
  }, [authLoading, currentUser, fetchStudentData]);

  const handleRefresh = () => {
    fetchStudentData(true);
  };

  const handleNavigate = (path) => {
    navigate(path);
  };

  const handleViewAssignment = (assignment) => {
    setSelectedAssignment(assignment);
    setShowAssignmentModal(true);
  };

  const handleSubmitAssignment = async (assignmentId, submissionData) => {
    try {
      const result = await assignmentsAPI.submitAssignment(assignmentId, submissionData);
      if (result.success) {
        // Refresh assignments data
        fetchStudentData(true);
        setShowAssignmentModal(false);
      }
    } catch (err) {
      console.error('Error submitting assignment:', err);
    }
  };

  const handleDownloadResource = async (resourceId) => {
    try {
      const result = await downloadsAPI.downloadFile(resourceId);
      if (result.success) {
        // Handle file download
        const url = window.URL.createObjectURL(new Blob([result.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `resource-${resourceId}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      }
    } catch (err) {
      console.error('Download error:', err);
    }
  };

  const handleBorrowBook = async (bookId) => {
    try {
      const result = await libraryAPI.borrowBook({ book_id: bookId });
      if (result.success) {
        // Refresh library data
        fetchStudentData(true);
      }
    } catch (err) {
      console.error('Error borrowing book:', err);
    }
  };

  // Enhanced navigation items
  const navigationItems = useMemo(() => [
    { id: 'dashboard', icon: House, label: 'Dashboard', badge: null },
    { id: 'timetable', icon: Clock, label: 'Timetable', badge: null },
    { id: 'assignments', icon: Journal, label: 'Assignments', badge: stats.pendingAssignments },
    { id: 'grades', icon: GraphUp, label: 'Grades', badge: null },
    { id: 'attendance', icon: CheckCircle, label: 'Attendance', badge: null },
    { id: 'library', icon: Book, label: 'Library', badge: stats.borrowedBooks },
    { id: 'resources', icon: Folder, label: 'Resources', badge: null },
    { id: 'notes', icon: Bookmark, label: 'Notes', badge: stats.notesCount },
  ], [stats]);

  // Enhanced utility functions
  const getAssignmentStatusBadge = (assignment) => {
    const dueDate = new Date(assignment.due_date);
    const today = new Date();
    
    if (assignment.status === 'submitted' || assignment.submission_status === 'submitted') {
      return <Badge bg="success">Submitted ✓</Badge>;
    }
    
    if (assignment.status === 'graded') {
      return <Badge bg="info">Graded</Badge>;
    }
    
    if (dueDate < today) {
      return <Badge bg="danger">Overdue ⚠️</Badge>;
    }
    
    const diffTime = dueDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return <Badge bg="warning">Due Today 🔥</Badge>;
    } else if (diffDays <= 3) {
      return <Badge bg="warning">{diffDays}d left</Badge>;
    }
    
    return <Badge bg="secondary">Pending</Badge>;
  };

  const getGradeColor = (grade) => {
    if (grade >= 90) return 'success';
    if (grade >= 80) return 'info';
    if (grade >= 70) return 'warning';
    if (grade >= 60) return 'primary';
    return 'danger';
  };

  const getGradeLetter = (grade) => {
    if (grade >= 90) return 'A';
    if (grade >= 80) return 'B';
    if (grade >= 70) return 'C';
    if (grade >= 60) return 'D';
    return 'F';
  };

  const getResourceIcon = (fileType) => {
    switch (fileType?.toLowerCase()) {
      case 'pdf': return <FileEarmarkPdf className="text-danger" size={20} />;
      case 'doc': case 'docx': return <FileEarmarkWord className="text-primary" size={20} />;
      case 'xls': case 'xlsx': return <FileEarmarkExcel className="text-success" size={20} />;
      case 'mp4': case 'avi': return <PlayBtn className="text-warning" size={20} />;
      case 'mp3': return <Headphones className="text-info" size={20} />;
      default: return <FileEarmarkMedical className="text-secondary" size={20} />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-KE', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-KE', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Filter and sort assignments
  const filteredAssignments = useMemo(() => {
    let filtered = assignmentsData;
    
    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(assignment =>
        assignment.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        assignment.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        assignment.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Filter by status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(assignment => {
        if (filterStatus === 'pending') {
          return assignment.status === 'pending' || assignment.status === 'draft';
        }
        if (filterStatus === 'submitted') {
          return assignment.status === 'submitted';
        }
        if (filterStatus === 'graded') {
          return assignment.status === 'graded';
        }
        if (filterStatus === 'overdue') {
          return new Date(assignment.due_date) < new Date();
        }
        return true;
      });
    }
    
    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'due_date') {
        return new Date(a.due_date) - new Date(b.due_date);
      }
      if (sortBy === 'subject') {
        return (a.subject || '').localeCompare(b.subject || '');
      }
      if (sortBy === 'priority') {
        return (b.priority || 0) - (a.priority || 0);
      }
      return 0;
    });
    
    return filtered;
  }, [assignmentsData, searchQuery, filterStatus, sortBy]);

  const getUserDisplayInfo = () => {
    if (userProfile) {
      return {
        firstName: userProfile.first_name || userProfile.firstName || 'Student',
        lastName: userProfile.last_name || userProfile.lastName || '',
        avatar: userProfile.avatar || userProfile.profile_picture,
        initials: (userProfile.first_name?.charAt(0) || '') + (userProfile.last_name?.charAt(0) || '') || 'S',
        admissionNumber: userProfile.admission_number || userProfile.student_id,
        gradeLevel: userProfile.grade_level || userProfile.class_name
      };
    }
    return {
      firstName: currentUser?.first_name || currentUser?.firstName || 'Student',
      lastName: currentUser?.last_name || currentUser?.lastName || '',
      avatar: null,
      initials: 'S',
      admissionNumber: currentUser?.admission_number || 'N/A',
      gradeLevel: currentUser?.grade_level || 'N/A'
    };
  };

  const { firstName, lastName, avatar, initials, admissionNumber, gradeLevel } = getUserDisplayInfo();
  const fullName = `${firstName} ${lastName}`.trim();

  if (authLoading || (loading && !refreshing)) {
    return (
      <Container className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="text-center">
          <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
          <p className="mt-3 fs-5">Loading your student portal...</p>
        </div>
      </Container>
    );
  }

  return (
    <div className="student-portal-page">
      {/* Enhanced Hero Section */}
      <section className="portal-hero bg-gradient-primary text-white py-4">
        <Container>
          <Row className="align-items-center">
            <Col lg={8}>
              <div className="d-flex align-items-center">
                <div className="me-4">
                  {avatar ? (
                    <Image 
                      src={avatar} 
                      roundedCircle 
                      width={70} 
                      height={70}
                      className="border border-3 border-white shadow"
                      alt={`${firstName}'s avatar`}
                      style={{ objectFit: 'cover' }}
                    />
                  ) : (
                    <div 
                      className="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow"
                      style={{ width: 70, height: 70 }}
                    >
                      <Person size={28} className="text-white" />
                    </div>
                  )}
                </div>
                
                <div>
                  <h1 className="display-6 fw-bold mb-2">Welcome back, {firstName}! 👨‍🎓</h1>
                  <p className="lead mb-3">
                    Track your academic journey and access learning resources
                  </p>
                  <div className="d-flex flex-wrap gap-2">
                    <Badge bg="light" text="dark" className="fs-6">
                      ID: {admissionNumber}
                    </Badge>
                    <Badge bg="light" text="dark" className="fs-6">
                      Grade {gradeLevel}
                    </Badge>
                    {academicInfo.academicYear && (
                      <Badge bg="light" text="dark" className="fs-6">
                        {academicInfo.academicYear.name}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </Col>
            
            <Col lg={4} className="text-end">
              <div className="d-flex gap-2 justify-content-end align-items-center">
                <Button 
                  variant="light" 
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="text-primary"
                  size="sm"
                >
                  <ArrowClockwise className={`me-2 ${refreshing ? 'spinning' : ''}`} size={14} />
                  Refresh
                </Button>
                
                <Dropdown>
                  <Dropdown.Toggle variant="outline-light" size="sm">
                    <Bell size={16} className="me-2" />
                    {notifications.length > 0 && (
                      <Badge bg="danger" pill className="ms-1">{notifications.length}</Badge>
                    )}
                  </Dropdown.Toggle>
                  <Dropdown.Menu align="end" className="shadow-lg">
                    <Dropdown.Header>Notifications</Dropdown.Header>
                    {notifications.slice(0, 5).map((notification, idx) => (
                      <Dropdown.Item key={idx} className="py-2">
                        <div className="d-flex align-items-start">
                          <Bell size={16} className="me-2 text-primary mt-1" />
                          <div>
                            <small className="fw-bold d-block">{notification.title}</small>
                            <small className="text-muted">{notification.message}</small>
                          </div>
                        </div>
                      </Dropdown.Item>
                    ))}
                    {notifications.length === 0 && (
                      <Dropdown.Item className="text-muted text-center">
                        No new notifications
                      </Dropdown.Item>
                    )}
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={() => setShowNotifications(true)}>
                      View All Notifications
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Portal Content */}
      <section className="py-4">
        <Container fluid>
          <Row>
            {/* Enhanced Sidebar Navigation */}
            <Col lg={3} xxl={2} className="mb-4">
              <Card className="shadow-sm border-0 sticky-top" style={{ top: '20px' }}>
                <Card.Body className="p-3">
                  <div className="student-profile text-center mb-4">
                    <div className="position-relative mb-3">
                      {avatar ? (
                        <Image 
                          src={avatar} 
                          roundedCircle 
                          width={100} 
                          height={100}
                          className="border border-3 border-primary shadow"
                          alt={`${firstName}'s avatar`}
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div 
                          className="rounded-circle bg-primary bg-opacity-10 d-flex align-items-center justify-content-center border border-3 border-primary shadow mx-auto"
                          style={{ width: 100, height: 100 }}
                        >
                          <Person size={40} className="text-primary" />
                        </div>
                      )}
                      <Badge 
                        bg={stats.attendanceRate >= 75 ? 'success' : 'warning'}
                        className="position-absolute top-0 end-0"
                      >
                        {stats.attendanceRate}%
                      </Badge>
                    </div>
                    
                    <h6 className="mb-1 fw-bold">{fullName}</h6>
                    <small className="text-muted d-block mb-2">{gradeLevel} Student</small>
                    
                    <div className="d-flex justify-content-center gap-2 mb-3">
                      <Button variant="outline-primary" size="sm" className="rounded-pill">
                        <PersonBadge size={12} className="me-1" />
                        Profile
                      </Button>
                      <Button variant="outline-secondary" size="sm" className="rounded-pill">
                        <ChatDots size={12} className="me-1" />
                        Messages
                      </Button>
                    </div>
                    
                    <div className="text-start">
                      <div className="d-flex justify-content-between mb-2">
                        <small>Attendance</small>
                        <small className="fw-bold">{stats.attendanceRate}%</small>
                      </div>
                      <ProgressBar 
                        now={stats.attendanceRate} 
                        variant={
                          stats.attendanceRate >= 90 ? 'success' :
                          stats.attendanceRate >= 75 ? 'info' :
                          stats.attendanceRate >= 60 ? 'warning' : 'danger'
                        }
                        className="mb-3"
                      />
                      
                      <div className="d-flex justify-content-between mb-2">
                        <small>Avg. Grade</small>
                        <small className="fw-bold text-success">{stats.averageGrade}%</small>
                      </div>
                      <ProgressBar 
                        now={stats.averageGrade} 
                        variant={getGradeColor(stats.averageGrade)}
                        className="mb-3"
                      />
                    </div>
                  </div>
                  
                  <nav className="portal-nav">
                    {navigationItems.map(item => (
                      <Button
                        key={item.id}
                        variant={activeTab === item.id ? 'primary' : 'outline-primary'}
                        className="portal-nav-item w-100 text-start d-flex align-items-center justify-content-between p-2 mb-2 rounded-pill"
                        onClick={() => setActiveTab(item.id)}
                      >
                        <div className="d-flex align-items-center">
                          <item.icon className="me-2" size={16} />
                          <span>{item.label}</span>
                        </div>
                        {item.badge !== null && item.badge > 0 && (
                          <Badge bg="danger" pill className="ms-2">{item.badge}</Badge>
                        )}
                      </Button>
                    ))}
                  </nav>
                  
                  <div className="mt-4 pt-3 border-top">
                    <small className="text-muted d-block mb-2">Quick Links</small>
                    <div className="d-grid gap-1">
                      <Button variant="outline-secondary" size="sm" className="text-start">
                        <CalendarWeek size={12} className="me-2" />
                        Academic Calendar
                      </Button>
                      <Button variant="outline-secondary" size="sm" className="text-start">
                        <Calculator size={12} className="me-2" />
                        GPA Calculator
                      </Button>
                      <Button variant="outline-secondary" size="sm" className="text-start">
                        <Globe size={12} className="me-2" />
                        Online Classes
                      </Button>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            {/* Main Content Area */}
            <Col lg={9} xxl={10}>
              {error && (
                <Alert variant="warning" dismissible onClose={() => setError(null)} className="mb-3">
                  <Alert.Heading>Notice</Alert.Heading>
                  {error}
                </Alert>
              )}

              <Card className="shadow-sm border-0 mb-4">
                <Card.Body className="p-4">
                  {/* Dashboard Tab */}
                  {activeTab === 'dashboard' && (
                    <div className="dashboard-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                          <h4 className="mb-0">Student Dashboard</h4>
                          <small className="text-muted">
                            Overview of your academic journey
                          </small>
                        </div>
                        <small className="text-muted">
                          Last updated: {new Date().toLocaleTimeString()}
                        </small>
                      </div>
                      
                      {/* Enhanced Quick Stats */}
                      <Row className="g-3 mb-4">
                        <Col xl={2} lg={4} md={4} sm={6}>
                          <Card className="text-center border-0 hover-lift shadow-sm">
                            <Card.Body className="p-3">
                              <div className="bg-primary bg-opacity-10 rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style={{width: '50px', height: '50px'}}>
                                <People size={20} className="text-primary" />
                              </div>
                              <h5 className="text-primary mb-1">{stats.activeClasses}</h5>
                              <p className="text-muted mb-0 small">Active Classes</p>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col xl={2} lg={4} md={4} sm={6}>
                          <Card className="text-center border-0 hover-lift shadow-sm">
                            <Card.Body className="p-3">
                              <div className="bg-warning bg-opacity-10 rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style={{width: '50px', height: '50px'}}>
                                <Journal size={20} className="text-warning" />
                              </div>
                              <h5 className="text-warning mb-1">{stats.pendingAssignments}</h5>
                              <p className="text-muted mb-0 small">Pending</p>
                              <small className="text-success">
                                {stats.completedAssignments} completed
                              </small>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col xl={2} lg={4} md={4} sm={6}>
                          <Card className="text-center border-0 hover-lift shadow-sm">
                            <Card.Body className="p-3">
                              <div className="bg-success bg-opacity-10 rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style={{width: '50px', height: '50px'}}>
                                <Award size={20} className="text-success" />
                              </div>
                              <h5 className="text-success mb-1">{stats.averageGrade}%</h5>
                              <p className="text-muted mb-0 small">Avg. Grade</p>
                              <small className="text-primary">
                                {getGradeLetter(stats.averageGrade)}
                              </small>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col xl={2} lg={4} md={4} sm={6}>
                          <Card className="text-center border-0 hover-lift shadow-sm">
                            <Card.Body className="p-3">
                              <div className="bg-info bg-opacity-10 rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style={{width: '50px', height: '50px'}}>
                                <CheckCircle size={20} className="text-info" />
                              </div>
                              <h5 className="text-info mb-1">{stats.attendanceRate}%</h5>
                              <p className="text-muted mb-0 small">Attendance</p>
                              <small className="text-info">
                                {attendanceData.filter(a => a.status === 'present').length} days
                              </small>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col xl={2} lg={4} md={4} sm={6}>
                          <Card className="text-center border-0 hover-lift shadow-sm">
                            <Card.Body className="p-3">
                              <div className="bg-secondary bg-opacity-10 rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style={{width: '50px', height: '50px'}}>
                                <Book size={20} className="text-secondary" />
                              </div>
                              <h5 className="text-secondary mb-1">{stats.borrowedBooks}</h5>
                              <p className="text-muted mb-0 small">Books</p>
                              <small className="text-warning">
                                {stats.upcomingExams} exams
                              </small>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col xl={2} lg={4} md={4} sm={6}>
                          <Card className="text-center border-0 hover-lift shadow-sm">
                            <Card.Body className="p-3">
                              <div className="bg-danger bg-opacity-10 rounded-circle mx-auto mb-3 d-flex align-items-center justify-content-center" style={{width: '50px', height: '50px'}}>
                                <Bookmark size={20} className="text-danger" />
                              </div>
                              <h5 className="text-danger mb-1">{stats.notesCount}</h5>
                              <p className="text-muted mb-0 small">Notes</p>
                              <small className="text-danger">
                                Personal notes
                              </small>
                            </Card.Body>
                          </Card>
                        </Col>
                      </Row>

                      <Row className="g-4">
                        {/* Today's Schedule */}
                        <Col xl={6} lg={12}>
                          <Card className="border-0 shadow-sm h-100">
                            <Card.Header className="bg-white border-0 py-3">
                              <div className="d-flex justify-content-between align-items-center">
                                <h5 className="mb-0">
                                  <Clock className="me-2 text-primary" />
                                  Today's Schedule
                                </h5>
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => setActiveTab('timetable')}
                                >
                                  View All
                                </Button>
                              </div>
                            </Card.Header>
                            <Card.Body className="p-0">
                              {upcomingEvents.length > 0 ? (
                                <ListGroup variant="flush">
                                  {upcomingEvents.slice(0, 6).map((classItem, index) => (
                                    <ListGroup.Item key={index} className="py-3 border-bottom">
                                      <div className="d-flex justify-content-between align-items-center">
                                        <div>
                                          <Badge bg="primary" className="me-2">
                                            {formatTime(classItem.start_time)}
                                          </Badge>
                                          <span className="fw-semibold">{classItem.subject}</span>
                                          <small className="text-muted d-block mt-1">
                                            {classItem.teacher} • {classItem.room}
                                          </small>
                                        </div>
                                        <ChevronRight size={16} className="text-muted" />
                                      </div>
                                    </ListGroup.Item>
                                  ))}
                                </ListGroup>
                              ) : (
                                <div className="text-center py-4">
                                  <Clock size={32} className="text-muted mb-3" />
                                  <p className="text-muted mb-2">No classes scheduled for today</p>
                                </div>
                              )}
                            </Card.Body>
                          </Card>
                        </Col>

                        {/* Upcoming Assignments */}
                        <Col xl={6} lg={12}>
                          <Card className="border-0 shadow-sm h-100">
                            <Card.Header className="bg-white border-0 py-3">
                              <div className="d-flex justify-content-between align-items-center">
                                <h5 className="mb-0">
                                  <Journal className="me-2 text-warning" />
                                  Upcoming Assignments
                                </h5>
                                <Badge bg="warning">{stats.pendingAssignments}</Badge>
                              </div>
                            </Card.Header>
                            <Card.Body className="p-0">
                              {assignmentsData.slice(0, 5).map((assignment, index) => (
                                <div key={index} className="p-3 border-bottom hover-item">
                                  <div className="d-flex justify-content-between align-items-start mb-2">
                                    <h6 className="mb-0" style={{ cursor: 'pointer' }} onClick={() => handleViewAssignment(assignment)}>
                                      {assignment.title}
                                    </h6>
                                    {getAssignmentStatusBadge(assignment)}
                                  </div>
                                  <div className="d-flex justify-content-between text-muted small">
                                    <span>{assignment.subject}</span>
                                    <span>
                                      <Clock size={12} className="me-1" />
                                      Due: {formatDate(assignment.due_date)}
                                    </span>
                                  </div>
                                </div>
                              ))}
                              {assignmentsData.length === 0 && (
                                <div className="text-center py-4">
                                  <CheckCircle size={32} className="text-muted mb-3" />
                                  <p className="text-muted mb-0">No pending assignments</p>
                                </div>
                              )}
                            </Card.Body>
                          </Card>
                        </Col>
                      </Row>

                      {/* Recent Grades & Performance */}
                      <Row className="mt-4">
                        <Col lg={8}>
                          <Card className="border-0 shadow-sm">
                            <Card.Header className="bg-white border-0 py-3">
                              <h5 className="mb-0">
                                <GraphUp className="me-2 text-success" />
                                Recent Grades & Performance
                              </h5>
                            </Card.Header>
                            <Card.Body>
                              {gradesData.slice(0, 5).map((grade, index) => (
                                <div key={index} className="d-flex justify-content-between align-items-center py-2 border-bottom">
                                  <div>
                                    <h6 className="mb-1">{grade.subject}</h6>
                                    <small className="text-muted">{grade.assignment || 'Overall'}</small>
                                  </div>
                                  <div className="text-end">
                                    <Badge bg={getGradeColor(grade.score || grade.grade)} className="fs-6 px-3 py-2">
                                      {grade.score || grade.grade}%
                                    </Badge>
                                    <div>
                                      <small className="text-muted">
                                        Grade: {getGradeLetter(grade.score || grade.grade)}
                                      </small>
                                    </div>
                                  </div>
                                </div>
                              ))}
                              {gradesData.length === 0 && (
                                <div className="text-center py-4">
                                  <Award size={32} className="text-muted mb-3" />
                                  <p className="text-muted mb-0">No grade data available</p>
                                </div>
                              )}
                            </Card.Body>
                          </Card>
                        </Col>

                        {/* Quick Actions */}
                        <Col lg={4}>
                          <Card className="border-0 shadow-sm h-100">
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
                                  className="text-start py-2 d-flex align-items-center"
                                  onClick={() => handleNavigate('/student/assignments/submit')}
                                >
                                  <FileText className="me-3" size={16} />
                                  <div>
                                    <div className="fw-bold">Submit Work</div>
                                    <small className="text-muted">Upload assignments</small>
                                  </div>
                                </Button>
                                <Button 
                                  variant="outline-success" 
                                  className="text-start py-2 d-flex align-items-center"
                                  onClick={() => handleNavigate('/library')}
                                >
                                  <Book className="me-3" size={16} />
                                  <div>
                                    <div className="fw-bold">Browse Library</div>
                                    <small className="text-muted">Find books & resources</small>
                                  </div>
                                </Button>
                                <Button 
                                  variant="outline-warning" 
                                  className="text-start py-2 d-flex align-items-center"
                                  onClick={() => setActiveTab('notes')}
                                >
                                  <Bookmark className="me-3" size={16} />
                                  <div>
                                    <div className="fw-bold">Take Notes</div>
                                    <small className="text-muted">Create study notes</small>
                                  </div>
                                </Button>
                                <Button 
                                  variant="outline-info" 
                                  className="text-start py-2 d-flex align-items-center"
                                  onClick={() => handleNavigate('/student/reports')}
                                >
                                  <GraphUp className="me-3" size={16} />
                                  <div>
                                    <div className="fw-bold">View Reports</div>
                                    <small className="text-muted">Performance analysis</small>
                                  </div>
                                </Button>
                              </div>
                            </Card.Body>
                          </Card>
                        </Col>
                      </Row>
                    </div>
                  )}

                  {/* Timetable Tab */}
                  {activeTab === 'timetable' && (
                    <div className="timetable-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                          <h4 className="mb-0">Weekly Class Timetable</h4>
                          <small className="text-muted">
                            {academicInfo.academicYear?.name || 'Current Academic Year'}
                          </small>
                        </div>
                        <div className="d-flex gap-2">
                          <Button variant="outline-primary" size="sm">
                            <Download className="me-2" />
                            Export PDF
                          </Button>
                          <Button variant="outline-secondary" size="sm">
                            <Calendar className="me-2" />
                            Calendar View
                          </Button>
                        </div>
                      </div>
                      
                      {timetableData.length > 0 ? (
                        <div className="table-responsive">
                          <Table bordered className="timetable-table align-middle">
                            <thead className="table-primary">
                              <tr>
                                <th className="text-center">Time</th>
                                {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(day => (
                                  <th key={day} className="text-center">{day}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {Array.from({ length: 8 }).map((_, timeIndex) => {
                                const timeSlot = `${8 + timeIndex}:00`;
                                return (
                                  <tr key={timeIndex}>
                                    <td className="fw-bold text-center">{timeSlot}</td>
                                    {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].map(day => {
                                      const classItem = timetableData.find(item => 
                                        item.day?.toLowerCase() === day && item.time === timeSlot
                                      );
                                      return (
                                        <td key={day} className="text-center p-2">
                                          {classItem ? (
                                            <div className="p-2 border rounded bg-light">
                                              <div className="fw-semibold">{classItem.subject}</div>
                                              <small className="text-muted d-block">{classItem.teacher}</small>
                                              <small className="text-muted">{classItem.room}</small>
                                            </div>
                                          ) : (
                                            <span className="text-muted">—</span>
                                          )}
                                        </td>
                                      );
                                    })}
                                  </tr>
                                );
                              })}
                            </tbody>
                          </Table>
                        </div>
                      ) : (
                        <div className="text-center py-5">
                          <Calendar size={48} className="text-muted mb-3" />
                          <h5>No timetable available</h5>
                          <p className="text-muted">Timetable will be updated soon</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Assignments Tab */}
                  {activeTab === 'assignments' && (
                    <div className="assignments-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                          <h4 className="mb-0">Assignments & Homework</h4>
                          <small className="text-muted">
                            Track and submit your assignments
                          </small>
                        </div>
                        <Button variant="primary" size="sm" onClick={() => handleNavigate('/student/assignments/submit')}>
                          <FileText className="me-2" />
                          Submit Work
                        </Button>
                      </div>
                      
                      {/* Filters and Search */}
                      <Card className="border-0 shadow-sm mb-4">
                        <Card.Body>
                          <Row className="g-3">
                            <Col md={6}>
                              <InputGroup>
                                <InputGroup.Text>
                                  <Search />
                                </InputGroup.Text>
                                <FormControl
                                  placeholder="Search assignments..."
                                  value={searchQuery}
                                  onChange={(e) => setSearchQuery(e.target.value)}
                                />
                              </InputGroup>
                            </Col>
                            <Col md={3}>
                              <Form.Select 
                                value={filterStatus}
                                onChange={(e) => setFilterStatus(e.target.value)}
                              >
                                <option value="all">All Status</option>
                                <option value="pending">Pending</option>
                                <option value="submitted">Submitted</option>
                                <option value="graded">Graded</option>
                                <option value="overdue">Overdue</option>
                              </Form.Select>
                            </Col>
                            <Col md={3}>
                              <Form.Select 
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                              >
                                <option value="due_date">Sort by Due Date</option>
                                <option value="subject">Sort by Subject</option>
                                <option value="priority">Sort by Priority</option>
                              </Form.Select>
                            </Col>
                          </Row>
                        </Card.Body>
                      </Card>

                      <div className="table-responsive">
                        <Table hover className="align-middle">
                          <thead className="table-light">
                            <tr>
                              <th>Subject</th>
                              <th>Assignment</th>
                              <th>Due Date</th>
                              <th>Status</th>
                              <th>Score</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {filteredAssignments.map((assignment, index) => (
                              <tr key={index}>
                                <td className="fw-semibold">
                                  <div className="d-flex align-items-center">
                                    <JournalText size={16} className="me-2 text-primary" />
                                    {assignment.subject}
                                  </div>
                                </td>
                                <td>
                                  <div className="fw-semibold" style={{ cursor: 'pointer' }} onClick={() => handleViewAssignment(assignment)}>
                                    {assignment.title}
                                  </div>
                                  <small className="text-muted">{assignment.description?.substring(0, 50)}...</small>
                                </td>
                                <td>
                                  <div>{formatDate(assignment.due_date)}</div>
                                  <small className="text-muted">
                                    {formatTime(assignment.due_time)}
                                  </small>
                                </td>
                                <td>{getAssignmentStatusBadge(assignment)}</td>
                                <td>
                                  {assignment.score ? (
                                    <Badge bg={getGradeColor(assignment.score)}>
                                      {assignment.score}%
                                    </Badge>
                                  ) : (
                                    <span className="text-muted">—</span>
                                  )}
                                </td>
                                <td>
                                  <div className="d-flex gap-1">
                                    <Button 
                                      variant="outline-primary" 
                                      size="sm"
                                      onClick={() => handleViewAssignment(assignment)}
                                    >
                                      <Eye size={12} />
                                    </Button>
                                    {assignment.status !== 'submitted' && assignment.status !== 'graded' && (
                                      <Button 
                                        variant="warning" 
                                        size="sm"
                                        onClick={() => handleNavigate(`/student/assignments/${assignment.id}/submit`)}
                                      >
                                        Submit
                                      </Button>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            ))}
                            {filteredAssignments.length === 0 && (
                              <tr>
                                <td colSpan="6" className="text-center py-5">
                                  <Journal size={48} className="text-muted mb-3" />
                                  <h5>No assignments found</h5>
                                  <p className="text-muted">You're all caught up!</p>
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </Table>
                      </div>
                    </div>
                  )}

                  {/* Grades Tab */}
                  {activeTab === 'grades' && (
                    <div className="grades-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                          <h4 className="mb-0">Academic Performance</h4>
                          <small className="text-muted">
                            Track your grades and academic progress
                          </small>
                        </div>
                        <Badge bg="success" className="fs-6 px-3 py-2">
                          Average: {stats.averageGrade}% ({getGradeLetter(stats.averageGrade)})
                        </Badge>
                      </div>
                      
                      {/* Performance Summary */}
                      <Row className="mb-4">
                        {gradesData.slice(0, 4).map((subject, index) => (
                          <Col lg={3} md={6} key={index} className="mb-3">
                            <Card className="border-0 shadow-sm h-100">
                              <Card.Body className="text-center">
                                <h6 className="mb-3">{subject.subject}</h6>
                                <div className="display-4 fw-bold mb-2" style={{ color: `var(--bs-${getGradeColor(subject.score || subject.grade)})` }}>
                                  {subject.score || subject.grade}%
                                </div>
                                <Badge bg={getGradeColor(subject.score || subject.grade)}>
                                  {getGradeLetter(subject.score || subject.grade)}
                                </Badge>
                                <div className="mt-3">
                                  <small className="text-muted">{subject.assignment || 'Overall'}</small>
                                </div>
                              </Card.Body>
                            </Card>
                          </Col>
                        ))}
                      </Row>

                      <div className="table-responsive">
                        <Table hover className="align-middle">
                          <thead className="table-light">
                            <tr>
                              <th>Subject</th>
                              <th>Assignment</th>
                              <th>Score</th>
                              <th>Grade</th>
                              <th>Date</th>
                              <th>Feedback</th>
                            </tr>
                          </thead>
                          <tbody>
                            {gradesData.map((grade, index) => (
                              <tr key={index}>
                                <td className="fw-semibold">{grade.subject}</td>
                                <td>{grade.assignment || 'Overall'}</td>
                                <td>
                                  <Badge bg={getGradeColor(grade.score || grade.grade)} className="fs-6">
                                    {grade.score || grade.grade}%
                                  </Badge>
                                </td>
                                <td>
                                  <strong className={`text-${getGradeColor(grade.score || grade.grade)}`}>
                                    {getGradeLetter(grade.score || grade.grade)}
                                  </strong>
                                </td>
                                <td>
                                  {grade.date ? formatDate(grade.date) : 'N/A'}
                                </td>
                                <td>
                                  <small className="text-muted">
                                    {grade.feedback || 'No feedback provided'}
                                  </small>
                                </td>
                              </tr>
                            ))}
                            {gradesData.length === 0 && (
                              <tr>
                                <td colSpan="6" className="text-center py-5">
                                  <Award size={48} className="text-muted mb-3" />
                                  <h5>No grade data available</h5>
                                  <p className="text-muted">Grades will appear here once available</p>
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </Table>
                      </div>
                    </div>
                  )}

                  {/* Attendance Tab */}
                  {activeTab === 'attendance' && (
                    <div className="attendance-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                          <h4 className="mb-0">Attendance Record</h4>
                          <small className="text-muted">
                            Track your attendance and punctuality
                          </small>
                        </div>
                        <Badge bg="info" className="fs-6 px-3 py-2">
                          Overall: {stats.attendanceRate}%
                        </Badge>
                      </div>
                      
                      {/* Attendance Summary */}
                      <Row className="mb-4">
                        <Col md={3} sm={6} className="mb-3">
                          <Card className="border-0 shadow-sm text-center">
                            <Card.Body>
                              <div className="text-success fw-bold fs-4">
                                {attendanceData.filter(a => a.status === 'present').length}
                              </div>
                              <div className="text-muted">Present Days</div>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col md={3} sm={6} className="mb-3">
                          <Card className="border-0 shadow-sm text-center">
                            <Card.Body>
                              <div className="text-danger fw-bold fs-4">
                                {attendanceData.filter(a => a.status === 'absent').length}
                              </div>
                              <div className="text-muted">Absent Days</div>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col md={3} sm={6} className="mb-3">
                          <Card className="border-0 shadow-sm text-center">
                            <Card.Body>
                              <div className="text-warning fw-bold fs-4">
                                {attendanceData.filter(a => a.status === 'late').length}
                              </div>
                              <div className="text-muted">Late Arrivals</div>
                            </Card.Body>
                          </Card>
                        </Col>
                        <Col md={3} sm={6} className="mb-3">
                          <Card className="border-0 shadow-sm text-center">
                            <Card.Body>
                              <div className="text-info fw-bold fs-4">
                                {attendanceData.filter(a => a.status === 'excused').length}
                              </div>
                              <div className="text-muted">Excused Absences</div>
                            </Card.Body>
                          </Card>
                        </Col>
                      </Row>

                      <div className="table-responsive">
                        <Table hover className="align-middle">
                          <thead className="table-light">
                            <tr>
                              <th>Date</th>
                              <th>Subject</th>
                              <th>Status</th>
                              <th>Teacher</th>
                              <th>Remarks</th>
                            </tr>
                          </thead>
                          <tbody>
                            {attendanceData.slice(0, 20).map((attendance, index) => {
                              const status = {
                                'present': { variant: 'success', text: 'Present ✓' },
                                'absent': { variant: 'danger', text: 'Absent ✗' },
                                'late': { variant: 'warning', text: 'Late ⏰' },
                                'excused': { variant: 'info', text: 'Excused 💬' }
                              }[attendance.status] || { variant: 'secondary', text: 'Unknown' };
                              
                              return (
                                <tr key={index}>
                                  <td>{formatDate(attendance.date)}</td>
                                  <td>{attendance.subject}</td>
                                  <td>
                                    <Badge bg={status.variant}>{status.text}</Badge>
                                  </td>
                                  <td>{attendance.teacher}</td>
                                  <td>
                                    <small className="text-muted">
                                      {attendance.remarks || '—'}
                                    </small>
                                  </td>
                                </tr>
                              );
                            })}
                            {attendanceData.length === 0 && (
                              <tr>
                                <td colSpan="5" className="text-center py-5">
                                  <CheckCircle size={48} className="text-muted mb-3" />
                                  <h5>No attendance records</h5>
                                  <p className="text-muted">Attendance data will appear here</p>
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </Table>
                      </div>
                    </div>
                  )}

                  {/* Library Tab */}
                  {activeTab === 'library' && (
                    <div className="library-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                          <h4 className="mb-0">Digital Library</h4>
                          <small className="text-muted">
                            Access books, resources, and study materials
                          </small>
                        </div>
                        <Button variant="primary" size="sm" onClick={() => handleNavigate('/library')}>
                          <Book className="me-2" />
                          Browse Library
                        </Button>
                      </div>
                      
                      <Row>
                        {libraryData.slice(0, 8).map((book, index) => (
                          <Col xl={3} lg={4} md={6} className="mb-3" key={index}>
                            <Card className="h-100 border-0 shadow-sm hover-lift">
                              <Card.Body className="p-3">
                                <div className="d-flex align-items-start mb-3">
                                  <div className="bg-primary bg-opacity-10 rounded p-2 me-3">
                                    <Book size={20} className="text-primary" />
                                  </div>
                                  <div>
                                    <h6 className="mb-1">{book.title}</h6>
                                    <small className="text-muted">by {book.author}</small>
                                  </div>
                                </div>
                                <div className="d-flex justify-content-between text-muted small mb-3">
                                  <span>Due: {formatDate(book.due_date)}</span>
                                  <Badge bg={new Date(book.due_date) < new Date() ? 'danger' : 'success'}>
                                    {new Date(book.due_date) < new Date() ? 'Overdue' : 'Active'}
                                  </Badge>
                                </div>
                                <div className="d-grid gap-1">
                                  <Button variant="outline-primary" size="sm">
                                    Read Online
                                  </Button>
                                  <Button variant="outline-secondary" size="sm">
                                    Download
                                  </Button>
                                </div>
                              </Card.Body>
                            </Card>
                          </Col>
                        ))}
                        {libraryData.length === 0 && (
                          <Col className="text-center py-5">
                            <Book size={48} className="text-muted mb-3" />
                            <h5>No borrowed books</h5>
                            <p className="text-muted mb-3">Visit the library to borrow books</p>
                            <Button variant="primary" onClick={() => handleNavigate('/library')}>
                              Explore Library
                            </Button>
                          </Col>
                        )}
                      </Row>
                    </div>
                  )}

                  {/* Resources Tab */}
                  {activeTab === 'resources' && (
                    <div className="resources-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <h4 className="mb-0">Learning Resources</h4>
                        <Button variant="outline-primary" size="sm">
                          <Download className="me-2" />
                          Download All
                        </Button>
                      </div>
                      
                      <Row>
                        {resourcesData.slice(0, 9).map((resource, index) => (
                          <Col xl={4} lg={4} md={6} className="mb-3" key={index}>
                            <Card className="h-100 border-0 shadow-sm hover-lift">
                              <Card.Body className="p-3">
                                <div className="d-flex align-items-start mb-3">
                                  <div className="me-3">
                                    {getResourceIcon(resource.file_type)}
                                  </div>
                                  <div className="flex-grow-1">
                                    <h6 className="mb-1">{resource.name || resource.title}</h6>
                                    <small className="text-muted">{resource.description?.substring(0, 60)}...</small>
                                  </div>
                                </div>
                                <div className="d-flex justify-content-between align-items-center">
                                  <small className="text-muted">
                                    {resource.size ? `${Math.round(resource.size / 1024)} KB` : 'N/A'}
                                  </small>
                                  <div className="d-flex gap-1">
                                    <Button 
                                      variant="outline-primary" 
                                      size="sm"
                                      onClick={() => handleDownloadResource(resource.id)}
                                    >
                                      <Download size={12} />
                                    </Button>
                                    <Button variant="outline-secondary" size="sm">
                                      <Eye size={12} />
                                    </Button>
                                  </div>
                                </div>
                              </Card.Body>
                            </Card>
                          </Col>
                        ))}
                        {resourcesData.length === 0 && (
                          <Col className="text-center py-5">
                            <Folder size={48} className="text-muted mb-3" />
                            <h5>No resources available</h5>
                            <p className="text-muted">Resources will be added soon</p>
                          </Col>
                        )}
                      </Row>
                    </div>
                  )}

                  {/* Notes Tab */}
                  {activeTab === 'notes' && (
                    <div className="notes-tab">
                      <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                          <h4 className="mb-0">Study Notes</h4>
                          <small className="text-muted">
                            Create and manage your study notes
                          </small>
                        </div>
                        <Button variant="primary" size="sm" onClick={() => handleNavigate('/notes/create')}>
                          <BookmarkCheck className="me-2" />
                          New Note
                        </Button>
                      </div>
                      
                      <Row>
                        {notesData.slice(0, 6).map((note, index) => (
                          <Col lg={4} md={6} className="mb-3" key={index}>
                            <Card className="h-100 border-0 shadow-sm hover-lift">
                              <Card.Body>
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                  <h6 className="mb-0">{note.title}</h6>
                                  <Badge bg="light" text="dark">{note.subject}</Badge>
                                </div>
                                <p className="text-muted small mb-3">
                                  {note.content?.substring(0, 100)}...
                                </p>
                                <div className="d-flex justify-content-between text-muted small">
                                  <span>{formatDate(note.created_at)}</span>
                                  <div className="d-flex gap-1">
                                    <Button variant="outline-primary" size="sm">
                                      <Eye size={12} />
                                    </Button>
                                    <Button variant="outline-secondary" size="sm">
                                      <Share size={12} />
                                    </Button>
                                  </div>
                                </div>
                              </Card.Body>
                            </Card>
                          </Col>
                        ))}
                        {notesData.length === 0 && (
                          <Col className="text-center py-5">
                            <Bookmark size={48} className="text-muted mb-3" />
                            <h5>No notes yet</h5>
                            <p className="text-muted mb-3">Start taking notes for your studies</p>
                            <Button variant="primary" onClick={() => handleNavigate('/notes/create')}>
                              Create Your First Note
                            </Button>
                          </Col>
                        )}
                      </Row>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Assignment Detail Modal */}
      <Modal show={showAssignmentModal} onHide={() => setShowAssignmentModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Assignment Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedAssignment && (
            <div>
              <h5>{selectedAssignment.title}</h5>
              <div className="d-flex gap-2 mb-3">
                <Badge bg="primary">{selectedAssignment.subject}</Badge>
                <Badge bg="secondary">{selectedAssignment.type}</Badge>
                {getAssignmentStatusBadge(selectedAssignment)}
              </div>
              <p>{selectedAssignment.description}</p>
              <div className="mb-3">
                <strong>Due Date:</strong> {formatDate(selectedAssignment.due_date)} at {formatTime(selectedAssignment.due_time)}
              </div>
              {selectedAssignment.instructions && (
                <div className="mb-3">
                  <strong>Instructions:</strong>
                  <p className="text-muted">{selectedAssignment.instructions}</p>
                </div>
              )}
              {selectedAssignment.attachments && selectedAssignment.attachments.length > 0 && (
                <div className="mb-3">
                  <strong>Attachments:</strong>
                  <div className="mt-2">
                    {selectedAssignment.attachments.map((file, idx) => (
                      <Button key={idx} variant="outline-secondary" size="sm" className="me-2 mb-2">
                        <FileText className="me-1" size={12} />
                        {file.name}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAssignmentModal(false)}>
            Close
          </Button>
          {selectedAssignment?.status !== 'submitted' && selectedAssignment?.status !== 'graded' && (
            <Button 
              variant="primary" 
              onClick={() => {
                handleNavigate(`/student/assignments/${selectedAssignment.id}/submit`);
                setShowAssignmentModal(false);
              }}
            >
              Submit Work
            </Button>
          )}
        </Modal.Footer>
      </Modal>

      {/* Notifications Modal */}
      <Modal show={showNotifications} onHide={() => setShowNotifications(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Notifications</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ListGroup variant="flush">
            {notifications.map((notification, idx) => (
              <ListGroup.Item key={idx} className="py-3">
                <div className="d-flex align-items-start">
                  <Bell size={20} className="me-3 text-primary mt-1" />
                  <div className="flex-grow-1">
                    <h6 className="mb-1">{notification.title}</h6>
                    <p className="mb-1">{notification.message}</p>
                    <small className="text-muted">{formatDate(notification.created_at)}</small>
                  </div>
                </div>
              </ListGroup.Item>
            ))}
            {notifications.length === 0 && (
              <div className="text-center py-5">
                <Bell size={48} className="text-muted mb-3" />
                <h5>No notifications</h5>
                <p className="text-muted">You're all caught up!</p>
              </div>
            )}
          </ListGroup>
        </Modal.Body>
      </Modal>

      {/* Footer */}
      <footer className="bg-light py-3 mt-4 border-top">
        <Container>
          <Row className="justify-content-between align-items-center">
            <Col md={6}>
              <small className="text-muted">
                &copy; {new Date().getFullYear()} School Management System - Student Portal
              </small>
            </Col>
            <Col md={6} className="text-end">
              <small className="text-muted">
                Last sync: {new Date().toLocaleString()} • 
                {refreshing && <span className="ms-2">🔄 Syncing data...</span>}
              </small>
            </Col>
          </Row>
        </Container>
      </footer>

      <style jsx>{`
        .portal-hero {
          background: linear-gradient(135deg, var(--bs-primary) 0%, #0d6efd 100%);
        }
        
        .portal-nav-item {
          border-radius: 50px;
          transition: all 0.3s ease;
        }
        
        .portal-nav-item:hover {
          transform: translateX(5px);
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .hover-lift {
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .hover-lift:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        }
        
        .hover-item:hover {
          background-color: rgba(0,0,0,0.02);
        }
        
        .timetable-table td {
          vertical-align: middle;
        }
        
        .spinning {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .student-portal-page {
          background-color: #f8f9fa;
          min-height: 100vh;
        }
        
        .bg-gradient-primary {
          background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        }
      `}</style>
    </div>
  );
}

export default StudentPortal;