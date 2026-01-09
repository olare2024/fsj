import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Nav, Tab, Badge, Button, ListGroup } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Resources = () => {
  const { currentUser } = useAuth();
  const [resources, setResources] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResources = async () => {
      setLoading(true);
      
      const mockResources = {
        cbc: [
          {
            id: 1,
            title: 'CBC Grade 1-3 Learning Materials',
            description: 'Complete set of learning materials for lower primary',
            type: 'package',
            subjects: ['Literacy', 'Kiswahili', 'Mathematics', 'Environmental'],
            updated: '2024-01-20'
          },
          {
            id: 2,
            title: 'Competency Based Assessment Tools',
            description: 'Assessment rubrics and tools for CBC evaluation',
            type: 'assessment',
            subjects: ['All Subjects'],
            updated: '2024-01-18'
          }
        ],
        cambridge: [
          {
            id: 1,
            title: 'IGCSE Past Papers Collection',
            description: 'Complete collection of IGCSE past papers 2018-2023',
            type: 'exams',
            subjects: ['Mathematics', 'Physics', 'Chemistry', 'Biology'],
            updated: '2024-01-22'
          },
          {
            id: 2,
            title: 'A-Level Syllabus Resources',
            description: 'Detailed syllabus and teaching resources for A-Level',
            type: 'syllabus',
            subjects: ['Mathematics', 'Physics', 'Chemistry'],
            updated: '2024-01-15'
          }
        ],
        teaching: [
          {
            id: 1,
            title: 'Lesson Plan Templates',
            description: 'Professional lesson plan templates for all subjects',
            type: 'template',
            subjects: ['All Subjects'],
            updated: '2024-01-10'
          },
          {
            id: 2,
            title: 'Interactive Teaching Tools',
            description: 'Digital tools and apps for interactive classroom teaching',
            type: 'tools',
            subjects: ['All Subjects'],
            updated: '2024-01-08'
          }
        ],
        student: [
          {
            id: 1,
            title: 'Study Skills Guide',
            description: 'Comprehensive guide to effective study techniques',
            type: 'guide',
            subjects: ['All Subjects'],
            updated: '2024-01-25'
          },
          {
            id: 2,
            title: 'Revision Timetable Templates',
            description: 'Customizable revision timetable templates',
            type: 'template',
            subjects: ['All Subjects'],
            updated: '2024-01-12'
          }
        ]
      };

      setTimeout(() => {
        setResources(mockResources);
        setLoading(false);
      }, 1000);
    };

    fetchResources();
  }, []);

  const getTypeBadge = (type) => {
    const variants = {
      'package': 'primary',
      'assessment': 'info',
      'exams': 'warning',
      'syllabus': 'success',
      'template': 'secondary',
      'tools': 'dark',
      'guide': 'danger'
    };
    return <Badge bg={variants[type] || 'secondary'}>{type}</Badge>;
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading resources...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2>Learning Resources</h2>
            <Button variant="primary">
              <i className="bi bi-plus-circle"></i> Suggest Resource
            </Button>
          </div>

          <Tab.Container defaultActiveKey="cbc">
            <Card>
              <Card.Header>
                <Nav variant="tabs" className="card-header-tabs">
                  <Nav.Item>
                    <Nav.Link eventKey="cbc">
                      <i className="bi bi-journal-bookmark"></i> CBC Resources
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="cambridge">
                      <i className="bi bi-globe"></i> Cambridge Resources
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="teaching">
                      <i className="bi bi-easel"></i> Teaching Resources
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="student">
                      <i className="bi bi-mortarboard"></i> Student Resources
                    </Nav.Link>
                  </Nav.Item>
                </Nav>
              </Card.Header>
              <Card.Body>
                <Tab.Content>
                  {/* CBC Resources */}
                  <Tab.Pane eventKey="cbc">
                    <Row>
                      {resources.cbc?.map(resource => (
                        <Col md={6} key={resource.id} className="mb-4">
                          <Card className="h-100">
                            <Card.Header className="d-flex justify-content-between align-items-center">
                              {getTypeBadge(resource.type)}
                              <Badge bg="light" text="dark">
                                Updated: {resource.updated}
                              </Badge>
                            </Card.Header>
                            <Card.Body>
                              <h6 className="card-title">{resource.title}</h6>
                              <p className="card-text">{resource.description}</p>
                              <div className="mb-3">
                                <strong>Subjects:</strong>
                                <div className="mt-1">
                                  {resource.subjects.map((subject, idx) => (
                                    <Badge key={idx} bg="outline-primary" className="me-1 mb-1">
                                      {subject}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            </Card.Body>
                            <Card.Footer>
                              <div className="d-flex gap-2">
                                <Button variant="primary" size="sm">
                                  <i className="bi bi-eye"></i> View
                                </Button>
                                <Button variant="outline-success" size="sm">
                                  <i className="bi bi-download"></i> Download
                                </Button>
                              </div>
                            </Card.Footer>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>

                  {/* Cambridge Resources */}
                  <Tab.Pane eventKey="cambridge">
                    <Row>
                      {resources.cambridge?.map(resource => (
                        <Col md={6} key={resource.id} className="mb-4">
                          <Card className="h-100">
                            <Card.Header className="d-flex justify-content-between align-items-center">
                              {getTypeBadge(resource.type)}
                              <Badge bg="light" text="dark">
                                Updated: {resource.updated}
                              </Badge>
                            </Card.Header>
                            <Card.Body>
                              <h6 className="card-title">{resource.title}</h6>
                              <p className="card-text">{resource.description}</p>
                              <div className="mb-3">
                                <strong>Subjects:</strong>
                                <div className="mt-1">
                                  {resource.subjects.map((subject, idx) => (
                                    <Badge key={idx} bg="outline-info" className="me-1 mb-1">
                                      {subject}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            </Card.Body>
                            <Card.Footer>
                              <div className="d-flex gap-2">
                                <Button variant="primary" size="sm">
                                  <i className="bi bi-eye"></i> View
                                </Button>
                                <Button variant="outline-success" size="sm">
                                  <i className="bi bi-download"></i> Download
                                </Button>
                              </div>
                            </Card.Footer>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>

                  {/* Teaching Resources */}
                  <Tab.Pane eventKey="teaching">
                    <Row>
                      {resources.teaching?.map(resource => (
                        <Col md={6} key={resource.id} className="mb-4">
                          <Card className="h-100">
                            <Card.Header className="d-flex justify-content-between align-items-center">
                              {getTypeBadge(resource.type)}
                              <Badge bg="light" text="dark">
                                Updated: {resource.updated}
                              </Badge>
                            </Card.Header>
                            <Card.Body>
                              <h6 className="card-title">{resource.title}</h6>
                              <p className="card-text">{resource.description}</p>
                              <div className="mb-3">
                                <strong>Subjects:</strong>
                                <div className="mt-1">
                                  {resource.subjects.map((subject, idx) => (
                                    <Badge key={idx} bg="outline-success" className="me-1 mb-1">
                                      {subject}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            </Card.Body>
                            <Card.Footer>
                              <div className="d-flex gap-2">
                                <Button variant="primary" size="sm">
                                  <i className="bi bi-eye"></i> View
                                </Button>
                                <Button variant="outline-success" size="sm">
                                  <i className="bi bi-download"></i> Download
                                </Button>
                              </div>
                            </Card.Footer>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>

                  {/* Student Resources */}
                  <Tab.Pane eventKey="student">
                    <Row>
                      {resources.student?.map(resource => (
                        <Col md={6} key={resource.id} className="mb-4">
                          <Card className="h-100">
                            <Card.Header className="d-flex justify-content-between align-items-center">
                              {getTypeBadge(resource.type)}
                              <Badge bg="light" text="dark">
                                Updated: {resource.updated}
                              </Badge>
                            </Card.Header>
                            <Card.Body>
                              <h6 className="card-title">{resource.title}</h6>
                              <p className="card-text">{resource.description}</p>
                              <div className="mb-3">
                                <strong>Subjects:</strong>
                                <div className="mt-1">
                                  {resource.subjects.map((subject, idx) => (
                                    <Badge key={idx} bg="outline-warning" className="me-1 mb-1">
                                      {subject}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            </Card.Body>
                            <Card.Footer>
                              <div className="d-flex gap-2">
                                <Button variant="primary" size="sm">
                                  <i className="bi bi-eye"></i> View
                                </Button>
                                <Button variant="outline-success" size="sm">
                                  <i className="bi bi-download"></i> Download
                                </Button>
                              </div>
                            </Card.Footer>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>
                </Tab.Content>
              </Card.Body>
            </Card>
          </Tab.Container>

          {/* Quick Links */}
          <Row className="mt-4">
            <Col md={4}>
              <Card>
                <Card.Header>
                  <h6 className="mb-0">Quick Links</h6>
                </Card.Header>
                <Card.Body>
                  <ListGroup variant="flush">
                    <ListGroup.Item action>
                      <i className="bi bi-link-45deg me-2"></i>
                      Kenya Institute of Curriculum Development
                    </ListGroup.Item>
                    <ListGroup.Item action>
                      <i className="bi bi-link-45deg me-2"></i>
                      Cambridge Assessment International Education
                    </ListGroup.Item>
                    <ListGroup.Item action>
                      <i className="bi bi-link-45deg me-2"></i>
                      Teachers Service Commission
                    </ListGroup.Item>
                    <ListGroup.Item action>
                      <i className="bi bi-link-45deg me-2"></i>
                      Ministry of Education Kenya
                    </ListGroup.Item>
                  </ListGroup>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default Resources;