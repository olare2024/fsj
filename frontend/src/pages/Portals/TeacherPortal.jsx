import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
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
  Dropdown,
  Placeholder,
  Modal,
  Form
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  ArrowClockwise, 
  FileText, 
  People, 
  Clock, 
  CheckCircle, 
  Plus, 
  Eye, 
  PersonCircle,
  CalendarEvent,
  ExclamationTriangle,
  FileEarmark,
  Download,
  Book,
  Person,
  Calendar,
  Journal,
  GraphUp,
  Bell,
  ClockHistory,
  Check2Circle,
  Award,
  FileEarmarkText,
  FileEarmarkCheck,
  FileEarmarkBarGraph,
  Gear,
  ThreeDotsVertical,
  ChevronRight,
  Search,
  Filter,
  SortDown,
  Pencil,
  Trash,
  Upload,
  Clock as ClockIcon,
  BarChart,
  Envelope,
  Telephone,
  House,
  Briefcase,
  CardChecklist
} from 'react-bootstrap-icons';

// ==================== IMPORT APIS ====================
import { teacherAPI } from '../../services/teacherAPI';  // Your teacher API
import authAPI from '../../services/authAPI';
import notesAPI from '../../services/notesAPI';
import libraryAPI from '../../services/libraryAPI';
import timetableAPI from '../../services/timetableAPI';
import { gradesAPI } from '../../services/gradesAPI';
import { attendanceAPI } from '../../services/attendanceAPI';
import assignmentsAPI from '../../services/assignmentsAPI';
import academicAPI from '../../services/academicAPI';
import downloadsAPI from '../../services/downloadsAPI';

// ==================== HELPER COMPONENTS ====================
const SkeletonLoader = ({ count = 3, height = 100 }) => (
  <div className="skeleton-container">
    {Array.from({ length: count }).map((_, i) => (
      <Card key={i} className="border-0 shadow-sm mb-3">
        <Card.Body>
          <Placeholder as={Card.Title} animation="wave">
            <Placeholder xs={6} />
          </Placeholder>
          <Placeholder as={Card.Text} animation="wave">
            <Placeholder xs={12} />
            <Placeholder xs={8} />
          </Placeholder>
        </Card.Body>
      </Card>
    ))}
  </div>
);

const TabErrorBoundary = ({ children, fallback = null }) => {
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const handleError = (error) => {
      console.error('Tab Error:', error);
      setHasError(true);
    };

    window.addEventListener('error', handleError);
    
    return () => {
      window.removeEventListener('error', handleError);
    };
  }, []);

  if (hasError) {
    return fallback || (
      <Alert variant="warning" className="m-3">
        <Alert.Heading>Something went wrong</Alert.Heading>
        <p>This section couldn't be loaded. Try refreshing the tab.</p>
        <Button variant="outline-warning" size="sm" onClick={() => setHasError(false)}>
          Retry
        </Button>
      </Alert>
    );
  }

  return children;
};

