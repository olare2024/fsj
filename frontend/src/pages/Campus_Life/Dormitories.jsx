import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Dormitories() {
  const [activeTab, setActiveTab] = useState('residence-halls');

  const residenceHalls = [
    {
      name: 'Pioneer Hall',
      type: 'First-Year Students',
      capacity: '200 students',
      rooms: 'Double occupancy',
      amenities: ['Study lounges', 'Common kitchen', 'Laundry facilities', 'Wi-Fi throughout'],
      features: ['ADA accessible', '24/7 security', 'Resident advisors'],
      image: '/images/pioneer-hall.jpg'
    },
    {
      name: 'Explorer Hall',
      type: 'Upperclass Students',
      capacity: '150 students',
      rooms: 'Single & Double suites',
      amenities: ['Private bathrooms', 'Study rooms', 'Game room', 'Fitness center'],
      features: ['Air conditioning', 'Elevator access', 'Package reception'],
      image: '/images/explorer-hall.jpg'
    },
    {
      name: 'Innovator Hall',
      type: 'Honors Program',
      capacity: '100 students',
      rooms: 'Single occupancy suites',
      amenities: ['Private study carrels', 'Seminar rooms', 'Music practice rooms', 'Roof terrace'],
      features: ['Smart classrooms', 'Research labs', 'Faculty-in-residence'],
      image: '/images/innovator-hall.jpg'
    }
  ];

  const roomTypes = [
    {
      type: 'Standard Double',
      description: 'Traditional double room with shared hallway bathroom',
      size: '180 sq ft',
      occupancy: '2 students',
      cost: '$4,500/semester',
      includes: ['Twin XL bed', 'Desk & chair', 'Wardrobe', 'Bookshelf']
    },
    {
      type: 'Single Suite',
      description: 'Private room with shared suite bathroom',
      size: '120 sq ft',
      occupancy: '1 student',
      cost: '$6,800/semester',
      includes: ['Twin XL bed', 'Study area', 'Private closet', 'Mini-fridge']
    },
    {
      type: 'Double Suite',
      description: 'Two-bedroom suite with shared living area',
      size: '350 sq ft',
      occupancy: '4 students',
      cost: '$5,200/semester/person',
      includes: ['Private bedrooms', 'Common area', 'Kitchenette', 'Two bathrooms']
    }
  ];

  const policies = [
    {
      category: 'Visitation Hours',
      rules: [
        'Guests allowed: 10:00 AM - 12:00 AM',
        'Overnight guests require prior approval',
        'Maximum 2 guests per resident'
      ]
    },
    {
      category: 'Quiet Hours',
      rules: [
        'Sunday-Thursday: 10:00 PM - 8:00 AM',
        'Friday-Saturday: 12:00 AM - 10:00 AM',
        '24-hour quiet floors available'
      ]
    },
    {
      category: 'Safety & Security',
      rules: [
        'Keycard access required after 8:00 PM',
        'No open flames or candles',
        'Emergency procedures posted on each floor'
      ]
    }
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Campus Housing</h1>
          <p className="lead">Your home away from home - comfortable, safe, and supportive living environments</p>
        </div>
        <Link to="/campus-life" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Campus Life
        </Link>
      </div>

      {/* Hero Section */}
      <div className="card bg-primary text-white mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="display-6 fw-bold">Live and Learn Together</h2>
              <p className="lead mb-0">
                Our residence halls are designed to foster community, support academic success, 
                and provide a comfortable living experience for all students.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-house-door display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>85%</h3>
              <p className="mb-0">Students Live On Campus</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>6</h3>
              <p className="mb-0">Residence Halls</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>24/7</h3>
              <p className="mb-0">Resident Support</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-secondary text-white">
            <div className="card-body text-center">
              <h3>100%</h3>
              <p className="mb-0">Secure Facilities</p>
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
                className={`nav-link ${activeTab === 'residence-halls' ? 'active' : ''}`}
                onClick={() => setActiveTab('residence-halls')}
              >
                <i className="bi bi-building me-2"></i>
                Residence Halls
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'room-types' ? 'active' : ''}`}
                onClick={() => setActiveTab('room-types')}
              >
                <i className="bi bi-door-closed me-2"></i>
                Room Types
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'policies' ? 'active' : ''}`}
                onClick={() => setActiveTab('policies')}
              >
                <i className="bi bi-journal-text me-2"></i>
                Policies
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'apply' ? 'active' : ''}`}
                onClick={() => setActiveTab('apply')}
              >
                <i className="bi bi-pencil me-2"></i>
                Apply for Housing
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Residence Halls Tab */}
          {activeTab === 'residence-halls' && (
            <div>
              <h4>Our Residence Halls</h4>
              <p className="text-muted mb-4">
                Each residence hall offers unique features and communities to suit different student needs.
              </p>

              <div className="row g-4">
                {residenceHalls.map((hall, index) => (
                  <div key={index} className="col-lg-4">
                    <div className="card h-100">
                      <div className="card-img-top bg-light d-flex align-items-center justify-content-center" style={{height: '200px'}}>
                        <i className="bi bi-building display-1 text-muted"></i>
                      </div>
                      <div className="card-body">
                        <h5 className="card-title">{hall.name}</h5>
                        <p className="card-text text-muted">{hall.type}</p>
                        
                        <div className="hall-details">
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Capacity:</strong>
                            <span>{hall.capacity}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-3">
                            <strong>Room Types:</strong>
                            <span>{hall.rooms}</span>
                          </div>

                          <h6>Amenities:</h6>
                          <div className="d-flex flex-wrap gap-1 mb-3">
                            {hall.amenities.map((amenity, idx) => (
                              <span key={idx} className="badge bg-primary">{amenity}</span>
                            ))}
                          </div>

                          <h6>Features:</h6>
                          <div className="d-flex flex-wrap gap-1">
                            {hall.features.map((feature, idx) => (
                              <span key={idx} className="badge bg-secondary">{feature}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm me-2">
                          View Photos
                        </button>
                        <button className="btn btn-outline-secondary btn-sm">
                          Floor Plans
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Room Types Tab */}
          {activeTab === 'room-types' && (
            <div>
              <h4>Room Types & Accommodations</h4>
              <p className="text-muted mb-4">
                Choose the living arrangement that best fits your needs and preferences.
              </p>

              <div className="row g-4">
                {roomTypes.map((room, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{room.type}</h5>
                      </div>
                      <div className="card-body">
                        <p className="card-text">{room.description}</p>
                        
                        <div className="room-specs">
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Size:</strong>
                            <span>{room.size}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Occupancy:</strong>
                            <span>{room.occupancy}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-3">
                            <strong>Cost:</strong>
                            <span className="text-success fw-bold">{room.cost}</span>
                          </div>

                          <h6>Includes:</h6>
                          <ul className="list-unstyled">
                            {room.includes.map((item, idx) => (
                              <li key={idx} className="mb-1">
                                <i className="bi bi-check-circle text-success me-2"></i>
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-primary btn-sm w-100">
                          Select This Room
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Special Accommodations</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        We provide accommodations for students with disabilities, medical needs, 
                        or other special circumstances.
                      </p>
                      <ul>
                        <li>ADA accessible rooms</li>
                        <li>Single rooms for medical needs</li>
                        <li>Allergy-sensitive housing</li>
                        <li>Gender-inclusive housing options</li>
                      </ul>
                      <button className="btn btn-outline-primary">
                        Request Accommodations
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">What to Bring</h5>
                    </div>
                    <div className="card-body">
                      <div className="row">
                        <div className="col-6">
                          <h6>Do Bring:</h6>
                          <ul className="small">
                            <li>Bed linens (Twin XL)</li>
                            <li>Towels & toiletries</li>
                            <li>Desk lamp</li>
                            <li>Study supplies</li>
                          </ul>
                        </div>
                        <div className="col-6">
                          <h6>Don't Bring:</h6>
                          <ul className="small">
                            <li>Candles/incense</li>
                            <li>Hot plates</li>
                            <li>Pets (except fish)</li>
                            <li>Weapons</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Policies Tab */}
          {activeTab === 'policies' && (
            <div>
              <h4>Residence Life Policies</h4>
              <p className="text-muted mb-4">
                These policies ensure a safe, respectful, and productive living environment for all residents.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  {policies.map((policy, index) => (
                    <div key={index} className="card mb-4">
                      <div className="card-header">
                        <h5 className="mb-0">{policy.category}</h5>
                      </div>
                      <div className="card-body">
                        <ul className="list-unstyled">
                          {policy.rules.map((rule, ruleIndex) => (
                            <li key={ruleIndex} className="mb-2">
                              <i className="bi bi-check-circle text-primary me-2"></i>
                              {rule}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}

                  <div className="alert alert-warning">
                    <h6><i className="bi bi-exclamation-triangle me-2"></i>Important Notice</h6>
                    <p className="mb-0">
                      Violation of residence policies may result in disciplinary action, 
                      including possible removal from campus housing. All students are 
                      expected to read and comply with the complete Student Housing Agreement.
                    </p>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-light">
                    <div className="card-body text-center">
                      <i className="bi bi-headset display-4 text-primary mb-3"></i>
                      <h5>Need Help?</h5>
                      <p className="text-muted">
                        Our Residence Life staff is here to support you.
                      </p>
                      <div className="d-grid gap-2">
                        <button className="btn btn-primary">
                          Contact RA
                        </button>
                        <button className="btn btn-outline-primary">
                          Emergency Contact
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h5 className="mb-0">Quick Links</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-secondary text-start">
                          Maintenance Request
                        </button>
                        <button className="btn btn-outline-secondary text-start">
                          Room Change Request
                        </button>
                        <button className="btn btn-outline-secondary text-start">
                          Package Tracking
                        </button>
                        <button className="btn btn-outline-secondary text-start">
                          Laundry Status
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Apply for Housing Tab */}
          {activeTab === 'apply' && (
            <div>
              <h4>Apply for Campus Housing</h4>
              <p className="text-muted mb-4">
                Secure your spot in our campus community. Follow these steps to apply for housing.
              </p>

              <div className="row">
                <div className="col-lg-8">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Housing Application Process</h5>
                    </div>
                    <div className="card-body">
                      <div className="steps">
                        <div className="step">
                          <div className="step-number">1</div>
                          <div className="step-content">
                            <h5>Submit Admission Application</h5>
                            <p>
                              You must be accepted to Delvok Academy before you can apply for housing.
                            </p>
                          </div>
                        </div>
                        <div className="step">
                          <div className="step-number">2</div>
                          <div className="step-content">
                            <h5>Complete Housing Application</h5>
                            <p>
                              Log into the housing portal and complete the online application form.
                            </p>
                          </div>
                        </div>
                        <div className="step">
                          <div className="step-number">3</div>
                          <div className="step-content">
                            <h5>Pay Housing Deposit</h5>
                            <p>
                              Submit the $300 housing deposit to secure your room assignment.
                            </p>
                          </div>
                        </div>
                        <div className="step">
                          <div className="step-number">4</div>
                          <div className="step-content">
                            <h5>Room Selection</h5>
                            <p>
                              Based on your application date and preferences, select your room.
                            </p>
                          </div>
                        </div>
                        <div className="step">
                          <div className="step-number">5</div>
                          <div className="step-content">
                            <h5>Receive Assignment</h5>
                            <p>
                              You'll receive your room assignment and roommate information.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h5 className="mb-0">Important Dates</h5>
                    </div>
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table table-striped">
                          <thead>
                            <tr>
                              <th>Term</th>
                              <th>Application Opens</th>
                              <th>Priority Deadline</th>
                              <th>Move-In Day</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr>
                              <td>Fall Semester</td>
                              <td>March 1</td>
                              <td>May 1</td>
                              <td>August 15</td>
                            </tr>
                            <tr>
                              <td>Spring Semester</td>
                              <td>November 1</td>
                              <td>December 1</td>
                              <td>January 10</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card bg-primary text-white">
                    <div className="card-body text-center">
                      <h5>Ready to Apply?</h5>
                      <p>
                        Begin your housing application process today.
                      </p>
                      <div className="d-grid gap-2">
                        <button className="btn btn-light">
                          Start Housing Application
                        </button>
                        <button className="btn btn-outline-light">
                          Housing Portal Login
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-header">
                      <h5 className="mb-0">Contact Housing Office</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-flex mb-3">
                        <i className="bi bi-telephone text-primary me-3"></i>
                        <div>
                          <strong>Phone</strong>
                          <div>(555) 123-HOME</div>
                        </div>
                      </div>
                      <div className="d-flex mb-3">
                        <i className="bi bi-envelope text-primary me-3"></i>
                        <div>
                          <strong>Email</strong>
                          <div>housing@delvok.edu</div>
                        </div>
                      </div>
                      <div className="d-flex">
                        <i className="bi bi-clock text-primary me-3"></i>
                        <div>
                          <strong>Office Hours</strong>
                          <div>Mon-Fri: 9:00 AM - 5:00 PM</div>
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

export default Dormitories;