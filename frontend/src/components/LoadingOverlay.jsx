import React from 'react';
import PropTypes from 'prop-types';
import './LoadingOverlay.css';

const LoadingOverlay = ({
  message = 'Loading...',
  submessage = '',
  show = true,
  dark = false,
  spinnerColor = 'primary',
  spinnerSize = 'medium',
  showProgress = false,
  progress = 0,
  indeterminate = true,
  showCancel = false,
  onCancel,
  showDots = false,
  showPercentage = false,
  fadeIn = true,
  children
}) => {
  if (!show) return null;

  const spinnerClasses = `loading-spinner ${spinnerColor} ${spinnerSize}`;
  const overlayClasses = `loading-overlay ${dark ? 'dark' : ''} ${fadeIn ? 'fade-in' : ''}`;

  return (
    <div className={overlayClasses}>
      <div className="loading-overlay-content">
        <div className={spinnerClasses}></div>
        
        {message && <div className="loading-message">{message}</div>}
        
        {submessage && <div className="loading-submessage">{submessage}</div>}
        
        {showProgress && (
          <div className="loading-progress">
            <div 
              className={`loading-progress-bar ${indeterminate ? 'indeterminate' : ''}`}
              style={{ width: indeterminate ? '30%' : `${Math.min(progress, 100)}%` }}
            ></div>
          </div>
        )}
        
        {showDots && (
          <div className="loading-dots">
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
          </div>
        )}
        
        {showPercentage && !indeterminate && (
          <div className="loading-percentage">{Math.round(progress)}%</div>
        )}
        
        {showCancel && onCancel && (
          <button 
            className="loading-cancel-btn"
            onClick={onCancel}
            type="button"
          >
            Cancel
          </button>
        )}
        
        {children}
      </div>
    </div>
  );
};

LoadingOverlay.propTypes = {
  message: PropTypes.string,
  submessage: PropTypes.string,
  show: PropTypes.bool,
  dark: PropTypes.bool,
  spinnerColor: PropTypes.oneOf(['primary', 'success', 'warning', 'danger', 'light']),
  spinnerSize: PropTypes.oneOf(['small', 'medium', 'large']),
  showProgress: PropTypes.bool,
  progress: PropTypes.number,
  indeterminate: PropTypes.bool,
  showCancel: PropTypes.bool,
  onCancel: PropTypes.func,
  showDots: PropTypes.bool,
  showPercentage: PropTypes.bool,
  fadeIn: PropTypes.bool,
  children: PropTypes.node
};

export default LoadingOverlay;