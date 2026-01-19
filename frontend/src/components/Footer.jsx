import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Footer.css'; // Create this CSS file

function Footer() {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [currentYear] = useState(new Date().getFullYear());
  const location = useLocation();

  // Scroll to top functionality
  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (email && validateEmail(email)) {
      try {
        // Simulate API call
        console.log('Subscribing email:', email);
        setSubscribed(true);
        setEmail('');
        setTimeout(() => setSubscribed(false), 5000);
      } catch (error) {
        console.error('Subscription failed:', error);
      }
    }
  };

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const quickLinks = {
    'Academics': [
      { name: 'Curriculum', path: '/curriculum' },
      { name: 'Programs', path: '/programs' },
      { name: 'Departments', path: '/departments' },
      { name: 'Courses', path: '/courses' },
      { name: 'Faculty', path: '/faculty' }
    ],
    'Student Life': [
      { name: 'Student Clubs', path: '/student-clubs' },
      { name: 'Athletics', path: '/athletics' },
      { name: 'Arts', path: '/arts' },
      { name: 'Events', path: '/events' },
      { name: 'Gallery', path: '/gallery' }
    ],
    'Admissions': [
      { name: 'Apply Now', path: '/apply' },
      { name: 'Requirements', path: '/requirements' },
      { name: 'Tuition', path: '/tuition' },
      { name: 'Scholarships', path: '/scholarships' },
      { name: 'Campus Tour', path: '/campus-tour' }
    ],
    'Resources': [
      { name: 'Library', path: '/library' },
      { name: 'Calendar', path: '/calendar' },
      { name: 'Documents', path: '/documents' },
      { name: 'Downloads', path: '/downloads' },
      { name: 'Tech Support', path: '/tech-support' }
    ]
  };

  const portalLinks = {
    'Student Portal': '/student-portal',
    'Parent Portal': '/parent-portal', 
    'Teacher Portal': '/teacher-dashboard',
    'Admin Portal': '/admin'
  };

  const socialLinks = [
    { 
      name: 'Facebook', 
      icon: 'bi bi-facebook', 
      url: 'https://facebook.com/delvokacademy',
      color: '#1877F2'
    },
    { 
      name: 'Twitter', 
      icon: 'bi bi-twitter-x', 
      url: 'https://twitter.com/delvokacademy',
      color: '#000000'
    },
    { 
      name: 'Instagram', 
      icon: 'bi bi-instagram', 
      url: 'https://instagram.com/delvokacademy',
      color: '#E4405F'
    },
    { 
      name: 'LinkedIn', 
      icon: 'bi bi-linkedin', 
      url: 'https://linkedin.com/school/delvokacademy',
      color: '#0A66C2'
    },
    { 
      name: 'YouTube', 
      icon: 'bi bi-youtube', 
      url: 'https://youtube.com/delvokacademy',
      color: '#FF0000'
    },
    { 
      name: 'WhatsApp', 
      icon: 'bi bi-whatsapp', 
      url: 'https://wa.me/254700123456',
      color: '#25D366'
    }
  ];

  const contactInfo = [
    {
      icon: 'bi bi-geo-alt-fill',
      text: '123 Education Road, Westlands, Nairobi, Kenya',
      link: 'https://maps.google.com/?q=123+Education+Road+Nairobi'
    },
    {
      icon: 'bi bi-telephone-fill',
      text: '+254-700-123-456',
      link: 'tel:+254700123456'
    },
    {
      icon: 'bi bi-envelope-fill',
      text: 'info@delvok.ac.ke',
      link: 'mailto:info@delvok.ac.ke'
    },
    {
      icon: 'bi bi-clock-fill',
      text: 'Mon - Fri: 7:00 AM - 5:00 PM',
      link: null
    }
  ];

  return (
    <footer className="footer bg-dark text-white position-relative">
      {/* Main Footer Content */}
      <div className="footer-main py-5">
        <div className="container">
          <div className="row g-4">
            {/* School Information */}
            <div className="col-xl-4 col-lg-5 col-md-6">
              <div className="footer-brand mb-4">
                <div className="school-logo d-flex align-items-center mb-3">
                  <div className="logo-wrapper position-relative me-3">
                    <span className="logo-icon fs-2">🏫</span>
                  </div>
                  <div>
                    <h4 className="mb-0 fw-bold text-primary">Delvok Academy</h4>
                    <small className="text-light opacity-75">CBC Education Center</small>
                  </div>
                </div>
                
                <p className="footer-description text-light mb-4">
                  Providing quality CBC education from Grade 1 to 12. Nurturing future leaders 
                  through competency-based curriculum and holistic development since 2010.
                </p>
                
                <div className="footer-contact">
                  {contactInfo.map((contact, index) => (
                    <div key={index} className="contact-item d-flex align-items-center mb-3">
                      <i className={`${contact.icon} text-primary me-3 fs-6`}></i>
                      {contact.link ? (
                        <a 
                          href={contact.link} 
                          className="text-light text-decoration-none hover-link"
                          target={contact.link.startsWith('http') ? '_blank' : '_self'}
                          rel={contact.link.startsWith('http') ? 'noopener noreferrer' : ''}
                        >
                          {contact.text}
                        </a>
                      ) : (
                        <span className="text-light">{contact.text}</span>
                      )}
                    </div>
                  ))}
                </div>

                {/* Portal Quick Access */}
                <div className="portal-access mt-4">
                  <h6 className="text-primary mb-3">Quick Portals</h6>
                  <div className="d-flex flex-wrap gap-2">
                    {Object.entries(portalLinks).map(([name, path]) => (
                      <Link
                        key={name}
                        to={path}
                        className="btn btn-outline-primary btn-sm portal-btn"
                      >
                        {name}
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Links Sections */}
            <div className="col-xl-8 col-lg-7 col-md-6">
              <div className="row">
                {Object.entries(quickLinks).map(([category, links]) => (
                  <div key={category} className="col-sm-6 col-lg-3 mb-4">
                    <h6 className="footer-heading text-primary mb-3 position-relative">
                      {category}
                    </h6>
                    <ul className="footer-links list-unstyled">
                      {links.map(link => (
                        <li key={link.name} className="mb-2">
                          <Link 
                            to={link.path} 
                            className={`footer-link text-light text-decoration-none ${
                              location.pathname === link.path ? 'active' : ''
                            }`}
                          >
                            {link.name}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>

              {/* Social Links & Accreditation */}
              <div className="row mt-4">
                <div className="col-lg-8">
                  <div className="social-section">
                    <h6 className="text-primary mb-3">Follow Us</h6>
                    <div className="d-flex flex-wrap gap-3">
                      {socialLinks.map(social => (
                        <a
                          key={social.name}
                          href={social.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="social-link d-flex align-items-center justify-content-center"
                          title={social.name}
                          style={{ 
                            backgroundColor: `${social.color}15`,
                            border: `1px solid ${social.color}30`
                          }}
                        >
                          <i className={social.icon} style={{ color: social.color }}></i>
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="accreditation text-center text-lg-end">
                    <div className="accreditation-badge bg-primary rounded p-3 mb-3">
                      <i className="bi bi-award-fill fs-2 d-block mb-2"></i>
                      <small className="fw-bold">KNEC ACCREDITED</small>
                    </div>
                    <small className="text-light opacity-75">
                      Ministry of Education Registered
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Newsletter Subscription */}
          <div className="row mt-5">
            <div className="col-lg-10 mx-auto">
              <div 
                className="newsletter-card bg-gradient-primary rounded-3 p-4 position-relative overflow-hidden"
                style={{
                  background: 'linear-gradient(135deg, var(--bs-primary) 0%, #0056b3 100%)'
                }}
              >
                <div className="newsletter-pattern position-absolute top-0 end-0 h-100 w-50 opacity-10">
                  <i className="bi bi-journal-bookmark-fill fs-1"></i>
                </div>
                
                <div className="row align-items-center position-relative">
                  <div className="col-md-7 mb-3 mb-md-0">
                    <h5 className="text-white mb-2">
                      <i className="bi bi-envelope-check me-2"></i>
                      Stay Updated
                    </h5>
                    <p className="text-light mb-0 opacity-90">
                      Get the latest news, events, and academic updates delivered to your inbox.
                    </p>
                  </div>
                  <div className="col-md-5">
                    {subscribed ? (
                      <div className="alert alert-success mb-0 text-center py-2 border-0">
                        <i className="bi bi-check-circle-fill me-2"></i>
                        Thank you for subscribing!
                      </div>
                    ) : (
                      <form onSubmit={handleSubscribe} className="d-flex gap-2">
                        <div className="flex-grow-1">
                          <input
                            type="email"
                            className="form-control form-control-lg"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                          />
                        </div>
                        <button 
                          type="submit" 
                          className="btn btn-light btn-lg px-3 d-flex align-items-center"
                        >
                          <i className="bi bi-send-fill"></i>
                        </button>
                      </form>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Bottom */}
      <div className="footer-bottom bg-dark border-top border-secondary py-4">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-md-7 mb-3 mb-md-0">
              <div className="d-flex flex-column flex-md-row align-items-center align-items-md-start gap-3">
                <p className="mb-0 text-center text-md-start">
                  &copy; {currentYear} Delvok Academy. All rights reserved.
                </p>
                <div className="d-flex flex-wrap justify-content-center justify-content-md-start gap-3">
                  <Link to="/privacy-policy" className="text-light text-decoration-none small hover-link">
                    Privacy Policy
                  </Link>
                  <Link to="/terms-of-service" className="text-light text-decoration-none small hover-link">
                    Terms of Service
                  </Link>
                  <Link to="/sitemap" className="text-light text-decoration-none small hover-link">
                    Sitemap
                  </Link>
                  <Link to="/contact" className="text-light text-decoration-none small hover-link">
                    Contact
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="col-md-5 text-center text-md-end">
              <div className="d-flex flex-column flex-md-row align-items-center justify-content-md-end gap-3">
                <div className="developer-credit">
                  <small className="text-light opacity-75">
                    Made with <i className="bi bi-heart-fill text-danger mx-1"></i> for education
                  </small>
                </div>
                <div className="stats d-none d-md-flex gap-3">
                  <small className="text-light opacity-75">
                    <i className="bi bi-people-fill me-1"></i> 1500+ Students
                  </small>
                  <small className="text-light opacity-75">
                    <i className="bi bi-mortarboard-fill me-1"></i> 80+ Teachers
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Back to Top Button */}
      <button 
        className={`back-to-top btn btn-primary rounded-circle shadow-lg ${
          showBackToTop ? 'show' : ''
        }`}
        onClick={scrollToTop}
        aria-label="Back to top"
      >
        <i className="bi bi-chevron-up"></i>
      </button>
    </footer>
  );
}

export default Footer;