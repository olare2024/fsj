import React, { useState, useEffect } from 'react';
import { 
  Container, Row, Col, Card, Table, Badge, Button, Form, 
  Modal, Alert, ProgressBar, InputGroup, Dropdown 
} from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Assignments = () => {
  const { currentUser } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [alert, setAlert] = useState({ show: false, message: '', type: '' });
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('dueDate');

  // New assignment form state
  const [newAssignment, setNewAssignment] = useState({
    title: '',
    subject: '',
    dueDate: '',
    description: '',
    totalMarks: '',
    attachments: []
  });

  useEffect(() => {
    fetchAssignments();
  }, [currentUser.role]);

  const fetchAssignments = async () => {
    setLoading(true);
    
    const mockAssignments = [
      {
        id: 1,
        title: 'Mathematics Problem Set',
        subject: 'Mathematics',
        dueDate: '2024-01-25',
        status: currentUser.role === 'student' ? 'submitted' : 'graded',
        marks: '18/20',
        totalMarks: 20,
        description: 'Complete problems 1-20 from chapter 4. Show all your work and calculations.',
        submittedDate: '2024-01-24',
        grade: 'A',
        feedback: 'Excellent work! Well organized and detailed solutions.',
        attachments: ['worksheet.pdf'],
        submissions: 25,
        graded: 18
      },
      {
        id: 2,
        title: 'English Essay - Climate Change',
        subject: 'English',
        dueDate: '2024-01-28',
        status: currentUser.role === 'student' ? 'pending' : 'submitted',
        marks: '-',
        totalMarks: 25,
        description: 'Write a 500-word essay discussing the impacts of climate change and potential solutions.',
        submittedDate: null,
        grade: null,
        feedback: null,
        attachments: ['essay_guidelines.pdf'],
        submissions: 15,
        graded: 0
      },
      {
        id: 3,
        title: 'Science Project - Renewable Energy',
        subject: 'Science',
        dueDate: '2024-02-01',
        status: 'pending',
        marks: '-',
        totalMarks: 30,
        description: 'Group project on renewable energy sources. Create a presentation and research paper.',
        submittedDate: null,
        grade: null,
        feedback: null,
        attachments: ['project_rubric.pdf', 'research_guidelines.docx'],
        submissions: 0,
        graded: 0
      },
      {
        id: 4,
        title: 'History Research Paper',
        subject: 'History',
        dueDate: '2024-01-20',
        status: 'overdue',
        marks: '-',
        totalMarks: 25,
        description: 'Research paper on Ancient Civilizations. Minimum 1000 words with proper citations.',
        submittedDate: null,
        grade: null,
        feedback: null,
        attachments: ['research_topics.pdf'],
        submissions: 20,
        graded: 15
      },
    ];

    setTimeout(() => {
      setAssignments(mockAssignments);
      setLoading(false);
    }, 1000);
  };

  const getStatusBadge = (status) => {
    switch(status) {
      case 'submitted': return <Badge bg="info">Submitted</Badge>;
      case 'graded': return <Badge bg="success">Graded</Badge>;
      case 'pending': return <Badge bg="warning">Pending</Badge>;
      case 'overdue': return <Badge bg="danger">Overdue</Badge>;
      default: return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  const getGradeBadge = (grade) => {
    if (!grade) return null;
    
    const gradeColors = {
      'A': 'success',
      'B': 'primary',
      'C': 'warning',
      'D': 'danger',
      'F': 'dark'
    };
    
    return <Badge bg={gradeColors[grade] || 'secondary'}>{grade}</Badge>;
  };

  const handleCreateAssignment = () => {
    // Validate form
    if (!newAssignment.title || !newAssignment.subject || !newAssignment.dueDate) {
      showAlert('Please fill in all required fields', 'danger');
      return;
    }

    const assignment = {
      id: assignments.length + 1,
      ...newAssignment,
      status: 'pending',
      submissions: 0,
      graded: 0
    };

    setAssignments(prev => [assignment, ...prev]);
    setShowCreateModal(false);
    setNewAssignment({
      title: '',
      subject: '',
      dueDate: '',
      description: '',
      totalMarks: '',
      attachments: []
    });
    showAlert('Assignment created successfully!', 'success');
  };

  const handleSubmitAssignment = (assignment) => {
    const updatedAssignments = assignments.map(a => 
      a.id === assignment.id ? { ...a, status: 'submitted', submittedDate: new Date().toISOString().split('T')[0] } : a
    );
    
    setAssignments(updatedAssignments);
    setShowSubmitModal(false);
    showAlert('Assignment submitted successfully!', 'success');
  };

  const showAlert = (message, type) => {
    setAlert({ show: true, message, type });
    setTimeout(() => setAlert({ show: false, message: '', type: '' }), 5000);
  };

  const isOverdue = (dueDate) => {
    return new Date(dueDate) < new Date();
  };

  const calculateProgress = (assignment) => {
    if (assignment.submissions === 0) return 0;
    return Math.round((assignment.graded / assignment.submissions) * 100);
  };

  // Filter and sort assignments
  const filteredAndSortedAssignments = assignments
    .filter(assignment => {
      if (filter === 'all') return true;
      if (filter === 'overdue') return isOverdue(assignment.dueDate) && assignment.status === 'pending';
      return assignment.status === filter;
    })
    .filter(assignment => 
      assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      assignment.subject.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch(sortBy) {
        case 'dueDate':
          return new Date(a.dueDate) - new Date(b.dueDate);
        case 'title':
          return a.title.localeCompare(b.title);
        case 'subject':
          return a.subject.localeCompare(b.subject);
        case 'status':
          return a.status.localeCompare(b.status);
        default:
          return 0;
      }
    });

  const assignmentStats = {
    total: assignments.length,
    completed: assignments.filter(a => a.status === 'graded' || a.status === 'submitted').length,
    pending: assignments.filter(a => a.status === 'pending' && !isOverdue(a.dueDate)).length,
    overdue: assignments.filter(a => a.status === 'pending' && isOverdue(a.dueDate)).length,
    averageScore: '85%'
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
            <span className="visually-hidden">Loading assignments...</span>
          </div>
          <p className="mt-3 text-muted">Loading assignments...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      {/* Alert */}
      {alert.show && (
        <Alert variant={alert.type} dismissible onClose={() => setAlert({ show: false, message: '', type: '' })}>
          {alert.message}
        </Alert>
      )}

      <Row>
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 className="mb-1">Assignments</h2>
              <p className="text-muted mb-0">
                {currentUser.role === 'student' ? 'Manage your assignments' : 'Manage class assignments'}
              </p>
            </div>
            {currentUser.role === 'teacher' && (
              <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                <i className="bi bi-plus-circle me-2"></i> Create Assignment
              </Button>
            )}
          </div>

          {/* Filters and Search */}
          <Card className="mb-4">
            <Card.Body>
              <Row className="g-3">
                <Col md={4}>
                  <InputGroup>
                    <InputGroup.Text>
                      <i className="bi bi-search"></i>
                    </InputGroup.Text>
                    <Form.Control
                      placeholder="Search assignments..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </InputGroup>
                </Col>
                <Col md={3}>
                  <Form.Select 
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                  >
                    <option value="all">All Assignments</option>
                    <option value="pending">Pending</option>
                    <option value="submitted">Submitted</option>
                    <option value="graded">Graded</option>
                    <option value="overdue">Overdue</option>
                  </Form.Select>
                </Col>
                <Col md={3}>
                  <Form.Select 
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="dueDate">Sort by Due Date</option>
                    <option value="title">Sort by Title</option>
                    <option value="subject">Sort by Subject</option>
                    <option value="status">Sort by Status</option>
                  </Form.Select>
                </Col>
                <Col md={2}>
                  <Button 
                    variant="outline-secondary" 
                    onClick={fetchAssignments}
                    disabled={loading}
                  >
                    <i className="bi bi-arrow-clockwise"></i>
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Assignments Table */}
          <Card>
            <Card.Header>
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">
                  {currentUser.role === 'student' ? 'My Assignments' : 'Class Assignments'}
                  <Badge bg="light" text="dark" className="ms-2">
                    {filteredAndSortedAssignments.length}
                  </Badge>
                </h5>
              </div>
            </Card.Header>
            <Card.Body className="p-0">
              <Table responsive striped hover className="mb-0">
                <thead className="bg-light">
                  <tr>
                    <th>Assignment</th>
                    <th>Subject</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th>Marks/Grade</th>
                    {currentUser.role === 'teacher' && (
                      <>
                        <th>Submissions</th>
                        <th>Grading Progress</th>
                      </>
                    )}
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAndSortedAssignments.map((assignment) => (
                    <tr key={assignment.id}>
                      <td>
                        <div>
                          <strong className="d-block">{assignment.title}</strong>
                          <small className="text-muted">{assignment.description}</small>
                          {assignment.attachments.length > 0 && (
                            <div className="mt-1">
                              <small>
                                <i className="bi bi-paperclip me-1"></i>
                                {assignment.attachments.length} file(s)
                              </small>
                            </div>
                          )}
                        </div>
                      </td>
                      <td>
                        <Badge bg="outline-primary" text="dark">
                          {assignment.subject}
                        </Badge>
                      </td>
                      <td>
                        <div>
                          {assignment.dueDate}
                          {isOverdue(assignment.dueDate) && assignment.status === 'pending' && (
                            <div>
                              <small className="text-danger">
                                <i className="bi bi-exclamation-triangle me-1"></i>
                                Overdue
                              </small>
                            </div>
                          )}
                        </div>
                      </td>
                      <td>{getStatusBadge(assignment.status)}</td>
                      <td>
                        {assignment.marks !== '-' ? (
                          <div>
                            <Badge bg="success">{assignment.marks}</Badge>
                            {assignment.grade && (
                              <div className="mt-1">
                                {getGradeBadge(assignment.grade)}
                              </div>
                            )}
                          </div>
                        ) : (
                          '-'
                        )}
                      </td>
                      {currentUser.role === 'teacher' && (
                        <>
                          <td>
                            <div className="text-center">
                              <strong>{assignment.submissions}</strong>
                              <small className="text-muted d-block">students</small>
                            </div>
                          </td>
                          <td style={{ minWidth: '120px' }}>
                            <div className="d-flex align-items-center">
                              <ProgressBar 
                                now={calculateProgress(assignment)} 
                                variant={calculateProgress(assignment) === 100 ? 'success' : 'primary'}
                                style={{ flex: 1 }}
                              />
                              <small className="ms-2">{calculateProgress(assignment)}%</small>
                            </div>
                            <small className="text-muted">
                              {assignment.graded}/{assignment.submissions} graded
                            </small>
                          </td>
                        </>
                      )}
                      <td>
                        <Dropdown>
                          <Dropdown.Toggle variant="outline-primary" size="sm" id="dropdown-basic">
                            Actions
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            <Dropdown.Item>
                              <i className="bi bi-eye me-2"></i>
                              View Details
                            </Dropdown.Item>
                            
                            {currentUser.role === 'student' ? (
                              assignment.status === 'pending' ? (
                                <Dropdown.Item 
                                  onClick={() => {
                                    setSelectedAssignment(assignment);
                                    setShowSubmitModal(true);
                                  }}
                                >
                                  <i className="bi bi-upload me-2"></i>
                                  Submit
                                </Dropdown.Item>
                              ) : (
                                <Dropdown.Item>
                                  <i className="bi bi-download me-2"></i>
                                  Download
                                </Dropdown.Item>
                              )
                            ) : (
                              <>
                                <Dropdown.Item>
                                  <i className="bi bi-list-check me-2"></i>
                                  Grade Submissions
                                </Dropdown.Item>
                                <Dropdown.Item>
                                  <i className="bi bi-pencil me-2"></i>
                                  Edit
                                </Dropdown.Item>
                              </>
                            )}
                          </Dropdown.Menu>
                        </Dropdown>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              
              {filteredAndSortedAssignments.length === 0 && (
                <div className="text-center py-5">
                  <i className="bi bi-inbox display-1 text-muted"></i>
                  <p className="text-muted mt-3">No assignments found</p>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Statistics Card */}
          {currentUser.role === 'student' && (
            <Row className="mt-4">
              <Col lg={8}>
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Assignment Statistics</h6>
                  </Card.Header>
                  <Card.Body>
                    <Row className="text-center">
                      <Col md={3} className="border-end">
                        <h4 className="text-primary">{assignmentStats.total}</h4>
                        <small className="text-muted">Total</small>
                      </Col>
                      <Col md={3} className="border-end">
                        <h4 className="text-success">{assignmentStats.completed}</h4>
                        <small className="text-muted">Completed</small>
                      </Col>
                      <Col md={3} className="border-end">
                        <h4 className="text-warning">{assignmentStats.pending}</h4>
                        <small className="text-muted">Pending</small>
                      </Col>
                      <Col md={3}>
                        <h4 className="text-danger">{assignmentStats.overdue}</h4>
                        <small className="text-muted">Overdue</small>
                      </Col>
                    </Row>
                    <div className="mt-3">
                      <div className="d-flex justify-content-between mb-1">
                        <span>Overall Progress</span>
                        <strong>{assignmentStats.averageScore}</strong>
                      </div>
                      <ProgressBar 
                        now={85} 
                        variant="success" 
                        style={{ height: '8px' }}
                      />
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}
        </Col>
      </Row>

      {/* Create Assignment Modal */}
      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create New Assignment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Title *</Form.Label>
                  <Form.Control
                    type="text"
                    value={newAssignment.title}
                    onChange={(e) => setNewAssignment({...newAssignment, title: e.target.value})}
                    placeholder="Enter assignment title"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Subject *</Form.Label>
                  <Form.Control
                    type="text"
                    value={newAssignment.subject}
                    onChange={(e) => setNewAssignment({...newAssignment, subject: e.target.value})}
                    placeholder="Enter subject"
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Due Date *</Form.Label>
                  <Form.Control
                    type="date"
                    value={newAssignment.dueDate}
                    onChange={(e) => setNewAssignment({...newAssignment, dueDate: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Total Marks</Form.Label>
                  <Form.Control
                    type="number"
                    value={newAssignment.totalMarks}
                    onChange={(e) => setNewAssignment({...newAssignment, totalMarks: e.target.value})}
                    placeholder="Enter total marks"
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={newAssignment.description}
                onChange={(e) => setNewAssignment({...newAssignment, description: e.target.value})}
                placeholder="Enter assignment description and instructions..."
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateAssignment}>
            Create Assignment
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Submit Assignment Modal */}
      <Modal show={showSubmitModal} onHide={() => setShowSubmitModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Submit Assignment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedAssignment && (
            <>
              <h6>{selectedAssignment.title}</h6>
              <p className="text-muted">{selectedAssignment.description}</p>
              
              <Form.Group className="mb-3">
                <Form.Label>Upload Files</Form.Label>
                <Form.Control type="file" multiple />
                <Form.Text className="text-muted">
                  You can upload multiple files (PDF, DOC, PPT, images)
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Additional Comments</Form.Label>
                <Form.Control as="textarea" rows={3} placeholder="Any additional comments..." />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowSubmitModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={() => handleSubmitAssignment(selectedAssignment)}>
            Submit Assignment
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Assignments;