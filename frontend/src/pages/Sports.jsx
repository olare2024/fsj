import React, { useState } from 'react';

function Sports() {
  const [activeSport, setActiveSport] = useState('all');

  const sports = [
    {
      id: 1,
      name: 'Football',
      category: 'team',
      description: 'Develop teamwork, strategy, and physical fitness through competitive football.',
      coach: 'Coach James Mwangi',
      practice: 'Monday & Wednesday, 4:00 PM',
      location: 'Main Football Field',
      team: 'Senior Team',
      members: 20,
      achievements: ['County Champions 2023', 'Regional Semi-finalists'],
      image: '/images/sports/football.jpg',
      status: 'active',
      level: 'competitive'
    },
    {
      id: 2,
      name: 'Basketball',
      category: 'team',
      description: 'Fast-paced game focusing on agility, coordination, and team strategy.',
      coach: 'Coach David Kimani',
      practice: 'Tuesday & Thursday, 4:30 PM',
      location: 'Basketball Court',
      team: 'Varsity Team',
      members: 15,
      achievements: ['Regional Champions', 'MVP Award 2023'],
      image: '/images/sports/basketball.jpg',
      status: 'active',
      level: 'competitive'
    },
    {
      id: 3,
      name: 'Athletics',
      category: 'individual',
      description: 'Track and field events including sprints, long distance, and field events.',
      coach: 'Coach Sarah Johnson',
      practice: 'Daily, 3:30 PM',
      location: 'School Track',
      team: 'Various',
      members: 35,
      achievements: ['10 Gold Medals County Meet', 'Record Breakers'],
      image: '/images/sports/athletics.jpg',
      status: 'active',
      level: 'competitive'
    },
    {
      id: 4,
      name: 'Swimming',
      category: 'individual',
      description: 'Competitive swimming training for various strokes and distances.',
      coach: 'Coach Grace Wambui',
      practice: 'Monday, Wednesday, Friday - 3:00 PM',
      location: 'School Pool',
      team: 'Swim Team',
      members: 18,
      achievements: ['Regional Swim Meet Winners', 'New Records Set'],
      image: '/images/sports/swimming.jpg',
      status: 'active',
      level: 'competitive'
    },
    {
      id: 5,
      name: 'Volleyball',
      category: 'team',
      description: 'Develop coordination, teamwork, and strategic play in volleyball.',
      coach: 'Coach Robert Ochieng',
      practice: 'Tuesday & Thursday, 3:30 PM',
      location: 'Volleyball Court',
      team: 'Junior & Senior Teams',
      members: 24,
      achievements: ['County Volleyball League', 'Sportsmanship Award'],
      image: '/images/sports/volleyball.jpg',
      status: 'active',
      level: 'competitive'
    },
    {
      id: 6,
      name: 'Table Tennis',
      category: 'individual',
      description: 'Fast-paced indoor sport focusing on reflexes and precision.',
      coach: 'Coach Peter Njoroge',
      practice: 'Friday, 4:00 PM',
      location: 'Games Room',
      team: 'Table Tennis Club',
      members: 12,
      achievements: ['Individual Championships', 'Team Tournament'],
      image: '/images/sports/table-tennis.jpg',
      status: 'active',
      level: 'recreational'
    },
    {
      id: 7,
      name: 'Badminton',
      category: 'individual',
      description: 'Develop agility and strategic thinking through badminton.',
      coach: 'Coach Lucy Kamau',
      practice: 'Wednesday, 4:00 PM',
      location: 'School Hall',
      team: 'Badminton Club',
      members: 16,
      achievements: ['Regional Tournament', 'Skills Development'],
      image: '/images/sports/badminton.jpg',
      status: 'active',
      level: 'recreational'
    },
    {
      id: 8,
      name: 'Rugby',
      category: 'team',
      description: 'Build strength, endurance, and teamwork in rugby.',
      coach: 'Coach Michael Omondi',
      practice: 'Monday & Friday, 4:30 PM',
      location: 'Rugby Field',
      team: 'School Team',
      members: 25,
      achievements: ['Developing Program', 'Friendly Matches'],
      image: '/images/sports/rugby.jpg',
      status: 'active',
      level: 'development'
    }
  ];

  const categories = [
    { id: 'all', name: 'All Sports', count: sports.length },
    { id: 'team', name: 'Team Sports', count: sports.filter(sport => sport.category === 'team').length },
    { id: 'individual', name: 'Individual Sports', count: sports.filter(sport => sport.category === 'individual').length }
  ];

  const levels = [
    { id: 'all', name: 'All Levels', count: sports.length },
    { id: 'competitive', name: 'Competitive', count: sports.filter(sport => sport.level === 'competitive').length },
    { id: 'recreational', name: 'Recreational', count: sports.filter(sport => sport.level === 'recreational').length },
    { id: 'development', name: 'Development', count: sports.filter(sport => sport.level === 'development').length }
  ];

  const [activeLevel, setActiveLevel] = useState('all');

  const filteredSports = sports.filter(sport => {
    const categoryMatch = activeSport === 'all' || sport.category === activeSport;
    const levelMatch = activeLevel === 'all' || sport.level === activeLevel;
    return categoryMatch && levelMatch;
  });

  const getLevelColor = (level) => {
    const colors = {
      competitive: 'danger',
      recreational: 'success',
      development: 'warning'
    };
    return colors[level] || 'secondary';
  };

  const getCategoryColor = (category) => {
    return category === 'team' ? 'primary' : 'info';
  };

  const SportsCard = ({ sport }) => (
    <div className="col-md-6 col-lg-4">
      <div className="card sports-card h-100 shadow-sm border-0">
        <div className="sports-image position-relative">
          <div className={`image-placeholder bg-${getCategoryColor(sport.category)} rounded-top p-4 text-white text-center`}>
            <i className="bi bi-trophy display-4"></i>
          </div>
          <div className="sports-badges position-absolute top-0 end-0 m-3">
            <span className={`badge bg-${getLevelColor(sport.level)} me-1`}>
              {sport.level.charAt(0).toUpperCase() + sport.level.slice(1)}
            </span>
            <span className={`badge bg-${getCategoryColor(sport.category)}`}>
              {sport.category.charAt(0).toUpperCase() + sport.category.slice(1)}
            </span>
          </div>
          <div className="members-badge position-absolute bottom-0 start-0 m-3">
            <span className="badge bg-dark">
              <i className="bi bi-people me-1"></i>
              {sport.members} players
            </span>
          </div>
        </div>
        
        <div className="card-body">
          <h5 className="card-title">{sport.name}</h5>
          <p className="card-text text-muted small">{sport.description}</p>
          
          <div className="sports-details">
            <div className="detail-item mb-2">
              <i className="bi bi-person text-primary me-2"></i>
              <small>Coach: {sport.coach}</small>
            </div>
            <div className="detail-item mb-2">
              <i className="bi bi-clock text-primary me-2"></i>
              <small>{sport.practice}</small>
            </div>
            <div className="detail-item mb-2">
              <i className="bi bi-geo-alt text-primary me-2"></i>
              <small>{sport.location}</small>
            </div>
            <div className="detail-item mb-3">
              <i className="bi bi-people text-primary me-2"></i>
              <small>Team: {sport.team}</small>
            </div>
          </div>

          {sport.achievements.length > 0 && (
            <div className="achievements">
              <h6 className="small fw-bold mb-2">Recent Achievements:</h6>
              {sport.achievements.slice(0, 2).map((achievement, idx) => (
                <span key={idx} className="badge bg-light text-dark border me-1 mb-1 small">
                  {achievement}
                </span>
              ))}
              {sport.achievements.length > 2 && (
                <span className="badge bg-secondary small">
                  +{sport.achievements.length - 2} more
                </span>
              )}
            </div>
          )}
        </div>
        
        <div className="card-footer bg-transparent border-0">
          <div className="d-flex justify-content-between align-items-center">
            <span className={`badge bg-${sport.status === 'active' ? 'success' : 'secondary'}`}>
              {sport.status === 'active' ? 'Active' : 'Off-season'}
            </span>
            <button className="btn btn-outline-primary btn-sm">
              Try Out <i className="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="sports-page">
      {/* Hero Section */}
      <section className="sports-hero bg-success text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">School Sports</h1>
              <p className="lead fs-4">
                Excellence in Athletics, Character in Competition
              </p>
              <p className="mb-4">
                Develop physical fitness, teamwork, and sportsmanship through our 
                comprehensive sports program with competitive and recreational options.
              </p>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">⚽</div>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics */}
      <section className="py-4 bg-light">
        <div className="container">
          <div className="row text-center">
            <div className="col-md-3">
              <div className="display-6 fw-bold text-primary">{sports.length}</div>
              <p className="text-muted">Sports Offered</p>
            </div>
            <div className="col-md-3">
              <div className="display-6 fw-bold text-success">
                {sports.reduce((total, sport) => total + sport.members, 0)}+
              </div>
              <p className="text-muted">Student Athletes</p>
            </div>
            <div className="col-md-3">
              <div className="display-6 fw-bold text-warning">15</div>
              <p className="text-muted">Qualified Coaches</p>
            </div>
            <div className="col-md-3">
              <div className="display-6 fw-bold text-info">25+</div>
              <p className="text-muted">Championships Won</p>
            </div>
          </div>
        </div>
      </section>

      {/* Filters */}
      <section className="py-4">
        <div className="container">
          <div className="row">
            <div className="col-md-6 mb-3">
              <h6 className="text-center mb-3">Filter by Category</h6>
              <div className="d-flex flex-wrap gap-2 justify-content-center">
                {categories.map(category => (
                  <button
                    key={category.id}
                    className={`btn ${
                      activeSport === category.id ? 'btn-primary' : 'btn-outline-primary'
                    }`}
                    onClick={() => setActiveSport(category.id)}
                  >
                    {category.name}
                    <span className="badge bg-secondary ms-1">{category.count}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="col-md-6">
              <h6 className="text-center mb-3">Filter by Level</h6>
              <div className="d-flex flex-wrap gap-2 justify-content-center">
                {levels.map(level => (
                  <button
                    key={level.id}
                    className={`btn ${
                      activeLevel === level.id ? `btn-${getLevelColor(level.id)}` : `btn-outline-${getLevelColor(level.id)}`
                    }`}
                    onClick={() => setActiveLevel(level.id)}
                  >
                    {level.name}
                    <span className="badge bg-secondary ms-1">{level.count}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Sports Grid */}
      <section className="py-5">
        <div className="container">
          <div className="row g-4">
            {filteredSports.map(sport => (
              <SportsCard key={sport.id} sport={sport} />
            ))}
          </div>

          {filteredSports.length === 0 && (
            <div className="text-center py-5">
              <i className="bi bi-trophy display-1 text-muted"></i>
              <h4 className="mt-3 text-muted">No sports found</h4>
              <p className="text-muted">
                Try adjusting your filters to see more sports.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Facilities Section */}
      <section className="py-5 bg-primary text-white">
        <div className="container">
          <h2 className="text-center display-6 fw-bold mb-5">Sports Facilities</h2>
          <div className="row g-4">
            {[
              { name: 'Olympic-size Swimming Pool', icon: '🏊', desc: 'Heated pool for training and competitions' },
              { name: 'All-weather Football Pitch', icon: '⚽', desc: 'Professional turf with floodlights' },
              { name: 'Basketball Courts', icon: '🏀', desc: 'Indoor and outdoor courts available' },
              { name: 'Athletics Track', icon: '🏃', desc: '400m synthetic track with field events' },
              { name: 'Tennis Courts', icon: '🎾', desc: 'Hard courts for tennis training' },
              { name: 'Sports Hall', icon: '🏟️', desc: 'Multi-purpose indoor sports facility' }
            ].map((facility, index) => (
              <div key={index} className="col-md-6 col-lg-4">
                <div className="card facility-card bg-dark border-0 h-100">
                  <div className="card-body text-center p-4">
                    <div className="facility-icon display-4 mb-3">{facility.icon}</div>
                    <h5 className="card-title">{facility.name}</h5>
                    <p className="card-text text-light opacity-75">{facility.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Upcoming Events */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center display-6 fw-bold text-primary mb-5">Upcoming Sports Events</h2>
          <div className="row">
            <div className="col-lg-8 mx-auto">
              <div className="card shadow-sm border-0">
                <div className="card-body">
                  <div className="table-responsive">
                    <table className="table table-hover">
                      <thead className="table-success">
                        <tr>
                          <th>Date</th>
                          <th>Event</th>
                          <th>Sport</th>
                          <th>Location</th>
                          <th>Type</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Mar 22, 2024</td>
                          <td>Inter-school Football Tournament</td>
                          <td>Football</td>
                          <td>Home Field</td>
                          <td><span className="badge bg-danger">Competitive</span></td>
                        </tr>
                        <tr>
                          <td>Mar 29, 2024</td>
                          <td>Annual Sports Day</td>
                          <td>Athletics</td>
                          <td>School Track</td>
                          <td><span className="badge bg-success">Recreational</span></td>
                        </tr>
                        <tr>
                          <td>Apr 5, 2024</td>
                          <td>Basketball Friendly Match</td>
                          <td>Basketball</td>
                          <td>Away Game</td>
                          <td><span className="badge bg-warning">Development</span></td>
                        </tr>
                        <tr>
                          <td>Apr 12, 2024</td>
                          <td>Swimming Gala</td>
                          <td>Swimming</td>
                          <td>School Pool</td>
                          <td><span className="badge bg-danger">Competitive</span></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <style jsx>{`
        .sports-hero {
          background: linear-gradient(135deg, var(--bs-success) 0%, #198754 100%);
        }
        
        .sports-card {
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .sports-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
        }
        
        .image-placeholder {
          min-height: 150px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .sports-badges, .members-badge {
          z-index: 1;
        }
        
        .detail-item {
          display: flex;
          align-items: center;
        }
        
        .achievements {
          border-top: 1px solid #e9ecef;
          padding-top: 1rem;
        }
        
        .facility-card {
          transition: transform 0.3s ease;
        }
        
        .facility-card:hover {
          transform: translateY(-5px);
        }
        
        @media (max-width: 768px) {
          .sports-hero .display-4 {
            font-size: 2.5rem;
          }
          
          .btn {
            margin-bottom: 0.5rem;
          }
        }
      `}</style>
    </div>
  );
}

export default Sports;