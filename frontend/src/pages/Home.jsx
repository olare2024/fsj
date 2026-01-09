import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { studentsAPI } from '../services/studentAPI.js';
import { academicAPI } from '../services/academicAPI.js';
import { newsAPI } from '../services/newsAPI.js';
import { eventAPI } from '../services/eventAPI.js';
import { analyticsAPI } from '../services/analyticsAPI.js';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Home Component Error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
          <div className="text-center p-4">
            <div className="display-1 text-primary mb-3">⚠️</div>
            <h3 className="text-dark mb-3">Something went wrong</h3>
            <p className="text-muted mb-4">
              We're having trouble loading the page. Please try refreshing.
            </p>
            <button 
              className="btn btn-primary me-3"
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </button>
            <button 
              className="btn btn-outline-primary"
              onClick={() => this.setState({ hasError: false })}
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Image Component with Enhanced Features
const ImageWithFallback = React.memo(({ 
  src, 
  fallback, 
  alt, 
  className = '', 
  width, 
  height,
  ...props 
}) => {
  const [error, setError] = useState(false);
  const [loaded, setLoaded] = useState(false);
  
  return (
    <div className={`image-container position-relative ${className}`}>
      {!error ? (
        <>
          {!loaded && (
            <div className="image-placeholder position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-light">
              <div className="spinner-border spinner-border-sm text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}
          <img 
            src={src} 
            alt={alt}
            className={`img-fluid ${loaded ? 'opacity-100' : 'opacity-0'} transition-opacity`}
            onLoad={() => setLoaded(true)}
            onError={() => setError(true)}
            loading="lazy"
            width={width}
            height={height}
            {...props}
          />
        </>
      ) : (
        <div className="d-flex align-items-center justify-content-center bg-light text-muted w-100 h-100 rounded">
          <span className="fs-1">{fallback}</span>
        </div>
      )}
    </div>
  );
});

// Video Banner Component
const VideoBanner = React.memo(({ 
  src, 
  poster, 
  fallbackImage,
  alt,
  autoPlay = true,
  loop = true,
  muted = true,
  controls = false,
  className = ''
}) => {
  const [error, setError] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const videoRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (video && autoPlay) {
      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.catch(error => {
          console.log('Video autoplay prevented:', error);
          // Fallback to showing controls if autoplay fails
          video.controls = true;
        });
      }
    }
  }, [autoPlay]);

  return (
    <div className={`video-container position-relative ${className}`}>
      {!error ? (
        <>
          {!loaded && (
            <div className="video-placeholder position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-dark">
              <div className="spinner-border spinner-border-sm text-light" role="status">
                <span className="visually-hidden">Loading video...</span>
              </div>
            </div>
          )}
          <video
            ref={videoRef}
            className={`video-banner ${loaded ? 'opacity-100' : 'opacity-0'}`}
            src={src}
            poster={poster}
            autoPlay={autoPlay}
            loop={loop}
            muted={muted}
            controls={controls}
            playsInline
            preload="metadata"
            onLoadedData={() => setLoaded(true)}
            onError={() => setError(true)}
            aria-label={alt}
          >
            <source src={src} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </>
      ) : (
        <div 
          className="fallback-image w-100 h-100 d-flex align-items-center justify-content-center bg-dark text-light"
          style={{ backgroundImage: `url(${fallbackImage})`, backgroundSize: 'cover', backgroundPosition: 'center' }}
        >
          <span className="fs-1">{fallbackImage ? '' : '🎬'}</span>
        </div>
      )}
    </div>
  );
});

// Stats Card Component
const StatsCard = React.memo(({ number, label, icon, description, color, onClick }) => (
  <div 
    className={`stat-card text-center p-4 rounded-3 shadow-sm hover-lift border-${color} border-top border-4`}
    onClick={onClick}
    role="button"
    tabIndex={0}
    onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
    aria-label={`${label}: ${number}`}
  >
    <div className="stat-icon display-4 mb-3" aria-hidden="true">{icon}</div>
    <h3 className="fw-bold text-primary mb-2">{number}</h3>
    <h6 className="text-dark mb-2">{label}</h6>
    <p className="text-muted small mb-0">{description}</p>
  </div>
));

