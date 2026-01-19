// src/pages/Resource_mngt/Calendar.jsx - COMPLETE FIXED VERSION
import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {academicsAPI} from '../../services/academicAPI';
import userAPI from '../../services/userAPI';
import { 
  CalendarIcon,
  ClockIcon,
  PersonIcon,
  BookIcon,
  HomeIcon,
  SchoolIcon,
  UsersIcon,
  BellIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FilterIcon,
  DownloadIcon,
  PrintIcon
} from '../../components/Icons';

const Calendar = () => {
  const { currentUser, isAuthenticated, hasRole, loading: authLoading } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('month'); // 'month', 'week', 'day'
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'academic', 'events', 'personal'

  useEffect(() => {
    if (isAuthenticated && currentUser) {
      fetchCalendarEvents();
    }
  }, [currentDate, filter, isAuthenticated, currentUser]);

  // Redirect to login if not authenticated
  if (!authLoading && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Show loading while authentication is being checked
  if (authLoading || !currentUser) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3">Loading calendar...</p>
        </div>
      </div>
    );
  }

  const fetchCalendarEvents = async () => {
    try {
      setLoading(true);
      
      // Example of using userAPI (if needed)
      // const userProfile = await userAPI.getCurrentUser();
      // console.log('User profile:', userProfile);
      
      // This would typically come from your API
      const mockEvents = [
        {
          id: 1,
          title: 'Parent-Teacher Conference',
          type: 'academic',
          date: new Date(new Date().getFullYear(), new Date().getMonth(), 15),
          time: '14:00',
          duration: 60,
          location: 'School Main Hall',
          description: 'Quarterly parent-teacher meetings',
          participants: ['All Parents', 'Teachers'],
          color: 'primary'
        },
        {
          id: 2,
          title: 'Science Fair',
          type: 'events',
          date: new Date(new Date().getFullYear(), new Date().getMonth(), 20),
          time: '09:00',
          duration: 180,
          location: 'Science Building',
          description: 'Annual science fair exhibition',
          participants: ['Students', 'Parents', 'Teachers'],
          color: 'success'
        },
        {
          id: 3,
          title: 'Sports Day',
          type: 'events',
          date: new Date(new Date().getFullYear(), new Date().getMonth(), 25),
          time: '08:00',
          duration: 240,
          location: 'Sports Ground',
          description: 'Inter-class sports competition',
          participants: ['All Students'],
          color: 'warning'
        },
        {
          id: 4,
          title: 'End of Term Exams',
          type: 'academic',
          date: new Date(new Date().getFullYear(), new Date().getMonth(), 28),
          time: '08:30',
          duration: 90,
          location: 'Classrooms',
          description: 'Final examinations for the term',
          participants: ['All Students'],
          color: 'danger'
        },
        {
          id: 5,
          title: 'Staff Meeting',
          type: 'academic',
          date: new Date(new Date().getFullYear(), new Date().getMonth(), 5),
          time: '15:00',
          duration: 90,
          location: 'Staff Room',
          description: 'Monthly staff development meeting',
          participants: ['Teaching Staff'],
          color: 'info'
        }
      ];

      // Filter events based on selected filter
      const filteredEvents = filter === 'all' 
        ? mockEvents 
        : mockEvents.filter(event => event.type === filter);

      setEvents(filteredEvents);
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigateDate = (direction) => {
    const newDate = new Date(currentDate);
    if (view === 'month') {
      newDate.setMonth(newDate.getMonth() + direction);
    } else if (view === 'week') {
      newDate.setDate(newDate.getDate() + (direction * 7));
    } else {
      newDate.setDate(newDate.getDate() + direction);
    }
    setCurrentDate(newDate);
  };

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const getMonthName = (date) => {
    return date.toLocaleString('default', { month: 'long', year: 'numeric' });
  };

  const getEventsForDay = (day) => {
    return events.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.getDate() === day &&
             eventDate.getMonth() === currentDate.getMonth() &&
             eventDate.getFullYear() === currentDate.getFullYear();
    });
  };

  const renderMonthView = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    // Add cells for each day of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const dayEvents = getEventsForDay(day);
      const isToday = new Date().getDate() === day && 
                     new Date().getMonth() === currentDate.getMonth() && 
                     new Date().getFullYear() === currentDate.getFullYear();

      days.push(
        <div 
          key={day} 
          className={`calendar-day ${isToday ? 'today' : ''}`}
          onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth(), day))}
        >
          <div className="day-number">{day}</div>
          <div className="day-events">
            {dayEvents.slice(0, 2).map(event => (
              <div 
                key={event.id} 
                className={`event-dot bg-${event.color}`}
                title={event.title}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedEvent(event);
                }}
              ></div>
            ))}
            {dayEvents.length > 2 && (
              <div className="more-events">+{dayEvents.length - 2} more</div>
            )}
          </div>
        </div>
      );
    }

    return days;
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3">Loading calendar events...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h2 mb-2">
            <CalendarIcon className="me-2" />
            School Calendar
          </h1>
          <p className="lead text-muted mb-0">
            Welcome, {currentUser.first_name || currentUser.firstName || 'User'}! Stay updated with academic events and activities
          </p>
        </div>
        <div className="d-flex gap-2">
          <button className="btn btn-outline-secondary">
            <PrintIcon className="me-2" />
            Print
          </button>
          <button className="btn btn-outline-secondary">
            <DownloadIcon className="me-2" />
            Export
          </button>
          <Link to="/events" className="btn btn-primary">
            <PlusIcon className="me-2" />
            View All Events
          </Link>
        </div>
      </div>

      <div className="row">
        {/* Main Calendar */}
        <div className="col-lg-9">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-0 py-3">
              <div className="d-flex justify-content-between align-items-center">
                <div className="d-flex align-items-center gap-3">
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => navigateDate(-1)}
                  >
                    <ChevronLeftIcon />
                  </button>
                  <h4 className="mb-0 fw-semibold">{getMonthName(currentDate)}</h4>
                  <button 
                    className="btn btn-outline-secondary"
                    onClick={() => navigateDate(1)}
                  >
                    <ChevronRightIcon />
                  </button>
                  <button 
                    className="btn btn-outline-primary"
                    onClick={() => setCurrentDate(new Date())}
                  >
                    Today
                  </button>
                </div>
                <div className="d-flex gap-2">
                  <select 
                    className="form-select"
                    value={view}
                    onChange={(e) => setView(e.target.value)}
                  >
                    <option value="month">Month</option>
                    <option value="week">Week</option>
                    <option value="day">Day</option>
                  </select>
                  <div className="dropdown">
                    <button 
                      className="btn btn-outline-secondary dropdown-toggle"
                      type="button"
                      data-bs-toggle="dropdown"
                    >
                      <FilterIcon className="me-2" />
                      Filter
                    </button>
                    <ul className="dropdown-menu">
                      <li>
                        <button 
                          className={`dropdown-item ${filter === 'all' ? 'active' : ''}`}
                          onClick={() => setFilter('all')}
                        >
                          All Events
                        </button>
                      </li>
                      <li>
                        <button 
                          className={`dropdown-item ${filter === 'academic' ? 'active' : ''}`}
                          onClick={() => setFilter('academic')}
                        >
                          Academic
                        </button>
                      </li>
                      <li>
                        <button 
                          className={`dropdown-item ${filter === 'events' ? 'active' : ''}`}
                          onClick={() => setFilter('events')}
                        >
                          School Events
                        </button>
                      </li>
                      <li>
                        <button 
                          className={`dropdown-item ${filter === 'personal' ? 'active' : ''}`}
                          onClick={() => setFilter('personal')}
                        >
                          Personal
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div className="card-body">
              {/* Day headers */}
              <div className="calendar-header">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="calendar-day-header">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar grid */}
              <div className="calendar-grid">
                {renderMonthView()}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="col-lg-3">
          {/* Upcoming Events */}
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold">
                <BellIcon className="me-2" />
                Upcoming Events
              </h5>
            </div>
            <div className="card-body">
              {events
                .filter(event => new Date(event.date) >= new Date())
                .sort((a, b) => new Date(a.date) - new Date(b.date))
                .slice(0, 5)
                .map(event => (
                  <div key={event.id} className="mb-3 pb-3 border-bottom">
                    <div className="d-flex justify-content-between align-items-start mb-1">
                      <h6 className="mb-0 fw-semibold">{event.title}</h6>
                      <span className={`badge bg-${event.color}`}>
                        {event.type}
                      </span>
                    </div>
                    <div className="d-flex align-items-center text-muted small mb-1">
                      <CalendarIcon size={12} className="me-1" />
                      {new Date(event.date).toLocaleDateString()}
                    </div>
                    <div className="d-flex align-items-center text-muted small">
                      <ClockIcon size={12} className="me-1" />
                      {event.time} • {event.location}
                    </div>
                  </div>
                ))}
              {events.filter(event => new Date(event.date) >= new Date()).length === 0 && (
                <div className="text-center py-3">
                  <p className="text-muted mb-0">No upcoming events</p>
                </div>
              )}
            </div>
          </div>

          {/* Event Types Legend */}
          <div className="card shadow-sm border-0">
            <div className="card-header bg-white border-0 py-3">
              <h5 className="mb-0 fw-semibold">Event Types</h5>
            </div>
            <div className="card-body">
              <div className="d-flex flex-column gap-2">
                <div className="d-flex align-items-center">
                  <div className="event-legend-dot bg-primary me-2"></div>
                  <small>Academic Events</small>
                </div>
                <div className="d-flex align-items-center">
                  <div className="event-legend-dot bg-success me-2"></div>
                  <small>School Events</small>
                </div>
                <div className="d-flex align-items-center">
                  <div className="event-legend-dot bg-warning me-2"></div>
                  <small>Sports & Activities</small>
                </div>
                <div className="d-flex align-items-center">
                  <div className="event-legend-dot bg-danger me-2"></div>
                  <small>Exams & Tests</small>
                </div>
                <div className="d-flex align-items-center">
                  <div className="event-legend-dot bg-info me-2"></div>
                  <small>Meetings</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Event Modal */}
      {selectedEvent && (
        <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{selectedEvent.title}</h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={() => setSelectedEvent(null)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="row">
                  <div className="col-12">
                    <p>{selectedEvent.description}</p>
                  </div>
                  <div className="col-6">
                    <strong>Date:</strong>
                    <p>{new Date(selectedEvent.date).toLocaleDateString()}</p>
                  </div>
                  <div className="col-6">
                    <strong>Time:</strong>
                    <p>{selectedEvent.time} ({selectedEvent.duration} mins)</p>
                  </div>
                  <div className="col-12">
                    <strong>Location:</strong>
                    <p>{selectedEvent.location}</p>
                  </div>
                  <div className="col-12">
                    <strong>Participants:</strong>
                    <p>{selectedEvent.participants.join(', ')}</p>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setSelectedEvent(null)}
                >
                  Close
                </button>
                <button type="button" className="btn btn-primary">
                  Add to My Calendar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Custom CSS */}
      <style jsx>{`
        .calendar-header {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          gap: 1px;
          background-color: #e9ecef;
          border: 1px solid #dee2e6;
        }

        .calendar-day-header {
          padding: 10px;
          text-align: center;
          font-weight: 600;
          background-color: #f8f9fa;
        }

        .calendar-grid {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          gap: 1px;
          background-color: #e9ecef;
          border: 1px solid #dee2e6;
          border-top: none;
        }

        .calendar-day {
          min-height: 120px;
          padding: 8px;
          background-color: white;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .calendar-day:hover {
          background-color: #f8f9fa;
        }

        .calendar-day.today {
          background-color: #e7f1ff;
        }

        .calendar-day.empty {
          background-color: #f8f9fa;
          cursor: default;
        }

        .day-number {
          font-weight: 600;
          margin-bottom: 5px;
        }

        .event-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-bottom: 2px;
          cursor: pointer;
        }

        .more-events {
          font-size: 0.75rem;
          color: #6c757d;
          margin-top: 2px;
        }

        .event-legend-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }
      `}</style>
    </div>
  );
};

export default Calendar;