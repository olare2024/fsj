import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, 
  Alert, Spinner, Form, InputGroup, Dropdown, Modal,
  ProgressBar, Pagination, Tooltip, OverlayTrigger,
  ButtonGroup, Tabs, Tab, Placeholder, FormCheck,
  DropdownButton, Nav, NavItem, NavLink
} from 'react-bootstrap';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Pencil as EditIcon,
  Plus as PlusIcon,
  Trash as DeleteIcon,
  Eye as ViewIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  FunnelFill as FilterIcon,
  ArrowClockwise as RefreshIcon,
  ExclamationTriangle as AlertTriangleIcon,
  Calendar as CalendarIcon,
  People as UsersIcon,
  FileText as FileTextIcon,
  ThreeDotsVertical as MoreVerticalIcon,
  SortAlphaDown as SortAscIcon,
  SortAlphaDownAlt as SortDescIcon,
  ClipboardCheck as AssignmentIcon,
  Award as GradeIcon,
  Book as BookIcon,
  Building as SchoolIcon,
  CheckCircle as CheckCircleIcon,
  Clock as ClockIcon,
  ExclamationTriangle,
  XCircle as XCircleIcon,
  Info as InfoIcon,
  Copy as CopyIcon,
  EyeSlash as EyeSlashIcon,
  CheckSquare as CheckSquareIcon,
  CalendarCheck as CalendarCheckIcon,
  FileCheck as FileCheckIcon,
  Share as ShareIcon,
  GraphUp as AnalyticsIcon,
  Tag as TagIcon,
  Layers as LayersIcon,
  BarChart as BarChartIcon,
  Funnel as FilterXIcon,
  Archive as ArchiveIcon,
  Send as SendIcon,
  Envelope as MailIcon,
  Bell as BellIcon,
  GraphUpArrow as TrendingUpIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Grid3x3 as GridIcon,
  List as ListIcon,
  Check as CheckIcon,
  X as XIcon,
  Files as DocumentDuplicateIcon,
  BellFill as BellRingIcon,
  
  File as FileIcon,
  CalendarDay as CalendarDaysIcon,
  Plus as FilterPlusIcon,
  ChevronDown as ChevronDownIcon,
  ChevronUp as ChevronUpIcon,
  Star as StarIcon,
  Bullseye as TargetIcon,
  Percent as PercentIcon,

  // Replacements for invalid Heroicons-style names
  Book as BookOpenIcon,
  FileEarmarkBarGraph as FileBarChartIcon,
  Calendar as CalendarClockIcon,

  PersonCheck as UserCheckIcon,
  CalendarRange as CalendarRangeIcon,
  Gear as SettingsIcon,
  Folder as FolderIcon,
  Folder2Open as FolderOpenIcon,
  FolderPlus as FolderPlusIcon,
  ClockHistory as TimerIcon,
  PeopleFill as UsersRoundIcon,
  FileEarmarkText as FileEditIcon,
  FileEarmarkMedical as FileSearchIcon,
  FileX as FileXIcon,
  Clipboard2Check as ClipboardCheckIcon
} from "react-bootstrap-icons";




import { assignmentsAPI, ASSIGNMENT_CONSTANTS } from '../../services/assignmentsAPI-old';
import { academicAPI } from '../../services/academicAPI';
import { useAuth } from '../../context/AuthContext';
import  useDebounce  from '../../hooks/useDebounce';
import { toast } from 'react-toastify';

// ==================== HELPER COMPONENTS ====================

// Skeleton Loader Component
const AssignmentSkeleton = ({ count = 5 }) => (
  <tbody>
    {Array.from({ length: count }).map((_, index) => (
      <tr key={index}>
        <td>
          <div className="d-flex align-items-center">
            <Placeholder as="div" animation="wave" className="rounded me-2" style={{ width: 40, height: 40 }} />
            <div className="flex-grow-1">
              <Placeholder as="div" animation="wave" style={{ width: '60%', height: 20 }} className="mb-1" />
              <Placeholder as="div" animation="wave" style={{ width: '40%', height: 15 }} />
            </div>
          </div>
        </td>
        <td>
          <Placeholder as="div" animation="wave" style={{ width: '70%', height: 20 }} />
        </td>
        <td>
          <Placeholder as="div" animation="wave" style={{ width: '60%', height: 20 }} />
        </td>
        <td>
          <Placeholder as="div" animation="wave" style={{ width: 80, height: 25 }} className="rounded-pill" />
        </td>
        <td>
          <Placeholder as="div" animation="wave" style={{ width: '80%', height: 20 }} />
        </td>
        <td>
          <Placeholder as="div" animation="wave" style={{ width: 120, height: 30 }} />
        </td>
      </tr>
    ))}
  </tbody>
);

// Empty State Component
const EmptyState = ({ title, message, icon: Icon = FileTextIcon, action }) => (
  <div className="text-center py-5">
    <div className="mb-4">
      <div className="rounded-circle bg-light d-inline-flex align-items-center justify-content-center" 
           style={{ width: 80, height: 80 }}>
        <Icon size={32} className="text-muted" />
      </div>
    </div>
    <h5 className="text-muted mb-2">{title}</h5>
    <p className="text-muted mb-4" style={{ maxWidth: '400px', margin: '0 auto' }}>
      {message}
    </p>
    {action}
  </div>
);

// Status Badge Component
const StatusBadge = ({ status, showIcon = true }) => {
  const statusConfig = {
    draft: { variant: 'secondary', icon: FileTextIcon, label: 'Draft' },
    published: { variant: 'success', icon: CheckCircleIcon, label: 'Published' },
    in_progress: { variant: 'info', icon: ClockIcon, label: 'In Progress' },
    closed: { variant: 'dark', icon: XCircleIcon, label: 'Closed' },
    graded: { variant: 'primary', icon: GradeIcon, label: 'Graded' },
    archived: { variant: 'warning', icon: ArchiveIcon, label: 'Archived' }
  };

  const config = statusConfig[status] || { variant: 'secondary', icon: InfoIcon, label: status };

  return (
    <Badge bg={config.variant} className="d-inline-flex align-items-center gap-1">
      {showIcon && <config.icon size={12} />}
      <span className="text-uppercase">{config.label}</span>
    </Badge>
  );
};

