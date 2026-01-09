import React from 'react';

function About() {
  return (
    <div className="about-page">
      {/* Hero Section */}
      <section className="about-hero bg-primary text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">About Delvok Academy</h1>
              <p className="lead fs-4">
                Excellence in Education Since 2010 - Nurturing Future Leaders
              </p>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">🏫</div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-5">
        <div className="container">
          <div className="row g-4">
            <div className="col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <div className="text-primary display-6 mb-3">🎯</div>
                  <h3 className="card-title text-primary">Our Mission</h3>
                  <p className="card-text">
                    To provide quality education that nurtures holistic development, 
                    fosters critical thinking, and prepares students for lifelong learning 
                    and responsible citizenship in a dynamic world.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <div className="text-success display-6 mb-3">👁️</div>
                  <h3 className="card-title text-success">Our Vision</h3>
                  <p className="card-text">
                    To be a center of academic excellence that produces innovative, 
                    ethical, and globally competitive individuals who contribute 
                    positively to society.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* School History */}
      <section className="py-5 bg-light">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6">
              <h2 className="display-6 fw-bold text-primary mb-4">Our Story</h2>
              <p className="lead mb-4">
                Founded in 2010, Delvok Academy has grown from a small community school 
                to a leading educational institution in Kenya.
              </p>
              <div className="timeline">
                <div className="timeline-item">
                  <div className="timeline-year text-primary fw-bold">2010</div>
                  <div className="timeline-content">
                    <h5>Foundation</h5>
                    <p>Established with 50 students and 5 teachers</p>
                  </div>
                </div>
                <div className="timeline-item">
                  <div className="timeline-year text-primary fw-bold">2015</div>
                  <div className="timeline-content">
                    <h5>Expansion</h5>
                    <p>Introduced CBC curriculum and expanded to Grade 6</p>
                  </div>
                </div>
                <div className="timeline-item">
                  <div className="timeline-year text-primary fw-bold">2020</div>
                  <div className="timeline-content">
                    <h5>Modernization</h5>
                    <p>Opened new science labs and computer centers</p>
                  </div>
                </div>
                <div className="timeline-item">
                  <div className="timeline-year text-primary fw-bold">2024</div>
                  <div className="timeline-content">
                    <h5>Excellence</h5>
                    <p>Over 500 students with state-of-the-art facilities</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="about-image text-center">
                <div className="image-placeholder bg-primary rounded p-5 text-white">
                  <i className="bi bi-building display-1"></i>
                  <p className="mt-3">School Campus Image</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Values */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center display-6 fw-bold text-primary mb-5">Our Core Values</h2>
          <div className="row g-4">
            {[
              { icon: '⚖️', title: 'Integrity', desc: 'Honesty and ethical conduct in all endeavors' },
              { icon: '🌟', title: 'Excellence', desc: 'Striving for the highest standards in education' },
              { icon: '🤝', title: 'Respect', desc: 'Valuing diversity and treating all with dignity' },
              { icon: '💡', title: 'Innovation', desc: 'Embracing creativity and modern teaching methods' },
              { icon: '🌍', title: 'Global Citizenship', desc: 'Preparing students for worldwide challenges' },
              { icon: '❤️', title: 'Compassion', desc: 'Caring for others and the community' }
            ].map((value, index) => (
              <div key={index} className="col-md-4">
                <div className="card value-card border-0 h-100 text-center">
                  <div className="card-body p-4">
                    <div className="value-icon display-6 mb-3">{value.icon}</div>
                    <h5 className="card-title">{value.title}</h5>
                    <p className="card-text text-muted">{value.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <style jsx>{`
        .about-hero {
          background: linear-gradient(135deg, var(--bs-primary) 0%, #0056b3 100%);
        }
        
        .timeline {
          position: relative;
          padding-left: 2rem;
        }
        
        .timeline::before {
          content: '';
          position: absolute;
          left: 0;
          top: 0;
          bottom: 0;
          width: 4px;
          background: var(--bs-primary);
          border-radius: 2px;
        }
        
        .timeline-item {
          position: relative;
          margin-bottom: 2rem;
        }
        
        .timeline-year {
          position: absolute;
          left: -2rem;
          top: 0;
          background: white;
          padding: 0.25rem 0.5rem;
          border: 2px solid var(--bs-primary);
          border-radius: 20px;
          font-size: 0.875rem;
        }
        
        .timeline-content {
          padding-left: 1rem;
        }
        
        .value-card {
          transition: transform 0.3s ease;
        }
        
        .value-card:hover {
          transform: translateY(-5px);
        }
        
        .image-placeholder {
          min-height: 300px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </div>
  );
}

export default About;