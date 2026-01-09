import React, { useState, useEffect } from 'react';
import {
  Container, Row, Col, Card, Table, Button, Badge,
  Alert, Spinner, Form, Modal, ProgressBar,
  Dropdown, Tabs, Tab, InputGroup
} from 'react-bootstrap';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon, DownloadIcon, PrintIcon, EditIcon,
  CalendarIcon, UserIcon, FileTextIcon, CheckCircleIcon,
  ClockIcon, XCircleIcon, SendIcon, EyeIcon,
  SaveIcon, PlusIcon, UsersIcon, BookIcon,
  GradeIcon, DocumentIcon, HistoryIcon, FilterIcon
} from '../../components/Icons';
import { teacherAPI } from '../../services/teacherAPI';
import { useAuth } from '../../context/AuthContext';

const AssignmentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  const [assignment, setAssignment] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [grading, setGrading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('submissions');
  const [showGradeModal, setShowGradeModal] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [gradeData, setGradeData] = useState({ score: '', comments: '' });

  useEffect(() => {
    fetchAssignmentData();
  }, [id]);

  const fetchAssignmentData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch assignment details
      const assignmentResult = await teacherAPI.getAssignment(id);
      if (assignmentResult.success) {
        setAssignment(assignmentResult.data);
        
        // Fetch submissions for this assignment
        const submissionsResult = await teacherAPI.getSubmissions(id);
        if (submissionsResult.success) {
          setSubmissions(submissionsResult.data || []);
        }

        // Fetch class students
        const studentsResult = await teacherAPI.getClassStudents(assignmentResult.data.class_id);
        if (studentsResult.success) {
          setStudents(studentsResult.data || []);
        }
      } else {
        setError('Failed to load assignment details');
      }
    } catch (err) {
      setError('Failed to load assignment data');
    } finally {
      setLoading(false);
    }
  };

  const handleGradeSubmission = (submission) => {
    setSelectedSubmission(submission);
    setGradeData({
      score: submission.score || '',
      comments: submission.comments || ''
    });
    setShowGradeModal(true);
  };

  const submitGrade = async () => {
    try {
      setGrading(true);
      setError('');

      const result = await teacherAPI.gradeSubmission(selectedSubmission.id, {
        score: parseFloat(gradeData.score),
        comments: gradeData.comments,
        graded_by: currentUser.id
      });

      if (result.success) {
        setSuccess('Grade submitted successfully!');
        setShowGradeModal(false);
        fetchAssignmentData(); // Refresh data
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError(result.error?.message || 'Failed to submit grade');
      }
    } catch (err) {
      setError('Failed to submit grade');
    } finally {
      setGrading(false);
    }
  };

  const getStatusVariant = (status) => {
    const variants = {
      'submitted': 'success',
      'graded': 'primary',
      'late': 'warning',
      'missing': 'danger',
      'draft': 'secondary'
    };
    return variants[status] || 'secondary';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'submitted': <CheckCircleIcon size={14} />,
      'graded': <GradeIcon size={14} />,
      'late': <ClockIcon size={14} />,
      'missing': <XCircleIcon size={14} />,
      'draft': <FileTextIcon size={14} />
    };
    return icons[status] || <FileTextIcon size={14} />;
  };

  const calculateStats = () => {
    const totalStudents = students.length;
    const submitted = submissions.filter(s => s.status === 'submitted' || s.status === 'graded').length;
    const graded = submissions.filter(s => s.status === 'graded').length;
    const averageScore = submissions.filter(s => s.score)
      .reduce((acc, curr) => acc + parseFloat(curr.score), 0) / graded || 0;

    return {
      totalStudents,
      submitted,
      graded,
      averageScore: averageScore.toFixed(1),
      submissionRate: totalStudents ? ((submitted / totalStudents) * 100).toFixed(1) : 0
    };
  };

  const stats = calculateStats();

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" />
          <p className="mt-3 text-muted">Loading assignment details...</p>
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
            <div>
              <Button 
                variant="outline-secondary" 
                className="mb-2"
                onClick={() => navigate('/assignments')}
              >
                <ArrowLeftIcon className="me-2" size={16} />
                Back to Assignments
              </Button>
              <h1 className="h3 mb-1 d-flex align-items-center">
                <BookIcon className="me-2" size={24} />
                {assignment?.title || 'Assignment Details'}
              </h1>
              <p className="text-muted mb-0">
                {assignment?.description || 'View and manage assignment submissions'}
              </p>
            </div>
            <div className="d-flex gap-2">
              <Button variant="outline-primary">
                <DownloadIcon className="me-2" size={16} />
                Export
              </Button>
              <Button variant="outline-secondary">
                <PrintIcon className="me-2" size={16} />
                Print
              </Button>
              <Button variant="primary">
                <EditIcon className="me-2" size={16} />
                Edit Assignment
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          <XCircleIcon className="me-2" size={16} />
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          <CheckCircleIcon className="me-2" size={16} />
          {success}
        </Alert>
      )}

      <Row>
        {/* Assignment Info Sidebar */}
        <Col lg={4} className="mb-4">
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white d-flex align-items-center">
              <DocumentIcon className="me-2" size={18} />
              <h6 className="mb-0">Assignment Information</h6>
            </Card.Header>
            <Card.Body>
              {assignment && (
                <>
                  <div className="mb-3">
                    <strong className="d-flex align-items-center">
                      <BookIcon className="me-2" size={14} />
                      Title:
                    </strong>
                    <p className="mb-0">{assignment.title}</p>
                  </div>
                  
                  <div className="mb-3">
                    <strong>Description:</strong>
                    <p className="mb-0 text-muted">{assignment.description}</p>
                  </div>
                  
                  <div className="mb-3">
                    <strong className="d-flex align-items-center">
                      <CalendarIcon className="me-2" size={14} />
                      Due Date:
                    </strong>
                    <p className="mb-0">
                      {new Date(assignment.due_date).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="mb-3">
                    <strong>Total Points:</strong>
                    <p className="mb-0">
                      <Badge bg="primary">{assignment.max_score} points</Badge>
                    </p>
                  </div>
                  
                  <div className="mb-3">
                    <strong>Status:</strong>
                    <p className="mb-0">
                      <Badge bg={new Date(assignment.due_date) > new Date() ? 'success' : 'warning'}>
                        {new Date(assignment.due_date) > new Date() ? 'Active' : 'Closed'}
                      </Badge>
                    </p>
                  </div>
                  
                  <div className="mb-3">
                    <strong>Instructions:</strong>
                    <p className="mb-0 text-muted small">
                      {assignment.instructions || 'No specific instructions provided.'}
                    </p>
                  </div>
                </>
              )}
            </Card.Body>
          </Card>

          {/* Statistics Card */}
          <Card className="border-0 shadow-sm mt-4">
            <Card.Header className="bg-white d-flex align-items-center">
              <GradeIcon className="me-2" size={18} />
              <h6 className="mb-0">Submission Statistics</h6>
            </Card.Header>
            <Card.Body>
              <div className="text-center mb-3">
                <UsersIcon size={24} className="text-primary mb-2" />
                <div className="h4 text-primary mb-1">{stats.submitted}/{stats.totalStudents}</div>
                <small className="text-muted">Submitted</small>
              </div>
              
              <div className="text-center mb-3">
                <CheckCircleIcon size={24} className="text-success mb-2" />
                <div className="h4 text-success mb-1">{stats.graded}</div>
                <small className="text-muted">Graded</small>
              </div>
              
              <div className="text-center mb-3">
                <GradeIcon size={24} className="text-info mb-2" />
                <div className="h4 text-info mb-1">{stats.averageScore}</div>
                <small className="text-muted">Average Score</small>
              </div>
              
              <div className="text-center">
                <ProgressBar 
                  now={stats.submissionRate} 
                  label={`${stats.submissionRate}%`}
                  variant={stats.submissionRate >= 80 ? 'success' : stats.submissionRate >= 60 ? 'warning' : 'danger'}
                />
                <small className="text-muted">Submission Rate</small>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Main Content */}
        <Col lg={8}>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white">
              <Tabs activeKey={activeTab} onSelect={setActiveTab} className="border-0">
                <Tab 
                  eventKey="submissions" 
                  title={
                    <span className="d-flex align-items-center">
                      <FileTextIcon className="me-2" size={14} />
                      Submissions ({submissions.length})
                    </span>
                  }
                />
                <Tab 
                  eventKey="grades" 
                  title={
                    <span className="d-flex align-items-center">
                      <GradeIcon className="me-2" size={14} />
                      Grades
                    </span>
                  }
                />
                <Tab 
                  eventKey="analytics" 
                  title={
                    <span className="d-flex align-items-center">
                      <HistoryIcon className="me-2" size={14} />
                      Analytics
                    </span>
                  }
                />
              </Tabs>
            </Card.Header>
            <Card.Body className="p-0">
              {activeTab === 'submissions' && (
                <div className="table-responsive">
                  <Table className="mb-0" striped>
                    <thead className="bg-light">
                      <tr>
                        <th>Student</th>
                        <th>Submission Date</th>
                        <th>Status</th>
                        <th>Score</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {students.map(student => {
                        const submission = submissions.find(s => s.student_id === student.id);
                        return (
                          <tr key={student.id}>
                            <td>
                              <div className="d-flex align-items-center">
                                <UserIcon className="me-2 text-muted" size={14} />
                                <div>
                                  <div className="fw-semibold">{student.full_name}</div>
                                  <small className="text-muted">{student.admission_number}</small>
                                </div>
                              </div>
                            </td>
                            <td>
                              {submission?.submitted_at ? (
                                new Date(submission.submitted_at).toLocaleDateString()
                              ) : (
                                <span className="text-muted">-</span>
                              )}
                            </td>
                            <td>
                              <Badge 
                                bg={getStatusVariant(submission?.status || 'missing')}
                                className="d-flex align-items-center"
                              >
                                {getStatusIcon(submission?.status || 'missing')}
                                <span className="ms-1">
                                  {submission?.status ? submission.status.charAt(0).toUpperCase() + submission.status.slice(1) : 'Not Submitted'}
                                </span>
                              </Badge>
                            </td>
                            <td>
                              {submission?.score ? (
                                <strong className={submission.score >= (assignment.max_score * 0.7) ? 'text-success' : 'text-danger'}>
                                  {submission.score}/{assignment.max_score}
                                </strong>
                              ) : (
                                <span className="text-muted">-</span>
                              )}
                            </td>
                            <td>
                              {submission ? (
                                <Button
                                  variant="outline-primary"
                                  size="sm"
                                  onClick={() => handleGradeSubmission(submission)}
                                >
                                  <GradeIcon className="me-1" size={12} />
                                  {submission.score ? 'Regrade' : 'Grade'}
                                </Button>
                              ) : (
                                <span className="text-muted">No submission</span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </Table>
                </div>
              )}

              {activeTab === 'grades' && (
                <div className="p-4 text-center">
                  <GradeIcon size={48} className="text-muted mb-3" />
                  <h5 className="text-muted">Grade Distribution</h5>
                  <p className="text-muted">
                    Grade distribution chart and analytics will be displayed here.
                  </p>
                </div>
              )}

              {activeTab === 'analytics' && (
                <div className="p-4 text-center">
                  <HistoryIcon size={48} className="text-muted mb-3" />
                  <h5 className="text-muted">Assignment Analytics</h5>
                  <p className="text-muted">
                    Detailed analytics and performance metrics will be displayed here.
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Grade Submission Modal */}
      <Modal show={showGradeModal} onHide={() => setShowGradeModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title className="d-flex align-items-center">
            <GradeIcon className="me-2" size={20} />
            Grade Submission
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedSubmission && (
            <>
              <div className="mb-4">
                <h6>Student: {selectedSubmission.student_name}</h6>
                <p className="text-muted mb-0">
                  Submitted on: {new Date(selectedSubmission.submitted_at).toLocaleDateString()}
                </p>
              </div>

              <Form>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Score</Form.Label>
                      <InputGroup>
                        <Form.Control
                          type="number"
                          min="0"
                          max={assignment?.max_score}
                          value={gradeData.score}
                          onChange={(e) => setGradeData(prev => ({
                            ...prev,
                            score: e.target.value
                          }))}
                          placeholder="Enter score"
                        />
                        <InputGroup.Text>/{assignment?.max_score}</InputGroup.Text>
                      </InputGroup>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Percentage</Form.Label>
                      <Form.Control
                        type="text"
                        readOnly
                        value={gradeData.score ? ((gradeData.score / assignment.max_score) * 100).toFixed(1) + '%' : ''}
                        className="bg-light"
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Form.Group className="mb-3">
                  <Form.Label>Comments & Feedback</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    value={gradeData.comments}
                    onChange={(e) => setGradeData(prev => ({
                      ...prev,
                      comments: e.target.value
                    }))}
                    placeholder="Provide feedback to the student..."
                  />
                </Form.Group>
              </Form>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowGradeModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={submitGrade}
            disabled={grading || !gradeData.score}
          >
            {grading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Grading...
              </>
            ) : (
              <>
                <SaveIcon className="me-2" size={16} />
                Save Grade
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default AssignmentDetail;