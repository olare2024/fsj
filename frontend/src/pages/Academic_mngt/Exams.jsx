import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Alert, ProgressBar } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Exams = () => {
  const { currentUser } = useAuth();
  const [exams, setExams] = useState([]);
  const [upcomingExams, setUpcomingExams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchExams = async () => {
      setLoading(true);
      
      const mockExams = [
        {
          id: 1,
          name: 'End of Term 1 Examinations',
          subject: 'All Subjects',
          date: '2024-03-15',
          time: '08:00 AM - 04:00 PM',
          room: 'Various',
          type: 'Major',
          status: 'completed',
          score: '85%'
        },
        {
          id: 2,
          name: 'Mathematics Mid-Term',
          subject: 'Mathematics',
          date: '2024-02-10',
          time: '09:00 AM - 11:00 AM',
          room: 'Room 101',
          type: 'Minor',
          status: 'upcoming',
          score: '-'
        },
        {
          id: 3,
          name: 'Science Practical',
          subject: 'Science',
          date: '2024-02-15',
          time: '10:00 AM - 12:00 PM',
          room: 'Lab 1',
          type: 'Practical',
          status: 'upcoming',
          score: '-'
        },
      ];

      const mockUpcoming = [
        {
          id: 2,
          name: 'Mathematics Mid-Term',
          subject: 'Mathematics',
          date: '2024-02-10',
          daysLeft: 5
        },
        {
          id: 3,
          name: 'Science Practical',
          subject: 'Science',
          date: '2024-02-15',
          daysLeft: 10
        },
      ];

      setTimeout(() => {
        setExams(mockExams);
        setUpcomingExams(mockUpcoming);
        setLoading(false);
      }, 1000);
    };

    fetchExams();
  }, []);

  const getStatusBadge = (status) => {
    switch(status) {
      case 'completed': return <Badge bg="success">Completed</Badge>;
      case 'upcoming': return <Badge bg="warning">Upcoming</Badge>;
      case 'ongoing': return <Badge bg="info">Ongoing</Badge>;
      default: return <Badge bg="secondary">Scheduled</Badge>;
    }
  };

  const getTypeBadge = (type) => {
    switch(type) {
      case 'Major': return <Badge bg="danger">Major</Badge>;
      case 'Minor': return <Badge bg="warning">Minor</Badge>;
      case 'Practical': return <Badge bg="info">Practical</Badge>;
      default: return <Badge bg="secondary">Quiz</Badge>;
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading exams...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <h2 className="mb-4">Examination Center</h2>

          {currentUser.role === 'student' && upcomingExams.length > 0 && (
            <Alert variant="info" className="mb-4">
              <Alert.Heading>Upcoming Exams</Alert.Heading>
              You have {upcomingExams.length} upcoming exam(s). Start preparing!
            </Alert>
          )}

          <Row className="mb-4">
            {currentUser.role === 'student' && upcomingExams.map(exam => (
              <Col md={6} lg={4} key={exam.id} className="mb-3">
                <Card className="h-100">
                  <Card.Header>
                    <Badge bg="warning" className="float-end">
                      {exam.daysLeft} days
                    </Badge>
                    <h6 className="mb-0">{exam.subject}</h6>
                  </Card.Header>
                  <Card.Body>
                    <h6>{exam.name}</h6>
                    <p className="mb-1"><small>Date: {exam.date}</small></p>
                    <ProgressBar now={100 - (exam.daysLeft / 30 * 100)} variant="success" />
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>

          <Card>
            <Card.Header>
              <h5 className="mb-0">
                {currentUser.role === 'student' ? 'My Exam Schedule' : 'Exam Schedule'}
              </h5>
            </Card.Header>
            <Card.Body>
              <Table responsive striped hover>
                <thead>
                  <tr>
                    <th>Exam Name</th>
                    <th>Subject</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Room</th>
                    <th>Type</th>
                    <th>Status</th>
                    {currentUser.role === 'student' && <th>Score</th>}
                  </tr>
                </thead>
                <tbody>
                  {exams.map((exam) => (
                    <tr key={exam.id}>
                      <td><strong>{exam.name}</strong></td>
                      <td>{exam.subject}</td>
                      <td>{exam.date}</td>
                      <td>{exam.time}</td>
                      <td>{exam.room}</td>
                      <td>{getTypeBadge(exam.type)}</td>
                      <td>{getStatusBadge(exam.status)}</td>
                      {currentUser.role === 'student' && (
                        <td>
                          {exam.score !== '-' ? (
                            <Badge bg="success">{exam.score}</Badge>
                          ) : (
                            '-'
                          )}
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {currentUser.role === 'student' && (
            <Row className="mt-4">
              <Col md={6}>
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Exam Performance Summary</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Average Score:</span>
                      <Badge bg="primary">82%</Badge>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Exams Completed:</span>
                      <strong>8</strong>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Upcoming Exams:</span>
                      <Badge bg="warning">3</Badge>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span>Class Rank:</span>
                      <strong>7/45</strong>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Exams;