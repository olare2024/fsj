import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Badge, Form, Spinner, Alert, Dropdown } from 'react-bootstrap';
import { useAuth } from '../context/AuthContext';

const Notifications = () => {
  const { currentUser, markNotificationAsRead, markAllNotificationsAsRead, clearAllNotifications } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedNotifications, setSelectedNotifications] = useState(new Set());

  useEffect(() => {
    // Simulate loading notifications
    const loadNotifications = async () => {
      setLoading(true);
      
      // Mock notifications data
      const mockNotifications = [
        {
          id: 1,
          title: 'New Assignment Posted',
          message: 'Mathematics assignment for Chapter 4 has been posted. Due date: 2024-02-20',
          type: 'academic',
          priority: 'high',
          timestamp: '2024-02-15T10:30:00Z',
          read: false,
          actionUrl: '/assignments'
        },
        {
          id: 2,
          title: 'Grade Updated',
          message: 'Your Science exam grade has been updated. Check your grades for details.',
          type: 'academic',
          priority: 'medium',
          timestamp: '2024-02-14T16:45:00Z',
          read: false,
          actionUrl: '/grades'
        },
        {
          id: 3,
          title: 'Parent-Teacher Meeting',
          message: 'Term 1 parent-teacher meeting scheduled for February 25th. Please confirm your attendance.',
          type: 'event',
          priority: 'medium',
          timestamp: '2024-02-14T09:15:00Z',
          read: true,
          actionUrl: '/calendar'
        },
        {
          id: 4,
          title: 'Library Book Due',
          message: 'Your borrowed book "Advanced Mathematics" is due tomorrow. Please return or renew.',
          type: 'reminder',
          priority: 'low',
          timestamp: '2024-02-13T14:20:00Z',
          read: true,
          actionUrl: '/library'
        },
        {
          id: 5,
          title: 'Sports Day Update',
          message: 'Sports day has been rescheduled to March 1st due to weather conditions.',
          type: 'event',
          priority: 'medium',
          timestamp: '2024-02-12T11:00:00Z',
          read: true,
          actionUrl: '/athletics'
        },
        {
          id: 6,
          title: 'Fee Payment Reminder',
          message: 'Second term fees are due next week. Please make payment before the deadline.',
          type: 'financial',
          priority: 'high',
          timestamp: '2024-02-11T08:30:00Z',
          read: false,
          actionUrl: '/billing'
        },
        {
          id: 7,
          title: 'Club Meeting Cancelled',
          message: 'Science club meeting for today has been cancelled. New schedule will be communicated.',
          type: 'club',
          priority: 'low',
          timestamp: '2024-02-10T15:45:00Z',
          read: true,
          actionUrl: '/clubs'
        },
        {
          id: 8,
          title: 'System Maintenance',
          message: 'Scheduled system maintenance on Saturday from 2:00 AM to 4:00 AM. System may be unavailable.',
          type: 'system',
          priority: 'low',
          timestamp: '2024-02-09T13:20:00Z',
          read: true,
          actionUrl: null
        }
      ];

      setTimeout(() => {
        setNotifications(mockNotifications);
        setLoading(false);
      }, 1000);
    };

    loadNotifications();
  }, []);

  const handleMarkAsRead = async (notificationId) => {
    try {
      await markNotificationAsRead(notificationId);
      setNotifications(prev =>
        prev.map(notif =>
          notif.id === notificationId ? { ...notif, read: true } : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsAsRead();
      setNotifications(prev =>
        prev.map(notif => ({ ...notif, read: true }))
      );
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const handleClearAll = async () => {
    try {
      await clearAllNotifications();
      setNotifications([]);
    } catch (error) {
      console.error('Error clearing notifications:', error);
    }
  };

  const handleNotificationSelect = (notificationId) => {
    setSelectedNotifications(prev => {
      const newSelection = new Set(prev);
      if (newSelection.has(notificationId)) {
        newSelection.delete(notificationId);
      } else {
        newSelection.add(notificationId);
      }
      return newSelection;
    });
  };

  const handleSelectAll = () => {
    if (selectedNotifications.size === filteredNotifications.length) {
      setSelectedNotifications(new Set());
    } else {
      setSelectedNotifications(new Set(filteredNotifications.map(n => n.id)));
    }
  };

  const getPriorityBadge = (priority) => {
    const variants = {
      'high': 'danger',
      'medium': 'warning',
      'low': 'secondary'
    };
    return <Badge bg={variants[priority]} className="text-capitalize">{priority}</Badge>;
  };

  const getTypeIcon = (type) => {
    const icons = {
      'academic': 'bi-journal-text',
      'event': 'bi-calendar-event',
      'reminder': 'bi-bell',
      'financial': 'bi-cash-coin',
      'club': 'bi-people',
      'system': 'bi-gear'
    };
    return <i className={`bi ${icons[type] || 'bi-bell'} me-2`}></i>;
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !notification.read;
    return notification.type === filter;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading notifications...</span>
          </Spinner>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2>Notifications</h2>
              <p className="text-muted mb-0">
                Stay updated with school activities and important information
              </p>
            </div>
            {unreadCount > 0 && (
              <Badge bg="danger" pill>
                {unreadCount} unread
              </Badge>
            )}
          </div>

          {/* Notification Actions */}
          <Card className="mb-4">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div className="d-flex gap-2">
                  <Form.Select 
                    style={{ width: '150px' }}
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                  >
                    <option value="all">All Notifications</option>
                    <option value="unread">Unread Only</option>
                    <option value="academic">Academic</option>
                    <option value="event">Events</option>
                    <option value="financial">Financial</option>
                    <option value="club">Clubs</option>
                    <option value="system">System</option>
                  </Form.Select>

                  {filteredNotifications.length > 0 && (
                    <Form.Check
                      type="checkbox"
                      label="Select All"
                      checked={selectedNotifications.size === filteredNotifications.length}
                      onChange={handleSelectAll}
                    />
                  )}
                </div>

                <div className="d-flex gap-2">
                  {selectedNotifications.size > 0 && (
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={() => {
                        selectedNotifications.forEach(id => handleMarkAsRead(id));
                        setSelectedNotifications(new Set());
                      }}
                    >
                      Mark Selected as Read
                    </Button>
                  )}
                  
                  <Dropdown>
                    <Dropdown.Toggle variant="outline-secondary" size="sm">
                      <i className="bi bi-gear me-1"></i>
                      Actions
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      <Dropdown.Item onClick={handleMarkAllAsRead}>
                        <i className="bi bi-check-all me-2"></i>
                        Mark All as Read
                      </Dropdown.Item>
                      <Dropdown.Item onClick={handleClearAll}>
                        <i className="bi bi-trash me-2"></i>
                        Clear All Notifications
                      </Dropdown.Item>
                    </Dropdown.Menu>
                  </Dropdown>
                </div>
              </div>
            </Card.Body>
          </Card>

          {/* Notifications List */}
          {filteredNotifications.length === 0 ? (
            <Card>
              <Card.Body className="text-center py-5">
                <i className="bi bi-bell-slash text-muted" style={{ fontSize: '3rem' }}></i>
                <h5 className="mt-3 text-muted">No notifications</h5>
                <p className="text-muted">
                  {filter === 'unread' 
                    ? "You're all caught up! No unread notifications."
                    : "You don't have any notifications yet."
                  }
                </p>
              </Card.Body>
            </Card>
          ) : (
            <Card>
              <Card.Body className="p-0">
                {filteredNotifications.map(notification => (
                  <div
                    key={notification.id}
                    className={`p-3 border-bottom ${
                      !notification.read ? 'bg-light bg-opacity-50' : ''
                    } ${selectedNotifications.has(notification.id) ? 'bg-primary bg-opacity-10' : ''}`}
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleNotificationSelect(notification.id)}
                  >
                    <div className="d-flex align-items-start">
                      <Form.Check
                        type="checkbox"
                        checked={selectedNotifications.has(notification.id)}
                        onChange={() => handleNotificationSelect(notification.id)}
                        onClick={(e) => e.stopPropagation()}
                        className="me-3 mt-1"
                      />
                      
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-start mb-1">
                          <h6 className="mb-0">
                            {getTypeIcon(notification.type)}
                            {notification.title}
                            {!notification.read && (
                              <Badge bg="primary" pill className="ms-2">
                                New
                              </Badge>
                            )}
                          </h6>
                          <div className="d-flex gap-2 align-items-center">
                            {getPriorityBadge(notification.priority)}
                            <small className="text-muted">
                              {formatTime(notification.timestamp)}
                            </small>
                          </div>
                        </div>
                        
                        <p className="mb-2 text-muted">{notification.message}</p>
                        
                        <div className="d-flex gap-2">
                          {!notification.read && (
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleMarkAsRead(notification.id);
                              }}
                            >
                              Mark as Read
                            </Button>
                          )}
                          
                          {notification.actionUrl && (
                            <Button
                              variant="outline-secondary"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                // Navigate to action URL
                                window.location.href = notification.actionUrl;
                              }}
                            >
                              View Details
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </Card.Body>
            </Card>
          )}

          {/* Notification Preferences */}
          <Card className="mt-4">
            <Card.Header>
              <h6 className="mb-0">Notification Preferences</h6>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <p className="text-muted mb-3">
                    Manage how you receive notifications and what types of notifications you want to see.
                  </p>
                  <Button variant="outline-primary" href="/settings?tab=notifications">
                    <i className="bi bi-gear me-2"></i>
                    Manage Notification Settings
                  </Button>
                </Col>
                <Col md={6}>
                  <div className="bg-light rounded p-3">
                    <h6>Quick Settings</h6>
                    <div className="small">
                      <div className="d-flex justify-content-between mb-1">
                        <span>Email Notifications:</span>
                        <Badge bg="success">Enabled</Badge>
                      </div>
                      <div className="d-flex justify-content-between mb-1">
                        <span>Push Notifications:</span>
                        <Badge bg="success">Enabled</Badge>
                      </div>
                      <div className="d-flex justify-content-between">
                        <span>SMS Notifications:</span>
                        <Badge bg="secondary">Disabled</Badge>
                      </div>
                    </div>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Notifications;