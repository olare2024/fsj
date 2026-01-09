// src/App.jsx - COMPLETE FIXED VERSION
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext.jsx';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './App.css';

// Layout Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import AuthRedirectGuard from './components/AuthRedirectGuard';
import RoleBasedDashboard from './components/RoleBasedDashboard';

// ==================== COMPONENT IMPORTS ====================

// Public Pages
import Home from './pages/Home';
import About from './pages/About';
import Academics from './pages/Academics';
import Contact from './pages/Contact';
import News from './pages/News';
import Events from './pages/Events';
import Gallery from './pages/Gallery';
import Club from './pages/Club';
import Sports from './pages/Sports';
import Dashboard from './pages/Dashboard';

// Auth Pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import ForgotPassword from './pages/Auth/ForgotPassword';
import ResetPassword from './pages/Auth/ResetPassword';
import OTPVerification from './pages/Auth/OTPVerification';
import VerifyAccount from './pages/Auth/VerifyAccount';
import CompleteProfile from './pages/Auth/CompleteProfile';

// Role-Specific Portal Pages
import AdminPortal from './pages/Portals/AdminPortal';
import TeacherPortal from './pages/Portals/TeacherPortal';
import StudentPortal from './pages/Portals/StudentPortal';
import ParentPortal from './pages/Portals/ParentPortal';
import AccountantPortal from './pages/Portals/AccountantPortal';
import StaffPortal from './pages/Portals/StaffPortal';
import LibraryPortal from './pages/Portals/LibraryPortal';
import ITPortal from './pages/Portals/ITPortal';
import CounselorPortal from './pages/Portals/CounselorPortal';

// Additional Portals
import HeadTeacherPortal from './pages/Portals/HeadTeacherPortal';
import CurriculumPortal from './pages/Portals/CurriculumPortal';

// Academic Pages
import Curriculum from './pages/Academic/Curriculum';
import Programs from './pages/Academic/Programs';
import Departments from './pages/Academic/Departments';
import Faculty from './pages/Academic/Faculty';
import Courses from './pages/Academic/Courses';

// Student Life Pages
import StudentClubs from './pages/Student_Life/StudentClubs';
import Athletics from './pages/Student_Life/Athletics';
import Arts from './pages/Student_Life/Arts';
import StudentServices from './pages/Student_Life/StudentServices';
import Counseling from './pages/Student_Life/Counseling';

// Admission Pages
import Apply from './pages/Admission/Apply';
import Requirements from './pages/Admission/Requirements';
import Tuition from './pages/Admission/Tuition';
import Scholarships from './pages/Admission/Scholarships';
import CampusTour from './pages/Admission/CampusTour';

// Resource Pages
import Library from './pages/Resource_mngt/Library';
import Calendar from './pages/Resource_mngt/Calendar';
import Documents from './pages/Resource_mngt/Documents';
import Resources from './pages/Resource_mngt/Resources';
import Downloads from './pages/Resource_mngt/Downloads';

// Profile & Settings
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import Notifications from './pages/Notifications';

// Academic Management
import Grades from './pages/Academic_mngt/Grades';
import Attendance from './pages/Academic_mngt/Attendance';
import Assignments from './pages/Academic_mngt/Assignments';
import Timetable from './pages/Academic_mngt/Timetable';
import Exams from './pages/Academic_mngt/Exams';
import Reports from './pages/Academic_mngt/Reports';

// ==================== FINANCE MODULE PAGES ====================
import FinanceDashboard from './pages/Finance/FinanceDashboard';
import FeeStructure from './pages/Finance/FeeStructure';
import Billing from './pages/Finance/Billing';
import PaymentHistory from './pages/Finance/PaymentHistory';
import InvoiceManagement from './pages/Finance/InvoiceManagement';

// Receipt Management
import Receipts from './pages/Finance/Receipts/Receipts';
import CreateReceipt from './pages/Finance/Receipts/CreateReceipt';
import ReceiptDetail from './pages/Finance/Receipts/ReceiptDetail';
import BulkReceiptUpload from './pages/Finance/Receipts/BulkReceiptUpload';

