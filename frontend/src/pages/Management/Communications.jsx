import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Communications() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('announcements');
  const [messageType, setMessageType] = useState('announcement');
  const [recipientGroup, setRecipientGroup] = useState('all');
  const [messageSubject, setMessageSubject] = useState('');
  const [messageContent, setMessageContent] = useState('');

  const announcements = [
    {
      id: 1,
      title: 'School Closed for Winter Break',
      content: 'The school will be closed from December 23rd to January 3rd for winter break. Classes resume on January 4th.',
      author: 'Principal Johnson',
      date: '2024-12-15',
      priority: 'high',
      audience: 'all',
      status: 'published'
    },
    {
      id: 2,
      title: 'Parent-Teacher Conference Schedule',
      content: 'Parent-teacher conferences are scheduled for next week. Please book your time slot through the parent portal.',
      author: 'Academic Office',
      date: '2024-12-10',
      priority: 'medium',
      audience: 'parents',
      status: 'published'
    },
    {
      id: 3,
      title: 'Science Fair Registration Open',
      content: 'Registration for the annual science fair is now open. Students in grades 6-12 are encouraged to participate.',
      author: 'Science Department',
      date: '2024-12-08',
      priority: 'medium',
      audience: 'students',
      status: 'published'
    },
    {
      id: 4,
      title: 'Staff Meeting Agenda',
      content: 'The monthly staff meeting will cover curriculum updates and professional development opportunities.',
      author: 'Principal Johnson',
      date: '2024-12-05',
      priority: 'low',
      audience: 'staff',
      status: 'draft'
    }
  ];

  const messageTemplates = [
    {
      id: 1,
      name: 'Welcome Message - New Students',
      category: 'welcome',
      lastUsed: '2024-01-15',
      usageCount: 45
    },
    {
      id: 2,
      name: 'Payment Reminder',
      category: 'billing',
      lastUsed: '2024-01-14',
      usageCount: 23
    },
    {
      id: 3,
      name: 'Absence Notification',
      category: 'attendance',
      lastUsed: '2024-01-12',
      usageCount: 67
    },
    {
      id: 4,
      name: 'Event Invitation',
      category: 'events',
      lastUsed: '2024-01-10',
      usageCount: 34
    }
  ];

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high': return 'bg-danger';
      case 'medium': return 'bg-warning';
      case 'low': return 'bg-info';
      default: return 'bg-secondary';
    }
  };

  const getAudienceBadge = (audience) => {
    switch (audience) {
      case 'all': return 'bg-primary';
      case 'students': return 'bg-success';
      case 'parents': return 'bg-info';
      case 'staff': return 'bg-warning';
      case 'teachers': return 'bg-secondary';
      default: return 'bg-light text-dark';
    }
  };

  const getStatusBadge = (status) => {
    return status === 'published' ? 'bg-success' : 'bg-warning';
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    // Handle message sending logic
    alert('Message sent successfully!');
    setMessageSubject('');
    setMessageContent('');
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Communications</h1>
          <p className="lead">Manage school-wide communications, announcements, and messaging</p>
        </div>
        <Link to="/admin" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admin
        </Link>
      </div>

      {/* Communication Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>156</h3>
              <p className="mb-0">Messages Sent</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>24</h3>
              <p className="mb-0">Active Announcements</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>89%</h3>
              <p className="mb-0">Open Rate</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>12</h3>
              <p className="mb-0">Templates</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'announcements' ? 'active' : ''}`}
                onClick={() => setActiveTab('announcements')}
              >
                <i className="bi bi-megaphone me-2"></i>
                Announcements
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'compose' ? 'active' : ''}`}
                onClick={() => setActiveTab('compose')}
              >
                <i className="bi bi-pencil me-2"></i>
                Compose Message
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'templates' ? 'active' : ''}`}
                onClick={() => setActiveTab('templates')}
              >
                <i className="bi bi-file-earmark me-2"></i>
                Message Templates
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'analytics' ? 'active' : ''}`}
                onClick={() => setActiveTab('analytics')}
              >
                <i className="bi bi-graph-up me-2"></i>
                Analytics
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Announcements Tab */}
          {activeTab === 'announcements' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="mb-0">School Announcements</h5>
                <button className="btn btn-primary">
                  <i className="bi bi-plus-circle me-2"></i>
                  New Announcement
                </button>
              </div>

              <div className="row g-4">
                {announcements.map(announcement => (
                  <div key={announcement.id} className="col-12">
                    <div className="card">
                      <div className="card-body">
                        <div className="d-flex justify-content-between align-items-start mb-3">
                          <h5 className="card-title mb-1">{announcement.title}</h5>
                          <div className="d-flex gap-2">
                            <span className={`badge ${getPriorityBadge(announcement.priority)}`}>
                              {announcement.priority}
                            </span>
                            <span className={`badge ${getAudienceBadge(announcement.audience)}`}>
                              {announcement.audience}
                            </span>
                            <span className={`badge ${getStatusBadge(announcement.status)}`}>
                              {announcement.status}
                            </span>
                          </div>
                        </div>
                        
                        <p className="card-text">{announcement.content}</p>
                        
                        <div className="d-flex justify-content-between align-items-center">
                          <div>
                            <small className="text-muted">
                              By {announcement.author} • {announcement.date}
                            </small>
                          </div>
                          <div className="btn-group">
                            <button className="btn btn-sm btn-outline-primary">
                              <i className="bi bi-eye"></i>
                            </button>
                            <button className="btn btn-sm btn-outline-warning">
                              <i className="bi bi-pencil"></i>
                            </button>
                            <button className="btn btn-sm btn-outline-danger">
                              <i className="bi bi-trash"></i>
                            </button>
                            <button className="btn btn-sm btn-outline-success">
                              <i className="bi bi-send"></i>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Compose Message Tab */}
          {activeTab === 'compose' && (
            <div>
              <h5 className="mb-4">Compose New Message</h5>
              <form onSubmit={handleSendMessage}>
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label className="form-label">Message Type</label>
                    <select
                      className="form-select"
                      value={messageType}
                      onChange={(e) => setMessageType(e.target.value)}
                      required
                    >
                      <option value="announcement">Announcement</option>
                      <option value="alert">Alert</option>
                      <option value="reminder">Reminder</option>
                      <option value="newsletter">Newsletter</option>
                      <option value="event">Event</option>
                    </select>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Recipient Group</label>
                    <select
                      className="form-select"
                      value={recipientGroup}
                      onChange={(e) => setRecipientGroup(e.target.value)}
                      required
                    >
                      <option value="all">All Users</option>
                      <option value="students">Students Only</option>
                      <option value="parents">Parents Only</option>
                      <option value="teachers">Teachers Only</option>
                      <option value="staff">Staff Only</option>
                      <option value="specific">Specific Grade/Class</option>
                    </select>
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label">Subject</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Enter message subject..."
                    value={messageSubject}
                    onChange={(e) => setMessageSubject(e.target.value)}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Message Content</label>
                  <textarea
                    className="form-control"
                    rows="8"
                    placeholder="Type your message here... You can use rich text formatting."
                    value={messageContent}
                    onChange={(e) => setMessageContent(e.target.value)}
                    required
                  ></textarea>
                </div>

                <div className="mb-3">
                  <label className="form-label">Attachments (Optional)</label>
                  <input
                    type="file"
                    className="form-control"
                    multiple
                  />
                  <div className="form-text">
                    You can attach documents, images, or other files (max 25MB total)
                  </div>
                </div>

                <div className="mb-4">
                  <label className="form-label">Delivery Options</label>
                  <div className="form-check">
                    <input className="form-check-input" type="checkbox" id="emailDelivery" defaultChecked />
                    <label className="form-check-label" htmlFor="emailDelivery">
                      Send via Email
                    </label>
                  </div>
                  <div className="form-check">
                    <input className="form-check-input" type="checkbox" id="portalDelivery" defaultChecked />
                    <label className="form-check-label" htmlFor="portalDelivery">
                      Post to Portal
                    </label>
                  </div>
                  <div className="form-check">
                    <input className="form-check-input" type="checkbox" id="smsDelivery" />
                    <label className="form-check-label" htmlFor="smsDelivery">
                      Send SMS (if available)
                    </label>
                  </div>
                </div>

                <div className="d-flex gap-2">
                  <button type="submit" className="btn btn-primary">
                    <i className="bi bi-send me-2"></i>
                    Send Message
                  </button>
                  <button type="button" className="btn btn-outline-secondary">
                    <i className="bi bi-floppy me-2"></i>
                    Save Draft
                  </button>
                  <button type="button" className="btn btn-outline-warning">
                    <i className="bi bi-eye me-2"></i>
                    Preview
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="mb-0">Message Templates</h5>
                <button className="btn btn-primary">
                  <i className="bi bi-plus-circle me-2"></i>
                  New Template
                </button>
              </div>

              <div className="row g-4">
                {messageTemplates.map(template => (
                  <div key={template.id} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-body">
                        <h6 className="card-title">{template.name}</h6>
                        <span className="badge bg-light text-dark mb-2">
                          {template.category}
                        </span>
                        <div className="template-meta">
                          <small className="text-muted d-block">
                            Last used: {template.lastUsed}
                          </small>
                          <small className="text-muted">
                            Used {template.usageCount} times
                          </small>
                        </div>
                      </div>
                      <div className="card-footer">
                        <div className="d-flex gap-2">
                          <button className="btn btn-sm btn-outline-primary flex-fill">
                            Use Template
                          </button>
                          <button className="btn btn-sm btn-outline-warning">
                            <i className="bi bi-pencil"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div>
              <h5 className="mb-4">Communication Analytics</h5>
              <div className="row">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">Message Engagement</h6>
                      <p className="text-muted">Open rates and click-through rates</p>
                      {/* Analytics chart would go here */}
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">Audience Reach</h6>
                      <p className="text-muted">Message distribution by audience type</p>
                      {/* Audience chart would go here */}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row mt-4">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-bell display-4 text-primary mb-3"></i>
              <h5>Quick Alerts</h5>
              <p className="text-muted">
                Send urgent alerts to specific groups
              </p>
              <button className="btn btn-primary">Send Alert</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-calendar-event display-4 text-success mb-3"></i>
              <h5>Event Notifications</h5>
              <p className="text-muted">
                Schedule event reminders
              </p>
              <button className="btn btn-success">Schedule</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-people display-4 text-info mb-3"></i>
              <h5>Group Messaging</h5>
              <p className="text-muted">
                Message specific classes or groups
              </p>
              <button className="btn btn-info">Message Groups</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Communications;