import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, Button, Form, Modal, Tab, Nav } from 'react-bootstrap';

const StudentClubs = () => {
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [selectedClub, setSelectedClub] = useState(null);

  const clubs = [
    {
      id: 1,
      name: 'Science & Technology Club',
      category: 'academic',
      description: 'Explore the wonders of science and technology through experiments, projects, and competitions.',
      meetingSchedule: 'Every Tuesday, 3:30 PM - 5:00 PM',
      location: 'Science Lab 2',
      facultyAdvisor: 'Dr. Wanjiku',
      members: 45,
      status: 'Active',
      achievements: ['National Science Fair Winners 2023', 'Robotics Competition Finalists'],
      requirements: 'Interest in science and technology'
    },
    {
      id: 2,
      name: 'Debate & Public Speaking',
      category: 'academic',
      description: 'Develop critical thinking and public speaking skills through structured debates and discussions.',
      meetingSchedule: 'Every Wednesday, 4:00 PM - 5:30 PM',
      location: 'Library Conference Room',
      facultyAdvisor: 'Mr. Omondi',
      members: 32,
      status: 'Active',
      achievements: ['Regional Debate Champions', 'Model UN Excellence Award'],
      requirements: 'Willingness to learn and participate'
    },
    {
      id: 3,
      name: 'Environmental Club',
      category: 'service',
      description: 'Promote environmental awareness and sustainability through projects and community initiatives.',
      meetingSchedule: 'Every Thursday, 3:30 PM - 4:30 PM',
      location: 'Green House',
      facultyAdvisor: 'Mrs. Muthoni',
      members: 28,
      status: 'Active',
      achievements: ['School Recycling Program', 'Tree Planting Initiative'],
      requirements: 'Passion for environmental conservation'
    },
    {
      id: 4,
      name: 'Drama & Theater',
      category: 'arts',
      description: 'Express creativity through acting, play production, and theatrical performances.',
      meetingSchedule: 'Monday & Friday, 4:00 PM - 6:00 PM',
      location: 'Auditorium',
      facultyAdvisor: 'Ms. Akinyi',
      members: 35,
      status: 'Active',
      achievements: ['School Production Awards', 'Drama Festival Participants'],
      requirements: 'Audition required for major roles'
    },
    {
      id: 5,
      name: 'Chess Club',
      category: 'games',
      description: 'Strategic thinking and friendly competition through chess games and tournaments.',
      meetingSchedule: 'Every Friday, 3:30 PM - 5:00 PM',
      location: 'Common Room',
      facultyAdvisor: 'Mr. Kamau',
      members: 25,
      status: 'Active',
      achievements: ['Inter-school Chess Tournament', 'Club Championship'],
      requirements: 'All skill levels welcome'
    },
    {
      id: 6,
      name: 'Community Service Club',
      category: 'service',
      description: 'Make a difference in the community through volunteer work and service projects.',
      meetingSchedule: 'Every Saturday, 9:00 AM - 12:00 PM',
      location: 'Various Community Locations',
      facultyAdvisor: 'Mrs. Ndirangu',
      members: 40,
      status: 'Active',
      achievements: ['Community Outreach Awards', 'Service Learning Projects'],
      requirements: 'Commitment to service activities'
    }
  ];

  const categories = [
    { name: 'all', label: 'All Clubs' },
    { name: 'academic', label: 'Academic' },
    { name: 'arts', label: 'Arts & Culture' },
    { name: 'service', label: 'Service' },
    { name: 'games', label: 'Games & Strategy' }
  ];

  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredClubs = selectedCategory === 'all' 
    ? clubs 
    : clubs.filter(club => club.category === selectedCategory);

  const getCategoryBadge = (category) => {
    const variants = {
      'academic': 'primary',
      'arts': 'success',
      'service': 'info',
      'games': 'warning'
    };
    return <Badge bg={variants[category] || 'secondary'}>{category}</Badge>;
  };

  const handleJoinClick = (club) => {
    setSelectedClub(club);
    setShowJoinModal(true);
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Student Clubs & Societies</h1>
            <p className="lead">Discover your passions, develop new skills, and make lasting friendships</p>
          </div>

          {/* Category Filter */}
          <Card className="mb-4">
            <Card.Body className="text-center">
              <h5 className="mb-3">Browse Clubs by Category</h5>
              <div className="d-flex flex-wrap justify-content-center gap-2">
                {categories.map(category => (
                  <Button
                    key={category.name}
                    variant={selectedCategory === category.name ? 'primary' : 'outline-primary'}
                    onClick={() => setSelectedCategory(category.name)}
                  >
                    {category.label}
                  </Button>
                ))}
              </div>
            </Card.Body>
          </Card>

          {/* Clubs Grid */}
          <Row>
            {filteredClubs.map(club => (
              <Col md={6} lg={4} key={club.id} className="mb-4">
                <Card className="h-100">
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    {getCategoryBadge(club.category)}
                    <Badge bg={club.status === 'Active' ? 'success' : 'secondary'}>
                      {club.members} members
                    </Badge>
                  </Card.Header>
                  <Card.Body>
                    <h5 className="card-title">{club.name}</h5>
                    <p className="card-text">{club.description}</p>
                    
                    <div className="mb-3">
                      <small className="text-muted">
                        <strong>Meeting:</strong> {club.meetingSchedule}<br />
                        <strong>Location:</strong> {club.location}<br />
                        <strong>Advisor:</strong> {club.facultyAdvisor}
                      </small>
                    </div>

                    {club.achievements.length > 0 && (
                      <div className="mb-3">
                        <strong>Achievements:</strong>
                        <ul className="small mb-0">
                          {club.achievements.slice(0, 2).map((achievement, idx) => (
                            <li key={idx}>{achievement}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </Card.Body>
                  <Card.Footer>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => handleJoinClick(club)}
                    >
                      Join Club
                    </Button>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>

          {/* Club Statistics */}
          <Row className="mt-4">
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3>{clubs.length}</h3>
                  <p className="text-muted mb-0">Active Clubs</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-success">
                    {clubs.reduce((total, club) => total + club.members, 0)}
                  </h3>
                  <p className="text-muted mb-0">Total Members</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-info">
                    {clubs.filter(club => club.category === 'academic').length}
                  </h3>
                  <p className="text-muted mb-0">Academic Clubs</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-warning">15+</h3>
                  <p className="text-muted mb-0">Annual Events</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Join Club Modal */}
          <Modal show={showJoinModal} onHide={() => setShowJoinModal(false)}>
            <Modal.Header closeButton>
              <Modal.Title>Join {selectedClub?.name}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              {selectedClub && (
                <div>
                  <p><strong>Description:</strong> {selectedClub.description}</p>
                  <p><strong>Requirements:</strong> {selectedClub.requirements}</p>
                  <p><strong>Meeting Schedule:</strong> {selectedClub.meetingSchedule}</p>
                  <p><strong>Location:</strong> {selectedClub.location}</p>
                  
                  <Form>
                    <Form.Group className="mb-3">
                      <Form.Label>Why do you want to join this club?</Form.Label>
                      <Form.Control as="textarea" rows={3} required />
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Previous Experience (if any)</Form.Label>
                      <Form.Control as="textarea" rows={2} />
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Check
                        type="checkbox"
                        label="I commit to attending regular meetings and participating in club activities"
                        required
                      />
                    </Form.Group>
                  </Form>
                </div>
              )}
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={() => setShowJoinModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={() => setShowJoinModal(false)}>
                Submit Application
              </Button>
            </Modal.Footer>
          </Modal>

          {/* Start New Club Section */}
          <Card className="mt-4">
            <Card.Header>
              <h5 className="mb-0">Want to Start a New Club?</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={8}>
                  <p>
                    Have an idea for a new club? We encourage students to take initiative and 
                    create clubs that match their interests and passions.
                  </p>
                  <ul>
                    <li>Find at least 10 interested students</li>
                    <li>Identify a faculty advisor</li>
                    <li>Submit a club proposal</li>
                    <li>Present to the Student Activities Committee</li>
                  </ul>
                </Col>
                <Col md={4} className="text-center">
                  <Button variant="outline-primary">
                    Start New Club
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default StudentClubs;