// ==================== MODAL COMPONENTS ====================
const LeaveApplicationModal = ({ show, onHide, onSubmit }) => {
  const [formData, setFormData] = useState({
    leave_type: '',
    start_date: '',
    end_date: '',
    reason: '',
    emergency_contact: '',
    address_during_leave: ''
  });

  const handleSubmit = () => {
    onSubmit(formData);
    onHide();
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Apply for Leave</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Leave Type</Form.Label>
                <Form.Select 
                  value={formData.leave_type}
                  onChange={(e) => setFormData({...formData, leave_type: e.target.value})}
                >
                  <option value="">Select leave type</option>
                  <option value="annual">Annual Leave</option>
                  <option value="sick">Sick Leave</option>
                  <option value="maternity">Maternity Leave</option>
                  <option value="paternity">Paternity Leave</option>
                  <option value="compassionate">Compassionate Leave</option>
                  <option value="study">Study Leave</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Emergency Contact</Form.Label>
                <Form.Control 
                  type="text"
                  placeholder="Phone number"
                  value={formData.emergency_contact}
                  onChange={(e) => setFormData({...formData, emergency_contact: e.target.value})}
                />
              </Form.Group>
            </Col>
          </Row>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Start Date</Form.Label>
                <Form.Control 
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>End Date</Form.Label>
                <Form.Control 
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                />
              </Form.Group>
            </Col>
          </Row>
          <Form.Group className="mb-3">
            <Form.Label>Address During Leave</Form.Label>
            <Form.Control 
              as="textarea"
              rows={2}
              placeholder="Where will you be during your leave?"
              value={formData.address_during_leave}
              onChange={(e) => setFormData({...formData, address_during_leave: e.target.value})}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Reason</Form.Label>
            <Form.Control 
              as="textarea"
              rows={3}
              placeholder="Please provide details for your leave request"
              value={formData.reason}
              onChange={(e) => setFormData({...formData, reason: e.target.value})}
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit}>
          Submit Application
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

const UploadDocumentModal = ({ show, onHide, onSubmit }) => {
  const [formData, setFormData] = useState({
    document_type: '',
    title: '',
    file: null,
    description: '',
    expiry_date: ''
  });

  const handleFileChange = (e) => {
    setFormData({...formData, file: e.target.files[0]});
  };

  const handleSubmit = () => {
    const data = new FormData();
    Object.keys(formData).forEach(key => {
      if (formData[key]) {
        data.append(key, formData[key]);
      }
    });
    onSubmit(data);
    onHide();
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Upload Document</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Document Type</Form.Label>
            <Form.Select 
              value={formData.document_type}
              onChange={(e) => setFormData({...formData, document_type: e.target.value})}
            >
              <option value="">Select type</option>
              <option value="certificate">Certificate</option>
              <option value="id">ID Copy</option>
              <option value="tsc">TSC Certificate</option>
              <option value="contract">Employment Contract</option>
              <option value="performance">Performance Review</option>
              <option value="other">Other</option>
            </Form.Select>
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Title</Form.Label>
            <Form.Control 
              type="text"
              placeholder="Document title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control 
              as="textarea"
              rows={2}
              placeholder="Optional description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Expiry Date (if applicable)</Form.Label>
            <Form.Control 
              type="date"
              value={formData.expiry_date}
              onChange={(e) => setFormData({...formData, expiry_date: e.target.value})}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>File</Form.Label>
            <Form.Control 
              type="file"
              onChange={handleFileChange}
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit}>
          Upload
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

// ==================== MAIN COMPONENT ====================
const TeacherPortal = () => {
  const { currentUser, loading: authLoading, logout } = useAuth();
  const navigate = useNavigate();
  const isMounted = useRef(true);
  
  // Main state
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  // Section states
  const [classes, setClasses] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [libraryResources, setLibraryResources] = useState([]);
  const [timetable, setTimetable] = useState([]);
  const [academicData, setAcademicData] = useState({ academicYear: null });
  const [downloads, setDownloads] = useState([]);
  const [studentGrades, setStudentGrades] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  
  // Teacher-specific states
  const [teacherProfile, setTeacherProfile] = useState(null);
  const [teacherDocuments, setTeacherDocuments] = useState([]);
  const [teacherQualifications, setTeacherQualifications] = useState([]);
  const [teacherTrainings, setTeacherTrainings] = useState([]);
  const [teacherLeaves, setTeacherLeaves] = useState([]);
  const [teacherAssignments, setTeacherAssignments] = useState([]);
  const [teacherAttendance, setTeacherAttendance] = useState([]);
  const [performanceIndicators, setPerformanceIndicators] = useState([]);
  
  // UI states
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [assignmentFilter, setAssignmentFilter] = useState('all');
  
  // Modal states
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  // Stats
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalSubjects: 0,
    totalClasses: 0,
    attendanceRate: 0,
    pendingGrading: 0,
    overdueAssignments: 0,
    libraryBooks: 0,
    upcomingEvents: 0,
    downloadedResources: 0,
    averageGrade: 0,
    leavesUsed: 0,
    leavesRemaining: 0,
    documentsPending: 0,
    upcomingTrainings: 0
  });

  // ==================== HELPER FUNCTIONS ====================
  const extractArrayFromResponse = (responseData) => {
    if (!responseData) return [];
    
    if (responseData.success && responseData.data !== undefined) {
      return extractArrayFromResponse(responseData.data);
    }
    
    if (Array.isArray(responseData)) {
      return responseData;
    }
    
    const possibleArrayProps = [
      'results', 'data', 'items', 'records', 'list', 
      'assignments', 'grades', 'files', 'resources', 
      'schedule', 'classes', 'timetable', 'notifications',
      'students', 'subjects', 'events', 'documents',
      'qualifications', 'trainings', 'leaves'
    ];
    
    for (const prop of possibleArrayProps) {
      if (responseData[prop] && Array.isArray(responseData[prop])) {
        return responseData[prop];
      }
    }
    
    if (typeof responseData === 'object') {
      const allValues = Object.values(responseData);
      for (const value of allValues) {
        if (Array.isArray(value)) {
          return value;
        }
      }
    }
    
    return [];
  };

  const fetchWithErrorHandling = async (apiCall, errorMessage) => {
    try {
      const response = await apiCall();
      return response;
    } catch (err) {
      console.warn(`${errorMessage}:`, err);
      return { 
        success: false, 
        data: [], 
        message: err.response?.data?.error || err.message 
      };
    }
  };

  const validateClassData = (classData) => {
    if (!classData || typeof classData !== 'object') return null;
    
    return {
      id: classData.id || classData.uuid || Math.random().toString(36).substr(2, 9),
      name: classData.name || classData.class_name || 'Unnamed Class',
      subject: classData.subject_name || classData.subject || 'No Subject',
      gradeLevel: classData.grade_level || classData.grade || 'N/A',
      section: classData.section || 'Main',
      studentCount: classData.student_count || classData.enrolled_students || 0,
      subjectCode: classData.subject_code || '',
      isValid: true
    };
  };

  const validateAssignmentData = (assignmentData) => {
    if (!assignmentData || typeof assignmentData !== 'object') return null;
    
    return {
      id: assignmentData.id || assignmentData.uuid || Math.random().toString(36).substr(2, 9),
      title: assignmentData.title || 'Untitled Assignment',
      description: assignmentData.description || '',
      subject: assignmentData.subject_name || assignmentData.subject || 'No Subject',
      className: assignmentData.class_name || assignmentData.class || 'No Class',
      dueDate: assignmentData.due_date,
      dueTime: assignmentData.due_time,
      status: assignmentData.status?.toLowerCase() || 'draft',
      submissionsCount: assignmentData.submissions_count || 0,
      totalStudents: assignmentData.total_students || 0,
      createdAt: assignmentData.created_at || new Date().toISOString(),
      isValid: true
    };
  };

  // ==================== DATA FETCHING ====================
  const fetchTeacherDashboard = useCallback(async (showRefreshing = false) => {
    if (!isMounted.current) return;

    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');

      const teacherId = currentUser?.id;

      if (!teacherId) {
        throw new Error('No user ID available');
      }

      // Fetch teacher dashboard data
      const dashboardResult = await fetchWithErrorHandling(
        () => teacherAPI.getDashboard(),
        'Failed to fetch teacher dashboard'
      );

      if (dashboardResult.success && dashboardResult.data) {
        processDashboardData(dashboardResult.data);
      } else {
        // Fallback to individual APIs if dashboard fails
        await fetchIndividualTeacherData();
      }

      // Fetch additional teacher-specific data
      await fetchAdditionalTeacherData(teacherId);

    } catch (err) {
      if (isMounted.current) {
        setError('Failed to load teacher data. Please try again.');
        console.error('Error fetching teacher data:', err);
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, [currentUser?.id]);

  const processDashboardData = (dashboardData) => {
    if (!dashboardData) return;
    
    const {
      profile,
      classes = [],
      assignments = [],
      timetable = [],
      library_resources = [],
      attendance_records = [],
      student_grades = [],
      downloads = [],
      academic_year,
      statistics = {},
      notifications: apiNotifications = []
    } = dashboardData;

    // Set profile data
    if (profile) {
      setTeacherProfile(profile);
    }

    // Set academic data
    if (academic_year) {
      setAcademicData(prev => ({ ...prev, academicYear: academic_year }));
    }

    // Process classes
    const validatedClasses = Array.isArray(classes) 
      ? classes.map(validateClassData).filter(Boolean)
      : [];
    setClasses(validatedClasses);

    // Process assignments
    const validatedAssignments = Array.isArray(assignments)
      ? assignments.map(validateAssignmentData).filter(Boolean)
      : [];
    setAssignments(validatedAssignments);

    // Set other data
    setTimetable(Array.isArray(timetable) ? timetable : []);
    setLibraryResources(Array.isArray(library_resources) ? library_resources : []);
    setAttendanceRecords(Array.isArray(attendance_records) ? attendance_records : []);
    setStudentGrades(Array.isArray(student_grades) ? student_grades : []);
    setDownloads(Array.isArray(downloads) ? downloads : []);
    
    // Set notifications
    if (Array.isArray(apiNotifications)) {
      setNotifications(apiNotifications);
    }

    // Update stats from dashboard statistics
    if (statistics && typeof statistics === 'object') {
      setStats(prev => ({
        ...prev,
        totalStudents: statistics.total_students || 0,
        totalSubjects: statistics.total_subjects || 0,
        totalClasses: statistics.total_classes || 0,
        attendanceRate: statistics.attendance_rate || 0,
        pendingGrading: statistics.pending_grading || 0,
        overdueAssignments: statistics.overdue_assignments || 0,
        libraryBooks: statistics.library_books || 0,
        upcomingEvents: statistics.upcoming_events || 0,
        averageGrade: statistics.average_grade || 0
      }));
    }
  };

  const fetchIndividualTeacherData = async () => {
    const teacherId = currentUser?.id;
    
    const [
      profileResult,
      classesResult,
      assignmentsResult,
      timetableResult,
      attendanceResult,
      gradesResult
    ] = await Promise.allSettled([
      fetchWithErrorHandling(() => teacherAPI.getMyProfile(), 'Failed to fetch profile'),
      fetchWithErrorHandling(() => teacherAPI.getCurrentAssignments(), 'Failed to fetch assignments'),
      fetchWithErrorHandling(() => academicAPI.getClasses(), 'Failed to fetch classes'),
      fetchWithErrorHandling(() => timetableAPI.getTeacherTimetable(), 'Failed to fetch timetable'),
      fetchWithErrorHandling(() => teacherAPI.getAttendance({ teacher_id: teacherId }), 'Failed to fetch attendance'),
      fetchWithErrorHandling(() => gradesAPI.getGrades({ teacher_id: teacherId }), 'Failed to fetch grades')
    ]);

    if (profileResult.status === 'fulfilled' && profileResult.value.success) {
      setTeacherProfile(profileResult.value.data);
    }

    if (classesResult.status === 'fulfilled' && classesResult.value.success) {
      const classesData = extractArrayFromResponse(classesResult.value.data);
      const validatedClasses = classesData.map(validateClassData).filter(Boolean);
      setClasses(validatedClasses);
    }

    if (assignmentsResult.status === 'fulfilled' && assignmentsResult.value.success) {
      const assignmentsData = extractArrayFromResponse(assignmentsResult.value.data);
      const validatedAssignments = assignmentsData.map(validateAssignmentData).filter(Boolean);
      setAssignments(validatedAssignments);
    }

    if (timetableResult.status === 'fulfilled' && timetableResult.value.success) {
      const timetableData = extractArrayFromResponse(timetableResult.value.data);
      setTimetable(timetableData);
    }

    if (attendanceResult.status === 'fulfilled' && attendanceResult.value.success) {
      const attendanceData = extractArrayFromResponse(attendanceResult.value.data);
      setAttendanceRecords(attendanceData);
    }

    if (gradesResult.status === 'fulfilled' && gradesResult.value.success) {
      const gradesData = extractArrayFromResponse(gradesResult.value.data);
      setStudentGrades(gradesData);
    }
  };

  const fetchAdditionalTeacherData = async (teacherId) => {
    const [
      documentsResult,
      qualificationsResult,
      trainingsResult,
      leavesResult,
      performanceResult
    ] = await Promise.allSettled([
      fetchWithErrorHandling(() => teacherAPI.getDocuments({ teacher_id: teacherId }), 'Failed to fetch documents'),
      fetchWithErrorHandling(() => teacherAPI.getQualifications({ teacher_id: teacherId }), 'Failed to fetch qualifications'),
      fetchWithErrorHandling(() => teacherAPI.getUpcomingTrainings(), 'Failed to fetch trainings'),
      fetchWithErrorHandling(() => teacherAPI.getCurrentLeaves(), 'Failed to fetch leaves'),
      fetchWithErrorHandling(() => teacherAPI.getPerformanceSummary(), 'Failed to fetch performance')
    ]);

    if (documentsResult.status === 'fulfilled' && documentsResult.value.success) {
      const documentsData = extractArrayFromResponse(documentsResult.value.data);
      setTeacherDocuments(documentsData);
    }

    if (qualificationsResult.status === 'fulfilled' && qualificationsResult.value.success) {
      const qualificationsData = extractArrayFromResponse(qualificationsResult.value.data);
      setTeacherQualifications(qualificationsData);
    }

    if (trainingsResult.status === 'fulfilled' && trainingsResult.value.success) {
      const trainingsData = extractArrayFromResponse(trainingsResult.value.data);
      setTeacherTrainings(trainingsData);
    }

    if (leavesResult.status === 'fulfilled' && leavesResult.value.success) {
      const leavesData = extractArrayFromResponse(leavesResult.value.data);
      setTeacherLeaves(leavesData);
    }

    if (performanceResult.status === 'fulfilled' && performanceResult.value.success) {
      const performanceData = extractArrayFromResponse(performanceResult.value.data);
      setPerformanceIndicators(performanceData);
    }
  };

  // ==================== USE EFFECTS ====================
  useEffect(() => {
    isMounted.current = true;
    
    const loadData = async () => {
      if (!authLoading && currentUser) {
        await fetchTeacherDashboard();
      }
    };
    
    loadData();
    
    return () => {
      isMounted.current = false;
    };
  }, [authLoading, currentUser, fetchTeacherDashboard]);

  // ==================== MEMOIZED CALCULATIONS ====================
  const classStats = useMemo(() => {
    if (!Array.isArray(classes)) return {};
    
    const totalStudents = classes.reduce((acc, cls) => 
      acc + (cls.studentCount || 0), 0);
    
    const uniqueSubjects = new Set(
      classes.map(cls => cls.subject).filter(Boolean)
    );
    
    return {
      totalStudents,
      uniqueSubjects: uniqueSubjects.size,
      totalClasses: classes.length
    };
  }, [classes]);

  const assignmentStats = useMemo(() => {
    if (!Array.isArray(assignments)) return {};
    
    const pending = assignments.filter(a => 
      a.status === 'submitted' || a.status === 'pending_review'
    );
    
    const overdue = assignments.filter(a => 
      a.status === 'overdue' || 
      (a.dueDate && new Date(a.dueDate) < new Date() && a.status !== 'graded')
    );
    
    const graded = assignments.filter(a => a.status === 'graded');
    
    return {
      pending: pending.length,
      overdue: overdue.length,
      graded: graded.length,
      total: assignments.length,
      completionRate: assignments.length > 0 ? 
        Math.round((graded.length / assignments.length) * 100) : 0
    };
  }, [assignments]);

  const upcomingClasses = useMemo(() => {
    if (!Array.isArray(timetable)) return [];
    
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    return timetable
      .filter(event => {
        const eventDate = new Date(event.start_time || event.date || Date.now());
        const eventDay = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());
        return eventDay.getTime() === today.getTime() && eventDate >= now;
      })
      .sort((a, b) => {
        const dateA = new Date(a.start_time || a.date || Date.now());
        const dateB = new Date(b.start_time || b.date || Date.now());
        return dateA - dateB;
      })
      .slice(0, 5);
  }, [timetable]);

  const pendingGrading = useMemo(() => {
    if (!Array.isArray(assignments)) return [];
    
    return assignments
      .filter(a => 
        a.status === 'submitted' || a.status === 'pending_review'
      )
      .sort((a, b) => {
        const dateA = new Date(a.dueDate || a.createdAt || 0);
        const dateB = new Date(b.dueDate || b.createdAt || 0);
        return dateA - dateB;
      })
      .slice(0, 5);
  }, [assignments]);

  const recentGrades = useMemo(() => {
    if (!Array.isArray(studentGrades)) return [];
    
    return [...studentGrades]
      .filter(grade => grade.score !== undefined && grade.score !== null)
      .sort((a, b) => {
        const dateA = new Date(a.date || a.graded_at || a.created_at || 0);
        const dateB = new Date(b.date || b.graded_at || b.created_at || 0);
        return dateB - dateA;
      })
      .slice(0, 5);
  }, [studentGrades]);

  const filteredAssignments = useMemo(() => {
    if (!Array.isArray(assignments)) return [];
    
    let filtered = [...assignments];
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(a => 
        a.title.toLowerCase().includes(query) ||
        a.subject.toLowerCase().includes(query) ||
        a.className.toLowerCase().includes(query) ||
        a.description.toLowerCase().includes(query)
      );
    }
    
    if (assignmentFilter !== 'all') {
      filtered = filtered.filter(a => 
        a.status === assignmentFilter.toLowerCase()
      );
    }
    
    return filtered;
  }, [assignments, searchQuery, assignmentFilter]);

  const unreadNotifications = useMemo(() => {
    if (!Array.isArray(notifications)) return 0;
    return notifications.filter(n => !n.read).length;
  }, [notifications]);

  const expiringDocuments = useMemo(() => {
    if (!Array.isArray(teacherDocuments)) return [];
    
    const now = new Date();
    const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
    
    return teacherDocuments.filter(doc => {
      if (!doc.expiry_date) return false;
      const expiryDate = new Date(doc.expiry_date);
      return expiryDate <= thirtyDaysFromNow && expiryDate >= now;
    });
  }, [teacherDocuments]);

  const pendingLeaves = useMemo(() => {
    if (!Array.isArray(teacherLeaves)) return [];
    return teacherLeaves.filter(leave => 
      leave.status === 'pending' || leave.status === 'submitted'
    );
  }, [teacherLeaves]);

  // ==================== EVENT HANDLERS ====================
  const handleRefresh = () => {
    fetchTeacherDashboard(true);
  };

  const handleNavigate = (path) => {
    navigate(path);
  };

  const handleApplyForLeave = async (leaveData) => {
    try {
      const result = await teacherAPI.applyForLeave(leaveData);
      if (result.success) {
        setTeacherLeaves(prev => [result.data, ...prev]);
        setError('');
      } else {
        setError(result.error?.message || 'Failed to apply for leave');
      }
    } catch (err) {
      setError('Failed to apply for leave. Please try again.');
    }
  };

  const handleUploadDocument = async (documentData) => {
    try {
      const result = await teacherAPI.uploadDocument(documentData);
      if (result.success) {
        setTeacherDocuments(prev => [result.data, ...prev]);
        setError('');
      } else {
        setError(result.error?.message || 'Failed to upload document');
      }
    } catch (err) {
      setError('Failed to upload document. Please try again.');
    }
  };

  const handleDownloadResource = async (fileId, fileName) => {
    try {
      const result = await downloadsAPI.downloadFile(fileId);
      if (result.success && result.data) {
        const url = window.URL.createObjectURL(new Blob([result.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', fileName || `resource-${fileId}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Download error:', err);
      setError('Failed to download resource. Please try again.');
    }
  };

  const handleMarkNotificationRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    );
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout error:', err);
      setError('Failed to logout. Please try again.');
    }
  };

  // ==================== UTILITY FUNCTIONS ====================
  const getUserDisplayInfo = () => {
    if (teacherProfile) {
      return {
        firstName: teacherProfile.first_name || teacherProfile.firstName || 'Teacher',
        lastName: teacherProfile.last_name || teacherProfile.lastName || '',
        avatar: teacherProfile.avatar || teacherProfile.profile_picture,
        initials: (teacherProfile.first_name?.charAt(0) || '') + (teacherProfile.last_name?.charAt(0) || '') || 'T',
        email: teacherProfile.email || currentUser?.email || '',
        role: teacherProfile.role || 'Teacher',
        tscNumber: teacherProfile.tsc_number || 'Not set',
        department: teacherProfile.department?.name || teacherProfile.department || 'No Department',
        specialization: teacherProfile.specialization || 'Not specified'
      };
    }
    return {
      firstName: currentUser?.first_name || currentUser?.firstName || 'Teacher',
      lastName: currentUser?.last_name || currentUser?.lastName || '',
      avatar: null,
      initials: 'T',
      email: currentUser?.email || '',
      role: currentUser?.role || 'Teacher',
      tscNumber: currentUser?.tsc_number || 'Not set',
      department: currentUser?.department || 'No Department',
      specialization: currentUser?.specialization || 'Not specified'
    };
  };

  const { 
    firstName, 
    lastName, 
    avatar, 
    initials, 
    email, 
    role,
    tscNumber,
    department,
    specialization 
  } = getUserDisplayInfo();

  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-KE').format(number || 0);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('en-KE', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    } catch {
      return 'Invalid date';
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    try {
      if (timeString.includes(':')) {
        return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-KE', {
          hour: '2-digit',
          minute: '2-digit'
        });
      }
      return timeString;
    } catch {
      return timeString;
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-KE', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Invalid date';
    }
  };

  const getAssignmentStatusVariant = (status) => {
    if (!status) return 'secondary';
    
    const statusLower = status.toLowerCase();
    switch (statusLower) {
      case 'submitted':
      case 'pending_review':
        return 'warning';
      case 'graded':
      case 'completed':
        return 'success';
      case 'overdue':
      case 'late':
        return 'danger';
      case 'draft':
        return 'secondary';
      case 'published':
      case 'active':
        return 'primary';
      default:
        return 'info';
    }
  };

  const getLeaveStatusVariant = (status) => {
    if (!status) return 'secondary';
    
    const statusLower = status.toLowerCase();
    switch (statusLower) {
      case 'approved':
        return 'success';
      case 'pending':
      case 'submitted':
        return 'warning';
      case 'rejected':
        return 'danger';
      case 'cancelled':
        return 'secondary';
      default:
        return 'info';
    }
  };

  const getDocumentStatusVariant = (status) => {
    if (!status) return 'secondary';
    
    const statusLower = status.toLowerCase();
    switch (statusLower) {
      case 'verified':
      case 'approved':
        return 'success';
      case 'pending':
        return 'warning';
      case 'rejected':
      case 'expired':
        return 'danger';
      default:
        return 'info';
    }
  };

  // ==================== RENDER LOADING STATE ====================
  if (authLoading || (loading && !refreshing)) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" size="lg" />
          <p className="mt-3 text-muted">Loading your teacher portal...</p>
          <SkeletonLoader count={3} />
        </div>
      </Container>
    );
  }

  // ==================== MAIN RENDER ====================
  return (
    <Container fluid className="mt-3 teacher-portal">
      {/* Enhanced Page Header */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 bg-gradient-primary text-white shadow-sm">
            <Card.Body className="py-4 px-4">
              <Row className="align-items-center">
                <Col md={8}>
                  <div className="d-flex align-items-center">
                    <div className="me-4 position-relative">
                      {avatar ? (
                        <Image 
                          src={avatar} 
                          roundedCircle 
                          width={80} 
                          height={80}
                          className="border border-3 border-white shadow"
                          alt={`${firstName}'s avatar`}
                          style={{ objectFit: 'cover' }}
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.parentElement.innerHTML = `
                              <div class="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow" style="width: 80px; height: 80px">
                                <span class="text-white fw-bold fs-4">${initials}</span>
                              </div>
                            `;
                          }}
                        />
                      ) : (
                        <div 
                          className="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow"
                          style={{ width: 80, height: 80 }}
                        >
                          <span className="text-white fw-bold fs-4">{initials}</span>
                        </div>
                      )}
                      <div className="position-absolute bottom-0 end-0 bg-success rounded-circle border border-3 border-white"
                           style={{ width: 20, height: 20 }}></div>
                    </div>
                    <div>
                      <div className="d-flex align-items-center mb-1">
                        <h1 className="h2 mb-0 me-2">Welcome back, {firstName}! 👨‍🏫</h1>
                        <Badge bg="light" text="dark" className="fs-6">
                          {role}
                        </Badge>
                      </div>
                      <p className="mb-1 opacity-75 d-flex align-items-center">
                        <Briefcase size={14} className="me-2" />
                        {department} • {specialization}
                      </p>
                      <p className="mb-1 opacity-75">
                        <CalendarEvent size={14} className="me-1" />
                        {academicData.academicYear?.name || 'Academic Year 2024'}
                      </p>
                      <small className="opacity-75 d-flex align-items-center">
                        <Clock size={12} className="me-1" />
                        Last updated: {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        {refreshing && <span className="ms-2">🔄 Refreshing...</span>}
                      </small>
                    </div>
                  </div>
                </Col>
                <Col md={4} className="text-end">
                  <div className="d-flex gap-2 justify-content-end flex-wrap align-items-center">
                    {/* Notifications */}
                    <Dropdown align="end">
                      <Dropdown.Toggle variant="light" className="position-relative">
                        <Bell size={18} />
                        {unreadNotifications > 0 && (
                          <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                            {unreadNotifications > 9 ? '9+' : unreadNotifications}
                          </span>
                        )}
                      </Dropdown.Toggle>
                      <Dropdown.Menu style={{ minWidth: '300px', maxHeight: '400px', overflowY: 'auto' }}>
                        <Dropdown.Header className="sticky-top bg-white">
                          <div className="d-flex justify-content-between align-items-center">
                            <span>Notifications</span>
                            {unreadNotifications > 0 && (
                              <Button 
                                variant="link" 
                                size="sm" 
                                className="p-0"
                                onClick={() => setNotifications(prev => 
                                  prev.map(n => ({ ...n, read: true }))
                                )}
                              >
                                Mark all as read
                              </Button>
                            )}
                          </div>
                        </Dropdown.Header>
                        {notifications.length > 0 ? (
                          <>
                            {notifications.slice(0, 5).map(notification => (
                              <Dropdown.Item 
                                key={notification.id}
                                className={`py-2 ${!notification.read ? 'fw-bold bg-light' : ''}`}
                                onClick={() => handleMarkNotificationRead(notification.id)}
                              >
                                <div className="d-flex justify-content-between align-items-start">
                                  <div>
                                    <div className="d-flex align-items-center mb-1">
                                      <Badge bg={
                                        notification.type === 'assignment' ? 'warning' :
                                        notification.type === 'meeting' ? 'info' : 'danger'
                                      } className="me-2">
                                        {notification.type}
                                      </Badge>
                                    </div>
                                    {notification.message}
                                    <div className="text-muted small">{notification.time}</div>
                                  </div>
                                  {!notification.read && (
                                    <span className="badge bg-primary">New</span>
                                  )}
                                </div>
                              </Dropdown.Item>
                            ))}
                            <Dropdown.Divider />
                            <Dropdown.Item as={Link} to="/teacher/notifications" className="text-center">
                              View all notifications
                            </Dropdown.Item>
                          </>
                        ) : (
                          <Dropdown.ItemText className="text-center py-3 text-muted">
                            No new notifications
                          </Dropdown.ItemText>
                        )}
                      </Dropdown.Menu>
                    </Dropdown>
                    
                    <Button 
                      variant="light" 
                      onClick={handleRefresh}
                      disabled={refreshing}
                      className="text-primary"
                    >
                      <ArrowClockwise className={`me-1 ${refreshing ? 'spinning' : ''}`} size={16} />
                      Refresh
                    </Button>
                    
                    <Button 
                      variant="white" 
                      className="text-primary d-none d-md-flex"
                      onClick={() => handleNavigate('/teacher/assignments/create')}
                    >
                      <Plus className="me-1" />
                      New Assignment
                    </Button>
                    
                    <Dropdown align="end">
                      <Dropdown.Toggle variant="light" size="sm">
                        <ThreeDotsVertical size={18} />
                      </Dropdown.Toggle>
                      <Dropdown.Menu>
                        <Dropdown.Header className="text-truncate" style={{ maxWidth: '200px' }}>
                          TSC: {tscNumber}
                        </Dropdown.Header>
                        <Dropdown.Item as={Link} to="/teacher/profile">
                          <PersonCircle className="me-2" />
                          My Profile
                        </Dropdown.Item>
                        <Dropdown.Item as={Link} to="/teacher/documents">
                          <FileEarmark className="me-2" />
                          My Documents
                        </Dropdown.Item>
                        <Dropdown.Item as={Link} to="/teacher/leaves">
                          <Calendar className="me-2" />
                          Leave Management
                        </Dropdown.Item>
                        <Dropdown.Divider />
                        <Dropdown.Item as={Link} to="/teacher/settings">
                          <Gear className="me-2" />
                          Settings
                        </Dropdown.Item>
                        <Dropdown.Divider />
                        <Dropdown.Item onClick={handleLogout} className="text-danger">
                          Logout
                        </Dropdown.Item>
                      </Dropdown.Menu>
                    </Dropdown>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Error Alert */}
      {error && (
        <Row className="px-3 mb-3">
          <Col>
            <Alert variant="warning" dismissible onClose={() => setError('')}>
              <Alert.Heading>
                <ExclamationTriangle className="me-2" />
                Notice
              </Alert.Heading>
              {error}
              <div className="mt-2">
                <Button variant="outline-warning" size="sm" onClick={handleRefresh}>
                  Try Again
                </Button>
              </div>
            </Alert>
          </Col>
        </Row>
      )}

      {/* Navigation Tabs */}
      <Row className="mb-4 px-3">
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Body className="py-1">
              <Tabs
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                className="border-0 teacher-tabs"
                fill
              >
                <Tab eventKey="overview" title={
                  <div className="d-flex align-items-center justify-content-center py-1">
                    <GraphUp className="me-2" />
                    Overview
                  </div>
                } />
                <Tab eventKey="classes" title={
                  <div className="d-flex align-items-center justify-content-center py-1">
                    <People className="me-2" />
                    Classes
                    <Badge bg="primary" className="ms-2" pill>
                      {classes.length}
                    </Badge>
                  </div>
                } />
                <Tab eventKey="assignments" title={
                  <div className="d-flex align-items-center justify-content-center py-1">
                    <Journal className="me-2" />
                    Assignments
                    <Badge bg="warning" className="ms-2" pill>
                      {assignmentStats.pending}
                    </Badge>
                  </div>
                } />
                <Tab eventKey="timetable" title={
                  <div className="d-flex align-items-center justify-content-center py-1">
                    <Calendar className="me-2" />
                    Timetable
                  </div>
                } />
                <Tab eventKey="professional" title={
                  <div className="d-flex align-items-center justify-content-center py-1">
                    <Briefcase className="me-2" />
                    Professional
                    {expiringDocuments.length > 0 && (
                      <Badge bg="danger" className="ms-2" pill>
                        {expiringDocuments.length}
                      </Badge>
                    )}
                  </div>
                } />
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Overview Tab */}
      <TabErrorBoundary>
        {activeTab === 'overview' && (
          <>
            {/* Teacher Stats Cards */}
            <Row className="mb-4 px-3">
              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Total Students</h6>
                        <h2 className="mb-0 text-primary">{formatNumber(stats.totalStudents)}</h2>
                        <small className="text-muted">Across {stats.totalClasses} classes</small>
                      </div>
                      <div className="bg-primary bg-opacity-10 p-3 rounded">
                        <People size={24} className="text-primary" />
                      </div>
                    </div>
                    <div className="mt-3">
                      <Link to="/teacher/students" className="text-decoration-none">
                        View Students <ChevronRight size={14} />
                      </Link>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Pending Grading</h6>
                        <h2 className="mb-0 text-warning">{stats.pendingGrading}</h2>
                        <small className="text-muted">{stats.overdueAssignments} overdue</small>
                      </div>
                      <div className="bg-warning bg-opacity-10 p-3 rounded">
                        <FileEarmarkText size={24} className="text-warning" />
                      </div>
                    </div>
                    {stats.pendingGrading > 0 && (
                      <Button 
                        variant="warning" 
                        size="sm" 
                        className="mt-3 w-100"
                        onClick={() => {
                          handleNavigate('/teacher/assignments');
                          setActiveTab('assignments');
                        }}
                      >
                        <FileEarmarkCheck className="me-1" />
                        Grade Now
                      </Button>
                    )}
                  </Card.Body>
                </Card>
              </Col>

              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Leave Balance</h6>
                        <h2 className="mb-0 text-info">{stats.leavesRemaining}</h2>
                        <small className="text-muted">{stats.leavesUsed} days used</small>
                      </div>
                      <div className="bg-info bg-opacity-10 p-3 rounded">
                        <Calendar size={24} className="text-info" />
                      </div>
                    </div>
                    <div className="mt-3">
                      <Button 
                        variant="outline-info" 
                        size="sm" 
                        className="w-100"
                        onClick={() => setShowLeaveModal(true)}
                      >
                        Apply for Leave
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Average Grade</h6>
                        <h2 className="mb-0 text-success">{stats.averageGrade}%</h2>
                        <small className="text-muted">Class average</small>
                      </div>
                      <div className="bg-success bg-opacity-10 p-3 rounded">
                        <Award size={24} className="text-success" />
                      </div>
                    </div>
                    <div className="mt-3">
                      <Link to="/teacher/grades" className="text-decoration-none">
                        View Grades <ChevronRight size={14} />
                      </Link>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>

            {/* Today's Schedule & Pending Actions */}
            <Row className="px-3">
              <Col lg={6} className="mb-4">
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0 py-3 d-flex justify-content-between align-items-center">
                    <h5 className="mb-0 d-flex align-items-center">
                      <Calendar className="me-2 text-primary" />
                      Today's Schedule
                    </h5>
                    <Link to="/teacher/timetable" className="text-decoration-none small">
                      View Full Schedule
                    </Link>
                  </Card.Header>
                  <Card.Body className="p-0">
                    {upcomingClasses.length > 0 ? (
                      <ListGroup variant="flush">
                        {upcomingClasses.map((classItem, index) => (
                          <ListGroup.Item 
                            key={classItem.id || index}
                            className="py-3 border-start-0 border-end-0"
                            action
                            onClick={() => handleNavigate(`/teacher/classes/${classItem.class_id || index}`)}
                          >
                            <div className="d-flex justify-content-between align-items-center">
                              <div>
                                <div className="d-flex align-items-center mb-1">
                                  <Badge bg="primary" className="me-2">
                                    {formatTime(classItem.start_time)}
                                  </Badge>
                                  <h6 className="mb-0">{classItem.subject_name || classItem.subject || 'No Subject'}</h6>
                                </div>
                                <small className="text-muted">
                                  {classItem.class_name || classItem.class || 'No Class'} • {classItem.room || 'TBA'}
                                </small>
                              </div>
                              <ChevronRight size={16} className="text-muted" />
                            </div>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    ) : (
                      <div className="text-center py-5">
                        <Calendar size={48} className="text-muted mb-3 opacity-50" />
                        <p className="text-muted mb-2">No classes scheduled for today</p>
                        <Button 
                          variant="outline-primary" 
                          size="sm"
                          onClick={() => {
                            handleNavigate('/teacher/timetable');
                            setActiveTab('timetable');
                          }}
                        >
                          View Weekly Schedule
                        </Button>
                      </div>
                    )}
                  </Card.Body>
                </Card>
              </Col>

              <Col lg={6} className="mb-4">
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0 py-3 d-flex justify-content-between align-items-center">
                    <h5 className="mb-0 d-flex align-items-center">
                      <Journal className="me-2 text-warning" />
                      Pending Grading
                    </h5>
                    <Link to="/teacher/assignments" className="text-decoration-none small">
                      View All
                    </Link>
                  </Card.Header>
                  <Card.Body className="p-0">
                    {pendingGrading.length > 0 ? (
                      <ListGroup variant="flush">
                        {pendingGrading.map((assignment) => (
                          <ListGroup.Item 
                            key={assignment.id}
                            className="py-3 border-start-0 border-end-0"
                          >
                            <div className="d-flex justify-content-between align-items-start">
                              <div className="flex-grow-1">
                                <div className="d-flex justify-content-between align-items-start mb-1">
                                  <h6 className="mb-0">
                                    <Link 
                                      to={`/teacher/assignments/${assignment.id}`}
                                      className="text-decoration-none"
                                    >
                                      {assignment.title || 'Untitled Assignment'}
                                    </Link>
                                  </h6>
                                  <Badge bg={getAssignmentStatusVariant(assignment.status)}>
                                    {assignment.submissionsCount || 0} subs
                                  </Badge>
                                </div>
                                <div className="d-flex text-muted small">
                                  <span className="me-3">
                                    {assignment.subject || 'No Subject'}
                                  </span>
                                  <span>
                                    Due: {formatDate(assignment.dueDate)}
                                  </span>
                                </div>
                              </div>
                            </div>
                            <div className="mt-2">
                              <Button 
                                variant="outline-warning" 
                                size="sm"
                                onClick={() => handleNavigate(`/teacher/assignments/${assignment.id}/grade`)}
                              >
                                <FileEarmarkCheck className="me-1" />
                                Grade Now
                              </Button>
                            </div>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    ) : (
                      <div className="text-center py-5">
                        <Journal size={48} className="text-muted mb-3 opacity-50" />
                        <p className="text-muted mb-2">No pending assignments to grade</p>
                        <Button 
                          variant="outline-primary" 
                          size="sm"
                          onClick={() => handleNavigate('/teacher/assignments/create')}
                        >
                          Create Assignment
                        </Button>
                      </div>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            </Row>

            {/* Recent Grades & Quick Actions */}
            <Row className="px-3">
              <Col lg={6} className="mb-4">
                <Card className="border-0 shadow-sm">
                  <Card.Header className="bg-white border-0 py-3">
                    <h5 className="mb-0 d-flex align-items-center">
                      <Award className="me-2 text-success" />
                      Recent Grades
                    </h5>
                  </Card.Header>
                  <Card.Body className="p-0">
                    {recentGrades.length > 0 ? (
                      <Table responsive className="mb-0" hover>
                        <thead className="bg-light">
                          <tr>
                            <th>Student</th>
                            <th>Subject</th>
                            <th>Score</th>
                            <th>Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {recentGrades.map((grade, index) => (
                            <tr key={index}>
                              <td>
                                <div className="d-flex align-items-center">
                                  <div className="bg-light rounded-circle d-flex align-items-center justify-content-center me-2"
                                       style={{ width: 32, height: 32 }}>
                                    <Person size={14} />
                                  </div>
                                  {grade.student_name || grade.student?.name || 'Student'}
                                </div>
                              </td>
                              <td>{grade.subject_name || grade.subject || 'No Subject'}</td>
                              <td>
                                <Badge bg={
                                  (grade.score || 0) >= 80 ? 'success' :
                                  (grade.score || 0) >= 60 ? 'warning' : 'danger'
                                }>
                                  {grade.score || 0}%
                                </Badge>
                              </td>
                              <td>{formatDate(grade.date || grade.graded_at)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    ) : (
                      <div className="text-center py-4">
                        <Award size={40} className="text-muted mb-2 opacity-50" />
                        <p className="text-muted mb-0">No grades entered yet</p>
                      </div>
                    )}
                  </Card.Body>
                  {recentGrades.length > 0 && (
                    <Card.Footer className="bg-white border-0 py-2 text-end">
                      <Link to="/teacher/grades" className="text-decoration-none small">
                        View All Grades
                      </Link>
                    </Card.Footer>
                  )}
                </Card>
              </Col>

              <Col lg={6} className="mb-4">
                <Card className="border-0 shadow-sm">
                  <Card.Header className="bg-white border-0 py-3">
                    <h5 className="mb-0 d-flex align-items-center">
                      <ClockHistory className="me-2 text-primary" />
                      Quick Actions
                    </h5>
                  </Card.Header>
                  <Card.Body>
                    <Row>
                      <Col md={6} className="mb-3">
                        <Button 
                          variant="outline-primary" 
                          className="w-100 h-100 py-3 d-flex flex-column align-items-center justify-content-center"
                          onClick={() => handleNavigate('/teacher/attendance')}
                        >
                          <CheckCircle size={24} className="mb-2" />
                          <div className="fw-bold">Take Attendance</div>
                          <small className="text-muted">Mark today</small>
                        </Button>
                      </Col>
                      <Col md={6} className="mb-3">
                        <Button 
                          variant="outline-success" 
                          className="w-100 h-100 py-3 d-flex flex-column align-items-center justify-content-center"
                          onClick={() => handleNavigate('/teacher/assignments/create')}
                        >
                          <Journal size={24} className="mb-2" />
                          <div className="fw-bold">Create Assignment</div>
                          <small className="text-muted">New task</small>
                        </Button>
                      </Col>
                      <Col md={6} className="mb-3">
                        <Button 
                          variant="outline-warning" 
                          className="w-100 h-100 py-3 d-flex flex-column align-items-center justify-content-center"
                          onClick={() => handleNavigate('/teacher/grades/enter')}
                        >
                          <Award size={24} className="mb-2" />
                          <div className="fw-bold">Enter Grades</div>
                          <small className="text-muted">Update marks</small>
                        </Button>
                      </Col>
                      <Col md={6} className="mb-3">
                        <Button 
                          variant="outline-info" 
                          className="w-100 h-100 py-3 d-flex flex-column align-items-center justify-content-center"
                          onClick={() => setShowUploadModal(true)}
                        >
                          <Upload size={24} className="mb-2" />
                          <div className="fw-bold">Upload Document</div>
                          <small className="text-muted">Professional</small>
                        </Button>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </>
        )}
      </TabErrorBoundary>

      {/* Classes Tab */}
      <TabErrorBoundary>
        {activeTab === 'classes' && (
          <Row className="px-3">
            <Col>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3 d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">My Classes</h5>
                  <div className="d-flex gap-2">
                    <Button 
                      variant="outline-primary" 
                      size="sm"
                      onClick={() => handleNavigate('/teacher/classes')}
                    >
                      Manage Classes
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body>
                  {classes.length > 0 ? (
                    <Row>
                      {classes.map((classItem) => (
                        <Col lg={4} md={6} className="mb-3" key={classItem.id}>
                          <Card className="h-100 border hover-lift">
                            <Card.Body>
                              <div className="d-flex justify-content-between align-items-start mb-3">
                                <div>
                                  <Badge bg="primary" className="mb-2">
                                    Grade {classItem.gradeLevel || 'N/A'}
                                  </Badge>
                                  <h6 className="card-title mb-1">{classItem.name}</h6>
                                  <p className="text-muted mb-0">{classItem.subject}</p>
                                </div>
                                <Badge bg="light" text="dark">
                                  {classItem.section}
                                </Badge>
                              </div>
                              <div className="d-flex justify-content-between text-muted small mb-4">
                                <span className="d-flex align-items-center">
                                  <People size={14} className="me-1" />
                                  {classItem.studentCount} Students
                                </span>
                                <span className="d-flex align-items-center">
                                  <Book size={14} className="me-1" />
                                  {classItem.subjectCode || 'All'}
                                </span>
                              </div>
                              <div className="d-grid gap-2">
                                <Button 
                                  variant="primary" 
                                  size="sm"
                                  onClick={() => handleNavigate(`/teacher/classes/${classItem.id}`)}
                                >
                                  View Class Details
                                </Button>
                                <div className="d-flex gap-1">
                                  <Button 
                                    variant="outline-success" 
                                    size="sm"
                                    className="flex-fill"
                                    onClick={() => handleNavigate(`/teacher/attendance?class=${classItem.id}`)}
                                  >
                                    Attendance
                                  </Button>
                                  <Button 
                                    variant="outline-warning" 
                                    size="sm"
                                    className="flex-fill"
                                    onClick={() => handleNavigate(`/teacher/grades?class=${classItem.id}`)}
                                  >
                                    Grades
                                  </Button>
                                </div>
                              </div>
                            </Card.Body>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  ) : (
                    <div className="text-center py-5">
                      <People size={48} className="text-muted mb-3 opacity-50" />
                      <h5 className="text-muted mb-2">No classes assigned</h5>
                      <p className="text-muted mb-4">You haven't been assigned to any classes yet.</p>
                      <Button 
                        variant="primary"
                        onClick={() => handleNavigate('/teacher/classes')}
                      >
                        Request Classes
                      </Button>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}
      </TabErrorBoundary>

      {/* Assignments Tab */}
      <TabErrorBoundary>
        {activeTab === 'assignments' && (
          <Row className="px-3">
            <Col>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">All Assignments</h5>
                    <div className="d-flex gap-2 align-items-center">
                      <div className="input-group input-group-sm" style={{ width: '250px' }}>
                        <span className="input-group-text bg-white">
                          <Search size={14} />
                        </span>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="Search assignments..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                        />
                      </div>
                      <Dropdown>
                        <Dropdown.Toggle variant="outline-secondary" size="sm">
                          <Filter className="me-1" size={14} />
                          Filter
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Item 
                            active={assignmentFilter === 'all'}
                            onClick={() => setAssignmentFilter('all')}
                          >
                            All
                          </Dropdown.Item>
                          <Dropdown.Item 
                            active={assignmentFilter === 'submitted'}
                            onClick={() => setAssignmentFilter('submitted')}
                          >
                            Pending
                          </Dropdown.Item>
                          <Dropdown.Item 
                            active={assignmentFilter === 'graded'}
                            onClick={() => setAssignmentFilter('graded')}
                          >
                            Graded
                          </Dropdown.Item>
                          <Dropdown.Item 
                            active={assignmentFilter === 'overdue'}
                            onClick={() => setAssignmentFilter('overdue')}
                          >
                            Overdue
                          </Dropdown.Item>
                          <Dropdown.Item 
                            active={assignmentFilter === 'draft'}
                            onClick={() => setAssignmentFilter('draft')}
                          >
                            Draft
                          </Dropdown.Item>
                        </Dropdown.Menu>
                      </Dropdown>
                      <Button 
                        variant="primary" 
                        size="sm"
                        onClick={() => handleNavigate('/teacher/assignments/create')}
                      >
                        <Plus className="me-1" size={16} />
                        New Assignment
                      </Button>
                    </div>
                  </div>
                </Card.Header>
                <Card.Body className="p-0">
                  {filteredAssignments.length > 0 ? (
                    <div className="table-responsive">
                      <Table hover className="mb-0">
                        <thead className="bg-light">
                          <tr>
                            <th>Assignment</th>
                            <th>Subject</th>
                            <th>Class</th>
                            <th>Due Date</th>
                            <th>Status</th>
                            <th>Submissions</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredAssignments.slice(0, 15).map((assignment) => (
                            <tr key={assignment.id}>
                              <td>
                                <div>
                                  <Link 
                                    to={`/teacher/assignments/${assignment.id}`}
                                    className="text-decoration-none fw-semibold"
                                  >
                                    {assignment.title}
                                  </Link>
                                  <div className="text-muted small mt-1">
                                    {assignment.description?.substring(0, 50) || 'No description'}...
                                  </div>
                                </div>
                              </td>
                              <td>{assignment.subject}</td>
                              <td>
                                <Badge bg="light" text="dark">
                                  {assignment.className}
                                </Badge>
                              </td>
                              <td>
                                <div className="d-flex flex-column">
                                  <Badge bg={new Date(assignment.dueDate || Date.now()) < new Date() ? 'danger' : 'primary'}>
                                    {formatDate(assignment.dueDate)}
                                  </Badge>
                                  <small className="text-muted">
                                    {formatTime(assignment.dueTime)}
                                  </small>
                                </div>
                              </td>
                              <td>
                                <Badge bg={getAssignmentStatusVariant(assignment.status)}>
                                  {assignment.status?.replace('_', ' ') || 'Active'}
                                </Badge>
                              </td>
                              <td>
                                <div className="d-flex align-items-center">
                                  <span className={(assignment.submissionsCount || 0) > 0 ? 'fw-bold text-success' : 'text-muted'}>
                                    {assignment.submissionsCount || 0}
                                  </span>
                                  <span className="text-muted small ms-1">
                                    / {assignment.totalStudents || '?'}
                                  </span>
                                </div>
                              </td>
                              <td>
                                <div className="d-flex gap-1">
                                  <Button 
                                    variant="outline-primary" 
                                    size="sm"
                                    onClick={() => handleNavigate(`/teacher/assignments/${assignment.id}`)}
                                    title="View"
                                  >
                                    <Eye size={12} />
                                  </Button>
                                  {assignment.status === 'submitted' && (
                                    <Button 
                                      variant="warning" 
                                      size="sm"
                                      onClick={() => handleNavigate(`/teacher/assignments/${assignment.id}/grade`)}
                                      title="Grade"
                                    >
                                      <FileEarmarkCheck size={12} />
                                    </Button>
                                  )}
                                  <Button 
                                    variant="outline-info" 
                                    size="sm"
                                    onClick={() => handleNavigate(`/teacher/assignments/${assignment.id}/submissions`)}
                                    title="Submissions"
                                  >
                                    <FileText size={12} />
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
                      <Journal size={48} className="text-muted mb-3 opacity-50" />
                      <h5 className="text-muted mb-2">No assignments found</h5>
                      <p className="text-muted mb-4">
                        {searchQuery || assignmentFilter !== 'all' 
                          ? 'Try changing your search or filter criteria.' 
                          : 'Create your first assignment to get started.'}
                      </p>
                      <Button 
                        variant="primary"
                        onClick={() => handleNavigate('/teacher/assignments/create')}
                      >
                        <Plus className="me-1" />
                        Create Your First Assignment
                      </Button>
                    </div>
                  )}
                </Card.Body>
                {filteredAssignments.length > 15 && (
                  <Card.Footer className="bg-white border-0 py-3 text-center">
                    <Link to="/teacher/assignments" className="text-decoration-none">
                      View All Assignments ({filteredAssignments.length})
                    </Link>
                  </Card.Footer>
                )}
              </Card>
            </Col>
          </Row>
        )}
      </TabErrorBoundary>

      {/* Timetable Tab */}
      <TabErrorBoundary>
        {activeTab === 'timetable' && (
          <Row className="px-3">
            <Col>
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">Weekly Schedule</h5>
                    <div className="d-flex gap-2">
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        onClick={() => handleNavigate('/teacher/timetable/print')}
                      >
                        <FileText className="me-1" />
                        Print
                      </Button>
                      <Button 
                        variant="primary" 
                        size="sm"
                        onClick={() => handleNavigate('/teacher/timetable/edit')}
                      >
                        Edit Schedule
                      </Button>
                    </div>
                  </div>
                </Card.Header>
                <Card.Body>
                  {timetable.length > 0 ? (
                    <div className="table-responsive">
                      <Table striped hover>
                        <thead>
                          <tr>
                            <th>Day</th>
                            <th>Time</th>
                            <th>Subject</th>
                            <th>Class</th>
                            <th>Room</th>
                            <th>Type</th>
                          </tr>
                        </thead>
                        <tbody>
                          {timetable.slice(0, 20).map((event, index) => {
                            const eventDate = new Date(event.date || event.start_time || Date.now());
                            const dayName = eventDate.toLocaleDateString('en-KE', { weekday: 'long' });
                            const isToday = eventDate.toDateString() === new Date().toDateString();
                            
                            return (
                              <tr key={event.id || index} className={isToday ? 'table-primary' : ''}>
                                <td>
                                  <div className="d-flex align-items-center">
                                    {isToday && <Badge bg="primary" className="me-2">Today</Badge>}
                                    {dayName}
                                  </div>
                                </td>
                                <td>
                                  <div className="fw-semibold">
                                    {formatTime(event.start_time)} - {formatTime(event.end_time)}
                                  </div>
                                  <small className="text-muted">
                                    {formatDate(event.date)}
                                  </small>
                                </td>
                                <td className="fw-semibold">{event.subject_name || event.subject || 'No Subject'}</td>
                                <td>{event.class_name || event.class || 'No Class'}</td>
                                <td>
                                  <Badge bg="secondary">{event.room || 'TBA'}</Badge>
                                </td>
                                <td>
                                  <Badge bg={
                                    event.type === 'lecture' ? 'primary' :
                                    event.type === 'lab' ? 'success' :
                                    event.type === 'tutorial' ? 'info' : 'secondary'
                                  }>
                                    {event.type || 'Class'}
                                  </Badge>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </Table>
                    </div>
                  ) : (
                    <div className="text-center py-5">
                      <Calendar size={48} className="text-muted mb-3 opacity-50" />
                      <h5 className="text-muted mb-2">No schedule available</h5>
                      <p className="text-muted mb-4">Your timetable hasn't been set up yet.</p>
                      <Button 
                        variant="primary"
                        onClick={() => handleNavigate('/teacher/timetable/edit')}
                      >
                        Set Up Timetable
                      </Button>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}
      </TabErrorBoundary>

      {/* Professional Tab */}
      <TabErrorBoundary>
        {activeTab === 'professional' && (
          <>
            {/* Professional Summary Cards */}
            <Row className="mb-4 px-3">
              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Documents</h6>
                        <h2 className="mb-0 text-primary">{teacherDocuments.length}</h2>
                        <small className="text-muted">
                          {expiringDocuments.length} expiring soon
                        </small>
                      </div>
                      <div className="bg-primary bg-opacity-10 p-3 rounded">
                        <FileEarmark size={24} className="text-primary" />
                      </div>
                    </div>
                    <div className="mt-3">
                      <Button 
                        variant="outline-primary" 
                        size="sm" 
                        className="w-100"
                        onClick={() => setShowUploadModal(true)}
                      >
                        <Upload className="me-1" />
                        Upload New
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Qualifications</h6>
                        <h2 className="mb-0 text-success">{teacherQualifications.length}</h2>
                        <small className="text-muted">Academic credentials</small>
                      </div>
                      <div className="bg-success bg-opacity-10 p-3 rounded">
                        <Award size={24} className="text-success" />
                      </div>
                    </div>
                    <div className="mt-3">
                      <Link to="/teacher/qualifications" className="text-decoration-none">
                        View All <ChevronRight size={14} />
                      </Link>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Trainings</h6>
                        <h2 className="mb-0 text-info">{teacherTrainings.length}</h2>
                        <small className="text-muted">Professional development</small>
                      </div>
                      <div className="bg-info bg-opacity-10 p-3 rounded">
                        <CardChecklist size={24} className="text-info" />
                      </div>
                    </div>
                    <div className="mt-3">
                      <Link to="/teacher/trainings" className="text-decoration-none">
                        View Trainings <ChevronRight size={14} />
                      </Link>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              <Col xl={3} lg={6} className="mb-3">
                <Card className="h-100 border-0 shadow-sm hover-lift">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title text-uppercase text-muted mb-2">Leave Requests</h6>
                        <h2 className="mb-0 text-warning">{pendingLeaves.length}</h2>
                        <small className="text-muted">Pending approval</small>
                      </div>
                      <div className="bg-warning bg-opacity-10 p-3 rounded">
                        <Calendar size={24} className="text-warning" />
                      </div>
                    </div>
                    <div className="mt-3">
                      <Button 
                        variant="outline-warning" 
                        size="sm" 
                        className="w-100"
                        onClick={() => setShowLeaveModal(true)}
                      >
                        Apply for Leave
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>

            {/* Documents Section */}
            <Row className="px-3 mb-4">
              <Col>
                <Card className="border-0 shadow-sm">
                  <Card.Header className="bg-white border-0 py-3 d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">My Documents</h5>
                    <div className="d-flex gap-2">
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        onClick={() => setShowUploadModal(true)}
                      >
                        <Upload className="me-1" />
                        Upload Document
                      </Button>
                      <Button 
                        variant="primary" 
                        size="sm"
                        onClick={() => handleNavigate('/teacher/documents')}
                      >
                        View All
                      </Button>
                    </div>
                  </Card.Header>
                  <Card.Body>
                    {teacherDocuments.length > 0 ? (
                      <div className="table-responsive">
                        <Table hover>
                          <thead>
                            <tr>
                              <th>Document</th>
                              <th>Type</th>
                              <th>Status</th>
                              <th>Expiry Date</th>
                              <th>Uploaded</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {teacherDocuments.slice(0, 10).map((doc) => (
                              <tr key={doc.id}>
                                <td className="fw-semibold">
                                  <div className="d-flex align-items-center">
                                    <FileEarmark className="me-2 text-primary" />
                                    {doc.title || doc.document_type}
                                  </div>
                                  {doc.description && (
                                    <small className="text-muted d-block mt-1">
                                      {doc.description.substring(0, 60)}...
                                    </small>
                                  )}
                                </td>
                                <td>
                                  <Badge bg="secondary" className="text-capitalize">
                                    {doc.document_type || 'Document'}
                                  </Badge>
                                </td>
                                <td>
                                  <Badge bg={getDocumentStatusVariant(doc.status)}>
                                    {doc.status || 'Pending'}
                                  </Badge>
                                </td>
                                <td>
                                  {doc.expiry_date ? (
                                    <div className={`${new Date(doc.expiry_date) < new Date() ? 'text-danger' : ''}`}>
                                      {formatDate(doc.expiry_date)}
                                    </div>
                                  ) : 'N/A'}
                                </td>
                                <td>
                                  <small className="text-muted">
                                    {formatDate(doc.uploaded_at || doc.created_at)}
                                  </small>
                                </td>
                                <td>
                                  <div className="d-flex gap-1">
                                    {doc.file_url && (
                                      <Button 
                                        variant="outline-primary" 
                                        size="sm"
                                        onClick={() => window.open(doc.file_url, '_blank')}
                                      >
                                        <Eye size={12} />
                                      </Button>
                                    )}
                                    {doc.status !== 'verified' && (
                                      <Button 
                                        variant="outline-warning" 
                                        size="sm"
                                        onClick={() => handleNavigate(`/teacher/documents/${doc.id}/edit`)}
                                      >
                                        <Pencil size={12} />
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
                        <FileEarmark size={48} className="text-muted mb-3 opacity-50" />
                        <h5 className="text-muted mb-2">No documents uploaded</h5>
                        <p className="text-muted mb-4">Upload your professional documents to get started.</p>
                        <Button 
                          variant="primary"
                          onClick={() => setShowUploadModal(true)}
                        >
                          <Upload className="me-1" />
                          Upload Your First Document
                        </Button>
                      </div>
                    )}
                  </Card.Body>
                </Card>
              </Col>
            </Row>

            {/* Qualifications & Trainings */}
            <Row className="px-3">
              <Col lg={6} className="mb-4">
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0 py-3">
                    <h5 className="mb-0">Qualifications</h5>
                  </Card.Header>
                  <Card.Body>
                    {teacherQualifications.length > 0 ? (
                      <ListGroup variant="flush">
                        {teacherQualifications.slice(0, 5).map((qual) => (
                          <ListGroup.Item key={qual.id} className="border-0 py-2">
                            <div className="d-flex justify-content-between align-items-start">
                              <div>
                                <h6 className="mb-1">{qual.qualification_name || 'Qualification'}</h6>
                                <small className="text-muted">
                                  {qual.institution} • {formatDate(qual.year_awarded)}
                                </small>
                              </div>
                              <Badge bg={qual.verified ? 'success' : 'warning'}>
                                {qual.verified ? 'Verified' : 'Pending'}
                              </Badge>
                            </div>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    ) : (
                      <div className="text-center py-4">
                        <Award size={40} className="text-muted mb-2 opacity-50" />
                        <p className="text-muted mb-0">No qualifications added</p>
                      </div>
                    )}
                  </Card.Body>
                  <Card.Footer className="bg-white border-0 py-2">
                    <Link to="/teacher/qualifications" className="text-decoration-none">
                      View All Qualifications
                    </Link>
                  </Card.Footer>
                </Card>
              </Col>

              <Col lg={6} className="mb-4">
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0 py-3">
                    <h5 className="mb-0">Upcoming Trainings</h5>
                  </Card.Header>
                  <Card.Body>
                    {teacherTrainings.length > 0 ? (
                      <ListGroup variant="flush">
                        {teacherTrainings.slice(0, 5).map((training) => (
                          <ListGroup.Item key={training.id} className="border-0 py-2">
                            <div className="d-flex justify-content-between align-items-start">
                              <div>
                                <h6 className="mb-1">{training.training_name || 'Training'}</h6>
                                <small className="text-muted">
                                  {formatDate(training.start_date)} - {formatDate(training.end_date)}
                                </small>
                              </div>
                              <Badge bg={training.completed ? 'success' : 'primary'}>
                                {training.completed ? 'Completed' : 'Upcoming'}
                              </Badge>
                            </div>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    ) : (
                      <div className="text-center py-4">
                        <CardChecklist size={40} className="text-muted mb-2 opacity-50" />
                        <p className="text-muted mb-0">No upcoming trainings</p>
                      </div>
                    )}
                  </Card.Body>
                  <Card.Footer className="bg-white border-0 py-2">
                    <Link to="/teacher/trainings" className="text-decoration-none">
                      View All Trainings
                    </Link>
                  </Card.Footer>
                </Card>
              </Col>
            </Row>
          </>
        )}
      </TabErrorBoundary>

      {/* Modals */}
      <LeaveApplicationModal
        show={showLeaveModal}
        onHide={() => setShowLeaveModal(false)}
        onSubmit={handleApplyForLeave}
      />

      <UploadDocumentModal
        show={showUploadModal}
        onHide={() => setShowUploadModal(false)}
        onSubmit={handleUploadDocument}
      />

      {/* Footer */}
      <Row className="mt-4 px-3">
        <Col>
          <Card className="border-0 bg-light">
            <Card.Body className="py-3">
              <div className="d-flex justify-content-between align-items-center flex-wrap">
                <div className="mb-2 mb-md-0">
                  <small className="text-muted d-flex align-items-center">
                    <Clock size={12} className="me-1" />
                    Data loaded: {new Date().toLocaleString()}
                    {refreshing && <span className="ms-2">🔄 Refreshing data...</span>}
                  </small>
                </div>
                <div className="d-flex flex-wrap gap-3">
                  <small className="text-muted">
                    <People className="me-1" size={12} />
                    {stats.totalStudents} students
                  </small>
                  <small className="text-muted">
                    <Book className="me-1" size={12} />
                    {stats.totalSubjects} subjects
                  </small>
                  <small className="text-muted">
                    <Journal className="me-1" size={12} />
                    {stats.totalClasses} classes
                  </small>
                  <small className="text-muted">
                    <FileEarmarkCheck className="me-1" size={12} />
                    {stats.pendingGrading} pending
                  </small>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Custom CSS */}
      <style jsx>{`
        .teacher-portal {
          min-height: 100vh;
        }
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
        .hover-lift {
          transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .hover-lift:hover {
          transform: translateY(-2px);
          box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
        }
        .teacher-tabs .nav-link {
          color: #6c757d;
          font-weight: 500;
          border: none;
          padding: 0.75rem 1rem;
        }
        .teacher-tabs .nav-link.active {
          color: #007bff;
          background-color: transparent;
          border-bottom: 3px solid #007bff;
        }
        .teacher-tabs .nav-link:hover {
          color: #0056b3;
        }
        .skeleton-container {
          width: 100%;
        }
        .skeleton-container .card {
          background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
          background-size: 200% 100%;
          animation: loading 1.5s infinite;
        }
        @keyframes loading {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </Container>
  );
};

export default TeacherPortal;