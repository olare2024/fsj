import React, { useState, useEffect, useCallback } from 'react';
import {
  Container, Row, Col, Card, Table, Button, Badge,
  Alert, Spinner, Form, Modal, ProgressBar, InputGroup,
  Dropdown, Pagination, Tabs, Tab
} from 'react-bootstrap';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeftIcon, SaveIcon, CheckCircleIcon, XCircleIcon, SearchIcon,
  FilterIcon, DownloadIcon, UploadIcon, ViewIcon, SendIcon, ClockIcon,
  FileTextIcon, UserIcon, StarIcon, MessageSquareIcon, AwardIcon,
  GradeIcon, AssignmentIcon
} from '../../components/Icons';
import { teacherAPI } from '../../services/teacherAPI';
import { useAuth } from '../../context/AuthContext';

const GradeAssignment = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [assignment, setAssignment] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [grading, setGrading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    sortBy: 'submission_date',
    sortOrder: 'desc'
  });
  const [pagination, setPagination] = useState({
    current: 1,
    total: 0,
    pageSize: 10
  });
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [gradeModal, setGradeModal] = useState(false);
  const [bulkAction, setBulkAction] = useState('');
  const [selectedSubmissions, setSelectedSubmissions] = useState(new Set());

  const fetchAssignmentData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const [assignmentResult, submissionsResult] = await Promise.all([
        teacherAPI.getAssignmentSubmissions(id),
        teacherAPI.getAssignmentSubmissions(id)
      ]);

      if (assignmentResult.success) {
        setAssignment(assignmentResult.data?.assignment);
        setSubmissions(assignmentResult.data?.submissions || []);
        setFilteredSubmissions(assignmentResult.data?.submissions || []);
        setPagination(prev => ({
          ...prev,
          total: assignmentResult.data?.submissions?.length || 0
        }));
      } else {
        setError(assignmentResult.error?.message || 'Failed to load assignment data');
      }
    } catch (err) {
      setError('An unexpected error occurred while loading assignment data');
      console.error('Error fetching assignment data:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchAssignmentData();
    }
  }, [id, fetchAssignmentData]);

  useEffect(() => {
    let filtered = [...submissions];

    // Apply search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(submission =>
        submission.student_name?.toLowerCase().includes(searchLower) ||
        submission.student_admission_no?.toLowerCase().includes(searchLower)
      );
    }

    // Apply status filter
    if (filters.status) {
      filtered = filtered.filter(submission => submission.status === filters.status);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[filters.sortBy];
      let bValue = b[filters.sortBy];

      if (filters.sortBy === 'submission_date' || filters.sortBy === 'graded_at') {
        aValue = new Date(aValue || 0);
        bValue = new Date(bValue || 0);
      }

      if (filters.sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredSubmissions(filtered);
    setPagination(prev => ({ ...prev, total: filtered.length }));
  }, [submissions, filters]);

  const handleGradeSubmission = async (submissionId, gradeData) => {
    try {
      setGrading(true);
      setError('');

      const result = await teacherAPI.gradeAssignment(submissionId, gradeData);
      if (result.success) {
        setSuccess('Grade submitted successfully!');
        fetchAssignmentData();
        setGradeModal(false);
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error?.message || 'Failed to submit grade');
      }
    } catch (err) {
      setError('An unexpected error occurred while grading');
      console.error('Error grading submission:', err);
    } finally {
      setGrading(false);
    }
  };

  const handleBulkAction = async (action) => {
    if (selectedSubmissions.size === 0) return;

    try {
      setGrading(true);
      setError('');

      // This would call your bulk action API
      // For now, just show a success message
      setSuccess(`${action} applied to ${selectedSubmissions.size} submissions`);
      setSelectedSubmissions(new Set());
      setBulkAction('');

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(`Failed to perform ${action} on selected submissions`);
    } finally {
      setGrading(false);
    }
  };

  const toggleSubmissionSelection = (submissionId) => {
    const newSelection = new Set(selectedSubmissions);
    if (newSelection.has(submissionId)) {
      newSelection.delete(submissionId);
    } else {
      newSelection.add(submissionId);
    }
    setSelectedSubmissions(newSelection);
  };

  const selectAllSubmissions = () => {
    if (selectedSubmissions.size === filteredSubmissions.length) {
      setSelectedSubmissions(new Set());
    } else {
      setSelectedSubmissions(new Set(filteredSubmissions.map(s => s.id)));
    }
  };

  const getStatusVariant = (status) => {
    const variants = {
      'submitted': 'warning',
      'graded': 'success',
      'late': 'danger',
      'not_submitted': 'secondary',
      'returned': 'info'
    };
    return variants[status] || 'primary';
  };

  const getGradeColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'info';
    if (percentage >= 40) return 'warning';
    return 'danger';
  };

  const calculatePercentage = (submission) => {
    if (!submission.marks_obtained || !assignment?.total_marks) return 0;
    return (submission.marks_obtained / assignment.total_marks) * 100;
  };

  const getGradingProgress = () => {
    const total = submissions.length;
    const graded = submissions.filter(s => s.status === 'graded').length;
    return {
      total,
      graded,
      percentage: total > 0 ? (graded / total) * 100 : 0
    };
  };

  const gradingProgress = getGradingProgress();

  // Pagination
  const paginatedSubmissions = filteredSubmissions.slice(
    (pagination.current - 1) * pagination.pageSize,
    pagination.current * pagination.pageSize
  );

  const totalPages = Math.ceil(pagination.total / pagination.pageSize);

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" />
          <p className="mt-3 text-muted">Loading assignment submissions...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div className="d-flex align-items-center">
              <Button
                variant="outline-secondary"
                onClick={() => navigate('/teacher/assignments')}
                className="me-3"
              >
                <ArrowLeftIcon size={16} />
              </Button>
              <div>
                <h1 className="h3 mb-1">
                  <GradeIcon className="me-2" size={24} />
                  Grade Submissions
                </h1>
                <p className="text-muted mb-0">
                  {assignment?.title} • {submissions.length} submissions
                  {gradingProgress.total > 0 && (
                    <span className="ms-2">
                      • <strong>{Math.round(gradingProgress.percentage)}%</strong> graded
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div className="d-flex gap-2">
              <Button variant="outline-primary">
                <DownloadIcon className="me-2" size={16} />
                Export Grades
              </Button>
              <Button variant="primary" onClick={fetchAssignmentData}>
                Refresh
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {/* Assignment Summary */}
      {assignment && (
        <Card className="border-0 shadow-sm mb-4">
          <Card.Body>
            <Row className="align-items-center">
              <Col md={6}>
                <h5 className="mb-1">
                  <AssignmentIcon className="me-2" size={20} />
                  {assignment.title}
                </h5>
                <p className="text-muted mb-2">{assignment.description}</p>
                <div className="d-flex gap-3 text-muted small">
                  <span>
                    <FileTextIcon className="me-1" size={14} />
                    {assignment.assignment_type}
                  </span>
                  <span>
                    <GradeIcon className="me-1" size={14} />
                    {assignment.total_marks} marks
                  </span>
                  <span>
                    <ClockIcon className="me-1" size={14} />
                    Due: {new Date(assignment.due_date).toLocaleDateString()}
                  </span>
                </div>
              </Col>
              <Col md={6}>
                <div className="d-flex justify-content-end gap-3">
                  <div className="text-center">
                    <div className="h4 mb-0 text-primary">{submissions.length}</div>
                    <small className="text-muted">Total Submissions</small>
                  </div>
                  <div className="text-center">
                    <div className="h4 mb-0 text-success">
                      {submissions.filter(s => s.status === 'graded').length}
                    </div>
                    <small className="text-muted">Graded</small>
                  </div>
                  <div className="text-center">
                    <div className="h4 mb-0 text-warning">
                      {submissions.filter(s => s.status === 'submitted').length}
                    </div>
                    <small className="text-muted">Pending</small>
                  </div>
                </div>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}

      {/* Grading Progress */}
      <Card className="border-0 shadow-sm mb-4">
        <Card.Body>
          <div className="d-flex justify-content-between align-items-center mb-2">
            <h6 className="mb-0">Grading Progress</h6>
            <span className="text-muted">
              {gradingProgress.graded} of {gradingProgress.total} graded
            </span>
          </div>
          <ProgressBar>
            <ProgressBar
              variant="success"
              now={gradingProgress.percentage}
              key={1}
            />
          </ProgressBar>
        </Card.Body>
      </Card>

      {/* Filters and Bulk Actions */}
      <Card className="border-0 shadow-sm mb-4">
        <Card.Body>
          <Row className="g-3 align-items-center">
            <Col md={4}>
              <InputGroup>
                <InputGroup.Text>
                  <SearchIcon size={14} />
                </InputGroup.Text>
                <Form.Control
                  placeholder="Search students..."
                  value={filters.search}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                />
              </InputGroup>
            </Col>
            <Col md={2}>
              <Form.Select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              >
                <option value="">All Status</option>
                <option value="submitted">Pending</option>
                <option value="graded">Graded</option>
                <option value="late">Late</option>
                <option value="not_submitted">Not Submitted</option>
              </Form.Select>
            </Col>
            <Col md={3}>
              <Dropdown>
                <Dropdown.Toggle variant="outline-secondary">
                  Bulk Actions ({selectedSubmissions.size})
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={() => handleBulkAction('download')}>
                    <DownloadIcon className="me-2" size={14} />
                    Download Selected
                  </Dropdown.Item>
                  <Dropdown.Item onClick={() => handleBulkAction('approve')}>
                    <CheckCircleIcon className="me-2" size={14} />
                    Mark as Graded
                  </Dropdown.Item>
                  <Dropdown.Item onClick={() => handleBulkAction('return')}>
                    <XCircleIcon className="me-2" size={14} />
                    Return for Revision
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </Col>
            <Col md={3} className="text-end">
              <Button
                variant="outline-danger"
                size="sm"
                onClick={selectAllSubmissions}
              >
                {selectedSubmissions.size === filteredSubmissions.length ? 'Deselect All' : 'Select All'}
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Submissions Table */}
      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-0 py-3">
          <h5 className="mb-0">Student Submissions ({pagination.total})</h5>
        </Card.Header>
        <Card.Body className="p-0">
          {filteredSubmissions.length > 0 ? (
            <div className="table-responsive">
              <Table className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th style={{ width: '40px' }}>
                      <Form.Check
                        type="checkbox"
                        checked={selectedSubmissions.size === filteredSubmissions.length}
                        onChange={selectAllSubmissions}
                      />
                    </th>
                    <th>Student</th>
                    <th>Submission Date</th>
                    <th>Status</th>
                    <th>Marks</th>
                    <th>Grade</th>
                    <th>Feedback</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedSubmissions.map((submission) => {
                    const percentage = calculatePercentage(submission);
                    return (
                      <tr key={submission.id}>
                        <td>
                          <Form.Check
                            type="checkbox"
                            checked={selectedSubmissions.has(submission.id)}
                            onChange={() => toggleSubmissionSelection(submission.id)}
                          />
                        </td>
                        <td>
                          <div>
                            <div className="fw-semibold">
                              <UserIcon className="me-2" size={14} />
                              {submission.student_name}
                            </div>
                            <small className="text-muted">{submission.student_admission_no}</small>
                          </div>
                        </td>
                        <td>
                          {submission.submission_date ? (
                            <div className="d-flex align-items-center">
                              <CalendarIcon className="me-2" size={14} />
                              {new Date(submission.submission_date).toLocaleDateString()}
                            </div>
                          ) : (
                            <span className="text-muted">Not submitted</span>
                          )}
                        </td>
                        <td>
                          <Badge bg={getStatusVariant(submission.status)}>
                            {submission.status}
                          </Badge>
                          {submission.is_late && (
                            <Badge bg="danger" className="ms-1">
                              <ClockIcon className="me-1" size={10} />
                              Late
                            </Badge>
                          )}
                        </td>
                        <td>
                          {submission.marks_obtained ? (
                            <div>
                              <span className="fw-semibold">{submission.marks_obtained}</span>
                              <span className="text-muted">/{assignment?.total_marks}</span>
                            </div>
                          ) : (
                            <span className="text-muted">-</span>
                          )}
                        </td>
                        <td>
                          {submission.grade ? (
                            <Badge bg={getGradeColor(percentage)}>
                              {submission.grade}
                            </Badge>
                          ) : (
                            <span className="text-muted">-</span>
                          )}
                        </td>
                        <td>
                          {submission.teacher_feedback ? (
                            <Button variant="outline-info" size="sm">
                              <MessageSquareIcon size={14} />
                            </Button>
                          ) : (
                            <span className="text-muted">No feedback</span>
                          )}
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => {
                                setSelectedSubmission(submission);
                                setGradeModal(true);
                              }}
                            >
                              {submission.status === 'graded' ? 'Regrade' : 'Grade'}
                            </Button>
                            <Button variant="outline-secondary" size="sm">
                              <ViewIcon size={14} />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-5">
              <FileTextIcon size={48} className="text-muted mb-3" />
              <h5 className="text-muted">No submissions found</h5>
              <p className="text-muted">
                {filters.search || filters.status 
                  ? 'Try adjusting your filters' 
                  : 'No students have submitted this assignment yet'
                }
              </p>
            </div>
          )}
        </Card.Body>

        {/* Pagination */}
        {filteredSubmissions.length > 0 && totalPages > 1 && (
          <Card.Footer className="bg-white border-0">
            <div className="d-flex justify-content-between align-items-center">
              <small className="text-muted">
                Showing {((pagination.current - 1) * pagination.pageSize) + 1} to{' '}
                {Math.min(pagination.current * pagination.pageSize, pagination.total)} of{' '}
                {pagination.total} submissions
              </small>
              <Pagination className="mb-0">
                <Pagination.Prev
                  disabled={pagination.current === 1}
                  onClick={() => setPagination(prev => ({ ...prev, current: prev.current - 1 }))}
                />
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <Pagination.Item
                    key={page}
                    active={page === pagination.current}
                    onClick={() => setPagination(prev => ({ ...prev, current: page }))}
                  >
                    {page}
                  </Pagination.Item>
                ))}
                <Pagination.Next
                  disabled={pagination.current === totalPages}
                  onClick={() => setPagination(prev => ({ ...prev, current: prev.current + 1 }))}
                />
              </Pagination>
            </div>
          </Card.Footer>
        )}
      </Card>

      {/* Grade Submission Modal */}
      <Modal show={gradeModal} onHide={() => setGradeModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <GradeIcon className="me-2" size={20} />
            Grade Submission - {selectedSubmission?.student_name}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedSubmission && (
            <Tabs defaultActiveKey="grading">
              <Tab eventKey="grading" title={
                <span>
                  <GradeIcon className="me-2" size={14} />
                  Grading
                </span>
              }>
                <Form>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Marks Obtained</Form.Label>
                        <Form.Control
                          type="number"
                          min="0"
                          max={assignment?.total_marks}
                          defaultValue={selectedSubmission.marks_obtained || ''}
                          placeholder={`Max: ${assignment?.total_marks}`}
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Grade</Form.Label>
                        <Form.Select defaultValue={selectedSubmission.grade || ''}>
                          <option value="">Select Grade</option>
                          <option value="A">A (90-100%)</option>
                          <option value="B">B (80-89%)</option>
                          <option value="C">C (70-79%)</option>
                          <option value="D">D (60-69%)</option>
                          <option value="E">E (50-59%)</option>
                          <option value="F">F (Below 50%)</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  </Row>

                  <Form.Group className="mb-3">
                    <Form.Label>Teacher Feedback</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={4}
                      defaultValue={selectedSubmission.teacher_feedback || ''}
                      placeholder="Provide constructive feedback to the student..."
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Rubric Scores (Optional)</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={2}
                      placeholder='e.g., {"content": 8, "creativity": 9, "accuracy": 7}'
                    />
                  </Form.Group>
                </Form>
              </Tab>

              <Tab eventKey="submission" title={
                <span>
                  <FileTextIcon className="me-2" size={14} />
                  Submission Details
                </span>
              }>
                <div className="mb-3">
                  <strong>Submitted:</strong>{' '}
                  {selectedSubmission.submission_date 
                    ? new Date(selectedSubmission.submission_date).toLocaleString()
                    : 'Not submitted'
                  }
                </div>

                {selectedSubmission.submission_text && (
                  <div className="mb-3">
                    <strong>Submission Text:</strong>
                    <div className="border rounded p-3 mt-1 bg-light">
                      {selectedSubmission.submission_text}
                    </div>
                  </div>
                )}

                {selectedSubmission.submission_file && (
                  <div className="mb-3">
                    <strong>Attached File:</strong>
                    <div className="mt-1">
                      <Button variant="outline-primary" size="sm">
                        <DownloadIcon className="me-2" size={14} />
                        Download File
                      </Button>
                    </div>
                  </div>
                )}
              </Tab>
            </Tabs>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setGradeModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={() => handleGradeSubmission(selectedSubmission.id, {})}
            disabled={grading}
          >
            {grading ? <Spinner animation="border" size="sm" /> : 'Submit Grade'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default GradeAssignment;