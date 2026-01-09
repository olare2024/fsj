import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, ProgressBar, Nav } from 'react-bootstrap';

const Apply = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Student Information
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    gender: '',
    nationality: '',
    
    // Contact Information
    parentName: '',
    parentEmail: '',
    parentPhone: '',
    address: '',
    
    // Academic Information
    currentSchool: '',
    gradeApplying: '',
    curriculum: '',
    previousGrades: '',
    
    // Additional Information
    medicalConditions: '',
    specialNeeds: '',
    extracurricular: '',
    
    // Documents
    birthCertificate: null,
    previousReports: null,
    photo: null
  });

  const steps = [
    { number: 1, title: 'Student Info' },
    { number: 2, title: 'Contact Info' },
    { number: 3, title: 'Academic Info' },
    { number: 4, title: 'Additional Info' },
    { number: 5, title: 'Documents' },
    { number: 6, title: 'Review & Submit' }
  ];

  const handleInputChange = (e) => {
    const { name, value, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: files ? files[0] : value
    }));
  };

  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, steps.length));
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle form submission
    console.log('Application submitted:', formData);
    alert('Application submitted successfully!');
  };

  const progress = ((currentStep - 1) / (steps.length - 1)) * 100;

  return (
    <Container className="mt-4">
      <Row className="justify-content-center">
        <Col lg={10}>
          <div className="text-center mb-5">
            <h1>Admission Application</h1>
            <p className="lead">Join Delvok Academy - Excellence in CBC & Cambridge Education</p>
          </div>

          {/* Progress Bar */}
          <Card className="mb-4">
            <Card.Body>
              <ProgressBar now={progress} className="mb-3" />
              <div className="d-flex justify-content-between">
                {steps.map(step => (
                  <div key={step.number} className="text-center">
                    <div 
                      className={`rounded-circle d-inline-flex align-items-center justify-content-center ${
                        step.number <= currentStep ? 'bg-primary text-white' : 'bg-light text-muted'
                      }`}
                      style={{ width: '40px', height: '40px' }}
                    >
                      {step.number}
                    </div>
                    <div className="mt-1 small">{step.title}</div>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>

          <Card>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                {/* Step 1: Student Information */}
                {currentStep === 1 && (
                  <div>
                    <h4 className="mb-4">Student Information</h4>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>First Name *</Form.Label>
                          <Form.Control
                            type="text"
                            name="firstName"
                            value={formData.firstName}
                            onChange={handleInputChange}
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Last Name *</Form.Label>
                          <Form.Control
                            type="text"
                            name="lastName"
                            value={formData.lastName}
                            onChange={handleInputChange}
                            required
                          />
                        </Form.Group>
                      </Col>
                    </Row>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Date of Birth *</Form.Label>
                          <Form.Control
                            type="date"
                            name="dateOfBirth"
                            value={formData.dateOfBirth}
                            onChange={handleInputChange}
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Gender *</Form.Label>
                          <Form.Select
                            name="gender"
                            value={formData.gender}
                            onChange={handleInputChange}
                            required
                          >
                            <option value="">Select Gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                          </Form.Select>
                        </Form.Group>
                      </Col>
                    </Row>
                    <Form.Group className="mb-3">
                      <Form.Label>Nationality *</Form.Label>
                      <Form.Control
                        type="text"
                        name="nationality"
                        value={formData.nationality}
                        onChange={handleInputChange}
                        required
                      />
                    </Form.Group>
                  </div>
                )}

                {/* Step 2: Contact Information */}
                {currentStep === 2 && (
                  <div>
                    <h4 className="mb-4">Parent/Guardian Contact Information</h4>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Parent/Guardian Name *</Form.Label>
                          <Form.Control
                            type="text"
                            name="parentName"
                            value={formData.parentName}
                            onChange={handleInputChange}
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Relationship to Student *</Form.Label>
                          <Form.Select required>
                            <option value="">Select Relationship</option>
                            <option value="father">Father</option>
                            <option value="mother">Mother</option>
                            <option value="guardian">Guardian</option>
                          </Form.Select>
                        </Form.Group>
                      </Col>
                    </Row>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Email Address *</Form.Label>
                          <Form.Control
                            type="email"
                            name="parentEmail"
                            value={formData.parentEmail}
                            onChange={handleInputChange}
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Phone Number *</Form.Label>
                          <Form.Control
                            type="tel"
                            name="parentPhone"
                            value={formData.parentPhone}
                            onChange={handleInputChange}
                            required
                          />
                        </Form.Group>
                      </Col>
                    </Row>
                    <Form.Group className="mb-3">
                      <Form.Label>Home Address *</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="address"
                        value={formData.address}
                        onChange={handleInputChange}
                        required
                      />
                    </Form.Group>
                  </div>
                )}

                {/* Step 3: Academic Information */}
                {currentStep === 3 && (
                  <div>
                    <h4 className="mb-4">Academic Information</h4>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Current School *</Form.Label>
                          <Form.Control
                            type="text"
                            name="currentSchool"
                            value={formData.currentSchool}
                            onChange={handleInputChange}
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Grade Applying For *</Form.Label>
                          <Form.Select
                            name="gradeApplying"
                            value={formData.gradeApplying}
                            onChange={handleInputChange}
                            required
                          >
                            <option value="">Select Grade</option>
                            <optgroup label="CBC">
                              <option value="grade1">Grade 1</option>
                              <option value="grade2">Grade 2</option>
                              <option value="grade3">Grade 3</option>
                              <option value="grade4">Grade 4</option>
                              <option value="grade5">Grade 5</option>
                              <option value="grade6">Grade 6</option>
                            </optgroup>
                            <optgroup label="Junior Secondary">
                              <option value="grade7">Grade 7</option>
                              <option value="grade8">Grade 8</option>
                              <option value="grade9">Grade 9</option>
                            </optgroup>
                            <optgroup label="Cambridge">
                              <option value="igcse1">IGCSE Year 1</option>
                              <option value="igcse2">IGCSE Year 2</option>
                              <option value="as-level">AS Level</option>
                              <option value="a-level">A Level</option>
                            </optgroup>
                          </Form.Select>
                        </Form.Group>
                      </Col>
                    </Row>
                    <Form.Group className="mb-3">
                      <Form.Label>Curriculum Preference</Form.Label>
                      <div>
                        <Form.Check
                          inline
                          type="radio"
                          name="curriculum"
                          value="cbc"
                          label="CBC (Competency Based Curriculum)"
                          checked={formData.curriculum === 'cbc'}
                          onChange={handleInputChange}
                        />
                        <Form.Check
                          inline
                          type="radio"
                          name="curriculum"
                          value="cambridge"
                          label="Cambridge International"
                          checked={formData.curriculum === 'cambridge'}
                          onChange={handleInputChange}
                        />
                      </div>
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Previous Academic Performance</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="previousGrades"
                        value={formData.previousGrades}
                        onChange={handleInputChange}
                        placeholder="Briefly describe previous academic performance and achievements"
                      />
                    </Form.Group>
                  </div>
                )}

                {/* Step 4: Additional Information */}
                {currentStep === 4 && (
                  <div>
                    <h4 className="mb-4">Additional Information</h4>
                    <Form.Group className="mb-3">
                      <Form.Label>Medical Conditions</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={2}
                        name="medicalConditions"
                        value={formData.medicalConditions}
                        onChange={handleInputChange}
                        placeholder="List any medical conditions or allergies"
                      />
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Special Educational Needs</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={2}
                        name="specialNeeds"
                        value={formData.specialNeeds}
                        onChange={handleInputChange}
                        placeholder="Describe any special educational needs or support required"
                      />
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Extracurricular Interests</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="extracurricular"
                        value={formData.extracurricular}
                        onChange={handleInputChange}
                        placeholder="Sports, arts, clubs, or other interests"
                      />
                    </Form.Group>
                  </div>
                )}

                {/* Step 5: Document Upload */}
                {currentStep === 5 && (
                  <div>
                    <h4 className="mb-4">Required Documents</h4>
                    <Alert variant="info">
                      Please upload scanned copies of the following documents. Files should be in PDF or JPEG format.
                    </Alert>
                    <Form.Group className="mb-3">
                      <Form.Label>Birth Certificate *</Form.Label>
                      <Form.Control
                        type="file"
                        name="birthCertificate"
                        onChange={handleInputChange}
                        accept=".pdf,.jpg,.jpeg,.png"
                        required
                      />
                      <Form.Text className="text-muted">
                        Upload a clear copy of the student's birth certificate
                      </Form.Text>
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Previous School Reports *</Form.Label>
                      <Form.Control
                        type="file"
                        name="previousReports"
                        onChange={handleInputChange}
                        accept=".pdf,.jpg,.jpeg,.png"
                        required
                      />
                      <Form.Text className="text-muted">
                        Upload recent school reports (last 2 years)
                      </Form.Text>
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Passport Photo</Form.Label>
                      <Form.Control
                        type="file"
                        name="photo"
                        onChange={handleInputChange}
                        accept=".jpg,.jpeg,.png"
                      />
                      <Form.Text className="text-muted">
                        Recent passport-sized photograph
                      </Form.Text>
                    </Form.Group>
                  </div>
                )}

                {/* Step 6: Review and Submit */}
                {currentStep === 6 && (
                  <div>
                    <h4 className="mb-4">Review Your Application</h4>
                    <Alert variant="warning">
                      Please review all information carefully before submitting. You will not be able to make changes after submission.
                    </Alert>
                    
                    <Card className="mb-3">
                      <Card.Header>
                        <h6>Student Information</h6>
                      </Card.Header>
                      <Card.Body>
                        <p><strong>Name:</strong> {formData.firstName} {formData.lastName}</p>
                        <p><strong>Date of Birth:</strong> {formData.dateOfBirth}</p>
                        <p><strong>Gender:</strong> {formData.gender}</p>
                        <p><strong>Nationality:</strong> {formData.nationality}</p>
                      </Card.Body>
                    </Card>

                    <Card className="mb-3">
                      <Card.Header>
                        <h6>Contact Information</h6>
                      </Card.Header>
                      <Card.Body>
                        <p><strong>Parent/Guardian:</strong> {formData.parentName}</p>
                        <p><strong>Email:</strong> {formData.parentEmail}</p>
                        <p><strong>Phone:</strong> {formData.parentPhone}</p>
                        <p><strong>Address:</strong> {formData.address}</p>
                      </Card.Body>
                    </Card>

                    <Card className="mb-3">
                      <Card.Header>
                        <h6>Academic Information</h6>
                      </Card.Header>
                      <Card.Body>
                        <p><strong>Current School:</strong> {formData.currentSchool}</p>
                        <p><strong>Grade Applying:</strong> {formData.gradeApplying}</p>
                        <p><strong>Curriculum:</strong> {formData.curriculum}</p>
                      </Card.Body>
                    </Card>

                    <Form.Group className="mb-3">
                      <Form.Check
                        type="checkbox"
                        label="I certify that all information provided is true and accurate"
                        required
                      />
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Check
                        type="checkbox"
                        label="I agree to the terms and conditions of Delvok Academy"
                        required
                      />
                    </Form.Group>
                  </div>
                )}

                {/* Navigation Buttons */}
                <div className="d-flex justify-content-between mt-4">
                  <Button
                    variant="outline-secondary"
                    onClick={prevStep}
                    disabled={currentStep === 1}
                  >
                    Previous
                  </Button>
                  
                  {currentStep < steps.length ? (
                    <Button variant="primary" onClick={nextStep}>
                      Next
                    </Button>
                  ) : (
                    <Button variant="success" type="submit">
                      Submit Application
                    </Button>
                  )}
                </div>
              </Form>
            </Card.Body>
          </Card>

          {/* Application Tips */}
          <Card className="mt-4">
            <Card.Header>
              <h5 className="mb-0">Application Tips</h5>
            </Card.Header>
            <Card.Body>
              <ul className="mb-0">
                <li>Ensure all information is accurate and complete</li>
                <li>Have digital copies of required documents ready</li>
                <li>Applications are processed within 5-7 working days</li>
                <li>You will receive a confirmation email upon submission</li>
                <li>Contact admissions@delvok.ac.ke for assistance</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Apply;