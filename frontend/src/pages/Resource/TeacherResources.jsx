import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function TeacherResources() {
  const { currentUser } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const resources = [
    {
      id: 1,
      title: 'Lesson Plan Templates',
      category: 'planning',
      description: 'Customizable lesson plan templates for all subjects and grade levels',
      fileType: 'doc',
      fileSize: '2.1 MB',
      downloads: 245,
      rating: 4.8,
      featured: true
    },
    {
      id: 2,
      title: 'Classroom Management Strategies',
      category: 'management',
      description: 'Proven techniques for effective classroom management and student engagement',
      fileType: 'pdf',
      fileSize: '3.4 MB',
      downloads: 189,
      rating: 4.6,
      featured: true
    },
    {
      id: 3,
      title: 'Assessment Rubrics Collection',
      category: 'assessment',
      description: 'Comprehensive collection of grading rubrics for various assignments',
      fileType: 'pdf',
      fileSize: '1.8 MB',
      downloads: 167,
      rating: 4.7,
      featured: false
    },
    {
      id: 4,
      title: 'STEM Activity Guides',
      category: 'stem',
      description: 'Hands-on STEM activities and experiments for elementary and middle school',
      fileType: 'pdf',
      fileSize: '4.2 MB',
      downloads: 134,
      rating: 4.9,
      featured: true
    },
    {
      id: 5,
      title: 'Differentiated Instruction Toolkit',
      category: 'instruction',
      description: 'Resources for implementing differentiated instruction strategies',
      fileType: 'zip',
      fileSize: '5.7 MB',
      downloads: 98,
      rating: 4.5,
      featured: false
    },
    {
      id: 6,
      title: 'Digital Classroom Tools Guide',
      category: 'technology',
      description: 'Guide to digital tools and platforms for enhanced teaching',
      fileType: 'pdf',
      fileSize: '2.9 MB',
      downloads: 211,
      rating: 4.7,
      featured: true
    }
  ];

  const categories = [
    { value: 'all', label: 'All Categories', count: resources.length },
    { value: 'planning', label: 'Lesson Planning', count: resources.filter(r => r.category === 'planning').length },
    { value: 'management', label: 'Classroom Management', count: resources.filter(r => r.category === 'management').length },
    { value: 'assessment', label: 'Assessment', count: resources.filter(r => r.category === 'assessment').length },
    { value: 'stem', label: 'STEM Resources', count: resources.filter(r => r.category === 'stem').length },
    { value: 'instruction', label: 'Instruction', count: resources.filter(r => r.category === 'instruction').length },
    { value: 'technology', label: 'Technology', count: resources.filter(r => r.category === 'technology').length }
  ];

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || resource.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getFileTypeIcon = (type) => {
    switch (type) {
      case 'pdf': return 'bi-file-pdf';
      case 'doc': return 'bi-file-word';
      case 'zip': return 'bi-file-zip';
      default: return 'bi-file-earmark';
    }
  };

  const getFileTypeColor = (type) => {
    switch (type) {
      case 'pdf': return 'danger';
      case 'doc': return 'primary';
      case 'zip': return 'warning';
      default: return 'secondary';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Teacher Resources</h1>
          <p className="lead">
            Welcome back, {currentUser?.firstName}! Access teaching materials and professional development resources.
          </p>
        </div>
        <Link to="/dashboard" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Dashboard
        </Link>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>{resources.length}</h3>
              <p className="mb-0">Total Resources</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>{resources.filter(r => r.featured).length}</h3>
              <p className="mb-0">Featured</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>{resources.reduce((sum, r) => sum + r.downloads, 0)}+</h3>
              <p className="mb-0">Total Downloads</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>4.7/5</h3>
              <p className="mb-0">Average Rating</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-6">
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search resources..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-4">
              <select
                className="form-select"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map(category => (
                  <option key={category.value} value={category.value}>
                    {category.label} ({category.count})
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-2">
              <button className="btn btn-primary w-100">
                <i className="bi bi-plus-circle me-2"></i>
                Upload
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Resources */}
      <div className="mb-4">
        <h4 className="mb-3">
          <i className="bi bi-star-fill text-warning me-2"></i>
          Featured Resources
        </h4>
        <div className="row g-3">
          {resources.filter(r => r.featured).slice(0, 2).map(resource => (
            <div key={resource.id} className="col-md-6">
              <div className="card border-warning">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <span className="badge bg-warning">Featured</span>
                    <span className={`badge bg-${getFileTypeColor(resource.fileType)}`}>
                      {resource.fileType.toUpperCase()}
                    </span>
                  </div>
                  <h5 className="card-title">{resource.title}</h5>
                  <p className="card-text">{resource.description}</p>
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <small className="text-muted me-3">
                        <i className="bi bi-download me-1"></i>
                        {resource.downloads}
                      </small>
                      <small className="text-muted">
                        <i className="bi bi-star-fill text-warning me-1"></i>
                        {resource.rating}
                      </small>
                    </div>
                    <button className="btn btn-primary btn-sm">
                      <i className="bi bi-download me-1"></i>
                      Download
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* All Resources Grid */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">All Teaching Resources</h5>
        </div>
        <div className="card-body">
          <div className="row g-4">
            {filteredResources.map(resource => (
              <div key={resource.id} className="col-md-6 col-lg-4">
                <div className="card h-100 shadow-sm">
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <i className={`bi ${getFileTypeIcon(resource.fileType)} text-${getFileTypeColor(resource.fileType)} fs-4`}></i>
                      {resource.featured && (
                        <span className="badge bg-warning">Featured</span>
                      )}
                    </div>
                    <h6 className="card-title">{resource.title}</h6>
                    <p className="card-text small text-muted">{resource.description}</p>
                    
                    <div className="resource-meta">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <span className="badge bg-light text-dark">{resource.category}</span>
                        <small className="text-muted">{resource.fileSize}</small>
                      </div>
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <small className="text-muted me-2">
                            <i className="bi bi-download me-1"></i>
                            {resource.downloads}
                          </small>
                          <small className="text-muted">
                            <i className="bi bi-star-fill text-warning me-1"></i>
                            {resource.rating}
                          </small>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="card-footer">
                    <div className="d-flex gap-2">
                      <button className="btn btn-primary btn-sm flex-fill">
                        <i className="bi bi-download me-1"></i>
                        Download
                      </button>
                      <button className="btn btn-outline-secondary btn-sm">
                        <i className="bi bi-eye"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredResources.length === 0 && (
            <div className="text-center py-5">
              <i className="bi bi-search display-1 text-muted mb-3"></i>
              <h4>No resources found</h4>
              <p className="text-muted">
                Try adjusting your search terms or browse different categories.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Professional Development Section */}
      <div className="card mt-4">
        <div className="card-header">
          <h5 className="mb-0">Professional Development</h5>
        </div>
        <div className="card-body">
          <div className="row g-4">
            <div className="col-md-4">
              <div className="text-center">
                <i className="bi bi-laptop display-4 text-primary mb-3"></i>
                <h6>Online Workshops</h6>
                <p className="small text-muted">
                  Live and recorded professional development sessions
                </p>
                <button className="btn btn-outline-primary btn-sm">View Schedule</button>
              </div>
            </div>
            <div className="col-md-4">
              <div className="text-center">
                <i className="bi bi-people display-4 text-success mb-3"></i>
                <h6>Teacher Communities</h6>
                <p className="small text-muted">
                  Connect with colleagues and share best practices
                </p>
                <button className="btn btn-outline-success btn-sm">Join Groups</button>
              </div>
            </div>
            <div className="col-md-4">
              <div className="text-center">
                <i className="bi bi-award display-4 text-warning mb-3"></i>
                <h6>Certification</h6>
                <p className="small text-muted">
                  Continuing education and certification programs
                </p>
                <button className="btn btn-outline-warning btn-sm">Learn More</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TeacherResources;