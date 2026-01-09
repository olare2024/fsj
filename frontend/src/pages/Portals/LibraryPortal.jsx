// frontend/src/pages/Portals/LibraryPortal.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { libraryAPI } from '../../services/libraryAPI';

const LibraryPortal = () => {
  const { currentUser, getFullName } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showBookModal, setShowBookModal] = useState(false);
  const [showBorrowModal, setShowBorrowModal] = useState(false);
  const [newBook, setNewBook] = useState({
    title: '',
    author: '',
    isbn: '',
    category: '',
    copies: 1,
    location: ''
  });
  const [borrowData, setBorrowData] = useState({
    student_id: '',
    book_id: '',
    due_date: ''
  });

  // Mock API function - replace with actual API
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // Replace with actual API call
      const mockData = {
        library_stats: [
          { title: 'Total Books', value: 12540, color: 'primary', icon: '📚' },
          { title: 'Available Books', value: 8430, color: 'success', icon: '✅' },
          { title: 'Borrowed Books', value: 2876, color: 'warning', icon: '📖' },
          { title: 'Overdue Books', value: 234, color: 'danger', icon: '⏰' }
        ],
        recent_activities: [
          { 
            id: 1, 
            type: 'borrow', 
            student: 'John Mutisya', 
            book: 'Introduction to Physics', 
            time: '2 hours ago', 
            status: 'active' 
          },
          { 
            id: 2, 
            type: 'return', 
            student: 'Mary Achieng', 
            book: 'Chemistry Fundamentals', 
            time: '4 hours ago', 
            status: 'completed' 
          },
          { 
            id: 3, 
            type: 'reservation', 
            student: 'Peter Omondi', 
            book: 'Advanced Mathematics', 
            time: '1 day ago', 
            status: 'pending' 
          }
        ],
        popular_books: [
          { id: 1, title: 'Introduction to Computer Science', author: 'Dr. James Wilson', available: 5, total: 8 },
          { id: 2, title: 'Physics for Beginners', author: 'Prof. Sarah Johnson', available: 3, total: 6 },
          { id: 3, title: 'Chemistry Fundamentals', author: 'Dr. Michael Brown', available: 2, total: 5 },
          { id: 4, title: 'English Literature Guide', author: 'Prof. Emily Davis', available: 7, total: 10 }
        ],
        categories: [
          { name: 'Science & Technology', count: 3450, color: 'primary' },
          { name: 'Literature & Fiction', count: 2890, color: 'success' },
          { name: 'History & Geography', count: 1870, color: 'info' },
          { name: 'Mathematics', count: 1560, color: 'warning' },
          { name: 'Languages', count: 1230, color: 'danger' },
          { name: 'Reference', count: 980, color: 'secondary' }
        ]
      };
      
      setDashboardData(mockData);
      setError(null);
    } catch (err) {
      setError('Failed to load library data');
      console.error('Error loading library dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const libraryStats = dashboardData?.library_stats || [];
  const recentActivities = dashboardData?.recent_activities || [];
  const popularBooks = dashboardData?.popular_books || [];
  const categories = dashboardData?.categories || [];

  const quickActions = [
    {
      title: 'Book Management',
      description: 'Add, edit, and manage books',
      icon: '📚',
      path: '/library/books',
      color: 'primary'
    },
    {
      title: 'Borrow Book',
      description: 'Process book borrowing',
      icon: '📖',
      path: '#',
      color: 'success',
      action: () => setShowBorrowModal(true)
    },
    {
      title: 'Return Book',
      description: 'Process book returns',
      icon: '↩️',
      path: '/library/returns',
      color: 'info'
    },
    {
      title: 'Catalog Search',
      description: 'Search library catalog',
      icon: '🔍',
      path: '/library/search',
      color: 'warning'
    },
    {
      title: 'Reports',
      description: 'Generate library reports',
      icon: '📊',
      path: '/library/reports',
      color: 'danger'
    },
    {
      title: 'Add New Book',
      description: 'Add book to collection',
      icon: '➕',
      path: '#',
      color: 'secondary',
      action: () => setShowBookModal(true)
    }
  ];

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { class: 'bg-success', text: 'Active' },
      completed: { class: 'bg-info', text: 'Completed' },
      pending: { class: 'bg-warning', text: 'Pending' },
      overdue: { class: 'bg-danger', text: 'Overdue' }
    };
    
    const config = statusConfig[status] || { class: 'bg-secondary', text: status };
    return `<span class="badge ${config.class}">${config.text}</span>`;
  };

  const getActivityIcon = (type) => {
    const icons = {
      borrow: '📖',
      return: '↩️',
      reservation: '⏰',
      renewal: '🔄',
      default: '📚'
    };
    return icons[type] || icons.default;
  };

  const handleAddBook = async (e) => {
    e.preventDefault();
    try {
      // Add API call to create book
      console.log('Adding book:', newBook);
      setShowBookModal(false);
      setNewBook({ title: '', author: '', isbn: '', category: '', copies: 1, location: '' });
      // Refresh data
      loadDashboardData();
    } catch (error) {
      console.error('Failed to add book:', error);
    }
  };

  const handleBorrowBook = async (e) => {
    e.preventDefault();
    try {
      // Add API call to borrow book
      console.log('Borrowing book:', borrowData);
      setShowBorrowModal(false);
      setBorrowData({ student_id: '', book_id: '', due_date: '' });
      // Refresh data
      loadDashboardData();
    } catch (error) {
      console.error('Failed to borrow book:', error);
    }
  };

  const getAvailabilityColor = (available, total) => {
    const percentage = (available / total) * 100;
    if (percentage >= 50) return 'success';
    if (percentage >= 25) return 'warning';
    return 'danger';
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 text-muted">Loading Library Portal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      {/* Header Section */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Library Portal</h1>
              <p className="text-muted mb-0">
                Welcome, {getFullName()}! Library management and book tracking.
              </p>
            </div>
            <div className="d-flex align-items-center gap-3">
              <span className="badge bg-primary">
                <i className="fas fa-book me-1"></i>
                Librarian
              </span>
              <div className="btn-group">
                <button className="btn btn-primary" onClick={() => setShowBookModal(true)}>
                  <i className="fas fa-plus me-1"></i>
                  Add Book
                </button>
                <button className="btn btn-success" onClick={() => setShowBorrowModal(true)}>
                  <i className="fas fa-book-open me-1"></i>
                  Borrow Book
                </button>
              </div>
            </div>
          </div>
          <hr />
        </div>
      </div>

      {error && (
        <div className="row mb-4">
          <div className="col-12">
            <div className="alert alert-warning alert-dismissible fade show" role="alert">
              <i className="fas fa-exclamation-triangle me-2"></i>
              {error}
              <button type="button" className="btn-close" onClick={() => setError(null)}></button>
            </div>
          </div>
        </div>
      )}

      {/* Library Statistics */}
      <div className="row mb-4">
        {libraryStats.map((stat, index) => (
          <div key={index} className="col-12 col-sm-6 col-lg-3 mb-3">
            <div className={`card border-${stat.color} h-100`}>
              <div className="card-body text-center">
                <div className="mb-2" style={{ fontSize: '2rem' }}>
                  {stat.icon}
                </div>
                <h2 className={`text-${stat.color}`}>{stat.value.toLocaleString()}</h2>
                <p className="text-muted mb-0">{stat.title}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="row">
        {/* Quick Actions */}
        <div className="col-12 col-lg-8 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h5 className="card-title mb-0">Quick Actions</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {quickActions.map((action, index) => (
                  <div key={index} className="col-12 col-sm-6 col-md-4 mb-3">
                    <button
                      className={`btn btn-outline-${action.color} w-100 h-100 p-3 text-start`}
                      onClick={action.action || (() => window.location.href = action.path)}
                    >
                      <div className="d-flex align-items-center">
                        <span className="me-3" style={{ fontSize: '1.5rem' }}>
                          {action.icon}
                        </span>
                        <div>
                          <div className="fw-bold">{action.title}</div>
                          <small className="text-muted">{action.description}</small>
                        </div>
                      </div>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="col-12 col-lg-4 mb-4">
          <div className="card h-100">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Recent Activities</h5>
              <span className="badge bg-primary">{recentActivities.length}</span>
            </div>
            <div className="card-body">
              {recentActivities.length > 0 ? (
                <div className="list-group list-group-flush">
                  {recentActivities.map((activity, index) => (
                    <div key={activity.id} className="list-group-item">
                      <div className="d-flex align-items-start">
                        <div className="flex-shrink-0 me-3" style={{ fontSize: '1.5rem' }}>
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-grow-1">
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <span className="fw-bold">{activity.student}</span>
                              <small className="text-muted d-block">{activity.book}</small>
                            </div>
                            <span 
                              dangerouslySetInnerHTML={{ 
                                __html: getStatusBadge(activity.status) 
                              }} 
                            />
                          </div>
                          <small className="text-muted">{activity.time}</small>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <div className="text-muted mb-2">No recent activities</div>
                  <small className="text-muted">Library activities will appear here</small>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Popular Books */}
        <div className="col-12 col-lg-6 mb-4">
          <div className="card h-100">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Popular Books</h5>
              <button className="btn btn-sm btn-outline-primary">
                View All
              </button>
            </div>
            <div className="card-body">
              <div className="list-group list-group-flush">
                {popularBooks.map((book, index) => (
                  <div key={book.id} className="list-group-item d-flex justify-content-between align-items-center">
                    <div className="flex-grow-1">
                      <div className="fw-bold">{book.title}</div>
                      <small className="text-muted">by {book.author}</small>
                    </div>
                    <div className="text-end">
                      <div className={`badge bg-${getAvailabilityColor(book.available, book.total)}`}>
                        {book.available}/{book.total} available
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Book Categories */}
        <div className="col-12 col-lg-6 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h5 className="card-title mb-0">Book Categories</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {categories.map((category, index) => (
                  <div key={index} className="col-6 mb-3">
                    <div className={`card border-${category.color}`}>
                      <div className="card-body text-center p-3">
                        <h6 className="card-title">{category.name}</h6>
                        <h4 className={`text-${category.color}`}>{category.count.toLocaleString()}</h4>
                        <small className="text-muted">Books</small>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Library Announcements */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-header">
              <h5 className="card-title mb-0 text-primary">
                <i className="fas fa-bullhorn me-2"></i>
                Library Announcements
              </h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-4 mb-3">
                  <div className="d-flex align-items-center p-3 bg-white rounded">
                    <i className="fas fa-clock text-warning fs-4 me-3"></i>
                    <div>
                      <div className="fw-bold">Extended Hours</div>
                      <div className="text-muted">Library open until 8 PM during exams</div>
                    </div>
                  </div>
                </div>
                <div className="col-md-4 mb-3">
                  <div className="d-flex align-items-center p-3 bg-white rounded">
                    <i className="fas fa-book text-success fs-4 me-3"></i>
                    <div>
                      <div className="fw-bold">New Arrivals</div>
                      <div className="text-muted">200+ new books added this month</div>
                    </div>
                  </div>
                </div>
                <div className="col-md-4 mb-3">
                  <div className="d-flex align-items-center p-3 bg-white rounded">
                    <i className="fas fa-exclamation-triangle text-danger fs-4 me-3"></i>
                    <div>
                      <div className="fw-bold">Overdue Notices</div>
                      <div className="text-muted">Please return overdue books</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Book Modal */}
      {showBookModal && (
        <div className="modal show d-block" tabIndex="-1">
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add New Book</h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={() => setShowBookModal(false)}
                ></button>
              </div>
              <form onSubmit={handleAddBook}>
                <div className="modal-body">
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Book Title</label>
                      <input 
                        type="text" 
                        className="form-control"
                        value={newBook.title}
                        onChange={(e) => setNewBook({...newBook, title: e.target.value})}
                        required
                      />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Author</label>
                      <input 
                        type="text" 
                        className="form-control"
                        value={newBook.author}
                        onChange={(e) => setNewBook({...newBook, author: e.target.value})}
                        required
                      />
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">ISBN</label>
                      <input 
                        type="text" 
                        className="form-control"
                        value={newBook.isbn}
                        onChange={(e) => setNewBook({...newBook, isbn: e.target.value})}
                      />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Category</label>
                      <select 
                        className="form-select"
                        value={newBook.category}
                        onChange={(e) => setNewBook({...newBook, category: e.target.value})}
                        required
                      >
                        <option value="">Select Category</option>
                        <option value="science">Science & Technology</option>
                        <option value="literature">Literature & Fiction</option>
                        <option value="history">History & Geography</option>
                        <option value="mathematics">Mathematics</option>
                        <option value="languages">Languages</option>
                        <option value="reference">Reference</option>
                      </select>
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Number of Copies</label>
                      <input 
                        type="number" 
                        className="form-control"
                        value={newBook.copies}
                        onChange={(e) => setNewBook({...newBook, copies: parseInt(e.target.value)})}
                        min="1"
                        required
                      />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Location</label>
                      <input 
                        type="text" 
                        className="form-control"
                        value={newBook.location}
                        onChange={(e) => setNewBook({...newBook, location: e.target.value})}
                        placeholder="e.g., Shelf A5, Row 3"
                      />
                    </div>
                  </div>
                </div>
                <div className="modal-footer">
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => setShowBookModal(false)}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Add Book
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Borrow Book Modal */}
      {showBorrowModal && (
        <div className="modal show d-block" tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Borrow Book</h5>
                <button 
                  type="button" 
                  className="btn-close"
                  onClick={() => setShowBorrowModal(false)}
                ></button>
              </div>
              <form onSubmit={handleBorrowBook}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Student ID</label>
                    <input 
                      type="text" 
                      className="form-control"
                      value={borrowData.student_id}
                      onChange={(e) => setBorrowData({...borrowData, student_id: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Book ID/ISBN</label>
                    <input 
                      type="text" 
                      className="form-control"
                      value={borrowData.book_id}
                      onChange={(e) => setBorrowData({...borrowData, book_id: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Due Date</label>
                    <input 
                      type="date" 
                      className="form-control"
                      value={borrowData.due_date}
                      onChange={(e) => setBorrowData({...borrowData, due_date: e.target.value})}
                      required
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => setShowBorrowModal(false)}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-success">
                    Process Borrow
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal Backdrops */}
      {(showBookModal || showBorrowModal) && <div className="modal-backdrop show"></div>}
    </div>
  );
};

export default LibraryPortal;