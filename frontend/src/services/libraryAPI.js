import api from './api';

// ==================== HELPER FUNCTIONS ====================

const handleError = (error) => {
  if (error.name === 'AbortError') {
    return {
      success: false,
      error: {
        message: 'Request cancelled',
        code: 'CANCELLED'
      }
    };
  }

  if (!error.response) {
    return {
      success: false,
      error: {
        message: error.message || 'Network error',
        code: 'NETWORK_ERROR'
      }
    };
  }

  return {
    success: false,
    error: {
      message: error.response?.data?.error || error.response?.data?.detail || error.message,
      details: error.response?.data?.details || error.response?.data,
      status: error.response?.status,
      code: getErrorCode(error.response?.status)
    }
  };
};

const getErrorCode = (status) => {
  const codes = {
    400: 'VALIDATION_ERROR',
    401: 'UNAUTHORIZED',
    403: 'FORBIDDEN',
    404: 'NOT_FOUND',
    409: 'CONFLICT',
    422: 'UNPROCESSABLE_ENTITY',
    500: 'SERVER_ERROR'
  };
  return codes[status] || 'UNKNOWN_ERROR';
};

// ==================== LIBRARY API ====================

export const libraryAPI = {
  // ==================== CATEGORIES ====================
  
  // Get categories
  getCategories: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/categories/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get category tree
  getCategoryTree: async (signal = null) => {
    try {
      const response = await api.get('/library/categories/tree/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get books in category
  getCategoryBooks: async (categoryId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/library/categories/${categoryId}/books/`, {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== AUTHORS ====================
  
  // Get authors
  getAuthors: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/authors/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get author details
  getAuthor: async (authorId, signal = null) => {
    try {
      const response = await api.get(`/library/authors/${authorId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get author's books
  getAuthorBooks: async (authorId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/library/authors/${authorId}/books/`, {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== PUBLISHERS ====================
  
  // Get publishers
  getPublishers: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/publishers/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== BOOKS ====================
  
  // Get books
  getBooks: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/books/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get book by ID
  getBook: async (bookId, signal = null) => {
    try {
      const response = await api.get(`/library/books/${bookId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Create book
  createBook: async (bookData, signal = null) => {
    try {
      const response = await api.post('/library/books/', bookData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Update book
  updateBook: async (bookId, bookData, signal = null) => {
    try {
      const response = await api.put(`/library/books/${bookId}/`, bookData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Delete book
  deleteBook: async (bookId, signal = null) => {
    try {
      const response = await api.delete(`/library/books/${bookId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get available books
  getAvailableBooks: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/books/available/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get popular books
  getPopularBooks: async (signal = null) => {
    try {
      const response = await api.get('/library/books/popular/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get new arrivals
  getNewArrivals: async (signal = null) => {
    try {
      const response = await api.get('/library/books/new_arrivals/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get book copies
  getBookCopies: async (bookId, signal = null) => {
    try {
      const response = await api.get(`/library/books/${bookId}/copies/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get book borrow history
  getBookBorrowHistory: async (bookId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/library/books/${bookId}/borrow_history/`, {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get book reviews
  getBookReviews: async (bookId, params = {}, signal = null) => {
    try {
      const response = await api.get(`/library/books/${bookId}/reviews/`, {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Add book review
  addBookReview: async (bookId, reviewData, signal = null) => {
    try {
      const response = await api.post(`/library/books/${bookId}/add_review/`, reviewData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Reserve book
  reserveBook: async (bookId, signal = null) => {
    try {
      const response = await api.post(`/library/books/${bookId}/reserve/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== BORROWING ====================
  
  // Get borrow records
  getBorrowRecords: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/borrows/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Borrow a book
  borrowBook: async (borrowData, signal = null) => {
    try {
      const response = await api.post('/library/borrows/borrow/', borrowData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Return a book
  returnBook: async (borrowId, returnData, signal = null) => {
    try {
      const response = await api.post(`/library/borrows/${borrowId}/return_book/`, returnData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Renew a book
  renewBook: async (borrowId, signal = null) => {
    try {
      const response = await api.post(`/library/borrows/${borrowId}/renew/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get overdue books
  getOverdueBooks: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/borrows/overdue/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get current borrows
  getCurrentBorrows: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/borrows/current/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Pay fine
  payFine: async (borrowId, signal = null) => {
    try {
      const response = await api.post(`/library/borrows/${borrowId}/pay_fine/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== REVIEWS ====================
  
  // Get reviews
  getReviews: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/reviews/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Vote review as helpful
  voteHelpfulReview: async (reviewId, signal = null) => {
    try {
      const response = await api.post(`/library/reviews/${reviewId}/vote_helpful/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Approve review (librarian only)
  approveReview: async (reviewId, signal = null) => {
    try {
      const response = await api.post(`/library/reviews/${reviewId}/approve/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== READING LISTS ====================
  
  // Get reading lists
  getReadingLists: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/reading-lists/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Add book to reading list
  addToReadingList: async (listId, bookData, signal = null) => {
    try {
      const response = await api.post(`/library/reading-lists/${listId}/add_book/`, bookData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Remove book from reading list
  removeFromReadingList: async (listId, bookData, signal = null) => {
    try {
      const response = await api.post(`/library/reading-lists/${listId}/remove_book/`, bookData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Mark book as completed
  markBookCompleted: async (listId, bookData, signal = null) => {
    try {
      const response = await api.post(`/library/reading-lists/${listId}/mark_completed/`, bookData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== RESERVATIONS ====================
  
  // Get reservations
  getReservations: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/reservations/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Create reservation
  createReservation: async (reservationData, signal = null) => {
    try {
      const response = await api.post('/library/reservations/reserve/', reservationData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Cancel reservation
  cancelReservation: async (reservationId, signal = null) => {
    try {
      const response = await api.post(`/library/reservations/${reservationId}/cancel/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Fulfill reservation (librarian only)
  fulfillReservation: async (reservationId, signal = null) => {
    try {
      const response = await api.post(`/library/reservations/${reservationId}/fulfill/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== DIGITAL RESOURCES ====================
  
  // Get digital resources
  getDigitalResources: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/digital-resources/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Download digital resource
  downloadDigitalResource: async (resourceId, signal = null) => {
    try {
      const response = await api.post(`/library/digital-resources/${resourceId}/download/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // View digital resource (increment view count)
  viewDigitalResource: async (resourceId, signal = null) => {
    try {
      const response = await api.post(`/library/digital-resources/${resourceId}/view/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get popular digital resources
  getPopularDigitalResources: async (signal = null) => {
    try {
      const response = await api.get('/library/digital-resources/popular/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get resources by type
  getResourcesByType: async (signal = null) => {
    try {
      const response = await api.get('/library/digital-resources/by_type/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== TEACHER RESOURCES ====================
  
  // Get teacher resources
  getTeacherResources: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/teacher-resources/', { 
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      console.warn('Teacher resources API Error - returning empty data:', error);
      return {
        success: true,
        data: { results: [], count: 0 },
        status: 200
      };
    }
  },

  // Get teacher resources by subject
  getTeacherResourcesBySubject: async (signal = null) => {
    try {
      const response = await api.get('/library/teacher-resources/by_subject/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get my teacher resources
  getMyTeacherResources: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/teacher-resources/my_resources/', { 
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Download teacher resource
  downloadTeacherResource: async (resourceId, signal = null) => {
    try {
      const response = await api.post(`/library/teacher-resources/${resourceId}/download/`, {}, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Create teacher resource
  createTeacherResource: async (resourceData, signal = null) => {
    try {
      const response = await api.post('/library/teacher-resources/', resourceData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get popular teacher resources
  getPopularTeacherResources: async (signal = null) => {
    try {
      const response = await api.get('/library/teacher-resources/popular/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== STATISTICS ====================
  
  // Get library statistics
  getLibraryStats: async (signal = null) => {
    try {
      const response = await api.get('/library/stats/overall/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get user library statistics
  getUserLibraryStats: async (signal = null) => {
    try {
      const response = await api.get('/library/stats/user/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get daily statistics
  getDailyStats: async (params = {}, signal = null) => {
    try {
      const response = await api.get('/library/stats/daily/', {
        params,
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== SEARCH ====================
  
  // Advanced book search
  searchBooks: async (searchData, signal = null) => {
    try {
      const response = await api.post('/library/search/books/', searchData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Advanced digital resource search
  searchDigitalResources: async (searchData, signal = null) => {
    try {
      const response = await api.post('/library/search/digital/', searchData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== BULK OPERATIONS ====================
  
  // Bulk import books
  bulkImportBooks: async (booksData, signal = null) => {
    try {
      const response = await api.post('/library/bulk/import/', booksData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Bulk update books
  bulkUpdateBooks: async (updateData, signal = null) => {
    try {
      const response = await api.post('/library/bulk/update/', updateData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Export books
  exportBooks: async (format = 'json', params = {}, signal = null) => {
    try {
      const response = await api.get('/library/export/books/', {
        params: { format, ...params },
        responseType: format === 'json' ? 'json' : 'blob',
        signal
      });
      return {
        success: true,
        data: response.data,
        status: response.status,
        format: format
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== NOTIFICATIONS ====================
  
  // Get library notifications
  getLibraryNotifications: async (signal = null) => {
    try {
      const response = await api.get('/library/notifications/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== RECOMMENDATIONS ====================
  
  // Get book recommendations
  getBookRecommendations: async (signal = null) => {
    try {
      const response = await api.get('/library/recommendations/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== USER ENDPOINTS ====================
  
  // Get user's current borrows
  getUserCurrentBorrows: async (signal = null) => {
    try {
      const response = await api.get('/library/user/current-borrows/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get user's reading progress
  getUserReadingProgress: async (signal = null) => {
    try {
      const response = await api.get('/library/user/reading-progress/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== LIBRARIAN ENDPOINTS ====================
  
  // Get overdue list (librarian only)
  getOverdueList: async (signal = null) => {
    try {
      const response = await api.get('/library/librarian/overdue-list/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get fine management (librarian only)
  getFineManagement: async (signal = null) => {
    try {
      const response = await api.get('/library/librarian/fine-management/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Pay fine (librarian only)
  processFinePayment: async (paymentData, signal = null) => {
    try {
      const response = await api.post('/library/librarian/fine-management/', paymentData, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get inventory check (librarian only)
  getInventoryCheck: async (signal = null) => {
    try {
      const response = await api.get('/library/librarian/inventory-check/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // ==================== PUBLIC ENDPOINTS ====================
  
  // Get public catalog
  getPublicCatalog: async (signal = null) => {
    try {
      const response = await api.get('/library/public/catalog/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get public book details
  getPublicBookDetail: async (bookId, signal = null) => {
    try {
      const response = await api.get(`/library/public/books/${bookId}/`, { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  },

  // Get public digital resources
  getPublicDigitalResources: async (signal = null) => {
    try {
      const response = await api.get('/library/public/digital/', { signal });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleError(error);
    }
  }
};

// ==================== LIBRARY CONSTANTS ====================

export const LIBRARY_CONSTANTS = {
  BOOK_TYPES: {
    TEXTBOOK: 'textbook',
    REFERENCE: 'reference',
    FICTION: 'fiction',
    NON_FICTION: 'non_fiction',
    BIOGRAPHY: 'biography',
    MAGAZINE: 'magazine',
    JOURNAL: 'journal',
    RESEARCH: 'research',
    THESIS: 'thesis',
    PERIODICAL: 'periodical'
  },
  
  BOOK_FORMATS: {
    HARDCOVER: 'hardcover',
    PAPERBACK: 'paperback',
    SPIRAL: 'spiral',
    EBOOK: 'ebook',
    AUDIOBOOK: 'audiobook'
  },
  
  LANGUAGES: {
    ENGLISH: 'en',
    KISWAHILI: 'sw',
    FRENCH: 'fr',
    ARABIC: 'ar',
    OTHER: 'other'
  },
  
  CURRICULUM_TYPES: {
    CBC: 'cbc',
    EIGHT_FOUR_FOUR: '8-4-4',
    IGCSE: 'igcse',
    IB: 'ib'
  },
  
  RESOURCE_TYPES: {
    EBOOK: 'ebook',
    AUDIOBOOK: 'audiobook',
    VIDEO: 'video',
    AUDIO: 'audio',
    DOCUMENT: 'document',
    PRESENTATION: 'presentation',
    WEBSITE: 'website',
    DATABASE: 'database'
  },
  
  TEACHER_RESOURCE_TYPES: {
    LESSON_PLAN: 'lesson_plan',
    WORKSHEET: 'worksheet',
    ASSESSMENT: 'assessment',
    CURRICULUM_GUIDE: 'curriculum_guide',
    TEACHING_AID: 'teaching_aid',
    PROFESSIONAL_DEVELOPMENT: 'professional_development'
  },
  
  BORROW_STATUS: {
    PENDING: 'pending',
    APPROVED: 'approved',
    ISSUED: 'issued',
    OVERDUE: 'overdue',
    RETURNED: 'returned',
    LOST: 'lost',
    DAMAGED: 'damaged'
  },
  
  RESERVATION_STATUS: {
    PENDING: 'pending',
    CONFIRMED: 'confirmed',
    READY: 'ready',
    CANCELLED: 'cancelled',
    EXPIRED: 'expired'
  },
  
  BOOK_CONDITION: {
    NEW: 'new',
    GOOD: 'good',
    FAIR: 'fair',
    POOR: 'poor',
    DAMAGED: 'damaged'
  },
  
  // Loan periods (in days)
  LOAN_PERIODS: {
    STUDENT: 14,
    TEACHER: 30,
    STAFF: 21,
    DEFAULT: 14
  },
  
  // Fine rates (per day)
  FINE_RATES: {
    STUDENT: 10,
    TEACHER: 5,
    STAFF: 7,
    DEFAULT: 10
  },
  
  // Maximum renewals
  MAX_RENEWALS: {
    STUDENT: 2,
    TEACHER: 3,
    STAFF: 2,
    DEFAULT: 2
  }
};

export default libraryAPI;