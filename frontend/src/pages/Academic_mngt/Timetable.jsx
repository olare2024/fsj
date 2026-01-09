import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Form } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Timetable = () => {
  const { currentUser } = useAuth();
  const [timetable, setTimetable] = useState([]);
  const [selectedDay, setSelectedDay] = useState('Monday');
  const [loading, setLoading] = useState(true);

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const periods = [
    { time: '07:30 - 08:30', number: 1 },
    { time: '08:30 - 09:30', number: 2 },
    { time: '09:30 - 10:30', number: 3 },
    { time: '10:30 - 11:00', number: 'Break' },
    { time: '11:00 - 12:00', number: 4 },
    { time: '12:00 - 13:00', number: 5 },
    { time: '13:00 - 14:00', number: 'Lunch' },
    { time: '14:00 - 15:00', number: 6 },
    { time: '15:00 - 16:00', number: 7 },
  ];

  useEffect(() => {
    const fetchTimetable = async () => {
      setLoading(true);
      
      const mockTimetable = {
        'Monday': [
          { period: 1, subject: 'Mathematics', teacher: 'Mr. Kamau', room: 'Room 101' },
          { period: 2, subject: 'English', teacher: 'Mrs. Achieng', room: 'Room 102' },
          { period: 3, subject: 'Science', teacher: 'Dr. Otieno', room: 'Lab 1' },
          { period: 'Break', subject: 'Break', teacher: '', room: '' },
          { period: 4, subject: 'Kiswahili', teacher: 'Mr. Mwangi', room: 'Room 103' },
          { period: 5, subject: 'Social Studies', teacher: 'Ms. Wanjiku', room: 'Room 104' },
          { period: 'Lunch', subject: 'Lunch', teacher: '', room: '' },
          { period: 6, subject: 'Physical Education', teacher: 'Coach Kipchoge', room: 'Field' },
          { period: 7, subject: 'Music', teacher: 'Mrs. Nyong\'o', room: 'Music Room' },
        ],
        'Tuesday': [
          { period: 1, subject: 'English', teacher: 'Mrs. Achieng', room: 'Room 102' },
          { period: 2, subject: 'Mathematics', teacher: 'Mr. Kamau', room: 'Room 101' },
          { period: 3, subject: 'Geography', teacher: 'Ms. Wanjiku', room: 'Room 104' },
          { period: 'Break', subject: 'Break', teacher: '', room: '' },
          { period: 4, subject: 'Science', teacher: 'Dr. Otieno', room: 'Lab 1' },
          { period: 5, subject: 'Computer Studies', teacher: 'Mr. Tech', room: 'Computer Lab' },
          { period: 'Lunch', subject: 'Lunch', teacher: '', room: '' },
          { period: 6, subject: 'Art', teacher: 'Mrs. Artist', room: 'Art Room' },
          { period: 7, subject: 'Club Activities', teacher: '', room: 'Various' },
        ],
        // ... similar data for other days
      };

      setTimeout(() => {
        setTimetable(mockTimetable[selectedDay] || []);
        setLoading(false);
      }, 1000);
    };

    fetchTimetable();
  }, [selectedDay]);

  const getSubjectColor = (subject) => {
    const colors = {
      'Mathematics': 'primary',
      'English': 'success',
      'Science': 'info',
      'Kiswahili': 'warning',
      'Social Studies': 'secondary',
      'Physical Education': 'danger',
      'Music': 'dark',
      'Geography': 'primary',
      'Computer Studies': 'info',
      'Art': 'warning',
    };
    return colors[subject] || 'secondary';
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading timetable...</span>
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
            <h2>School Timetable</h2>
            <Form.Select 
              style={{ width: '200px' }} 
              value={selectedDay}
              onChange={(e) => setSelectedDay(e.target.value)}
            >
              {days.map(day => (
                <option key={day} value={day}>{day}</option>
              ))}
            </Form.Select>
          </div>

          <Card>
            <Card.Header>
              <h5 className="mb-0">Class Schedule - {selectedDay}</h5>
            </Card.Header>
            <Card.Body>
              <Table responsive striped>
                <thead>
                  <tr>
                    <th>Period</th>
                    <th>Time</th>
                    <th>Subject</th>
                    <th>Teacher</th>
                    <th>Room</th>
                  </tr>
                </thead>
                <tbody>
                  {periods.map((period, index) => {
                    const schedule = timetable.find(item => item.period === period.number);
                    return (
                      <tr key={index}>
                        <td>
                          {typeof period.number === 'number' ? (
                            <Badge bg="secondary">Period {period.number}</Badge>
                          ) : (
                            <Badge bg="light" text="dark">{period.number}</Badge>
                          )}
                        </td>
                        <td>{period.time}</td>
                        <td>
                          {schedule ? (
                            <Badge bg={getSubjectColor(schedule.subject)}>
                              {schedule.subject}
                            </Badge>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td>{schedule?.teacher || '-'}</td>
                        <td>{schedule?.room || '-'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          <Row className="mt-4">
            <Col md={8}>
              <Card>
                <Card.Header>
                  <h6 className="mb-0">Weekly Overview</h6>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <thead>
                      <tr>
                        <th>Time</th>
                        {days.map(day => (
                          <th key={day}>{day}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>07:30 - 08:30</td>
                        {days.map(day => (
                          <td key={day}>
                            <Badge bg="primary" className="w-100">Math</Badge>
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td>08:30 - 09:30</td>
                        {days.map(day => (
                          <td key={day}>
                            <Badge bg="success" className="w-100">English</Badge>
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default Timetable;