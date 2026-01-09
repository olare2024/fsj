import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { libraryAPI, LIBRARY_CONSTANTS } from '../../services/libraryAPI';
import authAPI from '../../services/authAPI';
import { useAuth } from '../../context/AuthContext';

function Library() {
  // State Management
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [userBorrows, setUserBorrows] = useState([]);
  const [viewMode, setViewMode] = useState('public'); // 'public' or 'librarian'
  const [availableOnly, setAvailableOnly] = useState(false);
  
  // Hooks
  const { user, isAuthenticated, updateUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // User role checks
  const isLibrarian = user?.role === 'librarian';
  const isStudent = user?.role === 'student';
  const isTeacher = user?.role === 'teacher';
  const isAdmin = user?.role === 'admin';

  // Determine view mode based on route or user role
  useEffect(() => {
    if (location.pathname === '/library-portal' && isLibrarian) {
      setViewMode('librarian');
    } else {
      setViewMode('public');
    }
  }, [location.pathname, isLibrarian]);

  // Initialize data fetching
  useEffect(() => {
    const initializeData = async () => {
      setIsLoading(true);
      await Promise.all([
        fetchBooks(),
        fetchCategories(),
      ]);
      
      if (isAuthenticated) {
        await Promise.all([
          fetchLibraryStats(),
          fetchUserBorrows(),
        ]);
      }
      setIsLoading(false);
    };
    
    initializeData();
  }, [isAuthenticated]);

  // ==================== API INTEGRATION FUNCTIONS ====================

  // Fetch books from API
  const fetchBooks = async (search = '', category = '') => {
    try {
      const params = {};
      if (search) params.search = search;
      if (category && category !== 'all') params.category = category;
      
      // Add availability filter if needed
      if (availableOnly) params.available_only = true;
      
      const response = await libraryAPI.getBooks(params);
      
      if (response.success) {
        setBooks(response.data.results || response.data);
      } else {
        setError(response.error?.message || 'Failed to load books');
      }
    } catch (error) {
      setError('Error fetching books. Please try again.');
      console.error('Error fetching books:', error);
    }
  };

  // Fetch categories from API
  const fetchCategories = async () => {
    try {
      const response = await libraryAPI.getCategories();
      if (response.success) {
        const categoryList = ['all', ...response.data.map(cat => cat.name)];
        setCategories(categoryList);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Fallback categories
      setCategories(['all', 'Mathematics', 'Science', 'Literature', 'History', 'Arts']);
    }
  };

  // Fetch library statistics (authenticated only)
  const fetchLibraryStats = async () => {
    try {
      const response = await libraryAPI.getLibraryStats();
      if (response.success) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Error fetching library stats:', error);
    }
  };

  // Fetch user's current borrows
  const fetchUserBorrows = async () => {
    if (!user?.id) return;
    
    try {
      const response = await libraryAPI.getUserCurrentBorrows();
      if (response.success) {
        setUserBorrows(response.data.results || response.data);
      }
    } catch (error) {
      console.error('Error fetching user borrows:', error);
    }
  };

  // Handle book checkout
  const handleCheckout = async (bookId) => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: location.pathname } });
      return;
    }

    if (window.confirm('Are you sure you want to check out this book?')) {
      setIsActionLoading(true);
      try {
        const dueDate = new Date();
        dueDate.setDate(dueDate.getDate() + LIBRARY_CONSTANTS.LOAN_PERIODS.DEFAULT);
        
        const response = await libraryAPI.borrowBook({
          book: bookId,
          borrower: user.id,
          due_date: dueDate.toISOString()
        });

        if (response.success) {
          alert('Book checked out successfully!');
          // Refresh data
          await Promise.all([fetchBooks(), fetchUserBorrows()]);
          // Show success message
          showNotification('Book checked out successfully!', 'success');
        } else {
          alert(response.error?.message || 'Failed to check out book');
          showNotification(response.error?.message || 'Failed to check out book', 'error');
        }
      } catch (error) {
        alert('Error checking out book. Please try again.');
        console.error('Error checking out book:', error);
        showNotification('Error checking out book', 'error');
      } finally {
        setIsActionLoading(false);
      }
    }
  };

  // Handle reserve book
  const handleReserve = async (bookId) => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: location.pathname } });
      return;
    }

    if (window.confirm('Reserve this book?')) {
      setIsActionLoading(true);
      try {
        const response = await libraryAPI.reserveBook(bookId);
        if (response.success) {
          alert('Book reserved successfully! You will be notified when available.');
          await fetchBooks();
          showNotification('Book reserved successfully!', 'success');
        } else {
          alert(response.error?.message || 'Failed to reserve book');
          showNotification(response.error?.message || 'Failed to reserve book', 'error');
        }
      } catch (error) {
        alert('Error reserving book. Please try again.');
        console.error('Error reserving book:', error);
        showNotification('Error reserving book', 'error');
      } finally {
        setIsActionLoading(false);
      }
    }
  };

  // Handle renew book
  const handleRenew = async (borrowId) => {
    if (window.confirm('Renew this book?')) {
      setIsActionLoading(true);
      try {
        const response = await libraryAPI.renewBook(borrowId);
        if (response.success) {
          alert('Book renewed successfully!');
          await fetchUserBorrows();
          showNotification('Book renewed successfully!', 'success');
        } else {
          alert(response.error?.message || 'Failed to renew book');
          showNotification(response.error?.message || 'Failed to renew book', 'error');
        }
      } catch (error) {
        alert('Error renewing book. Please try again.');
        console.error('Error renewing book:', error);
        showNotification('Error renewing book', 'error');
      } finally {
        setIsActionLoading(false);
      }
    }
  };

  // Handle return book
  const handleReturn = async (borrowId) => {
    if (window.confirm('Return this book?')) {
      setIsActionLoading(true);
      try {
        const response = await libraryAPI.returnBook(borrowId, {});
        if (response.success) {
          alert('Book returned successfully!');
          await Promise.all([fetchBooks(), fetchUserBorrows()]);
          showNotification('Book returned successfully!', 'success');
        } else {
          alert(response.error?.message || 'Failed to return book');
          showNotification(response.error?.message || 'Failed to return book', 'error');
        }
      } catch (error) {
        alert('Error returning book. Please try again.');
        console.error('Error returning book:', error);
        showNotification('Error returning book', 'error');
      } finally {
        setIsActionLoading(false);
      }
    }
  };

  // Librarian actions
  const handleDeleteBook = async (bookId) => {
    if (window.confirm('Are you sure you want to delete this book?')) {
      setIsActionLoading(true);
      try {
        const response = await libraryAPI.deleteBook(bookId);
        if (response.success) {
          alert('Book deleted successfully!');
          await fetchBooks();
          showNotification('Book deleted successfully!', 'success');
        } else {
          alert('Failed to delete book');
          showNotification('Failed to delete book', 'error');
        }
      } catch (error) {
        alert('Error deleting book');
        console.error('Error:', error);
        showNotification('Error deleting book', 'error');
      } finally {
        setIsActionLoading(false);
      }
    }
  };

  // Search handling with debounce
  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    
    // Debounced search
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
      fetchBooks(value, selectedCategory);
    }, 300);
  };

  // Category change
  const handleCategoryChange = (e) => {
    const category = e.target.value;
    setSelectedCategory(category);
    fetchBooks(searchTerm, category);
  };

  // Filter books
  const filteredBooks = books.filter(book => {
    if (!searchTerm && selectedCategory === 'all' && !availableOnly) return true;
    
    const matchesSearch = searchTerm 
      ? (book.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
         book.author?.toLowerCase().includes(searchTerm.toLowerCase()) ||
         book.isbn?.includes(searchTerm))
      : true;
    
    const matchesCategory = selectedCategory === 'all' || 
      book.category?.toLowerCase() === selectedCategory.toLowerCase();
    
    const matchesAvailability = !availableOnly || book.available_copies > 0;
    
    return matchesSearch && matchesCategory && matchesAvailability;
  });

  // Helper functions
  const getAvailabilityStatus = (book) => {
    if (book.available_copies > 0) {
      return { text: 'Available', class: 'bg-success', canCheckout: true };
    } else if (book.total_copies > 0) {
      return { text: 'Checked Out', class: 'bg-warning', canCheckout: false };
    } else {
      return { text: 'Not Available', class: 'bg-danger', canCheckout: false };
    }
  };

  const showNotification = (message, type = 'info') => {
    // You can implement a proper notification system here
    console.log(`${type.toUpperCase()}: ${message}`);
  };

  // Loading Component
  if (isLoading) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <h4 className="mt-3">Loading Library...</h4>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>{viewMode === 'librarian' ? 'Library Management' : 'School Library'}</h1>
          <p className="lead mb-0">
            {viewMode === 'librarian' 
              ? 'Manage library resources and operations' 
              : 'Explore our extensive collection of resources'
            }
          </p>
          {isAuthenticated && user && (
            <p className="text-muted small">
              Welcome, {user.first_name || user.email}
            </p>
          )}
        </div>
        <div className="d-flex gap-2">
          {isAuthenticated && (
            <Link to="/dashboard" className="btn btn-outline-primary">
              <i className="bi bi-house-door me-2"></i>
              Dashboard
            </Link>
          )}
          {isLibrarian && viewMode === 'public' && (
            <Link to="/library-portal" className="btn btn-primary">
              <i className="bi bi-gear me-2"></i>
              Librarian Portal
            </Link>
          )}
          {isLibrarian && viewMode === 'librarian' && (
            <Link to="/library" className="btn btn-outline-secondary">
              <i className="bi bi-eye me-2"></i>
              Public View
            </Link>
          )}
          <Link to="/resources" className="btn btn-outline-secondary">
            <i className="bi bi-arrow-left me-2"></i>
            Resources
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      {isAuthenticated && stats && (
        <div className="row mb-4">
          <div className="col-md-3">
            <div className="card bg-primary text-white">
              <div className="card-body">
                <h5 className="card-title">Total Books</h5>
                <h2 className="mb-0">{stats.total_books || books.length}</h2>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card bg-success text-white">
              <div className="card-body">
                <h5 className="card-title">Available</h5>
                <h2 className="mb-0">{stats.available_books || books.filter(b => b.available_copies > 0).length}</h2>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card bg-info text-white">
              <div className="card-body">
                <h5 className="card-title">Categories</h5>
                <h2 className="mb-0">{stats.total_categories || categories.length - 1}</h2>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card bg-warning text-white">
              <div className="card-body">
                <h5 className="card-title">Active Loans</h5>
                <h2 className="mb-0">{stats.active_loans || userBorrows.length}</h2>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* User Borrows Summary */}
      {isAuthenticated && userBorrows.length > 0 && (
        <div className="card mb-4 border-warning">
          <div className="card-header bg-warning bg-opacity-10">
            <h5 className="mb-0">
              <i className="bi bi-book me-2"></i>
              Your Current Borrows ({userBorrows.length})
            </h5>
          </div>
          <div className="card-body">
            <div className="row">
              {userBorrows.slice(0, 3).map(borrow => (
                <div key={borrow.id} className="col-md-4">
                  <div className="d-flex align-items-center">
                    <div className="me-3">
                      <i className="bi bi-book fs-4"></i>
                    </div>
                    <div>
                      <strong>{borrow.book?.title || 'Unknown Book'}</strong>
                      <div className="small text-muted">
                        Due: {new Date(borrow.due_date).toLocaleDateString()}
                        {new Date(borrow.due_date) < new Date() && (
                          <span className="badge bg-danger ms-2">Overdue</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {userBorrows.length > 3 && (
              <div className="mt-2">
                <Link to="/library/my-borrows" className="btn btn-sm btn-outline-warning">
                  View All ({userBorrows.length})
                </Link>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search and Filter */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-8">
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search books, authors, ISBN..."
                  value={searchTerm}
                  onChange={handleSearch}
                />
              </div>
            </div>
            <div className="col-md-4">
              <select
                className="form-select"
                value={selectedCategory}
                onChange={handleCategoryChange}
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-12">
              <div className="form-check form-check-inline">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="showAvailableOnly"
                  checked={availableOnly}
                  onChange={(e) => {
                    setAvailableOnly(e.target.checked);
                    setTimeout(() => fetchBooks(searchTerm, selectedCategory), 100);
                  }}
                />
                <label className="form-check-label" htmlFor="showAvailableOnly">
                  Show available books only
                </label>
              </div>
              {(searchTerm || selectedCategory !== 'all' || availableOnly) && (
                <button
                  className="btn btn-sm btn-outline-secondary ms-3"
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedCategory('all');
                    setAvailableOnly(false);
                    fetchBooks();
                  }}
                >
                  <i className="bi bi-x-circle me-1"></i>
                  Clear Filters
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Books Grid */}
      <div className="mb-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5>
            {filteredBooks.length > 0 
              ? `Showing ${filteredBooks.length} books`
              : 'No books found'
            }
          </h5>
          <div className="d-flex gap-2">
            <Link to="/library/digital" className="btn btn-outline-success btn-sm">
              <i className="bi bi-laptop me-1"></i>
              Digital Resources
            </Link>
            {isAuthenticated && (
              <Link to="/library/my-borrows" className="btn btn-outline-info btn-sm">
                <i className="bi bi-book me-1"></i>
                My Borrows
              </Link>
            )}
          </div>
        </div>

        {filteredBooks.length > 0 ? (
          <div className="row g-4">
            {filteredBooks.map(book => {
              const availability = getAvailabilityStatus(book);
              const isBorrowedByUser = userBorrows.some(b => b.book?.id === book.id);
              
              return (
                <div key={book.id} className="col-md-6 col-lg-4 col-xl-3">
                  <div className="card h-100 shadow-sm hover-shadow">
                    {book.cover_image ? (
                      <img 
                        src={book.cover_image} 
                        alt={book.title}
                        className="card-img-top"
                        style={{ height: '200px', objectFit: 'cover' }}
                      />
                    ) : (
                      <div className="card-img-top bg-light d-flex align-items-center justify-content-center" style={{ height: '200px' }}>
                        <i className="bi bi-book fs-1 text-muted"></i>
                      </div>
                    )}
                    <div className="card-body">
                      <h6 className="card-title text-truncate" title={book.title}>
                        {book.title}
                      </h6>
                      <p className="card-text text-muted small">
                        by {book.author || 'Unknown Author'}
                      </p>
                      
                      <div className="book-details">
                        <div className="d-flex justify-content-between align-items-center mb-2">
                          <span className="badge bg-secondary">
                            {book.category || 'Uncategorized'}
                          </span>
                          <span className={`badge ${availability.class}`}>
                            {availability.text}
                            {book.available_copies > 0 && ` (${book.available_copies})`}
                          </span>
                        </div>
                        
                        <div className="small text-muted">
                          {book.isbn && (
                            <div className="d-flex align-items-center mb-1">
                              <i className="bi bi-upc-scan me-2"></i>
                              ISBN: {book.isbn}
                            </div>
                          )}
                          {book.location && (
                            <div className="d-flex align-items-center">
                              <i className="bi bi-geo-alt me-2"></i>
                              Shelf: {book.location}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="card-footer">
                      <div className="d-flex gap-2">
                        {viewMode === 'librarian' ? (
                          <>
                            <Link 
                              to={`/library/edit/${book.id}`}
                              className="btn btn-warning btn-sm flex-grow-1"
                            >
                              <i className="bi bi-pencil me-1"></i>
                              Edit
                            </Link>
                            <button 
                              className="btn btn-danger btn-sm"
                              onClick={() => handleDeleteBook(book.id)}
                              disabled={isActionLoading}
                            >
                              <i className="bi bi-trash"></i>
                            </button>
                            <Link 
                              to={`/library/books/${book.id}`}
                              className="btn btn-outline-info btn-sm"
                            >
                              <i className="bi bi-info-circle"></i>
                            </Link>
                          </>
                        ) : (
                          <>
                            {isBorrowedByUser ? (
                              <>
                                <button 
                                  className="btn btn-success btn-sm flex-grow-1"
                                  onClick={() => {
                                    const borrow = userBorrows.find(b => b.book?.id === book.id);
                                    if (borrow) handleRenew(borrow.id);
                                  }}
                                  disabled={isActionLoading}
                                >
                                  <i className="bi bi-arrow-clockwise me-1"></i>
                                  Renew
                                </button>
                                <button 
                                  className="btn btn-primary btn-sm"
                                  onClick={() => {
                                    const borrow = userBorrows.find(b => b.book?.id === book.id);
                                    if (borrow) handleReturn(borrow.id);
                                  }}
                                  disabled={isActionLoading}
                                >
                                  <i className="bi bi-check-circle"></i>
                                </button>
                              </>
                            ) : (
                              <button 
                                className="btn btn-primary btn-sm flex-grow-1"
                                onClick={() => handleCheckout(book.id)}
                                disabled={!availability.canCheckout || isActionLoading}
                                title={availability.canCheckout ? 'Check out this book' : 'No copies available'}
                              >
                                {availability.canCheckout ? (
                                  <>
                                    <i className="bi bi-cart-check me-1"></i>
                                    Check Out
                                  </>
                                ) : (
                                  'Unavailable'
                                )}
                              </button>
                            )}
                            {!availability.canCheckout && availability.text === 'Checked Out' && (
                              <button 
                                className="btn btn-warning btn-sm"
                                onClick={() => handleReserve(book.id)}
                                disabled={isActionLoading}
                              >
                                <i className="bi bi-bookmark"></i>
                              </button>
                            )}
                            <Link 
                              to={`/library/books/${book.id}`}
                              className="btn btn-outline-secondary btn-sm"
                            >
                              <i className="bi bi-info-circle"></i>
                            </Link>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="card">
            <div className="card-body text-center py-5">
              <i className="bi bi-book" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
              <h4 className="mt-3">No books found</h4>
              <p className="text-muted">
                {searchTerm || selectedCategory !== 'all' || availableOnly
                  ? 'Try adjusting your search or filter criteria'
                  : 'No books available in the library'
                }
              </p>
              {(searchTerm || selectedCategory !== 'all' || availableOnly) && (
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedCategory('all');
                    setAvailableOnly(false);
                    fetchBooks();
                  }}
                >
                  Clear filters
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Additional Information Panels */}
      <div className="row g-4">
        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-clock-history text-warning me-2"></i>
                Borrowing Rules
              </h5>
            </div>
            <div className="card-body">
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-2"></i>
                  <strong>Loan Period:</strong> {LIBRARY_CONSTANTS.LOAN_PERIODS.DEFAULT} days
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-2"></i>
                  <strong>Max Renewals:</strong> {LIBRARY_CONSTANTS.MAX_RENEWALS.DEFAULT}
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-2"></i>
                  <strong>Late Fee:</strong> Ksh {LIBRARY_CONSTANTS.FINE_RATES.DEFAULT}/day
                </li>
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-2"></i>
                  <strong>Max Books:</strong> {isStudent ? '3' : isTeacher ? '10' : '5'} at a time
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-laptop text-info me-2"></i>
                Digital Library
              </h5>
            </div>
            <div className="card-body">
              <p className="mb-3">
                Access e-books, audiobooks, and online resources from anywhere.
              </p>
              <div className="d-grid">
                <Link to="/library/digital" className="btn btn-outline-info">
                  Explore Digital Resources
                </Link>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-question-circle text-primary me-2"></i>
                Need Help?
              </h5>
            </div>
            <div className="card-body">
              <p className="mb-3">
                Contact the library staff for assistance or book recommendations.
              </p>
              <div className="d-grid">
                <a href="mailto:library@school.edu" className="btn btn-outline-primary">
                  <i className="bi bi-envelope me-2"></i>
                  library@school.edu
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Librarian Tools */}
      {isLibrarian && viewMode === 'public' && (
        <div className="mt-4 p-3 bg-light rounded">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h5 className="mb-1">Librarian Tools</h5>
              <p className="small text-muted mb-0">
                Access library management features
              </p>
            </div>
            <div className="d-flex gap-2">
              <Link to="/library-portal" className="btn btn-primary">
                <i className="bi bi-gear me-1"></i>
                Librarian Portal
              </Link>
              <Link to="/library/add-book" className="btn btn-success">
                <i className="bi bi-plus-circle me-1"></i>
                Add Book
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Action Loading Overlay */}
      {isActionLoading && (
        <div className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
             style={{ backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999 }}>
          <div className="text-center bg-white rounded p-4">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-2 mb-0">Processing...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Library;