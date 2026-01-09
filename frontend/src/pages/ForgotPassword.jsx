import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle password reset logic here
    setIsSubmitted(true);
  };

  return (
    <div className="container-fluid py-5 bg-light min-vh-100">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-4">
          <div className="card shadow">
            <div className="card-body p-4">
              <div className="text-center mb-4">
                <h2 className="card-title">Reset Password</h2>
                <p className="text-muted">
                  {isSubmitted 
                    ? 'Check your email for reset instructions' 
                    : 'Enter your email to reset your password'
                  }
                </p>
              </div>

              {!isSubmitted ? (
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">Email Address</label>
                    <input
                      type="email"
                      className="form-control"
                      id="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <button type="submit" className="btn btn-primary w-100 mb-3">
                    Send Reset Link
                  </button>
                </form>
              ) : (
                <div className="text-center">
                  <i className="bi bi-envelope-check display-4 text-success mb-3"></i>
                  <p>We've sent password reset instructions to your email.</p>
                </div>
              )}

              <div className="text-center">
                <Link to="/login" className="text-decoration-none">
                  <i className="bi bi-arrow-left me-1"></i>
                  Back to Login
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;