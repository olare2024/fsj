import React from 'react';
import { useAuth } from '../context/AuthContext';
import AdminPortal from '../pages/Portals/AdminPortal';
import TeacherPortal from '../pages/Portals/TeacherPortal';
import StudentPortal from '../pages/Portals/StudentPortal';
import ParentPortal from '../pages/Portals/ParentPortal';
import FinancePortal from '../pages/Portals/FinancePortal';
import StaffPortal from '../pages/Portals/StaffPortal';

const DashboardPortalRenderer = () => {
  const { currentUser, loading } = useAuth();
  
  if (loading || !currentUser) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  console.log('DashboardPortalRenderer: Rendering portal for', currentUser.role);
  
  switch(currentUser.role) {
    case 'admin':
      return <AdminPortal />;
    case 'teacher':
    case 'head_teacher':
    case 'curriculum_coordinator':
      return <TeacherPortal />;
    case 'student':
      return <StudentPortal />;
    case 'parent':
      return <ParentPortal />;
    case 'accountant':
      return <FinancePortal />;
    case 'office_staff':
    case 'staff':
      return <StaffPortal />;
    case 'librarian':
      return <LibraryPortal />;
    case 'it_support':
      return <ITPortal />;
    case 'counselor':
      return <CounselorPortal />;
    default:
      console.warn('Unknown role:', currentUser.role);
      return (
        <div className="container mt-4">
          <div className="alert alert-warning">
            <h4>Access Issue</h4>
            <p>Your role ({currentUser.role}) does not have a designated portal.</p>
            <p>Please contact administration.</p>
          </div>
        </div>
      );
  }
};

export default DashboardPortalRenderer;