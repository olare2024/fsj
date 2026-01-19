// src/pages/Auth/Login.jsx - CLEANED VERSION
import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Form, 
  Button, 
  Alert, 
  Spinner,
  InputGroup
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

const Login = () => {
  const { 
    login, 
    loading, 
    error, 
    clearError,
    isAuthenticated,
    currentUser
  } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [localLoading, setLocalLoading] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && currentUser) {
      const redirectPath = getDashboardPath(currentUser);
      navigate(redirectPath, { replace: true });
    }
  }, [isAuthenticated, currentUser, navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear field-specific errors
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    if (error) clearError();
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.email) {
      errors.email = 'School email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Please enter a valid school email address';
    }
    
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const getDashboardPath = (user) => {
    if (!user) return '-portal';
    
    switch (user.role) {
      case 'student':
        return '/student-portal';
      case 'teacher':
        return '/teacher-portal';
      case 'parent':
        return '/parent-portal';
      case 'admin':
        return '/admin-portal';
      case 'accountant':
        return '/finance-portal';
      case 'head_teacher':
        return '/head-teacher-portal';
      case 'curriculum_coordinator':
        return '/curriculum-portal';
      case 'librarian':
        return '/library-portal';
      case 'counselor':
        return '/counselor-portal';
      case 'it_support':
        return '/it-portal';
      case 'office_staff':
        return '/staff-portal';
      default:
        return '-portal';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalLoading(true);
    clearError();
    
    if (!validateForm()) {
      setLocalLoading(false);
      return;
    }

    try {
      const result = await login(formData);
      
      if (result.success) {
        if (result.requires_2fa) {
          navigate('/verify-otp', {
            state: {
              email: formData.email,
              session_token: result.session_token,
              user_id: result.user_id,
              method: result.method,
              masked_email: result.masked_email || formData.email,
              expires_in: result.expires_in,
              message: result.message,
              purpose: 'login',
              intended_redirect: result.redirect_url || getDashboardPath(result.user)
            },
            replace: true
          });
        } else {
          // Direct login successful, redirect to appropriate dashboard
          const redirectPath = result.redirect_url || getDashboardPath(result.user);
          navigate(redirectPath, { 
            replace: true,
            state: { 
              message: 'Login successful! Welcome to Delvok Academy.',
              type: 'success',
              user: result.user
            }
          });
        }
      }
    } catch (error) {
      // Error is handled by the AuthContext
    } finally {
      setLocalLoading(false);
    }
  };

  const isLoading = loading || localLoading;

  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100 py-4">
      <Row className="w-100 justify-content-center">
        <Col md={6} lg={5} xl={4}>
          <Card className="shadow border-0 auth-card">
            <Card.Body className="p-4 p-md-5">
              {/* Header */}
              <div className="text-center mb-4">
                <div className="school-logo mb-3">
                  <i className="bi bi-mortarboard-fill text-primary" style={{ fontSize: '3rem' }}></i>
                </div>
                <h2 className="school-name text-primary fw-bold">Delvok Academy</h2>
                <p className="text-muted mb-3">School Management System</p>
                
                {/* Security Notice */}
                <div className="alert alert-info py-2 small mb-0">
                  <i className="bi bi-shield-check me-2"></i>
                  Secure login with OTP verification required for staff
                </div>
              </div>

              {/* Success/Info Messages */}
              {location.state?.message && (
                <Alert 
                  variant={location.state?.type === 'success' ? 'success' : 'info'} 
                  className="mb-4"
                >
                  <i className={`bi bi-${location.state?.type === 'success' ? 'check-circle' : 'info-circle'} me-2`}></i>
                  {location.state.message}
                </Alert>
              )}

              {/* Error Alert */}
              {error && (
                <Alert variant="danger" className="mb-4" dismissible onClose={clearError}>
                  <Alert.Heading className="h6 mb-2">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error.includes('locked') ? 'Account Locked' : 
                     error.includes('suspended') ? 'Account Suspended' : 'Login Failed'}
                  </Alert.Heading>
                  {error}
                  {error.includes('locked') && (
                    <div className="mt-2 small">
                      <i className="bi bi-info-circle me-1"></i>
                      Your account has been locked due to multiple failed login attempts. 
                      Please try again in 30 minutes or contact support.
                    </div>
                  )}
                </Alert>
              )}

              {/* Login Form */}
              <Form onSubmit={handleSubmit} noValidate>
                {/* Email Field */}
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold">
                    School Email <span className="text-danger">*</span>
                  </Form.Label>
                  <InputGroup>
                    <InputGroup.Text>
                      <i className="bi bi-envelope"></i>
                    </InputGroup.Text>
                    <Form.Control
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      isInvalid={!!fieldErrors.email}
                      required
                      placeholder="your.name@delvok.ac.ke"
                      autoComplete="email"
                      disabled={isLoading}
                      autoFocus
                    />
                  </InputGroup>
                  <Form.Control.Feedback type="invalid">
                    {fieldErrors.email}
                  </Form.Control.Feedback>
                </Form.Group>

                {/* Password Field */}
                <Form.Group className="mb-4">
                  <Form.Label className="fw-semibold">
                    Password <span className="text-danger">*</span>
                  </Form.Label>
                  <InputGroup>
                    <InputGroup.Text>
                      <i className="bi bi-lock"></i>
                    </InputGroup.Text>
                    <Form.Control
                      type={showPassword ? "text" : "password"}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      isInvalid={!!fieldErrors.password}
                      required
                      placeholder="Enter your password"
                      autoComplete="current-password"
                      disabled={isLoading}
                    />
                    <Button
                      variant="outline-secondary"
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={isLoading}
                    >
                      <i className={`bi bi-eye${showPassword ? '-slash' : ''}`}></i>
                    </Button>
                    <Form.Control.Feedback type="invalid">
                      {fieldErrors.password}
                    </Form.Control.Feedback>
                  </InputGroup>
                  
                  <div className="d-flex justify-content-between align-items-center mt-2">
                    <Form.Check
                      type="checkbox"
                      name="rememberMe"
                      checked={formData.rememberMe}
                      onChange={handleChange}
                      label="Remember me"
                      className="small"
                      disabled={isLoading}
                    />
                    <Link 
                      to="/forgot-password" 
                      className="text-decoration-none small"
                    >
                      Forgot password?
                    </Link>
                  </div>
                </Form.Group>

                {/* Submit Button */}
                <div className="d-grid">
                  <Button
                    variant="primary"
                    type="submit"
                    size="lg"
                    disabled={isLoading}
                    className="fw-semibold py-2"
                  >
                    {isLoading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Signing In...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-box-arrow-in-right me-2"></i>
                        Sign In & Verify
                      </>
                    )}
                  </Button>
                </div>
              </Form>

              {/* Security Information */}
              <div className="mt-4 p-3 bg-light rounded small">
                <h6 className="fw-semibold mb-2">
                  <i className="bi bi-shield-check me-2"></i>
                  Security Information
                </h6>
                <ul className="mb-0 ps-3">
                  <li>Two-factor authentication required for staff accounts</li>
                  <li>OTP sent to your registered email/phone</li>
                  <li>Verification codes expire after 10 minutes</li>
                  <li>All login activities are monitored and logged</li>
                  <li>Use school-issued email addresses only</li>
                </ul>
              </div>

              {/* Registration Link */}
              <hr className="my-4" />
              <div className="text-center">
                <p className="text-muted mb-2">
                  New to Delvok Academy?
                </p>
                <Link 
                  to="/contact" 
                  className="btn btn-outline-primary"
                >
                  <i className="bi bi-person-plus me-2"></i>
                  Contact Us
                </Link>
              </div>

              {/* Support Contact */}
              <div className="text-center mt-3">
                <small className="text-muted">
                  <i className="bi bi-headset me-1"></i>
                  Need help? Contact{' '}
                  <a href="mailto:support@delvok.ac.ke" className="text-decoration-none">
                    support@delvok.ac.ke
                  </a>
                </small>
              </div>

              {/* System Status */}
              <div className="text-center mt-2">
                <small className="text-success">
                  <i className="bi bi-check-circle me-1"></i>
                  System Status: Operational
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Login;