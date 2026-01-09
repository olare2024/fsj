import React from 'react';
import { Link, useSearchParams } from 'react-router-dom';

function SearchResults() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  // Mock search results
  const results = [
    {
      type: 'page',
      title: 'About Delvok Academy',
      description: 'Learn about our school mission, vision, and values',
      path: '/about',
      relevance: 95
    },
    {
      type: 'teacher',
      title: 'Sarah Johnson - Science Teacher',
      description: 'Biology and Chemistry instructor with 10 years experience',
      path: '/teachers',
      relevance: 88
    },
    {
      type: 'event',
      title: 'Science Fair 2024',
      description: 'Annual science exhibition showcasing student projects',
      path: '/events',
      relevance: 76
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-lg-8">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1>Search Results</h1>
              <p className="lead">
                {query ? `Results for "${query}"` : 'Enter a search term to find content'}
              </p>
            </div>
            <Link to="/" className="btn btn-outline-primary">
              <i className="bi bi-arrow-left me-2"></i>
              Back to Home
            </Link>
          </div>

          {query ? (
            <div className="search-results">
              <p className="text-muted mb-4">
                Found {results.length} results in {Math.random() * 2 + 0.5}s
              </p>

              {results.map((result, index) => (
                <div key={index} className="card mb-3">
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <h5 className="card-title">
                        <Link to={result.path} className="text-decoration-none">
                          {result.title}
                        </Link>
                      </h5>
                      <span className="badge bg-secondary">{result.type}</span>
                    </div>
                    <p className="card-text">{result.description}</p>
                    <div className="d-flex justify-content-between align-items-center">
                      <Link to={result.path} className="text-primary text-decoration-none">
                        View Details →
                      </Link>
                      <small className="text-muted">
                        Relevance: {result.relevance}%
                      </small>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card">
              <div className="card-body text-center py-5">
                <i className="bi bi-search display-1 text-muted mb-3"></i>
                <h3>No Search Query</h3>
                <p className="text-muted">
                  Please enter a search term to find students, teachers, events, and more.
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Search Tips</h5>
            </div>
            <div className="card-body">
              <ul className="list-unstyled">
                <li className="mb-2">
                  <i className="bi bi-lightbulb text-warning me-2"></i>
                  Use specific keywords
                </li>
                <li className="mb-2">
                  <i className="bi bi-lightbulb text-warning me-2"></i>
                  Try teacher or student names
                </li>
                <li className="mb-2">
                  <i className="bi bi-lightbulb text-warning me-2"></i>
                  Search for events or programs
                </li>
                <li>
                  <i className="bi bi-lightbulb text-warning me-2"></i>
                  Use quotes for exact phrases
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SearchResults;