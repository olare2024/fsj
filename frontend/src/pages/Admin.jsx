import React from 'react';
import { useAuth } from '../context/AuthContext';

function Admin() {
  const { currentUser } = useAuth();

  return (
    <div className="admin-page">
      <div className="container mt-4">
        <div className="row">
          <div className="col-12">
            <div className="card">
              <div className="card-header bg-primary text-white">
                <h3 className="card-title mb-0">Admin Dashboard</h3>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-3">
                    <div className="card bg-info text-white text-center">
                      <div className="card-body">
                        <h4>485</h4>
                        <p>Total Students</p>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="card bg-success text-white text-center">
                      <div className="card-body">
                        <h4>35</h4>
                        <p>Teachers</p>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="card bg-warning text-dark text-center">
                      <div className="card-body">
                        <h4>24</h4>
                        <p>Classes</p>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="card bg-danger text-white text-center">
                      <div className="card-body">
                        <h4>15</h4>
                        <p>Pending Applications</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4">
                  <h5>Welcome, {currentUser?.firstName}!</h5>
                  <p className="text-muted">
                    This is the admin dashboard. Here you can manage all aspects of the school system.
                  </p>
                </div>

                <div className="row mt-4">
                  <div className="col-md-6">
                    <div className="card">
                      <div className="card-header">
                        <h6>Quick Actions</h6>
                      </div>
                      <div className="card-body">
                        <div className="d-grid gap-2">
                          <button className="btn btn-outline-primary">Manage Users</button>
                          <button className="btn btn-outline-success">View Reports</button>
                          <button className="btn btn-outline-warning">System Settings</button>
                          <button className="btn btn-outline-info">Backup Database</button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="card">
                      <div className="card-header">
                        <h6>Recent Activity</h6>
                      </div>
                      <div className="card-body">
                        <ul className="list-group list-group-flush">
                          <li className="list-group-item">New student registration - John Doe</li>
                          <li className="list-group-item">Grade submission - Mathematics</li>
                          <li className="list-group-item">Teacher account created - Mrs. Smith</li>
                          <li className="list-group-item">System backup completed</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Admin;