// Payment Management
import Payments from './pages/Finance/Payments/Payments';
import CreatePayment from './pages/Finance/Payments/CreatePayment';
import PaymentDetail from './pages/Finance/Payments/PaymentDetail';
import PaymentApproval from './pages/Finance/Payments/PaymentApproval';

// Debt Management
import DebtRecords from './pages/Finance/Debt/DebtRecords';
import StudentDebtOverview from './pages/Finance/Debt/StudentDebtOverview';
import DebtReports from './pages/Finance/Debt/DebtReports';

// Financial Reports
import FinancialReports from './pages/Finance/Reports/FinancialReports';
import IncomeStatement from './pages/Finance/Reports/IncomeStatement';
import BalanceSheet from './pages/Finance/Reports/BalanceSheet';
import CashFlow from './pages/Finance/Reports/CashFlow';
import FeeCollectionReport from './pages/Finance/Reports/FeeCollectionReport';

// Accountant Workspace
import AccountantWorkspace from './pages/Finance/Accountant/AccountantWorkspace';
import FinancialApprovals from './pages/Finance/Accountant/FinancialApprovals';
import Reconciliation from './pages/Finance/Accountant/Reconciliation';
import AuditTrail from './pages/Finance/Accountant/AuditTrail';

// Parent Finance Pages
import ParentBilling from './pages/Finance/Parent/ParentBilling';
import ChildFeeStatement from './pages/Finance/Parent/ChildFeeStatement';
import MakePayment from './pages/Finance/Parent/MakePayment';

// Admin Management
import UserManagement from './pages/Admin/UserManagement';
import SystemSettings from './pages/Admin/SystemSettings';
import Analytics from './pages/Admin/Analytics';
import Logs from './pages/Admin/Logs';
import AcademicManagement from './pages/Admin/AcademicManagement';
import SystemAdministration from './pages/Admin/SystemAdministration';
import AnalyticsAI from './pages/Admin/AnalyticsAI';
import DigitalCampus from './pages/Admin/DigitalCampus';
import ActivityLogs from './pages/Admin/ActivityLogs';

// Teacher Specific
import TeacherDashboard from './pages/Teacher/TeacherDashboard';
import GradeManagement from './pages/Teacher/GradeManagement';
import AttendanceManagement from './pages/Teacher/AttendanceManagement';
import TeacherAssignments from './pages/Teacher/TeacherAssignments';
import CreateAssignment from './pages/Teacher/CreateAssignment';
import GradeAssignment from './pages/Teacher/GradeAssignment';
import TeacherAttendance from './pages/Teacher/TeacherAttendance';
import TeacherTimetable from './pages/Teacher/TeacherTimetable';
import TeacherGrades from './pages/Teacher/TeacherGrades';
import TeacherReports from './pages/Teacher/TeacherReports';
import AssignmentDetail from './pages/Teacher/AssignmentDetail';

// Parent Specific
import ChildProgress from './pages/Parents/ChildProgress';
import ParentMeetings from './pages/Parents/ParentMeetings';

// Utility Pages
import NotFound from './pages/Utility/NotFound';
import Unauthorized from './pages/Utility/Unauthorized';
import SearchResults from './pages/Utility/SearchResults';
import PrivacyPolicy from './pages/Utility/PrivacyPolicy';
import TermsOfService from './pages/Utility/TermsOfService';

// Additional Public Pages
import FacultyDirectory from './pages/Public/FacultyDirectory';
import SchoolHistory from './pages/Public/SchoolHistory';
import MissionVision from './pages/Public/MissionVision';
import Leadership from './pages/Public/Leadership';
import Careers from './pages/Public/Careers';
import Testimonials from './pages/Public/Testimonials';

// Additional Academic Pages
import ElementarySchool from './pages/Academic/ElementarySchool';
import MiddleSchool from './pages/Academic/MiddleSchool';
import HighSchool from './pages/Academic/HighSchool';
import APCourses from './pages/Academic/APCourses';
import HonorsProgram from './pages/Academic/HonorsProgram';
import SummerPrograms from './pages/Academic/SummerPrograms';

// Additional Campus Life Pages
import Dormitories from './pages/Campus_Life/Dormitories';
import Dining from './pages/Campus_Life/Dining';
import HealthServices from './pages/Campus_Life/HealthServices';
import Transportation from './pages/Campus_Life/Transportation';
import Safety from './pages/Campus_Life/Safety';
import StudentHandbook from './pages/Campus_Life/StudentHandbook';

