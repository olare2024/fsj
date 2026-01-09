import React from 'react';
import { Link } from 'react-router-dom';

function Programs() {
  const programs = [
    {
      title: 'STEM Program',
      icon: 'bi-cpu',
      description: 'Science, Technology, Engineering, and Mathematics focus',
      benefits: ['Hands-on Labs', 'Robotics Club', 'Science Fairs'],
      duration: 'Full Academic Year'
    },
    {
      title: 'Arts & Humanities',
      icon: 'bi-palette',
      description: 'Creative expression and cultural studies',
      benefits: ['Art Exhibitions', 'Theater Productions', 'Creative Writing'],
      duration: 'Full Academic Year'
    },
    {
      title: 'Sports Academy',
      icon: 'bi-trophy',
      description: 'Athletic development and competition',
      benefits: ['Professional Coaching', 'Tournaments', 'Fitness Training'],
      duration: 'Full Academic Year'
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Special Programs</h1>
          <p className="lead">Enrichment programs beyond standard curriculum</p>
        </div>
        <Link to="/academics" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Academics
        </Link>
      </div>

      <div className="row g-4">
        {programs.map((program, index) => (
          <div key={index} className="col-md-6 col-lg-4">
            <div className="card h-100 shadow-sm">
              <div className="card-body text-center">
                <i className={`${program.icon} display-4 text-primary mb-3`}></i>
                <h5 className="card-title">{program.title}</h5>
                <p className="card-text">{program.description}</p>
                
                <h6>Program Benefits:</h6>
                <ul className="list-unstyled">
                  {program.benefits.map((benefit, idx) => (
                    <li key={idx} className="mb-1">
                      <i className="bi bi-check-circle text-success me-2"></i>
                      {benefit}
                    </li>
                  ))}
                </ul>
                
                <div className="mt-auto">
                  <small className="text-muted">Duration: {program.duration}</small>
                </div>
              </div>
              <div className="card-footer text-center">
                <button className="btn btn-primary me-2">Apply Now</button>
                <button className="btn btn-outline-secondary">Learn More</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Programs;