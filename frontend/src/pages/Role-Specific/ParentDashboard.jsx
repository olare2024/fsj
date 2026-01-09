import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { parentAPI } from '../../services/parentAPI';
import { 
  ArrowLeftIcon, 
  PersonIcon, 
  CalendarIcon, 
  GraphUpIcon,
  JournalCheckIcon, 
  CalendarCheckIcon, 
  PeopleIcon, 
  EnvelopeIcon,
  TelephoneIcon, 
  ChatIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  WarningIcon, 
  InfoIcon, 
  BellIcon, 
  BookIcon, 
  AwardIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  DashIcon,
  EyeIcon,
  DownloadIcon,
  PrintIcon,
  HistoryIcon,
  FileTextIcon,
  CreditCardIcon,
  ShieldCheckIcon
} from '../../components/Icons';

function ParentDashboard() {
  const { currentUser, isParent, getDashboardUrl } = useAuth();
  const navigate = useNavigate();
  const [selectedChild, setSelectedChild] = useState(0);
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [children, setChildren] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
  }, [selectedChild]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await parentAPI.getDashboardData();
      setDashboardData(response.data);
      setChildren(response.data.children || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const currentChild = children[selectedChild] || {};
  const currentData = dashboardData.childData?.[selectedChild] || {};

  // Enhanced quick actions with working links and role-based access
  const quickActions = [
    {
      title: 'Progress Reports',
      icon: GraphUpIcon,
      link: '/child-progress',
      color: 'primary',
      description: 'View detailed progress reports',
      badge: currentData.reports?.new || 0,
      permission: true // All parents can access
    },
    {
      title: 'View Grades',
      icon: JournalCheckIcon,
      link: '/grades',
      color: 'success',
      description: 'Check academic performance',
      badge: currentData.grades?.newAssignments || 0,
      permission: true
    },
    {
      title: 'Attendance',
      icon: CalendarCheckIcon,
      link: '/attendance',
      color: 'warning',
      description: 'Monitor attendance records',
      badge: currentData.attendance?.concerns || 0,
      permission: true
    },
    {
      title: 'Parent Meetings',
      icon: PeopleIcon,
      link: '/parent-meetings',
      color: 'info',
      description: 'Schedule and view meetings',
      badge: currentData.meetings?.upcoming || 0,
      permission: true
    },
    {
      title: 'Fee Statements',
      icon: CreditCardIcon,
      link: '/parent/billing',
      color: 'danger',
      description: 'View and pay fees',
      badge: currentData.financial?.pendingPayments || 0,
      permission: true
    },
    {
      title: 'School Calendar',
      icon: CalendarIcon,
      link: '/calendar',
      color: 'secondary',
      description: 'Upcoming events and holidays',
      badge: dashboardData.upcomingEvents?.length || 0,
      permission: true
    },
    {
      title: 'Assignments',
      icon: BookIcon,
      link: '/assignments',
      color: 'primary',
      description: 'View homework and projects',
      badge: currentData.assignments?.pending || 0,
      permission: true
    },
    {
      title: 'Behavior Reports',
      icon: ShieldCheckIcon,
      link: '/behavior-reports',
      color: 'info',
      description: 'Behavior and conduct reports',
      badge: currentData.behavior?.reports || 0,
      permission: true
    },
    {
      title: 'Report Cards',
      icon: FileTextIcon,
      link: '/report-cards',
      color: 'success',
      description: 'View academic report cards',
      badge: currentData.reports?.newReportCards || 0,
      permission: true
    },
    {
      title: 'Make Payment',
      icon: CreditCardIcon,
      link: '/parent/make-payment',
      color: 'warning',
      description: 'Pay school fees online',
      badge: currentData.financial?.overdue || 0,
      permission: true
    },
    {
      title: 'Teacher Contacts',
      icon: PeopleIcon,
      link: '/teacher-contacts',
      color: 'info',
      description: 'View teacher information',
      badge: 0,
      permission: true
    },
    {
      title: 'School Notices',
      icon: BellIcon,
      link: '/notices',
      color: 'secondary',
      description: 'Important school announcements',
      badge: dashboardData.announcements?.length || 0,
      permission: true
    }
  ];

  // Enhanced communication actions with actual functionality
  const communicationActions = [
    {
      title: 'Email Teacher',
      icon: EnvelopeIcon,
      action: 'email',
      color: 'primary',
      description: 'Send email to class teacher',
      handler: () => {
        const teacherEmail = currentChild.teacherEmail || 'teacher@delvok.academy';
        window.location.href = `mailto:${teacherEmail}?subject=Regarding ${currentChild.name}'s Progress&body=Dear Teacher,%0D%0A%0D%0AI would like to discuss ${currentChild.name}'s progress.%0D%0A%0D%0ARegards,%0D%0A${currentUser?.firstName} ${currentUser?.lastName}`;
      }
    },
    {
      title: 'Call School Office',
      icon: TelephoneIcon,
      action: 'call',
      color: 'success',
      description: 'Contact school administration',
      handler: () => {
        window.location.href = 'tel:+254700000000';
      }
    },
    {
      title: 'Schedule Conference',
      icon: CalendarIcon,
      action: 'schedule',
      color: 'warning',
      description: 'Book parent-teacher meeting',
      handler: () => {
        navigate('/parent-meetings?action=schedule');
      }
    },
    {
      title: 'Message Administrator',
      icon: ChatIcon,
      action: 'message',
      color: 'info',
      description: 'Send message to admin',
      handler: () => {
        navigate('/communications?type=admin&recipient=School+Administration');
      }
    },
    {
      title: 'Emergency Contact',
      icon: TelephoneIcon,
      action: 'emergency',
      color: 'danger',
      description: 'Urgent school contact',
      handler: () => {
        window.location.href = 'tel:+254711000000';
      }
    },
    {
      title: 'School Portal',
      icon: PersonIcon,
      action: 'portal',
      color: 'secondary',
      description: 'Access main school portal',
      handler: () => {
        navigate('/parent-portal');
      }
    }
  ];

  // Enhanced status indicators
  const getTrendIcon = (trend, value) => {
    const trendConfig = {
      'up': { icon: TrendingUpIcon, color: 'success', text: 'Improving' },
      'down': { icon: TrendingDownIcon, color: 'danger', text: 'Declining' },
      'stable': { icon: DashIcon, color: 'warning', text: 'Stable' },
      'new': { icon: TrendingUpIcon, color: 'info', text: 'New' }
    };
    
    const config = trendConfig[trend] || trendConfig.stable;
    const IconComponent = config.icon;
    
    return (
      <div className="d-flex align-items-center">
        <IconComponent className={`text-${config.color} me-1`} size={14} />
        <small className={`text-${config.color} fw-medium`}>
          {config.text} {value ? `(${value}%)` : ''}
        </small>
      </div>
    );
  };

  const getAttendanceStatus = (attendance) => {
    if (!attendance) return { variant: 'secondary', text: 'No data', icon: InfoIcon };
    
    const totalDays = attendance.present + attendance.absent + attendance.late;
    const attendanceRate = totalDays > 0 ? (attendance.present / totalDays) * 100 : 0;
    
    if (attendanceRate >= 95) return { variant: 'success', text: 'Excellent', icon: CheckCircleIcon };
    if (attendanceRate >= 90) return { variant: 'info', text: 'Good', icon: CheckCircleIcon };
    if (attendanceRate >= 85) return { variant: 'warning', text: 'Needs Attention', icon: WarningIcon };
    return { variant: 'danger', text: 'Concerning', icon: XCircleIcon };
  };

  const getGradeStatus = (grade) => {
    if (!grade) return { variant: 'secondary', text: 'No data', icon: InfoIcon };
    
    if (grade >= 90) return { variant: 'success', text: 'Excellent', icon: CheckCircleIcon };
    if (grade >= 80) return { variant: 'info', text: 'Good', icon: CheckCircleIcon };
    if (grade >= 70) return { variant: 'warning', text: 'Satisfactory', icon: WarningIcon };
    return { variant: 'danger', text: 'Needs Improvement', icon: XCircleIcon };
  };

  const getFinancialStatus = (financial) => {
    if (!financial) return { variant: 'secondary', text: 'No data', icon: InfoIcon };
    
    if (financial.balance === 0) return { variant: 'success', text: 'Paid', icon: CheckCircleIcon };
    if (financial.overdue > 0) return { variant: 'danger', text: 'Overdue', icon: XCircleIcon };
    if (financial.balance > 0) return { variant: 'warning', text: 'Pending', icon: WarningIcon };
    return { variant: 'info', text: 'Current', icon: InfoIcon };
  };

  // Export functions
  const exportReport = async (type) => {
    try {
      console.log(`Exporting ${type} report for ${currentChild.name}`);
      // Implement actual export functionality
      const response = await parentAPI.exportReport(type, currentChild.id);
      if (response.success) {
        // Create download link
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${currentChild.name}_${type}_report_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const printReport = () => {
    window.print();
  };

  // Enhanced child selection handler
  const handleChildSelect = (index) => {
    setSelectedChild(index);
    // Update URL to reflect selected child
    const childId = children[index]?.id;
    if (childId) {
      window.history.replaceState(null, '', `?child=${childId}`);
    }
  };

  // Enhanced communication handler
  const handleCommunication = (actionConfig) => {
    if (actionConfig.handler) {
      actionConfig.handler();
    }
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 text-muted">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      {/* Header Section */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 mb-2 text-dark fw-bold">Parent Dashboard</h1>
          <p className="lead text-muted mb-0">
            Welcome back, {currentUser?.firstName || 'Parent'}! {children.length > 0 ? 
              `Monitoring ${children.length} child${children.length > 1 ? 'ren' : ''}'s progress.` : 
              'No children registered yet.'}
          </p>
        </div>
        <div className="d-flex gap-2">
          <button 
            className="btn btn-outline-primary btn-sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <HistoryIcon className={`me-2 ${refreshing ? 'spin' : ''}`} size={16} />
            {refreshing ? 'Refreshing...' : 'Refresh Data'}
          </button>
          <Link to="/parent-portal" className="btn btn-outline-secondary btn-sm">
            <ArrowLeftIcon className="me-2" size={16} />
            Back to Portal
          </Link>
        </div>
      </div>

      {/* Child Selection with Enhanced UI */}
      {children.length > 0 && (
        <div className="card shadow-sm border-0 mb-4">
          <div className="card-header bg-white border-0 py-3">
            <div className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0 fw-semibold text-dark">Select Child</h5>
              <span className="badge bg-primary rounded-pill">{children.length} Registered</span>
            </div>
          </div>
          <div className="card-body">
            <div className="row g-3">
              {children.map((child, index) => {
                const childData = dashboardData.childData?.[index] || {};
                const attendanceStatus = getAttendanceStatus(childData.attendance);
                const gradeStatus = getGradeStatus(childData.grades?.average);
                const financialStatus = getFinancialStatus(childData.financial);
                
                return (
                  <div key={child.id} className="col-md-6 col-lg-4 col-xl-3">
                    <div 
                      className={`card cursor-pointer border-2 transition-all h-100 ${
                        selectedChild === index ? 'border-primary shadow-lg' : 'border-light'
                      }`}
                      onClick={() => handleChildSelect(index)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="card-body">
                        <div className="d-flex align-items-start">
                          <div className="child-avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3 flex-shrink-0"
                               style={{width: '50px', height: '50px', fontSize: '1.1rem', fontWeight: '600'}}>
                            {child.avatar || child.name?.charAt(0) || 'C'}
                          </div>
                          <div className="flex-grow-1">
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              <h6 className="mb-0 fw-semibold text-dark">{child.name || 'Child Name'}</h6>
                              {selectedChild === index && (
                                <CheckCircleIcon className="text-primary flex-shrink-0" size={18} />
                              )}
                            </div>
                            <p className="text-muted mb-2 small">
                              <BookIcon size={12} className="me-1" />
                              {child.grade || 'Grade'} • {child.teacher || 'Teacher'}
                            </p>
                            
                            {/* Status Indicators */}
                            <div className="d-flex flex-column gap-2">
                              <div className="d-flex justify-content-between align-items-center">
                                <small className="text-muted">Attendance</small>
                                <span className={`badge bg-${attendanceStatus.variant} d-flex align-items-center rounded-pill`}>
                                  <attendanceStatus.icon size={10} className="me-1" />
                                  {attendanceStatus.text}
                                </span>
                              </div>
                              <div className="d-flex justify-content-between align-items-center">
                                <small className="text-muted">Grades</small>
                                <span className={`badge bg-${gradeStatus.variant} d-flex align-items-center rounded-pill`}>
                                  <gradeStatus.icon size={10} className="me-1" />
                                  {childData.grades?.average ? `${childData.grades.average}%` : gradeStatus.text}
                                </span>
                              </div>
                              <div className="d-flex justify-content-between align-items-center">
                                <small className="text-muted">Fees</small>
                                <span className={`badge bg-${financialStatus.variant} d-flex align-items-center rounded-pill`}>
                                  <financialStatus.icon size={10} className="me-1" />
                                  {financialStatus.text}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Child Overview Stats */}
      {currentChild && (
        <>
          {/* Stats Header */}
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h4 className="mb-0 text-dark">
              {currentChild.name}'s Overview
              {currentData.grades?.average && (
                <span className="badge bg-success ms-2">
                  Overall: {currentData.grades.average}%
                </span>
              )}
            </h4>
            <div className="d-flex gap-2">
              <button 
                className="btn btn-sm btn-outline-primary"
                onClick={() => exportReport('comprehensive')}
              >
                <DownloadIcon size={14} className="me-1" />
                Export Report
              </button>
              <button 
                className="btn btn-sm btn-outline-secondary"
                onClick={printReport}
              >
                <PrintIcon size={14} className="me-1" />
                Print
              </button>
              <Link 
                to={`/child-progress?child=${currentChild.id}`}
                className="btn btn-sm btn-primary"
              >
                <EyeIcon size={14} className="me-1" />
                View Details
              </Link>
            </div>
          </div>

          <div className="row mb-4">
            {/* Attendance Card */}
            <div className="col-md-3 mb-3">
              <div className="card border-0 bg-primary text-white shadow-sm h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      <h3 className="mb-1">{currentData.attendance?.present || 0}</h3>
                      <p className="mb-2 opacity-75">Days Present</p>
                      <div className="d-flex flex-wrap gap-1 mb-2">
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          {currentData.attendance?.absent || 0} absences
                        </small>
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          {currentData.attendance?.late || 0} late
                        </small>
                      </div>
                      {getTrendIcon(currentData.attendance?.trend, currentData.attendance?.change)}
                    </div>
                    <div className="text-end">
                      <CalendarCheckIcon size={28} />
                      <div className="mt-1">
                        <small className="opacity-75">
                          {currentData.attendance?.rate || 0}% Rate
                        </small>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <Link 
                      to="/attendance" 
                      className="btn btn-sm btn-light text-primary w-100"
                    >
                      View Attendance Details
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Grades Card */}
            <div className="col-md-3 mb-3">
              <div className="card border-0 bg-success text-white shadow-sm h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      <h3 className="mb-1">{currentData.grades?.average || '0'}%</h3>
                      <p className="mb-2 opacity-75">Average Grade</p>
                      <div className="d-flex flex-wrap gap-1 mb-2">
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          {currentData.grades?.subjects || 0} subjects
                        </small>
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          Rank: {currentData.grades?.rank || 'N/A'}
                        </small>
                      </div>
                      {getTrendIcon(currentData.grades?.trend, currentData.grades?.change)}
                    </div>
                    <div className="text-end">
                      <GraphUpIcon size={28} />
                      <div className="mt-1">
                        <small className="opacity-75">
                          {currentData.grades?.completedAssignments || 0} completed
                        </small>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <Link 
                      to="/grades" 
                      className="btn btn-sm btn-light text-success w-100"
                    >
                      View Grade Details
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Assignments Card */}
            <div className="col-md-3 mb-3">
              <div className="card border-0 bg-warning text-white shadow-sm h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      <h3 className="mb-1">{currentData.assignments?.pending || 0}</h3>
                      <p className="mb-2 opacity-75">Pending Assignments</p>
                      <div className="d-flex flex-wrap gap-1 mb-2">
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          {currentData.assignments?.overdue || 0} overdue
                        </small>
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          {currentData.assignments?.completed || 0} done
                        </small>
                      </div>
                      <small className="opacity-75">
                        Next due: {currentData.assignments?.nextDue || 'None'}
                      </small>
                    </div>
                    <div className="text-end">
                      <JournalCheckIcon size={28} />
                      <div className="mt-1">
                        <small className="opacity-75">
                          {currentData.assignments?.completionRate || 0}% Complete
                        </small>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <Link 
                      to="/assignments" 
                      className="btn btn-sm btn-light text-warning w-100"
                    >
                      View Assignments
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Financial Card */}
            <div className="col-md-3 mb-3">
              <div className="card border-0 bg-info text-white shadow-sm h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      <h3 className="mb-1">
                        KES {currentData.financial?.balance?.toLocaleString() || '0'}
                      </h3>
                      <p className="mb-2 opacity-75">Fee Balance</p>
                      <div className="d-flex flex-wrap gap-1 mb-2">
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          {currentData.financial?.overdue || 0} overdue
                        </small>
                        <small className="opacity-75 bg-white bg-opacity-20 px-2 py-1 rounded">
                          Due: {currentData.financial?.nextDue || 'N/A'}
                        </small>
                      </div>
                      <small className="opacity-75">
                        Last payment: {currentData.financial?.lastPayment || 'N/A'}
                      </small>
                    </div>
                    <div className="text-end">
                      <CreditCardIcon size={28} />
                      <div className="mt-1">
                        <small className="opacity-75">
                          Status: {getFinancialStatus(currentData.financial).text}
                        </small>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3">
                    <Link 
                      to="/parent/billing" 
                      className="btn btn-sm btn-light text-info w-100"
                    >
                      View Fee Statement
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Quick Actions Grid */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0 fw-semibold text-dark">Quick Actions</h5>
                <small className="text-muted">
                  {currentChild.name ? `Actions for ${currentChild.name}` : 'Select a child to view actions'}
                </small>
              </div>
            </div>
            <div className="card-body">
              <div className="row g-3">
                {quickActions.map((action, index) => (
                  <div key={index} className="col-6 col-md-4 col-lg-3">
                    <Link 
                      to={action.link} 
                      className="text-decoration-none"
                      state={{ childId: currentChild.id, childName: currentChild.name }}
                    >
                      <div className="card h-100 border-0 shadow-sm-hover text-center transition-all position-relative">
                        {action.badge > 0 && (
                          <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                            {action.badge > 99 ? '99+' : action.badge}
                          </span>
                        )}
                        <div className="card-body p-3">
                          <div className={`bg-${action.color} bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3`}
                               style={{width: '60px', height: '60px'}}>
                            <action.icon size={24} className={`text-${action.color}`} />
                          </div>
                          <h6 className="card-title mb-1 fw-semibold text-dark">{action.title}</h6>
                          <small className="text-muted">{action.description}</small>
                        </div>
                      </div>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Left Column - Main Content */}
        <div className="col-lg-8">
          {/* Recent Activity */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
              <h5 className="mb-0 fw-semibold text-dark">Recent Activity</h5>
              <Link to="/activity" className="btn btn-sm btn-outline-primary">
                <EyeIcon size={14} className="me-1" />
                View All Activity
              </Link>
            </div>
            <div className="card-body">
              {dashboardData.recentActivity?.length > 0 ? (
                <div className="list-group list-group-flush">
                  {dashboardData.recentActivity.map((activity, index) => (
                    <div key={index} className="list-group-item px-0 py-3 border-0">
                      <div className="d-flex align-items-start">
                        <div className={`rounded-circle d-flex align-items-center justify-content-center me-3 flex-shrink-0 
                                      ${activity.type === 'grade' ? 'bg-success' : 
                                        activity.type === 'attendance' ? 'bg-warning' : 
                                        activity.type === 'behavior' ? 'bg-info' : 'bg-secondary'}`}
                             style={{width: '40px', height: '40px'}}>
                          {activity.type === 'grade' && <JournalCheckIcon size={18} className="text-white" />}
                          {activity.type === 'attendance' && <CalendarCheckIcon size={18} className="text-white" />}
                          {activity.type === 'behavior' && <ShieldCheckIcon size={18} className="text-white" />}
                          {activity.type === 'general' && <BellIcon size={18} className="text-white" />}
                        </div>
                        <div className="flex-grow-1">
                          <div className="d-flex justify-content-between align-items-start mb-1">
                            <h6 className="mb-0 fw-semibold text-dark">{activity.action}</h6>
                            <small className="text-muted">
                              <ClockIcon size={12} className="me-1" />
                              {activity.time}
                            </small>
                          </div>
                          <p className="text-muted mb-1 small">{activity.course}</p>
                          <small className="text-dark">{activity.details}</small>
                          {activity.child && (
                            <small className="badge bg-light text-dark ms-2">
                              {activity.child}
                            </small>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <InfoIcon size={48} className="text-muted mb-3" />
                  <h5 className="text-muted">No Recent Activity</h5>
                  <p className="text-muted">Activity will appear here as it happens.</p>
                  <Link to="/child-progress" className="btn btn-primary btn-sm">
                    Check Progress
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Sidebar */}
        <div className="col-lg-4">
          {/* Upcoming Events */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 d-flex justify-content-between align-items-center py-3">
              <h5 className="mb-0 fw-semibold text-dark">Upcoming Events</h5>
              <Link to="/calendar" className="btn btn-sm btn-outline-primary">
                <CalendarIcon className="me-1" size={14} />
                View Calendar
              </Link>
            </div>
            <div className="card-body">
              {dashboardData.upcomingEvents?.length > 0 ? (
                <div className="list-group list-group-flush">
                  {dashboardData.upcomingEvents.slice(0, 5).map((event, index) => (
                    <Link 
                      key={index}
                      to={`/calendar?event=${event.id}`}
                      className="list-group-item px-0 py-3 border-0 text-decoration-none"
                    >
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <h6 className="mb-0 fw-semibold text-dark">{event.title}</h6>
                        <span className={`badge ${
                          event.type === 'meeting' ? 'bg-primary' : 
                          event.type === 'exam' ? 'bg-danger' :
                          event.type === 'holiday' ? 'bg-success' : 'bg-warning'
                        } rounded-pill`}>
                          {event.type}
                        </span>
                      </div>
                      <div className="d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          <CalendarIcon size={12} className="me-1" />
                          {event.date} • {event.time}
                        </small>
                        {event.child && (
                          <small className={`badge ${
                            event.child === currentChild.name ? 'bg-primary' : 'bg-secondary'
                          } rounded-pill`}>
                            {event.child}
                          </small>
                        )}
                      </div>
                      {event.location && (
                        <small className="text-muted d-block mt-1">
                          📍 {event.location}
                        </small>
                      )}
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-3">
                  <CalendarIcon size={32} className="text-muted mb-2" />
                  <p className="text-muted small mb-0">No upcoming events</p>
                  <Link to="/calendar" className="btn btn-outline-primary btn-sm mt-2">
                    View School Calendar
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Quick Communication */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold text-dark">Quick Communication</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                {communicationActions.map((action, index) => (
                  <button 
                    key={index}
                    className={`btn btn-outline-${action.color} text-start d-flex align-items-center p-3`}
                    onClick={() => handleCommunication(action)}
                  >
                    <action.icon className="me-3" size={18} />
                    <div className="text-start">
                      <div className="fw-semibold text-dark">{action.title}</div>
                      <small className="text-muted">{action.description}</small>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* School Announcements */}
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold text-dark">
                <BellIcon className="me-2" size={18} />
                School Announcements
              </h5>
            </div>
            <div className="card-body">
              {dashboardData.announcements?.length > 0 ? (
                dashboardData.announcements.slice(0, 3).map((announcement, index) => (
                  <div key={index} className={`alert alert-${announcement.type} mb-3 border-0`}>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <h6 className="alert-heading fw-semibold mb-1">{announcement.title}</h6>
                      <small className="text-muted">
                        <ClockIcon size={12} className="me-1" />
                        {announcement.date}
                      </small>
                    </div>
                    <p className="small mb-2">{announcement.message}</p>
                    {announcement.link && (
                      <Link 
                        to={announcement.link} 
                        className="btn btn-sm btn-outline-primary mt-1"
                      >
                        Read More
                      </Link>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-3">
                  <BellIcon size={32} className="text-muted mb-2" />
                  <p className="text-muted small mb-0">No current announcements</p>
                </div>
              )}
              <div className="text-center">
                <Link to="/notices" className="btn btn-outline-primary btn-sm">
                  View All Announcements
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom CSS */}
      <style jsx>{`
        .shadow-sm-hover:hover {
          box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
          transform: translateY(-2px);
        }
        .transition-all {
          transition: all 0.2s ease-in-out;
        }
        .cursor-pointer {
          cursor: pointer;
        }
        .border-2 {
          border-width: 2px!important;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @media print {
          .btn, .badge, .card-header {
            display: none !important;
          }
          .card {
            border: 1px solid #ddd !important;
            box-shadow: none !important;
          }
        }
      `}</style>
    </div>
  );
}

export default ParentDashboard;