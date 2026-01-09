import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function ResearchPortal() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

  const researchItems = [
    {
      id: 1,
      title: 'The Impact of Technology on Student Learning Outcomes',
      authors: ['Dr. Sarah Johnson', 'Prof. Michael Chen'],
      category: 'education',
      type: 'journal',
      year: 2024,
      abstract: 'A comprehensive study examining how digital tools affect student performance across different learning environments.',
      citations: 42,
      access: 'open',
      tags: ['technology', 'learning outcomes', 'digital tools']
    },
    {
      id: 2,
      title: 'STEM Education in Early Childhood Development',
      authors: ['Dr. Emily Rodriguez'],
      category: 'stem',
      type: 'conference',
      year: 2023,
      abstract: 'Exploring the benefits of introducing STEM concepts to preschool and elementary school students.',
      citations: 28,
      access: 'subscription',
      tags: ['STEM', 'early childhood', 'curriculum']
    },
    {
      id: 3,
      title: 'Inclusive Classroom Practices for Diverse Learners',
      authors: ['Prof. James Wilson', 'Dr. Lisa Thompson'],
      category: 'inclusion',
      type: 'journal',
      year: 2024,
      abstract: 'Research on effective strategies for creating inclusive learning environments for students with diverse needs.',
      citations: 35,
      access: 'open',
      tags: ['inclusion', 'diversity', 'teaching strategies']
    },
    {
      id: 4,
      title: 'The Role of Artificial Intelligence in Personalized Learning',
      authors: ['Dr. Robert Kim', 'Prof. Amanda Davis'],
      category: 'technology',
      type: 'thesis',
      year: 2023,
      abstract: 'Investigating how AI-powered systems can adapt to individual student learning styles and paces.',
      citations: 19,
      access: 'open',
      tags: ['AI', 'personalized learning', 'adaptive systems']
    },
    {
      id: 5,
      title: 'Mental Health and Academic Performance in Adolescents',
      authors: ['Dr. Patricia Martinez'],
      category: 'psychology',
      type: 'journal',
      year: 2024,
      abstract: 'Longitudinal study on the relationship between mental wellness and academic achievement in high school students.',
      citations: 56,
      access: 'subscription',
      tags: ['mental health', 'academic performance', 'adolescents']
    },
    {
      id: 6,
      title: 'Project-Based Learning Assessment Framework',
      authors: ['Dr. Kevin Brown', 'Prof. Nancy White'],
      category: 'assessment',
      type: 'conference',
      year: 2023,
      abstract: 'Developing and validating assessment tools for project-based learning environments.',
      citations: 23,
      access: 'open',
      tags: ['PBL', 'assessment', 'framework']
    }
  ];

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'education', label: 'Education' },
    { value: 'stem', label: 'STEM' },
    { value: 'inclusion', label: 'Inclusion' },
    { value: 'technology', label: 'Technology' },
    { value: 'psychology', label: 'Psychology' },
    { value: 'assessment', label: 'Assessment' }
  ];

  const types = [
    { value: 'all', label: 'All Types' },
    { value: 'journal', label: 'Journal Articles' },
    { value: 'conference', label: 'Conference Papers' },
    { value: 'thesis', label: 'Theses' },
    { value: 'report', label: 'Research Reports' }
  ];

  const filteredItems = researchItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.abstract.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.authors.some(author => author.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    const matchesType = selectedType === 'all' || item.type === selectedType;
    return matchesSearch && matchesCategory && matchesType;
  });

  const getAccessBadge = (access) => {
    return access === 'open' 
      ? { class: 'bg-success', text: 'Open Access' }
      : { class: 'bg-warning', text: 'Subscription Required' };
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'journal': return 'bi-journal';
      case 'conference': return 'bi-mic';
      case 'thesis': return 'bi-file-earmark-text';
      case 'report': return 'bi-clipboard-data';
      default: return 'bi-file-text';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Research Portal</h1>
          <p className="lead">Access academic research and scholarly publications from our community</p>
        </div>
        <Link to="/resources" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Resources
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-5">
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search research papers, authors, keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
            <div className="col-md-3">
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
            <div className="col-md-3">
              <select
                className="form-select"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                {types.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-1">
              <button className="btn btn-primary w-100">
                <i className="bi bi-funnel"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Research Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>{researchItems.length}</h3>
              <p className="mb-0">Research Papers</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>{researchItems.filter(item => item.access === 'open').length}</h3>
              <p className="mb-0">Open Access</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>{researchItems.reduce((sum, item) => sum + item.citations, 0)}+</h3>
              <p className="mb-0">Total Citations</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>2024</h3>
              <p className="mb-0">Latest Research</p>
            </div>
          </div>
        </div>
      </div>

      {/* Research Papers List */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Research Publications</h5>
        </div>
        <div className="card-body">
          {filteredItems.map(item => {
            const accessBadge = getAccessBadge(item.access);
            return (
              <div key={item.id} className="research-item border-bottom pb-4 mb-4">
                <div className="d-flex justify-content-between align-items-start mb-2">
                  <h5 className="card-title mb-1">{item.title}</h5>
                  <span className={`badge ${accessBadge.class}`}>{accessBadge.text}</span>
                </div>
                
                <div className="d-flex align-items-center mb-2">
                  <i className={`bi ${getTypeIcon(item.type)} text-muted me-2`}></i>
                  <span className="text-muted me-3">{item.type.charAt(0).toUpperCase() + item.type.slice(1)}</span>
                  <span className="text-muted me-3">{item.year}</span>
                  <span className="text-muted">
                    <i className="bi bi-quote me-1"></i>
                    {item.citations} citations
                  </span>
                </div>

                <p className="card-text mb-3">{item.abstract}</p>

                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <strong className="text-muted">Authors: </strong>
                    <span>{item.authors.join(', ')}</span>
                  </div>
                  <div className="d-flex gap-2">
                    {item.tags.map((tag, index) => (
                      <span key={index} className="badge bg-light text-dark">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-3">
                  <button className="btn btn-primary btn-sm me-2">
                    <i className="bi bi-download me-1"></i>
                    Download PDF
                  </button>
                  <button className="btn btn-outline-secondary btn-sm me-2">
                    <i className="bi bi-quote me-1"></i>
                    Cite
                  </button>
                  <button className="btn btn-outline-secondary btn-sm">
                    <i className="bi bi-share me-1"></i>
                    Share
                  </button>
                </div>
              </div>
            );
          })}

          {filteredItems.length === 0 && (
            <div className="text-center py-5">
              <i className="bi bi-search display-1 text-muted mb-3"></i>
              <h4>No research papers found</h4>
              <p className="text-muted">
                Try adjusting your search criteria or browse different categories.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Additional Resources */}
      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Research Tools</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-database me-2"></i>
                  Academic Databases
                </button>
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-journals me-2"></i>
                  Reference Manager
                </button>
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-graph-up me-2"></i>
                  Data Analysis Tools
                </button>
                <button className="btn btn-outline-primary text-start">
                  <i className="bi bi-pencil-square me-2"></i>
                  Writing Assistance
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Research Support</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-person me-2"></i>
                  Research Advisor
                </button>
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-calendar me-2"></i>
                  Research Workshops
                </button>
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-cash-coin me-2"></i>
                  Grant Opportunities
                </button>
                <button className="btn btn-outline-success text-start">
                  <i className="bi bi-people me-2"></i>
                  Research Groups
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResearchPortal;