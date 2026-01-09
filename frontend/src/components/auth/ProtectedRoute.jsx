// src/components/auth/ProtectedRoute.jsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Container, Spinner, Alert } from 'react-bootstrap';

const ProtectedRoute = ({ children, roles = [], requireVerification = true }) => {
  const { isAuthenticated, currentUser, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="text-center">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2 text-muted">Checking authentication...</p>
        </div>
      </Container>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireVerification && !currentUser?.is_verified) {
    return (
      <Container className="mt-5">
        <Alert variant="warning">
          <Alert.Heading>Email Verification Required</Alert.Heading>
          <p>
            Please verify your email address before accessing this page. 
            Check your inbox for the verification link.
          </p>
          <hr />
          <div className="d-flex justify-content-between">
            <Button variant="outline-warning" onClick={() => window.location.reload()}>
              I've Verified My Email
            </Button>
            <Button variant="warning" onClick={() => {/* Resend verification logic */}}>
              Resend Verification Email
            </Button>
          </div>
        </Alert>
      </Container>
    );
  }

  if (roles.length > 0 && !roles.includes(currentUser?.role)) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <Alert.Heading>Access Denied</Alert.Heading>
          <p>
            You don't have permission to access this page. 
            Required roles: {roles.join(', ')}
          </p>
        </Alert>
      </Container>
    );
  }

  return children;
};

export default ProtectedRoute;