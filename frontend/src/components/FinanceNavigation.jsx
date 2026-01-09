// components/FinanceNavigation.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const FinanceNavigation = () => {
  const { currentUser } = useAuth();
  
  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }
  
  // Redirect based on role
  switch (currentUser.role) {
    case 'accountant':
      return <Navigate to="/accountant/accountant-portal" replace />;
    case 'admin':
      return <Navigate to="/finance" replace />;
    case 'parent':
      return <Navigate to="/parent/billing" replace />;
    default:
      return <Navigate to="/unauthorized" replace />;
  }
};

export default FinanceNavigation;