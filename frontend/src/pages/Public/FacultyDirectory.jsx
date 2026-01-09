import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function FacultyDirectory() {
  const [activeDepartment, setActiveDepartment] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const departments = [
    { id: 'all', name: 'All Faculty', count: 48 },
    { id: 'elementary', name: 'Elementary School', count: 12 },
    { id: 'middle', name: 'Middle School', count: 15 },
    { id: 'high', name: 'High School', count: 21 },
    { id: 'cbc', name: 'CBC Specialists', count: 8 },
    { id: 'cambridge', name: 'Cambridge Program', count: 10 },
    { id: 'special', name: 'Special Education', count: 6 }
  ];

  const facultyMembers = [
    {
      id: 1,
      name: 'Dr. Sarah Mwangi',
      position: 'Head of School',
      department: 'Administration',
      qualifications: ['PhD Education Leadership', 'MEd Curriculum Development', 'BEd Arts'],
      experience: '15 years',
      specialization: 'Educational Leadership, CBC Implementation',
      email: 's.mwangi@delvok.ac.ke',
      phone: 'Ext. 101',
      image: '/images/faculty/sarah-mwangi.jpg'
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
      image: '/images/faculty/james-ochieng.jpg'
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
      image: '/images/faculty/amina-hassan.jpg'
    },
    {
      id: 4,
      name: 'Prof. David Kimani',
      position: 'Science Department Head',
      department: 'High School',
      qualifications: ['PhD Chemistry', 'MSc Biochemistry', 'BEd Science'],
      experience: '18 years',
      specialization: 'IGCSE Chemistry, AP Chemistry, Research Methods',
      email: 'd.kimani@delvok.ac.ke',
      phone: 'Ext. 312',
      image: '/images/faculty/david-kimani.jpg'
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
      image: '/images/faculty/grace-wambui.jpg'
    },
    {
      id: 6,
      name: 'Mr. Robert Mutiso',
      position: 'Mathematics Specialist',
      department: 'Middle School',
      qualifications: ['MEd Mathematics', 'BEd Mathematics', 'Cambridge Mathematics Certified'],
      experience: '11 years',
      specialization: 'Cambridge Checkpoint, Problem Solving Strategies',
      email: 'r.mutiso@delvok.ac.ke',
      phone: 'Ext. 228',
      image: '/images/faculty/robert-mutiso.jpg'
    }
  ];

  const filteredFaculty = facultyMembers.filter(member => {
    const matchesDepartment = activeDepartment === 'all' || member.department.toLowerCase().includes(activeDepartment);
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
              <li className="breadcrumb-item"><Link to="/about">About</Link></li>
              <li className="breadcrumb-item active">Faculty Directory</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">Faculty Directory</h1>
              <p className="lead mb-0">Meet Our Dedicated Team of Educators</p>
            </div>
            <div className="badge bg-primary fs-6">
              {facultyMembers.length} Faculty Members
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter Section */}
      <div className="card mb-4">
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
                value={activeDepartment}
                onChange={(e) => setActiveDepartment(e.target.value)}
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

      {/* Department Filter Buttons */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex flex-wrap gap-2">
            {departments.map(dept => (
              <button
                key={dept.id}
                className={`btn ${activeDepartment === dept.id ? 'btn-primary' : 'btn-outline-primary'} btn-sm`}
                onClick={() => setActiveDepartment(dept.id)}
              >
                {dept.name} <span className="badge bg-light text-dark ms-1">{dept.count}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Faculty Grid */}
      <div className="row g-4">
        {filteredFaculty.length === 0 ? (
          <div className="col-12 text-center py-5">
            <i className="bi bi-search display-1 text-muted"></i>
            <h4 className="mt-3">No faculty members found</h4>
            <p className="text-muted">
              Try adjusting your search criteria or browse all departments.
            </p>
            <button 
              className="btn btn-primary"
              onClick={() => {
                setSearchTerm('');
                setActiveDepartment('all');
              }}
            >
              Show All Faculty
            </button>
          </div>
        ) : (
          filteredFaculty.map(member => (
            <div key={member.id} className="col-md-6 col-lg-4">
              <div className="card h-100 faculty-card">
                <div className="card-body">
                  <div className="row align-items-start mb-3">
                    <div className="col-4">
                      <div className="faculty-image-placeholder bg-light rounded-circle d-flex align-items-center justify-content-center"
                           style={{width: '80px', height: '80px'}}>
                        <i className="bi bi-person display-6 text-muted"></i>
                      </div>
                    </div>
                    <div className="col-8">
                      <h5 className="card-title mb-1">{member.name}</h5>
                      <p className="card-text text-primary mb-1">{member.position}</p>
                      <span className="badge bg-secondary">{member.department}</span>
                    </div>
                  </div>
                  
                  <div className="faculty-details">
                    <p className="card-text small mb-2">
                      <strong>Specialization:</strong> {member.specialization}
                    </p>
                    <p className="card-text small mb-2">
                      <strong>Experience:</strong> {member.experience}
                    </p>
                    <div className="mb-2">
                      <strong className="small">Qualifications:</strong>
                      <ul className="small mb-0 ps-3">
                        {member.qualifications.map((qual, idx) => (
                          <li key={idx}>{qual}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="card-footer bg-transparent">
                  <div className="row">
                    <div className="col-6">
                      <small className="text-muted">
                        <i className="bi bi-envelope me-1"></i>
                        {member.email}
                      </small>
                    </div>
                    <div className="col-6 text-end">
                      <small className="text-muted">
                        <i className="bi bi-telephone me-1"></i>
                        {member.phone}
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Faculty Statistics */}
      <div className="row mt-5">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-body">
              <h5 className="card-title mb-4">Faculty Excellence at Delvok Academy</h5>
              <div className="row text-center">
                <div className="col-md-3 mb-3">
                  <div className="display-6 fw-bold text-primary">95%</div>
                  <div className="small">Hold Advanced Degrees</div>
                </div>
                <div className="col-md-3 mb-3">
                  <div className="display-6 fw-bold text-primary">12+</div>
                  <div className="small">Years Average Experience</div>
                </div>
                <div className="col-md-3 mb-3">
                  <div className="display-6 fw-bold text-primary">100%</div>
                  <div className="small">Cambridge Certified Teachers</div>
                </div>
                <div className="col-md-3 mb-3">
                  <div className="display-6 fw-bold text-primary">25+</div>
                  <div className="small">Nationalities Represented</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FacultyDirectory;