// Submission Progress Component
const SubmissionProgress = ({ assignment }) => {
  const stats = assignment.submission_stats || assignment.statistics || {};
  const total = stats.total_students || stats.total || 0;
  const submitted = stats.submitted_count || stats.submitted || 0;
  const graded = stats.graded_count || stats.graded || 0;
  
  const submittedPercent = total > 0 ? (submitted / total) * 100 : 0;
  const gradedPercent = total > 0 ? (graded / total) * 100 : 0;
  const pendingPercent = Math.max(0, submittedPercent - gradedPercent);

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-1">
        <small className="text-muted">
          {submitted}/{total} submitted
        </small>
        <small className="text-muted">
          {graded} graded
        </small>
      </div>
      <ProgressBar className="mb-2" style={{ height: '6px' }}>
        <ProgressBar 
          variant="success" 
          now={gradedPercent} 
          key={1}
          label={`${Math.round(gradedPercent)}%`}
        />
        <ProgressBar 
          variant="warning" 
          now={pendingPercent} 
          key={2}
          label={`${Math.round(pendingPercent)}%`}
        />
      </ProgressBar>
      <small className="text-muted d-block text-center">
        {Math.round(submittedPercent)}% complete
      </small>
    </div>
  );
};

// ==================== MAIN COMPONENT ====================

