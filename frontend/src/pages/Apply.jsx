import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Apply() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Student Information
    firstName: '',
    lastName: '',
    birthDate: '',
    gender: '',
    
    // Contact Information
    email: '',
    phone: '',
    address: '',
    
    // Academic Information
    previousSchool: '',
    gradeLevel: '',
    interests: []
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        interests: checked 
          ? [...prev.interests, value]
          : prev.interests.filter(interest => interest !== value)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const nextStep = () => setCurrentStep(prev => prev + 1);
  const prevStep = () => setCurrentStep(prev => prev - 1);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle application submission
    alert('Application submitted successfully!');
  };

  const steps = [
    { number: 1, title: 'Student Info' },
    { number: 2, title: 'Contact Details' },
    { number: 3, title: 'Academic Info' },
    { number: 4, title: 'Review & Submit' }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1>Admission Application</h1>
              <p className="lead">Join the Delvok Academy community</p>
            </div>
            <Link to="/admissions" className="btn btn-outline-primary">
              <i className="bi bi-arrow-left me-2"></i>
              Back to Admissions
            </Link>
          </div>

          {/* Progress Steps */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="steps">
                {steps.map((step) => (
                  <div key={step.number} className="step">
                    <div className={`step-number ${currentStep >= step.number ? 'bg-primary' : 'bg-secondary'}`}>
                      {step.number}
                    </div>
                    <div className="step-title">{step.title}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Application Form */}
          <div className="card">
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                {currentStep === 1 && (
                  <div className="step-content">
                    <h4>Student Information</h4>
                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">First Name</label>
                          <input
                            type="text"
                            className="form-control"
                            name="firstName"
                            value={formData.firstName}
                            onChange={handleInputChange}
                            required
                          />
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Last Name</label>
                          <input
                            type="text"
                            className="form-control"
                            name="lastName"
                            value={formData.lastName}
                            onChange={handleInputChange}
                            required
                          />
                        </div>
                      </div>
                    </div>
                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Date of Birth</label>
                          <input
                            type="date"
                            className="form-control"
                            name="birthDate"
                            value={formData.birthDate}
                            onChange={handleInputChange}
                            required
                          />
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Gender</label>
                          <select
                            className="form-select"
                            name="gender"
                            value={formData.gender}
                            onChange={handleInputChange}
                            required
                          >
                            <option value="">Select Gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {currentStep === 2 && (
                  <div className="step-content">
                    <h4>Contact Information</h4>
                    {/* Contact form fields */}
                  </div>
                )}

                {currentStep === 3 && (
                  <div className="step-content">
                    <h4>Academic Information</h4>
                    {/* Academic form fields */}
                  </div>
                )}

                {currentStep === 4 && (
                  <div className="step-content">
                    <h4>Review Your Application</h4>
                    {/* Review summary */}
                  </div>
                )}

                <div className="d-flex justify-content-between mt-4">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={prevStep}
                    disabled={currentStep === 1}
                  >
                    Previous
                  </button>
                  
                  {currentStep < steps.length ? (
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={nextStep}
                    >
                      Next
                    </button>
                  ) : (
                    <button
                      type="submit"
                      className="btn btn-success"
                    >
                      Submit Application
                    </button>
                  )}
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .steps {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .step {
          display: flex;
          flex-direction: column;
          align-items: center;
          flex: 1;
        }
        .step-number {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          margin-bottom: 0.5rem;
        }
        .step-title {
          font-size: 0.9rem;
          text-align: center;
        }
      `}</style>
    </div>
  );
}

export default Apply;