import React from 'react';

function CampusLife() {
  const activities = [
    {
      category: 'Sports',
      icon: '⚽',
      items: ['Football', 'Basketball', 'Athletics', 'Swimming', 'Volleyball']
    },
    {
      category: 'Clubs',
      icon: '🎭',
      items: ['Drama Club', 'Music Club', 'Debate Club', 'Science Club', 'ICT Club']
    },
    {
      category: 'Arts',
      icon: '🎨',
      items: ['Drawing', 'Painting', 'Sculpture', 'Dance', 'Creative Writing']
    },
    {
      category: 'Leadership',
      icon: '👥',
      items: ['Student Council', 'Prefects', 'Class Monitors', 'Club Leaders']
    }
  ];

  return (
    <div className="campus-life-page">
      {/* Hero Section */}
      <section className="campus-hero bg-success text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">Campus Life</h1>
              <p className="lead fs-4">
                Beyond the Classroom - Holistic Development and Fun
              </p>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">🎪</div>
            </div>
          </div>
        </div>
      </section>

      {/* Activities Overview */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center display-6 fw-bold text-primary mb-5">Student Activities</h2>
          <div className="row g-4">
            {activities.map((activity, index) => (
              <div key={index} className="col-md-6 col-lg-3">
                <div className="card activity-card border-0 shadow-sm h-100">
                  <div className="card-body text-center p-4">
                    <div className="activity-icon display-1 mb-3">{activity.icon}</div>
                    <h5 className="card-title text-primary">{activity.category}</h5>
                    <ul className="list-unstyled">
                      {activity.items.map((item, idx) => (
                        <li key={idx} className="text-muted mb-1">
                          <i className="bi bi-check-circle text-success me-2"></i>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Facilities */}
      <section className="py-5 bg-light">
        <div className="container">
          <h2 className="text-center display-6 fw-bold text-primary mb-5">Our Facilities</h2>
          <div className="row g-4">
            {[
              { name: 'Science Labs', icon: '🔬', desc: 'Fully equipped laboratories for Physics, Chemistry, and Biology' },
              { name: 'Library', icon: '📚', desc: 'Extensive collection of books and digital learning resources' },
              { name: 'Sports Complex', icon: '🏟️', desc: 'Football field, basketball court, and swimming pool' },
              { name: 'Computer Lab', icon: '💻', desc: 'Modern computers with internet access and coding software' },
              { name: 'Art Studio', icon: '🎨', desc: 'Creative space for drawing, painting, and crafts' },
              { name: 'Music Room', icon: '🎵', desc: 'Instruments and practice rooms for music education' }
            ].map((facility, index) => (
              <div key={index} className="col-md-6 col-lg-4">
                <div className="card facility-card border-0 h-100">
                  <div className="card-body text-center p-4">
                    <div className="facility-icon display-4 mb-3">{facility.icon}</div>
                    <h5 className="card-title">{facility.name}</h5>
                    <p className="card-text text-muted">{facility.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Daily Schedule */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center display-6 fw-bold text-primary mb-5">Typical School Day</h2>
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <div className="card shadow-sm border-0">
                <div className="card-body">
                  <div className="schedule-timeline">
                    {[
                      { time: '7:30 AM', activity: 'Morning Assembly', desc: 'Prayers and announcements' },
                      { time: '8:00 AM', activity: 'Lesson 1-2', desc: 'Core subjects' },
                      { time: '10:00 AM', activity: 'Break', desc: 'Snack and relaxation' },
                      { time: '10:30 AM', activity: 'Lesson 3-4', desc: 'Subject continuation' },
                      { time: '12:30 PM', activity: 'Lunch Break', desc: 'Meal and social time' },
                      { time: '2:00 PM', activity: 'Co-curricular', desc: 'Clubs and sports' },
                      { time: '4:00 PM', activity: 'Dismissal', desc: 'School day ends' }
                    ].map((slot, index) => (
                      <div key={index} className="schedule-item d-flex align-items-center mb-4">
                        <div className="schedule-time bg-primary text-white rounded p-2 text-center me-4">
                          <div className="fw-bold">{slot.time}</div>
                        </div>
                        <div className="schedule-content flex-grow-1">
                          <h6 className="mb-1 fw-bold">{slot.activity}</h6>
                          <p className="text-muted mb-0 small">{slot.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <style jsx>{`
        .campus-hero {
          background: linear-gradient(135deg, var(--bs-success) 0%, #198754 100%);
        }
        
        .activity-card, .facility-card {
          transition: transform 0.3s ease;
        }
        
        .activity-card:hover, .facility-card:hover {
          transform: translateY(-5px);
        }
        
        .schedule-time {
          min-width: 80px;
          flex-shrink: 0;
        }
        
        .schedule-item {
          border-left: 3px solid var(--bs-primary);
          padding-left: 1rem;
        }
      `}</style>
    </div>
  );
}

export default CampusLife;