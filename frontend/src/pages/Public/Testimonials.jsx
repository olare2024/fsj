import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Testimonials() {
  const [activeCategory, setActiveCategory] = useState('all');

  const testimonialCategories = [
    { id: 'all', name: 'All Testimonials', count: 12 },
    { id: 'parents', name: 'Parents', count: 4 },
    { id: 'students', name: 'Students', count: 5 },
    { id: 'alumni', name: 'Alumni', count: 3 }
  ];

  const testimonials = [
    {
      id: 1,
      name: 'Mr. & Mrs. Otieno',
      role: 'Parents of Grade 5 Student',
      category: 'parents',
      image: '/images/testimonials/parents-otieno.jpg',
      content: 'The dual curriculum approach at Delvok Academy has been transformative for our daughter. She maintains strong Kenyan roots while developing global perspectives. The teachers are dedicated and the communication with parents is excellent.',
      rating: 5,
      year: 2024
    },
    {
      id: 2,
      name: 'Sarah Mwangi',
      role: 'Grade 11 Student - Cambridge Program',
      category: 'students',
      image: '/images/testimonials/sarah-mwangi.jpg',
      content: 'The Cambridge program challenged me to think critically and independently. The small class sizes mean I get personalized attention, and the teachers genuinely care about my success. I feel prepared for university anywhere in the world.',
      rating: 5,
      year: 2024
    },
    {
      id: 3,
      name: 'Dr. Amina Juma',
      role: 'Alumni - Class of 2015',
      category: 'alumni',
      image: '/images/testimonials/amina-juma.jpg',
      content: 'Delvok Academy laid the foundation for my medical career. The rigorous science program and research opportunities prepared me for university abroad. The dual curriculum gave me an edge in both local and international contexts.',
      rating: 5,
      year: 2024
    },
    {
      id: 4,
      name: 'Mr. David Kimani',
      role: 'Parent of CBC Grade 3 Student',
      category: 'parents',
      image: '/images/testimonials/david-kimani.jpg',
      content: 'We chose Delvok for the seamless integration of CBC with international standards. Our son is developing strong foundational skills while enjoying learning. The school\'s focus on character development is particularly impressive.',
      rating: 5,
      year: 2024
    },
    {
      id: 5,
      name: 'Kevin Omondi',
      role: 'Grade 8 Student - CBC Program',
      category: 'students',
      image: '/images/testimonials/kevin-omondi.jpg',
      content: 'I love how learning is practical and fun at Delvok. The CBC activities help me understand concepts better, and the Cambridge classes challenge me to think bigger. The sports facilities are amazing too!',
      rating: 5,
      year: 2024
    },
    {
      id: 6,
      name: 'Mark Chen',
      role: 'Alumni - Class of 2016',
      category: 'alumni',
      image: '/images/testimonials/mark-chen.jpg',
      content: 'The leadership opportunities and global perspective I gained at Delvok helped me secure a scholarship at Oxford. The teachers went above and beyond to support my university applications.',
      rating: 5,
      year: 2024
    }
  ];

  const featuredStories = [
    {
      title: 'From Delvok to MIT: A STEM Journey',
      student: 'Grace Wanjiku',
      achievement: 'Full scholarship to Massachusetts Institute of Technology',
      story: 'Grace\'s passion for robotics was nurtured through Delvok\'s advanced STEM program, leading to international competitions and ultimately, admission to MIT.',
      image: '/images/stories/grace-mit.jpg'
    },
    {
      title: 'Dual Curriculum Advantage',
      student: 'Ahmed Hassan',
      achievement: 'Accepted to both University of Nairobi and University of Toronto',
      story: 'Ahmed leveraged his dual qualifications to keep his options open, ultimately choosing based on his career goals rather than limited by curriculum constraints.',
      image: '/images/stories/ahmed-dual.jpg'
    }
  ];

  const filteredTestimonials = testimonials.filter(testimonial => 
    activeCategory === 'all' || testimonial.category === activeCategory
  );

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, index) => (
      <i 
        key={index}
        className={`bi ${index < rating ? 'bi-star-fill' : 'bi-star'} text-warning`}
      ></i>
    ));
  };

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Home</Link></li>
              <li className="breadcrumb-item"><Link to="/about">About</Link></li>
              <li className="breadcrumb-item active">Testimonials</li>
            </ol>
          </nav>
          
          <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-dark">Testimonials</h1>
            <p className="lead mb-0">Hear From Our Community</p>
            <div className="mt-3">
              <span className="badge bg-primary fs-6">Real Stories, Real Success</span>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="card bg-primary text-white mb-5">
        <div className="card-body p-5 text-center">
          <h2 className="display-5 fw-bold mb-3">Voices of Delvok Academy</h2>
          <p className="fs-5 mb-4">
            Discover what parents, students, and alumni have to say about their experiences 
            with our dual curriculum approach and community environment.
          </p>
          <div className="d-flex justify-content-center gap-3">
            <button className="btn btn-light btn-lg">
              Share Your Story
            </button>
            <button className="btn btn-outline-light btn-lg">
              Schedule a Tour
            </button>
          </div>
        </div>
      </div>

      {/* Testimonial Categories */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-body">
              <h5 className="mb-3">Filter Testimonials</h5>
              <div className="d-flex flex-wrap gap-3">
                {testimonialCategories.map(category => (
                  <button
                    key={category.id}
                    className={`btn ${activeCategory === category.id ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setActiveCategory(category.id)}
                  >
                    {category.name} <span className="badge bg-light text-dark ms-1">{category.count}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Testimonials Grid */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="mb-4">What Our Community Says</h3>
          <div className="row g-4">
            {filteredTestimonials.map(testimonial => (
              <div key={testimonial.id} className="col-lg-6">
                <div className="card h-100 testimonial-card">
                  <div className="card-body">
                    <div className="d-flex align-items-start mb-3">
                      <div className="testimonial-image-placeholder bg-light rounded-circle d-flex align-items-center justify-content-center me-3"
                           style={{width: '60px', height: '60px'}}>
                        <i className="bi bi-person display-6 text-muted"></i>
                      </div>
                      <div>
                        <h5 className="card-title mb-1">{testimonial.name}</h5>
                        <p className="card-text text-muted small mb-1">{testimonial.role}</p>
                        <div className="rating">
                          {renderStars(testimonial.rating)}
                        </div>
                      </div>
                    </div>
                    <p className="card-text fst-italic">"{testimonial.content}"</p>
                  </div>
                  <div className="card-footer bg-transparent">
                    <small className="text-muted">
                      Shared in {testimonial.year}
                    </small>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Success Stories */}
      <div className="row mb-5">
        <div className="col-12">
          <h3 className="text-center mb-4">Featured Success Stories</h3>
          <div className="row g-4">
            {featuredStories.map((story, index) => (
              <div key={index} className="col-lg-6">
                <div className="card h-100 feature-story">
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-4">
                        <div className="story-image-placeholder bg-light rounded d-flex align-items-center justify-content-center mb-3"
                             style={{height: '150px'}}>
                          <i className="bi bi-image display-4 text-muted"></i>
                        </div>
                      </div>
                      <div className="col-md-8">
                        <h5 className="card-title">{story.title}</h5>
                        <h6 className="text-primary">{story.student}</h6>
                        <p className="card-text"><strong>{story.achievement}</strong></p>
                        <p className="card-text">{story.story}</p>
                        <button className="btn btn-outline-primary btn-sm">
                          Read Full Story
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Statistics Section */}
      <div className="row mb-5">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-body py-5">
              <h3 className="text-center mb-4">By the Numbers</h3>
              <div className="row text-center">
                <div className="col-md-3 mb-4">
                  <div className="display-4 fw-bold text-primary">98%</div>
                  <div className="fs-5">Parent Satisfaction Rate</div>
                </div>
                <div className="col-md-3 mb-4">
                  <div className="display-4 fw-bold text-primary">95%</div>
                  <div className="fs-5">University Acceptance Rate</div>
                </div>
                <div className="col-md-3 mb-4">
                  <div className="display-4 fw-bold text-primary">2,500+</div>
                  <div className="fs-5">Alumni Worldwide</div>
                </div>
                <div className="col-md-3 mb-4">
                  <div className="display-4 fw-bold text-primary">4.8/5</div>
                  <div className="fs-5">Average Rating</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Video Testimonials Section */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h4 className="mb-0">Video Testimonials</h4>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6 mb-4">
                  <div className="video-placeholder bg-dark rounded d-flex align-items-center justify-content-center"
                       style={{height: '250px'}}>
                    <i className="bi bi-play-circle display-1 text-white"></i>
                  </div>
                  <div className="mt-2">
                    <h6>Parent Perspective: The Dual Curriculum Advantage</h6>
                    <small className="text-muted">Mr. & Mrs. Kamau share their experience</small>
                  </div>
                </div>
                <div className="col-md-6 mb-4">
                  <div className="video-placeholder bg-dark rounded d-flex align-items-center justify-content-center"
                       style={{height: '250px'}}>
                    <i className="bi bi-play-circle display-1 text-white"></i>
                  </div>
                  <div className="mt-2">
                    <h6>Alumni Success: From Delvok to Global Careers</h6>
                    <small className="text-muted">Graduates share their career journeys</small>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <button className="btn btn-primary">
                  View More Video Testimonials
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Share Your Story CTA */}
      <div className="row mt-5">
        <div className="col-lg-8 mx-auto">
          <div className="card bg-success text-white text-center">
            <div className="card-body py-5">
              <h3 className="mb-3">Share Your Delvok Story</h3>
              <p className="fs-5 mb-4">
                Are you a current parent, student, or alumni with a story to share? 
                We'd love to hear about your experience at Delvok Academy.
              </p>
              <button className="btn btn-light btn-lg">
                Submit Your Testimonial
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Testimonials;