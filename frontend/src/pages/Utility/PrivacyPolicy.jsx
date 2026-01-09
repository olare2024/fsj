import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function PrivacyPolicy() {
  const [activeSection, setActiveSection] = useState('overview');

  const policySections = [
    {
      id: 'overview',
      title: 'Overview',
      content: `Delvok Academy ("we," "our," or "us") is committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website and use our services.`
    },
    {
      id: 'information-collection',
      title: 'Information We Collect',
      content: `
        <h6>Personal Information</h6>
        <p>We may collect personal information that you voluntarily provide to us, including:</p>
        <ul>
          <li>Contact information (name, email, phone number, address)</li>
          <li>Student information (academic records, attendance, performance data)</li>
          <li>Parent/guardian information</li>
          <li>Employment information for job applicants</li>
          <li>Payment information for tuition and fees</li>
        </ul>

        <h6>Automatically Collected Information</h6>
        <p>When you visit our website, we may automatically collect:</p>
        <ul>
          <li>IP address and browser type</li>
          <li>Device information and operating system</li>
          <li>Pages visited and time spent on site</li>
          <li>Referring website and search terms</li>
        </ul>
      `
    },
    {
      id: 'information-use',
      title: 'How We Use Your Information',
      content: `
        <p>We use the information we collect for various purposes, including:</p>
        <ul>
          <li>Providing educational services and maintaining student records</li>
          <li>Processing admissions applications and enrollment</li>
          <li>Communicating with students, parents, and staff</li>
          <li>Processing payments and managing accounts</li>
          <li>Improving our website and services</li>
          <li>Complying with legal obligations and educational regulations</li>
          <li>Ensuring campus safety and security</li>
        </ul>
      `
    },
    {
      id: 'information-sharing',
      title: 'Information Sharing and Disclosure',
      content: `
        <p>We do not sell, trade, or otherwise transfer your personal information to third parties except in the following circumstances:</p>
        <ul>
          <li><strong>Educational Partners:</strong> With educational institutions for transfer purposes</li>
          <li><strong>Service Providers:</strong> With trusted third parties who assist in our operations</li>
          <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
          <li><strong>School Transitions:</strong> With receiving schools during student transfers</li>
          <li><strong>Emergency Situations:</strong> To protect the health and safety of individuals</li>
        </ul>
      `
    },
    {
      id: 'data-security',
      title: 'Data Security',
      content: `
        <p>We implement appropriate technical and organizational security measures to protect your personal information, including:</p>
        <ul>
          <li>Encryption of sensitive data in transit and at rest</li>
          <li>Regular security assessments and updates</li>
          <li>Access controls and authentication mechanisms</li>
          <li>Staff training on data protection</li>
          <li>Secure data backup and recovery procedures</li>
        </ul>
        <p>While we strive to protect your information, no method of transmission over the Internet is 100% secure.</p>
      `
    },
    {
      id: 'student-privacy',
      title: 'Student Privacy',
      content: `
        <p>We are particularly committed to protecting the privacy of our students:</p>
        <ul>
          <li>Compliance with the Kenyan Data Protection Act and other relevant regulations</li>
          <li>Parental consent required for collection of student information</li>
          <li>Limited access to student records based on educational need</li>
          <li>Protection of sensitive student information</li>
          <li>Age-appropriate privacy education for students</li>
        </ul>
      `
    },
    {
      id: 'data-retention',
      title: 'Data Retention',
      content: `
        <p>We retain personal information only for as long as necessary to fulfill the purposes for which it was collected, including:</p>
        <ul>
          <li><strong>Student Records:</strong> Maintained according to educational regulatory requirements</li>
          <li><strong>Financial Records:</strong> Retained for 7 years for audit purposes</li>
          <li><strong>Employment Records:</strong> Maintained as required by labor laws</li>
          <li><strong>Website Analytics:</strong> Retained for 26 months</li>
        </ul>
      `
    },
    {
      id: 'your-rights',
      title: 'Your Rights',
      content: `
        <p>You have the following rights regarding your personal information:</p>
        <ul>
          <li><strong>Access:</strong> Request access to your personal information</li>
          <li><strong>Correction:</strong> Request correction of inaccurate information</li>
          <li><strong>Deletion:</strong> Request deletion of your personal information</li>
          <li><strong>Objection:</strong> Object to processing of your information</li>
          <li><strong>Portability:</strong> Request transfer of your information</li>
          <li><strong>Withdrawal:</strong> Withdraw consent at any time</li>
        </ul>
        <p>To exercise these rights, please contact our Data Protection Officer.</p>
      `
    },
    {
      id: 'cookies',
      title: 'Cookies and Tracking',
      content: `
        <p>Our website uses cookies and similar tracking technologies to enhance your experience:</p>
        <ul>
          <li><strong>Essential Cookies:</strong> Required for basic website functionality</li>
          <li><strong>Analytics Cookies:</strong> Help us understand how visitors use our site</li>
          <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
          <li><strong>Marketing Cookies:</strong> Used for relevant advertising (with consent)</li>
        </ul>
        <p>You can control cookie settings through your browser preferences.</p>
      `
    },
    {
      id: 'third-party',
      title: 'Third-Party Links',
      content: `
        <p>Our website may contain links to third-party websites. We are not responsible for the privacy practices or content of these external sites. We encourage you to review the privacy policies of any third-party sites you visit.</p>
      `
    },
    {
      id: 'updates',
      title: 'Policy Updates',
      content: `
        <p>We may update this Privacy Policy from time to time. The updated version will be indicated by an updated "Last Revised" date at the bottom of this page. We encourage you to review this Privacy Policy periodically to stay informed about how we are protecting your information.</p>
      `
    },
    {
      id: 'contact',
      title: 'Contact Information',
      content: `
        <p>If you have any questions or concerns about this Privacy Policy or our data practices, please contact us:</p>
        <div class="row">
          <div class="col-md-6">
            <strong>Data Protection Officer</strong><br/>
            Delvok Academy<br/>
            P.O. Box 12345-00100<br/>
            Nairobi, Kenya<br/>
            Email: dpo@delvok.ac.ke<br/>
            Phone: +254 720 123 456
          </div>
          <div class="col-md-6">
            <strong>Office Hours</strong><br/>
            Monday - Friday: 8:00 AM - 5:00 PM<br/>
            Saturday: 9:00 AM - 1:00 PM<br/>
            Closed on Sundays and Public Holidays
          </div>
        </div>
      `
    }
  ];

  const lastUpdated = 'January 15, 2024';

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <nav aria-label="breadcrumb" className="mb-4">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item active">Privacy Policy</li>
            </ol>
          </nav>

          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-dark">Privacy Policy</h1>
              <p className="lead mb-0">How we protect and use your information</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">Last Updated</div>
              <div className="small text-muted">{lastUpdated}</div>
            </div>
          </div>

          <div className="row">
            {/* Table of Contents */}
            <div className="col-lg-3 mb-4">
              <div className="card sticky-top" style={{top: '20px'}}>
                <div className="card-header bg-primary text-white">
                  <h6 className="mb-0">Table of Contents</h6>
                </div>
                <div className="card-body p-0">
                  <div className="list-group list-group-flush">
                    {policySections.map(section => (
                      <button
                        key={section.id}
                        className={`list-group-item list-group-item-action text-start ${
                          activeSection === section.id ? 'active' : ''
                        }`}
                        onClick={() => setActiveSection(section.id)}
                      >
                        {section.title}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Policy Content */}
            <div className="col-lg-9">
              <div className="card">
                <div className="card-body">
                  {/* Current Section */}
                  {policySections
                    .filter(section => section.id === activeSection)
                    .map(section => (
                      <div key={section.id}>
                        <h3 className="text-primary mb-4">{section.title}</h3>
                        <div 
                          className="policy-content"
                          dangerouslySetInnerHTML={{ __html: section.content }}
                        />
                      </div>
                    ))
                  }

                  {/* Quick Actions */}
                  <div className="mt-5 pt-4 border-top">
                    <div className="row">
                      <div className="col-md-6">
                        <h6>Need Help?</h6>
                        <p className="small text-muted mb-3">
                          Contact our Data Protection Officer for privacy-related questions.
                        </p>
                        <button className="btn btn-outline-primary btn-sm">
                          <i className="bi bi-envelope me-2"></i>
                          Contact DPO
                        </button>
                      </div>
                      <div className="col-md-6">
                        <h6>Document Actions</h6>
                        <div className="d-flex gap-2">
                          <button className="btn btn-outline-secondary btn-sm">
                            <i className="bi bi-printer me-2"></i>
                            Print
                          </button>
                          <button className="btn btn-outline-secondary btn-sm">
                            <i className="bi bi-download me-2"></i>
                            Download PDF
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Important Notice */}
              <div className="alert alert-info mt-4">
                <div className="d-flex">
                  <i className="bi bi-info-circle display-6 text-primary me-3"></i>
                  <div>
                    <h6 className="alert-heading">Important Notice</h6>
                    <p className="mb-0">
                      This Privacy Policy applies to all personal information collected through our website, 
                      mobile applications, and during the course of providing educational services. By using 
                      our services, you consent to the practices described in this policy.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Styles */}
      <style jsx>{`
        .policy-content h6 {
          color: #2c3e50;
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
        }

        .policy-content ul {
          padding-left: 1.5rem;
        }

        .policy-content li {
          margin-bottom: 0.5rem;
        }

        .sticky-top {
          position: sticky;
          z-index: 100;
        }
      `}</style>
    </div>
  );
}

export default PrivacyPolicy;