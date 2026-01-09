import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function StudentHandbook() {
  const [activeSection, setActiveSection] = useState('academics');
  const [searchTerm, setSearchTerm] = useState('');

  // Handbook data organized by sections
  const handbookData = {
    academics: {
      title: 'Academic Policies & Procedures',
      icon: 'bi-journal-bookmark',
      color: 'primary',
      content: [
        {
          category: 'Registration & Enrollment',
          items: [
            'Course registration deadlines and procedures',
            'Add/drop policies and timelines',
            'Credit load requirements and limits',
            'Waitlist procedures'
          ]
        },
        {
          category: 'Grading & Evaluation',
          items: [
            'Grading scale and GPA calculation',
            'Incomplete grade policies',
            'Grade appeal procedures',
            'Academic standing requirements'
          ]
        },
        {
          category: 'Academic Integrity',
          items: [
            'Plagiarism and citation guidelines',
            'Honor code expectations',
            'Consequences for academic dishonesty',
            'Appeals process for violations'
          ]
        },
        {
          category: 'Degree Requirements',
          items: [
            'General education requirements',
            'Major and minor requirements',
            'Graduation application process',
            'Transfer credit policies'
          ]
        }
      ]
    },
    campusLife: {
      title: 'Campus Life & Activities',
      icon: 'bi-people',
      color: 'success',
      content: [
        {
          category: 'Student Organizations',
          items: [
            'How to start a new student organization',
            'Funding and resource allocation',
            'Event planning guidelines',
            'Organization registration requirements'
          ]
        },
        {
          category: 'Residence Life',
          items: [
            'Dormitory rules and regulations',
            'Room assignment procedures',
            'Guest and visitation policies',
            'Check-in/check-out procedures'
          ]
        },
        {
          category: 'Campus Facilities',
          items: [
            'Library hours and access policies',
            'Recreation center guidelines',
            'Dining hall policies and meal plans',
            'Classroom and lab usage rules'
          ]
        },
        {
          category: 'Student Events',
          items: [
            'Event registration process',
            'Alcohol and substance policies',
            'Security requirements for events',
            'Funding and budgeting guidelines'
          ]
        }
      ]
    },
    conduct: {
      title: 'Student Conduct & Discipline',
      icon: 'bi-shield-check',
      color: 'warning',
      content: [
        {
          category: 'Code of Conduct',
          items: [
            'Expected behavior standards',
            'Prohibited activities and behaviors',
            'Dress code requirements',
            'Respect and inclusion policies'
          ]
        },
        {
          category: 'Disciplinary Procedures',
          items: [
            'Reporting violations process',
            'Judicial board procedures',
            'Sanctions and consequences',
            'Appeals process timeline'
          ]
        },
        {
          category: 'Alcohol & Substance Policies',
          items: [
            'Legal drinking age compliance',
            'Substance-free campus policies',
            'Medical amnesty provisions',
            'Education and prevention programs'
          ]
        },
        {
          category: 'Technology Usage',
          items: [
            'Acceptable use of campus networks',
            'Computer lab regulations',
            'Software licensing compliance',
            'Data privacy and security'
          ]
        }
      ]
    },
    services: {
      title: 'Student Services & Support',
      icon: 'bi-heart',
      color: 'info',
      content: [
        {
          category: 'Health & Wellness',
          items: [
            'Health center services and hours',
            'Mental health counseling services',
            'Health insurance requirements',
            'Emergency medical procedures'
          ]
        },
        {
          category: 'Academic Support',
          items: [
            'Tutoring center services',
            'Writing center assistance',
            'Study skills workshops',
            'Academic advising procedures'
          ]
        },
        {
          category: 'Career Services',
          items: [
            'Career counseling appointments',
            'Resume and interview preparation',
            'Internship and job search resources',
            'Career fair participation'
          ]
        },
        {
          category: 'Disability Services',
          items: [
            'Accommodation request process',
            'Accessibility resources',
            'Assistive technology available',
            'Advocacy and support services'
          ]
        }
      ]
    },
    financial: {
      title: 'Financial Information',
      icon: 'bi-cash-coin',
      color: 'secondary',
      content: [
        {
          category: 'Tuition & Fees',
          items: [
            'Tuition payment deadlines',
            'Fee breakdown and explanations',
            'Payment plan options',
            'Late payment penalties'
          ]
        },
        {
          category: 'Financial Aid',
          items: [
            'Scholarship application procedures',
            'Grant and loan disbursement',
            'Work-study program details',
            'Satisfactory academic progress'
          ]
        },
        {
          category: 'Billing & Refunds',
          items: [
            'Billing statement access',
            'Refund request procedures',
            'Third-party billing options',
            'Tax document availability'
          ]
        },
        {
          category: 'Financial Hardship',
          items: [
            'Emergency fund applications',
            'Financial counseling services',
            'Payment extension requests',
            'Withdrawal refund policies'
          ]
        }
      ]
    },
    safety: {
      title: 'Campus Safety & Emergency',
      icon: 'bi-exclamation-triangle',
      color: 'danger',
      content: [
        {
          category: 'Emergency Procedures',
          items: [
            'Emergency evacuation routes',
            'Severe weather shelter locations',
            'Active shooter response protocols',
            'Medical emergency procedures'
          ]
        },
        {
          category: 'Security Services',
          items: [
            'Campus security contact information',
            'Security escort services',
            'Emergency phone locations',
            'Crime reporting procedures'
          ]
        },
        {
          category: 'Personal Safety',
          items: [
            'Campus safety app features',
            'Self-defense class schedules',
            'Property protection guidelines',
            'Travel safety recommendations'
          ]
        },
        {
          category: 'Health & Safety Compliance',
          items: [
            'Immunization requirements',
            'Public health protocols',
            'Laboratory safety guidelines',
            'Sports and recreation safety'
          ]
        }
      ]
    }
  };

  // Quick links for easy navigation
  const quickLinks = [
    { title: 'Academic Calendar', url: '/calendar', icon: 'bi-calendar' },
    { title: 'Course Catalog', url: '/courses', icon: 'bi-book' },
    { title: 'Campus Map', url: '/map', icon: 'bi-map' },
    { title: 'IT Services', url: '/it', icon: 'bi-laptop' },
    { title: 'Dining Hours', url: '/dining', icon: 'bi-egg-fried' },
    { title: 'Transportation', url: '/transport', icon: 'bi-bus-front' }
  ];

  // Important contacts
  const importantContacts = [
    { department: 'Emergency Services', phone: '(555) 911-CAMPUS', description: '24/7 Campus Emergency' },
    { department: 'Security Office', phone: '(555) 123-SAFE', description: 'Non-emergency security' },
    { department: 'Health Center', phone: '(555) 456-HEAL', description: 'Medical appointments' },
    { department: 'Counseling Services', phone: '(555) 789-TALK', description: 'Mental health support' },
    { department: 'IT Help Desk', phone: '(555) 234-TECH', description: 'Technical support' },
    { department: 'Registrar Office', phone: '(555) 567-REG', description: 'Academic records' }
  ];

  // Filter content based on search term
  const filteredContent = handbookData[activeSection]?.content.map(category => ({
    ...category,
    items: category.items.filter(item => 
      item.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(category => category.items.length > 0);

  return (
    <div className="container-fluid py-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="display-5 fw-bold">Student Handbook</h1>
          <p className="lead mb-0">Your comprehensive guide to campus policies, procedures, and resources</p>
        </div>
        <Link to="/campus-life" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Campus Life
        </Link>
      </div>

      {/* Search Bar */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control form-control-lg"
                  placeholder="Search handbook policies, procedures, and resources..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-4 text-md-end mt-3 mt-md-0">
              <button className="btn btn-outline-secondary me-2">
                <i className="bi bi-printer me-2"></i>
                Print
              </button>
              <button className="btn btn-outline-secondary">
                <i className="bi bi-download me-2"></i>
                Download PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Sidebar Navigation */}
        <div className="col-lg-3 mb-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-list me-2"></i>
                Handbook Sections
              </h5>
            </div>
            <div className="card-body p-0">
              <div className="list-group list-group-flush">
                {Object.entries(handbookData).map(([key, section]) => (
                  <button
                    key={key}
                    className={`list-group-item list-group-item-action d-flex align-items-center ${
                      activeSection === key ? 'active' : ''
                    }`}
                    onClick={() => setActiveSection(key)}
                  >
                    <i className={`${section.icon} text-${section.color} me-3`}></i>
                    <span>{section.title}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="card mt-4">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-lightning me-2"></i>
                Quick Links
              </h5>
            </div>
            <div className="card-body">
              <div className="row g-2">
                {quickLinks.map((link, index) => (
                  <div key={index} className="col-6">
                    <a href={link.url} className="btn btn-outline-primary btn-sm w-100 mb-2">
                      <i className={`${link.icon} me-1`}></i>
                      {link.title}
                    </a>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Important Contacts */}
          <div className="card mt-4">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-telephone me-2"></i>
                Important Contacts
              </h5>
            </div>
            <div className="card-body">
              {importantContacts.map((contact, index) => (
                <div key={index} className="mb-3">
                  <div className="fw-bold small">{contact.department}</div>
                  <div className="text-primary">{contact.phone}</div>
                  <div className="text-muted small">{contact.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="col-lg-9">
          <div className="card">
            <div className="card-header bg-white">
              <div className="d-flex justify-content-between align-items-center">
                <div className="d-flex align-items-center">
                  <i className={`${handbookData[activeSection].icon} text-${handbookData[activeSection].color} display-6 me-3`}></i>
                  <div>
                    <h3 className="mb-0">{handbookData[activeSection].title}</h3>
                    <p className="text-muted mb-0">
                      Last updated: {new Date().toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="badge bg-light text-dark">
                  {filteredContent.reduce((total, category) => total + category.items.length, 0)} items
                </div>
              </div>
            </div>

            <div className="card-body">
              {searchTerm && (
                <div className="alert alert-info mb-4">
                  <i className="bi bi-info-circle me-2"></i>
                  Showing results for "<strong>{searchTerm}</strong>" in {handbookData[activeSection].title}
                </div>
              )}

              {filteredContent.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-search display-1 text-muted"></i>
                  <h4 className="mt-3">No results found</h4>
                  <p className="text-muted">
                    No policies match your search criteria. Try different keywords or browse the sections.
                  </p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setSearchTerm('')}
                  >
                    Clear Search
                  </button>
                </div>
              ) : (
                <div className="row g-4">
                  {filteredContent.map((category, categoryIndex) => (
                    <div key={categoryIndex} className="col-12">
                      <div className="card">
                        <div className="card-header">
                          <h5 className="mb-0">{category.category}</h5>
                        </div>
                        <div className="card-body">
                          <div className="row">
                            {category.items.map((item, itemIndex) => (
                              <div key={itemIndex} className="col-md-6 mb-3">
                                <div className="d-flex">
                                  <i className="bi bi-check-circle text-success mt-1 me-3"></i>
                                  <span>{item}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Handbook Footer */}
              <div className="mt-5 pt-4 border-top">
                <div className="row">
                  <div className="col-md-6">
                    <h6>Need Help Understanding a Policy?</h6>
                    <p className="small text-muted">
                      Contact your academic advisor or the relevant department for clarification on any handbook policy.
                    </p>
                  </div>
                  <div className="col-md-6">
                    <h6>Policy Updates</h6>
                    <p className="small text-muted">
                      This handbook is updated regularly. Students are responsible for staying informed about policy changes.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Emergency Notice */}
          <div className="alert alert-warning mt-4">
            <div className="d-flex align-items-center">
              <i className="bi bi-exclamation-triangle display-6 me-3"></i>
              <div>
                <h5 className="alert-heading mb-1">Important Notice</h5>
                <p className="mb-0">
                  This handbook contains official college policies. Violations may result in disciplinary action. 
                  For emergency situations, always refer to the latest emergency procedures and contact campus security immediately.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StudentHandbook;