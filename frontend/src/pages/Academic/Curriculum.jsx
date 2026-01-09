import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Curriculum() {
  const [activeLevel, setActiveLevel] = useState('cbc');

  const curriculumLevels = {
    cbc: {
      title: 'Kenyan CBC Curriculum',
      description: 'Competency-Based Curriculum aligned with Kenyan educational standards',
      levels: [
        {
          stage: 'Pre-Primary (PP1 & PP2)',
          age: '4-6 years',
          focus: 'Play-based learning and foundational skills development',
          competencies: [
            'Communication and language skills',
            'Psychomotor and creative skills',
            'Social and emotional development',
            'Environmental awareness',
            'Mathematical concepts'
          ],
          subjects: ['Language Activities', 'Mathematical Activities', 'Environmental Activities', 'Psychomotor Activities', 'Religious Education']
        },
        {
          stage: 'Lower Primary (Grade 1-3)',
          age: '6-9 years',
          focus: 'Literacy, numeracy, and social skills development',
          competencies: [
            'Reading, writing, and comprehension',
            'Basic arithmetic operations',
            'Digital literacy introduction',
            'Creative arts expression',
            'Health and hygiene practices'
          ],
          subjects: ['Literacy', 'Kiswahili', 'English', 'Mathematics', 'Environmental Activities', 'Hygiene & Nutrition', 'Religious Education', 'Creative Arts']
        },
        {
          stage: 'Upper Primary (Grade 4-6)',
          age: '9-12 years',
          focus: 'Subject specialization and skill application',
          competencies: [
            'Critical thinking and problem-solving',
            'Scientific inquiry and experimentation',
            'Social studies and citizenship',
            'Creative and performing arts',
            'Physical education and sports'
          ],
          subjects: ['English', 'Kiswahili', 'Mathematics', 'Science & Technology', 'Social Studies', 'CRE/IRE/HRE', 'Creative Arts', 'Physical Education']
        },
        {
          stage: 'Junior Secondary (Grade 7-9)',
          age: '12-15 years',
          focus: 'Pathway exploration and talent development',
          competencies: [
            'Career awareness and exploration',
            'Technical skills development',
            'Entrepreneurship mindset',
            'Digital literacy advancement',
            'Community service learning'
          ],
          subjects: [
            'Core: English, Kiswahili, Mathematics, Integrated Science, Social Studies, Pre-Technical Studies, Life Skills',
            'Optional: Agriculture, Home Science, Computer Studies, Performing Arts, Visual Arts, Business Studies, Foreign Languages'
          ]
        }
      ]
    },
    cambridge: {
      title: 'Cambridge International Curriculum',
      description: 'Internationally recognized curriculum preparing students for global opportunities',
      levels: [
        {
          stage: 'Cambridge Primary (Grade 1-6)',
          age: '5-11 years',
          focus: 'Building strong foundations in core subjects',
          competencies: [
            'English as first or second language',
            'Mathematical thinking and reasoning',
            'Scientific inquiry and investigation',
            'Digital literacy and ICT skills',
            'Global perspectives development'
          ],
          subjects: ['English', 'Mathematics', 'Science', 'ICT Starters', 'Global Perspectives'],
          assessment: 'Cambridge Primary Checkpoint in Grade 6'
        },
        {
          stage: 'Cambridge Lower Secondary (Grade 7-8)',
          age: '11-14 years',
          focus: 'Broad and balanced curriculum with progression',
          competencies: [
            'Advanced literacy and communication',
            'Problem-solving and analytical thinking',
            'Scientific method application',
            'Research and presentation skills',
            'Cross-cultural understanding'
          ],
          subjects: ['English', 'Mathematics', 'Science', 'ICT', 'Global Perspectives', 'Art & Design', 'Physical Education', 'Music'],
          assessment: 'Cambridge Lower Secondary Checkpoint'
        },
        {
          stage: 'Cambridge IGCSE (Grade 9-10)',
          age: '14-16 years',
          focus: 'Specialization and preparation for advanced studies',
          competencies: [
            'Subject-specific expertise',
            'Independent learning skills',
            'Examination preparation',
            'Research and project work',
            'University readiness'
          ],
          subjects: [
            'Compulsory: English Language, Mathematics, Combined Science',
            'Electives: Physics, Chemistry, Biology, Computer Science, Business Studies, Economics, Geography, History, Art & Design, Music, Foreign Languages'
          ],
          assessment: 'Cambridge IGCSE Examinations'
        }
      ]
    },
    integration: {
      title: 'Curriculum Integration Model',
      description: 'Seamless blending of CBC and Cambridge for optimal learning outcomes',
      features: [
        {
          area: 'Pedagogical Approach',
          description: 'Combining inquiry-based learning with competency development',
          benefits: [
            'Student-centered learning environment',
            'Differentiated instruction strategies',
            'Formative and summative assessment balance',
            'Real-world application of knowledge'
          ]
        },
        {
          area: 'Assessment Framework',
          description: 'Comprehensive evaluation combining both systems',
          benefits: [
            'Continuous competency assessment',
            'International benchmarking',
            'Individual progress tracking',
            'Multiple assessment methods'
          ]
        },
        {
          area: 'Skill Development',
          description: 'Holistic development of 21st century skills',
          benefits: [
            'Critical thinking and creativity',
            'Communication and collaboration',
            'Digital literacy and technological skills',
            'Cultural awareness and global citizenship'
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
              <li className="breadcrumb-item active">Curriculum</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Academic Curriculum</h1>
            <p className="lead mb-0">Dual Curriculum Excellence: Kenyan CBC & Cambridge International</p>
            <div className="mt-3">
              <span className="badge bg-primary fs-6">Kindergarten to Grade 12</span>
            </div>
          </div>
        </div>
      </div>

      {/* Curriculum Tabs */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <div className="d-flex flex-wrap gap-3">
                <button
                  className={`btn ${activeLevel === 'cbc' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveLevel('cbc')}
                >
                  <i className="bi bi-flag me-2"></i>
                  Kenyan CBC
                </button>
                <button
                  className={`btn ${activeLevel === 'cambridge' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveLevel('cambridge')}
                >
                  <i className="bi bi-globe me-2"></i>
                  Cambridge International
                </button>
                <button
                  className={`btn ${activeLevel === 'integration' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveLevel('integration')}
                >
                  <i className="bi bi-arrow-left-right me-2"></i>
                  Integration Model
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Curriculum Content */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h3 className="mb-0">{curriculumLevels[activeLevel].title}</h3>
              <p className="mb-0 mt-2">{curriculumLevels[activeLevel].description}</p>
            </div>
            <div className="card-body">
              {activeLevel === 'integration' ? (
                // Integration Model Content
                <div className="row g-4">
                  {curriculumLevels[activeLevel].features.map((feature, index) => (
                    <div key={index} className="col-lg-4">
                      <div className="card h-100 border-primary">
                        <div className="card-header">
                          <h5 className="mb-0">{feature.area}</h5>
                        </div>
                        <div className="card-body">
                          <p className="card-text">{feature.description}</p>
                          <h6>Benefits:</h6>
                          <ul className="small">
                            {feature.benefits.map((benefit, idx) => (
                              <li key={idx}>{benefit}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                // CBC and Cambridge Content
                <div className="row g-4">
                  {curriculumLevels[activeLevel].levels.map((level, index) => (
                    <div key={index} className="col-lg-6">
                      <div className="card h-100">
                        <div className="card-header bg-light">
                          <h5 className="mb-0">{level.stage}</h5>
                          <small className="text-muted">{level.age}</small>
                        </div>
                        <div className="card-body">
                          <p className="card-text fst-italic">{level.focus}</p>
                          
                          <h6>Key Competencies:</h6>
                          <ul className="small mb-3">
                            {level.competencies.map((competency, idx) => (
                              <li key={idx}>{competency}</li>
                            ))}
                          </ul>

                          <h6>Subjects:</h6>
                          {Array.isArray(level.subjects[0]) ? (
                            level.subjects.map((subjectGroup, idx) => (
                              <div key={idx} className="mb-2">
                                <strong>{subjectGroup.split(':')[0]}:</strong>
                                <div className="small">{subjectGroup.split(':')[1]}</div>
                              </div>
                            ))
                          ) : (
                            <div className="d-flex flex-wrap gap-2 mb-3">
                              {level.subjects.map((subject, idx) => (
                                <span key={idx} className="badge bg-secondary">{subject}</span>
                              ))}
                            </div>
                          )}

                          {level.assessment && (
                            <div className="mt-3 p-3 bg-warning rounded">
                              <strong>Assessment:</strong> {level.assessment}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Comparative Analysis */}
      <div className="row mt-5">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h4 className="mb-0">Curriculum Comparison</h4>
            </div>
            <div className="card-body">
              <div className="table-responsive">
                <table className="table table-bordered">
                  <thead>
                    <tr>
                      <th>Aspect</th>
                      <th>Kenyan CBC</th>
                      <th>Cambridge International</th>
                      <th>Delvok Integration</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Focus</strong></td>
                      <td>Competency development & national values</td>
                      <td>Academic excellence & global perspectives</td>
                      <td>Balanced development of both</td>
                    </tr>
                    <tr>
                      <td><strong>Assessment</strong></td>
                      <td>Continuous competency assessment</td>
                      <td>International standardized exams</td>
                      <td>Combined assessment approach</td>
                    </tr>
                    <tr>
                      <td><strong>Recognition</strong></td>
                      <td>National certification</td>
                      <td>International recognition</td>
                      <td>Dual certification advantage</td>
                    </tr>
                    <tr>
                      <td><strong>Pathways</strong></td>
                      <td>Local universities & careers</td>
                      <td>Global universities & careers</td>
                      <td>Multiple pathway options</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="row mt-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Benefits of Our Dual Curriculum</h3>
          <div className="row g-4">
            <div className="col-md-4">
              <div className="card text-center h-100">
                <div className="card-body">
                  <i className="bi bi-award display-4 text-primary mb-3"></i>
                  <h5>Global Competitiveness</h5>
                  <p className="card-text">
                    Students gain international qualifications while maintaining strong Kenyan roots.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card text-center h-100">
                <div className="card-body">
                  <i className="bi bi-lightbulb display-4 text-primary mb-3"></i>
                  <h5>Flexible Pathways</h5>
                  <p className="card-text">
                    Multiple options for university admission both locally and internationally.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card text-center h-100">
                <div className="card-body">
                  <i className="bi bi-people display-4 text-primary mb-3"></i>
                  <h5>Holistic Development</h5>
                  <p className="card-text">
                    Balanced approach developing both academic and practical life skills.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="row mt-5">
        <div className="col-12 text-center">
          <div className="card bg-primary text-white">
            <div className="card-body py-5">
              <h3 className="mb-3">Ready to Learn More?</h3>
              <p className="fs-5 mb-4">
                Discover how our dual curriculum can benefit your child's educational journey.
              </p>
              <div className="d-flex justify-content-center gap-3">
                <button className="btn btn-light btn-lg">
                  Download Curriculum Guide
                </button>
                <button className="btn btn-outline-light btn-lg">
                  Schedule Consultation
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Curriculum;