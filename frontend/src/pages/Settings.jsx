import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, Tab, Nav, Modal } from 'react-bootstrap';
import { useAuth } from '../context/AuthContext';

const Settings = () => {
  const { currentUser, updateSettings, changePassword } = useAuth();
  const [activeTab, setActiveTab] = useState('account');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [settings, setSettings] = useState({
    // Account Settings
    language: 'en',
    timezone: 'Africa/Nairobi',
    dateFormat: 'DD/MM/YYYY',
    
    // Privacy Settings
    profileVisibility: 'school',
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    
    // Security Settings
    twoFactorAuth: false,
    sessionTimeout: 60,
    
    // Communication Preferences
    newsletter: true,
    eventReminders: true,
    gradeAlerts: true,
    assignmentAlerts: true
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  useEffect(() => {
    if (currentUser?.settings) {
      setSettings(currentUser.settings);
    }
  }, [currentUser]);

  const handleSettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      await updateSettings(settings);
      setMessage('Settings updated successfully!');
    } catch (err) {
      setError('Failed to update settings. Please try again.');
      console.error('Settings update error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('New passwords do not match');
      setLoading(false);
      return;
    }

    try {
      await changePassword(passwordData.currentPassword, passwordData.newPassword);
      setMessage('Password changed successfully!');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (err) {
      setError('Failed to change password. Please check your current password.');
      console.error('Password change error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = () => {
    // In a real app, this would trigger a data export
    alert('Data export request has been submitted. You will receive an email with your data shortly.');
  };

  const handleDeleteAccount = () => {
    // In a real app, this would initiate account deletion
    alert('Account deletion request has been submitted. Our team will contact you for confirmation.');
    setShowDeleteModal(false);
  };

  const passwordStrength = (password) => {
    if (!password) return 0;
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const getPasswordStrengthColor = (strength) => {
    if (strength <= 2) return 'danger';
    if (strength <= 3) return 'warning';
    return 'success';
  };

  const getPasswordStrengthText = (strength) => {
    if (strength <= 2) return 'Weak';
    if (strength <= 3) return 'Medium';
    return 'Strong';
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2>Account Settings</h2>
            <small className="text-muted">Manage your account preferences and security</small>
          </div>

          {message && (
            <Alert variant="success" className="mb-3">
              <i className="bi bi-check-circle-fill me-2"></i>
              {message}
            </Alert>
          )}

          {error && (
            <Alert variant="danger" className="mb-3">
              <i className="bi bi-exclamation-triangle-fill me-2"></i>
              {error}
            </Alert>
          )}

          <Tab.Container activeKey={activeTab} onSelect={setActiveTab}>
            <Card>
              <Card.Header>
                <Nav variant="tabs" className="card-header-tabs">
                  <Nav.Item>
                    <Nav.Link eventKey="account">
                      <i className="bi bi-gear me-2"></i>
                      Account
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="privacy">
                      <i className="bi bi-shield me-2"></i>
                      Privacy
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="security">
                      <i className="bi bi-lock me-2"></i>
                      Security
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="notifications">
                      <i className="bi bi-bell me-2"></i>
                      Notifications
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="danger">
                      <i className="bi bi-exclamation-triangle me-2"></i>
                      Danger Zone
                    </Nav.Link>
                  </Nav.Item>
                </Nav>
              </Card.Header>

              <Card.Body>
                <Tab.Content>
                  {/* Account Settings Tab */}
                  <Tab.Pane eventKey="account">
                    <Form onSubmit={handleSaveSettings}>
                      <Row>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>Language</Form.Label>
                            <Form.Select
                              name="language"
                              value={settings.language}
                              onChange={handleSettingsChange}
                            >
                              <option value="en">English</option>
                              <option value="sw">Kiswahili</option>
                            </Form.Select>
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>Timezone</Form.Label>
                            <Form.Select
                              name="timezone"
                              value={settings.timezone}
                              onChange={handleSettingsChange}
                            >
                              <option value="Africa/Nairobi">East Africa Time (Nairobi)</option>
                              <option value="UTC">UTC</option>
                            </Form.Select>
                          </Form.Group>
                        </Col>
                      </Row>

                      <Form.Group className="mb-3">
                        <Form.Label>Date Format</Form.Label>
                        <div>
                          <Form.Check
                            inline
                            type="radio"
                            name="dateFormat"
                            value="DD/MM/YYYY"
                            checked={settings.dateFormat === 'DD/MM/YYYY'}
                            onChange={handleSettingsChange}
                            label="DD/MM/YYYY"
                          />
                          <Form.Check
                            inline
                            type="radio"
                            name="dateFormat"
                            value="MM/DD/YYYY"
                            checked={settings.dateFormat === 'MM/DD/YYYY'}
                            onChange={handleSettingsChange}
                            label="MM/DD/YYYY"
                          />
                          <Form.Check
                            inline
                            type="radio"
                            name="dateFormat"
                            value="YYYY-MM-DD"
                            checked={settings.dateFormat === 'YYYY-MM-DD'}
                            onChange={handleSettingsChange}
                            label="YYYY-MM-DD"
                          />
                        </div>
                      </Form.Group>

                      <div className="text-end">
                        <Button type="submit" variant="primary" disabled={loading}>
                          {loading ? (
                            <>
                              <Spinner
                                as="span"
                                animation="border"
                                size="sm"
                                role="status"
                                aria-hidden="true"
                                className="me-2"
                              />
                              Saving...
                            </>
                          ) : (
                            'Save Account Settings'
                          )}
                        </Button>
                      </div>
                    </Form>
                  </Tab.Pane>

                  {/* Privacy Settings Tab */}
                  <Tab.Pane eventKey="privacy">
                    <Form onSubmit={handleSaveSettings}>
                      <Form.Group className="mb-3">
                        <Form.Label>Profile Visibility</Form.Label>
                        <Form.Select
                          name="profileVisibility"
                          value={settings.profileVisibility}
                          onChange={handleSettingsChange}
                        >
                          <option value="private">Private (Only Me)</option>
                          <option value="school">School Community</option>
                          <option value="public">Public</option>
                        </Form.Select>
                        <Form.Text className="text-muted">
                          Control who can see your profile information
                        </Form.Text>
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>Data Sharing</Form.Label>
                        <Form.Check
                          type="checkbox"
                          name="newsletter"
                          checked={settings.newsletter}
                          onChange={handleSettingsChange}
                          label="Receive school newsletter and updates"
                        />
                        <Form.Text className="text-muted">
                          You can unsubscribe from newsletters at any time
                        </Form.Text>
                      </Form.Group>

                      <div className="text-end">
                        <Button type="submit" variant="primary" disabled={loading}>
                          Save Privacy Settings
                        </Button>
                      </div>
                    </Form>
                  </Tab.Pane>

                  {/* Security Settings Tab */}
                  <Tab.Pane eventKey="security">
                    {/* Change Password Section */}
                    <Card className="mb-4">
                      <Card.Header>
                        <h6 className="mb-0">Change Password</h6>
                      </Card.Header>
                      <Card.Body>
                        <Form onSubmit={handleChangePassword}>
                          <Form.Group className="mb-3">
                            <Form.Label>Current Password</Form.Label>
                            <Form.Control
                              type="password"
                              name="currentPassword"
                              value={passwordData.currentPassword}
                              onChange={handlePasswordChange}
                              required
                            />
                          </Form.Group>

                          <Form.Group className="mb-3">
                            <Form.Label>New Password</Form.Label>
                            <Form.Control
                              type="password"
                              name="newPassword"
                              value={passwordData.newPassword}
                              onChange={handlePasswordChange}
                              required
                            />
                            {passwordData.newPassword && (
                              <div className="mt-2">
                                <small>
                                  Password Strength:{' '}
                                  <span className={`text-${getPasswordStrengthColor(passwordStrength(passwordData.newPassword))}`}>
                                    {getPasswordStrengthText(passwordStrength(passwordData.newPassword))}
                                  </span>
                                </small>
                                <div className="progress mt-1" style={{ height: '5px' }}>
                                  <div
                                    className={`progress-bar bg-${getPasswordStrengthColor(passwordStrength(passwordData.newPassword))}`}
                                    style={{ width: `${(passwordStrength(passwordData.newPassword) / 5) * 100}%` }}
                                  ></div>
                                </div>
                              </div>
                            )}
                          </Form.Group>

                          <Form.Group className="mb-3">
                            <Form.Label>Confirm New Password</Form.Label>
                            <Form.Control
                              type="password"
                              name="confirmPassword"
                              value={passwordData.confirmPassword}
                              onChange={handlePasswordChange}
                              required
                            />
                            {passwordData.confirmPassword && passwordData.newPassword !== passwordData.confirmPassword && (
                              <Form.Text className="text-danger">
                                Passwords do not match
                              </Form.Text>
                            )}
                          </Form.Group>

                          <div className="text-end">
                            <Button type="submit" variant="primary" disabled={loading}>
                              Change Password
                            </Button>
                          </div>
                        </Form>
                      </Card.Body>
                    </Card>

                    {/* Two-Factor Authentication */}
                    <Card>
                      <Card.Header>
                        <h6 className="mb-0">Two-Factor Authentication</h6>
                      </Card.Header>
                      <Card.Body>
                        <Form.Group className="mb-3">
                          <Form.Check
                            type="switch"
                            name="twoFactorAuth"
                            checked={settings.twoFactorAuth}
                            onChange={handleSettingsChange}
                            label="Enable Two-Factor Authentication"
                          />
                          <Form.Text className="text-muted">
                            Add an extra layer of security to your account
                          </Form.Text>
                        </Form.Group>

                        {settings.twoFactorAuth && (
                          <Alert variant="info">
                            <i className="bi bi-info-circle me-2"></i>
                            Two-factor authentication will be configured on your next login.
                          </Alert>
                        )}

                        <div className="text-end">
                          <Button type="button" variant="outline-primary" onClick={handleSaveSettings}>
                            Save Security Settings
                          </Button>
                        </div>
                      </Card.Body>
                    </Card>
                  </Tab.Pane>

                  {/* Notifications Tab */}
                  <Tab.Pane eventKey="notifications">
                    <Form onSubmit={handleSaveSettings}>
                      <h6 className="mb-3">Notification Channels</h6>
                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          name="emailNotifications"
                          checked={settings.emailNotifications}
                          onChange={handleSettingsChange}
                          label="Email Notifications"
                        />
                      </Form.Group>
                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          name="smsNotifications"
                          checked={settings.smsNotifications}
                          onChange={handleSettingsChange}
                          label="SMS Notifications"
                        />
                      </Form.Group>
                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          name="pushNotifications"
                          checked={settings.pushNotifications}
                          onChange={handleSettingsChange}
                          label="Push Notifications"
                        />
                      </Form.Group>

                      <hr className="my-4" />

                      <h6 className="mb-3">Notification Types</h6>
                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          name="eventReminders"
                          checked={settings.eventReminders}
                          onChange={handleSettingsChange}
                          label="Event Reminders"
                        />
                      </Form.Group>
                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          name="gradeAlerts"
                          checked={settings.gradeAlerts}
                          onChange={handleSettingsChange}
                          label="Grade Alerts"
                        />
                      </Form.Group>
                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          name="assignmentAlerts"
                          checked={settings.assignmentAlerts}
                          onChange={handleSettingsChange}
                          label="Assignment Alerts"
                        />
                      </Form.Group>

                      <div className="text-end">
                        <Button type="submit" variant="primary" disabled={loading}>
                          Save Notification Settings
                        </Button>
                      </div>
                    </Form>
                  </Tab.Pane>

                  {/* Danger Zone Tab */}
                  <Tab.Pane eventKey="danger">
                    <Alert variant="warning">
                      <Alert.Heading>
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        Proceed with Caution
                      </Alert.Heading>
                      These actions are irreversible. Please be certain before proceeding.
                    </Alert>

                    <Card className="border-warning">
                      <Card.Header className="bg-warning bg-opacity-10">
                        <h6 className="mb-0">Export Your Data</h6>
                      </Card.Header>
                      <Card.Body>
                        <p>
                          Download a copy of all your personal data stored in our system.
                        </p>
                        <Button variant="outline-warning" onClick={handleExportData}>
                          <i className="bi bi-download me-2"></i>
                          Export My Data
                        </Button>
                      </Card.Body>
                    </Card>

                    <Card className="border-danger mt-4">
                      <Card.Header className="bg-danger bg-opacity-10">
                        <h6 className="mb-0 text-danger">Delete Account</h6>
                      </Card.Header>
                      <Card.Body>
                        <p className="text-danger">
                          Once you delete your account, there is no going back. This action
                          cannot be undone. All your data will be permanently removed from our systems.
                        </p>
                        <Button variant="danger" onClick={() => setShowDeleteModal(true)}>
                          <i className="bi bi-trash me-2"></i>
                          Delete My Account
                        </Button>
                      </Card.Body>
                    </Card>
                  </Tab.Pane>
                </Tab.Content>
              </Card.Body>
            </Card>
          </Tab.Container>

          {/* Delete Account Confirmation Modal */}
          <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
            <Modal.Header closeButton className="bg-danger text-white">
              <Modal.Title>Confirm Account Deletion</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <Alert variant="danger">
                <strong>This action cannot be undone!</strong>
              </Alert>
              <p>
                You are about to permanently delete your Delvok Academy account. 
                This will remove:
              </p>
              <ul>
                <li>All your personal information</li>
                <li>Academic records and progress</li>
                <li>Communication history</li>
                <li>Account settings and preferences</li>
              </ul>
              <p>
                <strong>Are you absolutely sure you want to proceed?</strong>
              </p>
              <Form.Group className="mb-3">
                <Form.Label>
                  Type <strong>DELETE MY ACCOUNT</strong> to confirm:
                </Form.Label>
                <Form.Control type="text" placeholder="DELETE MY ACCOUNT" />
              </Form.Group>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDeleteAccount}>
                Yes, Delete My Account
              </Button>
            </Modal.Footer>
          </Modal>
        </Col>
      </Row>
    </Container>
  );
};

export default Settings;