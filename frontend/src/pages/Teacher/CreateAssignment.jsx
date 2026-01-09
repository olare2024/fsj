import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'react-toastify';

// Bootstrap Components
import { 
  Container, Row, Col, Card, Form, Button, Alert, 
  Spinner, Tabs, Tab, Badge, InputGroup, Modal,
  ProgressBar, ListGroup, Table, OverlayTrigger, Tooltip
} from 'react-bootstrap';

// Icons
import { 
  ArrowLeft, Save, Eye, Calendar, Clock, Book, 
  People, FileText, Plus, Trash, Upload,
  Journal, JournalCheck, Award, CheckCircle,
  FileEarmark, Paperclip,
  ClockHistory, ExclamationTriangle, Stopwatch, Percent,
  JournalText, CardText, BookmarkCheck, Folder,
  Person, ArrowLeftRight, FileEarmarkCheck, FileEarmarkPlus,
  CardChecklist, ListCheck, Lightbulb, Bullseye, CheckSquare, ListTask,
  CalendarCheck, CalendarX, Star, InfoCircle,
  ArrowCounterclockwise, ClipboardCheck, FileEarmarkText,
  Gear, ShieldCheck, Award as AwardIcon
} from 'react-bootstrap-icons';

// APIs
import assignmentsAPI from '../../services/assignmentsAPI-old';
import { academicAPI } from '../../services/academicAPI';
import authAPI from '../../services/authAPI';

// ==================== CONSTANTS ====================
const DRAFT_STORAGE_KEY = 'assignment_draft_v3';
const TEMPLATE_STORAGE_KEY = 'assignment_templates';

// File size formatter
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// UUID validation
const isValidUUID = (uuid) => {
  if (!uuid || typeof uuid !== 'string') return false;
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

// Format backend errors
const formatBackendErrors = (errorData) => {
  if (typeof errorData === 'object' && errorData !== null) {
    return Object.entries(errorData)
      .map(([field, errors]) => {
        if (Array.isArray(errors)) {
          return `${field.replace('_', ' ')}: ${errors.join(', ')}`;
        } else if (typeof errors === 'string') {
          return `${field.replace('_', ' ')}: ${errors}`;
        }
        return `${field.replace('_', ' ')}: Invalid value`;
      })
      .join('; ');
  } else if (typeof errorData === 'string') {
    return errorData;
  } else if (errorData?.detail) {
    return errorData.detail;
  }
  return 'Unknown error occurred. Please try again.';
};

// ==================== HELPER COMPONENTS ====================
const RequiredFieldIndicator = () => (
  <span className="text-danger fw-bold" title="Required field"> *</span>
);

const FormFieldTooltip = ({ text }) => (
  <OverlayTrigger
    placement="top"
    overlay={<Tooltip id="tooltip-top">{text}</Tooltip>}
  >
    <InfoCircle size={14} className="ms-1 text-info" />
  </OverlayTrigger>
);

const FormValidationError = ({ message }) => (
  <Alert variant="danger" className="py-2 px-3 mt-1 mb-2">
    <ExclamationTriangle size={14} className="me-2" />
    <small>{message}</small>
  </Alert>
);

// ==================== UTILITY FUNCTIONS ====================
const getInitialFormData = () => {
  const defaultData = {
    title: '',
    description: '',
    assignment_type: 'homework',
    subject: '',
    classroom: '',
    academic_year: '',
    term: '',
    due_date: '',
    due_time: '23:59',
    total_marks: 100,
    passing_marks: 40,
    stream: '',
    category: '',
    difficulty_level: 'medium',
    estimated_completion_time: 60,
    instructions: '',
    learning_objectives: '',
    resources: '',
    curriculum: 'cbc',
    core_competencies: '',
    allow_late_submission: false,
    late_submission_penalty: 0,
    allow_resubmission: false,
    max_resubmissions: 1,
    require_approval: false,
    is_group_assignment: false,
    max_group_size: 1,
    status: 'draft',
    teacher_notes: '',
    visibility: 'all_students',
    publish_date: '',
  };

  try {
    const savedDraft = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (savedDraft) {
      const draftData = JSON.parse(savedDraft);
      const validatedDraft = Object.keys(defaultData).reduce((acc, key) => {
        if (draftData[key] !== undefined && draftData[key] !== null) {
          acc[key] = draftData[key];
        }
        return acc;
      }, {});
      return { ...defaultData, ...validatedDraft };
    }
  } catch (err) {
    console.warn('Failed to load draft:', err);
    localStorage.removeItem(DRAFT_STORAGE_KEY);
  }
  
  return defaultData;
};

const processAPIResponse = (response) => {
  if (response.status === 'fulfilled' && response.value?.success) {
    const data = response.value.data;
    if (Array.isArray(data)) return data;
    if (data?.results) return data.results;
    if (data?.data) return data.data;
  }
  return [];
};

const validateAndFilterFiles = (files) => {
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png',
    'image/gif',
    'text/plain',
    'video/mp4',
    'audio/mpeg',
    'application/zip'
  ];
  
  return files.filter(file => {
    if (file.size > 10 * 1024 * 1024) {
      toast.warning(`File "${file.name}" exceeds 10MB limit`);
      return false;
    }
    
    const isAllowed = allowedTypes.some(type => file.type.includes(type.replace('*', '')));
    if (!isAllowed) {
      toast.warning(`File "${file.name}" has unsupported type: ${file.type}`);
      return false;
    }
    
    return true;
  });
};

const prepareSubmissionData = (formData, userId) => {
  return {
    title: formData.title,
    description: formData.description || 'No description provided',
    assignment_type: formData.assignment_type,
    subject: formData.subject,
    classroom: formData.classroom,
    academic_year: formData.academic_year,
    term: formData.term,
    teacher: userId,
    due_date: formData.due_date ? `${formData.due_date}T${formData.due_time}:00` : 
              new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    total_marks: formData.total_marks,
    passing_marks: formData.passing_marks,
    status: 'draft',
    created_by: userId,
    ...(formData.instructions && { instructions: formData.instructions }),
    ...(formData.learning_objectives && { learning_objectives: formData.learning_objectives }),
    ...(formData.teacher_notes && { teacher_notes: formData.teacher_notes }),
    ...(formData.stream && { stream: formData.stream }),
    ...(formData.difficulty_level && { difficulty_level: formData.difficulty_level }),
    ...(formData.estimated_completion_time && { estimated_completion_time: formData.estimated_completion_time }),
    ...(formData.allow_late_submission !== undefined && { allow_late_submission: formData.allow_late_submission }),
    ...(formData.late_submission_penalty && { late_submission_penalty: formData.late_submission_penalty }),
    ...(formData.allow_resubmission !== undefined && { allow_resubmission: formData.allow_resubmission }),
    ...(formData.max_resubmissions && { max_resubmissions: formData.max_resubmissions }),
    ...(formData.is_group_assignment !== undefined && { is_group_assignment: formData.is_group_assignment }),
    ...(formData.max_group_size && { max_group_size: formData.max_group_size }),
    ...(formData.require_approval !== undefined && { require_approval: formData.require_approval }),
  };
};

