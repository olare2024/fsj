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
  Tabs,
  Tab,
  Modal,
  Form,
  InputGroup,
  Dropdown,
  Accordion,
  ListGroup,
  Image
} from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  // Curriculum Icons
  Book,
  BookFill,
  Journal,
  JournalCode,
  JournalText,
  FileEarmarkText,
  FileEarmarkSpreadsheet,
  FileEarmarkPdf,
  FileEarmarkExcel,
  FileEarmarkWord,
  FileEarmarkPlus,
  FileEarmarkMinus,
  // Organization Icons
  Folder,
  FolderFill,
  // Academic Icons
  ClipboardData,
  ClipboardCheck,
  ClipboardPlus,
  Pen,
  PenFill,
  Pencil,

  // People Icons
  People,
  PeopleFill,
  Person,
  PersonFill,
  PersonBadge,
  PersonCheck,
  PersonPlus,
  PersonDash,
  // Navigation & Actions
  ArrowClockwise,
  ArrowRepeat,
  ArrowCounterclockwise,
  Download,
  Upload,
  Share,
  Printer,
  Search,
  Filter,
  SortDown,
  SortUp,
  SortAlphaDown,
  SortAlphaUp,
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
  QuestionCircle,
  InfoCircle,
  Eye,
  EyeFill,
  EyeSlash,
  EyeSlashFill,
  Lock,
  LockFill,
  Unlock,
  UnlockFill,
  // Time & Calendar
  Calendar,
  CalendarFill,
  CalendarEvent,
  CalendarWeek,
  CalendarMonth,
  CalendarCheck,
  CalendarX,
  Clock,
  ClockHistory,
  Stopwatch,
  // Analytics
  GraphUp,
  GraphDown,
  BarChart,
  BarChartFill,
  PieChart,
  PieChartFill,
  FileEarmarkBarGraph,
  // Miscellaneous
  Gear,
  GearFill,
  Tools,
  Wrench,
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
  // Subject Specific
  Calculator,
  CalculatorFill,
  Palette,
  PaletteFill,
  MusicNote,
  MusicNoteBeamed,
  Globe,
  GlobeAmericas,
  GlobeEuropeAfrica,
  GlobeAsiaAustralia,

  // Languages
  Type,
  TypeBold,
  TypeItalic,
  Translate,
  // Physical Education
  Activity,
  HeartPulse,
  // New icons for curriculum
  Collection,
  CollectionFill,
  CollectionPlay,
  CollectionPlayFill,
  Layers,
  LayersFill,
  Stack,
  FileText,
  FileCheck,
  FileX,
  FilePlus,
  FileEarmark,
  FileEarmarkFill,
  FileEarmarkArrowDownFill,
  FileEarmarkArrowUpFill,
  FileEarmarkCheckFill,
  FileEarmarkPlusFill,
  FileEarmarkMinusFill,
  // Document Icons
  FileRichtext,
  FileEarmarkRichtext,
  FileEarmarkRichtextFill,
  FileEarmarkPpt,
  FileEarmarkPptFill,
  // Archive
  Archive,
  ArchiveFill,
  Box,
  BoxArrowDown,
  BoxArrowUp,
  BoxArrowLeft,
  BoxArrowRight,
  // Communication
  Chat,
  ChatFill,
  ChatLeft,
  ChatLeftFill,
  ChatRight,
  ChatRightFill,
  ChatSquare,
  ChatSquareFill,
  Envelope,
  EnvelopeFill,
  Bell,
  BellFill,
  // Media
  Camera,
  CameraFill,
  CameraVideo,
  CameraVideoFill,
  Image as ImageIcon,
  ImageFill,
  Film,
  // Display
  Display,
  DisplayFill,
  Laptop,
  LaptopFill,
  Tablet,
  TabletFill,
  Phone,
  PhoneFill
} from 'react-bootstrap-icons';

// Import APIs
import authAPI from '../../services/authAPI';
import curriculumAPI from '../../services/curriculumAPI';
import {academicsAPI} from '../../services/academicAPI';
import adminAPI from '../../services/adminAPI';

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
    'draft': 'secondary',
    'review': 'warning',
    'approved': 'success',
    'published': 'primary',
    'archived': 'dark',
    'active': 'success',
    'inactive': 'secondary',
    'pending': 'warning',
    'rejected': 'danger',
    'complete': 'success',
    'in-progress': 'info',
    'overdue': 'danger'
  };
  return variants[status] || 'secondary';
};