// News Card Component
const NewsCard = React.memo(({ item, onClick }) => (
  <div 
    className="card news-card h-100 shadow-sm hover-lift"
    onClick={() => onClick?.(item)}
    role="article"
    tabIndex={0}
    onKeyDown={(e) => e.key === 'Enter' && onClick?.(item)}
  >
    <ImageWithFallback
      src={item.image}
      fallback="📰"
      alt={item.title}
      className="card-img-top"
      style={{ height: '200px', objectFit: 'cover' }}
    />
    <div className="card-body">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <span className="badge bg-primary">{item.category}</span>
        <small className="text-muted">{item.readTime}</small>
      </div>
      <h5 className="card-title">{item.title}</h5>
      <p className="card-text text-muted">{item.excerpt}</p>
      <div className="d-flex justify-content-between align-items-center">
        <small className="text-muted">
          <i className="bi bi-calendar me-1" aria-hidden="true"></i>
          {new Date(item.date).toLocaleDateString()}
        </small>
        <small className="text-muted">By {item.author}</small>
      </div>
    </div>
  </div>
));

// Loading Skeleton Component
const LoadingSkeleton = () => (
  <div className="min-vh-100 d-flex flex-column justify-content-center align-items-center bg-light">
    <div className="text-center p-4">
      <div className="spinner-border text-primary mb-4" style={{width: '3rem', height: '3rem'}} role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      <h4 className="text-primary mb-2">Loading Delvok Academy</h4>
      <p className="text-muted">Preparing your educational journey...</p>
      <div className="progress mt-3" style={{width: '200px'}}>
        <div 
          className="progress-bar progress-bar-striped progress-bar-animated" 
          style={{width: '75%'}}
        ></div>
      </div>
    </div>
  </div>
);

