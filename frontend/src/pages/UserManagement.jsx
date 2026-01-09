import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function UserManagement() {
  const [users, setUsers] = useState([
    {
      id: 1,
      firstName: 'John',
      lastName: 'Student',
      email: 'john.student@delvok.edu',
      role: 'student',
      status: 'active',
      joinDate: '2024-01-15'
    },
    {
      id: 2,
      firstName: 'Sarah',
      lastName: 'Teacher',
      email: 'sarah.teacher@delvok.edu',
      role: 'teacher',
      status: 'active',
      joinDate: '2023-08-20'
    },
    {
      id: 3,
      firstName: 'Mike',
      lastName: 'Parent',
      email: 'mike.parent@email.com',
      role: 'parent',
      status: 'pending',
      joinDate: '2024-02-01'
    }
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredUsers = users.filter(user => {
    const matchesSearch = `${user.firstName} ${user.lastName}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter;
    return matchesSearch && matchesRole && matchesStatus;
  });

  const updateUserStatus = (userId, newStatus) => {
    setUsers(users.map(user => 
      user.id === userId ? { ...user, status: newStatus } : user
    ));
  };

  const deleteUser = (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      setUsers(users.filter(user => user.id !== userId));
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>User Management</h1>
          <p className="lead">Manage all system users and their permissions</p>
        </div>
        <Link to="/admin" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admin
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>{users.length}</h3>
              <p className="mb-0">Total Users</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>{users.filter(u => u.role === 'student').length}</h3>
              <p className="mb-0">Students</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>{users.filter(u => u.role === 'teacher').length}</h3>
              <p className="mb-0">Teachers</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>{users.filter(u => u.role === 'parent').length}</h3>
              <p className="mb-0">Parents</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-4">
              <input
                type="text"
                className="form-control"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <select
                className="form-select"
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
              >
                <option value="all">All Roles</option>
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="parent">Parent</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="col-md-3">
              <select
                className="form-select"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="pending">Pending</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
            <div className="col-md-2">
              <button className="btn btn-primary w-100">
                <i className="bi bi-plus-circle me-2"></i>
                Add User
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Join Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(user => (
                  <tr key={user.id}>
                    <td>
                      <div className="d-flex align-items-center">
                        <div className="user-avatar bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                             style={{width: '40px', height: '40px', fontSize: '0.9rem'}}>
                          {user.firstName[0]}{user.lastName[0]}
                        </div>
                        <div>
                          <div className="fw-bold">{user.firstName} {user.lastName}</div>
                        </div>
                      </div>
                    </td>
                    <td>{user.email}</td>
                    <td>
                      <span className={`badge bg-${getRoleBadgeColor(user.role)}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span className={`badge bg-${getStatusBadgeColor(user.status)}`}>
                        {user.status}
                      </span>
                    </td>
                    <td>{new Date(user.joinDate).toLocaleDateString()}</td>
                    <td>
                      <div className="btn-group">
                        <button 
                          className="btn btn-sm btn-outline-primary"
                          title="Edit User"
                        >
                          <i className="bi bi-pencil"></i>
                        </button>
                        <button 
                          className="btn btn-sm btn-outline-warning"
                          onClick={() => updateUserStatus(user.id, user.status === 'active' ? 'suspended' : 'active')}
                          title="Toggle Status"
                        >
                          <i className={`bi bi-${user.status === 'active' ? 'pause' : 'play'}`}></i>
                        </button>
                        <button 
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => deleteUser(user.id)}
                          title="Delete User"
                        >
                          <i className="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function getRoleBadgeColor(role) {
  switch (role) {
    case 'admin': return 'danger';
    case 'teacher': return 'warning';
    case 'student': return 'success';
    case 'parent': return 'info';
    default: return 'secondary';
  }
}

function getStatusBadgeColor(status) {
  switch (status) {
    case 'active': return 'success';
    case 'pending': return 'warning';
    case 'suspended': return 'danger';
    default: return 'secondary';
  }
}

export default UserManagement;