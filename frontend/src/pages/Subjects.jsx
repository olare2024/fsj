import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { subjectsAPI } from '../services/subjectsAPI.js';

function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [filteredSubjects, setFilteredSubjects] = useState([]);
  const [selectedGrade, setSelectedGrade] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSubject, setExpandedSubject] = useState(null);

  const gradeLevels = {
    'Lower Primary (1-3)': ['1', '2', '3'],
    'Upper Primary (4-6)': ['4', '5', '6'],
    'Junior Secondary (7-9)': ['7', '8', '9'],
    'Senior Secondary (10-12)': ['10', '11', '12']
  };

  const categories = [
    { value: 'all', label: 'All Categories', color: 'secondary' },
    { value: 'Core', label: 'Core Subjects', color: 'primary' },
    { value: 'Elective', label: 'Elective Subjects', color: 'success' },
    { value: 'Technical', label: 'Technical', color: 'warning' },
    { value: 'Languages', label: 'Languages', color: 'info' },
    { value: 'Arts', label: 'Arts & Sports', color: 'danger' }
  ];

  useEffect(() => {
    fetchSubjects();
  }, []);

  useEffect(() => {
    filterSubjects();
  }, [selectedGrade, selectedCategory, searchTerm, subjects]);

  const fetchSubjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await subjectsAPI.getAll();
      setSubjects(response.data);
    } catch (error) {
      console.error('Error fetching subjects:', error);
      setError('Failed to load subjects data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const filterSubjects = () => {
    let filtered = subjects;

    // Filter by grade
    if (selectedGrade !== 'all') {
      filtered = filtered.filter(subject => 
        subject.grades.includes(selectedGrade)
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(subject => 
        subject.category === selectedCategory
      );
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(subject =>
        subject.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        subject.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        subject.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredSubjects(filtered);
  };

  const getSubjectsByCategory = (category) => {
    return filteredSubjects.filter(subject => subject.category === category);
  };

  const getCategoryColor = (category) => {
    const cat = categories.find(c => c.value === category);
    return cat ? cat.color : 'secondary';
  };

  const toggleSubjectDetails = (subjectId, e) => {
    e.preventDefault();
    e.stopPropagation();
    setExpandedSubject(expandedSubject === subjectId ? null : subjectId);
  };

  const getGradeBadgeVariant = (grade) => {
    const variants = ['primary', 'success', 'warning', 'info', 'danger', 'dark'];
    return variants[parseInt(grade) % variants.length];
  };

  const SubjectCard = ({ subject }) => (
    <Link 
      to={`/subjects/${subject.id}`} 
      className="text-decoration-none"
      state={{ from: 'subjects-list' }}
    >
      <div className="card subject-card h-100 shadow-sm hover-card">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start mb-2">
            <h6 className="card-title mb-0 text-dark">{subject.name}</h6>
            <span className={`badge bg-${getCategoryColor(subject.category)}`}>
              {subject.category}
            </span>
          </div>
          
          <div className="mb-2">
            <small className="text-muted">Code: {subject.code}</small>
          </div>

          <div className="mb-3">
            <strong className="text-dark">Grades:</strong>
            <div className="mt-1">
              {subject.grades.map(grade => (
                <span 
                  key={grade} 
                  className={`badge bg-${getGradeBadgeVariant(grade)} me-1 mb-1`}
                >
                  Grade {grade}
                </span>
              ))}
            </div>
          </div>

          {subject.description && (
            <p className="card-text small text-muted">
              {expandedSubject === subject.id 
                ? subject.description
                : `${subject.description.substring(0, 100)}...`
              }
            </p>
          )}

          {subject.teacher && (
            <div className="mb-2">
              <small className="text-dark">
                <strong>Teacher:</strong> {subject.teacher}
              </small>
            </div>
          )}

          {subject.credits && (
            <div className="mb-3">
              <small className="text-dark">
                <strong>Credits:</strong> {subject.credits}
              </small>
            </div>
          )}

          <div className="d-flex justify-content-between align-items-center">
            {subject.description && subject.description.length > 100 && (
              <button 
                className="btn btn-sm btn-outline-primary"
                onClick={(e) => toggleSubjectDetails(subject.id, e)}
              >
                {expandedSubject === subject.id ? 'Show Less' : 'Read More'}
              </button>
            )}
            <span className="text-primary small fw-bold">
              View Details <i className="bi bi-arrow-right ms-1"></i>
            </span>
          </div>
        </div>
      </div>
    </Link>
  );

  // Alternative Subject Row for list view (optional)
  const SubjectRow = ({ subject }) => (
    <tr className="hover-row">
      <td>
        <Link 
          to={`/subjects/${subject.id}`} 
          className="text-decoration-none fw-bold text-dark"
        >
          {subject.name}
        </Link>
        <div>
          <small className="text-muted">Code: {subject.code}</small>
        </div>
      </td>
      <td>
        <span className={`badge bg-${getCategoryColor(subject.category)}`}>
          {subject.category}
        </span>
      </td>
      <td>
        {subject.grades.map(grade => (
          <span 
            key={grade} 
            className={`badge bg-${getGradeBadgeVariant(grade)} me-1 mb-1`}
          >
            Grade {grade}
          </span>
        ))}
      </td>
      <td>
        {subject.teacher && (
          <small>{subject.teacher}</small>
        )}
      </td>
      <td>
        <Link 
          to={`/subjects/${subject.id}`} 
          className="btn btn-sm btn-outline-primary"
        >
          Details
        </Link>
      </td>
    </tr>
  );

  const StatisticsCard = () => (
    <div className="row mb-4">
      <div className="col-md-3">
        <div className="card bg-primary text-white text-center">
          <div className="card-body">
            <h4>{subjects.length}</h4>
            <p className="mb-0">Total Subjects</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card bg-success text-white text-center">
          <div className="card-body">
            <h4>{getSubjectsByCategory('Core').length}</h4>
            <p className="mb-0">Core Subjects</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card bg-warning text-dark text-center">
          <div className="card-body">
            <h4>{getSubjectsByCategory('Elective').length}</h4>
            <p className="mb-0">Elective Subjects</p>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card bg-info text-white text-center">
          <div className="card-body">
            <h4>{new Set(subjects.flatMap(s => s.grades)).size}</h4>
            <p className="mb-0">Grade Levels</p>
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
              <span className="visually-hidden">Loading subjects...</span>
            </div>
            <p className="mt-3 text-muted">Loading school subjects...</p>
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
          <button className="btn btn-sm btn-outline-danger ms-auto" onClick={fetchSubjects}>
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
          <h1 className="display-5 fw-bold text-primary">School Subjects</h1>
          <p className="lead text-muted">
            Explore our comprehensive curriculum designed to nurture well-rounded individuals
          </p>
        </div>
        <div className="col-md-4 text-end">
          <button className="btn btn-outline-primary" onClick={fetchSubjects}>
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
            <div className="col-md-4">
              <label className="form-label">Search Subjects</label>
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by name, code, or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-4">
              <label className="form-label">Filter by Grade</label>
              <select 
                className="form-select" 
                value={selectedGrade} 
                onChange={(e) => setSelectedGrade(e.target.value)}
              >
                <option value="all">All Grades</option>
                {Object.entries(gradeLevels).map(([level, grades]) => (
                  <optgroup key={level} label={level}>
                    {grades.map(grade => (
                      <option key={grade} value={grade}>Grade {grade}</option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
            <div className="col-md-4">
              <label className="form-label">Filter by Category</label>
              <select 
                className="form-select" 
                value={selectedCategory} 
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map(category => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Active Filters */}
          <div className="mt-3">
            {(selectedGrade !== 'all' || selectedCategory !== 'all' || searchTerm) && (
              <div className="d-flex align-items-center">
                <small className="text-muted me-2">Active filters:</small>
                {selectedGrade !== 'all' && (
                  <span className="badge bg-primary me-2">
                    Grade: {selectedGrade}
                    <button 
                      className="btn-close btn-close-white ms-1" 
                      style={{ fontSize: '0.6rem' }}
                      onClick={() => setSelectedGrade('all')}
                    ></button>
                  </span>
                )}
                {selectedCategory !== 'all' && (
                  <span className={`badge bg-${getCategoryColor(selectedCategory)} me-2`}>
                    {categories.find(c => c.value === selectedCategory)?.label}
                    <button 
                      className="btn-close btn-close-white ms-1" 
                      style={{ fontSize: '0.6rem' }}
                      onClick={() => setSelectedCategory('all')}
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
          Showing {filteredSubjects.length} of {subjects.length} subjects
        </h5>
        {filteredSubjects.length === 0 && !loading && (
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={() => {
              setSelectedGrade('all');
              setSelectedCategory('all');
              setSearchTerm('');
            }}
          >
            Clear all filters
          </button>
        )}
      </div>

      {/* View Toggle (Optional) */}
      <div className="d-flex justify-content-end mb-3">
        <div className="btn-group" role="group">
          <button type="button" className="btn btn-outline-primary active">
            <i className="bi bi-grid"></i> Grid View
          </button>
          <button type="button" className="btn btn-outline-primary">
            <i className="bi bi-list"></i> List View
          </button>
        </div>
      </div>

      {/* Subjects Grid */}
      {filteredSubjects.length > 0 ? (
        <div className="row g-4">
          {filteredSubjects.map(subject => (
            <div key={subject.id} className="col-xl-4 col-lg-6 col-md-6">
              <SubjectCard subject={subject} />
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-5">
          <i className="bi bi-book" style={{ fontSize: '4rem', color: '#6c757d' }}></i>
          <h4 className="mt-3 text-muted">No subjects found</h4>
          <p className="text-muted">
            Try adjusting your filters or search terms to see more results.
          </p>
          <button 
            className="btn btn-primary"
            onClick={() => {
              setSelectedGrade('all');
              setSelectedCategory('all');
              setSearchTerm('');
            }}
          >
            Clear all filters
          </button>
        </div>
      )}

      {/* Alternative Table View (commented out but available) */}
      {/*
      <div className="card mt-4">
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Subject Name</th>
                  <th>Category</th>
                  <th>Grades</th>
                  <th>Teacher</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredSubjects.map(subject => (
                  <SubjectRow key={subject.id} subject={subject} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      */}

      {/* CBC Information */}
      <div className="card mt-5">
        <div className="card-header bg-gradient-primary text-white">
          <h5 className="mb-0">
            <i className="bi bi-info-circle me-2"></i>
            About CBC Curriculum
          </h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-8">
              <p className="lead">
                The Competency Based Curriculum (CBC) in Kenya focuses on developing 
                competencies rather than just content knowledge.
              </p>
              <p>
                It emphasizes the development of the following core competencies:
              </p>
              <div className="row">
                <div className="col-md-6">
                  <ul className="list-unstyled">
                    <li><i className="bi bi-check-circle text-success me-2"></i>Communication and collaboration</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Critical thinking and problem solving</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Creativity and imagination</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Digital literacy</li>
                  </ul>
                </div>
                <div className="col-md-6">
                  <ul className="list-unstyled">
                    <li><i className="bi bi-check-circle text-success me-2"></i>Citizenship</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Learning to learn</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Self-efficacy</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Environmental awareness</li>
                  </ul>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card bg-light">
                <div className="card-body">
                  <h6>Curriculum Structure</h6>
                  <div className="small">
                    <strong>Lower Primary:</strong> Grades 1-3<br/>
                    <strong>Upper Primary:</strong> Grades 4-6<br/>
                    <strong>Junior Secondary:</strong> Grades 7-9<br/>
                    <strong>Senior Secondary:</strong> Grades 10-12
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
        .hover-row:hover {
          background-color: rgba(0, 123, 255, 0.05);
        }
      `}</style>
    </div>
  );
}

export default Subjects;