const formatSubmissionError = (err) => {
  if (err.response?.data) {
    const errorData = err.response.data;
    if (typeof errorData === 'object' && errorData !== null) {
      if (errorData.academic_year) {
        return `Academic Year Error: ${Array.isArray(errorData.academic_year) ? errorData.academic_year[0] : errorData.academic_year}`;
      }
      return formatBackendErrors(errorData);
    }
  }
  return 'An unexpected error occurred. Please try again.';
};

const getItemName = (items, id) => {
  const item = items.find(item => item.id === id);
  return item?.name || 'Not set';
};

const formatDueDate = (formData) => {
  return formData.due_date ? `${formData.due_date} at ${formData.due_time}` : 'Not set';
};

const getBadgeProps = (value) => {
  const props = { pill: true };
  
  switch (value) {
    case 'draft':
      props.bg = 'secondary';
      break;
    case 'published':
      props.bg = 'success';
      break;
    case 'easy':
      props.bg = 'success';
      break;
    case 'medium':
      props.bg = 'warning';
      break;
    case 'hard':
      props.bg = 'danger';
      break;
    case 'challenging':
      props.bg = 'dark';
      break;
    default:
      props.bg = 'info';
  }
  
  return props;
};

// ==================== STATE COMPONENTS ====================
const LoadingState = () => (
  <Container className="d-flex justify-content-center align-items-center min-vh-100">
    <div className="text-center">
      <Spinner animation="border" variant="primary" size="lg" />
      <p className="mt-3">Loading assignment creator...</p>
      <small className="text-muted">Fetching required academic data</small>
    </div>
  </Container>
);

const SetupRequiredState = ({ missingItems, navigate, academicYears = [], subjects = [], classes = [], terms = [] }) => (
  <Container className="mt-5">
    <Alert variant="warning">
      <div className="d-flex align-items-start">
        <ExclamationTriangle className="me-3 mt-1" size={24} />
        <div>
          <h5>Academic Setup Required</h5>
          <p className="mb-2">Before creating assignments, you need to set up the following academic data:</p>
          
          <ListGroup variant="flush" className="mb-3">
            {missingItems.includes('Academic Years') && (
              <ListGroup.Item className="d-flex align-items-center">
                <Badge bg="danger" className="me-2">!</Badge>
                <div>
                  <strong>Academic Years</strong> - Define academic periods for organizing assignments by year
                </div>
              </ListGroup.Item>
            )}
            
            {missingItems.includes('Subjects/Courses') && (
              <ListGroup.Item className="d-flex align-items-center">
                <Badge bg="danger" className="me-2">!</Badge>
                <div>
                  <strong>Subjects/Courses</strong> - Create subjects or courses to assign to students
                </div>
              </ListGroup.Item>
            )}
            
            {missingItems.includes('Classes/Groups') && (
              <ListGroup.Item className="d-flex align-items-center">
                <Badge bg="danger" className="me-2">!</Badge>
                <div>
                  <strong>Classes/Groups</strong> - Create class groups for student organization
                </div>
              </ListGroup.Item>
            )}
            
            {missingItems.includes('Academic Terms') && (
              <ListGroup.Item className="d-flex align-items-center">
                <Badge bg="danger" className="me-2">!</Badge>
                <div>
                  <strong>Academic Terms</strong> - Create terms (e.g., Term 1, Term 2, Term 3)
                </div>
              </ListGroup.Item>
            )}
          </ListGroup>
          
          <div className="d-flex gap-2 flex-wrap">
            <Button 
              variant="outline-primary" 
              onClick={() => window.location.reload()}
              className="mb-2"
            >
              <ArrowCounterclockwise className="me-2" />
              Refresh Data
            </Button>
            <Button 
              variant="outline-secondary"
              onClick={() => navigate('/teacher/assignments')}
              className="mb-2"
            >
              <ArrowLeft className="me-2" />
              Back to Assignments
            </Button>
          </div>
        </div>
      </div>
    </Alert>
  </Container>
);

