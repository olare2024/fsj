import React from 'react';
import { Link } from 'react-router-dom';

function SchoolHistory() {
  const timelineEvents = [
    {
      year: '1995',
      title: 'Foundation Established',
      description: 'Delvok Academy founded by Dr. Elizabeth Delvok with a vision to provide world-class education in Kenya',
      image: '/images/history/foundation.jpg',
      milestone: 'Started with 50 students and 8 teachers'
    },
    {
      year: '1998',
      title: 'Cambridge Program Launch',
      description: 'Became one of the first schools in Kenya to offer Cambridge International curriculum alongside national system',
      image: '/images/history/cambridge-launch.jpg',
      milestone: 'First IGCSE class graduated with 100% pass rate'
    },
    {
      year: '2005',
      title: 'Campus Expansion',
      description: 'Moved to current 20-acre campus with state-of-the-art facilities and boarding program',
      image: '/images/history/campus-expansion.jpg',
      milestone: 'Student population grew to 500+'
    },
    {
      year: '2010',
      title: 'STEM Center Opening',
      description: 'Opened the Advanced Science and Technology Center with fully equipped laboratories',
      image: '/images/history/stem-center.jpg',
      milestone: 'First Kenyan school with dedicated robotics lab'
    },
    {
      year: '2017',
      title: 'CBC Implementation',
      description: 'Successfully integrated Kenyan Competency-Based Curriculum alongside Cambridge program',
      image: '/images/history/cbc-implementation.jpg',
      milestone: 'Pioneered dual curriculum approach in East Africa'
    },
    {
      year: '2023',
      title: 'Global Recognition',
      description: 'Awarded "Best International School in East Africa" by International School Awards',
      image: '/images/history/global-award.jpg',
      milestone: 'Alumni network spans 35 countries worldwide'
    }
  ];

  const founders = [
    {
      name: 'Dr. Elizabeth Delvok',
      role: 'Founder & Visionary',
      contribution: 'Established the school with a vision to bridge Kenyan and international education systems',
      image: '/images/founders/elizabeth-delvok.jpg'
    },
    {
      name: 'Prof. Michael Omondi',
      role: 'Co-Founder & Academic Director',
      contribution: 'Developed the dual curriculum model that became the school\'s signature approach',
      image: '/images/founders/michael-omondi.jpg'
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
              <li className="breadcrumb-item active">School History</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Our History & Legacy</h1>
            <p className="lead mb-0">28 Years of Educational Excellence in Kenya</p>
            <div className="mt-3">
              <span className="badge bg-primary fs-6">Established 1995</span>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-dark text-white mb-5">
        <div className="card-body p-5 text-center">
          <h2 className="display-5 fw-bold mb-3">Pioneering Dual Curriculum Education</h2>
          <p className="fs-5 mb-4">
            For nearly three decades, Delvok Academy has been at the forefront of educational innovation in Kenya, 
            successfully blending the best of Kenyan CBC and Cambridge International curricula to create globally 
            competitive students who remain rooted in their Kenyan heritage.
          </p>
        </div>
      </div>

      {/* Timeline Section */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-5">Our Journey Through the Years</h3>
          <div className="timeline-wrapper">
            {timelineEvents.map((event, index) => (
              <div key={index} className="timeline-item mb-5">
                <div className="row align-items-center">
                  <div className={`col-md-6 ${index % 2 === 0 ? '' : 'order-md-2'}`}>
                    <div className="timeline-content card h-100">
                      <div className="card-body">
                        <div className="timeline-year display-6 fw-bold text-primary mb-2">
                          {event.year}
                        </div>
                        <h4 className="card-title mb-3">{event.title}</h4>
                        <p className="card-text mb-3">{event.description}</p>
                        <div className="timeline-milestone p-3 bg-light rounded">
                          <i className="bi bi-star-fill text-warning me-2"></i>
                          <strong>Milestone:</strong> {event.milestone}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className={`col-md-6 ${index % 2 === 0 ? '' : 'order-md-1'}`}>
                    <div className="timeline-image-placeholder bg-light rounded d-flex align-items-center justify-content-center"
                         style={{height: '300px'}}>
                      <i className="bi bi-image display-1 text-muted"></i>
                      <small className="position-absolute bottom-0 start-0 p-2 text-muted">
                        {event.year} - {event.title}
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Founders Section */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Our Visionary Founders</h3>
          <div className="row justify-content-center">
            {founders.map((founder, index) => (
              <div key={index} className="col-md-6 col-lg-5 mb-4">
                <div className="card h-100 text-center">
                  <div className="card-body">
                    <div className="founder-image-placeholder bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                         style={{width: '120px', height: '120px'}}>
                      <i className="bi bi-person display-3 text-muted"></i>
                    </div>
                    <h5 className="card-title">{founder.name}</h5>
                    <p className="card-text text-primary">{founder.role}</p>
                    <p className="card-text">{founder.contribution}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Legacy Section */}
      <div className="row">
        <div className="col-lg-8 mx-auto">
          <div className="card bg-primary text-white">
            <div className="card-body p-5 text-center">
              <h3 className="display-6 fw-bold mb-3">Our Enduring Legacy</h3>
              <p className="fs-5 mb-4">
                Today, Delvok Academy stands as a testament to visionary educational leadership. 
                We continue to innovate while honoring our founding principles of academic excellence, 
                cultural pride, and global citizenship.
              </p>
              <div className="row text-center">
                <div className="col-md-4 mb-3">
                  <div className="display-4 fw-bold">2,500+</div>
                  <div>Alumni Worldwide</div>
                </div>
                <div className="col-md-4 mb-3">
                  <div className="display-4 fw-bold">28</div>
                  <div>Years of Excellence</div>
                </div>
                <div className="col-md-4 mb-3">
                  <div className="display-4 fw-bold">35+</div>
                  <div>Countries Represented</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SchoolHistory;