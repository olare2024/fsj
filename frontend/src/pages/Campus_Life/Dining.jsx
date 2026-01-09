import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Dining() {
  const [activeTab, setActiveTab] = useState('dining-halls');
  const [selectedDay, setSelectedDay] = useState('monday');

  const diningLocations = [
    {
      name: 'Commons Dining Hall',
      type: 'All-You-Care-to-Eat',
      hours: {
        weekdays: '7:00 AM - 8:00 PM',
        weekends: '9:00 AM - 7:00 PM'
      },
      features: ['Multiple stations', 'Vegetarian options', 'Gluten-free station', 'Salad bar'],
      specials: ['International cuisine days', 'Theme dinners', 'Chef specials']
    },
    {
      name: 'The Cafe',
      type: 'Grab & Go',
      hours: {
        weekdays: '6:30 AM - 10:00 PM',
        weekends: '8:00 AM - 9:00 PM'
      },
      features: ['Sandwiches', 'Salads', 'Smoothies', 'Pastries', 'Coffee bar'],
      specials: ['Daily baked goods', 'Seasonal drinks']
    },
    {
      name: 'Global Kitchen',
      type: 'International Cuisine',
      hours: {
        weekdays: '11:00 AM - 9:00 PM',
        weekends: '12:00 PM - 8:00 PM'
      },
      features: ['Asian stir-fry', 'Mexican', 'Mediterranean', 'Indian curries'],
      specials: ['Rotating regional specialties', 'Cooking demonstrations']
    }
  ];

  const mealPlans = [
    {
      name: 'Unlimited Plan',
      description: 'Unlimited access to Commons Dining Hall + $200 flex dollars',
      price: '$2,800/semester',
      bestFor: 'Students who eat most meals on campus',
      features: ['Unlimited dining hall visits', '$200 flex dollars', 'Guest passes: 10', 'Late night access']
    },
    {
      name: 'Block 210',
      description: '210 meals per semester + $300 flex dollars',
      price: '$2,500/semester',
      bestFor: 'Students with regular meal patterns',
      features: ['210 meals', '$300 flex dollars', 'Guest passes: 5', 'Meal rollover']
    },
    {
      name: 'Block 140',
      description: '140 meals per semester + $400 flex dollars',
      price: '$2,100/semester',
      bestFor: 'Students who eat fewer meals on campus',
      features: ['140 meals', '$400 flex dollars', 'Guest passes: 3', 'Flexible scheduling']
    }
  ];

  const weeklyMenu = {
    monday: {
      breakfast: ['Scrambled eggs', 'Oatmeal bar', 'Fresh fruit', 'Yogurt parfaits'],
      lunch: ['Grilled chicken sandwiches', 'Vegetable soup', 'Pasta bar', 'Garden salad'],
      dinner: ['Beef stir-fry', 'Steamed rice', 'Roasted vegetables', 'Ice cream bar']
    },
    tuesday: {
      breakfast: ['Pancakes', 'Breakfast potatoes', 'Sausage links', 'Fresh berries'],
      lunch: ['Taco bar', 'Black bean soup', 'Mexican rice', 'Chips & salsa'],
      dinner: ['Baked salmon', 'Quinoa pilaf', 'Steamed broccoli', 'Chocolate cake']
    },
    wednesday: {
      breakfast: ['French toast', 'Scrambled eggs', 'Breakfast meats', 'Fruit salad'],
      lunch: ['Pizza station', 'Minestrone soup', 'Caesar salad', 'Garlic bread'],
      dinner: ['Chicken curry', 'Basmati rice', 'Naan bread', 'Mango lassi']
    }
  };

  const nutritionInfo = [
    {
      category: 'Allergen-Friendly',
      options: ['Gluten-free station', 'Dairy-free alternatives', 'Nut-free preparation areas', 'Vegan options']
    },
    {
      category: 'Healthy Choices',
      options: ['Heart-healthy options', 'Low-sodium meals', 'Whole grain selections', 'Fresh fruit always available']
    },
    {
      category: 'Special Diets',
      options: ['Vegetarian & vegan', 'Kosher options', 'Halal selections', 'Medical diet accommodations']
    }
  ];

  const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Campus Dining</h1>
          <p className="lead">Delicious, nutritious meals prepared with care for our campus community</p>
        </div>
        <Link to="/campus-life" className="btn btn-outline-primary">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Campus Life
        </Link>
      </div>

      {/* Hero Section */}
      <div className="card bg-success text-white mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-8">
              <h2 className="display-6 fw-bold">Fuel Your Success</h2>
              <p className="lead mb-0">
                From fresh, locally-sourced ingredients to international flavors, our dining program 
                supports your academic journey with delicious and nutritious meals.
              </p>
            </div>
            <div className="col-md-4 text-center">
              <i className="bi bi-egg-fried display-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body text-center">
              <h3>3</h3>
              <p className="mb-0">Dining Locations</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body text-center">
              <h3>95%</h3>
              <p className="mb-0">Locally Sourced</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body text-center">
              <h3>24/7</h3>
              <p className="mb-0">Late Night Options</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-secondary text-white">
            <div className="card-body text-center">
              <h3>100%</h3>
              <p className="mb-0">Dietary Accommodations</p>
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
                className={`nav-link ${activeTab === 'dining-halls' ? 'active' : ''}`}
                onClick={() => setActiveTab('dining-halls')}
              >
                <i className="bi bi-shop me-2"></i>
                Dining Locations
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'meal-plans' ? 'active' : ''}`}
                onClick={() => setActiveTab('meal-plans')}
              >
                <i className="bi bi-credit-card me-2"></i>
                Meal Plans
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'menus' ? 'active' : ''}`}
                onClick={() => setActiveTab('menus')}
              >
                <i className="bi bi-journal-text me-2"></i>
                Weekly Menus
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'nutrition' ? 'active' : ''}`}
                onClick={() => setActiveTab('nutrition')}
              >
                <i className="bi bi-heart me-2"></i>
                Nutrition & Diets
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Dining Locations Tab */}
          {activeTab === 'dining-halls' && (
            <div>
              <h4>Our Dining Locations</h4>
              <p className="text-muted mb-4">
                Multiple dining options across campus to fit your schedule and preferences.
              </p>

              <div className="row g-4">
                {diningLocations.map((location, index) => (
                  <div key={index} className="col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{location.name}</h5>
                        <span className="badge bg-primary">{location.type}</span>
                      </div>
                      <div className="card-body">
                        <div className="hours mb-3">
                          <h6>Hours:</h6>
                          <div className="d-flex justify-content-between">
                            <span>Weekdays:</span>
                            <span>{location.hours.weekdays}</span>
                          </div>
                          <div className="d-flex justify-content-between">
                            <span>Weekends:</span>
                            <span>{location.hours.weekends}</span>
                          </div>
                        </div>

                        <h6>Features:</h6>
                        <div className="d-flex flex-wrap gap-1 mb-3">
                          {location.features.map((feature, idx) => (
                            <span key={idx} className="badge bg-success">{feature}</span>
                          ))}
                        </div>

                        <h6>Weekly Specials:</h6>
                        <ul className="small">
                          {location.specials.map((special, idx) => (
                            <li key={idx}>{special}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-outline-primary btn-sm me-2">
                          View Menu
                        </button>
                        <button className="btn btn-outline-secondary btn-sm">
                          Directions
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
                      <h5 className="mb-0">Mobile Ordering</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Skip the lines with our mobile ordering app. Order ahead and pick up your 
                        food when it's ready.
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
                      <h5 className="mb-0">Sustainability</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        We're committed to sustainable dining practices:
                      </p>
                      <ul className="small">
                        <li>Composting food waste</li>
                        <li>Reusable container program</li>
                        <li>Local farm partnerships</li>
                        <li>Plant-forward menu options</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Meal Plans Tab */}
          {activeTab === 'meal-plans' && (
            <div>
              <h4>Meal Plan Options</h4>
              <p className="text-muted mb-4">
                Choose the meal plan that works best for your lifestyle and dining needs.
              </p>

              <div className="row g-4">
                {mealPlans.map((plan, index) => (
                  <div key={index} className="col-lg-4">
                    <div className="card h-100">
                      <div className="card-header text-center">
                        <h5 className="mb-0">{plan.name}</h5>
                        <div className="h4 text-primary mt-2">{plan.price}</div>
                      </div>
                      <div className="card-body">
                        <p className="card-text">{plan.description}</p>
                        
                        <div className="mb-3">
                          <strong>Best for:</strong>
                          <div>{plan.bestFor}</div>
                        </div>

                        <h6>Features:</h6>
                        <ul className="list-unstyled">
                          {plan.features.map((feature, idx) => (
                            <li key={idx} className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="card-footer">
                        <button className="btn btn-primary w-100">
                          Select This Plan
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
                      <h5 className="mb-0">Flex Dollars</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Flex dollars can be used at all campus dining locations, vending machines, 
                        and campus convenience stores.
                      </p>
                      <ul>
                        <li>Roll over fall to spring semester</li>
                        <li>Use for guests and family</li>
                        <li>Convenient card swipe system</li>
                        <li>Add more funds anytime</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Plan Management</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-grid gap-2">
                        <button className="btn btn-outline-primary text-start">
                          Change Meal Plan
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          Add Flex Dollars
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          Check Balance
                        </button>
                        <button className="btn btn-outline-primary text-start">
                          Guest Passes
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Weekly Menus Tab */}
          {activeTab === 'menus' && (
            <div>
              <h4>Weekly Menus</h4>
              <p className="text-muted mb-4">
                Check out what's cooking this week across all dining locations.
              </p>

              {/* Day Selector */}
              <div className="card mb-4">
                <div className="card-body">
                  <div className="d-flex justify-content-between overflow-auto">
                    {days.map((day) => (
                      <button
                        key={day}
                        className={`btn ${selectedDay === day ? 'btn-primary' : 'btn-outline-primary'} text-capitalize mx-1`}
                        onClick={() => setSelectedDay(day)}
                      >
                        {day}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Menu Display */}
              <div className="row">
                <div className="col-lg-8">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0 text-capitalize">{selectedDay} Menu - Commons Dining Hall</h5>
                    </div>
                    <div className="card-body">
                      {weeklyMenu[selectedDay] && (
                        <div className="row">
                          <div className="col-md-4">
                            <h6>Breakfast</h6>
                            <ul className="list-unstyled">
                              {weeklyMenu[selectedDay].breakfast.map((item, idx) => (
                                <li key={idx} className="mb-1">
                                  <i className="bi bi-egg-fried text-warning me-2"></i>
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div className="col-md-4">
                            <h6>Lunch</h6>
                            <ul className="list-unstyled">
                              {weeklyMenu[selectedDay].lunch.map((item, idx) => (
                                <li key={idx} className="mb-1">
                                  <i className="bi bi-egg-fried text-success me-2"></i>
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div className="col-md-4">
                            <h6>Dinner</h6>
                            <ul className="list-unstyled">
                              {weeklyMenu[selectedDay].dinner.map((item, idx) => (
                                <li key={idx} className="mb-1">
                                  <i className="bi bi-egg-fried text-primary me-2"></i>
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="alert alert-info mt-4">
                    <h6><i className="bi bi-info-circle me-2"></i>Menu Information</h6>
                    <p className="mb-0">
                      Menus are subject to change based on product availability. We always offer 
                      vegetarian, vegan, and allergen-friendly options at every meal.
                    </p>
                  </div>
                </div>
                <div className="col-lg-4">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">This Week's Specials</h5>
                    </div>
                    <div className="card-body">
                      <div className="mb-3">
                        <strong>Tuesday:</strong>
                        <div>Taco Tuesday - Build your own tacos</div>
                      </div>
                      <div className="mb-3">
                        <strong>Thursday:</strong>
                        <div>Pasta Night - Fresh pasta station</div>
                      </div>
                      <div className="mb-3">
                        <strong>Friday:</strong>
                        <div>Fish Fry - Beer-battered cod</div>
                      </div>
                      <div>
                        <strong>Sunday:</strong>
                        <div>Brunch Buffet - 10:00 AM - 2:00 PM</div>
                      </div>
                    </div>
                  </div>

                  <div className="card mt-4">
                    <div className="card-body text-center">
                      <h5>Download Menu App</h5>
                      <p className="text-muted">
                        Get real-time menu updates and nutritional information on your phone.
                      </p>
                      <button className="btn btn-primary">
                        <i className="bi bi-phone me-2"></i>
                        Get the App
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Nutrition & Diets Tab */}
          {activeTab === 'nutrition' && (
            <div>
              <h4>Nutrition & Dietary Accommodations</h4>
              <p className="text-muted mb-4">
                We're committed to meeting all dietary needs and promoting healthy eating habits.
              </p>

              <div className="row g-4">
                {nutritionInfo.map((category, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100">
                      <div className="card-header">
                        <h5 className="mb-0">{category.category}</h5>
                      </div>
                      <div className="card-body">
                        <ul className="list-unstyled">
                          {category.options.map((option, idx) => (
                            <li key={idx} className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              {option}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Meet Our Nutritionist</h5>
                    </div>
                    <div className="card-body">
                      <div className="d-flex align-items-center mb-3">
                        <div className="nutritionist-avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                             style={{width: '60px', height: '60px', fontSize: '1.5rem'}}>
                          <i className="bi bi-person"></i>
                        </div>
                        <div>
                          <h6 className="mb-1">Dr. Sarah Chen</h6>
                          <p className="text-muted mb-0">Registered Dietitian</p>
                        </div>
                      </div>
                      <p>
                        Schedule a free consultation with our campus nutritionist for personalized 
                        dietary guidance and meal planning.
                      </p>
                      <button className="btn btn-primary">
                        Schedule Consultation
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">Special Diet Requests</h5>
                    </div>
                    <div className="card-body">
                      <p>
                        Need special dietary accommodations? We can help with:
                      </p>
                      <ul>
                        <li>Food allergies and intolerances</li>
                        <li>Medical dietary restrictions</li>
                        <li>Religious dietary requirements</li>
                        <li>Athletic performance nutrition</li>
                      </ul>
                      <button className="btn btn-outline-primary">
                        Request Accommodations
                      </button>
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

export default Dining;