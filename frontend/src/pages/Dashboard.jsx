// src/pages/Dashboard.js - COMPLETE UPDATED VERSION
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/apiService';
import {
  PersonIcon,
  PeopleIcon,
  JournalIcon,
  ClipboardIcon,
  GraphUpIcon,
  CalendarIcon,
  CalendarCheckIcon,
  BookIcon,
  ClockIcon,
  CheckCircleIcon,
  AwardIcon,
  BellIcon,
  ActivityIcon,
  SchoolIcon,
  CreditCardIcon,
  DownloadIcon,
  EyeIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  FileTextIcon,
  MegaphoneIcon,
  ShieldCheckIcon,
  DatabaseIcon,
  HardDriveIcon,
  RefreshIcon,
  CashIcon,
  ReceiptIcon,
  PaymentIcon,
  DebtIcon,
  ReportIcon,
  UsersIcon,
  BookOpenIcon,
  GraduationCapIcon,
  ExclamationTriangleIcon,
  InfoCircleIcon,
  LightbulbIcon,
  StarIcon,
  TrophyIcon,
  TargetIcon,
  SpeedometerIcon
} from '../components/Icons';

function Dashboard() {
  const { currentUser, getDashboardUrl, hasPermission, isStudent, isTeacher, isAdmin, isAccountant, isParent } = useAuth();
  const navigate = useNavigate();
  
  // State management
  const [dashboardData, setDashboardData] = useState({
    user: currentUser || {},
    stats: {},
    recentActivities: [],
    upcomingEvents: [],
    announcements: [],
    notifications: [],
    quickActions: [],
    systemAlerts: [],
    welcomeMessage: '',
    profileCompletion: 0,
    missingFields: [],
    isFallback: false,
    lastUpdated: null,
    apiStatus: 'checking'
  });
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeView, setActiveView] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [selectedWidgets, setSelectedWidgets] = useState(['stats', 'quick-actions', 'recent-activity', 'upcoming-events']);

  // Fetch dashboard data on component mount
  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 5 minutes
    const refreshInterval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        fetchDashboardData(true); // Silent refresh
      }
    }, 5 * 60 * 1000);
    
    return () => clearInterval(refreshInterval);
  }, []);

  // Main data fetching function
  const fetchDashboardData = async (silent = false) => {
    try {
      if (!silent) {
        setLoading(true);
      }
      setRefreshing(true);
      
      console.log('🔄 Fetching dashboard data...');
      
      // Get dashboard data from API service
      const result = await apiService.getRoleDashboard();
      
      if (result.success) {
        console.log('✅ Dashboard data fetched successfully');
        
        // Enhanced data processing
        const processedData = processDashboardData(result.data, result.isFallback || false);
        
        setDashboardData({
          ...processedData,
          apiStatus: 'connected',
          lastUpdated: new Date().toISOString(),
          isFallback: result.isFallback || false
        });
        
        // Update local storage if needed
        if (processedData.user && !result.isFallback) {
          localStorage.setItem('dashboard_cache', JSON.stringify({
            data: processedData,
            timestamp: Date.now()
          }));
        }
        
      } else {
        console.warn('⚠️ Using fallback dashboard data');
        setDashboardData(prev => ({
          ...prev,
          ...createFallbackDashboardData(),
          apiStatus: 'disconnected',
          lastUpdated: new Date().toISOString(),
          isFallback: true
        }));
      }
      
    } catch (error) {
      console.error('💥 Error fetching dashboard data:', error);
      setDashboardData(prev => ({
        ...prev,
        apiStatus: 'error',
        isFallback: true,
        error: error.message
      }));
    } finally {
      if (!silent) {
        setLoading(false);
      }
      setRefreshing(false);
    }
  };

  // Process and enhance dashboard data
  const processDashboardData = (apiData, isFallback) => {
    const user = apiData.user || currentUser || {};
    const role = user.role || 'student';
    
    // Calculate statistics based on role
    const stats = calculateRoleStats(role, apiData);
    
    // Generate recent activities
    const recentActivities = generateRecentActivities(role, apiData);
    
    // Get upcoming events
    const upcomingEvents = getUpcomingEvents(apiData);
    
    // Get quick actions
    const quickActions = getQuickActions(role);
    
    // Generate welcome message
    const welcomeMessage = getWelcomeMessage(role, user);
    
    // Calculate profile completion
    const profileCompletion = calculateProfileCompletion(user);
    const missingFields = getMissingFields(user);
    
    // Get system alerts
    const systemAlerts = getSystemAlerts(apiData);
    
    // Get notifications
    const notifications = getNotifications(apiData);
    
    // Get announcements
    const announcements = getAnnouncements(apiData);
    
    return {
      user,
      stats,
      recentActivities,
      upcomingEvents,
      quickActions,
      welcomeMessage,
      profileCompletion,
      missingFields,
      systemAlerts,
      notifications,
      announcements,
      isFallback
    };
  };

  // Create fallback data when API is unavailable
  const createFallbackDashboardData = () => {
    const user = currentUser || JSON.parse(localStorage.getItem('user_data') || '{}');
    const role = user.role || 'student';
    
    return {
      user,
      stats: calculateRoleStats(role, {}),
      recentActivities: [
        {
          id: 1,
          activity: 'You logged into the system',
          time: 'Just now',
          type: 'login',
          icon: 'login'
        },
        {
          id: 2,
          activity: 'Welcome to your dashboard',
          time: 'Today',
          type: 'welcome',
          icon: 'welcome'
        },
        {
          id: 3,
          activity: 'System is running in offline mode',
          time: 'Now',
          type: 'system',
          icon: 'offline'
        }
      ],
      upcomingEvents: [],
      quickActions: getQuickActions(role),
      welcomeMessage: getWelcomeMessage(role, user),
      profileCompletion: calculateProfileCompletion(user),
      missingFields: getMissingFields(user),
      systemAlerts: [
        {
          id: 1,
          type: 'warning',
          title: 'Limited Functionality',
          message: 'Dashboard is running in offline mode. Some features may be unavailable.',
          timestamp: new Date().toISOString()
        }
      ],
      notifications: [],
      announcements: [],
      isFallback: true
    };
  };

  // Calculate role-specific statistics
  const calculateRoleStats = (role, apiData) => {
    const baseStats = apiData.stats || {};
    
    switch (role) {
      case 'student':
        return {
          pendingAssignments: { 
            value: baseStats.pendingAssignments || 0, 
            label: 'Pending Assignments',
            icon: ClipboardIcon,
            color: 'warning',
            link: '/assignments',
            trend: 'up',
            trendValue: '+2'
          },
          averageGrade: { 
            value: baseStats.averageGrade || 'B+', 
            label: 'Average Grade',
            icon: GraphUpIcon,
            color: 'success',
            link: '/grades',
            trend: 'up',
            trendValue: '+0.5'
          },
          attendanceRate: { 
            value: baseStats.attendanceRate ? `${baseStats.attendanceRate}%` : '95%', 
            label: 'Attendance Rate',
            icon: CalendarCheckIcon,
            color: 'info',
            link: '/attendance',
            trend: 'stable',
            trendValue: '0%'
          },
          enrolledClasses: { 
            value: baseStats.enrolledClasses || 5, 
            label: 'Enrolled Classes',
            icon: SchoolIcon,
            color: 'primary',
            link: '/classes',
            trend: 'stable',
            trendValue: '0'
          }
        };
        
      case 'teacher':
        return {
          totalStudents: { 
            value: baseStats.totalStudents || 45, 
            label: 'Total Students',
            icon: PeopleIcon,
            color: 'primary',
            link: '/students',
            trend: 'up',
            trendValue: '+3'
          },
          activeClasses: { 
            value: baseStats.activeClasses || 6, 
            label: 'Active Classes',
            icon: JournalIcon,
            color: 'success',
            link: '/classes',
            trend: 'stable',
            trendValue: '0'
          },
          pendingGrades: { 
            value: baseStats.pendingGrades || 12, 
            label: 'Pending Grades',
            icon: ClipboardIcon,
            color: 'warning',
            link: '/grades',
            trend: 'up',
            trendValue: '+4'
          },
          attendanceRate: { 
            value: baseStats.attendanceRate ? `${baseStats.attendanceRate}%` : '92%', 
            label: 'Class Attendance',
            icon: CalendarCheckIcon,
            color: 'info',
            link: '/attendance',
            trend: 'up',
            trendValue: '+2%'
          }
        };
        
      case 'admin':
        return {
          totalUsers: { 
            value: baseStats.totalUsers || 324, 
            label: 'Total Users',
            icon: UsersIcon,
            color: 'primary',
            link: '/admin/users',
            trend: 'up',
            trendValue: '+12'
          },
          activeStudents: { 
            value: baseStats.activeStudents || 245, 
            label: 'Active Students',
            icon: GraduationCapIcon,
            color: 'success',
            link: '/students',
            trend: 'up',
            trendValue: '+8'
          },
          activeTeachers: { 
            value: baseStats.activeTeachers || 45, 
            label: 'Active Teachers',
            icon: PersonIcon,
            color: 'info',
            link: '/teachers',
            trend: 'stable',
            trendValue: '0'
          },
          pendingApprovals: { 
            value: baseStats.pendingApprovals || 7, 
            label: 'Pending Approvals',
            icon: ClockIcon,
            color: 'warning',
            link: '/admin/approvals',
            trend: 'down',
            trendValue: '-3'
          }
        };
        
      case 'accountant':
        return {
          totalRevenue: { 
            value: `KES ${(baseStats.totalRevenue || 1250000).toLocaleString()}`, 
            label: 'Total Revenue',
            icon: CashIcon,
            color: 'success',
            link: '/finance/reports',
            trend: 'up',
            trendValue: '+8.5%'
          },
          pendingPayments: { 
            value: baseStats.pendingPayments || 23, 
            label: 'Pending Payments',
            icon: PaymentIcon,
            color: 'warning',
            link: '/finance/payments',
            trend: 'up',
            trendValue: '+5'
          },
          outstandingDebt: { 
            value: `KES ${(baseStats.outstandingDebt || 245000).toLocaleString()}`, 
            label: 'Outstanding Debt',
            icon: DebtIcon,
            color: 'danger',
            link: '/finance/debts',
            trend: 'down',
            trendValue: '-12.3%'
          },
          receiptsToday: { 
            value: baseStats.receiptsToday || 45, 
            label: 'Receipts Today',
            icon: ReceiptIcon,
            color: 'info',
            link: '/finance/receipts',
            trend: 'up',
            trendValue: '+23.1%'
          }
        };
        
      case 'parent':
        return {
          childrenCount: { 
            value: baseStats.childrenCount || 2, 
            label: 'Children',
            icon: PeopleIcon,
            color: 'primary',
            link: '/children',
            trend: 'stable',
            trendValue: '0'
          },
          averageGrade: { 
            value: baseStats.averageGrade || 'B+', 
            label: 'Average Grade',
            icon: GraphUpIcon,
            color: 'success',
            link: '/child-progress',
            trend: 'up',
            trendValue: '+1.2%'
          },
          attendanceRate: { 
            value: baseStats.attendanceRate ? `${baseStats.attendanceRate}%` : '96%', 
            label: 'Attendance Rate',
            icon: CalendarCheckIcon,
            color: 'info',
            link: '/attendance',
            trend: 'stable',
            trendValue: '0%'
          },
          feeBalance: { 
            value: `KES ${(baseStats.feeBalance || 0).toLocaleString()}`, 
            label: 'Fee Balance',
            icon: CreditCardIcon,
            color: 'warning',
            link: '/parent/billing',
            trend: 'down',
            trendValue: '-25%'
          }
        };
        
      default:
        return baseStats;
    }
  };

  // Generate recent activities
  const generateRecentActivities = (role, apiData) => {
    const activities = apiData.recentActivities || [];
    
    if (activities.length === 0) {
      return [
        {
          id: 1,
          activity: 'You logged into the system',
          time: 'Just now',
          type: 'login',
          icon: 'login'
        },
        {
          id: 2,
          activity: 'Welcome to your dashboard',
          time: 'Today',
          type: 'welcome',
          icon: 'welcome'
        },
        {
          id: 3,
          activity: 'Dashboard initialized successfully',
          time: 'Now',
          type: 'system',
          icon: 'check'
        }
      ];
    }
    
    return activities.slice(0, 8);
  };

  // Get upcoming events
  const getUpcomingEvents = (apiData) => {
    const events = apiData.upcomingEvents || [];
    
    if (events.length === 0) {
      const today = new Date();
      return [
        {
          id: 1,
          title: 'Staff Meeting',
          date: new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          time: '10:00 AM',
          location: 'Conference Room',
          type: 'meeting',
          priority: 'medium'
        },
        {
          id: 2,
          title: 'Parent-Teacher Conference',
          date: new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          time: '2:00 PM',
          location: 'School Hall',
          type: 'conference',
          priority: 'high'
        },
        {
          id: 3,
          title: 'Sports Day',
          date: new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          time: '9:00 AM',
          location: 'School Ground',
          type: 'event',
          priority: 'medium'
        }
      ];
    }
    
    return events.slice(0, 5);
  };

  // Get quick actions based on role
  const getQuickActions = (role) => {
    const actions = {
      student: [
        {
          id: 1,
          title: 'View Assignments',
          description: 'Check pending assignments and deadlines',
          icon: ClipboardIcon,
          link: '/assignments',
          color: 'primary',
          badge: '3 new'
        },
        {
          id: 2,
          title: 'Check Grades',
          description: 'View your grades and performance',
          icon: GraphUpIcon,
          link: '/grades',
          color: 'success',
          badge: 'Updated'
        },
        {
          id: 3,
          title: 'Class Schedule',
          description: 'View your class timetable',
          icon: CalendarIcon,
          link: '/timetable',
          color: 'warning'
        },
        {
          id: 4,
          title: 'Learning Resources',
          description: 'Access study materials and resources',
          icon: BookIcon,
          link: '/resources',
          color: 'info'
        }
      ],
      teacher: [
        {
          id: 1,
          title: 'My Classes',
          description: 'Manage your assigned classes',
          icon: JournalIcon,
          link: '/classes',
          color: 'primary',
          badge: '6 active'
        },
        {
          id: 2,
          title: 'Take Attendance',
          description: 'Record student attendance',
          icon: CalendarCheckIcon,
          link: '/attendance',
          color: 'success',
          badge: 'Today'
        },
        {
          id: 3,
          title: 'Enter Grades',
          description: 'Grade student assignments',
          icon: ClipboardIcon,
          link: '/grades',
          color: 'warning',
          badge: '12 pending'
        },
        {
          id: 4,
          title: 'Lesson Plans',
          description: 'Create and manage lesson plans',
          icon: BookOpenIcon,
          link: '/lesson-plans',
          color: 'info'
        }
      ],
      admin: [
        {
          id: 1,
          title: 'User Management',
          description: 'Manage all system users',
          icon: UsersIcon,
          link: '/admin/users',
          color: 'primary',
          badge: '7 pending'
        },
        {
          id: 2,
          title: 'Academic Management',
          description: 'Manage curriculum and classes',
          icon: SchoolIcon,
          link: '/academic-management',
          color: 'success'
        },
        {
          id: 3,
          title: 'System Settings',
          description: 'Configure system settings',
          icon: ShieldCheckIcon,
          link: '/admin/settings',
          color: 'warning'
        },
        {
          id: 4,
          title: 'Analytics',
          description: 'View system analytics and reports',
          icon: GraphUpIcon,
          link: '/admin/analytics',
          color: 'info',
          badge: 'New'
        }
      ],
      accountant: [
        {
          id: 1,
          title: 'Finance Dashboard',
          description: 'Overview of financial status',
          icon: CreditCardIcon,
          link: '/finance',
          color: 'primary'
        },
        {
          id: 2,
          title: 'Process Payments',
          description: 'Handle incoming payments',
          icon: PaymentIcon,
          link: '/finance/payments',
          color: 'success',
          badge: '23 pending'
        },
        {
          id: 3,
          title: 'Manage Receipts',
          description: 'Issue and manage receipts',
          icon: ReceiptIcon,
          link: '/finance/receipts',
          color: 'warning',
          badge: '45 today'
        },
        {
          id: 4,
          title: 'Financial Reports',
          description: 'Generate financial reports',
          icon: ReportIcon,
          link: '/finance/reports',
          color: 'info'
        }
      ],
      parent: [
        {
          id: 1,
          title: 'Child Progress',
          description: 'Monitor academic performance',
          icon: GraphUpIcon,
          link: '/child-progress',
          color: 'primary'
        },
        {
          id: 2,
          title: 'Attendance',
          description: 'Check child attendance',
          icon: CalendarCheckIcon,
          link: '/attendance',
          color: 'success',
          badge: '96%'
        },
        {
          id: 3,
          title: 'Fee Statements',
          description: 'View and pay fees',
          icon: CreditCardIcon,
          link: '/parent/billing',
          color: 'warning',
          badge: 'Due'
        },
        {
          id: 4,
          title: 'Communications',
          description: 'School announcements and messages',
          icon: MegaphoneIcon,
          link: '/communications',
          color: 'info',
          badge: '2 new'
        }
      ]
    };
    
    return actions[role] || actions.student;
  };

  // Generate welcome message
  const getWelcomeMessage = (role, user) => {
    const firstName = user.first_name || user.firstName || user.email?.split('@')[0] || 'there';
    const timeOfDay = getTimeOfDay();
    
    const messages = {
      student: `${timeOfDay}, ${firstName}! Ready to learn and grow today? Check your assignments and track your progress.`,
      teacher: `${timeOfDay}, ${firstName}! Make a difference in your students' lives today.`,
      admin: `${timeOfDay}, ${firstName}! Overseeing school operations and ensuring smooth functioning.`,
      accountant: `${timeOfDay}, ${firstName}! Managing finances and keeping everything balanced.`,
      parent: `${timeOfDay}, ${firstName}! Staying connected with your child's education journey.`
    };
    
    return messages[role] || `Welcome back, ${firstName}!`;
  };

  // Get time of day for greeting
  const getTimeOfDay = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  // Calculate profile completion percentage
  const calculateProfileCompletion = (user) => {
    if (!user) return 0;
    
    const requiredFields = [
      'first_name', 'last_name', 'email', 'phone_number',
      'date_of_birth', 'gender', 'address'
    ];
    
    let completed = 0;
    for (const field of requiredFields) {
      const value = user[field];
      if (value && (typeof value !== 'string' || value.trim() !== '')) {
        completed++;
      }
    }
    
    return Math.round((completed / requiredFields.length) * 100);
  };

  // Get missing profile fields
  const getMissingFields = (user) => {
    if (!user) return [];
    
    const fields = [
      { key: 'first_name', label: 'First Name' },
      { key: 'last_name', label: 'Last Name' },
      { key: 'email', label: 'Email' },
      { key: 'phone_number', label: 'Phone Number' },
      { key: 'date_of_birth', label: 'Date of Birth' },
      { key: 'gender', label: 'Gender' },
      { key: 'address', label: 'Address' }
    ];
    
    return fields.filter(field => {
      const value = user[field.key];
      return !value || (typeof value === 'string' && value.trim() === '');
    });
  };

  // Get system alerts
  const getSystemAlerts = (apiData) => {
    const alerts = apiData.systemAlerts || [];
    
    if (alerts.length === 0 && dashboardData.isFallback) {
      return [
        {
          id: 1,
          type: 'info',
          title: 'Offline Mode',
          message: 'You are viewing cached data. Some features may be limited.',
          timestamp: new Date().toISOString(),
          action: { label: 'Refresh', handler: fetchDashboardData }
        }
      ];
    }
    
    return alerts.slice(0, 3);
  };

  // Get notifications
  const getNotifications = (apiData) => {
    return apiData.notifications || [];
  };

  // Get announcements
  const getAnnouncements = (apiData) => {
    return apiData.announcements || [];
  };

  // Get trend icon component
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon size={14} className="text-success" />;
      case 'down':
        return <TrendingDownIcon size={14} className="text-danger" />;
      default:
        return <GraphUpIcon size={14} className="text-warning" />;
    }
  };

  // Get trend text
  const getTrendText = (trend, value) => {
    switch (trend) {
      case 'up':
        return <span className="text-success fw-medium">+{value}</span>;
      case 'down':
        return <span className="text-danger fw-medium">-{value}</span>;
      default:
        return <span className="text-warning fw-medium">{value}</span>;
    }
  };

  // Handle widget customization
  const toggleWidget = (widgetId) => {
    setSelectedWidgets(prev => 
      prev.includes(widgetId)
        ? prev.filter(id => id !== widgetId)
        : [...prev, widgetId]
    );
  };

  // Handle manual refresh
  const handleRefresh = () => {
    fetchDashboardData();
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Loading state
  if (loading && !dashboardData.isFallback) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <h3 className="mt-4">Loading Your Dashboard</h3>
          <p className="text-muted">Preparing your personalized dashboard experience...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      {/* Header Section */}
      <div className="container-fluid py-4">
        <div className="row mb-4">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h1 className="display-6 fw-bold text-dark mb-1">Dashboard</h1>
                <p className="text-muted mb-0">
                  <ClockIcon size={14} className="me-1" />
                  Last updated: {new Date(dashboardData.lastUpdated || Date.now()).toLocaleTimeString()}
                  {dashboardData.isFallback && (
                    <span className="badge bg-warning ms-2">
                      <ExclamationTriangleIcon size={12} className="me-1" />
                      Offline Mode
                    </span>
                  )}
                </p>
              </div>
              
              <div className="d-flex gap-2">
                {/* Search Bar */}
                <form onSubmit={handleSearch} className="d-none d-md-block">
                  <div className="input-group">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search dashboard..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      style={{ minWidth: '250px' }}
                    />
                    <button className="btn btn-outline-primary" type="submit">
                      <i className="bi bi-search"></i>
                    </button>
                  </div>
                </form>
                
                {/* Refresh Button */}
                <button
                  className="btn btn-outline-primary"
                  onClick={handleRefresh}
                  disabled={refreshing}
                >
                  <RefreshIcon className={`me-2 ${refreshing ? 'spin' : ''}`} size={16} />
                  {refreshing ? 'Refreshing...' : 'Refresh'}
                </button>
                
                {/* Customize View */}
                <button
                  className="btn btn-outline-secondary"
                  onClick={() => setShowNotifications(!showNotifications)}
                >
                  <BellIcon size={16} />
                  {dashboardData.notifications.length > 0 && (
                    <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                      {dashboardData.notifications.length}
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* System Alerts */}
        {dashboardData.systemAlerts.length > 0 && (
          <div className="row mb-4">
            <div className="col-12">
              <div className="card border-0 shadow-sm">
                <div className="card-body p-3">
                  {dashboardData.systemAlerts.map(alert => (
                    <div key={alert.id} className={`alert alert-${alert.type} border-0 mb-2`}>
                      <div className="d-flex align-items-center">
                        <div className="flex-grow-1">
                          <strong>{alert.title}</strong> - {alert.message}
                        </div>
                        {alert.action && (
                          <button 
                            className="btn btn-sm btn-outline-dark ms-3"
                            onClick={alert.action.handler}
                          >
                            {alert.action.label}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Welcome Section */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="card bg-gradient-primary text-white border-0 shadow-lg overflow-hidden">
              <div className="card-body p-4 p-lg-5">
                <div className="row align-items-center">
                  <div className="col-lg-8">
                    <div className="d-flex align-items-center mb-3">
                      <div className="bg-white bg-opacity-20 rounded-circle d-flex align-items-center justify-content-center me-3"
                           style={{ width: '80px', height: '80px' }}>
                        <PersonIcon size={32} />
                      </div>
                      <div>
                        <h1 className="display-5 fw-bold mb-1">
                          {getTimeOfDay()}, {dashboardData.user.first_name || dashboardData.user.firstName || 'there'}!
                        </h1>
                        <p className="lead mb-0 opacity-90">
                          {dashboardData.welcomeMessage}
                        </p>
                      </div>
                    </div>
                    
                    {/* Profile Completion */}
                    {dashboardData.profileCompletion < 100 && (
                      <div className="mt-3">
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span className="text-white-75">Profile Completion</span>
                          <span className="badge bg-white text-primary">
                            {dashboardData.profileCompletion}%
                          </span>
                        </div>
                        <div className="progress" style={{ height: '8px' }}>
                          <div 
                            className="progress-bar bg-white" 
                            style={{ width: `${dashboardData.profileCompletion}%` }}
                          ></div>
                        </div>
                        {dashboardData.missingFields.length > 0 && (
                          <small className="text-white-75 mt-2 d-block">
                            Missing: {dashboardData.missingFields.map(f => f.label).join(', ')}
                            <Link to="/profile" className="text-white ms-2">
                              <i className="bi bi-arrow-right ms-1"></i> Complete Now
                            </Link>
                          </small>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="col-lg-4 text-lg-end">
                    <div className="mt-4 mt-lg-0">
                      <span className="badge bg-white text-primary fs-6 px-3 py-2 mb-3 d-inline-block">
                        <GraduationCapIcon size={18} className="me-2" />
                        {dashboardData.user.role ? 
                          dashboardData.user.role.charAt(0).toUpperCase() + dashboardData.user.role.slice(1) : 
                          'User'
                        }
                      </span>
                      <div className="d-flex flex-column gap-2">
                        <Link to={getDashboardUrl()} className="btn btn-light btn-lg">
                          <i className="bi bi-speedometer2 me-2"></i>
                          Go to {dashboardData.user.role || 'User'} Portal
                        </Link>
                        <Link to="/profile" className="btn btn-outline-light">
                          <i className="bi bi-person me-2"></i>
                          View Profile
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        {selectedWidgets.includes('stats') && (
          <div className="row g-4 mb-5">
            {Object.entries(dashboardData.stats).map(([key, stat]) => {
              const IconComponent = stat.icon;
              return (
                <div key={key} className="col-md-6 col-xl-3">
                  <Link to={stat.link} className="text-decoration-none">
                    <div className={`card border-0 h-100 shadow-sm hover-lift transition-all bg-${stat.color} text-white`}>
                      <div className="card-body position-relative p-4">
                        <div className="d-flex justify-content-between align-items-start mb-3">
                          <div>
                            <h2 className="fw-bold mb-0">{stat.value}</h2>
                            <p className="mb-1 fw-medium opacity-90">{stat.label}</p>
                          </div>
                          <div className={`bg-white bg-opacity-20 rounded-circle p-2`}>
                            <IconComponent size={24} className="opacity-90" />
                          </div>
                        </div>
                        <div className="d-flex justify-content-between align-items-center">
                          <div className="d-flex align-items-center">
                            {getTrendIcon(stat.trend)}
                            <span className="ms-2 small opacity-90">
                              {getTrendText(stat.trend, stat.trendValue)}
                            </span>
                          </div>
                          <span className="small opacity-75">vs last week</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </div>
              );
            })}
          </div>
        )}

        {/* Main Content Area */}
        <div className="row">
          {/* Left Column - Quick Actions & Recent Activity */}
          <div className="col-lg-8">
            {/* Quick Actions */}
            {selectedWidgets.includes('quick-actions') && (
              <div className="card shadow-sm border-0 mb-4">
                <div className="card-header bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="card-title mb-0 fw-semibold text-dark">
                      <SpeedometerIcon size={18} className="me-2" />
                      Quick Actions
                    </h5>
                    <Link to="/tools" className="btn btn-sm btn-outline-primary">
                      View All Tools
                    </Link>
                  </div>
                </div>
                <div className="card-body">
                  <div className="row g-3">
                    {dashboardData.quickActions.map(action => {
                      const IconComponent = action.icon;
                      return (
                        <div key={action.id} className="col-md-6 col-lg-3">
                          <Link to={action.link} className="text-decoration-none">
                            <div className="card border-0 shadow-sm-hover text-center h-100 transition-all">
                              <div className="card-body p-3">
                                <div className={`bg-${action.color} bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3`}
                                     style={{ width: '60px', height: '60px' }}>
                                  <IconComponent size={24} className={`text-${action.color}`} />
                                </div>
                                <h6 className="card-title mb-1 fw-semibold text-dark">{action.title}</h6>
                                <small className="text-muted d-block mb-2">{action.description}</small>
                                {action.badge && (
                                  <span className={`badge bg-${action.color} bg-opacity-25 text-${action.color}`}>
                                    {action.badge}
                                  </span>
                                )}
                              </div>
                            </div>
                          </Link>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Role-Specific Content */}
            {(isTeacher || isAdmin || isAccountant) && selectedWidgets.includes('role-content') && (
              <div className="card shadow-sm border-0 mb-4">
                <div className="card-header bg-white border-0 py-3">
                  <h5 className="card-title mb-0 fw-semibold text-dark">
                    {isTeacher && 'Class Management'}
                    {isAdmin && 'System Overview'}
                    {isAccountant && 'Financial Overview'}
                  </h5>
                </div>
                <div className="card-body">
                  {/* Role-specific content will go here */}
                  <p className="text-muted mb-0">
                    {isTeacher && 'Manage your classes, assignments, and student progress.'}
                    {isAdmin && 'Monitor system health, user activity, and overall performance.'}
                    {isAccountant && 'Track revenue, expenses, and financial transactions.'}
                  </p>
                </div>
              </div>
            )}

            {/* Recent Activity */}
            {selectedWidgets.includes('recent-activity') && (
              <div className="card shadow-sm border-0">
                <div className="card-header bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="card-title mb-0 fw-semibold text-dark">
                      <ActivityIcon size={18} className="me-2" />
                      Recent Activity
                    </h5>
                    <Link to="/activity" className="btn btn-sm btn-outline-primary">
                      <EyeIcon size={14} className="me-1" />
                      View All
                    </Link>
                  </div>
                </div>
                <div className="card-body">
                  <div className="activity-timeline">
                    {dashboardData.recentActivities.map(activity => (
                      <div key={activity.id} className="activity-item d-flex mb-3">
                        <div className={`bg-${activity.type === 'login' ? 'primary' : activity.type === 'welcome' ? 'success' : 'info'} text-white rounded-circle d-flex align-items-center justify-content-center me-3 flex-shrink-0`}
                             style={{ width: '40px', height: '40px' }}>
                          <ActivityIcon size={18} />
                        </div>
                        <div className="activity-content flex-grow-1">
                          <p className="mb-1 text-dark small fw-medium">{activity.activity}</p>
                          <small className="text-muted">
                            <ClockIcon size={12} className="me-1" />
                            {activity.time}
                          </small>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Upcoming Events & Notifications */}
          <div className="col-lg-4">
            {/* Upcoming Events */}
            {selectedWidgets.includes('upcoming-events') && (
              <div className="card shadow-sm border-0 mb-4">
                <div className="card-header bg-white border-0 py-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="card-title mb-0 fw-semibold text-dark">
                      <CalendarIcon size={18} className="me-2" />
                      Upcoming Events
                    </h5>
                    <Link to="/calendar" className="btn btn-sm btn-outline-primary">
                      Full Calendar
                    </Link>
                  </div>
                </div>
                <div className="card-body">
                  {dashboardData.upcomingEvents.length > 0 ? (
                    dashboardData.upcomingEvents.map(event => (
                      <div key={event.id} className="event-item d-flex mb-3 pb-3 border-bottom">
                        <div className="event-date text-center me-3">
                          <div className="bg-light rounded p-2">
                            <div className="fw-bold text-primary">
                              {new Date(event.date).toLocaleDateString('en-US', { day: 'numeric' })}
                            </div>
                            <div className="text-muted small">
                              {new Date(event.date).toLocaleDateString('en-US', { month: 'short' })}
                            </div>
                          </div>
                        </div>
                        <div className="event-content flex-grow-1">
                          <h6 className="mb-1 fw-semibold">{event.title}</h6>
                          <small className="text-muted d-block mb-1">
                            <ClockIcon size={12} className="me-1" />
                            {event.time}
                          </small>
                          <small className="text-muted d-block">{event.location}</small>
                          {event.priority === 'high' && (
                            <span className="badge bg-danger mt-1">High Priority</span>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-4">
                      <CalendarIcon size={32} className="text-muted mb-2" />
                      <p className="text-muted mb-0">No upcoming events</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Notifications Panel */}
            {showNotifications && (
              <div className="card shadow-sm border-0 mb-4">
                <div className="card-header bg-white border-0 py-3">
                  <h5 className="card-title mb-0 fw-semibold text-dark">
                    <BellIcon size={18} className="me-2" />
                    Notifications
                    {dashboardData.notifications.length > 0 && (
                      <span className="badge bg-danger ms-2">{dashboardData.notifications.length}</span>
                    )}
                  </h5>
                </div>
                <div className="card-body">
                  {dashboardData.notifications.length > 0 ? (
                    dashboardData.notifications.slice(0, 5).map(notification => (
                      <div key={notification.id} className="notification-item mb-3">
                        <div className="d-flex align-items-start">
                          <div className={`bg-${notification.type} text-white rounded-circle p-2 me-3`}>
                            <BellIcon size={14} />
                          </div>
                          <div className="flex-grow-1">
                            <p className="mb-1 small">{notification.message}</p>
                            <small className="text-muted">{notification.time}</small>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-3">
                      <p className="text-muted mb-0">No new notifications</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Profile Completion Card */}
            {dashboardData.profileCompletion < 100 && (
              <div className="card shadow-sm border-0 mb-4">
                <div className="card-header bg-white border-0 py-3">
                  <h5 className="card-title mb-0 fw-semibold text-dark">
                    <TargetIcon size={18} className="me-2" />
                    Complete Your Profile
                  </h5>
                </div>
                <div className="card-body">
                  <div className="text-center mb-3">
                    <div className="position-relative d-inline-block">
                      <div className="progress-circle" style={{ width: '120px', height: '120px' }}>
                        <div className="progress-circle-value">{dashboardData.profileCompletion}%</div>
                      </div>
                    </div>
                  </div>
                  <p className="text-center text-muted mb-3">
                    Complete your profile to unlock all features
                  </p>
                  {dashboardData.missingFields.length > 0 && (
                    <div className="mb-3">
                      <h6 className="small fw-bold mb-2">Missing Information:</h6>
                      <ul className="list-unstyled mb-0">
                        {dashboardData.missingFields.slice(0, 3).map(field => (
                          <li key={field.key} className="text-danger mb-1">
                            <small>
                              <i className="bi bi-exclamation-circle me-1"></i>
                              {field.label}
                            </small>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="text-center">
                    <Link to="/profile" className="btn btn-primary btn-sm">
                      Complete Profile
                    </Link>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Tips */}
            <div className="card shadow-sm border-0">
              <div className="card-header bg-white border-0 py-3">
                <h5 className="card-title mb-0 fw-semibold text-dark">
                  <LightbulbIcon size={18} className="me-2" />
                  Quick Tips
                </h5>
              </div>
              <div className="card-body">
                <div className="tip-item mb-3">
                  <div className="d-flex align-items-start">
                    <div className="bg-primary bg-opacity-10 text-primary rounded-circle p-2 me-3">
                      <LightbulbIcon size={14} />
                    </div>
                    <div>
                      <p className="mb-1 small fw-medium">Use the search bar to quickly find anything</p>
                    </div>
                  </div>
                </div>
                <div className="tip-item mb-3">
                  <div className="d-flex align-items-start">
                    <div className="bg-success bg-opacity-10 text-success rounded-circle p-2 me-3">
                      <StarIcon size={14} />
                    </div>
                    <div>
                      <p className="mb-1 small fw-medium">Click on statistic cards for detailed views</p>
                    </div>
                  </div>
                </div>
                <div className="tip-item">
                  <div className="d-flex align-items-start">
                    <div className="bg-info bg-opacity-10 text-info rounded-circle p-2 me-3">
                      <InfoCircleIcon size={14} />
                    </div>
                    <div>
                      <p className="mb-1 small fw-medium">Complete your profile for personalized experience</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Status Bar */}
        <div className="row mt-4">
          <div className="col-12">
            <div className="card border-0 bg-light">
              <div className="card-body py-2">
                <div className="d-flex justify-content-between align-items-center">
                  <div className="d-flex align-items-center">
                    <div className={`dot ${dashboardData.apiStatus === 'connected' ? 'bg-success' : dashboardData.apiStatus === 'error' ? 'bg-danger' : 'bg-warning'}`}></div>
                    <small className="ms-2 text-muted">
                      {dashboardData.apiStatus === 'connected' ? 'Connected to server' : 
                       dashboardData.apiStatus === 'error' ? 'Connection error' : 
                       'Checking connection...'}
                    </small>
                  </div>
                  <small className="text-muted">
                    {dashboardData.isFallback ? 'Using cached data' : 'Live data'} • 
                    Last refresh: {new Date(dashboardData.lastUpdated || Date.now()).toLocaleTimeString()}
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CSS Styles */}
      <style jsx>{`
        .dashboard-page {
          min-height: 100vh;
          background-color: #f8f9fa;
        }
        
        .hover-lift:hover {
          transform: translateY(-5px);
          transition: transform 0.3s ease;
        }
        
        .shadow-sm-hover:hover {
          box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
        }
        
        .transition-all {
          transition: all 0.2s ease-in-out;
        }
        
        .bg-gradient-primary {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .spin {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .progress-circle {
          position: relative;
          background: conic-gradient(#4e54c8 ${dashboardData.profileCompletion * 3.6}deg, #e9ecef 0deg);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .progress-circle:before {
          content: "";
          position: absolute;
          width: 90px;
          height: 90px;
          background: white;
          border-radius: 50%;
        }
        
        .progress-circle-value {
          position: relative;
          font-size: 1.5rem;
          font-weight: bold;
          color: #4e54c8;
        }
        
        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          display: inline-block;
        }
        
        .activity-item:last-child,
        .event-item:last-child {
          border-bottom: none !important;
          margin-bottom: 0 !important;
          padding-bottom: 0 !important;
        }
        
        .notification-item:last-child {
          margin-bottom: 0 !important;
        }
        
        .tip-item:last-child {
          margin-bottom: 0 !important;
        }
      `}</style>
    </div>
  );
}

export default Dashboard;