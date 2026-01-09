import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, Button, Table, Tab, Nav } from 'react-bootstrap';

const Athletics = () => {
  const [activeTab, setActiveTab] = useState('teams');

  const sportsTeams = [
    {
      id: 1,
      name: 'Football Team',
      gender: 'Boys & Girls',
      coach: 'Mr. Kipchoge',
      practice: 'Mon, Wed, Fri 4:00-6:00 PM',
      achievements: ['County Champions 2023', 'Regional Finals'],
      tryouts: 'Open - Contact Coach',
      level: 'Competitive'
    },
    {
      id: 2,
      name: 'Basketball',
      gender: 'Boys & Girls',
      coach: 'Ms. Adhiambo',
      practice: 'Tue, Thu 4:00-6:00 PM',
      achievements: ['City League Winners', 'Tournament Participants'],
      tryouts: 'Seasonal - January',
      level: 'Competitive'
    },
    {
      id: 3,
      name: 'Swimming',
      gender: 'Mixed',
      coach: 'Mrs. Wangari',
      practice: 'Daily 6:00-7:30 AM',
      achievements: ['National Qualifiers', 'Multiple Gold Medals'],
      tryouts: 'Skill Assessment Required',
      level: 'Elite'
    },
    {
      id: 4,
      name: 'Track & Field',
      gender: 'Mixed',
      coach: 'Mr. Chebet',
      practice: 'Mon-Fri 4:00-6:00 PM',
      achievements: ['County Records', 'National Champions'],
      tryouts: 'Open to All',
      level: 'Competitive'
    },
    {
      id: 5,
      name: 'Volleyball',
      gender: 'Girls',
      coach: 'Ms. Nyong\'o',
      practice: 'Tue, Thu, Sat 4:00-6:00 PM',
      achievements: ['Regional Champions', 'Tournament Winners'],
      tryouts: 'Seasonal - March',
      level: 'Competitive'
    },
    {
      id: 6,
      name: 'Rugby',
      gender: 'Boys',
      coach: 'Mr. Ochieng',
      practice: 'Mon, Wed, Fri 4:00-6:30 PM',
      achievements: ['County League', 'Developing Program'],
      tryouts: 'Open - Contact Coach',
      level: 'Development'
    }
  ];

  const facilities = [
    {
      name: 'Olympic Swimming Pool',
      description: '8-lane, 50-meter pool with diving boards',
      hours: '6:00 AM - 8:00 PM',
      booking: 'Advance booking required'
    },
    {
      name: 'Main Sports Field',
      description: 'Football pitch with athletics track',
      hours: '6:00 AM - 9:00 PM',
      booking: 'Team practice priority'
    },
    {
      name: 'Basketball Courts',
      description: '4 indoor courts with professional flooring',
      hours: '7:00 AM - 10:00 PM',
      booking: 'Open access when available'
    },
    {
      name: 'Tennis Courts',
      description: '6 all-weather courts with lighting',
      hours: '7:00 AM - 9:00 PM',
      booking: 'Court booking system'
    },
    {
      name: 'Fitness Center',
      description: 'Modern gym with cardio and weight equipment',
      hours: '6:00 AM - 10:00 PM',
      booking: 'Student membership required'
    },
    {
      name: 'Sports Hall',
      description: 'Multi-purpose indoor sports facility',
      hours: '7:00 AM - 10:00 PM',
      booking: 'Advance booking required'
    }
  ];

  const upcomingEvents = [
    {
      id: 1,
      event: 'Inter-House Athletics Competition',
      date: '2024-02-15',
      time: '8:00 AM - 4:00 PM',
      location: 'Main Sports Field',
      participants: 'All Students'
    },
    {
      id: 2,
      event: 'Swimming Gala',
      date: '2024-02-22',
      time: '9:00 AM - 1:00 PM',
      location: 'Swimming Pool',
      participants: 'Swimming Team'
    },
    {
      id: 3,
      event: 'Basketball Tournament',
      date: '2024-03-05',
      time: '4:00 PM - 8:00 PM',
      location: 'Sports Hall',
      participants: 'Basketball Teams'
    },
    {
      id: 4,
      event: 'County Football Finals',
      date: '2024-03-12',
      time: '2:00 PM - 5:00 PM',
      location: 'Main Field',
      participants: 'Football Team'
    }
  ];

  const getLevelBadge = (level) => {
    const variants = {
      'Elite': 'danger',
      'Competitive': 'warning',
      'Development': 'info'
    };
    return <Badge bg={variants[level] || 'secondary'}>{level}</Badge>;
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Athletics & Sports</h1>
            <p className="lead">Building champions in sports and in life</p>
          </div>

          <Tab.Container activeKey={activeTab} onSelect={setActiveTab}>
            <Card>
              <Card.Header>
                <Nav variant="tabs" className="card-header-tabs">
                  <Nav.Item>
                    <Nav.Link eventKey="teams">Sports Teams</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="facilities">Facilities</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="events">Events & Schedule</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="achievements">Achievements</Nav.Link>
                  </Nav.Item>
                </Nav>
              </Card.Header>
              <Card.Body>
                <Tab.Content>
                  {/* Sports Teams Tab */}
                  <Tab.Pane eventKey="teams">
                    <Row>
                      {sportsTeams.map(team => (
                        <Col md={6} key={team.id} className="mb-4">
                          <Card className="h-100">
                            <Card.Header className="d-flex justify-content-between align-items-center">
                              <h6 className="mb-0">{team.name}</h6>
                              {getLevelBadge(team.level)}
                            </Card.Header>
                            <Card.Body>
                              <p><strong>Coach:</strong> {team.coach}</p>
                              <p><strong>Practice:</strong> {team.practice}</p>
                              <p><strong>Gender:</strong> {team.gender}</p>
                              <p><strong>Tryouts:</strong> {team.tryouts}</p>
                              
                              {team.achievements.length > 0 && (
                                <div>
                                  <strong>Achievements:</strong>
                                  <ul className="small mb-0">
                                    {team.achievements.map((achievement, idx) => (
                                      <li key={idx}>{achievement}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </Card.Body>
                            <Card.Footer>
                              <Button variant="outline-primary" size="sm">
                                Contact Coach
                              </Button>
                            </Card.Footer>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>

                  {/* Facilities Tab */}
                  <Tab.Pane eventKey="facilities">
                    <Row>
                      {facilities.map((facility, index) => (
                        <Col md={6} key={index} className="mb-4">
                          <Card>
                            <Card.Body>
                              <h6>{facility.name}</h6>
                              <p className="text-muted">{facility.description}</p>
                              <div className="mb-2">
                                <small>
                                  <strong>Hours:</strong> {facility.hours}
                                </small>
                              </div>
                              <div className="mb-2">
                                <small>
                                  <strong>Booking:</strong> {facility.booking}
                                </small>
                              </div>
                              <Button variant="outline-primary" size="sm">
                                Check Availability
                              </Button>
                            </Card.Body>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>

                  {/* Events Tab */}
                  <Tab.Pane eventKey="events">
                    <Table responsive striped>
                      <thead>
                        <tr>
                          <th>Event</th>
                          <th>Date</th>
                          <th>Time</th>
                          <th>Location</th>
                          <th>Participants</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {upcomingEvents.map(event => (
                          <tr key={event.id}>
                            <td><strong>{event.event}</strong></td>
                            <td>{event.date}</td>
                            <td>{event.time}</td>
                            <td>{event.location}</td>
                            <td>{event.participants}</td>
                            <td>
                              <Button variant="outline-primary" size="sm">
                                View Details
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </Tab.Pane>

                  {/* Achievements Tab */}
                  <Tab.Pane eventKey="achievements">
                    <Row>
                      <Col md={6}>
                        <Card className="mb-4">
                          <Card.Header>
                            <h6 className="mb-0">Recent Achievements 2023-2024</h6>
                          </Card.Header>
                          <Card.Body>
                            <ul>
                              <li>County Football Champions - Senior Boys</li>
                              <li>Regional Swimming Gold Medals - 5 events</li>
                              <li>National Track & Field Qualifiers - 8 students</li>
                              <li>Basketball City League Winners - Girls Team</li>
                              <li>Volleyball Tournament Champions</li>
                              <li>Sportsmanship Award - County Athletics</li>
                            </ul>
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col md={6}>
                        <Card className="mb-4">
                          <Card.Header>
                            <h6 className="mb-0">Athlete of the Month</h6>
                          </Card.Header>
                          <Card.Body className="text-center">
                            <div className="mb-3">
                              <img 
                                src="/images/athlete-month.jpg" 
                                alt="Athlete of the Month"
                                className="rounded-circle"
                                style={{ width: '100px', height: '100px', objectFit: 'cover' }}
                              />
                            </div>
                            <h6>Sarah Wanjiku</h6>
                            <p className="text-muted mb-2">Grade 11 - Swimming</p>
                            <p>
                              "Sarah broke two school records in freestyle and 
                              represented the school at national level."
                            </p>
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>
                  </Tab.Pane>
                </Tab.Content>
              </Card.Body>
            </Card>
          </Tab.Container>

          {/* Sports Philosophy */}
          <Card className="mt-4">
            <Card.Header>
              <h5 className="mb-0">Our Sports Philosophy</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={8}>
                  <p>
                    At Delvok Academy, we believe sports are essential for holistic development. 
                    Our athletics program focuses on:
                  </p>
                  <ul>
                    <li>Developing physical fitness and healthy lifestyles</li>
                    <li>Building teamwork and leadership skills</li>
                    <li>Promoting sportsmanship and fair play</li>
                    <li>Balancing academic excellence with athletic achievement</li>
                    <li>Providing opportunities for all skill levels</li>
                  </ul>
                </Col>
                <Col md={4} className="text-center">
                  <div className="bg-light rounded p-4">
                    <h6>Sports Participation</h6>
                    <div className="mb-3">
                      <h3 className="text-primary">85%</h3>
                      <small>Students in Sports</small>
                    </div>
                    <Button variant="primary">
                      Download Sports Calendar
                    </Button>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Athletics;