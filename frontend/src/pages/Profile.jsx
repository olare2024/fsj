// src/pages/Profile.js - COMPLETE REWRITTEN VERSION
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import '../assets/css/Profile.css';

function Profile() {
  const navigate = useNavigate();
  const { currentUser, updateProfile, logout, hasRole, getProfileCompletionPercentage } = useAuth();
  
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    address: '',
    bio: '',
    date_of_birth: '',
    gender: '',
    profile_picture: null
  });
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [profileStats, setProfileStats] = useState({
    completion: 0,
    lastUpdated: '',
    daysSinceUpdate: 0
  });

  // Initialize form data from current user
  useEffect(() => {
    if (currentUser) {
      initializeFormData();
      calculateProfileStats();
    }
  }, [currentUser]);

  const initializeFormData = () => {
    setFormData({
      first_name: currentUser.first_name || currentUser.firstName || '',
      last_name: currentUser.last_name || currentUser.lastName || '',
      email: currentUser.email || '',
      phone_number: currentUser.phone_number || currentUser.phone || '',
      address: currentUser.address || '',
      bio: currentUser.bio || '',
      date_of_birth: currentUser.date_of_birth 
        ? formatDateForInput(currentUser.date_of_birth) 
        : '',
      gender: currentUser.gender || '',
      profile_picture: currentUser.profile_picture || null
    });

    // Set image preview if profile picture exists
    if (currentUser.profile_picture) {
      setImagePreview(currentUser.profile_picture);
    }

    setIsLoading(false);
  };

  const calculateProfileStats = () => {
    const completion = getProfileCompletionPercentage();
    const lastUpdated = currentUser.last_profile_update || currentUser.updated_at;
    
    let daysSinceUpdate = 0;
    if (lastUpdated) {
      const lastUpdateDate = new Date(lastUpdated);
      const today = new Date();
      daysSinceUpdate = Math.floor((today - lastUpdateDate) / (1000 * 60 * 60 * 24));
    }

    setProfileStats({
      completion,
      lastUpdated: lastUpdated ? formatDateDisplay(lastUpdated) : 'Never',
      daysSinceUpdate
    });
  };

  const formatDateForInput = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  };

  const formatDateDisplay = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.match('image/jpeg|image/png|image/gif')) {
      setErrors(prev => ({
        ...prev,
        profile_picture: 'Please select a valid image file (JPEG, PNG, GIF)'
      }));
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrors(prev => ({
        ...prev,
        profile_picture: 'Image size should be less than 5MB'
      }));
      return;
    }

    setProfileImage(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
    
    // Clear any previous errors
    setErrors(prev => ({
      ...prev,
      profile_picture: null
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields validation
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    if (!formData.phone_number.trim()) {
      newErrors.phone_number = 'Phone number is required';
    }

    // Student-specific validation
    if (hasRole('student')) {
      if (!formData.date_of_birth) {
        newErrors.date_of_birth = 'Date of birth is required for students';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setIsLoading(true);
      setSuccessMessage('');

      // Prepare form data for API
      const submitData = new FormData();
      
      // Add all form fields
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== undefined) {
          submitData.append(key, formData[key]);
        }
      });

      // Add profile picture if changed
      if (profileImage) {
        submitData.append('profile_picture', profileImage);
      }

      // Call API to update profile
      const response = await api.patch('/auth/profile/', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data) {
        // Update AuthContext
        updateProfile(response.data);
        
        setSuccessMessage('Profile updated successfully!');
        setIsEditing(false);
        setProfileImage(null);
        
        // Refresh profile stats
        calculateProfileStats();
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
      }

    } catch (error) {
      console.error('Error updating profile:', error);
      
      // Handle validation errors from backend
      if (error.response?.data) {
        const backendErrors = error.response.data;
        const formattedErrors = {};
        
        Object.keys(backendErrors).forEach(key => {
          if (Array.isArray(backendErrors[key])) {
            formattedErrors[key] = backendErrors[key][0];
          } else {
            formattedErrors[key] = backendErrors[key];
          }
        });
        
        setErrors(formattedErrors);
      } else {
        setErrors({ 
          general: 'Failed to update profile. Please try again.' 
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setImagePreview(currentUser.profile_picture || null);
    setProfileImage(null);
    setErrors({});
    initializeFormData();
  };

  const handleDeleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        setIsLoading(true);
        await api.delete('/auth/profile/');
        logout('Account deleted successfully');
      } catch (error) {
        console.error('Error deleting account:', error);
        setErrors({ 
          general: 'Failed to delete account. Please contact support.' 
        });
        setIsLoading(false);
      }
    }
  };

  const renderField = (label, name, type = 'text', options = {}) => {
    const isRequired = ['first_name', 'last_name', 'email', 'phone_number'].includes(name);
    const isStudentRequired = hasRole('student') && name === 'date_of_birth';
    
    return (
      <div className="mb-3">
        <label className="form-label">
          {label} {isRequired || isStudentRequired ? '*' : ''}
        </label>
        {type === 'textarea' ? (
          <textarea
            className={`form-control ${errors[name] ? 'is-invalid' : ''}`}
            name={name}
            value={formData[name] || ''}
            onChange={handleInputChange}
            disabled={!isEditing || isLoading}
            rows={options.rows || 3}
            placeholder={options.placeholder || ''}
          />
        ) : type === 'select' ? (
          <select
            className={`form-select ${errors[name] ? 'is-invalid' : ''}`}
            name={name}
            value={formData[name] || ''}
            onChange={handleInputChange}
            disabled={!isEditing || isLoading}
          >
            <option value="">Select {label.toLowerCase()}</option>
            {options.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        ) : (
          <input
            type={type}
            className={`form-control ${errors[name] ? 'is-invalid' : ''}`}
            name={name}
            value={formData[name] || ''}
            onChange={handleInputChange}
            disabled={!isEditing || isLoading}
            placeholder={options.placeholder || ''}
          />
        )}
        {errors[name] && (
          <div className="invalid-feedback">{errors[name]}</div>
        )}
      </div>
    );
  };

  const renderProfileImage = () => (
    <div className="profile-image-section">
      <div className="profile-image-container">
        {imagePreview ? (
          <img 
            src={imagePreview} 
            alt="Profile" 
            className="profile-image"
          />
        ) : (
          <div className="profile-image-placeholder">
            {getInitials()}
          </div>
        )}
        {isEditing && (
          <div className="profile-image-actions">
            <label className="btn btn-sm btn-outline-primary mb-2">
              <i className="bi bi-camera"></i> Change Photo
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="d-none"
                disabled={isLoading}
              />
            </label>
            {imagePreview && (
              <button
                type="button"
                className="btn btn-sm btn-outline-danger"
                onClick={() => {
                  setImagePreview(null);
                  setProfileImage(null);
                }}
                disabled={isLoading}
              >
                <i className="bi bi-trash"></i> Remove
              </button>
            )}
          </div>
        )}
      </div>
      {errors.profile_picture && (
        <div className="text-danger small mt-2">{errors.profile_picture}</div>
      )}
    </div>
  );

  const getInitials = () => {
    const firstName = formData.first_name || currentUser?.first_name || '';
    const lastName = formData.last_name || currentUser?.last_name || '';
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const renderProfileStats = () => (
    <div className="profile-stats">
      <h5 className="mb-3">Profile Statistics</h5>
      
      <div className="progress mb-3" style={{ height: '10px' }}>
        <div 
          className={`progress-bar ${profileStats.completion >= 90 ? 'bg-success' : profileStats.completion >= 70 ? 'bg-warning' : 'bg-danger'}`}
          role="progressbar"
          style={{ width: `${profileStats.completion}%` }}
          aria-valuenow={profileStats.completion}
          aria-valuemin="0"
          aria-valuemax="100"
        ></div>
      </div>
      <p className="text-center mb-0">
        <strong>{profileStats.completion}%</strong> Complete
      </p>
      
      <div className="mt-4">
        <p className="mb-1">
          <i className="bi bi-calendar me-2"></i>
          Last updated: {profileStats.lastUpdated}
        </p>
        {profileStats.daysSinceUpdate > 30 && (
          <p className="text-warning mb-0">
            <i className="bi bi-exclamation-triangle me-2"></i>
            Profile hasn't been updated in {profileStats.daysSinceUpdate} days
          </p>
        )}
      </div>
    </div>
  );

  if (isLoading && !currentUser) {
    return (
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-3">Loading profile...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-5">
      <div className="row">
        <div className="col-lg-8">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h1 className="h2 mb-0">My Profile</h1>
            <div className="d-flex gap-2">
              <Link to="/dashboard" className="btn btn-outline-primary">
                <i className="bi bi-arrow-left me-2"></i>Back to Dashboard
              </Link>
              {!isEditing ? (
                <button 
                  className="btn btn-primary"
                  onClick={() => setIsEditing(true)}
                  disabled={isLoading}
                >
                  <i className="bi bi-pencil me-2"></i>Edit Profile
                </button>
              ) : null}
            </div>
          </div>

          {successMessage && (
            <div className="alert alert-success alert-dismissible fade show" role="alert">
              <i className="bi bi-check-circle me-2"></i>
              {successMessage}
              <button 
                type="button" 
                className="btn-close" 
                onClick={() => setSuccessMessage('')}
              ></button>
            </div>
          )}

          {errors.general && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              <i className="bi bi-exclamation-triangle me-2"></i>
              {errors.general}
              <button 
                type="button" 
                className="btn-close" 
                onClick={() => setErrors(prev => ({ ...prev, general: null }))}
              ></button>
            </div>
          )}

          <div className="card mb-4">
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-4">
                    {renderProfileImage()}
                  </div>
                  <div className="col-md-8">
                    <div className="row">
                      <div className="col-md-6">
                        {renderField('First Name', 'first_name', 'text', {
                          placeholder: 'Enter your first name'
                        })}
                      </div>
                      <div className="col-md-6">
                        {renderField('Last Name', 'last_name', 'text', {
                          placeholder: 'Enter your last name'
                        })}
                      </div>
                    </div>

                    <div className="row">
                      <div className="col-md-6">
                        {renderField('Email Address', 'email', 'email', {
                          placeholder: 'Enter your email address'
                        })}
                      </div>
                      <div className="col-md-6">
                        {renderField('Phone Number', 'phone_number', 'tel', {
                          placeholder: 'Enter your phone number'
                        })}
                      </div>
                    </div>

                    {hasRole('student') && (
                      <div className="row">
                        <div className="col-md-6">
                          {renderField('Date of Birth', 'date_of_birth', 'date')}
                        </div>
                        <div className="col-md-6">
                          {renderField('Gender', 'gender', 'select', {
                            options: [
                              { value: 'male', label: 'Male' },
                              { value: 'female', label: 'Female' },
                              { value: 'other', label: 'Other' },
                              { value: 'prefer_not_to_say', label: 'Prefer not to say' }
                            ]
                          })}
                        </div>
                      </div>
                    )}

                    {renderField('Address', 'address', 'textarea', {
                      placeholder: 'Enter your address',
                      rows: 2
                    })}

                    {renderField('Bio', 'bio', 'textarea', {
                      placeholder: 'Tell us about yourself...',
                      rows: 4
                    })}

                    {isEditing && (
                      <div className="d-flex gap-2 mt-4">
                        <button 
                          type="submit" 
                          className="btn btn-success"
                          disabled={isLoading}
                        >
                          {isLoading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2"></span>
                              Saving...
                            </>
                          ) : (
                            <>
                              <i className="bi bi-check-circle me-2"></i>
                              Save Changes
                            </>
                          )}
                        </button>
                        <button 
                          type="button" 
                          className="btn btn-outline-secondary"
                          onClick={handleCancel}
                          disabled={isLoading}
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </form>
            </div>
          </div>

          {/* Additional Information Section */}
          <div className="row">
            {hasRole('student') && (
              <div className="col-md-6 mb-4">
                <div className="card h-100">
                  <div className="card-header">
                    <h6 className="mb-0">Academic Information</h6>
                  </div>
                  <div className="card-body">
                    <p><strong>Admission Number:</strong> {currentUser?.admission_number || 'N/A'}</p>
                    <p><strong>Grade Level:</strong> {currentUser?.grade_level || 'N/A'}</p>
                    <p><strong>Current Class:</strong> {currentUser?.current_class || 'N/A'}</p>
                    <Link to="/academics" className="btn btn-sm btn-outline-primary">
                      View Academic Details
                    </Link>
                  </div>
                </div>
              </div>
            )}

            {hasRole('teacher') && (
              <div className="col-md-6 mb-4">
                <div className="card h-100">
                  <div className="card-header">
                    <h6 className="mb-0">Professional Information</h6>
                  </div>
                  <div className="card-body">
                    <p><strong>Staff ID:</strong> {currentUser?.staff_id || 'N/A'}</p>
                    <p><strong>Department:</strong> {currentUser?.department || 'N/A'}</p>
                    <p><strong>Designation:</strong> {currentUser?.designation || 'N/A'}</p>
                    <Link to="/teacher-portal" className="btn btn-sm btn-outline-primary">
                      View Teacher Portal
                    </Link>
                  </div>
                </div>
              </div>
            )}

            <div className="col-md-6 mb-4">
              <div className="card h-100">
                <div className="card-header">
                  <h6 className="mb-0">Account Security</h6>
                </div>
                <div className="card-body">
                  <div className="d-grid gap-2">
                    <Link to="/change-password" className="btn btn-outline-primary">
                      <i className="bi bi-key me-2"></i>Change Password
                    </Link>
                    <Link to="/two-factor" className="btn btn-outline-primary">
                      <i className="bi bi-shield-lock me-2"></i>Two-Factor Authentication
                    </Link>
                    <button 
                      className="btn btn-outline-danger"
                      onClick={handleDeleteAccount}
                      disabled={isLoading}
                    >
                      <i className="bi bi-trash me-2"></i>Delete Account
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card mb-4">
            <div className="card-header">
              <h5 className="mb-0">Profile Completion</h5>
            </div>
            <div className="card-body">
              {renderProfileStats()}
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-header">
              <h5 className="mb-0">Quick Links</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <Link to="/settings" className="btn btn-outline-primary">
                  <i className="bi bi-gear me-2"></i>Account Settings
                </Link>
                <Link to="/notifications" className="btn btn-outline-primary">
                  <i className="bi bi-bell me-2"></i>Notifications
                </Link>
                <Link to="/privacy" className="btn btn-outline-primary">
                  <i className="bi bi-shield me-2"></i>Privacy Settings
                </Link>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Account Information</h5>
            </div>
            <div className="card-body">
              <table className="table table-sm">
                <tbody>
                  <tr>
                    <td><strong>Account Type:</strong></td>
                    <td>{currentUser?.role || 'N/A'}</td>
                  </tr>
                  <tr>
                    <td><strong>Member Since:</strong></td>
                    <td>{currentUser?.date_joined ? formatDateDisplay(currentUser.date_joined) : 'N/A'}</td>
                  </tr>
                  <tr>
                    <td><strong>Last Login:</strong></td>
                    <td>{currentUser?.last_login ? formatDateDisplay(currentUser.last_login) : 'N/A'}</td>
                  </tr>
                  <tr>
                    <td><strong>Status:</strong></td>
                    <td>
                      {currentUser?.is_verified ? (
                        <span className="badge bg-success">Verified</span>
                      ) : (
                        <span className="badge bg-warning">Unverified</span>
                      )}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;