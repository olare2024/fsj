import React from 'react';
import { Container, Row, Col, Card, Table, Badge, Alert, ListGroup } from 'react-bootstrap';

const Requirements = () => {
  const ageRequirements = [
    { grade: 'Grade 1', age: '6 years by August', curriculum: 'CBC' },
    { grade: 'Grade 2', age: '7 years by August', curriculum: 'CBC' },
    { grade: 'Grade 3', age: '8 years by August', curriculum: 'CBC' },
    { grade: 'Grade 4', age: '9 years by August', curriculum: 'CBC' },
    { grade: 'Grade 5', age: '10 years by August', curriculum: 'CBC' },
    { grade: 'Grade 6', age: '11 years by August', curriculum: 'CBC' },
    { grade: 'Grade 7', age: '12 years by August', curriculum: 'CBC' },
    { grade: 'IGCSE Year 1', age: '14+ years', curriculum: 'Cambridge' },
    { grade: 'AS Level', age: '16+ years', curriculum: 'Cambridge' },
    { grade: 'A Level', age: '17+ years', curriculum: 'Cambridge' }
  ];

  const documentRequirements = [
    {
      document: 'Birth Certificate',
      description: 'Original or certified copy',
      required: 'All applicants'
    },
    {
      document: 'Previous School Reports',
      description: 'Last 2 years academic reports',
      required: 'All applicants'
    },
    {
      document: 'Transfer Certificate',
      description: 'From previous school',
      required: 'All transferring students'
    },
    {
      document: 'Passport Photos',
      description: '4 recent passport-sized photos',
      required: 'All applicants'
    },
    {
      document: 'Medical Form',
      description: 'Completed school medical form',
      required: 'All applicants'
    },
    {
      document: 'Passport Copy',
      description: 'For international students',
      required: 'International students only'
    }
  ];

  const academicRequirements = [
    {
      level: 'CBC Lower Primary (1-3)',
      requirements: [
        'Readiness assessment',
        'Previous preschool reports',
        'Age requirement met'
      ]
    },
    {
      level: 'CBC Upper Primary (4-6)',
      requirements: [
        'Satisfactory performance in previous grade',
        'Mathematics and literacy assessment',
        'Good conduct report'
      ]
    },
    {
      level: 'Junior Secondary (7-9)',
      requirements: [
        'KCPE results or equivalent',
        'Mathematics and English proficiency test',
        'Interview with academic staff'
      ]
    },
    {
      level: 'Cambridge IGCSE',
      requirements: [
        'Completion of Grade 9 or equivalent',
        'English language proficiency test',
        'Mathematics and science assessment',
        'Personal statement'
      ]
    },
    {
      level: 'Cambridge A-Level',
      requirements: [
        '5+ IGCSE passes (Grades A*-C)',
        'B+ average in relevant subjects',
        'Interview with department heads',
        'Academic reference letters'
      ]
    }
  ];

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Admission Requirements</h1>
            <p className="lead">Understanding the requirements for joining Delvok Academy</p>
          </div>

          <Alert variant="info" className="mb-4">
            <Alert.Heading>Important Notice</Alert.Heading>
            Admission to Delvok Academy is competitive and based on academic merit, 
            character, and potential to contribute to our school community. Meeting 
            minimum requirements does not guarantee admission.
          </Alert>

          {/* Age Requirements */}
          <Card className="mb-4">
            <Card.Header>
              <h4 className="mb-0">
                <i className="bi bi-calendar-check text-primary me-2"></i>
                Age Requirements
              </h4>
            </Card.Header>
            <Card.Body>
              <Table responsive striped>
                <thead>
                  <tr>
                    <th>Grade Level</th>
                    <th>Age Requirement</th>
                    <th>Curriculum</th>
                  </tr>
                </thead>
                <tbody>
                  {ageRequirements.map((req, index) => (
                    <tr key={index}>
                      <td><strong>{req.grade}</strong></td>
                      <td>{req.age}</td>
                      <td>
                        <Badge bg={req.curriculum === 'CBC' ? 'success' : 'info'}>
                          {req.curriculum}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {/* Document Requirements */}
          <Card className="mb-4">
            <Card.Header>
              <h4 className="mb-0">
                <i className="bi bi-folder-check text-success me-2"></i>
                Required Documents
              </h4>
            </Card.Header>
            <Card.Body>
              <Table responsive striped>
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Description</th>
                    <th>Required For</th>
                  </tr>
                </thead>
                <tbody>
                  {documentRequirements.map((doc, index) => (
                    <tr key={index}>
                      <td><strong>{doc.document}</strong></td>
                      <td>{doc.description}</td>
                      <td>{doc.required}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          <Row>
            {/* Academic Requirements */}
            <Col lg={8}>
              <Card className="mb-4">
                <Card.Header>
                  <h4 className="mb-0">
                    <i className="bi bi-mortarboard text-warning me-2"></i>
                    Academic Requirements by Level
                  </h4>
                </Card.Header>
                <Card.Body>
                  {academicRequirements.map((level, index) => (
                    <div key={index} className="mb-4">
                      <h5 className="text-primary">{level.level}</h5>
                      <ListGroup variant="flush">
                        {level.requirements.map((req, reqIndex) => (
                          <ListGroup.Item key={reqIndex} className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            {req}
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                      {index < academicRequirements.length - 1 && <hr />}
                    </div>
                  ))}
                </Card.Body>
              </Card>
            </Col>

            {/* Additional Information */}
            <Col lg={4}>
              <Card className="mb-4">
                <Card.Header>
                  <h5 className="mb-0">Application Process</h5>
                </Card.Header>
                <Card.Body>
                  <ListGroup variant="flush">
                    <ListGroup.Item>
                      <strong>1. Submit Application</strong>
                      <br />
                      Complete online application form
                    </ListGroup.Item>
                    <ListGroup.Item>
                      <strong>2. Assessment</strong>
                      <br />
                      Academic testing and interviews
                    </ListGroup.Item>
                    <ListGroup.Item>
                      <strong>3. Document Review</strong>
                      <br />
                      Verification of submitted documents
                    </ListGroup.Item>
                    <ListGroup.Item>
                      <strong>4. Admission Decision</strong>
                      <br />
                      Committee review and decision
                    </ListGroup.Item>
                    <ListGroup.Item>
                      <strong>5. Enrollment</strong>
                      <br />
                      Fee payment and registration
                    </ListGroup.Item>
                  </ListGroup>
                </Card.Body>
              </Card>

              <Card className="mb-4">
                <Card.Header>
                  <h5 className="mb-0">Key Dates</h5>
                </Card.Header>
                <Card.Body>
                  <ListGroup variant="flush">
                    <ListGroup.Item>
                      <strong>Application Opens:</strong>
                      <br />
                      January 15, 2024
                    </ListGroup.Item>
                    <ListGroup.Item>
                      <strong>Priority Deadline:</strong>
                      <br />
                      March 31, 2024
                    </ListGroup.Item>
                    <ListGroup.Item>
                      <strong>Final Deadline:</strong>
                      <br />
                      May 15, 2024
                    </ListGroup.Item>
                    <ListGroup.Item>
                      <strong>Academic Year Starts:</strong>
                      <br />
                      September 2, 2024
                    </ListGroup.Item>
                  </ListGroup>
                </Card.Body>
              </Card>

              <Card>
                <Card.Header>
                  <h5 className="mb-0">Need Help?</h5>
                </Card.Header>
                <Card.Body>
                  <p>Contact our admissions team:</p>
                  <ul className="list-unstyled">
                    <li>
                      <i className="bi bi-envelope me-2"></i>
                      admissions@delvok.ac.ke
                    </li>
                    <li>
                      <i className="bi bi-phone me-2"></i>
                      +254 700 123 456
                    </li>
                    <li>
                      <i className="bi bi-clock me-2"></i>
                      Mon-Fri, 8:00 AM - 4:00 PM
                    </li>
                  </ul>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default Requirements;