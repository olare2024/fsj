// src/pages/Admin/AcademicManagement.jsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Container, Row, Col, Card, Table, Button, Badge, Form, 
  Nav, Spinner, Alert, Modal, Toast, ToastContainer, InputGroup,
  Tabs, Tab, Dropdown, Accordion, ProgressBar, Pagination
} from 'react-bootstrap';
import { 
  Link, 
  useNavigate,
  useSearchParams,
  generatePath 
} from 'react-router-dom';

import { 
  Download,          // ✅ Correct
  Plus,              // ✅ Correct
  Search,            // ✅ Correct
  BarChartLine,         // ✅ Correct
  Calendar,          // ✅ Correct
  FileText,          // ✅ Correct
           // ✅ Correct
  Person,              // ✅ Correct
  Eye,               // ✅ Correct
  Pencil,            // ✅ Edit icon
  Trash2,            // ✅ Correct
  ExclamationCircle, // ✅ Correct
  Book,              // ✅ Book icon
  ChevronRight,      // ✅ Chevron
  ChevronDown,       // ✅ Chevron
  ArrowLeft,         // ✅ Arrow
  ArrowRight,        // ✅ Arrow
  Filter,            // ✅ Filter
  SortDown,          // ✅ Sort
  SortUp,            // ✅ Sort
  Upload,            // ✅ Upload
  FileEarmark,       // ✅ File
  FileEarmarkArrowDown, // ✅ Download file
  People,            // ✅ People
  Gear,              // ✅ Gear
  CalendarCheck,     // ✅ Calendar check
  CalendarX,         // ✅ Calendar X
  Clock,             // ✅ Clock
  CheckCircle,       // ✅ Check circle
  XCircle,           // ✅ X circle
  InfoCircle,        // ✅ Info circle
  QuestionCircle,    // ✅ Question circle
           // ✅ Book open for overview
  FileArrowDown      // ✅ File download
} from 'react-bootstrap-icons';

import { 
  academicsAPI,

  ACADEMIC_CONSTANTS 
} from '../../services/academicAPI';
import authAPI from '../../services/authAPI';

