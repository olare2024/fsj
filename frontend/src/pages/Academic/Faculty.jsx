import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Faculty() {
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const facultyMembers = [
    {
      id: 1,
      name: 'Dr. Sarah Mwangi',
      position: 'Head of School',
      department: 'Administration',
      qualifications: ['PhD Educational Leadership', 'MEd Curriculum Development', 'BEd Arts'],
      experience: '15 years',
      specialization: 'Educational Leadership, CBC Implementation',
      email: 's.mwangi@delvok.ac.ke',
      phone: 'Ext. 101',
      image: '/images/faculty/sarah-mwangi.jpg',
      bio: 'Dr. Mwangi has been instrumental in developing Delvok Academy\'s dual curriculum model and expanding international partnerships.',
      achievements: [
        'Pioneered dual curriculum integration',
        'Established university pathway programs',
        'Led school accreditation processes'
      ]
    },
    {
      id: 2,
      name: 'Mr. James Ochieng',
      position: 'Head of Cambridge Program',
      department: 'Cambridge Program',
      qualifications: ['MSc Mathematics', 'PGCE International Education', 'BEd Science'],
      experience: '12 years',
      specialization: 'IGCSE Mathematics, Further Mathematics',
      email: 'j.ochieng@delvok.ac.ke',
      phone: 'Ext. 205',
      image: '/images/faculty/james-ochieng.jpg',
      bio: 'Mr. Ochieng brings extensive experience in international education and has trained teachers across East Africa.',
      achievements: [
        'Cambridge Teacher Trainer',
        'Mathematics Olympiad Coach',
        'Published educational materials'
      ]
    },
    {
      id: 3,
      name: 'Mrs. Amina Hassan',
      position: 'CBC Coordinator',
      department: 'CBC Specialists',
      qualifications: ['MEd Early Childhood', 'BEd Primary Education', 'CBC Trainer Certificate'],
      experience: '10 years',
      specialization: 'Lower Primary, Literacy Development',
      email: 'a.hassan@delvok.ac.ke',
      phone: 'Ext. 156',
      image: '/images/faculty/amina-hassan.jpg',
      bio: 'Mrs. Hassan is a certified CBC trainer who has developed innovative approaches to competency-based assessment.',
      achievements: [
        'CBC Master Trainer',
        'Literacy Program Developer',
        'Early Childhood Education Specialist'
      ]
    },
    {
      id: 4,
      name: 'Prof. David Kimani',
      position: 'Science Department Head',
      department: 'Sciences',
      qualifications: ['PhD Chemistry', 'MSc Biochemistry', 'BEd Science'],
      experience: '18 years',
      specialization: 'IGCSE Chemistry, AP Chemistry, Research Methods',
      email: 'd.kimani@delvok.ac.ke',
      phone: 'Ext. 312',
      image: '/images/faculty/david-kimani.jpg',
      bio: 'Professor Kimani maintains an active research program while mentoring young scientists and developing curriculum.',
      achievements: [
        'Published research papers',
        'Science Fair Coordinator',
        'University Research Collaborator'
      ]
    },
    {
      id: 5,
      name: 'Ms. Grace Wambui',
      position: 'Elementary School Lead',
      department: 'Elementary School',
      qualifications: ['MEd Child Psychology', 'BEd Early Childhood', 'Montessori Certified'],
      experience: '8 years',
      specialization: 'Play-based Learning, Social-Emotional Development',
      email: 'g.wambui@delvok.ac.ke',
      phone: 'Ext. 102',
      image: '/images/faculty/grace-wambui.jpg',
      bio: 'Ms. Wambui specializes in early childhood development and has implemented innovative play-based learning strategies.',
      achievements: [
        'Montessori Certification',
        'Child Development Workshops',
        'Parent Education Programs'
      ]
    },
    {
      id: 6,
      name: 'Mr. Robert Mutiso',
      position: 'Mathematics Specialist',
      department: 'Mathematics',
      qualifications: ['MEd Mathematics', 'BEd Mathematics', 'Cambridge Mathematics Certified'],
      experience: '11 years',
      specialization: 'Cambridge Checkpoint, Problem Solving Strategies',
      email: 'r.mutiso@delvok.ac.ke',
      phone: 'Ext. 228',
      image: '/images/faculty/robert-mutiso.jpg',
      bio: 'Mr. Mutiso has developed unique problem-solving approaches that help students excel in mathematics competitions.',
      achievements: [
        'Math Olympiad Coach',
        'Curriculum Developer',
        'Teacher Training Facilitator'
      ]
    }
  ];

  const departments = [
    { id: 'all', name: 'All Faculty', count: facultyMembers.length },
    { id: 'administration', name: 'Administration', count: 1 },
    { id: 'cambridge', name: 'Cambridge Program', count: 1 },
    { id: 'cbc', name: 'CBC Specialists', count: 1 },
    { id: 'sciences', name: 'Sciences', count: 1 },
    { id: 'elementary', name: 'Elementary School', count: 1 },
    { id: 'mathematics', name: 'Mathematics', count: 1 }
  ];

  const filteredFaculty = facultyMembers.filter(member => {
    const matchesDepartment = activeFilter === 'all' || 
      member.department.toLowerCase().includes(activeFilter);
    const matchesSearch = member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.specialization.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesDepartment && matchesSearch;
  });

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/academics">Academics</Link></li>
              <li className="breadcrumb-item active">Faculty</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Our Faculty</h1>
            <p className="lead mb-0">Dedicated Educators Committed to Student Success</p>
            <div className="mt-3">
              <span className="badge bg-primary fs-6">Highly Qualified & Experienced</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <div className="row">
                <div className="col-md-8">
                  <div className="input-group">
                    <span className="input-group-text">
                      <i className="bi bi-search"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search faculty by name, position, or specialization..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="col-md-4 mt-3 mt-md-0">
                  <select 
                    className="form-select"
                    value={activeFilter}
                    onChange={(e) => setActiveFilter(e.target.value)}
                  >
                    {departments.map(dept => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name} ({dept.count})
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Faculty Grid */}
      <div className="row g-4">
        {filteredFaculty.map(member => (
          <div key={member.id} className="col-lg-6">
            <div className="card h-100 faculty-card">
              <div className="card-body">
                <div className="row">
                  <div className="col-md-4">
                    <div className="faculty-image-placeholder bg-light rounded-circle d-flex align-items-center justify-content-center mb-3"
                         style={{width: '120px', height: '120px'}}>
                      <i className="bi bi-person display-3 text-muted"></i>
                    </div>
                  </div>
                  <div className="col-md-8">
                    <h4 className="card-title">{member.name}</h4>
                    <p className="card-text text-primary fs-5">{member.position}</p>
                    <span className="badge bg-secondary mb-3">{member.department}</span>
                    
                    <p className="card-text small">{member.bio}</p>
                    
                    <div className="faculty-contact mb-3">
                      <div className="small">
                        <i className="bi bi-envelope me-2"></i>
                        {member.email}
                      </div>
                      <div className="small">
                        <i className="bi bi-telephone me-2"></i>
                        {member.phone}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="row mt-3">
                  <div className="col-md-6">
                    <h6>Qualifications:</h6>
                    <ul className="small">
                      {member.qualifications.map((qual, idx) => (
                        <li key={idx}>{qual}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="col-md-6">
                    <h6>Specialization:</h6>
                    <p className="small">{member.specialization}</p>
                    
                    <h6>Experience:</h6>
                    <p className="small">{member.experience}</p>
                  </div>
                </div>

                <div className="mt-3">
                  <h6>Key Achievements:</h6>
                  <ul className="small">
                    {member.achievements.map((achievement, idx) => (
                      <li key={idx}>
                        <i className="bi bi-award text-warning me-2"></i>
                        {achievement}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="card-footer bg-transparent">
                <button className="btn btn-outline-primary btn-sm me-2">
                  View Profile
                </button>
                <button className="btn btn-primary btn-sm">
                  Schedule Meeting
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Faculty Statistics */}
      <div className="row mt-5">
        <div className="col-12">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <h4 className="text-center mb-4">Faculty Excellence at Delvok Academy</h4>
              <div className="row text-center">
                <div className="col-md-3 mb-3">
                  <div className="display-4 fw-bold">95%</div>
                  <div>Hold Advanced Degrees</div>
                </div>
                <div className="col-md-3 mb-3">
                  <div className="display-4 fw-bold">12+</div>
                  <div>Years Average Experience</div>
                </div>
                <div className="col-md-3 mb-3">
                  <div className="display-4 fw-bold">100%</div>
                  <div>Cambridge Certified</div>
                </div>
                <div className="col-md-3 mb-3">
                  <div className="display-4 fw-bold">25+</div>
                  <div>Nationalities Represented</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Professional Development */}
      <div className="row mt-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Faculty Development Programs</h3>
          <div className="row g-4">
            <div className="col-md-4">
              <div className="card text-center h-100">
                <div className="card-body">
                  <i className="bi bi-journal-bookmark display-4 text-success mb-3"></i>
                  <h5>Continuous Training</h5>
                  <p className="card-text">
                    Regular workshops on both CBC and Cambridge curriculum updates and teaching methodologies.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card text-center h-100">
                <div className="card-body">
                  <i className="bi bi-globe display-4 text-success mb-3"></i>
                  <h5>International Conferences</h5>
                  <p className="card-text">
                    Opportunities to attend and present at international educational conferences worldwide.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card text-center h-100">
                <div className="card-body">
                  <i className="bi bi-graph-up display-4 text-success mb-3"></i>
                  <h5>Research Opportunities</h5>
                  <p className="card-text">
                    Support for faculty research projects and educational innovation initiatives.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Join Our Team */}
      <div className="row mt-5">
        <div className="col-12 text-center">
          <div className="card bg-light">
            <div className="card-body py-5">
              <h3 className="mb-3">Interested in Joining Our Faculty?</h3>
              <p className="fs-5 mb-4">
                We're always looking for passionate educators to join our team.
              </p>
              <div className="row justify-content-center">
                <div className="col-md-6">
                  <div className="mb-3">
                    <i className="bi bi-envelope text-primary me-2"></i>
                    careers@delvok.ac.ke
                  </div>
                  <div className="mb-3">
                    <i className="bi bi-telephone text-primary me-2"></i>
                    +254 720 123 456
                  </div>
                </div>
              </div>
              <Link to="/careers" className="btn btn-primary btn-lg mt-3">
                View Current Openings
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Faculty;