import React from 'react';
import { Link } from 'react-router-dom';

function MissionVision() {
  const coreValues = [
    {
      title: 'Academic Excellence',
      description: 'Pursuing the highest standards in both Kenyan CBC and Cambridge curricula',
      icon: 'bi-award',
      color: 'primary'
    },
    {
      title: 'Cultural Pride',
      description: 'Nurturing Kenyan identity while embracing global perspectives',
      icon: 'bi-flag',
      color: 'success'
    },
    {
      title: 'Innovation',
      description: 'Continuously evolving our teaching methods and curriculum delivery',
      icon: 'bi-lightbulb',
      color: 'warning'
    },
    {
      title: 'Integrity',
      description: 'Upholding honesty, ethics, and moral courage in all we do',
      icon: 'bi-shield-check',
      color: 'info'
    },
    {
      title: 'Community',
      description: 'Building strong relationships among students, staff, and parents',
      icon: 'bi-people',
      color: 'secondary'
    },
    {
      title: 'Global Citizenship',
      description: 'Preparing students to contribute positively to the world',
      icon: 'bi-globe',
      color: 'danger'
    }
  ];

  const strategicPillars = [
    {
      pillar: 'Dual Curriculum Excellence',
      description: 'Maintain leadership in delivering both Kenyan CBC and Cambridge International curricula',
      initiatives: [
        'Continuous teacher training in both systems',
        'Curriculum integration research',
        'Student performance benchmarking'
      ]
    },
    {
      pillar: '21st Century Skills',
      description: 'Develop critical thinking, creativity, and digital literacy across all grades',
      initiatives: [
        'STEAM integration in all subjects',
        'Digital citizenship program',
        'Entrepreneurship education'
      ]
    },
    {
      pillar: 'Sustainable Development',
      description: 'Incorporate sustainability and environmental stewardship in education',
      initiatives: [
        'Green campus initiatives',
        'Environmental education',
        'Community sustainability projects'
      ]
    },
    {
      pillar: 'Global Partnerships',
      description: 'Expand international collaborations and student exchange programs',
      initiatives: [
        'University pathway programs',
        'International school partnerships',
        'Global classroom projects'
      ]
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/about">About</Link></li>
              <li className="breadcrumb-item active">Mission & Vision</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Our Mission & Vision</h1>
            <p className="lead mb-0">Guiding Principles for Educational Excellence</p>
          </div>
        </div>
      </div>

      {/* Mission Section */}
      <div className="row mb-5">
        <div className="col-lg-10 mx-auto">
          <div className="card bg-primary text-white">
            <div className="card-body p-5 text-center">
              <i className="bi bi-compass display-1 mb-3 opacity-50"></i>
              <h2 className="display-5 fw-bold mb-3">Our Mission</h2>
              <p className="fs-3 fst-italic mb-0">
                "To provide a transformative educational experience that integrates the best of Kenyan 
                and international curricula, nurturing academically excellent, culturally grounded, 
                and globally competitive citizens who make positive contributions to society."
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Vision Section */}
      <div className="row mb-5">
        <div className="col-lg-10 mx-auto">
          <div className="card bg-success text-white">
            <div className="card-body p-5 text-center">
              <i className="bi bi-eye display-1 mb-3 opacity-50"></i>
              <h2 className="display-5 fw-bold mb-3">Our Vision</h2>
              <p className="fs-3 fst-italic mb-0">
                "To be East Africa's leading educational institution renowned for pioneering 
                dual-curriculum excellence and developing future-ready leaders who excel 
                both locally and globally."
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Core Values */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Our Core Values</h3>
          <div className="row g-4">
            {coreValues.map((value, index) => (
              <div key={index} className="col-md-6 col-lg-4">
                <div className="card h-100 text-center border-0 shadow-sm">
                  <div className="card-body">
                    <i className={`${value.icon} display-1 text-${value.color} mb-3`}></i>
                    <h5 className="card-title">{value.title}</h5>
                    <p className="card-text">{value.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Strategic Pillars */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Strategic Pillars 2023-2028</h3>
          <div className="row g-4">
            {strategicPillars.map((pillar, index) => (
              <div key={index} className="col-lg-6">
                <div className="card h-100 border-primary">
                  <div className="card-header bg-primary text-white">
                    <h5 className="mb-0">{pillar.pillar}</h5>
                  </div>
                  <div className="card-body">
                    <p className="card-text">{pillar.description}</p>
                    <h6 className="mt-4">Key Initiatives:</h6>
                    <ul className="list-unstyled">
                      {pillar.initiatives.map((initiative, idx) => (
                        <li key={idx} className="mb-2">
                          <i className="bi bi-arrow-right-circle text-primary me-2"></i>
                          {initiative}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Educational Philosophy */}
      <div className="row">
        <div className="col-lg-8 mx-auto">
          <div className="card">
            <div className="card-header bg-dark text-white">
              <h4 className="mb-0">Our Educational Philosophy</h4>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <h5 className="text-primary">Holistic Development</h5>
                  <p>
                    We believe in educating the whole child - academically, socially, emotionally, 
                    and physically. Our dual curriculum approach ensures students develop both 
                    strong academic foundations and essential life skills.
                  </p>
                </div>
                <div className="col-md-6">
                  <h5 className="text-primary">Student-Centered Learning</h5>
                  <p>
                    Every student is unique. We personalize learning experiences to match individual 
                    strengths, interests, and learning styles while maintaining high academic standards.
                  </p>
                </div>
              </div>
              <div className="row mt-4">
                <div className="col-md-6">
                  <h5 className="text-primary">Cultural Integration</h5>
                  <p>
                    We celebrate Kenyan heritage while preparing students for global citizenship. 
                    Our curriculum seamlessly blends local context with international perspectives.
                  </p>
                </div>
                <div className="col-md-6">
                  <h5 className="text-primary">Lifelong Learning</h5>
                  <p>
                    We instill a love for learning that extends beyond the classroom. Our graduates 
                    are equipped with the skills and mindset to thrive in a rapidly changing world.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="row mt-5">
        <div className="col-12 text-center">
          <div className="card bg-light">
            <div className="card-body py-5">
              <h3 className="mb-3">Join Our Educational Journey</h3>
              <p className="fs-5 mb-4">
                Become part of a community committed to educational excellence and innovation.
              </p>
              <div className="d-flex justify-content-center gap-3">
                <button className="btn btn-primary btn-lg">
                  Schedule a Tour
                </button>
                <button className="btn btn-outline-primary btn-lg">
                  Download Prospectus
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MissionVision;