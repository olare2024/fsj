import React from 'react';
import { Link } from 'react-router-dom';

function Leadership() {
  const leadershipTeam = [
    {
      name: 'Dr. Sarah Mwangi',
      position: 'Head of School',
      qualifications: ['PhD Educational Leadership', 'MEd Curriculum Design', 'BEd Arts'],
      experience: '15 years in educational leadership',
      bio: 'Dr. Mwangi has been instrumental in developing Delvok Academy\'s dual curriculum model and expanding the school\'s international partnerships.',
      email: 's.mwangi@delvok.ac.ke',
      phone: '+254 720 100 001',
      image: '/images/leadership/sarah-mwangi.jpg',
      responsibilities: [
        'Overall school administration and strategic direction',
        'Curriculum development and implementation',
        'International accreditation and partnerships',
        'Faculty development and leadership'
      ]
    },
    {
      name: 'Mr. James Ochieng',
      position: 'Deputy Head - Academics',
      qualifications: ['MSc Mathematics', 'PGCE International Education', 'BEd Science'],
      experience: '12 years in academic administration',
      bio: 'Mr. Ochieng oversees the academic programs across both CBC and Cambridge curricula, ensuring academic excellence and continuous improvement.',
      email: 'j.ochieng@delvok.ac.ke',
      phone: '+254 720 100 002',
      image: '/images/leadership/james-ochieng.jpg',
      responsibilities: [
        'Academic program coordination',
        'Teacher professional development',
        'Student academic performance monitoring',
        'Curriculum alignment and innovation'
      ]
    },
    {
      name: 'Mrs. Amina Hassan',
      position: 'Deputy Head - Student Affairs',
      qualifications: ['MEd Educational Psychology', 'BEd Counseling', 'Child Protection Certified'],
      experience: '10 years in student welfare and development',
      bio: 'Mrs. Hassan leads student support services, ensuring a safe and nurturing environment for all students\' holistic development.',
      email: 'a.hassan@delvok.ac.ke',
      phone: '+254 720 100 003',
      image: '/images/leadership/amina-hassan.jpg',
      responsibilities: [
        'Student welfare and pastoral care',
        'Discipline and behavior management',
        'Parent communication and engagement',
        'Student leadership development'
      ]
    },
    {
      name: 'Mr. David Kamau',
      position: 'Business Manager',
      qualifications: ['MBA Finance', 'CPA K', 'BCom Accounting'],
      experience: '14 years in school administration and finance',
      bio: 'Mr. Kamau manages the school\'s financial operations and infrastructure development, ensuring sustainable growth and resource optimization.',
      email: 'd.kamau@delvok.ac.ke',
      phone: '+254 720 100 004',
      image: '/images/leadership/david-kamau.jpg',
      responsibilities: [
        'Financial planning and management',
        'Infrastructure development',
        'Human resources administration',
        'Strategic resource allocation'
      ]
    }
  ];

  const boardMembers = [
    {
      name: 'Dr. Elizabeth Delvok',
      role: 'Chairperson & Founder',
      affiliation: 'Delvok Education Foundation',
      expertise: 'Educational Entrepreneurship'
    },
    {
      name: 'Prof. Michael Omondi',
      role: 'Vice Chairperson',
      affiliation: 'University of Nairobi',
      expertise: 'Curriculum Development'
    },
    {
      name: 'Ms. Grace Wanjiku',
      role: 'Treasurer',
      affiliation: 'Kenya Bankers Association',
      expertise: 'Finance & Investment'
    },
    {
      name: 'Mr. Robert Mutiso',
      role: 'Secretary',
      affiliation: 'Ministry of Education',
      expertise: 'Educational Policy'
    }
  ];

  const departmentHeads = [
    {
      department: 'CBC Program',
      head: 'Mrs. Grace Wambui',
      focus: 'Kenyan Competency-Based Curriculum Implementation'
    },
    {
      department: 'Cambridge Program',
      head: 'Mr. James Ochieng',
      focus: 'International Curriculum Excellence'
    },
    {
      department: 'Elementary School',
      head: 'Ms. Linda Chebet',
      focus: 'Early Years Foundation & Development'
    },
    {
      department: 'Middle School',
      head: 'Mr. Peter Njoroge',
      focus: 'Transition & Skill Building'
    },
    {
      department: 'High School',
      head: 'Dr. David Kimani',
      focus: 'University Preparation & Specialization'
    },
    {
      department: 'Special Needs Education',
      head: 'Mrs. Susan Akinyi',
      focus: 'Inclusive Education Support'
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
              <li className="breadcrumb-item active">Leadership Team</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Leadership Team</h1>
            <p className="lead mb-0">Guiding Delvok Academy Towards Educational Excellence</p>
          </div>
        </div>
      </div>

      {/* Senior Leadership Team */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Senior Leadership Team</h3>
          <div className="row g-4">
            {leadershipTeam.map((leader, index) => (
              <div key={index} className="col-lg-6">
                <div className="card h-100 leadership-card">
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-4">
                        <div className="leader-image-placeholder bg-light rounded-circle d-flex align-items-center justify-content-center mb-3"
                             style={{width: '120px', height: '120px'}}>
                          <i className="bi bi-person display-3 text-muted"></i>
                        </div>
                      </div>
                      <div className="col-md-8">
                        <h4 className="card-title">{leader.name}</h4>
                        <p className="card-text text-primary fs-5">{leader.position}</p>
                        <p className="card-text small">{leader.bio}</p>
                        
                        <div className="leader-contact mb-3">
                          <div className="small">
                            <i className="bi bi-envelope me-2"></i>
                            {leader.email}
                          </div>
                          <div className="small">
                            <i className="bi bi-telephone me-2"></i>
                            {leader.phone}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="leader-details mt-4">
                      <h6 className="text-primary">Key Responsibilities:</h6>
                      <ul className="small">
                        {leader.responsibilities.map((resp, idx) => (
                          <li key={idx}>{resp}</li>
                        ))}
                      </ul>
                      
                      <div className="row mt-3">
                        <div className="col-md-6">
                          <strong>Qualifications:</strong>
                          <ul className="small">
                            {leader.qualifications.map((qual, idx) => (
                              <li key={idx}>{qual}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="col-md-6">
                          <strong>Experience:</strong>
                          <div className="small">{leader.experience}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Department Heads */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Academic Department Heads</h3>
          <div className="row g-3">
            {departmentHeads.map((dept, index) => (
              <div key={index} className="col-md-6 col-lg-4">
                <div className="card h-100 text-center">
                  <div className="card-body">
                    <h5 className="card-title text-primary">{dept.department}</h5>
                    <p className="card-text fw-bold">{dept.head}</p>
                    <p className="card-text small">{dept.focus}</p>
                    <button className="btn btn-outline-primary btn-sm">
                      Contact Department
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Board of Directors */}
      <div className="row">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-body">
              <h3 className="text-center mb-4">Board of Directors</h3>
              <div className="row justify-content-center">
                {boardMembers.map((member, index) => (
                  <div key={index} className="col-md-6 col-lg-3 mb-4">
                    <div className="card h-100 text-center">
                      <div className="card-body">
                        <h5 className="card-title">{member.name}</h5>
                        <p className="card-text text-primary">{member.role}</p>
                        <p className="card-text small">{member.affiliation}</p>
                        <div className="badge bg-secondary">{member.expertise}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="text-center mt-4">
                <p className="text-muted">
                  The Board of Directors provides strategic oversight and governance, 
                  ensuring Delvok Academy remains true to its mission and vision.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Leadership Philosophy */}
      <div className="row mt-5">
        <div className="col-lg-8 mx-auto">
          <div className="card border-primary">
            <div className="card-header bg-primary text-white">
              <h4 className="mb-0">Our Leadership Philosophy</h4>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <h5 className="text-primary">Servant Leadership</h5>
                  <p>
                    We believe in leading by serving - putting the needs of students, teachers, 
                    and the community first in all our decisions and actions.
                  </p>
                </div>
                <div className="col-md-6">
                  <h5 className="text-primary">Collaborative Decision-Making</h5>
                  <p>
                    Important decisions are made through consultation with stakeholders, 
                    ensuring diverse perspectives are considered and valued.
                  </p>
                </div>
              </div>
              <div className="row mt-4">
                <div className="col-md-6">
                  <h5 className="text-primary">Innovation & Adaptability</h5>
                  <p>
                    We embrace change and continuously seek innovative approaches to education 
                    while maintaining our core values and academic standards.
                  </p>
                </div>
                <div className="col-md-6">
                  <h5 className="text-primary">Transparency & Accountability</h5>
                  <p>
                    We maintain open communication with our community and take responsibility 
                    for our actions and decisions.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Leadership;