import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Alert, Form, Button, Card, Container, Row, Col, Spinner } from 'react-bootstrap';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [sessionToken, setSessionToken] = useState('');

  const { requestPasswordReset } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await requestPasswordReset(email);
      
      if (result.success) {
        setSessionToken(result.sessionToken);
        setSuccess(true);
      } else {
        setError(result.error || 'Failed to send OTP. Please try again.');
      }
    } catch (err) {
      setError(
        err.response?.data?.error || 
        'Failed to send OTP. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleOTPVerification = () => {
    // Navigate to OTP verification page with the session token
    navigate('/reset-password', {
      state: {
        sessionToken: sessionToken,
        email: email,
        verificationType: 'password_reset'
      }
    });
  };

  if (success) {
    return (
      <Container className="d-flex align-items-center justify-content-center min-vh-100 py-4">
        <Row className="w-100 justify-content-center">
          <Col md={6} lg={5} xl={4}>
            <Card className="shadow border-0">
              <Card.Body className="p-4 p-md-5 text-center">
                <div className="mb-4">
                  <div className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center" 
                       style={{ width: '80px', height: '80px' }}>
                    <i className="fas fa-shield-check text-white fs-2"></i>
                  </div>
                </div>
                
                <h3 className="text-success fw-bold mb-3">OTP Sent Successfully</h3>
                
                <p className="text-muted mb-4">
                  We've sent a 6-digit verification code to{' '}
                  <strong className="text-dark">{email}</strong>. 
                  Please check your email and enter the code to reset your password.
                </p>

                <div className="alert alert-info text-start small">
                  <i className="fas fa-info-circle me-2"></i>
                  <strong>Security Note:</strong> The OTP code will expire in 10 minutes 
                  for your protection.
                </div>

                <div className="d-grid gap-2 mt-4">
                  <Button
                    variant="primary"
                    onClick={handleOTPVerification}
                    size="lg"
                  >
                    <i className="fas fa-key me-2"></i>
                    Enter Verification Code
                  </Button>
                  
                  <Button
                    variant="outline-secondary"
                    onClick={() => setSuccess(false)}
                  >
                    <i className="fas fa-edit me-2"></i>
                    Change Email Address
                  </Button>
                  
                  <Link 
                    to="/login" 
                    className="btn btn-outline-primary text-decoration-none"
                  >
                    <i className="fas fa-arrow-left me-2"></i>
                    Back to Login
                  </Link>
                </div>

                <div className="mt-4 p-3 bg-light rounded small">
                  <p className="mb-2">
                    <i className="fas fa-question-circle me-2"></i>
                    Didn't receive the code?
                  </p>
                  <Button
                    variant="link"
                    className="p-0 text-decoration-none"
                    onClick={handleSubmit}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Resending OTP...
                      </>
                    ) : (
                      'Click here to resend OTP'
                    )}
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100 py-4">
      <Row className="w-100 justify-content-center">
        <Col md={6} lg={5} xl={4}>
          <Card className="shadow border-0">
            <Card.Body className="p-4 p-md-5">
              {/* Header */}
              <div className="text-center mb-4">
                <div className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                     style={{ width: '60px', height: '60px' }}>
                  <i className="fas fa-lock text-white fs-4"></i>
                </div>
                <h2 className="text-primary fw-bold">Reset Password</h2>
                <p className="text-muted">
                  Enter your school email address and we'll send a verification code to reset your password.
                </p>
              </div>

              {/* Error Alert */}
              {error && (
                <Alert variant="danger" className="mb-4" dismissible onClose={() => setError('')}>
                  <Alert.Heading className="h6 mb-2">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    Request Failed
                  </Alert.Heading>
                  {error}
                </Alert>
              )}

              {/* Reset Form */}
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-4">
                  <Form.Label className="fw-semibold">
                    School Email Address <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="your.name@delvok.edu"
                    autoComplete="email"
                    className="py-2"
                  />
                  <Form.Text className="text-muted small">
                    Enter the email address associated with your Delvok Academy account.
                  </Form.Text>
                </Form.Group>

                {/* Submit Button */}
                <div className="d-grid mb-4">
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={loading || !email}
                    size="lg"
                    className="fw-semibold py-2"
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Sending OTP...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-paper-plane me-2"></i>
                        Send Verification Code
                      </>
                    )}
                  </Button>
                </div>
              </Form>

              {/* Security Information */}
              <div className="p-3 bg-light rounded small mb-4">
                <h6 className="fw-semibold mb-2">
                  <i className="fas fa-shield-alt me-2"></i>
                  Security Process
                </h6>
                <ul className="mb-0 ps-3">
                  <li>Enter your registered school email</li>
                  <li>Receive a 6-digit OTP via email</li>
                  <li>Verify OTP to reset your password</li>
                  <li>OTP expires in 10 minutes for security</li>
                </ul>
              </div>

              {/* Back to Login */}
              <div className="text-center">
                <Link 
                  to="/login" 
                  className="btn btn-outline-primary text-decoration-none"
                >
                  <i className="fas fa-arrow-left me-2"></i>
                  Back to Login
                </Link>
              </div>

              {/* Support Contact */}
              <div className="text-center mt-3">
                <small className="text-muted">
                  Need assistance? Contact{' '}
                  <a href="mailto:support@delvok.edu" className="text-decoration-none">
                    support@delvok.edu
                  </a>
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ForgotPassword;