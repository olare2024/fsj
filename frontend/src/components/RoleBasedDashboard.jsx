// src/components/RoleBasedDashboard.jsx - FIXED VERSION
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const RoleBasedDashboard = () => {
  const { currentUser, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated && currentUser) {
      const redirectPath = getDashboardPath(currentUser);
      console.log('🔄 RoleBasedDashboard: Redirecting to', redirectPath);
      navigate(redirectPath, { replace: true });
    } else {
      navigate('/login', { replace: true });
    }
  }, [isAuthenticated, currentUser, navigate]);

  const getDashboardPath = (user) => {
    if (!user) return '/login';
    
    switch (user.role) {
      case 'student':
        return '/student-portal';
      case 'teacher':
        return '/teacher-portal';
      case 'parent':
        return '/parent-portal';
      case 'admin':
        return '/admin-portal';
      case 'accountant':
        return '/finance-portal';
      case 'head_teacher':
        return '/teacher-portal';
      case 'curriculum_coordinator':
        return '/curriculum/dashboard';
      case 'librarian':
        return '/library-portal';
      case 'counselor':
        return '/counselor-portal';
      case 'it_support':
        return '/it-portal';
      case 'office_staff':
        return '/staff-portal';
      default:
        return '/dashboard';
    }
  };

  // Show loading while redirecting
  return (
    <div className="d-flex justify-content-center align-items-center min-vh-100">
      <div className="text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Redirecting to your portal...</span>
        </div>
        <p className="mt-3 text-muted">Redirecting to your dashboard...</p>
      </div>
    </div>
  );
};

export default RoleBasedDashboard;