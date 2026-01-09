import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { studentsAPI } from '../../services/studentAPI';
import { academicAPI } from '../../services/academicAPI';
import { assignmentsAPI } from '../../services/assignmentsAPI';
import { attendanceAPI } from '../../services/attendanceAPI';
import { subjectsAPI } from '../../services/subjectsAPI';
import { financeAPI } from '../../services/financeAPI';
import { 
  Calendar, Clock, Book, FileText, Calculator, 
  Search, Award, Briefcase, People, GraphUp,
  Clipboard, Chat, Headphones, CameraVideo, Download,
  CheckCircle, ClockHistory, ExclamationTriangle,
  Star, ArrowUpRight, Bookmark, Bell, CreditCard,
  Filter, SortDown, Grid, List, Eye, Cash
} from 'react-bootstrap-icons';

function StudentResources() {
  const { currentUser } = useAuth();
  const [activeCategory, setActiveCategory] = useState('study');
  const [studentData, setStudentData] = useState({
    active_classes: 0,
    pending_assignments: 0,
    overall_average: '0%',
    upcoming_exams: 0,
    upcoming_events: 0
  });
  const [financeData, setFinanceData] = useState({
    total_balance: 0,
    pending_payments: 0,
    paid_amount: 0,
    due_date: null
  });
  const [loading, setLoading] = useState(true);
  const [upcomingDeadlines, setUpcomingDeadlines] = useState([]);
  const [recentResources, setRecentResources] = useState([]);
  const [favoriteResources, setFavoriteResources] = useState([]);
  const [resources, setResources] = useState({
    study: [],
    tools: [],
    college: [],
    finance: []
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('popular');

  useEffect(() => {
    fetchStudentData();
    fetchFinanceData();
    fetchUpcomingDeadlines();
    fetchRecentResources();
    fetchFavoriteResources();
    fetchResources();
  }, []);

  const fetchStudentData = async () => {
    try {
      setLoading(true);
      const response = await studentsAPI.getDashboard();
      if (response.success) {
        setStudentData(response.data);
      } else {
        console.error('Error fetching student data:', response.error);
      }
    } catch (error) {
      console.error('Error fetching student data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFinanceData = async () => {
    try {
      // Get student fees information
      const feesResponse = await studentsAPI.getFees();
      if (feesResponse.success) {
        const feesData = feesResponse.data;
        setFinanceData({
          total_balance: feesData.total_balance || 0,
          pending_payments: feesData.pending_payments || 0,
          paid_amount: feesData.paid_amount || 0,
          due_date: feesData.next_due_date || null,
          outstanding_invoices: feesData.outstanding_invoices || 0
        });
      }

      // Get receipts for the student
      const receiptsResponse = await financeAPI.getReceipts({ 
        student_id: currentUser?.id 
      });
      if (receiptsResponse.success) {
        // Store receipts data for display
        setFinanceData(prev => ({
          ...prev,
          recent_receipts: receiptsResponse.data.receipts?.slice(0, 3) || []
        }));
      }
    } catch (error) {
      console.error('Error fetching finance data:', error);
    }
  };

  const fetchUpcomingDeadlines = async () => {
    try {
      const response = await assignmentsAPI.getStudentAssignments(currentUser?.id);
      if (response.success) {
        const deadlines = response.data.assignments?.map(assignment => ({
          id: assignment.id,
          title: assignment.title,
          subject: assignment.subject?.name || 'General',
          type: assignment.type || 'Assignment',
          dueDate: assignment.due_date,
          dueTime: assignment.due_time || '23:59',
          priority: assignment.priority || 'medium',
          description: assignment.description,
          submitted: assignment.submission_status === 'submitted'
        })) || [];
        setUpcomingDeadlines(deadlines);
      }
    } catch (error) {
      console.error('Error fetching deadlines:', error);
    }
  };

  const fetchRecentResources = async () => {
    try {
      const response = await academicAPI.getSubjects();
      if (response.success) {
        const recent = response.data.subjects?.slice(0, 5).map(subject => ({
          id: subject.id,
          title: `New material for ${subject.name}`,
          timestamp: new Date().toLocaleDateString(),
          type: 'subject_update'
        })) || [];
        setRecentResources(recent);
      }
    } catch (error) {
      console.error('Error fetching recent resources:', error);
    }
  };

  const fetchFavoriteResources = async () => {
    try {
      // Mock favorites data - replace with actual API call
      const mockFavorites = [
        { id: 1, resource_id: 1, title: 'Study Guides Library', type: 'study' },
        { id: 2, resource_id: 7, title: 'Digital Notebook', type: 'tool' }
      ];
      setFavoriteResources(mockFavorites);
    } catch (error) {
      console.error('Error fetching favorite resources:', error);
    }
  };

  const fetchResources = async () => {
    try {
      // Transform backend data to match frontend structure
      const transformedResources = {
        study: [
          {
            id: 1,
            title: 'Study Guides Library',
            description: 'Comprehensive study guides for all subjects',
            icon: Book,
            color: 'primary',
            link: '/library/study-guides',
            stats: '150+ Guides',
            popularity: 95,
            lastUpdated: '2024-01-15',
            tags: ['guides', 'subjects', 'exams']
          },
          {
            id: 2,
            title: 'Homework Help',
            description: 'Get help with assignments from tutors',
            icon: Clipboard,
            color: 'success',
            link: '/homework-help',
            stats: '24/7 Support',
            popularity: 88,
            lastUpdated: '2024-01-10',
            tags: ['tutoring', 'homework', 'support']
          }
        ],
        tools: [
          {
            id: 7,
            title: 'Digital Notebook',
            description: 'Advanced online note-taking',
            icon: Book,
            color: 'primary',
            link: '/tools/notebook',
            stats: 'Sync Across Devices',
            popularity: 91,
            lastUpdated: '2024-01-11',
            tags: ['notes', 'organization', 'sync']
          },
          {
            id: 8,
            title: 'Assignment Tracker',
            description: 'Track deadlines and submissions',
            icon: Calendar,
            color: 'success',
            link: '/tools/assignments',
            stats: 'Real-time Updates',
            popularity: 87,
            lastUpdated: '2024-01-09',
            tags: ['tracking', 'deadlines', 'reminders']
          }
        ],
        college: [
          {
            id: 13,
            title: 'College Search',
            description: 'Explore universities and programs',
            icon: Briefcase,
            color: 'primary',
            link: '/college/search',
            stats: '5000+ Colleges',
            popularity: 83,
            lastUpdated: '2024-01-03',
            tags: ['colleges', 'search', 'comparison']
          }
        ],
        finance: [
          {
            id: 19,
            title: 'Fee Payment',
            description: 'View and pay your school fees online',
            icon: CreditCard,
            color: 'success',
            link: '/finance/payments',
            stats: `Balance: $${financeData.total_balance}`,
            popularity: 90,
            lastUpdated: new Date().toISOString().split('T')[0],
            tags: ['payment', 'fees', 'online']
          },
          {
            id: 20,
            title: 'Receipts & Invoices',
            description: 'Access your payment receipts and invoices',
            icon: FileText,
            color: 'info',
            link: '/finance/receipts',
            stats: `${financeData.recent_receipts?.length || 0} Receipts`,
            popularity: 85,
            lastUpdated: '2024-01-14',
            tags: ['receipts', 'invoices', 'records']
          },
          {
            id: 21,
            title: 'Fee Structure',
            description: 'View detailed fee breakdown and due dates',
            icon: CashStack,
            color: 'warning',
            link: '/finance/fee-structure',
            stats: `Due: ${financeData.due_date ? new Date(financeData.due_date).toLocaleDateString() : 'N/A'}`,
            popularity: 82,
            lastUpdated: '2024-01-12',
            tags: ['fees', 'structure', 'breakdown']
          },
          {
            id: 22,
            title: 'Payment History',
            description: 'Track your payment history and status',
            icon: ClockHistory,
            color: 'secondary',
            link: '/finance/payment-history',
            stats: `Paid: $${financeData.paid_amount}`,
            popularity: 78,
            lastUpdated: '2024-01-13',
            tags: ['history', 'payments', 'tracking']
          }
        ]
      };
      setResources(transformedResources);
    } catch (error) {
      console.error('Error fetching resources:', error);
    }
  };

  const quickLinks = [
    { 
      name: 'Class Schedule', 
      icon: Calendar, 
      link: '/timetable',
      description: 'View your daily schedule',
      badge: 'Updated'
    },
    { 
      name: 'Grades', 
      icon: GraphUp, 
      link: '/grades',
      description: 'Check your academic progress',
      badge: 'Live'
    },
    { 
      name: 'Assignments', 
      icon: Clipboard, 
      link: '/assignments',
      description: 'Manage your tasks',
      badge: studentData.pending_assignments > 0 ? `${studentData.pending_assignments} pending` : null
    },
    { 
      name: 'Finance', 
      icon: CreditCard, 
      link: '/finance',
      description: 'View fees and payments',
      badge: financeData.total_balance > 0 ? `$${financeData.total_balance} due` : 'Paid'
    },
    { 
      name: 'Library', 
      icon: Book, 
      link: '/library',
      description: 'Access digital resources',
      badge: 'New'
    },
    { 
      name: 'Events', 
      icon: Calendar, 
      link: '/events',
      description: 'Upcoming campus events',
      badge: studentData.upcoming_events > 0 ? `${studentData.upcoming_events} events` : null
    }
  ];

  // Filter and sort resources
  const filteredResources = resources[activeCategory]
    ?.filter(resource => 
      resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      resource.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      resource.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return b.popularity - a.popularity;
        case 'recent':
          return new Date(b.lastUpdated) - new Date(a.lastUpdated);
        case 'alphabetical':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    }) || [];

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high':
        return <span className="badge bg-danger">High Priority</span>;
      case 'medium':
        return <span className="badge bg-warning">Medium Priority</span>;
      case 'low':
        return <span className="badge bg-info">Low Priority</span>;
      default:
        return <span className="badge bg-secondary">No Priority</span>;
    }
  };

  const getDueDateBadge = (dueDate) => {
    if (!dueDate) return <span className="badge bg-secondary">No due date</span>;
    
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return <span className="badge bg-danger">Overdue</span>;
    } else if (diffDays === 0) {
      return <span className="badge bg-warning">Due Today</span>;
    } else if (diffDays === 1) {
      return <span className="badge bg-warning">Tomorrow</span>;
    } else if (diffDays <= 7) {
      return <span className="badge bg-info">{diffDays} days</span>;
    } else {
      return <span className="badge bg-success">{diffDays} days</span>;
    }
  };

  const getPopularityBadge = (popularity) => {
    if (popularity >= 90) return <span className="badge bg-success">Very Popular</span>;
    if (popularity >= 80) return <span className="badge bg-info">Popular</span>;
    if (popularity >= 70) return <span className="badge bg-warning">Average</span>;
    return <span className="badge bg-secondary">New</span>;
  };

  const getFinanceStatusBadge = (balance) => {
    if (balance === 0) {
      return <span className="badge bg-success">All Paid</span>;
    } else if (balance > 0) {
      return <span className="badge bg-warning">Payment Due</span>;
    } else {
      return <span className="badge bg-info">Credit</span>;
    }
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 fs-5">Loading your academic resources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      {/* Header Section */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 mb-2 fw-bold text-gradient">Student Resources Hub</h1>
          <p className="lead text-muted mb-0">
            Welcome back, <strong>{currentUser?.first_name || currentUser?.firstName || 'Student'}</strong>! 
            Access tools and resources to support your learning journey.
          </p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/student/dashboard" className="btn btn-outline-primary">
            <ClockHistory className="me-2" />
            Back to Portal
          </Link>
          <button className="btn btn-primary">
            <Bell className="me-2" />
            Notifications
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card border-0 bg-gradient-primary text-white shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h3 className="mb-0">{studentData.active_classes || 0}</h3>
                  <p className="mb-0 opacity-75">Active Classes</p>
                </div>
                <Book size={28} className="opacity-75" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card border-0 bg-gradient-success text-white shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h3 className="mb-0">{studentData.pending_assignments || 0}</h3>
                  <p className="mb-0 opacity-75">Pending Assignments</p>
                </div>
                <Clipboard size={28} className="opacity-75" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card border-0 bg-gradient-info text-white shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h3 className="mb-0">{studentData.overall_average || '0%'}</h3>
                  <p className="mb-0 opacity-75">Overall Average</p>
                </div>
                <GraphUp size={28} className="opacity-75" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card border-0 bg-gradient-warning text-white shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h3 className="mb-0">${financeData.total_balance || 0}</h3>
                  <p className="mb-0 opacity-75">Outstanding Balance</p>
                </div>
                <CreditCard size={28} className="opacity-75" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="card shadow-sm border-0 mb-4">
        <div className="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
          <h5 className="mb-0 fw-semibold">Quick Access</h5>
          <span className="text-muted small">Frequently used tools</span>
        </div>
        <div className="card-body">
          <div className="row g-3">
            {quickLinks.map((link, index) => (
              <div key={index} className="col-6 col-md-4 col-lg-2">
                <Link to={link.link} className="text-decoration-none">
                  <div className="card h-100 border-0 shadow-sm-hover text-center transition-all quick-link-card">
                    <div className="card-body p-3">
                      <div className="position-relative">
                        <link.icon size={24} className="text-primary mb-2" />
                        {link.badge && (
                          <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                            {link.badge}
                          </span>
                        )}
                      </div>
                      <h6 className="card-title mb-1 fw-semibold">{link.name}</h6>
                      <small className="text-muted d-none d-md-block">{link.description}</small>
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Resource Categories with Search and Filters */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white border-0 py-3">
          <div className="row align-items-center">
            <div className="col-md-6">
              <ul className="nav nav-pills">
                <li className="nav-item">
                  <button
                    className={`nav-link ${activeCategory === 'study' ? 'active' : ''}`}
                    onClick={() => setActiveCategory('study')}
                  >
                    <Book className="me-2" />
                    Study Resources
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${activeCategory === 'tools' ? 'active' : ''}`}
                    onClick={() => setActiveCategory('tools')}
                  >
                    <Clipboard className="me-2" />
                    Learning Tools
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${activeCategory === 'college' ? 'active' : ''}`}
                    onClick={() => setActiveCategory('college')}
                  >
                    <Award className="me-2" />
                    College & Career
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${activeCategory === 'finance' ? 'active' : ''}`}
                    onClick={() => setActiveCategory('finance')}
                  >
                    <CreditCard className="me-2" />
                    Finance
                  </button>
                </li>
              </ul>
            </div>
            <div className="col-md-6">
              <div className="d-flex gap-2 justify-content-end">
                <div className="input-group input-group-sm" style={{ maxWidth: '250px' }}>
                  <span className="input-group-text bg-light border-end-0">
                    <Search size={14} />
                  </span>
                  <input
                    type="text"
                    className="form-control border-start-0"
                    placeholder="Search resources..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div className="dropdown">
                  <button className="btn btn-outline-secondary btn-sm dropdown-toggle" data-bs-toggle="dropdown">
                    <Filter className="me-1" size={14} />
                    Sort: {sortBy}
                  </button>
                  <ul className="dropdown-menu">
                    <li><button className="dropdown-item" onClick={() => setSortBy('popular')}>Most Popular</button></li>
                    <li><button className="dropdown-item" onClick={() => setSortBy('recent')}>Recently Updated</button></li>
                    <li><button className="dropdown-item" onClick={() => setSortBy('alphabetical')}>Alphabetical</button></li>
                  </ul>
                </div>
                <div className="btn-group btn-group-sm">
                  <button 
                    className={`btn btn-outline-secondary ${viewMode === 'grid' ? 'active' : ''}`}
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid size={14} />
                  </button>
                  <button 
                    className={`btn btn-outline-secondary ${viewMode === 'list' ? 'active' : ''}`}
                    onClick={() => setViewMode('list')}
                  >
                    <List size={14} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="card-body">
          {searchQuery && (
            <div className="mb-3">
              <small className="text-muted">
                Showing {filteredResources.length} results for "{searchQuery}"
              </small>
            </div>
          )}
          
          <div className={viewMode === 'grid' ? "row g-4" : "list-group list-group-flush"}>
            {filteredResources.map((resource, index) => (
              viewMode === 'grid' ? (
                <div key={resource.id} className="col-md-6 col-xl-4">
                  <div className="card h-100 border-0 shadow-sm-hover transition-all resource-card">
                    <div className="card-body p-4">
                      <div className="d-flex align-items-start mb-3">
                        <div className={`bg-${resource.color} bg-opacity-10 rounded p-3 me-3`}>
                          <resource.icon size={24} className={`text-${resource.color}`} />
                        </div>
                        <div className="flex-grow-1">
                          <div className="d-flex justify-content-between align-items-start">
                            <h6 className="card-title mb-1 fw-semibold">{resource.title}</h6>
                            <button 
                              className="btn btn-sm btn-link p-0 text-warning"
                              onClick={(e) => {
                                e.preventDefault();
                                // toggleFavorite(resource.id);
                              }}
                            >
                              <Star size={16} fill={favoriteResources.some(fav => fav.resource_id === resource.id) ? 'currentColor' : 'none'} />
                            </button>
                          </div>
                          <div className="d-flex align-items-center gap-2 mb-1">
                            <small className="text-muted">{resource.stats}</small>
                            {getPopularityBadge(resource.popularity)}
                          </div>
                        </div>
                      </div>
                      <p className="card-text text-muted small mb-3">{resource.description}</p>
                      
                      <div className="mb-3">
                        {resource.tags.map((tag, tagIndex) => (
                          <span key={tagIndex} className="badge bg-light text-dark me-1 mb-1">
                            #{tag}
                          </span>
                        ))}
                      </div>
                      
                      <div className="d-flex justify-content-between align-items-center">
                        <Link 
                          to={resource.link} 
                          className="btn btn-sm btn-outline-primary rounded-pill"
                          // onClick={() => markResourceAsViewed(resource.id)}
                        >
                          <Eye className="me-1" size={14} />
                          Access Resource
                        </Link>
                        <div className="d-flex align-items-center text-muted small">
                          <Clock size={12} className="me-1" />
                          Updated {new Date(resource.lastUpdated).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div key={resource.id} className="list-group-item px-0 py-3 border-0">
                  <div className="d-flex align-items-center">
                    <div className={`bg-${resource.color} bg-opacity-10 rounded p-2 me-3`}>
                      <resource.icon size={20} className={`text-${resource.color}`} />
                    </div>
                    <div className="flex-grow-1">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <h6 className="mb-0 fw-semibold">{resource.title}</h6>
                        <div className="d-flex align-items-center gap-2">
                          {getPopularityBadge(resource.popularity)}
                          <button 
                            className="btn btn-sm btn-link p-0 text-warning"
                            // onClick={() => toggleFavorite(resource.id)}
                          >
                            <Star size={16} fill={favoriteResources.some(fav => fav.resource_id === resource.id) ? 'currentColor' : 'none'} />
                          </button>
                        </div>
                      </div>
                      <p className="text-muted small mb-2">{resource.description}</p>
                      <div className="d-flex align-items-center gap-3">
                        <small className="text-muted">{resource.stats}</small>
                        <div>
                          {resource.tags.map((tag, tagIndex) => (
                            <span key={tagIndex} className="badge bg-light text-dark me-1">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="text-end ms-3">
                      <Link 
                        to={resource.link} 
                        className="btn btn-sm btn-outline-primary"
                        // onClick={() => markResourceAsViewed(resource.id)}
                      >
                        Access
                      </Link>
                    </div>
                  </div>
                </div>
              )
            ))}
          </div>
          
          {filteredResources.length === 0 && (
            <div className="text-center py-5">
              <Search size={48} className="text-muted mb-3" />
              <h5>No resources found</h5>
              <p className="text-muted">Try adjusting your search criteria</p>
              <button 
                className="btn btn-outline-primary"
                onClick={() => setSearchQuery('')}
              >
                Clear Search
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Upcoming Deadlines & Support */}
      <div className="row mt-4">
        <div className="col-lg-8">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
              <h5 className="mb-0 fw-semibold">Upcoming Deadlines</h5>
              <Link to="/assignments" className="btn btn-sm btn-outline-primary">
                View All Assignments
              </Link>
            </div>
            <div className="card-body">
              {upcomingDeadlines.length > 0 ? (
                <div className="list-group list-group-flush">
                  {upcomingDeadlines.slice(0, 5).map((deadline, index) => (
                    <div key={index} className="list-group-item px-0 py-3">
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <div className="d-flex align-items-center mb-1">
                            <h6 className="mb-0 me-2">{deadline.title}</h6>
                            {getPriorityBadge(deadline.priority)}
                          </div>
                          <p className="text-muted small mb-1">
                            {deadline.subject} • {deadline.type}
                          </p>
                          <div className="d-flex align-items-center">
                            <Clock size={14} className="text-muted me-1" />
                            <small className="text-muted">
                              Due: {new Date(deadline.dueDate).toLocaleDateString()} at {deadline.dueTime}
                            </small>
                          </div>
                        </div>
                        <div className="text-end">
                          {getDueDateBadge(deadline.dueDate)}
                          {deadline.submitted && (
                            <CheckCircle size={16} className="text-success ms-2" />
                          )}
                        </div>
                      </div>
                      {deadline.description && (
                        <p className="text-muted small mt-2 mb-0">{deadline.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <CheckCircle size={48} className="text-success mb-3" />
                  <h5>All Caught Up!</h5>
                  <p className="text-muted">No upcoming deadlines. Great work!</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Support & Finance Summary Section */}
        <div className="col-lg-4">
          {/* Finance Summary */}
          <div className="card bg-light border-0 shadow-sm mb-4">
            <div className="card-header bg-white border-0 py-3">
              <h6 className="mb-0 fw-semibold">Finance Summary</h6>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <span className="text-muted">Outstanding Balance:</span>
                <strong className={`fs-5 ${financeData.total_balance > 0 ? 'text-danger' : 'text-success'}`}>
                  ${financeData.total_balance || 0}
                </strong>
              </div>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <span className="text-muted">Amount Paid:</span>
                <strong className="text-success">${financeData.paid_amount || 0}</strong>
              </div>
              {financeData.due_date && (
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <span className="text-muted">Next Due Date:</span>
                  <span className={`badge ${new Date(financeData.due_date) < new Date() ? 'bg-danger' : 'bg-warning'}`}>
                    {new Date(financeData.due_date).toLocaleDateString()}
                  </span>
                </div>
              )}
              <div className="d-grid gap-2">
                <Link to="/finance/payments" className="btn btn-primary btn-sm">
                  <CreditCard className="me-2" />
                  Make Payment
                </Link>
                <Link to="/finance/receipts" className="btn btn-outline-primary btn-sm">
                  <FileText className="me-2" />
                  View Receipts
                </Link>
              </div>
            </div>
          </div>

          {/* Support Section */}
          <div className="card bg-light border-0 shadow-sm">
            <div className="card-body text-center p-4">
              <Headphones size={48} className="text-primary mb-3" />
              <h5>Need Help?</h5>
              <p className="text-muted mb-4">
                Our student support team is here to help you succeed in your academic journey.
              </p>
              <div className="d-grid gap-2">
                <button className="btn btn-primary">
                  <Chat className="me-2" />
                  Live Chat Support
                </button>
                <button className="btn btn-outline-primary">
                  <Calendar className="me-2" />
                  Schedule Tutoring
                </button>
                <button className="btn btn-outline-secondary">
                  <CameraVideo className="me-2" />
                  Video Help Library
                </button>
              </div>
              <hr className="my-4" />
              <div className="text-start">
                <h6 className="small fw-semibold mb-2">Quick Contacts</h6>
                <div className="small text-muted">
                  <div className="mb-1">
                    <strong>Academic Advisor:</strong><br />
                    advisor@school.edu
                  </div>
                  <div className="mb-1">
                    <strong>Finance Office:</strong><br />
                    finance@school.edu
                  </div>
                  <div>
                    <strong>Emergency:</strong><br />
                    (555) 123-HELP
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom CSS */}
      <style jsx>{`
        .text-gradient {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .bg-gradient-primary {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .bg-gradient-success {
          background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        }
        .bg-gradient-info {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        }
        .bg-gradient-warning {
          background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        }
        .shadow-sm-hover:hover {
          box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
          transform: translateY(-2px);
        }
        .transition-all {
          transition: all 0.2s ease-in-out;
        }
        .nav-pills .nav-link {
          color: #6c757d;
          font-weight: 500;
        }
        .nav-pills .nav-link.active {
          background-color: #0d6efd;
          color: white;
        }
        .bg-opacity-10 {
          background-color: rgba(var(--bs-primary-rgb), 0.1);
        }
        .quick-link-card:hover {
          background-color: #f8f9fa;
        }
        .resource-card:hover .card-title {
          color: #0d6efd;
        }
      `}</style>
    </div>
  );
}

export default StudentResources;