// Additional Admission Pages
import InternationalStudents from './pages/Admission/InternationalStudents';
import TransferStudents from './pages/Admission/TransferStudents';
import ApplicationStatus from './pages/Admission/ApplicationStatus';
import FinancialAid from './pages/Admission/FinancialAid';

// Additional Resource Pages
import ParentResources from './pages/Resource/ParentResources';
import TeacherResources from './pages/Resource/TeacherResources';
import ResearchPortal from './pages/Resource/ResearchPortal';
import TechSupport from './pages/Resource/TechSupport';

// Additional Management Pages
import CourseManagement from './pages/Management/CourseManagement';
import ClassManagement from './pages/Management/ClassManagement';
import EnrollmentManagement from './pages/Management/EnrollmentManagement';
import Communications from './pages/Management/Communications';

// Loading component for better UX
const LoadingSpinner = () => (
  <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
    <div className="spinner-border text-primary" role="status">
      <span className="visually-hidden">Loading...</span>
    </div>
  </div>
);

// Route Debugger Component
const RouteDebugger = () => {
  const { currentUser, getDashboardUrl } = useAuth();
  const [hasLogged, setHasLogged] = React.useState(false);
  
  React.useEffect(() => {
    if (currentUser && !hasLogged && process.env.NODE_ENV === 'development') {
      console.log('🔍 ROUTE DEBUG:');
      console.log('Current User:', currentUser);
      console.log('Calculated Dashboard URL:', getDashboardUrl());
      console.log('Current Path:', window.location.pathname);
      setHasLogged(true);
    }
  }, [currentUser, hasLogged, getDashboardUrl]);
  
  return null;
};

