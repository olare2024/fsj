import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Courses() {
  const [activeLevel, setActiveLevel] = useState('primary');
  const [activeSubject, setActiveSubject] = useState('all');

  const courseLevels = {
    primary: {
      title: 'Primary School Courses',
      description: 'Foundation courses for Grades 1-6 following both CBC and Cambridge Primary',
      subjects: {
        all: {
          name: 'All Primary Courses',
          courses: [
            {
              code: 'ENG-PRI',
              name: 'English Language',
              levels: ['Grade 1-6'],
              curriculum: ['CBC', 'Cambridge Primary'],
              description: 'Developing reading, writing, speaking, and listening skills',
              objectives: [
                'Phonics and reading fluency',
                'Creative writing skills',
                'Grammar and vocabulary',
                'Comprehension strategies'
              ]
            },
            {
              code: 'MATH-PRI',
              name: 'Mathematics',
              levels: ['Grade 1-6'],
              curriculum: ['CBC', 'Cambridge Primary'],
              description: 'Building strong mathematical foundations and problem-solving skills',
              objectives: [
                'Number sense and operations',
                'Geometry and measurement',
                'Data handling',
                'Problem-solving strategies'
              ]
            },
            {
              code: 'SCI-PRI',
              name: 'Science',
              levels: ['Grade 1-6'],
              curriculum: ['CBC', 'Cambridge Primary'],
              description: 'Introduction to scientific inquiry and investigation',
              objectives: [
                'Scientific method',
                'Life processes',
                'Materials and properties',
                'Forces and energy'
              ]
            }
          ]
        },
        languages: {
          name: 'Languages',
          courses: [
            {
              code: 'KIS-PRI',
              name: 'Kiswahili',
              levels: ['Grade 1-6'],
              curriculum: ['CBC'],
              description: 'Developing proficiency in Kenya\'s national language',
              objectives: [
                'Reading and writing skills',
                'Oral communication',
                'Cultural understanding',
                'Grammar and vocabulary'
              ]
            },
            {
              code: 'FRN-PRI',
              name: 'French',
              levels: ['Grade 4-6'],
              curriculum: ['Cambridge Primary'],
              description: 'Introduction to French language and culture',
              objectives: [
                'Basic conversation skills',
                'Vocabulary building',
                'Cultural awareness',
                'Simple reading and writing'
              ]
            }
          ]
        }
      }
    },
    secondary: {
      title: 'Secondary School Courses',
      description: 'Specialized courses for Grades 7-12 with CBC Junior Secondary and Cambridge IGCSE options',
      subjects: {
        all: {
          name: 'All Secondary Courses',
          courses: [
            {
              code: 'ENG-IGCSE',
              name: 'IGCSE English',
              levels: ['Grade 9-10'],
              curriculum: ['Cambridge IGCSE'],
              description: 'Advanced English language and literature studies',
              objectives: [
                'Literary analysis',
                'Advanced writing skills',
                'Critical reading',
                'Oral presentation'
              ],
              exam: 'Cambridge IGCSE English'
            },
            {
              code: 'MATH-IGCSE',
              name: 'IGCSE Mathematics',
              levels: ['Grade 9-10'],
              curriculum: ['Cambridge IGCSE'],
              description: 'Comprehensive mathematics curriculum for international standards',
              objectives: [
                'Algebra and functions',
                'Geometry and trigonometry',
                'Statistics and probability',
                'Calculus foundations'
              ],
              exam: 'Cambridge IGCSE Mathematics'
            }
          ]
        },
        sciences: {
          name: 'Sciences',
          courses: [
            {
              code: 'PHY-IGCSE',
              name: 'IGCSE Physics',
              levels: ['Grade 9-10'],
              curriculum: ['Cambridge IGCSE'],
              description: 'Study of matter, energy, and their interactions',
              objectives: [
                'Mechanics and motion',
                'Electricity and magnetism',
                'Waves and optics',
                'Modern physics'
              ],
              exam: 'Cambridge IGCSE Physics'
            },
            {
              code: 'CHEM-IGCSE',
              name: 'IGCSE Chemistry',
              levels: ['Grade 9-10'],
              curriculum: ['Cambridge IGCSE'],
              description: 'Comprehensive study of chemical principles and reactions',
              objectives: [
                'Atomic structure',
                'Chemical bonding',
                'Organic chemistry',
                'Laboratory techniques'
              ],
              exam: 'Cambridge IGCSE Chemistry'
            }
          ]
        }
      }
    },
    advanced: {
      title: 'Advanced Level Courses',
      description: 'University preparation courses including Advanced Placement and specialized programs',
      subjects: {
        all: {
          name: 'All Advanced Courses',
          courses: [
            {
              code: 'AP-CALC',
              name: 'AP Calculus',
              levels: ['Grade 11-12'],
              curriculum: ['Advanced Placement'],
              description: 'College-level calculus course covering limits, derivatives, and integrals',
              objectives: [
                'Limits and continuity',
                'Differential calculus',
                'Integral calculus',
                'Applications of calculus'
              ],
              exam: 'AP Calculus AB/BC'
            },
            {
              code: 'AP-BIO',
              name: 'AP Biology',
              levels: ['Grade 11-12'],
              curriculum: ['Advanced Placement'],
              description: 'Comprehensive biology course at college level',
              objectives: [
                'Cellular processes',
                'Genetics and evolution',
                'Ecology and diversity',
                'Laboratory investigations'
              ],
              exam: 'AP Biology'
            }
          ]
        }
      }
    }
  };

  const subjectCategories = {
    primary: ['all', 'languages', 'mathematics', 'sciences', 'arts', 'physical'],
    secondary: ['all', 'sciences', 'humanities', 'languages', 'mathematics', 'creative'],
    advanced: ['all', 'sciences', 'mathematics', 'humanities', 'languages']
  };

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/academics">Academics</Link></li>
              <li className="breadcrumb-item active">Courses</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Course Catalog</h1>
            <p className="lead mb-0">Comprehensive Course Offerings Across All Grade Levels</p>
            <div className="mt-3">
              <span className="badge bg-primary fs-6">Dual Curriculum Options</span>
            </div>
          </div>
        </div>
      </div>

      {/* Level Navigation */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body text-center">
              <div className="d-flex flex-wrap justify-content-center gap-3">
                <button
                  className={`btn ${activeLevel === 'primary' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => {
                    setActiveLevel('primary');
                    setActiveSubject('all');
                  }}
                >
                  <i className="bi bi-mortarboard me-2"></i>
                  Primary School
                </button>
                <button
                  className={`btn ${activeLevel === 'secondary' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => {
                    setActiveLevel('secondary');
                    setActiveSubject('all');
                  }}
                >
                  <i className="bi bi-journal-text me-2"></i>
                  Secondary School
                </button>
                <button
                  className={`btn ${activeLevel === 'advanced' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => {
                    setActiveLevel('advanced');
                    setActiveSubject('all');
                  }}
                >
                  <i className="bi bi-award me-2"></i>
                  Advanced Level
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subject Filter */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <h6 className="mb-3">Filter by Subject Area:</h6>
              <div className="d-flex flex-wrap gap-2">
                {subjectCategories[activeLevel].map(subject => (
                  <button
                    key={subject}
                    className={`btn ${activeSubject === subject ? 'btn-success' : 'btn-outline-success'} btn-sm`}
                    onClick={() => setActiveSubject(subject)}
                  >
                    {courseLevels[activeLevel].subjects[subject]?.name || subject.charAt(0).toUpperCase() + subject.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Courses Content */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h3 className="mb-0">{courseLevels[activeLevel].title}</h3>
              <p className="mb-0 mt-2">{courseLevels[activeLevel].description}</p>
            </div>
            <div className="card-body">
              {courseLevels[activeLevel].subjects[activeSubject] ? (
                <div className="row g-4">
                  {courseLevels[activeLevel].subjects[activeSubject].courses.map((course, index) => (
                    <div key={index} className="col-lg-6">
                      <div className="card h-100 course-card">
                        <div className="card-header bg-light d-flex justify-content-between align-items-center">
                          <div>
                            <h5 className="mb-0">{course.name}</h5>
                            <small className="text-muted">Code: {course.code}</small>
                          </div>
                          <div className="d-flex flex-wrap gap-1">
                            {course.curriculum.map((curr, idx) => (
                              <span key={idx} className="badge bg-primary">{curr}</span>
                            ))}
                          </div>
                        </div>
                        <div className="card-body">
                          <p className="card-text">{course.description}</p>
                          
                          <div className="row mb-3">
                            <div className="col-md-6">
                              <strong>Grade Levels:</strong>
                              <div>{course.levels.join(', ')}</div>
                            </div>
                            {course.exam && (
                              <div className="col-md-6">
                                <strong>Final Exam:</strong>
                                <div>{course.exam}</div>
                              </div>
                            )}
                          </div>

                          <h6>Learning Objectives:</h6>
                          <ul className="small">
                            {course.objectives.map((objective, idx) => (
                              <li key={idx}>{objective}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="card-footer bg-transparent">
                          <div className="d-flex justify-content-between align-items-center">
                            <small className="text-muted">
                              {course.curriculum.length > 1 ? 'Dual Curriculum' : 'Single Curriculum'}
                            </small>
                            <div>
                              <button className="btn btn-outline-primary btn-sm me-2">
                                Syllabus
                              </button>
                              <button className="btn btn-primary btn-sm">
                                Course Details
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-5">
                  <i className="bi bi-journal-x display-1 text-muted"></i>
                  <h4 className="mt-3">No courses found</h4>
                  <p className="text-muted">
                    No courses available for the selected subject area.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Course Selection Guide */}
      <div className="row mt-5">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h4 className="mb-0">Course Selection Guidelines</h4>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <h5>Primary School (Grade 1-6)</h5>
                  <ul>
                    <li>All students take core subjects in both curricula</li>
                    <li>Language options begin in Grade 4</li>
                    <li>Arts and physical education are compulsory</li>
                    <li>Cambridge Checkpoint in Grade 6</li>
                  </ul>
                </div>
                <div className="col-md-6">
                  <h5>Secondary School (Grade 7-12)</h5>
                  <ul>
                    <li>Pathway selection in Grade 7</li>
                    <li>Subject specialization from Grade 9</li>
                    <li>IGCSE subject combinations available</li>
                    <li>Advanced Placement options in Grades 11-12</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Curriculum Comparison */}
      <div className="row mt-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Curriculum Comparison</h3>
          <div className="table-responsive">
            <table className="table table-bordered">
              <thead className="table-primary">
                <tr>
                  <th>Feature</th>
                  <th>Kenyan CBC</th>
                  <th>Cambridge International</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Assessment Method</strong></td>
                  <td>Continuous competency assessment</td>
                  <td>Standardized international examinations</td>
                </tr>
                <tr>
                  <td><strong>Focus</strong></td>
                  <td>Practical skills and national values</td>
                  <td>Academic rigor and global perspectives</td>
                </tr>
                <tr>
                  <td><strong>Recognition</strong></td>
                  <td>National universities and employers</td>
                  <td>International universities worldwide</td>
                </tr>
                <tr>
                  <td><strong>Teaching Approach</strong></td>
                  <td>Student-centered, activity-based</td>
                  <td>Inquiry-based, research-oriented</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Course Registration */}
      <div className="row mt-5">
        <div className="col-12 text-center">
          <div className="card bg-primary text-white">
            <div className="card-body py-5">
              <h3 className="mb-3">Need Help Choosing Courses?</h3>
              <p className="fs-5 mb-4">
                Our academic advisors are available to help students and parents select the right courses.
              </p>
              <div className="row justify-content-center">
                <div className="col-md-6">
                  <div className="mb-3">
                    <i className="bi bi-envelope me-2"></i>
                    academic.advising@delvok.ac.ke
                  </div>
                  <div className="mb-3">
                    <i className="bi bi-telephone me-2"></i>
                    +254 720 123 457
                  </div>
                </div>
              </div>
              <button className="btn btn-light btn-lg mt-3">
                Schedule Academic Advising
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Courses;