// src/components/AuthRedirectGuard.jsx
import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AuthRedirectGuard = ({ children }) => {
  const { isAuthenticated, loading, getDashboardUrl } = useAuth();
  const location = useLocation();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsChecking(false);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  if (loading || isChecking) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2 text-muted">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    const returnUrl = new URLSearchParams(location.search).get('returnUrl');
    const redirectTo = returnUrl || getDashboardUrl();
    return <Navigate to={redirectTo} replace />;
  }

  return children;
};

export default AuthRedirectGuard;