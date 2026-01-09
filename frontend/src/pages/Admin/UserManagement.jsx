import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import adminAPI from '../../services/adminAPI';
import debounce from 'lodash/debounce';
import { format } from 'date-fns';

function UserManagement() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('all');
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0,
    totalPages: 1
  });

  // Advanced filter states
  const [filters, setFilters] = useState({
    status: '',
    curriculum: '',
    department: '',
    grade: '',
    dateJoinedFrom: '',
    dateJoinedTo: '',
    isVerified: '',
    isSuspended: '',
    house: '',
    gender: '',
    nationality: ''
  });

  // Role definitions from Django model
  const ROLE_CONFIG = {
    admin: { label: 'Administrator', color: 'bg-danger', icon: 'bi-shield-check' },
    head_teacher: { label: 'Head Teacher', color: 'bg-purple', icon: 'bi-award' },
    curriculum_coordinator: { label: 'Curriculum Coordinator', color: 'bg-info', icon: 'bi-book' },
    teacher: { label: 'Teacher', color: 'bg-primary', icon: 'bi-person-badge' },
    office_staff: { label: 'Office Staff', color: 'bg-secondary', icon: 'bi-briefcase' },
    student: { label: 'Student', color: 'bg-success', icon: 'bi-person' },
    parent: { label: 'Parent', color: 'bg-warning', icon: 'bi-people-fill' },
    librarian: { label: 'Librarian', color: 'bg-orange', icon: 'bi-book-half' },
    accountant: { label: 'Accountant', color: 'bg-teal', icon: 'bi-calculator' },
    it_support: { label: 'IT Support', color: 'bg-indigo', icon: 'bi-laptop' },
    counselor: { label: 'Counselor', color: 'bg-pink', icon: 'bi-heart' }
  };

  const CURRICULUM_CONFIG = {
    cbc: { label: 'CBC', color: 'bg-success' },
    icse: { label: 'ICSE', color: 'bg-primary' },
    american: { label: 'American', color: 'bg-danger' },
    british: { label: 'British', color: 'bg-info' },
    montessori: { label: 'Montessori', color: 'bg-warning' },
    combined: { label: 'Combined', color: 'bg-secondary' },
    igcse: { label: 'IGCSE', color: 'bg-purple' },
    ib: { label: 'IB', color: 'bg-teal' }
  };

  const HOUSE_CHOICES = {
    unity: 'Unity House',
    courage: 'Courage House',
    wisdom: 'Wisdom House',
    success: 'Success House',
    excellence: 'Excellence House',
    integrity: 'Integrity House',
    bravery: 'Bravery House',
    honor: 'Honor House'
  };

  const GENDER_CHOICES = {
    male: 'Male',
    female: 'Female',
    other: 'Other',
    prefer_not_to_say: 'Prefer not to say'
  };

  const BLOOD_GROUP_CHOICES = {
    a_positive: 'A+',
    a_negative: 'A-',
    b_positive: 'B+',
    b_negative: 'B-',
    ab_positive: 'AB+',
    ab_negative: 'AB-',
    o_positive: 'O+',
    o_negative: 'O-'
  };

  // Debounced search
  const debouncedSearch = useCallback(
    debounce((term) => {
      setSearchTerm(term);
    }, 300),
    []
  );

  // Fetch users from backend API
  const fetchUsers = useCallback(async (page = 1, filters = {}) => {
    try {
      setLoading(true);
      setError('');
      
      const params = {
        role: activeTab !== 'all' ? activeTab : undefined,
        search: searchTerm,
        page,
        page_size: pagination.pageSize,
        ...filters
      };

      const response = await adminAPI.getUsers(params);

      if (response.success) {
        const usersData = response.data.results || response.data;
        const paginationData = response.data.pagination || {
          page: 1,
          page_size: pagination.pageSize,
          total: usersData.length,
          total_pages: 1
        };

        setUsers(usersData);
        setFilteredUsers(usersData);
        
        setPagination({
          page: paginationData.page,
          pageSize: paginationData.page_size,
          total: paginationData.total,
          totalPages: paginationData.total_pages
        });
      } else {
        setError(response.error?.message || 'Failed to fetch users');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [activeTab, searchTerm, pagination.pageSize]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Search functionality with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      applyFilters();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, filters]);

  const applyFilters = () => {
    let filtered = users;

    // Apply search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(user =>
        user.first_name?.toLowerCase().includes(term) ||
        user.last_name?.toLowerCase().includes(term) ||
        user.email?.toLowerCase().includes(term) ||
        (user.admission_number && user.admission_number.toLowerCase().includes(term)) ||
        (user.staff_id && user.staff_id.toLowerCase().includes(term)) ||
        (user.phone_number && user.phone_number.includes(term))
      );
    }

    // Apply advanced filters
    if (filters.status) {
      filtered = filtered.filter(user => 
        filters.status === 'active' ? user.is_active : !user.is_active
      );
    }

    if (filters.curriculum) {
      filtered = filtered.filter(user => 
        user.primary_curriculum === filters.curriculum
      );
    }

    if (filters.department) {
      filtered = filtered.filter(user => 
        user.department?.toLowerCase().includes(filters.department.toLowerCase())
      );
    }

    if (filters.grade) {
      filtered = filtered.filter(user => 
        user.grade_level?.toLowerCase().includes(filters.grade.toLowerCase())
      );
    }

    if (filters.isVerified !== '') {
      filtered = filtered.filter(user => 
        user.is_verified === (filters.isVerified === 'true')
      );
    }

    if (filters.isSuspended !== '') {
      filtered = filtered.filter(user => 
        user.is_suspended === (filters.isSuspended === 'true')
      );
    }

    if (filters.house) {
      filtered = filtered.filter(user => 
        user.house === filters.house
      );
    }

    if (filters.gender) {
      filtered = filtered.filter(user => 
        user.gender === filters.gender
      );
    }

    if (filters.nationality) {
      filtered = filtered.filter(user => 
        user.nationality?.toLowerCase().includes(filters.nationality.toLowerCase())
      );
    }

    setFilteredUsers(filtered);
  };

  const handleUserSelect = (userId) => {
    setSelectedUsers(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSelectAll = () => {
    if (selectedUsers.length === filteredUsers.length && filteredUsers.length > 0) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(filteredUsers.map(user => user.id));
    }
  };

  const handleStatusChange = async (userId, newStatus) => {
    try {
      setLoading(true);
      
      const response = await adminAPI.updateUser(userId, {
        is_active: newStatus === 'active'
      });

      if (response.success) {
        setUsers(prev => prev.map(user =>
          user.id === userId ? { ...user, ...response.data } : user
        ));
        setSuccess(`User ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully`);
      } else {
        setError(response.error?.message || 'Failed to update user status');
      }
    } catch (error) {
      console.error('Error updating user status:', error);
      setError('Failed to update user status');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkAction = async (action) => {
    if (selectedUsers.length === 0) return;

    try {
      setLoading(true);
      
      let response;
      switch (action) {
        case 'activate':
          response = await adminAPI.bulkUserActions('activate', selectedUsers);
          break;
        case 'deactivate':
          response = await adminAPI.bulkUserActions('deactivate', selectedUsers);
          break;
        case 'approve':
          response = await adminAPI.bulkUserActions('approve', selectedUsers);
          break;
        case 'suspend':
          response = await adminAPI.bulkUserActions('suspend', selectedUsers);
          break;
        case 'delete':
          if (!window.confirm(`Are you sure you want to delete ${selectedUsers.length} users? This action cannot be undone.`)) return;
          response = await adminAPI.bulkUserActions('delete', selectedUsers);
          break;
        default:
          return;
      }

      if (response.success) {
        await fetchUsers();
        setSelectedUsers([]);
        setSuccess(`Bulk ${action} completed successfully for ${selectedUsers.length} users`);
      } else {
        setError(response.error?.message || 'Bulk action failed');
      }
    } catch (error) {
      console.error('Error performing bulk action:', error);
      setError('Failed to perform bulk action');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      setLoading(true);
      
      // Add confirm_password if not present
      const submitData = {
        ...userData,
        confirm_password: userData.confirm_password || userData.password
      };
      
      const response = await adminAPI.createUser(submitData);
      
      if (response.success) {
        setShowAddUserModal(false);
        await fetchUsers();
        setSuccess('User created successfully');
      } else {
        setError(response.error?.message || 'Failed to create user');
      }
    } catch (error) {
      console.error('Error creating user:', error);
      setError('Failed to create user: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (userId, userData) => {
    try {
      setLoading(true);
      
      const response = await adminAPI.updateUser(userId, userData);
      
      if (response.success) {
        setEditingUser(null);
        await fetchUsers();
        setSuccess('User updated successfully');
      } else {
        setError(response.error?.message || 'Failed to update user');
      }
    } catch (error) {
      console.error('Error updating user:', error);
      setError('Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;

    try {
      setLoading(true);
      
      const response = await adminAPI.deleteUser(userId);
      
      if (response.success) {
        await fetchUsers();
        setSuccess('User deleted successfully');
      } else {
        setError(response.error?.message || 'Failed to delete user');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Failed to delete user');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (userId) => {
    if (!window.confirm('Reset password for this user? They will receive an email with instructions.')) return;

    try {
      setLoading(true);
      const response = await adminAPI.resetUserPassword(userId);
      
      if (response.success) {
        setSuccess('Password reset email sent successfully');
      } else {
        setError(response.error?.message || 'Failed to reset password');
      }
    } catch (error) {
      console.error('Error resetting password:', error);
      setError('Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  const handleSendVerification = async (userId, type = 'email') => {
    try {
      setLoading(true);
      const response = await adminAPI.sendVerification(userId, type);
      
      if (response.success) {
        setSuccess(`${type === 'email' ? 'Email' : 'Phone'} verification sent successfully`);
      } else {
        setError(response.error?.message || `Failed to send ${type} verification`);
      }
    } catch (error) {
      console.error('Error sending verification:', error);
      setError(`Failed to send ${type} verification`);
    } finally {
      setLoading(false);
    }
  };

  const getRoleStats = () => {
    const stats = {};
    Object.keys(ROLE_CONFIG).forEach(role => {
      stats[role] = users.filter(user => user.role === role).length;
    });
    stats.total = users.length;
    stats.active = users.filter(user => user.is_active).length;
    stats.inactive = users.filter(user => !user.is_active).length;
    stats.verified = users.filter(user => user.is_verified).length;
    stats.suspended = users.filter(user => user.is_suspended).length;
    
    return stats;
  };

  const stats = getRoleStats();

  const formatUserData = (user) => {
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
    const roleConfig = ROLE_CONFIG[user.role] || ROLE_CONFIG.student;
    const curriculumConfig = user.primary_curriculum ? CURRICULUM_CONFIG[user.primary_curriculum] : null;
    
    return {
      ...user,
      name: fullName,
      displayRole: roleConfig.label,
      roleColor: roleConfig.color,
      roleIcon: roleConfig.icon,
      displayCurriculum: curriculumConfig?.label,
      curriculumColor: curriculumConfig?.color,
      lastLogin: user.last_login ? format(new Date(user.last_login), 'MMM dd, yyyy HH:mm') : 'Never',
      joinDate: user.date_joined ? format(new Date(user.date_joined), 'MMM dd, yyyy') : 'N/A',
      age: user.date_of_birth ? calculateAge(new Date(user.date_of_birth)) : null
    };
  };

  const calculateAge = (birthDate) => {
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  useEffect(() => {
    if (success || error) {
      const timer = setTimeout(() => {
        setSuccess('');
        setError('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [success, error]);

  const handleExport = async (format = 'csv') => {
    try {
      setLoading(true);
      const response = await adminAPI.exportUsers({
        format,
        filters: { role: activeTab !== 'all' ? activeTab : null, ...filters }
      });
      
      if (response.success && response.data.url) {
        window.open(response.data.url, '_blank');
        setSuccess(`Export generated successfully`);
      } else {
        setError('Failed to generate export');
      }
    } catch (error) {
      console.error('Error exporting users:', error);
      setError('Failed to export users');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      fetchUsers(newPage);
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/admin">Admin</Link></li>
              <li className="breadcrumb-item active">User Management</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">User Management</h1>
              <p className="lead mb-0">Manage all system users and their permissions</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">{stats.total} Total Users</div>
              <div className="small text-muted mt-1">
                {stats.active} active • {stats.verified} verified
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
          <button type="button" className="btn-close" onClick={() => setError('')}></button>
        </div>
      )}
      
      {success && (
        <div className="alert alert-success alert-dismissible fade show" role="alert">
          <i className="bi bi-check-circle me-2"></i>
          {success}
          <button type="button" className="btn-close" onClick={() => setSuccess('')}></button>
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="text-center py-4">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}

      {/* Role Statistics */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">User Statistics</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {Object.entries(ROLE_CONFIG).map(([role, config]) => (
                  <div className="col-md-3 col-6 mb-3" key={role}>
                    <div className={`card border-0 ${config.color} text-white`}>
                      <div className="card-body text-center">
                        <i className={`bi ${config.icon} fs-2 mb-2`}></i>
                        <div className="display-6 fw-bold">{stats[role]}</div>
                        <div>{config.label}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Card */}
      <div className="card">
        <div className="card-header">
          <div className="d-flex justify-content-between align-items-center">
            {/* Role Tabs */}
            <ul className="nav nav-tabs card-header-tabs">
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'all' ? 'active' : ''}`}
                  onClick={() => setActiveTab('all')}
                >
                  <i className="bi bi-grid me-2"></i>
                  All Users
                  <span className="badge bg-secondary ms-2">{stats.total}</span>
                </button>
              </li>
              {Object.entries(ROLE_CONFIG).map(([role, config]) => (
                <li className="nav-item" key={role}>
                  <button
                    className={`nav-link ${activeTab === role ? 'active' : ''}`}
                    onClick={() => setActiveTab(role)}
                  >
                    <i className={`bi ${config.icon} me-2`}></i>
                    {config.label}
                    <span className={`badge ${config.color} ms-2`}>{stats[role]}</span>
                  </button>
                </li>
              ))}
            </ul>

            {/* Action Buttons */}
            <div className="d-flex gap-2">
              <button 
                className="btn btn-outline-secondary"
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                disabled={loading}
              >
                <i className="bi bi-funnel me-2"></i>
                Filters
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setShowAddUserModal(true)}
                disabled={loading}
              >
                <i className="bi bi-plus-circle me-2"></i>
                Add User
              </button>
            </div>
          </div>
        </div>

        {/* Advanced Filters */}
        {showAdvancedFilters && (
          <div className="card-body border-bottom">
            <div className="row g-3">
              <div className="col-md-3">
                <label className="form-label">Status</label>
                <select 
                  className="form-select"
                  value={filters.status}
                  onChange={(e) => setFilters({...filters, status: e.target.value})}
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Verified</label>
                <select 
                  className="form-select"
                  value={filters.isVerified}
                  onChange={(e) => setFilters({...filters, isVerified: e.target.value})}
                >
                  <option value="">All</option>
                  <option value="true">Verified</option>
                  <option value="false">Not Verified</option>
                </select>
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Curriculum</label>
                <select 
                  className="form-select"
                  value={filters.curriculum}
                  onChange={(e) => setFilters({...filters, curriculum: e.target.value})}
                >
                  <option value="">All Curriculums</option>
                  {Object.entries(CURRICULUM_CONFIG).map(([key, config]) => (
                    <option key={key} value={key}>{config.label}</option>
                  ))}
                </select>
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Gender</label>
                <select 
                  className="form-select"
                  value={filters.gender}
                  onChange={(e) => setFilters({...filters, gender: e.target.value})}
                >
                  <option value="">All Genders</option>
                  {Object.entries(GENDER_CHOICES).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
              
              <div className="col-md-3">
                <label className="form-label">House</label>
                <select 
                  className="form-select"
                  value={filters.house}
                  onChange={(e) => setFilters({...filters, house: e.target.value})}
                >
                  <option value="">All Houses</option>
                  {Object.entries(HOUSE_CHOICES).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Department</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter department..."
                  value={filters.department}
                  onChange={(e) => setFilters({...filters, department: e.target.value})}
                />
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Grade Level</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter grade level..."
                  value={filters.grade}
                  onChange={(e) => setFilters({...filters, grade: e.target.value})}
                />
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Nationality</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Enter nationality..."
                  value={filters.nationality}
                  onChange={(e) => setFilters({...filters, nationality: e.target.value})}
                />
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Joined From</label>
                <input
                  type="date"
                  className="form-control"
                  value={filters.dateJoinedFrom}
                  onChange={(e) => setFilters({...filters, dateJoinedFrom: e.target.value})}
                />
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Joined To</label>
                <input
                  type="date"
                  className="form-control"
                  value={filters.dateJoinedTo}
                  onChange={(e) => setFilters({...filters, dateJoinedTo: e.target.value})}
                />
              </div>
              
              <div className="col-md-3">
                <label className="form-label">Suspended</label>
                <select 
                  className="form-select"
                  value={filters.isSuspended}
                  onChange={(e) => setFilters({...filters, isSuspended: e.target.value})}
                >
                  <option value="">All</option>
                  <option value="true">Suspended</option>
                  <option value="false">Not Suspended</option>
                </select>
              </div>
              
              <div className="col-md-3 d-flex align-items-end">
                <button 
                  className="btn btn-outline-secondary w-100"
                  onClick={() => setFilters({
                    status: '',
                    curriculum: '',
                    department: '',
                    grade: '',
                    dateJoinedFrom: '',
                    dateJoinedTo: '',
                    isVerified: '',
                    isSuspended: '',
                    house: '',
                    gender: '',
                    nationality: ''
                  })}
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="card-body">
          {/* Search and Bulk Actions */}
          <div className="row mb-4">
            <div className="col-md-6">
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search users by name, email, ID..."
                  defaultValue={searchTerm}
                  onChange={(e) => debouncedSearch(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>
            
            <div className="col-md-6">
              <div className="d-flex gap-2 justify-content-end">
                {selectedUsers.length > 0 && (
                  <div className="btn-group">
                    <button className="btn btn-outline-primary btn-sm">
                      {selectedUsers.length} selected
                    </button>
                    <button 
                      className="btn btn-outline-success btn-sm"
                      onClick={() => handleBulkAction('activate')}
                      disabled={loading}
                    >
                      <i className="bi bi-check-circle me-1"></i>
                      Activate
                    </button>
                    <button 
                      className="btn btn-outline-warning btn-sm"
                      onClick={() => handleBulkAction('deactivate')}
                      disabled={loading}
                    >
                      <i className="bi bi-pause-circle me-1"></i>
                      Deactivate
                    </button>
                    <button 
                      className="btn btn-outline-danger btn-sm"
                      onClick={() => handleBulkAction('delete')}
                      disabled={loading}
                    >
                      <i className="bi bi-trash me-1"></i>
                      Delete
                    </button>
                  </div>
                )}
                
                <div className="btn-group">
                  <button 
                    className="btn btn-outline-secondary btn-sm dropdown-toggle"
                    data-bs-toggle="dropdown"
                    disabled={loading}
                  >
                    <i className="bi bi-download me-2"></i>
                    Export
                  </button>
                  <ul className="dropdown-menu">
                    <li><button className="dropdown-item" onClick={() => handleExport('csv')}>CSV</button></li>
                    <li><button className="dropdown-item" onClick={() => handleExport('excel')}>Excel</button></li>
                    <li><button className="dropdown-item" onClick={() => handleExport('pdf')}>PDF</button></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Users Table */}
          <div className="table-responsive">
            <table className="table table-hover">
              <thead className="table-light">
                <tr>
                  <th width="40">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={selectedUsers.length === filteredUsers.length && filteredUsers.length > 0}
                      onChange={handleSelectAll}
                      disabled={loading}
                    />
                  </th>
                  <th>User</th>
                  <th>Contact</th>
                  <th>Role</th>
                  <th>Academic Info</th>
                  <th>Status</th>
                  <th>Verification</th>
                  <th>Last Login</th>
                  <th width="150">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(user => {
                  const formattedUser = formatUserData(user);
                  return (
                    <tr key={user.id} className={user.is_suspended ? 'table-danger' : ''}>
                      <td>
                        <input
                          type="checkbox"
                          className="form-check-input"
                          checked={selectedUsers.includes(user.id)}
                          onChange={() => handleUserSelect(user.id)}
                          disabled={loading}
                        />
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <div className="user-avatar bg-light rounded-circle d-flex align-items-center justify-content-center me-3"
                               style={{width: '40px', height: '40px'}}>
                            {user.profile_picture ? (
                              <img 
                                src={user.profile_picture} 
                                alt={formattedUser.name}
                                className="rounded-circle"
                                style={{width: '100%', height: '100%', objectFit: 'cover'}}
                              />
                            ) : (
                              <i className="bi bi-person text-muted"></i>
                            )}
                          </div>
                          <div>
                            <div className="fw-bold">{formattedUser.name}</div>
                            <div className="small text-muted">
                              {user.admission_number || user.staff_id || 'No ID'}
                              {formattedUser.age && ` • ${formattedUser.age}yrs`}
                              {user.house && ` • ${HOUSE_CHOICES[user.house] || user.house}`}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="small">
                          <div>{user.email}</div>
                          {user.phone_number && (
                            <div className="text-muted">
                              <i className="bi bi-telephone me-1"></i>
                              {user.phone_number}
                            </div>
                          )}
                          {user.nationality && (
                            <div className="text-muted">
                              <i className="bi bi-geo-alt me-1"></i>
                              {user.nationality}
                            </div>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${formattedUser.roleColor} d-flex align-items-center`}>
                          <i className={`bi ${formattedUser.roleIcon} me-1`}></i>
                          {formattedUser.displayRole}
                        </span>
                        {user.gender && (
                          <div className="small mt-1">
                            {GENDER_CHOICES[user.gender] || user.gender}
                          </div>
                        )}
                      </td>
                      <td>
                        <div className="small">
                          {user.grade_level && (
                            <div>Grade: {user.grade_level}</div>
                          )}
                          {user.primary_curriculum && (
                            <div>
                              <span className={`badge ${formattedUser.curriculumColor}`}>
                                {formattedUser.displayCurriculum}
                              </span>
                            </div>
                          )}
                          {user.department && (
                            <div className="text-muted">Dept: {user.department}</div>
                          )}
                          {user.designation && (
                            <div className="text-muted">Role: {user.designation}</div>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="d-flex flex-column gap-1">
                          <span className={`badge ${user.is_active ? 'bg-success' : 'bg-warning'}`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                          {user.is_suspended && (
                            <span className="badge bg-danger">Suspended</span>
                          )}
                          {user.is_on_leave && (
                            <span className="badge bg-info">On Leave</span>
                          )}
                          {user.profile_completed && (
                            <span className="badge bg-success">Profile Complete</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="d-flex flex-column gap-1">
                          <span className={`badge ${user.is_verified ? 'bg-success' : 'bg-secondary'}`}>
                            <i className="bi bi-check-circle me-1"></i>
                            {user.is_verified ? 'Verified' : 'Not Verified'}
                          </span>
                          <div className="small">
                            <span className={`badge ${user.email_verified ? 'bg-success' : 'bg-secondary'}`}>
                              Email {user.email_verified ? '✓' : '✗'}
                            </span>
                            <span className={`badge ${user.phone_verified ? 'bg-success' : 'bg-secondary'} ms-1`}>
                              Phone {user.phone_verified ? '✓' : '✗'}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="small">
                          <div>{formattedUser.lastLogin}</div>
                          <div className="text-muted">
                            <i className="bi bi-calendar me-1"></i>
                            Joined: {formattedUser.joinDate}
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          <button 
                            className="btn btn-outline-primary"
                            onClick={() => setEditingUser(user)}
                            disabled={loading}
                            title="Edit User"
                          >
                            <i className="bi bi-pencil"></i>
                          </button>
                          <button 
                            className={`btn ${user.is_active ? 'btn-outline-warning' : 'btn-outline-success'}`}
                            onClick={() => handleStatusChange(
                              user.id, 
                              user.is_active ? 'inactive' : 'active'
                            )}
                            disabled={loading}
                            title={user.is_active ? 'Deactivate' : 'Activate'}
                          >
                            <i className={`bi bi-${user.is_active ? 'pause' : 'play'}`}></i>
                          </button>
                          <div className="dropdown">
                            <button 
                              className="btn btn-outline-secondary dropdown-toggle"
                              data-bs-toggle="dropdown"
                              disabled={loading}
                            >
                              <i className="bi bi-gear"></i>
                            </button>
                            <ul className="dropdown-menu">
                              <li>
                                <button 
                                  className="dropdown-item"
                                  onClick={() => handleResetPassword(user.id)}
                                >
                                  <i className="bi bi-key me-2"></i>
                                  Reset Password
                                </button>
                              </li>
                              <li>
                                <button 
                                  className="dropdown-item"
                                  onClick={() => handleSendVerification(user.id, 'email')}
                                >
                                  <i className="bi bi-envelope me-2"></i>
                                  Verify Email
                                </button>
                              </li>
                              <li>
                                <button 
                                  className="dropdown-item"
                                  onClick={() => handleSendVerification(user.id, 'phone')}
                                >
                                  <i className="bi bi-phone me-2"></i>
                                  Verify Phone
                                </button>
                              </li>
                              <li>
                                <button 
                                  className="dropdown-item"
                                  onClick={() => navigator.clipboard.writeText(user.id)}
                                >
                                  <i className="bi bi-clipboard me-2"></i>
                                  Copy User ID
                                </button>
                              </li>
                              <li><hr className="dropdown-divider" /></li>
                              <li>
                                <button 
                                  className="dropdown-item text-danger"
                                  onClick={() => handleDeleteUser(user.id)}
                                >
                                  <i className="bi bi-trash me-2"></i>
                                  Delete User
                                </button>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Empty State */}
          {filteredUsers.length === 0 && !loading && (
            <div className="text-center py-5">
              <i className="bi bi-people display-1 text-muted"></i>
              <h4 className="mt-3">No users found</h4>
              <p className="text-muted">
                {searchTerm || Object.values(filters).some(f => f) 
                  ? 'Try adjusting your search or filter terms' 
                  : `No ${activeTab === 'all' ? 'users' : activeTab + 's'} in the system`}
              </p>
              {!searchTerm && !Object.values(filters).some(f => f) && (
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowAddUserModal(true)}
                  disabled={loading}
                >
                  <i className="bi bi-plus-circle me-2"></i>
                  Add User
                </button>
              )}
            </div>
          )}

          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className="d-flex justify-content-between align-items-center mt-4">
              <div className="text-muted">
                Showing {(pagination.page - 1) * pagination.pageSize + 1} to{' '}
                {Math.min(pagination.page * pagination.pageSize, pagination.total)} of{' '}
                {pagination.total} users
              </div>
              <nav>
                <ul className="pagination">
                  <li className={`page-item ${pagination.page === 1 ? 'disabled' : ''}`}>
                    <button 
                      className="page-link" 
                      onClick={() => handlePageChange(pagination.page - 1)}
                      disabled={loading || pagination.page === 1}
                    >
                      Previous
                    </button>
                  </li>
                  
                  {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
                    let pageNum;
                    if (pagination.totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (pagination.page <= 3) {
                      pageNum = i + 1;
                    } else if (pagination.page >= pagination.totalPages - 2) {
                      pageNum = pagination.totalPages - 4 + i;
                    } else {
                      pageNum = pagination.page - 2 + i;
                    }
                    
                    return (
                      <li key={pageNum} className={`page-item ${pagination.page === pageNum ? 'active' : ''}`}>
                        <button 
                          className="page-link" 
                          onClick={() => handlePageChange(pageNum)}
                          disabled={loading}
                        >
                          {pageNum}
                        </button>
                      </li>
                    );
                  })}
                  
                  <li className={`page-item ${pagination.page === pagination.totalPages ? 'disabled' : ''}`}>
                    <button 
                      className="page-link" 
                      onClick={() => handlePageChange(pagination.page + 1)}
                      disabled={loading || pagination.page === pagination.totalPages}
                    >
                      Next
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showAddUserModal && (
        <AddUserModal 
          onClose={() => setShowAddUserModal(false)}
          onSubmit={handleCreateUser}
          loading={loading}
          ROLE_CONFIG={ROLE_CONFIG}
          CURRICULUM_CONFIG={CURRICULUM_CONFIG}
          GENDER_CHOICES={GENDER_CHOICES}
          HOUSE_CHOICES={HOUSE_CHOICES}
          BLOOD_GROUP_CHOICES={BLOOD_GROUP_CHOICES}
        />
      )}

      {editingUser && (
        <EditUserModal 
          user={editingUser}
          onClose={() => setEditingUser(null)}
          onSubmit={handleUpdateUser}
          loading={loading}
          ROLE_CONFIG={ROLE_CONFIG}
          CURRICULUM_CONFIG={CURRICULUM_CONFIG}
          GENDER_CHOICES={GENDER_CHOICES}
          HOUSE_CHOICES={HOUSE_CHOICES}
          BLOOD_GROUP_CHOICES={BLOOD_GROUP_CHOICES}
        />
      )}
    </div>
  );
}

// AddUserModal Component
const AddUserModal = ({ onClose, onSubmit, loading, ROLE_CONFIG, CURRICULUM_CONFIG, GENDER_CHOICES, HOUSE_CHOICES, BLOOD_GROUP_CHOICES }) => {
  const [formData, setFormData] = useState({
    // Core Information
    first_name: '',
    last_name: '',
    middle_name: '',
    email: '',
    role: 'student',
    
    // Contact Information
    phone_number: '',
    alternative_phone: '',
    address: '',
    city: '',
    country: 'Kenya',
    
    // Personal Information
    date_of_birth: '',
    gender: '',
    nationality: 'Kenyan',
    id_number: '',
    
    // Academic Information (Student-specific)
    primary_curriculum: 'cbc',
    grade_level: '',
    current_class: '',
    house: '',
    academic_year: '',
    
    // Professional Information (Staff-specific)
    department: '',
    designation: '',
    qualification: '',
    specialization: '',
    years_of_experience: 0,
    
    // Student-specific
    parent_name: '',
    parent_email: '',
    parent_phone: '',
    parent_occupation: '',
    
    // Medical Information
    blood_group: '',
    medical_info: '',
    allergies: '',
    chronic_conditions: '',
    current_medications: '',
    doctor_name: '',
    doctor_phone: '',
    
    // Additional Information
    previous_school: '',
    
    // Account Settings
    password: '',
    confirm_password: '',
    is_active: true,
    is_verified: false,
    send_welcome_email: true
  });

  const [errors, setErrors] = useState({});
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const validateStep = (stepNumber) => {
    const newErrors = {};
    
    switch (stepNumber) {
      case 1: // Basic Information
        if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
        if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';
        if (!formData.email.trim()) {
          newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
          newErrors.email = 'Email is invalid';
        }
        if (!formData.role) newErrors.role = 'Role is required';
        break;
        
      case 2: // Role-specific Information
        if (formData.role === 'student') {
          if (!formData.grade_level) newErrors.grade_level = 'Grade level is required for students';
          if (!formData.primary_curriculum) newErrors.primary_curriculum = 'Curriculum is required for students';
          if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required for students';
        }
        
        // Check department for ALL staff roles
        const staffRoles = [
          'accountant', 'head_teacher', 'curriculum_coordinator',
          'teacher', 'admin', 'it_support', 'counselor', 
          'librarian', 'office_staff'
        ];
        
        if (staffRoles.includes(formData.role) && !formData.department) {
          newErrors.department = 'Department is required for staff members';
        }
        
        // For parents, require at least one child-related field
        if (formData.role === 'parent') {
          if (!formData.parent_name && !formData.parent_phone && !formData.parent_email) {
            newErrors.parent_name = 'At least one parent/guardian field is required';
          }
        }
        break;
        
      case 3: // Contact Information
        if (!formData.phone_number.trim()) newErrors.phone_number = 'Phone number is required';
        if (!formData.address.trim()) newErrors.address = 'Address is required';
        if (!formData.nationality.trim()) newErrors.nationality = 'Nationality is required';
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateForm = () => {
    return validateStep(1) && validateStep(2) && validateStep(3);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      setStep(1); // Go back to first step to show errors
      return;
    }
    
    // Prepare data for submission
    const submitData = { ...formData };
    
    // Add confirm_password if password is provided
    if (formData.password) {
      submitData.confirm_password = formData.confirm_password || formData.password;
    }
    
    // Remove unnecessary fields based on role
    if (formData.role !== 'student') {
      delete submitData.primary_curriculum;
      delete submitData.grade_level;
      delete submitData.current_class;
      delete submitData.house;
      delete submitData.parent_name;
      delete submitData.parent_email;
      delete submitData.parent_phone;
      delete submitData.parent_occupation;
    }
    
    if (formData.role !== 'parent') {
      delete submitData.parent_name;
      delete submitData.parent_email;
      delete submitData.parent_phone;
      delete submitData.parent_occupation;
    }
    
    const staffRoles = [
      'accountant', 'head_teacher', 'curriculum_coordinator',
      'teacher', 'admin', 'it_support', 'counselor', 
      'librarian', 'office_staff'
    ];
    
    if (!staffRoles.includes(formData.role)) {
      delete submitData.department;
      delete submitData.designation;
      delete submitData.qualification;
      delete submitData.specialization;
      delete submitData.years_of_experience;
    }
    
    onSubmit(submitData);
  };

  const handleRoleChange = (role) => {
    // List of all staff roles that need department
    const staffRoles = [
      'accountant', 'head_teacher', 'curriculum_coordinator',
      'teacher', 'admin', 'it_support', 'counselor', 
      'librarian', 'office_staff'
    ];
    
    setFormData(prev => ({
      ...prev,
      role: role,
      // Reset role-specific fields when role changes
      primary_curriculum: role === 'student' ? 'cbc' : '',
      grade_level: role === 'student' ? '' : '',
      current_class: role === 'student' ? '' : '',
      house: role === 'student' ? '' : '',
      department: staffRoles.includes(role) ? prev.department : '',
      designation: staffRoles.includes(role) ? prev.designation : ''
    }));
  };

  const handleNextStep = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    }
  };

  const handlePrevStep = () => {
    setStep(step - 1);
  };

  const isSubmitDisabled = () => {
    return loading || 
           (formData.password && formData.confirm_password && formData.password !== formData.confirm_password);
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="step-content">
            <h5 className="mb-4">Basic Information</h5>
            <div className="row">
              <div className="col-md-4">
                <div className="mb-3">
                  <label className="form-label">First Name *</label>
                  <input 
                    type="text" 
                    className={`form-control ${errors.first_name ? 'is-invalid' : ''}`}
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    disabled={loading}
                  />
                  {errors.first_name && <div className="invalid-feedback">{errors.first_name}</div>}
                </div>
              </div>
              <div className="col-md-4">
                <div className="mb-3">
                  <label className="form-label">Last Name *</label>
                  <input 
                    type="text" 
                    className={`form-control ${errors.last_name ? 'is-invalid' : ''}`}
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    disabled={loading}
                  />
                  {errors.last_name && <div className="invalid-feedback">{errors.last_name}</div>}
                </div>
              </div>
              <div className="col-md-4">
                <div className="mb-3">
                  <label className="form-label">Middle Name</label>
                  <input 
                    type="text" 
                    className="form-control"
                    value={formData.middle_name}
                    onChange={(e) => setFormData({...formData, middle_name: e.target.value})}
                    disabled={loading}
                  />
                </div>
              </div>
            </div>
            
            <div className="row">
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Email *</label>
                  <input 
                    type="email" 
                    className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    disabled={loading}
                  />
                  {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                </div>
              </div>
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Role *</label>
                  <select 
                    className={`form-select ${errors.role ? 'is-invalid' : ''}`}
                    value={formData.role}
                    onChange={(e) => handleRoleChange(e.target.value)}
                    disabled={loading}
                  >
                    {Object.entries(ROLE_CONFIG).map(([key, config]) => (
                      <option key={key} value={key}>{config.label}</option>
                    ))}
                  </select>
                  {errors.role && <div className="invalid-feedback">{errors.role}</div>}
                </div>
              </div>
            </div>
          </div>
        );
        
      case 2:
        return (
          <div className="step-content">
            <h5 className="mb-4">Role-specific Information</h5>
            
            {/* Student-specific fields */}
            {formData.role === 'student' && (
              <div className="row mb-4">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Grade Level *</label>
                    <select 
                      className={`form-select ${errors.grade_level ? 'is-invalid' : ''}`}
                      value={formData.grade_level}
                      onChange={(e) => setFormData({...formData, grade_level: e.target.value})}
                      disabled={loading}
                    >
                      <option value="">Select Grade Level</option>
                      <option value="PP1">PP1</option>
                      <option value="PP2">PP2</option>
                      <option value="Grade 1">Grade 1</option>
                      <option value="Grade 2">Grade 2</option>
                      <option value="Grade 3">Grade 3</option>
                      <option value="Grade 4">Grade 4</option>
                      <option value="Grade 5">Grade 5</option>
                      <option value="Grade 6">Grade 6</option>
                      <option value="Grade 7">Grade 7</option>
                      <option value="Grade 8">Grade 8</option>
                      <option value="Grade 9">Grade 9</option>
                      <option value="Grade 10">Grade 10</option>
                      <option value="Grade 11">Grade 11</option>
                      <option value="Grade 12">Grade 12</option>
                    </select>
                    {errors.grade_level && <div className="invalid-feedback">{errors.grade_level}</div>}
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Curriculum *</label>
                    <select 
                      className={`form-select ${errors.primary_curriculum ? 'is-invalid' : ''}`}
                      value={formData.primary_curriculum}
                      onChange={(e) => setFormData({...formData, primary_curriculum: e.target.value})}
                      disabled={loading}
                    >
                      {Object.entries(CURRICULUM_CONFIG).map(([key, config]) => (
                        <option key={key} value={key}>{config.label}</option>
                      ))}
                    </select>
                    {errors.primary_curriculum && <div className="invalid-feedback">{errors.primary_curriculum}</div>}
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Date of Birth *</label>
                    <input 
                      type="date" 
                      className={`form-control ${errors.date_of_birth ? 'is-invalid' : ''}`}
                      value={formData.date_of_birth}
                      onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                      disabled={loading}
                    />
                    {errors.date_of_birth && <div className="invalid-feedback">{errors.date_of_birth}</div>}
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">House</label>
                    <select 
                      className="form-select"
                      value={formData.house}
                      onChange={(e) => setFormData({...formData, house: e.target.value})}
                      disabled={loading}
                    >
                      <option value="">Select House</option>
                      {Object.entries(HOUSE_CHOICES).map(([key, label]) => (
                        <option key={key} value={key}>{label}</option>
                      ))}
                    </select>
                  </div>
                </div>
                
                {/* Parent/Guardian Information */}
                <div className="col-12">
                  <h6 className="mt-4 mb-3">Parent/Guardian Information</h6>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Parent Name</label>
                    <input 
                      type="text" 
                      className={`form-control ${errors.parent_name ? 'is-invalid' : ''}`}
                      value={formData.parent_name}
                      onChange={(e) => setFormData({...formData, parent_name: e.target.value})}
                      disabled={loading}
                    />
                    {errors.parent_name && <div className="invalid-feedback">{errors.parent_name}</div>}
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Parent Phone</label>
                    <input 
                      type="tel" 
                      className="form-control"
                      value={formData.parent_phone}
                      onChange={(e) => setFormData({...formData, parent_phone: e.target.value})}
                      disabled={loading}
                    />
                  </div>
                </div>
              </div>
            )}
            
            {/* Staff-specific fields */}
            {['teacher', 'admin', 'accountant', 'head_teacher', 'curriculum_coordinator', 'it_support', 'counselor', 'librarian', 'office_staff'].includes(formData.role) && (
              <div className="row mb-4">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Department *</label>
                    <input 
                      type="text" 
                      className={`form-control ${errors.department ? 'is-invalid' : ''}`}
                      value={formData.department}
                      onChange={(e) => setFormData({...formData, department: e.target.value})}
                      disabled={loading}
                      placeholder="e.g., Mathematics, Administration, Finance"
                    />
                    {errors.department && <div className="invalid-feedback">{errors.department}</div>}
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Designation</label>
                    <input 
                      type="text" 
                      className="form-control"
                      value={formData.designation}
                      onChange={(e) => setFormData({...formData, designation: e.target.value})}
                      disabled={loading}
                      placeholder="e.g., Senior Teacher, Head of Department"
                    />
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Years of Experience</label>
                    <input 
                      type="number" 
                      className="form-control"
                      value={formData.years_of_experience}
                      onChange={(e) => setFormData({...formData, years_of_experience: parseInt(e.target.value) || 0})}
                      disabled={loading}
                      min="0"
                      max="50"
                    />
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Qualification</label>
                    <input 
                      type="text" 
                      className="form-control"
                      value={formData.qualification}
                      onChange={(e) => setFormData({...formData, qualification: e.target.value})}
                      disabled={loading}
                      placeholder="e.g., B.Ed, M.Sc"
                    />
                  </div>
                </div>
              </div>
            )}
            
            {/* Parent-specific fields */}
            {formData.role === 'parent' && (
              <div className="row mb-4">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Parent Name *</label>
                    <input 
                      type="text" 
                      className={`form-control ${errors.parent_name ? 'is-invalid' : ''}`}
                      value={formData.parent_name}
                      onChange={(e) => setFormData({...formData, parent_name: e.target.value})}
                      disabled={loading}
                    />
                    {errors.parent_name && <div className="invalid-feedback">{errors.parent_name}</div>}
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Parent Phone</label>
                    <input 
                      type="tel" 
                      className="form-control"
                      value={formData.parent_phone}
                      onChange={(e) => setFormData({...formData, parent_phone: e.target.value})}
                      disabled={loading}
                    />
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Parent Email</label>
                    <input 
                      type="email" 
                      className="form-control"
                      value={formData.parent_email}
                      onChange={(e) => setFormData({...formData, parent_email: e.target.value})}
                      disabled={loading}
                    />
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Parent Occupation</label>
                    <input 
                      type="text" 
                      className="form-control"
                      value={formData.parent_occupation}
                      onChange={(e) => setFormData({...formData, parent_occupation: e.target.value})}
                      disabled={loading}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        );
        
      case 3:
        return (
          <div className="step-content">
            <h5 className="mb-4">Contact & Personal Information</h5>
            
            <div className="row">
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Phone Number *</label>
                  <input 
                    type="tel" 
                    className={`form-control ${errors.phone_number ? 'is-invalid' : ''}`}
                    value={formData.phone_number}
                    onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                    disabled={loading}
                    placeholder="+254712345678"
                  />
                  {errors.phone_number && <div className="invalid-feedback">{errors.phone_number}</div>}
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Alternative Phone</label>
                  <input 
                    type="tel" 
                    className="form-control"
                    value={formData.alternative_phone}
                    onChange={(e) => setFormData({...formData, alternative_phone: e.target.value})}
                    disabled={loading}
                  />
                </div>
              </div>
            </div>
            
            <div className="row">
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Gender</label>
                  <select 
                    className="form-select"
                    value={formData.gender}
                    onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    disabled={loading}
                  >
                    <option value="">Select Gender</option>
                    {Object.entries(GENDER_CHOICES).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Nationality *</label>
                  <input 
                    type="text" 
                    className={`form-control ${errors.nationality ? 'is-invalid' : ''}`}
                    value={formData.nationality}
                    onChange={(e) => setFormData({...formData, nationality: e.target.value})}
                    disabled={loading}
                  />
                  {errors.nationality && <div className="invalid-feedback">{errors.nationality}</div>}
                </div>
              </div>
            </div>
            
            <div className="mb-3">
              <label className="form-label">Address *</label>
              <textarea 
                className={`form-control ${errors.address ? 'is-invalid' : ''}`}
                value={formData.address}
                onChange={(e) => setFormData({...formData, address: e.target.value})}
                disabled={loading}
                rows="2"
              />
              {errors.address && <div className="invalid-feedback">{errors.address}</div>}
            </div>
            
            <div className="row">
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">City</label>
                  <input 
                    type="text" 
                    className="form-control"
                    value={formData.city}
                    onChange={(e) => setFormData({...formData, city: e.target.value})}
                    disabled={loading}
                  />
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Country</label>
                  <input 
                    type="text" 
                    className="form-control"
                    value={formData.country}
                    onChange={(e) => setFormData({...formData, country: e.target.value})}
                    disabled={loading}
                  />
                </div>
              </div>
            </div>
            
            {/* Medical Information (Optional) */}
            <div className="mb-3">
              <label className="form-label">Medical Information (Optional)</label>
              <textarea 
                className="form-control"
                value={formData.medical_info}
                onChange={(e) => setFormData({...formData, medical_info: e.target.value})}
                disabled={loading}
                rows="2"
                placeholder="Any important medical information..."
              />
            </div>
          </div>
        );
        
      case 4:
        return (
          <div className="step-content">
            <h5 className="mb-4">Account Settings</h5>
            
            <div className="row">
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Password (Optional)</label>
                  <input 
                    type="password" 
                    className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    disabled={loading}
                    minLength={8}
                  />
                  {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                  <div className="form-text">
                    At least 8 characters with letters and numbers
                  </div>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Confirm Password {formData.password ? '*' : ''}</label>
                  <input 
                    type="password" 
                    className={`form-control ${errors.confirm_password ? 'is-invalid' : ''}`}
                    value={formData.confirm_password}
                    onChange={(e) => setFormData({...formData, confirm_password: e.target.value})}
                    disabled={loading}
                    minLength={8}
                  />
                  {errors.confirm_password && <div className="invalid-feedback">{errors.confirm_password}</div>}
                </div>
              </div>
            </div>
            
            {formData.password && formData.confirm_password && formData.password !== formData.confirm_password && (
              <div className="alert alert-warning py-2">
                <i className="bi bi-exclamation-triangle me-2"></i>
                Passwords do not match
              </div>
            )}
            
            <div className="form-text mb-3">
              If password is not provided, a random password will be generated and sent to the user's email.
            </div>
            
            {/* Options */}
            <div className="row mt-3">
              <div className="col-md-6">
                <div className="form-check">
                  <input 
                    type="checkbox" 
                    className="form-check-input"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    disabled={loading}
                    id="isActive"
                  />
                  <label className="form-check-label" htmlFor="isActive">
                    Account is active
                  </label>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="form-check">
                  <input 
                    type="checkbox" 
                    className="form-check-input"
                    checked={formData.is_verified}
                    onChange={(e) => setFormData({...formData, is_verified: e.target.checked})}
                    disabled={loading}
                    id="isVerified"
                  />
                  <label className="form-check-label" htmlFor="isVerified">
                    Verified account
                  </label>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="form-check">
                  <input 
                    type="checkbox" 
                    className="form-check-input"
                    checked={formData.send_welcome_email}
                    onChange={(e) => setFormData({...formData, send_welcome_email: e.target.checked})}
                    disabled={loading}
                    id="sendWelcome"
                  />
                  <label className="form-check-label" htmlFor="sendWelcome">
                    Send welcome email
                  </label>
                </div>
              </div>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="modal fade show" style={{display: 'block', backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Add New User</h5>
            <button 
              type="button" 
              className="btn-close"
              onClick={onClose}
              disabled={loading}
            ></button>
          </div>
          
          {/* Step Progress */}
          <div className="modal-header border-bottom">
            <div className="w-100">
              <div className="progress" style={{height: '5px'}}>
                <div 
                  className="progress-bar" 
                  role="progressbar" 
                  style={{width: `${(step / totalSteps) * 100}%`}}
                ></div>
              </div>
              <div className="d-flex justify-content-between mt-2">
                {[1, 2, 3, 4].map((stepNum) => (
                  <div 
                    key={stepNum} 
                    className={`text-center ${step >= stepNum ? 'text-primary' : 'text-muted'}`}
                    style={{flex: 1}}
                  >
                    <div className={`rounded-circle d-inline-flex align-items-center justify-content-center ${step >= stepNum ? 'bg-primary text-white' : 'bg-light'} ${step === stepNum ? 'border border-primary' : ''}`}
                         style={{width: '30px', height: '30px'}}>
                      {stepNum}
                    </div>
                    <div className="small mt-1">
                      {stepNum === 1 && 'Basic'}
                      {stepNum === 2 && 'Role Info'}
                      {stepNum === 3 && 'Contact'}
                      {stepNum === 4 && 'Account'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              {renderStep()}
            </div>
            
            <div className="modal-footer">
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={step > 1 ? handlePrevStep : onClose}
                disabled={loading}
              >
                {step > 1 ? 'Back' : 'Cancel'}
              </button>
              
              {step < totalSteps ? (
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={handleNextStep}
                  disabled={loading}
                >
                  Next
                </button>
              ) : (
                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  disabled={isSubmitDisabled()}
                >
                  {loading ? 'Creating...' : 'Create User'}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// EditUserModal Component
const EditUserModal = ({ user, onClose, onSubmit, loading, ROLE_CONFIG, CURRICULUM_CONFIG, GENDER_CHOICES, HOUSE_CHOICES, BLOOD_GROUP_CHOICES }) => {
  const [formData, setFormData] = useState({
    // Core Information
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    middle_name: user.middle_name || '',
    email: user.email || '',
    role: user.role || 'student',
    
    // Contact Information
    phone_number: user.phone_number || '',
    alternative_phone: user.alternative_phone || '',
    address: user.address || '',
    city: user.city || '',
    country: user.country || 'Kenya',
    
    // Personal Information
    date_of_birth: user.date_of_birth ? user.date_of_birth.split('T')[0] : '',
    gender: user.gender || '',
    nationality: user.nationality || 'Kenyan',
    id_number: user.id_number || '',
    
    // Academic Information
    primary_curriculum: user.primary_curriculum || '',
    grade_level: user.grade_level || '',
    current_class: user.current_class || '',
    house: user.house || '',
    
    // Professional Information
    department: user.department || '',
    designation: user.designation || '',
    qualification: user.qualification || '',
    specialization: user.specialization || '',
    years_of_experience: user.years_of_experience || 0,
    
    // Student-specific
    parent_name: user.parent_name || '',
    parent_email: user.parent_email || '',
    parent_phone: user.parent_phone || '',
    parent_occupation: user.parent_occupation || '',
    
    // Medical Information
    blood_group: user.blood_group || '',
    medical_info: user.medical_info || '',
    allergies: user.allergies || '',
    chronic_conditions: user.chronic_conditions || '',
    current_medications: user.current_medications || '',
    doctor_name: user.doctor_name || '',
    doctor_phone: user.doctor_phone || '',
    
    // Account Status
    is_active: user.is_active || false,
    is_verified: user.is_verified || false,
    is_suspended: user.is_suspended || false,
    is_on_leave: user.is_on_leave || false,
    is_approved: user.is_approved || false,
    profile_completed: user.profile_completed || false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Prepare data for submission
    const submitData = { ...formData };
    
    // Remove password fields if they exist
    delete submitData.password;
    delete submitData.confirm_password;
    
    // Remove unnecessary fields based on role
    if (formData.role !== 'student') {
      delete submitData.primary_curriculum;
      delete submitData.grade_level;
      delete submitData.current_class;
      delete submitData.house;
      delete submitData.parent_name;
      delete submitData.parent_email;
      delete submitData.parent_phone;
      delete submitData.parent_occupation;
    }
    
    if (formData.role !== 'parent') {
      delete submitData.parent_name;
      delete submitData.parent_email;
      delete submitData.parent_phone;
      delete submitData.parent_occupation;
    }
    
    const staffRoles = [
      'accountant', 'head_teacher', 'curriculum_coordinator',
      'teacher', 'admin', 'it_support', 'counselor', 
      'librarian', 'office_staff'
    ];
    
    if (!staffRoles.includes(formData.role)) {
      delete submitData.department;
      delete submitData.designation;
      delete submitData.qualification;
      delete submitData.specialization;
      delete submitData.years_of_experience;
    }
    
    onSubmit(user.id, submitData);
  };

  return (
    <div className="modal fade show" style={{display: 'block', backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog modal-xl">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Edit User</h5>
            <button 
              type="button" 
              className="btn-close"
              onClick={onClose}
              disabled={loading}
            ></button>
          </div>
          
          <div className="modal-body">
            <div className="row mb-4">
              <div className="col-12">
                <div className="d-flex align-items-center">
                  <div className="user-avatar bg-light rounded-circle d-flex align-items-center justify-content-center me-3"
                       style={{width: '60px', height: '60px'}}>
                    {user.profile_picture ? (
                      <img 
                        src={user.profile_picture} 
                        alt={user.first_name}
                        className="rounded-circle"
                        style={{width: '100%', height: '100%', objectFit: 'cover'}}
                      />
                    ) : (
                      <i className="bi bi-person text-muted fs-3"></i>
                    )}
                  </div>
                  <div>
                    <h5 className="mb-0">{user.first_name} {user.last_name}</h5>
                    <div className="text-muted">
                      {user.admission_number || user.staff_id || user.email}
                    </div>
                    <div className="small">
                      <span className={`badge ${ROLE_CONFIG[user.role]?.color || 'bg-secondary'}`}>
                        {ROLE_CONFIG[user.role]?.label || user.role}
                      </span>
                      <span className={`badge ${user.is_active ? 'bg-success' : 'bg-warning'} ms-2`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tabs for different sections */}
            <ul className="nav nav-tabs mb-4" id="editUserTabs" role="tablist">
              <li className="nav-item" role="presentation">
                <button className="nav-link active" id="basic-tab" data-bs-toggle="tab" data-bs-target="#basic" type="button">
                  Basic Info
                </button>
              </li>
              <li className="nav-item" role="presentation">
                <button className="nav-link" id="academic-tab" data-bs-toggle="tab" data-bs-target="#academic" type="button">
                  Academic/Professional
                </button>
              </li>
              <li className="nav-item" role="presentation">
                <button className="nav-link" id="contact-tab" data-bs-toggle="tab" data-bs-target="#contact" type="button">
                  Contact
                </button>
              </li>
              <li className="nav-item" role="presentation">
                <button className="nav-link" id="medical-tab" data-bs-toggle="tab" data-bs-target="#medical" type="button">
                  Medical
                </button>
              </li>
              <li className="nav-item" role="presentation">
                <button className="nav-link" id="status-tab" data-bs-toggle="tab" data-bs-target="#status" type="button">
                  Status
                </button>
              </li>
            </ul>

            <form onSubmit={handleSubmit}>
              <div className="tab-content" id="editUserTabsContent">
                {/* Basic Information Tab */}
                <div className="tab-pane fade show active" id="basic" role="tabpanel">
                  <div className="row">
                    <div className="col-md-4">
                      <div className="mb-3">
                        <label className="form-label">First Name</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={formData.first_name}
                          onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="mb-3">
                        <label className="form-label">Last Name</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={formData.last_name}
                          onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="mb-3">
                        <label className="form-label">Middle Name</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={formData.middle_name}
                          onChange={(e) => setFormData({...formData, middle_name: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Email</label>
                        <input 
                          type="email" 
                          className="form-control" 
                          value={formData.email}
                          onChange={(e) => setFormData({...formData, email: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Gender</label>
                        <select 
                          className="form-select"
                          value={formData.gender}
                          onChange={(e) => setFormData({...formData, gender: e.target.value})}
                          disabled={loading}
                        >
                          <option value="">Select Gender</option>
                          {Object.entries(GENDER_CHOICES).map(([key, label]) => (
                            <option key={key} value={key}>{label}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Date of Birth</label>
                        <input 
                          type="date" 
                          className="form-control" 
                          value={formData.date_of_birth}
                          onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">National ID/Passport</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={formData.id_number}
                          onChange={(e) => setFormData({...formData, id_number: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Academic/Professional Tab */}
                <div className="tab-pane fade" id="academic" role="tabpanel">
                  {user.role === 'student' ? (
                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Grade Level</label>
                          <select 
                            className="form-select"
                            value={formData.grade_level}
                            onChange={(e) => setFormData({...formData, grade_level: e.target.value})}
                            disabled={loading}
                          >
                            <option value="">Select Grade Level</option>
                            <option value="PP1">PP1</option>
                            <option value="PP2">PP2</option>
                            <option value="Grade 1">Grade 1</option>
                            <option value="Grade 2">Grade 2</option>
                            <option value="Grade 3">Grade 3</option>
                            <option value="Grade 4">Grade 4</option>
                            <option value="Grade 5">Grade 5</option>
                            <option value="Grade 6">Grade 6</option>
                            <option value="Grade 7">Grade 7</option>
                            <option value="Grade 8">Grade 8</option>
                            <option value="Grade 9">Grade 9</option>
                            <option value="Grade 10">Grade 10</option>
                            <option value="Grade 11">Grade 11</option>
                            <option value="Grade 12">Grade 12</option>
                          </select>
                        </div>
                      </div>
                      
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Curriculum</label>
                          <select 
                            className="form-select"
                            value={formData.primary_curriculum}
                            onChange={(e) => setFormData({...formData, primary_curriculum: e.target.value})}
                            disabled={loading}
                          >
                            <option value="">Select Curriculum</option>
                            {Object.entries(CURRICULUM_CONFIG).map(([key, config]) => (
                              <option key={key} value={key}>{config.label}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">House</label>
                          <select 
                            className="form-select"
                            value={formData.house}
                            onChange={(e) => setFormData({...formData, house: e.target.value})}
                            disabled={loading}
                          >
                            <option value="">Select House</option>
                            {Object.entries(HOUSE_CHOICES).map(([key, label]) => (
                              <option key={key} value={key}>{label}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Current Class</label>
                          <input 
                            type="text" 
                            className="form-control" 
                            value={formData.current_class}
                            onChange={(e) => setFormData({...formData, current_class: e.target.value})}
                            disabled={loading}
                          />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Department</label>
                          <input 
                            type="text" 
                            className="form-control" 
                            value={formData.department}
                            onChange={(e) => setFormData({...formData, department: e.target.value})}
                            disabled={loading}
                          />
                        </div>
                      </div>
                      
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Designation</label>
                          <input 
                            type="text" 
                            className="form-control" 
                            value={formData.designation}
                            onChange={(e) => setFormData({...formData, designation: e.target.value})}
                            disabled={loading}
                          />
                        </div>
                      </div>
                      
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Qualification</label>
                          <input 
                            type="text" 
                            className="form-control" 
                            value={formData.qualification}
                            onChange={(e) => setFormData({...formData, qualification: e.target.value})}
                            disabled={loading}
                          />
                        </div>
                      </div>
                      
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label className="form-label">Years of Experience</label>
                          <input 
                            type="number" 
                            className="form-control" 
                            value={formData.years_of_experience}
                            onChange={(e) => setFormData({...formData, years_of_experience: parseInt(e.target.value) || 0})}
                            disabled={loading}
                            min="0"
                            max="50"
                          />
                        </div>
                      </div>
                      
                      <div className="col-12">
                        <div className="mb-3">
                          <label className="form-label">Specialization</label>
                          <textarea 
                            className="form-control"
                            value={formData.specialization}
                            onChange={(e) => setFormData({...formData, specialization: e.target.value})}
                            disabled={loading}
                            rows="2"
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Contact Information Tab */}
                <div className="tab-pane fade" id="contact" role="tabpanel">
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Phone Number</label>
                        <input 
                          type="tel" 
                          className="form-control" 
                          value={formData.phone_number}
                          onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Alternative Phone</label>
                        <input 
                          type="tel" 
                          className="form-control" 
                          value={formData.alternative_phone}
                          onChange={(e) => setFormData({...formData, alternative_phone: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">City</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={formData.city}
                          onChange={(e) => setFormData({...formData, city: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Country</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={formData.country}
                          onChange={(e) => setFormData({...formData, country: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Address</label>
                    <textarea 
                      className="form-control"
                      value={formData.address}
                      onChange={(e) => setFormData({...formData, address: e.target.value})}
                      disabled={loading}
                      rows="3"
                    />
                  </div>
                  
                  {/* Emergency Contact */}
                  <div className="row">
                    <div className="col-12">
                      <h6 className="mb-3">Emergency Contact</h6>
                    </div>
                    
                    <div className="col-md-4">
                      <div className="mb-3">
                        <label className="form-label">Contact Name</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={user.emergency_contact_name || ''}
                          onChange={(e) => setFormData({...formData, emergency_contact_name: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="col-md-4">
                      <div className="mb-3">
                        <label className="form-label">Contact Phone</label>
                        <input 
                          type="tel" 
                          className="form-control" 
                          value={user.emergency_contact_phone || ''}
                          onChange={(e) => setFormData({...formData, emergency_contact_phone: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                    
                    <div className="col-md-4">
                      <div className="mb-3">
                        <label className="form-label">Relationship</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={user.emergency_contact_relationship || ''}
                          onChange={(e) => setFormData({...formData, emergency_contact_relationship: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Medical Information Tab */}
                <div className="tab-pane fade" id="medical" role="tabpanel">
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Blood Group</label>
                        <select 
                          className="form-select"
                          value={formData.blood_group}
                          onChange={(e) => setFormData({...formData, blood_group: e.target.value})}
                          disabled={loading}
                        >
                          <option value="">Select Blood Group</option>
                          {Object.entries(BLOOD_GROUP_CHOICES).map(([key, label]) => (
                            <option key={key} value={key}>{label}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Doctor Name</label>
                        <input 
                          type="text" 
                          className="form-control" 
                          value={formData.doctor_name}
                          onChange={(e) => setFormData({...formData, doctor_name: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Doctor Phone</label>
                        <input 
                          type="tel" 
                          className="form-control" 
                          value={formData.doctor_phone}
                          onChange={(e) => setFormData({...formData, doctor_phone: e.target.value})}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Allergies</label>
                    <textarea 
                      className="form-control"
                      value={formData.allergies}
                      onChange={(e) => setFormData({...formData, allergies: e.target.value})}
                      disabled={loading}
                      rows="2"
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Chronic Conditions</label>
                    <textarea 
                      className="form-control"
                      value={formData.chronic_conditions}
                      onChange={(e) => setFormData({...formData, chronic_conditions: e.target.value})}
                      disabled={loading}
                      rows="2"
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Current Medications</label>
                    <textarea 
                      className="form-control"
                      value={formData.current_medications}
                      onChange={(e) => setFormData({...formData, current_medications: e.target.value})}
                      disabled={loading}
                      rows="2"
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Medical Information</label>
                    <textarea 
                      className="form-control"
                      value={formData.medical_info}
                      onChange={(e) => setFormData({...formData, medical_info: e.target.value})}
                      disabled={loading}
                      rows="3"
                    />
                  </div>
                </div>

                {/* Status Tab */}
                <div className="tab-pane fade" id="status" role="tabpanel">
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input 
                            type="checkbox" 
                            className="form-check-input"
                            checked={formData.is_active}
                            onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                            disabled={loading}
                            id="editIsActive"
                          />
                          <label className="form-check-label" htmlFor="editIsActive">
                            Active Account
                          </label>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input 
                            type="checkbox" 
                            className="form-check-input"
                            checked={formData.is_verified}
                            onChange={(e) => setFormData({...formData, is_verified: e.target.checked})}
                            disabled={loading}
                            id="editIsVerified"
                          />
                          <label className="form-check-label" htmlFor="editIsVerified">
                            Verified Account
                          </label>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input 
                            type="checkbox" 
                            className="form-check-input"
                            checked={formData.is_approved}
                            onChange={(e) => setFormData({...formData, is_approved: e.target.checked})}
                            disabled={loading}
                            id="editIsApproved"
                          />
                          <label className="form-check-label" htmlFor="editIsApproved">
                            Approved Account
                          </label>
                        </div>
                      </div>
                    </div>
                    
                    <div className="col-md-6">
                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input 
                            type="checkbox" 
                            className="form-check-input"
                            checked={formData.is_suspended}
                            onChange={(e) => setFormData({...formData, is_suspended: e.target.checked})}
                            disabled={loading}
                            id="editIsSuspended"
                          />
                          <label className="form-check-label" htmlFor="editIsSuspended">
                            Suspended Account
                          </label>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input 
                            type="checkbox" 
                            className="form-check-input"
                            checked={formData.is_on_leave}
                            onChange={(e) => setFormData({...formData, is_on_leave: e.target.checked})}
                            disabled={loading}
                            id="editIsOnLeave"
                          />
                          <label className="form-check-label" htmlFor="editIsOnLeave">
                            On Leave
                          </label>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input 
                            type="checkbox" 
                            className="form-check-input"
                            checked={formData.profile_completed}
                            onChange={(e) => setFormData({...formData, profile_completed: e.target.checked})}
                            disabled={loading}
                            id="editProfileCompleted"
                          />
                          <label className="form-check-label" htmlFor="editProfileCompleted">
                            Profile Completed
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={onClose}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  disabled={loading}
                >
                  {loading ? 'Updating...' : 'Update User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;