import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Club() {
  const [activeCategory, setActiveCategory] = useState('all');

  const clubs = [
    {
      id: 1,
      name: 'Science & Technology Club',
      category: 'academic',
      description: 'Explore the wonders of science through experiments, projects, and competitions.',
      meeting: 'Every Wednesday, 3:00 PM',
      location: 'Science Lab',
      teacher: 'Dr. Sarah Johnson',
      members: 25,
      achievements: ['National Science Fair Winners 2023', 'Innovation Award 2022'],
      image: '/images/clubs/science-club.jpg',
      status: 'active'
    },
    {
      id: 2,
      name: 'Debate & Public Speaking Club',
      category: 'academic',
      description: 'Develop critical thinking and public speaking skills through structured debates.',
      meeting: 'Every Tuesday, 4:00 PM',
      location: 'Library Conference Room',
      teacher: 'Ms. Grace Wambui',
      members: 18,
      achievements: ['Regional Debate Champions 2023', 'Best Speaker Award 2022'],
      image: '/images/clubs/debate-club.jpg',
      status: 'active'
    },
    {
      id: 3,
      name: 'Drama & Theater Club',
      category: 'arts',
      description: 'Express creativity through acting, script writing, and stage performances.',
      meeting: 'Every Thursday, 3:30 PM',
      location: 'Auditorium',
      teacher: 'Mr. David Omondi',
      members: 22,
      achievements: ['Drama Festival Gold Medal', 'Best Play 2023'],
      image: '/images/clubs/drama-club.jpg',
      status: 'active'
    },
    {
      id: 4,
      name: 'Music Club',
      category: 'arts',
      description: 'Learn various musical instruments and participate in school performances.',
      meeting: 'Every Monday, 4:00 PM',
      location: 'Music Room',
      teacher: 'Mrs. Lucy Kamau',
      members: 30,
      achievements: ['Music Festival Winners', 'Outstanding Performance Award'],
      image: '/images/clubs/music-club.jpg',
      status: 'active'
    },
    {
      id: 5,
      name: 'Environmental Club',
      category: 'service',
      description: 'Promote environmental awareness and participate in conservation projects.',
      meeting: 'Every Friday, 3:00 PM',
      location: 'Biology Lab',
      teacher: 'Mr. Robert Ochieng',
      members: 20,
      achievements: ['Tree Planting Initiative', 'Clean Energy Project'],
      image: '/images/clubs/environment-club.jpg',
      status: 'active'
    },
    {
      id: 6,
      name: 'ICT & Coding Club',
      category: 'academic',
      description: 'Learn programming, web development, and digital skills for the future.',
      meeting: 'Every Wednesday, 4:30 PM',
      location: 'Computer Lab',
      teacher: 'Mr. James Mwangi',
      members: 28,
      achievements: ['Hackathon Winners', 'App Development Contest'],
      image: '/images/clubs/coding-club.jpg',
      status: 'active'
    },
    {
      id: 7,
      name: 'Chess Club',
      category: 'games',
      description: 'Develop strategic thinking through chess tournaments and training sessions.',
      meeting: 'Every Monday, 3:30 PM',
      location: 'Library',
      teacher: 'Mr. Peter Njoroge',
      members: 15,
      achievements: ['County Chess Champions', 'Individual Medalists'],
      image: '/images/clubs/chess-club.jpg',
      status: 'active'
    },
    {
      id: 8,
      name: 'Journalism Club',
      category: 'media',
      description: 'Produce school newspaper, manage social media, and report school events.',
      meeting: 'Every Thursday, 4:00 PM',
      location: 'Media Center',
      teacher: 'Mrs. Amina Hassan',
      members: 12,
      achievements: ['Best School Newspaper Award', 'Media Excellence'],
      image: '/images/clubs/journalism-club.jpg',
      status: 'active'
    }
  ];

  const categories = [
    { id: 'all', name: 'All Clubs', count: clubs.length },
    { id: 'academic', name: 'Academic', count: clubs.filter(club => club.category === 'academic').length },
    { id: 'arts', name: 'Arts', count: clubs.filter(club => club.category === 'arts').length },
    { id: 'service', name: 'Service', count: clubs.filter(club => club.category === 'service').length },
    { id: 'games', name: 'Games', count: clubs.filter(club => club.category === 'games').length },
    { id: 'media', name: 'Media', count: clubs.filter(club => club.category === 'media').length }
  ];

  const filteredClubs = activeCategory === 'all' 
    ? clubs 
    : clubs.filter(club => club.category === activeCategory);

  const getCategoryColor = (category) => {
    const colors = {
      academic: 'primary',
      arts: 'success',
      service: 'warning',
      games: 'info',
      media: 'danger'
    };
    return colors[category] || 'secondary';
  };

  const ClubCard = ({ club }) => (
    <div className="col-md-6 col-lg-4">
      <div className="card club-card h-100 shadow-sm border-0">
        <div className="club-image position-relative">
          <div className={`image-placeholder bg-${getCategoryColor(club.category)} rounded-top p-4 text-white text-center`}>
            <i className="bi bi-people display-4"></i>
          </div>
          <div className="club-badges position-absolute top-0 end-0 m-3">
            <span className={`badge bg-${getCategoryColor(club.category)}`}>
              {club.category.charAt(0).toUpperCase() + club.category.slice(1)}
            </span>
          </div>
          <div className="members-badge position-absolute bottom-0 start-0 m-3">
            <span className="badge bg-dark">
              <i className="bi bi-people me-1"></i>
              {club.members} members
            </span>
          </div>
        </div>
        
        <div className="card-body">
          <h5 className="card-title">{club.name}</h5>
          <p className="card-text text-muted small">{club.description}</p>
          
          <div className="club-details">
            <div className="detail-item mb-2">
              <i className="bi bi-clock text-primary me-2"></i>
              <small>{club.meeting}</small>
            </div>
            <div className="detail-item mb-2">
              <i className="bi bi-geo-alt text-primary me-2"></i>
              <small>{club.location}</small>
            </div>
            <div className="detail-item mb-3">
              <i className="bi bi-person text-primary me-2"></i>
              <small>Teacher: {club.teacher}</small>
            </div>
          </div>

          {club.achievements.length > 0 && (
            <div className="achievements">
              <h6 className="small fw-bold mb-2">Achievements:</h6>
              {club.achievements.slice(0, 2).map((achievement, idx) => (
                <span key={idx} className="badge bg-light text-dark border me-1 mb-1 small">
                  {achievement}
                </span>
              ))}
              {club.achievements.length > 2 && (
                <span className="badge bg-secondary small">
                  +{club.achievements.length - 2} more
                </span>
              )}
            </div>
          )}
        </div>
        
        <div className="card-footer bg-transparent border-0">
          <div className="d-flex justify-content-between align-items-center">
            <span className={`badge bg-${club.status === 'active' ? 'success' : 'secondary'}`}>
              {club.status === 'active' ? 'Active' : 'Inactive'}
            </span>
            <button className="btn btn-outline-primary btn-sm">
              Join Club <i className="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="clubs-page">
      {/* Hero Section */}
      <section className="clubs-hero bg-primary text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">Student Clubs</h1>
              <p className="lead fs-4">
                Discover Your Passion, Develop Your Talents
              </p>
              <p className="mb-4">
                Join one of our diverse clubs to explore interests, develop skills, 
                and make lasting friendships beyond the classroom.
              </p>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">👥</div>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics */}
      <section className="py-4 bg-light">
        <div className="container">
          <div className="row text-center">
            <div className="col-md-3">
              <div className="display-6 fw-bold text-primary">{clubs.length}</div>
              <p className="text-muted">Active Clubs</p>
            </div>
            <div className="col-md-3">
              <div className="display-6 fw-bold text-success">
                {clubs.reduce((total, club) => total + club.members, 0)}+
              </div>
              <p className="text-muted">Student Members</p>
            </div>
            <div className="col-md-3">
              <div className="display-6 fw-bold text-warning">{categories.length - 1}</div>
              <p className="text-muted">Categories</p>
            </div>
            <div className="col-md-3">
              <div className="display-6 fw-bold text-info">15+</div>
              <p className="text-muted">Awards This Year</p>
            </div>
          </div>
        </div>
      </section>

      {/* Category Filter */}
      <section className="py-4">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="d-flex flex-wrap gap-2 justify-content-center">
                {categories.map(category => (
                  <button
                    key={category.id}
                    className={`btn ${
                      activeCategory === category.id ? 'btn-primary' : 'btn-outline-primary'
                    } position-relative`}
                    onClick={() => setActiveCategory(category.id)}
                  >
                    {category.name}
                    <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-secondary">
                      {category.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Clubs Grid */}
      <section className="py-5">
        <div className="container">
          <div className="row g-4">
            {filteredClubs.map(club => (
              <ClubCard key={club.id} club={club} />
            ))}
          </div>

          {filteredClubs.length === 0 && (
            <div className="text-center py-5">
              <i className="bi bi-people display-1 text-muted"></i>
              <h4 className="mt-3 text-muted">No clubs found</h4>
              <p className="text-muted">
                Try selecting a different category to see more clubs.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* How to Join Section */}
      <section className="py-5 bg-light">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6">
              <h2 className="display-6 fw-bold text-primary mb-4">How to Join a Club</h2>
              <div className="steps">
                {[
                  { step: 1, title: 'Explore Clubs', desc: 'Browse through our diverse club offerings' },
                  { step: 2, title: 'Attend Meeting', desc: 'Visit a club meeting to learn more' },
                  { step: 3, title: 'Register', desc: 'Fill out the club registration form' },
                  { step: 4, title: 'Participate', desc: 'Start attending regular meetings and activities' }
                ].map(step => (
                  <div key={step.step} className="step-item d-flex align-items-start mb-4">
                    <div className="step-number bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3 flex-shrink-0">
                      {step.step}
                    </div>
                    <div>
                      <h6 className="fw-bold mb-1">{step.title}</h6>
                      <p className="text-muted mb-0">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="col-lg-6">
              <div className="card border-0 shadow">
                <div className="card-body p-4">
                  <h5 className="card-title text-primary mb-4">Start a New Club</h5>
                  <p className="card-text mb-4">
                    Have an idea for a new club? We encourage student initiative and 
                    creativity. Start your own club with teacher supervision.
                  </p>
                  <div className="requirements">
                    <h6 className="fw-bold mb-3">Requirements:</h6>
                    <ul className="list-unstyled">
                      <li className="mb-2">
                        <i className="bi bi-check-circle text-success me-2"></i>
                        Minimum of 10 interested students
                      </li>
                      <li className="mb-2">
                        <i className="bi bi-check-circle text-success me-2"></i>
                        Teacher/staff advisor
                      </li>
                      <li className="mb-2">
                        <i className="bi bi-check-circle text-success me-2"></i>
                        Clear purpose and goals
                      </li>
                      <li className="mb-2">
                        <i className="bi bi-check-circle text-success me-2"></i>
                        Regular meeting schedule
                      </li>
                    </ul>
                  </div>
                  <button className="btn btn-primary mt-3">
                    <i className="bi bi-plus-circle me-2"></i>
                    Propose New Club
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <style jsx>{`
        .clubs-hero {
          background: linear-gradient(135deg, var(--bs-primary) 0%, #0056b3 100%);
        }
        
        .club-card {
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .club-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
        }
        
        .image-placeholder {
          min-height: 150px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .club-badges, .members-badge {
          z-index: 1;
        }
        
        .step-number {
          width: 40px;
          height: 40px;
          font-weight: bold;
        }
        
        .detail-item {
          display: flex;
          align-items: center;
        }
        
        .achievements {
          border-top: 1px solid #e9ecef;
          padding-top: 1rem;
        }
        
        .btn .badge {
          font-size: 0.6rem;
        }
        
        @media (max-width: 768px) {
          .clubs-hero .display-4 {
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

export default Club;