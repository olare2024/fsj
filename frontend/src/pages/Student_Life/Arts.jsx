import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Button, Carousel, Tab, Nav, Modal, Form } from 'react-bootstrap';

const Arts = () => {
  const [activeTab, setActiveTab] = useState('visual');
  const [showGalleryModal, setShowGalleryModal] = useState(false);
  const [selectedArtwork, setSelectedArtwork] = useState(null);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Preload images or initialize any required data
  }, []);

  const ImageWithFallback = ({ src, fallback, alt, className, ...props }) => {
    const [error, setError] = useState(false);
    
    return (
      <>
        {!error ? (
          <img 
            src={src} 
            alt={alt}
            className={className}
            onError={() => setError(true)}
            {...props}
          />
        ) : (
          <div className={`${className} d-flex align-items-center justify-content-center bg-light text-muted`}>
            <span className="fs-1">{fallback}</span>
          </div>
        )}
      </>
    );
  };

  const bannerSlides = [
    {
      id: 1,
      title: "Visual Arts Excellence",
      subtitle: "Explore painting, drawing, sculpture and digital arts",
      image: "/src/assets/img/arts/visual-arts-banner.jpg",
      fallback: "🎨",
      theme: "primary"
    },
    {
      id: 2,
      title: "Performing Arts",
      subtitle: "Music, dance, drama and theatrical productions",
      image: "/src/assets/img/arts/performing-arts-banner.jpg",
      fallback: "🎭",
      theme: "success"
    },
    {
      id: 3,
      title: "Creative Expression",
      subtitle: "Nurturing artistic talent and creative thinking",
      image: "/src/assets/img/art/creative-expression-banner.jpg",
      fallback: "✨",
      theme: "warning"
    }
  ];

  const visualArts = [
    {
      id: 1,
      title: 'Annual Art Exhibition',
      description: 'Showcasing student artwork from various mediums including painting, drawing, and sculpture. Features both traditional and contemporary pieces.',
      schedule: 'March 15-30, 2024',
      location: 'School Art Gallery',
      instructor: 'Mrs. Sarah Artist',
      level: 'All Levels',
      image: '/src/assets/img/arts/art-exhibition.jpg',
      fallback: '🖼️',
      requirements: ['Portfolio Review', 'All Mediums Welcome'],
      capacity: 'Unlimited',
      fee: 'Free'
    },
    {
      id: 2,
      title: 'Digital Arts Program',
      description: 'Exploring digital painting, graphic design, and animation using modern technology and software tools.',
      schedule: 'Ongoing - Weekly Workshops',
      location: 'Computer Lab 3',
      instructor: 'Mr. James Digital',
      level: 'Intermediate',
      image: '/src/assets/img/art/digital-arts.jpg',
      fallback: '💻',
      requirements: ['Basic Computer Skills', 'Artistic Background'],
      capacity: '20 Students',
      fee: 'KSh 2,000 per term'
    },
    {
      id: 3,
      title: 'Pottery & Ceramics',
      description: 'Hands-on experience with clay, wheel throwing, and ceramic techniques. Learn traditional and modern pottery methods.',
      schedule: 'Tuesday & Thursday, 4:00-6:00 PM',
      location: 'Art Studio 2',
      instructor: 'Ms. Grace Potter',
      level: 'Beginner Friendly',
      image: '/src/assets/img/art/pottery.jpg',
      fallback: '🏺',
      requirements: ['No Experience Needed', 'Creative Mindset'],
      capacity: '15 Students',
      fee: 'KSh 3,500 per term'
    },
    {
      id: 4,
      title: 'Photography Club',
      description: 'Learn photography techniques, composition, and digital editing. Field trips and photo walks included.',
      schedule: 'Wednesday, 3:30-5:30 PM',
      location: 'Photo Studio',
      instructor: 'Mr. Alex Lens',
      level: 'All Levels',
      image: '/src/assets/img/art/photography.jpg',
      fallback: '📸',
      requirements: ['Camera Recommended', 'Smartphone Acceptable'],
      capacity: '25 Students',
      fee: 'KSh 1,500 per term'
    }
  ];

  const performingArts = [
    {
      id: 1,
      title: 'School Drama Production',
      description: 'Annual school play with auditions, rehearsals, and public performances. Multiple roles available.',
      schedule: 'Production: May 2024',
      location: 'School Auditorium',
      instructor: 'Ms. Linda Director',
      participants: '60+ Students',
      image: '/src/assets/img/art/drama.jpg',
      fallback: '🎬',
      requirements: ['Audition Required', 'Commitment Essential'],
      roles: ['Actors', 'Stage Crew', 'Directors']
    },
    {
      id: 2,
      title: 'Music Ensembles',
      description: 'Various musical groups including choir, orchestra, and jazz band. Performances throughout the year.',
      schedule: 'Regular rehearsals throughout week',
      location: 'Music Department',
      instructor: 'Mr. David Maestro',
      participants: '100+ Students',
      image: '/src/assets/img/art/music.jpg',
      fallback: '🎵',
      requirements: ['Basic Music Knowledge', 'Instrument/Singing'],
      ensembles: ['Choir', 'Orchestra', 'Jazz Band']
    },
    {
      id: 3,
      title: 'Dance Company',
      description: 'Contemporary, traditional, and modern dance performances and competitions. Multiple dance styles.',
      schedule: 'Monday & Wednesday, 4:30-6:30 PM',
      location: 'Dance Studio',
      instructor: 'Mrs. Maria Dancer',
      participants: '40+ Students',
      image: '/src/assets/img/art/dance.jpg',
      fallback: '💃',
      requirements: ['Dance Experience Preferred', 'Physical Fitness'],
      styles: ['Contemporary', 'Traditional', 'Hip Hop']
    }
  ];

  const studentArtworks = [
    {
      id: 1,
      title: 'African Sunset',
      artist: 'Grace Wambui - Grade 10',
      medium: 'Oil on Canvas',
      description: 'A vibrant depiction of the Kenyan landscape at sunset, capturing the rich colors and textures of the African terrain.',
      image: '/src/assets/img/artwork/african-sunset.jpg',
      fallback: '🌅',
      awards: ['Best in Show - 2023', 'Regional Art Competition Winner'],
      year: '2023',
      category: 'Painting'
    },
    {
      id: 2,
      title: 'Urban Dreams',
      artist: 'David Ochieng - Grade 12',
      medium: 'Digital Art',
      description: 'Modern interpretation of city life and aspirations, exploring the intersection of technology and urban culture.',
      image: '/src/assets/img/artwork/urban-dreams.jpg',
      fallback: '🏙️',
      awards: ['Digital Arts Excellence Award'],
      year: '2024',
      category: 'Digital Art'
    },
    {
      id: 3,
      title: 'Cultural Heritage',
      artist: 'Amina Mohammed - Grade 11',
      medium: 'Mixed Media',
      description: 'Celebrating traditional African art forms through contemporary mixed media techniques and materials.',
      image: '/src/assets/img/artwork/cultural-heritage.jpg',
      fallback: '🌍',
      awards: ['Cultural Preservation Award'],
      year: '2023',
      category: 'Mixed Media'
    },
    {
      id: 4,
      title: 'Abstract Emotions',
      artist: 'Brian Kimathi - Grade 9',
      medium: 'Acrylic on Canvas',
      description: 'Expressive abstract composition exploring the complexity of human emotions through color and form.',
      image: '/src/assets/img/artwork/abstract-emotions.jpg',
      fallback: '🎨',
      awards: ['Young Artist Recognition'],
      year: '2024',
      category: 'Abstract'
    }
  ];

  const upcomingEvents = [
    {
      id: 1,
      name: 'Spring Music Concert',
      date: '2024-03-20',
      time: '6:30 PM',
      location: 'Auditorium',
      type: 'Music',
      image: '/src/assets/img/events/spring-concert.jpg',
      tickets: 'KSh 200 Students, KSh 500 Adults'
    },
    {
      id: 2,
      name: 'Art Exhibition Opening',
      date: '2024-03-15',
      time: '4:00 PM',
      location: 'Art Gallery',
      type: 'Visual Arts',
      image: '/src/assets/img/events/art-opening.jpg',
      tickets: 'Free Admission'
    },
    {
      id: 3,
      name: 'Drama Festival',
      date: '2024-04-05',
      time: '7:00 PM',
      location: 'Main Hall',
      type: 'Theater',
      image: '/src/assets/img/events/drama-festival.jpg',
      tickets: 'KSh 300 Students, KSh 700 Adults'
    },
    {
      id: 4,
      name: 'Dance Showcase',
      date: '2024-04-12',
      time: '6:00 PM',
      location: 'Auditorium',
      type: 'Dance',
      image: '/src/assets/img/events/dance-showcase.jpg',
      tickets: 'KSh 250 Students, KSh 600 Adults'
    }
  ];

  const artsFacilities = [
    {
      name: 'Art Studios',
      image: '/src/assets/img/facilities/art-studio.jpg',
      description: 'Dedicated spaces for various art forms with natural lighting and professional equipment.',
      features: ['2 Painting Studios', 'Pottery Workshop', 'Digital Arts Lab', 'Photography Darkroom', 'Printmaking Studio'],
      capacity: '50+ Students'
    },
    {
      name: 'Performing Arts Center',
      image: '/src/assets/img/facilities/performing-arts-center.jpg',
      description: 'State-of-the-art facility for music, dance, and theatrical performances.',
      features: ['500-seat Auditorium', 'Music Practice Rooms', 'Dance Studio', 'Drama Spaces', 'Recording Studio'],
      capacity: '200+ Students'
    },
    {
      name: 'Exhibition Gallery',
      image: '/src/assets/img/facilities/gallery.jpg',
      description: 'Professional gallery space for displaying student artwork and hosting exhibitions.',
      features: ['Rotating Exhibitions', 'Professional Lighting', 'Opening Events', 'Visitor Space'],
      capacity: '100+ Visitors'
    }
  ];

  const handleArtworkClick = (artwork) => {
    setSelectedArtwork(artwork);
    setShowGalleryModal(true);
  };

  const handleJoinProgram = (program) => {
    setSelectedProgram(program);
    setShowJoinModal(true);
  };

  const filteredVisualArts = visualArts.filter(program =>
    program.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    program.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    program.instructor.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredPerformingArts = performingArts.filter(program =>
    program.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    program.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    program.instructor.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="arts-page">
      {/* Hero Banner */}
      <section className="arts-hero-banner bg-dark text-white">
        <Carousel>
          {bannerSlides.map((slide) => (
            <Carousel.Item key={slide.id}>
              <div 
                className="banner-slide d-flex align-items-center justify-content-center"
                style={{
                  backgroundImage: `linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url(${slide.image})`,
                  height: '400px',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
              >
                <div className="banner-fallback text-center">
                  <span className="display-1">{slide.fallback}</span>
                </div>
                <div className="banner-content text-center">
                  <h1 className="display-4 fw-bold mb-3">{slide.title}</h1>
                  <p className="lead fs-3">{slide.subtitle}</p>
                  <Button 
                    variant="light" 
                    size="lg" 
                    className="mt-3"
                    onClick={() => setActiveTab('visual')}
                  >
                    Explore Programs
                  </Button>
                </div>
              </div>
            </Carousel.Item>
          ))}
        </Carousel>
      </section>

      <Container className="mt-4">
        <Row>
          <Col>
            <div className="text-center mb-5">
              <h1 className="text-primary">Arts & Creative Expression</h1>
              <p className="lead">Nurturing creativity and artistic talent across all disciplines at Delvok Academy</p>
            </div>

            {/* Search Bar */}
            <Card className="mb-4">
              <Card.Body>
                <Row className="align-items-center">
                  <Col md={6}>
                    <h5 className="mb-0">Find Your Creative Path</h5>
                    <small className="text-muted">Discover arts programs that match your interests</small>
                  </Col>
                  <Col md={6}>
                    <Form.Group>
                      <Form.Control
                        type="text"
                        placeholder="Search programs, instructors, or keywords..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                </Row>
              </Card.Body>
            </Card>

            {/* Featured Artwork Carousel */}
            <Card className="mb-4">
              <Card.Header className="bg-primary text-white">
                <h5 className="mb-0">
                  <i className="bi bi-star-fill me-2"></i>
                  Featured Student Artwork
                </h5>
              </Card.Header>
              <Card.Body>
                <Carousel indicators={false} interval={4000}>
                  {studentArtworks.map(artwork => (
                    <Carousel.Item key={artwork.id}>
                      <div 
                        className="d-flex justify-content-center align-items-center"
                        style={{ height: '400px', cursor: 'pointer' }}
                        onClick={() => handleArtworkClick(artwork)}
                      >
                        <div className="text-center position-relative">
                          <ImageWithFallback
                            src={artwork.image}
                            fallback={artwork.fallback}
                            alt={artwork.title}
                            style={{ 
                              maxHeight: '300px', 
                              maxWidth: '100%', 
                              objectFit: 'contain' 
                            }}
                          />
                          <div className="mt-3">
                            <h5 className="text-primary">{artwork.title}</h5>
                            <p className="text-muted mb-1">{artwork.artist} - {artwork.medium}</p>
                            <Badge bg="info" className="me-1">{artwork.category}</Badge>
                            <Badge bg="success">{artwork.year}</Badge>
                          </div>
                        </div>
                      </div>
                    </Carousel.Item>
                  ))}
                </Carousel>
              </Card.Body>
            </Card>

            {/* Programs Tabs */}
            <Tab.Container activeKey={activeTab} onSelect={setActiveTab}>
              <Card>
                <Card.Header>
                  <Nav variant="tabs" className="card-header-tabs">
                    <Nav.Item>
                      <Nav.Link eventKey="visual">
                        <i className="bi bi-palette me-2"></i>
                        Visual Arts
                      </Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="performing">
                        <i className="bi bi-music-note-beamed me-2"></i>
                        Performing Arts
                      </Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="events">
                        <i className="bi bi-calendar-event me-2"></i>
                        Events & Shows
                      </Nav.Link>
                    </Nav.Item>
                    <Nav.Item>
                      <Nav.Link eventKey="facilities">
                        <i className="bi bi-building me-2"></i>
                        Facilities
                      </Nav.Link>
                    </Nav.Item>
                  </Nav>
                </Card.Header>
                <Card.Body>
                  <Tab.Content>
                    {/* Visual Arts Tab */}
                    <Tab.Pane eventKey="visual">
                      <Row>
                        {filteredVisualArts.map(program => (
                          <Col md={6} lg={4} key={program.id} className="mb-4">
                            <Card className="h-100 shadow-sm hover-lift">
                              <div className="program-image" style={{height: '200px', overflow: 'hidden'}}>
                                <ImageWithFallback
                                  src={program.image}
                                  fallback={program.fallback}
                                  alt={program.title}
                                  className="w-100 h-100"
                                  style={{objectFit: 'cover'}}
                                />
                              </div>
                              <Card.Body>
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                  <h6 className="card-title text-primary">{program.title}</h6>
                                  <Badge bg="outline-primary">{program.level}</Badge>
                                </div>
                                <p className="card-text small">{program.description}</p>
                                <div className="mb-3">
                                  <small className="text-muted">
                                    <strong>Instructor:</strong> {program.instructor}<br/>
                                    <strong>Schedule:</strong> {program.schedule}<br/>
                                    <strong>Location:</strong> {program.location}<br/>
                                    <strong>Fee:</strong> {program.fee}
                                  </small>
                                </div>
                                <div className="mb-2">
                                  {program.requirements.map((req, idx) => (
                                    <Badge key={idx} bg="light" text="dark" className="me-1 mb-1 small">
                                      {req}
                                    </Badge>
                                  ))}
                                </div>
                              </Card.Body>
                              <Card.Footer>
                                <Button 
                                  variant="primary" 
                                  size="sm" 
                                  className="w-100"
                                  onClick={() => handleJoinProgram(program)}
                                >
                                  Join Program
                                </Button>
                              </Card.Footer>
                            </Card>
                          </Col>
                        ))}
                      </Row>
                    </Tab.Pane>

                    {/* Performing Arts Tab */}
                    <Tab.Pane eventKey="performing">
                      <Row>
                        {filteredPerformingArts.map(program => (
                          <Col md={6} lg={4} key={program.id} className="mb-4">
                            <Card className="h-100 shadow-sm hover-lift">
                              <div className="program-image" style={{height: '200px', overflow: 'hidden'}}>
                                <ImageWithFallback
                                  src={program.image}
                                  fallback={program.fallback}
                                  alt={program.title}
                                  className="w-100 h-100"
                                  style={{objectFit: 'cover'}}
                                />
                              </div>
                              <Card.Body>
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                  <h6 className="card-title text-success">{program.title}</h6>
                                  <Badge bg="outline-success">{program.participants}</Badge>
                                </div>
                                <p className="card-text small">{program.description}</p>
                                <div className="mb-3">
                                  <small className="text-muted">
                                    <strong>Instructor:</strong> {program.instructor}<br/>
                                    <strong>Schedule:</strong> {program.schedule}<br/>
                                    <strong>Location:</strong> {program.location}
                                  </small>
                                </div>
                                <div className="mb-2">
                                  {program.roles && program.roles.map((role, idx) => (
                                    <Badge key={idx} bg="light" text="dark" className="me-1 mb-1 small">
                                      {role}
                                    </Badge>
                                  ))}
                                </div>
                              </Card.Body>
                              <Card.Footer>
                                <Button 
                                  variant="success" 
                                  size="sm" 
                                  className="w-100"
                                  onClick={() => handleJoinProgram(program)}
                                >
                                  Audition/Join
                                </Button>
                              </Card.Footer>
                            </Card>
                          </Col>
                        ))}
                      </Row>
                    </Tab.Pane>

                    {/* Events Tab */}
                    <Tab.Pane eventKey="events">
                      <Row>
                        <Col md={8}>
                          <h5 className="mb-4">Upcoming Arts Events</h5>
                          {upcomingEvents.map(event => (
                            <Card key={event.id} className="mb-3 shadow-sm">
                              <Card.Body>
                                <Row className="align-items-center">
                                  <Col md={2} className="text-center">
                                    <div className="bg-primary text-white rounded p-2">
                                      <strong>{new Date(event.date).toLocaleDateString('en-US', { month: 'short' })}</strong>
                                      <div className="fs-4">{new Date(event.date).getDate()}</div>
                                    </div>
                                  </Col>
                                  <Col md={6}>
                                    <h6 className="mb-1">{event.name}</h6>
                                    <p className="mb-1 text-muted">
                                      <i className="bi bi-clock me-1"></i>
                                      {event.time} • {event.location}
                                    </p>
                                    <Badge bg="info">{event.type}</Badge>
                                    <small className="d-block text-muted mt-1">
                                      Tickets: {event.tickets}
                                    </small>
                                  </Col>
                                  <Col md={4} className="text-end">
                                    <Button variant="primary" size="sm" className="me-2">
                                      Get Tickets
                                    </Button>
                                    <Button variant="outline-secondary" size="sm">
                                      Add to Calendar
                                    </Button>
                                  </Col>
                                </Row>
                              </Card.Body>
                            </Card>
                          ))}
                        </Col>
                        <Col md={4}>
                          <Card className="sticky-top" style={{top: '20px'}}>
                            <Card.Header>
                              <h6 className="mb-0">Arts Resources</h6>
                            </Card.Header>
                            <Card.Body>
                              <div className="d-grid gap-2">
                                <Button variant="outline-primary" className="mb-2">
                                  <i className="bi bi-download me-2"></i>
                                  Spring 2024 Calendar
                                </Button>
                                <Button variant="outline-success" className="mb-2">
                                  <i className="bi bi-file-earmark-text me-2"></i>
                                  Program Application Forms
                                </Button>
                                <Button variant="outline-warning" className="mb-2">
                                  <i className="bi bi-camera me-2"></i>
                                  Photo Gallery
                                </Button>
                                <Button variant="outline-info">
                                  <i className="bi bi-headphones me-2"></i>
                                  Audio Recordings
                                </Button>
                              </div>
                            </Card.Body>
                          </Card>
                        </Col>
                      </Row>
                    </Tab.Pane>

                    {/* Facilities Tab */}
                    <Tab.Pane eventKey="facilities">
                      <Row>
                        {artsFacilities.map((facility, index) => (
                          <Col md={6} lg={4} key={index} className="mb-4">
                            <Card className="h-100 shadow-sm">
                              <div className="facility-image" style={{height: '200px', overflow: 'hidden'}}>
                                <ImageWithFallback
                                  src={facility.image}
                                  fallback="🏢"
                                  alt={facility.name}
                                  className="w-100 h-100"
                                  style={{objectFit: 'cover'}}
                                />
                              </div>
                              <Card.Body>
                                <h6 className="card-title text-primary">{facility.name}</h6>
                                <p className="card-text small">{facility.description}</p>
                                <ul className="small">
                                  {facility.features.map((feature, idx) => (
                                    <li key={idx}>{feature}</li>
                                  ))}
                                </ul>
                                <div className="mt-2">
                                  <small className="text-muted">
                                    <strong>Capacity:</strong> {facility.capacity}
                                  </small>
                                </div>
                              </Card.Body>
                              <Card.Footer>
                                <Button variant="outline-primary" size="sm" className="w-100">
                                  Schedule Tour
                                </Button>
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

            {/* Arts Achievements */}
            <Card className="mt-4">
              <Card.Header className="bg-warning text-dark">
                <h5 className="mb-0">
                  <i className="bi bi-trophy me-2"></i>
                  Arts Achievements & Recognition
                </h5>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={6}>
                    <h6 className="text-primary">Recent Awards 2023-2024</h6>
                    <div className="achievement-list">
                      {[
                        'National Arts Competition - 1st Place Visual Arts',
                        'Regional Drama Festival - Best Original Script',
                        'Music Championships - Gold Medal Choir',
                        'Young Artists Exhibition - Featured Works',
                        'Dance Competition - Contemporary Category Winners',
                        'Digital Arts Fair - Innovation Award',
                        'Photography Contest - Landscape Category Winner'
                      ].map((award, index) => (
                        <div key={index} className="d-flex align-items-center mb-2">
                          <i className="bi bi-award-fill text-warning me-2"></i>
                          <span>{award}</span>
                        </div>
                      ))}
                    </div>
                  </Col>
                  <Col md={6}>
                    <h6 className="text-primary">Student Recognition</h6>
                    <Card className="mb-3">
                      <Card.Body>
                        <div className="d-flex align-items-center">
                          <div className="artist-avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style={{width: '50px', height: '50px'}}>
                            <i className="bi bi-person-fill"></i>
                          </div>
                          <div>
                            <strong>Artist of the Month:</strong>
                            <div>Maria Kamau (Grade 11)</div>
                            <small className="text-muted">Digital Arts & Painting</small>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                    <div className="mb-3">
                      <strong>Upcoming Exhibition:</strong>
                      <div>"Young Visionaries" at National Gallery - April 2024</div>
                    </div>
                    <div>
                      <strong>Scholarship Opportunities:</strong>
                      <div>5 students received arts scholarships totaling KSh 500,000</div>
                    </div>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* Gallery Modal */}
      <Modal show={showGalleryModal} onHide={() => setShowGalleryModal(false)} size="lg" centered>
        <Modal.Header closeButton className="bg-primary text-white">
          <Modal.Title>{selectedArtwork?.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body className="text-center">
          {selectedArtwork && (
            <>
              <ImageWithFallback
                src={selectedArtwork.image}
                fallback={selectedArtwork.fallback}
                alt={selectedArtwork.title}
                style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain' }}
                className="mb-3"
              />
              <div className="text-start">
                <h6 className="text-primary">{selectedArtwork.artist}</h6>
                <p className="text-muted mb-2">{selectedArtwork.medium} • {selectedArtwork.year}</p>
                <p className="mb-3">{selectedArtwork.description}</p>
                {selectedArtwork.awards && selectedArtwork.awards.length > 0 && (
                  <div>
                    <h6>Awards & Recognition:</h6>
                    <ul>
                      {selectedArtwork.awards.map((award, index) => (
                        <li key={index}>{award}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowGalleryModal(false)}>
            Close
          </Button>
          <Button variant="primary">
            <i className="bi bi-download me-2"></i>
            Download High Resolution
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Join Program Modal */}
      <Modal show={showJoinModal} onHide={() => setShowJoinModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Join {selectedProgram?.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedProgram && (
            <>
              <p>You're about to join: <strong>{selectedProgram.title}</strong></p>
              <p><strong>Instructor:</strong> {selectedProgram.instructor}</p>
              <p><strong>Schedule:</strong> {selectedProgram.schedule}</p>
              <p><strong>Location:</strong> {selectedProgram.location}</p>
              {selectedProgram.fee && <p><strong>Fee:</strong> {selectedProgram.fee}</p>}
              
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Full Name</Form.Label>
                  <Form.Control type="text" placeholder="Enter your full name" />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Grade/Class</Form.Label>
                  <Form.Control type="text" placeholder="Enter your grade/class" />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Previous Experience (Optional)</Form.Label>
                  <Form.Control as="textarea" rows={3} placeholder="Describe any relevant experience..." />
                </Form.Group>
              </Form>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowJoinModal(false)}>
            Cancel
          </Button>
          <Button variant="primary">
            Submit Application
          </Button>
        </Modal.Footer>
      </Modal>

      <style jsx>{`
        .arts-page {
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          min-height: 100vh;
        }
        
        .arts-hero-banner .carousel-item {
          transition: transform 0.6s ease-in-out;
        }
        
        .banner-slide {
          position: relative;
        }
        
        .banner-fallback {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0.1;
          z-index: 1;
        }
        
        .banner-content {
          position: relative;
          z-index: 2;
        }
        
        .hover-lift {
          transition: all 0.3s ease;
        }
        
        .hover-lift:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        }
        
        .program-image, .facility-image {
          transition: transform 0.3s ease;
        }
        
        .card:hover .program-image img,
        .card:hover .facility-image img {
          transform: scale(1.05);
        }
        
        .achievement-list {
          max-height: 300px;
          overflow-y: auto;
        }
        
        .artist-avatar {
          flex-shrink: 0;
        }
        
        @media (max-width: 768px) {
          .arts-hero-banner .display-4 {
            font-size: 2rem;
          }
          
          .arts-hero-banner .lead {
            font-size: 1.2rem;
          }
        }
      `}</style>
    </div>
  );
};

export default Arts;