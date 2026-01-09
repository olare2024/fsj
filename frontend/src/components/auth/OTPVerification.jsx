// src/components/auth/OTPVerification.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Card, Container, Row, Col, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const OTPVerification = ({ type = 'login', email, sessionToken, onSuccess, onBack }) => {
  const { verifyLoginOTP, verifyRegistrationOTP, resendOTP, loading, error, clearError } = useAuth();
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [countdown, setCountdown] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();
  const location = useLocation();
  const inputRefs = useRef([]);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanResend(true);
    }
  }, [countdown]);

  const handleOtpChange = (index, value) => {
    if (!/^\d?$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1].focus();
    }

    clearError();
  };

  const handleKeyDown = (index, e) => {
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
    e.preventDefault();
    const otpCode = otp.join('');
    
    if (otpCode.length !== 6) {
      clearError();
      return;
    }

    try {
      let result;
      
      if (type === 'login') {
        result = await verifyLoginOTP(sessionToken, otpCode);
      } else {
        result = await verifyRegistrationOTP(sessionToken, otpCode);
      }

      if (result.success) {
        setSuccess(type === 'login' ? 'Login successful!' : 'Account verified successfully!');
        
        if (onSuccess) {
          onSuccess(result);
        } else if (type === 'login') {
          // Redirect to dashboard or intended destination
          const from = location.state?.from?.pathname || result.dashboardUrl || '/dashboard';
          navigate(from, { replace: true });
        } else {
          // Redirect to login after registration verification
          navigate('/login', { 
            state: { 
              message: 'Account verified successfully! You can now login.',
              email: email
            }
          });
        }
      }
    } catch (error) {
      // Error is handled by AuthContext
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0].focus();
    }
  };

  const handleResendOTP = async () => {
    setResendLoading(true);
    clearError();
    
    try {
      const result = await resendOTP(sessionToken, type === 'login' ? 'login' : 'account_verification');
      
      if (result.success) {
        setCountdown(60);
        setCanResend(false);
        setSuccess('New OTP sent to your email!');
        setOtp(['', '', '', '', '', '']);
        inputRefs.current[0].focus();
      }
    } catch (error) {
      // Error handled by AuthContext
    } finally {
      setResendLoading(false);
    }
  };

  const getTitle = () => {
    switch (type) {
      case 'login': return 'Verify Login';
      case 'registration': return 'Verify Your Account';
      case 'password_reset': return 'Verify Password Reset';
      default: return 'Verify OTP';
    }
  };

  const getSubtitle = () => {
    switch (type) {
      case 'login': return 'Enter the 6-digit code sent to your email to complete login';
      case 'registration': return 'Enter the 6-digit code sent to your email to verify your account';
      case 'password_reset': return 'Enter the 6-digit code to reset your password';
      default: return 'Enter the 6-digit verification code';
    }
  };

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100">
      <Row className="w-100 justify-content-center">
        <Col md={6} lg={5} xl={4}>
          <Card className="shadow border-0">
            <Card.Body className="p-4 p-md-5">
              <div className="text-center mb-4">
                <h2 className="text-primary fw-bold">{getTitle()}</h2>
                <p className="text-muted mb-3">{getSubtitle()}</p>
                {email && (
                  <p className="text-dark fw-semibold">
                    Code sent to: <span className="text-primary">{email}</span>
                  </p>
                )}
              </div>

              {error && (
                <Alert variant="danger" className="mb-4">
                  <Alert.Heading className="h6 mb-2">Verification Failed</Alert.Heading>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert variant="success" className="mb-4">
                  {success}
                </Alert>
              )}

              <Form onSubmit={handleSubmit}>
                <div className="mb-4">
                  <div className="d-flex justify-content-between mb-3">
                    {[0, 1, 2, 3, 4, 5].map((index) => (
                      <Form.Control
                        key={index}
                        ref={(el) => (inputRefs.current[index] = el)}
                        type="text"
                        maxLength="1"
                        value={otp[index]}
                        onChange={(e) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        onPaste={index === 0 ? handlePaste : undefined}
                        className="text-center mx-1 otp-input"
                        style={{
                          height: '60px',
                          fontSize: '1.5rem',
                          fontWeight: 'bold'
                        }}
                        disabled={loading}
                      />
                    ))}
                  </div>
                  
                  <div className="text-center">
                    <small className="text-muted">
                      {countdown > 0 ? (
                        `Resend code in ${countdown}s`
                      ) : (
                        <Button
                          variant="link"
                          className="p-0 text-decoration-none"
                          onClick={handleResendOTP}
                          disabled={resendLoading || !canResend}
                        >
                          {resendLoading ? (
                            <>
                              <Spinner animation="border" size="sm" className="me-2" />
                              Resending...
                            </>
                          ) : (
                            'Resend OTP'
                          )}
                        </Button>
                      )}
                    </small>
                  </div>
                </div>

                <div className="d-grid gap-2">
                  <Button
                    variant="primary"
                    type="submit"
                    size="lg"
                    disabled={loading || otp.join('').length !== 6}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Verifying...
                      </>
                    ) : (
                      'Verify Code'
                    )}
                  </Button>

                  {onBack && (
                    <Button
                      variant="outline-secondary"
                      onClick={onBack}
                      disabled={loading}
                    >
                      Back
                    </Button>
                  )}
                </div>
              </Form>

              <div className="text-center mt-4">
                <p className="text-muted small mb-0">
                  Didn't receive the code? Check your spam folder or{' '}
                  <Button
                    variant="link"
                    className="p-0 text-decoration-none"
                    onClick={handleResendOTP}
                    disabled={resendLoading || !canResend}
                  >
                    request a new one
                  </Button>
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default OTPVerification;