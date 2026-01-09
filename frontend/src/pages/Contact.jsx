import React, { useState } from 'react';

function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // For now, just show success message
    alert('Thank you for your message! We will get back to you soon.');
    setFormData({
      name: '',
      email: '',
      subject: '',
      message: ''
    });
  };

  return (
    <div className="contact-page">
      <div className="container mt-4">
        <div className="row">
          <div className="col-lg-8 mx-auto">
            <div className="card shadow-sm">
              <div className="card-header bg-primary text-white">
                <h3 className="card-title mb-0">Contact Us</h3>
              </div>
              <div className="card-body p-4">
                <div className="row mb-4">
                  <div className="col-md-4 text-center">
                    <div className="contact-info">
                      <i className="bi bi-geo-alt fs-1 text-primary"></i>
                      <h5>Address</h5>
                      <p>123 Education Road<br />Nairobi, Kenya</p>
                    </div>
                  </div>
                  <div className="col-md-4 text-center">
                    <div className="contact-info">
                      <i className="bi bi-telephone fs-1 text-primary"></i>
                      <h5>Phone</h5>
                      <p>+254-700-123-456</p>
                    </div>
                  </div>
                  <div className="col-md-4 text-center">
                    <div className="contact-info">
                      <i className="bi bi-envelope fs-1 text-primary"></i>
                      <h5>Email</h5>
                      <p>info@delvok.ac.ke</p>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleSubmit}>
                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label htmlFor="name" className="form-label">Full Name</label>
                        <input
                          type="text"
                          className="form-control"
                          id="name"
                          name="name"
                          value={formData.name}
                          onChange={handleChange}
                          required
                        />
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label htmlFor="email" className="form-label">Email Address</label>
                        <input
                          type="email"
                          className="form-control"
                          id="email"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="subject" className="form-label">Subject</label>
                    <input
                      type="text"
                      className="form-control"
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label htmlFor="message" className="form-label">Message</label>
                    <textarea
                      className="form-control"
                      id="message"
                      name="message"
                      rows="5"
                      value={formData.message}
                      onChange={handleChange}
                      required
                    ></textarea>
                  </div>

                  <button type="submit" className="btn btn-primary btn-lg">
                    Send Message
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Contact;