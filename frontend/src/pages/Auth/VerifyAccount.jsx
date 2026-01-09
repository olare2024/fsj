import React, { useState, useEffect } from 'react';
import { useLocation, Navigate, useSearchParams } from 'react-router-dom';
import OTPVerification from './OTPVerification';
import { useAuth } from '../../context/AuthContext';
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Alert, 
  Button, 
  Spinner 
} from 'react-bootstrap';

const VerifyAccount = () => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [verificationData, setVerificationData] = useState(null);

  useEffect(() => {
    // Extract verification data from multiple sources
    const extractVerificationData = () => {
      // Get data from URL parameters first
      const urlType = searchParams.get('type');
      const urlEmail = searchParams.get('email');
      const urlSessionToken = searchParams.get('session_token');
      const urlUserId = searchParams.get('user_id');

      // Get data from location state
      const stateType = location.state?.type;
      const stateEmail = location.state?.email;
      const stateSessionToken = location.state?.sessionToken;
      const stateUserId = location.state?.userId;

      // Combine with priority: URL params > location state > defaults
      const data = {
        type: urlType || stateType || 'registration',
        email: urlEmail || stateEmail,
        sessionToken: urlSessionToken || stateSessionToken,
        userId: urlUserId || stateUserId,
        
        // Additional context
        from: location.state?.from,
        redirectUrl: location.state?.redirectUrl,
        message: location.state?.message
      };

      // Clean up undefined values
      Object.keys(data).forEach(key => {
        if (data[key] === undefined || data[key] === 'undefined' || data[key] === '') {
          delete data[key];
        }
      });

      return data;
    };

    const data = extractVerificationData();
    setVerificationData(data);
    setLoading(false);
  }, [location, searchParams]);

  // Redirect if already authenticated (unless it's a multi-factor auth scenario)
  if (isAuthenticated && verificationData?.type !== 'mfa') {
    return <Navigate to="/dashboard" replace />;
  }

  // Show loading while extracting data
  if (loading || authLoading) {
    return (
      <Container className="d-flex align-items-center justify-content-center min-vh-100">
        <Row className="w-100 justify-content-center">
          <Col md={6} lg={4}>
            <Card className="shadow border-0 text-center">
              <Card.Body className="p-5">
                <Spinner animation="border" variant="primary" className="mb-3" />
                <h5>Loading Verification</h5>
                <p className="text-muted">Preparing your verification session...</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  // Handle missing critical data
  if (!verificationData?.sessionToken) {
    return (
      <Container className="d-flex align-items-center justify-content-center min-vh-100">
        <Row className="w-100 justify-content-center">
          <Col md={6} lg={5}>
            <Card className="shadow border-0">
              <Card.Body className="p-4 p-md-5 text-center">
                <div className="text-warning mb-4">
                  <i className="fas fa-exclamation-triangle fa-3x"></i>
                </div>
                <h4 className="text-warning mb-3">Invalid Verification Session</h4>
                
                <Alert variant="warning" className="text-start">
                  <p className="mb-3">
                    <strong>We couldn't find your verification session.</strong> This might happen if:
                  </p>
                  <ul className="mb-3">
                    <li>You refreshed the page</li>
                    <li>The session expired</li>
                    <li>You accessed this page directly</li>
                  </ul>
                </Alert>

                <div className="d-grid gap-2">
                  {/* Dynamic back button based on verification type */}
                  {verificationData?.type === 'login' && (
                    <Button 
                      variant="primary" 
                      onClick={() => window.history.back()}
                    >
                      <i className="fas fa-arrow-left me-2"></i>
                      Back to Login
                    </Button>
                  )}
                  
                  {verificationData?.type === 'registration' && (
                    <Button 
                      variant="primary" 
                      onClick={() => window.location.href = '/register'}
                    >
                      <i className="fas fa-user-plus me-2"></i>
                      Back to Registration
                    </Button>
                  )}
                  
                  {verificationData?.type === 'password_reset' && (
                    <Button 
                      variant="primary" 
                      onClick={() => window.location.href = '/forgot-password'}
                    >
                      <i className="fas fa-key me-2"></i>
                      Back to Password Reset
                    </Button>
                  )}

                  {/* Fallback button */}
                  {!verificationData?.type && (
                    <Button 
                      variant="primary" 
                      onClick={() => window.location.href = '/'}
                    >
                      <i className="fas fa-home me-2"></i>
                      Go to Homepage
                    </Button>
                  )}

                  <Button 
                    variant="outline-secondary" 
                    onClick={() => window.location.reload()}
                  >
                    <i className="fas fa-redo me-2"></i>
                    Try Again
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  // Render OTP verification with all available data
  return (
    <OTPVerification
      type={verificationData.type}
      email={verificationData.email}
      sessionToken={verificationData.sessionToken}
      userId={verificationData.userId}
      autoRedirect={true}
      onBack={() => {
        // Dynamic back navigation based on verification type
        switch (verificationData.type) {
          case 'login':
            window.history.back();
            break;
          case 'registration':
            window.location.href = '/register';
            break;
          case 'password_reset':
            window.location.href = '/forgot-password';
            break;
          default:
            window.history.back();
        }
      }}
    />
  );
};

export default VerifyAccount;