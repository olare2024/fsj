import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Transportation() {
  const [activeTab, setActiveTab] = useState('shuttle');

  const shuttleRoutes = [
    {
      name: 'Campus Loop',
      description: 'Circles main campus every 15 minutes',
      hours: '7:00 AM - 11:00 PM',
      frequency: '15 minutes',
      stops: ['Main Entrance', 'Library', 'Student Center', 'Residence Halls', 'Academic Buildings'],
      status: 'operational'
    },
    {
      name: 'Downtown Express',
      description: 'Direct service to downtown area',
      hours: '6:30 AM - 10:00 PM',
      frequency: '30 minutes',
      stops: ['Student Center', 'City Center', 'Shopping District', 'Entertainment Area'],
      status: 'operational'
    },
    {
      name: 'Weekend Shopper',
      description: 'Weekend shopping and grocery service',
      hours: 'Sat-Sun: 9:00 AM - 6:00 PM',
      frequency: '45 minutes',
      stops: ['Campus', 'Supermarket', 'Mall', 'Pharmacy', 'Campus'],
      status: 'operational'
    }
  ];

  const parkingOptions = [
    {
      lot: 'A - Student Parking',
      location: 'North Campus',
      capacity: '250 spots',
      permit: '$150/semester',
      restrictions: 'Student permit required 7 AM - 5 PM',
      availability: 'Medium'
    },
    {
      lot: 'B - Commuter Parking',
      location: 'East Campus',
      capacity: '180 spots',
      permit: '$100/semester',
      restrictions: 'Commuter permit only',
      availability: 'High'
    },
    {
      lot: 'C - Visitor Parking',
      location: 'Main Entrance',
      capacity: '75 spots',
      permit: 'Daily rate: $5',
      restrictions: '2-hour limit, pay station',
      availability: 'Low'
    }
  ];

  const publicTransportation = [
    {
      service: 'City Bus Route 15',
      description: 'Direct route to campus from city center',
      frequency: '20 minutes',
      hours: '5:30 AM - 11:30 PM',
      cost: 'Student discount available',
      stops: ['City Terminal', 'Campus Main Gate', 'Student Center']
    },
    {
      service: 'Metro Rail - Green Line',
      description: 'Light rail service with campus station',
      frequency: '15 minutes',
      hours: '6:00 AM - 12:00 AM',
      cost: 'Reduced student fare',
      stops: ['Downtown Station', 'Campus Station', 'North Terminal']
    }
  ];

  const bikeProgram = [
    {
      program: 'Bike Share',
      description: 'Rent bikes for campus travel',
      cost: 'Free for students',
      locations: '8 stations across campus',
      requirements: 'Student ID required'
    },
    {
      program: 'Bike Repair Stations',
      description: 'Free tools and air pumps',
      cost: 'Free',
      locations: '4 locations',
      requirements: 'Bring your own bike'
    },
    {
      program: 'Bike Registration',
      description: 'Register your bike for security',
      cost: 'Free',
      locations: 'Campus Security Office',
      requirements: 'Proof of ownership'
    }
  ];

  const getAvailabilityBadge = (availability) => {
    switch (availability.toLowerCase()) {
      case 'high': return 'bg-success';
      case 'medium': return 'bg-warning';
      case 'low': return 'bg-danger';
      default: return 'bg-secondary';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Campus Transportation</h1>
          <p className="lead">Getting around campus and the city made easy and convenient</p>
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
              <h2 className="display-6 fw-bold">Easy Campus Navigation</h2>
              <p className="lead mb-0">
                Multiple transportation options to help you move around campus and explore the city 
                safely and efficiently.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-bus-front display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body text-center">
              <h3>24/7</h3>
              <p className="mb-0">Safe Ride Service</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>Free</h3>
              <p className="mb-0">Campus Shuttle</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>500+</h3>
              <p className="mb-0">Parking Spots</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-secondary text-white">
            <div className="card-body text-center">
              <h3>8</h3>
              <p className="mb-0">Bike Stations</p>
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
                className={`nav-link ${activeTab === 'shuttle' ? 'active' : ''}`}
                onClick={() => setActiveTab('shuttle')}
              >
                <i className="bi bi-bus-front me-2"></i>
                Campus Shuttle
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'parking' ? 'active' : ''}`}
                onClick={() => setActiveTab('parking')}
              >
                <i className="bi bi-p-square me-2"></i>
                Parking
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'public' ? 'active' : ''}`}
                onClick={() => setActiveTab('public')}
              >
                <i className="bi bi-train-front me-2"></i>
                Public Transit
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'bike' ? 'active' : ''}`}
                onClick={() => setActiveTab('bike')}
              >
                <i className="bi bi-bicycle me-2"></i>
                Bike Programs
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Campus Shuttle Tab */}
          {activeTab === 'shuttle' && (
            <div>
              <h4>Campus Shuttle Service</h4>
              <p className="text-muted mb-4">
                Free shuttle service connecting all campus locations and nearby areas.
              </p>

              <div className="row g-4">
                {shuttleRoutes.map((route, index) => (
                  <div key={index} className="col-lg-4">
                    <div className="card h-100">
                      <div className="card-header d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">{route.name}</h5>
                        <span className="badge bg-success">{route.status}</span>
                      </div>
                      <div className="card-body">
                        <p className="card-text">{route.description}</p>
                        
                        <div className="route-details">
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Hours:</strong>
                            <span>{route.hours}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-3">
                            <strong>Frequency:</strong>
                            <span>{route.frequency}</span>
                          </div>

                          <h6>Main Stops:</h6>
                          <ul className="small">
                            {route.stops.map((stop, idx) => (
                              <li key={idx}>{stop}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm me-2">
                          Live Tracking
                        </button>
                        <button className="btn btn-outline-secondary btn-sm">
                          Full Schedule
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
                      <h5 className="mb-0">Shuttle App</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Track shuttles in real-time with our mobile app. See estimated arrival 
                        times and receive service alerts.
                      </p>
                      <div className="d-grid gap-2">
                        <button className="btn btn-primary">
                          <i className="bi bi-phone me-2"></i>
                          Download App
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Safe Ride Service</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        After shuttle hours, use our Safe Ride service for secure transportation 
                        around campus.
                      </p>
                      <ul>
                        <li>Available: 11:00 PM - 7:00 AM</li>
                        <li>Call: (555) RIDE-NOW</li>
                        <li>Free for students with ID</li>
                        <li>On-demand service</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Parking Tab */}
          {activeTab === 'parking' && (
            <div>
              <h4>Parking Information</h4>
              <p className="text-muted mb-4">
                Parking options and regulations for students, faculty, and visitors.
              </p>

              <div className="row g-4">
                {parkingOptions.map((lot, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">Lot {lot.lot}</h5>
                        <span className={`badge ${getAvailabilityBadge(lot.availability)}`}>
                          {lot.availability} Availability
                        </span>
                      </div>
                      <div className="card-body">
                        <div className="lot-details">
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Location:</strong>
                            <span>{lot.location}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Capacity:</strong>
                            <span>{lot.capacity}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-3">
                            <strong>Permit Cost:</strong>
                            <span className="text-success">{lot.permit}</span>
                          </div>

                          <h6>Restrictions:</h6>
                          <p className="small text-muted">{lot.restrictions}</p>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-primary btn-sm w-100">
                          Purchase Permit
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
                      <h5 className="mb-0">Parking Regulations</h5>
                    </div>
                    <div className="card-body">
                      <ul>
                        <li>Permit must be displayed at all times</li>
                        <li>No parking in fire lanes or disabled spots without permit</li>
                        <li>Overnight parking allowed in designated lots</li>
                        <li>Violators subject to fines and towing</li>
                      </ul>
                      <button className="btn btn-outline-primary">
                        View Complete Regulations
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Electric Vehicle Charging</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        EV charging stations available in Lot A and Lot B.
                      </p>
                      <ul>
                        <li>4 charging stations in Lot A</li>
                        <li>2 charging stations in Lot B</li>
                        <li>Cost: $0.15 per kWh</li>
                        <li>Reservation through parking app</li>
                      </ul>
                      <button className="btn btn-outline-success">
                        Reserve Charger
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Public Transit Tab */}
          {activeTab === 'public' && (
            <div>
              <h4>Public Transportation</h4>
              <p className="text-muted mb-4">
                Connect with city-wide transportation services from campus.
              </p>

              <div className="row g-4">
                {publicTransportation.map((service, index) => (
                  <div key={index} className="col-lg-6">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{service.service}</h5>
                      </div>
                      <div className="card-body">
                        <p className="card-text">{service.description}</p>
                        
                        <div className="service-details">
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Frequency:</strong>
                            <span>{service.frequency}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Hours:</strong>
                            <span>{service.hours}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-3">
                            <strong>Cost:</strong>
                            <span className="text-success">{service.cost}</span>
                          </div>

                          <h6>Key Stops:</h6>
                          <div className="d-flex flex-wrap gap-1">
                            {service.stops.map((stop, idx) => (
                              <span key={idx} className="badge bg-primary">{stop}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm me-2">
                          Schedule
                        </button>
                        <button className="btn btn-outline-secondary btn-sm">
                          Fare Information
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
                      <h5 className="mb-0">Student Transit Pass</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Discounted transit passes for unlimited rides on all city buses and rail services.
                      </p>
                      <ul>
                        <li>Cost: $45 per semester</li>
                        <li>Unlimited rides on all routes</li>
                        <li>Available at Student Services</li>
                        <li>Valid for entire semester</li>
                      </ul>
                      <button className="btn btn-primary">
                        Purchase Transit Pass
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Transportation Resources</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-primary text-start">
                          City Transit Map
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          Trip Planner
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          Service Alerts
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          Lost & Found
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Bike Programs Tab */}
          {activeTab === 'bike' && (
            <div>
              <h4>Bike Programs & Facilities</h4>
              <p className="text-muted mb-4">
                Sustainable transportation options and bike-friendly campus amenities.
              </p>

              <div className="row g-4">
                {bikeProgram.map((program, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{program.program}</h5>
                      </div>
                      <div className="card-body">
                        <p className="card-text">{program.description}</p>
                        
                        <div className="program-details">
                          <div className="d-flex justify-content-between mb-2">
                            <strong>Cost:</strong>
                            <span className="text-success">{program.cost}</span>
                          </div>
                          <div className="d-flex justify-content-between mb-3">
                            <strong>Locations:</strong>
                            <span>{program.locations}</span>
                          </div>

                          <h6>Requirements:</h6>
                          <p className="small text-muted">{program.requirements}</p>
                        </div>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm w-100">
                          Learn More
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
                      <h5 className="mb-0">Bike Safety</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Stay safe while biking on and around campus.
                      </p>
                      <ul>
                        <li>Always wear a helmet</li>
                        <li>Use bike lanes when available</li>
                        <li>Follow traffic signals and signs</li>
                        <li>Use lights at night</li>
                        <li>Lock your bike securely</li>
                      </ul>
                      <button className="btn btn-outline-primary">
                        Safety Guidelines
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Bike Map & Routes</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Discover the best bike routes around campus and the city.
                      </p>
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-success">
                          Campus Bike Map
                        </button>
                        <button className="btn btn-outline-success">
                          City Bike Routes
                        </button>
                        <button className="btn btn-outline-success">
                          Bike Trail Guide
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Transportation;