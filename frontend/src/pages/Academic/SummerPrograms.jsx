import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function SummerPrograms() {
  const [activeCategory, setActiveCategory] = useState('academic');

  const programCategories = {
    academic: {
      name: 'Academic Enrichment',
      icon: 'bi-journal-bookmark',
      programs: [
        {
          title: 'STEM Discovery Camp',
          age: 'Ages 10-14',
          duration: '4 weeks',
          dates: 'June 3-28, 2024',
          description: 'Hands-on science experiments, robotics, coding, and engineering challenges',
          highlights: ['Daily lab sessions', 'Guest scientists', 'Science fair project'],
          fee: 'KES 45,000'
        },
        {
          title: 'Young Writers Workshop',
          age: 'Ages 12-16',
          duration: '3 weeks',
          dates: 'July 8-26, 2024',
          description: 'Creative writing, journalism, and storytelling with published authors',
          highlights: ['Publishing opportunity', 'Author mentorship', 'Writing portfolio'],
          fee: 'KES 35,000'
        },
        {
          title: 'Math Olympiad Training',
          age: 'Ages 13-17',
          duration: '4 weeks',
          dates: 'June 3-28, 2024',
          description: 'Advanced problem-solving techniques for math competitions',
          highlights: ['Competition preparation', 'University professor guidance', 'Team Kenya trials'],
          fee: 'KES 50,000'
        }
      ]
    },
    sports: {
      name: 'Sports & Athletics',
      icon: 'bi-trophy',
      programs: [
        {
          title: 'Swimming Academy',
          age: 'Ages 6-16',
          duration: '3 weeks',
          dates: 'Multiple sessions',
          description: 'Learn to swim or improve technique with certified coaches',
          highlights: ['Small group lessons', 'Water safety training', 'Progress certificates'],
          fee: 'KES 25,000'
        },
        {
          title: 'Basketball Intensive',
          age: 'Ages 10-18',
          duration: '4 weeks',
          dates: 'July 1-26, 2024',
          description: 'Professional basketball training and team development',
          highlights: ['College scout exposure', 'Strength conditioning', 'Tournament play'],
          fee: 'KES 40,000'
        },
        {
          title: 'Tennis Camp',
          age: 'Ages 8-16',
          duration: '3 weeks',
          dates: 'August 5-23, 2024',
          description: 'Comprehensive tennis instruction for all skill levels',
          highlights: ['ITF certified coaches', 'Match play experience', 'Fitness training'],
          fee: 'KES 35,000'
        }
      ]
    },
    arts: {
      name: 'Creative Arts',
      icon: 'bi-palette',
      programs: [
        {
          title: 'Digital Arts Studio',
          age: 'Ages 12-18',
          duration: '3 weeks',
          dates: 'July 8-26, 2024',
          description: 'Graphic design, animation, and digital media production',
          highlights: ['Professional software training', 'Portfolio development', 'Industry guest speakers'],
          fee: 'KES 42,000'
        },
        {
          title: 'Music Production',
          age: 'Ages 14-18',
          duration: '4 weeks',
          dates: 'June 3-28, 2024',
          description: 'Learn music theory, composition, and digital audio workstation skills',
          highlights: ['Recording studio access', 'Professional producer mentorship', 'Original composition'],
          fee: 'KES 48,000'
        },
        {
          title: 'Drama & Theater',
          age: 'Ages 10-16',
          duration: '3 weeks',
          dates: 'August 5-23, 2024',
          description: 'Acting techniques, stage production, and performance skills',
          highlights: ['Final stage production', 'Professional director coaching', 'Costume and set design'],
          fee: 'KES 38,000'
        }
      ]
    },
    leadership: {
      name: 'Leadership & Service',
      icon: 'bi-people',
      programs: [
        {
          title: 'Young Leaders Summit',
          age: 'Ages 15-18',
          duration: '2 weeks',
          dates: 'July 15-26, 2024',
          description: 'Leadership development, public speaking, and community project design',
          highlights: ['Model UN simulation', 'Community service project', 'Leadership certificate'],
          fee: 'KES 30,000'
        },
        {
          title: 'Environmental Stewards',
          age: 'Ages 12-16',
          duration: '3 weeks',
          dates: 'June 10-28, 2024',
          description: 'Environmental science, conservation projects, and sustainability',
          highlights: ['Field research', 'Community clean-up', 'Environmental advocacy training'],
          fee: 'KES 32,000'
        }
      ]
    }
  };

  const registrationSteps = [
    {
      step: '1. Choose Program',
      description: 'Select your preferred summer program and session'
    },
    {
      step: '2. Complete Form',
      description: 'Fill out the online registration form with student information'
    },
    {
      step: '3. Submit Payment',
      description: 'Pay program fees through our secure payment portal'
    },
    {
      step: '4. Receive Confirmation',
      description: 'Get program details and preparation information'
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
              <li className="breadcrumb-item active">Summer Programs</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-success">Summer Programs 2024</h1>
              <p className="lead mb-0">Enriching Experiences Beyond the Regular School Year</p>
            </div>
            <div className="badge bg-success fs-6">
              June - August 2024
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-success text-white mb-5">
        <div className="card-body p-5">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="fw-bold mb-3">Summer of Discovery and Growth</h2>
              <p className="fs-5 mb-4">
                Delvok Academy Summer Programs offer exciting opportunities for students to 
                explore new interests, develop skills, and make new friends in a fun and 
                supportive environment. From academic enrichment to sports and arts, we have 
                something for every student.
              </p>
              <div className="d-flex gap-3">
                <button className="btn btn-light btn-lg text-success">
                  Register Now
                </button>
                <button className="btn btn-outline-light btn-lg">
                  Download Brochure
                </button>
              </div>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-sun display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Program Categories Navigation */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <h5 className="mb-3">Program Categories</h5>
              <div className="d-flex flex-wrap gap-3">
                {Object.entries(programCategories).map(([key, category]) => (
                  <button
                    key={key}
                    className={`btn ${activeCategory === key ? 'btn-success' : 'btn-outline-success'}`}
                    onClick={() => setActiveCategory(key)}
                  >
                    <i className={`${category.icon} me-2`}></i>
                    {category.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Programs Grid */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">{programCategories[activeCategory].name} Programs</h3>
          <div className="row g-4">
            {programCategories[activeCategory].programs.map((program, index) => (
              <div key={index} className="col-lg-6">
                <div className="card h-100 border-success">
                  <div className="card-header bg-success text-white d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">{program.title}</h5>
                    <span className="badge bg-light text-success">{program.age}</span>
                  </div>
                  <div className="card-body">
                    <div className="row mb-3">
                      <div className="col-md-6">
                        <strong>Duration:</strong>
                        <div>{program.duration}</div>
                      </div>
                      <div className="col-md-6">
                        <strong>Dates:</strong>
                        <div>{program.dates}</div>
                      </div>
                    </div>
                    
                    <p className="card-text">{program.description}</p>
                    
                    <h6>Program Highlights:</h6>
                    <ul className="small">
                      {program.highlights.map((highlight, idx) => (
                        <li key={idx}>{highlight}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="card-footer bg-transparent d-flex justify-content-between align-items-center">
                    <div className="text-success fw-bold">{program.fee}</div>
                    <div>
                      <button className="btn btn-outline-success btn-sm me-2">
                        Details
                      </button>
                      <button className="btn btn-success btn-sm">
                        Register
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="row">
        {/* Registration Process */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-success text-white">
              <h5 className="mb-0">How to Register</h5>
            </div>
            <div className="card-body">
              {registrationSteps.map((step, index) => (
                <div key={index} className="mb-4">
                  <div className="d-flex align-items-start">
                    <div className="bg-success text-white rounded-circle p-2 me-3">
                      <strong>{step.step.split('.')[0]}</strong>
                    </div>
                    <div>
                      <h6 className="mb-1">{step.step}</h6>
                      <p className="mb-0">{step.description}</p>
                    </div>
                  </div>
                </div>
              ))}
              <div className="alert alert-info mt-3">
                <strong>Early Bird Discount:</strong> Register before March 31, 2024 
                and receive 15% off program fees.
              </div>
            </div>
          </div>
        </div>

        {/* Program Features */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">What's Included</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <i className="bi bi-check-circle text-success me-2"></i>
                <strong>Expert Instruction:</strong> Certified teachers and industry professionals
              </div>
              <div className="mb-3">
                <i className="bi bi-check-circle text-success me-2"></i>
                <strong>Materials & Equipment:</strong> All necessary supplies provided
              </div>
              <div className="mb-3">
                <i className="bi bi-check-circle text-success me-2"></i>
                <strong>Lunch & Snacks:</strong> Healthy meals and refreshments daily
              </div>
              <div className="mb-3">
                <i className="bi bi-check-circle text-success me-2"></i>
                <strong>Progress Reports:</strong> Detailed feedback and certificates
              </div>
              <div className="mb-3">
                <i className="bi bi-check-circle text-success me-2"></i>
                <strong>Safety First:</strong> Certified first-aid staff and secure campus
              </div>
              <div className="mb-3">
                <i className="bi bi-check-circle text-success me-2"></i>
                <strong>Extended Care:</strong> Optional early drop-off and late pick-up
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="card mt-4">
            <div className="card-body text-center">
              <h6>Questions About Summer Programs?</h6>
              <p className="small text-muted mb-3">
                Contact our Summer Programs Coordinator
              </p>
              <div className="mb-2">
                <i className="bi bi-envelope text-success me-2"></i>
                summer@delvok.ac.ke
              </div>
              <div className="mb-3">
                <i className="bi bi-telephone text-success me-2"></i>
                +254 720 123 456
              </div>
              <button className="btn btn-outline-success btn-sm">
                Schedule Consultation
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SummerPrograms;