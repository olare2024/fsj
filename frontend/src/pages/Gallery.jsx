import React, { useState } from 'react';

function Gallery() {
  const [activeCategory, setActiveCategory] = useState('all');

  const galleryItems = [
    {
      id: 1,
      title: 'Science Lab Activities',
      category: 'academics',
      image: '/images/gallery/science-lab.jpg',
      description: 'Students conducting experiments in our modern science laboratories'
    },
    {
      id: 2,
      title: 'Sports Day 2024',
      category: 'sports',
      image: '/images/gallery/sports-day.jpg',
      description: 'Annual inter-house sports competition'
    },
    {
      id: 3,
      title: 'Music Festival',
      category: 'arts',
      image: '/images/gallery/music-festival.jpg',
      description: 'Students performing at the regional music festival'
    },
    {
      id: 4,
      category: 'academics',
      image: '/images/gallery/computer-lab.jpg',
      title: 'Computer Class',
      description: 'ICT lessons in our fully equipped computer lab'
    },
    {
      id: 5,
      title: 'Art Exhibition',
      category: 'arts',
      image: '/images/gallery/art-exhibition.jpg',
      description: 'Student artwork displayed in annual exhibition'
    },
    {
      id: 6,
      title: 'Library Reading',
      category: 'academics',
      image: '/images/gallery/library.jpg',
      description: 'Students engaged in research and reading activities'
    },
    {
      id: 7,
      title: 'Basketball Team',
      category: 'sports',
      image: '/images/gallery/basketball.jpg',
      description: 'School basketball team during practice session'
    },
    {
      id: 8,
      title: 'Cultural Day',
      category: 'events',
      image: '/images/gallery/cultural-day.jpg',
      description: 'Traditional performances during cultural day celebrations'
    },
    {
      id: 9,
      title: 'Graduation Ceremony',
      category: 'events',
      image: '/images/gallery/graduation.jpg',
      description: 'Grade 12 students during graduation ceremony'
    }
  ];

  const categories = [
    { id: 'all', name: 'All Photos', count: galleryItems.length },
    { id: 'academics', name: 'Academics', count: galleryItems.filter(item => item.category === 'academics').length },
    { id: 'sports', name: 'Sports', count: galleryItems.filter(item => item.category === 'sports').length },
    { id: 'arts', name: 'Arts', count: galleryItems.filter(item => item.category === 'arts').length },
    { id: 'events', name: 'Events', count: galleryItems.filter(item => item.category === 'events').length }
  ];

  const filteredItems = activeCategory === 'all' 
    ? galleryItems 
    : galleryItems.filter(item => item.category === activeCategory);

  return (
    <div className="gallery-page">
      {/* Hero Section */}
      <section className="gallery-hero bg-info text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">School Gallery</h1>
              <p className="lead fs-4">
                Capturing Moments of Learning, Growth, and Achievement
              </p>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">📸</div>
            </div>
          </div>
        </div>
      </section>

      {/* Category Filter */}
      <section className="py-4 bg-light">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="d-flex flex-wrap gap-2 justify-content-center">
                {categories.map(category => (
                  <button
                    key={category.id}
                    className={`btn ${
                      activeCategory === category.id ? 'btn-primary' : 'btn-outline-primary'
                    } position-relative`}
                    onClick={() => setActiveCategory(category.id)}
                  >
                    {category.name}
                    <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-secondary">
                      {category.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Gallery Grid */}
      <section className="py-5">
        <div className="container">
          <div className="row g-4">
            {filteredItems.map(item => (
              <div key={item.id} className="col-md-6 col-lg-4">
                <div className="card gallery-card h-100 shadow-sm border-0">
                  <div className="gallery-image position-relative overflow-hidden">
                    <div className="image-placeholder bg-secondary p-5 text-white text-center">
                      <i className="bi bi-image display-4"></i>
                      <p className="mt-2 small">School Photo</p>
                    </div>
                    <div className="gallery-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center opacity-0">
                      <button className="btn btn-light btn-sm">
                        <i className="bi bi-zoom-in me-1"></i>
                        View
                      </button>
                    </div>
                  </div>
                  <div className="card-body">
                    <h6 className="card-title">{item.title}</h6>
                    <p className="card-text text-muted small">{item.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredItems.length === 0 && (
            <div className="text-center py-5">
              <i className="bi bi-images display-1 text-muted"></i>
              <h4 className="mt-3 text-muted">No photos found</h4>
              <p className="text-muted">Try selecting a different category.</p>
            </div>
          )}
        </div>
      </section>

      {/* Statistics */}
      <section className="py-5 bg-primary text-white">
        <div className="container">
          <div className="row text-center">
            <div className="col-md-3">
              <div className="display-4 fw-bold">{galleryItems.length}+</div>
              <p>Photos in Gallery</p>
            </div>
            <div className="col-md-3">
              <div className="display-4 fw-bold">{categories.length}</div>
              <p>Categories</p>
            </div>
            <div className="col-md-3">
              <div className="display-4 fw-bold">2024</div>
              <p>Current Year</p>
            </div>
            <div className="col-md-3">
              <div className="display-4 fw-bold">100+</div>
              <p>Events Captured</p>
            </div>
          </div>
        </div>
      </section>

      <style jsx>{`
        .gallery-hero {
          background: linear-gradient(135deg, var(--bs-info) 0%, #0dcaf0 100%);
        }
        
        .gallery-card {
          transition: transform 0.3s ease;
          cursor: pointer;
        }
        
        .gallery-card:hover {
          transform: translateY(-5px);
        }
        
        .gallery-image {
          border-radius: 0.375rem 0.375rem 0 0;
        }
        
        .gallery-overlay {
          background: rgba(0, 0, 0, 0.7);
          transition: opacity 0.3s ease;
        }
        
        .gallery-card:hover .gallery-overlay {
          opacity: 1;
        }
        
        .image-placeholder {
          min-height: 250px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
        
        .btn .badge {
          font-size: 0.6rem;
        }
      `}</style>
    </div>
  );
}

export default Gallery;