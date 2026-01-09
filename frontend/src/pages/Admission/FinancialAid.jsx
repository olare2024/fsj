import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function FinancialAid() {
  const [activeTab, setActiveTab] = useState('types');
  const [showCalculator, setShowCalculator] = useState(false);

  const aidTypes = [
    {
      type: 'Merit Scholarships',
      description: 'Awarded based on academic achievement, talents, or special skills',
      amount: 'Up to full tuition',
      deadline: 'Rolling',
      requirements: ['Minimum 3.5 GPA', 'Strong academic record', 'May require interview'],
      application: 'Automatic consideration with application'
    },
    {
      type: 'Need-Based Grants',
      description: 'Awarded based on demonstrated financial need',
      amount: 'Varies by need',
      deadline: 'February 1',
      requirements: ['Completed FAFSA', 'Financial need verification', 'Maintain satisfactory academic progress'],
      application: 'FAFSA required'
    },
    {
      type: 'Athletic Scholarships',
      description: 'For students who excel in sports and will participate in school athletics',
      amount: 'Partial to full tuition',
      deadline: 'Varies by sport',
      requirements: ['Athletic ability', 'Team participation', 'Academic eligibility'],
      application: 'Coach recommendation required'
    },
    {
      type: 'Arts Scholarships',
      description: 'For students with exceptional talent in visual arts, music, or theater',
      amount: 'Up to $10,000/year',
      deadline: 'March 1',
      requirements: ['Portfolio or audition', 'Artistic merit', 'Academic minimums'],
      application: 'Portfolio/audition required'
    }
  ];

  const deadlines = [
    { name: 'Early Decision Financial Aid', date: 'January 15', status: 'upcoming' },
    { name: 'FAFSA Priority Deadline', date: 'February 1', status: 'upcoming' },
    { name: 'Merit Scholarship Consideration', date: 'March 1', status: 'open' },
    { name: 'Transfer Student Aid', date: 'May 1', status: 'open' }
  ];

  const calculatorFields = {
    familyIncome: '',
    householdSize: '',
    assets: '',
    expenses: ''
  };

  const [calcData, setCalcData] = useState(calculatorFields);

  const handleCalcChange = (field, value) => {
    setCalcData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateAid = () => {
    // Simple mock calculation
    const income = parseInt(calcData.familyIncome) || 0;
    const household = parseInt(calcData.householdSize) || 1;
    
    let estimatedAid = 0;
    if (income < 50000) {
      estimatedAid = 15000;
    } else if (income < 100000) {
      estimatedAid = 10000;
    } else if (income < 150000) {
      estimatedAid = 5000;
    }
    
    // Adjust for household size
    if (household > 4) estimatedAid += 2000;
    
    return estimatedAid;
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Financial Aid & Scholarships</h1>
          <p className="lead">Making quality education affordable for every family</p>
        </div>
        <Link to="/admissions" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Admissions
        </Link>
      </div>

      {/* Hero Section */}
      <div className="card bg-success text-white mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="display-6 fw-bold">Invest in Your Future</h2>
              <p className="lead mb-0">
                Over 65% of our students receive financial assistance. We're committed to making 
                Delvok Academy accessible through generous aid packages and scholarships.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-cash-coin display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>$2.5M</h3>
              <p className="mb-0">Awarded Annually</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>65%</h3>
              <p className="mb-0">Students Receive Aid</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>50+</h3>
              <p className="mb-0">Scholarship Programs</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>100%</h3>
              <p className="mb-0">Meet Demonstrated Need</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Tabs */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'types' ? 'active' : ''}`}
                onClick={() => setActiveTab('types')}
              >
                <i className="bi bi-award me-2"></i>
                Aid Types
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'process' ? 'active' : ''}`}
                onClick={() => setActiveTab('process')}
              >
                <i className="bi bi-gear me-2"></i>
                Application Process
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'calculator' ? 'active' : ''}`}
                onClick={() => setActiveTab('calculator')}
              >
                <i className="bi bi-calculator me-2"></i>
                Aid Calculator
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'deadlines' ? 'active' : ''}`}
                onClick={() => setActiveTab('deadlines')}
              >
                <i className="bi bi-calendar me-2"></i>
                Deadlines
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Aid Types Tab */}
          {activeTab === 'types' && (
            <div>
              <h4>Types of Financial Assistance</h4>
              <p className="text-muted mb-4">
                We offer various types of financial aid to help make your education affordable.
              </p>

              <div className="row g-4">
                {aidTypes.map((aid, index) => (
                  <div key={index} className="col-md-6">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{aid.type}</h5>
                      </div>
                      <div className="card-body">
                        <p className="card-text">{aid.description}</p>
                        
                        <div className="aid-details">
                          <div className="d-flex justify-content-between align-items-center mb-2">
                            <strong>Amount:</strong>
                            <span className="text-success">{aid.amount}</span>
                          </div>
                          <div className="d-flex justify-content-between align-items-center mb-3">
                            <strong>Deadline:</strong>
                            <span className="text-primary">{aid.deadline}</span>
                          </div>

                          <h6>Requirements:</h6>
                          <ul className="small">
                            {aid.requirements.map((req, reqIndex) => (
                              <li key={reqIndex}>{req}</li>
                            ))}
                          </ul>

                          <div className="application-info">
                            <small className="text-muted">
                              <strong>Application:</strong> {aid.application}
                            </small>
                          </div>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm">
                          Learn More
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="alert alert-info mt-4">
                <h6><i className="bi bi-lightbulb me-2"></i>Maximize Your Aid Package</h6>
                <p className="mb-0">
                  Students can receive multiple types of aid. Most merit scholarships can be 
                  combined with need-based grants. Contact our financial aid office to discuss 
                  your specific situation.
                </p>
              </div>
            </div>
          )}

          {/* Application Process Tab */}
          {activeTab === 'process' && (
            <div>
              <h4>Financial Aid Application Process</h4>
              <p className="text-muted mb-4">
                Follow these steps to apply for financial assistance.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="steps">
                    <div className="step">
                      <div className="step-number">1</div>
                      <div className="step-content">
                        <h5>Submit Admission Application</h5>
                        <p>
                          Complete your Delvok Academy admission application. Many scholarships 
                          require separate applications, but some are automatically considered.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">2</div>
                      <div className="step-content">
                        <h5>Complete FAFSA</h5>
                        <p>
                          Submit the Free Application for Federal Student Aid (FAFSA) using our 
                          school code: <strong>003456</strong>. This is required for need-based aid.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">3</div>
                      <div className="step-content">
                        <h5>Apply for Scholarships</h5>
                        <p>
                          Review available scholarships and submit any required additional 
                          applications, essays, or portfolios by the deadlines.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">4</div>
                      <div className="step-content">
                        <h5>Submit Additional Documents</h5>
                        <p>
                          Provide any requested verification documents, tax returns, or 
                          additional financial information.
                        </p>
                      </div>
                    </div>
                    <div className="step">
                      <div className="step-number">5</div>
                      <div className="step-content">
                        <h5>Receive Aid Package</h5>
                        <p>
                          You will receive your financial aid award letter detailing all 
                          grants, scholarships, and loan options.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-light">
                    <div className="card-header">
                      <h5 className="mb-0">Required Documents</h5>
                    </div>
                    <div className="card-body">
                      <ul className="list-unstyled">
                        <li className="mb-2">
                          <i className="bi bi-file-text text-primary me-2"></i>
                          Completed FAFSA
                        </li>
                        <li className="mb-2">
                          <i className="bi bi-file-text text-primary me-2"></i>
                          Tax returns (2 years)
                        </li>
                        <li className="mb-2">
                          <i className="bi bi-file-text text-primary me-2"></i>
                          W-2 forms
                        </li>
                        <li className="mb-2">
                          <i className="bi bi-file-text text-primary me-2"></i>
                          Bank statements
                        </li>
                        <li className="mb-2">
                          <i className="bi bi-file-text text-primary me-2"></i>
                          Investment records
                        </li>
                        <li>
                          <i className="bi bi-file-text text-primary me-2"></i>
                          Scholarship applications
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Aid Calculator Tab */}
          {activeTab === 'calculator' && (
            <div>
              <h4>Financial Aid Calculator</h4>
              <p className="text-muted mb-4">
                Get an early estimate of your potential financial aid package.
              </p>

              <div className="row">
                <div className="col-lg-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Estimate Your Aid</h5>
                    </div>
                    <div className="card-body">
                      <form>
                        <div className="mb-3">
                          <label className="form-label">Annual Family Income</label>
                          <div className="input-group">
                            <span className="input-group-text">$</span>
                            <input
                              type="number"
                              className="form-control"
                              value={calcData.familyIncome}
                              onChange={(e) => handleCalcChange('familyIncome', e.target.value)}
                              placeholder="Enter annual income"
                            />
                          </div>
                        </div>

                        <div className="mb-3">
                          <label className="form-label">Household Size</label>
                          <input
                            type="number"
                            className="form-control"
                            value={calcData.householdSize}
                            onChange={(e) => handleCalcChange('householdSize', e.target.value)}
                            placeholder="Number of family members"
                            min="1"
                            max="10"
                          />
                        </div>

                        <div className="mb-3">
                          <label className="form-label">Assets (Savings, Investments)</label>
                          <div className="input-group">
                            <span className="input-group-text">$</span>
                            <input
                              type="number"
                              className="form-control"
                              value={calcData.assets}
                              onChange={(e) => handleCalcChange('assets', e.target.value)}
                              placeholder="Total assets"
                            />
                          </div>
                        </div>

                        <div className="mb-3">
                          <label className="form-label">Monthly Expenses</label>
                          <div className="input-group">
                            <span className="input-group-text">$</span>
                            <input
                              type="number"
                              className="form-control"
                              value={calcData.expenses}
                              onChange={(e) => handleCalcChange('expenses', e.target.value)}
                              placeholder="Monthly expenses"
                            />
                          </div>
                        </div>

                        <button
                          type="button"
                          className="btn btn-primary"
                          onClick={() => setShowCalculator(true)}
                        >
                          Calculate Aid Estimate
                        </button>
                      </form>
                    </div>
                  </div>
                </div>

                <div className="col-lg-6">
                  {showCalculator ? (
                    <div className="card bg-success text-white">
                      <div className="card-body text-center">
                        <h5>Estimated Financial Aid</h5>
                        <div className="display-4 fw-bold my-4">
                          ${calculateAid().toLocaleString()}
                        </div>
                        <p className="mb-3">
                          Estimated annual aid package based on the information provided.
                        </p>
                        <div className="alert alert-light text-dark">
                          <small>
                            <strong>Note:</strong> This is an estimate only. Your actual aid 
                            package may vary based on complete financial review and available funds.
                          </small>
                        </div>
                        <button 
                          className="btn btn-light"
                          onClick={() => setShowCalculator(false)}
                        >
                          Recalculate
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="card bg-light">
                      <div className="card-body text-center py-5">
                        <i className="bi bi-calculator display-1 text-muted mb-3"></i>
                        <h5>Get Your Estimate</h5>
                        <p className="text-muted">
                          Fill out the form to see an estimate of your potential financial aid package.
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="card mt-4">
                    <div className="card-body">
                      <h6>Next Steps</h6>
                      <ul className="small">
                        <li>This estimate is for planning purposes only</li>
                        <li>Complete the FAFSA for official determination</li>
                        <li>Apply for additional scholarships</li>
                        <li>Contact financial aid with questions</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Deadlines Tab */}
          {activeTab === 'deadlines' && (
            <div>
              <h4>Financial Aid Deadlines</h4>
              <p className="text-muted mb-4">
                Mark these important dates on your calendar to ensure you don't miss any opportunities.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="card">
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table table-striped">
                          <thead>
                            <tr>
                              <th>Program/Deadline</th>
                              <th>Date</th>
                              <th>Status</th>
                              <th>Action</th>
                            </tr>
                          </thead>
                          <tbody>
                            {deadlines.map((deadline, index) => (
                              <tr key={index}>
                                <td>
                                  <strong>{deadline.name}</strong>
                                </td>
                                <td>{deadline.date}</td>
                                <td>
                                  <span className={`badge ${
                                    deadline.status === 'upcoming' ? 'bg-warning' :
                                    deadline.status === 'open' ? 'bg-success' :
                                    'bg-secondary'
                                  }`}>
                                    {deadline.status}
                                  </span>
                                </td>
                                <td>
                                  <button className="btn btn-sm btn-outline-primary">
                                    Apply Now
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="alert alert-warning mt-4">
                    <h6><i className="bi bi-exclamation-triangle me-2"></i>Important Reminders</h6>
                    <ul className="mb-0">
                      <li>FAFSA becomes available October 1 each year</li>
                      <li>Some scholarships have limited funds - apply early</li>
                      <li>International students have different deadlines and requirements</li>
                    </ul>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-primary text-white">
                    <div className="card-body text-center">
                      <h5>Ready to Apply?</h5>
                      <p>
                        Start your financial aid application today. Our team is here to help 
                        you navigate the process.
                      </p>
                      <div className="d-grid gap-2">
                        <button className="btn btn-light">
                          Start FAFSA
                        </button>
                        <button className="btn btn-outline-light">
                          View Scholarship Applications
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h5 className="mb-0">Financial Aid Office</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-flex mb-3">
                        <i className="bi bi-envelope text-primary me-3"></i>
                        <div>
                          <strong>Email</strong>
                          <div>finaid@delvok.edu</div>
                        </div>
                      </div>
                      <div className="d-flex mb-3">
                        <i className="bi bi-telephone text-primary me-3"></i>
                        <div>
                          <strong>Phone</strong>
                          <div>(555) 123-FAID</div>
                        </div>
                      </div>
                      <div className="d-flex">
                        <i className="bi bi-clock text-primary me-3"></i>
                        <div>
                          <strong>Office Hours</strong>
                          <div>Mon-Fri: 8:30 AM - 5:00 PM</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .steps {
          position: relative;
          padding-left: 30px;
        }
        .step {
          position: relative;
          margin-bottom: 2rem;
        }
        .step-number {
          position: absolute;
          left: -30px;
          top: 0;
          width: 40px;
          height: 40px;
          background: var(--bs-primary);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
        }
        .step:not(:last-child):after {
          content: '';
          position: absolute;
          left: -11px;
          top: 40px;
          bottom: -2rem;
          width: 2px;
          background: var(--bs-primary);
          opacity: 0.3;
        }
      `}</style>
    </div>
  );
}

export default FinancialAid;