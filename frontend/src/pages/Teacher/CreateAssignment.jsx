// src/pages/Teacher/CreateAssignment.jsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  useNavigate, 
  useLocation, 
  useParams,
  Link 
} from 'react-router-dom';
import { 
  Container, 
  Row, 
  Col, 
  Card, 
  Form, 
  Button, 
  Alert, 
  Spinner,
  Badge,
  InputGroup,
  Modal,
  Tabs,
  Tab
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';
import assignmentsAPI, { ASSIGNMENT_CONSTANTS } from '../../services/assignmentsAPI';
import academicsAPI from '../../services/academicAPI';

// Icon components - using simple text or react-bootstrap icons
const Icon = ({ name, className = "", size = 16 }) => {
  const icons = {
    arrowLeft: '←',
    save: '💾',
    upload: '📤',
    clock: '🕒',
    calendar: '📅',
    book: '📚',
    users: '👥',
    award: '🏆',
    fileText: '📄',
    plus: '+',
    x: '×',
    alertCircle: '⚠️',
    checkCircle: '✓',
    copy: '📋',
    back: '↩',
    edit: '✏️',
    download: '⬇️',
    print: '🖨️'
  };
  
  return (
    <span 
      className={`icon ${className}`}
      style={{ fontSize: `${size}px` }}
    >
      {icons[name] || name}
    </span>
  );
};

// Validation utilities
const validateAssignmentData = (data) => {
  const errors = {};
  
  if (!data.title?.trim()) {
    errors.title = 'Assignment title is required';
  } else if (data.title.length < 3) {
    errors.title = 'Title must be at least 3 characters';
  }
  
  if (!data.description?.trim()) {
    errors.description = 'Description is required';
  }
  
  if (!data.assignment_type) {
    errors.assignment_type = 'Assignment type is required';
  }
  
  if (!data.due_date) {
    errors.due_date = 'Due date is required';
  } else {
    const dueDate = new Date(data.due_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (dueDate < today) {
      errors.due_date = 'Due date cannot be in the past';
    }
  }
  
  if (data.total_marks) {
    const marks = parseFloat(data.total_marks);
    if (marks <= 0) {
      errors.total_marks = 'Total marks must be greater than 0';
    }
    if (marks > 1000) {
      errors.total_marks = 'Total marks cannot exceed 1000';
    }
  }
  
  if (data.passing_marks && data.total_marks) {
    const passing = parseFloat(data.passing_marks);
    const total = parseFloat(data.total_marks);
    if (passing > total) {
      errors.passing_marks = 'Passing marks cannot exceed total marks';
    }
  }
  
  if (data.available_from && data.due_date) {
    const availableFrom = new Date(data.available_from);
    const dueDate = new Date(data.due_date);
    
    if (availableFrom > dueDate) {
      errors.available_from = 'Available from date must be before due date';
    }
  }
  
  if (data.late_submission_penalty) {
    const penalty = parseFloat(data.late_submission_penalty);
    if (penalty < 0 || penalty > 100) {
      errors.late_submission_penalty = 'Penalty must be between 0 and 100%';
    }
  }
  
  if (!data.subject_ids?.length) {
    errors.subject_ids = 'At least one subject is required';
  }
  
  if (!data.class_ids?.length) {
    errors.class_ids = 'At least one class is required';
  }
  
  return errors;
};

const CreateAssignment = () => {
  const { currentUser, isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  
  const isEditMode = Boolean(id);
  
  // ==================== STATE ====================
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [academicData, setAcademicData] = useState({
    subjects: [],
    classes: [],
    gradeLevels: []
  });
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assignment_type: ASSIGNMENT_CONSTANTS.TYPES.HOMEWORK,
    difficulty_level: ASSIGNMENT_CONSTANTS.DIFFICULTY.MEDIUM,
    status: ASSIGNMENT_CONSTANTS.STATUS.DRAFT,
    
    // Academic data
    subject_ids: [],
    class_ids: [],
    grade_level_ids: [],
    academic_year_id: '',
    academic_term_id: '',
    
    // Dates
    due_date: '',
    available_from: '',
    
    // Grading
    total_marks: '',
    passing_marks: '',
    grading_rubric: '',
    
    // Submission settings
    allow_late_submission: false,
    late_submission_penalty: '',
    late_submission_deadline: '',
    max_resubmissions: 0,
    allow_attachments: true,
    max_attachment_size: 10, // MB
    allowed_file_types: ['.pdf', '.doc', '.docx', '.jpg', '.png'],
    
    // Additional settings
    is_group_assignment: false,
    max_group_size: 1,
    requires_presentation: false,
    estimated_completion_time: '',
    
    // Instructions and resources
    instructions: '',
    resources: [],
    additional_notes: '',
    
    // Tags and categories
    tags: [],
    category_id: '',
    
    // Publishing
    publish_immediately: false,
    notify_students: false
  });
  
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [assignment, setAssignment] = useState(null);
  const [categories, setCategories] = useState([]);
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [availableClasses, setAvailableClasses] = useState([]);
  const [newResource, setNewResource] = useState('');
  const [newTag, setNewTag] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');
  
  // File upload state
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);
  
  // ==================== EFFECTS ====================
  
  // Check authentication
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login', { 
        state: { from: location.pathname } 
      });
      return;
    }
    
    if (currentUser && !currentUser.is_teacher && !currentUser.is_admin) {
      navigate('/unauthorized');
      return;
    }
  }, [authLoading, isAuthenticated, currentUser, navigate, location]);
  
  // Load academic data
  useEffect(() => {
    const loadAcademicData = async () => {
      try {
        setLoading(true);
        
        // Load subjects
        const subjectsResponse = await academicsAPI.getSubjects({ 
          page_size: 100,
          is_active: true 
        });
        
        // Load classes
        const classesResponse = await academicsAPI.getClassrooms({ 
          page_size: 100,
          is_active: true 
        });
        
        // Load categories
        const categoriesResponse = await assignmentsAPI.getCategories();
        
        setAvailableSubjects(subjectsResponse.success ? subjectsResponse.data.results : []);
        setAvailableClasses(classesResponse.success ? classesResponse.data.results : []);
        setCategories(categoriesResponse.success ? categoriesResponse.data.results : []);
        
        if (subjectsResponse.success && classesResponse.success) {
          setAcademicData({
            subjects: subjectsResponse.data.results,
            classes: classesResponse.data.results,
            gradeLevels: [] // You might need to load these separately
          });
        }
        
      } catch (error) {
        console.error('Error loading academic data:', error);
        setErrorMessage('Failed to load academic data');
      } finally {
        setLoading(false);
      }
    };
    
    if (isAuthenticated) {
      loadAcademicData();
    }
  }, [isAuthenticated]);
  
  // Load assignment data for editing
  useEffect(() => {
    if (isEditMode && id) {
      const loadAssignment = async () => {
        try {
          setLoading(true);
          const response = await assignmentsAPI.getAssignmentById(id);
          
          if (response.success) {
            const assignmentData = response.data;
            setAssignment(assignmentData);
            
            // Format dates for input fields
            const formatDateForInput = (dateString) => {
              if (!dateString) return '';
              const date = new Date(dateString);
              return date.toISOString().split('T')[0];
            };
            
            setFormData({
              ...formData,
              title: assignmentData.title || '',
              description: assignmentData.description || '',
              assignment_type: assignmentData.assignment_type || ASSIGNMENT_CONSTANTS.TYPES.HOMEWORK,
              difficulty_level: assignmentData.difficulty_level || ASSIGNMENT_CONSTANTS.DIFFICULTY.MEDIUM,
              status: assignmentData.status || ASSIGNMENT_CONSTANTS.STATUS.DRAFT,
              
              subject_ids: assignmentData.subjects?.map(s => s.id) || [],
              class_ids: assignmentData.classes?.map(c => c.id) || [],
              grade_level_ids: assignmentData.grade_levels?.map(g => g.id) || [],
              
              due_date: formatDateForInput(assignmentData.due_date),
              available_from: formatDateForInput(assignmentData.available_from),
              
              total_marks: assignmentData.total_marks || '',
              passing_marks: assignmentData.passing_marks || '',
              grading_rubric: assignmentData.grading_rubric || '',
              
              allow_late_submission: assignmentData.allow_late_submission || false,
              late_submission_penalty: assignmentData.late_submission_penalty || '',
              late_submission_deadline: formatDateForInput(assignmentData.late_submission_deadline),
              max_resubmissions: assignmentData.max_resubmissions || 0,
              allow_attachments: assignmentData.allow_attachments !== false,
              max_attachment_size: assignmentData.max_attachment_size || 10,
              allowed_file_types: assignmentData.allowed_file_types || ['.pdf', '.doc', '.docx', '.jpg', '.png'],
              
              is_group_assignment: assignmentData.is_group_assignment || false,
              max_group_size: assignmentData.max_group_size || 1,
              requires_presentation: assignmentData.requires_presentation || false,
              estimated_completion_time: assignmentData.estimated_completion_time || '',
              
              instructions: assignmentData.instructions || '',
              resources: assignmentData.resources || [],
              additional_notes: assignmentData.additional_notes || '',
              
              tags: assignmentData.tags || [],
              category_id: assignmentData.category?.id || '',
              
              publish_immediately: false,
              notify_students: false
            });
          } else {
            setErrorMessage('Failed to load assignment data');
          }
        } catch (error) {
          console.error('Error loading assignment:', error);
          setErrorMessage('Failed to load assignment data');
        } finally {
          setLoading(false);
        }
      };
      
      loadAssignment();
    }
  }, [isEditMode, id]);
  
  // ==================== HANDLERS ====================
  
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };
  
  const handleSelectChange = (name, selectedOptions) => {
    const values = selectedOptions.map(option => option.value);
    
    setFormData(prev => ({
      ...prev,
      [name]: values
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };
  
  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    
    const validFiles = files.filter(file => {
      const maxSize = formData.max_attachment_size * 1024 * 1024; // Convert MB to bytes
      
      if (file.size > maxSize) {
        alert(`File ${file.name} exceeds maximum size of ${formData.max_attachment_size}MB`);
        return false;
      }
      
      // Check file extension
      const extension = '.' + file.name.split('.').pop().toLowerCase();
      if (!formData.allowed_file_types.includes(extension)) {
        alert(`File type ${extension} is not allowed. Allowed types: ${formData.allowed_file_types.join(', ')}`);
        return false;
      }
      
      return true;
    });
    
    setAttachments(prev => [...prev, ...validFiles]);
  };
  
  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };
  
  const addResource = () => {
    if (newResource.trim()) {
      setFormData(prev => ({
        ...prev,
        resources: [...prev.resources, newResource.trim()]
      }));
      setNewResource('');
    }
  };
  
  const removeResource = (index) => {
    setFormData(prev => ({
      ...prev,
      resources: prev.resources.filter((_, i) => i !== index)
    }));
  };
  
  const addTag = () => {
    if (newTag.trim()) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };
  
  const removeTag = (index) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter((_, i) => i !== index)
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    const validationErrors = validateAssignmentData(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    
    setSubmitting(true);
    setErrorMessage('');
    setSuccessMessage('');
    
    try {
      // Prepare data for API
      const submissionData = assignmentsAPI.formatAssignmentData(formData);
      
      let response;
      
      if (isEditMode) {
        // Update existing assignment
        response = await assignmentsAPI.updateAssignment(id, submissionData);
      } else {
        // Create new assignment
        response = await assignmentsAPI.createAssignment(submissionData);
      }
      
      if (response.success) {
        const successMsg = isEditMode 
          ? 'Assignment updated successfully!' 
          : 'Assignment created successfully!';
        
        setSuccessMessage(successMsg);
        
        // Clear form if not in edit mode
        if (!isEditMode) {
          setFormData({
            title: '',
            description: '',
            assignment_type: ASSIGNMENT_CONSTANTS.TYPES.HOMEWORK,
            difficulty_level: ASSIGNMENT_CONSTANTS.DIFFICULTY.MEDIUM,
            status: ASSIGNMENT_CONSTANTS.STATUS.DRAFT,
            subject_ids: [],
            class_ids: [],
            grade_level_ids: [],
            due_date: '',
            available_from: '',
            total_marks: '',
            passing_marks: '',
            grading_rubric: '',
            allow_late_submission: false,
            late_submission_penalty: '',
            late_submission_deadline: '',
            max_resubmissions: 0,
            allow_attachments: true,
            max_attachment_size: 10,
            allowed_file_types: ['.pdf', '.doc', '.docx', '.jpg', '.png'],
            is_group_assignment: false,
            max_group_size: 1,
            requires_presentation: false,
            estimated_completion_time: '',
            instructions: '',
            resources: [],
            additional_notes: '',
            tags: [],
            category_id: '',
            publish_immediately: false,
            notify_students: false
          });
          setAttachments([]);
        }
        
        // Redirect after delay
        setTimeout(() => {
          if (formData.publish_immediately) {
            navigate(`/teacher/assignments/${response.data.id}/preview`);
          } else {
            navigate('/teacher/assignments');
          }
        }, 2000);
      } else {
        setErrorMessage(response.error?.message || 'Failed to save assignment');
        
        // Handle validation errors
        if (response.error?.validationErrors) {
          setErrors(response.error.validationErrors);
        }
      }
    } catch (error) {
      console.error('Error saving assignment:', error);
      setErrorMessage('An unexpected error occurred. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleSaveDraft = async () => {
    // Save as draft
    const draftData = {
      ...formData,
      status: ASSIGNMENT_CONSTANTS.STATUS.DRAFT,
      publish_immediately: false
    };
    
    setFormData(draftData);
    
    // Trigger submit
    handleSubmit(new Event('submit'));
  };
  
  const handlePublish = async () => {
    // Validate first
    const validationErrors = validateAssignmentData(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    
    setFormData(prev => ({
      ...prev,
      publish_immediately: true,
      status: ASSIGNMENT_CONSTANTS.STATUS.PUBLISHED
    }));
    
    // Trigger submit after state update
    setTimeout(() => {
      handleSubmit(new Event('submit'));
    }, 100);
  };
  
  const duplicateAssignment = async () => {
    if (!assignment) return;
    
    try {
      setSubmitting(true);
      const response = await assignmentsAPI.duplicateAssignment(assignment.id, {
        include_attachments: true,
        include_resources: true
      });
      
      if (response.success) {
        setSuccessMessage('Assignment duplicated successfully!');
        // Redirect to edit the duplicated assignment
        setTimeout(() => {
          navigate(`/teacher/assignments/${response.data.id}/edit`);
        }, 1500);
      } else {
        setErrorMessage('Failed to duplicate assignment');
      }
    } catch (error) {
      console.error('Error duplicating assignment:', error);
      setErrorMessage('Failed to duplicate assignment');
    } finally {
      setSubmitting(false);
    }
  };
  
  // ==================== RENDER HELPERS ====================
  
  if (authLoading || loading) {
    return (
      <Container className="mt-5">
        <Row className="justify-content-center">
          <Col md={6} className="text-center">
            <Spinner animation="border" variant="primary" />
            <p className="mt-3">Loading assignment form...</p>
          </Col>
        </Row>
      </Container>
    );
  }
  
  if (!currentUser || (!currentUser.is_teacher && !currentUser.is_admin)) {
    return null; // Will redirect in useEffect
  }
  
  const assignmentTypes = Object.entries(ASSIGNMENT_CONSTANTS.TYPES).map(([key, value]) => ({
    label: key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '),
    value: value
  }));
  
  const difficultyLevels = Object.entries(ASSIGNMENT_CONSTANTS.DIFFICULTY).map(([key, value]) => ({
    label: key.charAt(0).toUpperCase() + key.slice(1),
    value: value
  }));
  
  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <Button 
                variant="outline-secondary" 
                className="mb-2"
                onClick={() => navigate('/teacher/assignments')}
              >
                <Icon name="arrowLeft" size={14} className="me-2" />
                Back to Assignments
              </Button>
              <h1 className="h3 mb-1 d-flex align-items-center">
                <Icon name="book" size={20} className="me-2" />
                {isEditMode ? 'Edit Assignment' : 'Create New Assignment'}
              </h1>
              <p className="text-muted mb-0">
                {isEditMode 
                  ? 'Update assignment details and settings' 
                  : 'Create a new assignment for your students'
                }
              </p>
            </div>
            
            {isEditMode && assignment && (
              <Button
                variant="outline-secondary"
                onClick={duplicateAssignment}
                disabled={submitting}
              >
                <Icon name="copy" size={14} className="me-2" />
                Duplicate
              </Button>
            )}
          </div>
        </Col>
      </Row>
      
      {/* Messages */}
      {errorMessage && (
        <Alert variant="danger" dismissible onClose={() => setErrorMessage('')}>
          <Icon name="alertCircle" className="me-2" />
          {errorMessage}
        </Alert>
      )}
      
      {successMessage && (
        <Alert variant="success" dismissible onClose={() => setSuccessMessage('')}>
          <Icon name="checkCircle" className="me-2" />
          {successMessage}
        </Alert>
      )}
      
      <Form onSubmit={handleSubmit}>
        <Row>
          {/* Left Column - Form Tabs */}
          <Col lg={9}>
            <Card className="shadow-sm mb-4">
              <Card.Header className="bg-white">
                <Tabs 
                  activeKey={activeTab} 
                  onSelect={(k) => setActiveTab(k)}
                  className="border-0"
                >
                  <Tab eventKey="basic" title="Basic Info" />
                  <Tab eventKey="academic" title="Academic Settings" />
                  <Tab eventKey="timeline" title="Timeline" />
                  <Tab eventKey="grading" title="Grading" />
                  <Tab eventKey="submission" title="Submission Settings" />
                  <Tab eventKey="advanced" title="Advanced" />
                </Tabs>
              </Card.Header>
              <Card.Body>
                {/* Basic Info Tab */}
                {activeTab === 'basic' && (
                  <div className="space-y-4">
                    <Form.Group>
                      <Form.Label>Assignment Title *</Form.Label>
                      <Form.Control
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        isInvalid={!!errors.title}
                        placeholder="Enter assignment title"
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.title}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Form.Group>
                      <Form.Label>Description *</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={4}
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        isInvalid={!!errors.description}
                        placeholder="Describe the assignment objectives, requirements, and expectations..."
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.description}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Row>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>Assignment Type *</Form.Label>
                          <Form.Select
                            name="assignment_type"
                            value={formData.assignment_type}
                            onChange={handleInputChange}
                            isInvalid={!!errors.assignment_type}
                          >
                            <option value="">Select type</option>
                            {assignmentTypes.map(type => (
                              <option key={type.value} value={type.value}>
                                {type.label}
                              </option>
                            ))}
                          </Form.Select>
                          <Form.Control.Feedback type="invalid">
                            {errors.assignment_type}
                          </Form.Control.Feedback>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>Difficulty Level</Form.Label>
                          <Form.Select
                            name="difficulty_level"
                            value={formData.difficulty_level}
                            onChange={handleInputChange}
                          >
                            {difficultyLevels.map(level => (
                              <option key={level.value} value={level.value}>
                                {level.label}
                              </option>
                            ))}
                          </Form.Select>
                        </Form.Group>
                      </Col>
                    </Row>
                    
                    <Form.Group>
                      <Form.Label>Category</Form.Label>
                      <Form.Select
                        name="category_id"
                        value={formData.category_id}
                        onChange={handleInputChange}
                      >
                        <option value="">Select category (optional)</option>
                        {categories.map(category => (
                          <option key={category.id} value={category.id}>
                            {category.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </div>
                )}
                
                {/* Academic Settings Tab */}
                {activeTab === 'academic' && (
                  <div className="space-y-4">
                    <Form.Group>
                      <Form.Label>Subjects *</Form.Label>
                      <div className="border rounded p-3 bg-light">
                        <Row>
                          {availableSubjects.map(subject => (
                            <Col md={4} key={subject.id} className="mb-2">
                              <Form.Check
                                type="checkbox"
                                id={`subject-${subject.id}`}
                                label={subject.name}
                                checked={formData.subject_ids.includes(subject.id)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setFormData(prev => ({
                                      ...prev,
                                      subject_ids: [...prev.subject_ids, subject.id]
                                    }));
                                  } else {
                                    setFormData(prev => ({
                                      ...prev,
                                      subject_ids: prev.subject_ids.filter(id => id !== subject.id)
                                    }));
                                  }
                                }}
                              />
                            </Col>
                          ))}
                        </Row>
                      </div>
                      {errors.subject_ids && (
                        <div className="text-danger small mt-1">{errors.subject_ids}</div>
                      )}
                    </Form.Group>
                    
                    <Form.Group>
                      <Form.Label>Classes *</Form.Label>
                      <div className="border rounded p-3 bg-light">
                        <Row>
                          {availableClasses.map(classroom => (
                            <Col md={4} key={classroom.id} className="mb-2">
                              <Form.Check
                                type="checkbox"
                                id={`class-${classroom.id}`}
                                label={classroom.name}
                                checked={formData.class_ids.includes(classroom.id)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setFormData(prev => ({
                                      ...prev,
                                      class_ids: [...prev.class_ids, classroom.id]
                                    }));
                                  } else {
                                    setFormData(prev => ({
                                      ...prev,
                                      class_ids: prev.class_ids.filter(id => id !== classroom.id)
                                    }));
                                  }
                                }}
                              />
                            </Col>
                          ))}
                        </Row>
                      </div>
                      {errors.class_ids && (
                        <div className="text-danger small mt-1">{errors.class_ids}</div>
                      )}
                    </Form.Group>
                  </div>
                )}
                
                {/* Timeline Tab */}
                {activeTab === 'timeline' && (
                  <div className="space-y-4">
                    <Row>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>Available From</Form.Label>
                          <Form.Control
                            type="date"
                            name="available_from"
                            value={formData.available_from}
                            onChange={handleInputChange}
                            isInvalid={!!errors.available_from}
                          />
                          <Form.Control.Feedback type="invalid">
                            {errors.available_from}
                          </Form.Control.Feedback>
                          <Form.Text className="text-muted">
                            When students can start working on the assignment
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>Due Date *</Form.Label>
                          <Form.Control
                            type="date"
                            name="due_date"
                            value={formData.due_date}
                            onChange={handleInputChange}
                            isInvalid={!!errors.due_date}
                          />
                          <Form.Control.Feedback type="invalid">
                            {errors.due_date}
                          </Form.Control.Feedback>
                          <Form.Text className="text-muted">
                            When students must submit the assignment
                          </Form.Text>
                        </Form.Group>
                      </Col>
                    </Row>
                    
                    <Form.Group>
                      <Form.Label>Estimated Completion Time (hours)</Form.Label>
                      <InputGroup>
                        <Form.Control
                          type="number"
                          name="estimated_completion_time"
                          value={formData.estimated_completion_time}
                          onChange={handleInputChange}
                          min="0"
                          placeholder="e.g., 2"
                        />
                        <InputGroup.Text>hours</InputGroup.Text>
                      </InputGroup>
                      <Form.Text className="text-muted">
                        Estimated time students will need to complete this assignment
                      </Form.Text>
                    </Form.Group>
                  </div>
                )}
                
                {/* Grading Tab */}
                {activeTab === 'grading' && (
                  <div className="space-y-4">
                    <Row>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>Total Marks</Form.Label>
                          <Form.Control
                            type="number"
                            name="total_marks"
                            value={formData.total_marks}
                            onChange={handleInputChange}
                            isInvalid={!!errors.total_marks}
                            placeholder="e.g., 100"
                            min="0"
                            step="0.5"
                          />
                          <Form.Control.Feedback type="invalid">
                            {errors.total_marks}
                          </Form.Control.Feedback>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>Passing Marks</Form.Label>
                          <Form.Control
                            type="number"
                            name="passing_marks"
                            value={formData.passing_marks}
                            onChange={handleInputChange}
                            isInvalid={!!errors.passing_marks}
                            placeholder="e.g., 40"
                            min="0"
                            step="0.5"
                          />
                          <Form.Control.Feedback type="invalid">
                            {errors.passing_marks}
                          </Form.Control.Feedback>
                        </Form.Group>
                      </Col>
                    </Row>
                    
                    <Form.Group>
                      <Form.Label>Grading Rubric</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={4}
                        name="grading_rubric"
                        value={formData.grading_rubric}
                        onChange={handleInputChange}
                        placeholder="Describe how the assignment will be graded..."
                      />
                      <Form.Text className="text-muted">
                        Provide clear criteria for how students will be assessed
                      </Form.Text>
                    </Form.Group>
                  </div>
                )}
                
                {/* Submission Settings Tab */}
                {activeTab === 'submission' && (
                  <div className="space-y-4">
                    <Form.Check
                      type="switch"
                      id="allow_late_submission"
                      label="Allow late submissions"
                      checked={formData.allow_late_submission}
                      onChange={handleInputChange}
                      name="allow_late_submission"
                    />
                    
                    {formData.allow_late_submission && (
                      <Row>
                        <Col md={6}>
                          <Form.Group>
                            <Form.Label>Late Submission Penalty (% per day)</Form.Label>
                            <Form.Control
                              type="number"
                              name="late_submission_penalty"
                              value={formData.late_submission_penalty}
                              onChange={handleInputChange}
                              isInvalid={!!errors.late_submission_penalty}
                              placeholder="e.g., 10"
                              min="0"
                              max="100"
                              step="0.5"
                            />
                            <Form.Control.Feedback type="invalid">
                              {errors.late_submission_penalty}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group>
                            <Form.Label>Final Deadline for Late Submissions</Form.Label>
                            <Form.Control
                              type="date"
                              name="late_submission_deadline"
                              value={formData.late_submission_deadline}
                              onChange={handleInputChange}
                            />
                          </Form.Group>
                        </Col>
                      </Row>
                    )}
                    
                    <Form.Group>
                      <Form.Label>Maximum Resubmissions Allowed</Form.Label>
                      <Form.Control
                        type="number"
                        name="max_resubmissions"
                        value={formData.max_resubmissions}
                        onChange={handleInputChange}
                        placeholder="e.g., 2"
                        min="0"
                      />
                      <Form.Text className="text-muted">
                        Number of times students can resubmit (0 = no resubmissions)
                      </Form.Text>
                    </Form.Group>
                    
                    <Form.Check
                      type="switch"
                      id="allow_attachments"
                      label="Allow file attachments"
                      checked={formData.allow_attachments}
                      onChange={handleInputChange}
                      name="allow_attachments"
                    />
                    
                    {formData.allow_attachments && (
                      <>
                        <Row>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>Maximum File Size (MB)</Form.Label>
                              <Form.Control
                                type="number"
                                name="max_attachment_size"
                                value={formData.max_attachment_size}
                                onChange={handleInputChange}
                                min="1"
                                max="100"
                              />
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>Allowed File Types</Form.Label>
                              <div className="d-flex flex-wrap gap-1">
                                {formData.allowed_file_types.map((type, index) => (
                                  <Badge key={index} bg="primary" className="me-1">
                                    {type}
                                  </Badge>
                                ))}
                              </div>
                            </Form.Group>
                          </Col>
                        </Row>
                        
                        <Form.Group>
                          <Form.Label>Upload Assignment Files</Form.Label>
                          <Form.Control
                            type="file"
                            multiple
                            onChange={handleFileUpload}
                            ref={fileInputRef}
                          />
                          <Form.Text className="text-muted">
                            Upload any files or resources for this assignment
                          </Form.Text>
                          
                          {attachments.length > 0 && (
                            <div className="mt-3">
                              <h6>Uploaded Files:</h6>
                              <ul className="list-group">
                                {attachments.map((file, index) => (
                                  <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                                    <span>{file.name}</span>
                                    <Button
                                      variant="outline-danger"
                                      size="sm"
                                      onClick={() => removeAttachment(index)}
                                    >
                                      <Icon name="x" />
                                    </Button>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </Form.Group>
                      </>
                    )}
                  </div>
                )}
                
                {/* Advanced Tab */}
                {activeTab === 'advanced' && (
                  <div className="space-y-4">
                    <Form.Group>
                      <Form.Label>Detailed Instructions</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={4}
                        name="instructions"
                        value={formData.instructions}
                        onChange={handleInputChange}
                        placeholder="Provide step-by-step instructions for students..."
                      />
                    </Form.Group>
                    
                    <Form.Group>
                      <Form.Label>Learning Resources</Form.Label>
                      <div className="mb-2">
                        {formData.resources.map((resource, index) => (
                          <div key={index} className="d-flex justify-content-between align-items-center bg-light p-2 mb-1 rounded">
                            <span>{resource}</span>
                            <Button
                              variant="link"
                              size="sm"
                              onClick={() => removeResource(index)}
                              className="text-danger"
                            >
                              <Icon name="x" />
                            </Button>
                          </div>
                        ))}
                      </div>
                      <InputGroup>
                        <Form.Control
                          type="text"
                          value={newResource}
                          onChange={(e) => setNewResource(e.target.value)}
                          placeholder="Add a resource URL or description"
                          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addResource())}
                        />
                        <Button onClick={addResource}>
                          <Icon name="plus" />
                        </Button>
                      </InputGroup>
                    </Form.Group>
                    
                    <Form.Group>
                      <Form.Label>Tags</Form.Label>
                      <div className="mb-2">
                        {formData.tags.map((tag, index) => (
                          <Badge key={index} bg="success" className="me-1 mb-1">
                            {tag}
                            <Button
                              variant="link"
                              size="sm"
                              onClick={() => removeTag(index)}
                              className="text-white p-0 ms-1"
                            >
                              <Icon name="x" size={12} />
                            </Button>
                          </Badge>
                        ))}
                      </div>
                      <InputGroup>
                        <Form.Control
                          type="text"
                          value={newTag}
                          onChange={(e) => setNewTag(e.target.value)}
                          placeholder="Add a tag"
                          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                        />
                        <Button onClick={addTag} variant="success">
                          <Icon name="plus" />
                        </Button>
                      </InputGroup>
                    </Form.Group>
                    
                    <Form.Group>
                      <Form.Label>Additional Notes (Internal)</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="additional_notes"
                        value={formData.additional_notes}
                        onChange={handleInputChange}
                        placeholder="Any additional notes for teachers..."
                      />
                    </Form.Group>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
          
          {/* Right Column - Action Buttons & Summary */}
          <Col lg={3}>
            <Card className="shadow-sm mb-4">
              <Card.Header className="bg-white">
                <h6 className="mb-0">Actions</h6>
              </Card.Header>
              <Card.Body>
                <div className="d-grid gap-2">
                  <Button
                    variant="outline-secondary"
                    onClick={handleSaveDraft}
                    disabled={submitting}
                  >
                    <Icon name="save" className="me-2" />
                    Save as Draft
                  </Button>
                  
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Icon name="save" className="me-2" />
                        {isEditMode ? 'Update Assignment' : 'Create Assignment'}
                      </>
                    )}
                  </Button>
                  
                  <Button
                    variant="success"
                    onClick={handlePublish}
                    disabled={submitting}
                  >
                    <Icon name="upload" className="me-2" />
                    Publish Assignment
                  </Button>
                </div>
              </Card.Body>
            </Card>
            
            <Card className="shadow-sm">
              <Card.Header className="bg-white">
                <h6 className="mb-0">Summary</h6>
              </Card.Header>
              <Card.Body>
                <div className="small">
                  <p><strong>Title:</strong> {formData.title || 'Not set'}</p>
                  <p><strong>Type:</strong> {formData.assignment_type || 'Not set'}</p>
                  <p><strong>Subjects:</strong> {formData.subject_ids.length}</p>
                  <p><strong>Classes:</strong> {formData.class_ids.length}</p>
                  <p><strong>Due Date:</strong> {formData.due_date || 'Not set'}</p>
                  <p><strong>Total Marks:</strong> {formData.total_marks || 'Not set'}</p>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Form>
    </Container>
  );
};

export default CreateAssignment;