import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Table, Form, Modal, Badge } from 'react-bootstrap';

const StudentServices = () => {
  const [showAppointmentModal, setShowAppointmentModal] = useState(false);
  const [selectedService, setSelectedService] = useState('');

  const services = [
    {
      id: 1,
      name: 'Academic Support',
      description: 'Tutoring, study skills workshops, and academic resource center',
      contact: 'academicsupport@delvok.ac.ke',
      hours: 'Mon-Fri 8:00 AM - 4:00 PM',
      location: 'Learning Resource Center',
      appointmentRequired: true
    },
    {
      id: 2,
      name: 'Career Guidance',
      description: 'University applications, career counseling, and internship opportunities',
      contact: 'careers@delvok.ac.ke',
      hours: 'Mon-Fri 9:00 AM - 3:00 PM',
      location: 'Career Center',
      appointmentRequired: true
    },
    {
      id: 3,
      name: 'Health Services',
      description: 'Medical care, health education, and wellness programs',
      contact: 'health@delvok.ac.ke',
      hours: '24/7 Emergency, Mon-Fri 8:00 AM - 5:00 PM',
      location: 'Health Center',
      appointmentRequired: false
    },
    {
      id: 4,
      name: 'IT Support',
      description: 'Technical assistance, device support, and digital resources',
      contact: 'itsupport@delvok.ac.ke',
      hours: 'Mon-Fri 7:30 AM - 5:30 PM',
      location: 'IT Department',
      appointmentRequired: false
    },
    {
      id: 5,
      name: 'Library Services',
      description: 'Research assistance, book loans, and study spaces',
      contact: 'library@delvok.ac.ke',
      hours: 'Mon-Sat 7:00 AM - 9:00 PM',
      location: 'Main Library',
      appointmentRequired: false
    },
    {
      id: 6,
      name: 'Student Affairs',
      description: 'Student activities, leadership programs, and general support',
      contact: 'studentaffairs@delvok.ac.ke',
      hours: 'Mon-Fri 8:00 AM - 5:00 PM',
      location: 'Administration Building',
      appointmentRequired: false
    }
  ];

  const quickLinks = [
    {
      title: 'Request Transcript',
      description: 'Official academic records',
      link: '/documents/transcript'
    },
    {
      title: 'Report an Issue',
      description: 'Maintenance or facility problems',
      link: '/support/issues'
    },
    {
      title: 'Book Facilities',
      description: 'Reserve study rooms or event spaces',
      link: '/facilities/booking'
    },
    {
      title: 'Student ID Replacement',
      description: 'Lost or damaged student ID',
      link: '/services/id-replacement'
    }
  ];

  const announcements = [
    {
      id: 1,
      title: 'Extended Library Hours',
      content: 'Library will remain open until 10:00 PM during exam period',
      date: '2024-02-01',
      priority: 'high'
    },
    {
      id: 2,
      title: 'Career Fair 2024',
      content: 'Annual career fair scheduled for March 15th. Register now!',
      date: '2024-01-28',
      priority: 'medium'
    },
    {
      id: 3,
      title: 'New Tutoring Schedule',
      content: 'Updated peer tutoring schedule available online',
      date: '2024-01-25',
      priority: 'low'
    }
  ];

  const handleServiceClick = (serviceName) => {
    setSelectedService(serviceName);
    setShowAppointmentModal(true);
  };

  const getPriorityBadge = (priority) => {
    const variants = {
      'high': 'danger',
      'medium': 'warning',
      'low': 'info'
    };
    return <Badge bg={variants[priority]}>{priority}</Badge>;
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Student Services</h1>
            <p className="lead">Comprehensive support for your academic and personal success</p>
          </div>

          {/* Quick Services Overview */}
          <Row className="mb-4">
            <Col md={8}>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Available Services</h5>
                </Card.Header>
                <Card.Body>
                  <Table responsive striped>
                    <thead>
                      <tr>
                        <th>Service</th>
                        <th>Description</th>
                        <th>Contact</th>
                        <th>Hours</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {services.map(service => (
                        <tr key={service.id}>
                          <td><strong>{service.name}</strong></td>
                          <td>{service.description}</td>
                          <td>{service.contact}</td>
                          <td>{service.hours}</td>
                          <td>
                            <Button 
                              variant="outline-primary" 
                              size="sm"
                              onClick={() => handleServiceClick(service.name)}
                            >
                              {service.appointmentRequired ? 'Book Appointment' : 'Contact'}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              {/* Quick Links */}
              <Card className="mb-4">
                <Card.Header>
                  <h6 className="mb-0">Quick Links</h6>
                </Card.Header>
                <Card.Body>
                  {quickLinks.map((link, index) => (
                    <div key={index} className="mb-3">
                      <h6 className="mb-1">{link.title}</h6>
                      <p className="text-muted small mb-2">{link.description}</p>
                      <Button variant="outline-primary" size="sm">
                        Access Service
                      </Button>
                    </div>
                  ))}
                </Card.Body>
              </Card>

              {/* Announcements */}
              <Card>
                <Card.Header>
                  <h6 className="mb-0">Service Announcements</h6>
                </Card.Header>
                <Card.Body>
                  {announcements.map(announcement => (
                    <div key={announcement.id} className="mb-3 pb-3 border-bottom">
                      <div className="d-flex justify-content-between align-items-start mb-1">
                        <h6 className="mb-0">{announcement.title}</h6>
                        {getPriorityBadge(announcement.priority)}
                      </div>
                      <p className="small mb-1">{announcement.content}</p>
                      <small className="text-muted">{announcement.date}</small>
                    </div>
                  ))}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Service Locations Map */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Service Locations</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={8}>
                  <div className="bg-light rounded p-4 text-center">
                    <i className="bi bi-map" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
                    <h5 className="mt-3">Campus Services Map</h5>
                    <p className="text-muted">
                      Interactive map showing all student service locations
                    </p>
                    <Button variant="primary">
                      View Campus Map
                    </Button>
                  </div>
                </Col>
                <Col md={4}>
                  <h6>Key Service Locations</h6>
                  <ul className="list-unstyled">
                    <li className="mb-2">
                      <i className="bi bi-heart-pulse text-danger me-2"></i>
                      Health Center - Building A
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-book text-primary me-2"></i>
                      Library - Building B
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-briefcase text-success me-2"></i>
                      Career Center - Building C
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-laptop text-info me-2"></i>
                      IT Support - Building D
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-people text-warning me-2"></i>
                      Student Affairs - Main Admin
                    </li>
                  </ul>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Emergency Contacts */}
          <Card className="mb-4">
            <Card.Header className="bg-danger text-white">
              <h5 className="mb-0">Emergency Contacts</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={4}>
                  <div className="text-center p-3">
                    <i className="bi bi-telephone-fill text-danger" style={{ fontSize: '2rem' }}></i>
                    <h6 className="mt-2">Emergency Hotline</h6>
                    <p className="mb-1"><strong>+254 711 123 456</strong></p>
                    <small className="text-muted">24/7 Available</small>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center p-3">
                    <i className="bi bi-shield-check text-primary" style={{ fontSize: '2rem' }}></i>
                    <h6 className="mt-2">Campus Security</h6>
                    <p className="mb-1"><strong>+254 711 123 457</strong></p>
                    <small className="text-muted">Emergency Response</small>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center p-3">
                    <i className="bi bi-plus-circle text-success" style={{ fontSize: '2rem' }}></i>
                    <h6 className="mt-2">Health Emergency</h6>
                    <p className="mb-1"><strong>+254 711 123 458</strong></p>
                    <small className="text-muted">Medical Emergencies</small>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Service Hours Summary */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">Service Hours Summary</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h6>Regular Service Hours</h6>
                  <Table responsive size="sm">
                    <tbody>
                      <tr>
                        <td><strong>Academic Support:</strong></td>
                        <td>Mon-Fri 8:00 AM - 4:00 PM</td>
                      </tr>
                      <tr>
                        <td><strong>Career Guidance:</strong></td>
                        <td>Mon-Fri 9:00 AM - 3:00 PM</td>
                      </tr>
                      <tr>
                        <td><strong>Health Services:</strong></td>
                        <td>24/7 Emergency, Mon-Fri 8-5</td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
                <Col md={6}>
                  <h6>After-Hours Support</h6>
                  <ul>
                    <li>Emergency contacts available 24/7</li>
                    <li>Online resources accessible anytime</li>
                    <li>Email support with 24-hour response</li>
                    <li>Weekend library access available</li>
                  </ul>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Appointment Booking Modal */}
          <Modal show={showAppointmentModal} onHide={() => setShowAppointmentModal(false)}>
            <Modal.Header closeButton>
              <Modal.Title>Book Appointment - {selectedService}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Select Date</Form.Label>
                  <Form.Control type="date" required />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Preferred Time</Form.Label>
                  <Form.Select required>
                    <option value="">Select time slot</option>
                    <option>9:00 AM</option>
                    <option>10:00 AM</option>
                    <option>11:00 AM</option>
                    <option>2:00 PM</option>
                    <option>3:00 PM</option>
                    <option>4:00 PM</option>
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Reason for Appointment</Form.Label>
                  <Form.Control as="textarea" rows={3} required />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    label="I understand that I will receive a confirmation email"
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
                Book Appointment
              </Button>
            </Modal.Footer>
          </Modal>
        </Col>
      </Row>
    </Container>
  );
};

export default StudentServices;