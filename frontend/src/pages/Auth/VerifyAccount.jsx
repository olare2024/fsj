import React, { useState, useEffect, useMemo } from 'react';
import { useLocation, Navigate, useSearchParams, useNavigate } from 'react-router-dom';
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
  const { isAuthenticated, loading: authLoading, verifyLoginOTP } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [verificationData, setVerificationData] = useState(null);

  // Debug logging
  useEffect(() => {
    console.log('🔍 VerifyAccount Location State:', location.state);
    console.log('🔍 VerifyAccount URL Params:', {
      type: searchParams.get('type'),
      email: searchParams.get('email'),
      session_token: searchParams.get('session_token'),
      user_id: searchParams.get('user_id')
    });
  }, [location, searchParams]);

  useEffect(() => {
    const extractVerificationData = () => {
      // Get data from URL parameters (these come from the backend redirect)
      const urlType = searchParams.get('type');
      const urlEmail = searchParams.get('email');
      const urlSessionToken = searchParams.get('session_token'); // Note: session_token not sessionToken
      const urlUserId = searchParams.get('user_id');

      // Get data from location state (these come from frontend navigation)
      const stateType = location.state?.type;
      const stateEmail = location.state?.email;
      const stateSessionToken = location.state?.sessionToken || location.state?.session_token;
      const stateUserId = location.state?.userId || location.state?.user_id;

      // Priority: URL params > location state
      const data = {
        type: urlType || stateType || 'login', // Default to login if not specified
        email: urlEmail || stateEmail,
        sessionToken: urlSessionToken || stateSessionToken, // CRITICAL: Use sessionToken
        userId: urlUserId || stateUserId,
        
        // Additional data from backend
        method: location.state?.method || 'email',
        expires_in: location.state?.expires_in || 600,
        masked_email: location.state?.masked_email,
        
        // Context
        from: location.state?.from,
        redirectUrl: location.state?.redirectUrl || location.state?.redirect_url,
        message: location.state?.message
      };

      console.log('📦 Extracted Verification Data:', data);

      // Validate required fields
      if (!data.email || !data.sessionToken) {
        console.error('❌ Missing required verification data:', {
          hasEmail: !!data.email,
          hasSessionToken: !!data.sessionToken
        });
      }

      return data;
    };

    const data = extractVerificationData();
    setVerificationData(data);
    
    // Store in session storage for persistence
    if (data.email && data.sessionToken) {
      sessionStorage.setItem('otp_email', data.email);
      sessionStorage.setItem('otp_session_token', data.sessionToken);
      console.log('💾 Stored in session storage:', {
        email: data.email,
        sessionToken: data.sessionToken
      });
    }
    
    setLoading(false);
  }, [location, searchParams]);

  // Redirect if already authenticated (except for mfa)
  if (isAuthenticated && verificationData?.type !== 'mfa' && verificationData?.type !== '2fa') {
    console.log('🔄 Already authenticated, redirecting to dashboard');
    return <Navigate to="/dashboard" replace />;
  }

  // Test OTP verification directly
  const handleTestVerification = async () => {
    if (!verificationData?.sessionToken) {
      console.error('No session token available for test');
      return;
    }

    console.log('🧪 Testing OTP verification with:', {
      email: verificationData.email,
      sessionToken: verificationData.sessionToken,
      otp: '341848' // From your logs
    });

    try {
      const result = await verifyLoginOTP({
        email: verificationData.email,
        otp: '341848',
        method: 'email',
        session_token: verificationData.sessionToken // Note: backend expects session_token
      });
      
      console.log('✅ Test verification result:', result);
    } catch (error) {
      console.error('❌ Test verification failed:', {
        error: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
    }
  };

  // Show loading
  if (loading || authLoading) {
    return (
      <Container className="d-flex align-items-center justify-content-center min-vh-100">
        <Row className="w-100 justify-content-center">
          <Col md={6} lg={4}>
            <Card className="shadow border-0 text-center">
              <Card.Body className="p-5">
                <Spinner animation="border" variant="primary" className="mb-3" />
                <h5>Preparing Verification</h5>
                <p className="text-muted">Setting up your secure session...</p>
                
                {/* Debug info in dev mode */}
                {process.env.NODE_ENV === 'development' && (
                  <div className="mt-3 text-start small">
                    <p className="mb-1">Debug Info:</p>
                    <code className="d-block bg-light p-2 rounded">
                      {JSON.stringify({
                        type: searchParams.get('type'),
                        hasEmail: !!searchParams.get('email'),
                        hasToken: !!searchParams.get('session_token'),
                        locationState: location.state
                      }, null, 2)}
                    </code>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  // Handle missing data
  if (!verificationData?.sessionToken || !verificationData?.email) {
    console.error('🚫 Missing verification data:', verificationData);
    
    return (
      <Container className="d-flex align-items-center justify-content-center min-vh-100">
        <Row className="w-100 justify-content-center">
          <Col md={6} lg={5}>
            <Card className="shadow border-0">
              <Card.Body className="p-4 p-md-5 text-center">
                <div className="text-warning mb-4">
                  <i className="fas fa-exclamation-triangle fa-3x"></i>
                </div>
                <h4 className="text-warning mb-3">Verification Link Invalid</h4>
                
                <Alert variant="warning" className="text-start">
                  <p className="mb-2"><strong>Missing or invalid verification data:</strong></p>
                  <ul className="mb-0">
                    <li>Email: {verificationData?.email ? '✓' : '✗'}</li>
                    <li>Session Token: {verificationData?.sessionToken ? '✓' : '✗'}</li>
                    <li>Type: {verificationData?.type || 'Not specified'}</li>
                  </ul>
                  
                  <hr />
                  
                  <p className="mb-0 small">
                    <strong>Possible solutions:</strong>
                    <br />
                    1. Return to the previous step and try again
                    <br />
                    2. Check your email for a new verification link
                    <br />
                    3. Clear browser cache and cookies
                  </p>
                </Alert>

                <div className="d-grid gap-2 mt-4">
                  <Button 
                    variant="primary" 
                    onClick={() => navigate('/login')}
                  >
                    <i className="fas fa-sign-in-alt me-2"></i>
                    Return to Login
                  </Button>
                  
                  <Button 
                    variant="outline-secondary" 
                    onClick={() => window.location.reload()}
                  >
                    <i className="fas fa-redo me-2"></i>
                    Reload Page
                  </Button>
                  
                  {/* Debug button in development */}
                  {process.env.NODE_ENV === 'development' && verificationData?.sessionToken && (
                    <Button 
                      variant="outline-info" 
                      onClick={handleTestVerification}
                      size="sm"
                    >
                      <i className="fas fa-vial me-2"></i>
                      Test Verification API
                    </Button>
                  )}
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  // Success - render OTP verification
  console.log('✅ Rendering OTPVerification with:', {
    email: verificationData.email,
    sessionToken: verificationData.sessionToken?.slice(0, 20) + '...',
    type: verificationData.type,
    method: verificationData.method,
    expires_in: verificationData.expires_in
  });

  return (
    <OTPVerification
      email={verificationData.email}
      sessionToken={verificationData.sessionToken}
      method={verificationData.method || 'email'}
      expires_in={verificationData.expires_in || 600}
      masked_email={verificationData.masked_email || verificationData.email}
      type={verificationData.type || 'login'}
      autoRedirect={true}
      onBack={() => {
        switch (verificationData.type) {
          case 'registration':
            navigate('/register');
            break;
          case 'password_reset':
            navigate('/forgot-password');
            break;
          case 'login':
          default:
            navigate('/login');
        }
      }}
      onSuccess={(data) => {
        console.log('🎉 OTP verification successful:', data);
        // You can handle success callback here if needed
      }}
    />
  );
};

export default VerifyAccount;