const TeacherAssignments = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const abortControllerRef = useRef(null);
  
  // State management
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stats, setStats] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [selectedAssignments, setSelectedAssignments] = useState(new Set());
  const [viewMode, setViewMode] = useState(localStorage.getItem('assignmentViewMode') || 'table');
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'all');
  const [dropdownVisible, setDropdownVisible] = useState({});
  const [expandedAssignments, setExpandedAssignments] = useState(new Set());

  // Filters from URL params
  const initialFilters = {
    search: searchParams.get('search') || '',
    status: searchParams.get('status') || '',
    subject: searchParams.get('subject') || '',
    classroom: searchParams.get('classroom') || '',
    assignment_type: searchParams.get('type') || '',
    sortBy: searchParams.get('sort') || '-due_date',
    sortOrder: searchParams.get('order') || 'desc',
    academic_year: searchParams.get('academic_year') || '',
    term: searchParams.get('term') || '',
    date_from: searchParams.get('from') || '',
    date_to: searchParams.get('to') || '',
    difficulty_level: searchParams.get('difficulty') || '',
    category: searchParams.get('category') || '',
    curriculum: searchParams.get('curriculum') || ''
  };

  const [filters, setFilters] = useState(initialFilters);
  const debouncedSearch = useDebounce(filters.search, 500);

  const [pagination, setPagination] = useState({
    current: parseInt(searchParams.get('page')) || 1,
    total: 0,
    pageSize: parseInt(searchParams.get('page_size')) || 10
  });

  const [deleteModal, setDeleteModal] = useState({ 
    show: false, 
    assignment: null,
    bulk: false 
  });

  const [actionModal, setActionModal] = useState({
    show: false,
    type: '',
    assignments: [],
    data: {}
  });

  // ==================== EFFECTS ====================

  // Fetch initial data
  useEffect(() => {
    fetchInitialData();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    
    // Add all filters to URL
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== '') {
        params.set(key, value);
      }
    });
    
    // Add pagination
    params.set('page', pagination.current.toString());
    params.set('page_size', pagination.pageSize.toString());
    params.set('tab', activeTab);
    
    // Update URL without triggering navigation
    setSearchParams(params, { replace: true });
  }, [filters, pagination, activeTab, setSearchParams]);

  // Fetch assignments when filters/debounced search changes
  useEffect(() => {
    fetchAssignments();
  }, [debouncedSearch, filters.status, filters.subject, filters.classroom, 
      filters.assignment_type, filters.sortBy, filters.sortOrder, 
      filters.academic_year, filters.term, filters.date_from, 
      filters.date_to, filters.difficulty_level, filters.category, 
      filters.curriculum, activeTab]);

  // Handle location state messages
  useEffect(() => {
    if (location.state?.message) {
      const message = location.state.message;
      toast.success(message);
      
      const timer = setTimeout(() => {
        navigate(location.pathname, { replace: true, state: {} });
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [location, navigate]);

  // ==================== DATA FETCHING ====================

  const fetchInitialData = async () => {
    try {
      // Fetch subjects and classes in parallel
      const [subjectsResult, classesResult, statsResult] = await Promise.allSettled([
        academicAPI.getSubjects({ limit: 100, ordering: 'name' }),
        academicAPI.getClasses({ limit: 100, ordering: 'name' }),
        assignmentsAPI.getTeacherStats()
      ]);

      if (subjectsResult.status === 'fulfilled' && subjectsResult.value.success) {
        setSubjects(subjectsResult.value.data.results || subjectsResult.value.data);
      }

      if (classesResult.status === 'fulfilled' && classesResult.value.success) {
        setClasses(classesResult.value.data.results || classesResult.value.data);
      }

      if (statsResult.status === 'fulfilled' && statsResult.value.success) {
        setStats(statsResult.value.data);
      }
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const fetchAssignments = useCallback(async (page = 1, refresh = false) => {
    // Cancel previous request if exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    try {
      if (page === 1 && !refresh) setLoading(true);
      setRefreshing(true);
      setError('');

      // Build params
      const params = {
        limit: pagination.pageSize,
        offset: (page - 1) * pagination.pageSize,
        ordering: filters.sortBy,
        ...filters
      };

      // Remove empty params
      Object.keys(params).forEach(key => {
        if (!params[key] && key !== 'limit' && key !== 'offset' && key !== 'ordering') {
          delete params[key];
        }
      });

      // Handle active tab filters
      if (activeTab !== 'all') {
        switch (activeTab) {
          case 'draft':
            params.status = ASSIGNMENT_CONSTANTS.STATUS.DRAFT;
            break;
          case 'published':
            params.status = ASSIGNMENT_CONSTANTS.STATUS.PUBLISHED;
            break;
          case 'graded':
            params.status = ASSIGNMENT_CONSTANTS.STATUS.GRADED;
            break;
          case 'closed':
            params.status = ASSIGNMENT_CONSTANTS.STATUS.CLOSED;
            break;
          case 'overdue':
            params.is_overdue = true;
            break;
          case 'pending':
            params.has_pending_grading = true;
            break;
          case 'archived':
            params.status = ASSIGNMENT_CONSTANTS.STATUS.ARCHIVED;
            break;
        }
      }

      const result = await assignmentsAPI.getMyAssignments(params, abortControllerRef.current.signal);
      
      if (result.success) {
        const data = result.data;
        setAssignments(data.results || data);
        setPagination(prev => ({
          ...prev,
          current: page,
          total: data.count || (data.results ? data.results.length : 0)
        }));
        
        // Update stats if available
        if (data.statistics) {
          setStats(data.statistics);
        }
        
        setSuccess('');
      } else {
        if (result.error?.code !== 'CANCELLED') {
          setError(result.error?.message || 'Failed to load assignments');
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError('An unexpected error occurred while loading assignments');
        console.error('Error fetching assignments:', err);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [filters, pagination.pageSize, activeTab]);

  // ==================== FILTER HANDLERS ====================

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleClearFilters = () => {
    setFilters({
      search: '',
      status: '',
      subject: '',
      classroom: '',
      assignment_type: '',
      sortBy: '-due_date',
      sortOrder: 'desc',
      academic_year: '',
      term: '',
      date_from: '',
      date_to: '',
      difficulty_level: '',
      category: '',
      curriculum: ''
    });
    setPagination(prev => ({ ...prev, current: 1 }));
  };

  const handleSortChange = (field) => {
    setFilters(prev => ({
      ...prev,
      sortBy: prev.sortBy === field ? `-${field}` : field,
      sortOrder: prev.sortBy === field ? 'desc' : 'asc'
    }));
  };

  // ==================== ACTION HANDLERS ====================

  const handleRefresh = () => {
    fetchAssignments(pagination.current, true);
  };

  const handleBulkAction = async (action, assignmentIds = []) => {
    const ids = assignmentIds.length > 0 
      ? assignmentIds 
      : Array.from(selectedAssignments);
    
    if (ids.length === 0) {
      toast.warning('Please select at least one assignment');
      return;
    }

    try {
      setLoading(true);
      let result;

      switch (action) {
        case 'publish':
          result = await Promise.all(ids.map(id => 
            assignmentsAPI.publishAssignment(id)
          ));
          break;
        
        case 'unpublish':
          result = await Promise.all(ids.map(id => 
            assignmentsAPI.unpublishAssignment(id)
          ));
          break;
        
        case 'close':
          result = await Promise.all(ids.map(id => 
            assignmentsAPI.closeAssignment(id)
          ));
          break;
        
        case 'duplicate':
          result = await Promise.all(ids.map(id => 
            assignmentsAPI.duplicateAssignment(id, {
              title: `Copy of ${assignments.find(a => a.id === id)?.title}`
            })
          ));
          break;
        
        case 'archive':
          result = await Promise.all(ids.map(id => 
            assignmentsAPI.updateAssignment(id, { 
              status: ASSIGNMENT_CONSTANTS.STATUS.ARCHIVED 
            })
          ));
          break;
        
        case 'delete':
          setDeleteModal({ 
            show: true, 
            assignment: null, 
            bulk: true,
            assignmentIds: ids 
          });
          return;
        
        default:
          throw new Error('Unknown bulk action');
      }

      // Check if all operations succeeded
      const allSuccess = result.every(r => r.success);
      
      if (allSuccess) {
        const message = `${ids.length} assignment${ids.length > 1 ? 's' : ''} ${action}ed successfully`;
        toast.success(message);
        
        // Refresh assignments
        fetchAssignments(pagination.current, true);
        
        // Clear selection
        setSelectedAssignments(new Set());
      } else {
        toast.error(`Some operations failed. Please try again.`);
      }
    } catch (error) {
      console.error(`Error performing bulk ${action}:`, error);
      toast.error(`Failed to ${action} assignments`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAssignment = async (assignmentId) => {
    try {
      const result = await assignmentsAPI.deleteAssignment(assignmentId);
      
      if (result.success) {
        toast.success('Assignment deleted successfully!');
        setAssignments(prev => prev.filter(a => a.id !== assignmentId));
        setDeleteModal({ show: false, assignment: null, bulk: false });
        
        // Update stats
        if (stats) {
          setStats(prev => ({
            ...prev,
            total_assignments: Math.max(0, prev.total_assignments - 1)
          }));
        }
      } else {
        throw new Error(result.error?.message);
      }
    } catch (err) {
      toast.error(err.message || 'Failed to delete assignment');
    }
  };

  const handleBulkDelete = async () => {
    const ids = deleteModal.assignmentIds || [];
    
    try {
      setLoading(true);
      const results = await Promise.all(
        ids.map(id => assignmentsAPI.deleteAssignment(id))
      );
      
      const allSuccess = results.every(r => r.success);
      
      if (allSuccess) {
        toast.success(`${ids.length} assignment${ids.length > 1 ? 's' : ''} deleted successfully!`);
        setAssignments(prev => prev.filter(a => !ids.includes(a.id)));
        setSelectedAssignments(new Set());
        
        // Update stats
        if (stats) {
          setStats(prev => ({
            ...prev,
            total_assignments: Math.max(0, prev.total_assignments - ids.length)
          }));
        }
      } else {
        toast.error('Some assignments could not be deleted');
      }
    } catch (err) {
      toast.error('Failed to delete assignments');
    } finally {
      setLoading(false);
      setDeleteModal({ show: false, assignment: null, bulk: false });
    }
  };

  const handleSelectAll = () => {
    if (selectedAssignments.size === assignments.length) {
      setSelectedAssignments(new Set());
    } else {
      setSelectedAssignments(new Set(assignments.map(a => a.id)));
    }
  };

  const handleSelectAssignment = (assignmentId) => {
    const newSelection = new Set(selectedAssignments);
    if (newSelection.has(assignmentId)) {
      newSelection.delete(assignmentId);
    } else {
      newSelection.add(assignmentId);
    }
    setSelectedAssignments(newSelection);
  };

  const toggleAssignmentExpand = (assignmentId) => {
    const newExpanded = new Set(expandedAssignments);
    if (newExpanded.has(assignmentId)) {
      newExpanded.delete(assignmentId);
    } else {
      newExpanded.add(assignmentId);
    }
    setExpandedAssignments(newExpanded);
  };

  // ==================== FORMATTING FUNCTIONS ====================

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    // Format date
    const formattedDate = date.toLocaleDateString('en-KE', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
    
    // Add time if available
    const time = date.toLocaleTimeString('en-KE', {
      hour: '2-digit',
      minute: '2-digit'
    });
    
    // Add relative time indicator
    let relativeTime = '';
    if (diffDays === 0) {
      relativeTime = ' (Today)';
    } else if (diffDays === 1) {
      relativeTime = ' (Tomorrow)';
    } else if (diffDays === -1) {
      relativeTime = ' (Yesterday)';
    } else if (diffDays < 0) {
      relativeTime = ` (${Math.abs(diffDays)} days ago)`;
    } else if (diffDays > 0) {
      relativeTime = ` (in ${diffDays} days)`;
    }
    
    return (
      <div className="d-flex flex-column">
        <span className="fw-medium">{formattedDate}</span>
        <small className="text-muted">
          {time}
          {relativeTime && <span className="ms-1 text-warning">{relativeTime}</span>}
        </small>
      </div>
    );
  };

  const getAssignmentTypeLabel = (type) => {
    const typeMap = {
      'homework': 'Homework',
      'classwork': 'Classwork',
      'project': 'Project',
      'quiz': 'Quiz',
      'test': 'Test',
      'exam': 'Exam',
      'practical': 'Practical',
      'presentation': 'Presentation',
      'research': 'Research',
      'revision': 'Revision',
      'assessment': 'Assessment'
    };
    
    return typeMap[type] || type;
  };

  const getDifficultyBadge = (difficulty) => {
    const config = {
      'easy': { variant: 'success', icon: CheckCircleIcon },
      'medium': { variant: 'warning', icon: AlertTriangleIcon },
      'hard': { variant: 'danger', icon: XCircleIcon },
      'challenging': { variant: 'dark', icon: StarIcon }
    };
    
    const conf = config[difficulty] || { variant: 'secondary', icon: InfoIcon };
    
    return (
      <Badge bg={conf.variant} className="d-inline-flex align-items-center gap-1">
        <conf.icon size={10} />
        <span className="text-uppercase">{difficulty}</span>
      </Badge>
    );
  };

  // ==================== MEMOIZED VALUES ====================

  const filteredSubjects = useMemo(() => {
    return subjects.map(subject => ({
      value: subject.id,
      label: subject.name,
      code: subject.code
    }));
  }, [subjects]);

  const filteredClasses = useMemo(() => {
    return classes.map(cls => ({
      value: cls.id,
      label: cls.name || cls.display_name,
      grade: cls.grade_level
    }));
  }, [classes]);

  const assignmentTypes = useMemo(() => {
    return Object.entries(ASSIGNMENT_CONSTANTS.TYPES).map(([key, value]) => ({
      value,
      label: getAssignmentTypeLabel(value)
    }));
  }, []);

  const difficultyLevels = useMemo(() => {
    return Object.entries(ASSIGNMENT_CONSTANTS.DIFFICULTY).map(([key, value]) => ({
      value,
      label: value.charAt(0).toUpperCase() + value.slice(1)
    }));
  }, []);

  const tabStats = useMemo(() => {
    if (!stats) return {};
    
    return {
      all: stats.total_assignments || 0,
      draft: stats.draft_count || 0,
      published: stats.published_count || 0,
      graded: stats.graded_count || 0,
      closed: stats.closed_count || 0,
      overdue: stats.overdue_count || 0,
      pending: stats.pending_grading_count || 0,
      archived: stats.archived_count || 0
    };
  }, [stats]);

  // ==================== RENDER FUNCTIONS ====================

  const renderAssignmentRow = (assignment) => {
    const isExpanded = expandedAssignments.has(assignment.id);
    const isSelected = selectedAssignments.has(assignment.id);
    
    return (
      <React.Fragment key={assignment.id}>
        <tr className={isSelected ? 'table-primary' : ''}>
          <td style={{ width: '50px' }}>
            <FormCheck 
              checked={isSelected}
              onChange={() => handleSelectAssignment(assignment.id)}
              className="m-0"
            />
          </td>
          <td>
            <div className="d-flex align-items-center">
              <div className="me-3">
                <div className={`rounded p-2 bg-${getAssignmentTypeLabel(assignment.assignment_type).toLowerCase()}-subtle`}>
                  <AssignmentIcon size={20} />
                </div>
              </div>
              <div className="flex-grow-1">
                <div className="d-flex align-items-center mb-1">
                  <Link 
                    to={`/teacher/assignments/${assignment.id}`}
                    className="fw-semibold text-decoration-none"
                  >
                    {assignment.title}
                  </Link>
                  {assignment.is_overdue && (
                    <Badge bg="danger" className="ms-2">
                      <ClockIcon size={10} className="me-1" />
                      Overdue
                    </Badge>
                  )}
                </div>
                <div className="d-flex align-items-center gap-2">
                  <small className="text-muted">
                    <BookIcon size={12} className="me-1" />
                    {assignment.subject?.name || assignment.subject_name}
                  </small>
                  <small className="text-muted">
                    <SchoolIcon size={12} className="me-1" />
                    {assignment.classroom?.name || assignment.classroom_name}
                  </small>
                  {assignment.difficulty_level && (
                    <small>
                      {getDifficultyBadge(assignment.difficulty_level)}
                    </small>
                  )}
                </div>
              </div>
            </div>
          </td>
          <td>
            <div className="d-flex flex-column">
              <span className="fw-medium">{getAssignmentTypeLabel(assignment.assignment_type)}</span>
              <small className="text-muted">
                {assignment.total_marks} marks
              </small>
            </div>
          </td>
          <td>
            {formatDate(assignment.due_date)}
          </td>
          <td>
            <StatusBadge status={assignment.status} />
          </td>
          <td style={{ width: '150px' }}>
            <SubmissionProgress assignment={assignment} />
          </td>
          <td style={{ width: '100px' }}>
            <Dropdown onToggle={(isOpen) => setDropdownVisible(prev => ({ ...prev, [assignment.id]: isOpen }))}>
              <Dropdown.Toggle 
                variant="outline-secondary" 
                size="sm" 
                id={`assignment-actions-${assignment.id}`}
              >
                <MoreVerticalIcon size={14} />
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <Dropdown.Item as={Link} to={`/teacher/assignments/${assignment.id}`}>
                  <ViewIcon className="me-2" size={14} />
                  View Details
                </Dropdown.Item>
                <Dropdown.Item as={Link} to={`/teacher/assignments/${assignment.id}/submissions`}>
                  <UsersIcon className="me-2" size={14} />
                  Submissions ({assignment.submission_stats?.submitted || 0})
                </Dropdown.Item>
                <Dropdown.Item as={Link} to={`/teacher/assignments/${assignment.id}/grade`}>
                  <GradeIcon className="me-2" size={14} />
                  Grade
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item as={Link} to={`/teacher/assignments/${assignment.id}/edit`}>
                  <EditIcon className="me-2" size={14} />
                  Edit
                </Dropdown.Item>
                <Dropdown.Item onClick={() => {
                  assignmentsAPI.duplicateAssignment(assignment.id, {
                    title: `Copy of ${assignment.title}`
                  }).then(result => {
                    if (result.success) {
                      toast.success('Assignment duplicated successfully!');
                      fetchAssignments(pagination.current, true);
                    }
                  });
                }}>
                  <CopyIcon className="me-2" size={14} />
                  Duplicate
                </Dropdown.Item>
                <Dropdown.Divider />
                {assignment.status === ASSIGNMENT_CONSTANTS.STATUS.DRAFT && (
                  <Dropdown.Item onClick={() => {
                    assignmentsAPI.publishAssignment(assignment.id).then(result => {
                      if (result.success) {
                        toast.success('Assignment published!');
                        fetchAssignments(pagination.current, true);
                      }
                    });
                  }}>
                    <SendIcon className="me-2" size={14} />
                    Publish
                  </Dropdown.Item>
                )}
                {assignment.status === ASSIGNMENT_CONSTANTS.STATUS.PUBLISHED && (
                  <Dropdown.Item onClick={() => {
                    assignmentsAPI.unpublishAssignment(assignment.id).then(result => {
                      if (result.success) {
                        toast.success('Assignment unpublished!');
                        fetchAssignments(pagination.current, true);
                      }
                    });
                  }}>
                    <EyeSlashIcon className="me-2" size={14} />
                    Unpublish
                  </Dropdown.Item>
                )}
                {assignment.status !== ASSIGNMENT_CONSTANTS.STATUS.CLOSED && (
                  <Dropdown.Item onClick={() => {
                    assignmentsAPI.closeAssignment(assignment.id).then(result => {
                      if (result.success) {
                        toast.success('Assignment closed!');
                        fetchAssignments(pagination.current, true);
                      }
                    });
                  }}>
                    <XCircleIcon className="me-2" size={14} />
                    Close
                  </Dropdown.Item>
                )}
                <Dropdown.Item onClick={() => {
                  assignmentsAPI.updateAssignment(assignment.id, {
                    status: ASSIGNMENT_CONSTANTS.STATUS.ARCHIVED
                  }).then(result => {
                    if (result.success) {
                      toast.success('Assignment archived!');
                      fetchAssignments(pagination.current, true);
                    }
                  });
                }}>
                  <ArchiveIcon className="me-2" size={14} />
                  Archive
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item 
                  className="text-danger"
                  onClick={() => setDeleteModal({ show: true, assignment, bulk: false })}
                >
                  <DeleteIcon className="me-2" size={14} />
                  Delete
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </td>
        </tr>
        
        {/* Expanded Details Row */}
        {isExpanded && (
          <tr className="bg-light">
            <td colSpan={7}>
              <div className="p-3">
                <Row>
                  <Col md={6}>
                    <h6 className="mb-2">Assignment Details</h6>
                    {assignment.description && (
                      <p className="text-muted small mb-2">{assignment.description}</p>
                    )}
                    <div className="d-flex flex-wrap gap-2 mb-3">
                      <Badge bg="info">
                        <CalendarIcon size={12} className="me-1" />
                        Created: {formatDate(assignment.created_at)}
                      </Badge>
                      {assignment.updated_at !== assignment.created_at && (
                        <Badge bg="secondary">
                          <ClockIcon size={12} className="me-1" />
                          Updated: {formatDate(assignment.updated_at)}
                        </Badge>
                      )}
                      <Badge bg="warning">
                        <TimerIcon size={12} className="me-1" />
                        Est. Time: {assignment.estimated_completion_time} min
                      </Badge>
                    </div>
                  </Col>
                  <Col md={6}>
                    <h6 className="mb-2">Quick Actions</h6>
                    <div className="d-flex gap-2">
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        as={Link}
                        to={`/teacher/assignments/${assignment.id}/submissions`}
                      >
                        <UsersIcon className="me-1" size={14} />
                        View Submissions
                      </Button>
                      <Button 
                        variant="outline-success" 
                        size="sm"
                        as={Link}
                        to={`/teacher/assignments/${assignment.id}/analytics`}
                      >
                        <AnalyticsIcon className="me-1" size={14} />
                        Analytics
                      </Button>
                      <Button 
                        variant="outline-info" 
                        size="sm"
                        onClick={() => navigator.clipboard.writeText(
                          `${window.location.origin}/teacher/assignments/${assignment.id}`
                        )}
                      >
                        <ShareIcon className="me-1" size={14} />
                        Copy Link
                      </Button>
                    </div>
                  </Col>
                </Row>
              </div>
            </td>
          </tr>
        )}
      </React.Fragment>
    );
  };

  const renderBulkActions = () => {
    if (selectedAssignments.size === 0) return null;

    return (
      <Card className="border-0 shadow-sm mb-3">
        <Card.Body className="py-2">
          <div className="d-flex align-items-center justify-content-between">
            <div className="d-flex align-items-center">
              <Badge bg="primary" className="me-2">
                {selectedAssignments.size} selected
              </Badge>
              <Button 
                variant="link" 
                size="sm"
                onClick={() => setSelectedAssignments(new Set())}
                className="text-decoration-none"
              >
                Clear selection
              </Button>
            </div>
            <div className="d-flex gap-2">
              <DropdownButton
                title="Bulk Actions"
                variant="outline-primary"
                size="sm"
              >
                <Dropdown.Item onClick={() => handleBulkAction('publish')}>
                  <SendIcon className="me-2" size={14} />
                  Publish Selected
                </Dropdown.Item>
                <Dropdown.Item onClick={() => handleBulkAction('unpublish')}>
                  <EyeSlashIcon className="me-2" size={14} />
                  Unpublish Selected
                </Dropdown.Item>
                <Dropdown.Item onClick={() => handleBulkAction('close')}>
                  <XCircleIcon className="me-2" size={14} />
                  Close Selected
                </Dropdown.Item>
                <Dropdown.Item onClick={() => handleBulkAction('duplicate')}>
                  <CopyIcon className="me-2" size={14} />
                  Duplicate Selected
                </Dropdown.Item>
                <Dropdown.Item onClick={() => handleBulkAction('archive')}>
                  <ArchiveIcon className="me-2" size={14} />
                  Archive Selected
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item 
                  className="text-danger"
                  onClick={() => setDeleteModal({ 
                    show: true, 
                    assignment: null, 
                    bulk: true,
                    assignmentIds: Array.from(selectedAssignments)
                  })}
                >
                  <DeleteIcon className="me-2" size={14} />
                  Delete Selected
                </Dropdown.Item>
              </DropdownButton>
            </div>
          </div>
        </Card.Body>
      </Card>
    );
  };

  // ==================== RENDER ====================

  if (loading && !refreshing) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" />
          <p className="mt-3 text-muted">Loading your assignments...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">
                <AssignmentIcon className="me-2" size={24} />
                My Assignments
              </h1>
              <p className="text-muted mb-0">
                Manage and track all your assignments
                {stats && (
                  <span className="ms-2">
                    • Total: <strong>{stats.total_assignments}</strong>
                    {stats.overdue_count > 0 && (
                      <span className="text-danger ms-2">
                        • Overdue: <strong>{stats.overdue_count}</strong>
                      </span>
                    )}
                  </span>
                )}
              </p>
            </div>
            <div className="d-flex gap-2">
              <ButtonGroup>
                <Button 
                  variant={viewMode === 'table' ? 'primary' : 'outline-secondary'}
                  onClick={() => {
                    setViewMode('table');
                    localStorage.setItem('assignmentViewMode', 'table');
                  }}
                  size="sm"
                >
                  <ListIcon size={16} />
                </Button>
                <Button 
                  variant={viewMode === 'grid' ? 'primary' : 'outline-secondary'}
                  onClick={() => {
                    setViewMode('grid');
                    localStorage.setItem('assignmentViewMode', 'grid');
                  }}
                  size="sm"
                >
                  <GridIcon size={16} />
                </Button>
              </ButtonGroup>
              <Button 
                variant="outline-secondary" 
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <RefreshIcon className={`me-2 ${refreshing ? 'spinning' : ''}`} size={16} />
                Refresh
              </Button>
              <Button as={Link} to="/teacher/assignments/create" variant="primary">
                <PlusIcon className="me-2" size={16} />
                New Assignment
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {/* Messages */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')} className="mb-3">
          <ExclamationTriangle className="me-2" size={16} />
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')} className="mb-3">
          <CheckCircleIcon className="me-2" size={16} />
          {success}
        </Alert>
      )}

      {/* Statistics Cards */}
      {stats && (
        <Row className="mb-4">
          <Col xl={2} lg={4} md={6} className="mb-3">
            <Card className="border-0 bg-primary bg-opacity-10">
              <Card.Body className="text-center">
                <AssignmentIcon size={24} className="text-primary mb-2" />
                <h3 className="text-primary mb-1">{stats.total_assignments}</h3>
                <small className="text-muted">Total Assignments</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xl={2} lg={4} md={6} className="mb-3">
            <Card className="border-0 bg-success bg-opacity-10">
              <Card.Body className="text-center">
                <UsersIcon size={24} className="text-success mb-2" />
                <h3 className="text-success mb-1">{stats.total_submissions || 0}</h3>
                <small className="text-muted">Total Submissions</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xl={2} lg={4} md={6} className="mb-3">
            <Card className="border-0 bg-info bg-opacity-10">
              <Card.Body className="text-center">
                <GradeIcon size={24} className="text-info mb-2" />
                <h3 className="text-info mb-1">{stats.graded_submissions || 0}</h3>
                <small className="text-muted">Graded</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xl={2} lg={4} md={6} className="mb-3">
            <Card className="border-0 bg-warning bg-opacity-10">
              <Card.Body className="text-center">
                <ClockIcon size={24} className="text-warning mb-2" />
                <h3 className="text-warning mb-1">{stats.overdue_count}</h3>
                <small className="text-muted">Overdue</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xl={2} lg={4} md={6} className="mb-3">
            <Card className="border-0 bg-danger bg-opacity-10">
              <Card.Body className="text-center">
                <AlertTriangleIcon size={24} className="text-danger mb-2" />
                <h3 className="text-danger mb-1">{stats.pending_grading_count || 0}</h3>
                <small className="text-muted">Pending Grading</small>
              </Card.Body>
            </Card>
          </Col>
          <Col xl={2} lg={4} md={6} className="mb-3">
            <Card className="border-0 bg-secondary bg-opacity-10">
              <Card.Body className="text-center">
                <BarChartIcon size={24} className="text-secondary mb-2" />
                <h3 className="text-secondary mb-1">
                  {stats.average_score || 0}%
                </h3>
                <small className="text-muted">Avg. Score</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Navigation Tabs */}
      <Card className="border-0 shadow-sm mb-4">
        <Card.Body className="p-0">
          <Tabs
            activeKey={activeTab}
            onSelect={(key) => setActiveTab(key)}
            className="px-3 pt-2"
            fill
          >
            <Tab 
              eventKey="all" 
              title={
                <div className="d-flex align-items-center justify-content-center">
                  <AssignmentIcon className="me-2" size={14} />
                  All
                  <Badge bg="primary" className="ms-2" pill>
                    {tabStats.all}
                  </Badge>
                </div>
              }
            />
            <Tab 
              eventKey="draft" 
              title={
                <div className="d-flex align-items-center justify-content-center">
                  <FileTextIcon className="me-2" size={14} />
                  Draft
                  <Badge bg="secondary" className="ms-2" pill>
                    {tabStats.draft}
                  </Badge>
                </div>
              }
            />
            <Tab 
              eventKey="published" 
              title={
                <div className="d-flex align-items-center justify-content-center">
                  <SendIcon className="me-2" size={14} />
                  Published
                  <Badge bg="success" className="ms-2" pill>
                    {tabStats.published}
                  </Badge>
                </div>
              }
            />
            <Tab 
              eventKey="graded" 
              title={
                <div className="d-flex align-items-center justify-content-center">
                  <GradeIcon className="me-2" size={14} />
                  Graded
                  <Badge bg="primary" className="ms-2" pill>
                    {tabStats.graded}
                  </Badge>
                </div>
              }
            />
            <Tab 
              eventKey="overdue" 
              title={
                <div className="d-flex align-items-center justify-content-center">
                  <ClockIcon className="me-2" size={14} />
                  Overdue
                  <Badge bg="danger" className="ms-2" pill>
                    {tabStats.overdue}
                  </Badge>
                </div>
              }
            />
            <Tab 
              eventKey="pending" 
              title={
                <div className="d-flex align-items-center justify-content-center">
                  <AlertTriangleIcon className="me-2" size={14} />
                  Pending
                  <Badge bg="warning" className="ms-2" pill>
                    {tabStats.pending}
                  </Badge>
                </div>
              }
            />
            <Tab 
              eventKey="archived" 
              title={
                <div className="d-flex align-items-center justify-content-center">
                  <ArchiveIcon className="me-2" size={14} />
                  Archived
                  <Badge bg="secondary" className="ms-2" pill>
                    {tabStats.archived}
                  </Badge>
                </div>
              }
            />
          </Tabs>
        </Card.Body>
      </Card>

      {/* Bulk Actions */}
      {renderBulkActions()}

      {/* Filters */}
      <Card className="border-0 shadow-sm mb-4">
        <Card.Body>
          <Row className="g-3">
            <Col md={3}>
              <InputGroup>
                <InputGroup.Text>
                  <SearchIcon size={14} />
                </InputGroup.Text>
                <Form.Control
                  placeholder="Search assignments..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
              </InputGroup>
            </Col>
            <Col md={2}>
              <Form.Select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <option value="">All Status</option>
                <option value={ASSIGNMENT_CONSTANTS.STATUS.DRAFT}>Draft</option>
                <option value={ASSIGNMENT_CONSTANTS.STATUS.PUBLISHED}>Published</option>
                <option value={ASSIGNMENT_CONSTANTS.STATUS.GRADED}>Graded</option>
                <option value={ASSIGNMENT_CONSTANTS.STATUS.CLOSED}>Closed</option>
              </Form.Select>
            </Col>
            <Col md={2}>
              <Form.Select
                value={filters.subject}
                onChange={(e) => handleFilterChange('subject', e.target.value)}
              >
                <option value="">All Subjects</option>
                {filteredSubjects.map(subject => (
                  <option key={subject.value} value={subject.value}>
                    {subject.label} ({subject.code})
                  </option>
                ))}
              </Form.Select>
            </Col>
            <Col md={2}>
              <Form.Select
                value={filters.classroom}
                onChange={(e) => handleFilterChange('classroom', e.target.value)}
              >
                <option value="">All Classes</option>
                {filteredClasses.map(cls => (
                  <option key={cls.value} value={cls.value}>
                    {cls.label} {cls.grade && `(Grade ${cls.grade})`}
                  </option>
                ))}
              </Form.Select>
            </Col>
            <Col md={2}>
              <Form.Select
                value={filters.assignment_type}
                onChange={(e) => handleFilterChange('assignment_type', e.target.value)}
              >
                <option value="">All Types</option>
                {assignmentTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Form.Select>
            </Col>
            <Col md={1}>
              <OverlayTrigger
                placement="bottom"
                overlay={<Tooltip>Clear all filters</Tooltip>}
              >
                <Button 
                  variant="outline-danger" 
                  className="w-100"
                  onClick={handleClearFilters}
                >
                  <FilterXIcon size={14} />
                </Button>
              </OverlayTrigger>
            </Col>
          </Row>
          
          {/* Advanced Filters */}
          <div className="mt-3">
            <Button
              variant="link"
              size="sm"
              className="text-decoration-none p-0"
              onClick={() => setExpandedAssignments(prev => 
                prev.has('filters') 
                  ? new Set([...prev].filter(x => x !== 'filters'))
                  : new Set([...prev, 'filters'])
              )}
            >
              <FilterPlusIcon size={14} className="me-1" />
              {expandedAssignments.has('filters') ? 'Hide' : 'Show'} Advanced Filters
              {expandedAssignments.has('filters') ? 
                <ChevronUpIcon size={14} className="ms-1" /> : 
                <ChevronDownIcon size={14} className="ms-1" />
              }
            </Button>
            
            {expandedAssignments.has('filters') && (
              <Row className="g-3 mt-2">
                <Col md={3}>
                  <Form.Control
                    type="date"
                    placeholder="From Date"
                    value={filters.date_from}
                    onChange={(e) => handleFilterChange('date_from', e.target.value)}
                  />
                </Col>
                <Col md={3}>
                  <Form.Control
                    type="date"
                    placeholder="To Date"
                    value={filters.date_to}
                    onChange={(e) => handleFilterChange('date_to', e.target.value)}
                  />
                </Col>
                <Col md={3}>
                  <Form.Select
                    value={filters.difficulty_level}
                    onChange={(e) => handleFilterChange('difficulty_level', e.target.value)}
                  >
                    <option value="">All Difficulties</option>
                    {difficultyLevels.map(diff => (
                      <option key={diff.value} value={diff.value}>
                        {diff.label}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                <Col md={3}>
                  <Button 
                    variant="outline-primary"
                    className="w-100"
                    onClick={() => handleSortChange('due_date')}
                  >
                    {filters.sortOrder === 'desc' ? <SortDescIcon className="me-1" size={14} /> : <SortAscIcon className="me-1" size={14} />}
                    Sort by Due Date
                  </Button>
                </Col>
              </Row>
            )}
          </div>
        </Card.Body>
      </Card>

      {/* Assignments Table */}
      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-0 py-3">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">
              {activeTab === 'all' ? 'All' : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} 
              {' '}Assignments ({pagination.total})
              {refreshing && <small className="text-muted ms-2">🔄 Updating...</small>}
            </h5>
            <div className="d-flex gap-2">
              <Dropdown>
                <Dropdown.Toggle variant="outline-primary" size="sm">
                  <DownloadIcon className="me-2" size={14} />
                  Export
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={() => assignmentsAPI.exportAssignments('csv', filters)}>
                    CSV Format
                  </Dropdown.Item>
                  <Dropdown.Item onClick={() => assignmentsAPI.exportAssignments('excel', filters)}>
                    Excel Format
                  </Dropdown.Item>
                  <Dropdown.Item onClick={() => assignmentsAPI.exportAssignments('pdf', filters)}>
                    PDF Format
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </div>
        </Card.Header>
        <Card.Body className="p-0">
          {assignments.length > 0 ? (
            <div className="table-responsive">
              <Table className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th style={{ width: '50px' }}>
                      <FormCheck 
                        checked={selectedAssignments.size === assignments.length}
                        onChange={handleSelectAll}
                        className="m-0"
                      />
                    </th>
                    <th>Assignment</th>
                    <th>Type</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th>Submissions</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {assignments.map(renderAssignmentRow)}
                </tbody>
              </Table>
            </div>
          ) : loading ? (
            <AssignmentSkeleton count={5} />
          ) : (
            <EmptyState
              title="No assignments found"
              message={filters.search || filters.status || filters.subject || filters.classroom 
                ? 'Try adjusting your search criteria or clear filters.' 
                : 'Create your first assignment to get started!'}
              icon={AssignmentIcon}
              action={
                <Button as={Link} to="/teacher/assignments/create" variant="primary">
                  <PlusIcon className="me-2" size={16} />
                  Create New Assignment
                </Button>
              }
            />
          )}
        </Card.Body>

        {/* Pagination */}
        {assignments.length > 0 && pagination.total > pagination.pageSize && (
          <Card.Footer className="bg-white border-0">
            <div className="d-flex justify-content-between align-items-center">
              <small className="text-muted">
                Showing {((pagination.current - 1) * pagination.pageSize) + 1} to{' '}
                {Math.min(pagination.current * pagination.pageSize, pagination.total)} of{' '}
                {pagination.total} assignments
              </small>
              <Pagination className="mb-0">
                <Pagination.First 
                  disabled={pagination.current === 1}
                  onClick={() => fetchAssignments(1)}
                />
                <Pagination.Prev 
                  disabled={pagination.current === 1}
                  onClick={() => fetchAssignments(pagination.current - 1)}
                />
                {Array.from({ length: Math.min(5, Math.ceil(pagination.total / pagination.pageSize)) }, (_, i) => {
                  const page = i + 1;
                  return (
                    <Pagination.Item
                      key={page}
                      active={page === pagination.current}
                      onClick={() => fetchAssignments(page)}
                    >
                      {page}
                    </Pagination.Item>
                  );
                })}
                <Pagination.Next 
                  disabled={pagination.current === Math.ceil(pagination.total / pagination.pageSize)}
                  onClick={() => fetchAssignments(pagination.current + 1)}
                />
                <Pagination.Last 
                  disabled={pagination.current === Math.ceil(pagination.total / pagination.pageSize)}
                  onClick={() => fetchAssignments(Math.ceil(pagination.total / pagination.pageSize))}
                />
              </Pagination>
            </div>
          </Card.Footer>
        )}
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal show={deleteModal.show} onHide={() => setDeleteModal({ show: false, assignment: null, bulk: false })}>
        <Modal.Header closeButton>
          <Modal.Title>
            <DeleteIcon className="me-2" size={20} />
            {deleteModal.bulk ? 'Confirm Bulk Delete' : 'Confirm Delete'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {deleteModal.bulk ? (
            <div>
              <p>Are you sure you want to delete {deleteModal.assignmentIds?.length || selectedAssignments.size} selected assignments?</p>
              <p className="text-danger">
                <strong>Warning:</strong> This action cannot be undone. All assignment data, including submissions and grades, will be permanently deleted.
              </p>
            </div>
          ) : (
            <div>
              <p>Are you sure you want to delete the assignment "{deleteModal.assignment?.title}"?</p>
              <p className="text-danger">
                <strong>Warning:</strong> This action cannot be undone. All assignment data, including submissions and grades, will be permanently deleted.
              </p>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setDeleteModal({ show: false, assignment: null, bulk: false })}
          >
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={deleteModal.bulk ? handleBulkDelete : () => handleDeleteAssignment(deleteModal.assignment.id)}
          >
            <DeleteIcon className="me-2" size={14} />
            {deleteModal.bulk ? `Delete ${deleteModal.assignmentIds?.length || selectedAssignments.size} Assignments` : 'Delete Assignment'}
          </Button>
        </Modal.Footer>
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
        .table-hover tbody tr:hover {
          background-color: rgba(var(--bs-primary-rgb), 0.05);
        }
        .assignment-details {
          transition: all 0.3s ease;
        }
        .badge.bg-homework-subtle {
          background-color: rgba(var(--bs-primary-rgb), 0.1);
          color: var(--bs-primary);
        }
        .badge.bg-project-subtle {
          background-color: rgba(var(--bs-success-rgb), 0.1);
          color: var(--bs-success);
        }
        .badge.bg-quiz-subtle {
          background-color: rgba(var(--bs-info-rgb), 0.1);
          color: var(--bs-info);
        }
        .badge.bg-exam-subtle {
          background-color: rgba(var(--bs-danger-rgb), 0.1);
          color: var(--bs-danger);
        }
      `}</style>
    </Container>
  );
};

export default TeacherAssignments;