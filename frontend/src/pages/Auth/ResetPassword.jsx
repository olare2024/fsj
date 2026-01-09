import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const ResetPassword = () => {
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [validToken, setValidToken] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const { confirmResetPassword } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  useEffect(() => {
    // Validate token on component mount
    if (!token) {
      setError('Invalid or missing reset token. Please request a new password reset.');
      return;
    }
    
    // In a real app, you would validate the token with your backend
    // For now, we'll assume it's valid if it exists
    setValidToken(true);
  }, [token]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validatePassword = (password) => {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return {
      isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar,
      requirements: {
        minLength: password.length >= minLength,
        hasUpperCase,
        hasLowerCase,
        hasNumbers,
        hasSpecialChar
      }
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.isValid) {
      setError('Password does not meet security requirements');
      return;
    }

    setLoading(true);

    try {
      await confirmResetPassword(token, formData.password);
      setMessage('Password has been successfully reset. You can now sign in with your new password.');
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login', { replace: true });
      }, 3000);
    } catch (err) {
      setError('Failed to reset password. The reset link may have expired. Please request a new one.');
      console.error('Password reset confirmation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const passwordValidation = validatePassword(formData.password);

  if (!validToken && error) {
    return (
      <Container fluid className="bg-light min-vh-100 d-flex align-items-center">
        <Row className="w-100 justify-content-center">
          <Col xs={12} sm={10} md={6} lg={4}>
            <Card className="shadow">
              <Card.Body className="text-center p-4">
                <i className="bi bi-exclamation-triangle text-warning" style={{ fontSize: '3rem' }}></i>
                <h4 className="mt-3 text-danger">Invalid Reset Link</h4>
                <p className="text-muted mb-4">{error}</p>
                <Button as={Link} to="/forgot-password" variant="primary">
                  Request New Reset Link
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <Container fluid className="bg-light min-vh-100 d-flex align-items-center">
      <Row className="w-100 justify-content-center">
        <Col xs={12} sm={10} md={6} lg={4}>
          {/* School Logo and Header */}
          <div className="text-center mb-4">
            <img 
              src="/images/delvok-logo.png" 
              alt="Delvok Academy" 
              style={{ height: '80px' }}
              className="mb-3"
            />
            <h2 className="text-primary">Create New Password</h2>
            <p className="text-muted">Enter your new password below</p>
          </div>

          <Card className="shadow">
            <Card.Body className="p-4">
              {error && (
                <Alert variant="danger" className="mb-3">
                  <i className="bi bi-exclamation-triangle-fill me-2"></i>
                  {error}
                </Alert>
              )}

              {message && (
                <Alert variant="success" className="mb-3">
                  <i className="bi bi-check-circle-fill me-2"></i>
                  {message}
                  <div className="mt-2">
                    <small>Redirecting to login page...</small>
                  </div>
                </Alert>
              )}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>New Password</Form.Label>
                  <div className="position-relative">
                    <Form.Control
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Enter new password"
                      required
                      disabled={loading || message}
                    />
                    <Button
                      variant="link"
                      className="position-absolute top-50 end-0 translate-middle-y text-muted"
                      onClick={() => setShowPassword(!showPassword)}
                      type="button"
                    >
                      <i className={`bi ${showPassword ? 'bi-eye-slash' : 'bi-eye'}`}></i>
                    </Button>
                  </div>
                  
                  {/* Password Requirements */}
                  {formData.password && (
                    <div className="mt-2">
                      <small className="text-muted">Password must contain:</small>
                      <ul className="small mb-0">
                        <li className={passwordValidation.requirements.minLength ? 'text-success' : 'text-danger'}>
                          {passwordValidation.requirements.minLength ? '✓' : '✗'} At least 8 characters
                        </li>
                        <li className={passwordValidation.requirements.hasUpperCase ? 'text-success' : 'text-danger'}>
                          {passwordValidation.requirements.hasUpperCase ? '✓' : '✗'} One uppercase letter
                        </li>
                        <li className={passwordValidation.requirements.hasLowerCase ? 'text-success' : 'text-danger'}>
                          {passwordValidation.requirements.hasLowerCase ? '✓' : '✗'} One lowercase letter
                        </li>
                        <li className={passwordValidation.requirements.hasNumbers ? 'text-success' : 'text-danger'}>
                          {passwordValidation.requirements.hasNumbers ? '✓' : '✗'} One number
                        </li>
                        <li className={passwordValidation.requirements.hasSpecialChar ? 'text-success' : 'text-danger'}>
                          {passwordValidation.requirements.hasSpecialChar ? '✓' : '✗'} One special character
                        </li>
                      </ul>
                    </div>
                  )}
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Confirm New Password</Form.Label>
                  <Form.Control
                    type={showPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="Confirm new password"
                    required
                    disabled={loading || message}
                  />
                  {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                    <Form.Text className="text-danger">
                      <i className="bi bi-exclamation-triangle me-1"></i>
                      Passwords do not match
                    </Form.Text>
                  )}
                  {formData.confirmPassword && formData.password === formData.confirmPassword && passwordValidation.isValid && (
                    <Form.Text className="text-success">
                      <i className="bi bi-check-circle me-1"></i>
                      Passwords match and meet requirements
                    </Form.Text>
                  )}
                </Form.Group>

                <Button
                  variant="success"
                  type="submit"
                  className="w-100 py-2"
                  disabled={loading || message || !passwordValidation.isValid || formData.password !== formData.confirmPassword}
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
                      Resetting Password...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-shield-check me-2"></i>
                      Reset Password
                    </>
                  )}
                </Button>
              </Form>

              {/* Security Tips */}
              <div className="mt-4">
                <Alert variant="warning" className="mb-0">
                  <h6 className="alert-heading">
                    <i className="bi bi-shield-exclamation me-2"></i>
                    Security Tips
                  </h6>
                  <ul className="mb-0 small">
                    <li>Use a unique password you haven't used elsewhere</li>
                    <li>Consider using a password manager</li>
                    <li>Enable two-factor authentication for added security</li>
                    <li>Never share your password with anyone</li>
                  </ul>
                </Alert>
              </div>

              {/* Back to Login */}
              <div className="text-center mt-4">
                <Link to="/login" className="text-decoration-none">
                  <i className="bi bi-arrow-left me-1"></i>
                  Back to Sign In
                </Link>
              </div>
            </Card.Body>
          </Card>

          {/* Additional Support */}
          <Card className="mt-4">
            <Card.Body className="text-center">
              <h6>Still having trouble?</h6>
              <p className="small text-muted mb-2">
                Our support team is here to help you
              </p>
              <Button as={Link} to="/contact" variant="outline-primary" size="sm">
                Contact Support
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ResetPassword;