const CurriculumPortal = () => {
  const { currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [lastRefreshTime, setLastRefreshTime] = useState(Date.now());
  
  // User profile
  const [userProfile, setUserProfile] = useState(null);
  const [academicYear, setAcademicYear] = useState('');
  const [term, setTerm] = useState('');
  
  // Curriculum data
  const [curriculumOverview, setCurriculumOverview] = useState({
    totalSubjects: 0,
    totalUnits: 0,
    totalLessons: 0,
    totalResources: 0,
    pendingReviews: 0,
    completionRate: 0,
    curriculumVersion: '1.0',
    lastUpdated: null
  });
  
  // Detailed data
  const [subjects, setSubjects] = useState([]);
  const [subjectPlans, setSubjectPlans] = useState([]);
  const [lessonPlans, setLessonPlans] = useState([]);
  const [teachingResources, setTeachingResources] = useState([]);
  const [assessmentTools, setAssessmentTools] = useState([]);
  const [curriculumStandards, setCurriculumStandards] = useState([]);
  const [academicCalendar, setAcademicCalendar] = useState([]);
  const [teacherAssignments, setTeacherAssignments] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [recentUpdates, setRecentUpdates] = useState([]);
  const [resourceLibrary, setResourceLibrary] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  
  // Filter states
  const [filters, setFilters] = useState({
    subject: 'all',
    class: 'all',
    term: 'current',
    status: 'all',
    type: 'all',
    academicYear: 'current'
  });
  
  // Modal states
  const [showResourceModal, setShowResourceModal] = useState(false);
  const [showLessonModal, setShowLessonModal] = useState(false);
  const [showAssessmentModal, setShowAssessmentModal] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Form states
  const [resourceForm, setResourceForm] = useState({
    title: '',
    description: '',
    subject: '',
    class: '',
    type: 'document',
    file: null,
    tags: [],
    accessLevel: 'public',
    sharedWith: []
  });
  
  const [lessonForm, setLessonForm] = useState({
    title: '',
    subject: '',
    class: '',
    term: '',
    week: '',
    duration: '40',
    objectives: [''],
    materials: [''],
    activities: [''],
    assessment: '',
    notes: '',
    attachments: []
  });
  
  const [assessmentForm, setAssessmentForm] = useState({
    title: '',
    subject: '',
    class: '',
    type: 'quiz',
    maxScore: 100,
    duration: '60',
    questions: [],
    rubric: '',
    dueDate: ''
  });
  
  const [importForm, setImportForm] = useState({
    type: 'curriculum',
    format: 'csv',
    file: null,
    overwrite: false,
    academicYear: '',
    term: ''
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

  // Fetch all curriculum data
  const fetchCurriculumData = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError('');

      const [
        profileResult,
        overviewResult,
        subjectsResult,
        subjectPlansResult,
        lessonPlansResult,
        resourcesResult,
        assessmentsResult,
        standardsResult,
        calendarResult,
        assignmentsResult,
        reviewsResult,
        updatesResult,
        libraryResult,
        performanceResult
      ] = await Promise.all([
        authAPI.getCurrentUser(),
        curriculumAPI.getCurriculumOverview(),
        curriculumAPI.getAllSubjects(),
        curriculumAPI.getSubjectPlans({ academic_year: filters.academicYear }),
        curriculumAPI.getLessonPlans({ term: filters.term }),
        curriculumAPI.getTeachingResources({ type: filters.type !== 'all' ? filters.type : undefined }),
        curriculumAPI.getAssessmentTools(),
        curriculumAPI.getCurriculumStandards(),
        academicAPI.getAcademicCalendar(),
        curriculumAPI.getTeacherAssignments(),
        curriculumAPI.getPendingReviews(),
        curriculumAPI.getRecentUpdates(),
        curriculumAPI.getResourceLibrary(),
        curriculumAPI.getPerformanceData()
      ]);

      // Process results
      if (profileResult.success) {
        setUserProfile(profileResult.user || profileResult.data);
      }
      if (overviewResult.success) {
        setCurriculumOverview(overviewResult.data);
        setAcademicYear(overviewResult.data.academic_year || '2024');
        setTerm(overviewResult.data.current_term || 'Term 1');
      }
      if (subjectsResult.success) setSubjects(subjectsResult.data?.subjects || subjectsResult.data || []);
      if (subjectPlansResult.success) setSubjectPlans(subjectPlansResult.data?.plans || subjectPlansResult.data || []);
      if (lessonPlansResult.success) setLessonPlans(lessonPlansResult.data?.lessons || lessonPlansResult.data || []);
      if (resourcesResult.success) setTeachingResources(resourcesResult.data?.resources || resourcesResult.data || []);
      if (assessmentsResult.success) setAssessmentTools(assessmentsResult.data?.assessments || assessmentsResult.data || []);
      if (standardsResult.success) setCurriculumStandards(standardsResult.data?.standards || standardsResult.data || []);
      if (calendarResult.success) setAcademicCalendar(calendarResult.data?.events || calendarResult.data || []);
      if (assignmentsResult.success) setTeacherAssignments(assignmentsResult.data?.assignments || assignmentsResult.data || []);
      if (reviewsResult.success) setPendingReviews(reviewsResult.data?.reviews || reviewsResult.data || []);
      if (updatesResult.success) setRecentUpdates(updatesResult.data?.updates || updatesResult.data || []);
      if (libraryResult.success) setResourceLibrary(libraryResult.data?.resources || libraryResult.data || []);
      if (performanceResult.success) setPerformanceData(performanceResult.data?.performance || performanceResult.data || []);

      setLastRefreshTime(Date.now());

    } catch (err) {
      console.error('Error fetching curriculum data:', err);
      setError('Failed to load curriculum data. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [filters.academicYear, filters.term, filters.type]);

  useEffect(() => {
    if (!authLoading && currentUser) {
      fetchCurriculumData();
    }
  }, [authLoading, currentUser, fetchCurriculumData]);

  // Refresh function
  const handleRefresh = () => {
    fetchCurriculumData(true);
  };

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  // Add new resource
  const handleAddResource = async () => {
    try {
      setLoading(true);
      const formData = new FormData();
      Object.keys(resourceForm).forEach(key => {
        if (key === 'file' && resourceForm.file) {
          formData.append('file', resourceForm.file);
        } else if (key === 'tags' && Array.isArray(resourceForm.tags)) {
          formData.append('tags', resourceForm.tags.join(','));
        } else if (key === 'sharedWith' && Array.isArray(resourceForm.sharedWith)) {
          formData.append('shared_with', resourceForm.sharedWith.join(','));
        } else {
          formData.append(key, resourceForm[key]);
        }
      });

      const result = await curriculumAPI.addTeachingResource(formData);
      
      if (result.success) {
        setSuccess('Teaching resource added successfully!');
        setShowResourceModal(false);
        setResourceForm({
          title: '',
          description: '',
          subject: '',
          class: '',
          type: 'document',
          file: null,
          tags: [],
          accessLevel: 'public',
          sharedWith: []
        });
        fetchCurriculumData();
      } else {
        setError(result.error?.message || 'Failed to add resource');
      }
    } catch (err) {
      setError('Failed to add resource');
    } finally {
      setLoading(false);
    }
  };

  // Create lesson plan
  const handleCreateLessonPlan = async () => {
    try {
      setLoading(true);
      const result = await curriculumAPI.createLessonPlan(lessonForm);
      
      if (result.success) {
        setSuccess('Lesson plan created successfully!');
        setShowLessonModal(false);
        setLessonForm({
          title: '',
          subject: '',
          class: '',
          term: '',
          week: '',
          duration: '40',
          objectives: [''],
          materials: [''],
          activities: [''],
          assessment: '',
          notes: '',
          attachments: []
        });
        fetchCurriculumData();
      } else {
        setError(result.error?.message || 'Failed to create lesson plan');
      }
    } catch (err) {
      setError('Failed to create lesson plan');
    } finally {
      setLoading(false);
    }
  };

  // Create assessment
  const handleCreateAssessment = async () => {
    try {
      setLoading(true);
      const result = await curriculumAPI.createAssessmentTool(assessmentForm);
      
      if (result.success) {
        setSuccess('Assessment created successfully!');
        setShowAssessmentModal(false);
        setAssessmentForm({
          title: '',
          subject: '',
          class: '',
          type: 'quiz',
          maxScore: 100,
          duration: '60',
          questions: [],
          rubric: '',
          dueDate: ''
        });
        fetchCurriculumData();
      } else {
        setError(result.error?.message || 'Failed to create assessment');
      }
    } catch (err) {
      setError('Failed to create assessment');
    } finally {
      setLoading(false);
    }
  };

  // Approve/reject review
  const handleReviewAction = async (reviewId, action, comments = '') => {
    try {
      setLoading(true);
      const result = await curriculumAPI.processReview(reviewId, { action, comments });
      
      if (result.success) {
        setSuccess(`Review ${action}ed successfully!`);
        setPendingReviews(prev => prev.filter(review => review.id !== reviewId));
      } else {
        setError(result.error?.message || `Failed to ${action} review`);
      }
    } catch (err) {
      setError(`Failed to ${action} review`);
    } finally {
      setLoading(false);
    }
  };

  // Import curriculum data
  const handleImportData = async () => {
    try {
      setLoading(true);
      const formData = new FormData();
      Object.keys(importForm).forEach(key => {
        if (key === 'file' && importForm.file) {
          formData.append('file', importForm.file);
        } else {
          formData.append(key, importForm[key]);
        }
      });

      const result = await curriculumAPI.importCurriculumData(formData);
      
      if (result.success) {
        setSuccess('Curriculum data imported successfully!');
        setShowImportModal(false);
        setImportForm({
          type: 'curriculum',
          format: 'csv',
          file: null,
          overwrite: false,
          academicYear: '',
          term: ''
        });
        fetchCurriculumData();
      } else {
        setError(result.error?.message || 'Failed to import data');
      }
    } catch (err) {
      setError('Failed to import data');
    } finally {
      setLoading(false);
    }
  };

  // Export curriculum data
  const handleExportData = async (type = 'curriculum', format = 'pdf') => {
    try {
      setLoading(true);
      const result = await curriculumAPI.exportCurriculumData({
        type,
        format,
        academic_year: filters.academicYear,
        term: filters.term
      });
      
      if (result.success && result.data) {
        // Create download link
        const url = window.URL.createObjectURL(new Blob([result.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${type}_export_${new Date().toISOString().split('T')[0]}.${format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        setSuccess(`${type} exported successfully as ${format.toUpperCase()}`);
      }
    } catch (err) {
      setError('Failed to export data');
    } finally {
      setLoading(false);
    }
  };

  // Share resource
  const handleShareResource = async (resourceId, recipients) => {
    try {
      setLoading(true);
      const result = await curriculumAPI.shareResource(resourceId, { recipients });
      
      if (result.success) {
        setSuccess('Resource shared successfully!');
      } else {
        setError(result.error?.message || 'Failed to share resource');
      }
    } catch (err) {
      setError('Failed to share resource');
    } finally {
      setLoading(false);
    }
  };

  // Update curriculum standard
  const handleUpdateStandard = async (standardId, updates) => {
    try {
      setLoading(true);
      const result = await curriculumAPI.updateStandard(standardId, updates);
      
      if (result.success) {
        setSuccess('Curriculum standard updated successfully!');
        fetchCurriculumData();
      } else {
        setError(result.error?.message || 'Failed to update standard');
      }
    } catch (err) {
      setError('Failed to update standard');
    } finally {
      setLoading(false);
    }
  };

  // Filter data based on search term
  const filteredSubjects = useMemo(() => {
    return subjects.filter(subject => 
      searchTerm === '' || 
      subject.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      subject.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      subject.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [subjects, searchTerm]);

  const filteredResources = useMemo(() => {
    return teachingResources.filter(resource => 
      searchTerm === '' || 
      resource.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      resource.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      resource.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      resource.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [teachingResources, searchTerm]);

  if (authLoading || (loading && !refreshing)) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-3 text-muted">Loading curriculum portal...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Page Header */}
      <Row className="mb-4">
        <Col>
          <Card className="border-0 bg-gradient-purple text-white shadow">
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
                          alt="Curriculum Manager avatar"
                          style={{ objectFit: 'cover' }}
                        />
                      ) : (
                        <div 
                          className="rounded-circle bg-white bg-opacity-20 d-flex align-items-center justify-content-center border border-3 border-white shadow"
                          style={{ width: 80, height: 80 }}
                        >
                          <Book size={32} className="text-white" />
                        </div>
                      )}
                    </div>
                    <div>
                      <h1 className="h2 mb-1">Curriculum Development Portal</h1>
                      <p className="mb-1 opacity-75">
                        Welcome, {userProfile?.first_name || 'Curriculum Manager'}! Manage and develop academic curriculum
                      </p>
                      <small className="opacity-75">
                        Academic Year: {academicYear} • Term: {term} • 
                        Version: {curriculumOverview.curriculumVersion} • 
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
                      className="text-purple"
                    >
                      <ArrowClockwise className={`me-2 ${refreshing ? 'spinning' : ''}`} size={16} />
                      Refresh
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-purple"
                      onClick={() => setShowResourceModal(true)}
                    >
                      <FileEarmarkPlus className="me-2" />
                      Add Resource
                    </Button>
                    <Button 
                      variant="white" 
                      className="text-purple"
                      onClick={() => setShowLessonModal(true)}
                    >
                      <Journal className="me-2" />
                      New Lesson
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
                  <h6 className="card-title text-uppercase text-muted mb-2">Total Subjects</h6>
                  <h2 className="mb-0 text-primary">{formatNumber(curriculumOverview.totalSubjects)}</h2>
                  <small className="text-muted">
                    <Badge bg="success" className="me-1">
                      {subjects.filter(s => s.status === 'active').length} Active
                    </Badge>
                  </small>
                </div>
                <div className="bg-primary bg-opacity-10 p-3 rounded">
                  <Book size={24} className="text-primary" />
                </div>
              </div>
              <Button 
                variant="outline-primary" 
                size="sm" 
                className="mt-2 w-100"
                onClick={() => setActiveTab('subjects')}
              >
                View Subjects
              </Button>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Lesson Plans</h6>
                  <h2 className="mb-0 text-info">{formatNumber(curriculumOverview.totalLessons)}</h2>
                  <small className="text-muted">This term</small>
                </div>
                <div className="bg-info bg-opacity-10 p-3 rounded">
                  <Journal size={24} className="text-info" />
                </div>
              </div>
              <Button 
                variant="outline-info" 
                size="sm" 
                className="mt-2 w-100"
                onClick={() => setActiveTab('lessons')}
              >
                View Lessons
              </Button>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Resources</h6>
                  <h2 className="mb-0 text-success">{formatNumber(curriculumOverview.totalResources)}</h2>
                  <small className="text-muted">Teaching materials</small>
                </div>
                <div className="bg-success bg-opacity-10 p-3 rounded">
                  <Folder size={24} className="text-success" />
                </div>
              </div>
              <Button 
                variant="outline-success" 
                size="sm" 
                className="mt-2 w-100"
                onClick={() => setActiveTab('resources')}
              >
                Browse Resources
              </Button>
            </Card.Body>
          </Card>
        </Col>

        <Col xl={3} lg={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="card-title text-uppercase text-muted mb-2">Pending Reviews</h6>
                  <h2 className="mb-0 text-warning">{curriculumOverview.pendingReviews}</h2>
                  <small className="text-muted">Awaiting approval</small>
                </div>
                <div className="bg-warning bg-opacity-10 p-3 rounded">
                  <ClipboardCheck size={24} className="text-warning" />
                </div>
              </div>
              {curriculumOverview.pendingReviews > 0 && (
                <Button 
                  variant="warning" 
                  size="sm" 
                  className="mt-2 w-100"
                  onClick={() => setActiveTab('reviews')}
                >
                  Review Now
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
                <Tab eventKey="overview" title={
                  <>
                    <BarChart className="me-2" />
                    Overview
                  </>
                } />
                <Tab eventKey="subjects" title={
                  <>
                    <Book className="me-2" />
                    Subjects ({subjects.length})
                  </>
                } />
                <Tab eventKey="lessons" title={
                  <>
                    <Journal className="me-2" />
                    Lesson Plans ({lessonPlans.length})
                  </>
                } />
                <Tab eventKey="resources" title={
                  <>
                    <Folder className="me-2" />
                    Resources ({teachingResources.length})
                  </>
                } />
                <Tab eventKey="assessments" title={
                  <>
                    <ClipboardData className="me-2" />
                    Assessments ({assessmentTools.length})
                  </>
                } />
                <Tab eventKey="standards" title={
                  <>
                    <Award className="me-2" />
                    Standards ({curriculumStandards.length})
                  </>
                } />
                <Tab eventKey="reviews" title={
                  <>
                    <ClipboardCheck className="me-2" />
                    Reviews ({pendingReviews.length})
                    {curriculumOverview.pendingReviews > 0 && (
                      <Badge bg="warning" className="ms-2">{curriculumOverview.pendingReviews}</Badge>
                    )}
                  </>
                } />
                <Tab eventKey="library" title={
                  <>
                    <Collection className="me-2" />
                    Resource Library
                  </>
                } />
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Search and Filters */}
      {activeTab !== 'overview' && activeTab !== 'library' && (
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
                          Subject: {filters.subject === 'all' ? 'All' : filters.subject}
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Item onClick={() => handleFilterChange('subject', 'all')}>
                            All Subjects
                          </Dropdown.Item>
                          <Dropdown.Divider />
                          {subjects.map((subject, index) => (
                            <Dropdown.Item 
                              key={index}
                              onClick={() => handleFilterChange('subject', subject.name)}
                            >
                              {subject.code} - {subject.name}
                            </Dropdown.Item>
                          ))}
                        </Dropdown.Menu>
                      </Dropdown>

                      <Dropdown>
                        <Dropdown.Toggle variant="outline-secondary" size="sm">
                          <Book className="me-2" />
                          Class: {filters.class === 'all' ? 'All' : filters.class}
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Item onClick={() => handleFilterChange('class', 'all')}>
                            All Classes
                          </Dropdown.Item>
                          <Dropdown.Divider />
                          {['Form 1', 'Form 2', 'Form 3', 'Form 4', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4'].map((cls, index) => (
                            <Dropdown.Item 
                              key={index}
                              onClick={() => handleFilterChange('class', cls)}
                            >
                              {cls}
                            </Dropdown.Item>
                          ))}
                        </Dropdown.Menu>
                      </Dropdown>

                      <Dropdown>
                        <Dropdown.Toggle variant="outline-secondary" size="sm">
                          <CalendarEvent className="me-2" />
                          Status: {filters.status === 'all' ? 'All' : filters.status}
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'all')}>
                            All Statuses
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'active')}>
                            Active
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'draft')}>
                            Draft
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'pending')}>
                            Pending
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleFilterChange('status', 'archived')}>
                            Archived
                          </Dropdown.Item>
                        </Dropdown.Menu>
                      </Dropdown>

                      <Button 
                        variant="outline-secondary" 
                        size="sm"
                        onClick={() => {
                          setFilters({
                            subject: 'all',
                            class: 'all',
                            term: 'current',
                            status: 'all',
                            type: 'all',
                            academicYear: 'current'
                          });
                          setSearchTerm('');
                        }}
                      >
                        <ArrowCounterclockwise className="me-2" />
                        Reset
                      </Button>

                      <Dropdown>
                        <Dropdown.Toggle variant="primary" size="sm">
                          <Download className="me-2" />
                          Export
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Header>Export Format</Dropdown.Header>
                          <Dropdown.Item onClick={() => handleExportData(activeTab, 'pdf')}>
                            <FileEarmarkPdf className="me-2" />
                            PDF Document
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleExportData(activeTab, 'excel')}>
                            <FileEarmarkExcel className="me-2" />
                            Excel Spreadsheet
                          </Dropdown.Item>
                          <Dropdown.Item onClick={() => handleExportData(activeTab, 'word')}>
                            <FileEarmarkWord className="me-2" />
                            Word Document
                          </Dropdown.Item>
                          <Dropdown.Divider />
                          <Dropdown.Header>Quick Actions</Dropdown.Header>
                          <Dropdown.Item onClick={() => setShowImportModal(true)}>
                            <Upload className="me-2" />
                            Import Data
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
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
          <Row className="mb-4">
            <Col lg={8} className="mb-4">
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">Curriculum Development Status</h5>
                    <div className="d-flex gap-2">
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        onClick={() => setShowAssessmentModal(true)}
                      >
                        <ClipboardPlus className="me-1" />
                        Create Assessment
                      </Button>
                      <Button 
                        variant="primary" 
                        size="sm"
                        onClick={() => navigate('/curriculum/development')}
                      >
                        <Gear className="me-1" />
                        Development Tools
                      </Button>
                    </div>
                  </div>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <h6 className="text-muted mb-3">Completion Progress</h6>
                      <div className="mb-4">
                        <div className="d-flex justify-content-between mb-1">
                          <small>Curriculum Development</small>
                          <small className="fw-bold">{curriculumOverview.completionRate}%</small>
                        </div>
                        <ProgressBar 
                          now={curriculumOverview.completionRate} 
                          variant="success" 
                          className="mb-3"
                        />
                      </div>
                      
                      <h6 className="text-muted mb-3">Recent Updates</h6>
                      {recentUpdates.length > 0 ? (
                        <ListGroup variant="flush">
                          {recentUpdates.slice(0, 5).map((update, index) => (
                            <ListGroup.Item key={index}>
                              <div className="d-flex justify-content-between align-items-start">
                                <div>
                                  <h6 className="mb-1">{update.title}</h6>
                                  <small className="text-muted">{update.description}</small>
                                </div>
                                <Badge bg={getStatusBadge(update.status)}>
                                  {update.status}
                                </Badge>
                              </div>
                              <small className="text-muted d-block mt-1">
                                By {update.updated_by} • {formatDateTime(update.updated_at)}
                              </small>
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      ) : (
                        <p className="text-muted">No recent updates</p>
                      )}
                    </Col>
                    <Col md={6}>
                      <h6 className="text-muted mb-3">Subject Distribution</h6>
                      <div className="text-center">
                        <PieChart size={80} className="text-primary mb-2" />
                        <div className="d-flex justify-content-around mt-3">
                          <div className="text-center">
                            <div className="fw-bold text-success">Core</div>
                            <small>{subjects.filter(s => s.type === 'core').length} Subjects</small>
                          </div>
                          <div className="text-center">
                            <div className="fw-bold text-info">Elective</div>
                            <small>{subjects.filter(s => s.type === 'elective').length} Subjects</small>
                          </div>
                          <div className="text-center">
                            <div className="fw-bold text-warning">Optional</div>
                            <small>{subjects.filter(s => s.type === 'optional').length} Subjects</small>
                          </div>
                        </div>
                      </div>

                      <h6 className="text-muted mt-4 mb-3">Resource Types</h6>
                      <div className="d-flex flex-wrap gap-2">
                        <Badge bg="primary" className="p-2">
                          Documents ({teachingResources.filter(r => r.type === 'document').length})
                        </Badge>
                        <Badge bg="success" className="p-2">
                          Presentations ({teachingResources.filter(r => r.type === 'presentation').length})
                        </Badge>
                        <Badge bg="info" className="p-2">
                          Videos ({teachingResources.filter(r => r.type === 'video').length})
                        </Badge>
                        <Badge bg="warning" className="p-2">
                          Worksheets ({teachingResources.filter(r => r.type === 'worksheet').length})
                        </Badge>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>

            <Col lg={4} className="mb-4">
              <Card className="border-0 shadow-sm h-100">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">Academic Calendar</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {academicCalendar.length > 0 ? (
                    <ListGroup variant="flush">
                      {academicCalendar.slice(0, 5).map((event, index) => (
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
                            {event.type} • {event.venue}
                          </small>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <CalendarEvent size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No calendar events</p>
                    </div>
                  )}
                </Card.Body>
                <Card.Footer className="bg-white border-0">
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="w-100"
                    onClick={() => navigate('/curriculum/calendar')}
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
                  <h5 className="mb-0">Teacher Assignments</h5>
                </Card.Header>
                <Card.Body className="p-0">
                  {teacherAssignments.length > 0 ? (
                    <ListGroup variant="flush">
                      {teacherAssignments.map((assignment, index) => (
                        <ListGroup.Item key={index}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h6 className="mb-1">{assignment.subject}</h6>
                              <small className="text-muted">
                                {assignment.classes?.join(', ')} • Term {assignment.term}
                              </small>
                            </div>
                            <div>
                              <Badge bg="primary" className="me-2">
                                {assignment.teacher_count || 0} Teachers
                              </Badge>
                              <Badge bg={getStatusBadge(assignment.status)}>
                                {assignment.status}
                              </Badge>
                            </div>
                          </div>
                          <div className="d-flex justify-content-between align-items-center mt-2">
                            <small className="text-muted">
                              Last updated: {formatDate(assignment.updated_at)}
                            </small>
                            <Button 
                              variant="outline-primary" 
                              size="sm"
                              onClick={() => navigate(`/curriculum/assignments/${assignment.id}`)}
                            >
                              View
                            </Button>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <div className="text-center py-5">
                      <PersonBadge size={48} className="text-muted mb-3" />
                      <p className="text-muted mb-0">No teacher assignments</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>

            <Col lg={6} className="mb-4">
              <Card className="border-0 shadow-sm">
                <Card.Header className="bg-white border-0 py-3">
                  <h5 className="mb-0">Quick Actions</h5>
                </Card.Header>
                <Card.Body>
                  <div className="d-grid gap-2">
                    <Button 
                      variant="outline-primary" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => setShowLessonModal(true)}
                    >
                      <Journal className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">Create Lesson Plan</div>
                        <small className="text-muted">New lesson template</small>
                      </div>
                    </Button>
                    <Button 
                      variant="outline-success" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => navigate('/curriculum/standards')}
                    >
                      <Award className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">View Standards</div>
                        <small className="text-muted">Curriculum guidelines</small>
                      </div>
                    </Button>
                    <Button 
                      variant="outline-warning" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => setActiveTab('reviews')}
                    >
                      <ClipboardCheck className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">Review Submissions</div>
                        <small className="text-muted">{curriculumOverview.pendingReviews} pending</small>
                      </div>
                    </Button>
                    <Button 
                      variant="outline-info" 
                      className="text-start py-3 d-flex align-items-center"
                      onClick={() => navigate('/curriculum/reports')}
                    >
                      <FileEarmarkBarGraph className="me-3" size={20} />
                      <div>
                        <div className="fw-bold">Generate Reports</div>
                        <small className="text-muted">Curriculum analysis</small>
                      </div>
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* Subjects Tab */}
      {activeTab === 'subjects' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Subject Management ({subjects.length})</h5>
                  <div>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      className="me-2"
                      onClick={() => navigate('/curriculum/subjects/create')}
                    >
                      <Plus className="me-1" />
                      Add Subject
                    </Button>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => handleExportData('subjects', 'excel')}
                    >
                      <Download className="me-1" />
                      Export Subjects
                    </Button>
                  </div>
                </div>
              </Card.Header>
              <Card.Body className="p-0">
                {filteredSubjects.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover className="mb-0">
                      <thead className="table-light">
                        <tr>
                          <th>Code</th>
                          <th>Subject Name</th>
                          <th>Type</th>
                          <th>Classes</th>
                          <th>Teacher In Charge</th>
                          <th>Units</th>
                          <th>Status</th>
                          <th>Last Updated</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredSubjects.map((subject) => (
                          <tr key={subject.id}>
                            <td className="fw-semibold">{subject.code}</td>
                            <td>
                              <div className="fw-bold">{subject.name}</div>
                              <small className="text-muted">{subject.description}</small>
                            </td>
                            <td>
                              <Badge bg={subject.type === 'core' ? 'primary' : 'info'}>
                                {subject.type?.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <small>{subject.classes?.join(', ') || 'N/A'}</small>
                            </td>
                            <td>{subject.teacher_in_charge || 'Not assigned'}</td>
                            <td>
                              <Badge bg="secondary">{subject.unit_count || 0}</Badge>
                            </td>
                            <td>
                              <Badge bg={getStatusBadge(subject.status)}>
                                {subject.status?.toUpperCase()}
                              </Badge>
                            </td>
                            <td>
                              <small>{formatDate(subject.updated_at)}</small>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/curriculum/subjects/${subject.id}`)}
                                >
                                  <Eye size={12} />
                                </Button>
                                <Button 
                                  variant="outline-success" 
                                  size="sm"
                                  onClick={() => navigate(`/curriculum/subjects/${subject.id}/units`)}
                                >
                                  <Layers size={12} />
                                </Button>
                                <Button 
                                  variant="outline-warning" 
                                  size="sm"
                                  onClick={() => navigate(`/curriculum/subjects/${subject.id}/edit`)}
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
                    <Book size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No subjects found</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Lesson Plans Tab */}
      {activeTab === 'lessons' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Lesson Plans Management ({lessonPlans.length})</h5>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => setShowLessonModal(true)}
                  >
                    <Plus className="me-1" />
                    Create Lesson Plan
                  </Button>
                </div>
              </Card.Header>
              <Card.Body>
                <div className="table-responsive">
                  <Table hover>
                    <thead className="table-light">
                      <tr>
                        <th>Title</th>
                        <th>Subject</th>
                        <th>Class</th>
                        <th>Term/Week</th>
                        <th>Duration</th>
                        <th>Objectives</th>
                        <th>Status</th>
                        <th>Created By</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {lessonPlans.map((lesson) => (
                        <tr key={lesson.id}>
                          <td className="fw-semibold">{lesson.title}</td>
                          <td>{lesson.subject}</td>
                          <td>{lesson.class}</td>
                          <td>
                            <Badge bg="info">
                              Term {lesson.term} • Week {lesson.week}
                            </Badge>
                          </td>
                          <td>{lesson.duration} mins</td>
                          <td>
                            <small className="text-muted">
                              {lesson.objectives?.slice(0, 2).map((obj, i) => (
                                <div key={i}>• {obj}</div>
                              ))}
                              {lesson.objectives?.length > 2 && (
                                <span>... and {lesson.objectives.length - 2} more</span>
                              )}
                            </small>
                          </td>
                          <td>
                            <Badge bg={getStatusBadge(lesson.status)}>
                              {lesson.status?.toUpperCase()}
                            </Badge>
                          </td>
                          <td>{lesson.created_by}</td>
                          <td>
                            <div className="d-flex gap-1">
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => navigate(`/curriculum/lessons/${lesson.id}`)}
                              >
                                View
                              </Button>
                              <Button 
                                variant="outline-success" 
                                size="sm"
                                onClick={() => navigate(`/curriculum/lessons/${lesson.id}/edit`)}
                              >
                                Edit
                              </Button>
                              <Button 
                                variant="outline-info" 
                                size="sm"
                                onClick={() => handleShareResource(lesson.id, ['teachers'])}
                              >
                                Share
                              </Button>
                            </div>
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

      {/* Resources Tab */}
      {activeTab === 'resources' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Teaching Resources ({teachingResources.length})</h5>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => setShowResourceModal(true)}
                  >
                    <Plus className="me-1" />
                    Add Resource
                  </Button>
                </div>
              </Card.Header>
              <Card.Body>
                <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                  {filteredResources.map((resource) => (
                    <Col key={resource.id}>
                      <Card className="h-100">
                        <Card.Body>
                          <div className="d-flex align-items-start mb-3">
                            <div className={`p-2 rounded me-3 ${
                              resource.type === 'document' ? 'bg-primary bg-opacity-10' :
                              resource.type === 'video' ? 'bg-danger bg-opacity-10' :
                              resource.type === 'presentation' ? 'bg-success bg-opacity-10' :
                              'bg-warning bg-opacity-10'
                            }`}>
                              {resource.type === 'document' ? <FileEarmarkText className="text-primary" /> :
                               resource.type === 'video' ? <CameraVideo className="text-danger" /> :
                               resource.type === 'presentation' ? <FileEarmarkPpt className="text-success" /> :
                               <FileEarmarkSpreadsheet className="text-warning" />}
                            </div>
                            <div>
                              <h6 className="card-title mb-1">{resource.title}</h6>
                              <small className="text-muted">{resource.subject} • {resource.class}</small>
                            </div>
                          </div>
                          <p className="card-text small">{resource.description}</p>
                          <div className="d-flex flex-wrap gap-1 mb-3">
                            {resource.tags?.slice(0, 3).map((tag, index) => (
                              <Badge key={index} bg="secondary">{tag}</Badge>
                            ))}
                            {resource.tags?.length > 3 && (
                              <Badge bg="light" text="dark">+{resource.tags.length - 3}</Badge>
                            )}
                          </div>
                          <div className="d-flex justify-content-between align-items-center">
                            <small className="text-muted">
                              {formatDate(resource.created_at)}
                            </small>
                            <div className="d-flex gap-1">
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => window.open(resource.file_url, '_blank')}
                              >
                                <Eye size={12} />
                              </Button>
                              <Button 
                                variant="outline-success" 
                                size="sm"
                                onClick={() => window.open(resource.download_url, '_blank')}
                              >
                                <Download size={12} />
                              </Button>
                            </div>
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>
                  ))}
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Assessments Tab */}
      {activeTab === 'assessments' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Assessment Tools ({assessmentTools.length})</h5>
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => setShowAssessmentModal(true)}
                  >
                    <Plus className="me-1" />
                    Create Assessment
                  </Button>
                </div>
              </Card.Header>
              <Card.Body>
                <Accordion>
                  {assessmentTools.map((assessment, index) => (
                    <Accordion.Item eventKey={index.toString()} key={index}>
                      <Accordion.Header>
                        <div className="d-flex justify-content-between align-items-center w-100">
                          <div>
                            <h6 className="mb-0">{assessment.title}</h6>
                            <small className="text-muted">
                              {assessment.subject} • {assessment.class} • Type: {assessment.type}
                            </small>
                          </div>
                          <Badge bg={getStatusBadge(assessment.status)} className="me-2">
                            {assessment.status}
                          </Badge>
                        </div>
                      </Accordion.Header>
                      <Accordion.Body>
                        <Row>
                          <Col md={6}>
                            <p><strong>Description:</strong> {assessment.description}</p>
                            <p><strong>Max Score:</strong> {assessment.max_score}</p>
                            <p><strong>Duration:</strong> {assessment.duration} minutes</p>
                            <p><strong>Questions:</strong> {assessment.questions?.length || 0}</p>
                          </Col>
                          <Col md={6}>
                            <p><strong>Due Date:</strong> {formatDate(assessment.due_date)}</p>
                            <p><strong>Created By:</strong> {assessment.created_by}</p>
                            <p><strong>Usage Count:</strong> {assessment.usage_count || 0}</p>
                            <div className="d-flex gap-2 mt-3">
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => navigate(`/curriculum/assessments/${assessment.id}`)}
                              >
                                View Details
                              </Button>
                              <Button 
                                variant="outline-success" 
                                size="sm"
                                onClick={() => navigate(`/curriculum/assessments/${assessment.id}/preview`)}
                              >
                                Preview
                              </Button>
                              <Button 
                                variant="outline-info" 
                                size="sm"
                                onClick={() => handleShareResource(assessment.id, ['teachers'])}
                              >
                                Share
                              </Button>
                            </div>
                          </Col>
                        </Row>
                      </Accordion.Body>
                    </Accordion.Item>
                  ))}
                </Accordion>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Standards Tab */}
      {activeTab === 'standards' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Curriculum Standards ({curriculumStandards.length})</h5>
              </Card.Header>
              <Card.Body>
                <div className="table-responsive">
                  <Table hover>
                    <thead className="table-light">
                      <tr>
                        <th>Code</th>
                        <th>Standard</th>
                        <th>Subject Area</th>
                        <th>Grade Level</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {curriculumStandards.map((standard) => (
                        <tr key={standard.id}>
                          <td className="fw-semibold">{standard.code}</td>
                          <td>{standard.title}</td>
                          <td>
                            <Badge bg="info">{standard.subject_area}</Badge>
                          </td>
                          <td>{standard.grade_level}</td>
                          <td>
                            <small className="text-muted">{standard.description}</small>
                          </td>
                          <td>
                            <Badge bg={getStatusBadge(standard.status)}>
                              {standard.status?.toUpperCase()}
                            </Badge>
                          </td>
                          <td>
                            <div className="d-flex gap-1">
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => navigate(`/curriculum/standards/${standard.id}`)}
                              >
                                View
                              </Button>
                              <Button 
                                variant="outline-warning" 
                                size="sm"
                                onClick={() => handleUpdateStandard(standard.id, { status: 'active' })}
                              >
                                Activate
                              </Button>
                            </div>
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

      {/* Reviews Tab */}
      {activeTab === 'reviews' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Pending Reviews ({pendingReviews.length})</h5>
              </Card.Header>
              <Card.Body>
                {pendingReviews.length > 0 ? (
                  <div className="table-responsive">
                    <Table hover>
                      <thead className="table-light">
                        <tr>
                          <th>Item Type</th>
                          <th>Title</th>
                          <th>Submitted By</th>
                          <th>Date Submitted</th>
                          <th>Reviewers</th>
                          <th>Priority</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {pendingReviews.map((review) => (
                          <tr key={review.id}>
                            <td>
                              <Badge bg={
                                review.item_type === 'lesson_plan' ? 'primary' :
                                review.item_type === 'resource' ? 'success' :
                                review.item_type === 'assessment' ? 'warning' : 'info'
                              }>
                                {review.item_type?.replace('_', ' ')}
                              </Badge>
                            </td>
                            <td className="fw-semibold">{review.title}</td>
                            <td>{review.submitted_by}</td>
                            <td>{formatDate(review.submitted_at)}</td>
                            <td>
                              <small>{review.reviewers?.join(', ') || 'Not assigned'}</small>
                            </td>
                            <td>
                              <Badge bg={review.priority === 'high' ? 'danger' : 'warning'}>
                                {review.priority}
                              </Badge>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => navigate(`/curriculum/reviews/${review.id}`)}
                                >
                                  Review
                                </Button>
                                <Button 
                                  variant="success" 
                                  size="sm"
                                  onClick={() => handleReviewAction(review.id, 'approve')}
                                >
                                  Approve
                                </Button>
                                <Button 
                                  variant="danger" 
                                  size="sm"
                                  onClick={() => handleReviewAction(review.id, 'reject')}
                                >
                                  Reject
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
                    <ClipboardCheck size={48} className="text-muted mb-3" />
                    <p className="text-muted mb-0">No pending reviews</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Resource Library Tab */}
      {activeTab === 'library' && (
        <Row>
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Resource Library</h5>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <FileEarmarkText size={48} className="text-primary mb-3" />
                        <h6>Lesson Templates</h6>
                        <p className="text-muted small">Pre-built lesson plan templates</p>
                        <Button 
                          variant="outline-primary" 
                          size="sm"
                          className="w-100"
                          onClick={() => navigate('/curriculum/library/templates')}
                        >
                          Browse Templates
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <CameraVideo size={48} className="text-success mb-3" />
                        <h6>Educational Videos</h6>
                        <p className="text-muted small">Video resources for teaching</p>
                        <Button 
                          variant="outline-success" 
                          size="sm"
                          className="w-100"
                          onClick={() => navigate('/curriculum/library/videos')}
                        >
                          View Videos
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4} className="mb-3">
                    <Card className="border">
                      <Card.Body className="text-center">
                        <FileEarmarkSpreadsheet size={48} className="text-warning mb-3" />
                        <h6>Worksheets</h6>
                        <p className="text-muted small">Printable worksheets & activities</p>
                        <Button 
                          variant="outline-warning" 
                          size="sm"
                          className="w-100"
                          onClick={() => navigate('/curriculum/library/worksheets')}
                        >
                          View Worksheets
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>

                <div className="table-responsive">
                  <Table hover>
                    <thead className="table-light">
                      <tr>
                        <th>Resource Name</th>
                        <th>Type</th>
                        <th>Subject</th>
                        <th>Grade Level</th>
                        <th>Downloads</th>
                        <th>Rating</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resourceLibrary.slice(0, 10).map((resource, index) => (
                        <tr key={index}>
                          <td className="fw-semibold">{resource.name}</td>
                          <td>
                            <Badge bg="info">{resource.type}</Badge>
                          </td>
                          <td>{resource.subject}</td>
                          <td>{resource.grade_level}</td>
                          <td>
                            <Badge bg="secondary">{resource.download_count || 0}</Badge>
                          </td>
                          <td>
                            <div className="d-flex">
                              {[...Array(5)].map((_, i) => (
                                <StarFill 
                                  key={i} 
                                  className={`${i < Math.floor(resource.rating || 0) ? 'text-warning' : 'text-muted'}`} 
                                  size={12}
                                />
                              ))}
                              <small className="ms-2">({resource.rating?.toFixed(1) || '0.0'})</small>
                            </div>
                          </td>
                          <td>
                            <div className="d-flex gap-1">
                              <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => window.open(resource.preview_url, '_blank')}
                              >
                                <Eye size={12} />
                              </Button>
                              <Button 
                                variant="outline-success" 
                                size="sm"
                                onClick={() => window.open(resource.download_url, '_blank')}
                              >
                                <Download size={12} />
                              </Button>
                            </div>
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

      {/* Resource Modal */}
      <Modal show={showResourceModal} onHide={() => setShowResourceModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Add Teaching Resource</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Title</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="Enter resource title"
                    value={resourceForm.title}
                    onChange={(e) => setResourceForm({...resourceForm, title: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Resource Type</Form.Label>
                  <Form.Select 
                    value={resourceForm.type}
                    onChange={(e) => setResourceForm({...resourceForm, type: e.target.value})}
                  >
                    <option value="document">Document</option>
                    <option value="presentation">Presentation</option>
                    <option value="video">Video</option>
                    <option value="worksheet">Worksheet</option>
                    <option value="audio">Audio</option>
                    <option value="image">Image</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={3}
                placeholder="Describe the resource"
                value={resourceForm.description}
                onChange={(e) => setResourceForm({...resourceForm, description: e.target.value})}
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Subject</Form.Label>
                  <Form.Select 
                    value={resourceForm.subject}
                    onChange={(e) => setResourceForm({...resourceForm, subject: e.target.value})}
                  >
                    <option value="">Select Subject</option>
                    {subjects.map((subject, index) => (
                      <option key={index} value={subject.name}>{subject.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Class</Form.Label>
                  <Form.Select 
                    value={resourceForm.class}
                    onChange={(e) => setResourceForm({...resourceForm, class: e.target.value})}
                  >
                    <option value="">Select Class</option>
                    {['Form 1', 'Form 2', 'Form 3', 'Form 4', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4'].map((cls, index) => (
                      <option key={index} value={cls}>{cls}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>File</Form.Label>
              <Form.Control 
                type="file"
                onChange={(e) => setResourceForm({...resourceForm, file: e.target.files[0]})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Tags (comma separated)</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="e.g., mathematics, algebra, worksheet"
                value={resourceForm.tags.join(', ')}
                onChange={(e) => setResourceForm({...resourceForm, tags: e.target.value.split(',').map(tag => tag.trim())})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Access Level</Form.Label>
              <Form.Select 
                value={resourceForm.accessLevel}
                onChange={(e) => setResourceForm({...resourceForm, accessLevel: e.target.value})}
              >
                <option value="public">Public (All teachers)</option>
                <option value="department">Department Only</option>
                <option value="private">Private (Only me)</option>
                <option value="shared">Shared with specific teachers</option>
              </Form.Select>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowResourceModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleAddResource} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Add Resource'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Lesson Plan Modal */}
      <Modal show={showLessonModal} onHide={() => setShowLessonModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create Lesson Plan</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Lesson Title</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="Enter lesson title"
                    value={lessonForm.title}
                    onChange={(e) => setLessonForm({...lessonForm, title: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Duration (minutes)</Form.Label>
                  <Form.Control 
                    type="number" 
                    placeholder="40"
                    value={lessonForm.duration}
                    onChange={(e) => setLessonForm({...lessonForm, duration: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Subject</Form.Label>
                  <Form.Select 
                    value={lessonForm.subject}
                    onChange={(e) => setLessonForm({...lessonForm, subject: e.target.value})}
                  >
                    <option value="">Select Subject</option>
                    {subjects.map((subject, index) => (
                      <option key={index} value={subject.name}>{subject.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Class</Form.Label>
                  <Form.Select 
                    value={lessonForm.class}
                    onChange={(e) => setLessonForm({...lessonForm, class: e.target.value})}
                  >
                    <option value="">Select Class</option>
                    {['Form 1', 'Form 2', 'Form 3', 'Form 4', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4'].map((cls, index) => (
                      <option key={index} value={cls}>{cls}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group className="mb-3">
                  <Form.Label>Term</Form.Label>
                  <Form.Select 
                    value={lessonForm.term}
                    onChange={(e) => setLessonForm({...lessonForm, term: e.target.value})}
                  >
                    <option value="1">Term 1</option>
                    <option value="2">Term 2</option>
                    <option value="3">Term 3</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Week</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="e.g., Week 5 or Specific dates"
                value={lessonForm.week}
                onChange={(e) => setLessonForm({...lessonForm, week: e.target.value})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Learning Objectives</Form.Label>
              {lessonForm.objectives.map((objective, index) => (
                <div key={index} className="d-flex mb-2">
                  <Form.Control 
                    type="text" 
                    placeholder={`Objective ${index + 1}`}
                    value={objective}
                    onChange={(e) => {
                      const newObjectives = [...lessonForm.objectives];
                      newObjectives[index] = e.target.value;
                      setLessonForm({...lessonForm, objectives: newObjectives});
                    }}
                  />
                  {index === lessonForm.objectives.length - 1 && (
                    <Button 
                      variant="outline-primary" 
                      className="ms-2"
                      onClick={() => setLessonForm({...lessonForm, objectives: [...lessonForm.objectives, '']})}
                    >
                      <Plus />
                    </Button>
                  )}
                  {lessonForm.objectives.length > 1 && (
                    <Button 
                      variant="outline-danger" 
                      className="ms-1"
                      onClick={() => {
                        const newObjectives = lessonForm.objectives.filter((_, i) => i !== index);
                        setLessonForm({...lessonForm, objectives: newObjectives});
                      }}
                    >
                      <X />
                    </Button>
                  )}
                </div>
              ))}
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Materials/Resources Needed</Form.Label>
              {lessonForm.materials.map((material, index) => (
                <div key={index} className="d-flex mb-2">
                  <Form.Control 
                    type="text" 
                    placeholder={`Material ${index + 1}`}
                    value={material}
                    onChange={(e) => {
                      const newMaterials = [...lessonForm.materials];
                      newMaterials[index] = e.target.value;
                      setLessonForm({...lessonForm, materials: newMaterials});
                    }}
                  />
                  {index === lessonForm.materials.length - 1 && (
                    <Button 
                      variant="outline-primary" 
                      className="ms-2"
                      onClick={() => setLessonForm({...lessonForm, materials: [...lessonForm.materials, '']})}
                    >
                      <Plus />
                    </Button>
                  )}
                  {lessonForm.materials.length > 1 && (
                    <Button 
                      variant="outline-danger" 
                      className="ms-1"
                      onClick={() => {
                        const newMaterials = lessonForm.materials.filter((_, i) => i !== index);
                        setLessonForm({...lessonForm, materials: newMaterials});
                      }}
                    >
                      <X />
                    </Button>
                  )}
                </div>
              ))}
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Assessment Method</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={2}
                placeholder="How will you assess student learning?"
                value={lessonForm.assessment}
                onChange={(e) => setLessonForm({...lessonForm, assessment: e.target.value})}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowLessonModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateLessonPlan} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Create Lesson Plan'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Assessment Modal */}
      <Modal show={showAssessmentModal} onHide={() => setShowAssessmentModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create Assessment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Assessment Title</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="Enter assessment title"
                value={assessmentForm.title}
                onChange={(e) => setAssessmentForm({...assessmentForm, title: e.target.value})}
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Subject</Form.Label>
                  <Form.Select 
                    value={assessmentForm.subject}
                    onChange={(e) => setAssessmentForm({...assessmentForm, subject: e.target.value})}
                  >
                    <option value="">Select Subject</option>
                    {subjects.map((subject, index) => (
                      <option key={index} value={subject.name}>{subject.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Class</Form.Label>
                  <Form.Select 
                    value={assessmentForm.class}
                    onChange={(e) => setAssessmentForm({...assessmentForm, class: e.target.value})}
                  >
                    <option value="">Select Class</option>
                    {['Form 1', 'Form 2', 'Form 3', 'Form 4', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4'].map((cls, index) => (
                      <option key={index} value={cls}>{cls}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Assessment Type</Form.Label>
                  <Form.Select 
                    value={assessmentForm.type}
                    onChange={(e) => setAssessmentForm({...assessmentForm, type: e.target.value})}
                  >
                    <option value="quiz">Quiz</option>
                    <option value="test">Test</option>
                    <option value="assignment">Assignment</option>
                    <option value="project">Project</option>
                    <option value="presentation">Presentation</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Max Score</Form.Label>
                  <Form.Control 
                    type="number" 
                    placeholder="100"
                    value={assessmentForm.maxScore}
                    onChange={(e) => setAssessmentForm({...assessmentForm, maxScore: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Duration (minutes)</Form.Label>
                  <Form.Control 
                    type="number" 
                    placeholder="60"
                    value={assessmentForm.duration}
                    onChange={(e) => setAssessmentForm({...assessmentForm, duration: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Due Date</Form.Label>
              <Form.Control 
                type="date"
                value={assessmentForm.dueDate}
                onChange={(e) => setAssessmentForm({...assessmentForm, dueDate: e.target.value})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Rubric/Scoring Guide</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={3}
                placeholder="Describe the rubric or scoring criteria"
                value={assessmentForm.rubric}
                onChange={(e) => setAssessmentForm({...assessmentForm, rubric: e.target.value})}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAssessmentModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateAssessment} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Create Assessment'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Import Modal */}
      <Modal show={showImportModal} onHide={() => setShowImportModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Import Curriculum Data</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Import Type</Form.Label>
              <Form.Select 
                value={importForm.type}
                onChange={(e) => setImportForm({...importForm, type: e.target.value})}
              >
                <option value="curriculum">Curriculum Framework</option>
                <option value="subjects">Subjects</option>
                <option value="lesson_plans">Lesson Plans</option>
                <option value="resources">Teaching Resources</option>
                <option value="assessments">Assessments</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>File Format</Form.Label>
              <Form.Select 
                value={importForm.format}
                onChange={(e) => setImportForm({...importForm, format: e.target.value})}
              >
                <option value="csv">CSV</option>
                <option value="excel">Excel</option>
                <option value="json">JSON</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>File</Form.Label>
              <Form.Control 
                type="file"
                onChange={(e) => setImportForm({...importForm, file: e.target.files[0]})}
              />
              <Form.Text className="text-muted">
                Upload a CSV, Excel, or JSON file with the appropriate data structure.
              </Form.Text>
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Academic Year</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="e.g., 2024"
                    value={importForm.academicYear}
                    onChange={(e) => setImportForm({...importForm, academicYear: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Term</Form.Label>
                  <Form.Select 
                    value={importForm.term}
                    onChange={(e) => setImportForm({...importForm, term: e.target.value})}
                  >
                    <option value="">Select Term</option>
                    <option value="1">Term 1</option>
                    <option value="2">Term 2</option>
                    <option value="3">Term 3</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Check 
              type="checkbox"
              label="Overwrite existing data"
              checked={importForm.overwrite}
              onChange={(e) => setImportForm({...importForm, overwrite: e.target.checked})}
            />
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowImportModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleImportData} disabled={loading}>
            {loading ? <Spinner size="sm" /> : 'Import Data'}
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
                  Curriculum Portal v2.0 • Academic Year: {academicYear} • Term: {term} • 
                  Version: {curriculumOverview.curriculumVersion}
                </small>
                <div>
                  <small className="text-muted me-3">
                    Last Refresh: {new Date(lastRefreshTime).toLocaleString()}
                  </small>
                  <small className="text-muted">
                    Status: <Badge bg="success">Operational</Badge>
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
        .bg-gradient-purple {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
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

export default CurriculumPortal;