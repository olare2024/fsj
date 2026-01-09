import React, { useState, useEffect, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import authAPI from '../services/authAPI';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout, isAuthenticated } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(true);
  const [scrolled, setScrolled] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [authState, setAuthState] = useState({
    isAuth: false,
    user: null,
    loading: true
  });

  // Sync with authAPI state
  useEffect(() => {
    const checkAuth = () => {
      const isAuth = authAPI.isAuthenticated();
      const user = authAPI.getStoredUser();
      setAuthState({
        isAuth,
        user,
        loading: false
      });
    };

    checkAuth();
    
    // Listen for auth changes
    const handleAuthChange = () => {
      checkAuth();
    };

    // You could implement a custom event system or use context
    window.addEventListener('storage', handleAuthChange);
    
    return () => {
      window.removeEventListener('storage', handleAuthChange);
    };
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      setScrolled(isScrolled);
    };

    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Mock search function
  const performSearch = useCallback(async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    const mockResults = [
      { type: 'page', title: 'About Delvok Academy', path: '/about', description: 'Learn about our school' },
      { type: 'page', title: 'Academic Programs', path: '/academics', description: 'Our curriculum and programs' },
      { type: 'teacher', title: 'Sarah Johnson', path: '/teachers', description: 'Science Teacher' },
      { type: 'student', title: 'John Student', path: '/students', description: 'Grade 10 Student' },
      { type: 'event', title: 'Science Fair 2024', path: '/events', description: 'Annual science exhibition' },
      { type: 'course', title: 'Mathematics Grade 10', path: '/courses', description: 'Advanced mathematics course' },
    ].filter(item => 
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.description.toLowerCase().includes(query.toLowerCase())
    );

    setSearchResults(mockResults);
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      performSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, performSearch]);

  const isActive = (path) => location.pathname === path;

  const closeNavbar = () => {
    setIsCollapsed(true);
    setActiveDropdown(null);
    setShowSearch(false);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleNavClick = () => {
    closeNavbar();
  };

  const toggleDropdown = (dropdown) => {
    setActiveDropdown(activeDropdown === dropdown ? null : dropdown);
  };

  const handleLogout = async () => {
    try {
      // Use authAPI logout
      const refreshToken = localStorage.getItem('refresh_token');
      const result = await authAPI.logout(refreshToken ? { refresh: refreshToken } : null);
      
      if (result.success) {
        console.log('✅ Logout successful:', result.message);
      } else {
        console.log('⚠️ Logout API failed, clearing locally');
      }
      
      // Navigate to home
      navigate('/');
      closeNavbar();
      
      // Dispatch auth change event
      window.dispatchEvent(new Event('authStateChanged'));
    } catch (error) {
      console.error('❌ Logout error:', error);
      // Still clear local storage and navigate
      authAPI.clearAuthData();
      navigate('/');
      closeNavbar();
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
      closeNavbar();
    }
  };

  const handleSearchResultClick = (result) => {
    navigate(result.path);
    closeNavbar();
  };

  const toggleSearch = () => {
    setShowSearch(!showSearch);
    if (!showSearch) {
      setTimeout(() => {
        document.getElementById('search-input')?.focus();
      }, 100);
    } else {
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  // Get user display name from authAPI
  const getUserDisplayName = () => {
    if (authState.user) {
      return authAPI.getDisplayName();
    }
    return currentUser?.firstName || 'User';
  };

  // Get user role from authAPI
  const getUserRole = () => {
    if (authState.user) {
      return authState.user.role || 'guest';
    }
    return currentUser?.role || 'guest';
  };

  // Get user email from authAPI
  const getUserEmail = () => {
    if (authState.user) {
      return authState.user.email || '';
    }
    return currentUser?.email || '';
  };

  // Check if user is authenticated (combine both sources)
  const isUserAuthenticated = () => {
    return authState.isAuth || isAuthenticated;
  };

  // Upper navbar items (Quick Access)
  const upperNavigation = [
    { path: '/', label: 'Home', icon: 'bi-house' },
    { path: '/about', label: 'About', icon: 'bi-info-circle' },
    { path: '/news', label: 'News', icon: 'bi-newspaper' },
    { path: '/events', label: 'Events', icon: 'bi-calendar-event' },
    { path: '/contact', label: 'Contact', icon: 'bi-telephone' }
  ];

  // Main navigation categories for lower navbar
  const academicNavigation = [
    { path: '/academics', label: 'Overview', icon: 'bi-mortarboard' },
    { path: '/curriculum', label: 'Curriculum', icon: 'bi-journal-text' },
    { path: '/programs', label: 'Programs', icon: 'bi-diagram-3' },
    { path: '/departments', label: 'Departments', icon: 'bi-building' },
    { path: '/courses', label: 'Courses', icon: 'bi-journal' },
    { path: '/faculty', label: 'Faculty', icon: 'bi-people' },
    { path: '/elementary-school', label: 'Elementary', icon: 'bi-pencil' },
    { path: '/middle-school', label: 'Middle School', icon: 'bi-book' },
    { path: '/high-school', label: 'High School', icon: 'bi-laptop' },
    { path: '/ap-courses', label: 'AP Courses', icon: 'bi-star' },
    { path: '/honors-program', label: 'Honors Program', icon: 'bi-award' },
    { path: '/summer-programs', label: 'Summer Programs', icon: 'bi-sun' }
  ];

  const campusLifeNavigation = [
    { path: '/campus-life', label: 'Overview', icon: 'bi-tree' },
    { path: '/student-clubs', label: 'Clubs', icon: 'bi-people' },
    { path: '/athletics', label: 'Athletics', icon: 'bi-trophy' },
    { path: '/arts', label: 'Arts', icon: 'bi-palette' },
    { path: '/student-services', label: 'Student Services', icon: 'bi-heart' },
    { path: '/counseling', label: 'Counseling', icon: 'bi-chat' },
    { path: '/dormitories', label: 'Dormitories', icon: 'bi-house-door' },
    { path: '/dining', label: 'Dining', icon: 'bi-egg-fried' },
    { path: '/health-services', label: 'Health Services', icon: 'bi-plus-circle' },
    { path: '/transportation', label: 'Transportation', icon: 'bi-bus-front' },
    { path: '/safety', label: 'Safety', icon: 'bi-shield-check' },
    { path: '/student-handbook', label: 'Student Handbook', icon: 'bi-journal-bookmark' }
  ];

  const admissionNavigation = [
    { path: '/admissions', label: 'Overview', icon: 'bi-pencil' },
    { path: '/apply', label: 'Apply Now', icon: 'bi-pencil-square' },
    { path: '/requirements', label: 'Requirements', icon: 'bi-list-check' },
    { path: '/tuition', label: 'Tuition & Fees', icon: 'bi-cash' },
    { path: '/scholarships', label: 'Scholarships', icon: 'bi-award' },
    { path: '/financial-aid', label: 'Financial Aid', icon: 'bi-wallet' },
    { path: '/campus-tour', label: 'Campus Tour', icon: 'bi-geo' },
    { path: '/international-students', label: 'International Students', icon: 'bi-globe' },
    { path: '/transfer-students', label: 'Transfer Students', icon: 'bi-arrow-left-right' },
    { path: '/application-status', label: 'Application Status', icon: 'bi-clock' }
  ];

  const resourcesNavigation = [
    { path: '/resources', label: 'Overview', icon: 'bi-folder' },
    { path: '/library', label: 'Library', icon: 'bi-book' },
    { path: '/calendar', label: 'Calendar', icon: 'bi-calendar' },
    { path: '/documents', label: 'Documents', icon: 'bi-file-text' },
    { path: '/downloads', label: 'Downloads', icon: 'bi-download' },
    { path: '/parent-resources', label: 'Parent Resources', icon: 'bi-people' },
    { path: '/teacher-resources', label: 'Teacher Resources', icon: 'bi-person-badge' },
    { path: '/research-portal', label: 'Research Portal', icon: 'bi-search' },
    { path: '/tech-support', label: 'Tech Support', icon: 'bi-tools' }
  ];

  const aboutNavigation = [
    { path: '/about', label: 'Overview', icon: 'bi-info-circle' },
    { path: '/school-history', label: 'School History', icon: 'bi-clock-history' },
    { path: '/mission-vision', label: 'Mission & Vision', icon: 'bi-eye' },
    { path: '/leadership', label: 'Leadership', icon: 'bi-person-badge' },
    { path: '/faculty-directory', label: 'Faculty Directory', icon: 'bi-people' },
    { path: '/careers', label: 'Careers', icon: 'bi-briefcase' },
    { path: '/testimonials', label: 'Testimonials', icon: 'bi-chat-quote' }
  ];

  // Lower navbar main categories
  const lowerNavigation = [
    { 
      path: '/academics', 
      label: 'Academics', 
      icon: 'bi-book',
      dropdown: academicNavigation
    },
    { 
      path: '/campus-life', 
      label: 'Campus Life', 
      icon: 'bi-tree',
      dropdown: campusLifeNavigation
    },
    { 
      path: '/admissions', 
      label: 'Admissions', 
      icon: 'bi-pencil',
      dropdown: admissionNavigation
    },
    { 
      path: '/resources', 
      label: 'Resources', 
      icon: 'bi-folder',
      dropdown: resourcesNavigation
    },
    { 
      path: '/about', 
      label: 'About Us', 
      icon: 'bi-info-circle',
      dropdown: aboutNavigation
    }
  ];

  // Authenticated user navigation
  const authenticatedNavigation = [
    { path: '/dashboard', label: 'Dashboard', icon: 'bi-speedometer2' },
    ...lowerNavigation
  ];

  const lowerNavItems = isUserAuthenticated() ? authenticatedNavigation : lowerNavigation;

  // Handle keydown for accessibility
  const handleKeyDown = (e, callback) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      callback();
    }
  };

  if (authState.loading) {
    return null; // Or a loading spinner
  }

  return (
    <>
      {/* Upper Navbar - Quick Access & Auth */}
      <nav 
        className={`navbar navbar-expand-lg navbar-dark fixed-top transition-all upper-navbar ${
          scrolled ? 'bg-dark shadow' : 'bg-dark'
        }`}
        style={{
          transition: 'all 0.3s ease-in-out',
          padding: '0.4rem 0',
          minHeight: '45px',
          zIndex: 1030
        }}
      >
        <div className="container">
          {/* Quick Links - Desktop */}
          <ul className="navbar-nav d-none d-lg-flex flex-row me-auto">
            {upperNavigation.map((item) => (
              <li key={item.path} className="nav-item">
                <Link 
                  className={`nav-link px-2 ${isActive(item.path) ? 'text-warning fw-bold' : 'text-light'}`}
                  to={item.path}
                  style={{ fontSize: '0.85rem', fontWeight: '500' }}
                  onClick={closeNavbar}
                >
                  <i className={`${item.icon} me-1`}></i>
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>

          {/* Brand - Mobile Only */}
          <Link 
            className="navbar-brand fw-bold d-lg-none d-flex align-items-center" 
            to={isUserAuthenticated() ? "/dashboard" : "/"}
            onClick={closeNavbar}
            style={{ fontSize: '1rem' }}
          >
            <span className="school-icon me-1">🏫</span>
            Delvok Academy
          </Link>

          {/* Right Section - Search & Auth */}
          <div className="d-flex align-items-center ms-auto">
            {/* Search Toggle Button */}
            <button
              className="btn btn-link text-white me-2"
              onClick={toggleSearch}
              aria-label="Search"
              style={{ padding: '0.25rem' }}
              onKeyDown={(e) => handleKeyDown(e, toggleSearch)}
            >
              <i className={`bi ${showSearch ? 'bi-x-lg' : 'bi-search'}`}></i>
            </button>

            {/* Auth Section */}
            <div className="d-flex align-items-center">
              {isUserAuthenticated() ? (
                <div className="dropdown">
                  <button
                    className="btn btn-link text-white dropdown-toggle d-flex align-items-center"
                    onClick={() => toggleDropdown('user-upper')}
                    onKeyDown={(e) => handleKeyDown(e, () => toggleDropdown('user-upper'))}
                    style={{ fontSize: '0.85rem', fontWeight: '500' }}
                    aria-expanded={activeDropdown === 'user-upper'}
                  >
                    <i className="bi bi-person-circle me-1"></i>
                    {getUserDisplayName()}
                    <span className={`badge bg-${getRoleBadgeColor(getUserRole())} ms-1`} style={{ fontSize: '0.6rem' }}>
                      {getUserRole()}
                    </span>
                  </button>
                  <div className={`dropdown-menu dropdown-menu-end shadow-lg border-0 fade ${activeDropdown === 'user-upper' ? 'show' : ''}`}>
                    <div className="dropdown-header py-2">
                      <strong>{getUserDisplayName()}</strong>
                      <div className="small text-muted">{getUserEmail()}</div>
                    </div>
                    <div className="dropdown-divider"></div>
                    <Link className="dropdown-item d-flex align-items-center" to="/dashboard" onClick={closeNavbar}>
                      <i className="bi bi-speedometer2 me-2"></i>
                      Dashboard
                    </Link>
                    <Link className="dropdown-item d-flex align-items-center" to="/profile" onClick={closeNavbar}>
                      <i className="bi bi-person me-2"></i>
                      Profile
                    </Link>
                    <div className="dropdown-divider"></div>
                    <button 
                      className="dropdown-item d-flex align-items-center text-danger" 
                      onClick={handleLogout}
                      onKeyDown={(e) => handleKeyDown(e, handleLogout)}
                    >
                      <i className="bi bi-box-arrow-right me-2"></i>
                      Logout
                    </button>
                  </div>
                </div>
              ) : (
                <div className="d-flex align-items-center">
                  <Link 
                    to="/login" 
                    className="btn btn-outline-light btn-sm me-1"
                    onClick={closeNavbar}
                    style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                  >
                    <i className="bi bi-box-arrow-in-right me-1"></i>
                    Login
                  </Link>
                  {/* Registration button removed */}
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Lower Navbar - Main Navigation */}
      <nav 
        className={`navbar navbar-expand-lg navbar-dark fixed-top transition-all lower-navbar ${
          scrolled ? 'bg-primary shadow-lg' : 'bg-primary-gradient'
        }`}
        style={{
          transition: 'all 0.3s ease-in-out',
          padding: '0.6rem 0',
          minHeight: '65px',
          top: '45px', // Position below upper navbar
          zIndex: 1029
        }}
      >
        <div className="container">
          {/* Brand - Desktop Only */}
          <Link 
            className="navbar-brand fw-bold d-none d-lg-flex align-items-center" 
            to={isUserAuthenticated() ? "/dashboard" : "/"}
            onClick={closeNavbar}
            style={{ fontSize: '1.5rem' }}
          >
            <span className="school-icon me-2">🏫</span>
            Delvok Academy
          </Link>
          
          {/* Search Bar - Desktop */}
          {showSearch && (
            <div className="search-container-desktop me-4">
              <form onSubmit={handleSearchSubmit} className="position-relative">
                <input
                  id="search-input"
                  type="text"
                  className="form-control search-input"
                  placeholder="Search students, teachers, events, courses..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ width: '350px' }}
                  aria-label="Search"
                />
                <button type="submit" className="btn btn-light position-absolute end-0 top-0 h-100 border-0">
                  <i className="bi bi-search"></i>
                </button>
                
                {/* Search Results Dropdown */}
                {searchResults.length > 0 && (
                  <div className="search-results-dropdown position-absolute top-100 start-0 end-0 mt-1 shadow-lg">
                    {searchResults.map((result, index) => (
                      <div
                        key={index}
                        className="search-result-item p-3 border-bottom bg-white cursor-pointer"
                        onClick={() => handleSearchResultClick(result)}
                        onKeyDown={(e) => handleKeyDown(e, () => handleSearchResultClick(result))}
                        tabIndex={0}
                        role="button"
                        aria-label={`Go to ${result.title}`}
                      >
                        <div className="d-flex align-items-center">
                          <i className={`bi bi-${getResultIcon(result.type)} text-primary me-3`}></i>
                          <div className="flex-grow-1">
                            <div className="fw-bold">{result.title}</div>
                            <div className="text-muted small">{result.description}</div>
                          </div>
                          <span className="badge bg-light text-dark">{result.type}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </form>
            </div>
          )}

          <button 
            className="navbar-toggler border-0 d-lg-none" 
            type="button" 
            onClick={() => setIsCollapsed(!isCollapsed)}
            onKeyDown={(e) => handleKeyDown(e, () => setIsCollapsed(!isCollapsed))}
            aria-label="Toggle navigation"
            aria-expanded={!isCollapsed}
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          
          <div className={`collapse navbar-collapse ${!isCollapsed ? 'show' : ''}`} id="navbarNav">
            {/* Search Bar - Mobile */}
            <div className="d-lg-none mb-3">
              <form onSubmit={handleSearchSubmit} className="position-relative">
                <input
                  type="text"
                  className="form-control search-input"
                  placeholder="Search students, teachers, events..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  aria-label="Search"
                />
                <button type="submit" className="btn btn-light position-absolute end-0 top-0 h-100 border-0">
                  <i className="bi bi-search"></i>
                </button>
              </form>
            </div>

            <ul className="navbar-nav ms-auto">
              {lowerNavItems.map((item) => (
                <li 
                  key={item.path} 
                  className={`nav-item ${item.dropdown ? 'dropdown' : ''}`}
                  onClick={item.dropdown ? undefined : handleNavClick}
                >
                  {item.dropdown ? (
                    <>
                      <button
                        className={`nav-link position-relative py-2 px-3 mx-1 dropdown-toggle transition-all d-flex align-items-center ${
                          isActive(item.path) ? 'active fw-bold' : ''
                        }`}
                        onClick={() => toggleDropdown(item.label)}
                        onKeyDown={(e) => handleKeyDown(e, () => toggleDropdown(item.label))}
                        aria-expanded={activeDropdown === item.label}
                      >
                        <i className={`${item.icon} me-2`}></i>
                        {item.label}
                      </button>
                      <div className={`dropdown-menu shadow-lg border-0 fade ${activeDropdown === item.label ? 'show' : ''}`} style={{ minWidth: '250px' }}>
                        <div className="dropdown-header fw-bold text-primary">
                          <i className={`${item.icon} me-2`}></i>
                          {item.label}
                        </div>
                        <div className="dropdown-divider"></div>
                        {item.dropdown.map((dropdownItem) => (
                          <Link
                            key={dropdownItem.path}
                            className={`dropdown-item d-flex align-items-center py-2 ${isActive(dropdownItem.path) ? 'active' : ''}`}
                            to={dropdownItem.path}
                            onClick={closeNavbar}
                          >
                            <i className={`${dropdownItem.icon} me-2`}></i>
                            {dropdownItem.label}
                            {isActive(dropdownItem.path) && (
                              <i className="bi bi-check2 text-success ms-auto"></i>
                            )}
                          </Link>
                        ))}
                      </div>
                    </>
                  ) : (
                    <Link 
                      className={`nav-link position-relative py-2 px-3 mx-1 transition-all d-flex align-items-center ${
                        isActive(item.path) ? 'active fw-bold' : ''
                      }`}
                      to={item.path}
                      onClick={closeNavbar}
                      aria-current={isActive(item.path) ? 'page' : undefined}
                    >
                      <i className={`${item.icon} me-2`}></i>
                      {item.label}
                      {isActive(item.path) && (
                        <span className="active-indicator" aria-hidden="true"></span>
                      )}
                    </Link>
                  )}
                </li>
              ))}

              {/* Additional Links for Authenticated Users */}
              {isUserAuthenticated() && (
                <>
                  <li className="nav-item dropdown d-lg-none">
                    <button
                      className="nav-link position-relative py-2 px-3 mx-1 dropdown-toggle transition-all d-flex align-items-center"
                      onClick={() => toggleDropdown('quick-access')}
                      onKeyDown={(e) => handleKeyDown(e, () => toggleDropdown('quick-access'))}
                      aria-expanded={activeDropdown === 'quick-access'}
                    >
                      <i className="bi bi-lightning me-2"></i>
                      Quick Access
                    </button>
                    <div className={`dropdown-menu shadow-lg border-0 fade ${activeDropdown === 'quick-access' ? 'show' : ''}`}>
                      {getRoleQuickLinks(getUserRole()).map((link) => (
                        <Link
                          key={link.path}
                          className="dropdown-item d-flex align-items-center py-2"
                          to={link.path}
                          onClick={closeNavbar}
                        >
                          <i className={`${link.icon} me-2`}></i>
                          {link.label}
                        </Link>
                      ))}
                    </div>
                  </li>
                </>
              )}
            </ul>
          </div>
        </div>
      </nav>

      {/* Mobile Search Overlay */}
      {showSearch && (
        <div className="search-overlay d-lg-none">
          <div className="search-overlay-content">
            <form onSubmit={handleSearchSubmit} className="position-relative">
              <input
                type="text"
                className="form-control search-input-lg"
                placeholder="Search students, teachers, events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                autoFocus
                aria-label="Search"
              />
              <button 
                type="button" 
                className="btn btn-close position-absolute end-0 top-0 h-100"
                onClick={() => setShowSearch(false)}
                aria-label="Close search"
              />
            </form>
            {searchResults.length > 0 && (
              <div className="search-results-overlay">
                {searchResults.map((result, index) => (
                  <div
                    key={index}
                    className="search-result-item p-3 border-bottom bg-white"
                    onClick={() => {
                      handleSearchResultClick(result);
                      setShowSearch(false);
                    }}
                    onKeyDown={(e) => handleKeyDown(e, () => {
                      handleSearchResultClick(result);
                      setShowSearch(false);
                    })}
                    tabIndex={0}
                    role="button"
                  >
                    <div className="d-flex align-items-center">
                      <i className={`bi bi-${getResultIcon(result.type)} text-primary me-3`}></i>
                      <div className="flex-grow-1">
                        <div className="fw-bold">{result.title}</div>
                        <div className="text-muted small">{result.description}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

// Helper functions
function getRoleBadgeColor(role) {
  switch (role) {
    case 'admin': return 'danger';
    case 'teacher': return 'warning';
    case 'student': return 'success';
    case 'parent': return 'info';
    default: return 'secondary';
  }
}

function getResultIcon(type) {
  switch (type) {
    case 'page': return 'file-text';
    case 'teacher': return 'person-badge';
    case 'student': return 'person';
    case 'event': return 'calendar-event';
    case 'course': return 'journal';
    default: return 'file-text';
  }
}

function getRoleQuickLinks(role) {
  const baseLinks = [
    { path: '/profile', label: 'My Profile', icon: 'bi-person' },
    { path: '/settings', label: 'Settings', icon: 'bi-gear' }
  ];

  const roleLinks = {
    admin: [
      { path: '/admin', label: 'Admin Dashboard', icon: 'bi-speedometer2' },
      { path: '/admin/users', label: 'User Management', icon: 'bi-people' },
      { path: '/admin/analytics', label: 'Analytics', icon: 'bi-graph-up' }
    ],
    teacher: [
      { path: '/teacher-dashboard', label: 'Teacher Dashboard', icon: 'bi-speedometer2' },
      { path: '/grade-management', label: 'Grade Management', icon: 'bi-journal-check' },
      { path: '/attendance-management', label: 'Attendance', icon: 'bi-clipboard-check' }
    ],
    student: [
      { path: '/student-portal', label: 'Student Portal', icon: 'bi-speedometer2' },
      { path: '/grades', label: 'My Grades', icon: 'bi-journal-text' },
      { path: '/timetable', label: 'Class Schedule', icon: 'bi-calendar-week' }
    ],
    parent: [
      { path: '/parent-portal', label: 'Parent Portal', icon: 'bi-speedometer2' },
      { path: '/child-progress', label: 'Child Progress', icon: 'bi-graph-up' },
      { path: '/parent-meetings', label: 'Parent Meetings', icon: 'bi-calendar-check' }
    ]
  };

  return [...(roleLinks[role] || []), ...baseLinks];
}

export default Navbar;