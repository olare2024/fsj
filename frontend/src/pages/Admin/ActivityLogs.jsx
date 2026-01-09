// src/pages/Admin/ActivityLogs.jsx
import React, { useState } from 'react';
import { Container, Row, Col, Card, Table, Button, Form, Badge } from 'react-bootstrap';

const ActivityLogs = () => {
  const [filter, setFilter] = useState('all');
  
  const activities = [
    {
      id: 1,
      user: 'admin@school.edu',
      action: 'User Created',
      description: 'Created new student account: Emma Chen',
      timestamp: '2026-01-15 10:30:00',
      ip: '192.168.1.100',
      severity: 'info'
    },
    {
      id: 2,
      user: 'finance@school.edu',
      action: 'Payment Processed',
      description: 'Processed scholarship payment: KES 180,000',
      timestamp: '2026-01-15 09:15:00',
      ip: '192.168.1.101',
      severity: 'success'
    },
    {
      id: 3,
      user: 'system@school.edu',
      action: 'Security Alert',
      description: 'Multiple failed login attempts detected',
      timestamp: '2026-01-14 16:45:00',
      ip: '192.168.1.102',
      severity: 'warning'
    }
  ];

  const getSeverityVariant = (severity) => {
    const variants = {
      info: 'primary',
      success: 'success',
      warning: 'warning',
      error: 'danger'
    };
    return variants[severity] || 'secondary';
  };

  const filteredActivities = filter === 'all' 
    ? activities 
    : activities.filter(activity => activity.severity === filter);

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <h1>Activity Logs</h1>
          <p className="text-muted">System activity and audit trail</p>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Recent Activities</h5>
              <div className="d-flex gap-2">
                <Form.Select 
                  style={{ width: 'auto' }}
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option value="all">All Activities</option>
                  <option value="info">Info</option>
                  <option value="success">Success</option>
                  <option value="warning">Warning</option>
                </Form.Select>
                <Button variant="outline-primary">
                  Export Logs
                </Button>
              </div>
            </Card.Header>
            <Card.Body>
              <Table responsive>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>User</th>
                    <th>Action</th>
                    <th>Description</th>
                    <th>IP Address</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredActivities.map(activity => (
                    <tr key={activity.id}>
                      <td>{activity.timestamp}</td>
                      <td>{activity.user}</td>
                      <td>{activity.action}</td>
                      <td>{activity.description}</td>
                      <td>{activity.ip}</td>
                      <td>
                        <Badge bg={getSeverityVariant(activity.severity)}>
                          {activity.severity}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ActivityLogs;