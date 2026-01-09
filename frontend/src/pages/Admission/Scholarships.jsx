import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, Button, Alert, Form, Table } from 'react-bootstrap';

const Scholarships = () => {
  const [showApplication, setShowApplication] = useState(false);

  const scholarships = [
    {
      name: 'Academic Excellence Scholarship',
      type: 'Merit-based',
      coverage: 'Up to 100% tuition',
      deadline: '2024-03-15',
      status: 'Open',
      requirements: [
        'Top 5% in national exams',
        'Maintain A- average',
        'Leadership potential',
        'Community service involvement'
      ]
    },
    {
      name: 'Sports Talent Scholarship',
      type: 'Talent-based',
      coverage: '50-75% tuition',
      deadline: '2024-04-01',
      status: 'Open',
      requirements: [
        'National level representation',
        'Commitment to school teams',
        'Good academic standing',
        'Sportsmanship qualities'
      ]
    },
    {
      name: 'Arts & Creativity Scholarship',
      type: 'Talent-based',
      coverage: '25-50% tuition',
      deadline: '2024-04-01',
      status: 'Open',
      requirements: [
        'Portfolio of creative work',
        'Audition or presentation',
        'Academic potential',
        'Willingness to contribute to school arts'
      ]
    },
    {
      name: 'Community Leadership Scholarship',
      type: 'Leadership-based',
      coverage: '30-60% tuition',
      deadline: '2024-03-30',
      status: 'Open',
      requirements: [
        'Demonstrated community service',
        'Leadership roles held',
        'Strong recommendation letters',
        'Interview performance'
      ]
    },
    {
      name: 'STEM Innovation Scholarship',
      type: 'Merit-based',
      coverage: 'Up to 75% tuition',
      deadline: '2024-04-15',
      status: 'Open',
      requirements: [
        'Excellent math/science grades',
        'STEM project portfolio',
        'Innovation competition participation',
        'Teacher recommendations'
      ]
    }
  ];

  const getStatusBadge = (status) => {
    return status === 'Open' 
      ? <Badge bg="success">Open</Badge>
      : <Badge bg="danger">Closed</Badge>;
  };

  const getTypeBadge = (type) => {
    const variants = {
      'Merit-based': 'primary',
      'Talent-based': 'info',
      'Leadership-based': 'warning',
      'Need-based': 'success'
    };
    return <Badge bg={variants[type] || 'secondary'}>{type}</Badge>;
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Scholarships & Financial Aid</h1>
            <p className="lead">Investing in talented and deserving students</p>
          </div>

          <Alert variant="info" className="mb-4">
            <Alert.Heading>Scholarship Opportunities</Alert.Heading>
            Delvok Academy is committed to making quality education accessible through 
            various scholarship programs. We believe in nurturing talent and rewarding 
            excellence across academic, sports, arts, and leadership domains.
          </Alert>

          {/* Scholarship Cards */}
          <Row className="mb-4">
            {scholarships.map((scholarship, index) => (
              <Col md={6} lg={4} key={index} className="mb-4">
                <Card className="h-100">
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    {getTypeBadge(scholarship.type)}
                    {getStatusBadge(scholarship.status)}
                  </Card.Header>
                  <Card.Body>
                    <h5 className="card-title text-primary">{scholarship.name}</h5>
                    <p className="card-text">
                      <strong>Coverage:</strong> {scholarship.coverage}
                    </p>
                    <p className="card-text">
                      <strong>Deadline:</strong> {scholarship.deadline}
                    </p>
                    
                    <h6>Requirements:</h6>
                    <ul className="small">
                      {scholarship.requirements.map((req, idx) => (
                        <li key={idx}>{req}</li>
                      ))}
                    </ul>
                  </Card.Body>
                  <Card.Footer>
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => setShowApplication(true)}
                    >
                      Apply Now
                    </Button>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>

          {/* Scholarship Statistics */}
          <Row className="mb-4">
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-primary">25+</h3>
                  <p className="text-muted mb-0">Scholarships Awarded</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-success">KSh 15M+</h3>
                  <p className="text-muted mb-0">Total Value</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-info">5</h3>
                  <p className="text-muted mb-0">Scholarship Types</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h3 className="text-warning">85%</h3>
                  <p className="text-muted mb-0">Renewal Rate</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Application Process */}
          <Card className="mb-4">
            <Card.Header>
              <h4 className="mb-0">Application Process</h4>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h6>Step-by-Step Guide</h6>
                  <Table responsive>
                    <tbody>
                      <tr>
                        <td><strong>1. Review</strong></td>
                        <td>Check eligibility and requirements</td>
                      </tr>
                      <tr>
                        <td><strong>2. Prepare</strong></td>
                        <td>Gather required documents</td>
                      </tr>
                      <tr>
                        <td><strong>3. Apply</strong></td>
                        <td>Submit online application</td>
                      </tr>
                      <tr>
                        <td><strong>4. Assessment</strong></td>
                        <td>Tests, interviews, or auditions</td>
                      </tr>
                      <tr>
                        <td><strong>5. Decision</strong></td>
                        <td>Committee review and award</td>
                      </tr>
                    </tbody>
                  </Table>
                </Col>
                <Col md={6}>
                  <h6>Required Documents</h6>
                  <ul>
                    <li>Completed application form</li>
                    <li>Academic transcripts</li>
                    <li>Recommendation letters (2)</li>
                    <li>Personal statement</li>
                    <li>Portfolio (for talent-based)</li>
                    <li>Financial information (if applicable)</li>
                  </ul>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Scholarship Application Form */}
          {showApplication && (
            <Card className="mb-4">
              <Card.Header>
                <div className="d-flex justify-content-between align-items-center">
                  <h4 className="mb-0">Scholarship Application</h4>
                  <Button 
                    variant="outline-secondary" 
                    size="sm"
                    onClick={() => setShowApplication(false)}
                  >
                    Close
                  </Button>
                </div>
              </Card.Header>
              <Card.Body>
                <Form>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Select Scholarship</Form.Label>
                        <Form.Select required>
                          <option value="">Choose scholarship...</option>
                          {scholarships.map((scholarship, index) => (
                            <option key={index} value={scholarship.name}>
                              {scholarship.name}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Current Grade Level</Form.Label>
                        <Form.Select required>
                          <option value="">Select grade...</option>
                          <option value="grade6">Grade 6</option>
                          <option value="grade9">Grade 9</option>
                          <option value="igcse">IGCSE</option>
                          <option value="alevel">A Level</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  </Row>

                  <Form.Group className="mb-3">
                    <Form.Label>Personal Statement</Form.Label>
                    <Form.Control 
                      as="textarea" 
                      rows={4}
                      placeholder="Explain why you deserve this scholarship and how you will contribute to the school community..."
                      required
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Upload Supporting Documents</Form.Label>
                    <Form.Control type="file" multiple />
                    <Form.Text className="text-muted">
                      Upload academic records, recommendation letters, portfolio, etc.
                    </Form.Text>
                  </Form.Group>

                  <div className="d-flex gap-2">
                    <Button variant="primary" type="submit">
                      Submit Application
                    </Button>
                    <Button 
                      variant="outline-secondary"
                      onClick={() => setShowApplication(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </Form>
              </Card.Body>
            </Card>
          )}

          {/* FAQ Section */}
          <Card>
            <Card.Header>
              <h4 className="mb-0">Frequently Asked Questions</h4>
            </Card.Header>
            <Card.Body>
              <h6>Can I apply for multiple scholarships?</h6>
              <p className="mb-3">
                Yes, students can apply for multiple scholarships, but can only receive one scholarship award.
              </p>

              <h6>Are scholarships renewable?</h6>
              <p className="mb-3">
                Most scholarships are renewable annually, subject to maintaining academic performance 
                and meeting scholarship conditions.
              </p>

              <h6>When will I know the outcome?</h6>
              <p className="mb-3">
                Scholarship decisions are typically communicated within 4-6 weeks after the application deadline.
              </p>

              <h6>Can international students apply?</h6>
              <p className="mb-0">
                Yes, international students are eligible for most scholarship programs, though some may have specific requirements.
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Scholarships;