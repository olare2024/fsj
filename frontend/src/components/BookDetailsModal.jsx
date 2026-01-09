import React, { useState, useEffect } from 'react';
import { Modal, Button } from 'react-bootstrap';
import { libraryAPI } from '../api/libraryAPI';

function BookDetailsModal({ bookId, show, onHide }) {
  const [book, setBook] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (show && bookId) {
      fetchBookDetails();
    }
  }, [show, bookId]);

  const fetchBookDetails = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await libraryAPI.getBook(bookId);
      if (response.success) {
        setBook(response.data);
      } else {
        setError(response.error?.message || 'Failed to load book details');
      }
    } catch (error) {
      setError('Error loading book details');
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Book Details</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {isLoading && (
          <div className="text-center py-4">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        )}
        
        {error && (
          <div className="alert alert-danger">{error}</div>
        )}
        
        {book && !isLoading && !error && (
          <div className="row">
            <div className="col-md-4">
              {book.cover_image && (
                <img 
                  src={book.cover_image} 
                  alt={book.title}
                  className="img-fluid rounded"
                />
              )}
            </div>
            <div className="col-md-8">
              <h4>{book.title}</h4>
              <p className="text-muted">by {book.author}</p>
              
              <div className="mb-3">
                <strong>ISBN:</strong> {book.isbn || 'N/A'}
              </div>
              
              <div className="mb-3">
                <strong>Publisher:</strong> {book.publisher || 'N/A'}
              </div>
              
              <div className="mb-3">
                <strong>Publication Year:</strong> {book.publication_year || 'N/A'}
              </div>
              
              <div className="mb-3">
                <strong>Category:</strong> {book.category || 'N/A'}
              </div>
              
              <div className="mb-3">
                <strong>Location:</strong> {book.location || 'N/A'}
              </div>
              
              <div className="mb-3">
                <strong>Available Copies:</strong> {book.available_copies || 0} of {book.total_copies || 0}
              </div>
              
              {book.description && (
                <div className="mb-3">
                  <strong>Description:</strong>
                  <p>{book.description}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default BookDetailsModal;