import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { eventAPI } from '../services/eventAPI';
import { useNavigate } from 'react-router-dom';

function Events() {
  const [filter, setFilter] = useState('all');
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    total: 0,
    page_size: 12
  });
  const [sortBy, setSortBy] = useState('start_date');
  const [sortOrder, setSortOrder] = useState('asc');
  const [registrationLoading, setRegistrationLoading] = useState({});
  
  const { isAuthenticated, currentUser, hasPermission } = useAuth();
  const navigate = useNavigate();

  // Enhanced event types with better visuals
  const EVENT_TYPES = {
    academic: { label: 'Academic', color: 'primary', icon: '📚', gradient: 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)' },
    sports: { label: 'Sports', color: 'success', icon: '⚽', gradient: 'linear-gradient(135deg, #28a745 0%, #1e7e34 100%)' },
    cultural: { label: 'Cultural', color: 'warning', icon: '🎭', gradient: 'linear-gradient(135deg, #ffc107 0%, #e0a800 100%)' },
    community: { label: 'Community', color: 'info', icon: '🤝', gradient: 'linear-gradient(135deg, #17a2b8 0%, #138496 100%)' },
    holiday: { label: 'Holiday', color: 'danger', icon: '🎉', gradient: 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)' },
    workshop: { label: 'Workshop', color: 'secondary', icon: '🔧', gradient: 'linear-gradient(135deg, #6c757d 0%, #545b62 100%)' },
    meeting: { label: 'Meeting', color: 'dark', icon: '👥', gradient: 'linear-gradient(135deg, #343a40 0%, #23272b 100%)' },
    celebration: { label: 'Celebration', color: 'warning', icon: '🎊', gradient: 'linear-gradient(135deg, #ffc107 0%, #e0a800 100%)' },
    competition: { label: 'Competition', color: 'success', icon: '🏆', gradient: 'linear-gradient(135deg, #28a745 0%, #1e7e34 100%)' },
    field_trip: { label: 'Field Trip', color: 'info', icon: '🚌', gradient: 'linear-gradient(135deg, #17a2b8 0%, #138496 100%)' }
  };

  // Fetch events from backend API
  useEffect(() => {
    fetchEvents();
  }, [filter, pagination.current, sortBy, sortOrder]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: pagination.current,
        page_size: pagination.page_size,
        ordering: sortOrder === 'desc' ? `-${sortBy}` : sortBy
      };

      let result;
      switch (filter) {
        case 'upcoming':
          result = await eventAPI.getUpcomingEvents(params);
          break;
        case 'ongoing':
          result = await eventAPI.getOngoingEvents(params);
          break;
        case 'past':
          result = await eventAPI.getPastEvents(params);
          break;
        case 'featured':
          result = await eventAPI.getFeaturedEvents(params);
          break;
        default:
          if (filter !== 'all') {
            params.event_type = filter;
          }
          result = await eventAPI.getEvents(params);
      }

      if (result.success) {
        setEvents(result.data.results || result.data);
        // Handle pagination metadata
        if (result.data.count !== undefined) {
          setPagination(prev => ({
            ...prev,
            total: Math.ceil(result.data.count / prev.page_size)
          }));
        }
      } else {
        setError(result.error.message || 'Failed to load events');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  // Enhanced search with debouncing
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm.trim()) {
        handleSearch();
      } else if (searchTerm === '') {
        fetchEvents();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      fetchEvents();
      return;
    }

    try {
      setLoading(true);
      const result = await eventAPI.searchEvents(searchTerm);
      if (result.success) {
        setEvents(result.data.results || result.data);
        setPagination(prev => ({ ...prev, current: 1 }));
      } else {
        setError(result.error.message || 'Search failed');
      }
    } catch (err) {
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEventClick = (event) => {
    if (isAuthenticated) {
      navigate(`/events/${event.id}`);
    } else {
      setSelectedEvent(event);
      setShowModal(true);
    }
  };

  const handleRegister = async (eventId) => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/events' } });
      return;
    }

    setRegistrationLoading(prev => ({ ...prev, [eventId]: true }));

    try {
      const result = await eventAPI.registerForEvent(eventId);
      if (result.success) {
        // Show success notification
        showNotification('Successfully registered for the event!', 'success');
        fetchEvents(); // Refresh events to update registration counts
      } else {
        showNotification(result.error.message || 'Registration failed', 'error');
      }
    } catch (err) {
      showNotification('Registration failed. Please try again.', 'error');
    } finally {
      setRegistrationLoading(prev => ({ ...prev, [eventId]: false }));
    }
  };

  const showNotification = (message, type = 'info') => {
    // You can integrate with a proper notification system here
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-info';
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 5000);
  };

  const getEventStatus = (event) => {
    const now = new Date();
    const startDate = new Date(event.start_date);
    const endDate = new Date(event.end_date);

    if (now < startDate) return 'upcoming';
    if (now >= startDate && now <= endDate) return 'ongoing';
    return 'past';
  };

  const isEventFull = (event) => {
    return event.max_participants && event.registered_count >= event.max_participants;
  };

  const canRegister = (event) => {
    return event.requires_registration && 
           getEventStatus(event) === 'upcoming' && 
           !isEventFull(event) &&
           event.is_published &&
           !event.is_cancelled;
  };

  const formatDate = (dateString, options = {}) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      ...options
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getEventImage = (event) => {
    // Use event-specific placeholder based on type
    const placeholderImages = {
      academic: 'https://images.unsplash.com/photo-1588072432836-e100327d50ab?w=400&h=200&fit=crop',
      sports: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=200&fit=crop',
      cultural: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400&h=200&fit=crop',
      community: 'https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=400&h=200&fit=crop',
      workshop: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=200&fit=crop',
      meeting: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=200&fit=crop',
      celebration: 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400&h=200&fit=crop',
      competition: 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&h=200&fit=crop',
      field_trip: 'https://images.unsplash.com/photo-1527631746610-bca00a040d60?w=400&h=200&fit=crop'
    };
    
    return event.image || event.banner_image || placeholderImages[event.event_type] || 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=400&h=200&fit=crop';
  };

  const handlePageChange = (page) => {
    setPagination(prev => ({ ...prev, current: page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSortChange = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  const exportEvents = async () => {
    try {
      const result = await eventAPI.exportEvents();
      if (result.success) {
        // Create download link
        const url = window.URL.createObjectURL(new Blob([result.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `delvok-events-${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      showNotification('Failed to export events', 'error');
    }
  };

  if (loading && events.length === 0) {
    return (
      <div className="events-page">
        <div className="container py-5">
          <div className="text-center">
            <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
              <span className="visually-hidden">Loading events...</span>
            </div>
            <p className="mt-3 fs-5">Loading exciting events...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="events-page">
      {/* Enhanced Hero Section */}
      <section className="events-hero text-white py-5 position-relative overflow-hidden">
        <div 
          className="position-absolute top-0 start-0 w-100 h-100"
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            zIndex: -1
          }}
        ></div>
        <div className="container position-relative">
          <div className="row align-items-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-3">Delvok Academy Events</h1>
              <p className="lead fs-4 mb-4">
                Discover, Learn, and Grow Through Our Diverse Programs
              </p>
              <div className="d-flex flex-wrap gap-3">
                {isAuthenticated && hasPermission('events.create') && (
                  <button 
                    className="btn btn-light btn-lg shadow"
                    onClick={() => navigate('/events/create')}
                  >
                    <i className="bi bi-plus-circle me-2"></i>
                    Create New Event
                  </button>
                )}
                {hasPermission('events.export') && (
                  <button 
                    className="btn btn-outline-light btn-lg"
                    onClick={exportEvents}
                  >
                    <i className="bi bi-download me-2"></i>
                    Export Events
                  </button>
                )}
              </div>
            </div>
            <div className="col-lg-4 text-center">
              <div className="hero-icon display-1">🎓</div>
            </div>
          </div>
        </div>
      </section>

      {/* Enhanced Controls Section */}
      <section className="py-4 bg-white border-bottom">
        <div className="container">
          <div className="row g-3 align-items-center">
            {/* Search Bar */}
            <div className="col-md-5">
              <div className="input-group input-group-lg">
                <span className="input-group-text bg-light border-end-0">
                  <i className="bi bi-search text-muted"></i>
                </span>
                <input
                  type="text"
                  className="form-control border-start-0"
                  placeholder="Search events by title, description, or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Sort Controls */}
            <div className="col-md-3">
              <div className="dropdown">
                <button className="btn btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                  <i className="bi bi-sort-down me-2"></i>
                  Sort: {sortBy.replace('_', ' ')} {getSortIcon(sortBy)}
                </button>
                <ul className="dropdown-menu">
                  <li>
                    <button className="dropdown-item" onClick={() => handleSortChange('start_date')}>
                      Date {getSortIcon('start_date')}
                    </button>
                  </li>
                  <li>
                    <button className="dropdown-item" onClick={() => handleSortChange('title')}>
                      Title {getSortIcon('title')}
                    </button>
                  </li>
                  <li>
                    <button className="dropdown-item" onClick={() => handleSortChange('priority')}>
                      Priority {getSortIcon('priority')}
                    </button>
                  </li>
                </ul>
              </div>
            </div>

            {/* View Toggle */}
            <div className="col-md-2">
              <div className="btn-group w-100" role="group">
                <button
                  type="button"
                  className={`btn ${viewMode === 'grid' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setViewMode('grid')}
                  title="Grid View"
                >
                  <i className="bi bi-grid-3x3-gap"></i>
                </button>
                <button
                  type="button"
                  className={`btn ${viewMode === 'calendar' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setViewMode('calendar')}
                  title="Calendar View"
                >
                  <i className="bi bi-calendar-week"></i>
                </button>
              </div>
            </div>

            {/* Results Count */}
            <div className="col-md-2 text-end">
              <span className="text-muted fw-semibold">
                {events.length} {events.length === 1 ? 'event' : 'events'}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Enhanced Events Filter */}
      <section className="py-3 bg-light">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="d-flex flex-wrap gap-2 justify-content-center">
                <button
                  className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'} rounded-pill`}
                  onClick={() => setFilter('all')}
                >
                  All Events
                </button>
                <button
                  className={`btn ${filter === 'upcoming' ? 'btn-success' : 'btn-outline-success'} rounded-pill`}
                  onClick={() => setFilter('upcoming')}
                >
                  <i className="bi bi-arrow-up-circle me-1"></i>Upcoming
                </button>
                <button
                  className={`btn ${filter === 'ongoing' ? 'btn-warning' : 'btn-outline-warning'} rounded-pill`}
                  onClick={() => setFilter('ongoing')}
                >
                  <i className="bi bi-play-circle me-1"></i>Ongoing
                </button>
                <button
                  className={`btn ${filter === 'past' ? 'btn-secondary' : 'btn-outline-secondary'} rounded-pill`}
                  onClick={() => setFilter('past')}
                >
                  <i className="bi bi-check-circle me-1"></i>Past
                </button>
                <button
                  className={`btn ${filter === 'featured' ? 'btn-danger' : 'btn-outline-danger'} rounded-pill`}
                  onClick={() => setFilter('featured')}
                >
                  <i className="bi bi-star me-1"></i>Featured
                </button>
                
                {/* Event Type Filters */}
                {Object.entries(EVENT_TYPES).map(([type, config]) => (
                  <button
                    key={type}
                    className={`btn ${filter === type ? `btn-${config.color}` : `btn-outline-${config.color}`} rounded-pill`}
                    onClick={() => setFilter(type)}
                    title={config.label}
                  >
                    {config.icon} 
                    <span className="d-none d-md-inline"> {config.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Enhanced Error Display */}
      {error && (
        <div className="container mt-4">
          <div className="alert alert-danger alert-dismissible fade show d-flex align-items-center" role="alert">
            <i className="bi bi-exclamation-triangle-fill me-2 fs-5"></i>
            <div className="flex-grow-1">{error}</div>
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => setError(null)}
            ></button>
          </div>
        </div>
      )}

      {/* Enhanced Events Grid */}
      <section className="py-5">
        <div className="container">
          {viewMode === 'grid' ? (
            <>
              <div className="row g-4">
                {events.map(event => {
                  const eventType = EVENT_TYPES[event.event_type] || EVENT_TYPES.academic;
                  const status = getEventStatus(event);
                  const isFull = isEventFull(event);
                  const isRegistering = registrationLoading[event.id];
                  
                  return (
                    <div key={event.id} className="col-md-6 col-lg-4 col-xl-3">
                      <div className="card event-card h-100 shadow-sm border-0 overflow-hidden">
                        <div className="event-image position-relative overflow-hidden">
                          <img 
                            src={getEventImage(event)} 
                            alt={event.title}
                            className="card-img-top event-image"
                            style={{ height: '200px', objectFit: 'cover' }}
                            loading="lazy"
                          />
                          
                          {/* Enhanced Event Badges */}
                          <div className="event-badges position-absolute top-0 start-0 m-3 d-flex flex-column gap-1">
                            {event.is_featured && (
                              <span className="badge bg-danger bg-opacity-90">
                                <i className="bi bi-star-fill me-1"></i>Featured
                              </span>
                            )}
                            {event.is_cancelled && (
                              <span className="badge bg-dark bg-opacity-90">
                                <i className="bi bi-x-circle me-1"></i>Cancelled
                              </span>
                            )}
                            {event.has_fee && (
                              <span className="badge bg-warning text-dark bg-opacity-90">
                                <i className="bi bi-currency-dollar me-1"></i>Paid
                              </span>
                            )}
                          </div>
                          
                          {/* Event Type Badge */}
                          <div className="event-badge position-absolute top-0 end-0 m-3">
                            <span 
                              className="badge text-white border-0"
                              style={{ background: eventType.gradient }}
                            >
                              {eventType.icon} {eventType.label}
                            </span>
                          </div>

                          {/* Status Badge */}
                          <div className="position-absolute bottom-0 start-0 m-3">
                            <span className={`badge bg-${status === 'upcoming' ? 'success' : status === 'ongoing' ? 'warning' : 'secondary'} bg-opacity-90`}>
                              <i className={`bi bi-${status === 'upcoming' ? 'clock' : status === 'ongoing' ? 'play-circle' : 'check-circle'} me-1`}></i>
                              {status.charAt(0).toUpperCase() + status.slice(1)}
                            </span>
                          </div>

                          {/* Image Overlay on Hover */}
                          <div className="event-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center opacity-0">
                            <button 
                              className="btn btn-light btn-sm rounded-pill shadow"
                              onClick={() => handleEventClick(event)}
                            >
                              <i className="bi bi-eye me-1"></i>Quick View
                            </button>
                          </div>
                        </div>

                        <div className="card-body d-flex flex-column">
                          <div className="event-date text-muted small mb-2">
                            <i className="bi bi-calendar3 me-1"></i>
                            {formatDate(event.start_date)}
                          </div>
                          
                          <h5 className="card-title text-dark mb-2 line-clamp-2" style={{ minHeight: '3rem' }}>
                            {event.title}
                          </h5>
                          
                          <p className="card-text text-muted flex-grow-1 line-clamp-3">
                            {event.short_description || event.description?.substring(0, 120)}
                            {event.description?.length > 120 && '...'}
                          </p>
                          
                          <div className="event-meta mb-3">
                            <div className="event-location text-muted small mb-1">
                              <i className="bi bi-geo-alt me-1"></i>
                              {event.location}
                              {event.is_online && ' • Online'}
                              {event.is_hybrid && ' • Hybrid'}
                            </div>
                            
                            <div className="event-time text-muted small">
                              <i className="bi bi-clock me-1"></i>
                              {formatTime(event.start_date)} - {formatTime(event.end_date)}
                            </div>
                          </div>

                          {/* Enhanced Registration Info */}
                          {event.requires_registration && (
                            <div className="registration-info mb-3">
                              <div className="d-flex justify-content-between align-items-center mb-2">
                                <small className="text-muted">
                                  <i className="bi bi-people me-1"></i>
                                  {event.registered_count || 0} registered
                                  {event.max_participants && ` / ${event.max_participants}`}
                                </small>
                                {isFull && (
                                  <span className="badge bg-danger">
                                    <i className="bi bi-exclamation-triangle me-1"></i>Full
                                  </span>
                                )}
                              </div>
                              {event.max_participants && (
                                <div className="progress" style={{ height: '6px' }}>
                                  <div 
                                    className="progress-bar" 
                                    style={{ 
                                      width: `${Math.min(100, ((event.registered_count || 0) / event.max_participants) * 100)}%` 
                                    }}
                                  ></div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        <div className="card-footer bg-transparent border-0 pt-0">
                          <div className="d-flex gap-2">
                            <button 
                              className="btn btn-outline-primary btn-sm flex-fill"
                              onClick={() => handleEventClick(event)}
                            >
                              <i className="bi bi-info-circle me-1"></i>Details
                            </button>
                            
                            {canRegister(event) && (
                              <button 
                                className="btn btn-primary btn-sm position-relative"
                                onClick={() => handleRegister(event.id)}
                                disabled={isRegistering}
                              >
                                {isRegistering ? (
                                  <>
                                    <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                                    Registering...
                                  </>
                                ) : (
                                  <>
                                    <i className="bi bi-plus-circle me-1"></i>Register
                                  </>
                                )}
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Enhanced No Events Found */}
              {events.length === 0 && !loading && (
                <div className="text-center py-5">
                  <div className="empty-state">
                    <i className="bi bi-calendar-x display-1 text-muted mb-3"></i>
                    <h3 className="text-muted mb-3">No events found</h3>
                    <p className="text-muted mb-4">
                      {searchTerm ? 'Try adjusting your search terms or browse all events.' : 'Try selecting a different filter category.'}
                    </p>
                    {(searchTerm || filter !== 'all') && (
                      <button 
                        className="btn btn-primary"
                        onClick={() => {
                          setSearchTerm('');
                          setFilter('all');
                        }}
                      >
                        <i className="bi bi-arrow-clockwise me-1"></i>Show All Events
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Enhanced Pagination */}
              {pagination.total > 1 && (
                <div className="d-flex justify-content-center mt-5">
                  <nav>
                    <ul className="pagination">
                      <li className={`page-item ${pagination.current === 1 ? 'disabled' : ''}`}>
                        <button 
                          className="page-link"
                          onClick={() => handlePageChange(pagination.current - 1)}
                          disabled={pagination.current === 1}
                        >
                          <i className="bi bi-chevron-left"></i> Previous
                        </button>
                      </li>
                      
                      {/* Show limited page numbers */}
                      {[...Array(Math.min(5, pagination.total))].map((_, i) => {
                        const pageNum = i + 1;
                        return (
                          <li key={pageNum} className={`page-item ${pagination.current === pageNum ? 'active' : ''}`}>
                            <button 
                              className="page-link"
                              onClick={() => handlePageChange(pageNum)}
                            >
                              {pageNum}
                            </button>
                          </li>
                        );
                      })}
                      
                      {pagination.total > 5 && (
                        <li className="page-item disabled">
                          <span className="page-link">...</span>
                        </li>
                      )}
                      
                      <li className={`page-item ${pagination.current === pagination.total ? 'disabled' : ''}`}>
                        <button 
                          className="page-link"
                          onClick={() => handlePageChange(pagination.current + 1)}
                          disabled={pagination.current === pagination.total}
                        >
                          Next <i className="bi bi-chevron-right"></i>
                        </button>
                      </li>
                    </ul>
                  </nav>
                </div>
              )}
            </>
          ) : (
            /* Enhanced Calendar View */
            <div className="card shadow-sm border-0">
              <div className="card-header bg-white border-0 py-3">
                <h5 className="mb-0">
                  <i className="bi bi-calendar-week me-2"></i>
                  Events Calendar View
                </h5>
              </div>
              <div className="card-body">
                <div className="table-responsive">
                  <table className="table table-hover align-middle">
                    <thead className="table-light">
                      <tr>
                        <th style={{ width: '20%' }}>
                          <button 
                            className="btn btn-sm btn-link text-decoration-none text-dark p-0"
                            onClick={() => handleSortChange('start_date')}
                          >
                            Date & Time {getSortIcon('start_date')}
                          </button>
                        </th>
                        <th style={{ width: '30%' }}>Event</th>
                        <th style={{ width: '15%' }}>Type</th>
                        <th style={{ width: '15%' }}>Location</th>
                        <th style={{ width: '10%' }}>Status</th>
                        <th style={{ width: '10%' }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {events.map(event => {
                        const eventType = EVENT_TYPES[event.event_type] || EVENT_TYPES.academic;
                        const status = getEventStatus(event);
                        
                        return (
                          <tr key={event.id} className="event-row">
                            <td>
                              <div className="d-flex flex-column">
                                <strong className="text-primary">{formatDate(event.start_date, { month: 'short', day: 'numeric' })}</strong>
                                <small className="text-muted">
                                  {formatTime(event.start_date)} - {formatTime(event.end_date)}
                                </small>
                              </div>
                            </td>
                            <td>
                              <div className="fw-semibold text-dark mb-1">{event.title}</div>
                              <small className="text-muted line-clamp-2">
                                {event.short_description || event.description?.substring(0, 60)}...
                              </small>
                            </td>
                            <td>
                              <span 
                                className="badge text-white border-0"
                                style={{ background: eventType.gradient }}
                              >
                                {eventType.icon} {eventType.label}
                              </span>
                            </td>
                            <td>
                              <div className="text-muted">
                                <i className="bi bi-geo-alt me-1"></i>
                                {event.location}
                              </div>
                            </td>
                            <td>
                              <span className={`badge bg-${status === 'upcoming' ? 'success' : status === 'ongoing' ? 'warning' : 'secondary'}`}>
                                {status.charAt(0).toUpperCase() + status.slice(1)}
                              </span>
                            </td>
                            <td>
                              <div className="d-flex gap-1">
                                <button 
                                  className="btn btn-outline-primary btn-sm"
                                  onClick={() => handleEventClick(event)}
                                  title="View Details"
                                >
                                  <i className="bi bi-eye"></i>
                                </button>
                                {canRegister(event) && (
                                  <button 
                                    className="btn btn-primary btn-sm"
                                    onClick={() => handleRegister(event.id)}
                                    title="Register"
                                  >
                                    <i className="bi bi-plus-circle"></i>
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Enhanced Event Details Modal */}
      {showModal && selectedEvent && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg modal-dialog-centered">
            <div className="modal-content border-0 shadow-lg">
              <div className="modal-header bg-primary text-white">
                <h5 className="modal-title">
                  <i className="bi bi-info-circle me-2"></i>
                  {selectedEvent.title}
                </h5>
                <button 
                  type="button" 
                  className="btn-close btn-close-white"
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="row">
                  <div className="col-md-6">
                    <img 
                      src={getEventImage(selectedEvent)} 
                      alt={selectedEvent.title}
                      className="img-fluid rounded mb-3"
                    />
                  </div>
                  <div className="col-md-6">
                    <p className="text-muted">{selectedEvent.description}</p>
                    <div className="event-details">
                      <p>
                        <strong><i className="bi bi-calendar3 me-2"></i>Date:</strong><br/>
                        {formatDate(selectedEvent.start_date)}
                      </p>
                      <p>
                        <strong><i className="bi bi-clock me-2"></i>Time:</strong><br/>
                        {formatTime(selectedEvent.start_date)} - {formatTime(selectedEvent.end_date)}
                      </p>
                      <p>
                        <strong><i className="bi bi-geo-alt me-2"></i>Location:</strong><br/>
                        {selectedEvent.location}
                        {selectedEvent.is_online && ' (Online Event)'}
                        {selectedEvent.is_hybrid && ' (Hybrid Event)'}
                      </p>
                      {selectedEvent.organizer && (
                        <p>
                          <strong><i className="bi bi-person me-2"></i>Organizer:</strong><br/>
                          {selectedEvent.organizer}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Close
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={() => {
                    setShowModal(false);
                    navigate('/login', { state: { from: '/events' } });
                  }}
                >
                  <i className="bi bi-box-arrow-in-right me-1"></i>
                  Login to Register
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .events-hero {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .event-card {
          transition: all 0.3s ease;
        }
        
        .event-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 12px 35px rgba(0,0,0,0.15) !important;
        }
        
        .event-image {
          transition: all 0.3s ease;
        }
        
        .event-card:hover .event-image {
          transform: scale(1.08);
        }
        
        .event-overlay {
          background: rgba(0,0,0,0.7);
          transition: opacity 0.3s ease;
        }
        
        .event-card:hover .event-overlay {
          opacity: 1;
        }
        
        .event-badges {
          z-index: 2;
        }
        
        .event-badge {
          z-index: 2;
        }
        
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        .line-clamp-3 {
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        .event-row:hover {
          background-color: #f8f9fa;
        }
        
        .empty-state {
          max-width: 400px;
          margin: 0 auto;
        }
        
        @media (max-width: 768px) {
          .events-hero h1 {
            font-size: 2.5rem;
          }
          
          .hero-icon {
            font-size: 3rem;
          }
        }
      `}</style>
    </div>
  );
}

export default Events;