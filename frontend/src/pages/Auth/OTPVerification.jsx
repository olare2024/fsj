// src/pages/Auth/OTPVerification.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Form, 
  Button, 
  Alert, 
  Spinner 
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

const OTPVerification = () => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resendLoading, setResendLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [email, setEmail] = useState('');
  const [method, setMethod] = useState('email');
  const [sessionToken, setSessionToken] = useState('');
  const [maskedEmail, setMaskedEmail] = useState('');
  const [expiresIn, setExpiresIn] = useState(600);

  const inputRefs = useRef([]);
  const { verifyLoginOTP, resendOTP } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Get data from location state
    if (location.state) {
      setEmail(location.state.email || '');
      setSessionToken(location.state.session_token || '');
      setMethod(location.state.method || 'email');
      setMaskedEmail(location.state.masked_email || '');
      setExpiresIn(location.state.expires_in || 600);
    } else {
      // Redirect back to login if no state
      navigate('/login');
    }

    // Start countdown for OTP resend
    setCountdown(60);
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [navigate, location.state]);

  useEffect(() => {
    // Focus first input on mount
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, []);

  const handleOtpChange = (index, value) => {
    // Allow only numbers
    if (value && !/^\d+$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1].focus();
    }

    // Auto-submit when all fields are filled
    if (newOtp.every(digit => digit !== '') && index === 5) {
      handleSubmit();
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text');
    const pastedNumbers = pastedData.replace(/\D/g, '').split('').slice(0, 6);
    
    if (pastedNumbers.length === 6) {
      const newOtp = [...otp];
      pastedNumbers.forEach((num, index) => {
        newOtp[index] = num;
      });
      setOtp(newOtp);
      inputRefs.current[5].focus();
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    const otpCode = otp.join('');
    if (otpCode.length !== 6) {
      setError('Please enter the complete 6-digit code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('🔐 Verifying OTP...');
      
      const result = await verifyLoginOTP({
        email: email,
        otp: otpCode,
        method: method,
        session_token: sessionToken
      });

      console.log('🔍 OTP Verification Result:', result);

      if (result.success) {
        console.log('✅ OTP verification successful');
        navigate(result.redirect_url || '/dashboard', {
          replace: true,
          state: {
            message: 'Login successful! Welcome to Delvok Academy.',
            type: 'success'
          }
        });
      } else {
        setError(result.message || 'Invalid verification code');
        // Clear OTP on error
        setOtp(['', '', '', '', '', '']);
        if (inputRefs.current[0]) {
          inputRefs.current[0].focus();
        }
      }
    } catch (err) {
      console.error('💥 OTP verification error:', err);
      setError('Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setResendLoading(true);
    setError('');

    try {
      const result = await resendOTP(email, 'login');
      
      if (result.success) {
        setCountdown(60);
        // Start countdown again
        const timer = setInterval(() => {
          setCountdown(prev => {
            if (prev <= 1) {
              clearInterval(timer);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } else {
        setError(result.message || 'Failed to resend code');
      }
    } catch (err) {
      console.error('Resend OTP error:', err);
      setError('Failed to resend code. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100 py-4">
      <Row className="w-100 justify-content-center">
        <Col md={6} lg={5} xl={4}>
          <Card className="shadow border-0 auth-card">
            <Card.Body className="p-4 p-md-5">
              {/* Header */}
              <div className="text-center mb-4">
                <div className="verification-icon mb-3">
                  <i className="bi bi-shield-check text-success" style={{ fontSize: '3rem' }}></i>
                </div>
                <h3 className="text-success fw-bold">Verify Your Identity</h3>
                <p className="text-muted">
                  Enter the 6-digit verification code sent to
                </p>
                <p className="fw-semibold text-primary">{maskedEmail || email}</p>
              </div>

              {/* Error Alert */}
              {error && (
                <Alert variant="danger" className="mb-4">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {error}
                </Alert>
              )}

              {/* OTP Form */}
              <Form onSubmit={handleSubmit}>
                <div className="mb-4">
                  <Form.Label className="fw-semibold mb-3 text-center d-block">
                    6-Digit Verification Code
                  </Form.Label>
                  
                  <div className="d-flex justify-content-between gap-2 mb-3">
                    {otp.map((digit, index) => (
                      <Form.Control
                        key={index}
                        ref={el => inputRefs.current[index] = el}
                        type="text"
                        inputMode="numeric"
                        maxLength="1"
                        value={digit}
                        onChange={(e) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        onPaste={index === 0 ? handlePaste : undefined}
                        className="text-center otp-input"
                        disabled={loading}
                        autoComplete="one-time-code"
                      />
                    ))}
                  </div>

                  {/* Timer */}
                  <div className="text-center">
                    <small className="text-muted">
                      Code expires in: <strong>{formatTime(expiresIn)}</strong>
                    </small>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="d-grid mb-3">
                  <Button
                    variant="success"
                    type="submit"
                    size="lg"
                    disabled={loading || otp.join('').length !== 6}
                    className="fw-semibold py-2"
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Verifying...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle me-2"></i>
                        Verify & Continue
                      </>
                    )}
                  </Button>
                </div>

                {/* Resend Code */}
                <div className="text-center">
                  <p className="text-muted mb-2">
                    Didn't receive the code?
                  </p>
                  <Button
                    variant="outline-primary"
                    onClick={handleResendOTP}
                    disabled={resendLoading || countdown > 0}
                    size="sm"
                  >
                    {resendLoading ? (
                      <Spinner animation="border" size="sm" />
                    ) : countdown > 0 ? (
                      `Resend in ${formatTime(countdown)}`
                    ) : (
                      <>
                        <i className="bi bi-arrow-clockwise me-2"></i>
                        Resend Code
                      </>
                    )}
                  </Button>
                </div>
              </Form>

              {/* Security Notice */}
              <div className="mt-4 p-3 bg-light rounded small">
                <h6 className="fw-semibold mb-2">
                  <i className="bi bi-info-circle me-2"></i>
                  Important Security Notice
                </h6>
                <ul className="mb-0 ps-3">
                  <li>Never share your verification code with anyone</li>
                  <li>Delvok Academy staff will never ask for your code</li>
                  <li>Codes are valid for 10 minutes only</li>
                </ul>
              </div>

              {/* Back to Login */}
              <div className="text-center mt-4">
                <Button
                  variant="link"
                  onClick={() => navigate('/login')}
                  className="text-decoration-none"
                >
                  <i className="bi bi-arrow-left me-2"></i>
                  Back to Login
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default OTPVerification;