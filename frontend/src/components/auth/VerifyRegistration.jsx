import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Alert, Form, Button, Card, Container, Row, Col, Spinner, Modal } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const VerifyRegistration = () => {
  const { verifyRegistration, resendOTP } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [countdown, setCountdown] = useState(0);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  // Get registration data from navigation state
  const { sessionToken, userId, email } = location.state || {};

  useEffect(() => {
    if (!sessionToken || !email) {
      navigate('/register', { replace: true });
      return;
    }

    // Start countdown for OTP resend
    setCountdown(30);
  }, [sessionToken, email, navigate]);

  // Countdown timer for resend OTP
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleOtpChange = (element, index) => {
    if (isNaN(element.value)) return false;

    const newOtp = [...otp];
    newOtp[index] = element.value;
    setOtp(newOtp);

    // Auto-focus next input
    if (element.value !== '' && element.nextSibling) {
      element.nextSibling.focus();
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace') {
      if (otp[index] === '' && e.target.previousSibling) {
        e.target.previousSibling.focus();
      }
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData('text');
    const pasteNumbers = pasteData.replace(/\D/g, '').slice(0, 6);
    
    const newOtp = [...otp];
    pasteNumbers.split('').forEach((char, index) => {
      if (index < 6) newOtp[index] = char;
    });
    
    setOtp(newOtp);
    
    // Focus the last filled input
    const lastFilledIndex = Math.min(pasteNumbers.length, 5);
    const inputs = document.querySelectorAll('.otp-input');
    if (inputs[lastFilledIndex]) {
      inputs[lastFilledIndex].focus();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const otpCode = otp.join('');
    
    if (otpCode.length !== 6) {
      setError('Please enter the complete 6-digit OTP code');
      setLoading(false);
      return;
    }

    try {
      const result = await verifyRegistration(sessionToken, otpCode);
      
      if (result.success) {
        setSuccess('Account verified successfully! Redirecting to login...');
        setShowSuccessModal(true);
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login', { 
            replace: true,
            state: { 
              message: 'Account verified successfully! You can now login.',
              verifiedEmail: email
            }
          });
        }, 3000);
      } else {
        setError(result.error?.message || 'Verification failed. Please try again.');
        
        // Clear OTP on error
        if (result.error?.message?.includes('Invalid OTP')) {
          setOtp(['', '', '', '', '', '']);
          const firstInput = document.querySelector('.otp-input');
          if (firstInput) firstInput.focus();
        }
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (countdown > 0) return;
    
    setResendLoading(true);
    setError('');

    try {
      const result = await resendOTP(sessionToken, 'account_verification');
      
      if (result.success) {
        setSuccess('New OTP sent to your email and phone!');
        setCountdown(30); // Reset countdown
      } else {
        setError(result.error?.message || 'Failed to resend OTP. Please try again.');
      }
    } catch (err) {
      console.error('Resend OTP error:', err);
      setError('Failed to resend OTP. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  const handleQuickVerify = () => {
    // This would be called when user clicks the verification link in email
    // For now, we'll simulate it by showing a message
    setSuccess('If you clicked the verification link in your email, your account should be verified. You can still enter the OTP code manually.');
  };

  if (!sessionToken || !email) {
    return (
      <Container className="mt-5">
        <Row className="justify-content-center">
          <Col md={6}>
            <Alert variant="danger">
              <Alert.Heading>Invalid Verification Session</Alert.Heading>
              <p>Your verification session has expired or is invalid.</p>
              <hr />
              <div className="d-flex justify-content-between">
                <Button 
                  variant="outline-danger" 
                  onClick={() => navigate('/register')}
                >
                  Back to Registration
                </Button>
                <Button 
                  variant="outline-primary" 
                  onClick={() => navigate('/login')}
                >
                  Go to Login
                </Button>
              </div>
            </Alert>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <Container className="mt-4 mb-5">
      <Row className="justify-content-center">
        <Col md={6} lg={5}>
          <Card className="shadow border-0">
            <Card.Body className="p-4 p-md-5">
              <div className="text-center mb-4">
                <div className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                     style={{ width: '60px', height: '60px' }}>
                  <i className="fas fa-shield-alt text-white fs-4"></i>
                </div>
                <h2 className="text-primary fw-bold">Verify Your Account</h2>
                <p className="text-muted mb-2">
                  Enter the 6-digit verification code sent to:
                </p>
                <p className="fw-bold text-dark">{email}</p>
              </div>

              {error && (
                <Alert variant="danger" className="mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    <span>{error}</span>
                  </div>
                </Alert>
              )}

              {success && (
                <Alert variant="success" className="mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-check-circle me-2"></i>
                    <span>{success}</span>
                  </div>
                </Alert>
              )}

              <Form onSubmit={handleSubmit}>
                <div className="mb-4">
                  <Form.Label className="fw-semibold mb-3">
                    Verification Code <span className="text-danger">*</span>
                  </Form.Label>
                  
                  <div className="d-flex justify-content-between mb-3">
                    {otp.map((data, index) => (
                      <Form.Control
                        key={index}
                        type="text"
                        maxLength="1"
                        value={data}
                        onChange={e => handleOtpChange(e.target, index)}
                        onKeyDown={e => handleKeyDown(e, index)}
                        onPaste={handlePaste}
                        className="otp-input text-center fw-bold fs-5"
                        style={{
                          width: '50px',
                          height: '60px',
                          fontSize: '1.5rem',
                          margin: '0 5px'
                        }}
                        disabled={loading}
                      />
                    ))}
                  </div>
                  
                  <Form.Text className="text-muted">
                    Enter the 6-digit code from your email or SMS
                  </Form.Text>
                </div>

                <div className="d-grid mb-3">
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={loading || otp.join('').length !== 6}
                    size="lg"
                    className="fw-semibold py-2"
                  >
                    {loading ? (
                      <>
                        <Spinner
                          as="span"
                          animation="border"
                          size="sm"
                          role="status"
                          aria-hidden="true"
                          className="me-2"
                        />
                        Verifying...
                      </>
                    ) : (
                      'Verify Account'
                    )}
                  </Button>
                </div>
              </Form>

              <div className="text-center mb-4">
                <p className="text-muted mb-2">
                  Didn't receive the code?
                </p>
                <Button
                  variant="outline-primary"
                  onClick={handleResendOTP}
                  disabled={resendLoading || countdown > 0}
                  className="fw-semibold"
                >
                  {resendLoading ? (
                    <Spinner as="span" animation="border" size="sm" className="me-2" />
                  ) : countdown > 0 ? (
                    `Resend OTP (${countdown}s)`
                  ) : (
                    'Resend OTP'
                  )}
                </Button>
              </div>

              <div className="text-center">
                <p className="text-muted mb-2">
                  Check your email for a verification link for instant verification.
                </p>
                <Button
                  variant="link"
                  onClick={handleQuickVerify}
                  className="text-decoration-none"
                >
                  Click here if you used the email link
                </Button>
              </div>

              <hr className="my-4" />

              <div className="text-center">
                <p className="text-muted mb-0">
                  Having trouble?{' '}
                  <Link 
                    to="/support" 
                    className="text-decoration-none fw-semibold text-primary"
                  >
                    Contact Support
                  </Link>
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Success Modal */}
      <Modal show={showSuccessModal} centered backdrop="static">
        <Modal.Body className="text-center p-4">
          <div className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
               style={{ width: '80px', height: '80px' }}>
            <i className="fas fa-check text-white fs-2"></i>
          </div>
          <h4 className="text-success fw-bold mb-3">Account Verified!</h4>
          <p className="text-muted mb-4">
            Your account has been successfully verified. You will be redirected to the login page shortly.
          </p>
          <Button
            variant="success"
            onClick={() => navigate('/login', { replace: true })}
            className="fw-semibold"
          >
            Go to Login Now
          </Button>
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default VerifyRegistration;