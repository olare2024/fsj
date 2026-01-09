import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {teacherAPI} from '../services/teacherAPI.js';

function Teachers() {
  const [teachers, setTeachers] = useState([]);
  const [filteredTeachers, setFilteredTeachers] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedTeacher, setExpandedTeacher] = useState(null);

  const departments = [
    { value: 'all', label: 'All Departments', color: 'secondary' },
    { value: 'Mathematics', label: 'Mathematics', color: 'primary' },
    { value: 'Sciences', label: 'Sciences', color: 'success' },
    { value: 'Languages', label: 'Languages', color: 'info' },
    { value: 'Humanities', label: 'Humanities', color: 'warning' },
    { value: 'Technical', label: 'Technical', color: 'danger' },
    { value: 'Arts', label: 'Arts & Sports', color: 'purple' },
    { value: 'Administration', label: 'Administration', color: 'dark' }
  ];

  const subjects = [
    'Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'Kiswahili',
    'History', 'Geography', 'CRE', 'IRE', 'HRE', 'Business', 'Computer',
    'Music', 'Art', 'PE', 'French', 'German', 'Agriculture', 'Home Science'
  ];

  useEffect(() => {
    fetchTeachers();
  }, []);

  useEffect(() => {
    filterTeachers();
  }, [selectedDepartment, searchTerm, teachers]);

  const fetchTeachers = async () => {
    try {
      setLoading(true);
      setError(null);
      // Mock data - replace with actual API call
      const mockTeachers = [
        {
          id: 1,
          name: 'Dr. Sarah Johnson',
          title: 'PhD',
          department: 'Sciences',
          subjects: ['Physics', 'Chemistry'],
          email: 's.johnson@school.edu',
          phone: '+254-712-345-678',
          office: 'Science Block, Room 101',
          bio: 'Dr. Johnson has 15 years of teaching experience with a specialization in experimental physics. She has published several research papers in international journals.',
          image: '/images/teachers/sarah-johnson.jpg',
          joinDate: '2015-08-15',
          qualifications: ['PhD Physics', 'MSc Education', 'BEd Science'],
          isHead: true
        },
        {
          id: 2,
          name: 'Mr. David Kimani',
          title: 'MSc',
          department: 'Mathematics',
          subjects: ['Mathematics', 'Additional Mathematics'],
          email: 'd.kimani@school.edu',
          phone: '+254-723-456-789',
          office: 'Math Wing, Room 205',
          bio: 'Mr. Kimani specializes in making complex mathematical concepts accessible to students. He has been instrumental in improving math performance across all grades.',
          image: '/images/teachers/david-kimani.jpg',
          joinDate: '2018-01-10',
          qualifications: ['MSc Mathematics', 'BEd Mathematics'],
          isHead: false
        },
        {
          id: 3,
          name: 'Ms. Grace Wambui',
          title: 'MA',
          department: 'Languages',
          subjects: ['English', 'Literature'],
          email: 'g.wambui@school.edu',
          phone: '+254-734-567-890',
          office: 'Language Lab, Room 304',
          bio: 'Ms. Wambui is passionate about literature and creative writing. She runs the school\'s creative writing club and has mentored several award-winning young writers.',
          image: '/images/teachers/grace-wambui.jpg',
          joinDate: '2019-03-22',
          qualifications: ['MA Literature', 'BA Education'],
          isHead: true
        },
        {
          id: 4,
          name: 'Mr. Robert Ochieng',
          title: 'BSc',
          department: 'Technical',
          subjects: ['Computer Studies', 'Business Studies'],
          email: 'r.ochieng@school.edu',
          phone: '+254-745-678-901',
          office: 'Computer Lab, Room 401',
          bio: 'Mr. Ochieng brings industry experience to the classroom, having worked in tech before transitioning to teaching. He focuses on practical programming skills.',
          image: '/images/teachers/robert-ochieng.jpg',
          joinDate: '2020-09-05',
          qualifications: ['BSc Computer Science', 'PGDE'],
          isHead: false
        },
        {
          id: 5,
          name: 'Mrs. Amina Hassan',
          title: 'MEd',
          department: 'Humanities',
          subjects: ['History', 'Geography'],
          email: 'a.hassan@school.edu',
          phone: '+254-756-789-012',
          office: 'Humanities Block, Room 502',
          bio: 'Mrs. Hassan creates engaging historical narratives that help students connect with the past. She organizes annual educational trips to historical sites.',
          image: '/images/teachers/amina-hassan.jpg',
          joinDate: '2017-11-30',
          qualifications: ['MEd History', 'BA Education'],
          isHead: false
        },
        {
          id: 6,
          name: 'Coach James Mwangi',
          title: 'BEd',
          department: 'Arts',
          subjects: ['Physical Education', 'Games'],
          email: 'j.mwangi@school.edu',
          phone: '+254-767-890-123',
          office: 'Sports Office, Gym Building',
          bio: 'Coach Mwangi has trained several national-level athletes. He believes in sports as a tool for character building and holistic development.',
          image: '/images/teachers/james-mwangi.jpg',
          joinDate: '2016-05-15',
          qualifications: ['BEd Physical Education', 'Sports Science Diploma'],
          isHead: true
        }
      ];
      setTeachers(mockTeachers);
      // Actual API call:
      // const response = await teachersAPI.getAll();
      // setTeachers(response.data);
    } catch (error) {
      console.error('Error fetching teachers:', error);
      setError('Failed to load teachers data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const filterTeachers = () => {
    let filtered = teachers;

    // Filter by department
    if (selectedDepartment !== 'all') {
      filtered = filtered.filter(teacher => 
        teacher.department === selectedDepartment
      );
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(teacher =>
        teacher.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        teacher.subjects.some(subject => 
          subject.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        teacher.department.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredTeachers(filtered);
  };

  const getDepartmentColor = (department) => {
    const dept = departments.find(d => d.value === department);
    return dept ? dept.color : 'secondary';
  };

  const toggleTeacherDetails = (teacherId, e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    setExpandedTeacher(expandedTeacher === teacherId ? null : teacherId);
  };

  const getYearsOfService = (joinDate) => {
    const joinYear = new Date(joinDate).getFullYear();
    const currentYear = new Date().getFullYear();
    return currentYear - joinYear;
  };

  const TeacherCard = ({ teacher }) => (
    <Link 
      to={`/teachers/${teacher.id}`} 
      className="text-decoration-none"
      state={{ from: 'teachers-list' }}
    >
      <div className="card teacher-card h-100 shadow-sm hover-card">
        <div className="card-body">
          <div className="text-center mb-3">
            <div className="teacher-avatar mx-auto mb-2">
              {teacher.image ? (
                <img 
                  src={teacher.image} 
                  alt={teacher.name}
                  className="avatar-img"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div className="avatar-placeholder">
                {teacher.name.split(' ').map(n => n[0]).join('')}
              </div>
            </div>
            <h6 className="card-title mb-1 text-dark">{teacher.name}</h6>
            <small className="text-muted">{teacher.title}</small>
            {teacher.isHead && (
              <span className="badge bg-warning text-dark ms-2">Head</span>
            )}
          </div>

          <div className="mb-3">
            <span className={`badge bg-${getDepartmentColor(teacher.department)} w-100`}>
              {teacher.department}
            </span>
          </div>

          <div className="mb-3">
            <strong className="text-dark">Subjects:</strong>
            <div className="mt-1">
              {teacher.subjects.map(subject => (
                <span 
                  key={subject} 
                  className="badge bg-light text-dark border me-1 mb-1"
                >
                  {subject}
                </span>
              ))}
            </div>
          </div>

          <div className="mb-3">
            <small className="text-dark">
              <i className="bi bi-envelope me-1"></i>
              {teacher.email}
            </small>
            <br />
            <small className="text-dark">
              <i className="bi bi-telephone me-1"></i>
              {teacher.phone}
            </small>
          </div>

          {teacher.bio && (
            <p className="card-text small text-muted">
              {expandedTeacher === teacher.id 
                ? teacher.bio
                : `${teacher.bio.substring(0, 80)}...`
              }
            </p>
          )}

          <div className="d-flex justify-content-between align-items-center mt-auto">
            <small className="text-primary">
              {getYearsOfService(teacher.joinDate)} years service
            </small>
            {teacher.bio && teacher.bio.length > 80 && (
              <button 
                className="btn btn-sm btn-outline-primary"
                onClick={(e) => toggleTeacherDetails(teacher.id, e)}
              >
                {expandedTeacher === teacher.id ? 'Less' : 'More'}
              </button>
            )}
          </div>
        </div>
      </div>
    </Link>
  );

  const StatisticsCard = () => (
    <div className="row mb-4">
      <div className="col-md-3">
        <div className="card bg-primary text-white text-center">
          <div className="card-body">
            <h4>{teachers.length}</h4>
            <p className="mb-0">Total Teachers</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card bg-success text-white text-center">
          <div className="card-body">
            <h4>{departments.length - 1}</h4>
            <p className="mb-0">Departments</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card bg-warning text-dark text-center">
          <div className="card-body">
            <h4>{teachers.filter(t => t.isHead).length}</h4>
            <p className="mb-0">Department Heads</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card bg-info text-white text-center">
          <div className="card-body">
            <h4>{new Set(teachers.flatMap(t => t.subjects)).size}</h4>
            <p className="mb-0">Subjects Covered</p>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
          <div className="text-center">
            <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
              <span className="visually-hidden">Loading teachers...</span>
            </div>
            <p className="mt-3 text-muted">Loading our teaching staff...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger d-flex align-items-center" role="alert">
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          <div>{error}</div>
          <button className="btn btn-sm btn-outline-danger ms-auto" onClick={fetchTeachers}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      {/* Header Section */}
      <div className="row mb-4">
        <div className="col-md-8">
          <h1 className="display-5 fw-bold text-primary">Our Teachers</h1>
          <p className="lead text-muted">
            Meet our dedicated and experienced teaching staff committed to student success
          </p>
        </div>
        <div className="col-md-4 text-end">
          <button className="btn btn-outline-primary" onClick={fetchTeachers}>
            <i className="bi bi-arrow-clockwise me-2"></i>
            Refresh
          </button>
        </div>
      </div>

      {/* Statistics */}
      <StatisticsCard />

      {/* Filters Section */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-6">
              <label className="form-label">Search Teachers</label>
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by name, subject, or department..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-6">
              <label className="form-label">Filter by Department</label>
              <select 
                className="form-select" 
                value={selectedDepartment} 
                onChange={(e) => setSelectedDepartment(e.target.value)}
              >
                {departments.map(dept => (
                  <option key={dept.value} value={dept.value}>
                    {dept.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Active Filters */}
          <div className="mt-3">
            {(selectedDepartment !== 'all' || searchTerm) && (
              <div className="d-flex align-items-center">
                <small className="text-muted me-2">Active filters:</small>
                {selectedDepartment !== 'all' && (
                  <span className={`badge bg-${getDepartmentColor(selectedDepartment)} me-2`}>
                    {departments.find(d => d.value === selectedDepartment)?.label}
                    <button 
                      className="btn-close btn-close-white ms-1" 
                      style={{ fontSize: '0.6rem' }}
                      onClick={() => setSelectedDepartment('all')}
                    ></button>
                  </span>
                )}
                {searchTerm && (
                  <span className="badge bg-info me-2">
                    Search: {searchTerm}
                    <button 
                      className="btn-close btn-close-white ms-1" 
                      style={{ fontSize: '0.6rem' }}
                      onClick={() => setSearchTerm('')}
                    ></button>
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5>
          Showing {filteredTeachers.length} of {teachers.length} teachers
        </h5>
        {filteredTeachers.length === 0 && !loading && (
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={() => {
              setSelectedDepartment('all');
              setSearchTerm('');
            }}
          >
            Clear all filters
          </button>
        )}
      </div>

      {/* Teachers Grid */}
      {filteredTeachers.length > 0 ? (
        <div className="row g-4">
          {filteredTeachers.map(teacher => (
            <div key={teacher.id} className="col-xl-4 col-lg-6 col-md-6">
              <TeacherCard teacher={teacher} />
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-5">
          <i className="bi bi-person-x" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
          <h4 className="mt-3 text-muted">No teachers found</h4>
          <p className="text-muted">
            Try adjusting your filters or search terms to see more results.
          </p>
          <button 
            className="btn btn-primary"
            onClick={() => {
              setSelectedDepartment('all');
              setSearchTerm('');
            }}
          >
            Clear all filters
          </button>
        </div>
      )}

      {/* Teaching Philosophy Section */}
      <div className="card mt-5">
        <div className="card-header bg-gradient-primary text-white">
          <h5 className="mb-0">
            <i className="bi bi-mortarboard me-2"></i>
            Our Teaching Philosophy
          </h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-8">
              <p className="lead">
                At Delvok Academy, our teachers are more than educators - they are mentors, 
                guides, and inspirations to our students.
              </p>
              <div className="row">
                <div className="col-md-6">
                  <h6>Our Commitment:</h6>
                  <ul className="list-unstyled">
                    <li><i className="bi bi-check-circle text-success me-2"></i>Student-centered learning approaches</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Continuous professional development</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Innovative teaching methodologies</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Individualized attention and support</li>
                  </ul>
                </div>
                <div className="col-md-6">
                  <h6>Teacher Development:</h6>
                  <ul className="list-unstyled">
                    <li><i className="bi bi-check-circle text-success me-2"></i>Regular training workshops</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Collaborative lesson planning</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Peer observation and feedback</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Research and publication support</li>
                  </ul>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card bg-light">
                <div className="card-body text-center">
                  <i className="bi bi-award display-4 text-primary mb-3"></i>
                  <h6>Teacher Qualifications</h6>
                  <div className="small">
                    <strong>100%</strong> Certified Teachers<br/>
                    <strong>85%</strong> Postgraduate Degrees<br/>
                    <strong>12+</strong> Years Average Experience<br/>
                    <strong>98%</strong> Student Satisfaction
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .hover-card {
          transition: all 0.3s ease;
        }
        .hover-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
          border-color: var(--bs-primary);
        }
        .teacher-avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          position: relative;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .avatar-img {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          object-fit: cover;
        }
        .avatar-placeholder {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          font-weight: bold;
          font-size: 1.5rem;
        }
        .badge.bg-purple {
          background-color: #6f42c1 !important;
        }
      `}</style>
    </div>
  );
}

export default Teachers;