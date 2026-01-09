// src/components/ProtectedRoute.jsx
import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ 
  children, 
  requiredRole = null, 
  allowedRoles = [],
  fallbackPath = '/unauthorized'
}) => {
  const { 
    isAuthenticated, 
    loading, 
    currentUser,
    hasPermission 
  } = useAuth();
  const location = useLocation();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Small delay to ensure auth context is loaded
    const timer = setTimeout(() => {
      setIsChecking(false);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Show loading spinner while checking authentication
  if (loading || isChecking) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2 text-muted">Verifying access...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <Navigate 
        to={`/login?returnUrl=${encodeURIComponent(location.pathname + location.search)}`} 
        replace 
        state={{ from: location }}
      />
    );
  }

  // Check role-based access
  const hasRequiredAccess = () => {
    // If no role requirements, allow access
    if (!requiredRole && (!allowedRoles || allowedRoles.length === 0)) {
      return true;
    }

    // Check for specific required role
    if (requiredRole && currentUser?.role !== requiredRole) {
      return false;
    }

    // Check if user has any of the allowed roles
    if (allowedRoles && allowedRoles.length > 0) {
      return allowedRoles.includes(currentUser?.role);
    }

    return true;
  };

  if (!hasRequiredAccess()) {
    return <Navigate to={fallbackPath} replace />;
  }

  return children;
};

export default ProtectedRoute;