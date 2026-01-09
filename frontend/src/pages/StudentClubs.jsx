import React from 'react';
import { Link } from 'react-router-dom';

function StudentClubs() {
  const clubs = [
    {
      name: 'Robotics Club',
      category: 'STEM',
      advisor: 'Dr. Smith',
      meeting: 'Tuesdays, 3:30 PM',
      room: 'Science Lab 201',
      members: 25,
      description: 'Build and program robots for competitions'
    },
    {
      name: 'Debate Team',
      category: 'Academic',
      advisor: 'Ms. Johnson',
      meeting: 'Wednesdays, 4:00 PM',
      room: 'Library Conference Room',
      members: 18,
      description: 'Develop public speaking and critical thinking skills'
    },
    {
      name: 'Art Society',
      category: 'Arts',
      advisor: 'Mr. Davis',
      meeting: 'Mondays, 3:30 PM',
      room: 'Art Studio 105',
      members: 32,
      description: 'Explore various art forms and techniques'
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Student Clubs & Organizations</h1>
          <p className="lead">Join our vibrant community of student-led organizations</p>
        </div>
        <Link to="/campus-life" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Campus Life
        </Link>
      </div>

      <div className="row g-4">
        {clubs.map((club, index) => (
          <div key={index} className="col-md-6 col-lg-4">
            <div className="card h-100 shadow-sm">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">{club.name}</h5>
                <span className="badge bg-primary">{club.category}</span>
              </div>
              <div className="card-body">
                <p className="card-text">{club.description}</p>
                
                <div className="club-details">
                  <div className="d-flex align-items-center mb-2">
                    <i className="bi bi-person text-primary me-2"></i>
                    <span>Advisor: {club.advisor}</span>
                  </div>
                  <div className="d-flex align-items-center mb-2">
                    <i className="bi bi-clock text-primary me-2"></i>
                    <span>{club.meeting}</span>
                  </div>
                  <div className="d-flex align-items-center mb-2">
                    <i className="bi bi-geo-alt text-primary me-2"></i>
                    <span>Room: {club.room}</span>
                  </div>
                  <div className="d-flex align-items-center">
                    <i className="bi bi-people text-primary me-2"></i>
                    <span>{club.members} Members</span>
                  </div>
                </div>
              </div>
              <div className="card-footer">
                <div className="d-flex gap-2">
                  <button className="btn btn-primary btn-sm">Join Club</button>
                  <button className="btn btn-outline-secondary btn-sm">More Info</button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default StudentClubs;