function Home() {
  const [statistics, setStatistics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [news, setNews] = useState([]);
  const [events, setEvents] = useState([]);
  const [academicStats, setAcademicStats] = useState(null);
  const [apiErrors, setApiErrors] = useState({});
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);
  const [bannerType, setBannerType] = useState('image'); // 'image' or 'video'
  
  const navigate = useNavigate();
  const bannerRef = useRef(null);
  const slideIntervalRef = useRef(null);
  const observerRef = useRef(null);

  // Media assets with video support
  const bannerAssets = {
    image: {
      schoolBuilding: '/img/banner/school-building.jpg',
      scienceLab: '/img/banner/science-lab.jpg',
      studentsGroup: '/img/banner/students-group.jpg',
      sportsField: '/img/banner/sports-field.jpg',
    },
    video: {
      campusTour: '/video/campus-tour.mp4',
      schoolLife: '/video/school-life.mp4',
      graduation: '/video/graduation.mp4',
    },
    fallbacks: {
      campusTour: '/img/banner/school-building.jpg',
      schoolLife: '/img/banner/students-group.jpg',
      graduation: '/img/banner/sports-field.jpg',
    }
  };

  const newsImages = {
    scienceLab: '/img/news/science-lab.jpg',
    mathOlympiad: '/img/news/math-olympiad.jpg',
    parentWorkshop: '/img/news/parent-workshop.jpg',
  };

  // Memoized calculations
  const totalStudents = useMemo(() => 
    statistics.reduce((total, stat) => total + parseInt(stat.total || 0), 0),
    [statistics]
  );

  const overallGrowth = useMemo(() => {
    if (statistics.length === 0) return '+0%';
    const totalGrowth = statistics.reduce((sum, stat) => {
      const growth = parseInt(stat.growth) || 0;
      return sum + growth;
    }, 0);
    return `+${Math.round(totalGrowth / statistics.length)}%`;
  }, [statistics]);

  // Banner slides with video support
  const bannerSlides = useMemo(() => [
    {
      id: 1,
      type: 'video',
      title: "Experience Delvok Academy",
      subtitle: "Virtual campus tour showcasing our state-of-the-art facilities",
      video: bannerAssets.video.campusTour,
      poster: bannerAssets.fallbacks.campusTour,
      fallbackImage: bannerAssets.image.schoolBuilding,
      cta: "Take Virtual Tour",
      link: "/virtual-tour",
      theme: "primary",
      overlay: "rgba(30, 58, 138, 0.6)",
      features: ["Interactive Tour", "360° Views", "Facility Highlights"]
    },
    {
      id: 2,
      type: 'image',
      title: "Excellence in Education",
      subtitle: "Nurturing Future Leaders Through Quality CBC & Cambridge Curriculum",
      image: bannerAssets.image.schoolBuilding,
      fallbackImage: "🏫",
      cta: "Discover Our Programs",
      link: "/academics",
      theme: "primary",
      overlay: "rgba(30, 58, 138, 0.7)",
      features: ["CBC Curriculum", "Cambridge Program", "Qualified Teachers"]
    },
    {
      id: 3,
      type: 'image',
      title: "Modern Learning Environment",
      subtitle: "State-of-the-art facilities for holistic student development and innovation",
      image: bannerAssets.image.scienceLab,
      fallbackImage: "🔬",
      cta: "View Facilities",
      link: "/campus-tour",
      theme: "success",
      overlay: "rgba(21, 128, 61, 0.7)",
      features: ["Science Labs", "Library", "Sports Facilities"]
    },
    {
      id: 4,
      type: 'video',
      title: "Life at Delvok",
      subtitle: "Experience our vibrant community through student life highlights",
      video: bannerAssets.video.schoolLife,
      poster: bannerAssets.fallbacks.schoolLife,
      fallbackImage: bannerAssets.image.studentsGroup,
      cta: "Watch Student Stories",
      link: "/student-life",
      theme: "warning",
      overlay: "rgba(146, 64, 14, 0.6)",
      features: ["Student Activities", "Clubs", "Community Events"]
    }
  ], []);

  // Quick stats data with API integration
  const quickStats = useMemo(() => [
    { 
      number: `${totalStudents}+`, 
      label: 'Students Enrolled', 
      icon: '👨‍🎓',
      description: 'Growing community across 12 grades',
      color: 'primary',
      apiSource: 'students'
    },
    { 
      number: academicStats?.teachers || '42+', 
      label: 'Qualified Teachers', 
      icon: '👩‍🏫',
      description: 'Dedicated and certified teaching staff',
      color: 'success',
      apiSource: 'academic'
    },
    { 
      number: academicStats?.subjects || '18+', 
      label: 'Subjects Offered', 
      icon: '📖',
      description: 'Comprehensive CBC & Cambridge curriculum',
      color: 'warning',
      apiSource: 'academic'
    },
    { 
      number: '98%', 
      label: 'Parent Satisfaction', 
      icon: '⭐',
      description: 'Proven track record of excellence',
      color: 'info',
      apiSource: 'analytics'
    },
    { 
      number: academicStats?.classes || '24+', 
      label: 'Active Classes', 
      icon: '🏫',
      description: 'Well-structured learning environments',
      color: 'danger',
      apiSource: 'academic'
    },
    { 
      number: events?.length || '15+', 
      label: 'Upcoming Events', 
      icon: '📅',
      description: 'Academic and extracurricular activities',
      color: 'secondary',
      apiSource: 'events'
    }
  ], [totalStudents, academicStats, events]);

  // Grade levels data
  const gradeLevels = useMemo(() => [
    {
      title: 'Lower Primary',
      subtitle: 'Grades 1-3',
      description: 'Foundational literacy, numeracy, and life skills development',
      icon: '📚',
      color: 'primary',
      features: ['Literacy Skills', 'Numeracy', 'Environmental Activities', 'Creative Arts'],
      link: '/academics/elementary',
      studentCount: statistics.find(s => s.grade === '1-3')?.total || '45+'
    },
    {
      title: 'Upper Primary',
      subtitle: 'Grades 4-6',
      description: 'Enhanced curriculum with practical skills and project-based learning',
      icon: '🎒',
      color: 'success',
      features: ['Science & Technology', 'Social Studies', 'Agriculture', 'Home Science'],
      link: '/academics/elementary',
      studentCount: statistics.find(s => s.grade === '4-6')?.total || '42+'
    },
    {
      title: 'Junior Secondary',
      subtitle: 'Grades 7-9',
      description: 'Broad-based education with career guidance and skill development',
      icon: '🔬',
      color: 'warning',
      features: ['Pre-Technical Studies', 'Business Studies', 'Agriculture', 'Sports'],
      link: '/academics/middle-school',
      studentCount: statistics.find(s => s.grade === '7-9')?.total || '48+'
    },
    {
      title: 'Senior Secondary',
      subtitle: 'Grades 10-12',
      description: 'Specialized pathways with university preparation',
      icon: '🎓',
      color: 'info',
      features: ['STEM Pathway', 'Social Sciences', 'Arts & Sports', 'Technical'],
      link: '/academics/high-school',
      studentCount: statistics.find(s => s.grade === '10-12')?.total || '52+'
    }
  ], [statistics]);

  // Fetch all data
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setApiErrors({});

    try {
      // Fetch statistics in parallel
      const promises = [
        fetchStatistics(),
        fetchAcademicStats(),
        fetchNews(),
        fetchEvents(),
        fetchAnalytics()
      ];

      await Promise.allSettled(promises);
      
      trackInteraction('home_data_loaded', 'all_sections');
    } catch (error) {
      console.error('Error fetching home data:', error);
      setApiErrors(prev => ({ ...prev, general: error.message }));
    } finally {
      setLoading(false);
    }
  }, []);

  // Individual fetch functions
  const fetchStatistics = useCallback(async () => {
    try {
      const result = await studentsAPI.getStatistics();
      if (result.success) {
        setStatistics(result.data);
      } else {
        throw new Error(result.error?.message || 'Failed to fetch statistics');
      }
    } catch (error) {
      console.error('Error fetching statistics:', error);
      setApiErrors(prev => ({ ...prev, statistics: error.message }));
      // Use mock data as fallback
      setStatistics(getMockStatistics());
    }
  }, []);

  const fetchAcademicStats = useCallback(async () => {
    try {
      const [classesResult, subjectsResult, overviewResult] = await Promise.all([
        academicAPI.getClassStatistics(),
        academicAPI.getSubjects({ limit: 1 }),
        academicAPI.getAcademicOverview()
      ]);

      setAcademicStats({
        classes: classesResult.data?.total || 24,
        subjects: subjectsResult.data?.count || 18,
        teachers: overviewResult.data?.teachers || 42,
        activeClasses: overviewResult.data?.active_classes || 20
      });
    } catch (error) {
      console.error('Error fetching academic stats:', error);
      setApiErrors(prev => ({ ...prev, academic: error.message }));
    }
  }, []);

  const fetchNews = useCallback(async () => {
    try {
      const result = await newsAPI.getLatestNews({ limit: 3 });
      if (result.success) {
        setNews(result.data);
      } else {
        throw new Error(result.error?.message || 'Failed to fetch news');
      }
    } catch (error) {
      console.error('Error fetching news:', error);
      setApiErrors(prev => ({ ...prev, news: error.message }));
      setNews(getMockNews());
    }
  }, []);

  const fetchEvents = useCallback(async () => {
    try {
      const result = await eventAPI.getUpcomingEvents({ limit: 5 });
      if (result.success) {
        setEvents(result.data);
      } else {
        throw new Error(result.error?.message || 'Failed to fetch events');
      }
    } catch (error) {
      console.error('Error fetching events:', error);
      setApiErrors(prev => ({ ...prev, events: error.message }));
    }
  }, []);

  const fetchAnalytics = useCallback(async () => {
    try {
      const result = await analyticsAPI.getHomeAnalytics();
      if (result.success) {
        // Process analytics data if needed
        console.log('Analytics loaded:', result.data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setApiErrors(prev => ({ ...prev, analytics: error.message }));
    }
  }, []);

  // Mock data fallback functions
  const getMockStatistics = useCallback(() => [
    { grade: '1-3', total: '145', growth: '+8%' },
    { grade: '4-6', total: '142', growth: '+6%' },
    { grade: '7-9', total: '148', growth: '+10%' },
    { grade: '10-12', total: '152', growth: '+12%' }
  ], []);

  const getMockNews = useCallback(() => [
    {
      id: 1,
      title: 'New Science Lab Inauguration',
      excerpt: 'State-of-the-art science laboratory opened for senior students',
      date: '2024-02-15',
      image: newsImages.scienceLab,
      category: 'Facilities',
      author: 'Principal Office',
      readTime: '2 min read'
    },
    {
      id: 2,
      title: 'Math Olympiad Winners 2024',
      excerpt: 'Our students secure top positions in national mathematics competition',
      date: '2024-02-10',
      image: newsImages.mathOlympiad,
      category: 'Achievements',
      author: 'Math Department',
      readTime: '3 min read'
    },
    {
      id: 3,
      title: 'Parent Workshop Series Launch',
      excerpt: 'Interactive sessions on digital parenting and student support',
      date: '2024-02-05',
      image: newsImages.parentWorkshop,
      category: 'Community',
      author: 'PTA Committee',
      readTime: '4 min read'
    }
  ], []);

  // Banner navigation
  const nextSlide = useCallback(() => {
    setCurrentSlide(prev => (prev + 1) % bannerSlides.length);
  }, [bannerSlides.length]);

  const prevSlide = useCallback(() => {
    setCurrentSlide(prev => (prev - 1 + bannerSlides.length) % bannerSlides.length);
  }, [bannerSlides.length]);

  // Touch handlers for mobile
  const handleTouchStart = useCallback((e) => {
    setTouchStart(e.targetTouches[0].clientX);
  }, []);

  const handleTouchMove = useCallback((e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  }, []);

  const handleTouchEnd = useCallback(() => {
    if (touchStart - touchEnd > 50) {
      nextSlide();
    }
    if (touchStart - touchEnd < -50) {
      prevSlide();
    }
  }, [touchStart, touchEnd, nextSlide, prevSlide]);

  // Analytics tracking
  const trackInteraction = useCallback((action, label) => {
    if (window.gtag) {
      window.gtag('event', action, {
        event_category: 'Home Page',
        event_label: label
      });
    }
    console.log(`📊 Analytics: ${action} - ${label}`);
  }, []);

  const handleNextSlide = useCallback(() => {
    trackInteraction('banner_navigation', 'next');
    nextSlide();
  }, [nextSlide, trackInteraction]);

  const handlePrevSlide = useCallback(() => {
    trackInteraction('banner_navigation', 'prev');
    prevSlide();
  }, [prevSlide, trackInteraction]);

  const handleSlideClick = useCallback((index) => {
    trackInteraction('banner_dot_click', `slide_${index + 1}`);
    setCurrentSlide(index);
  }, [trackInteraction]);

  const handleStatClick = useCallback((stat) => {
    trackInteraction('stat_click', stat.label);
    
    // Navigate based on stat type
    switch(stat.apiSource) {
      case 'academic':
        navigate('/academics');
        break;
      case 'events':
        navigate('/events');
        break;
      case 'students':
        navigate('/students');
        break;
      default:
        // No navigation for other stats
        break;
    }
  }, [navigate, trackInteraction]);

  const handleNewsClick = useCallback((newsItem) => {
    trackInteraction('news_click', newsItem.title);
    navigate(`/news/${newsItem.id}`);
  }, [navigate, trackInteraction]);

  // Effects
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  useEffect(() => {
    // Intersection Observer for animations
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setIsVisible(true);
            entry.target.classList.add('visible');
            trackInteraction('section_view', entry.target.id || 'unknown_section');
          }
        });
      },
      { threshold: 0.1, rootMargin: '50px' }
    );

    const sections = document.querySelectorAll('.animate-on-scroll');
    sections.forEach(section => {
      observerRef.current.observe(section);
    });

    // Auto-rotate banner slides
    slideIntervalRef.current = setInterval(nextSlide, 7000);

    // Keyboard navigation
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowLeft') handlePrevSlide();
      if (e.key === 'ArrowRight') handleNextSlide();
      if (e.key === 'Escape' && bannerRef.current) {
        bannerRef.current.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      clearInterval(slideIntervalRef.current);
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [nextSlide, handlePrevSlide, handleNextSlide, trackInteraction]);

  // Handle banner type toggle (video/image)
  const toggleBannerType = useCallback(() => {
    setBannerType(prev => prev === 'image' ? 'video' : 'image');
    trackInteraction('banner_type_toggle', bannerType === 'image' ? 'video' : 'image');
  }, [bannerType, trackInteraction]);

  // Loading state
  if (loading) {
    return <LoadingSkeleton />;
  }

  // Get current slide
  const currentBannerSlide = bannerSlides[currentSlide];

  return (
    <ErrorBoundary>
      <div className="home-page">
        {/* Enhanced Hero Banner with Video Support */}
        <section 
          className="hero-banner"
          ref={bannerRef}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          aria-label="School promotional banner"
        >
          <div className="banner-slides">
            {bannerSlides.map((slide, index) => (
              <div 
                key={slide.id}
                className={`banner-slide ${index === currentSlide ? 'active' : ''}`}
                role="group"
                aria-label={`Slide ${index + 1} of ${bannerSlides.length}`}
                aria-hidden={index !== currentSlide}
              >
                {slide.type === 'video' ? (
                  <div className="video-overlay" style={{ backgroundColor: slide.overlay }}>
                    <VideoBanner
                      src={slide.video}
                      poster={slide.poster}
                      fallbackImage={slide.fallbackImage}
                      alt={slide.title}
                      className="w-100 h-100"
                      autoPlay={index === currentSlide}
                    />
                  </div>
                ) : (
                  <div 
                    className="image-overlay w-100 h-100"
                    style={{ 
                      backgroundImage: `linear-gradient(${slide.overlay}, ${slide.overlay}), url(${slide.image})` 
                    }}
                  />
                )}
                
                <div className="slide-content position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center">
                  <div className="container">
                    <div className="row align-items-center min-vh-80">
                      <div className="col-lg-8">
                        <div className="banner-content">
                          <h1 className="display-3 fw-bold text-white mb-4 animate-fade-in">
                            {slide.title}
                          </h1>
                          <p className="lead fs-3 text-white mb-4 animate-fade-in-delay">
                            {slide.subtitle}
                          </p>
                          
                          <div className="banner-features mb-4 animate-fade-in-delay">
                            {slide.features.map((feature, idx) => (
                              <span key={idx} className="badge bg-light text-primary me-2 mb-2 fs-6">
                                {feature}
                              </span>
                            ))}
                          </div>
                          
                          <div className="d-flex flex-wrap gap-3 animate-bounce-in">
                            <Link 
                              to={slide.link} 
                              className={`btn btn-${slide.theme} btn-lg px-5 py-3 fs-5`}
                              onClick={() => trackInteraction('cta_click', slide.cta)}
                            >
                              {slide.cta} <i className="bi bi-arrow-right ms-2"></i>
                            </Link>
                            <Link 
                              to="/contact" 
                              className="btn btn-outline-light btn-lg px-5 py-3 fs-5"
                              onClick={() => trackInteraction('cta_click', 'schedule_visit')}
                            >
                              Schedule Visit
                            </Link>
                            {slide.type === 'video' && (
                              <button 
                                className="btn btn-outline-light btn-lg px-5 py-3 fs-5"
                                onClick={toggleBannerType}
                              >
                                <i className={`bi bi-${bannerType === 'video' ? 'image' : 'play-circle'} me-2`}></i>
                                {bannerType === 'video' ? 'Show Images' : 'Show Videos'}
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Banner Controls */}
          <button 
            className="banner-control prev"
            onClick={handlePrevSlide}
            aria-label="Previous slide"
          >
            <i className="bi bi-chevron-left"></i>
          </button>
          <button 
            className="banner-control next"
            onClick={handleNextSlide}
            aria-label="Next slide"
          >
            <i className="bi bi-chevron-right"></i>
          </button>

          {/* Banner Navigation Dots */}
          <div className="banner-dots" role="tablist" aria-label="Banner slides">
            {bannerSlides.map((_, index) => (
              <button
                key={index}
                className={`dot ${index === currentSlide ? 'active' : ''}`}
                onClick={() => handleSlideClick(index)}
                role="tab"
                aria-selected={index === currentSlide}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>

          {/* Banner Progress Bar */}
          <div className="banner-progress">
            <div 
              className="progress-bar" 
              style={{ 
                width: `${((currentSlide + 1) / bannerSlides.length) * 100}%`,
                transition: 'width 0.3s ease'
              }}
            />
          </div>
        </section>

        {/* API Errors Alert */}
        {Object.keys(apiErrors).length > 0 && (
          <div className="container mt-3">
            <div className="alert alert-warning alert-dismissible fade show" role="alert">
              <i className="bi bi-exclamation-triangle me-2"></i>
              <strong>Note:</strong> Some data may be limited. 
              <button 
                type="button" 
                className="btn-close" 
                onClick={() => setApiErrors({})}
                aria-label="Close warning"
              ></button>
            </div>
          </div>
        )}

        {/* Quick Stats Section */}
        <section id="stats" className="py-5 bg-white animate-on-scroll" aria-label="School statistics">
          <div className="container">
            <div className="text-center mb-5">
              <span className="badge bg-primary mb-3">At a Glance</span>
              <h2 className="display-5 fw-bold text-primary mb-3">Delvok Academy by Numbers</h2>
              <p className="lead text-muted">Key metrics showcasing our growth and impact</p>
            </div>
            <div className="row g-4">
              {quickStats.map((stat, index) => (
                <div key={index} className="col-md-4 col-lg-2">
                  <StatsCard {...stat} onClick={() => handleStatClick(stat)} />
                </div>
              ))}
            </div>
            
            {/* Growth Indicator */}
            <div className="text-center mt-5">
              <div className="d-inline-flex align-items-center bg-light rounded-pill px-4 py-2">
                <span className="text-success fw-bold me-2">
                  <i className="bi bi-graph-up-arrow"></i> {overallGrowth}
                </span>
                <span className="text-muted">Overall Growth This Year</span>
              </div>
            </div>
          </div>
        </section>

        {/* School Levels Section */}
        <section id="programs" className="py-5 bg-light animate-on-scroll" aria-label="Academic programs">
          <div className="container">
            <div className="text-center mb-5">
              <span className="badge bg-primary mb-3">Our Programs</span>
              <h2 className="display-5 fw-bold text-primary mb-3">Educational Levels</h2>
              <p className="lead text-muted">Comprehensive CBC & Cambridge education from foundation to specialization</p>
            </div>
            <div className="row g-4">
              {gradeLevels.map((level, index) => (
                <div key={index} className="col-md-6 col-lg-3">
                  <Link 
                    to={level.link} 
                    className="text-decoration-none"
                    onClick={() => trackInteraction('program_click', level.title)}
                  >
                    <div className={`card level-card border-${level.color} h-100 shadow-sm hover-lift`}>
                      <div className="card-body text-center p-4">
                        <div className={`level-icon bg-${level.color} text-white rounded-circle mx-auto mb-4`}>
                          <span className="fs-2">{level.icon}</span>
                        </div>
                        <h5 className={`card-title text-${level.color} fw-bold`}>{level.title}</h5>
                        <h6 className="card-subtitle mb-3 text-muted">{level.subtitle}</h6>
                        <p className="card-text text-muted mb-4">{level.description}</p>
                        
                        <div className="student-count mb-3">
                          <span className="badge bg-light text-dark">
                            <i className="bi bi-people me-1"></i> {level.studentCount} Students
                          </span>
                        </div>
                        
                        <div className="features-list">
                          {level.features.map((feature, idx) => (
                            <span key={idx} className="badge bg-light text-dark border me-1 mb-1">
                              {feature}
                            </span>
                          ))}
                        </div>
                        
                        <div className="mt-3">
                          <span className="text-primary small">
                            Learn more <i className="bi bi-arrow-right ms-1"></i>
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Latest News Section */}
        <section id="news" className="py-5 bg-white animate-on-scroll" aria-label="Latest news">
          <div className="container">
            <div className="text-center mb-5">
              <span className="badge bg-success mb-3">Updates</span>
              <h2 className="display-5 fw-bold text-primary mb-3">Latest News & Announcements</h2>
              <p className="lead text-muted">Stay informed about our school activities and achievements</p>
            </div>
            <div className="row g-4">
              {news.map((item) => (
                <div key={item.id} className="col-md-4">
                  <NewsCard item={item} onClick={handleNewsClick} />
                </div>
              ))}
            </div>
            <div className="text-center mt-4">
              <Link 
                to="/news" 
                className="btn btn-outline-primary"
                onClick={() => trackInteraction('view_all_news', 'home_page')}
              >
                View All News <i className="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>
          </div>
        </section>

        {/* Upcoming Events Section */}
        {events.length > 0 && (
          <section id="events" className="py-5 bg-light animate-on-scroll" aria-label="Upcoming events">
            <div className="container">
              <div className="text-center mb-5">
                <span className="badge bg-warning mb-3">Events</span>
                <h2 className="display-5 fw-bold text-primary mb-3">Upcoming Events</h2>
                <p className="lead text-muted">Join us for these exciting upcoming activities</p>
              </div>
              <div className="row g-4">
                {events.slice(0, 3).map((event) => (
                  <div key={event.id} className="col-md-4">
                    <div className="card event-card h-100 shadow-sm hover-lift">
                      <div className="card-body">
                        <div className="d-flex align-items-center mb-3">
                          <div className="date-box bg-primary text-white text-center rounded p-3 me-3">
                            <div className="fs-4 fw-bold">{new Date(event.date).getDate()}</div>
                            <div className="small">{new Date(event.date).toLocaleString('default', { month: 'short' })}</div>
                          </div>
                          <div>
                            <h5 className="card-title mb-1">{event.title}</h5>
                            <p className="text-muted small mb-0">
                              <i className="bi bi-clock me-1"></i> {event.time}
                            </p>
                          </div>
                        </div>
                        <p className="card-text text-muted">{event.description}</p>
                        <div className="d-flex justify-content-between align-items-center">
                          <span className="badge bg-light text-dark">{event.category}</span>
                          <span className="text-muted small">
                            <i className="bi bi-geo-alt me-1"></i> {event.location}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="text-center mt-4">
                <Link 
                  to="/events" 
                  className="btn btn-outline-primary"
                  onClick={() => trackInteraction('view_all_events', 'home_page')}
                >
                  View Calendar <i className="bi bi-calendar ms-1"></i>
                </Link>
              </div>
            </div>
          </section>
        )}

        {/* Enhanced Call to Action */}
        <section id="cta" className="py-5 bg-primary text-white animate-on-scroll" aria-label="Call to action">
          <div className="container">
            <div className="row align-items-center">
              <div className="col-lg-8 mx-auto text-center">
                <h2 className="display-6 fw-bold mb-3">Ready to Join Our Community?</h2>
                <p className="lead mb-4 opacity-75">
                  Take the first step towards quality education and holistic development for your child. 
                  Limited spots available for {new Date().getFullYear() + 1} intake.
                </p>
                <div className="d-flex flex-wrap gap-3 justify-content-center">
                  <Link 
                    to="/admissions" 
                    className="btn btn-light btn-lg px-4 fw-bold"
                    onClick={() => trackInteraction('cta_click', 'apply_now_main')}
                  >
                    Apply Now
                  </Link>
                  <Link 
                    to="/contact" 
                    className="btn btn-outline-light btn-lg px-4"
                    onClick={() => trackInteraction('cta_click', 'schedule_visit_main')}
                  >
                    Schedule Visit
                  </Link>
                  <button 
                    className="btn btn-outline-light btn-lg px-4"
                    onClick={() => {
                      trackInteraction('cta_click', 'download_brochure');
                      // Implement brochure download
                      window.open('/downloads/brochure.pdf', '_blank');
                    }}
                  >
                    Download Brochure
                  </button>
                  <button 
                    className="btn btn-outline-light btn-lg px-4"
                    onClick={() => {
                      trackInteraction('cta_click', 'virtual_tour');
                      navigate('/virtual-tour');
                    }}
                  >
                    <i className="bi bi-play-circle me-2"></i> Virtual Tour
                  </button>
                </div>
                <p className="mt-4 small opacity-75">
                  <i className="bi bi-phone me-1"></i> Need help? Call us at +254 700 123 456
                </p>
              </div>
            </div>
          </div>
        </section>

        <style>{`
          .home-page {
            overflow-x: hidden;
          }
          
          .hero-banner {
            position: relative;
            height: 100vh;
            min-height: 600px;
            overflow: hidden;
          }
          
          .banner-slides {
            position: relative;
            height: 100%;
          }
          
          .banner-slide {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            transition: opacity 0.8s ease-in-out;
            display: flex;
            align-items: center;
          }
          
          .banner-slide.active {
            opacity: 1;
          }
          
          .video-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
          }
          
          .image-overlay {
            position: absolute;
            top: 0;
            left: 0;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            z-index: 1;
          }
          
          .slide-content {
            z-index: 2;
          }
          
          .video-container {
            width: 100%;
            height: 100%;
            overflow: hidden;
          }
          
          .video-banner {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: opacity 0.5s ease;
          }
          
          .video-placeholder, .image-placeholder {
            z-index: 1;
          }
          
          .min-vh-80 {
            min-height: 80vh;
          }
          
          .banner-control {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: none;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            transition: all 0.3s ease;
            z-index: 10;
            cursor: pointer;
          }
          
          .banner-control:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-50%) scale(1.1);
          }
          
          .banner-control.prev {
            left: 20px;
          }
          
          .banner-control.next {
            right: 20px;
          }
          
          .banner-dots {
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 12px;
            z-index: 10;
          }
          
          .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid white;
            background: transparent;
            cursor: pointer;
            transition: all 0.3s ease;
            padding: 0;
          }
          
          .dot.active {
            background: white;
            transform: scale(1.2);
          }
          
          .banner-progress {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: rgba(255, 255, 255, 0.2);
            z-index: 10;
          }
          
          .banner-progress .progress-bar {
            height: 100%;
            background: white;
            transition: width 0.3s ease;
          }
          
          .stat-card, .level-card, .news-card, .event-card {
            transition: all 0.3s ease;
            cursor: pointer;
          }
          
          .hover-lift:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15) !important;
          }
          
          .level-icon {
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s ease;
          }
          
          .level-card:hover .level-icon {
            transform: scale(1.1);
          }
          
          .date-box {
            min-width: 70px;
          }
          
          .animate-on-scroll {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.8s ease;
          }
          
          .animate-on-scroll.visible {
            opacity: 1;
            transform: translateY(0);
          }
          
          .transition-opacity {
            transition: opacity 0.3s ease;
          }
          
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
          }
          
          .animate-fade-in {
            animation: fadeIn 1s ease-out;
          }
          
          .animate-fade-in-delay {
            animation: fadeIn 1s ease-out 0.3s both;
          }
          
          .animate-bounce-in {
            animation: fadeIn 1s ease-out 0.6s both;
          }
          
          @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
          }
          
          .pulse-animation {
            animation: pulse 2s infinite;
          }
          
          @media (max-width: 768px) {
            .hero-banner {
              height: 70vh;
              min-height: 500px;
            }
            
            .display-3 {
              font-size: 2.5rem;
            }
            
            .lead.fs-3 {
              font-size: 1.25rem !important;
            }
            
            .banner-control {
              width: 50px;
              height: 50px;
              font-size: 1.25rem;
            }
            
            .banner-control.prev {
              left: 10px;
            }
            
            .banner-control.next {
              right: 10px;
            }
            
            .banner-dots {
              bottom: 20px;
            }
            
            .quick-stats .col-md-4 {
              margin-bottom: 1rem;
            }
          }
          
          @media (max-width: 576px) {
            .hero-banner {
              height: 60vh;
              min-height: 400px;
            }
            
            .display-3 {
              font-size: 2rem;
            }
            
            .lead.fs-3 {
              font-size: 1.1rem !important;
            }
            
            .btn-lg {
              padding: 0.75rem 1.5rem;
              font-size: 1rem;
            }
            
            .banner-control {
              width: 40px;
              height: 40px;
              font-size: 1rem;
            }
          }
          
          /* Accessibility improvements */
          .stat-card:focus,
          .level-card:focus,
          .news-card:focus,
          .event-card:focus {
            outline: 3px solid #4d90fe;
            outline-offset: 2px;
          }
          
          /* Reduced motion preferences */
          @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
              animation-duration: 0.01ms !important;
              animation-iteration-count: 1 !important;
              transition-duration: 0.01ms !important;
            }
            
            .animate-on-scroll {
              opacity: 1;
              transform: none;
            }
            
            .hover-lift:hover {
              transform: none;
            }
          }
        `}</style>
      </div>
    </ErrorBoundary>
  );
}

export default Home;