const AcademicManagement = () => {
  // Existing state declarations
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = searchParams.get('tab') || 'overview';
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'asc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const navigate = useNavigate();

  // State for different academic entities
  const [academicYears, setAcademicYears] = useState([]);
  const [academicTerms, setAcademicTerms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [subjectAssignments, setSubjectAssignments] = useState([]);
  const [lessonPlans, setLessonPlans] = useState([]);
  const [syllabi, setSyllabi] = useState([]);
  const [academicEvents, setAcademicEvents] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [academicOverview, setAcademicOverview] = useState(null);
  const [teacherWorkload, setTeacherWorkload] = useState([]);
  const [classStudents, setClassStudents] = useState({});
  const [classSubjects, setClassSubjects] = useState({});
  const [studentEnrollments, setStudentEnrollments] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  
  // Auth state
  const [user, setUser] = useState(null);
  const [userPermissions, setUserPermissions] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isTeacher, setIsTeacher] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalType, setModalType] = useState('');
  const [bulkData, setBulkData] = useState('');
  const [importFile, setImportFile] = useState(null);
  const [detailData, setDetailData] = useState(null);

  // Form states
  const [formData, setFormData] = useState({});
  const [formErrors, setFormErrors] = useState({});

  // Expanded rows for accordion
  const [expandedRows, setExpandedRows] = useState(new Set());

  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSearchParams({ tab });
    setCurrentPage(1);
    setSearchTerm('');
    setFilterStatus('all');
  };

  // Initialize auth and permissions
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setAuthLoading(true);
        const authResponse = await authAPI.initializeAuth();
        
        if (authResponse.success && authResponse.authenticated) {
          setUser(authResponse.user);
          
          // Get user permissions
          const permResponse = await authAPI.getPermissions();
          if (permResponse.success) {
            setUserPermissions(permResponse.permissions);
          }
          
          // Set role flags
          setIsAdmin(authAPI.isAdmin());
          setIsTeacher(authAPI.isTeacher());
        } else {
          // Redirect to login if not authenticated
          navigate('/login');
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        navigate('/login');
      } finally {
        setAuthLoading(false);
      }
    };

    initializeAuth();
  }, [navigate]);

  // Check if user has permission
  const hasPermission = useCallback((permission) => {
    if (!userPermissions || userPermissions.length === 0) return false;
    
    // If user has wildcard permission
    if (userPermissions.includes('*')) return true;
    
    // Check for specific permission
    if (Array.isArray(permission)) {
      return permission.some(perm => userPermissions.includes(perm));
    }
    return userPermissions.includes(permission);
  }, [userPermissions]);

  // Enhanced fetch data with auth check
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Check permissions based on active tab
      let requiredPermission = 'academic.view';
      switch (activeTab) {
        case 'academic-years':
          requiredPermission = 'academic.years.manage';
          break;
        case 'subjects':
          requiredPermission = 'academic.subjects.manage';
          break;
        case 'classes':
          requiredPermission = 'academic.classes.manage';
          break;
        case 'enrollments':
          requiredPermission = 'academic.enrollments.manage';
          break;
        case 'overview':
          requiredPermission = 'academic.overview.view';
          break;
      }

      if (!hasPermission(requiredPermission)) {
        setError('You do not have permission to view this section');
        setLoading(false);
        return;
      }

      let response;
      
      switch (activeTab) {
        case 'academic-years':
          response = await academicAPI.getAcademicYears({ 
            status: filterStatus !== 'all' ? filterStatus : undefined,
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            // Handle paginated response
            if (response.data.results) {
              setAcademicYears(response.data.results);
            } else {
              setAcademicYears(Array.isArray(response.data) ? response.data : []);
            }
          } else {
            throw new Error(response.message || 'Failed to fetch academic years');
          }
          break;

        case 'academic-terms':
          response = await academicAPI.getAcademicTerms({ 
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            setAcademicTerms(response.data.results || response.data);
          } else {
            throw new Error(response.message || 'Failed to fetch academic terms');
          }
          break;

        case 'subjects':
          response = await academicAPI.getSubjects({ 
            is_active: filterStatus !== 'all' ? (filterStatus === 'active') : undefined,
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            setSubjects(response.data.results || response.data);
          } else {
            throw new Error(response.message || 'Failed to fetch subjects');
          }
          break;

        case 'classes':
          response = await academicAPI.getClasses({ 
            is_active: filterStatus !== 'all' ? (filterStatus === 'active') : undefined,
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            setClasses(response.data.results || response.data);
          } else {
            throw new Error(response.message || 'Failed to fetch classes');
          }
          break;

        case 'subject-assignments':
          response = await academicAPI.getSubjectAssignments({ 
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            setSubjectAssignments(response.data.results || response.data);
          } else {
            throw new Error(response.message || 'Failed to fetch subject assignments');
          }
          break;

        case 'lesson-plans':
          response = await academicAPI.getLessonPlans({ 
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            setLessonPlans(response.data.results || response.data);
          } else {
            throw new Error(response.message || 'Failed to fetch lesson plans');
          }
          break;

        case 'syllabi':
          response = await academicAPI.getSyllabi({ 
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            setSyllabi(response.data.results || response.data);
          } else {
            throw new Error(response.message || 'Failed to fetch syllabi');
          }
          break;

        case 'academic-events':
          response = await academicAPI.getAcademicEvents({ 
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            setAcademicEvents(response.data.results || response.data);
          } else {
            throw new Error(response.message || 'Failed to fetch academic events');
          }
          break;

        case 'enrollments':
        case 'student-enrollments':
          response = await academicAPI.getEnrollments({ 
            status: filterStatus !== 'all' ? filterStatus : undefined,
            search: searchTerm || undefined,
            page: currentPage,
            page_size: itemsPerPage
          });
          if (response.success) {
            const data = response.data.results || response.data;
            setEnrollments(data);
            setStudentEnrollments(data);
          } else {
            throw new Error(response.message || 'Failed to fetch enrollments');
          }
          break;

        case 'overview':
          try {
            const [dashboardRes, workloadRes] = await Promise.all([
              academicAPI.getAcademicDashboard(),
              academicAPI.getTeacherWorkloadStatistics()
            ]);
            
            if (dashboardRes.success) {
              setAcademicOverview(dashboardRes.data);
            }
            if (workloadRes.success) {
              setTeacherWorkload(workloadRes.data.workload_data || workloadRes.data);
            }
          } catch (overviewErr) {
            console.error('Overview fetch error:', overviewErr);
            // Set default values
            setAcademicOverview({
              overview: {
                academic_year: {
                  name: 'No Academic Year Set'
                },
                statistics: {
                  classes: { total: 0 },
                  enrollments: { total: 0 },
                  teachers: { total: 0 },
                  events: { total: 0 }
                }
              }
            });
          }
          break;

        default:
          break;
      }
    } catch (err) {
      setError(err.message || 'Error fetching data');
      console.error('Error fetching academic data:', err);
    } finally {
      setLoading(false);
    }
  }, [activeTab, filterStatus, searchTerm, currentPage, itemsPerPage, hasPermission]);

  useEffect(() => {
    if (!authLoading) {
      fetchData();
    }
  }, [fetchData, authLoading]);

  // Handle search
  const handleSearch = useCallback(async (value) => {
    setSearchTerm(value);
    setCurrentPage(1);
    
    if (value.length >= 2) {
      try {
        const response = await academicAPI.academicSearch({ query: value, limit: 10 });
        if (response.success) {
          setSearchResults(response.data.results || response.data);
        }
      } catch (err) {
        console.error('Search error:', err);
      }
    }
  }, []);

  // Handle sort
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Enhanced filter and sort data
  const getFilteredSortedData = useMemo(() => {
    let data = [];
    switch (activeTab) {
      case 'academic-years': data = academicYears; break;
      case 'academic-terms': data = academicTerms; break;
      case 'subjects': data = subjects; break;
      case 'classes': data = classes; break;
      case 'subject-assignments': data = subjectAssignments; break;
      case 'lesson-plans': data = lessonPlans; break;
      case 'syllabi': data = syllabi; break;
      case 'academic-events': data = academicEvents; break;
      case 'enrollments': data = enrollments; break;
      case 'student-enrollments': data = studentEnrollments; break;
      default: data = [];
    }

    // Filter by status
    if (filterStatus !== 'all') {
      data = data.filter(item => {
        if (item.status !== undefined) {
          return item.status === filterStatus;
        }
        if (item.is_active !== undefined) {
          return item.is_active === (filterStatus === 'active');
        }
        return true;
      });
    }

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      data = data.filter(item => 
        item.name?.toLowerCase().includes(searchLower) ||
        item.code?.toLowerCase().includes(searchLower) ||
        item.description?.toLowerCase().includes(searchLower) ||
        item.email?.toLowerCase().includes(searchLower) ||
        item.admission_number?.toLowerCase().includes(searchLower) ||
        item.display_name?.toLowerCase().includes(searchLower) ||
        item.title?.toLowerCase().includes(searchLower)
      );
    }

    // Sort
    if (sortConfig.key) {
      data.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        
        if (aVal === bVal) return 0;
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;
        
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return sortConfig.direction === 'asc' 
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
        }
        
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return data;
  }, [activeTab, academicYears, academicTerms, subjects, classes, subjectAssignments, 
      lessonPlans, syllabi, academicEvents, enrollments, studentEnrollments, 
      filterStatus, searchTerm, sortConfig]);

  // Paginate data
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return getFilteredSortedData.slice(startIndex, startIndex + itemsPerPage);
  }, [getFilteredSortedData, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(getFilteredSortedData.length / itemsPerPage);

  // Toggle row expansion
  const toggleRowExpansion = (id) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  // Enhanced handleCreate with auth check
  const handleCreate = async () => {
    setFormErrors({});
    
    // Check permissions
    let requiredPermission = '';
    switch (modalType) {
      case 'academic-year':
        requiredPermission = 'academic.years.manage';
        break;
      case 'subject':
        requiredPermission = 'academic.subjects.manage';
        break;
      case 'class':
        requiredPermission = 'academic.classes.manage';
        break;
    }
    
    if (!hasPermission(requiredPermission)) {
      setError('You do not have permission to perform this action');
      return;
    }

    try {
      let response;
      
      switch (modalType) {
        case 'academic-year':
          response = await academicAPI.createAcademicYear(formData);
          break;
        case 'subject':
          response = await academicAPI.createSubject(formData);
          break;
        case 'class':
          response = await academicAPI.createClass(formData);
          break;
        default:
          throw new Error('Invalid modal type');
      }

      if (response.success) {
        setSuccess(`${modalType.replace('-', ' ')} created successfully!`);
        setShowCreateModal(false);
        setFormData({});
        fetchData();
      } else {
        if (response.errors) {
          setFormErrors(response.errors);
        } else {
          setError(response.message || 'Creation failed');
        }
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    }
  };

  // Enhanced handleUpdate function
  const handleUpdate = async () => {
    setFormErrors({});
    
    let requiredPermission = '';
    switch (modalType) {
      case 'academic-year':
        requiredPermission = 'academic.years.manage';
        break;
      case 'subject':
        requiredPermission = 'academic.subjects.manage';
        break;
      case 'class':
        requiredPermission = 'academic.classes.manage';
        break;
    }
    
    if (!hasPermission(requiredPermission)) {
      setError('You do not have permission to perform this action');
      return;
    }

    try {
      let response;
      
      switch (modalType) {
        case 'academic-year':
          response = await academicAPI.updateAcademicYear(selectedItem.id, formData);
          break;
        case 'subject':
          response = await academicAPI.updateSubject(selectedItem.id, formData);
          break;
        case 'class':
          response = await academicAPI.updateClass(selectedItem.id, formData);
          break;
        default:
          throw new Error('Invalid modal type for update');
      }

      if (response.success) {
        setSuccess(`${modalType.replace('-', ' ')} updated successfully!`);
        setShowCreateModal(false);
        setFormData({});
        setSelectedItem(null);
        fetchData();
      } else {
        if (response.errors) {
          setFormErrors(response.errors);
        } else {
          setError(response.message || 'Update failed');
        }
      }
    } catch (err) {
      setError(err.message || 'An error occurred during update');
    }
  };

  // Enhanced handleDelete function
  const handleDelete = async () => {
    if (!hasPermission('academic.delete')) {
      setError('You do not have permission to delete');
      setShowDeleteModal(false);
      return;
    }

    try {
      let response;
      
      switch (modalType) {
        case 'academic-year':
          response = await academicAPI.deleteAcademicYear(selectedItem.id);
          break;
        case 'subject':
          response = await academicAPI.deleteSubject(selectedItem.id);
          break;
        case 'class':
          response = await academicAPI.deleteClass(selectedItem.id);
          break;
        case 'academic-term':
          response = await academicAPI.deleteAcademicTerm(selectedItem.id);
          break;
        case 'lesson-plan':
          response = await academicAPI.deleteLessonPlan(selectedItem.id);
          break;
        case 'syllabus':
          response = await academicAPI.deleteSyllabus(selectedItem.id);
          break;
        case 'academic-event':
          response = await academicAPI.deleteAcademicEvent(selectedItem.id);
          break;
        case 'enrollment':
          response = await academicAPI.deleteEnrollment(selectedItem.id);
          break;
        default:
          throw new Error('Invalid modal type for deletion');
      }

      if (response.success) {
        setSuccess(`${modalType.replace('-', ' ')} deleted successfully!`);
        setShowDeleteModal(false);
        setSelectedItem(null);
        fetchData();
      } else {
        setError(response.message || 'Deletion failed');
      }
    } catch (err) {
      setError(err.message || 'An error occurred during deletion');
    }
  };

  // Enhanced handleBulkEnroll with auth check
  const handleBulkEnroll = async () => {
    if (!hasPermission('academic.enrollments.manage')) {
      setError('You do not have permission to enroll students');
      return;
    }

    try {
      const studentIds = bulkData.split('\n')
        .filter(id => id.trim())
        .map(id => id.trim())
        .filter(id => id.match(/^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$/));

      if (studentIds.length === 0) {
        setError('Please enter valid student UUIDs');
        return;
      }

      const enrollmentData = {
        student_ids: studentIds,
        class_id: selectedItem?.id,
        academic_year_id: selectedItem?.academic_year?.id || academicYears.find(y => y.is_current)?.id
      };

      const response = await academicAPI.bulkEnrollStudents(enrollmentData);
      
      if (response.success) {
        setSuccess(`Successfully enrolled ${response.createdCount || 0} students. ${response.errorCount || 0} failed.`);
        setShowBulkModal(false);
        setBulkData('');
        fetchData();
      } else {
        setError(response.message || 'Bulk enrollment failed');
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    }
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    if (type === 'file') {
      setFormData(prev => ({
        ...prev,
        [name]: files[0]
      }));
    } else if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        [name]: checked
      }));
    } else if (type === 'select-multiple') {
      const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
      setFormData(prev => ({
        ...prev,
        [name]: selectedOptions
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Clear error for this field
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  // Enhanced openCreateModal with form initialization
  const openCreateModal = (type, item = null) => {
    setModalType(type);
    setSelectedItem(item);
    
    if (item) {
      // Convert dates for form inputs
      const processedData = { ...item };
      if (item.start_date) {
        processedData.start_date = item.start_date.split('T')[0];
      }
      if (item.end_date) {
        processedData.end_date = item.end_date.split('T')[0];
      }
      if (item.date_of_birth) {
        processedData.date_of_birth = item.date_of_birth.split('T')[0];
      }
      setFormData(processedData);
    } else {
      // Initialize with default values
      const defaults = {
        is_active: true,
        status: 'active',
        academic_year: academicYears.find(y => y.is_current)?.id || '',
        grade_level: '',
        capacity: 30
      };
      setFormData(defaults);
    }
    
    setFormErrors({});
    setShowCreateModal(true);
  };

  // Enhanced openDeleteModal
  const openDeleteModal = (item, type) => {
    setSelectedItem(item);
    setModalType(type);
    setShowDeleteModal(true);
  };

  // Enhanced openBulkModal
  const openBulkModal = (classItem) => {
    setSelectedItem(classItem);
    setBulkData('');
    setShowBulkModal(true);
  };

  // View item details
  const viewItemDetails = (item, type) => {
    let path = '';
    switch (type) {
      case 'class':
        path = `/admin/academic/classes/${item.id}`;
        break;
      case 'subject':
        path = `/admin/academic/subjects/${item.id}`;
        break;
      case 'academic-year':
        path = `/admin/academic/years/${item.id}`;
        break;
      case 'student':
        path = `/admin/students/${item.id}`;
        break;
      case 'enrollment':
        path = `/admin/enrollments/${item.id}`;
        break;
      default:
        return;
    }
    navigate(path);
  };

  // Export data
  const handleExport = async () => {
    if (!hasPermission('academic.export')) {
      setError('You do not have permission to export data');
      return;
    }

    try {
      const response = await academicAPI.exportEnrollmentsCSV({});
      if (response.success) {
        setSuccess('Data exported successfully!');
      }
    } catch (err) {
      setError('Export failed: ' + err.message);
    }
  };

  // Get status badge color
  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'published':
      case 'enrolled':
      case 'approved':
      case 'completed':
        return 'success';
      case 'inactive':
      case 'draft':
      case 'dropped':
        return 'secondary';
      case 'pending':
      case 'waiting':
      case 'processing':
        return 'warning';
      case 'archived':
      case 'graduated':
        return 'dark';
      case 'suspended':
      case 'rejected':
      case 'cancelled':
        return 'danger';
      default:
        return 'primary';
    }
  };

  // Get tab title with count
  const getTabTitle = () => {
    const titles = {
      'overview': 'Academic Overview',
      'academic-years': `Academic Years (${academicYears.length})`,
      'academic-terms': `Academic Terms (${academicTerms.length})`,
      'subjects': `Subjects (${subjects.length})`,
      'classes': `Classes (${classes.length})`,
      'subject-assignments': `Subject Assignments (${subjectAssignments.length})`,
      'lesson-plans': `Lesson Plans (${lessonPlans.length})`,
      'syllabi': `Syllabi (${syllabi.length})`,
      'academic-events': `Academic Events (${academicEvents.length})`,
      'enrollments': `Enrollments (${enrollments.length})`,
      'student-enrollments': `Student Enrollments (${studentEnrollments.length})`,
    };
    return titles[activeTab] || 'Academic Management';
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  // Get class students
  const fetchClassStudents = async (classId) => {
    try {
      const response = await academicAPI.getClassStudents(classId);
      if (response.success) {
        setClassStudents(prev => ({
          ...prev,
          [classId]: response.data.results || response.data
        }));
      }
    } catch (err) {
      console.error('Error fetching class students:', err);
    }
  };

  // Get class subjects
  const fetchClassSubjects = async (classId) => {
    try {
      const response = await academicAPI.getClassSubjects(classId);
      if (response.success) {
        setClassSubjects(prev => ({
          ...prev,
          [classId]: response.data.results || response.data
        }));
      }
    } catch (err) {
      console.error('Error fetching class subjects:', err);
    }
  };

  // Get full class details
  const viewClassDetails = async (classId) => {
    try {
      const response = await academicAPI.getClass(classId);
      if (response.success) {
        setDetailData(response.data);
        setShowDetailModal(true);
      }
    } catch (err) {
      console.error('Error fetching class details:', err);
      setError('Failed to load class details');
    }
  };

  // Render loading state with auth check
  if (authLoading) {
    return (
      <Container fluid className="mt-4">
        <Row className="justify-content-center">
          <Col md={6} className="text-center">
            <Spinner animation="border" variant="primary" />
            <p className="mt-2">Checking authentication...</p>
          </Col>
        </Row>
      </Container>
    );
  }

  if (!user) {
    return (
      <Container fluid className="mt-4">
        <Alert variant="danger">
          <ExclamationCircle className="me-2" />
          You must be logged in to access this page.
        </Alert>
      </Container>
    );
  }

  // Check overall permission
  if (!hasPermission(['academic.view', 'academic.manage'])) {
    return (
      <Container fluid className="mt-4">
        <Alert variant="warning">
          <ExclamationCircle className="me-2" />
          You do not have permission to access academic management.
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Toast Notifications */}
      <ToastContainer position="top-end" className="p-3">
        {success && (
          <Toast onClose={() => setSuccess(null)} show={!!success} delay={3000} autohide bg="success">
            <Toast.Header>
              <strong className="me-auto">Success</strong>
            </Toast.Header>
            <Toast.Body className="text-white">{success}</Toast.Body>
          </Toast>
        )}
        {error && (
          <Toast onClose={() => setError(null)} show={!!error} delay={5000} autohide bg="danger">
            <Toast.Header>
              <strong className="me-auto">Error</strong>
            </Toast.Header>
            <Toast.Body className="text-white">{error}</Toast.Body>
          </Toast>
        )}
      </ToastContainer>

      {/* Header with Person Info */}
      <Row className="mb-4 align-items-center">
        <Col>
          <div className="d-flex align-items-center">
            <div>
              <h1 className="mb-1">{getTabTitle()}</h1>
              <p className="text-muted mb-0">
                Manage academic programs, courses, departments, and curriculum
                {academicOverview?.overview?.academic_year && activeTab === 'overview' && (
                  <span className="ms-2">
                    <Badge bg="info" className="ms-2">
                      {academicOverview.overview.academic_year.name}
                    </Badge>
                    <Badge bg="secondary" className="ms-2">
                      {academicOverview.overview.statistics?.classes?.total || 0} Classes
                    </Badge>
                    <Badge bg="success" className="ms-2">
                      {user?.role || 'Person'}
                    </Badge>
                  </span>
                )}
              </p>
            </div>
          </div>
        </Col>
        <Col xs="auto">
          <div className="d-flex gap-2">
            <Button 
              variant="outline-primary" 
              onClick={() => fetchData()}
              disabled={loading}
            >
              {loading ? <Spinner size="sm" /> : <><span className="me-1">↻</span> Refresh</>}
            </Button>
            {activeTab !== 'overview' && hasPermission('academic.create') && (
              <Button 
                variant="success" 
                onClick={() => openCreateModal(activeTab)}
              >
                <Plus size={16} className="me-1" />
                Add New
              </Button>
            )}
            {hasPermission('academic.export') && (
              <Dropdown>
                <Dropdown.Toggle variant="outline-secondary">
                  <FileArrowDown size={16} className="me-1" />
                  Export
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={handleExport}>Export Enrollments CSV</Dropdown.Item>
                  <Dropdown.Item onClick={() => setShowImportModal(true)}>Import Data</Dropdown.Item>
                  {hasPermission('academic.templates') && (
                    <Dropdown.Item>
                      Download Template
                    </Dropdown.Item>
                  )}
                </Dropdown.Menu>
              </Dropdown>
            )}
          </div>
        </Col>
      </Row>

      {/* Search and Filter Bar */}
      {activeTab !== 'overview' && (
        <Card className="mb-4">
          <Card.Body>
            <Row className="align-items-center">
              <Col md={4}>
                <InputGroup>
                  <InputGroup.Text>
                    <Search size={16} />
                  </InputGroup.Text>
                  <Form.Control
                    placeholder={`Search ${activeTab.replace('-', ' ')}...`}
                    value={searchTerm}
                    onChange={(e) => handleSearch(e.target.value)}
                  />
                </InputGroup>
              </Col>
              <Col md={3}>
                <Form.Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  {activeTab === 'enrollments' && (
                    <>
                      <option value="enrolled">Enrolled</option>
                      <option value="dropped">Dropped</option>
                      <option value="completed">Completed</option>
                    </>
                  )}
                </Form.Select>
              </Col>
              <Col md={5} className="text-end">
                <span className="text-muted me-3">
                  Showing {paginatedData.length} of {getFilteredSortedData.length} items
                </span>
                <Button 
                  variant="outline-secondary" 
                  size="sm"
                  onClick={() => setExpandedRows(new Set())}
                >
                  Collapse All
                </Button>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}

      {/* Navigation Tabs */}
      <Card className="mb-4">
        <Card.Body className="p-0">
          <Tabs
            activeKey={activeTab}
            onSelect={handleTabChange}
            className="border-bottom-0"
          >
            {/* Overview Tab */}
            <Tab eventKey="overview" title={<span><BarChartLine size={16} className="me-1" /> Overview</span>}>
              <div className="p-3">
                {loading ? (
                  <div className="text-center py-5">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-2">Loading overview data...</p>
                  </div>
                ) : academicOverview ? (
                  <Row>
                    {/* Academic Year Card */}
                    <Col lg={3} md={6} className="mb-4">
                      <Card className="border-primary border-2">
                        <Card.Body>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h6 className="text-muted mb-1">Current Academic Year</h6>
                              <h4 className="mb-0">{academicOverview.overview?.academic_year?.name || 'Not Set'}</h4>
                              <small className="text-muted">
                                {academicOverview.overview?.academic_year?.progress || 0}% Complete
                              </small>
                            </div>
                            <div className="avatar-sm">
                              <span className="avatar-title bg-primary rounded-circle">
                                <Calendar size={24} />
                              </span>
                            </div>
                          </div>
                          {academicOverview.overview?.academic_year?.progress && (
                            <ProgressBar 
                              now={academicOverview.overview.academic_year.progress} 
                              className="mt-2" 
                              variant="primary"
                              animated
                            />
                          )}
                        </Card.Body>
                      </Card>
                    </Col>

                    {/* Classes Card */}
                    <Col lg={3} md={6} className="mb-4">
                      <Card className="border-success border-2">
                        <Card.Body>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h6 className="text-muted mb-1">Total Classes</h6>
                              <h2 className="mb-0">{academicOverview.overview?.statistics?.classes?.total || 0}</h2>
                              <small className="text-muted">
                                {academicOverview.overview?.statistics?.classes?.active || 0} Active
                              </small>
                            </div>
                            <div className="avatar-sm">
                              <span className="avatar-title bg-success rounded-circle">
                                <Book size={24} />
                              </span>
                            </div>
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>

                    {/* Students Card */}
                    <Col lg={3} md={6} className="mb-4">
                      <Card className="border-info border-2">
                        <Card.Body>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h6 className="text-muted mb-1">Total Students</h6>
                              <h2 className="mb-0">{academicOverview.overview?.statistics?.enrollments?.total || 0}</h2>
                              <small className="text-muted">
                                {academicOverview.overview?.statistics?.enrollments?.new_this_month || 0} New This Month
                              </small>
                            </div>
                            <div className="avatar-sm">
                              <span className="avatar-title bg-info rounded-circle">
                                <Users size={24} />
                              </span>
                            </div>
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>

                    {/* Teachers Card */}
                    <Col lg={3} md={6} className="mb-4">
                      <Card className="border-warning border-2">
                        <Card.Body>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h6 className="text-muted mb-1">Total Teachers</h6>
                              <h2 className="mb-0">{academicOverview.overview?.statistics?.teachers?.total || 0}</h2>
                              <small className="text-muted">
                                {academicOverview.overview?.statistics?.teachers?.with_assignments || 0} Assigned
                              </small>
                            </div>
                            <div className="avatar-sm">
                              <span className="avatar-title bg-warning rounded-circle">
                                <Person size={24} />
                              </span>
                            </div>
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>

                    {/* Recent Activities */}
                    <Col lg={6} className="mb-4">
                      <Card>
                        <Card.Header>
                          <h5 className="mb-0">Recent Activities</h5>
                        </Card.Header>
                        <Card.Body>
                          {academicOverview.recent_activities?.enrollments?.length > 0 ? (
                            <ListGroup variant="flush">
                              {academicOverview.recent_activities.enrollments.slice(0, 5).map((enrollment, index) => (
                                <ListGroup.Item key={index} className="border-0">
                                  <div className="d-flex justify-content-between align-items-center">
                                    <div>
                                      <strong>{enrollment.student_name}</strong>
                                      <div className="text-muted small">
                                        Enrolled in {enrollment.class_name}
                                      </div>
                                    </div>
                                    <div className="text-end">
                                      <div className="text-muted small">
                                        {formatDate(enrollment.enrollment_date)}
                                      </div>
                                    </div>
                                  </div>
                                </ListGroup.Item>
                              ))}
                            </ListGroup>
                          ) : (
                            <Alert variant="info">
                              No recent activities found.
                            </Alert>
                          )}
                        </Card.Body>
                      </Card>
                    </Col>

                    {/* Teacher Workload */}
                    <Col lg={6} className="mb-4">
                      <Card>
                        <Card.Header>
                          <h5 className="mb-0">Teacher Workload</h5>
                        </Card.Header>
                        <Card.Body>
                          {teacherWorkload.length > 0 ? (
                            teacherWorkload.slice(0, 5).map((teacher, index) => (
                              <div key={index} className="mb-3">
                                <div className="d-flex justify-content-between align-items-center mb-1">
                                  <span>{teacher.teacher_name}</span>
                                  <span className="fw-bold">{teacher.workload_percentage}%</span>
                                </div>
                                <ProgressBar 
                                  now={teacher.workload_percentage} 
                                  variant={
                                    teacher.workload_percentage > 90 ? 'danger' :
                                    teacher.workload_percentage > 70 ? 'warning' : 'success'
                                  }
                                  animated={teacher.workload_percentage > 90}
                                />
                              </div>
                            ))
                          ) : (
                            <Alert variant="info">
                              No teacher workload data available.
                            </Alert>
                          )}
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>
                ) : (
                  <Alert variant="info">
                    No overview data available.
                  </Alert>
                )}
              </div>
            </Tab>

            {/* Academic Years Tab */}
            <Tab eventKey="academic-years" title={<span><Calendar size={16} className="me-1" /> Academic Years</span>}>
              <div className="p-3">
                {!hasPermission('academic.years.view') ? (
                  <Alert variant="warning">
                    You do not have permission to view academic years.
                  </Alert>
                ) : (
                  <>
                    {loading ? (
                      <div className="text-center py-5">
                        <Spinner animation="border" variant="primary" />
                        <p className="mt-2">Loading academic years...</p>
                      </div>
                    ) : (
                      <>
                        <Table hover responsive>
                          <thead>
                            <tr>
                              <th>Year Name</th>
                              <th>Start Date</th>
                              <th>End Date</th>
                              <th>Status</th>
                              <th>Classes</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {paginatedData.map(year => (
                              <tr key={year.id}>
                                <td>
                                  <strong>{year.name}</strong>
                                  {year.is_current && (
                                    <Badge bg="success" className="ms-2">Current</Badge>
                                  )}
                                </td>
                                <td>{formatDate(year.start_date)}</td>
                                <td>{formatDate(year.end_date)}</td>
                                <td>
                                  <Badge bg={getStatusBadge(year.status)}>
                                    {year.is_active ? 'Active' : 'Inactive'}
                                  </Badge>
                                </td>
                                <td>
                                  <Badge bg="info">{year.classes_count || 0}</Badge>
                                </td>
                                <td>
                                  <Button 
                                    size="sm" 
                                    variant="outline-primary" 
                                    className="me-2"
                                    onClick={() => viewItemDetails(year, 'academic-year')}
                                    title="View Details"
                                  >
                                    <Eye size={14} />
                                  </Button>
                                  {hasPermission('academic.years.manage') && (
                                    <>
                                      <Button 
                                        size="sm" 
                                        variant="outline-warning" 
                                        className="me-2"
                                        onClick={() => openCreateModal('academic-year', year)}
                                        title="Edit"
                                      >
                                        <Pencil size={14} />
                                      </Button>
                                      <Button 
                                        size="sm" 
                                        variant="outline-danger"
                                        onClick={() => openDeleteModal(year, 'academic-year')}
                                        title="Delete"
                                      >
                                        <Trash2 size={14} />
                                      </Button>
                                    </>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                        
                        {totalPages > 1 && (
                          <Pagination className="justify-content-center mt-3">
                            <Pagination.First onClick={() => setCurrentPage(1)} disabled={currentPage === 1} />
                            <Pagination.Prev onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} />
                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                              let pageNum;
                              if (totalPages <= 5) {
                                pageNum = i + 1;
                              } else if (currentPage <= 3) {
                                pageNum = i + 1;
                              } else if (currentPage >= totalPages - 2) {
                                pageNum = totalPages - 4 + i;
                              } else {
                                pageNum = currentPage - 2 + i;
                              }
                              
                              return (
                                <Pagination.Item 
                                  key={pageNum} 
                                  active={pageNum === currentPage}
                                  onClick={() => setCurrentPage(pageNum)}
                                >
                                  {pageNum}
                                </Pagination.Item>
                              );
                            })}
                            <Pagination.Next onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} />
                            <Pagination.Last onClick={() => setCurrentPage(totalPages)} disabled={currentPage === totalPages} />
                          </Pagination>
                        )}
                      </>
                    )}
                  </>
                )}
              </div>
            </Tab>

            {/* Subjects Tab */}
            <Tab eventKey="subjects" title={<span><FileText size={16} className="me-1" /> Subjects</span>}>
              <div className="p-3">
                {!hasPermission('academic.subjects.view') ? (
                  <Alert variant="warning">
                    You do not have permission to view subjects.
                  </Alert>
                ) : (
                  <>
                    {loading ? (
                      <div className="text-center py-5">
                        <Spinner animation="border" variant="primary" />
                        <p className="mt-2">Loading subjects...</p>
                      </div>
                    ) : (
                      <>
                        <Table hover responsive>
                          <thead>
                            <tr>
                              <th>Subject Name</th>
                              <th>Code</th>
                              <th>Category</th>
                              <th>Teacher</th>
                              <th>Status</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {paginatedData.map(subject => (
                              <tr key={subject.id}>
                                <td>
                                  <strong>{subject.name}</strong>
                                  {subject.description && (
                                    <small className="d-block text-muted">
                                      {subject.description.substring(0, 60)}...
                                    </small>
                                  )}
                                </td>
                                <td>
                                  <Badge bg="info">{subject.code}</Badge>
                                </td>
                                <td>
                                  <Badge bg="secondary">{subject.category || 'N/A'}</Badge>
                                </td>
                                <td>{subject.teacher_name || 'Not Assigned'}</td>
                                <td>
                                  <Badge bg={subject.is_active ? 'success' : 'secondary'}>
                                    {subject.is_active ? 'Active' : 'Inactive'}
                                  </Badge>
                                </td>
                                <td>
                                  <Button 
                                    size="sm" 
                                    variant="outline-primary" 
                                    className="me-2"
                                    onClick={() => viewItemDetails(subject, 'subject')}
                                    title="View Details"
                                  >
                                    <Eye size={14} />
                                  </Button>
                                  {hasPermission('academic.subjects.manage') && (
                                    <>
                                      <Button 
                                        size="sm" 
                                        variant="outline-warning" 
                                        className="me-2"
                                        onClick={() => openCreateModal('subject', subject)}
                                        title="Edit"
                                      >
                                        <Pencil size={14} />
                                      </Button>
                                      <Button 
                                        size="sm" 
                                        variant="outline-danger"
                                        onClick={() => openDeleteModal(subject, 'subject')}
                                        title="Delete"
                                      >
                                        <Trash2 size={14} />
                                      </Button>
                                    </>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                        
                        {/* Pagination similar to academic years */}
                      </>
                    )}
                  </>
                )}
              </div>
            </Tab>

            {/* Classes Tab */}
            <Tab eventKey="classes" title={<span><Users size={16} className="me-1" /> Classes</span>}>
              <div className="p-3">
                {!hasPermission('academic.classes.view') ? (
                  <Alert variant="warning">
                    You do not have permission to view classes.
                  </Alert>
                ) : (
                  <>
                    {loading ? (
                      <div className="text-center py-5">
                        <Spinner animation="border" variant="primary" />
                        <p className="mt-2">Loading classes...</p>
                      </div>
                    ) : (
                      <>
                        <Table hover responsive>
                          <thead>
                            <tr>
                              <th>Class Name</th>
                              <th>Academic Year</th>
                              <th>Grade Level</th>
                              <th>Students</th>
                              <th>Teacher</th>
                              <th>Status</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {paginatedData.map(classItem => (
                              <tr key={classItem.id}>
                                <td>
                                  <strong>{classItem.name}</strong>
                                  <small className="d-block text-muted">
                                    Room: {classItem.room_number || 'N/A'}
                                  </small>
                                </td>
                                <td>{classItem.academic_year_name || 'N/A'}</td>
                                <td>
                                  <Badge bg="primary">{classItem.grade_level}</Badge>
                                </td>
                                <td>
                                  <Badge bg="info">{classItem.student_count || 0}</Badge>
                                </td>
                                <td>{classItem.class_teacher_name || 'Not Assigned'}</td>
                                <td>
                                  <Badge bg={classItem.is_active ? 'success' : 'secondary'}>
                                    {classItem.is_active ? 'Active' : 'Inactive'}
                                  </Badge>
                                </td>
                                <td>
                                  <Button 
                                    size="sm" 
                                    variant="outline-primary" 
                                    className="me-2"
                                    onClick={() => viewClassDetails(classItem.id)}
                                    title="View Details"
                                  >
                                    <Eye size={14} />
                                  </Button>
                                  {hasPermission('academic.classes.manage') && (
                                    <>
                                      <Button 
                                        size="sm" 
                                        variant="outline-warning" 
                                        className="me-2"
                                        onClick={() => openCreateModal('class', classItem)}
                                        title="Edit"
                                      >
                                        <Pencil size={14} />
                                      </Button>
                                      <Button 
                                        size="sm" 
                                        variant="outline-success" 
                                        className="me-2"
                                        onClick={() => openBulkModal(classItem)}
                                        title="Bulk Enroll"
                                      >
                                        <Users size={14} />
                                      </Button>
                                    </>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                      </>
                    )}
                  </>
                )}
              </div>
            </Tab>

            {/* Enrollments Tab */}
            <Tab eventKey="enrollments" title={<span><Person size={16} className="me-1" /> Enrollments</span>}>
              <div className="p-3">
                {!hasPermission('academic.enrollments.view') ? (
                  <Alert variant="warning">
                    You do not have permission to view enrollments.
                  </Alert>
                ) : (
                  <>
                    {loading ? (
                      <div className="text-center py-5">
                        <Spinner animation="border" variant="primary" />
                        <p className="mt-2">Loading enrollments...</p>
                      </div>
                    ) : (
                      <>
                        <Table hover responsive>
                          <thead>
                            <tr>
                              <th>Student</th>
                              <th>Class</th>
                              <th>Academic Year</th>
                              <th>Enrollment Date</th>
                              <th>Status</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {paginatedData.map(enrollment => (
                              <tr key={enrollment.id}>
                                <td>
                                  <strong>{enrollment.student_name || enrollment.student?.full_name}</strong>
                                  <small className="d-block text-muted">
                                    {enrollment.enrollment_number || ''}
                                  </small>
                                </td>
                                <td>{enrollment.class_name || enrollment.class_enrolled?.display_name}</td>
                                <td>{enrollment.academic_year_name || enrollment.academic_year?.name}</td>
                                <td>{formatDate(enrollment.enrollment_date)}</td>
                                <td>
                                  <Badge bg={getStatusBadge(enrollment.status)}>
                                    {enrollment.status}
                                  </Badge>
                                </td>
                                <td>
                                  <Button 
                                    size="sm" 
                                    variant="outline-primary" 
                                    className="me-2"
                                    onClick={() => viewItemDetails(enrollment, 'enrollment')}
                                    title="View Details"
                                  >
                                    <Eye size={14} />
                                  </Button>
                                  {hasPermission('academic.enrollments.manage') && (
                                    <Button 
                                      size="sm" 
                                      variant="outline-danger"
                                      onClick={() => openDeleteModal(enrollment, 'enrollment')}
                                      title="Delete"
                                    >
                                      <Trash2 size={14} />
                                    </Button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                      </>
                    )}
                  </>
                )}
              </div>
            </Tab>

            {/* Add more tabs as needed */}
          </Tabs>
        </Card.Body>
      </Card>

      {/* All modals remain similar but with enhanced permission checks */}
      {/* Create/Edit Modal */}
      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedItem ? 'Edit' : 'Create'} {modalType.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            {/* Render form based on modalType */}
            {modalType === 'academic-year' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Year Name *</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name || ''}
                    onChange={handleInputChange}
                    isInvalid={!!formErrors.name}
                    placeholder="e.g., 2024-2025"
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.name}
                  </Form.Control.Feedback>
                </Form.Group>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Start Date *</Form.Label>
                      <Form.Control
                        type="date"
                        name="start_date"
                        value={formData.start_date || ''}
                        onChange={handleInputChange}
                        isInvalid={!!formErrors.start_date}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>End Date *</Form.Label>
                      <Form.Control
                        type="date"
                        name="end_date"
                        value={formData.end_date || ''}
                        onChange={handleInputChange}
                        isInvalid={!!formErrors.end_date}
                      />
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group className="mb-3">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="description"
                    value={formData.description || ''}
                    onChange={handleInputChange}
                    placeholder="Optional description"
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    label="Set as current academic year"
                    name="is_current"
                    checked={formData.is_current || false}
                    onChange={handleInputChange}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    label="Active"
                    name="is_active"
                    checked={formData.is_active !== false}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </>
            )}

            {/* Add forms for other modal types */}
            {modalType === 'subject' && (
              <>
                <Row>
                  <Col md={8}>
                    <Form.Group className="mb-3">
                      <Form.Label>Subject Name *</Form.Label>
                      <Form.Control
                        type="text"
                        name="name"
                        value={formData.name || ''}
                        onChange={handleInputChange}
                        isInvalid={!!formErrors.name}
                        placeholder="e.g., Mathematics, English"
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Subject Code *</Form.Label>
                      <Form.Control
                        type="text"
                        name="code"
                        value={formData.code || ''}
                        onChange={handleInputChange}
                        isInvalid={!!formErrors.code}
                        placeholder="e.g., MATH101"
                      />
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    name="category"
                    value={formData.category || ''}
                    onChange={handleInputChange}
                  >
                    <option value="">Select Category</option>
                    <option value="core">Core</option>
                    <option value="elective">Elective</option>
                    <option value="language">Language</option>
                    <option value="science">Science</option>
                    <option value="math">Mathematics</option>
                    <option value="humanities">Humanities</option>
                  </Form.Select>
                </Form.Group>
              </>
            )}

            {modalType === 'class' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Class Name *</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name || ''}
                    onChange={handleInputChange}
                    placeholder="e.g., Form 1A, Grade 5B"
                  />
                </Form.Group>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Grade Level</Form.Label>
                      <Form.Select
                        name="grade_level"
                        value={formData.grade_level || ''}
                        onChange={handleInputChange}
                      >
                        <option value="">Select Grade Level</option>
                        <option value="grade_1">Grade 1</option>
                        <option value="grade_2">Grade 2</option>
                        <option value="grade_3">Grade 3</option>
                        <option value="grade_4">Grade 4</option>
                        <option value="grade_5">Grade 5</option>
                        <option value="grade_6">Grade 6</option>
                        <option value="grade_7">Grade 7</option>
                        <option value="grade_8">Grade 8</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Academic Year</Form.Label>
                      <Form.Select
                        name="academic_year"
                        value={formData.academic_year || ''}
                        onChange={handleInputChange}
                      >
                        <option value="">Select Academic Year</option>
                        {academicYears.map(year => (
                          <option key={year.id} value={year.id}>
                            {year.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
              </>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
            Cancel
          </Button>
          <Button 
            variant={selectedItem ? 'warning' : 'primary'} 
            onClick={selectedItem ? handleUpdate : handleCreate}
            disabled={!hasPermission(`academic.${modalType.replace('-', '.')}.manage`)}
          >
            {selectedItem ? 'Update' : 'Create'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="danger" className="d-flex align-items-center">
            <ExclamationCircle size={24} className="me-2" />
            <span>
              Are you sure you want to delete <strong>{selectedItem?.name}</strong>?
            </span>
          </Alert>
          <p className="text-muted mt-2">
            This action cannot be undone. All associated data will be permanently removed.
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Bulk Enrollment Modal */}
      <Modal show={showBulkModal} onHide={() => setShowBulkModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Bulk Enroll Students</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="info">
            <strong>Class:</strong> {selectedItem?.name}
            <br />
            <strong>Academic Year:</strong> {selectedItem?.academic_year_name}
          </Alert>
          <Form.Group className="mb-3">
            <Form.Label>
              Enter Student IDs (UUIDs, one per line)
            </Form.Label>
            <Form.Control
              as="textarea"
              rows={10}
              value={bulkData}
              onChange={(e) => setBulkData(e.target.value)}
              placeholder="Enter student UUIDs, one per line:
550e8400-e29b-41d4-a716-446655440000
6ba7b810-9dad-11d1-80b4-00c04fd430c8
..."
            />
            <Form.Text className="text-muted">
              Enter student UUIDs only. Each UUID should be on a new line.
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowBulkModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleBulkEnroll}>
            Enroll Students
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Import Modal */}
      <Modal show={showImportModal} onHide={() => setShowImportModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Import Academic Data</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Select File</Form.Label>
            <Form.Control
              type="file"
              accept=".csv,.json,.xlsx"
              onChange={(e) => setImportFile(e.target.files[0])}
            />
            <Form.Text className="text-muted">
              Supported formats: CSV, JSON, Excel
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowImportModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={() => {
            // Handle import logic here
            setSuccess('Import functionality to be implemented');
            setShowImportModal(false);
          }}>
            Import
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Class Details Modal */}
      <Modal show={showDetailModal} onHide={() => setShowDetailModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>Class Details - {detailData?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {detailData ? (
            <Row>
              <Col md={6}>
                <h5>Basic Information</h5>
                <p><strong>Grade Level:</strong> {detailData.grade_level}</p>
                <p><strong>Room:</strong> {detailData.room_number || 'N/A'}</p>
                <p><strong>Capacity:</strong> {detailData.capacity}</p>
                <p><strong>Class Teacher:</strong> {detailData.class_teacher_name || 'N/A'}</p>
                <p><strong>Academic Year:</strong> {detailData.academic_year_name}</p>
              </Col>
              <Col md={6}>
                <h5>Statistics</h5>
                <p><strong>Total Students:</strong> {detailData.student_count || 0}</p>
                <p><strong>Subjects:</strong> {detailData.subject_count || 0}</p>
                <p><strong>Status:</strong> 
                  <Badge bg={detailData.is_active ? 'success' : 'secondary'} className="ms-2">
                    {detailData.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </p>
              </Col>
            </Row>
          ) : (
            <div className="text-center py-3">
              <Spinner animation="border" />
              <p className="mt-2">Loading details...</p>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
            Close
          </Button>
          {detailData && hasPermission('academic.classes.manage') && (
            <Button variant="primary" onClick={() => {
              setShowDetailModal(false);
              openCreateModal('class', detailData);
            }}>
              Edit Class
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default AcademicManagement;