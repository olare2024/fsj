import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Programs() {
  const [activeProgram, setActiveProgram] = useState('academic');

  const programCategories = {
    academic: {
      title: 'Academic Programs',
      description: 'Comprehensive educational programs from early years to pre-university',
      programs: [
        {
          name: 'Early Years Program',
          age: '2-6 years',
          duration: 'Pre-Primary 1 & 2',
          focus: 'Play-based learning and foundational development',
          features: [
            'Montessori-inspired learning environment',
            'Language and literacy foundation',
            'Social-emotional development',
            'Creative expression through arts',
            'Physical coordination and motor skills'
          ],
          outcomes: [
            'Strong foundational literacy and numeracy',
            'Confident communication skills',
            'Social readiness for formal schooling',
            'Curiosity and love for learning'
          ]
        },
        {
          name: 'Primary School Program',
          age: '6-13 years',
          duration: 'Grade 1-6',
          focus: 'Building core academic skills and character',
          features: [
            'Dual curriculum (CBC & Cambridge Primary)',
            'Integrated technology learning',
            'Project-based learning activities',
            'Extensive literacy program',
            'Mathematics mastery approach'
          ],
          outcomes: [
            'Solid academic foundation',
            'Critical thinking skills',
            'Digital literacy competence',
            'Leadership and teamwork abilities'
          ]
        },
        {
          name: 'Secondary School Program',
          age: '13-18 years',
          duration: 'Grade 7-12',
          focus: 'Specialization and university preparation',
          features: [
            'CBC Junior Secondary & Cambridge IGCSE',
            'Advanced placement courses',
            'Career guidance and counseling',
            'Research and independent study',
            'University preparation program'
          ],
          outcomes: [
            'University-ready qualifications',
            'Specialized subject knowledge',
            'Research and analytical skills',
            'Global citizenship awareness'
          ]
        }
      ]
    },
    special: {
      title: 'Special Programs',
      description: 'Enrichment programs enhancing the core curriculum',
      programs: [
        {
          name: 'Gifted and Talented Program',
          eligibility: 'By assessment and recommendation',
          focus: 'Accelerated learning for high-ability students',
          features: [
            'Individualized learning plans',
            'Advanced curriculum challenges',
            'Mentorship from subject experts',
            'Participation in academic competitions',
            'Research project opportunities'
          ],
          benefits: [
            'Intellectual stimulation and growth',
            'Leadership development',
            'University early admission opportunities',
            'Scholarship preparation'
          ]
        },
        {
          name: 'Learning Support Program',
          eligibility: 'Students with learning differences',
          focus: 'Individualized support and accommodation',
          features: [
            'Individual Education Plans (IEPs)',
            'Specialized instructional strategies',
            'Small group interventions',
            'Assistive technology integration',
            'Therapeutic support services'
          ],
          benefits: [
            'Academic progress at own pace',
            'Building self-confidence',
            'Developing coping strategies',
            'Successful mainstream integration'
          ]
        },
        {
          name: 'English Language Support',
          eligibility: 'Non-native English speakers',
          focus: 'English language acquisition and proficiency',
          features: [
            'Intensive English language classes',
            'ESL-certified instructors',
            'Language immersion activities',
            'Cross-cultural communication training',
            'Academic vocabulary development'
          ],
          benefits: [
            'Rapid English proficiency improvement',
            'Confident classroom participation',
            'Successful curriculum integration',
            'Cultural adaptation support'
          ]
        }
      ]
    },
    enrichment: {
      title: 'Enrichment Programs',
      description: 'Beyond classroom learning experiences',
      programs: [
        {
          name: 'STEAM Program',
          focus: 'Science, Technology, Engineering, Arts, and Mathematics',
          components: [
            'Robotics and coding classes',
            'Science laboratory investigations',
            'Engineering design challenges',
            'Digital arts and media production',
            'Mathematics Olympiad training'
          ],
          activities: [
            'Annual science fair',
            'Robotics competitions',
            'Coding bootcamps',
            'Maker space projects',
            'Industry expert workshops'
          ]
        },
        {
          name: 'Arts and Creativity',
          focus: 'Developing artistic talents and creative expression',
          components: [
            'Visual arts studio program',
            'Performing arts (music, drama, dance)',
            'Creative writing workshops',
            'Digital media production',
            'Cultural arts appreciation'
          ],
          activities: [
            'Annual art exhibition',
            'School musical productions',
            'Creative writing publications',
            'Music recitals and concerts',
            'Drama festival participation'
          ]
        },
        {
          name: 'Sports Academy',
          focus: 'Athletic development and sports excellence',
          components: [
            'Competitive sports training',
            'Physical fitness program',
            'Sports science education',
            'Team building and leadership',
            'Health and nutrition guidance'
          ],
          activities: [
            'Inter-school competitions',
            'Sports tournaments',
            'Athletic scholarship preparation',
            'Professional coaching sessions',
            'Fitness assessment and training'
          ]
        }
      ]
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/academics">Academics</Link></li>
              <li className="breadcrumb-item active">Programs</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Academic Programs</h1>
            <p className="lead mb-0">Comprehensive Educational Pathways for Every Student</p>
            <div className="mt-3">
              <span className="badge bg-success fs-6">Tailored Learning Experiences</span>
            </div>
          </div>
        </div>
      </div>

      {/* Program Navigation */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body text-center">
              <div className="d-flex flex-wrap justify-content-center gap-3">
                <button
                  className={`btn ${activeProgram === 'academic' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveProgram('academic')}
                >
                  <i className="bi bi-journal-bookmark me-2"></i>
                  Academic Programs
                </button>
                <button
                  className={`btn ${activeProgram === 'special' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveProgram('special')}
                >
                  <i className="bi bi-star me-2"></i>
                  Special Programs
                </button>
                <button
                  className={`btn ${activeProgram === 'enrichment' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveProgram('enrichment')}
                >
                  <i className="bi bi-lightning me-2"></i>
                  Enrichment Programs
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Programs Content */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h3 className="mb-0">{programCategories[activeProgram].title}</h3>
              <p className="mb-0 mt-2">{programCategories[activeProgram].description}</p>
            </div>
            <div className="card-body">
              <div className="row g-4">
                {programCategories[activeProgram].programs.map((program, index) => (
                  <div key={index} className="col-lg-6">
                    <div className="card h-100 program-card">
                      <div className="card-header bg-light">
                        <h5 className="mb-0">{program.name}</h5>
                        {(program.age || program.eligibility) && (
                          <small className="text-muted">
                            {program.age || program.eligibility}
                            {program.duration && ` • ${program.duration}`}
                          </small>
                        )}
                      </div>
                      <div className="card-body">
                        <p className="card-text fst-italic">{program.focus}</p>
                        
                        <h6>Key Features:</h6>
                        <ul className="small mb-3">
                          {program.features?.map((feature, idx) => (
                            <li key={idx}>{feature}</li>
                          ))}
                          {program.components?.map((component, idx) => (
                            <li key={idx}>{component}</li>
                          ))}
                        </ul>

                        {(program.outcomes || program.benefits || program.activities) && (
                          <>
                            <h6>
                              {program.outcomes ? 'Learning Outcomes:' : 
                               program.benefits ? 'Student Benefits:' : 'Program Activities:'}
                            </h6>
                            <ul className="small">
                              {(program.outcomes || program.benefits || program.activities)?.map((item, idx) => (
                                <li key={idx}>{item}</li>
                              ))}
                            </ul>
                          </>
                        )}
                      </div>
                      <div className="card-footer bg-transparent">
                        <button className="btn btn-outline-primary btn-sm">
                          Program Details
                        </button>
                        <button className="btn btn-primary btn-sm ms-2">
                          Apply Now
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Program Highlights */}
      <div className="row mt-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Program Highlights</h3>
          <div className="row g-4">
            <div className="col-md-3">
              <div className="card text-center h-100 border-0 shadow-sm">
                <div className="card-body">
                  <i className="bi bi-mortarboard display-4 text-success mb-3"></i>
                  <h5>Qualified Instructors</h5>
                  <p className="card-text small">
                    Certified teachers with expertise in both CBC and Cambridge curricula
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center h-100 border-0 shadow-sm">
                <div className="card-body">
                  <i className="bi bi-laptop display-4 text-success mb-3"></i>
                  <h5>Technology Integration</h5>
                  <p className="card-text small">
                    Modern technology tools enhancing learning experiences
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center h-100 border-0 shadow-sm">
                <div className="card-body">
                  <i className="bi bi-graph-up display-4 text-success mb-3"></i>
                  <h5>Progress Tracking</h5>
                  <p className="card-text small">
                    Comprehensive assessment and progress monitoring systems
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center h-100 border-0 shadow-sm">
                <div className="card-body">
                  <i className="bi bi-people display-4 text-success mb-3"></i>
                  <h5>Parent Partnership</h5>
                  <p className="card-text small">
                    Regular communication and involvement in student progress
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Admission Information */}
      <div className="row mt-5">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">Admission Process</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <h6>1. Application Submission</h6>
                <p className="small mb-0">Complete online application with required documents</p>
              </div>
              <div className="mb-3">
                <h6>2. Assessment & Interview</h6>
                <p className="small mb-0">Student assessment and family interview session</p>
              </div>
              <div className="mb-3">
                <h6>3. Placement Decision</h6>
                <p className="small mb-0">Admission committee review and placement</p>
              </div>
              <div className="mb-3">
                <h6>4. Enrollment</h6>
                <p className="small mb-0">Complete registration and fee payment</p>
              </div>
              <button className="btn btn-success btn-sm">
                Start Application
              </button>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-info text-white">
              <h5 className="mb-0">Program Calendar</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <h6>Academic Year 2024</h6>
                <p className="small mb-0">Three terms: January-April, May-August, September-November</p>
              </div>
              <div className="mb-3">
                <h6>Application Deadlines</h6>
                <p className="small mb-0">Rolling admissions with priority deadlines each term</p>
              </div>
              <div className="mb-3">
                <h6>Orientation Programs</h6>
                <p className="small mb-0">New student orientation before each term begins</p>
              </div>
              <div className="mb-3">
                <h6>Parent Workshops</h6>
                <p className="small mb-0">Regular workshops on curriculum and student support</p>
              </div>
              <button className="btn btn-info btn-sm">
                View Full Calendar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Section */}
      <div className="row mt-5">
        <div className="col-12 text-center">
          <div className="card bg-light">
            <div className="card-body py-5">
              <h3 className="mb-3">Have Questions About Our Programs?</h3>
              <p className="fs-5 mb-4">
                Our admissions team is ready to help you find the perfect program for your child.
              </p>
              <div className="row justify-content-center">
                <div className="col-md-4">
                  <div className="mb-3">
                    <i className="bi bi-envelope text-primary me-2"></i>
                    admissions@delvok.ac.ke
                  </div>
                  <div className="mb-3">
                    <i className="bi bi-telephone text-primary me-2"></i>
                    +254 720 123 456
                  </div>
                </div>
              </div>
              <button className="btn btn-primary btn-lg mt-3">
                Schedule a Campus Tour
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Programs;