import React, { useState, useEffect } from 'react';

function News() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data - replace with actual API call
  useEffect(() => {
    const mockNews = [
      {
        id: 1,
        title: 'Welcome to New Academic Year 2024',
        content: 'We are excited to welcome all students, parents, and staff to the new academic year 2024...',
        excerpt: 'Exciting new beginnings at Delvok Academy for 2024',
        category: 'general',
        publishedAt: '2024-01-15T10:00:00Z',
        author: { firstName: 'Admin', lastName: 'User' }
      },
      {
        id: 2,
        title: 'Science Fair Winners Announced',
        content: 'Our students have once again demonstrated exceptional talent and innovation...',
        excerpt: 'Student innovations shine at annual science competition',
        category: 'academic',
        publishedAt: '2024-01-10T14:30:00Z',
        author: { firstName: 'Sarah', lastName: 'Johnson' }
      },
      {
        id: 3,
        title: 'Basketball Team Wins Regional Championship',
        content: 'Our school basketball team has brought home the regional championship trophy...',
        excerpt: 'Victory for our talented basketball players',
        category: 'sports',
        publishedAt: '2024-01-08T16:45:00Z',
        author: { firstName: 'David', lastName: 'Kimani' }
      }
    ];

    setNews(mockNews);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="news-page">
      <div className="container mt-4">
        <div className="row">
          <div className="col-12">
            <h1 className="display-5 fw-bold text-primary mb-4">School News & Announcements</h1>
          </div>
        </div>

        <div className="row">
          {news.map((article) => (
            <div key={article.id} className="col-lg-6 mb-4">
              <div className="card news-card h-100 shadow-sm">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <span className={`badge bg-${
                      article.category === 'academic' ? 'primary' : 
                      article.category === 'sports' ? 'success' : 
                      article.category === 'events' ? 'warning' : 'info'
                    }`}>
                      {article.category.charAt(0).toUpperCase() + article.category.slice(1)}
                    </span>
                    <small className="text-muted">
                      {new Date(article.publishedAt).toLocaleDateString()}
                    </small>
                  </div>
                  
                  <h5 className="card-title">{article.title}</h5>
                  <p className="card-text text-muted">{article.excerpt}</p>
                  
                  <div className="d-flex justify-content-between align-items-center mt-auto">
                    <small className="text-muted">
                      By {article.author.firstName} {article.author.lastName}
                    </small>
                    <button className="btn btn-outline-primary btn-sm">
                      Read More
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default News;