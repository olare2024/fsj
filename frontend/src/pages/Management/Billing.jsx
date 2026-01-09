import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Billing() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('invoices');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');

  const invoices = [
    {
      id: 'INV-001',
      studentName: 'John Smith',
      gradeLevel: '9th Grade',
      amount: 2500.00,
      dueDate: '2024-02-01',
      status: 'paid',
      issuedDate: '2024-01-15',
      items: ['Tuition', 'Technology Fee']
    },
    {
      id: 'INV-002',
      studentName: 'Sarah Johnson',
      gradeLevel: '10th Grade',
      amount: 2700.00,
      dueDate: '2024-02-01',
      status: 'pending',
      issuedDate: '2024-01-15',
      items: ['Tuition', 'Lab Fees']
    },
    {
      id: 'INV-003',
      studentName: 'Michael Brown',
      gradeLevel: '11th Grade',
      amount: 2900.00,
      dueDate: '2024-02-01',
      status: 'overdue',
      issuedDate: '2024-01-15',
      items: ['Tuition', 'AP Exam Fees']
    },
    {
      id: 'INV-004',
      studentName: 'Emily Davis',
      gradeLevel: '9th Grade',
      amount: 2500.00,
      dueDate: '2024-02-01',
      status: 'paid',
      issuedDate: '2024-01-15',
      items: ['Tuition', 'Activity Fee']
    },
    {
      id: 'INV-005',
      studentName: 'David Wilson',
      gradeLevel: '12th Grade',
      amount: 3100.00,
      dueDate: '2024-02-01',
      status: 'pending',
      issuedDate: '2024-01-15',
      items: ['Tuition', 'Graduation Fee']
    }
  ];

  const billingStats = {
    totalRevenue: 125400.00,
    pendingPayments: 15600.00,
    overdueAmount: 5800.00,
    collectedThisMonth: 89200.00
  };

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = invoice.studentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         invoice.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === 'all' || invoice.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'paid': return { class: 'bg-success', text: 'Paid' };
      case 'pending': return { class: 'bg-warning', text: 'Pending' };
      case 'overdue': return { class: 'bg-danger', text: 'Overdue' };
      case 'cancelled': return { class: 'bg-secondary', text: 'Cancelled' };
      default: return { class: 'bg-secondary', text: status };
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Billing & Payments</h1>
          <p className="lead">Manage student invoices, payments, and financial records</p>
        </div>
        <Link to="/admin" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admin
        </Link>
      </div>

      {/* Billing Statistics */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h3>{formatCurrency(billingStats.totalRevenue)}</h3>
                  <p className="mb-0">Total Revenue</p>
                </div>
                <i className="bi bi-currency-dollar display-6 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h3>{formatCurrency(billingStats.pendingPayments)}</h3>
                  <p className="mb-0">Pending Payments</p>
                </div>
                <i className="bi bi-clock display-6 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-danger text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h3>{formatCurrency(billingStats.overdueAmount)}</h3>
                  <p className="mb-0">Overdue Amount</p>
                </div>
                <i className="bi bi-exclamation-triangle display-6 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h3>{formatCurrency(billingStats.collectedThisMonth)}</h3>
                  <p className="mb-0">This Month</p>
                </div>
                <i className="bi bi-calendar-month display-6 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'invoices' ? 'active' : ''}`}
                onClick={() => setActiveTab('invoices')}
              >
                <i className="bi bi-receipt me-2"></i>
                Invoices
                <span className="badge bg-primary ms-2">{invoices.length}</span>
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'payments' ? 'active' : ''}`}
                onClick={() => setActiveTab('payments')}
              >
                <i className="bi bi-credit-card me-2"></i>
                Payment Records
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'fees' ? 'active' : ''}`}
                onClick={() => setActiveTab('fees')}
              >
                <i className="bi bi-cash-coin me-2"></i>
                Fee Structure
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'reports' ? 'active' : ''}`}
                onClick={() => setActiveTab('reports')}
              >
                <i className="bi bi-graph-up me-2"></i>
                Financial Reports
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Invoices Tab */}
          {activeTab === 'invoices' && (
            <div>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="mb-0">Student Invoices</h5>
                <div className="d-flex gap-2">
                  <button className="btn btn-success">
                    <i className="bi bi-download me-2"></i>
                    Export
                  </button>
                  <button className="btn btn-primary">
                    <i className="bi bi-plus-circle me-2"></i>
                    Create Invoice
                  </button>
                </div>
              </div>

              {/* Search and Filter */}
              <div className="row g-3 mb-4">
                <div className="col-md-6">
                  <div className="input-group">
                    <span className="input-group-text">
                      <i className="bi bi-search"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search invoices by student name or ID..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="col-md-4">
                  <select
                    className="form-select"
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                  >
                    <option value="all">All Status</option>
                    <option value="paid">Paid</option>
                    <option value="pending">Pending</option>
                    <option value="overdue">Overdue</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
                <div className="col-md-2">
                  <button className="btn btn-outline-primary w-100">
                    <i className="bi bi-funnel me-2"></i>
                    Filter
                  </button>
                </div>
              </div>

              {/* Invoices Table */}
              <div className="table-responsive">
                <table className="table table-striped table-hover">
                  <thead>
                    <tr>
                      <th>Invoice ID</th>
                      <th>Student Name</th>
                      <th>Grade Level</th>
                      <th>Amount</th>
                      <th>Due Date</th>
                      <th>Status</th>
                      <th>Items</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredInvoices.map(invoice => {
                      const statusBadge = getStatusBadge(invoice.status);
                      const isOverdue = invoice.status === 'overdue';
                      
                      return (
                        <tr key={invoice.id} className={isOverdue ? 'table-danger' : ''}>
                          <td>
                            <strong>{invoice.id}</strong>
                          </td>
                          <td>
                            <div className="fw-bold">{invoice.studentName}</div>
                            <small className="text-muted">Issued: {invoice.issuedDate}</small>
                          </td>
                          <td>{invoice.gradeLevel}</td>
                          <td>
                            <strong>{formatCurrency(invoice.amount)}</strong>
                          </td>
                          <td>
                            <span className={isOverdue ? 'text-danger fw-bold' : ''}>
                              {invoice.dueDate}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${statusBadge.class}`}>
                              {statusBadge.text}
                            </span>
                          </td>
                          <td>
                            <small>
                              {invoice.items.slice(0, 2).join(', ')}
                              {invoice.items.length > 2 && '...'}
                            </small>
                          </td>
                          <td>
                            <div className="btn-group">
                              <button className="btn btn-sm btn-outline-primary">
                                <i className="bi bi-eye"></i>
                              </button>
                              <button className="btn btn-sm btn-outline-warning">
                                <i className="bi bi-pencil"></i>
                              </button>
                              <button className="btn btn-sm btn-outline-success">
                                <i className="bi bi-receipt"></i>
                              </button>
                              <button className="btn btn-sm btn-outline-info">
                                <i className="bi bi-send"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {filteredInvoices.length === 0 && (
                <div className="text-center py-5">
                  <i className="bi bi-search display-1 text-muted mb-3"></i>
                  <h4>No invoices found</h4>
                  <p className="text-muted">
                    Try adjusting your search criteria or filter settings.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Payment Records Tab */}
          {activeTab === 'payments' && (
            <div>
              <h5 className="mb-4">Payment Records</h5>
              <div className="alert alert-info">
                <i className="bi bi-info-circle me-2"></i>
                View and manage all payment transactions and records.
              </div>
              {/* Payment records content would go here */}
            </div>
          )}

          {/* Fee Structure Tab */}
          {activeTab === 'fees' && (
            <div>
              <h5 className="mb-4">Fee Structure & Pricing</h5>
              <div className="alert alert-warning">
                <i className="bi bi-exclamation-triangle me-2"></i>
                Configure tuition rates, fees, and payment plans.
              </div>
              {/* Fee structure content would go here */}
            </div>
          )}

          {/* Financial Reports Tab */}
          {activeTab === 'reports' && (
            <div>
              <h5 className="mb-4">Financial Reports & Analytics</h5>
              <div className="row">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">Revenue Overview</h6>
                      <p className="text-muted">Monthly revenue trends</p>
                      {/* Revenue chart would go here */}
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-body">
                      <h6 className="card-title">Payment Status</h6>
                      <p className="text-muted">Distribution of payment statuses</p>
                      {/* Payment status chart would go here */}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row mt-4">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-envelope display-4 text-primary mb-3"></i>
              <h5>Send Reminders</h5>
              <p className="text-muted">
                Send payment reminders to parents
              </p>
              <button className="btn btn-primary">Send Reminders</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-credit-card display-4 text-success mb-3"></i>
              <h5>Process Payments</h5>
              <p className="text-muted">
                Manually process offline payments
              </p>
              <button className="btn btn-success">Process Payment</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body text-center">
              <i className="bi bi-file-earmark-text display-4 text-warning mb-3"></i>
              <h5>Generate Reports</h5>
              <p className="text-muted">
                Create custom financial reports
              </p>
              <button className="btn btn-warning">Generate Report</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Billing;