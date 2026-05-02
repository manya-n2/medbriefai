import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Contact.css';

const Contact = () => {
  // 1. State Management for Form Fields
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    subject: 'General Inquiry',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 2. Handle Input Changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  // 3. Form Submission Handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Calling your FastAPI backend endpoint
      const response = await fetch('http://localhost:8000/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert("Success! Your message has been saved to the database.");
        // Reset form after success
        setFormData({
          full_name: '',
          email: '',
          subject: 'General Inquiry',
          message: ''
        });
      } else {
        const errorData = await response.json();
        alert(`Failed to send: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Connection Error:", error);
      alert("Could not connect to the server. Is the FastAPI backend running?");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="clinical-app">
      {/* 1. NAVBAR */}
      <nav className="navbar glass">
        <div className="nav-brand">
          <span className="logo-icon">⚕️</span>
          <span className="app-name">MedBrief AI</span>
        </div>
        <div className="nav-links">
          <Link to="/">Home</Link>
          <a href="/#features">Features</a>
          <a href="/#about">About</a>
          <Link to="/contact" className="active">Contact</Link>
        </div>
      </nav>

      {/* 2. CONTACT HERO */}
      <section className="contact-hero">
        <div className="glow-shape shape-1"></div>
        <div className="glow-shape shape-2"></div>
        <div className="hero-text fade-in">
          <h1 className="gradient-text">Get in Touch</h1>
          <p className="subheading">
            Have questions about our Agentic AI workflow or integration? 
            Our technical team is here to help.
          </p>
        </div>
      </section>

      {/* 3. CONTACT CONTENT */}
      <section className="contact-container">
        <div className="contact-grid">
          
          {/* Sidebar Info */}
          <div className="contact-info">
            <div className="info-card glass hover-elevate">
              <div className="icon">📧</div>
              <h4>Email Us</h4>
              <p>support@clinicalai.demo</p>
            </div>
            <div className="info-card glass hover-elevate">
              <div className="icon">🐙</div>
              <h4>Open Source</h4>
              <p>github.com/manya-n2/medbriefai</p>
            </div>
            <div className="info-card glass hover-elevate">
              <div className="icon">📍</div>
              <h4>Location</h4>
              <p>Engineering Hub, India</p>
            </div>
          </div>

          {/* Contact Form */}
          <div className="contact-form-wrapper glass fade-in">
            <form id="contactForm" onSubmit={handleSubmit}>
              <div className="input-row">
                <div className="input-group">
                  <label>Full Name</label>
                  <input 
                    type="text" 
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    placeholder="Enter your name" 
                    required 
                  />
                </div>
                <div className="input-group">
                  <label>Work Email</label>
                  <input 
                    type="email" 
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="xyz@example.com" 
                    required 
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Subject</label>
                <select 
                  className="goal-select"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                >
                  <option value="General Inquiry">General Inquiry</option>
                  <option value="Technical Support">Technical Support</option>
                  <option value="Partnership/API Access">Partnership/API Access</option>
                  <option value="Feedback">Feedback</option>
                </select>
              </div>

              <div className="input-group">
                <label>Message</label>
                <textarea 
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  placeholder="How can we assist you today?"
                  required
                ></textarea>
              </div>

              <button 
                type="submit" 
                className="btn-primary glow-hover"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Sending..." : "Send Message"}
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* 4. FOOTER */}
      <footer className="footer">
        <div className="footer-bottom">
          <p>&copy; 2026 MedBrief AI .</p>
        </div>
      </footer>
    </div>
  );
};

export default Contact;