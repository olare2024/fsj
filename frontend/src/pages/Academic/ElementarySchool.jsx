import React from 'react';
import { Link } from 'react-router-dom';

function ElementarySchool() {
  const gradeLevels = [
    {
      grade: 'Kindergarten',
      age: '4-5 years',
      focus: 'Play-based learning, social skills, basic literacy and numeracy',
      subjects: ['Language Activities', 'Mathematical Activities', 'Environmental Activities', 'Psychomotor Activities', 'Religious Education'],
      curriculum: ['CBC - Pre-Primary 1 & 2']
    },
    {
      grade: 'Grade 1-2',
      age: '6-7 years',
      focus: 'Foundational literacy, numeracy, and social development',
      subjects: ['Literacy', 'Kiswahili', 'English', 'Mathematics', 'Environmental Activities', 'Hygiene & Nutrition', 'Religious Education', 'Creative Activities'],
      curriculum: ['CBC - Lower Primary']
    },
    {
      grade: 'Grade 3',
      age: '8-9 years',
      focus: 'Building core academic skills and introducing Cambridge Checkpoint',
      subjects: ['English', 'Kiswahili', 'Mathematics', 'Science & Technology', 'Social Studies', 'Creative Arts', 'Religious Education', 'Physical Education'],
      curriculum: ['CBC - Lower Primary', 'Cambridge Primary Introduction']
    }
  ];

  const features = [
    {
      title: 'Dual Curriculum Approach',
      description: 'Seamless integration of Kenyan CBC and Cambridge Primary curriculum',
      icon: 'bi-journal-medical'
    },
    {
      title: 'Holistic Development',
      description: 'Focus on cognitive, physical, social, and emotional growth',
      icon: 'bi-people'
    },
    {
      title: 'Interactive Learning',
      description: 'Hands-on activities, educational games, and project-based learning',
      icon: 'bi-lightbulb'
    },
    {
      title: 'Individualized Attention',
      description: 'Small class sizes with personalized learning plans',
      icon: 'bi-person-check'
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/academics">Academics</Link></li>
              <li className="breadcrumb-item active">Elementary School</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">Elementary School</h1>
              <p className="lead mb-0">Kindergarten to Grade 3 - Building Strong Foundations</p>
            </div>
            <div className="badge bg-success fs-6">
              Ages 4-9 Years
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-light border-0 mb-5">
        <div className="card-body p-5">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="fw-bold mb-3">Nurturing Young Minds for Future Success</h2>
              <p className="fs-5 mb-4">
                At Delvok Academy Elementary School, we provide a nurturing environment where 
                children develop foundational skills through both Kenyan CBC and Cambridge Primary 
                curricula. Our approach balances academic excellence with character development.
              </p>
              <div className="d-flex gap-3">
                <button className="btn btn-primary btn-lg">
                  Schedule a Tour
                </button>
                <button className="btn btn-outline-primary btn-lg">
                  Download Curriculum
                </button>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-mortarboard display-1 text-primary opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Grade Levels */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Grade Levels & Curriculum</h3>
          <div className="row g-4">
            {gradeLevels.map((level, index) => (
              <div key={index} className="col-lg-4">
                <div className="card h-100 border-primary">
                  <div className="card-header bg-primary text-white">
                    <h5 className="mb-0">{level.grade}</h5>
                    <small>{level.age}</small>
                  </div>
                  <div className="card-body">
                    <p className="card-text">{level.focus}</p>
                    
                    <h6 className="mt-4">Core Subjects:</h6>
                    <ul className="small">
                      {level.subjects.map((subject, idx) => (
                        <li key={idx}>{subject}</li>
                      ))}
                    </ul>

                    <h6 className="mt-3">Curriculum:</h6>
                    <div className="d-flex flex-wrap gap-2">
                      {level.curriculum.map((curr, idx) => (
                        <span key={idx} className="badge bg-secondary">{curr}</span>
                      ))}
                    </div>
                  </div>
                  <div className="card-footer bg-transparent">
                    <button className="btn btn-outline-primary btn-sm">
                      Learn More
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">Our Elementary School Features</h3>
          <div className="row g-4">
            {features.map((feature, index) => (
              <div key={index} className="col-md-6 col-lg-3">
                <div className="card h-100 text-center border-0 shadow-sm">
                  <div className="card-body">
                    <i className={`${feature.icon} display-4 text-primary mb-3`}></i>
                    <h5>{feature.title}</h5>
                    <p className="card-text">{feature.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Daily Schedule */}
      <div className="row">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Typical Daily Schedule</h5>
            </div>
            <div className="card-body">
              <div className="timeline">
                <div className="timeline-item">
                  <strong>7:30 AM - 8:00 AM:</strong> Arrival & Morning Activities
                </div>
                <div className="timeline-item">
                  <strong>8:00 AM - 10:00 AM:</strong> Core Subjects (Literacy & Numeracy)
                </div>
                <div className="timeline-item">
                  <strong>10:00 AM - 10:30 AM:</strong> Break & Snack Time
                </div>
                <div className="timeline-item">
                  <strong>10:30 AM - 12:30 PM:</strong> Integrated Learning Activities
                </div>
                <div className="timeline-item">
                  <strong>12:30 PM - 1:30 PM:</strong> Lunch & Outdoor Play
                </div>
                <div className="timeline-item">
                  <strong>1:30 PM - 3:00 PM:</strong> Creative Arts & Special Subjects
                </div>
                <div className="timeline-item">
                  <strong>3:00 PM:</strong> Dismissal
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Assessment & Progress Tracking</h5>
            </div>
            <div className="card-body">
              <ul>
                <li>Continuous assessment through observations</li>
                <li>Portfolio-based learning documentation</li>
                <li>Parent-teacher conferences each term</li>
                <li>Progress reports with developmental milestones</li>
                <li>Cambridge Primary Checkpoint in Grade 3</li>
              </ul>
              <div className="mt-3">
                <button className="btn btn-primary me-2">
                  View Sample Report
                </button>
                <button className="btn btn-outline-primary">
                  Assessment Policy
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ElementarySchool;