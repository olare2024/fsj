import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function TermsOfService() {
  const [activeSection, setActiveSection] = useState('acceptance');
  const [acceptedTerms, setAcceptedTerms] = useState(false);

  const termsSections = [
    {
      id: 'acceptance',
      title: 'Acceptance of Terms',
      content: `
        <p>By accessing and using Delvok Academy's website, services, and facilities (collectively, the "Services"), you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using or accessing our Services.</p>
        
        <p>These terms apply to all visitors, users, students, parents, staff, and others who access or use the Services.</p>
      `
    },
    {
      id: 'services-description',
      title: 'Description of Services',
      content: `
        <p>Delvok Academy provides:</p>
        <ul>
          <li>Educational services through both Kenyan CBC and Cambridge International curricula</li>
          <li>Online learning platforms and educational resources</li>
          <li>Student information systems and parent portals</li>
          <li>Communication platforms for school community engagement</li>
          <li>Admissions and enrollment management services</li>
          <li>Extracurricular and co-curricular activities</li>
        </ul>
        
        <p>We reserve the right to modify, suspend, or discontinue any aspect of the Services at any time.</p>
      `
    },
    {
      id: 'user-accounts',
      title: 'User Accounts and Security',
      content: `
        <h6>Account Creation</h6>
        <p>To access certain Services, you may be required to create an account. You agree to:</p>
        <ul>
          <li>Provide accurate, current, and complete information during registration</li>
          <li>Maintain and promptly update your account information</li>
          <li>Maintain the security of your password and accept all risks of unauthorized access</li>
          <li>Notify us immediately of any unauthorized use of your account</li>
          <li>Take responsibility for all activities that occur under your account</li>
        </ul>

        <h6>Account Types</h6>
        <ul>
          <li><strong>Student Accounts:</strong> For enrolled students, subject to parental consent for minors</li>
          <li><strong>Parent Accounts:</strong> For parents/guardians of enrolled students</li>
          <li><strong>Staff Accounts:</strong> For faculty and administrative staff</li>
          <li><strong>Applicant Accounts:</strong> For prospective students during admissions process</li>
        </ul>
      `
    },
    {
      id: 'student-conduct',
      title: 'Student Conduct and Responsibilities',
      content: `
        <p>Students using our Services agree to:</p>
        <ul>
          <li>Adhere to the school's code of conduct and discipline policies</li>
          <li>Use technology resources responsibly and for educational purposes</li>
          <li>Respect intellectual property rights and copyright laws</li>
          <li>Maintain academic integrity and avoid plagiarism</li>
          <li>Use appropriate language and behavior in all communications</li>
          <li>Protect their login credentials and report any security concerns</li>
        </ul>

        <h6>Prohibited Activities</h6>
        <p>Students shall not:</p>
        <ul>
          <li>Share account credentials with others</li>
          <li>Attempt to bypass security measures</li>
          <li>Engage in cyberbullying or harassment</li>
          <li>Access or distribute inappropriate content</li>
          <li>Use services for commercial purposes</li>
          <li>Damage or interfere with system operations</li>
        </ul>
      `
    },
    {
      id: 'parent-responsibilities',
      title: 'Parent/Guardian Responsibilities',
      content: `
        <p>Parents/guardians of enrolled students agree to:</p>
        <ul>
          <li>Ensure their child complies with all school policies</li>
          <li>Monitor their child's use of school technology resources</li>
          <li>Provide accurate and updated contact information</li>
          <li>Review and acknowledge important school communications</li>
          <li>Participate in parent-teacher conferences and school events</li>
          <li>Ensure timely payment of school fees and charges</li>
        </ul>

        <h6>Communication Consent</h6>
        <p>By enrolling your child, you consent to:</p>
        <ul>
          <li>Receive school communications via email, SMS, and other channels</li>
          <li>Allow educational use of your child's work and achievements</li>
          <li>Emergency medical treatment when necessary</li>
          <li>Participation in school activities and field trips</li>
        </ul>
      `
    },
    {
      id: 'academic-policies',
      title: 'Academic Policies',
      content: `
        <h6>Attendance and Participation</h6>
        <p>Students are expected to maintain regular attendance and active participation in all academic activities as per school policies.</p>

        <h6>Assessment and Grading</h6>
        <p>Academic assessment follows the guidelines of both CBC and Cambridge International examination boards. Grading policies are outlined in the student handbook.</p>

        <h6>Academic Integrity</h6>
        <p>All students must maintain the highest standards of academic integrity. Plagiarism, cheating, or any form of academic dishonesty will result in disciplinary action.</p>

        <h6>Curriculum Changes</h6>
        <p>Delvok Academy reserves the right to modify curriculum, course offerings, and program requirements to maintain educational standards and compliance with regulatory bodies.</p>
      `
    },
    {
      id: 'fees-payment',
      title: 'Fees and Payment Terms',
      content: `
        <h6>Tuition and Fees</h6>
        <p>All tuition fees and charges are due as specified in the fee structure. The school reserves the right to revise fees with prior notice.</p>

        <h6>Payment Methods</h6>
        <p>Accepted payment methods include bank transfer, mobile money, and online payment platforms as specified by the school.</p>

        <h6>Late Payments</h6>
        <p>Late payments may incur penalties as outlined in the fee policy. Continued non-payment may result in suspension of services.</p>

        <h6>Refund Policy</h6>
        <p>Refund policies are detailed in the admissions agreement and are subject to school regulations and Kenyan education laws.</p>
      `
    },
    {
      id: 'intellectual-property',
      title: 'Intellectual Property',
      content: `
        <h6>School Materials</h6>
        <p>All educational materials, curriculum content, software, and school branding are the intellectual property of Delvok Academy and may not be reproduced without permission.</p>

        <h6>Student Work</h6>
        <p>Students retain ownership of their original work, but grant the school limited rights to display, reproduce, and use such work for educational purposes.</p>

        <h6>Third-Party Content</h6>
        <p>Use of third-party educational resources is subject to their respective terms and licensing agreements.</p>
      `
    },
    {
      id: 'privacy-data',
      title: 'Privacy and Data Protection',
      content: `
        <p>Our collection and use of personal information is governed by our Privacy Policy and complies with the Kenyan Data Protection Act.</p>

        <h6>Data Collection</h6>
        <p>We collect necessary personal information for educational purposes, administration, and communication.</p>

        <h6>Data Usage</h6>
        <p>Personal data is used solely for legitimate educational and administrative purposes.</p>

        <h6>Data Sharing</h6>
        <p>Information may be shared with educational authorities, examination boards, and service providers as required for educational purposes.</p>
      `
    },
    {
      id: 'termination',
      title: 'Termination and Suspension',
      content: `
        <h6>By the School</h6>
        <p>Delvok Academy may suspend or terminate access to Services for:</p>
        <ul>
          <li>Violation of these Terms of Service</li>
          <li>Non-payment of fees</li>
          <li>Behavior detrimental to the school community</li>
          <li>Failure to meet academic standards</li>
        </ul>

        <h6>By Users</h6>
        <p>Users may terminate their use of Services by following the withdrawal procedures outlined in school policies.</p>

        <h6>Effect of Termination</h6>
        <p>Upon termination, access to online services will be revoked, and outstanding fees remain payable.</p>
      `
    },
    {
      id: 'disclaimer',
      title: 'Disclaimer of Warranties',
      content: `
        <p>The Services are provided "as is" and "as available" without warranties of any kind, either express or implied.</p>

        <h6>Educational Outcomes</h6>
        <p>While we strive for academic excellence, Delvok Academy does not guarantee specific educational outcomes or examination results.</p>

        <h6>Service Availability</h6>
        <p>We do not guarantee uninterrupted access to online services and are not liable for temporary unavailability due to technical issues.</p>

        <h6>Third-Party Services</h6>
        <p>We are not responsible for third-party services, websites, or resources linked from our platform.</p>
      `
    },
    {
      id: 'limitation-liability',
      title: 'Limitation of Liability',
      content: `
        <p>To the fullest extent permitted by law, Delvok Academy shall not be liable for:</p>
        <ul>
          <li>Indirect, incidental, or consequential damages</li>
          <li>Loss of data or interruption of service</li>
          <li>Academic performance or examination results</li>
          <li>Actions of third-party service providers</li>
          <li>Events beyond our reasonable control</li>
        </ul>
      `
    },
    {
      id: 'governing-law',
      title: 'Governing Law and Dispute Resolution',
      content: `
        <h6>Governing Law</h6>
        <p>These Terms shall be governed by and construed in accordance with the laws of Kenya.</p>

        <h6>Dispute Resolution</h6>
        <p>Any disputes shall first be attempted to be resolved through:</p>
        <ol>
          <li>Informal discussion with school administration</li>
          <li>Formal written complaint to the Head of School</li>
          <li>Mediation as provided for in school policies</li>
        </ol>

        <h6>Jurisdiction</h6>
        <p>The courts of Kenya shall have exclusive jurisdiction over any disputes arising from these Terms.</p>
      `
    },
    {
      id: 'changes',
      title: 'Changes to Terms',
      content: `
        <p>Delvok Academy reserves the right to modify these Terms of Service at any time. We will notify users of significant changes through:</p>
        <ul>
          <li>Email notifications to registered users</li>
          <li>Notices on our website and portals</li>
          <li>School announcements and newsletters</li>
        </ul>

        <p>Continued use of the Services after changes constitutes acceptance of the modified terms.</p>
      `
    },
    {
      id: 'contact',
      title: 'Contact Information',
      content: `
        <p>For questions about these Terms of Service, please contact:</p>
        <div class="row">
          <div class="col-md-6">
            <strong>School Administration</strong><br/>
            Delvok Academy<br/>
            P.O. Box 12345-00100<br/>
            Nairobi, Kenya<br/>
            Email: admin@delvok.ac.ke<br/>
            Phone: +254 720 123 456
          </div>
          <div class="col-md-6">
            <strong>Office Hours</strong><br/>
            Monday - Friday: 7:30 AM - 5:00 PM<br/>
            Saturday: 8:00 AM - 1:00 PM<br/>
            Emergency: Available 24/7 for urgent matters
          </div>
        </div>
      `
    }
  ];

  const effectiveDate = 'January 15, 2024';

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <nav aria-label="breadcrumb" className="mb-4">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item active">Terms of Service</li>
            </ol>
          </nav>

          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-dark">Terms of Service</h1>
              <p className="lead mb-0">Rules and guidelines for using Delvok Academy services</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">Effective Date</div>
              <div className="small text-muted">{effectiveDate}</div>
            </div>
          </div>

          <div className="row">
            {/* Table of Contents */}
            <div className="col-lg-3 mb-4">
              <div className="card sticky-top" style={{top: '20px'}}>
                <div className="card-header bg-primary text-white">
                  <h6 className="mb-0">Sections</h6>
                </div>
                <div className="card-body p-0">
                  <div className="list-group list-group-flush">
                    {termsSections.map(section => (
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

            {/* Terms Content */}
            <div className="col-lg-9">
              <div className="card">
                <div className="card-body">
                  {/* Current Section */}
                  {termsSections
                    .filter(section => section.id === activeSection)
                    .map(section => (
                      <div key={section.id}>
                        <h3 className="text-primary mb-4">{section.title}</h3>
                        <div 
                          className="terms-content"
                          dangerouslySetInnerHTML={{ __html: section.content }}
                        />
                      </div>
                    ))
                  }

                  {/* Acceptance Section - Only show for certain sections */}
                  {(activeSection === 'acceptance' || activeSection === 'changes') && (
                    <div className="mt-5 p-4 bg-light rounded">
                      <div className="form-check mb-3">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          id="termsAcceptance"
                          checked={acceptedTerms}
                          onChange={(e) => setAcceptedTerms(e.target.checked)}
                        />
                        <label className="form-check-label" htmlFor="termsAcceptance">
                          I have read, understood, and agree to be bound by these Terms of Service
                        </label>
                      </div>
                      <button 
                        className={`btn ${acceptedTerms ? 'btn-primary' : 'btn-secondary'}`}
                        disabled={!acceptedTerms}
                      >
                        Acknowledge Terms
                      </button>
                    </div>
                  )}

                  {/* Quick Actions */}
                  <div className="mt-5 pt-4 border-top">
                    <div className="row">
                      <div className="col-md-6">
                        <h6>Need Clarification?</h6>
                        <p className="small text-muted mb-3">
                          Contact our administration office for questions about these terms.
                        </p>
                        <button className="btn btn-outline-primary btn-sm">
                          <i className="bi bi-question-circle me-2"></i>
                          Ask Questions
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
                          <Link to="/privacy-policy" className="btn btn-outline-info btn-sm">
                            <i className="bi bi-shield-check me-2"></i>
                            Privacy Policy
                          </Link>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Legal Notice */}
              <div className="alert alert-warning mt-4">
                <div className="d-flex">
                  <i className="bi bi-exclamation-triangle display-6 text-warning me-3"></i>
                  <div>
                    <h6 className="alert-heading">Legal Notice</h6>
                    <p className="mb-0">
                      These Terms of Service constitute a legally binding agreement between you and Delvok Academy. 
                      It is your responsibility to read and understand these terms before using our services. 
                      Continued use of our services indicates your acceptance of these terms.
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
        .terms-content h6 {
          color: #2c3e50;
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
        }

        .terms-content ul, .terms-content ol {
          padding-left: 1.5rem;
        }

        .terms-content li {
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

export default TermsOfService;