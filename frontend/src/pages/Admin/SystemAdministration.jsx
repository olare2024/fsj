// src/pages/Admin/SystemAdministration.jsx
import React, { useState } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Form, Alert } from 'react-bootstrap';

const SystemAdministration = () => {
  const [systemSettings, setSystemSettings] = useState({
    siteName: 'NextGen School System',
    maintenanceMode: false,
    emailNotifications: true,
    autoBackup: true,
    backupFrequency: 'daily'
  });

  const [serverStats, setServerStats] = useState({
    cpuUsage: '45%',
    memoryUsage: '68%',
    diskUsage: '72%',
    uptime: '99.9%'
  });

  const handleSettingChange = (key, value) => {
    setSystemSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <h1>System Administration</h1>
          <p className="text-muted">Manage system settings and server configuration</p>
        </Col>
      </Row>

      <Row>
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0">System Settings</h5>
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Site Name</Form.Label>
                  <Form.Control
                    type="text"
                    value={systemSettings.siteName}
                    onChange={(e) => handleSettingChange('siteName', e.target.value)}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    label="Maintenance Mode"
                    checked={systemSettings.maintenanceMode}
                    onChange={(e) => handleSettingChange('maintenanceMode', e.target.checked)}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    label="Email Notifications"
                    checked={systemSettings.emailNotifications}
                    onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    label="Automatic Backup"
                    checked={systemSettings.autoBackup}
                    onChange={(e) => handleSettingChange('autoBackup', e.target.checked)}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Backup Frequency</Form.Label>
                  <Form.Select
                    value={systemSettings.backupFrequency}
                    onChange={(e) => handleSettingChange('backupFrequency', e.target.value)}
                  >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </Form.Select>
                </Form.Group>

                <Button variant="primary">Save Settings</Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Server Status</h5>
            </Card.Header>
            <Card.Body>
              <Table borderless>
                <tbody>
                  <tr>
                    <td><strong>CPU Usage</strong></td>
                    <td>{serverStats.cpuUsage}</td>
                    <td>
                      <Badge bg={serverStats.cpuUsage < '50%' ? 'success' : 'warning'}>
                        {serverStats.cpuUsage < '50%' ? 'Normal' : 'High'}
                      </Badge>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Memory Usage</strong></td>
                    <td>{serverStats.memoryUsage}</td>
                    <td>
                      <Badge bg={serverStats.memoryUsage < '70%' ? 'success' : 'warning'}>
                        {serverStats.memoryUsage < '70%' ? 'Normal' : 'High'}
                      </Badge>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Disk Usage</strong></td>
                    <td>{serverStats.diskUsage}</td>
                    <td>
                      <Badge bg={serverStats.diskUsage < '80%' ? 'success' : 'warning'}>
                        {serverStats.diskUsage < '80%' ? 'Normal' : 'High'}
                      </Badge>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Uptime</strong></td>
                    <td>{serverStats.uptime}</td>
                    <td>
                      <Badge bg="success">Stable</Badge>
                    </td>
                  </tr>
                </tbody>
              </Table>

              <div className="mt-4">
                <h6>Quick Actions</h6>
                <div className="d-grid gap-2">
                  <Button variant="outline-primary">Clear Cache</Button>
                  <Button variant="outline-warning">Run Backup</Button>
                  <Button variant="outline-danger">Restart Services</Button>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default SystemAdministration;