// ==================== FORM SECTION COMPONENTS ====================
const renderBasicInfo = (props) => {
  const { formData, validationErrors, subjects, classes, streams, academicYears, terms, handleChange } = props;
  
  return (
    <div className="basic-info-section">
      <h5 className="border-bottom pb-2 mb-4">
        <FileText className="me-2" />
        Basic Information
      </h5>
      
      <Row>
        <Col md={8}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <BookmarkCheck className="me-2" size={14} />
              Assignment Title
              <RequiredFieldIndicator />
              <FormFieldTooltip text="A clear and descriptive title for the assignment" />
            </Form.Label>
            <Form.Control
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="e.g., Algebra II: Quadratic Equations Worksheet"
              isInvalid={!!validationErrors.title}
            />
            <Form.Control.Feedback type="invalid">
              {validationErrors.title}
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Be specific so students know what to expect
            </Form.Text>
          </Form.Group>
        </Col>
        <Col md={4}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <Journal className="me-2" size={14} />
              Type
              <RequiredFieldIndicator />
            </Form.Label>
            <Form.Select
              name="assignment_type"
              value={formData.assignment_type}
              onChange={handleChange}
              required
            >
              <option value="homework">Homework</option>
              <option value="classwork">Classwork</option>
              <option value="project">Project</option>
              <option value="quiz">Quiz</option>
              <option value="test">Test</option>
              <option value="exam">Exam</option>
              <option value="practical">Practical</option>
              <option value="presentation">Presentation</option>
              <option value="research">Research</option>
            </Form.Select>
          </Form.Group>
        </Col>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <CardText className="me-2" size={14} />
          Description
        </Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Provide a brief overview of the assignment..."
        />
      </Form.Group>

      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <Book className="me-2" size={14} />
              Subject
              <RequiredFieldIndicator />
            </Form.Label>
            <Form.Select
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
              isInvalid={!!validationErrors.subject}
            >
              <option value="">Select Subject</option>
              {subjects.map(subject => (
                <option key={subject.id} value={subject.id}>
                  {subject.name} {subject.code ? `(${subject.code})` : ''}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              {validationErrors.subject}
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <People className="me-2" size={14} />
              Class
              <RequiredFieldIndicator />
            </Form.Label>
            <Form.Select
              name="classroom"
              value={formData.classroom}
              onChange={handleChange}
              required
              isInvalid={!!validationErrors.classroom}
            >
              <option value="">Select Class</option>
              {classes.map(cls => (
                <option key={cls.id} value={cls.id}>
                  {cls.name} {cls.display_name ? `(${cls.display_name})` : ''}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              {validationErrors.classroom}
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
      </Row>

      {streams.length > 0 && (
        <Row>
          <Col md={6}>
            <Form.Group className="mb-3">
              <Form.Label className="fw-semibold">
                <ArrowLeftRight className="me-2" size={14} />
                Stream (Optional)
              </Form.Label>
              <Form.Select
                name="stream"
                value={formData.stream}
                onChange={handleChange}
              >
                <option value="">Select Stream (Optional)</option>
                {streams.map(stream => (
                  <option key={stream.id} value={stream.id}>
                    {stream.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>
      )}

      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <CalendarCheck className="me-2" size={14} />
              Academic Year
              <RequiredFieldIndicator />
            </Form.Label>
            <Form.Select
              name="academic_year"
              value={formData.academic_year}
              onChange={handleChange}
              required
              isInvalid={!!validationErrors.academic_year}
            >
              <option value="">Select Academic Year</option>
              {academicYears.map(year => (
                <option key={year.id} value={year.id}>
                  {year.name} {year.is_current ? '(Current)' : ''}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              {validationErrors.academic_year}
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <Calendar className="me-2" size={14} />
              Term
              <RequiredFieldIndicator />
            </Form.Label>
            <Form.Select
              name="term"
              value={formData.term}
              onChange={handleChange}
              required
              isInvalid={!!validationErrors.term}
            >
              <option value="">Select Term</option>
              {terms.map(term => (
                <option key={term.id} value={term.id}>
                  {term.name} {term.is_current ? '(Current)' : ''}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              {validationErrors.term}
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
      </Row>

      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <CalendarX className="me-2" size={14} />
              Due Date
              <RequiredFieldIndicator />
            </Form.Label>
            <Form.Control
              type="date"
              name="due_date"
              value={formData.due_date}
              onChange={handleChange}
              required
              min={new Date().toISOString().split('T')[0]}
              isInvalid={!!validationErrors.due_date}
            />
            <Form.Control.Feedback type="invalid">
              {validationErrors.due_date}
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <Clock className="me-2" size={14} />
              Due Time
              <RequiredFieldIndicator />
            </Form.Label>
            <Form.Control
              type="time"
              name="due_time"
              value={formData.due_time}
              onChange={handleChange}
              required
              isInvalid={!!validationErrors.due_time}
            />
            <Form.Control.Feedback type="invalid">
              {validationErrors.due_time}
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
      </Row>
    </div>
  );
};

const renderGradingSection = (props) => {
  const { formData, validationErrors, handleChange } = props;
  
  return (
    <div className="grading-section">
      <h5 className="border-bottom pb-2 mb-4">
        <Percent className="me-2" />
        Grading & Marks
      </h5>
      
      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <AwardIcon className="me-2" size={14} />
              Total Marks
              <RequiredFieldIndicator />
            </Form.Label>
            <InputGroup>
              <Form.Control
                type="number"
                name="total_marks"
                value={formData.total_marks}
                onChange={handleChange}
                required
                min="1"
                max="1000"
                step="0.5"
                isInvalid={!!validationErrors.total_marks}
              />
              <InputGroup.Text>marks</InputGroup.Text>
            </InputGroup>
            <Form.Control.Feedback type="invalid">
              {validationErrors.total_marks}
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Maximum marks for this assignment (1-1000)
            </Form.Text>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <CheckSquare className="me-2" size={14} />
              Passing Marks
            </Form.Label>
            <InputGroup>
              <Form.Control
                type="number"
                name="passing_marks"
                value={formData.passing_marks}
                onChange={handleChange}
                min="0"
                max={formData.total_marks}
                step="0.5"
                isInvalid={!!validationErrors.passing_marks}
              />
              <InputGroup.Text>marks</InputGroup.Text>
            </InputGroup>
            <Form.Control.Feedback type="invalid">
              {validationErrors.passing_marks}
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Minimum marks required to pass
            </Form.Text>
          </Form.Group>
        </Col>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <Stopwatch className="me-2" size={14} />
          Estimated Completion Time
        </Form.Label>
        <InputGroup>
          <Form.Control
            type="number"
            name="estimated_completion_time"
            value={formData.estimated_completion_time}
            onChange={handleChange}
            min="5"
            step="5"
          />
          <InputGroup.Text>minutes</InputGroup.Text>
        </InputGroup>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <Bullseye className="me-2" size={14} />
          Difficulty Level
        </Form.Label>
        <Form.Select
          name="difficulty_level"
          value={formData.difficulty_level}
          onChange={handleChange}
        >
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
          <option value="challenging">Challenging</option>
        </Form.Select>
      </Form.Group>
    </div>
  );
};

const renderCurriculumSection = (props) => {
  const { formData, handleChange } = props;
  
  return (
    <div className="curriculum-section">
      <h5 className="border-bottom pb-2 mb-4">
        <Bullseye className="me-2" />
        Curriculum & Competencies
      </h5>
      
      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <Book className="me-2" size={14} />
              Curriculum
            </Form.Label>
            <Form.Select
              name="curriculum"
              value={formData.curriculum}
              onChange={handleChange}
            >
              <option value="cbc">CBC (Competency Based Curriculum)</option>
              <option value="8-4-4">8-4-4 System</option>
              <option value="igcse">IGCSE</option>
              <option value="ib">International Baccalaureate</option>
              <option value="american">American Curriculum</option>
              <option value="british">British Curriculum</option>
            </Form.Select>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <Award className="me-2" size={14} />
              Core Competency
            </Form.Label>
            <Form.Select
              name="core_competencies"
              value={formData.core_competencies}
              onChange={handleChange}
            >
              <option value="">Select Competency</option>
              <option value="communication_collaboration">Communication & Collaboration</option>
              <option value="critical_thinking">Critical Thinking & Problem Solving</option>
              <option value="creativity_innovation">Creativity & Innovation</option>
              <option value="digital_literacy">Digital Literacy</option>
              <option value="learning_to_learn">Learning to Learn</option>
              <option value="self_efficacy">Self-efficacy</option>
            </Form.Select>
          </Form.Group>
        </Col>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <Lightbulb className="me-2" size={14} />
          Learning Objectives
        </Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          name="learning_objectives"
          value={formData.learning_objectives}
          onChange={handleChange}
          placeholder="Enter specific learning objectives (one per line)..."
        />
        <Form.Text className="text-muted">
          What students should be able to do after completing this assignment
        </Form.Text>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <ListCheck className="me-2" size={14} />
          Instructions
        </Form.Label>
        <Form.Control
          as="textarea"
          rows={4}
          name="instructions"
          value={formData.instructions}
          onChange={handleChange}
          placeholder="Provide clear instructions for students..."
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <Folder className="me-2" size={14} />
          Resources & Reading Materials
        </Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          name="resources"
          value={formData.resources}
          onChange={handleChange}
          placeholder="List recommended resources, textbooks, or websites..."
        />
      </Form.Group>
    </div>
  );
};

const renderRubricSection = (props) => {
  const { validationErrors, rubricItems, setRubricItems, calculateRubricTotal, formData } = props;
  
  const addRubricItem = () => {
    const newItem = {
      id: Date.now() + Math.random(),
      criteria: '',
      marks: 0,
      weight: 1,
      description: ''
    };
    setRubricItems([...rubricItems, newItem]);
  };

  const updateRubricItem = (id, field, value) => {
    setRubricItems(prev => 
      prev.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const removeRubricItem = (id) => {
    setRubricItems(prev => prev.filter(item => item.id !== id));
  };
  
  return (
    <div className="rubric-section">
      <h5 className="border-bottom pb-2 mb-4">
        <CardChecklist className="me-2" />
        Grading Rubric (Optional)
      </h5>
      
      {validationErrors.rubric && (
        <FormValidationError message={validationErrors.rubric} />
      )}
      
      <div className="mb-3">
        <Button 
          variant="outline-primary" 
          size="sm" 
          onClick={addRubricItem}
          className="mb-3"
        >
          <Plus className="me-1" />
          Add Rubric Item
        </Button>
        
        {rubricItems.length > 0 && (
          <div className="mb-3">
            <Table responsive bordered size="sm">
              <thead className="table-light">
                <tr>
                  <th width="30%">Criteria</th>
                  <th width="15%">Marks</th>
                  <th width="15%">Weight</th>
                  <th width="35%">Description</th>
                  <th width="5%"></th>
                </tr>
              </thead>
              <tbody>
                {rubricItems.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <Form.Control
                        type="text"
                        value={item.criteria}
                        onChange={(e) => updateRubricItem(item.id, 'criteria', e.target.value)}
                        placeholder="e.g., Content Quality"
                      />
                    </td>
                    <td>
                      <Form.Control
                        type="number"
                        value={item.marks}
                        onChange={(e) => updateRubricItem(item.id, 'marks', e.target.value)}
                        min="0"
                        step="0.5"
                      />
                    </td>
                    <td>
                      <Form.Control
                        type="number"
                        value={item.weight}
                        onChange={(e) => updateRubricItem(item.id, 'weight', e.target.value)}
                        min="0.1"
                        step="0.1"
                      />
                    </td>
                    <td>
                      <Form.Control
                        type="text"
                        value={item.description}
                        onChange={(e) => updateRubricItem(item.id, 'description', e.target.value)}
                        placeholder="Description of criteria"
                      />
                    </td>
                    <td className="text-center">
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => removeRubricItem(item.id)}
                      >
                        <Trash size={12} />
                      </Button>
                    </td>
                  </tr>
                ))}
                <tr className="table-primary">
                  <td className="fw-bold">Total</td>
                  <td className="fw-bold">{calculateRubricTotal()}</td>
                  <td className="fw-bold">{rubricItems.reduce((sum, item) => sum + (parseFloat(item.weight) || 0), 0).toFixed(1)}</td>
                  <td colSpan="2">
                    <small className={calculateRubricTotal() !== formData.total_marks ? 'text-danger' : 'text-success'}>
                      {calculateRubricTotal() === formData.total_marks 
                        ? '✓ Rubric matches total marks' 
                        : `✗ Rubric total (${calculateRubricTotal()}) doesn't match assignment total (${formData.total_marks})`}
                    </small>
                  </td>
                </tr>
              </tbody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
};

const renderAttachmentsSection = (props) => {
  const { attachments, handleAttachmentUpload, removeAttachment, formatFileSize } = props;
  
  return (
    <div className="attachments-section">
      <h5 className="border-bottom pb-2 mb-4">
        <Paperclip className="me-2" />
        Attachments
      </h5>
      
      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <Upload className="me-2" size={14} />
          Upload Files
        </Form.Label>
        <div className="border rounded p-3 text-center">
          <input
            type="file"
            id="attachment-upload"
            className="d-none"
            onChange={handleAttachmentUpload}
            multiple
            accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.txt,.mp4,.mp3,.zip"
          />
          <label htmlFor="attachment-upload" className="cursor-pointer">
            <div className="py-4">
              <FileEarmarkPlus size={48} className="text-muted mb-2" />
              <p className="mb-1">Click to browse or drag and drop files here</p>
              <p className="text-muted small mb-0">
                Max file size: 10MB. Supported: PDF, DOC, PPT, XLS, Images, Videos
              </p>
            </div>
          </label>
        </div>
      </Form.Group>

      {attachments.length > 0 && (
        <div className="mb-3">
          <h6 className="mb-3">Uploaded Files ({attachments.length})</h6>
          <ListGroup>
            {attachments.map((file, index) => (
              <ListGroup.Item key={index} className="d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center">
                  <FileEarmark className="me-3 text-primary" size={20} />
                  <div>
                    <div className="fw-medium">{file.name}</div>
                    <small className="text-muted">
                      {file.type.split('/')[1]?.toUpperCase() || 'FILE'} • {formatFileSize(file.size)}
                    </small>
                  </div>
                </div>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => removeAttachment(index)}
                >
                  <Trash size={12} />
                </Button>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </div>
      )}
    </div>
  );
};

const renderSettingsSection = (props) => {
  const { formData, validationErrors, handleChange } = props;
  
  return (
    <div className="settings-section">
      <h5 className="border-bottom pb-2 mb-4">
        <Gear className="me-2" />
        Settings & Advanced Options
      </h5>
      
      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <ClockHistory className="me-2" size={14} />
              Late Submission
            </Form.Label>
            <div className="d-flex align-items-center mb-2">
              <Form.Check
                type="switch"
                id="allow-late-submission"
                name="allow_late_submission"
                checked={formData.allow_late_submission}
                onChange={handleChange}
                label="Allow late submissions"
              />
            </div>
            {formData.allow_late_submission && (
              <InputGroup>
                <Form.Control
                  type="number"
                  name="late_submission_penalty"
                  value={formData.late_submission_penalty}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  step="0.5"
                  placeholder="Penalty percentage"
                  isInvalid={!!validationErrors.late_submission_penalty}
                />
                <InputGroup.Text>% penalty</InputGroup.Text>
                <Form.Control.Feedback type="invalid">
                  {validationErrors.late_submission_penalty}
                </Form.Control.Feedback>
              </InputGroup>
            )}
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <ArrowLeftRight className="me-2" size={14} />
              Resubmission
            </Form.Label>
            <div className="d-flex align-items-center mb-2">
              <Form.Check
                type="switch"
                id="allow-resubmission"
                name="allow_resubmission"
                checked={formData.allow_resubmission}
                onChange={handleChange}
                label="Allow students to resubmit"
              />
            </div>
            {formData.allow_resubmission && (
              <InputGroup>
                <Form.Control
                  type="number"
                  name="max_resubmissions"
                  value={formData.max_resubmissions}
                  onChange={handleChange}
                  min="1"
                  max="10"
                  placeholder="Maximum resubmissions"
                />
                <InputGroup.Text>times</InputGroup.Text>
              </InputGroup>
            )}
          </Form.Group>
        </Col>
      </Row>

      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <People className="me-2" size={14} />
              Group Assignment
            </Form.Label>
            <div className="d-flex align-items-center mb-2">
              <Form.Check
                type="switch"
                id="is-group-assignment"
                name="is_group_assignment"
                checked={formData.is_group_assignment}
                onChange={handleChange}
                label="This is a group assignment"
              />
            </div>
            {formData.is_group_assignment && (
              <InputGroup>
                <Form.Control
                  type="number"
                  name="max_group_size"
                  value={formData.max_group_size}
                  onChange={handleChange}
                  min="1"
                  max="10"
                  placeholder="Maximum group size"
                />
                <InputGroup.Text>students</InputGroup.Text>
              </InputGroup>
            )}
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label className="fw-semibold">
              <ShieldCheck className="me-2" size={14} />
              Approval Required
            </Form.Label>
            <div className="d-flex align-items-center">
              <Form.Check
                type="switch"
                id="require-approval"
                name="require_approval"
                checked={formData.require_approval}
                onChange={handleChange}
                label="Require approval before publishing"
              />
            </div>
          </Form.Group>
        </Col>
      </Row>

      <Form.Group className="mb-3">
        <Form.Label className="fw-semibold">
          <FileEarmarkText className="me-2" size={14} />
          Teacher Notes (Private)
        </Form.Label>
        <Form.Control
          as="textarea"
          rows={2}
          name="teacher_notes"
          value={formData.teacher_notes}
          onChange={handleChange}
          placeholder="Private notes for teachers only..."
        />
      </Form.Group>
    </div>
  );
};

const renderPreviewContent = (props) => {
  const { formData, subjects, classes, rubricItems, calculateRubricTotal, attachments, formatFileSize } = props;
  
  return (
    <Card>
      <Card.Header className="bg-light">
        <h4 className="mb-2">{formData.title}</h4>
        <div className="d-flex gap-2 flex-wrap">
          <Badge bg="secondary">{formData.assignment_type.toUpperCase()}</Badge>
          <Badge bg={
            formData.difficulty_level === 'easy' ? 'success' :
            formData.difficulty_level === 'medium' ? 'warning' :
            formData.difficulty_level === 'hard' ? 'danger' : 'dark'
          }>
            {formData.difficulty_level.toUpperCase()}
          </Badge>
          <Badge bg="primary">{formData.total_marks} Marks</Badge>
          <Badge bg="info">{formData.estimated_completion_time} min</Badge>
        </div>
      </Card.Header>
      <Card.Body>
        <div className="mb-4">
          <h5>Description</h5>
          <p className="text-muted">{formData.description || 'No description provided'}</p>
        </div>

        <Row className="mb-4">
          <Col md={6}>
            <div className="mb-3">
              <strong>Subject:</strong>
              <p>{subjects.find(s => s.id === formData.subject)?.name || 'Not set'}</p>
            </div>
            <div className="mb-3">
              <strong>Class:</strong>
              <p>{classes.find(c => c.id === formData.classroom)?.name || 'Not set'}</p>
            </div>
          </Col>
          <Col md={6}>
            <div className="mb-3">
              <strong>Due Date:</strong>
              <p>{formData.due_date ? `${formData.due_date} at ${formData.due_time}` : 'Not set'}</p>
            </div>
            <div className="mb-3">
              <strong>Passing Marks:</strong>
              <p>{formData.passing_marks} marks ({Math.round((formData.passing_marks/formData.total_marks)*100)}%)</p>
            </div>
          </Col>
        </Row>

        {formData.instructions && (
          <div className="mb-4">
            <h5>Instructions</h5>
            <div className="bg-light p-3 rounded">
              <pre className="mb-0" style={{ whiteSpace: 'pre-wrap' }}>{formData.instructions}</pre>
            </div>
          </div>
        )}

        {rubricItems.length > 0 && (
          <div className="mb-4">
            <h5>Grading Rubric</h5>
            <Table bordered size="sm">
              <thead>
                <tr>
                  <th>Criteria</th>
                  <th>Marks</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {rubricItems.map((item, index) => (
                  <tr key={index}>
                    <td>{item.criteria || 'Not specified'}</td>
                    <td>{item.marks}</td>
                    <td>{item.description || 'No description'}</td>
                  </tr>
                ))}
                <tr className="table-primary">
                  <td className="fw-bold">Total</td>
                  <td className="fw-bold">{calculateRubricTotal()}</td>
                  <td></td>
                </tr>
              </tbody>
            </Table>
          </div>
        )}

        {attachments.length > 0 && (
          <div>
            <h5>Attachments ({attachments.length})</h5>
            <ListGroup>
              {attachments.map((file, index) => (
                <ListGroup.Item key={index} className="d-flex align-items-center">
                  <FileEarmark className="me-3 text-primary" size={18} />
                  <div>
                    <div className="fw-medium">{file.name}</div>
                    <small className="text-muted">
                      {formatFileSize(file.size)}
                    </small>
                  </div>
                </ListGroup.Item>
              ))}
            </ListGroup>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

// ==================== MAIN COMPONENT ====================
const CreateAssignment = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const isMounted = useRef(true);
  const autoSaveTimer = useRef(null);

  // State management
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [previewModal, setPreviewModal] = useState(false);
  const [setupRequired, setSetupRequired] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [formTouched, setFormTouched] = useState(false);

  // Data states
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [academicYears, setAcademicYears] = useState([]);
  const [terms, setTerms] = useState([]);
  const [streams, setStreams] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [missingItems, setMissingItems] = useState([]);

  // Form states
  const [formData, setFormData] = useState(getInitialFormData);
  const [attachments, setAttachments] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [rubricItems, setRubricItems] = useState([]);

  // ==================== EFFECTS ====================

  // Check if user is teacher
  useEffect(() => {
    if (currentUser && currentUser.role !== 'teacher') {
      toast.error('Only teachers can create assignments.');
      navigate('/dashboard');
    }
  }, [currentUser, navigate]);

  // Auto-save draft
  const autoSaveDraft = useCallback(() => {
    if (autoSaveTimer.current) {
      clearTimeout(autoSaveTimer.current);
    }

    autoSaveTimer.current = setTimeout(() => {
      if (formData.title.trim()) {
        try {
          const draftToSave = {
            ...formData,
            attachments: attachments.map(file => ({
              name: file.name,
              size: file.size,
              type: file.type
            })),
            rubricItems,
            lastSaved: new Date().toISOString()
          };
          localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draftToSave));
          console.log('Auto-saved draft');
        } catch (err) {
          console.warn('Failed to auto-save draft:', err);
        }
      }
    }, 2000);
  }, [formData, attachments, rubricItems]);

  useEffect(() => {
    if (formTouched) {
      autoSaveDraft();
    }
  }, [formData, formTouched, autoSaveDraft]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimer.current) {
        clearTimeout(autoSaveTimer.current);
      }
    };
  }, []);

  // Fetch all required data
  useEffect(() => {
    let isMountedRef = true;
    
    const fetchData = async () => {
      if (!isMountedRef || !currentUser) return;
      
      setLoading(true);
      setError('');
      setSetupRequired(false);
      setMissingItems([]);

      try {
        const [
          subjectsResponse, 
          classesResponse, 
          academicYearsResponse, 
          termsResponse,
          streamsResponse
        ] = await Promise.allSettled([
          academicAPI.getSubjects({ limit: 100, ordering: 'name', is_active: true }),
          academicAPI.getClasses({ limit: 100, ordering: 'name', is_active: true }),
          academicAPI.getAcademicYears({ limit: 100, ordering: '-start_date', is_active: true }),
          academicAPI.getAcademicTerms({ limit: 100, ordering: '-start_date', is_active: true }),
          academicAPI.getStreams({ limit: 100, ordering: 'name' })
        ]);

        // Process responses
        const loadedSubjects = processAPIResponse(subjectsResponse);
        const loadedClasses = processAPIResponse(classesResponse);
        const loadedYears = processAPIResponse(academicYearsResponse);
        const loadedTerms = processAPIResponse(termsResponse);
        const loadedStreams = processAPIResponse(streamsResponse);

        setSubjects(loadedSubjects);
        setClasses(loadedClasses);
        setAcademicYears(loadedYears);
        setTerms(loadedTerms);
        setStreams(loadedStreams);

        // Check for setup requirements
        if (isMountedRef) {
          const missing = [];
          if (loadedYears.length === 0) missing.push('Academic Years');
          if (loadedSubjects.length === 0) missing.push('Subjects/Courses');
          if (loadedClasses.length === 0) missing.push('Classes/Groups');
          if (loadedTerms.length === 0) missing.push('Academic Terms');
          
          setMissingItems(missing);
          const hasRequiredData = missing.length === 0;

          if (!hasRequiredData) {
            setSetupRequired(true);
            setError(`Please set up: ${missing.join(', ')}`);
            toast.warning(`Missing required data: ${missing.join(', ')}`);
          } else {
            setSetupRequired(false);
            // Auto-select current year and term
            const currentYear = loadedYears.find(year => year.is_current);
            const currentTerm = loadedTerms.find(term => term.is_current);
            
            setFormData(prev => ({
              ...prev,
              ...(currentYear && { academic_year: currentYear.id }),
              ...(currentTerm && { term: currentTerm.id })
            }));
          }
        }

        // Load cached templates
        try {
          const cachedTemplates = localStorage.getItem(TEMPLATE_STORAGE_KEY);
          if (cachedTemplates) {
            setTemplates(JSON.parse(cachedTemplates));
          }
        } catch (cacheErr) {
          console.warn('Failed to load cached templates:', cacheErr);
        }

      } catch (err) {
        console.error('Error in fetchInitialData:', err);
        setError('Failed to load required data. Please check your connection and try again.');
        setSetupRequired(true);
        toast.error('Failed to load academic data. Please try again.');
      } finally {
        if (isMountedRef) {
          setLoading(false);
        }
      }
    };
    
    fetchData();
    
    return () => {
      isMountedRef = false;
    };
  }, [currentUser]);

  // ==================== EVENT HANDLERS ====================

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setFormTouched(true);
    setValidationErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handleSubmit = async (e, status = 'draft') => {
    e.preventDefault();
    
    if (submitting) return;
    
    setSubmitting(true);
    setSaving(true);
    
    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      setError('Please fix the errors in the form');
      toast.error('Please fix the form errors before submitting.');
      setSaving(false);
      setSubmitting(false);
      return;
    }
    
    setError('');
    setSuccess('');

    try {
      // Authentication check
      const authCheck = await authAPI.getCurrentUser();
      if (!authCheck.success) {
        setError('Authentication failed. Please login again.');
        toast.error('Authentication failed. Redirecting to login...');
        setTimeout(() => navigate('/login'), 2000);
        return;
      }

      const user = authCheck.user || currentUser;
      if (user?.role !== 'teacher') {
        setError('Only teachers can create assignments.');
        toast.error('Permission denied. Only teachers can create assignments.');
        setSaving(false);
        setSubmitting(false);
        return;
      }

      // Prepare submission data
      const submitData = prepareSubmissionData(formData, user.id);
      
      // Submit to API
      const result = await assignmentsAPI.createAssignment(submitData);
      
      if (result.success) {
        const assignmentId = result.data.id;
        const successMessage = status === 'draft' 
          ? 'Assignment saved as draft successfully!' 
          : 'Assignment published successfully!';
        
        localStorage.removeItem(DRAFT_STORAGE_KEY);
        setSuccess(successMessage);
        toast.success(successMessage);
        
        // Upload attachments if any
        if (attachments.length > 0) {
          await uploadAttachments(assignmentId);
        }
        
        setTimeout(() => {
          navigate('/teacher/assignments', {
            state: { 
              message: successMessage,
              assignmentId: assignmentId
            }
          });
        }, 1500);
      } else {
        const errorMessage = result.error?.message || 'Failed to create assignment. Please check your inputs.';
        setError(errorMessage);
        toast.error(errorMessage);
      }
    } catch (err) {
      console.error('Unexpected error:', err);
      const errorMessage = formatSubmissionError(err);
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setSaving(false);
      setSubmitting(false);
    }
  };

  const handleAttachmentUpload = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = validateAndFilterFiles(files);
    
    if (validFiles.length > 0) {
      setAttachments(prev => [...prev, ...validFiles]);
      setFormTouched(true);
      toast.success(`Added ${validFiles.length} file(s)`);
    }
    
    e.target.value = '';
  };

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
    setFormTouched(true);
  };

  // ==================== HELPER FUNCTIONS ====================

  const validateForm = () => {
    const errors = {};
    
    // Required fields validation
    if (!formData.title?.trim()) errors.title = 'Assignment title is required';
    if (!formData.subject) errors.subject = 'Please select a subject';
    if (!formData.classroom) errors.classroom = 'Please select a class';
    if (!formData.academic_year) errors.academic_year = 'Please select an academic year';
    if (!formData.term) errors.term = 'Please select a term';
    if (!formData.due_date) errors.due_date = 'Due date is required';
    if (!formData.due_time) errors.due_time = 'Due time is required';
    if (!formData.total_marks || formData.total_marks <= 0) errors.total_marks = 'Total marks must be greater than 0';
    if (formData.passing_marks > formData.total_marks) errors.passing_marks = 'Passing marks cannot exceed total marks';
    
    // Date validation
    if (formData.due_date) {
      const dueDate = new Date(formData.due_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (dueDate < today) errors.due_date = 'Due date cannot be in the past';
    }
    
    // UUID validation
    if (formData.academic_year && !isValidUUID(formData.academic_year)) {
      errors.academic_year = 'Invalid academic year selection';
    }
    if (formData.term && !isValidUUID(formData.term)) {
      errors.term = 'Invalid term selection';
    }
    
    // Rubric validation
    if (rubricItems.length > 0) {
      const rubricTotal = calculateRubricTotal();
      if (Math.abs(rubricTotal - formData.total_marks) > 0.01) {
        errors.rubric = `Rubric total (${rubricTotal}) doesn't match assignment total marks (${formData.total_marks})`;
      }
    }
    
    return errors;
  };

  const calculateRubricTotal = () => {
    return rubricItems.reduce((sum, item) => sum + (parseFloat(item.marks) || 0), 0);
  };

  const clearDraft = () => {
    if (window.confirm('Are you sure you want to clear this draft? This cannot be undone.')) {
      localStorage.removeItem(DRAFT_STORAGE_KEY);
      setFormData(getInitialFormData());
      setAttachments([]);
      setRubricItems([]);
      setValidationErrors({});
      setFormTouched(false);
      toast.info('Draft cleared successfully');
    }
  };

  const uploadAttachments = async (assignmentId) => {
    if (!attachments.length || !assignmentId) return;
    
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const totalFiles = attachments.length;
      let uploadedCount = 0;
      
      for (const file of attachments) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('assignment', assignmentId);
        formData.append('uploaded_by', currentUser.id);
        formData.append('file_name', file.name);
        formData.append('file_size', file.size);
        formData.append('file_type', file.type);
        
        await assignmentsAPI.uploadAssignmentAttachment(assignmentId, formData);
        uploadedCount++;
        setUploadProgress(Math.round((uploadedCount / totalFiles) * 100));
      }
      
      toast.success(`Uploaded ${totalFiles} attachment(s) successfully`);
    } catch (error) {
      console.error('Error uploading attachments:', error);
      toast.error('Failed to upload some attachments');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  // ==================== RENDER ====================

  if (loading) return <LoadingState />;
  
  if (setupRequired) return (
    <SetupRequiredState 
      missingItems={missingItems} 
      navigate={navigate}
      academicYears={academicYears}
      subjects={subjects}
      classes={classes}
      terms={terms}
    />
  );

  // ==================== SUB-COMPONENTS ====================
  const TabTitle = ({ icon: Icon, text }) => (
    <span>
      <Icon className="me-1" size={14} />
      {text}
    </span>
  );

  const SummaryItem = ({ label, value, isBadge = false, isBold = false }) => {
    let displayValue = value;
    
    if (isBadge) {
      const badgeProps = getBadgeProps(value);
      return (
        <ListGroup.Item className="d-flex justify-content-between align-items-center">
          <span>{label}</span>
          <Badge {...badgeProps}>{displayValue.toUpperCase()}</Badge>
        </ListGroup.Item>
      );
    }
    
    return (
      <ListGroup.Item className="d-flex justify-content-between align-items-center">
        <span>{label}</span>
        <span className={isBold ? 'fw-bold text-primary' : 'fw-semibold'}>
          {displayValue || 'Not set'}
        </span>
      </ListGroup.Item>
    );
  };

  const RequiredFieldsCheck = () => (
    <Alert variant={Object.keys(formData).some(key => !formData[key] && key !== 'status') ? 'light' : 'info'} className="mt-3 p-2 small">
      <div className="d-flex align-items-center">
        <InfoCircle className="me-2" size={14} />
        <div>
          <strong>Required Fields:</strong>
          <ul className="mb-0 mt-1">
            {['title', 'subject', 'classroom', 'academic_year', 'term', 'due_date', 'total_marks'].map(field => (
              <li key={field} className={formData[field] ? 'text-success' : 'text-danger'}>
                {formData[field] ? '✓ ' : '✗ '}{field.replace('_', ' ')}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Alert>
  );

  const QuickActionButton = ({ variant, onClick, disabled, icon: Icon, text, loading = false }) => (
    <Button 
      variant={variant} 
      onClick={onClick}
      disabled={disabled}
      className="d-flex justify-content-center align-items-center"
    >
      {loading ? (
        <Spinner animation="border" size="sm" className="me-2" />
      ) : (
        <Icon className="me-2" />
      )}
      {text}
    </Button>
  );

  return (
    <Container fluid className="mt-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center flex-wrap">
            <div className="d-flex align-items-center mb-2 mb-md-0">
              <Button 
                variant="outline-secondary" 
                onClick={() => navigate('/teacher/assignments')}
                className="me-3"
                size="sm"
              >
                <ArrowLeft size={16} />
              </Button>
              <div>
                <h1 className="h3 mb-1">
                  <Journal className="me-2" size={24} />
                  Create New Assignment
                </h1>
                <p className="text-muted mb-0">
                  {currentUser ? `Teacher: ${currentUser.full_name || currentUser.email}` : 'Loading...'}
                  {formTouched && (
                    <span className="ms-2 text-info">
                      <small>
                        <ClockHistory size={12} className="me-1" />
                        Auto-save enabled
                      </small>
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div className="d-flex gap-2 flex-wrap">
              <Button 
                variant="outline-danger"
                onClick={clearDraft}
                size="sm"
                disabled={saving || !formTouched}
              >
                <Trash className="me-1" size={14} />
                Clear Draft
              </Button>
              <Button 
                variant="outline-primary"
                onClick={() => setPreviewModal(true)}
                disabled={!formData.title || !formData.subject || !formData.classroom || saving}
                size="sm"
              >
                <Eye className="me-1" size={14} />
                Preview
              </Button>
              <Button 
                variant="outline-secondary"
                onClick={(e) => handleSubmit(e, 'draft')}
                disabled={saving || uploading || !formData.title}
                size="sm"
              >
                {saving ? <Spinner animation="border" size="sm" /> : <Save className="me-1" size={14} />}
                Save Draft
              </Button>
              <Button 
                variant="primary"
                onClick={(e) => handleSubmit(e, 'published')}
                disabled={saving || uploading}
                size="sm"
              >
                {saving ? <Spinner animation="border" size="sm" /> : 'Publish Assignment'}
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {/* Alerts */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')} className="mb-3">
          <ExclamationTriangle className="me-2" size={16} />
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')} className="mb-3">
          <CheckCircle className="me-2" size={16} />
          {success}
        </Alert>
      )}

      {uploading && (
        <Alert variant="info" className="mb-3">
          <div className="d-flex align-items-center">
            <Upload className="me-2" size={16} />
            <div className="flex-grow-1">
              <div className="d-flex justify-content-between">
                <span>Uploading {attachments.length} attachments...</span>
                <span>{Math.round(uploadProgress)}%</span>
              </div>
              <ProgressBar now={uploadProgress} className="mt-1" animated />
            </div>
          </div>
        </Alert>
      )}

      {/* Main Content */}
      <Row>
        <Col lg={8}>
          <Card className="border-0 shadow-sm mb-4">
            <Card.Body>
              <Tabs defaultActiveKey="basic" className="mb-4">
                <Tab eventKey="basic" title={<TabTitle icon={FileText} text="Basic Info" />}>
                  {renderBasicInfo({
                    formData,
                    validationErrors,
                    subjects,
                    classes,
                    streams,
                    academicYears,
                    terms,
                    handleChange
                  })}
                </Tab>

                <Tab eventKey="grading" title={<TabTitle icon={Percent} text="Grading" />}>
                  {renderGradingSection({
                    formData,
                    validationErrors,
                    handleChange
                  })}
                </Tab>

                <Tab eventKey="curriculum" title={<TabTitle icon={Bullseye} text="Curriculum" />}>
                  {renderCurriculumSection({
                    formData,
                    handleChange
                  })}
                </Tab>

                <Tab eventKey="rubric" title={<TabTitle icon={CardChecklist} text="Rubric" />}>
                  {renderRubricSection({
                    validationErrors,
                    rubricItems,
                    setRubricItems,
                    calculateRubricTotal,
                    formData
                  })}
                </Tab>

                <Tab eventKey="attachments" title={<TabTitle icon={Paperclip} text="Attachments" />}>
                  {renderAttachmentsSection({
                    attachments,
                    handleAttachmentUpload,
                    removeAttachment,
                    formatFileSize
                  })}
                </Tab>

                <Tab eventKey="settings" title={<TabTitle icon={Gear} text="Settings" />}>
                  {renderSettingsSection({
                    formData,
                    validationErrors,
                    handleChange
                  })}
                </Tab>
              </Tabs>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Summary Card */}
          <Card className="border-0 shadow-sm mb-4 sticky-top" style={{ top: '20px' }}>
            <Card.Header className="bg-primary text-white d-flex align-items-center">
              <JournalCheck className="me-2" />
              <h6 className="mb-0">Assignment Summary</h6>
            </Card.Header>
            <Card.Body>
              <ListGroup variant="flush">
                <SummaryItem label="Status:" value={formData.status} isBadge />
                <SummaryItem label="Type:" value={formData.assignment_type.replace('_', ' ')} />
                <SummaryItem label="Subject:" value={getItemName(subjects, formData.subject)} />
                <SummaryItem label="Class:" value={getItemName(classes, formData.classroom)} />
                <SummaryItem label="Academic Year:" value={getItemName(academicYears, formData.academic_year)} />
                <SummaryItem label="Term:" value={getItemName(terms, formData.term)} />
                <SummaryItem label="Due Date:" value={formatDueDate(formData)} />
                <SummaryItem label="Total Marks:" value={formData.total_marks} isBold />
                <SummaryItem label="Difficulty:" value={formData.difficulty_level} isBadge />
                <SummaryItem label="Attachments:" value={`${attachments.length} file(s)`} isBadge />
              </ListGroup>
              
              <RequiredFieldsCheck />
            </Card.Body>
          </Card>

          {/* Quick Actions Card */}
          <Card className="border-0 shadow-sm">
            <Card.Header className="d-flex align-items-center">
              <ClipboardCheck className="me-2" />
              <h6 className="mb-0">Quick Actions</h6>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <QuickActionButton
                  variant="outline-primary"
                  onClick={() => setPreviewModal(true)}
                  disabled={!formData.title || !formData.subject || !formData.classroom}
                  icon={Eye}
                  text="Preview Assignment"
                />
                <QuickActionButton
                  variant="outline-success"
                  onClick={(e) => handleSubmit(e, 'draft')}
                  disabled={saving || !formData.title}
                  icon={Save}
                  text="Save as Draft"
                  loading={saving}
                />
                <QuickActionButton
                  variant="primary"
                  onClick={(e) => handleSubmit(e, 'published')}
                  disabled={saving}
                  icon={FileEarmarkCheck}
                  text="Publish Now"
                  loading={saving}
                />
                <QuickActionButton
                  variant="outline-secondary"
                  onClick={clearDraft}
                  disabled={saving || !formTouched}
                  icon={Trash}
                  text="Clear Draft"
                />
              </div>
              
              {formTouched && (
                <div className="mt-3 text-center">
                  <small className="text-muted">
                    <ClockHistory size={12} className="me-1" />
                    Draft auto-saves every 2 seconds
                  </small>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Preview Modal */}
      <Modal 
        show={previewModal} 
        onHide={() => setPreviewModal(false)}
        size="lg"
        fullscreen="lg-down"
        centered
      >
        <Modal.Header closeButton className="bg-light">
          <Modal.Title className="d-flex align-items-center">
            <Eye className="me-2" />
            Assignment Preview
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {!formData.title ? (
            <Alert variant="warning">
              Please complete the basic information first to see the preview.
            </Alert>
          ) : (
            renderPreviewContent({
              formData,
              subjects,
              classes,
              rubricItems,
              calculateRubricTotal,
              attachments,
              formatFileSize
            })
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setPreviewModal(false)}>
            Close
          </Button>
          <Button 
            variant="primary" 
            onClick={(e) => {
              setPreviewModal(false);
              handleSubmit(e, 'published');
            }}
            disabled={saving}
          >
            {saving ? <Spinner animation="border" size="sm" /> : 'Publish Now'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default CreateAssignment;