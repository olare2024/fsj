import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function TechSupport() {
  const [activeTab, setActiveTab] = useState('tickets');
  const [ticketSubject, setTicketSubject] = useState('');
  const [ticketDescription, setTicketDescription] = useState('');
  const [ticketCategory, setTicketCategory] = useState('general');

  const tickets = [
    {
      id: 'TKT-001',
      subject: 'Login issues with student portal',
      status: 'open',
      priority: 'high',
      created: '2024-01-15',
      updated: '2024-01-15',
      category: 'login'
    },
    {
      id: 'TKT-002',
      subject: 'Slow internet connection in classroom',
      status: 'in-progress',
      priority: 'medium',
      created: '2024-01-14',
      updated: '2024-01-15',
      category: 'network'
    },
    {
      id: 'TKT-003',
      subject: 'Software installation request',
      status: 'resolved',
      priority: 'low',
      created: '2024-01-10',
      updated: '2024-01-12',
      category: 'software'
    }
  ];

  const knowledgeBase = [
    {
      category: 'Login Issues',
      articles: [
        {
          title: 'How to reset your password',
          views: 245,
          lastUpdated: '2024-01-10'
        },
        {
          title: 'Troubleshooting login errors',
          views: 189,
          lastUpdated: '2024-01-08'
        },
        {
          title: 'Two-factor authentication setup',
          views: 134,
          lastUpdated: '2024-01-05'
        }
      ]
    },
    {
      category: 'Software & Tools',
      articles: [
        {
          title: 'Installing educational software',
          views: 178,
          lastUpdated: '2024-01-12'
        },
        {
          title: 'Using the online gradebook',
          views: 267,
          lastUpdated: '2024-01-15'
        },
        {
          title: 'Accessing digital library resources',
          views: 156,
          lastUpdated: '2024-01-07'
        }
      ]
    },
    {
      category: 'Network & Connectivity',
      articles: [
        {
          title: 'Wi-Fi connection guide',
          views: 312,
          lastUpdated: '2024-01-14'
        },
        {
          title: 'Troubleshooting slow internet',
          views: 198,
          lastUpdated: '2024-01-11'
        },
        {
          title: 'VPN setup for remote access',
          views: 123,
          lastUpdated: '2024-01-09'
        }
      ]
    }
  ];

  const handleSubmitTicket = (e) => {
    e.preventDefault();
    // Handle ticket submission logic here
    alert('Support ticket submitted successfully!');
    setTicketSubject('');
    setTicketDescription('');
    setTicketCategory('general');
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'open': return 'bg-warning';
      case 'in-progress': return 'bg-info';
      case 'resolved': return 'bg-success';
      default: return 'bg-secondary';
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high': return 'bg-danger';
      case 'medium': return 'bg-warning';
      case 'low': return 'bg-success';
      default: return 'bg-secondary';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Technology Support</h1>
          <p className="lead">Get help with technical issues and IT services</p>
        </div>
        <Link to="/resources" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Resources
        </Link>
      </div>

      {/* Quick Help Cards */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <i className="bi bi-headset display-4 mb-3"></i>
              <h5>24/7 Support</h5>
              <p className="mb-0">Always available to help</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <i className="bi bi-clock-history display-4 mb-3"></i>
              <h5>Quick Response</h5>
              <p className="mb-0">Typically under 2 hours</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <i className="bi bi-check-circle display-4 mb-3"></i>
              <h5>95% Resolved</h5>
              <p className="mb-0">First contact resolution</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <i className="bi bi-people display-4 mb-3"></i>
              <h5>Expert Team</h5>
              <p className="mb-0">Certified technicians</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Tabs */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'tickets' ? 'active' : ''}`}
                onClick={() => setActiveTab('tickets')}
              >
                <i className="bi bi-ticket me-2"></i>
                My Support Tickets
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'new' ? 'active' : ''}`}
                onClick={() => setActiveTab('new')}
              >
                <i className="bi bi-plus-circle me-2"></i>
                New Ticket
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'knowledge' ? 'active' : ''}`}
                onClick={() => setActiveTab('knowledge')}
              >
                <i className="bi bi-book me-2"></i>
                Knowledge Base
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'contact' ? 'active' : ''}`}
                onClick={() => setActiveTab('contact')}
              >
                <i className="bi bi-telephone me-2"></i>
                Contact Support
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* My Tickets Tab */}
          {activeTab === 'tickets' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="mb-0">My Support Tickets</h5>
                <span className="badge bg-primary">{tickets.length} tickets</span>
              </div>

              {tickets.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>Ticket ID</th>
                        <th>Subject</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Created</th>
                        <th>Last Updated</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tickets.map(ticket => (
                        <tr key={ticket.id}>
                          <td>
                            <strong>{ticket.id}</strong>
                          </td>
                          <td>{ticket.subject}</td>
                          <td>
                            <span className={`badge ${getStatusBadge(ticket.status)}`}>
                              {ticket.status}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${getPriorityBadge(ticket.priority)}`}>
                              {ticket.priority}
                            </span>
                          </td>
                          <td>{ticket.created}</td>
                          <td>{ticket.updated}</td>
                          <td>
                            <button className="btn btn-sm btn-outline-primary">
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-5">
                  <i className="bi bi-inbox display-1 text-muted mb-3"></i>
                  <h4>No support tickets</h4>
                  <p className="text-muted">
                    You haven't submitted any support tickets yet.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* New Ticket Tab */}
          {activeTab === 'new' && (
            <div>
              <h5 className="mb-4">Submit New Support Ticket</h5>
              <form onSubmit={handleSubmitTicket}>
                <div className="row">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">Category</label>
                      <select
                        className="form-select"
                        value={ticketCategory}
                        onChange={(e) => setTicketCategory(e.target.value)}
                        required
                      >
                        <option value="general">General Support</option>
                        <option value="login">Login Issues</option>
                        <option value="software">Software Problems</option>
                        <option value="hardware">Hardware Issues</option>
                        <option value="network">Network/Connectivity</option>
                        <option value="email">Email Problems</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">Priority</label>
                      <select className="form-select" required>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label">Subject</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Brief description of the issue"
                    value={ticketSubject}
                    onChange={(e) => setTicketSubject(e.target.value)}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Description</label>
                  <textarea
                    className="form-control"
                    rows="6"
                    placeholder="Please provide detailed information about the issue, including any error messages, steps to reproduce, and what you were trying to accomplish..."
                    value={ticketDescription}
                    onChange={(e) => setTicketDescription(e.target.value)}
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
                    You can attach screenshots, error messages, or related files (max 10MB each)
                  </div>
                </div>

                <button type="submit" className="btn btn-primary">
                  <i className="bi bi-send me-2"></i>
                  Submit Ticket
                </button>
              </form>
            </div>
          )}

          {/* Knowledge Base Tab */}
          {activeTab === 'knowledge' && (
            <div>
              <h5 className="mb-4">Knowledge Base</h5>
              <div className="row">
                {knowledgeBase.map((section, index) => (
                  <div key={index} className="col-md-6 col-lg-4 mb-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h6 className="mb-0">{section.category}</h6>
                      </div>
                      <div className="card-body">
                        <div className="list-group list-group-flush">
                          {section.articles.map((article, articleIndex) => (
                            <a
                              key={articleIndex}
                              href="#"
                              className="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                            >
                              <span>{article.title}</span>
                              <small className="text-muted">
                                {article.views} views
                              </small>
                            </a>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Contact Support Tab */}
          {activeTab === 'contact' && (
            <div>
              <h5 className="mb-4">Contact Technical Support</h5>
              <div className="row">
                <div className="col-md-6">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="bi bi-telephone text-primary display-4 mb-3"></i>
                      <h5>Phone Support</h5>
                      <p className="mb-2">(555) 123-TECH</p>
                      <small className="text-muted">
                        Available 24/7 for urgent issues
                      </small>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="bi bi-envelope text-primary display-4 mb-3"></i>
                      <h5>Email Support</h5>
                      <p className="mb-2">support@delvok.edu</p>
                      <small className="text-muted">
                        Typically respond within 2 hours
                      </small>
                    </div>
                  </div>
                </div>
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="bi bi-chat-dots text-primary display-4 mb-3"></i>
                      <h5>Live Chat</h5>
                      <p className="mb-2">Available Online</p>
                      <small className="text-muted">
                        Mon-Fri, 8AM-6PM
                      </small>
                      <div className="mt-3">
                        <button className="btn btn-primary">
                          Start Chat
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="bi bi-clock text-primary display-4 mb-3"></i>
                      <h5>Service Hours</h5>
                      <p className="mb-1">Mon-Fri: 7:00 AM - 7:00 PM</p>
                      <p className="mb-1">Sat: 9:00 AM - 5:00 PM</p>
                      <p className="mb-0">Sun: Emergency Only</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Emergency Contact Banner */}
      <div className="alert alert-warning mt-4">
        <div className="d-flex align-items-center">
          <i className="bi bi-exclamation-triangle display-6 me-3"></i>
          <div>
            <h5 className="alert-heading mb-1">System Emergency?</h5>
            <p className="mb-0">
              For critical system outages affecting multiple users, call our emergency line immediately: 
              <strong> (555) 911-TECH</strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TechSupport;