// src/pages/Auth/OTPVerification.jsx - COMPLETE FIXED VERSION
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Form, 
  Button, 
  Alert, 
  Spinner,
  ProgressBar
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

// Helper function to mask email
const maskEmail = (email) => {
  if (!email) return '••••@delvok.ac.ke';
  const [username, domain] = email.split('@');
  if (username.length <= 2) return `•••@${domain}`;
  const masked = username[0] + '•••' + username.slice(-1);
  return `${masked}@${domain}`;
};

const OTPVerification = () => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [resendLoading, setResendLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [email, setEmail] = useState('');
  const [method, setMethod] = useState('email');
  const [sessionToken, setSessionToken] = useState('');
  const [maskedEmail, setMaskedEmail] = useState('');
  const [expiresIn, setExpiresIn] = useState(600);
  const [timeLeft, setTimeLeft] = useState(600);
  const [verificationAttempts, setVerificationAttempts] = useState(0);
  const [showAlternateMethods, setShowAlternateMethods] = useState(false);

  const inputRefs = useRef([]);
  const intervalRef = useRef(null);
  const resendTimerRef = useRef(null);
  const { verifyLoginOTP, resendOTP } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  // Initialize component
  useEffect(() => {
    console.log('🔧 OTPVerification component mounted');
    
    // Get data from multiple sources
    const stateData = location.state || {};
    const queryEmail = searchParams.get('email');
    const queryToken = searchParams.get('token');
    const queryMethod = searchParams.get('method');

    console.log('📦 Location state:', stateData);
    console.log('📦 Query params:', { queryEmail, queryToken, queryMethod });

    // Priority: 1. Location state, 2. Query params, 3. Session storage
    const finalEmail = stateData.email || queryEmail || sessionStorage.getItem('otp_email') || '';
    const finalSessionToken = stateData.session_token || queryToken || sessionStorage.getItem('otp_session_token') || '';
    const finalMethod = stateData.method || queryMethod || 'email';
    const finalMaskedEmail = stateData.masked_email || maskEmail(finalEmail);
    const finalExpiresIn = stateData.expires_in || 600;

    console.log('✅ Final data:', {
      finalEmail,
      finalSessionToken,
      finalMethod,
      finalMaskedEmail,
      finalExpiresIn
    });

    if (!finalEmail || !finalSessionToken) {
      console.warn('❌ Missing required data, redirecting to login');
      navigate('/login', { 
        state: { 
          error: 'Session expired. Please login again.' 
        } 
      });
      return;
    }

    setEmail(finalEmail);
    setSessionToken(finalSessionToken);
    setMethod(finalMethod);
    setMaskedEmail(finalMaskedEmail);
    setExpiresIn(finalExpiresIn);
    setTimeLeft(finalExpiresIn);

    // Store in session for persistence
    sessionStorage.setItem('otp_email', finalEmail);
    sessionStorage.setItem('otp_session_token', finalSessionToken);

    // Start countdown for OTP resend
    setCountdown(60);
    startResendTimer();

    // Start OTP expiry timer
    startExpiryTimer();

    return () => {
      console.log('🧹 Cleaning up timers');
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (resendTimerRef.current) {
        clearInterval(resendTimerRef.current);
      }
    };
  }, [navigate, location.state, searchParams]);

  useEffect(() => {
    // Focus first input on mount
    setTimeout(() => {
      if (inputRefs.current[0]) {
        inputRefs.current[0].focus();
      }
    }, 300);
  }, []);

  const startExpiryTimer = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(intervalRef.current);
          handleOTPExpired();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const startResendTimer = useCallback(() => {
    if (resendTimerRef.current) {
      clearInterval(resendTimerRef.current);
    }

    resendTimerRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(resendTimerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  const handleOTPExpired = () => {
    setError('OTP has expired. Please request a new code.');
    // Clear OTP fields
    setOtp(['', '', '', '', '', '']);
    // Disable inputs
    inputRefs.current.forEach(input => {
      if (input) input.disabled = true;
    });
  };

  const handleOtpChange = (index, value) => {
    console.log('🔄 OTP Change:', { index, value, currentOTP: otp });
    
    // Allow only single digit numbers
    const digit = value.replace(/\D/g, '').slice(-1);
    
    if (!digit && value !== '') {
      console.log('❌ Invalid input - not a number');
      return;
    }

    // Update OTP array
    setOtp(prevOtp => {
      const newOtp = [...prevOtp];
      newOtp[index] = digit;
      console.log('✅ New OTP array:', newOtp);
      return newOtp;
    });

    // Auto-focus next input
    if (digit && index < 5) {
      setTimeout(() => {
        if (inputRefs.current[index + 1]) {
          inputRefs.current[index + 1].focus();
        }
      }, 10);
    }

    // Clear errors when user starts typing
    if (error) {
      setError('');
    }
  };

  // Use useEffect to check for auto-submit
  useEffect(() => {
    const currentOtp = otp.join('');
    console.log('📊 OTP updated:', { otp, string: currentOtp, length: currentOtp.length });
    
    if (currentOtp.length === 6) {
      console.log('🚀 All digits filled, auto-submitting');
      handleSubmit();
    }
  }, [otp]);

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace') {
      if (!otp[index] && index > 0) {
        // Move to previous field if current is empty
        const newOtp = [...otp];
        newOtp[index - 1] = '';
        setOtp(newOtp);
        setTimeout(() => {
          if (inputRefs.current[index - 1]) {
            inputRefs.current[index - 1].focus();
          }
        }, 10);
      } else if (otp[index]) {
        // Clear current field
        const newOtp = [...otp];
        newOtp[index] = '';
        setOtp(newOtp);
      }
      e.preventDefault();
    }
    
    // Handle arrow keys
    else if (e.key === 'ArrowLeft' && index > 0) {
      if (inputRefs.current[index - 1]) {
        inputRefs.current[index - 1].focus();
      }
      e.preventDefault();
    } else if (e.key === 'ArrowRight' && index < 5) {
      if (inputRefs.current[index + 1]) {
        inputRefs.current[index + 1].focus();
      }
      e.preventDefault();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    console.log('📋 Pasting data:', pastedData);
    
    const pastedNumbers = pastedData.replace(/\D/g, '').split('').slice(0, 6);
    
    if (pastedNumbers.length === 6) {
      const newOtp = [...otp];
      pastedNumbers.forEach((num, index) => {
        newOtp[index] = num;
      });
      setOtp(newOtp);
      
      console.log('✅ Pasted OTP:', newOtp.join(''));
      
      // Focus last input
      setTimeout(() => {
        if (inputRefs.current[5]) {
          inputRefs.current[5].focus();
        }
      }, 10);
    } else {
      console.error('❌ Invalid paste - not 6 digits:', pastedNumbers);
      setError('Please paste a 6-digit code');
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    const otpCode = otp.join('');
    console.log('📤 Submit called with OTP:', {
      otpArray: otp,
      otpString: otpCode,
      length: otpCode.length,
      complete: otpCode.length === 6
    });
    
    if (otpCode.length !== 6) {
      console.error('❌ Incomplete OTP:', otpCode);
      setError('Please enter the complete 6-digit code');
      shakeInputs();
      return;
    }

    // Check attempts
    if (verificationAttempts >= 5) {
      setError('Too many failed attempts. Please request a new code.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      console.log('🔐 Verifying OTP...', {
        email,
        otp: otpCode,
        method,
        sessionToken,
        attempts: verificationAttempts + 1
      });
      
      const result = await verifyLoginOTP({
        email: email,
        otp: otpCode,
        method: method,
        session_token: sessionToken
      });

      console.log('🔍 OTP Verification Result:', result);

      if (result.success) {
        setVerificationAttempts(0);
        console.log('✅ OTP verification successful');
        setSuccess('Verification successful! Redirecting...');
        
        // Clear session storage
        sessionStorage.removeItem('otp_email');
        sessionStorage.removeItem('otp_session_token');
        
        // Delay for success message
        setTimeout(() => {
          navigate(result.redirect_url || '/dashboard', {
            replace: true,
            state: {
              message: 'Login successful! Welcome to Delvok Academy.',
              type: 'success',
              user: result.user,
              permissions: result.permissions,
              token: result.token
            }
          });
        }, 1000);
      } else {
        setVerificationAttempts(prev => prev + 1);
        setError(result.message || 'Invalid verification code');
        
        // Shake inputs on error
        shakeInputs();
        
        // Clear OTP on error (but not on first attempt)
        if (verificationAttempts >= 2) {
          setOtp(['', '', '', '', '', '']);
          setTimeout(() => {
            if (inputRefs.current[0]) {
              inputRefs.current[0].focus();
            }
          }, 300);
        }
        
        // Show lock warning
        if (verificationAttempts >= 3) {
          setError(`${result.message || 'Invalid code'}. ${5 - verificationAttempts} attempts remaining.`);
        }
      }
    } catch (err) {
      console.error('💥 OTP verification error:', err);
      setError('Verification failed. Please try again.');
      setVerificationAttempts(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  const shakeInputs = () => {
    inputRefs.current.forEach(input => {
      if (input) {
        input.classList.add('shake');
        setTimeout(() => {
          input.classList.remove('shake');
        }, 500);
      }
    });
  };

  const handleResendOTP = async () => {
    if (countdown > 0) return;
    
    setResendLoading(true);
    setError('');
    setSuccess('');

    try {
      console.log('🔄 Resending OTP to:', email);
      
      const result = await resendOTP(email, 'login');
      
      console.log('📬 Resend OTP result:', result);
      
      if (result.success) {
        console.log('✅ OTP resent successfully');
        setSuccess('New verification code sent!');
        setVerificationAttempts(0);
        
        // Reset OTP fields
        setOtp(['', '', '', '', '', '']);
        
        // Reset timers
        setTimeLeft(result.expires_in || 600);
        setCountdown(60);
        startExpiryTimer();
        startResendTimer();
        
        // Focus first input
        setTimeout(() => {
          if (inputRefs.current[0]) {
            inputRefs.current[0].focus();
          }
        }, 100);
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

  const handleTryAlternateMethod = async (alternateMethod) => {
    setLoading(true);
    try {
      const result = await resendOTP({
        email: email,
        method: alternateMethod,
        session_token: sessionToken,
        reason: 'alternate_method'
      });
      
      if (result.success) {
        setMethod(alternateMethod);
        setSuccess(`Code sent via ${alternateMethod === 'sms' ? 'SMS' : 'Email'}!`);
        setTimeLeft(result.expires_in || 600);
        setCountdown(60);
        startExpiryTimer();
        startResendTimer();
      }
    } catch (err) {
      setError(`Failed to send via ${alternateMethod}`);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercentage = (timeLeft / expiresIn) * 100;

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
                <h3 className="text-success fw-bold mb-2">Verify Your Identity</h3>
                <p className="text-muted mb-1">
                  Enter the 6-digit verification code sent to
                </p>
                <p className="fw-semibold text-primary mb-3">{maskedEmail}</p>
                
                {/* Timer Progress */}
                <div className="mb-3">
                  <ProgressBar 
                    now={progressPercentage} 
                    variant={progressPercentage > 50 ? 'success' : progressPercentage > 25 ? 'warning' : 'danger'}
                    animated 
                    style={{ height: '6px' }}
                  />
                  <small className="text-muted d-block mt-1">
                    Expires in: <strong className={timeLeft < 60 ? 'text-danger' : ''}>
                      {formatTime(timeLeft)}
                    </strong>
                  </small>
                </div>
              </div>

              {/* Success Alert */}
              {success && (
                <Alert variant="success" className="mb-4" dismissible onClose={() => setSuccess('')}>
                  <i className="bi bi-check-circle me-2"></i>
                  {success}
                </Alert>
              )}

              {/* Error Alert */}
              {error && (
                <Alert variant="danger" className="mb-4" dismissible onClose={() => setError('')}>
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {error}
                  {verificationAttempts >= 3 && (
                    <div className="mt-2 small">
                      <i className="bi bi-info-circle me-1"></i>
                      Too many failed attempts may lock your account temporarily.
                    </div>
                  )}
                </Alert>
              )}

              {/* Debug Info (Remove in production) */}
              <div className="mb-3 p-2 bg-light rounded small">
                <div className="d-flex justify-content-between align-items-center">
                  <span className="text-muted">Debug Info:</span>
                  <Button 
                    variant="outline-secondary" 
                    size="sm" 
                    onClick={() => {
                      console.log('🔍 Current State:', {
                        otp,
                        otpString: otp.join(''),
                        email,
                        sessionToken,
                        method,
                        timeLeft,
                        verificationAttempts
                      });
                      console.log('🔍 Input Refs:', inputRefs.current.map(ref => ({
                        value: ref?.value,
                        id: ref?.id
                      })));
                    }}
                  >
                    Show State
                  </Button>
                </div>
              </div>

              {/* OTP Form */}
              <Form onSubmit={handleSubmit}>
                <div className="mb-4">
                  <Form.Label className="fw-semibold mb-3 text-center d-block">
                    6-Digit Verification Code
                    <span className="text-danger">*</span>
                  </Form.Label>
                  
                  <div className="d-flex justify-content-between gap-2 mb-3">
                    {[0, 1, 2, 3, 4, 5].map((index) => (
                      <Form.Control
                        key={index}
                        ref={el => {
                          inputRefs.current[index] = el;
                        }}
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        maxLength="1"
                        value={otp[index]}
                        onChange={(e) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        onPaste={index === 0 ? handlePaste : undefined}
                        onFocus={(e) => e.target.select()}
                        onInput={(e) => {
                          // Ensure only numbers
                          e.target.value = e.target.value.replace(/\D/g, '');
                        }}
                        className={`text-center otp-input ${error ? 'border-danger' : ''}`}
                        disabled={loading || timeLeft === 0}
                        autoComplete="one-time-code"
                        style={{
                          height: '60px',
                          fontSize: '1.5rem',
                          fontWeight: 'bold',
                          width: '50px'
                        }}
                      />
                    ))}
                  </div>

                  <div className="text-center">
                    <small className="text-muted">
                      {method === 'email' ? 'Sent via Email' : 'Sent via SMS'} • 
                      Attempts: {verificationAttempts}/5
                    </small>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="d-grid mb-3">
                  <Button
                    variant="success"
                    type="submit"
                    size="lg"
                    disabled={loading || otp.join('').length !== 6 || timeLeft === 0}
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

                {/* Alternate Methods */}
                {showAlternateMethods && (
                  <div className="mb-3">
                    <p className="text-muted small mb-2">Try alternate method:</p>
                    <div className="d-flex gap-2">
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => handleTryAlternateMethod('sms')}
                        disabled={loading}
                      >
                        <i className="bi bi-phone me-1"></i>
                        Send SMS
                      </Button>
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => handleTryAlternateMethod('email')}
                        disabled={loading}
                      >
                        <i className="bi bi-envelope me-1"></i>
                        Send Email
                      </Button>
                    </div>
                  </div>
                )}

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
                      <>
                        <i className="bi bi-clock me-2"></i>
                        Resend in {formatTime(countdown)}
                      </>
                    ) : (
                      <>
                        <i className="bi bi-arrow-clockwise me-2"></i>
                        Resend Code
                      </>
                    )}
                  </Button>
                  
                  <div className="mt-2">
                    <Button
                      variant="link"
                      size="sm"
                      onClick={() => setShowAlternateMethods(!showAlternateMethods)}
                      className="text-decoration-none"
                    >
                      {showAlternateMethods ? 'Hide options' : 'Try another method'}
                    </Button>
                  </div>
                </div>
              </Form>

              {/* Security Notice */}
              <div className="mt-4 p-3 bg-light rounded small">
                <h6 className="fw-semibold mb-2">
                  <i className="bi bi-shield-check me-2"></i>
                  Security Guidelines
                </h6>
                <ul className="mb-0 ps-3">
                  <li>Never share your verification code with anyone</li>
                  <li>Delvok Academy staff will never ask for your code</li>
                  <li>Codes are valid for 10 minutes only</li>
                  <li>After 5 failed attempts, you'll need a new code</li>
                </ul>
              </div>

              {/* Back to Login */}
              <div className="text-center mt-4">
                <Button
                  variant="link"
                  onClick={() => {
                    sessionStorage.removeItem('otp_email');
                    sessionStorage.removeItem('otp_session_token');
                    navigate('/login');
                  }}
                  className="text-decoration-none"
                  disabled={loading}
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