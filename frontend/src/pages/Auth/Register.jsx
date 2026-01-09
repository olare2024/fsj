import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Alert, 
  Form, 
  Button, 
  Card, 
  Container, 
  Row, 
  Col, 
  Spinner,
  ProgressBar,
  Tooltip,
  OverlayTrigger,
  Accordion,
  Badge,
  ListGroup
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

// Temporary inline components to avoid import errors
const PasswordStrengthMeter = ({ strength, messages }) => {
  const getVariant = (strength) => {
    if (strength >= 80) return 'success';
    if (strength >= 60) return 'info';
    if (strength >= 40) return 'warning';
    return 'danger';
  };

  const getLabel = (strength) => {
    if (strength >= 80) return 'Strong';
    if (strength >= 60) return 'Good';
    if (strength >= 40) return 'Fair';
    return 'Weak';
  };

  return (
    <div className="mt-2">
      <div className="d-flex justify-content-between align-items-center mb-1">
        <small className="text-muted">Password Strength</small>
        <Badge bg={getVariant(strength)}>{getLabel(strength)}</Badge>
      </div>
      <ProgressBar 
        now={strength} 
        variant={getVariant(strength)}
        className="mb-2"
      />
      {messages.length > 0 && (
        <ListGroup variant="flush">
          {messages.map((message, index) => (
            <ListGroup.Item 
              key={index} 
              className="p-1 border-0"
              style={{ fontSize: '0.8rem' }}
            >
              <i className="fas fa-exclamation-circle text-warning me-2"></i>
              {message}
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
    </div>
  );
};

const CurriculumInfo = ({ curriculum }) => {
  const curriculumData = {
    cbc: {
      name: 'CBC (Competency Based Curriculum)',
      description: 'Kenya\'s new education system focusing on competencies and skills development',
      levels: ['Pre-Primary (PP1-PP2)', 'Lower Primary (Grade 1-3)', 'Upper Primary (Grade 4-6)', 'Junior Secondary (Grade 7-9)', 'Senior Secondary (Grade 10-12)'],
      features: ['Competency-based', 'Flexible learning paths', 'Focus on skills', 'Digital literacy']
    },
    igcse: {
      name: 'IGCSE (Cambridge)',
      description: 'International General Certificate of Secondary Education - globally recognized qualification',
      levels: ['Lower Secondary (Year 7-9)', 'IGCSE (Year 10-11)', 'A-Levels (Year 12-13)'],
      features: ['International recognition', 'Broad curriculum', 'University preparation', 'Global perspective']
    },
    ib: {
      name: 'International Baccalaureate (IB)',
      description: 'Comprehensive international education program promoting intercultural understanding',
      levels: ['Primary Years Programme (PYP)', 'Middle Years Programme (MYP)', 'Diploma Programme (DP)'],
      features: ['International mindedness', 'Holistic education', 'Critical thinking', 'Research skills']
    },
    american: {
      name: 'American Curriculum',
      description: 'US-based education system with standardized testing and college preparation',
      levels: ['Elementary School', 'Middle School', 'High School'],
      features: ['Standardized testing', 'College prep', 'Elective courses', 'AP classes']
    }
  };

  if (!curriculum || !curriculumData[curriculum]) {
    return null;
  }

  const data = curriculumData[curriculum];

  return (
    <Card className="mt-2 border-info">
      <Card.Header className="bg-info text-white py-2">
        <strong>{data.name}</strong>
      </Card.Header>
      <Card.Body className="p-3">
        <p className="mb-2">{data.description}</p>
        
        <div className="mb-2">
          <strong>Education Levels:</strong>
          <ul className="mb-1">
            {data.levels.map((level, index) => (
              <li key={index} style={{ fontSize: '0.9rem' }}>{level}</li>
            ))}
          </ul>
        </div>

        <div>
          <strong>Key Features:</strong>
          <div className="mt-1">
            {data.features.map((feature, index) => (
              <Badge key={index} bg="outline-info" text="dark" className="me-1 mb-1">
                {feature}
              </Badge>
            ))}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

const Register = () => {
  const { 
    register, 
    loading: authLoading,
    error: authError,
    clearError
  } = useAuth();
  
  const location = useLocation();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    role: 'student',
    phone: '',
    date_of_birth: '',
    gender: '',
    curriculum: '',
    county: '',
    town: '',
    estate: '',
    address: '',
    email_notifications: true,
    sms_notifications: false,
    preferred_otp_medium: 'email'
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [progress, setProgress] = useState(0);
  const [success, setSuccess] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [requiresOTP, setRequiresOTP] = useState(false);
  const navigate = useNavigate();

  // Enhanced Kenyan counties with regions
  const kenyanCounties = [
    { value: 'nairobi', label: 'Nairobi', region: 'Central' },
    { value: 'mombasa', label: 'Mombasa', region: 'Coast' },
    { value: 'kisumu', label: 'Kisumu', region: 'Nyanza' },
    { value: 'nakuru', label: 'Nakuru', region: 'Rift Valley' },
    { value: 'eldoret', label: 'Eldoret', region: 'Rift Valley' },
    { value: 'meru', label: 'Meru', region: 'Eastern' },
    { value: 'kiambu', label: 'Kiambu', region: 'Central' },
    { value: 'kakamega', label: 'Kakamega', region: 'Western' },
    { value: 'kisii', label: 'Kisii', region: 'Nyanza' },
    { value: 'nyeri', label: 'Nyeri', region: 'Central' },
    { value: 'machakos', label: 'Machakos', region: 'Eastern' },
    { value: 'thika', label: 'Thika', region: 'Central' },
    { value: 'malindi', label: 'Malindi', region: 'Coast' },
    { value: 'garissa', label: 'Garissa', region: 'North Eastern' }
  ];

  // Enhanced curriculum options with descriptions
  const curriculumOptions = [
    { 
      value: 'cbc', 
      label: 'CBC (Competency Based Curriculum)'
    },
    { 
      value: 'igcse', 
      label: 'IGCSE (Cambridge)'
    },
    { 
      value: 'ib', 
      label: 'International Baccalaureate (IB)'
    },
    { 
      value: 'american', 
      label: 'American Curriculum'
    },
  ];

  // Role descriptions
  const roleDescriptions = {
    student: 'For learners joining Delvok Academy programs',
    parent: 'For parents/guardians monitoring student progress',
    teacher: 'For educators and teaching staff',
    staff: 'For administrative and support staff'
  };

  // Calculate progress based on form completion
  useEffect(() => {
    calculateProgress();
  }, [formData]);

  // Clear auth errors when component mounts
  useEffect(() => {
    clearError();
  }, [clearError]);

  const calculateProgress = () => {
    let completed = 0;
    const totalFields = 8; // Basic required fields

    if (formData.first_name.trim()) completed++;
    if (formData.last_name.trim()) completed++;
    if (formData.email.trim()) completed++;
    if (formData.password) completed++;
    if (formData.password_confirm) completed++;
    if (formData.role) completed++;
    
    // Role-specific fields
    if (formData.role === 'student') {
      if (formData.date_of_birth) completed++;
      if (formData.curriculum) completed++;
      if (formData.county) completed++;
    }

    const progressPercentage = Math.min(100, Math.round((completed / totalFields) * 100));
    setProgress(progressPercentage);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    
    // Clear specific error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
    if (error) setError('');
    if (authError) clearError();
  };

  // Enhanced password strength validation
  const validatePasswordStrength = (password) => {
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[@$!%*?&]/.test(password),
    };

    const strength = Object.values(checks).filter(Boolean).length;
    const messages = [];

    if (!checks.length) messages.push('At least 8 characters');
    if (!checks.uppercase) messages.push('One uppercase letter');
    if (!checks.lowercase) messages.push('One lowercase letter');
    if (!checks.number) messages.push('One number');
    if (!checks.special) messages.push('One special character (@$!%*?&)');

    return {
      strength: (strength / 5) * 100,
      isValid: strength >= 4, // Require at least 4 out of 5 checks
      messages
    };
  };

  // Enhanced client-side validation
  const validateForm = () => {
    const errors = {};
    const passwordStrength = validatePasswordStrength(formData.password);

    // Required fields validation
    if (!formData.first_name?.trim()) {
      errors.first_name = 'First name is required';
    } else if (formData.first_name.trim().length < 2) {
      errors.first_name = 'First name must be at least 2 characters';
    }

    if (!formData.last_name?.trim()) {
      errors.last_name = 'Last name is required';
    } else if (formData.last_name.trim().length < 2) {
      errors.last_name = 'Last name must be at least 2 characters';
    }

    if (!formData.email?.trim()) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (!passwordStrength.isValid) {
      errors.password = 'Password does not meet strength requirements';
    }

    if (!formData.password_confirm) {
      errors.password_confirm = 'Please confirm your password';
    } else if (formData.password !== formData.password_confirm) {
      errors.password_confirm = 'Passwords do not match';
    }

    // Kenyan phone validation
    if (formData.phone && !/^(?:\+254|0)[17]\d{8}$/.test(formData.phone.replace(/\s/g, ''))) {
      errors.phone = 'Please enter a valid Kenyan phone number (e.g., +254712345678 or 0712345678)';
    }

    // Student-specific validation
    if (formData.role === 'student') {
      if (!formData.date_of_birth) {
        errors.date_of_birth = 'Date of birth is required for students';
      } else {
        const birthDate = new Date(formData.date_of_birth);
        const today = new Date();
        const age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        const adjustedAge = monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate()) 
          ? age - 1 
          : age;

        if (adjustedAge < 4) {
          errors.date_of_birth = 'Student must be at least 4 years old';
        } else if (adjustedAge > 25) {
          errors.date_of_birth = 'Student cannot be older than 25 years';
        }
      }

      if (!formData.curriculum) {
        errors.curriculum = 'Curriculum is required for students';
      }

      if (!formData.county) {
        errors.county = 'County is required for students';
      }
    }

    // County validation
    if (formData.county && !kenyanCounties.find(c => c.value === formData.county)) {
      errors.county = 'Please select a valid county';
    }

    return errors;
  };

  const formatPhoneNumber = (phone) => {
    // Remove all non-digit characters except +
    const cleaned = phone.replace(/[^\d+]/g, '');
    
    // Convert 07... to +2547...
    if (cleaned.startsWith('0') && cleaned.length === 10) {
      return '+254' + cleaned.substring(1);
    }
    
    // Ensure +254 format
    if (cleaned.startsWith('254') && !cleaned.startsWith('+254')) {
      return '+' + cleaned;
    }
    
    return cleaned;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setValidationErrors({});
    setRequiresOTP(false);
    clearError();
    
    // Client-side validation
    const clientErrors = validateForm();
    if (Object.keys(clientErrors).length > 0) {
      setValidationErrors(clientErrors);
      setError('Please fix the errors below before submitting');
      setLoading(false);
      return;
    }

    try {
      // Prepare data for API
      const userData = {
        email: formData.email.toLowerCase().trim(),
        password: formData.password,
        password_confirm: formData.password_confirm,
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        role: formData.role,
        phone: formData.phone ? formatPhoneNumber(formData.phone.trim()) : '',
        date_of_birth: formData.date_of_birth || '',
        gender: formData.gender || '',
        curriculum: formData.curriculum || '',
        county: formData.county || '',
        town: formData.town || '',
        estate: formData.estate || '',
        address: formData.address || '',
        email_notifications: formData.email_notifications,
        sms_notifications: formData.sms_notifications,
        preferred_otp_medium: formData.preferred_otp_medium
      };

      console.log('Sending registration data:', userData);

      const result = await register(userData);
      console.log('Registration result:', result);

      if (result.success) {
        if (result.requiresOTP) {
          // OTP verification required - redirect to verification page
          setRequiresOTP(true);
          setRegisteredEmail(formData.email);
          
          // Redirect to verification page
          navigate('/verify-account', {
            state: {
              type: 'registration',
              email: formData.email,
              sessionToken: result.sessionToken,
              userId: result.userId
            }
          });
        } else {
          // Direct registration success (OTP disabled)
          setSuccess(true);
          setRegisteredEmail(formData.email);
          setError('');
          
          // Auto-redirect after 3 seconds
          setTimeout(() => {
            navigate('/login', { 
              state: { 
                message: 'Registration successful! You can now login to your account.',
                email: formData.email,
                registrationSuccess: true
              }
            });
          }, 3000);
        }
      } else {
        // Enhanced error handling
        if (result.error) {
          // Handle object errors properly
          if (typeof result.error === 'object') {
            if (result.error.validationErrors) {
              setValidationErrors(result.error.validationErrors);
              setError('Please fix the validation errors below');
            } else if (result.error.details) {
              setValidationErrors(result.error.details);
              setError('Please fix the validation errors below');
            } else {
              setError(result.error.message || 'Registration failed. Please check the form for errors.');
            }
          } else if (typeof result.error === 'string') {
            setError(result.error);
          }
        } else if (result.message) {
          setError(result.message);
        } else {
          setError('Registration failed. Please try again.');
        }
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const isStudent = formData.role === 'student';
  const passwordStrength = validatePasswordStrength(formData.password);

  // OTP Required state - show loading while redirecting
  if (requiresOTP) {
    return (
      <Container className="mt-5">
        <Row className="justify-content-center">
          <Col md={8} lg={6}>
            <Card className="shadow border-0 text-center">
              <Card.Body className="p-5">
                <div className="text-primary mb-4">
                  <i className="fas fa-envelope fa-4x"></i>
                </div>
                <h2 className="text-primary mb-3">Verification Required</h2>
                <p className="lead mb-4">
                  Redirecting to verification page...
                </p>
                
                <Spinner animation="border" variant="primary" className="mb-3" />
                
                <Alert variant="info" className="text-start">
                  <Alert.Heading className="h6">
                    <i className="fas fa-info-circle me-2"></i>
                    Account Verification
                  </Alert.Heading>
                  <p className="mb-2">
                    We've sent a verification code to <strong>{registeredEmail}</strong>. 
                    Please check your email and enter the code to complete your registration.
                  </p>
                </Alert>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  // Success state (for direct registration without OTP)
  if (success) {
    return (
      <Container className="mt-5">
        <Row className="justify-content-center">
          <Col md={8} lg={6}>
            <Card className="shadow border-0 text-center">
              <Card.Body className="p-5">
                <div className="text-success mb-4">
                  <i className="fas fa-check-circle fa-4x"></i>
                </div>
                <h2 className="text-success mb-3">Registration Successful!</h2>
                <p className="lead mb-4">
                  Welcome to Delvok Academy! Your account has been created successfully.
                </p>
                
                <Alert variant="success" className="text-start">
                  <Alert.Heading className="h6">
                    <i className="fas fa-rocket me-2"></i>
                    Ready to Login
                  </Alert.Heading>
                  <p className="mb-2">
                    Your account has been created and you can now login to access all features.
                  </p>
                  <small className="text-muted">
                    Redirecting to login page automatically...
                  </small>
                </Alert>

                <div className="d-grid gap-2">
                  <Button 
                    variant="primary" 
                    onClick={() => navigate('/login')}
                    size="lg"
                  >
                    <i className="fas fa-sign-in-alt me-2"></i>
                    Continue to Login Now
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
    <Container className="mt-4 mb-5">
      <Row className="justify-content-center">
        <Col md={10} lg={8}>
          <Card className="shadow border-0">
            <Card.Header className="bg-primary text-white py-3">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4 className="mb-0">
                    <i className="fas fa-user-plus me-2"></i>
                    Join Delvok Academy
                  </h4>
                  <small>Create your account to start your educational journey</small>
                </div>
                <Badge bg="light" text="dark">
                  Progress: {progress}%
                </Badge>
              </div>
            </Card.Header>
            
            <Card.Body className="p-4 p-md-5">
              {/* Progress Bar */}
              <div className="mb-4">
                <div className="d-flex justify-content-between mb-2">
                  <small className="text-muted">Profile Completion</small>
                  <small className="text-muted">{progress}%</small>
                </div>
                <ProgressBar 
                  now={progress} 
                  variant={progress >= 80 ? "success" : progress >= 50 ? "warning" : "primary"}
                  animated 
                />
              </div>

              {/* Error Display */}
              {(error || authError) && (
                <Alert variant="danger" className="mb-4" dismissible onClose={() => { setError(''); clearError(); }}>
                  <Alert.Heading className="h6 mb-2">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    Registration Failed
                  </Alert.Heading>
                  {error || authError}
                </Alert>
              )}

              {/* Success message from location state */}
              {location.state?.message && (
                <Alert variant="success" className="mb-4">
                  <i className="fas fa-check-circle me-2"></i>
                  {location.state.message}
                </Alert>
              )}

              <Form onSubmit={handleSubmit} noValidate>
                {/* Personal Information Section */}
                <Accordion defaultActiveKey="0" className="mb-4">
                  <Accordion.Item eventKey="0">
                    <Accordion.Header>
                      <i className="fas fa-user me-2 text-primary"></i>
                      Personal Information
                      {formData.first_name && formData.last_name && (
                        <Badge bg="success" className="ms-2">
                          <i className="fas fa-check me-1"></i>
                          Complete
                        </Badge>
                      )}
                    </Accordion.Header>
                    <Accordion.Body>
                      <Row>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">
                              First Name <span className="text-danger">*</span>
                            </Form.Label>
                            <Form.Control
                              type="text"
                              name="first_name"
                              value={formData.first_name}
                              onChange={handleChange}
                              isInvalid={!!validationErrors.first_name}
                              required
                              placeholder="Enter your first name"
                              disabled={loading}
                            />
                            <Form.Control.Feedback type="invalid">
                              {validationErrors.first_name}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">
                              Last Name <span className="text-danger">*</span>
                            </Form.Label>
                            <Form.Control
                              type="text"
                              name="last_name"
                              value={formData.last_name}
                              onChange={handleChange}
                              isInvalid={!!validationErrors.last_name}
                              required
                              placeholder="Enter your last name"
                              disabled={loading}
                            />
                            <Form.Control.Feedback type="invalid">
                              {validationErrors.last_name}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                      </Row>

                      <Row>
                        <Col md={8}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">
                              Email Address <span className="text-danger">*</span>
                            </Form.Label>
                            <OverlayTrigger
                              placement="top"
                              overlay={
                                <Tooltip>
                                  We'll send verification and important updates to this email
                                </Tooltip>
                              }
                            >
                              <Form.Control
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.email}
                                required
                                placeholder="your.email@example.com"
                                disabled={loading}
                              />
                            </OverlayTrigger>
                            <Form.Control.Feedback type="invalid">
                              {validationErrors.email}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">
                              Phone Number
                              <OverlayTrigger
                                placement="top"
                                overlay={
                                  <Tooltip>
                                    Kenyan format: +254712345678 or 0712345678
                                  </Tooltip>
                                }
                              >
                                <i className="fas fa-info-circle ms-1 text-muted"></i>
                              </OverlayTrigger>
                            </Form.Label>
                            <Form.Control
                              type="tel"
                              name="phone"
                              value={formData.phone}
                              onChange={handleChange}
                              isInvalid={!!validationErrors.phone}
                              placeholder="0712345678"
                              disabled={loading}
                            />
                            <Form.Control.Feedback type="invalid">
                              {validationErrors.phone}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                      </Row>
                    </Accordion.Body>
                  </Accordion.Item>

                  {/* Role Selection */}
                  <Accordion.Item eventKey="1">
                    <Accordion.Header>
                      <i className="fas fa-id-card me-2 text-primary"></i>
                      Account Type
                      {formData.role && (
                        <Badge bg="success" className="ms-2">
                          Selected
                        </Badge>
                      )}
                    </Accordion.Header>
                    <Accordion.Body>
                      <Form.Group className="mb-3">
                        <Form.Label className="fw-semibold">
                          I am a <span className="text-danger">*</span>
                        </Form.Label>
                        <Form.Select
                          name="role"
                          value={formData.role}
                          onChange={handleChange}
                          isInvalid={!!validationErrors.role}
                          required
                          disabled={loading}
                        >
                          <option value="student">Student</option>
                          <option value="parent">Parent/Guardian</option>
                          <option value="teacher">Teacher</option>
                          <option value="staff">Staff</option>
                        </Form.Select>
                        <Form.Text className="text-muted">
                          <i className="fas fa-info-circle me-1"></i>
                          {roleDescriptions[formData.role]}
                        </Form.Text>
                        <Form.Control.Feedback type="invalid">
                          {validationErrors.role}
                        </Form.Control.Feedback>
                      </Form.Group>
                    </Accordion.Body>
                  </Accordion.Item>

                  {/* Student-specific fields */}
                  {isStudent && (
                    <Accordion.Item eventKey="2">
                      <Accordion.Header>
                        <i className="fas fa-graduation-cap me-2 text-primary"></i>
                        Student Information
                        {(formData.date_of_birth && formData.curriculum && formData.county) && (
                          <Badge bg="success" className="ms-2">
                            <i className="fas fa-check me-1"></i>
                            Complete
                          </Badge>
                        )}
                      </Accordion.Header>
                      <Accordion.Body>
                        <Row>
                          <Col md={6}>
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">
                                Date of Birth <span className="text-danger">*</span>
                              </Form.Label>
                              <Form.Control
                                type="date"
                                name="date_of_birth"
                                value={formData.date_of_birth}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.date_of_birth}
                                required
                                max={new Date().toISOString().split('T')[0]}
                                disabled={loading}
                              />
                              <Form.Control.Feedback type="invalid">
                                {validationErrors.date_of_birth}
                              </Form.Control.Feedback>
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">Gender</Form.Label>
                              <Form.Select
                                name="gender"
                                value={formData.gender}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.gender}
                                disabled={loading}
                              >
                                <option value="">Select Gender</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                                <option value="prefer_not_to_say">Prefer not to say</option>
                              </Form.Select>
                              <Form.Control.Feedback type="invalid">
                                {validationErrors.gender}
                              </Form.Control.Feedback>
                            </Form.Group>
                          </Col>
                        </Row>

                        <Row>
                          <Col md={6}>
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">
                                Curriculum <span className="text-danger">*</span>
                              </Form.Label>
                              <Form.Select
                                name="curriculum"
                                value={formData.curriculum}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.curriculum}
                                required
                                disabled={loading}
                              >
                                <option value="">Select Curriculum</option>
                                {curriculumOptions.map(option => (
                                  <option key={option.value} value={option.value}>
                                    {option.label}
                                  </option>
                                ))}
                              </Form.Select>
                              {formData.curriculum && (
                                <CurriculumInfo curriculum={formData.curriculum} />
                              )}
                              <Form.Control.Feedback type="invalid">
                                {validationErrors.curriculum}
                              </Form.Control.Feedback>
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">
                                County <span className="text-danger">*</span>
                              </Form.Label>
                              <Form.Select
                                name="county"
                                value={formData.county}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.county}
                                required
                                disabled={loading}
                              >
                                <option value="">Select County</option>
                                {kenyanCounties.map(county => (
                                  <option key={county.value} value={county.value}>
                                    {county.label} ({county.region})
                                  </option>
                                ))}
                              </Form.Select>
                              <Form.Control.Feedback type="invalid">
                                {validationErrors.county}
                              </Form.Control.Feedback>
                            </Form.Group>
                          </Col>
                        </Row>

                        <Row>
                          <Col md={6}>
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">Town/Area</Form.Label>
                              <Form.Control
                                type="text"
                                name="town"
                                value={formData.town}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.town}
                                placeholder="Enter your town or area"
                                disabled={loading}
                              />
                              <Form.Control.Feedback type="invalid">
                                {validationErrors.town}
                              </Form.Control.Feedback>
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">Estate/Neighborhood</Form.Label>
                              <Form.Control
                                type="text"
                                name="estate"
                                value={formData.estate}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.estate}
                                placeholder="Enter your estate or neighborhood"
                                disabled={loading}
                              />
                              <Form.Control.Feedback type="invalid">
                                {validationErrors.estate}
                              </Form.Control.Feedback>
                            </Form.Group>
                          </Col>
                        </Row>

                        <Form.Group className="mb-3">
                          <Form.Label className="fw-semibold">Full Address</Form.Label>
                          <Form.Control
                            as="textarea"
                            rows={3}
                            name="address"
                            value={formData.address}
                            onChange={handleChange}
                            isInvalid={!!validationErrors.address}
                            placeholder="Enter your complete physical address including street, building, etc."
                            disabled={loading}
                          />
                          <Form.Control.Feedback type="invalid">
                            {validationErrors.address}
                          </Form.Control.Feedback>
                        </Form.Group>
                      </Accordion.Body>
                    </Accordion.Item>
                  )}

                  {/* Security Section */}
                  <Accordion.Item eventKey="3">
                    <Accordion.Header>
                      <i className="fas fa-lock me-2 text-primary"></i>
                      Security & Preferences
                      {formData.password && formData.password_confirm && (
                        <Badge bg="success" className="ms-2">
                          <i className="fas fa-check me-1"></i>
                          Complete
                        </Badge>
                      )}
                    </Accordion.Header>
                    <Accordion.Body>
                      <Row>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">
                              Password <span className="text-danger">*</span>
                            </Form.Label>
                            <div className="position-relative">
                              <Form.Control
                                type={showPassword ? "text" : "password"}
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.password}
                                required
                                minLength="8"
                                placeholder="Create a strong password"
                                disabled={loading}
                              />
                              <Button
                                variant="outline-secondary"
                                size="sm"
                                className="position-absolute end-0 top-50 translate-middle-y border-0"
                                onClick={() => setShowPassword(!showPassword)}
                                style={{ right: '10px' }}
                              >
                                <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                              </Button>
                            </div>
                            
                            {formData.password && (
                              <PasswordStrengthMeter 
                                strength={passwordStrength.strength}
                                messages={passwordStrength.messages}
                              />
                            )}
                            
                            <Form.Control.Feedback type="invalid">
                              {validationErrors.password}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">
                              Confirm Password <span className="text-danger">*</span>
                            </Form.Label>
                            <Form.Control
                              type="password"
                              name="password_confirm"
                              value={formData.password_confirm}
                              onChange={handleChange}
                              isInvalid={!!validationErrors.password_confirm}
                              required
                              minLength="8"
                              placeholder="Confirm your password"
                              disabled={loading}
                            />
                            <Form.Control.Feedback type="invalid">
                              {validationErrors.password_confirm}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                      </Row>

                      <Row>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">Communication Preferences</Form.Label>
                            <div>
                              <Form.Check
                                type="checkbox"
                                name="email_notifications"
                                checked={formData.email_notifications}
                                onChange={handleChange}
                                label="Email notifications"
                                disabled={loading}
                              />
                              <Form.Check
                                type="checkbox"
                                name="sms_notifications"
                                checked={formData.sms_notifications}
                                onChange={handleChange}
                                label="SMS notifications"
                                disabled={loading}
                              />
                            </div>
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold">Preferred Verification Method</Form.Label>
                            <Form.Select
                              name="preferred_otp_medium"
                              value={formData.preferred_otp_medium}
                              onChange={handleChange}
                              disabled={loading}
                            >
                              <option value="email">Email</option>
                              <option value="sms">SMS</option>
                            </Form.Select>
                            <Form.Text className="text-muted">
                              How would you like to receive verification codes?
                            </Form.Text>
                          </Form.Group>
                        </Col>
                      </Row>
                    </Accordion.Body>
                  </Accordion.Item>
                </Accordion>

                {/* Terms and Submit */}
                <div className="mb-4">
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      id="terms-agreement"
                      label={
                        <span>
                          I agree to the{' '}
                          <Link to="/terms" className="text-decoration-none" target="_blank">
                            Terms of Service
                          </Link>{' '}
                          and{' '}
                          <Link to="/privacy" className="text-decoration-none" target="_blank">
                            Privacy Policy
                          </Link>
                          <span className="text-danger">*</span>
                        </span>
                      }
                      required
                      disabled={loading}
                    />
                  </Form.Group>

                  <div className="d-grid">
                    <Button
                      variant="primary"
                      type="submit"
                      disabled={loading || authLoading}
                      size="lg"
                      className="fw-semibold py-3"
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
                          Creating Account...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-user-plus me-2"></i>
                          Create Account
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </Form>

              <hr className="my-4" />

              <div className="text-center">
                <p className="text-muted mb-0">
                  Already have an account?{' '}
                  <Link 
                    to="/login" 
                    className="text-decoration-none fw-semibold text-primary"
                  >
                    <i className="fas fa-sign-in-alt me-1"></i>
                    Sign in here
                  </Link>
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Register;