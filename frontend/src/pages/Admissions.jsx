import React, { useState } from 'react';
import { admissionsAPI } from '../services/api';

function Admissions() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    dob: '',
    email: '',
    phone: '',
    curriculum_choice: 'CBC Kenya',
    current_school: '',
    applied_class: '',
    message: ''
  });
  const [attachment, setAttachment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    setAttachment(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const submitData = new FormData();
    Object.keys(formData).forEach(key => {
      submitData.append(key, formData[key]);
    });
    if (attachment) {
      submitData.append('attachment', attachment);
    }

    try {
      await admissionsAPI.apply(submitData);
      setSubmitted(true);
      setFormData({
        first_name: '',
        last_name: '',
        dob: '',
        email: '',
        phone: '',
        curriculum_choice: 'CBC Kenya',
        current_school: '',
        applied_class: '',
        message: ''
      });
      setAttachment(null);
    } catch (error) {
      console.error('Error submitting application:', error);
      alert('Error submitting application. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, 3));
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const gradeOptions = [
    'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6',
    'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'
  ];

  const admissionRequirements = [
    {
      level: 'Lower Primary (Grades 1-3)',
      requirements: ['Birth Certificate', 'Previous School Report (if any)', 'Medical Records']
    },
    {
      level: 'Upper Primary (Grades 4-6)',
      requirements: ['Birth Certificate', 'Previous School Reports', 'Transfer Certificate']
    },
    {
      level: 'Junior Secondary (Grades 7-9)',
      requirements: ['Birth Certificate', 'KCPE Results', 'All Previous Reports', 'Transfer Certificate']
    },
    {
      level: 'Senior Secondary (Grades 10-12)',
      requirements: ['Birth Certificate', 'KCPE Results', 'Junior Secondary Reports', 'Selection Letter']
    }
  ];

  const processSteps = [
    { step: 1, title: 'Application', description: 'Submit online application form' },
    { step: 2, title: 'Review', description: 'Document verification and assessment' },
    { step: 3, title: 'Interview', description: 'Student and parent interview' },
    { step: 4, title: 'Admission', description: 'Offer letter and enrollment' }
  ];

  if (submitted) {
    return (
      <div className="admissions-page">
        {/* Success Banner */}
        <section className="success-banner bg-success text-white py-5">
          <div className="container">
            <div className="row justify-content-center text-center">
              <div className="col-lg-8">
                <div className="success-icon display-1 mb-4">🎓</div>
                <h1 className="display-5 fw-bold mb-3">Application Submitted Successfully!</h1>
                <p className="lead mb-4">
                  Thank you for choosing Delvok Academy. We're excited to review your application 
                  and will contact you within 3-5 working days for the next steps.
                </p>
                <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center">
                  <button 
                    className="btn btn-light btn-lg px-4"
                    onClick={() => setSubmitted(false)}
                  >
                    Submit Another Application
                  </button>
                  <a href="/" className="btn btn-outline-light btn-lg px-4">
                    Return to Home
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Next Steps */}
        <section className="py-5 bg-light">
          <div className="container">
            <h2 className="text-center mb-5">What Happens Next?</h2>
            <div className="row g-4">
              {processSteps.map((step, index) => (
                <div key={step.step} className="col-md-6 col-lg-3">
                  <div className="card h-100 border-0 shadow-sm">
                    <div className="card-body text-center p-4">
                      <div className={`step-number bg-primary text-white rounded-circle mx-auto mb-3 ${index === 0 ? 'current-step' : ''}`}>
                        {step.step}
                      </div>
                      <h5 className="card-title">{step.title}</h5>
                      <p className="card-text text-muted">{step.description}</p>
                      {index === 0 && (
                        <span className="badge bg-success">Completed</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="admissions-page">
      {/* Hero Banner */}
      <section className="admissions-hero bg-primary text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">Join Delvok Academy</h1>
              <p className="lead fs-4 mb-4">
                Begin Your Educational Journey with Kenya's Premier CBC Institution
              </p>
              <div className="d-flex flex-wrap gap-3">
                <span className="badge bg-light text-primary fs-6">🏆 Quality Education</span>
                <span className="badge bg-light text-primary fs-6">👨‍🏫 Expert Teachers</span>
                <span className="badge bg-light text-primary fs-6">🔬 Modern Facilities</span>
                <span className="badge bg-light text-primary fs-6">🌱 Holistic Development</span>
              </div>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">🎓</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-5">
        <div className="container">
          <div className="row">
            {/* Application Form */}
            <div className="col-lg-8">
              <div className="card shadow-lg border-0">
                <div className="card-header bg-gradient-primary text-white py-4">
                  <div className="d-flex justify-content-between align-items-center">
                    <h3 className="card-title mb-0">Student Admissions Application</h3>
                    <div className="application-badge bg-white text-primary px-3 py-1 rounded-pill small fw-bold">
                      Step {currentStep} of 3
                    </div>
                  </div>
                </div>
                
                {/* Progress Steps */}
                <div className="card-body border-bottom">
                  <div className="progress-steps">
                    {[1, 2, 3].map(step => (
                      <div key={step} className="step-item">
                        <div className={`step-circle ${step === currentStep ? 'active' : step < currentStep ? 'completed' : ''}`}>
                          {step < currentStep ? '✓' : step}
                        </div>
                        <div className="step-label">
                          {step === 1 && 'Personal Info'}
                          {step === 2 && 'Academic Info'}
                          {step === 3 && 'Documents & Submit'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card-body p-4">
                  <form onSubmit={handleSubmit}>
                    {/* Step 1: Personal Information */}
                    {currentStep === 1 && (
                      <div className="step-content">
                        <h5 className="text-primary mb-4">Student Personal Information</h5>
                        <div className="row">
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">First Name *</label>
                              <input
                                type="text"
                                className="form-control form-control-lg"
                                name="first_name"
                                value={formData.first_name}
                                onChange={handleChange}
                                required
                                placeholder="Enter student's first name"
                              />
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">Last Name *</label>
                              <input
                                type="text"
                                className="form-control form-control-lg"
                                name="last_name"
                                value={formData.last_name}
                                onChange={handleChange}
                                required
                                placeholder="Enter student's last name"
                              />
                            </div>
                          </div>
                        </div>

                        <div className="row">
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">Date of Birth *</label>
                              <input
                                type="date"
                                className="form-control form-control-lg"
                                name="dob"
                                value={formData.dob}
                                onChange={handleChange}
                                required
                              />
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">Applying for Grade *</label>
                              <select
                                className="form-select form-select-lg"
                                name="applied_class"
                                value={formData.applied_class}
                                onChange={handleChange}
                                required
                              >
                                <option value="">Select Grade Level</option>
                                {gradeOptions.map(grade => (
                                  <option key={grade} value={grade}>{grade}</option>
                                ))}
                              </select>
                            </div>
                          </div>
                        </div>

                        <div className="text-end">
                          <button type="button" className="btn btn-primary btn-lg px-5" onClick={nextStep}>
                            Next <i className="bi bi-arrow-right ms-2"></i>
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Step 2: Contact & Academic Information */}
                    {currentStep === 2 && (
                      <div className="step-content">
                        <h5 className="text-primary mb-4">Contact & Academic Information</h5>
                        <div className="row">
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">Email Address *</label>
                              <input
                                type="email"
                                className="form-control form-control-lg"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                required
                                placeholder="parent@email.com"
                              />
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">Phone Number *</label>
                              <input
                                type="tel"
                                className="form-control form-control-lg"
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                                required
                                placeholder="+254 XXX XXX XXX"
                              />
                            </div>
                          </div>
                        </div>

                        <div className="row">
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">Current School</label>
                              <input
                                type="text"
                                className="form-control form-control-lg"
                                name="current_school"
                                value={formData.current_school}
                                onChange={handleChange}
                                placeholder="Name of current school"
                              />
                            </div>
                          </div>
                          <div className="col-md-6">
                            <div className="mb-3">
                              <label className="form-label fw-semibold">Curriculum Choice</label>
                              <select
                                className="form-select form-select-lg"
                                name="curriculum_choice"
                                value={formData.curriculum_choice}
                                onChange={handleChange}
                              >
                                <option value="CBC Kenya">CBC Kenya</option>
                                <option value="British Curriculum">British Curriculum</option>
                                <option value="IB Programme">IB Programme</option>
                              </select>
                            </div>
                          </div>
                        </div>

                        <div className="d-flex justify-content-between">
                          <button type="button" className="btn btn-outline-primary btn-lg px-5" onClick={prevStep}>
                            <i className="bi bi-arrow-left me-2"></i> Back
                          </button>
                          <button type="button" className="btn btn-primary btn-lg px-5" onClick={nextStep}>
                            Next <i className="bi bi-arrow-right ms-2"></i>
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Step 3: Additional Information & Submit */}
                    {currentStep === 3 && (
                      <div className="step-content">
                        <h5 className="text-primary mb-4">Additional Information & Documents</h5>
                        
                        <div className="mb-4">
                          <label className="form-label fw-semibold">Additional Message</label>
                          <textarea
                            className="form-control form-control-lg"
                            name="message"
                            value={formData.message}
                            onChange={handleChange}
                            rows="4"
                            placeholder="Tell us about your child's interests, achievements, or any special considerations..."
                          />
                        </div>

                        <div className="mb-4">
                          <label className="form-label fw-semibold">Supporting Documents</label>
                          <input
                            type="file"
                            className="form-control form-control-lg"
                            onChange={handleFileChange}
                            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                          />
                          <div className="form-text">
                            You can upload previous report cards, birth certificate, or other supporting documents (PDF, Word, or Images).
                          </div>
                        </div>

                        <div className="alert alert-info">
                          <h6 className="alert-heading">
                            <i className="bi bi-info-circle me-2"></i>
                            Important Note
                          </h6>
                          After submission, our admissions team will contact you to schedule an interview 
                          and provide details about required documentation.
                        </div>

                        <div className="d-flex justify-content-between">
                          <button type="button" className="btn btn-outline-primary btn-lg px-5" onClick={prevStep}>
                            <i className="bi bi-arrow-left me-2"></i> Back
                          </button>
                          <button 
                            type="submit" 
                            className="btn btn-success btn-lg px-5"
                            disabled={loading}
                          >
                            {loading ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                                Submitting...
                              </>
                            ) : (
                              <>
                                Submit Application <i className="bi bi-send-check ms-2"></i>
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    )}
                  </form>
                </div>
              </div>
            </div>

            {/* Sidebar Information */}
            <div className="col-lg-4">
              {/* Requirements Card */}
              <div className="card shadow-sm border-0 mb-4">
                <div className="card-header bg-light">
                  <h5 className="mb-0">
                    <i className="bi bi-file-earmark-text me-2"></i>
                    Admission Requirements
                  </h5>
                </div>
                <div className="card-body">
                  {admissionRequirements.map((level, index) => (
                    <div key={index} className="mb-3">
                      <h6 className="text-primary">{level.level}</h6>
                      <ul className="list-unstyled mb-0">
                        {level.requirements.map((req, idx) => (
                          <li key={idx} className="small text-muted">
                            <i className="bi bi-check-circle text-success me-1"></i>
                            {req}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Contact Info Card */}
              <div className="card shadow-sm border-0 bg-primary text-white">
                <div className="card-body text-center">
                  <div className="display-6 mb-3">📞</div>
                  <h5>Need Help?</h5>
                  <p className="mb-3">Our admissions team is here to assist you.</p>
                  <div className="mb-2">
                    <i className="bi bi-telephone me-2"></i>
                    +254-700-123-456
                  </div>
                  <div className="mb-3">
                    <i className="bi bi-envelope me-2"></i>
                    admissions@delvok.edu
                  </div>
                  <button className="btn btn-light btn-sm">
                    <i className="bi bi-chat-dots me-2"></i>
                    Live Chat
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <style jsx>{`
        .admissions-hero {
          background: linear-gradient(135deg, var(--bs-primary) 0%, #0056b3 100%);
        }
        
        .bg-gradient-primary {
          background: linear-gradient(135deg, var(--bs-primary) 0%, #0056b3 100%) !important;
        }
        
        .progress-steps {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .step-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          flex: 1;
        }
        
        .step-circle {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #e9ecef;
          color: #6c757d;
          font-weight: bold;
          margin-bottom: 0.5rem;
          transition: all 0.3s ease;
        }
        
        .step-circle.active {
          background: var(--bs-primary);
          color: white;
          transform: scale(1.1);
        }
        
        .step-circle.completed {
          background: var(--bs-success);
          color: white;
        }
        
        .step-label {
          font-size: 0.875rem;
          font-weight: 500;
          color: #6c757d;
        }
        
        .step-circle.active + .step-label {
          color: var(--bs-primary);
          font-weight: 600;
        }
        
        .step-content {
          animation: fadeIn 0.5s ease-in;
        }
        
        .application-badge {
          font-size: 0.875rem;
        }
        
        .step-number {
          width: 50px;
          height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 1.25rem;
        }
        
        .current-step {
          animation: pulse 2s infinite;
        }
        
        .success-banner {
          background: linear-gradient(135deg, var(--bs-success) 0%, #198754 100%);
        }
        
        .success-icon {
          animation: bounce 1s ease-in-out;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-10px); }
          60% { transform: translateY(-5px); }
        }
        
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); }
        }
        
        .form-control-lg, .form-select-lg {
          border-radius: 10px;
          border: 2px solid #e9ecef;
          transition: all 0.3s ease;
        }
        
        .form-control-lg:focus, .form-select-lg:focus {
          border-color: var(--bs-primary);
          box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
        }
        
        @media (max-width: 768px) {
          .progress-steps {
            flex-direction: column;
            gap: 1rem;
          }
          
          .step-item {
            flex-direction: row;
            width: 100%;
          }
          
          .step-circle {
            margin-bottom: 0;
            margin-right: 1rem;
          }
        }
      `}</style>
    </div>
  );
}

export default Admissions;