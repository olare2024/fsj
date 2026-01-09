import React, { useState, useEffect } from 'react';
import {
  Container, Row, Col, Card, Table, Button, Badge,
  Alert, Spinner, Form, ListGroup
} from 'react-bootstrap';
import { teacherAPI } from '../../services/teacherAPI';
import { useAuth } from '../../context/AuthContext';
import {
  CalendarIcon, ClockIcon, MapPinIcon, UsersIcon, DownloadIcon,
  BarChartIcon, ViewIcon, HomeIcon, SchoolIcon
} from '../../components/Icons';

const TeacherTimetable = () => {
  const { currentUser } = useAuth();
  const [timetable, setTimetable] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedDay, setSelectedDay] = useState('Monday');
  const [viewMode, setViewMode] = useState('weekly');

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  useEffect(() => {
    fetchTimetable();
  }, []);

  const fetchTimetable = async () => {
    try {
      setLoading(true);
      setError('');
      
      const result = await teacherAPI.getTimetable();
      if (result.success) {
        setTimetable(result.data || []);
      } else {
        setError(result.error?.message || 'Failed to load timetable');
      }
    } catch (err) {
      setError('Failed to load timetable');
    } finally {
      setLoading(false);
    }
  };

  const getPeriodsForDay = (day) => {
    return timetable.filter(period => period.day_of_week === day)
                   .sort((a, b) => a.start_time.localeCompare(b.start_time));
  };

  const getTimeDisplay = (time) => {
    return new Date(`1970-01-01T${time}`).toLocaleTimeString([], { 
      hour: '2-digit', minute: '2-digit' 
    });
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" />
          <p className="mt-3 text-muted">Loading timetable...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Teaching Timetable</h1>
              <p className="text-muted mb-0">Your weekly teaching schedule</p>
            </div>
            <div className="d-flex gap-2">
              <Button variant="outline-primary">
                <DownloadIcon className="me-2" size={16} />
                Export
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Row>
        <Col>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">
                  <CalendarIcon className="me-2" size={20} />
                  Weekly Schedule
                </h5>
                <div>
                  <Button
                    variant={viewMode === 'weekly' ? 'primary' : 'outline-primary'}
                    size="sm"
                    className="me-2"
                    onClick={() => setViewMode('weekly')}
                  >
                    Weekly View
                  </Button>
                  <Button
                    variant={viewMode === 'daily' ? 'primary' : 'outline-primary'}
                    size="sm"
                    onClick={() => setViewMode('daily')}
                  >
                    Daily View
                  </Button>
                </div>
              </div>
            </Card.Header>
            <Card.Body className="p-0">
              {viewMode === 'weekly' ? (
                <div className="table-responsive">
                  <Table className="mb-0">
                    <thead className="bg-light">
                      <tr>
                        <th style={{ width: '120px' }}>Time</th>
                        {daysOfWeek.map(day => (
                          <th key={day}>{day}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {Array.from({ length: 9 }, (_, i) => {
                        const hour = i + 8;
                        const timeSlot = `${hour.toString().padStart(2, '0')}:00`;
                        
                        return (
                          <tr key={timeSlot}>
                            <td className="bg-light fw-semibold">{timeSlot}</td>
                            {daysOfWeek.map(day => {
                              const period = timetable.find(p => 
                                p.day_of_week === day && 
                                p.start_time.startsWith(timeSlot.slice(0, 2))
                              );
                              
                              return (
                                <td key={day} style={{ minHeight: '80px', verticalAlign: 'top' }}>
                                  {period ? (
                                    <div className="p-2 border rounded bg-primary text-white">
                                      <div className="fw-bold small">{period.subject?.name}</div>
                                      <div className="small">{period.class_group?.name}</div>
                                      <div className="small">
                                        <MapPinIcon size={12} className="me-1" />
                                        Room {period.room_number}
                                      </div>
                                      <div className="small">
                                        <ClockIcon size={12} className="me-1" />
                                        {getTimeDisplay(period.start_time)}-{getTimeDisplay(period.end_time)}
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="text-muted text-center small py-3">
                                      Free Period
                                    </div>
                                  )}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </Table>
                </div>
              ) : (
                <Row className="g-3 p-3">
                  <Col md={3}>
                    <ListGroup>
                      {daysOfWeek.map(day => (
                        <ListGroup.Item
                          key={day}
                          action
                          active={selectedDay === day}
                          onClick={() => setSelectedDay(day)}
                          className="d-flex justify-content-between align-items-center"
                        >
                          {day}
                          <Badge bg={selectedDay === day ? 'light' : 'primary'} text={selectedDay === day ? 'dark' : 'white'}>
                            {getPeriodsForDay(day).length}
                          </Badge>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  </Col>
                  <Col md={9}>
                    <h5>{selectedDay}'s Schedule</h5>
                    {getPeriodsForDay(selectedDay).length > 0 ? (
                      getPeriodsForDay(selectedDay).map((period, index) => (
                        <Card key={index} className="mb-3">
                          <Card.Body>
                            <Row>
                              <Col md={8}>
                                <h6 className="mb-1">{period.subject?.name}</h6>
                                <p className="mb-1 text-muted">
                                  <UsersIcon className="me-1" size={14} />
                                  {period.class_group?.name}
                                </p>
                                <small className="text-muted">
                                  <MapPinIcon className="me-1" size={12} />
                                  Room {period.room_number}
                                </small>
                              </Col>
                              <Col md={4} className="text-end">
                                <div className="fw-bold text-primary">
                                  {getTimeDisplay(period.start_time)} - {getTimeDisplay(period.end_time)}
                                </div>
                                <Badge bg="light" text="dark" className="mt-1">
                                  {period.period_type}
                                </Badge>
                              </Col>
                            </Row>
                          </Card.Body>
                        </Card>
                      ))
                    ) : (
                      <div className="text-center py-5 text-muted">
                        <CalendarIcon size={48} className="mb-3" />
                        <h5>No classes scheduled</h5>
                        <p>Enjoy your free day!</p>
                      </div>
                    )}
                  </Col>
                </Row>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default TeacherTimetable;