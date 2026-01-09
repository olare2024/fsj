// src/pages/Admin/AnalyticsAI.jsx
import React, { useState } from 'react';
import { Container, Row, Col, Card, Table, Button, Nav, ProgressBar } from 'react-bootstrap';

const AnalyticsAI = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const analyticsData = {
    studentPerformance: [
      { subject: 'Mathematics', average: 85, improvement: '+5%' },
      { subject: 'Science', average: 78, improvement: '+3%' },
      { subject: 'English', average: 82, improvement: '+4%' }
    ],
    aiPredictions: [
      { student: 'John Doe', prediction: 'High Achiever', confidence: '92%' },
      { student: 'Jane Smith', prediction: 'Needs Support', confidence: '78%' },
      { student: 'Mike Johnson', prediction: 'Average', confidence: '85%' }
    ]
  };

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <h1>Analytics & AI Dashboard</h1>
          <p className="text-muted">AI-powered insights and predictive analytics</p>
        </Col>
      </Row>

      <Nav variant="tabs" activeKey={activeTab} onSelect={setActiveTab} className="mb-4">
        <Nav.Item>
          <Nav.Link eventKey="overview">Overview</Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="predictions">AI Predictions</Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="trends">Trend Analysis</Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="reports">Reports</Nav.Link>
        </Nav.Item>
      </Nav>

      {activeTab === 'overview' && (
        <Row>
          <Col lg={6} className="mb-4">
            <Card>
              <Card.Header>
                <h5 className="mb-0">Student Performance Analytics</h5>
              </Card.Header>
              <Card.Body>
                <Table responsive>
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Average Score</th>
                      <th>Improvement</th>
                      <th>Progress</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyticsData.studentPerformance.map((item, index) => (
                      <tr key={index}>
                        <td>{item.subject}</td>
                        <td>{item.average}%</td>
                        <td>{item.improvement}</td>
                        <td>
                          <ProgressBar now={item.average} variant={item.average > 80 ? 'success' : 'warning'} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>

          <Col lg={6} className="mb-4">
            <Card>
              <Card.Header>
                <h5 className="mb-0">AI Learning Predictions</h5>
              </Card.Header>
              <Card.Body>
                <Table responsive>
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Prediction</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyticsData.aiPredictions.map((item, index) => (
                      <tr key={index}>
                        <td>{item.student}</td>
                        <td>{item.prediction}</td>
                        <td>{item.confidence}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {activeTab === 'predictions' && (
        <Card>
          <Card.Header>
            <h5 className="mb-0">Advanced AI Predictions</h5>
          </Card.Header>
          <Card.Body>
            <p>AI-powered predictive analytics coming soon...</p>
            <Button variant="primary">Generate New Predictions</Button>
          </Card.Body>
        </Card>
      )}
    </Container>
  );
};

export default AnalyticsAI;