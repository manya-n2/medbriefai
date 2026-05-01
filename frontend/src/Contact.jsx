import React from 'react';
import { Link } from 'react-router-dom';
import './Contact.css';

const Contact = () => {
  // Handler for form submission (optional logic)
  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Message sent! (This is a demo)");
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
          {/* Use Link to navigate back to Home without refreshing */}
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
                  <input type="text" placeholder="XYZ" required />
                </div>
                <div className="input-group">
                  <label>Work Email</label>
                  <input type="email" placeholder="xyz@example.com" required />
                </div>
              </div>

              <div className="input-group">
                <label>Subject</label>
                <select className="goal-select">
                  <option>General Inquiry</option>
                  <option>Technical Support</option>
                  <option>Partnership/API Access</option>
                  <option>Feedback</option>
                </select>
              </div>

              <div className="input-group">
                <label>Message</label>
                <textarea placeholder="How can we assist you today?"></textarea>
              </div>

              <button type="submit" className="btn-primary glow-hover">
                Send Message
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