function AppContent() {
  const { isAuthenticated, currentUser, loading } = useAuth();

  // Show loading spinner while checking authentication
  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="App">
      <RouteDebugger />
      <Navbar />
      <main className="main-content">
        <Routes>
          {/* ==================== PUBLIC ROUTES ==================== */}
          
          {/* Main Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/academics" element={<Academics />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/news" element={<News />} />
          <Route path="/events" element={<Events />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/clubs" element={<Club />} />
          <Route path="/sports" element={<Sports />} />

          {/* About Section */}
          <Route path="/school-history" element={<SchoolHistory />} />
          <Route path="/mission-vision" element={<MissionVision />} />
          <Route path="/leadership" element={<Leadership />} />
          <Route path="/careers" element={<Careers />} />
          <Route path="/testimonials" element={<Testimonials />} />
          <Route path="/faculty-directory" element={<FacultyDirectory />} />
          
          {/* Academic Public Routes */}
          <Route path="/curriculum" element={<Curriculum />} />
          <Route path="/programs" element={<Programs />} />
          <Route path="/departments" element={<Departments />} />
          <Route path="/faculty" element={<Faculty />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/elementary-school" element={<ElementarySchool />} />
          <Route path="/middle-school" element={<MiddleSchool />} />
          <Route path="/high-school" element={<HighSchool />} />
          <Route path="/ap-courses" element={<APCourses />} />
          <Route path="/honors-program" element={<HonorsProgram />} />
          <Route path="/summer-programs" element={<SummerPrograms />} />
          
          {/* Student Life */}
          <Route path="/student-clubs" element={<StudentClubs />} />
          <Route path="/athletics" element={<Athletics />} />
          <Route path="/arts" element={<Arts />} />
          <Route path="/student-services" element={<StudentServices />} />
          <Route path="/counseling" element={<Counseling />} />
          <Route path="/dormitories" element={<Dormitories />} />
          <Route path="/dining" element={<Dining />} />
          <Route path="/health-services" element={<HealthServices />} />
          <Route path="/transportation" element={<Transportation />} />
          <Route path="/safety" element={<Safety />} />
          <Route path="/student-handbook" element={<StudentHandbook />} />
          
          {/* Admission */}
          <Route path="/apply" element={<Apply />} />
          <Route path="/requirements" element={<Requirements />} />
          <Route path="/tuition" element={<Tuition />} />
          <Route path="/scholarships" element={<Scholarships />} />
          <Route path="/campus-tour" element={<CampusTour />} />
          <Route path="/international-students" element={<InternationalStudents />} />
          <Route path="/transfer-students" element={<TransferStudents />} />
          <Route path="/application-status" element={<ApplicationStatus />} />
          <Route path="/financial-aid" element={<FinancialAid />} />
          
          {/* Resources */}
          <Route path="/library" element={<Library />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/downloads" element={<Downloads />} />
          <Route path="/parent-resources" element={<ParentResources />} />
          <Route path="/teacher-resources" element={<TeacherResources />} />
          <Route path="/research-portal" element={<ResearchPortal />} />
          <Route path="/tech-support" element={<TechSupport />} />
          
          {/* Legal */}
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/terms-of-service" element={<TermsOfService />} />

          {/* Search */}
          <Route path="/search" element={<SearchResults />} />

          {/* ==================== AUTHENTICATION ROUTES ==================== */}
          <Route 
            path="/login" 
            element={
              <AuthRedirectGuard>
                <Login />
              </AuthRedirectGuard>
            } 
          />
          <Route 
            path="/register" 
            element={
              <AuthRedirectGuard>
                <Register />
              </AuthRedirectGuard>
            } 
          />
          <Route 
            path="/forgot-password" 
            element={
              <AuthRedirectGuard>
                <ForgotPassword />
              </AuthRedirectGuard>
            } 
          />
          <Route 
            path="/reset-password" 
            element={
              <AuthRedirectGuard>
                <ResetPassword />
              </AuthRedirectGuard>
            } 
          />
          <Route 
            path="/verify-account" 
            element={
              <AuthRedirectGuard>
                <VerifyAccount />
              </AuthRedirectGuard>
            } 
          />
          <Route 
            path="/verify-otp" 
            element={
              <AuthRedirectGuard>
                <OTPVerification />
              </AuthRedirectGuard>
            } 
          />

          {/* ==================== PORTAL & DASHBOARD ROUTES ==================== */}
          
          {/* Universal Dashboard Route - Handles all roles */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <RoleBasedDashboard />
              </ProtectedRoute>
            } 
          />

          {/* Legacy Dashboard Route (optional) */}
          <Route 
            path="/legacy-dashboard" 
            element={
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin', 'parent', 'accountant', 'office_staff']}>
                <Dashboard />
              </ProtectedRoute>
            } 
          />

          {/* Role-Specific Portal Routes - Updated to match AuthContext */}
          <Route 
            path="/admin/admin-portal" 
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/teacher-portal" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/student/student-portal" 
            element={
              <ProtectedRoute requiredRole="student">
                <StudentPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/parent/parent-portal" 
            element={
              <ProtectedRoute requiredRole="parent">
                <ParentPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/accountant/accountant-portal" 
            element={
              <ProtectedRoute requiredRole="accountant">
                <AccountantPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/staff/staff-portal" 
            element={
              <ProtectedRoute requiredRole="office_staff">
                <StaffPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/library/library-portal" 
            element={
              <ProtectedRoute requiredRole="librarian">
                <LibraryPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/it/it-portal" 
            element={
              <ProtectedRoute requiredRole="it_support">
                <ITPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/counselor/counselor-portal" 
            element={
              <ProtectedRoute requiredRole="counselor">
                <CounselorPortal />
              </ProtectedRoute>
            } 
          />
          {/* Additional Portal Routes */}
          <Route 
            path="/head-teacher/headteacher-portal" 
            element={
              <ProtectedRoute requiredRole="head_teacher">
                <HeadTeacherPortal />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/curriculum/curriculum-portal" 
            element={
              <ProtectedRoute requiredRole="curriculum_coordinator">
                <CurriculumPortal />
              </ProtectedRoute>
            } 
          />

          {/* Legacy Portal Routes (for backward compatibility) */}
          <Route 
            path="/admin-portal" 
            element={
              <Navigate to="/admin/admin-portal" replace />
            } 
          />
          <Route 
            path="/teacher-portal" 
            element={
              <Navigate to="/teacher/teacher-portal" replace />
            } 
          />
          <Route 
            path="/student-portal" 
            element={
              <Navigate to="/student/student-portal" replace />
            } 
          />
          <Route 
            path="/parent-portal" 
            element={
              <Navigate to="/parent/parent-portal" replace />
            } 
          />
          <Route 
            path="/finance-portal" 
            element={
              <Navigate to="/accountant/accountant-portal" replace />
            } 
          />
          <Route 
            path="/staff-portal" 
            element={
              <Navigate to="/staff/staff-portal" replace />
            } 
          />

          {/* ==================== COMMON PROTECTED ROUTES ==================== */}
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/notifications" 
            element={
              <ProtectedRoute>
                <Notifications />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/complete-profile" 
            element={
              <ProtectedRoute>
                <CompleteProfile />
              </ProtectedRoute>
            } 
          />

          {/* ==================== FINANCE MODULE ROUTES ==================== */}
          
          {/* Finance Dashboard & Overview */}
          <Route 
            path="/finance" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <FinanceDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/fee-structure" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <FeeStructure />
              </ProtectedRoute>
            } 
          />

          {/* Receipt Management */}
          <Route 
            path="/finance/receipts" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <Receipts />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/receipts/create" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <CreateReceipt />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/receipts/:id" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <ReceiptDetail />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/receipts/bulk-upload" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <BulkReceiptUpload />
              </ProtectedRoute>
            } 
          />

          {/* Payment Management */}
          <Route 
            path="/finance/payments" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <Payments />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/payments/create" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <CreatePayment />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/payments/:id" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <PaymentDetail />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/payments/approval" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <PaymentApproval />
              </ProtectedRoute>
            } 
          />

          {/* Billing & Invoices */}
          <Route 
            path="/billing" 
            element={
              <ProtectedRoute allowedRoles={['admin', 'parent', 'accountant']}>
                <Billing />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/payment-history" 
            element={
              <ProtectedRoute allowedRoles={['admin', 'parent', 'accountant']}>
                <PaymentHistory />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/invoices" 
            element={
              <ProtectedRoute allowedRoles={['admin', 'parent', 'accountant']}>
                <InvoiceManagement />
              </ProtectedRoute>
            } 
          />

          {/* Debt Management */}
          <Route 
            path="/finance/debts" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <DebtRecords />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/student-debts/:studentId" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin', 'parent']}>
                <StudentDebtOverview />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/debt-reports" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <DebtReports />
              </ProtectedRoute>
            } 
          />

          {/* Financial Reports */}
          <Route 
            path="/finance/reports" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <FinancialReports />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/reports/income-statement" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <IncomeStatement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/reports/balance-sheet" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <BalanceSheet />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/reports/cash-flow" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <CashFlow />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/reports/fee-collection" 
            element={
              <ProtectedRoute allowedRoles={['accountant', 'admin']}>
                <FeeCollectionReport />
              </ProtectedRoute>
            } 
          />

          {/* Accountant Workspace */}
          <Route 
            path="/finance/accountant/workspace" 
            element={
              <ProtectedRoute requiredRole="accountant">
                <AccountantWorkspace />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/accountant/approvals" 
            element={
              <ProtectedRoute requiredRole="accountant">
                <FinancialApprovals />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/accountant/reconciliation" 
            element={
              <ProtectedRoute requiredRole="accountant">
                <Reconciliation />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/finance/accountant/audit-trail" 
            element={
              <ProtectedRoute requiredRole="accountant">
                <AuditTrail />
              </ProtectedRoute>
            } 
          />

          {/* Parent Finance */}
          <Route 
            path="/parent/billing" 
            element={
              <ProtectedRoute requiredRole="parent">
                <ParentBilling />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/parent/fee-statement" 
            element={
              <ProtectedRoute requiredRole="parent">
                <ChildFeeStatement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/parent/make-payment" 
            element={
              <ProtectedRoute requiredRole="parent">
                <MakePayment />
              </ProtectedRoute>
            } 
          />

          {/* ==================== ADMIN FINANCE ROUTES ==================== */}
          {/* Add these routes to fix the /admin/finance issue */}
          <Route 
            path="/admin/finance" 
            element={
              <ProtectedRoute requiredRole="admin">
                <FinanceDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/finance/*" 
            element={
              <ProtectedRoute requiredRole="admin">
                <Navigate to="/admin/finance" replace />
              </ProtectedRoute>
            } 
          />

          {/* ==================== ACADEMIC MANAGEMENT ROUTES ==================== */}
          <Route 
            path="/grades" 
            element={
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin', 'parent']}>
                <Grades />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/attendance" 
            element={
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin', 'parent']}>
                <Attendance />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/assignments" 
            element={
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin']}>
                <Assignments />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/timetable" 
            element={
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin', 'parent']}>
                <Timetable />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/exams" 
            element={
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin', 'parent']}>
                <Exams />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/reports" 
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin', 'parent']}>
                <Reports />
              </ProtectedRoute>
            } 
          />

          {/* Teacher Portal Routes */}
          <Route 
            path="/teacher/assignments" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherAssignments />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/assignments/create" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <CreateAssignment />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/assignments/:id/grade" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <GradeAssignment />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/assignments/:id" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <AssignmentDetail />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/attendance" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherAttendance />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/timetable" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherTimetable />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/grades" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherGrades />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/reports" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <TeacherReports />
              </ProtectedRoute>
            } 
          />

          {/* ==================== ADMIN MANAGEMENT ROUTES ==================== */}
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute requiredRole="admin">
                <Navigate to="/admin/users" replace />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/admin/users" 
            element={
              <ProtectedRoute requiredRole="admin">
                <UserManagement />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/admin/users/create" 
            element={
              <ProtectedRoute requiredRole="admin">
                <UserManagement />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/admin/settings" 
            element={
              <ProtectedRoute requiredRole="admin">
                <SystemSettings />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/admin/analytics-old" 
            element={
              <ProtectedRoute requiredRole="admin">
                <Analytics />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/admin/analytics" 
            element={
              <ProtectedRoute requiredRole="admin">
                <AnalyticsAI />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/admin/logs" 
            element={
              <ProtectedRoute requiredRole="admin">
                <Logs />
              </ProtectedRoute>
            } 
          />

          {/* Admin Management Routes */}
          <Route 
            path="/admin/academic" 
            element={
              <ProtectedRoute requiredRole="admin">
                <AcademicManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/system" 
            element={
              <ProtectedRoute requiredRole="admin">
                <SystemAdministration />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/admin/digital-campus" 
            element={
              <ProtectedRoute requiredRole="admin">
                <DigitalCampus />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/activity" 
            element={
              <ProtectedRoute requiredRole="admin">
                <ActivityLogs />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/whats-new" 
            element={
              <ProtectedRoute requiredRole="admin">
                <div className="container mt-4">
                  <h1>What's New in 2026</h1>
                  <p>Latest features and updates...</p>
                </div>
              </ProtectedRoute>
            } 
          />

          {/* ==================== TEACHER MANAGEMENT ROUTES ==================== */}
          <Route 
            path="/teacher/grade-management" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <GradeManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teacher/attendance-management" 
            element={
              <ProtectedRoute requiredRole="teacher">
                <AttendanceManagement />
              </ProtectedRoute>
            } 
          />

          {/* ==================== PARENT MANAGEMENT ROUTES ==================== */}
          <Route 
            path="/parent/child-progress" 
            element={
              <ProtectedRoute requiredRole="parent">
                <ChildProgress />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/parent/meetings" 
            element={
              <ProtectedRoute requiredRole="parent">
                <ParentMeetings />
              </ProtectedRoute>
            } 
          />

          {/* ==================== MANAGEMENT ROUTES ==================== */}
          <Route 
            path="/students" 
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <UserManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teachers" 
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <UserManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/subjects" 
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <CourseManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/course-management" 
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <CourseManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/class-management" 
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <ClassManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/enrollment-management" 
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <EnrollmentManagement />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/communications" 
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <Communications />
              </ProtectedRoute>
            } 
          />

          {/* ==================== UTILITY ROUTES ==================== */}
          <Route path="/unauthorized" element={<Unauthorized />} />
          
          {/* Redirect authenticated users to dashboard, others to home */}
          <Route 
            path="/home" 
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/" replace />
            } 
          />
          
          {/* Catch-all route for 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;