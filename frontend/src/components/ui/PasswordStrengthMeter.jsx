import React from 'react';
import { ProgressBar, ListGroup, Badge } from 'react-bootstrap';

const PasswordStrengthMeter = ({ strength, messages }) => {
  const getVariant = (strength) => {
    if (strength >= 80) return 'success';
    if (strength >= 60) return 'info';
    if (strength >= 40) return 'warning';
    return 'danger';
  };

  const getLabel = (strength) => {
    if (strength >= 80) return 'Strong';
    if (strength >= 60) return 'Good';
    if (strength >= 40) return 'Fair';
    return 'Weak';
  };

  return (
    <div className="mt-2">
      <div className="d-flex justify-content-between align-items-center mb-1">
        <small className="text-muted">Password Strength</small>
        <Badge bg={getVariant(strength)}>{getLabel(strength)}</Badge>
      </div>
      <ProgressBar 
        now={strength} 
        variant={getVariant(strength)}
        className="mb-2"
      />
      {messages.length > 0 && (
        <ListGroup variant="flush">
          {messages.map((message, index) => (
            <ListGroup.Item 
              key={index} 
              className="p-1 border-0"
              style={{ fontSize: '0.8rem' }}
            >
              <i className="fas fa-exclamation-circle text-warning me-2"></i>
              {message}
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
    </div>
  );
};

export default PasswordStrengthMeter;