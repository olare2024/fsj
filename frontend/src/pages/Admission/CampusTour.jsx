import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Carousel, Form, Badge, Modal } from 'react-bootstrap';

const CampusTour = () => {
  const [showBookingModal, setShowBookingModal] = useState(false);

  const campusHighlights = [
    {
      title: 'Modern Classrooms',
      description: 'Technology-enabled learning spaces with interactive whiteboards and comfortable seating',
      image: '/images/classrooms.jpg',
      features: ['Smart boards', 'Air conditioning', 'Ergonomic furniture']
    },
    {
      title: 'Science Laboratories',
      description: 'Fully equipped labs for Physics, Chemistry, and Biology with latest equipment',
      image: '/images/labs.jpg',
      features: ['Modern equipment', 'Safety systems', 'Research-grade tools']
    },
    {
      title: 'Sports Facilities',
      description: 'Olympic-sized swimming pool, football field, basketball courts, and indoor sports complex',
      image: '/images/sports.jpg',
      features: ['Swimming pool', 'Multiple courts', 'Fitness center']
    },
    {
      title: 'Library & Resource Center',
      description: 'Extensive collection of books, digital resources, and quiet study areas',
      image: '/images/library.jpg',
      features: ['20,000+ books', 'Digital resources', 'Study pods']
    },
    {
      title: 'Arts & Music Center',
      description: 'Dedicated spaces for visual arts, music practice, and performance',
      image: '/images/arts.jpg',
      features: ['Art studios', 'Music rooms', 'Performance theater']
    },
    {
      title: 'Boarding Facilities',
      description: 'Comfortable and secure boarding houses with modern amenities',
      image: '/images/boarding.jpg',
      features: ['WiFi enabled', 'Study areas', 'Recreational spaces']
    }
  ];

  const tourSlots = [
    { day: 'Monday', slots: ['10:00 AM', '2:00 PM'] },
    { day: 'Wednesday', slots: ['10:00 AM', '2:00 PM'] },
    { day: 'Friday', slots: ['10:00 AM', '2:00 PM', '4:00 PM'] },
    { day: 'Saturday', slots: ['9:00 AM', '11:00 AM', '1:00 PM'] }
  ];

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Campus Tour</h1>
            <p className="lead">Experience the Delvok Academy difference firsthand</p>
          </div>

          {/* Campus Overview */}
          <Card className="mb-4">
            <Card.Body>
              <Row>
                <Col lg={6}>
                  <h4>Welcome to Our Campus</h4>
                  <p>
                    Nestled on a 20-acre green campus in Karen, Delvok Academy offers 
                    state-of-the-art facilities designed to inspire learning and growth. 
                    Our campus seamlessly blends modern architecture with natural surroundings, 
                    creating an ideal environment for both CBC and Cambridge curricula.
                  </p>
                  <div className="d-flex gap-2 mb-3">
                    <Badge bg="primary">20 Acre Campus</Badge>
                    <Badge bg="success">Green Environment</Badge>
                    <Badge bg="info">Modern Facilities</Badge>
                  </div>
                  <Button 
                    variant="primary" 
                    size="lg"
                    onClick={() => setShowBookingModal(true)}
                  >
                    Book a Campus Tour
                  </Button>
                </Col>
                <Col lg={6}>
                  <Carousel>
                    <Carousel.Item>
                      <img
                        className="d-block w-100"
                        src="/images/campus-aerial.jpg"
                        alt="Aerial view of campus"
                        style={{ height: '300px', objectFit: 'cover' }}
                      />
                      <Carousel.Caption>
                        <h5>Aerial Campus View</h5>
                      </Carousel.Caption>
                    </Carousel.Item>
                    <Carousel.Item>
                      <img
                        className="d-block w-100"
                        src="/images/campus-entrance.jpg"
                        alt="Campus entrance"
                        style={{ height: '300px', objectFit: 'cover' }}
                      />
                      <Carousel.Caption>
                        <h5>Main Entrance</h5>
                      </Carousel.Caption>
                    </Carousel.Item>
                  </Carousel>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Campus Highlights */}
          <h3 className="text-center mb-4">Campus Highlights</h3>
          <Row className="mb-4">
            {campusHighlights.map((highlight, index) => (
              <Col md={6} lg={4} key={index} className="mb-4">
                <Card className="h-100">
                  <Card.Img 
                    variant="top" 
                    src={highlight.image}
                    style={{ height: '200px', objectFit: 'cover' }}
                  />
                  <Card.Body>
                    <h5 className="card-title">{highlight.title}</h5>
                    <p className="card-text">{highlight.description}</p>
                    <ul className="small">
                      {highlight.features.map((feature, idx) => (
                        <li key={idx}>{feature}</li>
                      ))}
                    </ul>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>

          {/* Virtual Tour */}
          <Card className="mb-4">
            <Card.Header>
              <h4 className="mb-0">
                <i className="bi bi-camera-video text-primary me-2"></i>
                Virtual Campus Tour
              </h4>
            </Card.Header>
            <Card.Body className="text-center">
              <p className="lead mb-4">
                Can't visit in person? Take our virtual tour from the comfort of your home!
              </p>
              <div className="bg-light rounded p-5 mb-4">
                <i className="bi bi-play-circle-fill text-primary" style={{ fontSize: '4rem' }}></i>
                <h5 className="mt-3">360° Virtual Experience</h5>
                <p className="text-muted">
                  Interactive tour of our classrooms, labs, and facilities
                </p>
              </div>
              <Button variant="outline-primary" size="lg">
                Start Virtual Tour
              </Button>
            </Card.Body>
          </Card>

          {/* Campus Map */}
          <Card className="mb-4">
            <Card.Header>
              <h4 className="mb-0">Campus Map</h4>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={8}>
                  <div className="bg-light rounded p-4 text-center">
                    <i className="bi bi-map" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
                    <p className="mt-3 mb-0">Interactive campus map coming soon</p>
                  </div>
                </Col>
                <Col md={4}>
                  <h6>Key Locations</h6>
                  <ul className="list-unstyled">
                    <li className="mb-2">
                      <i className="bi bi-building text-primary me-2"></i>
                      Administration Block
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-book text-success me-2"></i>
                      Academic Blocks
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-flask text-info me-2"></i>
                      Science Complex
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-trophy text-warning me-2"></i>
                      Sports Complex
                    </li>
                    <li className="mb-2">
                      <i className="bi bi-house-door text-danger me-2"></i>
                      Boarding Houses
                    </li>
                  </ul>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Booking Modal */}
          <Modal show={showBookingModal} onHide={() => setShowBookingModal(false)} size="lg">
            <Modal.Header closeButton>
              <Modal.Title>Book a Campus Tour</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <Form>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Full Name *</Form.Label>
                      <Form.Control type="text" required />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Email Address *</Form.Label>
                      <Form.Control type="email" required />
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Phone Number *</Form.Label>
                      <Form.Control type="tel" required />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Student Grade Level</Form.Label>
                      <Form.Select>
                        <option>Select grade...</option>
                        <option>Grade 1-3 (CBC)</option>
                        <option>Grade 4-6 (CBC)</option>
                        <option>Grade 7-9 (Junior Secondary)</option>
                        <option>IGCSE</option>
                        <option>A Level</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group className="mb-3">
                  <Form.Label>Preferred Tour Date *</Form.Label>
                  <Form.Control type="date" required />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Preferred Time Slot *</Form.Label>
                  <Form.Select required>
                    <option value="">Select time slot...</option>
                    {tourSlots.flatMap(day => 
                      day.slots.map(slot => (
                        <option key={`${day.day}-${slot}`} value={`${day.day}-${slot}`}>
                          {day.day} at {slot}
                        </option>
                      ))
                    )}
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Special Requirements</Form.Label>
                  <Form.Control as="textarea" rows={3} placeholder="Any special requirements or questions..." />
                </Form.Group>
                <Alert variant="info">
                  <small>
                    Tour confirmation will be sent via email within 24 hours. 
                    Tours typically last 1.5-2 hours and include a guided walk 
                    of key facilities and Q&A session with admissions staff.
                  </small>
                </Alert>
              </Form>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={() => setShowBookingModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={() => setShowBookingModal(false)}>
                Book Tour
              </Button>
            </Modal.Footer>
          </Modal>

          {/* Contact Information */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">Visit Us</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h6>Address</h6>
                  <p>
                    Delvok Academy<br />
                    Karen Road<br />
                    Nairobi, Kenya<br />
                    P.O. Box 12345-00100
                  </p>
                </Col>
                <Col md={6}>
                  <h6>Contact Information</h6>
                  <p>
                    <i className="bi bi-telephone me-2"></i>
                    +254 700 123 456<br />
                    <i className="bi bi-envelope me-2"></i>
                    admissions@delvok.ac.ke<br />
                    <i className="bi bi-clock me-2"></i>
                    Mon-Fri: 8:00 AM - 4:00 PM
                  </p>
                </Col>
              </Row>
              <div className="text-center mt-3">
                <Button variant="outline-primary" className="me-2">
                  <i className="bi bi-download me-1"></i>
                  Download Campus Map
                </Button>
                <Button variant="outline-success">
                  <i className="bi bi-share me-1"></i>
                  Share Tour Information
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default CampusTour;