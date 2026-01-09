import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, Modal, Alert, Tab, Nav } from 'react-bootstrap';

const Counseling = () => {
  const [showAppointmentModal, setShowAppointmentModal] = useState(false);
  const [showEmergencyModal, setShowEmergencyModal] = useState(false);

  const counselingServices = [
    {
      id: 1,
      name: 'Academic Counseling',
      description: 'Support with course selection, study skills, and academic planning',
      counselor: 'Mr. Academic Advisor',
      specialization: 'Educational Planning',
      availability: 'Mon, Wed, Fri 9:00 AM - 3:00 PM'
    },
    {
      id: 2,
      name: 'Personal Counseling',
      description: 'Confidential support for personal issues and emotional well-being',
      counselor: 'Ms. Personal Counselor',
      specialization: 'Mental Health',
      availability: 'Tue, Thu 9:00 AM - 4:00 PM'
    },
    {
      id: 3,
      name: 'Career Counseling',
      description: 'Guidance on career choices, university applications, and future planning',
      counselor: 'Mrs. Career Advisor',
      specialization: 'Career Development',
      availability: 'Mon-Fri 10:00 AM - 2:00 PM'
    },
    {
      id: 4,
      name: 'Peer Counseling',
      description: 'Support from trained student peers for everyday challenges',
      counselor: 'Peer Counselors',
      specialization: 'Student Support',
      availability: 'Daily during lunch breaks'
    }
  ];

  const resources = [
    {
      title: 'Study Skills Guide',
      type: 'PDF Resource',
      description: 'Effective study techniques and time management strategies',
      link: '/resources/study-skills'
    },
    {
      title: 'Stress Management',
      type: 'Video Series',
      description: 'Techniques for managing academic and personal stress',
      link: '/resources/stress-management'
    },
    {
      title: 'Career Assessment',
      type: 'Online Tool',
      description: 'Interactive assessment to explore career interests',
      link: '/resources/career-assessment'
    },
    {
      title: 'Mental Health Resources',
      type: 'Resource List',
      description: 'Local and online mental health support services',
      link: '/resources/mental-health'
    }
  ];

  const emergencyContacts = [
    {
      name: 'Crisis Hotline',
      number: '1190',
      description: 'National Suicide Prevention Hotline',
      available: '24/7'
    },
    {
      name: 'Mental Health Emergency',
      number: '+254 720 123 456',
      description: 'Immediate mental health support',
      available: '24/7'
    },
    {
      name: 'Child Helpline',
      number: '116',
      description: 'Free counseling for children and young adults',
      available: '24/7'
    },
    {
      name: 'School Counselor Emergency',
      number: '+254 711 123 459',
      description: 'After-hours school counselor contact',
      available: '24/7'
    }
  ];

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Counseling & Support Services</h1>
            <p className="lead">Your well-being is our priority. We're here to help you thrive.</p>
          </div>

          <Alert variant="info" className="mb-4">
            <Alert.Heading>Confidential & Supportive Environment</Alert.Heading>
            All counseling services are completely confidential. Our qualified counselors 
            provide a safe, non-judgmental space for you to discuss any concerns or challenges.
          </Alert>

          {/* Emergency Banner */}
          <Card className="mb-4 border-danger">
            <Card.Body className="bg-danger text-white text-center">
              <h5 className="mb-3">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                Need Immediate Help?
              </h5>
              <p className="mb-3">
                If you or someone you know is in crisis or needs immediate support, 
                don't hesitate to reach out.
              </p>
              <Button 
                variant="light" 
                size="lg"
                onClick={() => setShowEmergencyModal(true)}
              >
                Get Emergency Help Now
              </Button>
            </Card.Body>
          </Card>

          <Tab.Container defaultActiveKey="services">
            <Card>
              <Card.Header>
                <Nav variant="tabs" className="card-header-tabs">
                  <Nav.Item>
                    <Nav.Link eventKey="services">Counseling Services</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="resources">Resources</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="selfhelp">Self-Help Tools</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="faq">FAQ</Nav.Link>
                  </Nav.Item>
                </Nav>
              </Card.Header>
              <Card.Body>
                <Tab.Content>
                  {/* Services Tab */}
                  <Tab.Pane eventKey="services">
                    <Row>
                      {counselingServices.map(service => (
                        <Col md={6} key={service.id} className="mb-4">
                          <Card className="h-100">
                            <Card.Body>
                              <h5 className="card-title">{service.name}</h5>
                              <p className="card-text">{service.description}</p>
                              <div className="mb-3">
                                <p className="mb-1">
                                  <strong>Counselor:</strong> {service.counselor}
                                </p>
                                <p className="mb-1">
                                  <strong>Specialization:</strong> {service.specialization}
                                </p>
                                <p className="mb-0">
                                  <strong>Availability:</strong> {service.availability}
                                </p>
                              </div>
                            </Card.Body>
                            <Card.Footer>
                              <Button 
                                variant="primary"
                                onClick={() => setShowAppointmentModal(true)}
                              >
                                Schedule Appointment
                              </Button>
                            </Card.Footer>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>

                  {/* Resources Tab */}
                  <Tab.Pane eventKey="resources">
                    <Row>
                      {resources.map((resource, index) => (
                        <Col md={6} key={index} className="mb-3">
                          <Card>
                            <Card.Body>
                              <h6>{resource.title}</h6>
                              <Badge bg="secondary" className="mb-2">{resource.type}</Badge>
                              <p className="card-text">{resource.description}</p>
                              <Button variant="outline-primary" size="sm">
                                Access Resource
                              </Button>
                            </Card.Body>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>

                  {/* Self-Help Tools Tab */}
                  <Tab.Pane eventKey="selfhelp">
                    <Row>
                      <Col md={6}>
                        <Card className="mb-4">
                          <Card.Header>
                            <h6 className="mb-0">Mood Tracker</h6>
                          </Card.Header>
                          <Card.Body>
                            <p>Track your daily mood and identify patterns:</p>
                            <Form>
                              <Form.Group className="mb-3">
                                <Form.Label>How are you feeling today?</Form.Label>
                                <Form.Select>
                                  <option>Excellent 😊</option>
                                  <option>Good 🙂</option>
                                  <option>Neutral 😐</option>
                                  <option>Not Great 😕</option>
                                  <option>Difficult 😔</option>
                                </Form.Select>
                              </Form.Group>
                              <Button variant="outline-primary">
                                Save Entry
                              </Button>
                            </Form>
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col md={6}>
                        <Card className="mb-4">
                          <Card.Header>
                            <h6 className="mb-0">Stress Management Exercises</h6>
                          </Card.Header>
                          <Card.Body>
                            <ul className="list-unstyled">
                              <li className="mb-2">
                                <Button variant="outline-info" size="sm" className="w-100 mb-1">
                                  Breathing Exercise (5 mins)
                                </Button>
                              </li>
                              <li className="mb-2">
                                <Button variant="outline-success" size="sm" className="w-100 mb-1">
                                  Guided Meditation (10 mins)
                                </Button>
                              </li>
                              <li className="mb-2">
                                <Button variant="outline-warning" size="sm" className="w-100 mb-1">
                                  Quick Relaxation (3 mins)
                                </Button>
                              </li>
                            </ul>
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>
                  </Tab.Pane>

                  {/* FAQ Tab */}
                  <Tab.Pane eventKey="faq">
                    <h6>Frequently Asked Questions</h6>
                    <div className="mb-4">
                      <h6>Is counseling confidential?</h6>
                      <p>
                        Yes, all counseling sessions are completely confidential. Information is 
                        only shared with your permission or in specific situations where there is 
                        risk of harm to yourself or others.
                      </p>
                    </div>
                    <div className="mb-4">
                      <h6>How do I schedule an appointment?</h6>
                      <p>
                        You can schedule through this portal, email the counseling department, 
                        or visit the counseling office in person. Emergency appointments are 
                        available for urgent situations.
                      </p>
                    </div>
                    <div className="mb-4">
                      <h6>What if I need help after hours?</h6>
                      <p>
                        We provide 24/7 emergency contact numbers for urgent situations. 
                        For non-urgent matters, you can leave a message and we'll respond 
                        the next business day.
                      </p>
                    </div>
                    <div className="mb-4">
                      <h6>Is there a cost for counseling services?</h6>
                      <p>
                        No, all counseling services are provided free of charge to 
                        Delvok Academy students.
                      </p>
                    </div>
                  </Tab.Pane>
                </Tab.Content>
              </Card.Body>
            </Card>
          </Tab.Container>

          {/* Counseling Principles */}
          <Card className="mt-4">
            <Card.Header>
              <h5 className="mb-0">Our Counseling Approach</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={4}>
                  <div className="text-center mb-3">
                    <i className="bi bi-shield-check text-primary" style={{ fontSize: '2rem' }}></i>
                    <h6 className="mt-2">Confidential</h6>
                    <p className="small">Your privacy is protected at all times</p>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center mb-3">
                    <i className="bi bi-heart text-success" style={{ fontSize: '2rem' }}></i>
                    <h6 className="mt-2">Supportive</h6>
                    <p className="small">Non-judgmental, empathetic support</p>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center mb-3">
                    <i className="bi bi-lightbulb text-warning" style={{ fontSize: '2rem' }}></i>
                    <h6 className="mt-2">Empowering</h6>
                    <p className="small">Helping you develop coping strategies</p>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Appointment Modal */}
          <Modal show={showAppointmentModal} onHide={() => setShowAppointmentModal(false)}>
            <Modal.Header closeButton>
              <Modal.Title>Schedule Counseling Appointment</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Select Service Type</Form.Label>
                  <Form.Select required>
                    <option value="">Choose service...</option>
                    {counselingServices.map(service => (
                      <option key={service.id} value={service.name}>
                        {service.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Preferred Date</Form.Label>
                  <Form.Control type="date" required />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Preferred Time</Form.Label>
                  <Form.Select required>
                    <option value="">Select time...</option>
                    <option>9:00 AM</option>
                    <option>10:00 AM</option>
                    <option>11:00 AM</option>
                    <option>2:00 PM</option>
                    <option>3:00 PM</option>
                    <option>4:00 PM</option>
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Brief Description of Concern</Form.Label>
                  <Form.Control as="textarea" rows={3} placeholder="Optional - helps us prepare for your session" />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    label="I understand this service is confidential"
                    required
                  />
                </Form.Group>
              </Form>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={() => setShowAppointmentModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={() => setShowAppointmentModal(false)}>
                Schedule Appointment
              </Button>
            </Modal.Footer>
          </Modal>

          {/* Emergency Help Modal */}
          <Modal show={showEmergencyModal} onHide={() => setShowEmergencyModal(false)} size="lg">
            <Modal.Header closeButton className="bg-danger text-white">
              <Modal.Title>Emergency Support Contacts</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <Alert variant="warning">
                <Alert.Heading>Immediate Assistance Available</Alert.Heading>
                If you are in immediate danger or experiencing a mental health crisis, 
                please call emergency services first.
              </Alert>

              <Row>
                {emergencyContacts.map((contact, index) => (
                  <Col md={6} key={index} className="mb-3">
                    <Card>
                      <Card.Body>
                        <h6>{contact.name}</h6>
                        <h5 className="text-primary">{contact.number}</h5>
                        <p className="small mb-1">{contact.description}</p>
                        <Badge bg="success">{contact.available}</Badge>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>

              <div className="text-center mt-4">
                <Button variant="danger" size="lg">
                  <i className="bi bi-telephone-fill me-2"></i>
                  Call Emergency Services: 999
                </Button>
              </div>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={() => setShowEmergencyModal(false)}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
        </Col>
      </Row>
    </Container>
  );
};

export default Counseling;