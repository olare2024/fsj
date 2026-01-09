import React from 'react';
import { Link } from 'react-router-dom';

function Curriculum() {
  const curriculumData = [
    {
      level: 'Elementary School',
      description: 'Foundational learning with focus on core subjects',
      subjects: ['Mathematics', 'Language Arts', 'Science', 'Social Studies'],
      features: ['Interactive Learning', 'Project-Based', 'Individual Attention']
    },
    {
      level: 'Middle School',
      description: 'Building on fundamentals with expanded subject choices',
      subjects: ['Advanced Math', 'Literature', 'Biology', 'World History'],
      features: ['Specialized Tracks', 'Elective Courses', 'Skill Development']
    },
    {
      level: 'High School',
      description: 'College preparatory curriculum with advanced placement',
      subjects: ['Calculus', 'Physics', 'Chemistry', 'Advanced Literature'],
      features: ['AP Courses', 'College Credit', 'Career Preparation']
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Academic Curriculum</h1>
          <p className="lead">Comprehensive learning pathways for all grade levels</p>
        </div>
        <Link to="/academics" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Academics
        </Link>
      </div>

      <div className="row g-4">
        {curriculumData.map((level, index) => (
          <div key={index} className="col-lg-4">
            <div className="card h-100 shadow-sm">
              <div className="card-header bg-primary text-white">
                <h5 className="mb-0">{level.level}</h5>
              </div>
              <div className="card-body">
                <p className="card-text">{level.description}</p>
                
                <h6>Core Subjects:</h6>
                <ul className="list-unstyled">
                  {level.subjects.map((subject, idx) => (
                    <li key={idx} className="mb-1">
                      <i className="bi bi-bookmark text-primary me-2"></i>
                      {subject}
                    </li>
                  ))}
                </ul>

                <h6>Key Features:</h6>
                <div className="d-flex flex-wrap gap-2">
                  {level.features.map((feature, idx) => (
                    <span key={idx} className="badge bg-light text-dark">
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
              <div className="card-footer">
                <button className="btn btn-outline-primary btn-sm">
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Curriculum;