import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Form, Button, Alert } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Grades = () => {
  const { currentUser } = useAuth();
  const [grades, setGrades] = useState([]);
  const [selectedTerm, setSelectedTerm] = useState('Term 1');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    const fetchGrades = async () => {
      setLoading(true);
      // Mock data based on user role
      const mockGrades = currentUser.role === 'student' 
        ? [
            { subject: 'Mathematics', assignment: 85, exam: 90, total: 87.5, grade: 'A', comments: 'Excellent work' },
            { subject: 'English', assignment: 78, exam: 82, total: 80, grade: 'B+', comments: 'Good improvement' },
            { subject: 'Science', assignment: 92, exam: 88, total: 90, grade: 'A', comments: 'Outstanding performance' },
            { subject: 'Kiswahili', assignment: 75, exam: 80, total: 77.5, grade: 'B', comments: 'Satisfactory' },
            { subject: 'Social Studies', assignment: 88, exam: 85, total: 86.5, grade: 'A-', comments: 'Very good' },
          ]
        : [
            // Teacher view with multiple students
            { student: 'John Doe', mathematics: 'A', english: 'B+', science: 'A', kiswahili: 'B', socialStudies: 'A-' },
            { student: 'Jane Smith', mathematics: 'B+', english: 'A', science: 'A-', kiswahili: 'A', socialStudies: 'B+' },
            { student: 'Mike Johnson', mathematics: 'A-', english: 'B', science: 'B+', kiswahili: 'B', socialStudies: 'A' },
          ];
      
      setTimeout(() => {
        setGrades(mockGrades);
        setLoading(false);
      }, 1000);
    };

    fetchGrades();
  }, [currentUser, selectedTerm]);

  const getGradeColor = (grade) => {
    switch(grade) {
      case 'A': return 'success';
      case 'B+': return 'primary';
      case 'B': return 'info';
      case 'C+': return 'warning';
      case 'C': return 'warning';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading grades...</span>
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
            <h2>Academic Grades</h2>
            <Form.Select 
              style={{ width: '200px' }} 
              value={selectedTerm}
              onChange={(e) => setSelectedTerm(e.target.value)}
            >
              <option>Term 1</option>
              <option>Term 2</option>
              <option>Term 3</option>
            </Form.Select>
          </div>

          <Card>
            <Card.Header>
              <h5 className="mb-0">
                {currentUser.role === 'student' ? 'My Grades' : 'Class Grades'} - {selectedTerm}
              </h5>
            </Card.Header>
            <Card.Body>
              {currentUser.role === 'student' ? (
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Assignment (%)</th>
                      <th>Exam (%)</th>
                      <th>Total (%)</th>
                      <th>Grade</th>
                      <th>Teacher Comments</th>
                    </tr>
                  </thead>
                  <tbody>
                    {grades.map((grade, index) => (
                      <tr key={index}>
                        <td><strong>{grade.subject}</strong></td>
                        <td>{grade.assignment}</td>
                        <td>{grade.exam}</td>
                        <td><strong>{grade.total}</strong></td>
                        <td>
                          <Badge bg={getGradeColor(grade.grade)}>
                            {grade.grade}
                          </Badge>
                        </td>
                        <td>{grade.comments}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      <th>Student Name</th>
                      <th>Mathematics</th>
                      <th>English</th>
                      <th>Science</th>
                      <th>Kiswahili</th>
                      <th>Social Studies</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {grades.map((student, index) => (
                      <tr key={index}>
                        <td><strong>{student.student}</strong></td>
                        <td><Badge bg={getGradeColor(student.mathematics)}>{student.mathematics}</Badge></td>
                        <td><Badge bg={getGradeColor(student.english)}>{student.english}</Badge></td>
                        <td><Badge bg={getGradeColor(student.science)}>{student.science}</Badge></td>
                        <td><Badge bg={getGradeColor(student.kiswahili)}>{student.kiswahili}</Badge></td>
                        <td><Badge bg={getGradeColor(student.socialStudies)}>{student.socialStudies}</Badge></td>
                        <td>
                          <Button variant="outline-primary" size="sm">
                            Edit
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>

          {currentUser.role === 'student' && (
            <Row className="mt-4">
              <Col md={6}>
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Grade Summary</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Average Grade:</span>
                      <Badge bg="primary">B+</Badge>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Overall Percentage:</span>
                      <strong>84.2%</strong>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span>Class Position:</span>
                      <strong>5/45</strong>
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

export default Grades;