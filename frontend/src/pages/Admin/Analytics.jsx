import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function Analytics() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState('month');
  const [analyticsData, setAnalyticsData] = useState({});

  // Mock analytics data - in real app, this would come from API
  useEffect(() => {
    const mockData = {
      overview: {
        totalStudents: 1247,
        totalTeachers: 48,
        activeParents: 895,
        systemUsage: 92,
        revenue: 45890000,
        attendanceRate: 94.5,
        averageGrade: 78.2
      },
      academic: {
        curriculumPerformance: {
          cbc: { average: 76.8, trend: 'up' },
          igcse: { average: 82.4, trend: 'up' }
        },
        subjectPerformance: [
          { subject: 'Mathematics', average: 81.2, trend: 'up' },
          { subject: 'English', average: 78.5, trend: 'stable' },
          { subject: 'Science', average: 79.8, trend: 'up' },
          { subject: 'Kiswahili', average: 75.2, trend: 'down' }
        ],
        gradeDistribution: {
          'A (80-100%)': 35,
          'B (70-79%)': 42,
          'C (60-69%)': 18,
          'D (Below 60%)': 5
        }
      },
      financial: {
        revenueByMonth: {
          'Jan': 3850000,
          'Feb': 4120000,
          'Mar': 3980000,
          'Apr': 4250000
        },
        feeCollection: {
          collected: 85,
          pending: 12,
          overdue: 3
        },
        expenses: {
          salaries: 28500000,
          facilities: 5200000,
          resources: 3800000,
          other: 1500000
        }
      },
      userActivity: {
        dailyLogins: 2341,
        activeSessions: 892,
        peakHours: '10:00 AM',
        popularFeatures: ['Gradebook', 'Attendance', 'Parent Portal', 'Resources']
      }
    };

    setAnalyticsData(mockData);
  }, [dateRange]);

  const renderOverview = () => (
    <div className="row">
      <div className="col-md-3 col-6 mb-4">
        <div className="card border-0 bg-primary text-white">
          <div className="card-body text-center">
            <div className="display-6 fw-bold">{analyticsData.overview?.totalStudents}</div>
            <div>Total Students</div>
            <div className="small mt-2">
              <i className="bi bi-arrow-up text-success me-1"></i>
              5.2% increase
            </div>
          </div>
        </div>
      </div>
      <div className="col-md-3 col-6 mb-4">
        <div className="card border-0 bg-success text-white">
          <div className="card-body text-center">
            <div className="display-6 fw-bold">{analyticsData.overview?.attendanceRate}%</div>
            <div>Attendance Rate</div>
            <div className="small mt-2">
              <i className="bi bi-arrow-up text-warning me-1"></i>
              1.3% increase
            </div>
          </div>
        </div>
      </div>
      <div className="col-md-3 col-6 mb-4">
        <div className="card border-0 bg-info text-white">
          <div className="card-body text-center">
            <div className="display-6 fw-bold">{analyticsData.overview?.averageGrade}%</div>
            <div>Average Grade</div>
            <div className="small mt-2">
              <i className="bi bi-arrow-up text-success me-1"></i>
              2.1% increase
            </div>
          </div>
        </div>
      </div>
      <div className="col-md-3 col-6 mb-4">
        <div className="card border-0 bg-warning text-white">
          <div className="card-body text-center">
            <div className="display-6 fw-bold">{analyticsData.overview?.systemUsage}%</div>
            <div>System Usage</div>
            <div className="small mt-2">
              <i className="bi bi-arrow-up text-success me-1"></i>
              3.7% increase
            </div>
          </div>
        </div>
      </div>

      <div className="col-md-6 mb-4">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">Curriculum Performance</h6>
          </div>
          <div className="card-body">
            <div className="row text-center">
              <div className="col-6">
                <div className="display-4 fw-bold text-success">
                  {analyticsData.academic?.curriculumPerformance?.cbc?.average}%
                </div>
                <div>CBC Average</div>
                <div className="small text-success">
                  <i className="bi bi-arrow-up me-1"></i>
                  {analyticsData.academic?.curriculumPerformance?.cbc?.trend === 'up' ? 'Improving' : 'Declining'}
                </div>
              </div>
              <div className="col-6">
                <div className="display-4 fw-bold text-primary">
                  {analyticsData.academic?.curriculumPerformance?.igcse?.average}%
                </div>
                <div>IGCSE Average</div>
                <div className="small text-primary">
                  <i className="bi bi-arrow-up me-1"></i>
                  {analyticsData.academic?.curriculumPerformance?.igcse?.trend === 'up' ? 'Improving' : 'Declining'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="col-md-6 mb-4">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">Grade Distribution</h6>
          </div>
          <div className="card-body">
            {Object.entries(analyticsData.academic?.gradeDistribution || {}).map(([grade, percentage]) => (
              <div key={grade} className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span>{grade}</span>
                  <span>{percentage}%</span>
                </div>
                <div className="progress">
                  <div 
                    className="progress-bar" 
                    style={{width: `${percentage}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderAcademicAnalytics = () => (
    <div className="row">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">Subject Performance</h6>
          </div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Average Grade</th>
                    <th>Trend</th>
                    <th>Performance</th>
                  </tr>
                </thead>
                <tbody>
                  {analyticsData.academic?.subjectPerformance?.map((subject, index) => (
                    <tr key={index}>
                      <td className="fw-bold">{subject.subject}</td>
                      <td>
                        <span className={`badge ${
                          subject.average >= 80 ? 'bg-success' :
                          subject.average >= 70 ? 'bg-primary' :
                          subject.average >= 60 ? 'bg-warning' : 'bg-danger'
                        }`}>
                          {subject.average}%
                        </span>
                      </td>
                      <td>
                        <i className={`bi bi-arrow-${
                          subject.trend === 'up' ? 'up-circle text-success' :
                          subject.trend === 'down' ? 'down-circle text-danger' :
                          'dash-circle text-secondary'
                        }`}></i>
                      </td>
                      <td>
                        <div className="progress" style={{height: '8px'}}>
                          <div 
                            className="progress-bar" 
                            style={{width: `${subject.average}%`}}
                          ></div>
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
      <div className="col-md-4">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">Curriculum Comparison</h6>
          </div>
          <div className="card-body">
            <div className="text-center mb-4">
              <div className="display-4 fw-bold text-primary">
                {((analyticsData.academic?.curriculumPerformance?.igcse?.average - 
                  analyticsData.academic?.curriculumPerformance?.cbc?.average) || 0).toFixed(1)}%
              </div>
              <div>Performance Gap</div>
            </div>
            <div className="mb-3">
              <strong>CBC Strengths:</strong>
              <ul className="small mt-2">
                <li>Practical skills development</li>
                <li>Competency-based assessment</li>
                <li>Local curriculum alignment</li>
              </ul>
            </div>
            <div className="mb-3">
              <strong>IGCSE Strengths:</strong>
              <ul className="small mt-2">
                <li>International recognition</li>
                <li>University preparation</li>
                <li>Global perspectives</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFinancialAnalytics = () => (
    <div className="row">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">Revenue Trends</h6>
          </div>
          <div className="card-body">
            <div className="row text-center">
              {Object.entries(analyticsData.financial?.revenueByMonth || {}).map(([month, revenue]) => (
                <div key={month} className="col-md-3 col-6 mb-3">
                  <div className="card border-0 bg-light">
                    <div className="card-body">
                      <div className="fw-bold text-primary">
                        KES {(revenue / 1000000).toFixed(1)}M
                      </div>
                      <div className="small text-muted">{month}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card mt-4">
          <div className="card-header">
            <h6 className="mb-0">Expense Breakdown</h6>
          </div>
          <div className="card-body">
            {Object.entries(analyticsData.financial?.expenses || {}).map(([category, amount]) => (
              <div key={category} className="mb-3">
                <div className="d-flex justify-content-between mb-1">
                  <span className="text-capitalize">{category}</span>
                  <span>KES {(amount / 1000000).toFixed(1)}M</span>
                </div>
                <div className="progress">
                  <div 
                    className="progress-bar" 
                    style={{width: `${(amount / analyticsData.financial?.expenses?.salaries) * 100}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="col-md-4">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">Fee Collection Status</h6>
          </div>
          <div className="card-body text-center">
            <div className="mb-4">
              <div className="display-4 fw-bold text-success">
                {analyticsData.financial?.feeCollection?.collected}%
              </div>
              <div>Collected</div>
            </div>
            <div className="row">
              <div className="col-6">
                <div className="text-warning fw-bold">
                  {analyticsData.financial?.feeCollection?.pending}%
                </div>
                <div className="small">Pending</div>
              </div>
              <div className="col-6">
                <div className="text-danger fw-bold">
                  {analyticsData.financial?.feeCollection?.overdue}%
                </div>
                <div className="small">Overdue</div>
              </div>
            </div>
          </div>
        </div>

        <div className="card mt-4">
          <div className="card-header">
            <h6 className="mb-0">Financial Health</h6>
          </div>
          <div className="card-body">
            <div className="mb-3">
              <strong>Revenue vs Expenses</strong>
              <div className="small text-success">
                <i className="bi bi-arrow-up me-1"></i>
                15% profit margin
              </div>
            </div>
            <div className="mb-3">
              <strong>Collection Efficiency</strong>
              <div className="small text-warning">
                <i className="bi bi-dash me-1"></i>
                85% collection rate
              </div>
            </div>
            <div className="mb-3">
              <strong>Financial Reserves</strong>
              <div className="small text-info">
                <i className="bi bi-check-circle me-1"></i>
                6 months operational
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUserAnalytics = () => (
    <div className="row">
      <div className="col-md-6">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">User Activity</h6>
          </div>
          <div className="card-body">
            <div className="row text-center">
              <div className="col-6 mb-4">
                <div className="display-4 fw-bold text-primary">
                  {analyticsData.userActivity?.dailyLogins}
                </div>
                <div>Daily Logins</div>
              </div>
              <div className="col-6 mb-4">
                <div className="display-4 fw-bold text-success">
                  {analyticsData.userActivity?.activeSessions}
                </div>
                <div>Active Sessions</div>
              </div>
            </div>
            <div className="mb-3">
              <strong>Peak Usage:</strong> {analyticsData.userActivity?.peakHours}
            </div>
            <div>
              <strong>Popular Features:</strong>
              <div className="mt-2">
                {analyticsData.userActivity?.popularFeatures?.map((feature, index) => (
                  <span key={index} className="badge bg-primary me-2 mb-2">
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="col-md-6">
        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">System Performance</h6>
          </div>
          <div className="card-body">
            <div className="mb-3">
              <strong>Uptime</strong>
              <div className="progress mb-2">
                <div className="progress-bar bg-success" style={{width: '99.8%'}}>99.8%</div>
              </div>
            </div>
            <div className="mb-3">
              <strong>Response Time</strong>
              <div className="progress mb-2">
                <div className="progress-bar bg-info" style={{width: '95%'}}>95% under 500ms</div>
              </div>
            </div>
            <div className="mb-3">
              <strong>Storage Usage</strong>
              <div className="progress mb-2">
                <div className="progress-bar bg-warning" style={{width: '68%'}}>68% used</div>
              </div>
            </div>
            <div className="mb-3">
              <strong>API Requests</strong>
              <div className="progress mb-2">
                <div className="progress-bar bg-primary" style={{width: '82%'}}>82% success rate</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/admin">Admin</Link></li>
              <li className="breadcrumb-item active">Analytics</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">System Analytics</h1>
              <p className="lead mb-0">Comprehensive insights and performance metrics</p>
            </div>
            <div className="text-end">
              <select 
                className="form-select"
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                style={{width: 'auto', display: 'inline-block'}}
              >
                <option value="week">Last 7 Days</option>
                <option value="month">Last 30 Days</option>
                <option value="quarter">Last Quarter</option>
                <option value="year">Last Year</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <i className="bi bi-speedometer2 me-2"></i>
                Overview
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'academic' ? 'active' : ''}`}
                onClick={() => setActiveTab('academic')}
              >
                <i className="bi bi-journal-bookmark me-2"></i>
                Academic
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'financial' ? 'active' : ''}`}
                onClick={() => setActiveTab('financial')}
              >
                <i className="bi bi-graph-up me-2"></i>
                Financial
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'user' ? 'active' : ''}`}
                onClick={() => setActiveTab('user')}
              >
                <i className="bi bi-people me-2"></i>
                User Activity
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Overview Tab */}
          {activeTab === 'overview' && renderOverview()}

          {/* Academic Analytics Tab */}
          {activeTab === 'academic' && renderAcademicAnalytics()}

          {/* Financial Analytics Tab */}
          {activeTab === 'financial' && renderFinancialAnalytics()}

          {/* User Analytics Tab */}
          {activeTab === 'user' && renderUserAnalytics()}
        </div>
      </div>

      {/* Export and Reporting */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-body">
              <h6 className="mb-3">Reports & Export</h6>
              <div className="row">
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-primary w-100">
                    <i className="bi bi-file-pdf me-2"></i>
                    PDF Report
                  </button>
                </div>
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-success w-100">
                    <i className="bi bi-file-excel me-2"></i>
                    Excel Export
                  </button>
                </div>
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-info w-100">
                    <i className="bi bi-graph-up me-2"></i>
                    Custom Report
                  </button>
                </div>
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-warning w-100">
                    <i className="bi bi-clock me-2"></i>
                    Schedule Report
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;